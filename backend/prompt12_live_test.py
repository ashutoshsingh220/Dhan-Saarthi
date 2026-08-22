import os
os.environ["DATABASE_URL"] = "sqlite:///./test_prompt12_live.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-prompt12-live"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User

engine = create_engine("sqlite:///./test_prompt12_live.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_prompt12_live_verification():
    print("==================================================================")
    print("PROMPT 12 LIVE E2E VERIFICATION SCRIPT")
    print("==================================================================")

    # 1. Clean Database Initialization
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[1/12] Database initialized cleanly.")

    # 2. Register & Auth
    reg = client.post("/api/auth/register", json={
        "full_name": "Sita Devi",
        "email": "sita_voice@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2/12] User registration successful.")

    # 3. Profile Onboarding
    prof = client.put("/api/profile", json={
        "age": 32,
        "occupation": "Homemaker",
        "monthly_income": "40000",
        "monthly_expenses": "20000",
        "savings": "60000",
        "financial_goal": "Child Education",
        "risk_preference": "moderate",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard",
    }, headers=headers)
    assert prof.status_code == 200, f"Profile error: {prof.text}"
    print("[3/12] Profile onboarding completed.")

    # 4. Generate Twin
    twin_res = client.put("/api/financial-twin/generate", headers=headers)
    assert twin_res.status_code == 200, f"Twin error: {twin_res.text}"

    print("[4/12] Financial Twin generated.")


    # 5. Non-Stream Chat Verification
    chat1 = client.post("/api/saarthi/chat", json={"message": "Mujhe bachat ke bare me batao"}, headers=headers)
    assert chat1.status_code == 200
    session_id = chat1.json()["session_id"]
    print(f"[5/12] POST /api/saarthi/chat responded 200 OK (Session ID: {session_id[:8]}...).")

    # 6. Streaming Chat Verification
    stream_res = client.post("/api/saarthi/chat/stream", json={"message": "Mere pas har mahine 10000 rupaye bachte hain", "session_id": session_id}, headers=headers)
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]
    assert len(stream_res.text) > 0
    print("[6/12] POST /api/saarthi/chat/stream responded 200 OK with SSE text stream.")

    # 7. DB Persistence Verification
    db = TestingSessionLocal()
    user = db.scalar(select(User).where(User.email == "sita_voice@example.com"))
    session = db.scalar(select(ChatSession).where(ChatSession.user_id == user.id))
    msgs = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id)).all()
    assert len(msgs) >= 4
    print(f"[7/12] Chat session message history persisted in DB ({len(msgs)} messages stored).")
    db.close()

    # 8. ContextBuilder Integration with Voice Language
    from app.services.context_builder import ContextBuilder
    db = TestingSessionLocal()
    user_obj = db.scalar(select(User).where(User.email == "sita_voice@example.com"))
    ai_ctx = ContextBuilder.build_user_context(user_obj, db=db)
    db.close()
    assert "Preferred Language: Hindi" in ai_ctx
    print("[8/12] ContextBuilder generated Hindi voice-aware prompt context.")


    # 9. Session Ownership Security Isolation (403)
    reg2 = client.post("/api/auth/register", json={"full_name": "Unauth User", "email": "unauth@example.com", "password": "password123"})
    token2 = reg2.json()["access_token"]
    unauth_res = client.post("/api/saarthi/chat/stream", json={"message": "Hacked query", "session_id": session_id}, headers={"Authorization": f"Bearer {token2}"})
    assert unauth_res.status_code == 403
    print("[9/12] Session ownership security isolation verified (403 Forbidden).")

    # 10. Empty Message Validation (400)
    empty_res = client.post("/api/saarthi/chat/stream", json={"message": "   "}, headers=headers)
    assert empty_res.status_code == 400
    print("[10/12] Empty message validation verified (400 Bad Request).")

    # 11. Unauthorized Access Verification (401)
    no_auth_res = client.post("/api/saarthi/chat/stream", json={"message": "No auth"})
    assert no_auth_res.status_code == 401
    print("[11/12] Unauthorized access rejected (401 Unauthorized).")

    # 12. Complete Session History Endpoint Verification
    history_res = client.get(f"/api/saarthi/sessions/{session_id}/messages", headers=headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 4
    print("[12/12] GET /api/saarthi/sessions/{session_id}/messages verified.")

    print("\n==================================================================")
    print("ALL 12 LIVE E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_prompt12_live_verification()
