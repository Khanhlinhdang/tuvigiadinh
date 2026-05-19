"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FamilyMemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., description="chồng/vợ/con/cha/mẹ/anh/chị/em")
    gender: str = Field(..., description="nam/nữ")
    birth_year: int = Field(..., ge=1900, le=2050)
    birth_month: Optional[int] = Field(None, ge=1, le=12)
    birth_day: Optional[int] = Field(None, ge=1, le=31)
    birth_hour: Optional[str] = None


class FamilyMemberResponse(BaseModel):
    id: int
    family_id: int
    name: str
    role: str
    gender: str
    birth_year: int
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: Optional[str] = None
    thien_can: Optional[str] = None
    dia_chi: Optional[str] = None
    ngu_hanh: Optional[str] = None
    nap_am: Optional[str] = None
    energy_role: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class FamilyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    members: List[FamilyMemberResponse] = []

    class Config:
        from_attributes = True


class CompatibilityRequest(BaseModel):
    member1_id: int
    member2_id: int
    family_id: int


class PairCompatibility(BaseModel):
    member1_name: str
    member2_name: str
    member1_role: str
    member2_role: str
    member1_can_chi: str
    member2_can_chi: str
    can_compatibility: dict
    chi_compatibility: dict
    hanh_compatibility: dict
    overall_score: int
    compatibility_level: str
    summary: str
    recommendations: List[str]


class FamilyAnalysisResponse(BaseModel):
    family_name: str
    members_count: int
    pairs_analysis: List[PairCompatibility]
    family_overall_score: int
    family_dynamics: str
    ai_interpretation: Optional[str] = None
    annual_forecast: Optional[dict] = None


class AnnualForecastRequest(BaseModel):
    family_id: int
    year: int = Field(..., ge=2020, le=2050)


class ChatRequest(BaseModel):
    family_id: int
    question: str = Field(..., min_length=1, max_length=1000)
