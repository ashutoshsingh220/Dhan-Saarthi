import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def generate_uuid_str() -> str:
    return str(uuid.uuid4())

class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheme_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=generate_uuid_str)

    name: Mapped[str] = mapped_column(String(255), index=True)
    short_name: Mapped[str] = mapped_column(String(100))

    category: Mapped[str] = mapped_column(String(50), index=True)
    tags_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON string array

    target_groups: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    benefits_summary: Mapped[str] = mapped_column(Text)
    benefit_type: Mapped[str] = mapped_column(String(50))

    official_authority: Mapped[str] = mapped_column(String(255))
    official_url: Mapped[str] = mapped_column(String(500))
    application_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    geographic_scope: Mapped[str] = mapped_column(String(30), default="NATIONAL")
    states_supported_json: Mapped[str] = mapped_column(Text, default='["ALL"]')  # JSON string array

    eligibility_rules_json: Mapped[str] = mapped_column(Text, default="{}")  # JSON dict
    required_documents_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON string array
    how_to_apply_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON string array

    important_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_last_verified_at: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
