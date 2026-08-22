import logging
from app.models.user import UserProfile
from app.schemas.recommendation import EmergencyBufferAnalysis, PriorityItem

logger = logging.getLogger(__name__)

# Configurable constants for emergency buffer thresholds
BUFFER_CRITICAL_MONTHS = 1.0
BUFFER_LOW_MONTHS = 3.0
BUFFER_MODERATE_MONTHS = 6.0

class FinancialPriorityService:
    """
    100% Deterministic Financial Priority & Emergency Buffer Analysis Engine.
    """

    @staticmethod
    def analyze_emergency_buffer(savings: float, monthly_expenses: float) -> EmergencyBufferAnalysis:
        if monthly_expenses <= 0:
            return EmergencyBufferAnalysis(
                monthly_expenses=0.0,
                current_savings=savings,
                coverage_months=0.0,
                status="INSUFFICIENT_DATA",
                target_recommended_savings=0.0,
                explanation="Monthly expenses are not recorded; cannot compute exact emergency buffer coverage."
            )

        coverage = round(savings / monthly_expenses, 2)
        target = round(monthly_expenses * 3.0, 2)

        if coverage < BUFFER_CRITICAL_MONTHS:
            status = "CRITICAL_BUFFER"
            explanation = f"Your current savings buffer (₹{savings:,.2f}) covers only {coverage:.1f} months of expenses. Building a 3-month buffer (₹{target:,.2f}) is critical."
        elif coverage < BUFFER_LOW_MONTHS:
            status = "LOW_BUFFER"
            explanation = f"Your savings buffer covers {coverage:.1f} months of expenses. Reaching 3 to 6 months of expenses will provide strong financial safety."
        elif coverage < BUFFER_MODERATE_MONTHS:
            status = "MODERATE_BUFFER"
            target = round(monthly_expenses * 6.0, 2)
            explanation = f"Your savings buffer covers {coverage:.1f} months of expenses. You have a solid safety cushion."
        else:
            status = "STRONG_BUFFER"
            target = round(monthly_expenses * 6.0, 2)
            explanation = f"Your savings buffer covers {coverage:.1f} months of expenses. You have an excellent emergency reserve."

        return EmergencyBufferAnalysis(
            monthly_expenses=monthly_expenses,
            current_savings=savings,
            coverage_months=coverage,
            status=status,
            target_recommended_savings=target,
            explanation=explanation
        )

    @staticmethod
    def classify_priorities(
        profile: UserProfile,
        buffer_analysis: EmergencyBufferAnalysis,
        goals: list,
        surplus: float
    ) -> list[PriorityItem]:
        priorities = []

        # 1. Emergency Buffer Priority
        if buffer_analysis.status in ["CRITICAL_BUFFER", "LOW_BUFFER"]:
            priorities.append(PriorityItem(
                title="Build Emergency Buffer",
                category="EMERGENCY_BUFFER",
                priority_level="HIGH",
                reason=buffer_analysis.explanation,
                action_guidance="Direct a higher portion of monthly surplus into liquid savings or high-yield savings accounts before expanding high-volatility investments.",
                data_basis=["monthly_expenses", "savings"]
            ))

        # 2. Debt Priority (Transparent data limit disclosure)
        priorities.append(PriorityItem(
            title="High-Cost Debt Review",
            category="HIGH_COST_DEBT",
            priority_level="MEDIUM",
            reason="Debt information is not recorded in your profile. High-interest debt (>12% APR) should always be prioritized over market investments.",
            action_guidance="If you hold high-cost loans or credit balances, clear them first as loan interest often exceeds investment returns.",
            data_basis=["debt_information_unrecorded"]
        ))

        # 3. Essential Goals Priority
        at_risk_goals = [g for g in goals if g.plan and g.plan.feasibility_status == "AT_RISK"]
        tight_goals = [g for g in goals if g.plan and g.plan.feasibility_status == "TIGHT"]

        if at_risk_goals:
            g_names = ", ".join([g.name for g in at_risk_goals])
            priorities.append(PriorityItem(
                title="Adjust At-Risk Smart Goals",
                category="ESSENTIAL_GOALS",
                priority_level="HIGH",
                reason=f"Goal(s) '{g_names}' require higher monthly contributions than your current surplus easily supports.",
                action_guidance="Extend your goal target timeline or reduce non-essential expenses to make your monthly requirement feasible.",
                data_basis=["goals", "monthly_surplus", "plan_feasibility"]
            ))
        elif tight_goals:
            g_names = ", ".join([g.name for g in tight_goals])
            priorities.append(PriorityItem(
                title="Maintain Tight Financial Goals",
                category="ESSENTIAL_GOALS",
                priority_level="MEDIUM",
                reason=f"Goal(s) '{g_names}' are feasible but consume a large portion of your monthly surplus.",
                action_guidance="Maintain strict monthly contribution discipline while keeping a flexible cash buffer.",
                data_basis=["goals", "monthly_surplus"]
            ))
        elif goals:
            priorities.append(PriorityItem(
                title="Continue Planned Goal Contributions",
                category="ESSENTIAL_GOALS",
                priority_level="MEDIUM",
                reason="Your active goals are fully feasible based on recorded surplus.",
                action_guidance="Keep executing your planned monthly contributions on schedule.",
                data_basis=["goals", "monthly_surplus"]
            ))

        # 4. Long Term Investing / Market Exposure
        if buffer_analysis.status in ["MODERATE_BUFFER", "STRONG_BUFFER"] and surplus > 0:
            priorities.append(PriorityItem(
                title="Explore Diversified Wealth Building",
                category="LONG_TERM_INVESTING",
                priority_level="MEDIUM",
                reason="Your liquid savings buffer is healthy and you have positive monthly surplus.",
                action_guidance="Consider allocating uncommitted surplus into diversified index funds, mutual funds, or government schemes for long-term growth.",
                data_basis=["savings_buffer", "monthly_surplus", "risk_preference"]
            ))
        else:
            priorities.append(PriorityItem(
                title="Focus on Capital Preservation & Liquidity",
                category="MARKET_EXPOSURE",
                priority_level="LOW",
                reason="Until your emergency reserve reaches 3 months, liquidity should remain your primary focus over high-risk assets.",
                action_guidance="Learn basic market concepts through Financial Literacy modules before committing large sums.",
                data_basis=["coverage_months", "risk_preference"]
            ))

        return priorities
