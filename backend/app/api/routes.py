from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.api.deps import get_current_user, get_current_user_optional
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.planning import FinancialGoal
from app.models.scam import ScamIndicator, ScamScan
from app.models.user import FinancialTwin, User, UserProfile
import app.models  # noqa: F401
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.schemas.chat import ChatMessageDetail, ChatMessageRequest, ChatMessageResponse, ChatSessionSummary
from app.schemas.market import MarketAssetSchema, MarketOverviewResponse
from app.schemas.recommendation import PersonalizedRecommendationResponse


from app.schemas.planning import (
    GoalCreateRequest,
    GoalDetailResponse,
    GoalUpdateRequest,
    ProgressUpdateRequest,
)
from app.schemas.learning import (
    LearningModuleResponse,
    LearningProgressSummaryResponse,
    LearningRecommendationResponse,
    QuizQuestionPublic,
    QuizResultResponse,
    QuizSubmissionRequest,
)
from app.schemas.profile import ProfileResponse, ProfileUpsertRequest
from app.schemas.scam import ScamAnalyzeRequest, ScamHistoryResponse, ScamScanResponse
from app.schemas.scheme import (
    GovernmentSchemePublic,
    SCHEME_CATEGORIES,
    SchemeCategoryCount,
    SchemeEligibilityResponse,
    SchemeRecommendationResponse,
    SupportContextResponse,
    SupportContextUpdateRequest,
)
from app.schemas.twin import FinancialTwinResponse
from app.services.learning_service import LearningService
from app.services.personalization_service import calculate_age
from app.services.planning_service import PlanningService
from app.services.saarthi_service import SaarthiService
from app.services.scam_detection_service import ScamDetectionService
from app.services.scheme_eligibility_service import SchemeEligibilityService
from app.services.scheme_recommendation_service import SchemeRecommendationService
from app.services.scheme_service import SchemeService
from app.services.twin import calculate_initial_twin


router = APIRouter(prefix="/api", tags=["API"])
saarthi_service = SaarthiService()
planning_service = PlanningService()


def auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(str(user.id)), user=UserResponse.model_validate(user), onboarding_complete=user.profile is not None)


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == str(payload.email).lower())):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(full_name=payload.full_name.strip(), email=str(payload.email).lower(), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return auth_response(user)


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return auth_response(user)


@router.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"user": UserResponse.model_validate(user), "onboarding_complete": user.profile is not None}


def _build_profile_response(profile: UserProfile) -> ProfileResponse:
    """Construct ProfileResponse including the deterministic derived_age.
    preferred_language and accessibility_mode live on User, so we pull them there.
    """
    derived_age = None
    if profile.date_of_birth is not None:
        derived_age = calculate_age(profile.date_of_birth)
    # Build a dict from the ORM object, supplementing fields from the related User
    data = {col.name: getattr(profile, col.name) for col in profile.__table__.columns}
    data["preferred_language"] = profile.user.preferred_language
    data["accessibility_mode"] = profile.user.accessibility_mode
    data["derived_age"] = derived_age
    data["total_savings"] = getattr(profile, "total_savings", 0.0) or 0.0
    data["monthly_savings"] = getattr(profile, "monthly_savings", 0.0) or getattr(profile, "savings", 0.0) or 0.0
    data["consent_given"] = getattr(profile, "consent_given", False) or False
    data["consent_given_at"] = getattr(profile, "consent_given_at", None)
    resp = ProfileResponse.model_validate(data)
    return resp


@router.get("/profile", response_model=ProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    if user.profile is None:
        raise HTTPException(status_code=404, detail="Financial profile has not been completed")
    return _build_profile_response(user.profile)


@router.put("/profile", response_model=ProfileResponse)
def upsert_profile(payload: ProfileUpsertRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.preferred_language, user.accessibility_mode = payload.preferred_language, payload.accessibility_mode
    # Exclude language/accessibility (stored on User) and personalization/accessibility/consent fields handled separately
    values = payload.model_dump(exclude={
        "preferred_language", "accessibility_mode",
        "date_of_birth", "education_level",
        "financial_knowledge_level", "preferred_explanation_level", "occupation_status",
        "accessibility_mode_enabled", "accessibility_profile", "text_size_preference",
        "high_contrast_enabled", "reduce_motion_enabled", "simplified_interface_enabled",
        "voice_navigation_enabled", "auto_speak_important_results", "sequential_navigation_enabled",
        "consent_given", "consent_given_at",
    })
    
    # Financial savings sync
    if payload.monthly_savings is not None and float(payload.monthly_savings) > 0:
        values["monthly_savings"] = float(payload.monthly_savings)
        values["savings"] = float(payload.monthly_savings)
    elif payload.savings is not None and float(payload.savings) > 0:
        values["monthly_savings"] = float(payload.savings)
        values["savings"] = float(payload.savings)

    if payload.total_savings is not None:
        values["total_savings"] = float(payload.total_savings)

    profile = user.profile
    if profile is None:
        profile = UserProfile(user_id=user.id, **values)
        db.add(profile)
    else:
        for key, value in values.items():
            setattr(profile, key, value)

    # Apply personalization, accessibility & legal consent fields
    extra_fields = [
        "date_of_birth", "education_level",
        "financial_knowledge_level", "preferred_explanation_level", "occupation_status",
        "accessibility_mode_enabled", "accessibility_profile", "text_size_preference",
        "high_contrast_enabled", "reduce_motion_enabled", "simplified_interface_enabled",
        "voice_navigation_enabled", "auto_speak_important_results", "sequential_navigation_enabled",
        "consent_given", "consent_given_at",
    ]
    payload_dict = payload.model_dump(exclude_unset=True)
    for field in extra_fields:
        if field in payload_dict:
            setattr(profile, field, payload_dict[field])

    if payload.consent_given and profile.consent_given_at is None:
        profile.consent_given_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)
    return _build_profile_response(profile)






@router.get("/financial-twin", response_model=FinancialTwinResponse)
def get_twin(user: User = Depends(get_current_user)):
    if user.financial_twin is None:
        raise HTTPException(status_code=404, detail="Financial Twin has not been generated")
    return user.financial_twin


@router.put("/financial-twin/generate", response_model=FinancialTwinResponse)
def generate_twin(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.profile is None:
        raise HTTPException(status_code=400, detail="Complete your financial profile before generating a Financial Twin")
    score, risk_level, summary = calculate_initial_twin(user.profile)
    twin = user.financial_twin
    if twin is None:
        twin = FinancialTwin(user_id=user.id, financial_health_score=score, risk_level=risk_level, financial_summary=summary); db.add(twin)
    else:
        twin.financial_health_score, twin.risk_level, twin.financial_summary = score, risk_level, summary
    db.commit(); db.refresh(twin)
    return twin


# --- AI SAARTHI CHAT ENDPOINTS ---
from fastapi.responses import StreamingResponse


@router.post("/saarthi/chat", response_model=ChatMessageResponse)
def chat_with_saarthi(payload: ChatMessageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return saarthi_service.process_message(db=db, user=user, message_text=payload.message, session_uuid=payload.session_id)


@router.post("/saarthi/chat/stream")
def chat_with_saarthi_stream(payload: ChatMessageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clean_text = payload.message.strip()
    if not clean_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message content cannot be empty")
    generator = saarthi_service.process_message_stream(db=db, user=user, message_text=payload.message, session_uuid=payload.session_id)
    return StreamingResponse(generator, media_type="text/event-stream")





@router.get("/saarthi/sessions", response_model=list[ChatSessionSummary])
def list_chat_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return saarthi_service.get_user_sessions(db=db, user=user)


@router.get("/saarthi/sessions/{session_id}/messages", response_model=list[ChatMessageDetail])
def get_chat_session_messages(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return saarthi_service.get_session_messages(db=db, user=user, session_uuid=session_id)


# --- SMART FINANCIAL PLANNING ENDPOINTS (PROMPT 4) ---
@router.post("/planning/goals", response_model=GoalDetailResponse, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = planning_service.create_goal(
        db=db,
        user=user,
        name=payload.name,
        category=payload.category,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        target_date=payload.target_date,
    )
    return goal


@router.get("/planning/goals", response_model=list[GoalDetailResponse])
def get_user_goals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return planning_service.get_user_goals(db=db, user=user)


@router.get("/planning/goals/{goal_id}", response_model=GoalDetailResponse)
def get_goal_detail(goal_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return planning_service.get_goal_by_uuid(db=db, user=user, goal_uuid=goal_id)


@router.put("/planning/goals/{goal_id}", response_model=GoalDetailResponse)
def update_goal(goal_id: str, payload: GoalUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = planning_service.get_goal_by_uuid(db=db, user=user, goal_uuid=goal_id)
    if payload.name is not None: goal.name = payload.name.strip()
    if payload.category is not None: goal.category = payload.category
    if payload.target_amount is not None: goal.target_amount = payload.target_amount
    if payload.target_date is not None: goal.target_date = payload.target_date
    planning_service.recalculate_plan(db=db, user=user, goal=goal)
    db.commit(); db.refresh(goal)
    return goal


@router.post("/planning/goals/{goal_id}/progress", response_model=GoalDetailResponse)
def record_goal_progress(goal_id: str, payload: ProgressUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return planning_service.record_progress(db=db, user=user, goal_uuid=goal_id, contribution_amount=payload.amount)


@router.post("/planning/goals/{goal_id}/recalculate", response_model=GoalDetailResponse)
def recalculate_goal_plan(goal_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = planning_service.get_goal_by_uuid(db=db, user=user, goal_uuid=goal_id)
    planning_service.recalculate_plan(db=db, user=user, goal=goal)
    db.commit(); db.refresh(goal)
    return goal


# --- SCAM SHIELD ENDPOINTS (PROMPT 5) ---
@router.post("/scam-shield/analyze", response_model=ScamScanResponse, status_code=status.HTTP_201_CREATED)
def analyze_scam_message(payload: ScamAnalyzeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = ScamDetectionService.analyze(payload.message)
    scan = ScamScan(
        user_id=user.id,
        input_text=payload.message,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        summary=result["summary"],
    )
    scan.recommended_actions = result["recommended_actions"]
    db.add(scan)
    db.commit()
    db.refresh(scan)

    for ind in result["indicators"]:
        indicator = ScamIndicator(
            scan_id=scan.id,
            indicator_type=ind["indicator_type"],
            matched_text=ind["matched_text"],
            severity=ind["severity"],
            points=ind["points"],
        )
        db.add(indicator)
    db.commit()
    db.refresh(scan)
    return scan


@router.get("/scam-shield/history", response_model=ScamHistoryResponse)
def get_scam_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scans = db.scalars(
        select(ScamScan).where(ScamScan.user_id == user.id).order_by(ScamScan.created_at.desc())
    ).all()
    return ScamHistoryResponse(scans=scans, total_count=len(scans))


@router.get("/scam-shield/history/{scan_id}", response_model=ScamScanResponse)
def get_scam_scan_detail(scan_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scan = db.scalar(select(ScamScan).where(ScamScan.scan_uuid == scan_id))
    if scan is None or scan.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this scan result")
    return scan


@router.delete("/scam-shield/history/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scam_scan(scan_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scan = db.scalar(select(ScamScan).where(ScamScan.scan_uuid == scan_id))
    if scan is None or scan.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this scan result")
    db.delete(scan)
    db.commit()
    return None


# --- FINANCIAL LITERACY ENDPOINTS (PROMPT 6) ---
@router.get("/learn/modules", response_model=list[LearningModuleResponse])
def get_learning_modules(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LearningService.get_modules(db=db, user=user)


@router.get("/learn/progress", response_model=LearningProgressSummaryResponse)
def get_learning_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LearningService.get_progress_summary(db=db, user=user)


@router.get("/learn/recommendations", response_model=list[LearningRecommendationResponse])
def get_learning_recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LearningService.get_recommendations(db=db, user=user)


@router.get("/learn/modules/{module_id}", response_model=LearningModuleResponse)
def get_learning_module_detail(module_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    module = LearningService.get_module_detail(db=db, user=user, module_id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail=f"Learning module '{module_id}' not found")
    return module


@router.post("/learn/modules/{module_id}/start", response_model=LearningModuleResponse)
def start_learning_module(module_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return LearningService.start_module(db=db, user=user, module_id=module_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/learn/modules/{module_id}/quiz", response_model=list[QuizQuestionPublic])
def get_learning_quiz(module_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return LearningService.get_quiz(db=db, module_id=module_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/learn/modules/{module_id}/quiz", response_model=QuizResultResponse)
def submit_learning_quiz(module_id: str, payload: QuizSubmissionRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return LearningService.submit_quiz(db=db, user=user, module_id=module_id, answers=payload.answers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- GOVERNMENT SCHEME DISCOVERY ENDPOINTS (PROMPT 9) ---
@router.put("/profile/support-context", response_model=SupportContextResponse)
def update_support_context(payload: SupportContextUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = user.profile
    if profile is None:
        raise HTTPException(status_code=400, detail="Complete your financial profile before updating scheme support context")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return SupportContextResponse(
        state=profile.state,
        district=profile.district,
        rural_or_urban=profile.rural_or_urban,
        farming_interest=profile.farming_interest or False,
        business_interest=profile.business_interest or False,
        farm_activity=profile.farm_activity,
        business_stage=profile.business_stage,
        business_sector=profile.business_sector,
        business_registration_status=profile.business_registration_status,
    )


@router.get("/schemes/categories", response_model=list[SchemeCategoryCount])
def get_scheme_categories(db: Session = Depends(get_db)):
    schemes = SchemeService.get_all_schemes(db)
    counts: dict[str, int] = {cat: 0 for cat in SCHEME_CATEGORIES}
    for s in schemes:
        if s.category in counts:
            counts[s.category] += 1
        for t in s.tags:
            if t in counts and t != s.category:
                counts[t] += 1
    return [
        SchemeCategoryCount(category_id=cat, category_name=cat.replace("_", " ").title(), count=counts[cat])
        for cat in SCHEME_CATEGORIES
    ]


@router.get("/schemes/recommendations", response_model=list[SchemeRecommendationResponse])
def get_scheme_recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SchemeRecommendationService.get_recommendations_for_user(db=db, user=user)


@router.get("/schemes", response_model=list[GovernmentSchemePublic])
def list_schemes(category: str | None = None, search: str | None = None, db: Session = Depends(get_db)):
    return SchemeService.get_all_schemes(db=db, category=category, search=search)


@router.get("/schemes/{scheme_id}", response_model=GovernmentSchemePublic)
def get_scheme_detail(scheme_id: str, db: Session = Depends(get_db)):
    scheme = SchemeService.get_scheme_by_uuid_or_id(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Government scheme '{scheme_id}' not found")
    return SchemeService.to_public_schema(scheme)


@router.post("/schemes/{scheme_id}/eligibility-check", response_model=SchemeEligibilityResponse)
def check_scheme_eligibility(scheme_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheme = SchemeService.get_scheme_by_uuid_or_id(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Government scheme '{scheme_id}' not found")
    return SchemeEligibilityService.evaluate_eligibility(scheme=scheme, profile=user.profile, user=user)


from app.services.market_service import MarketService



# --- PROMPT 10: MARKET INTELLIGENCE ENDPOINTS ---

@router.get("/market/overview", response_model=MarketOverviewResponse)
def get_market_overview(
    force_refresh: bool = False,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    return MarketService.get_market_overview(db=db, user=user, force_refresh=force_refresh)


@router.get("/market/assets/{symbol}", response_model=MarketAssetSchema)
def get_asset_detail(
    symbol: str,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    asset = MarketService.get_asset_detail(db=db, symbol=symbol, user=user)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Market asset '{symbol}' not found")
    return asset


@router.post("/market/refresh", response_model=MarketOverviewResponse)
def refresh_market_overview(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MarketService.get_market_overview(db=db, user=user, force_refresh=True)


from app.core.config import settings
from app.services.recommendation_service import RecommendationService
from app.services.user_financial_intelligence_service import UserFinancialIntelligenceService


# --- PROMPT 11: RECOMMENDATION & PORTFOLIO GUIDANCE ENDPOINTS ---

@router.get("/recommendations", response_model=PersonalizedRecommendationResponse)
def get_personalized_recommendation(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecommendationService.get_latest_recommendation(db=db, user=user)


@router.post("/recommendations/generate", response_model=PersonalizedRecommendationResponse)
def generate_personalized_recommendation(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return RecommendationService.generate_recommendations(db=db, user=user)


# --- PROMPT 14: SYSTEM INTEGRATION & ORCHESTRATION ENDPOINTS ---

@router.get("/dashboard/brief")
def get_todays_financial_brief(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns Today's Financial Brief (Prompt 14 Part B).
    Deterministic personalized daily intelligence summary.
    """
    return UserFinancialIntelligenceService.generate_todays_financial_brief(user, db)


@router.get("/dashboard/snapshot")
def get_user_intelligence_snapshot(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns Unified User Financial Intelligence Snapshot (Prompt 14 Part A).
    Central deterministic aggregation of all modules.
    """
    return UserFinancialIntelligenceService.get_user_intelligence_snapshot(user, db)


@router.get("/system/health")
def system_health_check(db: Session = Depends(get_db)):
    """
    Backend diagnostic health endpoint (Prompt 14 Part L).
    Reports service availability without exposing secrets.
    """
    db_status = "healthy"
    try:
        db.execute(select(1))
    except Exception:
        db_status = "unhealthy"

    gemini_status = "configured" if getattr(settings, "gemini_api_key", None) else "not_configured"
    market_provider = "alpha_vantage" if getattr(settings, "alpha_vantage_api_key", None) else "baseline_provider"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "gemini": gemini_status,
        "market_provider": market_provider,
        "market_cache": "available",
        "voice_mode": "frontend_capability_based",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }






