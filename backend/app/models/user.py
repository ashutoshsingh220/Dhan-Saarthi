from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    preferred_language: Mapped[str] = mapped_column(String(30), default="English")
    accessibility_mode: Mapped[str] = mapped_column(String(30), default="standard")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile: Mapped["UserProfile | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    financial_twin: Mapped["FinancialTwin | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[list["FinancialGoal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    scam_scans: Mapped[list["ScamScan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    learning_progress: Mapped[list["UserLearningProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occupation: Mapped[str] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    monthly_income: Mapped[float] = mapped_column(Numeric(14, 2))
    monthly_expenses: Mapped[float] = mapped_column(Numeric(14, 2))
    savings: Mapped[float] = mapped_column(Numeric(14, 2))
    financial_goal: Mapped[str] = mapped_column(String(255))
    risk_preference: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- PROMPT 8: Extended personalization profile fields (all nullable for backward compatibility) ---
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    financial_knowledge_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    preferred_explanation_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    occupation_status: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # --- PROMPT 9: Government Scheme Support Context fields (all nullable for backward compatibility) ---
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rural_or_urban: Mapped[str | None] = mapped_column(String(20), nullable=True)
    farming_interest: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    business_interest: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    farm_activity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    business_stage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    business_sector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    business_registration_status: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # --- PROMPT 13: Accessibility Mode Preference fields (all nullable for backward compatibility) ---
    accessibility_mode_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    accessibility_profile: Mapped[str | None] = mapped_column(String(30), nullable=True, default="STANDARD")
    text_size_preference: Mapped[str | None] = mapped_column(String(20), nullable=True, default="STANDARD")
    high_contrast_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    reduce_motion_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    simplified_interface_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    voice_navigation_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    auto_speak_important_results: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    sequential_navigation_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)

    user: Mapped[User] = relationship(back_populates="profile")



class FinancialTwin(Base):
    __tablename__ = "financial_twins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    financial_health_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(30))
    financial_summary: Mapped[str] = mapped_column(Text)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="financial_twin")

