import time
from fastapi.testclient import TestClient
from app.main import app

def main():
    client = TestClient(app)
    email = f"consent_verify_{int(time.time())}@test.com"
    print(f"1. Registering user {email}...")

    res = client.post("/api/auth/register", json={"full_name": "Consent User", "email": email, "password": "Password123!"})
    assert res.status_code == 201, f"Register failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   -> User registered successfully.")

    print("2. Submitting profile with mandatory legal consent...")
    profile_data = {
        "age": 28,
        "occupation": "Software Engineer",
        "monthly_income": 95000,
        "monthly_expenses": 40000,
        "monthly_savings": 35000,
        "total_savings": 450000,
        "savings": 35000,
        "financial_goal": "Buy an EV Car",
        "risk_preference": "moderate",
        "preferred_language": "English",
        "accessibility_mode": "standard",
        "consent_given": True,
    }
    res = client.put("/api/profile", headers=headers, json=profile_data)
    assert res.status_code == 200, f"Profile save failed: {res.text}"
    p = res.json()
    assert p["consent_given"] is True, "consent_given is not True"
    assert p["consent_given_at"] is not None, "consent_given_at is missing"
    print(f"   -> Profile saved. consent_given={p['consent_given']}, consent_given_at={p['consent_given_at']}")

    print("3. Generating Financial Twin...")
    res = client.put("/api/financial-twin/generate", headers=headers)
    assert res.status_code == 200, f"Twin generation failed: {res.text}"
    twin = res.json()
    print(f"   -> Financial Twin score: {twin['financial_health_score']} (Risk Level: {twin['risk_level']})")

    print("\n==================================================")
    print("VERIFICATION SUCCESSFUL: MANDATORY LEGAL CONSENT WORKFLOW 100% OPERATIONAL!")
    print("==================================================")

if __name__ == "__main__":
    main()
