import os

os.environ["DATABASE_URL"] = "sqlite:///./test_dhan_saarthi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.scheme_service import SchemeService

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
    db = TestingSessionLocal()
    SchemeService.seed_initial_schemes(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def _register_and_onboard(email: str, occupation: str = "Farmer", profile_extra: dict = None) -> str:
    res = client.post("/api/auth/register", json={"full_name": "Scheme User", "email": email, "password": "password123"})
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "age": 35,
        "occupation": occupation,
        "monthly_income": 30000,
        "monthly_expenses": 18000,
        "savings": 50000,
        "financial_goal": "Buy tractor",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
    }
    if profile_extra:
        payload.update(profile_extra)
    client.put("/api/profile", json=payload, headers=headers)
    return token


# --- TESTS ---

def test_scheme_catalog_retrieval():
    res = client.get("/api/schemes")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10
    names = [s["short_name"] for s in data]
    assert "PM-KISAN" in names
    assert "PMFBY" in names
    assert "Kisan Credit Card" in names
    assert "MUDRA Yojana" in names
    assert "PMEGP" in names


def test_category_filtering():
    res = client.get("/api/schemes?category=FARMER_SUPPORT")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    for s in data:
        assert s["category"] == "FARMER_SUPPORT" or "FARMER_SUPPORT" in s["tags"]


def test_categories_endpoint_counts():
    res = client.get("/api/schemes/categories")
    assert res.status_code == 200
    cats = res.json()
    assert len(cats) >= 10
    cat_dict = {c["category_id"]: c["count"] for c in cats}
    assert cat_dict["FARMER_SUPPORT"] >= 1
    assert cat_dict["SMALL_BUSINESS"] >= 1


def test_farmer_recommendation_logic():
    token = _register_and_onboard("farmer_p9@example.com", occupation="Farmer")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/schemes/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) >= 1
    top_scheme = recs[0]["scheme"]["short_name"]
    assert top_scheme in ["PM-KISAN", "PMFBY", "Kisan Credit Card", "AIF"]
    assert recs[0]["relevance_rank"] in ["HIGHLY_RELEVANT", "RELEVANT"]


def test_business_recommendation_logic():
    token = _register_and_onboard("biz_p9@example.com", occupation="Shopkeeper", profile_extra={"occupation_status": "BUSINESS_OWNER"})
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/schemes/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    top_names = [r["scheme"]["short_name"] for r in recs[:3]]
    assert any(name in top_names for name in ["MUDRA Yojana", "PMEGP", "Stand-Up India"])


def test_rural_user_recommendation_logic():
    token = _register_and_onboard("rural_p9@example.com", occupation="Handicraft Maker")
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/api/profile/support-context", headers=headers, json={"rural_or_urban": "RURAL", "business_interest": True})
    res = client.get("/api/schemes/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    rec_names = [r["scheme"]["short_name"] for r in recs]
    assert "PMEGP" in rec_names or "PMFME" in rec_names


def test_relevance_ranking_determinism():
    token = _register_and_onboard("det_p9@example.com", occupation="Farmer")
    headers = {"Authorization": f"Bearer {token}"}
    res1 = client.get("/api/schemes/recommendations", headers=headers).json()
    res2 = client.get("/api/schemes/recommendations", headers=headers).json()
    assert [r["scheme"]["id"] for r in res1] == [r["scheme"]["id"] for r in res2]


def test_eligibility_classification_determinism():
    token = _register_and_onboard("elig_p9@example.com", occupation="Farmer")
    headers = {"Authorization": f"Bearer {token}"}
    schemes = client.get("/api/schemes").json()
    pmkisan = next(s for s in schemes if s["short_name"] == "PM-KISAN")

    res = client.post(f"/api/schemes/{pmkisan['scheme_id']}/eligibility-check", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["eligibility_status"] in ["POTENTIALLY_ELIGIBLE", "LIKELY_RELEVANT"]
    assert "disclaimer" in data
    assert "official_url" in data
    assert len(data["match_reasons"]) >= 1


def test_missing_information_classification():
    token = _register_and_onboard("noinfo_p9@example.com", occupation="Other")
    headers = {"Authorization": f"Bearer {token}"}
    schemes = client.get("/api/schemes").json()
    pmfme = next(s for s in schemes if s["short_name"] == "PMFME")

    res = client.post(f"/api/schemes/{pmfme['scheme_id']}/eligibility-check", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["missing_information"]) >= 1


def test_invalid_area_type_validation():
    token = _register_and_onboard("invalidarea_p9@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.put("/api/profile/support-context", headers=headers, json={"rural_or_urban": "METRO_CITY"})
    assert res.status_code == 422


def test_scheme_detail_retrieval():
    schemes = client.get("/api/schemes").json()
    target = schemes[0]
    res = client.get(f"/api/schemes/{target['scheme_id']}")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == target["name"]
    assert "required_documents" in data
    assert "how_to_apply" in data


def test_official_url_presence_for_seeded_schemes():
    schemes = client.get("/api/schemes").json()
    for s in schemes:
        assert s["official_url"].startswith("http")
        assert s["official_authority"] != ""
        assert s["source_last_verified_at"] != ""


def test_support_context_user_isolation():
    token_a = _register_and_onboard("user_a_p9@example.com")
    token_b = _register_and_onboard("user_b_p9@example.com")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    client.put("/api/profile/support-context", headers=headers_a, json={"state": "Maharashtra", "rural_or_urban": "RURAL"})
    client.put("/api/profile/support-context", headers=headers_b, json={"state": "Punjab", "rural_or_urban": "URBAN"})

    profile_a = client.get("/api/profile", headers=headers_a).json()
    profile_b = client.get("/api/profile", headers=headers_b).json()

    assert profile_a["state"] == "Maharashtra"
    assert profile_b["state"] == "Punjab"


def test_ai_context_includes_verified_scheme_facts():
    from app.services.context_builder import ContextBuilder
    db = TestingSessionLocal()
    token = _register_and_onboard("aicontext_p9@example.com", occupation="Farmer")
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/api/profile/support-context", headers=headers, json={"state": "Rajasthan", "rural_or_urban": "RURAL", "farm_activity": "CROP_FARMING"})

    from app.models.user import User
    user = db.scalar(select(User).where(User.email == "aicontext_p9@example.com"))
    ctx = ContextBuilder.build_user_context(user)
    db.close()

    assert "GOVERNMENT SCHEME SUPPORT CONTEXT" in ctx
    assert "State / District: Rajasthan" in ctx
    assert "Area Type: RURAL" in ctx
