import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FinancialPriorityOrchestrator:
    """
    Deterministic Cross-Module Priority Engine.
    Enforces a strict, transparent priority hierarchy across all Dhan Saarthi modules.

    Hierarchy:
    1. CRITICAL SCAM / SAFETY ISSUE (Recent HIGH/CRITICAL scam risk)
    2. CRITICAL EMERGENCY BUFFER (< 1.0 month buffer)
    3. HIGH-COST DEBT (High cost debt priority)
    4. FINANCIAL GOAL AT RISK (Goal plan feasibility AT_RISK or TIGHT)
    5. IMPORTANT GOVERNMENT SUPPORT OPPORTUNITY (Highly relevant schemes found)
    6. LOW FINANCIAL LITERACY IN RELEVANT AREA (Incomplete learning modules)
    7. LONG-TERM INVESTMENT / WEALTH BUILDING (Strong buffer, healthy surplus)
    8. GENERAL MARKET AWARENESS (Market pulse context)
    """

    @classmethod
    def evaluate_top_priority(
        cls,
        scam_scans: List[Any],
        buffer_status: str,
        buffer_coverage: float,
        at_risk_goals: List[Any],
        tight_goals: List[Any],
        high_relevance_schemes: List[Any],
        incomplete_learning_modules: List[Any],
        surplus: float,
        market_pulse: str,
    ) -> Dict[str, Any]:

        # 1. CRITICAL SCAM / SAFETY ISSUE
        recent_high_scams = [
            s for s in scam_scans
            if getattr(s, "risk_level", "").upper() in ("HIGH", "CRITICAL")
        ]
        if recent_high_scams:
            latest_scam = recent_high_scams[0]
            risk = getattr(latest_scam, "risk_level", "HIGH").upper()
            return {
                "priority_category": "SCAM_SAFETY",
                "priority_level": "CRITICAL" if risk == "CRITICAL" else "HIGH",
                "reason": f"Scam Shield flagged a recent message with {risk} fraud risk.",
                "recommended_next_action": "Do not transfer money, share OTPs, or click suspicious links. Review the scan details in Scam Shield.",
                "source_modules": ["scam_shield"],
                "action_route": "/domain/scam-shield",
            }

        # 2. CRITICAL EMERGENCY BUFFER
        if buffer_status == "CRITICAL_BUFFER" or buffer_coverage < 1.0:
            return {
                "priority_category": "EMERGENCY_BUFFER",
                "priority_level": "CRITICAL",
                "reason": f"Your current liquid savings cover less than 1 month of essential expenses ({buffer_coverage:.1f} months).",
                "recommended_next_action": "Focus your monthly surplus on building an emergency buffer before investing in high-volatility assets.",
                "source_modules": ["financial_twin", "recommendations"],
                "action_route": "/domain/recommendations",
            }

        # 3. LOW EMERGENCY BUFFER / DEBT WARNING
        if buffer_status == "LOW_BUFFER" or (1.0 <= buffer_coverage < 3.0):
            return {
                "priority_category": "EMERGENCY_BUFFER",
                "priority_level": "HIGH",
                "reason": f"Your savings buffer covers {buffer_coverage:.1f} months of expenses. Reaching a 3-month buffer ensures financial safety.",
                "recommended_next_action": "Allocate a portion of your monthly surplus to build your emergency savings cushion.",
                "source_modules": ["financial_twin", "recommendations"],
                "action_route": "/domain/recommendations",
            }

        # 4. FINANCIAL GOAL AT RISK
        if at_risk_goals:
            g_names = ", ".join([getattr(g, "name", "Goal") for g in at_risk_goals])
            return {
                "priority_category": "GOAL_AT_RISK",
                "priority_level": "HIGH",
                "reason": f"Goal(s) '{g_names}' require higher monthly contributions than your current surplus supports.",
                "recommended_next_action": "Adjust goal timelines or target amounts in Smart Planning to make your plan feasible.",
                "source_modules": ["smart_planning"],
                "action_route": "/domain/planning",
            }

        if tight_goals:
            g_names = ", ".join([getattr(g, "name", "Goal") for g in tight_goals])
            return {
                "priority_category": "GOAL_TIGHT",
                "priority_level": "MEDIUM",
                "reason": f"Goal(s) '{g_names}' are achievable but require strict monthly savings consistency.",
                "recommended_next_action": "Review your monthly plan in Smart Planning to maintain your savings discipline.",
                "source_modules": ["smart_planning"],
                "action_route": "/domain/planning",
            }

        # 5. IMPORTANT GOVERNMENT SUPPORT OPPORTUNITY
        if high_relevance_schemes:
            top_scheme = high_relevance_schemes[0]
            s_name = getattr(top_scheme, "scheme_name", "Government Scheme")
            return {
                "priority_category": "GOVERNMENT_SCHEME",
                "priority_level": "MEDIUM",
                "reason": f"You are highly relevant for government support scheme '{s_name}'.",
                "recommended_next_action": "Explore eligible government subsidies, financial aid, or low-interest loan support.",
                "source_modules": ["government_schemes"],
                "action_route": "/domain/schemes",
            }

        # 6. LOW FINANCIAL LITERACY IN RELEVANT AREA
        if incomplete_learning_modules:
            top_mod = incomplete_learning_modules[0]
            m_title = getattr(top_mod, "title", "Financial Literacy Module")
            return {
                "priority_category": "FINANCIAL_LITERACY",
                "priority_level": "MEDIUM",
                "reason": f"Expand your financial knowledge by completing '{m_title}'.",
                "recommended_next_action": "Complete short bite-sized learning lessons and quizzes to strengthen your financial skills.",
                "source_modules": ["financial_literacy"],
                "action_route": "/(tabs)/learn",
            }

        # 7. LONG-TERM INVESTMENT / WEALTH BUILDING
        if buffer_status in ("MODERATE_BUFFER", "STRONG_BUFFER") and surplus > 0:
            return {
                "priority_category": "WEALTH_BUILDING",
                "priority_level": "LOW",
                "reason": "With a healthy emergency buffer and positive monthly surplus, you are well-positioned for long-term wealth building.",
                "recommended_next_action": "Review your personalized portfolio guidance ranges and optimize long-term asset allocations.",
                "source_modules": ["recommendations"],
                "action_route": "/domain/recommendations",
            }

        # 8. GENERAL MARKET AWARENESS
        return {
            "priority_category": "MARKET_AWARENESS",
            "priority_level": "LOW",
            "reason": f"Current Market Pulse is {market_pulse}. Keep track of market movements for financial awareness.",
            "recommended_next_action": "Stay informed about market trends while maintaining your disciplined long-term plan.",
            "source_modules": ["market_intelligence"],
            "action_route": "/domain/market-intelligence",
        }
