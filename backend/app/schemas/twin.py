from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FinancialTwinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    financial_health_score: int
    risk_level: str
    financial_summary: str
    last_updated: datetime
