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

# 1. GET /health
s, b = req("GET", "/health")
results.append(("1. Health check", s, s == 200))
print(f"1. Health check -> status: {s}")

# 2. Register User A
email_a = "saarthi_user_a@test.com"
s, b = req("POST", "/api/auth/register", {"full_name": "Rohan Sharma", "email": email_a, "password": "Password123!"})
if s == 409:
    s, b = req("POST", "/api/auth/login", {"email": email_a, "password": "Password123!"})

token_a = b.get("access_token", "")
auth_a = {"Authorization": f"Bearer {token_a}"}

# Onboard User A profile & twin
req("PUT", "/api/profile", {
    "age": 32, "gender": "Male", "occupation": "Product Manager", "city": "Bengaluru",
    "monthly_income": 120000, "monthly_expenses": 65000, "savings": 350000,
    "financial_goal": "Home Purchase", "risk_preference": "moderate",
    "preferred_language": "English", "accessibility_mode": "standard"
}, auth_a)
req("PUT", "/api/financial-twin/generate", headers=auth_a)
results.append(("2. Register & Onboard User A", s, bool(token_a)))
print(f"2. User A onboarded -> token received: {'YES' if token_a else 'NO'}")

# 3. AI Saarthi Chat - First Message
s_chat1, b_chat1 = req("POST", "/api/saarthi/chat", {"message": "How can I improve my financial health score?"}, auth_a)
session_id_a = b_chat1.get("session_id", "")
response_text1 = b_chat1.get("response", "")
ok_chat1 = s_chat1 == 200 and bool(session_id_a) and bool(response_text1)
results.append(("3. POST /api/saarthi/chat (First Turn)", s_chat1, ok_chat1))
print(f"3. First turn -> status: {s_chat1}, session_id: {session_id_a[:8]}...")
print(f"   Response snippet: {response_text1[:100]}...")

# 4. AI Saarthi Chat - Follow-up Turn
s_chat2, b_chat2 = req("POST", "/api/saarthi/chat", {
    "message": "What should I do first for my Home Purchase goal?",
    "session_id": session_id_a
}, auth_a)
response_text2 = b_chat2.get("response", "")
ok_chat2 = s_chat2 == 200 and b_chat2.get("session_id") == session_id_a and bool(response_text2)
results.append(("4. POST /api/saarthi/chat (Follow-up Turn)", s_chat2, ok_chat2))
print(f"4. Follow-up turn -> status: {s_chat2}")
print(f"   Response snippet: {response_text2[:100]}...")

# 5. User Isolation Security Test (Register User B & Attempt Access User A session)
email_b = "saarthi_user_b@test.com"
s_b, b_b = req("POST", "/api/auth/register", {"full_name": "Priya Patel", "email": email_b, "password": "Password123!"})
if s_b == 409:
    s_b, b_b = req("POST", "/api/auth/login", {"email": email_b, "password": "Password123!"})
token_b = b_b.get("access_token", "")
auth_b = {"Authorization": f"Bearer {token_b}"}

# User B attempts to access User A messages
s_leak, b_leak = req("GET", f"/api/saarthi/sessions/{session_id_a}/messages", headers=auth_b)
ok_isolation = s_leak in [403, 404]
results.append(("5. Session Ownership Security Isolation", s_leak, ok_isolation))
print(f"5. User B session access attempt -> status: {s_leak} (Expect 403/404) -> Isolated: {ok_isolation}")

passed = sum(1 for r in results if r[2])
print(f"\n=== PROMPT 3 AI SAARTHI LIVE VERIFICATION: {passed}/{len(results)} PASSED ===")
for name, status, ok in results:
    print(f"  {'PASS' if ok else 'FAIL'} [{status}] {name}")

if passed != len(results):
    sys.exit(1)
