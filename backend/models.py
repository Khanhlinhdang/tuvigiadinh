"""
Database models for Tử Vi Gia Đình
"""
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Google subject identifier (sub claim). Unique per Google account.
    google_sub = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(200), index=True, nullable=False)
    name = Column(String(200), nullable=True)
    picture = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, default=datetime.utcnow)

    families = relationship("Family", back_populates="owner", cascade="all, delete-orphan")


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="families")
    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")
    saved_analyses = relationship(
        "SavedAnalysis", back_populates="family", cascade="all, delete-orphan"
    )


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # chồng, vợ, con, cha, mẹ, anh, chị, em
    gender = Column(String(10), nullable=False)  # nam, nữ
    occupation = Column(String(200), nullable=True)  # Nghề nghiệp / lĩnh vực
    birth_year = Column(Integer, nullable=False)
    birth_month = Column(Integer, nullable=True)
    birth_day = Column(Integer, nullable=True)
    birth_hour = Column(String(10), nullable=True)  # Giờ sinh (chi)

    # Birth calendar: "solar" (dương lịch) or "lunar" (âm lịch).
    # The raw birth_year/month/day above are stored in the user's chosen
    # calendar. The corresponding date in the other calendar is computed
    # automatically and persisted in the columns below.
    birth_calendar = Column(String(10), nullable=True, default="solar")
    solar_year = Column(Integer, nullable=True)
    solar_month = Column(Integer, nullable=True)
    solar_day = Column(Integer, nullable=True)
    lunar_year = Column(Integer, nullable=True)
    lunar_month = Column(Integer, nullable=True)
    lunar_day = Column(Integer, nullable=True)
    is_leap_month = Column(Integer, nullable=True, default=0)  # 0/1 flag

    # Computed fields
    thien_can = Column(String(10), nullable=True)
    dia_chi = Column(String(10), nullable=True)
    ngu_hanh = Column(String(10), nullable=True)
    nap_am = Column(String(100), nullable=True)
    energy_role = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("Family", back_populates="members")


class SavedAnalysis(Base):
    """Persist a snapshot of an analysis run so users can revisit it."""
    __tablename__ = "saved_analyses"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(300), nullable=True)
    note = Column(Text, nullable=True)
    # Snapshot of the full analysis payload (JSON)
    payload = Column(Text, nullable=False)  # store JSON string for portability
    family_overall_score = Column(Integer, nullable=True)
    analysis_mode = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("Family", back_populates="saved_analyses")
