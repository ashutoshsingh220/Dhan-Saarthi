import os

os.environ["DATABASE_URL"] = "sqlite:///./test_dhan_saarthi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient
from app.db.base import Base
from app.db.session import engine
from app.main import app


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_auth_profile_and_twin_flow():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        registered = client.post("/api/auth/register", json={"full_name": "Asha Sharma", "email": "asha@example.com", "password": "securepass123"})
        assert registered.status_code == 201
        headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
        assert client.get("/api/auth/me", headers=headers).json()["onboarding_complete"] is False
        profile = {"age": 28, "gender": "Female", "occupation": "Designer", "city": "Pune", "monthly_income": 60000, "monthly_expenses": 35000, "savings": 120000, "financial_goal": "Buy a home", "risk_preference": "moderate", "preferred_language": "Hindi", "accessibility_mode": "standard"}
        assert client.put("/api/profile", json=profile, headers=headers).status_code == 200
        twin = client.put("/api/financial-twin/generate", headers=headers)
        assert twin.status_code == 200 and 0 <= twin.json()["financial_health_score"] <= 100
