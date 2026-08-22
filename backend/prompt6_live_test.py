import os
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def run_live_tests():
    print("=== PROMPT 6 FINANCIAL LITERACY LIVE E2E VERIFICATION ===")

    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("  PASS [200] 1. Health check")

    # 2. Register & Onboard User A
    user_a_email = f"user_a_learn_{int(time.time())}@example.com"
    res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Aarav Sharma",
        "email": user_a_email,
        "password": "password123"
    })
    assert res.status_code == 201, f"User A registration failed: {res.text}"
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    requests.put(f"{BASE_URL}/api/profile", json={
        "age": 28,
        "occupation": "Product Analyst",
        "city": "Mumbai",
        "monthly_income": 75000,
        "monthly_expenses": 30000,
        "savings": 150000,
        "financial_goal": "Financial Literacy & Wealth Growth",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard"
    }, headers=headers_a)
    requests.put(f"{BASE_URL}/api/financial-twin/generate", headers=headers_a)
    print("  PASS [201] 2. Register & Onboard User A")

    # 3. Retrieve Learning Modules Catalogue
    res_mods = requests.get(f"{BASE_URL}/api/learn/modules", headers=headers_a)
    assert res_mods.status_code == 200, f"Get modules failed: {res_mods.text}"
    modules = res_mods.json()
    assert len(modules) == 6, f"Expected 6 modules, got {len(modules)}"
    print(f"  PASS [200] 3. Retrieve Learning Catalogue ({len(modules)} modules seeded)")

    # 4. Retrieve Personalized Recommendations
    res_recs = requests.get(f"{BASE_URL}/api/learn/recommendations", headers=headers_a)
    assert res_recs.status_code == 200, f"Get recommendations failed: {res_recs.text}"
    recs = res_recs.json()
    assert len(recs) >= 1, "Expected at least 1 recommendation"
    print(f"  PASS [200] 4. Retrieve Recommendations (Top: '{recs[0]['title']}')")

    # 5. Get Module Detail
    res_detail = requests.get(f"{BASE_URL}/api/learn/modules/savings-basics", headers=headers_a)
    assert res_detail.status_code == 200, f"Module detail failed: {res_detail.text}"
    mod_data = res_detail.json()
    assert mod_data["module_id"] == "savings-basics"
    assert mod_data["status"] == "NOT_STARTED"
    print("  PASS [200] 5. Get Module Detail ('savings-basics')")

    # 6. Start Module
    res_start = requests.post(f"{BASE_URL}/api/learn/modules/savings-basics/start", headers=headers_a)
    assert res_start.status_code == 200, f"Start module failed: {res_start.text}"
    assert res_start.json()["status"] == "IN_PROGRESS"
    print("  PASS [200] 6. Start Module (Status updated to IN_PROGRESS)")

    # 7. Get Quiz Questions (Verify correct_option_index is hidden)
    res_quiz = requests.get(f"{BASE_URL}/api/learn/modules/savings-basics/quiz", headers=headers_a)
    assert res_quiz.status_code == 200, f"Get quiz failed: {res_quiz.text}"
    quiz_qs = res_quiz.json()
    assert len(quiz_qs) == 3
    for q in quiz_qs:
        assert "correct_option_index" not in q, "Security breach: correct answers exposed!"
    print("  PASS [200] 7. Get Quiz Questions (Security Verified: Answers Hidden)")

    # 8. Submit Quiz Answers (100% correct: [1, 1, 2])
    res_sub = requests.post(f"{BASE_URL}/api/learn/modules/savings-basics/quiz", json={"answers": [1, 1, 2]}, headers=headers_a)
    assert res_sub.status_code == 200, f"Submit quiz failed: {res_sub.text}"
    result_data = res_sub.json()
    assert result_data["score_percentage"] == 100.0
    assert result_data["correct_count"] == 3
    assert result_data["status"] == "COMPLETED"
    print(f"  PASS [200] 8. Submit Quiz Answers (Score: {result_data['score_percentage']}%, Status: {result_data['status']})")

    # 9. Verify Progress Persistence
    res_prog = requests.get(f"{BASE_URL}/api/learn/progress", headers=headers_a)
    assert res_prog.status_code == 200, f"Get progress failed: {res_prog.text}"
    prog_data = res_prog.json()
    assert prog_data["completed_modules"] == 1
    assert prog_data["completion_percentage"] == 16.7
    print(f"  PASS [200] 9. Progress Persistence ({prog_data['completed_modules']}/{prog_data['total_modules']} completed = {prog_data['completion_percentage']}%)")

    # 10. Multi-User Isolation Test
    user_b_email = f"user_b_learn_{int(time.time())}@example.com"
    res_b = requests.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Rohan Verma",
        "email": user_b_email,
        "password": "password123"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_prog_b = requests.get(f"{BASE_URL}/api/learn/progress", headers=headers_b)
    assert res_prog_b.json()["completed_modules"] == 0, "User B leaked User A's progress!"
    print("  PASS [200] 10. Multi-User Progress Security Isolation (User B isolated from User A)")

    # 11. AI Saarthi Financial Literacy Topic Explanation
    prompt_txt = "Can you explain the key concepts of Savings Basics in simple terms?"
    res_ai = requests.post(f"{BASE_URL}/api/saarthi/chat", json={"message": prompt_txt}, headers=headers_a)
    assert res_ai.status_code == 200, f"AI Saarthi chat failed: {res_ai.text}"
    ai_resp = res_ai.json()["response"]
    print(f"  PASS [200] 11. AI Saarthi Financial Literacy Topic Explanation (Snippet: '{ai_resp[:90]}...')")

    print("\n=== PROMPT 6 FINANCIAL LITERACY LIVE VERIFICATION: 11/11 PASSED ===")


if __name__ == "__main__":
    run_live_tests()
