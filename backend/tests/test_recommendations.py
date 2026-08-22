import os
os.environ["DATABASE_URL"] = "sqlite:///./test_dhan_saarthi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-rec"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.recommendation import FinancialRecommendationSnapshot
from app.models.user import User
from app.services.financial_priority_service import FinancialPriorityService

engine = create_engine("sqlite:///./test_dhan_saarthi.db", connect_args={"check_same_thread": False})
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

def _register_and_onboard(email: str = "rec@example.com", income: float = 60000.0, expenses: float = 30000.0, savings: float = 45000.0) -> str:
    res = client.post("/api/auth/register", json={"full_name": "Recommendation Tester", "email": email, "password": "password123"})
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/api/profile", json={
        "age": 28,
        "occupation": "Engineer",
        "monthly_income": income,
        "monthly_expenses": expenses,
        "savings": savings,
        "financial_goal": "Home Purchase",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
    }, headers=headers)
    return token

# --- TESTS ---

def test_emergency_buffer_critical_classification():
    buf = FinancialPriorityService.analyze_emergency_buffer(savings=10000.0, monthly_expenses=30000.0)
    assert buf.status == "CRITICAL_BUFFER"
    assert buf.coverage_months == 0.33

def test_emergency_buffer_low_classification():
    buf = FinancialPriorityService.analyze_emergency_buffer(savings=60000.0, monthly_expenses=30000.0)
    assert buf.status == "LOW_BUFFER"
    assert buf.coverage_months == 2.0

def test_emergency_buffer_moderate_classification():
    buf = FinancialPriorityService.analyze_emergency_buffer(savings=120000.0, monthly_expenses=30000.0)
    assert buf.status == "MODERATE_BUFFER"
    assert buf.coverage_months == 4.0

def test_emergency_buffer_strong_classification():
    buf = FinancialPriorityService.analyze_emergency_buffer(savings=200000.0, monthly_expenses=30000.0)
    assert buf.status == "STRONG_BUFFER"
    assert buf.coverage_months == 6.67

def test_emergency_buffer_zero_expenses_handling():
    buf = FinancialPriorityService.analyze_emergency_buffer(savings=50000.0, monthly_expenses=0.0)
    assert buf.status == "INSUFFICIENT_DATA"

def test_recommendation_endpoint_authenticated():
    token = _register_and_onboard("rec_auth@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/recommendations", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "top_priority" in data
    assert "allocation_guidance" in data
    assert data["monthly_capacity"]["surplus"] == 30000.0

def test_recommendation_generation_endpoint():
    token = _register_and_onboard("rec_gen@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/recommendations/generate", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["recommendation_status"] == "ACTIVE"

def test_data_completeness_disclosure():
    token = _register_and_onboard("rec_comp@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/recommendations", headers=headers)
    data = res.json()
    assert data["data_completeness"] in ["COMPLETE", "PARTIAL", "INSUFFICIENT"]
    assert "Debt and insurance" in data["data_completeness_note"]

def test_allocation_ranges_within_surplus_capacity():
    token = _register_and_onboard("rec_alloc@example.com", income=80000.0, expenses=40000.0, savings=100000.0)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/recommendations", headers=headers)
    data = res.json()
    surplus = data["monthly_capacity"]["surplus"]
    assert surplus == 40000.0
    for item in data["allocation_guidance"]:
        assert item["suggested_range_min"] <= item["suggested_range_max"]
        assert item["suggested_range_max"] <= surplus

def test_goal_aware_recommendations():
    token = _register_and_onboard("rec_goal@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/planning/goals", json={
        "name": "New Car",
        "category": "vehicle",
        "target_amount": 500000,
        "current_amount": 50000,
        "target_date": "2027-12-31"
    }, headers=headers)

    res = client.get("/api/recommendations", headers=headers)
    data = res.json()
    assert len(data["goal_considerations"]) >= 1
    g_item = data["goal_considerations"][0]
    assert g_item["goal_name"] == "New Car"

def test_no_fabricated_expected_returns():
    token = _register_and_onboard("rec_nofake@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/recommendations", headers=headers)
    data = res.json()
    json_str = str(data)
    assert "guaranteed" not in json_str.lower() or "not guarantee" in json_str.lower()

def test_stale_market_data_warning():
    token = _register_and_onboard("rec_stale@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/recommendations", headers=headers)
    data = res.json()
    assert "warning_note" in data["market_context_summary"]

def test_user_ownership_isolation():
    token1 = _register_and_onboard("user1_rec@example.com")
    token2 = _register_and_onboard("user2_rec@example.com")

    res1 = client.get("/api/recommendations", headers={"Authorization": f"Bearer {token1}"})
    res2 = client.get("/api/recommendations", headers={"Authorization": f"Bearer {token2}"})

    assert res1.json()["recommendation_id"] != res2.json()["recommendation_id"]

def test_recommendation_snapshot_persisted():
    token = _register_and_onboard("rec_db@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/recommendations", headers=headers)
    assert res.status_code == 200

    db = TestingSessionLocal()
    count = db.scalar(select(FinancialRecommendationSnapshot))
    db.close()
    assert count is not None

def test_context_builder_includes_recommendations():
    from app.services.context_builder import ContextBuilder
    token = _register_and_onboard("rec_ctx@example.com")
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "rec_ctx@example.com"))
    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "PERSONALIZED FINANCIAL RECOMMENDATIONS" in ctx
    assert "Top Financial Priority:" in ctx
