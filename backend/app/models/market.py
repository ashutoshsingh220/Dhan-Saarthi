import uuid
from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def generate_uuid_str() -> str:
    return str(uuid.uuid4())

class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=generate_uuid_str)
    source: Mapped[str] = mapped_column(String(50), default="YAHOO_FINANCE")
    freshness: Mapped[str] = mapped_column(String(20), default="LIVE")  # LIVE, CACHED, STALE, UNAVAILABLE
    market_pulse: Mapped[str] = mapped_column(String(20), default="MIXED")  # POSITIVE, NEGATIVE, MIXED, CALM, UNAVAILABLE
    pulse_summary: Mapped[str] = mapped_column(Text)
    assets_json: Mapped[str] = mapped_column(Text)  # JSON representation of all tracked assets
    insights_json: Mapped[str] = mapped_column(Text)  # JSON array of observations
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
