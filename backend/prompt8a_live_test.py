import sys
import uuid
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import engine

def run_prompt8a_live_verification():
    print("==================================================")
    print("RUNNING PROMPT 8A LIVE E2E VERIFICATION SCRIPT")
    print("==================================================")

    client = TestClient(app)

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("OK 1. Backend Health Check PASSED")

    # 2. Register User A
    email_a = f"usera_{uuid.uuid4().hex[:6]}@dhan.in"
    res_a = client.post("/api/auth/register", json={
        "full_name": "User Alpha",
        "email": email_a,
        "password": "Password123!"
    })
    assert res_a.status_code == 201, f"User A registration failed: {res_a.text}"
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("OK 2. User A Registration & JWT Generation PASSED")

    # 3. Save Profile for User A with Age, Monthly Savings (25,000) and Total Savings (300,000)
    profile_payload_a = {
        "age": 25,
        "occupation": "Software Engineer",
        "gender": "Male",
        "city": "Bengaluru",
        "monthly_income": 80000,
        "monthly_expenses": 55000,
        "monthly_savings": 25000,
        "total_savings": 300000,
        "savings": 25000,
        "financial_goal": "Buy a house",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
        "education_level": "UNDERGRADUATE",
        "financial_knowledge_level": "INTERMEDIATE",
        "preferred_explanation_level": "SIMPLE"
    }
    res_prof_a = client.put("/api/profile", json=profile_payload_a, headers=headers_a)
    assert res_prof_a.status_code == 200, f"Profile save failed: {res_prof_a.text}"
    prof_data_a = res_prof_a.json()
    assert float(prof_data_a["age"]) == 25, "Age mismatch"
    assert float(prof_data_a["monthly_savings"]) == 25000.0, "Monthly savings mismatch"
    assert float(prof_data_a["total_savings"]) == 300000.0, "Total savings mismatch"
    print("OK 3. Profile Save with Age, Monthly Savings & Total Savings PASSED")

    # 4. Verify Total Savings and Monthly Savings remain distinct
    assert float(prof_data_a["total_savings"]) != float(prof_data_a["monthly_savings"]), "Total savings must be distinct from monthly savings"
    print("OK 4. Total Savings vs Monthly Savings Separation PASSED")


    # 5. Financial Twin Generation
    res_twin = client.put("/api/financial-twin/generate", headers=headers_a)
    assert res_twin.status_code == 200, f"Twin generation failed: {res_twin.text}"
    twin_data = res_twin.json()
    assert twin_data["financial_health_score"] > 0, "Twin health score invalid"
    assert "300,000" in twin_data["financial_summary"] or "total accumulated savings" in twin_data["financial_summary"].lower(), "Twin summary missing Total Savings"
    print(f"OK 5. Financial Twin Generation (Score: {twin_data['financial_health_score']}) PASSED")

    # 6. Smart Goal Planning (Verify Total Savings is NOT silently auto-allocated into goal)
    future_date = "2027-12-31"
    goal_payload = {
        "name": "Home Down Payment",
        "category": "home",
        "target_amount": 500000,
        "current_amount": 100000,
        "target_date": future_date
    }
    res_goal = client.post("/api/planning/goals", json=goal_payload, headers=headers_a)
    assert res_goal.status_code == 201, f"Goal creation failed: {res_goal.text}"
    goal_data = res_goal.json()
    assert float(goal_data["current_amount"]) == 100000.0, "Goal current amount should remain 100,000 (total savings must not be auto-transferred)"

    assert goal_data["plan"]["feasibility_status"] in ["FEASIBLE", "TIGHT", "AT_RISK"], "Plan feasibility invalid"
    print("OK 6. Smart Planning Goal Creation & Non-Transfer of Total Savings PASSED")

    # 7. Scam Shield Contextual Scan Analysis
    scam_payload = {
        "message": "URGENT: Your bank account will be blocked today unless you click http://fake-verify-upi.com and enter your PIN immediately!"
    }

    res_scam = client.post("/api/scam-shield/analyze", json=scam_payload, headers=headers_a)
    assert res_scam.status_code in [200, 201], f"Scam analysis failed: {res_scam.text}"

    scam_data = res_scam.json()
    assert scam_data["risk_level"] in ["HIGH", "CRITICAL"], "Scam risk level should be HIGH or CRITICAL"
    print(f"OK 7. Scam Shield Threat Analysis (Risk: {scam_data['risk_level']}, Score: {scam_data['risk_score']}) PASSED")

    # 8. Government Scheme Discovery Context
    res_scheme = client.get("/api/schemes/recommendations", headers=headers_a)
    assert res_scheme.status_code == 200, f"Schemes failed: {res_scheme.text}"
    schemes_data = res_scheme.json()
    assert len(schemes_data) > 0, "No government scheme recommendations returned"
    first_scheme = schemes_data[0]["scheme"]
    print(f"OK 8. Government Scheme Discovery ('{first_scheme['name']}') PASSED")

    # 9. AI Saarthi Chat Contextual Query Execution
    contextual_prompt = f"Please explain my financial plan for '{goal_data['name']}' in simple terms. Target: RS. 500,000, Current saved: RS. 100,000, Required: RS. {goal_data['plan']['monthly_required']}/month."
    res_chat = client.post("/api/saarthi/chat", json={"message": contextual_prompt}, headers=headers_a)
    assert res_chat.status_code == 200, f"Saarthi chat failed: {res_chat.text}"
    chat_data = res_chat.json()
    assert len(chat_data["response"]) > 10, "Empty AI response"
    session_id_a = chat_data["session_id"]
    print("OK 9. AI Saarthi Contextual Chat Request PASSED")

    # 10. Chat Message Persistence Verification
    res_msgs = client.get(f"/api/saarthi/sessions/{session_id_a}/messages", headers=headers_a)
    assert res_msgs.status_code == 200, f"Messages fetch failed: {res_msgs.text}"
    msgs = res_msgs.json()
    assert len(msgs) >= 2, "Chat history must contain user message + AI response"
    assert msgs[-2]["role"] == "user", "Second to last message should be user"
    assert msgs[-1]["role"] == "model", "Last message should be AI model response"
    print(f"OK 10. Chat Message Persistence ({len(msgs)} messages persisted) PASSED")

    # 11. Cross-User Isolation Security Verification
    email_b = f"userb_{uuid.uuid4().hex[:6]}@dhan.in"
    res_b = client.post("/api/auth/register", json={
        "full_name": "User Beta",
        "email": email_b,
        "password": "Password123!"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempting to access User A's chat session messages must be denied (403/404)
    res_b_chat = client.get(f"/api/saarthi/sessions/{session_id_a}/messages", headers=headers_b)
    assert res_b_chat.status_code in [403, 404], f"Cross-user chat leak detected! Status: {res_b_chat.status_code}"

    # User B attempting to access User A's goal progress update must be denied (403/404)
    res_b_goal = client.post(f"/api/planning/goals/{goal_data['id']}/progress", json={"amount": 5000}, headers=headers_b)
    assert res_b_goal.status_code in [403, 404], f"Cross-user goal leak detected! Status: {res_b_goal.status_code}"
    print("OK 11. Cross-User Security Isolation PASSED")

    print("==================================================")
    print("ALL 11 PROMPT 8A LIVE E2E STEPS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_prompt8a_live_verification()
