"""
Authentication layer: Google OAuth (ID token) + JWT session tokens.

Verifies Google ID tokens (the `credential` returned by Google Identity
Services on the frontend) without requiring an extra HTTP round trip
by using google-auth's `id_token.verify_oauth2_token` which fetches and
caches Google's public keys automatically.

Issues short-lived JWTs that the frontend includes as
`Authorization: Bearer <token>` for all protected API calls.
"""
from __future__ import annotations

import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from models import User

logger = logging.getLogger(__name__)
load_dotenv()


# ============ Config ============

# Toggle to disable auth (useful for first run / local dev when no
# Google client id is configured yet). When AUTH_ENABLED is false ALL
# authentication checks are bypassed.
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() not in ("0", "false", "no")

# JWT secret. Must be configured in any production deployment. When
# missing we generate a random per-process secret so existing tokens are
# invalidated on every restart (fail-secure) instead of using a known
# default that anyone can forge tokens against.
_JWT_SECRET_ENV = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
if _JWT_SECRET_ENV:
    JWT_SECRET = _JWT_SECRET_ENV
else:
    JWT_SECRET = secrets.token_urlsafe(48)
    if AUTH_ENABLED:
        logger.warning(
            "JWT_SECRET is not set. Generated an ephemeral per-process secret; "
            "issued tokens will be invalidated on every restart. Set JWT_SECRET "
            "in the environment for production deployments."
        )

JWT_ALGORITHM = "HS256"
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "24"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


def _read_non_negative_int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError:
        logger.warning("%s=%r is invalid. Falling back to %s.", name, raw, default)
        return default
    if value < 0:
        logger.warning("%s=%r is negative. Falling back to %s.", name, raw, default)
        return default
    return value


GOOGLE_TOKEN_CLOCK_SKEW_SECONDS = _read_non_negative_int_env(
    "GOOGLE_TOKEN_CLOCK_SKEW_SECONDS", 60
)

# Explicit dev mode flag to enable insecure helpers (e.g., decoding
# Google ID tokens without signature verification when google-auth is
# unavailable). Defaults to off so production deployments are safe.
DEV_MODE = os.getenv("DEV_MODE", "").lower() in ("1", "true", "yes")


bearer_scheme = HTTPBearer(auto_error=False)


# ============ Google ID token verification ============

def verify_google_id_token(credential: str) -> dict:
    """Verify a Google ID token (JWT) and return its payload.

    Always uses google-auth to verify the signature and issuer against
    Google's public keys. If google-auth is not installed the request
    fails closed unless DEV_MODE=true is explicitly set, in which case a
    signature-less decode is performed (development only).
    """
    if not credential:
        raise HTTPException(status_code=400, detail="Thiếu Google credential")

    # Preferred: real Google verification
    try:
        from google.oauth2 import id_token  # type: ignore
        from google.auth.transport import requests as g_requests  # type: ignore

        request = g_requests.Request()
        if GOOGLE_CLIENT_ID:
            info = id_token.verify_oauth2_token(
                credential,
                request,
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=GOOGLE_TOKEN_CLOCK_SKEW_SECONDS,
            )
        else:
            # No client id configured: verify signature only.
            info = id_token.verify_oauth2_token(
                credential,
                request,
                clock_skew_in_seconds=GOOGLE_TOKEN_CLOCK_SKEW_SECONDS,
            )
        if info.get("iss") not in (
            "accounts.google.com",
            "https://accounts.google.com",
        ):
            raise HTTPException(status_code=401, detail="Issuer không hợp lệ")
        return info
    except ImportError:
        if not DEV_MODE:
            logger.error(
                "google-auth is not installed; refusing to verify Google ID "
                "token without signature verification. Install google-auth or "
                "set DEV_MODE=true for local development."
            )
            raise HTTPException(
                status_code=503,
                detail="Hệ thống chưa cấu hình xác thực Google (thiếu google-auth)",
            )
        # DEV-only fallback - decode without signature verification.
        logger.warning(
            "DEV_MODE active: accepting Google ID token without signature "
            "verification. Do NOT enable this in production."
        )
        try:
            payload = jwt.get_unverified_claims(credential)
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Token không hợp lệ: {e}")
        return payload
    except HTTPException:
        raise
    except Exception as e:  # google-auth raises ValueError on bad tokens
        msg = str(e)
        if "Token used too early" in msg:
            raise HTTPException(
                status_code=401,
                detail=(
                    "Google token không hợp lệ do lệch thời gian hệ thống. "
                    "Vui lòng đồng bộ giờ máy chủ/máy khách và thử lại. "
                    f"(clock skew hiện tại: {GOOGLE_TOKEN_CLOCK_SKEW_SECONDS}s)"
                ),
            )
        raise HTTPException(status_code=401, detail=f"Google token không hợp lệ: {e}")


# ============ JWT session tokens ============

def create_access_token(user: User) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name or "",
        "iat": now,
        "exp": now + JWT_EXP_HOURS * 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ: {e}")


# ============ User upsert ============

def upsert_user_from_google(db: Session, info: dict) -> User:
    sub = info.get("sub")
    email = info.get("email") or ""
    if not sub:
        raise HTTPException(status_code=400, detail="Google payload thiếu 'sub'")

    user = db.query(User).filter(User.google_sub == sub).first()
    now = datetime.utcnow()
    if user:
        user.email = email or user.email
        user.name = info.get("name") or user.name
        user.picture = info.get("picture") or user.picture
        user.last_login_at = now
    else:
        user = User(
            google_sub=sub,
            email=email,
            name=info.get("name"),
            picture=info.get("picture"),
            last_login_at=now,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ============ FastAPI dependencies ============

def get_current_user_factory(get_db):
    """Build a `get_current_user` dependency that uses the given db getter.

    Returned dependency raises 401 if no/invalid token. When AUTH_ENABLED
    is false, returns None (i.e., public access).
    """

    def get_current_user(
        request: Request,
        creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
        db: Session = Depends(get_db),
    ) -> Optional[User]:
        if not AUTH_ENABLED:
            return None
        if not creds or not creds.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Yêu cầu đăng nhập",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = decode_access_token(creds.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token thiếu sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")
        return user

    return get_current_user


def auth_enabled() -> bool:
    return AUTH_ENABLED
