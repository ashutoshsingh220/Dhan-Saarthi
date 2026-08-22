import os
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def run_live_tests():
    print("=== PROMPT 5 SCAM SHIELD LIVE E2E VERIFICATION ===")

    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("  PASS [200] 1. Health check")

    # 2. Register & Onboard User A
    user_a_email = f"user_a_scam_{int(time.time())}@example.com"
    res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Aarav Sharma",
        "email": user_a_email,
        "password": "password123"
    })
    assert res.status_code == 201, f"User A registration failed: {res.text}"
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Profile & Financial Twin
    requests.put(f"{BASE_URL}/api/profile", json={
        "age": 30,
        "occupation": "Software Developer",
        "city": "Bengaluru",
        "monthly_income": 80000,
        "monthly_expenses": 35000,
        "savings": 200000,
        "financial_goal": "Fraud Protection & Home Downpayment",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard"
    }, headers=headers_a)
    requests.put(f"{BASE_URL}/api/financial-twin/generate", headers=headers_a)
    print("  PASS [201] 2. Register & Onboard User A")

    # 3. Analyze Safe Message
    safe_msg = "Your monthly bank statement for July is ready. View it securely through your official banking application."
    res_safe = requests.post(f"{BASE_URL}/api/scam-shield/analyze", json={"message": safe_msg}, headers=headers_a)
    assert res_safe.status_code == 201, f"Safe analyze failed: {res_safe.text}"
    safe_data = res_safe.json()
    assert safe_data["risk_level"] == "LOW", f"Expected LOW risk, got {safe_data['risk_level']}"
    assert safe_data["risk_score"] == 0, f"Expected 0 score, got {safe_data['risk_score']}"
    print(f"  PASS [201] 3. Safe message analysis (Score: {safe_data['risk_score']}/100, Risk: {safe_data['risk_level']})")

    # 4. Analyze Critical Scam Message
    scam_msg = "Urgent: Your SBI bank account will be blocked immediately due to KYC failure. Verify PAN now at http://bit.ly/fake-kyc and enter OTP."
    res_scam = requests.post(f"{BASE_URL}/api/scam-shield/analyze", json={"message": scam_msg}, headers=headers_a)
    assert res_scam.status_code == 201, f"Scam analyze failed: {res_scam.text}"
    scam_data = res_scam.json()
    scan_id = scam_data["id"]
    assert scam_data["risk_level"] == "CRITICAL", f"Expected CRITICAL risk, got {scam_data['risk_level']}"
    assert scam_data["risk_score"] >= 75, f"Expected >= 75 score, got {scam_data['risk_score']}"
    assert len(scam_data["indicators"]) >= 4, f"Expected >= 4 indicators, got {len(scam_data['indicators'])}"
    print(f"  PASS [201] 4. Critical scam analysis (Scan ID: {scan_id[:8]}..., Score: {scam_data['risk_score']}/100, Indicators: {len(scam_data['indicators'])})")

    # 5. Get Scam History
    res_hist = requests.get(f"{BASE_URL}/api/scam-shield/history", headers=headers_a)
    assert res_hist.status_code == 200, f"History failed: {res_hist.text}"
    hist_data = res_hist.json()
    assert hist_data["total_count"] >= 2, f"Expected >= 2 scans, got {hist_data['total_count']}"
    print(f"  PASS [200] 5. Get Scam History (Total Scans: {hist_data['total_count']})")

    # 6. Detailed Scan Retrieval
    res_detail = requests.get(f"{BASE_URL}/api/scam-shield/history/{scan_id}", headers=headers_a)
    assert res_detail.status_code == 200, f"Detail failed: {res_detail.text}"
    assert res_detail.json()["id"] == scan_id
    print("  PASS [200] 6. Detailed Scan Retrieval")

    # 7. AI Saarthi Scam Explanation Integration
    prompt_txt = f"Why is my message with scan ID {scan_id} flagged as {scam_data['risk_level']} risk ({scam_data['risk_score']}/100)?"
    res_ai = requests.post(f"{BASE_URL}/api/saarthi/chat", json={"message": prompt_txt}, headers=headers_a)
    assert res_ai.status_code == 200, f"AI Saarthi chat failed: {res_ai.text}"
    ai_resp = res_ai.json()["response"]
    print(f"  PASS [200] 7. AI Saarthi Scam Explanation Integration (Response Snippet: '{ai_resp[:90]}...')")

    # 8. Register User B & Security Ownership Isolation Test
    user_b_email = f"user_b_scam_{int(time.time())}@example.com"
    res_b = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Rohan Verma",
        "email": user_b_email,
        "password": "password123"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_b_view = requests.get(f"{BASE_URL}/api/scam-shield/history/{scan_id}", headers=headers_b)
    assert res_b_view.status_code in [403, 404], f"Expected 403/404, got {res_b_view.status_code}"
    print(f"  PASS [{res_b_view.status_code}] 8. Goal Ownership Security Isolation (User B cannot access User A's scan)")

    # 9. Delete Scan Verification
    res_del = requests.delete(f"{BASE_URL}/api/scam-shield/history/{scan_id}", headers=headers_a)
    assert res_del.status_code == 204, f"Delete failed: {res_del.text}"
    print("  PASS [204] 9. Delete Scan Verification")

    print("\n=== PROMPT 5 SCAM SHIELD LIVE VERIFICATION: 9/9 PASSED ===")


if __name__ == "__main__":
    run_live_tests()
