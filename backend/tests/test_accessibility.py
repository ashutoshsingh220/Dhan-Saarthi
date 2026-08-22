import os
os.environ["JWT_SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import engine, get_db
from app.main import app
from app.models.user import User
from app.services.accessibility_service import AccessibilityService, ACCESSIBILITY_PROFILES
from app.services.context_builder import ContextBuilder

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def _register_user(email: str = "a11y_user@example.com") -> str:
    res = client.post("/api/auth/register", json={"full_name": "Ramesh Kumar", "email": email, "password": "password123"})
    assert res.status_code == 201
    return res.json()["access_token"]

def _onboard_user(token: str, acc_data: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "age": 45,
        "occupation": "Farmer",
        "monthly_income": 35000,
        "monthly_expenses": 20000,
        "savings": 50000,
        "financial_goal": "Farm Equipment",
        "risk_preference": "moderate",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard",
    }
    if acc_data:
        payload.update(acc_data)
    res = client.put("/api/profile", json=payload, headers=headers)
    assert res.status_code == 200, f"Profile error: {res.text}"
    return res.json()

# --- PROMPT 13 ACCESSIBILITY TESTS ---

def test_accessibility_mode_defaults_correctly():
    token = _register_user("default_a11y@example.com")
    prof = _onboard_user(token)
    assert prof["accessibility_mode_enabled"] is False
    assert prof["accessibility_profile"] == "STANDARD"
    assert prof["text_size_preference"] == "STANDARD"
    assert prof["high_contrast_enabled"] is False

def test_existing_users_without_accessibility_fields_remain_valid():
    token = _register_user("legacy_a11y@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    # Onboard using standard payload
    res = client.put("/api/profile", json={
        "age": 30, "occupation": "Worker", "monthly_income": 25000, "monthly_expenses": 15000,
        "savings": 30000, "financial_goal": "Savings", "risk_preference": "low"
    }, headers=headers)
    assert res.status_code == 200

def test_invalid_accessibility_profile_rejected():
    token = _register_user("invalid_prof@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.put("/api/profile", json={
        "age": 40, "occupation": "Driver", "monthly_income": 30000, "monthly_expenses": 20000,
        "savings": 40000, "financial_goal": "Home", "risk_preference": "moderate",
        "accessibility_profile": "INVALID_PROFILE"
    }, headers=headers)
    assert res.status_code == 422

def test_accessibility_preferences_persist_correctly():
    token = _register_user("persist_a11y@example.com")
    prof = _onboard_user(token, {
        "accessibility_mode_enabled": True,
        "accessibility_profile": "VISUAL_ASSIST",
        "text_size_preference": "LARGE",
        "high_contrast_enabled": True,
        "voice_navigation_enabled": True,
        "sequential_navigation_enabled": True,
    })
    assert prof["accessibility_mode_enabled"] is True
    assert prof["accessibility_profile"] == "VISUAL_ASSIST"
    assert prof["text_size_preference"] == "LARGE"
    assert prof["high_contrast_enabled"] is True
    assert prof["voice_navigation_enabled"] is True

def test_context_builder_includes_accessibility_context():
    token = _register_user("ctx_a11y@example.com")
    _onboard_user(token, {
        "accessibility_mode_enabled": True,
        "accessibility_profile": "LOW_LITERACY",
    })
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "ctx_a11y@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "=== ACCESSIBILITY CONTEXT ===" in ctx
    assert "Accessibility Mode: ENABLED" in ctx
    assert "Accessibility Profile: LOW_LITERACY" in ctx

def test_visual_assist_removes_visual_reference_instructions():
    token = _register_user("visual_assist@example.com")
    _onboard_user(token, {
        "accessibility_mode_enabled": True,
        "accessibility_profile": "VISUAL_ASSIST",
    })
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "visual_assist@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "Avoid Visual-Only References: YES" in ctx
    assert "DO NOT say 'look at the graph'" in ctx

def test_low_literacy_produces_simplified_communication_instructions():
    token = _register_user("low_lit@example.com")
    _onboard_user(token, {
        "accessibility_mode_enabled": True,
        "accessibility_profile": "LOW_LITERACY",
    })
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "low_lit@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "Use short, everyday sentences and plain spoken language." in ctx

def test_elderly_friendly_produces_patient_step_by_step_instructions():
    token = _register_user("elderly@example.com")
    _onboard_user(token, {
        "accessibility_mode_enabled": True,
        "accessibility_profile": "ELDERLY_FRIENDLY",
    })
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "elderly@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "Use a calm, patient, slower-paced explanation style." in ctx

def test_voice_assist_produces_audio_optimized_instructions():
    token = _register_user("voice_assist@example.com")
    _onboard_user(token, {
        "accessibility_mode_enabled": True,
        "accessibility_profile": "VOICE_ASSIST",
    })
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "voice_assist@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "Format responses for optimal audio listening" in ctx

def test_accessibility_mode_can_be_disabled():
    token = _register_user("disable_a11y@example.com")
    _onboard_user(token, {"accessibility_mode_enabled": True, "accessibility_profile": "VISUAL_ASSIST"})
    prof_off = _onboard_user(token, {"accessibility_mode_enabled": False, "accessibility_profile": "STANDARD"})
    assert prof_off["accessibility_mode_enabled"] is False
    assert prof_off["accessibility_profile"] == "STANDARD"

def test_backward_compatibility_prompts_1_to_12_remains_intact():
    token = _register_user("regr_a11y@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    _onboard_user(token)

    # Verify Twin
    twin_res = client.put("/api/financial-twin/generate", headers=headers)
    assert twin_res.status_code == 200

    # Verify Chat
    chat_res = client.post("/api/saarthi/chat", json={"message": "Mujhe bachat ke bare me batao"}, headers=headers)
    assert chat_res.status_code == 200

    # Verify Schemes
    sch_res = client.get("/api/schemes/recommendations", headers=headers)
    assert sch_res.status_code == 200

    # Verify Recommendations
    rec_res = client.get("/api/recommendations", headers=headers)
    assert rec_res.status_code == 200
