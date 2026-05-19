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
    FamilyAnalysisResponse, AnnualForecastRequest, ChatRequest
)
from astrology_engine import get_can_chi_from_year, get_ngu_hanh, get_personality_traits, get_energy_role
from compatibility_engine import analyze_family, get_family_annual_forecast
from ai_layer import get_ai_interpretation, get_ai_family_chat

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tuvigiadinh.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


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
    """Compute astrological data for a family member"""
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


def member_to_dict(member: FamilyMember) -> dict:
    """Convert FamilyMember model to dict for analysis"""
    return {
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "gender": member.gender,
        "birth_year": member.birth_year,
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
    """Add a member to a family"""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Không tìm thấy gia đình")

    # Compute astrological data
    astro = compute_member_astrology(member.birth_year)

    db_member = FamilyMember(
        family_id=family_id,
        name=member.name,
        role=member.role,
        gender=member.gender,
        birth_year=member.birth_year,
        birth_month=member.birth_month,
        birth_day=member.birth_day,
        birth_hour=member.birth_hour,
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

    # Get AI interpretation
    family_data = {
        "name": family.name,
        "members": members_data,
    }
    ai_interpretation = await get_ai_interpretation(family_data, analysis)
    analysis["ai_interpretation"] = ai_interpretation

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

    # Build analysis context
    analysis = analyze_family(members_data)
    analysis_context = f"Điểm tổng hợp gia đình: {analysis['family_overall_score']}/100. {analysis['family_dynamics']}"

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
