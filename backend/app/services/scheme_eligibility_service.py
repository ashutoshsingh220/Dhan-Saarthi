import json
from typing import TYPE_CHECKING
from app.schemas.scheme import SchemeEligibilityResponse

if TYPE_CHECKING:
    from app.models.scheme import GovernmentScheme
    from app.models.user import User, UserProfile

DISCLAIMER_TEXT = (
    "Final eligibility and benefits depend on current government rules, state guidelines, "
    "and official application verification. Please verify final eligibility through the official government portal."
)

class SchemeEligibilityService:
    @staticmethod
    def evaluate_eligibility(
        scheme: "GovernmentScheme",
        profile: "UserProfile | None",
        user: "User",
    ) -> SchemeEligibilityResponse:
        """
        Deterministically evaluate user profile and support context against a government scheme.
        DO NOT use AI or LLM here. All scoring and matching is 100% rule-based.
        """
        match_reasons: list[str] = []
        missing_info: list[str] = []

        rules = json.loads(scheme.eligibility_rules_json) if scheme.eligibility_rules_json else {}
        tags = json.loads(scheme.tags_json) if scheme.tags_json else []

        score = 20  # Base starting score for active catalog schemes

        if not profile:
            return SchemeEligibilityResponse(
                scheme_id=scheme.scheme_uuid,
                scheme_name=scheme.name,
                relevance_status="NEEDS_MORE_INFORMATION",
                eligibility_status="NEEDS_MORE_INFORMATION",
                relevance_score=10,
                match_reasons=["Scheme is active in government catalog."],
                missing_information=["Financial profile and location/occupation context have not been completed."],
                disclaimer=DISCLAIMER_TEXT,
                official_url=scheme.official_url,
            )

        # 1. Occupation Matching
        occ_upper = (profile.occupation or "").upper()
        occ_status_upper = (profile.occupation_status or "").upper()

        is_farmer = (
            "FARM" in occ_upper or "KISAN" in occ_upper or "AGRI" in occ_upper
            or occ_status_upper == "FARMER" or getattr(profile, "farming_interest", False)
        )
        is_business = (
            "BUSINESS" in occ_upper or "SHOP" in occ_upper or "SELF" in occ_upper
            or occ_status_upper in ["SELF_EMPLOYED", "BUSINESS_OWNER"]
            or getattr(profile, "business_interest", False)
        )

        if scheme.category in ["FARMER_SUPPORT", "AGRICULTURE_LOAN", "CROP_INSURANCE", "AGRICULTURAL_INFRASTRUCTURE", "FARM_EQUIPMENT", "IRRIGATION"]:
            if is_farmer:
                score += 35
                match_reasons.append("Your occupation or selected interest matches Agricultural/Farming support.")
            else:
                missing_info.append("Confirm if you engage in agricultural or farming activities.")

        elif scheme.category in ["DAIRY_AND_LIVESTOCK"]:
            farm_act = (getattr(profile, "farm_activity", "") or "").upper()
            if is_farmer or farm_act in ["DAIRY", "LIVESTOCK"]:
                score += 35
                match_reasons.append("Your profile indicates involvement in farming or dairy/livestock activities.")
            else:
                missing_info.append("Confirm if you manage livestock, dairy, or animal husbandry operations.")

        elif scheme.category in ["FISHERIES"]:
            farm_act = (getattr(profile, "farm_activity", "") or "").upper()
            if farm_act == "FISHERIES":
                score += 40
                match_reasons.append("Your profile activity specifically matches Fisheries and Aquaculture.")
            elif is_farmer:
                score += 20
                match_reasons.append("You are in agriculture; fisheries schemes support allied agricultural diversification.")
            else:
                missing_info.append("Confirm if you practice inland or marine fisheries/aquaculture.")

        elif scheme.category in ["SMALL_BUSINESS", "MICRO_ENTERPRISE", "SELF_EMPLOYMENT", "ENTREPRENEURSHIP"]:
            if is_business:
                score += 35
                match_reasons.append("Your occupation or self-employment status matches Micro & Small Business support.")
            else:
                missing_info.append("Confirm your small business or self-employment intentions.")

        elif scheme.category == "WOMEN_ENTREPRENEURSHIP":
            gender_upper = (profile.gender or "").upper()
            if gender_upper in ["FEMALE", "WOMAN"]:
                score += 35
                match_reasons.append("This scheme explicitly prioritizes Women Entrepreneurs.")
            if is_business or is_farmer:
                score += 15
                match_reasons.append("You have an active or proposed enterprise/livelihood.")
            else:
                missing_info.append("Confirm gender identity and greenfield business plans.")

        elif scheme.category == "RURAL_ENTERPRISE":
            area_upper = (getattr(profile, "rural_or_urban", "") or "").upper()
            if area_upper == "RURAL":
                score += 30
                match_reasons.append("Your location is classified as Rural, matching rural enterprise subsidies.")
            if is_business or is_farmer:
                score += 20
                match_reasons.append("Your enterprise/farming background aligns with rural business development.")
            else:
                missing_info.append("Specify whether your venture is located in a rural area.")

        # 2. Location / State Matching
        user_state = (getattr(profile, "state", "") or "").strip().upper()
        states_supported = json.loads(scheme.states_supported_json) if scheme.states_supported_json else ["ALL"]
        if "ALL" in states_supported or (user_state and user_state in [s.upper() for s in states_supported]):
            score += 10
            match_reasons.append("Scheme is accessible in your geographic region/state.")
        elif user_state:
            missing_info.append(f"Verify if {user_state} is specifically covered under state guidelines.")

        # 3. Derived Age check
        if profile.date_of_birth:
            from app.services.personalization_service import calculate_age
            age = calculate_age(profile.date_of_birth)
            min_age = rules.get("min_age", 18)
            max_age = rules.get("max_age", 75)
            if min_age <= age <= max_age:
                score += 10
                match_reasons.append(f"Your verified age ({age} years) meets the eligible age criteria ({min_age}-{max_age} years).")
            else:
                missing_info.append(f"Scheme age requirement is {min_age}-{max_age} years (your age: {age}).")

        # 4. Mandatory Document checklist check
        docs = json.loads(scheme.required_documents_json) if scheme.required_documents_json else []
        if docs:
            missing_info.append(f"Required documents to prepare: {', '.join(docs[:3])}.")

        # Clamp score between 0 and 100
        relevance_score = min(max(score, 0), 100)

        # Categorize Statuses
        if relevance_score >= 70:
            relevance_status = "HIGHLY_RELEVANT"
            eligibility_status = "POTENTIALLY_ELIGIBLE"
        elif relevance_score >= 45:
            relevance_status = "RELEVANT"
            eligibility_status = "POTENTIALLY_ELIGIBLE"
        elif relevance_score >= 25:
            relevance_status = "EXPLORE"
            eligibility_status = "LIKELY_RELEVANT"
        else:
            relevance_status = "NEEDS_MORE_INFORMATION"
            eligibility_status = "NEEDS_MORE_INFORMATION"

        return SchemeEligibilityResponse(
            scheme_id=scheme.scheme_uuid,
            scheme_name=scheme.name,
            relevance_status=relevance_status,
            eligibility_status=eligibility_status,
            relevance_score=relevance_score,
            match_reasons=match_reasons,
            missing_information=missing_info,
            disclaimer=DISCLAIMER_TEXT,
            official_url=scheme.official_url,
        )
