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


def test_new_user_registration_and_login_resilience():
    with TestClient(app) as client:
        # Test registering with spaces and mixed case email
        res = client.post(
            "/api/auth/register",
            json={
                "full_name": "New User",
                "email": "  NewGmailUser@Gmail.Com  ",
                "password": "MyStrongPassword123!",
            },
        )
        assert res.status_code == 201, f"Registration failed: {res.text}"
        data = res.json()
        assert data["user"]["email"] == "newgmailuser@gmail.com"
        assert "access_token" in data

        # Test logging in with clean email
        login_res = client.post(
            "/api/auth/login",
            json={
                "email": "newgmailuser@gmail.com",
                "password": "MyStrongPassword123!",
            },
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        assert "access_token" in login_res.json()

        # Test logging in with mixed-case and trailing whitespace email
        login_res2 = client.post(
            "/api/auth/login",
            json={
                "email": "  NEWGMAILUSER@GMAIL.COM  ",
                "password": "MyStrongPassword123!",
            },
        )
        assert login_res2.status_code == 200, f"Login with whitespace failed: {login_res2.text}"
        assert "access_token" in login_res2.json()
