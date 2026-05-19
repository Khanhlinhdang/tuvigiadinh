"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class FamilyMemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., description="chồng/vợ/con/cha/mẹ/anh/chị/em")
    gender: str = Field(..., description="nam/nữ")
    occupation: Optional[str] = Field(None, max_length=200, description="Nghề nghiệp / lĩnh vực")
    birth_year: int = Field(..., ge=1900, le=2050)
    birth_month: Optional[int] = Field(None, ge=1, le=12)
    birth_day: Optional[int] = Field(None, ge=1, le=31)
    birth_hour: Optional[str] = None
    birth_calendar: Optional[str] = Field(
        "solar",
        description="Loại lịch của ngày sinh: 'solar' (dương) hoặc 'lunar' (âm)",
    )
    is_leap_month: Optional[bool] = Field(
        False, description="Tháng nhuận (chỉ dùng khi birth_calendar='lunar')"
    )


class FamilyMemberUpdate(BaseModel):
    """All fields optional - partial update."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = Field(None, max_length=200)
    birth_year: Optional[int] = Field(None, ge=1900, le=2050)
    birth_month: Optional[int] = Field(None, ge=1, le=12)
    birth_day: Optional[int] = Field(None, ge=1, le=31)
    birth_hour: Optional[str] = None
    birth_calendar: Optional[str] = None
    is_leap_month: Optional[bool] = None


class FamilyMemberResponse(BaseModel):
    id: int
    family_id: int
    name: str
    role: str
    gender: str
    occupation: Optional[str] = None
    birth_year: int
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: Optional[str] = None
    birth_calendar: Optional[str] = "solar"
    solar_year: Optional[int] = None
    solar_month: Optional[int] = None
    solar_day: Optional[int] = None
    lunar_year: Optional[int] = None
    lunar_month: Optional[int] = None
    lunar_day: Optional[int] = None
    is_leap_month: Optional[bool] = False
    thien_can: Optional[str] = None
    dia_chi: Optional[str] = None
    ngu_hanh: Optional[str] = None
    nap_am: Optional[str] = None
    energy_role: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DateConversionRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    calendar: str = Field("solar", description="'solar' hoặc 'lunar'")
    is_leap_month: bool = False


class FamilyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class FamilyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class FamilyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
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


# ============ Auth ============

class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., description="Google ID token (JWT) từ Google Identity Services")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Saved Analyses ============

class SavedAnalysisCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    note: Optional[str] = None


class SavedAnalysisSummary(BaseModel):
    id: int
    family_id: int
    title: Optional[str] = None
    note: Optional[str] = None
    family_overall_score: Optional[int] = None
    analysis_mode: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SavedAnalysisDetail(SavedAnalysisSummary):
    payload: Any  # decoded JSON

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
