import json
import logging
from fastapi.testclient import TestClient

from app.main import app

logging.basicConfig(level=logging.INFO)

def audit_market_endpoint():
    print("==================================================")
    print("AUDITING MARKET PLUS API ENDPOINT & DATA FLOW")
    print("==================================================")

    client = TestClient(app)

    # 1. First Call: GET /api/market/overview
    print("\n1. Making initial call to GET /api/market/overview...")
    res1 = client.get("/api/market/overview")
    assert res1.status_code == 200, f"Endpoint call failed: {res1.text}"
    data1 = res1.json()

    print(f"   -> Status Code: {res1.status_code}")
    print(f"   -> Source: {data1['source']}")
    print(f"   -> Freshness: {data1['freshness']}")
    print(f"   -> Is Stale: {data1['is_stale']}")
    print(f"   -> Fetched At: {data1['fetched_at']}")
    print(f"   -> Market Pulse: {data1['market_pulse']}")
    print(f"   -> Tracked Assets ({len(data1['tracked_assets'])} assets):")

    fallback_nifty = 24540.20
    fallback_sensex = 80620.80
    nifty_live = False

    for asset in data1["tracked_assets"]:
        sym = asset["symbol"]
        price = asset["current_price"]
        change = asset["absolute_change"]
        pct = asset["percentage_change"]
        direction = asset["direction"]
        src = asset["source"]
        print(f"      - {sym} ({asset['display_name']}): RS. {price} | Change: {change} ({pct}%) [{direction}] - Source: {src}")


        if sym == "NIFTY50" and price != fallback_nifty:
            nifty_live = True

    print("\n2. Making second call to GET /api/market/overview?force_refresh=true...")
    res2 = client.get("/api/market/overview?force_refresh=true")
    assert res2.status_code == 200, f"Force refresh call failed: {res2.text}"
    data2 = res2.json()

    print(f"   -> Status Code: {res2.status_code}")
    print(f"   -> Source: {data2['source']}")
    print(f"   -> Freshness: {data2['freshness']}")
    print(f"   -> Fetched At: {data2['fetched_at']}")

    print("\n==================================================")
    if nifty_live or data1["source"] in ["LIVE_PUBLIC_MARKET", "ALPHA_VANTAGE"]:
        print("VERIFICATION RESULT: LIVE MARKET DATA SUCCESSFULLY FETCHED & VERIFIED!")
    else:
        print("VERIFICATION RESULT: FALLBACK DATA USED (OFFLINE/FALLBACK MODE)")
    print("==================================================")

if __name__ == "__main__":
    audit_market_endpoint()
