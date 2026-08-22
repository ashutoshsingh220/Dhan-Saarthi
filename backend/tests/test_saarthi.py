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


def register_and_onboard(email: str, name: str) -> str:
    res = client.post("/api/auth/register", json={"full_name": name, "email": email, "password": "password123"})
    token = res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/api/profile",
        headers=auth_headers,
        json={
            "age": 29,
            "occupation": "Analyst",
            "monthly_income": 60000,
            "monthly_expenses": 30000,
            "savings": 100000,
            "financial_goal": "Retirement Fund",
            "risk_preference": "moderate",
            "preferred_language": "English",
            "accessibility_mode": "standard",
        },
    )
    client.put("/api/financial-twin/generate", headers=auth_headers)
    return token


def test_chat_unauthorized():
    res = client.post("/api/saarthi/chat", json={"message": "Hello"})
    assert res.status_code == 401


def test_chat_empty_message():
    token = register_and_onboard("test_empty@example.com", "Test Empty")
    res = client.post("/api/saarthi/chat", json={"message": "   "}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400


def test_chat_flow_and_persistence_mocked():
    token = register_and_onboard("user_a@example.com", "User A")
    headers = {"Authorization": f"Bearer {token}"}

    # Mock Gemini client response
    with patch("app.providers.gemini_client.GeminiClient.generate_response") as mock_gemini:
        mock_gemini.return_value = "This is a mocked AI Saarthi financial advice response."

        # Send first message (creates session)
        res1 = client.post("/api/saarthi/chat", json={"message": "How can I increase my savings buffer?"}, headers=headers)
        assert res1.status_code == 200
        data1 = res1.json()
        assert "session_id" in data1
        assert data1["response"] == "This is a mocked AI Saarthi financial advice response."
        session_id = data1["session_id"]

        # Send follow-up message in same session
        res2 = client.post("/api/saarthi/chat", json={"message": "What should I do next?", "session_id": session_id}, headers=headers)
        assert res2.status_code == 200
        assert res2.json()["session_id"] == session_id

    # Verify session list
    sessions_res = client.get("/api/saarthi/sessions", headers=headers)
    assert sessions_res.status_code == 200
    sessions = sessions_res.json()
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == session_id

    # Verify session messages (user + model messages = 4 messages total for 2 turns)
    msg_res = client.get(f"/api/saarthi/sessions/{session_id}/messages", headers=headers)
    assert msg_res.status_code == 200
    messages = msg_res.json()
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "model"


def test_session_ownership_security_isolation():
    token_a = register_and_onboard("user_owner_a@example.com", "Owner A")
    token_b = register_and_onboard("user_attacker_b@example.com", "Attacker B")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    with patch("app.providers.gemini_client.GeminiClient.generate_response") as mock_gemini:
        mock_gemini.return_value = "User A confidential response."
        res_a = client.post("/api/saarthi/chat", json={"message": "Secret user A query"}, headers=headers_a)
        session_id_a = res_a.json()["session_id"]

    # User B attempts to access User A's session messages
    msg_res_b = client.get(f"/api/saarthi/sessions/{session_id_a}/messages", headers=headers_b)
    assert msg_res_b.status_code in [403, 404]

    # User B attempts to post a message into User A's session
    chat_res_b = client.post("/api/saarthi/chat", json={"message": "Hijack query", "session_id": session_id_a}, headers=headers_b)
    assert chat_res_b.status_code in [403, 404]
