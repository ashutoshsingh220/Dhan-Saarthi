from datetime import date, timedelta
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

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


def register_and_onboard(email: str, name: str, income: float = 60000, expenses: float = 30000) -> str:
    res = client.post("/api/auth/register", json={"full_name": name, "email": email, "password": "password123"})
    token = res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/api/profile",
        headers=auth_headers,
        json={
            "age": 30,
            "occupation": "Engineer",
            "monthly_income": income,
            "monthly_expenses": expenses,
            "savings": 100000,
            "financial_goal": "Home Purchase",
            "risk_preference": "moderate",
            "preferred_language": "English",
            "accessibility_mode": "standard",
        },
    )
    client.put("/api/financial-twin/generate", headers=auth_headers)
    return token


def test_goal_validation():
    token = register_and_onboard("test_val@example.com", "Val User")
    headers = {"Authorization": f"Bearer {token}"}

    # Past date rejection
    past_date = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
    res = client.post("/api/planning/goals", headers=headers, json={
        "name": "Past Goal",
        "category": "emergency_fund",
        "target_amount": 100000,
        "current_amount": 0,
        "target_date": past_date
    })
    assert res.status_code == 400

    # Negative amount rejection
    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    res2 = client.post("/api/planning/goals", headers=headers, json={
        "name": "Negative Goal",
        "category": "emergency_fund",
        "target_amount": -5000,
        "current_amount": 0,
        "target_date": future_date
    })
    assert res2.status_code == 422


def test_goal_creation_and_deterministic_planning():
    token = register_and_onboard("planner@example.com", "Planner User", income=100000, expenses=50000)
    headers = {"Authorization": f"Bearer {token}"}

    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    res = client.post("/api/planning/goals", headers=headers, json={
        "name": "House Downpayment",
        "category": "home",
        "target_amount": 240000,
        "current_amount": 0,
        "target_date": future_date
    })

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "House Downpayment"
    assert "plan" in data
    plan = data["plan"]

    # Available capacity = 100,000 - 50,000 = 50,000
    # Remaining = 240,000 over 12 months = 20,000/month
    # 50,000 >= 20,000 -> FEASIBLE
    assert plan["available_monthly_capacity"] == 50000.0
    assert plan["monthly_required"] == 20000.0
    assert plan["feasibility_status"] == "FEASIBLE"
    assert len(plan["milestones"]) == 4


def test_tight_and_at_risk_feasibility_classification():
    # User surplus = 15,000
    token = register_and_onboard("tight@example.com", "Tight User", income=45000, expenses=30000)
    headers = {"Authorization": f"Bearer {token}"}

    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")

    # Tight goal: required 18,000/mo (surplus 15,000 is between 75% and 100% of 18,000)
    res_tight = client.post("/api/planning/goals", headers=headers, json={
        "name": "Car Purchase",
        "category": "vehicle",
        "target_amount": 216000,
        "current_amount": 0,
        "target_date": future_date
    })
    assert res_tight.status_code == 201
    assert res_tight.json()["plan"]["feasibility_status"] == "TIGHT"

    # At Risk goal: required 40,000/mo (surplus 15,000 is < 75% of 40,000)
    res_risk = client.post("/api/planning/goals", headers=headers, json={
        "name": "Luxury Villa",
        "category": "home",
        "target_amount": 480000,
        "current_amount": 0,
        "target_date": future_date
    })
    assert res_risk.status_code == 201
    assert res_risk.json()["plan"]["feasibility_status"] == "AT_RISK"


def test_progress_tracking_and_goal_completion():
    token = register_and_onboard("progress@example.com", "Progress User")
    headers = {"Authorization": f"Bearer {token}"}

    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    res = client.post("/api/planning/goals", headers=headers, json={
        "name": "Emergency Fund",
        "category": "emergency_fund",
        "target_amount": 50000,
        "current_amount": 10000,
        "target_date": future_date
    })
    goal_id = res.json()["id"]

    # Add 40,000 progress (reaches 50,000 target)
    res_prog = client.post(f"/api/planning/goals/{goal_id}/progress", headers=headers, json={"amount": 40000})
    assert res_prog.status_code == 200
    updated = res_prog.json()
    assert updated["current_amount"] == 50000.0
    assert updated["status"] == "completed"


def test_planning_security_user_isolation():
    token_a = register_and_onboard("owner_a@example.com", "Owner A")
    token_b = register_and_onboard("attacker_b@example.com", "Attacker B")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    res_a = client.post("/api/planning/goals", headers=headers_a, json={
        "name": "User A Private Goal",
        "category": "travel",
        "target_amount": 100000,
        "current_amount": 10000,
        "target_date": future_date
    })
    goal_id_a = res_a.json()["id"]

    # User B attempts to view User A's goal
    res_get_b = client.get(f"/api/planning/goals/{goal_id_a}", headers=headers_b)
    assert res_get_b.status_code in [403, 404]

    # User B attempts to add progress to User A's goal
    res_prog_b = client.post(f"/api/planning/goals/{goal_id_a}/progress", headers=headers_b, json={"amount": 5000})
    assert res_prog_b.status_code in [403, 404]
