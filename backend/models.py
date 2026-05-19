"""
Database models for Tử Vi Gia Đình
"""
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # chồng, vợ, con, cha, mẹ, anh, chị, em
    gender = Column(String(10), nullable=False)  # nam, nữ
    birth_year = Column(Integer, nullable=False)
    birth_month = Column(Integer, nullable=True)
    birth_day = Column(Integer, nullable=True)
    birth_hour = Column(String(10), nullable=True)  # Giờ sinh (chi)

    # Computed fields
    thien_can = Column(String(10), nullable=True)
    dia_chi = Column(String(10), nullable=True)
    ngu_hanh = Column(String(10), nullable=True)
    nap_am = Column(String(100), nullable=True)
    energy_role = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("Family", back_populates="members")
