from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GoalCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="other", pattern="^(emergency_fund|education|travel|home|vehicle|investment|other)$")
    target_amount: float = Field(gt=0, description="Target amount must be positive")
    current_amount: float = Field(default=0.0, ge=0, description="Current saved amount cannot be negative")
    target_date: date


class GoalUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, pattern="^(emergency_fund|education|travel|home|vehicle|investment|other)$")
    target_amount: float | None = Field(default=None, gt=0)
    target_date: date | None = Field(default=None)


class ProgressUpdateRequest(BaseModel):
    amount: float = Field(gt=0, description="Progress contribution amount must be positive")


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    milestone_date: date
    target_amount: float
    status: str
    completed_at: datetime | None = None


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    monthly_required: float
    recommended_monthly_contribution: float
    available_monthly_capacity: float
    feasibility_status: str
    feasibility_percentage: float
    estimated_completion_date: date
    recommendation_text: str
    milestones: list[MilestoneResponse] = []


class GoalDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: str = Field(validation_alias="goal_uuid", serialization_alias="id")
    name: str
    category: str
    target_amount: float
    current_amount: float
    target_date: date
    status: str
    created_at: datetime
    updated_at: datetime
    plan: PlanResponse | None = None
