"""
Tử Vi Gia Đình - Family Relationship Intelligence System
FastAPI Backend
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import json

from models import Base, Family, FamilyMember, User, SavedAnalysis
from schemas import (
    FamilyCreate, FamilyUpdate, FamilyResponse,
    FamilyMemberCreate, FamilyMemberUpdate, FamilyMemberResponse,
    FamilyAnalysisResponse, AnnualForecastRequest, ChatRequest,
    DateConversionRequest,
    GoogleLoginRequest, TokenResponse, UserResponse,
    SavedAnalysisCreate, SavedAnalysisSummary, SavedAnalysisDetail,
)
from astrology_engine import get_can_chi_from_year, get_ngu_hanh, get_personality_traits, get_energy_role
from compatibility_engine import analyze_family, get_family_annual_forecast
from ai_layer import get_ai_interpretation, get_ai_family_chat, has_openai_key
from lunar_calendar import solar_to_lunar, lunar_to_solar
from data_sources import all_sources
from auth import (
    verify_google_id_token,
    upsert_user_from_google,
    create_access_token,
    get_current_user_factory,
    auth_enabled,
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tuvigiadinh.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Lightweight migration: add new lunar/solar columns to existing
    # family_members tables (created before this version).
    _migrate_add_lunar_columns()
    yield


def _migrate_add_lunar_columns():
    """Add new columns to family_members / families if they're missing.

    SQLAlchemy's create_all() does not alter existing tables. For users
    upgrading from a previous version we issue ALTER TABLE statements
    for the columns introduced in this release. Safe to run repeatedly.

    All identifiers in the ALTER TABLE statements come from a fixed
    allow-list defined here (no user input), and are additionally
    validated against an identifier regex before interpolation, to
    satisfy linters that flag any string-built SQL.
    """
    import re
    member_new_columns = [
        ("birth_calendar", "VARCHAR(10) DEFAULT 'solar'"),
        ("solar_year", "INTEGER"),
        ("solar_month", "INTEGER"),
        ("solar_day", "INTEGER"),
        ("lunar_year", "INTEGER"),
        ("lunar_month", "INTEGER"),
        ("lunar_day", "INTEGER"),
        ("is_leap_month", "INTEGER DEFAULT 0"),
        ("occupation", "VARCHAR(200)"),
    ]
    family_new_columns = [
        ("owner_id", "INTEGER"),
    ]
    allowed_type_pattern = re.compile(r"^[A-Z]+(\([0-9]+\))?( DEFAULT '?[A-Za-z0-9 ]+'?)?$")
    ident_pattern = re.compile(r"^[a-z_][a-z0-9_]*$")
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    with engine.begin() as conn:
        for table, cols in (
            ("family_members", member_new_columns),
            ("families", family_new_columns),
        ):
            if table not in tables:
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            for name, col_type in cols:
                if not ident_pattern.match(name) or not allowed_type_pattern.match(col_type):
                    continue
                if name not in existing:
                    try:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"))
                    except Exception as e:
                        print(f"[migration] could not add column {name} on {table}: {e}")


app = FastAPI(
    title="Tử Vi Gia Đình API",
    description="Family Relationship Intelligence System based on Eastern Astrology",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_current_user = get_current_user_factory(get_db)


def _ensure_family_owner(family: Family, user: User | None):
    """Ensure the current user owns the family (when auth is enabled).

    Legacy families (owner_id is NULL, created before auth) are accessible
    to any authenticated user. After this access they are claimed by the
    first user who touches them.
    """
    if not auth_enabled() or user is None:
        return
    if family.owner_id is None:
        family.owner_id = user.id
        return
    if family.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập gia đình này")


def compute_member_astrology(birth_year: int) -> dict:
    """Compute astrological data for a family member.

    Note: birth_year here MUST be the lunar year, because the sexagenary
    cycle (Can Chi) is based on the lunar calendar.
    """
    can, chi = get_can_chi_from_year(birth_year)
    hanh_info = get_ngu_hanh(can, chi)
    traits = get_personality_traits(can, chi)
    energy_role = get_energy_role(can, chi, {"can_hanh": hanh_info["can_hanh"]})

    return {
        "thien_can": can,
        "dia_chi": chi,
        "ngu_hanh": hanh_info["can_hanh"],
        "nap_am": hanh_info["nap_am"],
        "energy_role": energy_role,
        "traits": traits,
    }


def resolve_birth_dates(
    birth_calendar: str,
    year: int,
    month: int | None,
    day: int | None,
    is_leap_month: bool,
) -> dict:
    """Resolve both solar and lunar dates given a user-supplied date.

    Returns a dict with solar_year/month/day, lunar_year/month/day,
    is_leap_month and the effective 'lunar_year' that should be used
    to compute Can Chi.

    If month/day is missing, we cannot perform conversion - we fall
    back to using the supplied year as the lunar year for Can Chi
    (this is the legacy behaviour for backwards compatibility).
    """
    if month and day:
        if birth_calendar == "lunar":
            solar = lunar_to_solar(year, month, day, is_leap_month)
            return {
                "solar_year": solar["solar_year"],
                "solar_month": solar["solar_month"],
                "solar_day": solar["solar_day"],
                "lunar_year": year,
                "lunar_month": month,
                "lunar_day": day,
                "is_leap_month": is_leap_month,
                "effective_lunar_year": year,
            }
        # solar -> lunar
        lunar = solar_to_lunar(year, month, day)
        return {
            "solar_year": year,
            "solar_month": month,
            "solar_day": day,
            "lunar_year": lunar["lunar_year"],
            "lunar_month": lunar["lunar_month"],
            "lunar_day": lunar["lunar_day"],
            "is_leap_month": lunar["is_leap_month"],
            "effective_lunar_year": lunar["lunar_year"],
        }
    # Missing month/day: keep year-only behaviour. Treat the supplied
    # year as the lunar year if user said 'lunar', else as solar year.
    if birth_calendar == "lunar":
        return {
            "solar_year": None, "solar_month": None, "solar_day": None,
            "lunar_year": year, "lunar_month": None, "lunar_day": None,
            "is_leap_month": is_leap_month,
            "effective_lunar_year": year,
        }
    return {
        "solar_year": year, "solar_month": None, "solar_day": None,
        "lunar_year": None, "lunar_month": None, "lunar_day": None,
        "is_leap_month": False,
        "effective_lunar_year": year,
    }


def member_to_dict(member: FamilyMember) -> dict:
    """Convert FamilyMember model to dict for analysis"""
    return {
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "gender": member.gender,
        "occupation": member.occupation or "",
        "birth_year": member.birth_year,
        "birth_month": member.birth_month,
        "birth_day": member.birth_day,
        "birth_hour": member.birth_hour or "",
        "birth_calendar": member.birth_calendar or "solar",
        "solar_year": member.solar_year,
        "solar_month": member.solar_month,
        "solar_day": member.solar_day,
        "lunar_year": member.lunar_year,
        "lunar_month": member.lunar_month,
        "lunar_day": member.lunar_day,
        "is_leap_month": bool(member.is_leap_month),
        "thien_can": member.thien_can or "",
        "dia_chi": member.dia_chi or "",
        "ngu_hanh": member.ngu_hanh or "",
        "nap_am": member.nap_am or "",
        "energy_role": member.energy_role or "",
    }


def _sort_key_for_birth(m: dict) -> tuple:
    """Best-effort comparable date key for ordering children by birth."""
    y = m.get("solar_year") or m.get("lunar_year") or m.get("birth_year") or 0
    mo = m.get("solar_month") or m.get("lunar_month") or m.get("birth_month") or 0
    d = m.get("solar_day") or m.get("lunar_day") or m.get("birth_day") or 0
    return (y, mo, d, m.get("id") or 0)


def _annotate_members(members_data: list[dict]) -> list[dict]:
    """Add derived fields: age, birth_order/birth_order_label for children."""
    from datetime import datetime as _dt

    current_year = _dt.now().year
    children = [m for m in members_data if (m.get("role") or "") == "con"]
    children_sorted = sorted(children, key=_sort_key_for_birth)
    total = len(children_sorted)
    order_map: dict[int, tuple[int, str]] = {}
    for idx, ch in enumerate(children_sorted):
        order = idx + 1
        if total == 1:
            label = "con duy nhất"
        elif order == 1:
            label = "con đầu (con cả)"
        elif order == total:
            label = "con út"
        else:
            label = f"con thứ {order}"
        order_map[id(ch)] = (order, label)

    for m in members_data:
        by = m.get("birth_year")
        m["age"] = (current_year - by) if isinstance(by, int) and by > 0 else None
        if id(m) in order_map:
            order, label = order_map[id(m)]
            m["birth_order"] = order
            m["birth_order_label"] = label
            m["siblings_count"] = total
        else:
            m["birth_order"] = None
            m["birth_order_label"] = None
            m["siblings_count"] = total if (m.get("role") or "") == "con" else 0
    return members_data


# ============ Auth Endpoints ============

@app.get("/api/auth/config")
def auth_config():
    """Public: return whether auth is required and the Google client id
    so the frontend can render the login button correctly."""
    return {
        "auth_enabled": auth_enabled(),
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
    }


@app.post("/api/auth/google", response_model=TokenResponse)
def login_with_google(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Exchange a Google ID token for an application JWT."""
    info = verify_google_id_token(req.credential)
    user = upsert_user_from_google(db, info)
    token = create_access_token(user)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    return user


# ============ Family Endpoints ============

@app.get("/")
def root():
    return {"message": "Tử Vi Gia Đình API", "version": "1.1.0"}


@app.get("/api/families", response_model=list[FamilyResponse])
def get_families(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Get families owned by the current user (or all if auth is disabled)."""
    q = db.query(Family)
    if auth_enabled() and user is not None:
        q = q.filter((Family.owner_id == user.id) | (Family.owner_id.is_(None)))
    return q.order_by(Family.created_at.desc()).all()


@app.post("/api/families", response_model=FamilyResponse)
def create_family(
    family: FamilyCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Create a new family owned by the current user."""
    db_family = Family(
        name=family.name,
        description=family.description,
        owner_id=user.id if user else None,
    )
    db.add(db_family)
    db.commit()
    db.refresh(db_family)
    return db_family


@app.get("/api/families/{family_id}", response_model=FamilyResponse)
def get_family(
    family_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Get a specific family with all members"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)
    db.commit()  # persist potential ownership claim
    return family


@app.patch("/api/families/{family_id}", response_model=FamilyResponse)
def update_family(
    family_id: int,
    payload: FamilyUpdate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Edit a family's name and/or description."""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)
    if payload.name is not None:
        family.name = payload.name
    if payload.description is not None:
        family.description = payload.description
    db.commit()
    db.refresh(family)
    return family


@app.delete("/api/families/{family_id}")
def delete_family(
    family_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Delete a family"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)
    db.delete(family)
    db.commit()
    return {"message": "Đã xóa gia đình"}


# ============ Family Member Endpoints ============

@app.post("/api/families/{family_id}/members", response_model=FamilyMemberResponse)
def add_family_member(
    family_id: int,
    member: FamilyMemberCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Add a member to a family.

    Accepts either solar or lunar birth date via `birth_calendar`.
    The system stores both calendar representations and uses the lunar
    year (which the sexagenary cycle is based on) to compute Can Chi.
    """
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)

    birth_calendar = (member.birth_calendar or "solar").lower()
    if birth_calendar not in ("solar", "lunar"):
        raise HTTPException(
            status_code=400,
            detail="birth_calendar phải là 'solar' hoặc 'lunar'",
        )

    try:
        dates = resolve_birth_dates(
            birth_calendar,
            member.birth_year,
            member.birth_month,
            member.birth_day,
            bool(member.is_leap_month),
        )
    except Exception as e:  # invalid date for conversion
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển đổi ngày sinh: {e}",
        )

    # Compute astrological data using the LUNAR year
    astro = compute_member_astrology(dates["effective_lunar_year"])

    db_member = FamilyMember(
        family_id=family_id,
        name=member.name,
        role=member.role,
        gender=member.gender,
        occupation=member.occupation,
        birth_year=member.birth_year,
        birth_month=member.birth_month,
        birth_day=member.birth_day,
        birth_hour=member.birth_hour,
        birth_calendar=birth_calendar,
        solar_year=dates["solar_year"],
        solar_month=dates["solar_month"],
        solar_day=dates["solar_day"],
        lunar_year=dates["lunar_year"],
        lunar_month=dates["lunar_month"],
        lunar_day=dates["lunar_day"],
        is_leap_month=1 if dates["is_leap_month"] else 0,
        thien_can=astro["thien_can"],
        dia_chi=astro["dia_chi"],
        ngu_hanh=astro["ngu_hanh"],
        nap_am=astro["nap_am"],
        energy_role=astro["energy_role"],
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@app.patch("/api/families/{family_id}/members/{member_id}", response_model=FamilyMemberResponse)
def update_family_member(
    family_id: int,
    member_id: int,
    payload: FamilyMemberUpdate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Update a family member. Recomputes Can-Chi/Ngũ hành if birth
    date or calendar changes."""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)

    db_member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id, FamilyMember.family_id == family_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

    data = payload.model_dump(exclude_unset=True)

    # Simple scalar updates
    for f in ("name", "role", "gender", "occupation", "birth_hour"):
        if f in data and data[f] is not None:
            setattr(db_member, f, data[f])

    # Date / calendar update requires re-resolving
    date_keys = {"birth_year", "birth_month", "birth_day", "birth_calendar", "is_leap_month"}
    if date_keys & data.keys():
        new_year = data.get("birth_year", db_member.birth_year)
        new_month = data.get("birth_month", db_member.birth_month)
        new_day = data.get("birth_day", db_member.birth_day)
        new_cal = (data.get("birth_calendar") or db_member.birth_calendar or "solar").lower()
        new_leap = bool(data.get("is_leap_month", bool(db_member.is_leap_month)))
        if new_cal not in ("solar", "lunar"):
            raise HTTPException(status_code=400, detail="birth_calendar phải là 'solar' hoặc 'lunar'")
        try:
            dates = resolve_birth_dates(new_cal, new_year, new_month, new_day, new_leap)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Không thể chuyển đổi ngày sinh: {e}")
        astro = compute_member_astrology(dates["effective_lunar_year"])
        db_member.birth_year = new_year
        db_member.birth_month = new_month
        db_member.birth_day = new_day
        db_member.birth_calendar = new_cal
        db_member.solar_year = dates["solar_year"]
        db_member.solar_month = dates["solar_month"]
        db_member.solar_day = dates["solar_day"]
        db_member.lunar_year = dates["lunar_year"]
        db_member.lunar_month = dates["lunar_month"]
        db_member.lunar_day = dates["lunar_day"]
        db_member.is_leap_month = 1 if dates["is_leap_month"] else 0
        db_member.thien_can = astro["thien_can"]
        db_member.dia_chi = astro["dia_chi"]
        db_member.ngu_hanh = astro["ngu_hanh"]
        db_member.nap_am = astro["nap_am"]
        db_member.energy_role = astro["energy_role"]

    db.commit()
    db.refresh(db_member)
    return db_member


@app.delete("/api/families/{family_id}/members/{member_id}")
def delete_member(
    family_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Delete a family member"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)
    member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id,
        FamilyMember.family_id == family_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")
    db.delete(member)
    db.commit()
    return {"message": "Đã xóa thành viên"}


# ============ Analysis Endpoints ============

@app.get("/api/families/{family_id}/analysis")
async def get_family_analysis(
    family_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Get comprehensive family compatibility analysis"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)

    if len(family.members) < 2:
        raise HTTPException(
            status_code=400,
            detail="Cần ít nhất 2 thành viên để phân tích tương hợp"
        )

    members_data = _annotate_members([member_to_dict(m) for m in family.members])

    # Run compatibility analysis
    analysis = analyze_family(members_data)

    # Attach current-year forecast so the AI/offline interpretation can
    # reference vận khí năm hiện tại.
    from datetime import datetime as _dt
    current_year = _dt.now().year
    try:
        analysis["annual_forecast"] = get_family_annual_forecast(members_data, current_year)
    except Exception:
        analysis["annual_forecast"] = None

    # Get AI interpretation (falls back to rich offline analysis if no key)
    family_data = {
        "name": family.name,
        "members": members_data,
    }
    ai_interpretation = await get_ai_interpretation(family_data, analysis)
    analysis["ai_interpretation"] = ai_interpretation
    analysis["analysis_mode"] = "online" if has_openai_key() else "offline"
    analysis["sources"] = all_sources()
    analysis["members_snapshot"] = members_data

    return {
        "family_name": family.name,
        "members_count": len(family.members),
        **analysis
    }


@app.post("/api/families/{family_id}/forecast")
def get_annual_forecast(
    family_id: int,
    request: AnnualForecastRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Get annual forecast for the family"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)

    members_data = _annotate_members([member_to_dict(m) for m in family.members])
    forecast = get_family_annual_forecast(members_data, request.year)

    return forecast


# ============ Saved Analyses Endpoints ============

@app.get("/api/families/{family_id}/saved-analyses", response_model=list[SavedAnalysisSummary])
def list_saved_analyses(
    family_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)
    rows = (
        db.query(SavedAnalysis)
        .filter(SavedAnalysis.family_id == family_id)
        .order_by(SavedAnalysis.created_at.desc())
        .all()
    )
    return rows


@app.post("/api/families/{family_id}/saved-analyses", response_model=SavedAnalysisDetail)
async def save_family_analysis(
    family_id: int,
    payload: SavedAnalysisCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Compute fresh analysis and persist a snapshot."""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)
    if len(family.members) < 2:
        raise HTTPException(
            status_code=400, detail="Cần ít nhất 2 thành viên để phân tích",
        )

    members_data = _annotate_members([member_to_dict(m) for m in family.members])
    analysis = analyze_family(members_data)
    from datetime import datetime as _dt
    current_year = _dt.now().year
    try:
        analysis["annual_forecast"] = get_family_annual_forecast(members_data, current_year)
    except Exception:
        analysis["annual_forecast"] = None
    family_data = {"name": family.name, "members": members_data}
    analysis["ai_interpretation"] = await get_ai_interpretation(family_data, analysis)
    analysis["analysis_mode"] = "online" if has_openai_key() else "offline"
    analysis["sources"] = all_sources()
    analysis["members_snapshot"] = members_data
    analysis["family_name"] = family.name
    analysis["members_count"] = len(family.members)

    record = SavedAnalysis(
        family_id=family_id,
        user_id=user.id if user else None,
        title=payload.title or f"Phân tích {current_year}",
        note=payload.note,
        payload=json.dumps(analysis, ensure_ascii=False),
        family_overall_score=analysis.get("family_overall_score"),
        analysis_mode=analysis.get("analysis_mode"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return SavedAnalysisDetail(
        id=record.id,
        family_id=record.family_id,
        title=record.title,
        note=record.note,
        family_overall_score=record.family_overall_score,
        analysis_mode=record.analysis_mode,
        created_at=record.created_at,
        payload=analysis,
    )


@app.get("/api/saved-analyses/{analysis_id}", response_model=SavedAnalysisDetail)
def get_saved_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    record = db.query(SavedAnalysis).filter(SavedAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản phân tích")
    family = db.query(Family).filter(Family.id == record.family_id).first()
    if family:
        _ensure_family_owner(family, user)
    try:
        payload = json.loads(record.payload)
    except Exception:
        payload = {}
    return SavedAnalysisDetail(
        id=record.id,
        family_id=record.family_id,
        title=record.title,
        note=record.note,
        family_overall_score=record.family_overall_score,
        analysis_mode=record.analysis_mode,
        created_at=record.created_at,
        payload=payload,
    )


@app.delete("/api/saved-analyses/{analysis_id}")
def delete_saved_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    record = db.query(SavedAnalysis).filter(SavedAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản phân tích")
    family = db.query(Family).filter(Family.id == record.family_id).first()
    if family:
        _ensure_family_owner(family, user)
    db.delete(record)
    db.commit()
    return {"message": "Đã xóa"}


@app.post("/api/families/{family_id}/chat")
async def family_chat(
    family_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """AI Family Advisor chat"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    _ensure_family_owner(family, user)

    members_data = _annotate_members([member_to_dict(m) for m in family.members])

    # Build analysis context with pair-by-pair summary so the model can
    # reference specific Sinh-Khắc relationships when answering.
    analysis = analyze_family(members_data)
    score = analysis.get("family_overall_score", 50)
    dynamics = analysis.get("family_dynamics", "")
    pair_lines = []
    for p in analysis.get("pairs_analysis", []):
        sk = (p.get("sinh_khac") or {}).get("headline", "")
        pair_lines.append(
            f"- {p.get('member1_name','?')} ↔ {p.get('member2_name','?')} "
            f"({p.get('relationship_type') or 'quan hệ'}): "
            f"{p.get('overall_score','?')}/100 - {p.get('compatibility_level','')}"
            + (f" | {sk}" if sk else "")
        )
    pair_block = "\n".join(pair_lines) if pair_lines else "(chưa đủ cặp để phân tích)"
    analysis_context = (
        f"Điểm tổng hợp gia đình: {score}/100. {dynamics}\n"
        f"Phân tích các cặp quan hệ:\n{pair_block}"
    )

    family_data = {
        "name": family.name,
        "members": members_data,
    }

    response = await get_ai_family_chat(family_data, request.question, analysis_context)

    return {"response": response}


@app.get("/api/astrology/can-chi/{year}")
def get_can_chi(year: int):
    """Get Can Chi for a specific year"""
    if year < 1900 or year > 2100:
        raise HTTPException(status_code=400, detail="Năm phải từ 1900 đến 2100")

    can, chi = get_can_chi_from_year(year)
    hanh_info = get_ngu_hanh(can, chi)

    return {
        "year": year,
        "thien_can": can,
        "dia_chi": chi,
        "ngu_hanh": hanh_info["can_hanh"],
        "nap_am": hanh_info["nap_am"],
        "display": f"Năm {can} {chi}"
    }


@app.post("/api/astrology/convert-date")
def convert_date(req: DateConversionRequest):
    """Convert a date between solar and lunar Vietnamese calendars."""
    calendar = (req.calendar or "solar").lower()
    if calendar not in ("solar", "lunar"):
        raise HTTPException(
            status_code=400, detail="calendar phải là 'solar' hoặc 'lunar'"
        )
    try:
        if calendar == "solar":
            lunar = solar_to_lunar(req.year, req.month, req.day)
            return {
                "input": {"calendar": "solar", "year": req.year, "month": req.month, "day": req.day},
                "solar": {"year": req.year, "month": req.month, "day": req.day},
                "lunar": lunar,
            }
        solar = lunar_to_solar(req.year, req.month, req.day, req.is_leap_month)
        return {
            "input": {"calendar": "lunar", "year": req.year, "month": req.month, "day": req.day, "is_leap_month": req.is_leap_month},
            "lunar": {"year": req.year, "month": req.month, "day": req.day, "is_leap_month": req.is_leap_month},
            "solar": solar,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi chuyển đổi: {e}")


@app.get("/api/astrology/sources")
def get_sources():
    """Return the bibliography of references used by offline analysis."""
    return {"sources": all_sources()}


@app.get("/api/health/ai")
def ai_health():
    """Report whether OpenAI API key is configured (offline mode otherwise)."""
    return {
        "openai_configured": has_openai_key(),
        "mode": "online" if has_openai_key() else "offline",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
