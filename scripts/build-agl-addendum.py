#!/usr/bin/env python3
"""Builds the round-five addendum PDF: assets/ai-governance-lab-round-five.pdf (7 x 10 in).
Edition 1 of the book is left as it was; this adds the 14 cases of 24 Oct 2026 and the framework map."""
import html, json, os, sys, threading, http.server, socketserver, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ai-governance-lab-round-five.pdf")
PORT = 8772
e = lambda s: html.escape(str(s), quote=True)
words = lambda s: str(s).replace("_", " ")
src = open(os.path.join(ROOT, "assets/agl-r5.js")).read()
R5 = json.loads(src[src.index("{"):src.rindex("}") + 1])
D0 = open(os.path.join(ROOT, "assets/agl-data.js")).read()
D = json.loads(D0[D0.index("{"):D0.rindex("}") + 1])
CSS = open(os.path.join(ROOT, "scripts/agl-book.css"), encoding="utf-8").read()
MARK = {"ok": ("Works", "ok"), "stop": ("Stopped", "stop"), "miss": ("Gets through", "miss"), "note": ("Step", "note")}
ORDER = ["V", "R", "I", "E"]
NAMES = {"V": "Vendor and third-party AI access", "R": "Retrieval and document permissions", "I": "Agent identity, more cases", "E": "Audit evidence, more cases"}

def case(c):
    k = R5["text"][c["id"]]
    steps = "".join(f'<li class="st {MARK[s[0]][1]}"><span class="tag">{MARK[s[0]][0]}</span> {e(s[1])}</li>' for s in k["steps"])
    return f'''<section class="case"><h4><span class="cid">{c["id"]}</span> {e(c["title"])}</h4>
<p class="what">{e(k["what"])}</p><ol class="steps">{steps}</ol>
<p class="res"><b>Result:</b> {e(k["result"])}</p><p class="why"><b>Why it matters:</b> {e(k["why"])}</p>
<p class="rounds">My guess: {e(words(c["expected"]))} &middot; What came out: {e(words(c["actual"]))}{"" if c["verdict"] == "as expected" else " <i>(different from my guess)</i>"}</p></section>'''

def key(c): return (ORDER.index(c["track"]), int(c["id"][1:]))
cases = sorted(R5["cases"], key=key)
body = ""
for t in ORDER:
    cs = [c for c in cases if c["track"] == t]
    body += f'<h3>Track {t}: {NAMES[t]}</h3>' + "".join(case(c) for c in cs)
old = R5["oldmap"]
rows = ""
for c in D["controls"]:
    m = old.get(c["id"])
    if m:
        rows += f'<tr><td><b>{c["id"]}</b> {e(c["control"])}</td><td>{e(m["iso27001"]) or "-"}</td><td>{e(m["nist80053"]) or "-"}</td><td>{e(m["pci"]) or "-"}</td><td>{e(m["hipaa"]) or "-"}</td></tr>'
for c in R5["controls"]:
    rows += f'<tr><td><b>{c["id"]}</b> {e(c["control"])} ({", ".join(c["cases"])})</td><td>{e(c["iso27001"])}</td><td>{e(c["nist80053"])}</td><td>{e(c["pci"])}</td><td>{e(c["hipaa"])}</td></tr>'
html_doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.titlepage{{height:8.2in}}</style></head><body>
<section class="titlepage"><p class="eyebrow">AI governance lab &middot; addendum</p><h1>Round five</h1>
<p class="sub">Fourteen more cases, written after I audited the lab: vendor &ldquo;read access&rdquo;, search that ignores file permissions, movers, access reviews, and the log. With the controls mapped to ISO 27001, NIST 800-53, PCI DSS and HIPAA.</p>
<p class="by">Roshan Trivedi<br><span style="font:400 10pt 'DM Sans';color:#52617a">24 October 2026 &middot; roshantrivedi.co.in/ai-governance-lab</span></p></section>
<section class="chapter" id="a1"><div class="chap-head"><span class="chapno">Read this first</span><h2>Why there is an addendum</h2></div>
<p class="lead">Edition one of &ldquo;Does AI Governance Hold?&rdquo; has 59 lab cases and nine assistant tests. After I audited it from an identity-governance view, I found gaps I had not tested.</p>
<p>The biggest was the sentence vendors use: &ldquo;our AI only needs read access on your domain&rdquo;. The lab did not test it. So I wrote the expected results for 14 new cases and committed them to the lab repository at 23:38 on 24 October 2026. Then I wrote the code and ran them.</p>
<p>All 14 came out as I guessed. Please read that carefully. It shows that the controls I added do what I built them to do. It does not show they are enough, because I wrote both the guess and the code. One case, I13, crashed on the first run because my test did not let time pass before issuing a new token. I fixed the test, not the lab, and kept both result files.</p>
<p>Everything here is made up: a lender called Kaveri Finance, and numbers that follow real formats (Aadhaar numbers pass the Verhoeff check, card numbers pass Luhn, PANs follow the format only). The numbers are random, so one could match a real person&rsquo;s by chance. None came from a real record.</p></section>
<section class="chapter" id="a2"><div class="chap-head"><span class="chapno">Part one</span><h2>The 14 cases</h2></div>{body}</section>
<section class="chapter" id="a3"><div class="chap-head"><span class="chapno">Part two</span><h2>Controls and where they sit</h2></div>
<p>The first sixteen controls were mapped to AI frameworks in edition one. This table shows the same controls against ISO/IEC 27001:2022 Annex A, NIST SP 800-53, PCI DSS 4.0 and HIPAA, plus seven new controls (C17 to C23). A dash means I did not map it. It is my own reading, not legal advice and not a certification. Check each number against your own copy of the standard.</p>
<table class="plain tiny"><thead><tr><th>Control</th><th>ISO 27001</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead><tbody>{rows}</tbody></table>
<p style="margin-top:10pt">For the Indian rules on the new controls: DPDP Act section 8 (safeguards and processors) and section 16 (transfers), the RBI master direction on outsourcing of IT services, and the CERT-In directions on logs.</p></section>
<section class="chapter" id="a4"><div class="chap-head"><span class="chapno">Part three</span><h2>What this still does not cover</h2></div>
<ul><li>These cases test small models of the controls (a consent register, a search with a permission list, an identity service). They do not connect to a real mail system, directory or cloud tenant.</li>
<li>Not tested: more than one hop of delegation between agents, real single sign-on and provisioning protocols, binding a token to the caller&rsquo;s key, real-time revocation signals between systems, and erasing one person from a hash-chained log.</li>
<li>The next big step on the vendor question is a test against a real sandbox tenant, with a real consent screen and a real directory.</li>
<li>If you can see a weak test, please tell me. I would rather learn it from you than from an incident.</li></ul>
<p style="margin-top:14pt"><b>Everything is free:</b> roshantrivedi.co.in/ai-governance-lab</p></section></body></html>'''

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def main():
    from playwright.sync_api import sync_playwright
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(); p = b.new_page()
            p.set_content(html_doc.replace("url(/assets/", f"url(http://localhost:{PORT}/assets/"), wait_until="networkidle"); p.wait_for_timeout(800)
            foot = '<div style="width:100%;font:9px DM Sans,Arial,sans-serif;color:#6b7a90;display:flex;justify-content:space-between;padding:0 0.7in"><span>Does AI Governance Hold? Addendum: round five &middot; Roshan Trivedi</span><span class="pageNumber"></span></div>'
            p.pdf(path=OUT, width="7in", height="10in", print_background=True, display_header_footer=True, header_template="<span></span>", footer_template=foot,
                  margin=dict(top="0.7in", bottom="0.85in", left="0.7in", right="0.7in"))
            b.close()
    finally:
        s.shutdown()
    from pypdf import PdfReader
    print(len(PdfReader(OUT).pages), "pages", os.path.getsize(OUT))
main()
