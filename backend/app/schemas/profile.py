from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.personalization_service import (
    EDUCATION_LEVELS,
    EXPLANATION_LEVELS,
    FINANCIAL_KNOWLEDGE_LEVELS,
    OCCUPATION_STATUSES,
    calculate_age,
)

ACCESSIBILITY_PROFILES = {"STANDARD", "VISUAL_ASSIST", "VOICE_ASSIST", "LOW_LITERACY", "ELDERLY_FRIENDLY"}
TEXT_SIZE_PREFERENCES = {"SMALL", "STANDARD", "LARGE", "EXTRA_LARGE"}

_TODAY = date.today  # callable so tests can monkey-patch if needed


class ProfileUpsertRequest(BaseModel):
    # --- existing fields ---
    age: int = Field(ge=1, le=120)
    gender: str | None = Field(default=None, max_length=50)
    occupation: str = Field(min_length=2, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    monthly_income: Decimal = Field(ge=0)
    monthly_expenses: Decimal = Field(ge=0)
    savings: Decimal = Field(default=Decimal(0), ge=0)
    total_savings: Optional[Decimal] = Field(default=Decimal(0), ge=0)
    monthly_savings: Optional[Decimal] = Field(default=Decimal(0), ge=0)
    financial_goal: str = Field(min_length=2, max_length=255)
    risk_preference: str = Field(pattern="^(low|moderate|high)$")
    preferred_language: str = Field(default="English", max_length=30)
    accessibility_mode: str = Field(default="standard", pattern="^(standard|voice_first)$")


    # --- PROMPT 8: personalization fields (all optional for backward compatibility) ---
    date_of_birth: Optional[date] = Field(default=None)
    education_level: Optional[str] = Field(default=None, max_length=50)
    financial_knowledge_level: Optional[str] = Field(default=None, max_length=30)
    preferred_explanation_level: Optional[str] = Field(default=None, max_length=20)
    occupation_status: Optional[str] = Field(default=None, max_length=30)

    # --- PROMPT 13: accessibility fields (all optional for backward compatibility) ---
    accessibility_mode_enabled: Optional[bool] = Field(default=None)
    accessibility_profile: Optional[str] = Field(default=None, max_length=30)
    text_size_preference: Optional[str] = Field(default=None, max_length=20)
    high_contrast_enabled: Optional[bool] = Field(default=None)
    reduce_motion_enabled: Optional[bool] = Field(default=None)
    simplified_interface_enabled: Optional[bool] = Field(default=None)
    voice_navigation_enabled: Optional[bool] = Field(default=None)
    auto_speak_important_results: Optional[bool] = Field(default=None)
    sequential_navigation_enabled: Optional[bool] = Field(default=None)

    @field_validator("date_of_birth")
    @classmethod
    def dob_must_not_be_future(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        today = _TODAY()
        if v > today:
            raise ValueError("date_of_birth cannot be in the future")
        age = calculate_age(v, today)
        if age > 120:
            raise ValueError("date_of_birth results in an implausible age (>120 years)")
        return v

    @field_validator("education_level")
    @classmethod
    def education_level_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in EDUCATION_LEVELS:
            raise ValueError(f"education_level must be one of: {sorted(EDUCATION_LEVELS)}")
        return v

    @field_validator("financial_knowledge_level")
    @classmethod
    def financial_knowledge_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in FINANCIAL_KNOWLEDGE_LEVELS:
            raise ValueError(f"financial_knowledge_level must be one of: {sorted(FINANCIAL_KNOWLEDGE_LEVELS)}")
        return v

    @field_validator("preferred_explanation_level")
    @classmethod
    def explanation_level_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in EXPLANATION_LEVELS:
            raise ValueError(f"preferred_explanation_level must be one of: {sorted(EXPLANATION_LEVELS)}")
        return v

    @field_validator("occupation_status")
    @classmethod
    def occupation_status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in OCCUPATION_STATUSES:
            raise ValueError(f"occupation_status must be one of: {sorted(OCCUPATION_STATUSES)}")
        return v

    @field_validator("accessibility_profile")
    @classmethod
    def accessibility_profile_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ACCESSIBILITY_PROFILES:
            raise ValueError(f"accessibility_profile must be one of: {sorted(ACCESSIBILITY_PROFILES)}")
        return v

    @field_validator("text_size_preference")
    @classmethod
    def text_size_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TEXT_SIZE_PREFERENCES:
            raise ValueError(f"text_size_preference must be one of: {sorted(TEXT_SIZE_PREFERENCES)}")
        return v


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # existing fields
    id: int
    user_id: int
    age: int
    gender: Optional[str] = None
    occupation: str
    city: Optional[str] = None
    monthly_income: Decimal
    monthly_expenses: Decimal
    savings: Decimal
    total_savings: Optional[Decimal] = Decimal(0)
    monthly_savings: Optional[Decimal] = Decimal(0)
    financial_goal: str

    risk_preference: str
    preferred_language: str
    accessibility_mode: str
    created_at: datetime
    updated_at: datetime

    # PROMPT 8 personalization fields
    date_of_birth: Optional[date] = None
    education_level: Optional[str] = None
    financial_knowledge_level: Optional[str] = None
    preferred_explanation_level: Optional[str] = None
    occupation_status: Optional[str] = None

    # PROMPT 9 support context fields
    state: Optional[str] = None
    district: Optional[str] = None
    rural_or_urban: Optional[str] = None
    farming_interest: Optional[bool] = False
    business_interest: Optional[bool] = False
    farm_activity: Optional[str] = None
    business_stage: Optional[str] = None
    business_sector: Optional[str] = None
    business_registration_status: Optional[str] = None

    # PROMPT 13 accessibility fields
    accessibility_mode_enabled: Optional[bool] = False
    accessibility_profile: Optional[str] = "STANDARD"
    text_size_preference: Optional[str] = "STANDARD"
    high_contrast_enabled: Optional[bool] = False
    reduce_motion_enabled: Optional[bool] = False
    simplified_interface_enabled: Optional[bool] = False
    voice_navigation_enabled: Optional[bool] = False
    auto_speak_important_results: Optional[bool] = False
    sequential_navigation_enabled: Optional[bool] = False

    # derived — populated by the API route, not stored in DB
    derived_age: Optional[int] = None



