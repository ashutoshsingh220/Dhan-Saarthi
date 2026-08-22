import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(50), default="other")  # emergency_fund, education, travel, home, vehicle, investment, other
    target_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    current_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0)
    target_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, completed, paused
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="goals")
    plan: Mapped["FinancialPlan | None"] = relationship(
        back_populates="goal", uselist=False, cascade="all, delete-orphan"
    )


class FinancialPlan(Base):
    __tablename__ = "financial_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("financial_goals.id"), unique=True, index=True)
    monthly_required: Mapped[float] = mapped_column(Numeric(14, 2))
    recommended_monthly_contribution: Mapped[float] = mapped_column(Numeric(14, 2))
    available_monthly_capacity: Mapped[float] = mapped_column(Numeric(14, 2))
    feasibility_status: Mapped[str] = mapped_column(String(20))  # FEASIBLE, TIGHT, AT_RISK
    feasibility_percentage: Mapped[float] = mapped_column(Numeric(6, 2))
    estimated_completion_date: Mapped[date] = mapped_column(Date)
    recommendation_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    goal: Mapped[FinancialGoal] = relationship(back_populates="plan")
    milestones: Mapped[list["FinancialPlanMilestone"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="FinancialPlanMilestone.milestone_date"
    )


class FinancialPlanMilestone(Base):
    __tablename__ = "financial_plan_milestones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("financial_plans.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    milestone_date: Mapped[date] = mapped_column(Date)
    target_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, completed
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    plan: Mapped[FinancialPlan] = relationship(back_populates="milestones")
