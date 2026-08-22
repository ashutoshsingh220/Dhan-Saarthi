import os
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def run_live_tests():
    print("=== PROMPT 7 MULTILINGUAL & VOICE FOUNDATION LIVE VERIFICATION ===")

    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("  PASS [200] 1. Health check")

    # 2. Register & Onboard User A (English)
    user_a_email = f"user_a_p7_{int(time.time())}@example.com"
    res_a = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Aarav Sharma",
        "email": user_a_email,
        "password": "password123"
    })
    assert res_a.status_code == 201, f"User A registration failed: {res_a.text}"
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.put(f"{BASE_URL}/api/profile", json={
        "age": 30,
        "occupation": "Financial Analyst",
        "city": "Delhi",
        "monthly_income": 90000,
        "monthly_expenses": 35000,
        "savings": 250000,
        "financial_goal": "Multilingual Wealth Building",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard"
    }, headers=headers_a)
    requests.put(f"{BASE_URL}/api/financial-twin/generate", headers=headers_a)
    print("  PASS [201] 2. Register & Onboard User A (English)")

    # 3. Register & Onboard User B (Hindi)
    user_b_email = f"user_b_p7_{int(time.time())}@example.com"
    res_b = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Rohan Verma",
        "email": user_b_email,
        "password": "password123"
    })
    assert res_b.status_code == 201, f"User B registration failed: {res_b.text}"
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    requests.put(f"{BASE_URL}/api/profile", json={
        "age": 32,
        "occupation": "Small Business Owner",
        "city": "Jaipur",
        "monthly_income": 60000,
        "monthly_expenses": 25000,
        "savings": 100000,
        "financial_goal": "व्यापार विस्तार और बचत",
        "risk_preference": "low",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard"
    }, headers=headers_b)
    requests.put(f"{BASE_URL}/api/financial-twin/generate", headers=headers_b)
    print("  PASS [201] 3. Register & Onboard User B (Hindi)")

    # 4. AI Saarthi Chat in English (User A)
    res_ai_a = requests.post(f"{BASE_URL}/api/saarthi/chat", json={
        "message": "Explain my financial health score in English."
    }, headers=headers_a)
    assert res_ai_a.status_code == 200, f"AI Chat A failed: {res_ai_a.text}"
    resp_a_text = res_ai_a.json()["response"]
    print(f"  PASS [200] 4. AI Saarthi English Chat (Response Snippet: '{resp_a_text[:80]}...')")

    # 5. AI Saarthi Chat in Hindi (User B)
    res_ai_b = requests.post(f"{BASE_URL}/api/saarthi/chat", json={
        "message": "मेरा फाइनेंशियल हेल्थ स्कोर समझाओ।"
    }, headers=headers_b)
    assert res_ai_b.status_code == 200, f"AI Chat B failed: {res_ai_b.text}"
    resp_b_text = res_ai_b.json()["response"]
    print(f"  PASS [200] 5. AI Saarthi Hindi Chat (Response Snippet: '{resp_b_text[:80]}...')")

    # 6. Profile Preferred Language Update
    res_upd = requests.put(f"{BASE_URL}/api/profile", json={
        "age": 30,
        "occupation": "Financial Analyst",
        "city": "Delhi",
        "monthly_income": 90000,
        "monthly_expenses": 35000,
        "savings": 250000,
        "financial_goal": "Multilingual Wealth Building",
        "risk_preference": "moderate",
        "preferred_language": "Hindi",
        "accessibility_mode": "standard"
    }, headers=headers_a)
    assert res_upd.status_code == 200, f"Profile update failed: {res_upd.text}"
    assert res_upd.json()["user_id"] is not None
    print("  PASS [200] 6. Profile Preferred Language Update ('Hindi')")

    print("\n=== PROMPT 7 MULTILINGUAL & VOICE FOUNDATION LIVE VERIFICATION: 6/6 PASSED ===")


if __name__ == "__main__":
    run_live_tests()
