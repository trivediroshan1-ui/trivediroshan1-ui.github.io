#!/usr/bin/env python3
"""Puts the round-ten section (an assistant that answers from documents, with the animated journey of one question) into
ai-governance-lab/index.html between markers, before the round-nine block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r10.js").read()
R10 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-10.json", "assets/ai-governance-lab-round-ten-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-ten-guesses.json", "rb").read()).hexdigest()
assert sha == R10["cases_sha256"], (sha, R10["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("bu", "The person asking"), ("iga", "Permissions and gateway"), ("dir", "Document store and index"),
         ("ai", "The assistant"), ("aud", "Logs and audit"), ("hr", "Privacy and data protection")]
STEPS = [
 ("hr", "A person joins, or comes back", "HR, with the platform team",
  "A joiner, a rehire or a contractor starts. A rehire gets a fresh account and the new job's baseline, not the old account back. A contractor from an agency must have an end date, so the account expires on its own.",
  ["Hire event", "Baseline access", "End date"],
  "None. This is plain process.", ["C7", "C9"]),
 ("hr", "Their details change", "HR sync to the directory",
  "A surname changes. The sync matches on the staff ID, which never changes, and sends only the fields that changed. It does not replace the whole record, so a disabled account stays disabled.",
  ["Staff ID", "Changed fields only"],
  "None.", ["C6", "C8"]),
 ("iga", "They sign in and get a token", "The identity provider",
  "The token is short-lived and tied to a key that the caller holds. A copied token alone is not enough. If the key is taken too, this does not help, and the lab says so.",
  ["Short token", "Key proof"],
  "None. An AI model is not involved in this round.", ["C1", "C2"]),
 ("dir", "An app checks the token on its own", "The application",
  "The app does not call the identity provider each time. It checks the signature, the expiry and a revoke list. It also checks its own clock against a trusted reference and refuses to decide if they differ too much.",
  ["Signature", "Expiry", "Clock check"],
  "None.", ["C12"]),
 ("iga", "The person leaves and a signal goes out", "The identity provider, signed",
  "HR ends the person's employment. The identity provider sends a signed revoke signal. The app ignores unsigned messages, and orders signals by the time on the event, so a late message cannot undo a newer one.",
  ["Signed signal", "Event time"],
  "None.", ["C3", "C4", "C5"]),
 ("bu", "An emergency happens", "The on-call engineer",
  "A break-glass account is used at 2 am. A person is alerted within a minute, and when the account is checked back in its password is changed.",
  ["Alert", "New password"],
  "None.", ["C10"]),
 ("aud", "The log records it, without personal data", "The audit log",
  "The tamper-evident log holds a pseudonym, and the real name sits in a separate store. An erasure request deletes the name there, and the chain of hashes still checks.",
  ["Pseudonym", "Hash chain"],
  "None.", ["C11"]),
]
legend = "".join(f'<li data-lane="{k}"><i></i>{e(n)}</li>' for k, n in LANES)
def step(s):
    lane, title, who, what, data, ai, cases = s
    links = "".join(f'<a href="/ai-governance-lab/cases/#{c}">{c}</a>' for c in cases)
    return (f'<li class="lc-step" data-lane="{lane}"><h4>{e(title)} <span class="lc-who">{e(who)}</span></h4><p>{e(what)}</p>'
            f'<ul class="lc-data" aria-label="Data">{"".join(f"<li>{e(d)}</li>" for d in data)}</ul>'
            f'<p class="lc-ai"><b>AI&rsquo;s part:</b> {e(ai)}</p>' + (f'<p class="lc-cases">Lab cases: {links}</p>' if links else "") + '</li>')
steps_html = "".join(step(s) for s in STEPS)
rows = "".join(
    f'<tr><td data-label="Case"><a href="/ai-governance-lab/cases/#{c["id"]}">{c["id"]}</a></td><td data-label="What I tested">{e(c["title"])}</td>'
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R10["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R10["controls"])
m = R10["mutations"]

block = f'''<!-- r10:start -->
      <section id="credentials">
        <h2>Credentials, sessions and identity edge cases (round ten)</h2>
        <p class="body-text">Rounds six to eight were about agents. Round ten goes back to the identity basics that were on my open list: what happens to a copied token, to a person who leaves while their session is still alive, to a disabled account when HR syncs, to a rehire, a surname change, an agency contractor, an emergency account, a request to erase a name from the log, and a clock that is wrong. These are the things an identity and access person gets asked about first.</p>
        <p class="body-text">The animation below follows one person through their time at the company and shows where each case sits. It is a design, tested here on small models I wrote, and it says who does each step.</p>
        <div class="agl lc" aria-label="The journey of one person through the company">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">I wrote the expected result for 12 new cases (C1 to C12) and saved them before writing any code, on 25 Oct 2026 at 03:53 IST. All 12 came out as I guessed the first time. That says my guesses were easy, not that real systems are safe. I then switched off {m["total"]} controls one at a time in a copy of the code, and the matching case noticed {m["noticed"]} of {m["total"]}. C2 has no such check, because it is a limit: nothing in the lab stops an attacker who has the token and the key.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-ten-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>Everything is a small model I wrote. There is no real identity provider, no real SCIM server, no real tenant and no AI model.</li>
          <li>The proof of a key uses a shared secret as a stand-in. Real systems use a public key, as in DPoP or mutual TLS. Whether a real implementation checks the proof correctly is not tested.</li>
          <li>C2 is a limit, not a fix. C11 does not test whether a pseudonym plus other fields could still identify a person.</li>
          <li>C6 assumes a server that sets &lsquo;active&rsquo; to true when a PUT leaves it out. Some servers do, some do not. Check yours.</li>
          <li>I wrote the guesses and the code, and none of the 12 differed on the first run, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every case.</li>
          <li>This round ran in a Linux sandbox with Python 3.11 and on my MacBook Air (Python 3.9.6) with the same verdicts: 12 of 12 as guessed and 12 of 12 control-off checks noticed. Both sets of files are on the run page.</li>
          <li>The mapping below is my own reading, not legal advice and not a certification.</li>
        </ul>
        <h3>Where the eight new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#Q1">case explorer</a> (track Q). This round is in the addendum PDF (rounds five to ten), not in the book.</p>
      </section>
<!-- r10:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r10:start -->.*?<!-- r10:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r9:start -->" in h
h = h.replace("<!-- r9:start -->", block + "<!-- r9:start -->", 1)
h = h.replace("lists all 127 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight and 12 in round nine)",
              "lists all 139 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight, 12 in round nine and 12 in round ten)")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count('id="credentials"'), sha[:12])
