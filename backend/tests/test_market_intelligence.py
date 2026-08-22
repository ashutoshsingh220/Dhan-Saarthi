import os
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["ALPHA_VANTAGE_API_KEY"] = "MOCK_ALPHA_VANTAGE_KEY"

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import engine, get_db
from app.main import app
from app.models.market import MarketSnapshot
from app.models.user import User
from app.providers.market_data_provider import AlphaVantageMarketDataProvider, BaseMarketDataProvider

from app.schemas.market import MarketAssetSchema
from app.services.market_insight_service import MarketInsightService
from app.services.market_service import MarketService

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

def _register_and_onboard(email: str = "market@example.com") -> str:
    res = client.post("/api/auth/register", json={"full_name": "Market Tester", "email": email, "password": "password123"})
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/api/profile", json={
        "age": 30,
        "occupation": "Analyst",
        "monthly_income": 50000,
        "monthly_expenses": 30000,
        "savings": 100000,
        "financial_goal": "Wealth Building",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
    }, headers=headers)
    return token

# --- TESTS ---

def test_direction_calculation_rules():
    up_asset = MarketAssetSchema(
        symbol="NIFTY50", display_name="NIFTY 50", asset_type="EQUITY_INDEX",
        current_price=24500.0, currency="INR", absolute_change=100.0, percentage_change=0.5,
        direction="UP", updated_at="2026-08-22T00:00:00Z"
    )
    assert up_asset.direction == "UP"

    down_asset = MarketAssetSchema(
        symbol="SENSEX", display_name="SENSEX", asset_type="EQUITY_INDEX",
        current_price=80000.0, currency="INR", absolute_change=-200.0, percentage_change=-0.25,
        direction="DOWN", updated_at="2026-08-22T00:00:00Z"
    )
    assert down_asset.direction == "DOWN"

def test_market_pulse_positive():
    assets = [
        MarketAssetSchema(symbol=s, display_name=s, asset_type="EQUITY_INDEX", current_price=100, currency="INR", absolute_change=10, percentage_change=1.0, direction="UP", updated_at="now")
        for s in ["A1", "A2", "A3", "A4"]
    ]
    pulse, summary = MarketInsightService.calculate_market_pulse(assets)
    assert pulse == "POSITIVE"

def test_market_pulse_negative():
    assets = [
        MarketAssetSchema(symbol=s, display_name=s, asset_type="EQUITY_INDEX", current_price=100, currency="INR", absolute_change=-10, percentage_change=-1.0, direction="DOWN", updated_at="now")
        for s in ["A1", "A2", "A3", "A4"]
    ]
    pulse, summary = MarketInsightService.calculate_market_pulse(assets)
    assert pulse == "NEGATIVE"

def test_market_pulse_calm():
    assets = [
        MarketAssetSchema(symbol=s, display_name=s, asset_type="EQUITY_INDEX", current_price=100, currency="INR", absolute_change=0.01, percentage_change=0.01, direction="FLAT", updated_at="now")
        for s in ["A1", "A2", "A3", "A4"]
    ]
    pulse, summary = MarketInsightService.calculate_market_pulse(assets)
    assert pulse == "CALM"

def test_alpha_vantage_provider_missing_key():
    provider = AlphaVantageMarketDataProvider(api_key="")
    assets, source, is_live = provider.fetch_market_snapshot()
    assert is_live is False
    assert source == "BASELINE_MARKET_PROVIDER"

@patch("httpx.Client.get")
def test_alpha_vantage_provider_valid_response(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "Realtime Currency Exchange Rate": {
            "1. From_Currency Code": "USD",
            "3. To_Currency Code": "INR",
            "5. Exchange Rate": "83.95"
        }
    }
    mock_get.return_value = mock_resp

    provider = AlphaVantageMarketDataProvider(api_key="TEST_KEY")
    assets, source, is_live = provider.fetch_market_snapshot()

    assert is_live is True
    assert source == "ALPHA_VANTAGE"
    assert "USDINR" in assets
    assert assets["USDINR"]["current_price"] == 83.95

@patch("httpx.Client.get")
def test_alpha_vantage_provider_rate_limit_response(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute."
    }
    mock_get.return_value = mock_resp

    provider = AlphaVantageMarketDataProvider(api_key="TEST_KEY")
    assets, source, is_live = provider.fetch_market_snapshot()

    assert is_live is False
    assert source == "BASELINE_MARKET_PROVIDER"

@patch("httpx.Client.get")
def test_alpha_vantage_provider_timeout_fallback(mock_get):
    mock_get.side_effect = Exception("Connection timeout")

    provider = AlphaVantageMarketDataProvider(api_key="TEST_KEY")
    assets, source, is_live = provider.fetch_market_snapshot()

    assert is_live is False
    assert source == "BASELINE_MARKET_PROVIDER"

def test_market_overview_endpoint_unauthenticated():
    res = client.get("/api/market/overview")
    assert res.status_code == 200
    data = res.json()
    assert "market_pulse" in data
    assert "tracked_assets" in data
    assert len(data["tracked_assets"]) >= 5

def test_asset_detail_endpoint():
    res = client.get("/api/market/assets/NIFTY50")
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "NIFTY50"

def test_asset_detail_not_found():
    res = client.get("/api/market/assets/NON_EXISTENT_SYMBOL")
    assert res.status_code == 404

def test_manual_refresh_endpoint():
    token = _register_and_onboard("mkt_ref@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/market/refresh", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["source"] != ""

def test_market_context_in_ai_saarthi():
    from app.services.context_builder import ContextBuilder
    db = TestingSessionLocal()
    token = _register_and_onboard("ai_mkt@example.com")
    user = db.scalar(select(User).where(User.email == "ai_mkt@example.com"))

    ctx = ContextBuilder.build_user_context(user, db=db)
    db.close()

    assert "LIVE MARKET INTELLIGENCE" in ctx
    assert "Market Pulse:" in ctx
