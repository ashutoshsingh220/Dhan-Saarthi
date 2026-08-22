import os
os.environ["DATABASE_URL"] = "sqlite:///./test_prompt10_live.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-prompt10-live"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine("sqlite:///./test_prompt10_live.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def run_prompt10_live_verification():
    print("==================================================================")
    print("PROMPT 10 LIVE E2E VERIFICATION SCRIPT")
    print("==================================================================")

    # 1. Clean Database Initialization
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[1/9] Database initialized cleanly.")

    # 2. Register & Auth
    reg = client.post("/api/auth/register", json={
        "full_name": "Ramesh Kumar",
        "email": "ramesh_mkt@example.com",
        "password": "password123"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[2/9] User registration & authentication successful.")

    # 3. Fetch Market Overview
    res = client.get("/api/market/overview", headers=headers)
    assert res.status_code == 200
    ov = res.json()
    print("[3/9] GET /api/market/overview endpoint responded 200 OK.")

    # 4. Verify Freshness & Source Metadata
    freshness = ov["freshness"]
    source = ov["source"]
    fetched_at = ov["fetched_at"]
    assert freshness in ["LIVE", "CACHED", "STALE", "UNAVAILABLE"]
    print(f"[4/9] Freshness Metadata: '{freshness}' | Source: '{source}' | Fetched At: {fetched_at}")

    # 5. Verify Asset Directions & Values
    assets = ov["tracked_assets"]
    assert len(assets) >= 5
    symbols = [a["symbol"] for a in assets]
    print(f"[5/9] Tracked Assets ({len(assets)}): {', '.join(symbols)}")
    for a in assets:
        assert a["direction"] in ["UP", "DOWN", "FLAT", "UNAVAILABLE"]
        assert a["current_price"] > 0

    # 6. Verify Market Pulse
    pulse = ov["market_pulse"]
    summary = ov["pulse_summary"]
    assert pulse in ["POSITIVE", "NEGATIVE", "MIXED", "CALM", "UNAVAILABLE"]
    print(f"[6/9] Calculated Market Pulse: '{pulse}' — Summary: {summary}")

    # 7. Single Asset Detail Endpoint
    nifty_res = client.get("/api/market/assets/NIFTY50", headers=headers)
    assert nifty_res.status_code == 200
    nifty = nifty_res.json()
    assert nifty["display_name"] == "NIFTY 50"
    print(f"[7/9] GET /api/market/assets/NIFTY50: INR {nifty['current_price']} ({nifty['direction']})")

    # 8. Manual Refresh Endpoint
    ref_res = client.post("/api/market/refresh", headers=headers)
    assert ref_res.status_code == 200
    ref_ov = ref_res.json()
    assert "tracked_assets" in ref_ov
    print("[8/9] POST /api/market/refresh triggered manual dataset update successfully.")

    # 9. AI Saarthi ContextBuilder Integration
    from app.services.context_builder import ContextBuilder
    from app.models.user import User
    from sqlalchemy import select
    db = TestingSessionLocal()
    user_obj = db.scalar(select(User).where(User.email == "ramesh_mkt@example.com"))
    ai_ctx = ContextBuilder.build_user_context(user_obj, db=db)
    db.close()
    assert "LIVE MARKET INTELLIGENCE" in ai_ctx
    assert "Market Pulse:" in ai_ctx
    print("[9/9] ContextBuilder generated Market Intelligence context block for AI Saarthi.")

    print("\n==================================================================")
    print("ALL 9 LIVE E2E VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_prompt10_live_verification()
