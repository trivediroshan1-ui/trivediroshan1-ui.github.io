#!/usr/bin/env python3
"""Puts the round-eight section (when an agent goes around the gateway, with the animated first-hour response) into ai-governance-lab/index.html
between markers, before the round-seven block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r8.js").read()
R8 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-8.json", "assets/ai-governance-lab-round-eight-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-eight-guesses.json", "rb").read()).hexdigest()
assert sha == R8["cases_sha256"], (sha, R8["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("dir", "Identity API and directory"), ("iga", "Gateway, executor, policy"), ("aud", "Security operations and audit"),
         ("bu", "Sponsor and business unit"), ("hr", "HR and legal"), ("ai", "AI agent")]
STEPS = [
 ("dir", "A change with no decision behind it", "Identity API and its own change log",
  "The identity system records a change. Nothing the gateway signed matches it. Perhaps the agent found a leaked token, or a second tool had its own.",
  ["API change log", "Caller", "Credential id"],
  "It went round the gateway. Whether it was fooled or simply wrong does not matter here.", ["B1", "B2"]),
 ("aud", "The comparison flags it", "A scheduled job, run by security operations",
  "The job lines up the identity system's change log against the gateway's signed decisions. Every change should match one. The odd one out is a bypass alert, and approved changes made the same day are not flagged.",
  ["Change log", "Signed decisions", "Alert"],
  "None. This job is plain code, so the agent cannot talk it out of anything.", ["B2"]),
 ("iga", "The policy switches the agent off", "The kill-switch policy, run by the gateway and vault",
  "If the change can be traced to one agent, its token stops working, its waiting approvals are cancelled, its lent credentials are revoked and the leaked token is revoked. If it cannot be traced, a person is alerted. The change itself is left alone.",
  ["Agent token", "Waiting approvals", "Vault leases", "Leaked token"],
  "Switched off. It can be brought back only by a named approver after review.", ["B3", "B8"]),
 ("aud", "Evidence first", "Security operations",
  "Before anyone cleans up, copy the logs, hash the copy and record who copied it and when. The chain of log lines shows any edit, and a saved anchor shows any cut.",
  ["Directory log", "Gateway log", "Vault log", "Hash", "Custody record"],
  "May help to collect. Never holds the only copy.", ["B10", "B12"]),
 ("bu", "A person decides what to undo", "Agent sponsor and the head of IAM",
  "The sponsor and the head of IAM look at the evidence and decide whether to reverse the change. A named approver does it through the normal request path.",
  ["Decision", "Named approver"],
  "Cannot approve its own roll-back.", ["B3"]),
 ("iga", "Close the hole", "IAM engineering",
  "Rotate whatever was reached and find where it was lying. Make credentials work only from the caller they were lent to. Remove the network route. Add the case to the tests that run before every change.",
  ["Rotated credential", "Caller binding", "No network route", "New test"],
  "None.", ["B1", "B4", "B5"]),
 ("hr", "If a person was involved", "HR and legal, with a named case owner",
  "If the signal points to a person (for example heavy exports after a resignation notice), a case with a copy of the evidence goes to a named owner. HR and legal decide next steps, including whether to report to anyone. Accommodations and medical detail never go in the case.",
  ["Signal", "Case owner", "Evidence copy"],
  "Raises a signal. Does not accuse, and cannot contact the police.", ["B10", "B9", "B11"]),
 ("aud", "Learn and practise", "Auditor and the response team",
  "Report the incident and the time it took. Add a drill every quarter. Watch the lists for the account states that matter: a leaver's account touched after it was disabled, a mover who keeps old access.",
  ["Time to switch off", "Drill result", "Watch alerts"],
  "None.", ["B6", "B7"]),
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
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R8["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R8["controls"])
m = R8["mutations"]

block = f'''<!-- r8:start -->
      <section id="bypass">
        <h2>When an agent goes around the gateway (round eight)</h2>
        <p class="body-text">The pattern above works only if the agent cannot get round it. So I asked the awkward question: what if it does? An agent might find a token in a config file, or hold a second tool with its own credential. This round tests three layers. First, make it hard: a credential works only from the caller it was lent to, and the agent&rsquo;s runtime has no route to the identity system. Second, notice: every change in the identity system&rsquo;s own log must match a decision the gateway signed, and a change with no decision is a bypass. Third, answer: switch the agent off, revoke what it could use, keep the evidence, and let a person decide what to undo.</p>
        <p class="body-text">The animation below is the first hour after a bypass alert. It is a design, tested here on small models, and it names who does each step.</p>
        <div class="agl lc" aria-label="The first hour after a bypass alert">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">I wrote the expected result for 12 new cases (B1 to B12) and saved them before writing any code, on 25 Oct 2026 at 01:07 IST. They cover a direct call with a leaked token, the same call when the API wrongly accepts it, the response policy, a missing network route, a lease used by the wrong caller or too late, a leaver&rsquo;s account that is touched or switched back on, a mover who asks for new access too soon, a sponsor who leaves, a helper for a person who needs assistive technology, a possible offence by a person, requests for sensitive data, and a tampered audit log. All 12 came out as I guessed. I then switched off {m["total"]} controls one at a time in a copy of the code, and the matching case noticed all {m["noticed"]}.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-eight-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>The identity API, vault, network and log are small models I wrote. Real products, mutual TLS or token binding, and real networks will behave differently.</li>
          <li>The agent does not really try to get round the wall. Each case makes it do the wrong thing and checks what stands in the way.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every way round.</li>
          <li>Changes made by other approved paths, such as the HR sync job, are not part of the comparison. If a bypass makes exactly the same change as a real request at the same moment, only the extra one is flagged.</li>
          <li>The offence case only shows a signal reaching a person with evidence. What counts as an offence, what may be monitored and what a court accepts are for legal advice, not this lab.</li>
          <li>The mapping below is my own reading, not legal advice and not a certification.</li>
        </ul>
        <h3>Where the six new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#B1">case explorer</a> (track B). This round is not in the book or the round-five addendum.</p>
      </section>
<!-- r8:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r8:start -->.*?<!-- r8:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r7:start -->" in h
h = h.replace("<!-- r7:start -->", block + "<!-- r7:start -->", 1)
h = h.replace("lists all 103 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six and 12 in round seven)",
              "lists all 115 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven and 12 in round eight)")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count('id="bypass"'), sha[:12])
