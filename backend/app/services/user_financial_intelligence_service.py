import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.accessibility_service import AccessibilityService
from app.services.financial_priority_orchestrator import FinancialPriorityOrchestrator
from app.services.financial_priority_service import FinancialPriorityService
from app.services.learning_service import LearningService
from app.services.market_insight_service import MarketInsightService
from app.services.market_service import MarketService
from app.services.personalization_service import build_personalization_context
from app.services.planning_service import PlanningService
from app.services.recommendation_service import RecommendationService
from app.services.scam_detection_service import ScamDetectionService
from app.services.scheme_recommendation_service import SchemeRecommendationService
from app.services.twin import calculate_initial_twin


logger = logging.getLogger(__name__)


class UserFinancialIntelligenceService:
    """
    Central Financial Intelligence Aggregation Service (Prompt 14 Part A & B).
    Aggregates existing verified services deterministically into a single snapshot
    and produces Today's Financial Brief.
    """

    @classmethod
    def get_user_intelligence_snapshot(cls, user: User, db: Session) -> Dict[str, Any]:
        profile = user.profile
        twin = user.financial_twin

        # Calculate profile completeness percentage
        profile_completeness = cls._compute_profile_completeness(user)

        # 1. Financial Twin metrics
        twin_data = {
            "health_score": twin.financial_health_score if twin else 50,
            "income": float(profile.monthly_income) if profile else 0.0,
            "expenses": float(profile.monthly_expenses) if profile else 0.0,
            "savings": float(profile.savings) if profile else 0.0,
            "surplus": float(profile.monthly_income - profile.monthly_expenses) if profile else 0.0,
            "financial_status": twin.risk_level if twin else "INITIALIZING",
        }


        # 2. Emergency Buffer & Recommendations
        savings = twin_data["savings"]
        expenses = twin_data["expenses"]
        surplus = twin_data["surplus"]

        try:
            buffer_analysis = FinancialPriorityService.analyze_emergency_buffer(savings, expenses)
            rec_snapshot = RecommendationService.generate_recommendations(db, user)
            rec_data = {
                "top_priority": rec_snapshot.top_priority.model_dump() if rec_snapshot.top_priority else None,
                "allocation_guidance": [a.model_dump() for a in rec_snapshot.allocation_guidance] if rec_snapshot.allocation_guidance else None,
            }
        except Exception as e:
            logger.warning(f"Error computing recommendations snapshot: {e}")
            buffer_analysis = None
            rec_data = {"top_priority": None, "allocation_guidance": None}

        buffer_status = buffer_analysis.status if buffer_analysis else "INSUFFICIENT_DATA"
        buffer_coverage = buffer_analysis.coverage_months if buffer_analysis else 0.0

        # 3. Goals & Smart Planning
        goals = getattr(user, "goals", [])
        at_risk_goals = [g for g in goals if getattr(g, "plan", None) and g.plan.feasibility_status == "AT_RISK"]
        tight_goals = [g for g in goals if getattr(g, "plan", None) and g.plan.feasibility_status == "TIGHT"]
        upcoming_milestones = []
        for g in goals:
            if getattr(g, "plan", None) and getattr(g.plan, "milestones", None):
                for m in g.plan.milestones:
                    if getattr(m, "status", "") != "completed":
                        upcoming_milestones.append({
                            "goal_name": g.name,
                            "milestone_name": m.title,
                            "target_amount": float(m.target_amount),
                            "target_date": str(m.milestone_date),
                        })


        goals_data = {
            "total_goals": len(goals),
            "at_risk_count": len(at_risk_goals),
            "tight_count": len(tight_goals),
            "upcoming_milestones": upcoming_milestones[:3],
        }

        # 4. Market Context
        try:
            mkt_overview = MarketService.get_market_overview(db, user=user)
            mkt_insights = MarketInsightService.generate_market_insights(
                mkt_overview.tracked_assets,
                explanation_level=getattr(profile, "preferred_explanation_level", "BALANCED") if profile else "BALANCED"
            )
            observation = mkt_insights[0].observation if mkt_insights else mkt_overview.pulse_summary
            market_data = {
                "market_pulse": mkt_overview.market_pulse,
                "freshness": mkt_overview.freshness,
                "data_source": mkt_overview.source,
                "observation": observation,
            }
        except Exception as e:
            logger.warning(f"Error fetching market intelligence snapshot: {e}")
            market_data = {
                "market_pulse": "UNAVAILABLE",
                "freshness": "UNAVAILABLE",
                "data_source": "UNKNOWN",
                "observation": "Market data is currently unavailable.",
            }

        # 5. Government Support
        try:
            scheme_recs = SchemeRecommendationService.get_recommendations_for_user(db, user)
            high_rel = [s for s in scheme_recs if getattr(s, "relevance_rank", "") == "HIGHLY_RELEVANT"]
            gov_data = {
                "relevant_schemes_count": len(scheme_recs),
                "high_relevance_count": len(high_rel),
                "top_schemes": [
                    {
                        "scheme_name": s.scheme.name,
                        "category": s.scheme.category,
                        "relevance_rank": s.relevance_rank,
                        "key_benefits": s.scheme.benefits_summary,
                    }
                    for s in scheme_recs[:3]
                ],
            }
        except Exception as e:
            logger.warning(f"Error computing scheme recommendations snapshot: {e}")
            high_rel = []
            gov_data = {"relevant_schemes_count": 0, "high_relevance_count": 0, "top_schemes": []}

        # 6. Financial Literacy
        try:
            prog_summary = LearningService.get_progress_summary(db, user)
            all_mods = LearningService.get_modules(db, user)
            completed_count = prog_summary.completed_modules if prog_summary else 0
            incomplete_mods = [m for m in all_mods if getattr(m, "status", "") != "COMPLETED"]
            literacy_data = {
                "completed_count": completed_count,
                "incomplete_count": len(incomplete_mods),
                "recommended_module": incomplete_mods[0].title if incomplete_mods else "All Modules Completed",
            }
        except Exception as e:
            logger.warning(f"Error fetching literacy snapshot: {e}")
            incomplete_mods = []
            literacy_data = {"completed_count": 0, "incomplete_count": 0, "recommended_module": "Financial Literacy"}



        # 7. Scam Safety
        scam_scans = getattr(user, "scam_scans", [])
        high_risk_scans = [s for s in scam_scans if getattr(s, "risk_level", "").upper() in ("HIGH", "CRITICAL")]
        latest_risk = scam_scans[-1].risk_level if scam_scans else "NONE"
        scam_data = {
            "total_scans": len(scam_scans),
            "high_risk_count": len(high_risk_scans),
            "latest_risk_level": latest_risk,
        }

        # 8. Accessibility Context
        acc_context = AccessibilityService.build_accessibility_context(profile)

        # 9. Personalization Context
        person_context = build_personalization_context(profile, language=user.preferred_language) if profile else {}

        # 10. Top Priority (Orchestrator)
        top_priority = FinancialPriorityOrchestrator.evaluate_top_priority(
            scam_scans=scam_scans,
            buffer_status=buffer_status,
            buffer_coverage=buffer_coverage,
            at_risk_goals=at_risk_goals,
            tight_goals=tight_goals,
            high_relevance_schemes=high_rel,
            incomplete_learning_modules=incomplete_mods,
            surplus=surplus,
            market_pulse=market_data["market_pulse"],
        )

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "profile_completeness": profile_completeness,
            "financial_twin": twin_data,
            "top_financial_priority": top_priority,
            "recommendations": rec_data,
            "goals": goals_data,
            "market_context": market_data,
            "government_support": gov_data,
            "literacy": literacy_data,
            "scam_safety": scam_data,
            "accessibility": acc_context,
            "personalization": person_context,
        }

    @classmethod
    def generate_todays_financial_brief(cls, user: User, db: Session) -> Dict[str, Any]:
        """
        Generates Today's Financial Brief deterministically (Prompt 14 Part B).
        Tailored to language, explanation level, accessibility profile, and voice preferences.
        Does NOT rely on Gemini for underlying facts.
        """
        snapshot = cls.get_user_intelligence_snapshot(user, db)
        lang = user.preferred_language.lower()
        is_hindi = "hi" in lang or lang == "hindi"

        profile = user.profile
        exp_level = getattr(profile, "preferred_explanation_level", "BALANCED") if profile else "BALANCED"
        acc_profile = snapshot["accessibility"].get("accessibility_profile", "STANDARD")
        top_priority = snapshot["top_financial_priority"]

        # Build bullet points deterministically
        points = []

        # Point 1: Top priority
        p_reason = top_priority["reason"]
        p_action = top_priority["recommended_next_action"]
        if is_hindi:
            points.append(f"मुख्य प्राथमिकता: {p_reason} {p_action}")
        else:
            points.append(f"Top Priority: {p_reason} {p_action}")

        # Point 2: Goal status
        goals = snapshot["goals"]
        if goals["at_risk_count"] > 0:
            msg = f"{goals['at_risk_count']} लक्ष्य को पुनर्मूल्यांकन की आवश्यकता है।" if is_hindi else f"{goals['at_risk_count']} goal(s) require contribution adjustments."
            points.append(msg)
        elif goals["total_goals"] > 0:
            msg = f"आपके {goals['total_goals']} वित्तीय लक्ष्य सही दिशा में आगे बढ़ रहे हैं।" if is_hindi else f"Your {goals['total_goals']} financial goal(s) are progressing as planned."
            points.append(msg)

        # Point 3: Market pulse
        mkt = snapshot["market_context"]
        pulse = mkt["market_pulse"]
        if is_hindi:
            points.append(f"आज का मार्केट पल्स {pulse} है। यह आपके दीर्घकालिक योजना को प्रभावित नहीं करता है।")
        else:
            points.append(f"Today's Market Pulse is {pulse}. This context should not disrupt your long-term plan.")

        # Point 4: Government schemes (if relevant)
        gov = snapshot["government_support"]
        if gov["high_relevance_count"] > 0:
            msg = f"आपकी प्रोफाइल के अनुसार {gov['high_relevance_count']} सरकारी योजनाएं उपयोगी हो सकती हैं।" if is_hindi else f"{gov['high_relevance_count']} government scheme(s) match your profile requirements."
            points.append(msg)

        # Point 5: Literacy / Scam (if detailed)
        if exp_level == "DETAILED":
            lit = snapshot["literacy"]
            if lit.get("recommended_module"):
                msg = f"अनुशंसित शिक्षण मॉड्यूल: {lit['recommended_module']}" if is_hindi else f"Recommended Learning Module: {lit['recommended_module']}"
                points.append(msg)

        # Format depending on explanation level and accessibility profile
        if exp_level == "SIMPLE" or acc_profile in ("LOW_LITERACY", "ELDERLY_FRIENDLY"):
            points = points[:3]  # Max 3 concise bullet points

        greeting = cls._generate_greeting(user.full_name, is_hindi)

        summary_sentence = (
            f"{greeting} आपकी मुख्य प्राथमिकता: {top_priority['reason']}"
            if is_hindi
            else f"{greeting} Your top priority today is: {top_priority['reason']}"
        )

        return {
            "greeting": greeting,
            "summary_sentence": summary_sentence,
            "bullet_points": points,
            "top_priority": top_priority,
            "explanation_level": exp_level,
            "accessibility_profile": acc_profile,
            "language": "hi" if is_hindi else "en",
        }


    @staticmethod
    def _compute_profile_completeness(user: User) -> int:
        profile = user.profile
        if not profile:
            return 20
        score = 50
        if profile.date_of_birth:
            score += 10
        if profile.education_level:
            score += 10
        if profile.financial_knowledge_level:
            score += 10
        if profile.occupation_status:
            score += 10
        if getattr(profile, "state", None):
            score += 10
        return min(score, 100)

    @staticmethod
    def _generate_greeting(full_name: str, is_hindi: bool) -> str:
        first_name = full_name.split(" ")[0] if full_name else ""
        hour = datetime.now().hour
        if is_hindi:
            if hour < 12:
                time_str = "शुभ प्रभात"
            elif hour < 17:
                time_str = "शुभ दोपहर"
            else:
                time_str = "शुभ संध्या"
            return f"{time_str}, {first_name}" if first_name else time_str
        else:
            if hour < 12:
                time_str = "Good Morning"
            elif hour < 17:
                time_str = "Good Afternoon"
            else:
                time_str = "Good Evening"
            return f"{time_str}, {first_name}" if first_name else time_str
