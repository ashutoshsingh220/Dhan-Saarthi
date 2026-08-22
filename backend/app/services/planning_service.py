from datetime import date, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.planning import FinancialGoal, FinancialPlan, FinancialPlanMilestone
from app.models.user import User


def add_months(orig_date: date, months: int) -> date:
    new_year = orig_date.year + (orig_date.month + months - 1) // 12
    new_month = (orig_date.month + months - 1) % 12 + 1
    new_day = min(orig_date.day, [31, 29 if new_year % 4 == 0 and (new_year % 100 != 0 or new_year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][new_month - 1])
    return date(new_year, new_month, new_day)


class PlanningService:
    def create_goal(
        self, db: Session, user: User, name: str, category: str, target_amount: float, current_amount: float, target_date: date
    ) -> FinancialGoal:
        today = date.today()
        if target_date <= today:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target date must be in the future")
        if current_amount > target_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current saved amount cannot exceed target amount")

        goal = FinancialGoal(
            user_id=user.id,
            name=name.strip(),
            category=category,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            status="completed" if current_amount >= target_amount else "active",
        )
        db.add(goal)
        db.flush()

        self.recalculate_plan(db=db, user=user, goal=goal)
        db.commit()
        db.refresh(goal)
        return goal

    def recalculate_plan(self, db: Session, user: User, goal: FinancialGoal) -> FinancialPlan:
        today = date.today()
        target_amount = float(goal.target_amount)
        current_amount = float(goal.current_amount)
        remaining_amount = max(0.0, target_amount - current_amount)

        # Calculate remaining months
        if goal.target_date <= today:
            remaining_months = 1
        else:
            remaining_months = max(1, (goal.target_date.year - today.year) * 12 + (goal.target_date.month - today.month))

        monthly_required = round(remaining_amount / remaining_months, 2)

        # Available Monthly Capacity from profile
        profile = user.profile
        if profile and profile.monthly_income and profile.monthly_expenses:
            available_capacity = max(0.0, float(profile.monthly_income) - float(profile.monthly_expenses))
        else:
            available_capacity = 0.0

        # Feasibility ratio & percentage
        if monthly_required <= 0:
            feasibility_ratio = 1.0
            feasibility_percentage = 100.0
            feasibility_status = "FEASIBLE"
        elif available_capacity <= 0:
            feasibility_ratio = 0.0
            feasibility_percentage = 0.0
            feasibility_status = "AT_RISK"
        else:
            feasibility_ratio = available_capacity / monthly_required
            feasibility_percentage = round(min(999.99, feasibility_ratio * 100.0), 2)

            if feasibility_ratio >= 1.0:
                feasibility_status = "FEASIBLE"
            elif feasibility_ratio >= 0.75:
                feasibility_status = "TIGHT"
            else:
                feasibility_status = "AT_RISK"

        # Recommended monthly contribution
        if available_capacity > 0:
            recommended_monthly = min(available_capacity, monthly_required)
        else:
            recommended_monthly = monthly_required

        # Estimated completion date
        if available_capacity > 0 and monthly_required > available_capacity and remaining_amount > 0:
            months_needed = int(remaining_amount / available_capacity) + (1 if remaining_amount % available_capacity > 0 else 0)
            estimated_completion_date = add_months(today, months_needed)
        else:
            estimated_completion_date = goal.target_date

        # Recommendation text
        if feasibility_status == "FEASIBLE":
            rec_text = f"Your current monthly surplus of ₹{available_capacity:,.2f} is sufficient to meet the required ₹{monthly_required:,.2f}/month."
        elif feasibility_status == "TIGHT":
            rec_text = f"Your goal requires ₹{monthly_required:,.2f}/month, utilizing most of your ₹{available_capacity:,.2f}/month surplus. Keep expenses steady."
        else:
            if available_capacity > 0:
                diff = monthly_required - available_capacity
                rec_text = f"Required contribution (₹{monthly_required:,.2f}/month) exceeds your surplus (₹{available_capacity:,.2f}/month) by ₹{diff:,.2f}. Consider extending your target date."
            else:
                rec_text = f"Required contribution is ₹{monthly_required:,.2f}/month. Update your profile surplus to assess capacity accurately."

        # Fetch or create plan
        plan = goal.plan
        if plan is None:
            plan = FinancialPlan(
                goal_id=goal.id,
                monthly_required=monthly_required,
                recommended_monthly_contribution=recommended_monthly,
                available_monthly_capacity=available_capacity,
                feasibility_status=feasibility_status,
                feasibility_percentage=feasibility_percentage,
                estimated_completion_date=estimated_completion_date,
                recommendation_text=rec_text,
            )
            db.add(plan)
            db.flush()
        else:
            plan.monthly_required = monthly_required
            plan.recommended_monthly_contribution = recommended_monthly
            plan.available_monthly_capacity = available_capacity
            plan.feasibility_status = feasibility_status
            plan.feasibility_percentage = feasibility_percentage
            plan.estimated_completion_date = estimated_completion_date
            plan.recommendation_text = rec_text
            plan.updated_at = datetime.now()

        # Generate or update milestones (4 checkpoints)
        db.query(FinancialPlanMilestone).filter(FinancialPlanMilestone.plan_id == plan.id).delete()

        checkpoints = [
            ("25% Saved", 0.25, 1),
            ("50% Halfway Mark", 0.50, 2),
            ("75% Final Stretch", 0.75, 3),
            ("100% Goal Achieved", 1.00, 4),
        ]

        for title, ratio, step in checkpoints:
            m_target = round(target_amount * ratio, 2)
            m_months = max(1, int(remaining_months * ratio))
            m_date = add_months(today, m_months) if goal.target_date > today else goal.target_date
            if m_date > goal.target_date:
                m_date = goal.target_date

            is_done = current_amount >= m_target
            milestone = FinancialPlanMilestone(
                plan_id=plan.id,
                title=f"Checkpoint {step}: {title}",
                milestone_date=m_date,
                target_amount=m_target,
                status="completed" if is_done else "pending",
                completed_at=datetime.now() if is_done else None,
            )
            db.add(milestone)

        return plan

    def record_progress(self, db: Session, user: User, goal_uuid: str, contribution_amount: float) -> FinancialGoal:
        if contribution_amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contribution amount must be positive")

        goal = db.scalar(select(FinancialGoal).where(FinancialGoal.goal_uuid == goal_uuid))
        if goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial goal not found")
        if goal.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this financial goal is denied")

        new_current = float(goal.current_amount) + contribution_amount
        goal.current_amount = min(float(goal.target_amount), new_current)
        if goal.current_amount >= float(goal.target_amount):
            goal.status = "completed"

        self.recalculate_plan(db=db, user=user, goal=goal)
        db.commit()
        db.refresh(goal)
        return goal

    def get_user_goals(self, db: Session, user: User) -> list[FinancialGoal]:
        return db.scalars(
            select(FinancialGoal)
            .where(FinancialGoal.user_id == user.id)
            .order_by(FinancialGoal.created_at.desc())
        ).all()

    def get_goal_by_uuid(self, db: Session, user: User, goal_uuid: str) -> FinancialGoal:
        goal = db.scalar(select(FinancialGoal).where(FinancialGoal.goal_uuid == goal_uuid))
        if goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial goal not found")
        if goal.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this financial goal is denied")
        return goal
