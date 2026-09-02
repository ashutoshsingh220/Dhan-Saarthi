import json
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ScamScan(Base):
    __tablename__ = "scam_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    input_text: Mapped[str] = mapped_column(Text)
    input_type: Mapped[str] = mapped_column(String(20), default="text") # text or image
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer)  # 0 to 100
    risk_level: Mapped[str] = mapped_column(String(30))  # LOW, MODERATE, HIGH, CRITICAL
    summary: Mapped[str] = mapped_column(Text)
    recommended_actions_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON string array
    retrieved_evidence_json: Mapped[str] = mapped_column(Text, default="[]") # JSON string array of RAG evidence
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="scam_scans")
    indicators: Mapped[list["ScamIndicator"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan", order_by="ScamIndicator.id"
    )

    @property
    def recommended_actions(self) -> list[str]:
        try:
            return json.loads(self.recommended_actions_json)
        except Exception:
            return []

    @recommended_actions.setter
    def recommended_actions(self, value: list[str]) -> None:
        self.recommended_actions_json = json.dumps(value)
        
    @property
    def retrieved_evidence(self) -> list[dict]:
        try:
            return json.loads(self.retrieved_evidence_json)
        except Exception:
            return []

    @retrieved_evidence.setter
    def retrieved_evidence(self, value: list[dict]) -> None:
        self.retrieved_evidence_json = json.dumps(value)


class ScamIndicator(Base):
    __tablename__ = "scam_indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scam_scans.id", ondelete="CASCADE"), index=True)
    indicator_type: Mapped[str] = mapped_column(String(50))  # URGENCY_PRESSURE, FINANCIAL_THREAT, SENSITIVE_INFO_REQUEST, etc.
    matched_text: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(30))  # low, medium, high, critical
    points: Mapped[int] = mapped_column(Integer)

    scan: Mapped[ScamScan] = relationship(back_populates="indicators")
