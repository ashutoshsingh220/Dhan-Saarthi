from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

CompletenessType = Literal["COMPLETE", "PARTIAL", "INSUFFICIENT"]
BufferStatusType = Literal["CRITICAL_BUFFER", "LOW_BUFFER", "MODERATE_BUFFER", "STRONG_BUFFER", "INSUFFICIENT_DATA"]
PriorityLevelType = Literal["HIGH", "MEDIUM", "LOW"]

class PriorityItem(BaseModel):
    title: str
    category: str
    priority_level: PriorityLevelType
    reason: str
    action_guidance: str
    data_basis: list[str] = Field(default_factory=list)

class AllocationGuidanceItem(BaseModel):
    category: str
    suggested_range_min: float
    suggested_range_max: float
    reason: str

class GoalConsiderationItem(BaseModel):
    goal_id: str
    goal_name: str
    feasibility_status: str
    monthly_required: float
    guidance_note: str

class EmergencyBufferAnalysis(BaseModel):
    monthly_expenses: float
    current_savings: float
    coverage_months: float
    status: BufferStatusType
    target_recommended_savings: float
    explanation: str

class MonthlyCapacitySchema(BaseModel):
    income: float
    expenses: float
    surplus: float
    unallocated_flexibility: float

class MarketContextSummarySchema(BaseModel):
    pulse: str
    freshness: str
    source: str
    warning_note: str

class RiskProfileSummarySchema(BaseModel):
    preference: str
    guidance_note: str

class PersonalizedRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: str
    generated_at: str
    data_completeness: CompletenessType
    data_completeness_note: str
    recommendation_status: str = "ACTIVE"
    monthly_capacity: MonthlyCapacitySchema
    top_priority: PriorityItem
    financial_priorities: list[PriorityItem] = Field(default_factory=list)
    emergency_buffer_analysis: EmergencyBufferAnalysis
    allocation_guidance: list[AllocationGuidanceItem] = Field(default_factory=list)
    goal_considerations: list[GoalConsiderationItem] = Field(default_factory=list)
    market_context_summary: MarketContextSummarySchema
    risk_profile: RiskProfileSummarySchema
    educational_notes: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "These recommendations are generated deterministically based on recorded financial data and market context "
        "for education and planning support. Past performance does not guarantee future returns. "
        "Dhan Saarthi does not execute trades or guarantee financial returns."
    )
