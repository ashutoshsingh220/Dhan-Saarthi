import os

os.environ["DATABASE_URL"] = "sqlite:///./test_dhan_saarthi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.personalization_service import (
    EDUCATION_LEVELS,
    EXPLANATION_LEVELS,
    FINANCIAL_KNOWLEDGE_LEVELS,
    OCCUPATION_STATUSES,
    calculate_age,
)

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


def _register_and_onboard(email: str, personalization: dict = None) -> str:
    res = client.post("/api/auth/register", json={"full_name": "Test User", "email": email, "password": "password123"})
    assert res.status_code == 201, f"Register failed: {res.json()}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "age": 30,
        "occupation": "Engineer",
        "monthly_income": 80000,
        "monthly_expenses": 40000,
        "savings": 200000,
        "financial_goal": "Buy a car",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
    }
    if personalization:
        payload.update(personalization)
    client.put("/api/profile", json=payload, headers=headers)
    return token


# ---------------------------------------------------------------------------
# Unit tests for personalization service
# ---------------------------------------------------------------------------

def test_calculate_age_birthday_occurred():
    today = date(2025, 8, 22)
    dob = date(1995, 6, 15)
    assert calculate_age(dob, today) == 30


def test_calculate_age_birthday_not_yet():
    today = date(2025, 8, 22)
    dob = date(1995, 9, 1)
    assert calculate_age(dob, today) == 29


def test_calculate_age_birthday_exact():
    today = date(2025, 8, 22)
    dob = date(1995, 8, 22)
    assert calculate_age(dob, today) == 30


def test_enum_values_complete():
    assert "BEGINNER" in FINANCIAL_KNOWLEDGE_LEVELS
    assert "BASIC" in FINANCIAL_KNOWLEDGE_LEVELS
    assert "INTERMEDIATE" in FINANCIAL_KNOWLEDGE_LEVELS
    assert "ADVANCED" in FINANCIAL_KNOWLEDGE_LEVELS
    assert "SIMPLE" in EXPLANATION_LEVELS
    assert "BALANCED" in EXPLANATION_LEVELS
    assert "DETAILED" in EXPLANATION_LEVELS
    assert "PRIMARY_OR_BELOW" in EDUCATION_LEVELS
    assert "PREFER_NOT_TO_SAY" in EDUCATION_LEVELS
    assert "STUDENT" in OCCUPATION_STATUSES
    assert "PREFER_NOT_TO_SAY" in OCCUPATION_STATUSES


# ---------------------------------------------------------------------------
# API integration tests
# ---------------------------------------------------------------------------

def test_profile_without_personalization_fields():
    token = _register_and_onboard("noperson@p8.com")
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["date_of_birth"] is None
    assert data["education_level"] is None
    assert data["financial_knowledge_level"] is None
    assert data["preferred_explanation_level"] is None
    assert data["occupation_status"] is None
    assert data["derived_age"] is None


def test_profile_with_personalization_fields():
    token = _register_and_onboard("person@p8.com", {
        "date_of_birth": "1995-06-15",
        "education_level": "UNDERGRADUATE",
        "financial_knowledge_level": "BASIC",
        "preferred_explanation_level": "SIMPLE",
        "occupation_status": "SALARIED",
    })
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["education_level"] == "UNDERGRADUATE"
    assert data["financial_knowledge_level"] == "BASIC"
    assert data["preferred_explanation_level"] == "SIMPLE"
    assert data["occupation_status"] == "SALARIED"
    assert data["derived_age"] is not None
    assert isinstance(data["derived_age"], int)
    assert 0 <= data["derived_age"] <= 120


def test_dob_future_date_rejected():
    token = _register_and_onboard("futuredob@p8.com")
    res = client.put("/api/profile", headers={"Authorization": f"Bearer {token}"}, json={
        "age": 25, "occupation": "Engineer", "monthly_income": 50000,
        "monthly_expenses": 25000, "savings": 100000, "financial_goal": "Save",
        "risk_preference": "low", "preferred_language": "English", "accessibility_mode": "standard",
        "date_of_birth": "2099-01-01",
    })
    assert res.status_code == 422


def test_invalid_education_level_rejected():
    token = _register_and_onboard("invalidedu@p8.com")
    res = client.put("/api/profile", headers={"Authorization": f"Bearer {token}"}, json={
        "age": 25, "occupation": "Engineer", "monthly_income": 50000,
        "monthly_expenses": 25000, "savings": 100000, "financial_goal": "Save",
        "risk_preference": "low", "preferred_language": "English", "accessibility_mode": "standard",
        "education_level": "PHONO_GRAD",
    })
    assert res.status_code == 422


def test_invalid_financial_knowledge_rejected():
    token = _register_and_onboard("invalidfk@p8.com")
    res = client.put("/api/profile", headers={"Authorization": f"Bearer {token}"}, json={
        "age": 25, "occupation": "Engineer", "monthly_income": 50000,
        "monthly_expenses": 25000, "savings": 100000, "financial_goal": "Save",
        "risk_preference": "low", "preferred_language": "English", "accessibility_mode": "standard",
        "financial_knowledge_level": "EXPERT",
    })
    assert res.status_code == 422


def test_invalid_explanation_level_rejected():
    token = _register_and_onboard("invalidexp@p8.com")
    res = client.put("/api/profile", headers={"Authorization": f"Bearer {token}"}, json={
        "age": 25, "occupation": "Engineer", "monthly_income": 50000,
        "monthly_expenses": 25000, "savings": 100000, "financial_goal": "Save",
        "risk_preference": "low", "preferred_language": "English", "accessibility_mode": "standard",
        "preferred_explanation_level": "EXPERT",
    })
    assert res.status_code == 422


def test_derived_age_is_server_side():
    '''Derived age is calculated from DOB, not the profile age field.'''
    token = _register_and_onboard("dob_age_test@p8.com", {
        "age": 99,
        "date_of_birth": "1995-06-15",
    })
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["derived_age"] != 99
    assert 20 <= data["derived_age"] <= 50


def test_personalization_fields_can_be_cleared():
    token = _register_and_onboard("clearperson@p8.com", {
        "education_level": "UNDERGRADUATE",
        "financial_knowledge_level": "INTERMEDIATE",
    })
    headers = {"Authorization": f"Bearer {token}"}
    res = client.put("/api/profile", headers=headers, json={
        "age": 30, "occupation": "Engineer", "monthly_income": 80000,
        "monthly_expenses": 40000, "savings": 200000, "financial_goal": "Buy a car",
        "risk_preference": "moderate", "preferred_language": "English", "accessibility_mode": "standard",
        "education_level": None,
        "financial_knowledge_level": None,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["education_level"] is None
    assert data["financial_knowledge_level"] is None


def test_prefer_not_to_say_accepted():
    token = _register_and_onboard("prefernot@p8.com", {
        "education_level": "PREFER_NOT_TO_SAY",
        "occupation_status": "PREFER_NOT_TO_SAY",
    })
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["education_level"] == "PREFER_NOT_TO_SAY"
    assert data["occupation_status"] == "PREFER_NOT_TO_SAY"


def test_prompt8a_separate_total_and_monthly_savings():
    """Verify Age, Total Savings, and Monthly Savings persist separately."""
    token = _register_and_onboard("savings_test@p8.com", {
        "monthly_savings": 25000,
        "total_savings": 300000,
    })
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert float(data["monthly_savings"]) == 25000
    assert float(data["total_savings"]) == 300000
    assert data["age"] == 30



def test_prompt8a_invalid_age_rejected():
    """Verify age boundaries (1-120)."""
    token = _register_and_onboard("age_boundary@p8.com")
    res = client.put("/api/profile", headers={"Authorization": f"Bearer {token}"}, json={
        "age": 150, "occupation": "Engineer", "monthly_income": 50000,
        "monthly_expenses": 25000, "savings": 100000, "financial_goal": "Save",
        "risk_preference": "low", "preferred_language": "English", "accessibility_mode": "standard",
    })
    assert res.status_code == 422

