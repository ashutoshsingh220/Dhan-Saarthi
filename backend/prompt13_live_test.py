import os
os.environ["DATABASE_URL"] = "sqlite:///./test_prompt13_live.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-prompt13-live"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

engine = create_engine("sqlite:///./test_prompt13_live.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_prompt13_live_verification():
    print("==================================================================")
    print("PROMPT 13 LIVE E2E VERIFICATION SCRIPT")
    print("==================================================================")

    # 1. Clean Database Initialization
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[1/15] Database initialized cleanly.")

    # 2. Register & Auth
    reg = client.post("/api/auth/register", json={
        "full_name": "Laxmi Devi",
        "email": "laxmi_a11y@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2/15] User registration successful.")

    # 3. Standard Profile Onboarding
    prof1 = client.put("/api/profile", json={
        "age": 55,
        "occupation": "Homemaker",
        "monthly_income": 30000,
        "monthly_expenses": 18000,
        "savings": 45000,
        "financial_goal": "Family Security",
        "risk_preference": "low",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard",
    }, headers=headers)
    assert prof1.status_code == 200
    print("[3/15] Standard profile onboarding completed.")

    # 4. Save Accessibility Preferences (VISUAL_ASSIST)
    prof2 = client.put("/api/profile", json={
        "age": 55,
        "occupation": "Homemaker",
        "monthly_income": 30000,
        "monthly_expenses": 18000,
        "savings": 45000,
        "financial_goal": "Family Security",
        "risk_preference": "low",
        "preferred_language": "Hindi",
        "accessibility_mode": "voice_first",
        "accessibility_mode_enabled": True,
        "accessibility_profile": "VISUAL_ASSIST",
        "text_size_preference": "LARGE",
        "high_contrast_enabled": True,
        "voice_navigation_enabled": True,
        "sequential_navigation_enabled": True,
    }, headers=headers)
    assert prof2.status_code == 200
    print("[4/15] Saved Accessibility Preferences (VISUAL_ASSIST, Large Text, High Contrast).")

    # 5. GET /api/profile Verification
    get_prof = client.get("/api/profile", headers=headers)
    assert get_prof.status_code == 200
    data = get_prof.json()
    assert data["accessibility_mode_enabled"] is True
    assert data["accessibility_profile"] == "VISUAL_ASSIST"
    assert data["text_size_preference"] == "LARGE"
    assert data["high_contrast_enabled"] is True
    print("[5/15] GET /api/profile verified accessibility fields.")

    # 6. ContextBuilder VISUAL_ASSIST Rules
    from app.services.context_builder import ContextBuilder
    db = TestingSessionLocal()
    user_obj = db.scalar(select(User).where(User.email == "laxmi_a11y@example.com"))
    ctx1 = ContextBuilder.build_user_context(user_obj, db=db)
    db.close()
    assert "Accessibility Profile: VISUAL_ASSIST" in ctx1
    assert "Avoid Visual-Only References: YES" in ctx1
    print("[6/15] ContextBuilder generated VISUAL_ASSIST rules (avoid visual spatial references).")

    # 7. ContextBuilder LOW_LITERACY Rules
    client.put("/api/profile", json={
        "age": 55, "occupation": "Homemaker", "monthly_income": 30000, "monthly_expenses": 18000,
        "savings": 45000, "financial_goal": "Family Security", "risk_preference": "low",
        "accessibility_mode_enabled": True, "accessibility_profile": "LOW_LITERACY"
    }, headers=headers)
    db = TestingSessionLocal()
    user_obj = db.scalar(select(User).where(User.email == "laxmi_a11y@example.com"))
    ctx2 = ContextBuilder.build_user_context(user_obj, db=db)
    db.close()
    assert "Accessibility Profile: LOW_LITERACY" in ctx2
    assert "Use short, everyday sentences and plain spoken language." in ctx2
    print("[7/15] ContextBuilder generated LOW_LITERACY simplified communication rules.")

    # 8. ContextBuilder ELDERLY_FRIENDLY Rules
    client.put("/api/profile", json={
        "age": 55, "occupation": "Homemaker", "monthly_income": 30000, "monthly_expenses": 18000,
        "savings": 45000, "financial_goal": "Family Security", "risk_preference": "low",
        "accessibility_mode_enabled": True, "accessibility_profile": "ELDERLY_FRIENDLY"
    }, headers=headers)
    db = TestingSessionLocal()
    user_obj = db.scalar(select(User).where(User.email == "laxmi_a11y@example.com"))
    ctx3 = ContextBuilder.build_user_context(user_obj, db=db)
    db.close()
    assert "Accessibility Profile: ELDERLY_FRIENDLY" in ctx3
    assert "Use a calm, patient, slower-paced explanation style." in ctx3
    print("[8/15] ContextBuilder generated ELDERLY_FRIENDLY patient explanation rules.")

    # 9. Invalid Accessibility Profile Rejection
    bad_res = client.put("/api/profile", json={
        "age": 55, "occupation": "Homemaker", "monthly_income": 30000, "monthly_expenses": 18000,
        "savings": 45000, "financial_goal": "Family Security", "risk_preference": "low",
        "accessibility_profile": "SUPER_ACCESSIBLE"
    }, headers=headers)
    assert bad_res.status_code == 422
    print("[9/15] Invalid accessibility profile rejected (422 Unprocessable Entity).")

    # 10. Disable Accessibility Mode
    off_res = client.put("/api/profile", json={
        "age": 55, "occupation": "Homemaker", "monthly_income": 30000, "monthly_expenses": 18000,
        "savings": 45000, "financial_goal": "Family Security", "risk_preference": "low",
        "accessibility_mode_enabled": False, "accessibility_profile": "STANDARD"
    }, headers=headers)
    assert off_res.status_code == 200
    assert off_res.json()["accessibility_mode_enabled"] is False
    print("[10/15] Disabled Accessibility Mode successfully.")

    # 11. AI Saarthi Chat Operational
    chat_res = client.post("/api/saarthi/chat", json={"message": "Mujhe bachat ke bare me batao"}, headers=headers)
    assert chat_res.status_code == 200
    print("[11/15] AI Saarthi Chat operational.")

    # 12. Financial Twin Operational
    twin_res = client.put("/api/financial-twin/generate", headers=headers)
    assert twin_res.status_code == 200
    print("[12/15] Financial Twin operational.")

    # 13. Personalized Recommendations Operational
    rec_res = client.get("/api/recommendations", headers=headers)
    assert rec_res.status_code == 200
    print("[13/15] Personalized Recommendations operational.")

    # 14. Market Intelligence Operational
    mkt_res = client.get("/api/market/overview")
    assert mkt_res.status_code == 200
    print("[14/15] Market Intelligence operational.")

    # 15. Government Schemes Operational
    sch_res = client.get("/api/schemes/recommendations", headers=headers)
    assert sch_res.status_code == 200
    print("[15/15] Government Schemes operational.")

    print("\n==================================================================")
    print("ALL 15 LIVE E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_prompt13_live_verification()
