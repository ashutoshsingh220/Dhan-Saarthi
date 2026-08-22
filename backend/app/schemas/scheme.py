from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

# Category constants
SCHEME_CATEGORIES = [
    "FARMER_SUPPORT",
    "AGRICULTURE_LOAN",
    "CROP_INSURANCE",
    "AGRICULTURAL_INFRASTRUCTURE",
    "FARM_EQUIPMENT",
    "IRRIGATION",
    "DAIRY_AND_LIVESTOCK",
    "FISHERIES",
    "RURAL_ENTERPRISE",
    "SMALL_BUSINESS",
    "MICRO_ENTERPRISE",
    "SELF_EMPLOYMENT",
    "ENTREPRENEURSHIP",
    "WOMEN_ENTREPRENEURSHIP",
    "SKILL_AND_BUSINESS_SUPPORT",
]

class GovernmentSchemePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scheme_id: str
    name: str
    short_name: str
    category: str
    tags: list[str] = Field(default_factory=list)

    target_groups: str
    description: str
    benefits_summary: str
    benefit_type: str
    official_authority: str
    official_url: str
    application_url: Optional[str] = None
    status: str
    geographic_scope: str
    states_supported: list[str] = Field(default_factory=list)
    eligibility_rules: dict = Field(default_factory=dict)
    required_documents: list[str] = Field(default_factory=list)
    how_to_apply: list[str] = Field(default_factory=list)
    important_notes: Optional[str] = None
    source_last_verified_at: str

class SchemeCategoryCount(BaseModel):
    category_id: str
    category_name: str
    count: int

class SchemeEligibilityResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    relevance_status: Literal["HIGHLY_RELEVANT", "RELEVANT", "EXPLORE", "NEEDS_MORE_INFORMATION"]
    eligibility_status: Literal["LIKELY_RELEVANT", "POTENTIALLY_ELIGIBLE", "NEEDS_MORE_INFORMATION", "NOT_CURRENTLY_MATCHED"]
    relevance_score: int
    match_reasons: list[str]
    missing_information: list[str]
    disclaimer: str
    official_url: str

class SchemeRecommendationResponse(BaseModel):
    scheme: GovernmentSchemePublic
    relevance_rank: Literal["HIGHLY_RELEVANT", "RELEVANT", "EXPLORE", "NEEDS_MORE_INFORMATION"]
    relevance_score: int
    why_recommended: str
    what_to_verify_next: list[str]
    official_source_url: str

class SupportContextUpdateRequest(BaseModel):
    state: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    rural_or_urban: Optional[str] = Field(default=None, pattern="^(RURAL|URBAN|SEMI_URBAN)$")
    farming_interest: Optional[bool] = Field(default=None)
    business_interest: Optional[bool] = Field(default=None)
    farm_activity: Optional[str] = Field(default=None, max_length=50)
    business_stage: Optional[str] = Field(default=None, max_length=30)
    business_sector: Optional[str] = Field(default=None, max_length=50)
    business_registration_status: Optional[str] = Field(default=None, max_length=30)

class SupportContextResponse(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    rural_or_urban: Optional[str] = None
    farming_interest: bool = False
    business_interest: bool = False
    farm_activity: Optional[str] = None
    business_stage: Optional[str] = None
    business_sector: Optional[str] = None
    business_registration_status: Optional[str] = None
