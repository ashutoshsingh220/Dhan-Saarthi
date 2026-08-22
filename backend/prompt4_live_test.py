import urllib.request, urllib.error, json, sys, io
from datetime import date, timedelta
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

# 1. Health check
s, b = req("GET", "/health")
results.append(("1. Health check", s, s == 200))

# 2. Register & Onboard User A
email_a = "planner_live_a@test.com"
s_a, b_a = req("POST", "/api/auth/register", {"full_name": "Aarav Gupta", "email": email_a, "password": "Password123!"})
if s_a == 409:
    s_a, b_a = req("POST", "/api/auth/login", {"email": email_a, "password": "Password123!"})
token_a = b_a.get("access_token", "")
auth_a = {"Authorization": f"Bearer {token_a}"}

req("PUT", "/api/profile", {
    "age": 30, "gender": "Male", "occupation": "Software Developer", "city": "Pune",
    "monthly_income": 120000, "monthly_expenses": 60000, "savings": 200000,
    "financial_goal": "Home Downpayment", "risk_preference": "moderate",
    "preferred_language": "English", "accessibility_mode": "standard"
}, auth_a)
req("PUT", "/api/financial-twin/generate", headers=auth_a)
results.append(("2. Register & Onboard User A", s_a, bool(token_a)))

# 3. Create Financial Goal & Calculate Plan
target_date_str = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
s_goal, b_goal = req("POST", "/api/planning/goals", {
    "name": "Home Downpayment Goal",
    "category": "home",
    "target_amount": 240000,
    "current_amount": 20000,
    "target_date": target_date_str
}, auth_a)

goal_id_a = b_goal.get("id", "")
plan = b_goal.get("plan", {})
feasibility = plan.get("feasibility_status", "")
req_monthly = plan.get("monthly_required", 0)
ok_goal = s_goal == 201 and bool(goal_id_a) and feasibility == "FEASIBLE" and req_monthly > 0
results.append(("3. POST /api/planning/goals (Create Goal & Plan)", s_goal, ok_goal))
print(f"3. Created Goal '{b_goal.get('name')}' -> ID: {goal_id_a[:8]}..., Feasibility: {feasibility}, Required: ₹{req_monthly:,.2f}/mo")

# 4. Record Progress (+50,000)
s_prog, b_prog = req("POST", f"/api/planning/goals/{goal_id_a}/progress", {"amount": 50000}, auth_a)
new_curr = b_prog.get("current_amount", 0)
ok_prog = s_prog == 200 and new_curr == 70000
results.append(("4. POST /api/planning/goals/{id}/progress (+₹50k)", s_prog, ok_prog))
print(f"4. Updated Progress -> Current Saved: ₹{new_curr:,.2f}")

# 5. Ask AI Saarthi to explain plan
s_ai, b_ai = req("POST", "/api/saarthi/chat", {"message": "Can you explain my Home Downpayment Goal financial plan?"}, auth_a)
ai_resp = b_ai.get("response", "")
ok_ai = s_ai == 200 and bool(ai_resp)
results.append(("5. AI Saarthi Plan Explanation Integration", s_ai, ok_ai))
print(f"5. AI Saarthi Response Snippet: {ai_resp[:120]}...")

# 6. Session & User Isolation (User B attempts access to User A goal)
email_b = "planner_live_b@test.com"
s_b, b_b = req("POST", "/api/auth/register", {"full_name": "Neha Verma", "email": email_b, "password": "Password123!"})
if s_b == 409:
    s_b, b_b = req("POST", "/api/auth/login", {"email": email_b, "password": "Password123!"})
token_b = b_b.get("access_token", "")
auth_b = {"Authorization": f"Bearer {token_b}"}

s_leak, b_leak = req("GET", f"/api/planning/goals/{goal_id_a}", headers=auth_b)
ok_isolation = s_leak in [403, 404]
results.append(("6. Goal Ownership Security Isolation", s_leak, ok_isolation))
print(f"6. User B goal access attempt -> status: {s_leak} (Expect 403/404) -> Isolated: {ok_isolation}")

passed = sum(1 for r in results if r[2])
print(f"\n=== PROMPT 4 SMART PLANNING LIVE VERIFICATION: {passed}/{len(results)} PASSED ===")
for name, status, ok in results:
    print(f"  {'PASS' if ok else 'FAIL'} [{status}] {name}")

if passed != len(results):
    sys.exit(1)
