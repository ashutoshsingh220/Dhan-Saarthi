import urllib.request, urllib.error, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://localhost:8000"

def req(method, path, body=None, headers={}):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    h = {"Content-Type": "application/json", **headers}
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

results = []

# Step 1: Health check
s, b = req("GET", "/health")
results.append(("1. GET /health", s, s == 200))
print(f"1. Health check -> {s} {b}")

# Step 2: Register user
email = "prompt2_user@test.com"
s, b = req("POST", "/api/auth/register", {"full_name": "Ashutosh Verma", "email": email, "password": "SecurePassword123"})
if s == 409:
    s, b = req("POST", "/api/auth/login", {"email": email, "password": "SecurePassword123"})

token = b.get("access_token", "")
results.append(("2. Register/Login JWT received", s, (s in [200, 201]) and bool(token)))
print(f"2. Auth -> status: {s}, token received: {'YES' if token else 'NO'}")

auth_headers = {"Authorization": f"Bearer {token}"}

# Step 3: Upsert Profile
profile_payload = {
    "age": 28,
    "gender": "Male",
    "occupation": "Software Engineer",
    "city": "Bengaluru",
    "monthly_income": 95000,
    "monthly_expenses": 50000,
    "savings": 250000,
    "financial_goal": "Home Down Payment",
    "risk_preference": "moderate",
    "preferred_language": "English",
    "accessibility_mode": "standard"
}
s, b = req("PUT", "/api/profile", profile_payload, auth_headers)
results.append(("3. PUT /api/profile", s, s == 200 and b.get("occupation") == "Software Engineer"))
print(f"3. Profile upsert -> status: {s}, occupation: {b.get('occupation')}")

# Step 4: Generate Financial Twin
s, b = req("PUT", "/api/financial-twin/generate", headers=auth_headers)
score = b.get("financial_health_score", -1)
results.append(("4. PUT /api/financial-twin/generate", s, s == 200 and 0 <= score <= 100))
print(f"4. Twin generate -> status: {s}, score: {score}, risk: {b.get('risk_level')}")

# Step 5: Session Restoration simulation (GET /auth/me -> GET /profile -> GET /financial-twin)
s_me, me_body = req("GET", "/api/auth/me", headers=auth_headers)
s_prof, prof_body = req("GET", "/api/profile", headers=auth_headers)
s_twin, twin_body = req("GET", "/api/financial-twin", headers=auth_headers)

session_restored = (
    s_me == 200 and me_body.get("onboarding_complete") == True and
    s_prof == 200 and float(prof_body.get("monthly_income", 0)) == 95000 and
    s_twin == 200 and twin_body.get("financial_health_score") == score
)
results.append(("5. App Restart & Session Restoration Flow", s_twin, session_restored))
print(f"5. Session restore -> me: {s_me}, prof: {s_prof}, twin: {s_twin}, restored: {session_restored}")

# Step 6: Verify Financial Twin Detail View data readiness
detail_ready = (
    twin_body.get("financial_summary") is not None and
    prof_body.get("financial_goal") == "Home Down Payment" and
    prof_body.get("risk_preference") == "moderate"
)
results.append(("6. Financial Twin Detail Data Integrity", 200, detail_ready))
print(f"6. Twin Detail data -> goal: {prof_body.get('financial_goal')}, summary len: {len(twin_body.get('financial_summary', ''))}")

passed = sum(1 for r in results if r[2])
print(f"\n=== PROMPT 2 E2E FLOW VERIFICATION: {passed}/{len(results)} PASSED ===")
for name, status, ok in results:
    print(f"  {'PASS' if ok else 'FAIL'} [{status}] {name}")

if passed != len(results):
    sys.exit(1)
