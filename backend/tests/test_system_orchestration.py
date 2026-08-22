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
from app.services.context_builder import ContextBuilder
from app.services.financial_priority_orchestrator import FinancialPriorityOrchestrator
from app.services.user_financial_intelligence_service import UserFinancialIntelligenceService

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

def _register_user(email: str = "orchestration_user@example.com") -> str:
    res = client.post("/api/auth/register", json={"full_name": "Vikram Singh", "email": email, "password": "password123"})
    assert res.status_code == 201
    return res.json()["access_token"]

def _onboard_user(token: str, custom_data: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "age": 35,
        "occupation": "Small Business Owner",
        "monthly_income": 60000,
        "monthly_expenses": 35000,
        "savings": 20000, # < 1 month buffer -> CRITICAL_BUFFER
        "financial_goal": "Business Expansion",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
    }
    if custom_data:
        payload.update(custom_data)
    res = client.put("/api/profile", json=payload, headers=headers)
    assert res.status_code == 200
    return res.json()

# --- PROMPT 14 SYSTEM ORCHESTRATION TESTS ---

def test_unified_snapshot_aggregation():
    token = _register_user("snap_agg@example.com")
    _onboard_user(token)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/dashboard/snapshot", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "generated_at" in data
    assert "profile_completeness" in data
    assert "financial_twin" in data
    assert "top_financial_priority" in data
    assert "market_context" in data

def test_todays_financial_brief_endpoint():
    token = _register_user("brief_endpoint@example.com")
    _onboard_user(token)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/dashboard/brief", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "greeting" in data
    assert "summary_sentence" in data
    assert "bullet_points" in data
    assert len(data["bullet_points"]) > 0

def test_scam_priority_overrides_market_awareness():
    # Mock recent high scam scan
    scam = FinancialPriorityOrchestrator.evaluate_top_priority(
        scam_scans=[type("Scam", (), {"risk_level": "HIGH"})()],
        buffer_status="STRONG_BUFFER",
        buffer_coverage=6.0,
        at_risk_goals=[],
        tight_goals=[],
        high_relevance_schemes=[],
        incomplete_learning_modules=[],
        surplus=25000,
        market_pulse="POSITIVE",
    )
    assert scam["priority_category"] == "SCAM_SAFETY"
    assert scam["priority_level"] == "HIGH"
    assert scam["action_route"] == "/domain/scam-shield"

def test_emergency_fund_priority_evaluation():
    p = FinancialPriorityOrchestrator.evaluate_top_priority(
        scam_scans=[],
        buffer_status="CRITICAL_BUFFER",
        buffer_coverage=0.5,
        at_risk_goals=[],
        tight_goals=[],
        high_relevance_schemes=[],
        incomplete_learning_modules=[],
        surplus=10000,
        market_pulse="CALM",
    )
    assert p["priority_category"] == "EMERGENCY_BUFFER"
    assert p["priority_level"] == "CRITICAL"
    assert p["action_route"] == "/domain/recommendations"

def test_goal_at_risk_priority_evaluation():
    p = FinancialPriorityOrchestrator.evaluate_top_priority(
        scam_scans=[],
        buffer_status="STRONG_BUFFER",
        buffer_coverage=6.0,
        at_risk_goals=[type("Goal", (), {"name": "Buy Tractor"})()],
        tight_goals=[],
        high_relevance_schemes=[],
        incomplete_learning_modules=[],
        surplus=5000,
        market_pulse="CALM",
    )
    assert p["priority_category"] == "GOAL_AT_RISK"
    assert p["priority_level"] == "HIGH"
    assert p["action_route"] == "/domain/planning"

def test_government_scheme_priority_evaluation():
    p = FinancialPriorityOrchestrator.evaluate_top_priority(
        scam_scans=[],
        buffer_status="STRONG_BUFFER",
        buffer_coverage=6.0,
        at_risk_goals=[],
        tight_goals=[],
        high_relevance_schemes=[type("Scheme", (), {"scheme_name": "PMMY Mudra"})()],
        incomplete_learning_modules=[],
        surplus=15000,
        market_pulse="CALM",
    )
    assert p["priority_category"] == "GOVERNMENT_SCHEME"
    assert p["action_route"] == "/domain/schemes"

def test_simple_explanation_adaptation_in_brief():
    token = _register_user("simple_brief@example.com")
    _onboard_user(token, {"preferred_explanation_level": "SIMPLE"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/dashboard/brief", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["bullet_points"]) <= 3

def test_detailed_explanation_adaptation_in_brief():
    token = _register_user("detailed_brief@example.com")
    _onboard_user(token, {"preferred_explanation_level": "DETAILED"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/dashboard/brief", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["bullet_points"]) >= 3

def test_context_budget_enforcement():
    db = TestingSessionLocal()
    token = _register_user("budget_user@example.com")
    _onboard_user(token)
    user = db.scalar(select(User).where(User.email == "budget_user@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db, max_char_budget=500)
    db.close()
    assert len(ctx) <= 600 # Fits within budget cap plus warning footer

def test_system_health_endpoint():
    res = client.get("/api/system/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert "gemini" in data
    assert "market_provider" in data
    # Ensure no secrets exposed
    assert "api_key" not in str(data).lower()
    assert "secret" not in str(data).lower()

def test_cross_user_isolation_on_snapshot_and_brief():
    token1 = _register_user("user1_orch@example.com")
    _onboard_user(token1, {"monthly_income": 100000})

    token2 = _register_user("user2_orch@example.com")
    _onboard_user(token2, {"monthly_income": 20000})

    res1 = client.get("/api/dashboard/snapshot", headers={"Authorization": f"Bearer {token1}"})
    res2 = client.get("/api/dashboard/snapshot", headers={"Authorization": f"Bearer {token2}"})

    assert res1.json()["financial_twin"]["income"] == 100000.0
    assert res2.json()["financial_twin"]["income"] == 20000.0
