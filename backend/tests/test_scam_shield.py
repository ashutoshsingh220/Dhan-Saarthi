import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.scam_detection_service import ScamDetectionService

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


def register_user(email: str, name: str) -> dict:
    res = client.post("/api/auth/register", json={"full_name": name, "email": email, "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def test_scam_service_determinism_and_false_positive():
    # 1. Safe message test (LOW risk)
    safe_text = "Your monthly bank statement is ready. You can view it securely through the official banking application."
    res_safe = ScamDetectionService.analyze(safe_text)
    assert res_safe["risk_score"] == 0
    assert res_safe["risk_level"] == "LOW"
    assert len(res_safe["indicators"]) == 0

    # 2. Determinism test
    res_safe_again = ScamDetectionService.analyze(safe_text)
    assert res_safe == res_safe_again

    # 3. Moderate risk test (25-49)
    mod_text = "Congratulations SBI Customer! You won a cash prize reward. Claim your reward today only!"
    res_mod = ScamDetectionService.analyze(mod_text)
    assert 25 <= res_mod["risk_score"] < 50
    assert res_mod["risk_level"] == "MODERATE"

    # 4. High risk test (50-74)
    high_text = "Your account is suspended immediately. Send money or pay now for verification."
    res_high = ScamDetectionService.analyze(high_text)
    assert 50 <= res_high["risk_score"] < 75
    assert res_high["risk_level"] == "HIGH"

    # 5. Critical risk test (75-100)
    crit_text = "Urgent: Your SBI bank account will be blocked immediately due to KYC failure. Verify PAN now at http://bit.ly/fake-bank and enter your OTP."
    res_crit = ScamDetectionService.analyze(crit_text)
    assert res_crit["risk_score"] >= 75
    assert res_crit["risk_level"] == "CRITICAL"

    # Ordering check: Safe < Moderate < High < Critical
    assert res_safe["risk_score"] < res_mod["risk_score"] < res_high["risk_score"] < res_crit["risk_score"]


def test_scam_unauthorized():
    response = client.post("/api/scam-shield/analyze", json={"message": "Urgent bank update"})
    assert response.status_code == 401


def test_scam_empty_message_validation():
    headers = register_user("user_val@example.com", "Validation User")
    response = client.post("/api/scam-shield/analyze", json={"message": "  hi  "}, headers=headers)
    assert response.status_code == 422


def test_scam_analyze_and_persistence():
    headers = register_user("user_scam@example.com", "Scam User")
    msg = "Your account is suspended immediately. Send money verification fee to http://scam.link or enter PIN."
    response = client.post("/api/scam-shield/analyze", json={"message": msg}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["risk_score"] >= 50
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert len(data["indicators"]) > 0
    assert len(data["recommended_actions"]) > 0

    scan_id = data["id"]

    # History retrieval
    hist_resp = client.get("/api/scam-shield/history", headers=headers)
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["total_count"] >= 1
    assert hist_data["scans"][0]["id"] == scan_id

    # Detail retrieval
    detail_resp = client.get(f"/api/scam-shield/history/{scan_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == scan_id


def test_scam_ownership_security_isolation():
    headers_a = register_user("usera_scam@example.com", "User A")
    headers_b = register_user("userb_scam@example.com", "User B")

    # User A creates a scan
    msg = "Urgent: Card blocked immediately! Enter OTP at http://fake.url"
    resp_a = client.post("/api/scam-shield/analyze", json={"message": msg}, headers=headers_a)
    assert resp_a.status_code == 201
    scan_id = resp_a.json()["id"]

    # User B attempts to view User A's scan
    resp_b_view = client.get(f"/api/scam-shield/history/{scan_id}", headers=headers_b)
    assert resp_b_view.status_code in [403, 404]

    # User B attempts to delete User A's scan
    resp_b_del = client.delete(f"/api/scam-shield/history/{scan_id}", headers=headers_b)
    assert resp_b_del.status_code in [403, 404]

    # User A deletes own scan successfully
    resp_a_del = client.delete(f"/api/scam-shield/history/{scan_id}", headers=headers_a)
    assert resp_a_del.status_code == 204
