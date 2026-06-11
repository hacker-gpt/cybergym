"""
Core harness for solving the OWASP Juice Shop CTF hosted on ctf.hackergpt.app
via MultiJuicer (team: absolute-team).

Every request must carry the MultiJuicer routing cookie so the balancer proxies
to our team's Juice Shop pod. Attempts (success + failure) are logged to
attempts.jsonl with an approach description for the final report.
"""
import json, os, time, datetime, base64, requests, urllib3
urllib3.disable_warnings()

BASE = "https://ctf.hackergpt.app"
ROUTING_COOKIE = {"multi-juicer": "absolute-team.IuqnRPSFzDvPi/9o7FH6tpScwz1xtXPBnnVv8B562ts"}
HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPTS = os.path.join(HERE, "attempts.jsonl")

class Session:
    def __init__(self):
        self.s = requests.Session()
        self.s.verify = False
        self.s.cookies.update(ROUTING_COOKIE)
        self.s.headers.update({"User-Agent": "Mozilla/5.0 ctf-solver"})
        self.token = None
        self.email = None

    def req(self, method, path, auth=True, **kw):
        url = path if path.startswith("http") else BASE + path
        headers = kw.pop("headers", {})
        if auth and self.token:
            headers["Authorization"] = "Bearer " + self.token
        return self.s.request(method, url, headers=headers, timeout=40, **kw)

    def get(self, path, **kw):  return self.req("GET", path, **kw)
    def post(self, path, **kw): return self.req("POST", path, **kw)
    def put(self, path, **kw):  return self.req("PUT", path, **kw)
    def delete(self, path, **kw): return self.req("DELETE", path, **kw)

    # ---- auth ----
    def register(self, email, password, secanswer="test", secquestion=2):
        r = self.post("/api/Users/", auth=False, json={
            "email": email, "password": password, "passwordRepeat": password,
            "securityQuestion": {"id": secquestion, "question": "Q", "createdAt": ""},
            "securityAnswer": secanswer, "role": "customer"})
        return r

    def login(self, email, password, totp=None):
        body = {"email": email, "password": password}
        if totp: body["totpToken"] = totp
        r = self.post("/rest/user/login", auth=False, json=body)
        if r.status_code == 200 and "authentication" in r.text:
            self.token = r.json()["authentication"]["token"]
            self.email = email
        return r

# ---- challenge status ----
def challenge_status(sess=None):
    s = sess.s if sess else requests.Session()
    if not sess:
        s.verify = False; s.cookies.update(ROUTING_COOKIE)
    r = s.get(BASE + "/api/Challenges/", verify=False, timeout=40)
    data = r.json()["data"]
    return {c["key"]: c for c in data}

def solved_set(sess=None):
    return {k for k, c in challenge_status(sess).items() if c.get("solved")}

# ---- attempt logging ----
def log_attempt(key, name, approach, result, solved, detail=""):
    rec = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "key": key, "name": name, "approach": approach,
        "result": result, "solved": solved, "detail": str(detail)[:800],
    }
    with open(ATTEMPTS, "a") as f:
        f.write(json.dumps(rec) + "\n")
    flag = "SOLVED ✅" if solved else "----- ❌"
    print(f"  [{flag}] {key}: {result}")
    return solved

def jwt_decode(tok):
    p = tok.split(".")[1]
    p += "=" * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p))

if __name__ == "__main__":
    st = challenge_status()
    print("Total:", len(st), "Solved:", sum(1 for c in st.values() if c["solved"]))
