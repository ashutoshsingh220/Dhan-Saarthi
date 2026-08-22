from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScamAnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=5, max_length=5000, description="Suspicious text to analyze")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 5:
            raise ValueError("Message must be at least 5 non-whitespace characters long.")
        return stripped


class ScamIndicatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    indicator_type: str
    matched_text: str
    severity: str
    points: int


class ScamScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: str = Field(validation_alias="scan_uuid", serialization_alias="id")
    input_text: str
    risk_score: int
    risk_level: str
    summary: str
    recommended_actions: list[str]
    indicators: list[ScamIndicatorResponse] = []
    created_at: datetime


class ScamHistoryResponse(BaseModel):
    scans: list[ScamScanResponse]
    total_count: int
