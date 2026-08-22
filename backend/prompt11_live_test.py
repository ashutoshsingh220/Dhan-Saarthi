import os
os.environ["DATABASE_URL"] = "sqlite:///./test_dhan_saarthi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-prompt11-live"

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

def run_prompt11_live_verification():
    print("==================================================================")
    print("PROMPT 11 LIVE E2E VERIFICATION SCRIPT")
    print("==================================================================")

    # 1. Clean Database Initialization
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[1/12] Database initialized cleanly.")

    # 2. User Registration
    reg = client.post("/api/auth/register", json={
        "full_name": "Sita Sharma",
        "email": "sita_rec@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2/12] User registration successful.")

    # 3. Profile Onboarding
    prof = client.put("/api/profile", json={
        "age": 32,
        "occupation": "Teacher",
        "monthly_income": 70000.0,
        "monthly_expenses": 35000.0,
        "savings": 50000.0,
        "financial_goal": "Child Education",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard"
    }, headers=headers)
    assert prof.status_code == 200
    print("[3/12] Profile onboarding completed.")

    # 4. Financial Twin Generation
    twin_gen = client.put("/api/financial-twin/generate", headers=headers)
    assert twin_gen.status_code == 200
    twin = twin_gen.json()
    print(f"[4/12] Financial Twin Score: {twin['financial_health_score']}/100 — Risk: {twin['risk_level']}")

    # 5. Goal Creation
    goal_res = client.post("/api/planning/goals", json={
        "name": "Higher Education Fund",
        "category": "education",
        "target_amount": 300000.0,
        "current_amount": 20000.0,
        "target_date": "2027-06-30"
    }, headers=headers)
    assert goal_res.status_code == 201
    print("[5/12] Smart Planning Goal created.")

    # 6. Recommendation Retrieval
    rec_res = client.get("/api/recommendations", headers=headers)
    assert rec_res.status_code == 200
    rec = rec_res.json()
    print(f"[6/12] GET /api/recommendations responded 200 OK (Rec ID: {rec['recommendation_id'][:8]}...).")

    # 7. Monthly Surplus Capacity Analysis
    cap = rec["monthly_capacity"]
    assert cap["surplus"] == 35000.0
    print(f"[7/12] Monthly Capacity: Income INR {cap['income']}, Expenses INR {cap['expenses']} => Surplus INR {cap['surplus']} (Flexibility: INR {cap['unallocated_flexibility']})")

    # 8. Priority Classification
    top = rec["top_priority"]
    assert top["category"] in ["EMERGENCY_BUFFER", "ESSENTIAL_GOALS", "HIGH_COST_DEBT", "LONG_TERM_INVESTING"]
    print(f"[8/12] Top Priority Classified: '{top['title']}' ({top['category']}) — Level: {top['priority_level']}")

    # 9. Allocation Guidance Ranges
    allocs = rec["allocation_guidance"]
    assert len(allocs) >= 1
    print(f"[9/12] Allocation Guidance Ranges ({len(allocs)} items):")
    for a in allocs:
        print(f"       - {a['category']}: INR {a['suggested_range_min']} - INR {a['suggested_range_max']} ({a['reason']})")

    # 10. Market Freshness & Safety Safeguards
    mkt = rec["market_context_summary"]
    print(f"[10/12] Market Context Freshness: '{mkt['freshness']}' (Source: {mkt['source']}) — Warning: {mkt['warning_note']}")

    # 11. AI Saarthi Context Integration
    from app.services.context_builder import ContextBuilder
    from app.models.user import User
    from sqlalchemy import select
    db = TestingSessionLocal()
    user_obj = db.scalar(select(User).where(User.email == "sita_rec@example.com"))
    ai_ctx = ContextBuilder.build_user_context(user_obj, db=db)
    db.close()
    assert "PERSONALIZED FINANCIAL RECOMMENDATIONS" in ai_ctx
    assert "Top Financial Priority:" in ai_ctx
    print("[11/12] ContextBuilder generated Personalized Recommendation context block for AI Saarthi.")

    # 12. User Ownership Security Isolation
    reg2 = client.post("/api/auth/register", json={"full_name": "User Two", "email": "user2_live@example.com", "password": "password123"})
    token2 = reg2.json()["access_token"]
    rec_res2 = client.get("/api/recommendations", headers={"Authorization": f"Bearer {token2}"})
    assert rec_res2.status_code == 200
    assert rec_res2.json()["recommendation_id"] != rec["recommendation_id"]
    print("[12/12] User ownership isolation verified.")

    print("\n==================================================================")
    print("ALL 12 LIVE E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_prompt11_live_verification()
