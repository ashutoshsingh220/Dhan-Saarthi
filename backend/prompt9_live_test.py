import os
os.environ["DATABASE_URL"] = "sqlite:///./test_prompt9_live.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-prompt9-live"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.scheme_service import SchemeService

engine = create_engine("sqlite:///./test_prompt9_live.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_prompt9_live_verification():
    print("==================================================================")
    print("PROMPT 9 LIVE E2E VERIFICATION SCRIPT")
    print("==================================================================")

    # 1. Reset Database & Seed Schemes
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_count = SchemeService.seed_initial_schemes(db)
    db.close()
    print(f"[1/10] Database initialized cleanly. Seeded {seed_count} schemes.")

    # 2. Register & Auth
    reg = client.post("/api/auth/register", json={
        "full_name": "Sita Devi",
        "email": "sita@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2/10] User registration & auth successful.")

    # 3. Setup Profile & Personalization
    prof_res = client.put("/api/profile", json={
        "age": 32,
        "gender": "Female",
        "occupation": "Dairy & Crop Farmer",
        "city": "Nashik",
        "monthly_income": 25000,
        "monthly_expenses": 15000,
        "savings": 40000,
        "financial_goal": "Buy Dairy Processing Equipment",
        "risk_preference": "moderate",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard",
        "date_of_birth": "1994-04-10",
        "education_level": "SECONDARY",
        "financial_knowledge_level": "BASIC",
        "preferred_explanation_level": "SIMPLE",
        "occupation_status": "FARMER"
    }, headers=headers)
    assert prof_res.status_code == 200
    print("[3/10] Profile & Personalization updated.")

    # 4. Set Farmer / Rural Support Context
    ctx_res = client.put("/api/profile/support-context", json={
        "state": "Maharashtra",
        "district": "Nashik",
        "rural_or_urban": "RURAL",
        "farming_interest": True,
        "business_interest": False,
        "farm_activity": "DAIRY"
    }, headers=headers)
    assert ctx_res.status_code == 200
    assert ctx_res.json()["state"] == "Maharashtra"
    print("[4/10] Support context updated (Rural, Maharashtra, Dairy Farmer).")

    # 5. Fetch Farmer Scheme Recommendations
    farmer_recs_res = client.get("/api/schemes/recommendations", headers=headers)
    assert farmer_recs_res.status_code == 200
    f_recs = farmer_recs_res.json()
    assert len(f_recs) >= 3
    top_farmer_scheme = f_recs[0]["scheme"]["short_name"]
    print(f"[5/10] Top Farmer Recommendation: {top_farmer_scheme} (Rank: {f_recs[0]['relevance_rank']})")

    # 6. Switch to Small Business / Women Entrepreneurship Context & Verify Recommendations
    ctx_biz_res = client.put("/api/profile/support-context", json={
        "state": "Maharashtra",
        "district": "Nashik",
        "rural_or_urban": "RURAL",
        "farming_interest": False,
        "business_interest": True,
        "business_stage": "STARTING",
        "business_sector": "FOOD_PROCESSING"
    }, headers=headers)
    assert ctx_biz_res.status_code == 200

    biz_recs_res = client.get("/api/schemes/recommendations", headers=headers)
    assert biz_recs_res.status_code == 200
    b_recs = biz_recs_res.json()
    top_biz_names = [r["scheme"]["short_name"] for r in b_recs[:4]]
    print(f"[6/10] Top Small Business Recommendations: {', '.join(top_biz_names)}")
    assert any(name in top_biz_names for name in ["Stand-Up India", "PMFME", "PMEGP", "MUDRA Yojana"])

    # 7. Retrieve Scheme Detail by ID
    target_id = b_recs[0]["scheme"]["scheme_id"]
    detail_res = client.get(f"/api/schemes/{target_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["official_url"].startswith("http")
    assert len(detail["required_documents"]) >= 1
    print(f"[7/10] Scheme detail retrieved for '{detail['name']}'. Official URL: {detail['official_url']}")

    # 8. Perform Deterministic Eligibility Check
    elig_res = client.post(f"/api/schemes/{target_id}/eligibility-check", headers=headers)
    assert elig_res.status_code == 200
    elig = elig_res.json()
    assert elig["eligibility_status"] in ["POTENTIALLY_ELIGIBLE", "LIKELY_RELEVANT"]
    assert "disclaimer" in elig
    print(f"[8/10] Deterministic eligibility check executed. Status: {elig['eligibility_status']}")

    # 9. Verify ContextBuilder Integration for AI Saarthi
    from app.services.context_builder import ContextBuilder
    from app.models.user import User
    from sqlalchemy import select
    user_obj = db.scalar(select(User).where(User.email == "sita@example.com"))
    ai_ctx = ContextBuilder.build_user_context(user_obj)
    assert "GOVERNMENT SCHEME SUPPORT CONTEXT" in ai_ctx
    assert "State / District: Maharashtra" in ai_ctx
    assert "Area Type: RURAL" in ai_ctx
    print("[9/10] ContextBuilder generated scheme context block for AI Saarthi.")

    # 10. Security & User Isolation
    reg2 = client.post("/api/auth/register", json={
        "full_name": "Raju Farmer",
        "email": "raju@example.com",
        "password": "password123"
    })
    token2 = reg2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    client.put("/api/profile", json={
        "age": 40,
        "occupation": "Farmer",
        "monthly_income": 20000,
        "monthly_expenses": 12000,
        "savings": 30000,
        "financial_goal": "KCC credit",
        "risk_preference": "low",
        "preferred_language": "English",
        "accessibility_mode": "standard"
    }, headers=headers2)
    client.put("/api/profile/support-context", json={"state": "Punjab", "rural_or_urban": "RURAL"}, headers=headers2)

    prof1 = client.get("/api/profile", headers=headers).json()
    prof2 = client.get("/api/profile", headers=headers2).json()
    assert prof1["state"] == "Maharashtra"
    assert prof2["state"] == "Punjab"
    print("[10/10] Security and user isolation verified across multiple user accounts.")

    print("\n==================================================================")
    print("ALL 10 LIVE E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_prompt9_live_verification()
