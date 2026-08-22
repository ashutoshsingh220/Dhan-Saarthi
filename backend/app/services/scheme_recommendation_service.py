import json
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.scheme import SchemeRecommendationResponse
from app.services.scheme_eligibility_service import SchemeEligibilityService
from app.services.scheme_service import SchemeService

class SchemeRecommendationService:
    @staticmethod
    def get_recommendations_for_user(
        db: Session,
        user: User,
        limit: int = 10
    ) -> list[SchemeRecommendationResponse]:
        """
        Deterministically calculate and rank government scheme recommendations for a user.
        Combines profile, occupation, location, and scheme eligibility evaluation.
        """
        schemes = SchemeService.get_all_schemes(db)
        profile = user.profile

        recommendations: list[SchemeRecommendationResponse] = []

        for s_pub in schemes:
            scheme_orm = SchemeService.get_scheme_by_uuid_or_id(db, s_pub.scheme_id)
            if not scheme_orm:
                continue

            eligibility = SchemeEligibilityService.evaluate_eligibility(scheme_orm, profile, user)

            why_rec_parts = []
            if eligibility.match_reasons:
                why_rec_parts.append(eligibility.match_reasons[0])
            else:
                why_rec_parts.append("This national scheme matches general financial support categories.")

            why_recommended = " ".join(why_rec_parts)

            what_to_verify = []
            if eligibility.missing_information:
                what_to_verify.extend(eligibility.missing_information[:2])
            what_to_verify.append("Verify latest beneficiary guidelines on the official portal.")

            rec = SchemeRecommendationResponse(
                scheme=s_pub,
                relevance_rank=eligibility.relevance_status,
                relevance_score=eligibility.relevance_score,
                why_recommended=why_recommended,
                what_to_verify_next=what_to_verify,
                official_source_url=s_pub.official_url,
            )
            recommendations.append(rec)

        # Sort deterministically by relevance_score descending, then scheme name ascending
        recommendations.sort(key=lambda r: (-r.relevance_score, r.scheme.name))

        return recommendations[:limit]
