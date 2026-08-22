import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

def generate_uuid_str() -> str:
    return str(uuid.uuid4())

class FinancialRecommendationSnapshot(Base):
    __tablename__ = "financial_recommendation_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=generate_uuid_str)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    data_completeness: Mapped[str] = mapped_column(String(20), default="PARTIAL")  # COMPLETE, PARTIAL, INSUFFICIENT
    recommendation_status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    top_priority_title: Mapped[str] = mapped_column(String(150))
    top_priority_category: Mapped[str] = mapped_column(String(50))
    emergency_buffer_status: Mapped[str] = mapped_column(String(30))  # CRITICAL_BUFFER, LOW_BUFFER, MODERATE_BUFFER, STRONG_BUFFER, INSUFFICIENT_DATA

    priorities_json: Mapped[str] = mapped_column(Text)  # JSON list of priority items
    allocation_guidance_json: Mapped[str] = mapped_column(Text)  # JSON list of allocation ranges
    goal_considerations_json: Mapped[str] = mapped_column(Text)  # JSON list of goal insights
    market_context_json: Mapped[str] = mapped_column(Text)  # JSON object of market context
    disclaimer_version: Mapped[str] = mapped_column(String(50), default="v1.0")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="recommendation_snapshots")
