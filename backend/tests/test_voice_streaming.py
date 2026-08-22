import os
os.environ["JWT_SECRET_KEY"] = "test-voice-secret"

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import engine, get_db
from app.main import app
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User

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

def _register_user(email: str = "voice_user@example.com") -> str:
    res = client.post("/api/auth/register", json={"full_name": "Voice Tester", "email": email, "password": "password123"})
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/api/profile", json={
        "age": 28,
        "occupation": "Developer",
        "monthly_income": 60000,
        "monthly_expenses": 30000,
        "savings": 120000,
        "financial_goal": "Emergency Buffer",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
    }, headers=headers)
    return token

# --- VOICE & CHAT STREAMING TESTS ---

def test_streaming_unauthorized():
    res = client.post("/api/saarthi/chat/stream", json={"message": "Hello Saarthi"})
    assert res.status_code == 401

def test_streaming_empty_message():
    token = _register_user("empty_voice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/saarthi/chat/stream", json={"message": "   "}, headers=headers)
    assert res.status_code == 400

def test_streaming_chat_flow_and_persistence():
    token = _register_user("flow_voice@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/saarthi/chat/stream", json={"message": "How much emergency buffer should I save?"}, headers=headers)
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    assert len(res.text) > 0

    # Verify session and messages were persisted in DB
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "flow_voice@example.com"))
    session = db.scalar(select(ChatSession).where(ChatSession.user_id == user.id))
    assert session is not None

    msgs = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc())).all()
    assert len(msgs) == 2
    assert msgs[0].role == "user"
    assert msgs[0].content == "How much emergency buffer should I save?"
    assert msgs[1].role == "model"
    assert len(msgs[1].content) > 0
    db.close()

def test_session_ownership_security_isolation_streaming():
    token1 = _register_user("user1_stream@example.com")
    token2 = _register_user("user2_stream@example.com")

    # User 1 creates session via normal chat
    res1 = client.post("/api/saarthi/chat", json={"message": "User 1 initial prompt"}, headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    session_id = res1.json()["session_id"]

    # User 2 attempts to stream into User 1's session
    res2 = client.post("/api/saarthi/chat/stream", json={"message": "Hacked query", "session_id": session_id}, headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 403

def test_non_stream_chat_regression_remains_operational():
    token = _register_user("regr_chat@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/saarthi/chat", json={"message": "Hello from standard non-stream chat"}, headers=headers)
    assert res.status_code == 200
    assert "response" in res.json()
