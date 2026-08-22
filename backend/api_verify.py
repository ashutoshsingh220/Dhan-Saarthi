import urllib.request, urllib.error, json

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

# 1. GET /health
s, b = req("GET", "/health")
ok = s == 200 and b == {"status": "ok"}
results.append(("GET /health", s, ok))
print(f"1. GET /health -> {s} {b}")

# 2. POST register valid
s, b = req("POST", "/api/auth/register", {"full_name":"Priya Verma","email":"priya@test.com","password":"securePass123"})
ok = s == 201 and "access_token" in b and "password_hash" not in str(b)
results.append(("POST /api/auth/register valid", s, ok))
token = b.get("access_token", "")
print(f"2. POST /api/auth/register valid -> {s}, token: {'YES' if token else 'NO'}, no_pw_hash: {'password_hash' not in str(b)}")

# 3. POST register duplicate
s, b = req("POST", "/api/auth/register", {"full_name":"Priya Verma","email":"priya@test.com","password":"securePass123"})
ok = s == 409
results.append(("POST /api/auth/register duplicate->409", s, ok))
print(f"3. POST /api/auth/register duplicate -> {s} (expect 409)")

# 4. POST login valid
s, b = req("POST", "/api/auth/login", {"email":"priya@test.com","password":"securePass123"})
ok = s == 200 and "access_token" in b
results.append(("POST /api/auth/login valid", s, ok))
token = b.get("access_token", token)
print(f"4. POST /api/auth/login valid -> {s}, has token: {'YES' if token else 'NO'}")

# 5. POST login wrong password
s, b = req("POST", "/api/auth/login", {"email":"priya@test.com","password":"wrongpassword"})
ok = s == 401
results.append(("POST /api/auth/login wrong pw->401", s, ok))
print(f"5. POST /api/auth/login wrong pw -> {s} (expect 401)")

auth = {"Authorization": f"Bearer {token}"}

# 6. GET /api/auth/me valid JWT
s, b = req("GET", "/api/auth/me", headers=auth)
ok = s == 200 and b.get("onboarding_complete") == False
results.append(("GET /api/auth/me valid JWT", s, ok))
print(f"6. GET /api/auth/me valid -> {s}, onboarding_complete: {b.get('onboarding_complete')}")

# 7. GET /api/auth/me no JWT
s, b = req("GET", "/api/auth/me")
ok = s == 401
results.append(("GET /api/auth/me no JWT->401", s, ok))
print(f"7. GET /api/auth/me no JWT -> {s} (expect 401)")

# 8. GET /api/auth/me invalid JWT
s, b = req("GET", "/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
ok = s == 401
results.append(("GET /api/auth/me invalid JWT->401", s, ok))
print(f"8. GET /api/auth/me invalid JWT -> {s} (expect 401)")

# 9. GET /api/profile before onboarding
s, b = req("GET", "/api/profile", headers=auth)
ok = s == 404
results.append(("GET /api/profile before onboarding->404", s, ok))
print(f"9. GET /api/profile before onboarding -> {s} (expect 404)")

# 10. PUT /api/profile
profile = {"age":26,"gender":"Female","occupation":"Software Engineer","city":"Mumbai","monthly_income":80000,"monthly_expenses":45000,"savings":200000,"financial_goal":"Emergency fund","risk_preference":"moderate","preferred_language":"English","accessibility_mode":"standard"}
s, b = req("PUT", "/api/profile", profile, auth)
ok = s == 200 and b.get("occupation") == "Software Engineer"
results.append(("PUT /api/profile", s, ok))
print(f"10. PUT /api/profile -> {s}, occupation: {b.get('occupation')}")

# 11. GET /api/profile after onboarding
s, b = req("GET", "/api/profile", headers=auth)
ok = s == 200 and b.get("monthly_income") is not None
results.append(("GET /api/profile after onboarding", s, ok))
print(f"11. GET /api/profile after onboarding -> {s}, income: {b.get('monthly_income')}")

# 12. GET /api/financial-twin before generate
s, b = req("GET", "/api/financial-twin", headers=auth)
ok = s == 404
results.append(("GET /api/financial-twin before generate->404", s, ok))
print(f"12. GET /api/financial-twin before generate -> {s} (expect 404)")

# 13. PUT /api/financial-twin/generate
s, b = req("PUT", "/api/financial-twin/generate", headers=auth)
score = b.get("financial_health_score", -1)
ok = s == 200 and 0 <= score <= 100
results.append(("PUT /api/financial-twin/generate", s, ok))
print(f"13. PUT /api/financial-twin/generate -> {s}, score: {score}, risk: {b.get('risk_level')}")
print(f"    summary: {str(b.get('financial_summary',''))[:90]}")

# 14. GET /api/financial-twin after generate
s, b = req("GET", "/api/financial-twin", headers=auth)
ok = s == 200 and b.get("user_id") is not None and b.get("financial_health_score") == score
results.append(("GET /api/financial-twin after generate", s, ok))
print(f"14. GET /api/financial-twin after generate -> {s}, user_id: {b.get('user_id')}, score matches: {b.get('financial_health_score')==score}")

# Summary
passed = sum(1 for r in results if r[2])
print(f"\n=== SUMMARY: {passed}/{len(results)} PASSED ===")
for name, status, ok in results:
    print(f"  {'PASS' if ok else 'FAIL'} [{status}] {name}")