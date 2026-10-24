#!/usr/bin/env python3
"""Puts the round-five results and the framework map into ai-governance-lab/index.html (between markers, safe to re-run)."""
import re, json, html
src = open("assets/agl-r5.js").read()
R5 = json.loads(src[src.index("{"):src.rindex("}") + 1])
old = R5["oldmap"]
e = html.escape
def words(s): return e(str(s).replace("_", " "))
rows = "".join(
    f'<tr><td data-label="Case"><a href="/ai-governance-lab/cases/#{c["id"]}">{c["id"]}</a></td><td data-label="What I tested">{e(c["title"])}</td>'
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R5["cases"])
base = json.load(open("/dev/stdin")) if False else None
ctl_rows = ""
D = open("assets/agl-data.js").read()
D = json.loads(D[D.index("{"):D.rindex("}") + 1])
for c in D["controls"]:
    m = old.get(c["id"])
    if m:
        ctl_rows += f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])}</td><td data-label="ISO 27001:2022">{e(m["iso27001"]) or "—"}</td><td data-label="NIST 800-53">{e(m["nist80053"]) or "—"}</td><td data-label="PCI DSS 4.0">{e(m["pci"]) or "—"}</td><td data-label="HIPAA">{e(m["hipaa"]) or "—"}</td></tr>'
for c in R5["controls"]:
    ctl_rows += f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td><td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"])}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>'
block = f'''<!-- r5:start -->
      <section id="round5">
        <h2>Round five: gaps I found in my own audit</h2>
        <p class="body-text">After the first posts were drafted I audited the lab from an identity-governance view and found things I had not tested. The biggest was the sentence vendors use: &ldquo;our AI only needs read access on your domain&rdquo;. I wrote the expected results for 14 new cases first and committed them in the lab repository at 23:38 on 24 Oct 2026, then wrote the code and ran them. All 14 came out as I guessed. That says the controls I added do what I built them to do. It does not say they are enough, because I wrote both the guess and the code.</p>
        <p class="body-text">One case, I13, crashed on the first run because my test did not let any time pass before the new token was issued. I fixed the test, not the lab, and kept both result files.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <p class="body-text">Two of these show leaks on purpose: a plain search that ignores file permissions (R1) and a search index with an old copy of permissions (R2). A third shows a limit: a hash chain accepts a line with an earlier date (E16). Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#V1">case explorer</a>.</p>
      </section>

      <section id="frameworks">
        <h2>Where the controls sit in ISO 27001, NIST 800-53, PCI DSS and HIPAA</h2>
        <p class="body-text">The first sixteen controls were mapped to AI frameworks (ISO 42001, NIST AI RMF, the EU AI Act and Indian guidance), and that table is on the <a href="/ai-governance-lab/run/#agl-ctl">run page</a>. Auditors in finance and healthcare also ask about the older standards, so this table shows the same controls against ISO/IEC 27001:2022 Annex A, NIST SP 800-53, PCI DSS 4.0 and HIPAA, plus seven new controls (C17 to C23) for the round-five cases. A dash means I did not map it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">This is my own reading, not legal advice and not a certification. Standards change and numbering differs between versions, so check each reference against your own copy before you rely on it. For the Indian rules on the new controls: DPDP Act section 8 (safeguards, processors) and section 16 (transfers), the RBI master direction on outsourcing of IT services, and the CERT-In directions on logs.</p>
      </section>
<!-- r5:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r5:start -->.*?<!-- r5:end -->\n\n      ", "", h, flags=re.S)
h = h.replace('<section id="try">', block + '<section id="try">', 1)
h = h.replace("lists all 59 lab cases and the 9 assistant cases", "lists all 73 lab cases (59 from the first four rounds and 14 added in round five) and the 9 assistant cases")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count("round5"))
