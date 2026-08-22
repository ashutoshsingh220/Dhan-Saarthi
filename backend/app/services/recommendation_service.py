import json
import logging
from datetime import datetime, timezone
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recommendation import FinancialRecommendationSnapshot
from app.models.user import User
from app.schemas.recommendation import (
    AllocationGuidanceItem,
    CompletenessType,
    EmergencyBufferAnalysis,
    GoalConsiderationItem,
    MarketContextSummarySchema,
    MonthlyCapacitySchema,
    PersonalizedRecommendationResponse,
    PriorityItem,
    RiskProfileSummarySchema,
)
from app.services.financial_priority_service import FinancialPriorityService
from app.services.market_service import MarketService

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Main Recommendation Service for Personalized Financial & Portfolio Guidance.
    100% Deterministic backend calculations — NO LLM calculation.
    """

    @staticmethod
    def generate_recommendations(db: Session, user: User) -> PersonalizedRecommendationResponse:
        now = datetime.now(timezone.utc)
        profile = user.profile
        twin = user.financial_twin
        goals = getattr(user, "goals", [])

        # 1. Determine Data Completeness
        data_completeness: CompletenessType = "COMPLETE"
        completeness_notes = []

        if not profile:
            data_completeness = "INSUFFICIENT"
            completeness_notes.append("Financial profile incomplete.")
        else:
            if not twin:
                data_completeness = "PARTIAL"
                completeness_notes.append("Financial Twin not generated yet.")
            if not goals:
                if data_completeness != "INSUFFICIENT":
                    data_completeness = "PARTIAL"
                completeness_notes.append("No active smart financial goals recorded.")
            completeness_notes.append("Debt and insurance details are not currently recorded in your profile.")

        completeness_str = " ".join(completeness_notes)

        # Cashflow metrics
        income = float(profile.monthly_income) if profile else 0.0
        expenses = float(profile.monthly_expenses) if profile else 0.0
        savings = float(profile.savings) if profile else 0.0
        surplus = max(0.0, income - expenses)

        # 2. Emergency Buffer Analysis
        buffer_analysis = FinancialPriorityService.analyze_emergency_buffer(savings, expenses)

        # 3. Classify Priorities
        priorities = FinancialPriorityService.classify_priorities(profile, buffer_analysis, goals, surplus)
        top_priority = priorities[0] if priorities else PriorityItem(
            title="Complete Financial Profile",
            category="EMERGENCY_BUFFER",
            priority_level="HIGH",
            reason="Complete your income and expenses to receive tailored guidance.",
            action_guidance="Fill out your profile questionnaire in the app.",
            data_basis=["profile"]
        )

        # 4. Deterministic Monthly Surplus Allocation Guidance (Ranges & Reserve)
        allocation_items = []
        total_allocated_max = 0.0

        if surplus > 0:
            # Emergency buffer range
            if buffer_analysis.status in ["CRITICAL_BUFFER", "LOW_BUFFER"]:
                e_min = round(surplus * 0.30, 2)
                e_max = round(surplus * 0.50, 2)
                allocation_items.append(AllocationGuidanceItem(
                    category="Emergency Buffer",
                    suggested_range_min=e_min,
                    suggested_range_max=e_max,
                    reason="Savings buffer is below 3 months of expenses."
                ))
                total_allocated_max += e_max
            elif buffer_analysis.status == "MODERATE_BUFFER":
                e_min = round(surplus * 0.15, 2)
                e_max = round(surplus * 0.30, 2)
                allocation_items.append(AllocationGuidanceItem(
                    category="Emergency Buffer",
                    suggested_range_min=e_min,
                    suggested_range_max=e_max,
                    reason="Building reserve toward 6 months of safety cushion."
                ))
                total_allocated_max += e_max

            # Goal contributions range
            active_plans = [g for g in goals if g.plan]
            total_req_monthly = sum(float(g.plan.monthly_required) for g in active_plans) if active_plans else 0.0

            if total_req_monthly > 0:
                g_min = round(min(surplus * 0.30, total_req_monthly * 0.8), 2)
                g_max = round(min(surplus * 0.50, total_req_monthly), 2)
                allocation_items.append(AllocationGuidanceItem(
                    category="Active Financial Goals",
                    suggested_range_min=g_min,
                    suggested_range_max=g_max,
                    reason="Contributions toward active smart planning goals."
                ))
                total_allocated_max += g_max

            # Long term savings / investment learning range
            if buffer_analysis.status in ["MODERATE_BUFFER", "STRONG_BUFFER"]:
                inv_min = round(surplus * 0.15, 2)
                inv_max = round(surplus * 0.35, 2)
                allocation_items.append(AllocationGuidanceItem(
                    category="Long-Term Wealth & Diversification",
                    suggested_range_min=inv_min,
                    suggested_range_max=inv_max,
                    reason="Diversified wealth building and asset category allocation."
                ))
                total_allocated_max += inv_max

        flexibility = max(0.0, round(surplus - total_allocated_max, 2))
        monthly_capacity = MonthlyCapacitySchema(
            income=income,
            expenses=expenses,
            surplus=surplus,
            unallocated_flexibility=flexibility
        )

        # 5. Goal Considerations
        goal_considerations = []
        for g in goals:
            plan = g.plan
            if plan:
                req = float(plan.monthly_required)
                feas = plan.feasibility_status
                if feas == "AT_RISK":
                    note = f"Required monthly ₹{req:,.2f} exceeds comfortable surplus capacity. Consider extending target date."
                elif feas == "TIGHT":
                    note = f"Required monthly ₹{req:,.2f} is achievable but consumes most of monthly surplus."
                else:
                    note = f"Required monthly ₹{req:,.2f} is well supported by current surplus."
                goal_considerations.append(GoalConsiderationItem(
                    goal_id=g.goal_uuid if hasattr(g, "goal_uuid") else str(g.id),
                    goal_name=g.name,
                    feasibility_status=feas,
                    monthly_required=req,
                    guidance_note=note
                ))

        # 6. Prompt 10 Market Context Integration & Safety Safeguards
        try:
            market_ov = MarketService.get_market_overview(db, user=user)
            m_freshness = market_ov.freshness
            m_pulse = market_ov.market_pulse
            m_source = market_ov.source

            if m_freshness in ["STALE", "UNAVAILABLE"]:
                warning_note = "Market data is delayed or stale; current market conditions should not be used for time-sensitive decisions."
            elif m_source == "BASELINE_MARKET_PROVIDER":
                warning_note = "Market context is based on a baseline reference snapshot. Use for educational awareness only."
            else:
                warning_note = "Market conditions represent recent index movements. Diversification and time horizon matter most."
        except Exception:
            m_freshness = "UNAVAILABLE"
            m_pulse = "UNAVAILABLE"
            m_source = "NONE"
            warning_note = "Market data is currently unavailable."

        market_summary = MarketContextSummarySchema(
            pulse=m_pulse,
            freshness=m_freshness,
            source=m_source,
            warning_note=warning_note
        )

        # 7. Risk Profile Summary
        st_risk = profile.risk_preference.upper() if profile and profile.risk_preference else "MODERATE"
        risk_summary = RiskProfileSummarySchema(
            preference=st_risk,
            guidance_note=f"Your stated preference is '{st_risk}'. Higher volatility assets require a longer investment horizon (>5 years) and a complete emergency buffer."
        )

        # 8. Educational Notes
        educational_notes = [
            "Emergency savings buffer should always take priority over high-volatility assets.",
            "Surplus guidance ranges are intended as flexible benchmarks, not rigid prescriptions.",
            "Short-term goals (<3 years) benefit from capital-preservation assets like fixed deposits or liquid funds.",
            "Past market performance does not guarantee future investment returns."
        ]

        rec_uuid = str(uuid.uuid4())
        response = PersonalizedRecommendationResponse(
            recommendation_id=rec_uuid,
            generated_at=now.isoformat(),
            data_completeness=data_completeness,
            data_completeness_note=completeness_str,
            recommendation_status="ACTIVE",
            monthly_capacity=monthly_capacity,
            top_priority=top_priority,
            financial_priorities=priorities,
            emergency_buffer_analysis=buffer_analysis,
            allocation_guidance=allocation_items,
            goal_considerations=goal_considerations,
            market_context_summary=market_summary,
            risk_profile=risk_summary,
            educational_notes=educational_notes
        )

        # Persist DB Snapshot
        try:
            snapshot = FinancialRecommendationSnapshot(
                recommendation_uuid=rec_uuid,
                user_id=user.id,
                data_completeness=data_completeness,
                recommendation_status="ACTIVE",
                top_priority_title=top_priority.title,
                top_priority_category=top_priority.category,
                emergency_buffer_status=buffer_analysis.status,
                priorities_json=json.dumps([p.model_dump() for p in priorities]),
                allocation_guidance_json=json.dumps([a.model_dump() for a in allocation_items]),
                goal_considerations_json=json.dumps([g.model_dump() for g in goal_considerations]),
                market_context_json=json.dumps(market_summary.model_dump()),
                created_at=now
            )
            db.add(snapshot)
            db.commit()
        except Exception as ex:
            db.rollback()
            logger.warning(f"Failed to persist FinancialRecommendationSnapshot to DB: {ex}")

        return response

    @staticmethod
    def get_latest_recommendation(db: Session, user: User) -> PersonalizedRecommendationResponse:
        """Fetch or generate latest recommendation response."""
        return RecommendationService.generate_recommendations(db, user)
