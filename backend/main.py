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

from models import Base, Family, FamilyMember
from schemas import (
    FamilyCreate, FamilyResponse,
    FamilyMemberCreate, FamilyMemberResponse,
    FamilyAnalysisResponse, AnnualForecastRequest, ChatRequest,
    DateConversionRequest,
)
from astrology_engine import get_can_chi_from_year, get_ngu_hanh, get_personality_traits, get_energy_role
from compatibility_engine import analyze_family, get_family_annual_forecast
from ai_layer import get_ai_interpretation, get_ai_family_chat, has_openai_key
from lunar_calendar import solar_to_lunar, lunar_to_solar
from data_sources import all_sources

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
    """Add lunar/solar columns to family_members if they're missing.

    SQLAlchemy's create_all() does not alter existing tables. For users
    upgrading from a previous version we issue ALTER TABLE statements
    for the columns introduced in this release. Safe to run repeatedly.

    All identifiers in the ALTER TABLE statements come from a fixed
    allow-list defined here (no user input), and are additionally
    validated against an identifier regex before interpolation, to
    satisfy linters that flag any string-built SQL.
    """
    import re
    new_columns = [
        ("birth_calendar", "VARCHAR(10) DEFAULT 'solar'"),
        ("solar_year", "INTEGER"),
        ("solar_month", "INTEGER"),
        ("solar_day", "INTEGER"),
        ("lunar_year", "INTEGER"),
        ("lunar_month", "INTEGER"),
        ("lunar_day", "INTEGER"),
        ("is_leap_month", "INTEGER DEFAULT 0"),
    ]
    allowed_type_pattern = re.compile(r"^[A-Z]+(\([0-9]+\))?( DEFAULT '?[A-Za-z0-9 ]+'?)?$")
    ident_pattern = re.compile(r"^[a-z_][a-z0-9_]*$")
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    if "family_members" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("family_members")}
    with engine.begin() as conn:
        for name, col_type in new_columns:
            if not ident_pattern.match(name) or not allowed_type_pattern.match(col_type):
                # Defensive guard - constants above already pass, but
                # this prevents accidental future expansion with unsafe values.
                continue
            if name not in existing:
                try:
                    conn.execute(text(f"ALTER TABLE family_members ADD COLUMN {name} {col_type}"))
                except Exception as e:
                    # Non-fatal: log to stderr and continue.
                    print(f"[migration] could not add column {name}: {e}")


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
        "birth_year": member.birth_year,
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


# ============ Family Endpoints ============

@app.get("/")
def root():
    return {"message": "Tử Vi Gia Đình API", "version": "1.0.0"}


@app.get("/api/families", response_model=list[FamilyResponse])
def get_families(db: Session = Depends(get_db)):
    """Get all families"""
    families = db.query(Family).all()
    return families


@app.post("/api/families", response_model=FamilyResponse)
def create_family(family: FamilyCreate, db: Session = Depends(get_db)):
    """Create a new family"""
    db_family = Family(name=family.name, description=family.description)
    db.add(db_family)
    db.commit()
    db.refresh(db_family)
    return db_family


@app.get("/api/families/{family_id}", response_model=FamilyResponse)
def get_family(family_id: int, db: Session = Depends(get_db)):
    """Get a specific family with all members"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    return family


@app.delete("/api/families/{family_id}")
def delete_family(family_id: int, db: Session = Depends(get_db)):
    """Delete a family"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")
    db.delete(family)
    db.commit()
    return {"message": "Đã xóa gia đình"}


# ============ Family Member Endpoints ============

@app.post("/api/families/{family_id}/members", response_model=FamilyMemberResponse)
def add_family_member(
    family_id: int,
    member: FamilyMemberCreate,
    db: Session = Depends(get_db)
):
    """Add a member to a family.

    Accepts either solar or lunar birth date via `birth_calendar`.
    The system stores both calendar representations and uses the lunar
    year (which the sexagenary cycle is based on) to compute Can Chi.
    """
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")

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


@app.delete("/api/families/{family_id}/members/{member_id}")
def delete_member(family_id: int, member_id: int, db: Session = Depends(get_db)):
    """Delete a family member"""
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
async def get_family_analysis(family_id: int, db: Session = Depends(get_db)):
    """Get comprehensive family compatibility analysis"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")

    if len(family.members) < 2:
        raise HTTPException(
            status_code=400,
            detail="Cần ít nhất 2 thành viên để phân tích tương hợp"
        )

    members_data = [member_to_dict(m) for m in family.members]

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

    return {
        "family_name": family.name,
        "members_count": len(family.members),
        **analysis
    }


@app.post("/api/families/{family_id}/forecast")
def get_annual_forecast(
    family_id: int,
    request: AnnualForecastRequest,
    db: Session = Depends(get_db)
):
    """Get annual forecast for the family"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")

    members_data = [member_to_dict(m) for m in family.members]
    forecast = get_family_annual_forecast(members_data, request.year)

    return forecast


@app.post("/api/families/{family_id}/chat")
async def family_chat(
    family_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """AI Family Advisor chat"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")

    members_data = [member_to_dict(m) for m in family.members]

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
