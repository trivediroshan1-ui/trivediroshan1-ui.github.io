#!/usr/bin/env python3
"""Builds the addendum PDF for rounds five to twelve: assets/ai-governance-lab-addendum.pdf (7 x 10 in).
Edition 1 of the book and the round-five addendum are left as they were. This one adds rounds six to eight (25 Oct 2026),
the four new architecture diagrams, and one table of all controls. Run: python3 scripts/build-agl-addendum2.py"""
import base64, functools, html, http.server, json, os, socketserver, threading
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ai-governance-lab-addendum.pdf")
TMP = os.environ.get("ADD_TMP", "/tmp/agl-addendum"); os.makedirs(TMP, exist_ok=True)
PORT = 8773
e = lambda s: html.escape(str(s), quote=True)
words = lambda s: str(s).replace("_", " ")
def load(name):
    s = open(os.path.join(ROOT, f"assets/{name}.js")).read(); return json.loads(s[s.index("{"):s.rindex("}") + 1])
R = {5: load("agl-r5"), 6: load("agl-r6"), 7: load("agl-r7"), 8: load("agl-r8"), 9: load("agl-r9"), 10: load("agl-r10"), 11: load("agl-r11"), 12: load("agl-r12")}
D = load("agl-data")
CSS = open(os.path.join(ROOT, "scripts/agl-book.css"), encoding="utf-8").read()
MARK = {"ok": ("Works", "ok"), "stop": ("Stopped", "stop"), "miss": ("Gets through", "miss"), "note": ("Step", "note")}

def case(r, c):
    k = R[r]["text"][c["id"]]
    steps = "".join(f'<li class="st {MARK[s[0]][1]}"><span class="tag">{MARK[s[0]][0]}</span> {e(s[1])}</li>' for s in k["steps"])
    return f'''<section class="case"><h4><span class="cid">{c["id"]}</span> {e(c["title"])}</h4>
<p class="what">{e(k["what"])}</p><ol class="steps">{steps}</ol>
<p class="res"><b>Result:</b> {e(k["result"])}</p><p class="why"><b>Why it matters:</b> {e(k["why"])}</p>
<p class="rounds">My guess: {e(words(c["expected"]))} &middot; What came out: {e(words(c["actual"]))}{"" if c["verdict"] == "as expected" else " <i>(different from my guess)</i>"}</p></section>'''

def tracks(r, order, names):
    out = ""
    for t in order:
        cs = sorted([c for c in R[r]["cases"] if c["track"] == t], key=lambda c: int(c["id"][1:]))
        if cs: out += f'<h3>{names[t]}</h3>' + "".join(case(r, c) for c in cs)
    return out

def diagram(key, title, cap):
    p = os.path.join(TMP, f"{key}.png")
    with open(p, "rb") as f: b = base64.b64encode(f.read()).decode()
    return f'<figure class="fig"><img src="data:image/png;base64,{b}" alt="{e(title)}"><figcaption><b>{e(title)}.</b> {e(cap)}</figcaption></figure>'

def render_diagrams():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for k in ("gate", "hr", "bypass", "org", "lab"):
            svg = open(os.path.join(ROOT, f"assets/diagrams/agl-{k}.svg"), encoding="utf-8").read().split("?>", 1)[1]
            pg = b.new_page(viewport={"width": 700, "height": 900}, device_scale_factor=2, color_scheme="light", reduced_motion="reduce")
            pg.set_content(f"<body style='margin:0;background:#fff'>{svg}</body>")
            pg.wait_for_timeout(300)
            pg.query_selector("svg").screenshot(path=os.path.join(TMP, f"{k}.png"))
        b.close()

def control_rows():
    rows = ""
    old = R[5]["oldmap"]
    for c in D["controls"]:
        m = old.get(c["id"])
        if m: rows += f'<tr><td><b>{c["id"]}</b> {e(c["control"])}</td><td>{e(m["iso27001"]) or "-"}</td><td>{e(m["nist80053"]) or "-"}</td><td>{e(m["pci"]) or "-"}</td><td>{e(m["hipaa"]) or "-"}</td></tr>'
    for r in (5, 6, 7, 8, 9, 10, 11, 12):
        for c in R[r]["controls"]:
            rows += f'<tr><td><b>{c["id"]}</b> {e(c["control"])} ({", ".join(c["cases"])})</td><td>{e(c["iso27001"]) or "-"}</td><td>{e(c["nist80053"]) or "-"}</td><td>{e(c["pci"]) or "-"}</td><td>{e(c["hipaa"]) or "-"}</td></tr>'
    return rows

def build_html():
    m6, m7, m8, m9, m10, m11, m12 = R[6]["mutations"], R[7]["mutations"], R[8]["mutations"], R[9]["mutations"], R[10]["mutations"], R[11]["mutations"], R[12]["mutations"]
    menu = f'''<table class="plain"><thead><tr><th>Part</th><th>What it asks</th><th>Cases</th><th>Result</th></tr></thead><tbody>
<tr><td><b>Round five</b><br>24 Oct</td><td>Vendor &ldquo;read access&rdquo;, search that ignores file permissions, movers, access reviews, the log</td><td>14 (V, R, I, E)</td><td>All as guessed</td></tr>
<tr><td><b>Round six</b><br>25 Oct, 00:28 IST</td><td>If an agent only sends instructions to an identity API, what has to stand between it and the credentials?</td><td>18 (T1 to T18)</td><td>All as guessed; {m6["noticed"]} of {m6["total"]} control-off checks noticed</td></tr>
<tr><td><b>Round seven</b><br>25 Oct, 00:43 IST</td><td>How should an identity start? HR approval, two people, the minimum data, day-one MFA, reconciliation</td><td>12 (H1 to H12)</td><td>All as guessed; {m7["first_run_noticed"]} of {m7["first_run_total"]} first time, {m7["noticed"]} of {m7["total"]} after I fixed a weak test</td></tr>
<tr><td><b>Round eight</b><br>25 Oct, 01:07 IST</td><td>What if the agent goes round the gateway? Notice it, answer it, keep the evidence</td><td>12 (B1 to B12)</td><td>All as guessed; {m8["noticed"]} of {m8["total"]} control-off checks noticed</td></tr>
<tr><td><b>Round nine</b><br>25 Oct, 02:26 IST</td><td>An assistant that answers from documents: where is the permission checked, and what still leaks?</td><td>12 (Q1 to Q12)</td><td>All as guessed after I fixed a fault in my own code (first run {R[9]["first_run"]["as_expected"]} of {R[9]["first_run"]["total"]}); {m9["noticed"]} of {m9["total"]} control-off checks noticed</td></tr>
<tr><td><b>Round ten</b><br>25 Oct, 03:53 IST</td><td>The identity edge cases: copied tokens, revoke signals, sync, rehires, name changes, contractors, break-glass, erasure, clocks</td><td>12 (C1 to C12)</td><td>All as guessed the first time; {m10["noticed"]} of {m10["total"]} control-off checks noticed (C2 is a limit and has none)</td></tr>
<tr><td><b>Round eleven</b><br>25 Oct, 04:10 IST</td><td>Agents handing work to agents, real public-key signing, a compromised executor or gateway, key rotation, merged directories, replays, PAN masking</td><td>12 (D1 to D12)</td><td>All as guessed after I fixed a fault in my own test (first run {R[11]["first_run"]["as_expected"]} of {R[11]["first_run"]["total"]}); {m11["noticed"]} of {m11["total"]} control-off checks noticed (D12 is a limit and has none)</td></tr>
<tr><td><b>Round twelve</b><br>25 Oct, 04:58 IST</td><td>Approvals: self-approval, an edit after approval, one-click batches, stale approvals, an approver who leaves, split votes, two people approving each other</td><td>7 (F1 to F7)</td><td>All as guessed the first time; {m12["noticed"]} of {m12["total"]} control-off checks noticed (F7 is a limit and has none)</td></tr></tbody></table>'''
    figs = (diagram("lab", "The lab as a whole", "Four tracks, twelve rounds, an unseen-items test and a real assistant.") +
            diagram("gate", "The agent proposes; a gateway decides; an executor acts", "The agent holds no credential. A leaked token used directly is refused.") +
            diagram("hr", "From HR to the directory", "An identity starts in HR. A request with no approved hire event stops at step five.") +
            diagram("bypass", "How a bypass is noticed and answered", "Compare the identity system's log with the signed decisions, act at once, keep the evidence, let a person decide.") +
            diagram("org", "One set of controls, many business units", "The same controls for everyone, local decisions per business unit, policy down and reports up."))
    names5 = {"V": "Track V: Vendor and third-party AI access", "R": "Track R: Retrieval and document permissions", "I": "Track I: Agent identity, more cases", "E": "Track E: Audit evidence, more cases"}
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
.titlepage{{height:8.2in}}.fig{{margin:0 0 12pt;break-inside:avoid-page;text-align:center}}.fig img{{max-width:100%;max-height:6.6in;border:1px solid #cfd8e3;border-radius:6px}}.fig figcaption{{font-size:8.6pt;color:#52617a;margin-top:4pt;text-align:left}}</style></head><body>
<section class="titlepage"><p class="eyebrow">AI governance lab &middot; addendum</p><h1>Rounds five to twelve</h1>
<p class="sub">Ninety-nine more cases, each guessed before the code was written: vendors, retrieval, identity, the HR side of onboarding, agents that only send instructions, what happens when one goes round the gateway, an assistant that answers from documents, the identity edge cases from my open list, agents handing work to agents with real public-key signing, and approvals. With five diagrams and one table of the controls against ISO 27001, NIST 800-53, PCI DSS and HIPAA.</p>
<p class="by">Roshan Trivedi<br><span style="font:400 10pt 'DM Sans';color:#52617a">25 October 2026 &middot; roshantrivedi.co.in/ai-governance-lab</span></p></section>
<section class="chapter"><div class="chap-head"><span class="chapno">Read this first</span><h2>What is in here, in the order to read it</h2></div>
<p class="lead">Edition one of &ldquo;Does AI Governance Hold?&rdquo; has 59 lab cases and nine assistant tests. This addendum adds eight rounds, written after I audited the lab and questioned my own diagrams.</p>
{menu}
<p style="margin-top:10pt">Rounds five to twelve were each run twice, first in a Linux sandbox and then on a MacBook Air (Python 3.9.6), with the same verdicts. Every round follows the same method. I wrote what I expected for each case and committed it to the lab repository before writing the code, and I give the SHA-256 of each file so you can check it. After the run, I switched off the controls one at a time in a copy of the code to see whether the matching case noticed. Where a test was weak, I say so.</p>
<p>Everything is made up: a lender called Kaveri Finance and numbers that follow real formats on purpose. The AI model behind an agent is not tested. Each case assumes the agent was fooled or wrong and tests the wall around it. All &ldquo;as expected&rdquo; results show that my rules do what I built them to do, not that I thought of every attack, because I wrote both the guess and the code.</p></section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part one</span><h2>The pictures</h2></div>
<p class="lead">On the website these are animated. Here they are still.</p>{figs}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part two</span><h2>Round five: the audit gaps</h2></div>
<p>Fourteen cases, committed at 23:38 on 24 October 2026 (SHA-256 {R[5]["cases_sha256"]}). All 14 came out as I guessed.</p>{tracks(5, ["V", "R", "I", "E"], names5)}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part three</span><h2>Round six: the agent only sends instructions</h2></div>
<p>The question: if an agent never acts on identities itself, what has to stand between it and the credentials? A gateway checks the request and signs a decision. A separate executor borrows a five-minute credential from a vault and calls the identity API. The agent never holds the credential. Eighteen cases, committed at 00:28 IST on 25 October (SHA-256 {R[6]["cases_sha256"]}). All 18 came out as I guessed. {m6["noticed"]} of {m6["total"]} controls switched off were noticed.</p>{tracks(6, ["T"], {"T": "Track T: Agent instructions to an identity API"})}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part four</span><h2>Round seven: how an identity starts</h2></div>
<p>My first diagram started in the middle, with an agent sending a request. On a second look, an identity starts earlier, in HR. Twelve cases, committed at 00:43 IST (SHA-256 {R[7]["cases_sha256"]}). All 12 came out as I guessed. The first control-off run noticed {m7["first_run_noticed"]} of {m7["first_run_total"]}: my MFA test could not tell a missing MFA step from a missing signed policy. I rebuilt it and {m7["noticed"]} of {m7["total"]} were noticed. Both result files are kept.</p>{tracks(7, ["H"], {"H": "Track H: HR-driven identity lifecycle"})}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part five</span><h2>Round eight: when an agent goes round the gateway</h2></div>
<p>The pattern only works if the agent cannot get round it. Three layers: make it hard (a credential works only from the caller it was lent to, and the agent has no network route to the API), notice (every change in the identity system&rsquo;s log must match a signed decision) and answer (switch off what can be traced, keep the evidence, let a person decide what to undo). Twelve cases, committed at 01:07 IST (SHA-256 {R[8]["cases_sha256"]}). All 12 came out as I guessed. {m8["noticed"]} of {m8["total"]} controls switched off were noticed.</p>{tracks(8, ["B"], {"B": "Track B: Bypass, response, lists and evidence"})}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part six</span><h2>Round nine: an assistant that answers from documents</h2></div>
<p>Most company assistants search your documents and let a model write the answer. The question for governance: where is the permission checked, and what still leaks? Twelve cases, committed at 02:26 IST on 25 October (SHA-256 {R[9]["cases_sha256"]}). The first run gave {R[9]["first_run"]["as_expected"]} of {R[9]["first_run"]["total"]} as I guessed. The one that differed, Q8, was a fault in my own masking code (it only caught Aadhaar numbers written with spaces). I fixed the code, not the guess, and all 12 then came out as guessed. Both result files are kept. {m9["noticed"]} of {m9["total"]} controls switched off were noticed, though some of those checks are weak: for Q1 and Q2 they only show the case reacts when the leaking mode is changed, and for Q5 the gateway crashes instead of accepting the request.</p>{tracks(9, ["Q"], {"Q": "Track Q: Retrieval-augmented answers"})}<p>Three stronger control-off checks were added afterwards for Q1, Q2 and Q5, the weakest of the twelve. Q1 and Q2 now also remove the careless-model assumption (the model stops repeating restricted text, or obeys the &ldquo;do not reveal&rdquo; label), and both are noticed. The new Q5 check lets an unlisted action through the gateway and skips the shape check; the case does not notice, because a second layer, the executor, still refuses the request. Result: 14 of 15 noticed, the same in the sandbox and on my Mac. The old results are kept.</p></section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part seven</span><h2>Round ten: credentials, sessions and identity edge cases</h2></div>
<p>The identity basics from my open list: a copied token, a person who leaves while their session is alive, a sync that switches a disabled account back on, a rehire, a surname change, an agency contractor, an emergency account, a request to erase a name from a hash-chained log, and a clock that is wrong. Twelve cases, committed at 03:53 IST on 25 October (SHA-256 {R[10]["cases_sha256"]}). All 12 came out as I guessed the first time, which says my guesses were easy, not that real systems are safe. {m10["noticed"]} of {m10["total"]} controls switched off were noticed; C2 is a limit (a thief who has the token and the key) and has no such check. The proof of a key uses a shared secret as a stand-in for a public key, and C6 assumes a server that defaults &lsquo;active&rsquo; to true.</p>{tracks(10, ["C"], {"C": "Track C: Credentials, sessions and identity edge cases"})}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part eight</span><h2>Round eleven: agents handing work to agents, keys and mergers</h2></div>
<p>What happens when one agent hands work to another, what a compromised executor or gateway can sign, what a replayed request does, what a rotated key does, what two merged companies do to staff IDs, and whether PAN is masked as well as Aadhaar. Twelve cases, committed at 04:10 IST on 25 October (SHA-256 {R[11]["cases_sha256"]}). The first run gave {R[11]["first_run"]["as_expected"]} of {R[11]["first_run"]["total"]} as I guessed; the one that differed, D11, was a fault in my own test (it searched for one number written three ways), and I fixed the test, not the guess. I also reworked D12 afterwards, because the real limit is data handed from one agent to another. All 12 then came out as guessed, and {m11["noticed"]} of {m11["total"]} controls switched off were noticed (D12 is a limit and has no such check). The signatures are real Ed25519, in my own plain-Python version checked against a well-known library; it is for these tests only.</p>{tracks(11, ["D"], {"D": "Track D: Delegation, keys and organisations"})}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part nine</span><h2>Round twelve: approvals</h2></div>
<p>Every earlier round assumed a human approval step. This one tests it: who approved, was it the person who asked, did they approve what finally ran, was it still true when it ran, what if the approver left, and what if two approvers disagreed. Seven cases, committed at 04:58 IST on 25 October (SHA-256 {R[12]["cases_sha256"]}). All 7 came out as I guessed the first time, which says my guesses were easy, not that approvals are safe. {m12["noticed"]} of {m12["total"]} controls switched off were noticed; F7 (two people approving each other&rsquo;s requests) is a limit and has no such check. The approval queue is a small model I wrote, with no real approval product, no real people and no AI model. It ran in a sandbox and on my MacBook Air with the same verdicts.</p>{tracks(12, ["F"], {"F": "Track F: Approvals"})}</section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part ten</span><h2>Controls and where they sit</h2></div>
<p>The controls mapped to ISO/IEC 27001:2022 Annex A, NIST SP 800-53, PCI DSS 4.0 and HIPAA. A dash means I did not find a direct match. This is my own reading, not legal advice and not a certification. Check each reference against your own copy of the standard.</p>
<table class="plain tiny"><thead><tr><th>Control</th><th>ISO 27001</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead><tbody>{control_rows()}</tbody></table>
<p style="margin-top:10pt">Indian rules touched by the later rounds: the DPDP Act (minimisation, purpose, safeguards), the RBI direction on IT outsourcing and cyber security, the CERT-In directions on logs and incident reporting, and the Rights of Persons with Disabilities Act 2016 for accessible sign-in. I have not reproduced their text here. Ask counsel what applies.</p></section>
<section class="chapter"><div class="chap-head"><span class="chapno">Part eleven</span><h2>What this still does not cover</h2></div>
<ul><li>The vault, the identity API, the HR system, the directory, the network and the log are small models I wrote. They are not HashiCorp Vault, Delinea, SCIM products, Workday, SailPoint, Entra or Active Directory.</li>
<li>The document search is plain keyword matching, not a vector database, and the model that writes answers is a stand-in that repeats what it is given. Q10 (two allowed documents combine into something restricted) is a limit that no permission check stops.</li>
<li>No real agent tries to get round the wall. Each case makes it do the wrong thing and checks what stands in the way.</li>
<li>Not tested: real SCIM or Graph calls, real mutual TLS or token binding (round ten uses a stand-in), real approval products and real people (round twelve uses a small stand-in queue), a real identity provider, more than one country, and what a chain of allowed agents can do together (D12 is a limit). Real public-key signing, mergers and a compromised gateway or executor are modelled in round eleven, with small stand-ins.</li>
<li>Changes made by other approved paths, such as the HR sync job, are not part of the reconciliation. If a bypass makes exactly the same change as a real request at the same moment, only the extra one is flagged.</li>
<li>What counts as an offence, what may be monitored and what a court accepts are for counsel, not this lab.</li>
<li>The next big step is a test against a real sandbox tenant, and a held-out set of cases written by someone other than me. If you can see a weak test, please tell me. I would rather learn it from you than from an incident.</li></ul>
<p style="margin-top:14pt"><b>Everything is free:</b> roshantrivedi.co.in/ai-governance-lab</p></section></body></html>'''

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def main():
    from playwright.sync_api import sync_playwright
    render_diagrams()
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(); p = b.new_page()
            p.set_content(build_html().replace("url(/assets/", f"url(http://localhost:{PORT}/assets/"), wait_until="networkidle"); p.wait_for_timeout(800)
            foot = '<div style="width:100%;font:9px DM Sans,Arial,sans-serif;color:#6b7a90;display:flex;justify-content:space-between;padding:0 0.7in"><span>Does AI Governance Hold? Addendum: rounds five to twelve &middot; Roshan Trivedi</span><span class="pageNumber"></span></div>'
            p.pdf(path=OUT, width="7in", height="10in", print_background=True, display_header_footer=True, header_template="<span></span>", footer_template=foot,
                  margin=dict(top="0.7in", bottom="0.85in", left="0.7in", right="0.7in"))
            b.close()
    finally:
        s.shutdown()
    from pypdf import PdfReader
    print(len(PdfReader(OUT).pages), "pages", os.path.getsize(OUT))
main()
