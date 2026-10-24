#!/usr/bin/env python3
"""Puts the round-six section (agents that send instructions to an identity API) into ai-governance-lab/index.html
between markers, after the round-five block. Safe to re-run. Also copies the guesses file next to the site so its hash can be checked."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r6.js").read()
R6 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-6.json", "assets/ai-governance-lab-round-six-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-six-guesses.json", "rb").read()).hexdigest()
assert sha == R6["cases_sha256"], (sha, R6["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))
rows = "".join(
    f'<tr><td data-label="Case"><a href="/ai-governance-lab/cases/#{c["id"]}">{c["id"]}</a></td><td data-label="What I tested">{e(c["title"])}</td>'
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R6["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"])}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R6["controls"])
m = R6["mutations"]

SVG = '''<figure style="margin:1.4rem 0">
          <svg viewBox="0 0 460 470" role="img" aria-label="An agent sends a request to a gateway. A person approves risky requests. The gateway signs a decision for an executor. The executor borrows a short-lived credential from a vault and calls the identity API. The agent has no access to the vault. Every step is written to an audit log." style="max-width:100%;height:auto;display:block;margin:0 auto;font-size:12px" font-family="inherit">
            <defs><marker id="r6a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
            <g fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="140" y="10" width="180" height="54" rx="8"/>
              <rect x="140" y="112" width="180" height="64" rx="8" stroke="#7df2d0"/>
              <rect x="140" y="214" width="180" height="64" rx="8"/>
              <rect x="140" y="316" width="180" height="64" rx="8"/>
              <rect x="10" y="118" width="100" height="52" rx="8" stroke="#f7c873"/>
              <rect x="350" y="214" width="100" height="64" rx="8" stroke="#c4b5fd"/>
              <rect x="10" y="412" width="440" height="40" rx="8" stroke-dasharray="4 4"/>
              <path d="M230 64V110" marker-end="url(#r6a)"/>
              <path d="M230 176V212" marker-end="url(#r6a)"/>
              <path d="M230 278V314" marker-end="url(#r6a)"/>
              <path d="M110 144H138" marker-end="url(#r6a)" stroke="#f7c873"/>
              <path d="M320 246H348" marker-start="url(#r6a)" marker-end="url(#r6a)" stroke="#c4b5fd"/>
              <path d="M320 37H400V212" stroke="#ff8a80" stroke-dasharray="5 4" marker-end="url(#r6a)"/>
              <path d="M392 112l16 16M408 112l-16 16" stroke="#ff8a80" stroke-width="2.5"/>
            </g>
            <g fill="currentColor" text-anchor="middle">
              <text x="230" y="33" font-weight="600" font-size="13">Agent</text><text x="230" y="51" opacity=".8">proposes. Holds no secret</text>
              <text x="230" y="135" font-weight="600" font-size="13">Gateway</text><text x="230" y="153" opacity=".8">identity, shape, policy, rate</text><text x="230" y="168" opacity=".8">signs the decision</text>
              <text x="230" y="237" font-weight="600" font-size="13">Executor</text><text x="230" y="255" opacity=".8">ordinary code, own identity</text><text x="230" y="270" opacity=".8">checks the signature</text>
              <text x="230" y="339" font-weight="600" font-size="13">Identity API</text><text x="230" y="357" opacity=".8">create, disable, read</text><text x="230" y="372" opacity=".8">(SCIM-style model)</text>
              <text x="60" y="140" font-weight="600" font-size="13">Approver</text><text x="60" y="156" opacity=".8">a person</text>
              <text x="400" y="237" font-weight="600" font-size="13">Vault</text><text x="400" y="255" opacity=".8">lends a 5-minute</text><text x="400" y="270" opacity=".8">credential</text>
              <text x="230" y="436" opacity=".9">Audit log: who asked, what was decided, who approved. No secrets.</text>
            </g>
            <g fill="currentColor" opacity=".85">
              <text x="240" y="92">request, fixed shape</text>
              <text x="240" y="199">signed decision</text>
              <text x="240" y="301">call with the lease</text>
              <text x="332" y="82" text-anchor="start" fill="#ff8a80">no vault access</text>
              <text x="12" y="188" text-anchor="start" fill="#f7c873">risky actions wait</text>
            </g>
          </svg>
          <figcaption class="body-text" style="font-size:.9em;margin-top:.6rem">The agent only proposes. The checks sit outside it, and the only program that can read a credential is the executor.</figcaption>
        </figure>'''

block = f'''<!-- r6:start -->
      <section id="api-pattern">
        <h2>Zoom in: agents that send instructions to an API (round six)</h2>
        <p class="body-text">This zooms into steps 5 to 7 of the lifecycle above. An agent does not have to act on identities by itself. A safer pattern is that it only sends a request, and something else decides and acts. The request has a fixed shape, for example &ldquo;disable this account&rdquo;. A gateway outside the agent checks who the agent is, whether the action is on the list, whether a person must approve it and how many requests the agent has sent this hour. If everything passes, the gateway signs a decision. A separate program, the executor, checks the signature, borrows a short-lived credential from a vault, calls the identity API and gives the credential back.</p>
        <p class="body-text">The agent never holds the credential. That is the main design choice. Giving an agent &ldquo;read access to the vault&rdquo; so it can paste a password into an API call is the same mistake as giving an AI tool &ldquo;read access on your domain&rdquo;: it works, until something goes wrong.</p>
        {SVG}
        <p class="body-text">I wrote the expected result for 18 new cases (T1 to T18) and saved them before writing any code, on 25 Oct 2026 at 00:28 IST. They cover a joiner, a leaver with approval, a prompt-injected delete, approvals by the wrong people, a request with a made-up address in it, an agent reaching for the vault, the kill switch with a credential already lent out, a repeated request, personal data in the reason text, 25 requests in an hour, a forged decision, a lease used after it ended, a static password that is rotated on check-in, and two cases about the limits of the whole idea.</p>
        <p class="body-text">All 18 came out as I guessed. As a check on the tests themselves, I switched off {m["total"]} controls one at a time in a copy of the code. In {m["noticed"]} of {m["total"]} the matching case stopped passing, so those cases would notice if the control went missing.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-six-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>The vault and the identity API are small models I wrote for the lab. They are not HashiCorp Vault, Delinea Secret Server or any SCIM product, and a real tenant could behave differently.</li>
          <li>The AI model behind an agent is not tested. Each case assumes the agent was fooled or wrong and tests the wall around it.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every attack.</li>
          <li>T15 is a limit: a wrong but allowed request (the wrong person with the same name) passes every check. T18 is an anti-pattern shown by construction, not a finding.</li>
          <li>Not tested in this round: real SCIM calls, real approvals by people, and real mutual TLS between gateway and executor. Public-key signing, chains of agents handing work on, and a compromised gateway or executor are modelled in round eleven.</li>
        </ul>
        <h3>Questions I would ask a vendor who sells this</h3>
        <ul class="approach-list">
          <li>Does the agent ever hold the credential, even for a moment?</li>
          <li>Can it ask for anything that is not on a fixed list, and can it name the address the call goes to?</li>
          <li>Who approves a disable or a delete, and can that person be the one who set the agent up?</li>
          <li>When you switch the agent off, what happens to a credential it already triggered?</li>
          <li>Does the log keep names, free text or secrets?</li>
        </ul>
        <h3>Where the three new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">This is my own reading, not legal advice and not a certification. Check each reference against your own copy of the standard before you rely on it. Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#T1">case explorer</a> (track T). This round is not in the book or the round-five addendum.</p>
      </section>
<!-- r6:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r6:start -->.*?<!-- r6:end -->\n\n      ", "", h, flags=re.S)
h = h.replace('<section id="try">', block + '<section id="try">', 1)
h = h.replace("lists all 73 lab cases (59 from the first four rounds and 14 added in round five) and the 9 assistant cases",
              "lists all 91 lab cases (59 from the first four rounds, 14 added in round five and 18 in round six) and the 9 assistant cases")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count("api-pattern"), sha[:12])
