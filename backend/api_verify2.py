import urllib.request, urllib.error, json, sys
import io
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
token = ""

# Full run from top
s, b = req("GET", "/health")
results.append(("GET /health", s, s==200 and b=={"status":"ok"}))
print(f"1. GET /health -> {s} {b}")

s, b = req("POST", "/api/auth/register", {"full_name":"Arjun Mehta","email":"arjun@test.com","password":"securePass456"})
results.append(("POST /api/auth/register valid->201", s, s==201 and "access_token" in b and "password_hash" not in str(b)))
token = b.get("access_token","")
print(f"2. POST /api/auth/register -> {s}, token:{'YES' if token else 'NO'}, pw_hash_exposed:{'password_hash' in str(b)}")

s, b = req("POST", "/api/auth/register", {"full_name":"Arjun Mehta","email":"arjun@test.com","password":"securePass456"})
results.append(("POST /api/auth/register duplicate->409", s, s==409))
print(f"3. Duplicate register -> {s} (expect 409)")

s, b = req("POST", "/api/auth/login", {"email":"arjun@test.com","password":"securePass456"})
results.append(("POST /api/auth/login valid->200", s, s==200 and "access_token" in b))
token = b.get("access_token", token)
print(f"4. POST /api/auth/login -> {s}, token:{'YES' if token else 'NO'}")

s, b = req("POST", "/api/auth/login", {"email":"arjun@test.com","password":"wrongpassword"})
results.append(("POST /api/auth/login wrong pw->401", s, s==401))
print(f"5. Login wrong pw -> {s} (expect 401)")

auth = {"Authorization": f"Bearer {token}"}

s, b = req("GET", "/api/auth/me", headers=auth)
results.append(("GET /api/auth/me valid->200", s, s==200 and b.get("onboarding_complete")==False))
print(f"6. GET /api/auth/me -> {s}, onboarding_complete:{b.get('onboarding_complete')}")

s, b = req("GET", "/api/auth/me")
results.append(("GET /api/auth/me no JWT->401", s, s==401))
print(f"7. GET /api/auth/me no JWT -> {s} (expect 401)")

s, b = req("GET", "/api/auth/me", headers={"Authorization":"Bearer badtoken"})
results.append(("GET /api/auth/me invalid JWT->401", s, s==401))
print(f"8. GET /api/auth/me invalid JWT -> {s} (expect 401)")

s, b = req("GET", "/api/profile", headers=auth)
results.append(("GET /api/profile before onboarding->404", s, s==404))
print(f"9. GET /api/profile before onboarding -> {s} (expect 404)")

profile = {"age":30,"gender":"Male","occupation":"Engineer","city":"Pune","monthly_income":75000,"monthly_expenses":40000,"savings":150000,"financial_goal":"Buy a car","risk_preference":"moderate","preferred_language":"Hindi","accessibility_mode":"standard"}
s, b = req("PUT", "/api/profile", profile, auth)
results.append(("PUT /api/profile->200", s, s==200 and b.get("occupation")=="Engineer"))
print(f"10. PUT /api/profile -> {s}, occupation:{b.get('occupation')}")

s, b = req("GET", "/api/profile", headers=auth)
results.append(("GET /api/profile after onboarding->200", s, s==200 and float(b.get("monthly_income",0))==75000))
print(f"11. GET /api/profile -> {s}, income:{b.get('monthly_income')}")

s, b = req("GET", "/api/financial-twin", headers=auth)
results.append(("GET /api/financial-twin before generate->404", s, s==404))
print(f"12. GET /api/financial-twin before generate -> {s} (expect 404)")

s, b = req("PUT", "/api/financial-twin/generate", headers=auth)
score = b.get("financial_health_score", -1)
risk = b.get("risk_level","")
summary = b.get("financial_summary","").encode("ascii","replace").decode()
results.append(("PUT /api/financial-twin/generate->200", s, s==200 and 0<=score<=100))
print(f"13. PUT /api/financial-twin/generate -> {s}, score:{score}, risk:{risk}")
print(f"    summary(ascii): {summary[:80]}")

s, b = req("GET", "/api/financial-twin", headers=auth)
results.append(("GET /api/financial-twin after generate->200", s, s==200 and b.get("user_id") is not None and b.get("financial_health_score")==score))
print(f"14. GET /api/financial-twin -> {s}, user_id:{b.get('user_id')}, score_match:{b.get('financial_health_score')==score}")

passed = sum(1 for r in results if r[2])
print(f"\n=== SUMMARY: {passed}/{len(results)} PASSED ===")
for name, status, ok in results:
    print(f"  {'PASS' if ok else 'FAIL'} [{status}] {name}")