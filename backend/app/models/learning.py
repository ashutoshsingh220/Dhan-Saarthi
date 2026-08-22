import json
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))  # Basics, Budgeting, Credit, Safety, Investing, Goals
    difficulty: Mapped[str] = mapped_column(String(20), default="Beginner")  # Beginner, Intermediate, Advanced
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=5)
    lesson_content_json: Mapped[str] = mapped_column(Text)  # JSON structure of sections, concepts, takeaways
    quiz_questions_json: Mapped[str] = mapped_column(Text)  # JSON structure of 3 Qs (id, question, options, correct_option_index)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def lesson_content(self) -> dict:
        try:
            return json.loads(self.lesson_content_json)
        except Exception:
            return {}

    @lesson_content.setter
    def lesson_content(self, value: dict) -> None:
        self.lesson_content_json = json.dumps(value)

    @property
    def quiz_questions(self) -> list[dict]:
        try:
            return json.loads(self.quiz_questions_json)
        except Exception:
            return []

    @quiz_questions.setter
    def quiz_questions(self, value: list[dict]) -> None:
        self.quiz_questions_json = json.dumps(value)


class UserLearningProgress(Base):
    __tablename__ = "user_learning_progress"
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uq_user_module_progress"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    module_id: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(20), default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    quiz_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # Percentage, e.g. 100.0
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="learning_progress")
