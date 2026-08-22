import os
os.environ["DATABASE_URL"] = "sqlite:///./test_prompt8_live.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-live"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine("sqlite:///./test_prompt8_live.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_live_verification():
    print("==================================================================")
    print("PROMPT 8 LIVE E2E VERIFICATION SCRIPT")
    print("==================================================================")

    # 1. Reset Database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[1/6] Database initialized cleanly.")

    # 2. Register & Auth
    reg = client.post("/api/auth/register", json={
        "full_name": "Ramesh Kumar",
        "email": "ramesh@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2/6] User registration successful.")

    # 3. Save Extended Profile with Personalization Fields
    profile_payload = {
        "age": 45,
        "gender": "Male",
        "occupation": "Shopkeeper",
        "city": "Jaipur",
        "monthly_income": 45000,
        "monthly_expenses": 30000,
        "savings": 100000,
        "financial_goal": "Children Education",
        "risk_preference": "moderate",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard",
        "date_of_birth": "1980-05-15",
        "education_level": "SECONDARY",
        "financial_knowledge_level": "BASIC",
        "preferred_explanation_level": "SIMPLE",
        "occupation_status": "SELF_EMPLOYED"
    }
    put_res = client.put("/api/profile", json=profile_payload, headers=headers)
    assert put_res.status_code == 200, f"Failed put profile: {put_res.json()}"
    p_data = put_res.json()
    assert p_data["education_level"] == "SECONDARY"
    assert p_data["financial_knowledge_level"] == "BASIC"
    assert p_data["preferred_explanation_level"] == "SIMPLE"
    assert p_data["occupation_status"] == "SELF_EMPLOYED"
    assert p_data["derived_age"] is not None
    assert p_data["derived_age"] == 45 or p_data["derived_age"] == 46  # depending on current year
    print(f"[3/6] Extended Profile saved & verified. Derived Age: {p_data['derived_age']}")

    # 4. Fetch Profile & verify response structure
    get_res = client.get("/api/profile", headers=headers)
    assert get_res.status_code == 200
    g_data = get_res.json()
    assert g_data["derived_age"] == p_data["derived_age"]
    assert g_data["preferred_language"] == "Hindi"
    print("[4/6] GET /api/profile verified.")

    # 5. Invalid Personalization Validation Check (e.g. Future DOB)
    bad_payload = dict(profile_payload)
    bad_payload["date_of_birth"] = "2099-01-01"
    bad_res = client.put("/api/profile", json=bad_payload, headers=headers)
    assert bad_res.status_code == 422
    print("[5/6] Future DOB rejected with 422 as expected.")

    # 6. Update Personalization settings independently
    update_payload = dict(profile_payload)
    update_payload["preferred_explanation_level"] = "BALANCED"
    update_payload["financial_knowledge_level"] = "INTERMEDIATE"
    up_res = client.put("/api/profile", json=update_payload, headers=headers)
    assert up_res.status_code == 200
    up_data = up_res.json()
    assert up_data["preferred_explanation_level"] == "BALANCED"
    assert up_data["financial_knowledge_level"] == "INTERMEDIATE"
    print("[6/6] Personalization settings update verified.")

    print("\n==================================================================")
    print("ALL 6 LIVE E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_live_verification()
