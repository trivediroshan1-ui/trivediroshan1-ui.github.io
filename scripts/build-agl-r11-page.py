#!/usr/bin/env python3
"""Puts the round-eleven section (an assistant that answers from documents, with the animated journey of one question) into
ai-governance-lab/index.html between markers, before the round-ten block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r11.js").read()
R11 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-11.json", "assets/ai-governance-lab-round-eleven-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-eleven-guesses.json", "rb").read()).hexdigest()
assert sha == R11["cases_sha256"], (sha, R11["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("bu", "The person asking"), ("iga", "Permissions and gateway"), ("dir", "Document store and index"),
         ("ai", "The assistant"), ("aud", "Logs and audit"), ("hr", "Privacy and data protection")]
STEPS = [
 ("bu", "A person starts a job for an agent", "The person, with the agent's token",
  "The job is tied to the person who started it. The token the agent holds says who that is, and it is recorded at every step that follows.",
  ["Person", "Token", "Origin recorded"],
  "Receives the job. It acts for this person and for nobody else.", ["D3", "D4"]),
 ("ai", "The agent hands part of the job to another agent", "The agent",
  "The next agent gets less, never more: a token cut down to what it is registered for and what the task needs. The chain has a depth limit, so it cannot grow without anyone noticing.",
  ["Narrower token", "Depth limit"],
  "Can ask another agent to help. Cannot give it more than it has.", ["D1", "D2"]),
 ("iga", "The hand-off cannot be replayed", "The identity layer",
  "A signed request or message carries a one-time number and a short window. A copy captured by a thief is refused the second time.",
  ["One-time number", "Time window"],
  "None. An AI model is not involved in this round.", ["D5", "D10"]),
 ("iga", "The gateway signs; the executor only checks", "The gateway and the executor",
  "The gateway signs with a private key. The executor holds only the public half, so a compromised executor cannot forge a decision. Each key has an identifier and a retirement time, so a rotated key stops working.",
  ["Private key", "Public key", "Key id and retirement"],
  "None.", ["D6", "D8"]),
 ("iga", "High-risk actions need a second signature", "An approver, with a separate key",
  "Deleting a user is not decided by one signing point. A second signature from an approver whose key the gateway does not hold is required.",
  ["Second signature"],
  "None.", ["D7"]),
 ("aud", "The log names the person and every hop", "The audit log",
  "One line shows the person who started the job and the agents it passed through, so the first question after an incident has an answer.",
  ["Person", "Chain of agents"],
  "None.", ["D3"]),
 ("hr", "The person leaves, and everything handed on stops", "HR and the identity provider",
  "Each handed-on token checks the one it came from, back to the start. Cutting the person cuts the whole chain.",
  ["Departure", "Cascade"],
  "None.", ["D4"]),
 ("dir", "Companies merge, and IDs get a prefix", "The directory",
  "Two staff both called S001 do not become one person. Every ID carries its company.",
  ["Company prefix"],
  "None.", ["D9"]),
 ("dir", "Documents are masked after normalising", "The document index",
  "A PAN written in lower case or with a space is masked like one written in capitals. Round nine tested Aadhaar only.",
  ["Normalised text", "Masked numbers"],
  "None.", ["D11"]),
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
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R11["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R11["controls"])
m, fr = R11["mutations"], R11["first_run"]

block = f'''<!-- r11:start -->
      <section id="delegation">
        <h2>Agents handing work to agents, keys and mergers (round eleven)</h2>
        <p class="body-text">Round eleven is the part of my open list that was about agents and keys: what happens when one agent hands work to another, what a compromised executor or gateway can sign, what a replayed request does, what happens to a rotated key, what two merged companies do to staff IDs, and whether the PAN masking I skipped in round nine holds. It uses real public-key signatures (Ed25519), written in plain Python so the lab still needs nothing but Python.</p>
        <p class="body-text">The animation below follows one job from the person who starts it, through a chain of agents, to the log, and shows where each case sits. It is a design, tested here on small models I wrote, and it says who does each step.</p>
        <div class="agl lc" aria-label="The journey of one job through a chain of agents">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">I wrote the expected result for 12 new cases (D1 to D12) and saved them before writing any code, on 25 Oct 2026 at 04:10 IST. The first run gave {fr["as_expected"]} of {fr["total"]} as I guessed. The one that differed, D11, was a fault in my own test: it looked for one number written three different ways, so a hit in one document counted for all three. I fixed the test, not the guess, and all 12 then came out as guessed. I also reworked D12 after the first run, because the real limit is data handed from one agent to another, not permissions. Both result files are kept. I then switched off {m["total"]} controls one at a time in a copy of the code, and the matching case noticed {m["noticed"]} of {m["total"]}. D12 has no such check, because it is a limit.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-eleven-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>Everything is a small model I wrote. There is no real identity provider, no real tenant and no AI model.</li>
          <li>The Ed25519 signing is my own plain-Python version of the standard algorithm. I checked it against the standard's test vector and against a well-known library on 20 random keys and messages. It is slow and not safe for real keys; it is only for these tests.</li>
          <li>D12 is a limit, not a fix: two agents that are each allowed can still move data together.</li>
          <li>D11 uses a small search index, not the full document assistant from round nine, and one made-up PAN pattern.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every case.</li>
          <li>This round ran in a Linux sandbox with Python 3.11 and on my MacBook Air (Python 3.9.6) with the same verdicts: 12 of 12 as guessed and 11 of 11 control-off checks noticed. Both sets of files are on the run page.</li>
          <li>The mapping below is my own reading, not legal advice and not a certification.</li>
        </ul>
        <h3>Where the seven new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#Q1">case explorer</a> (track Q). This round is in the addendum PDF (rounds five to ten), not in the book.</p>
      </section>
<!-- r11:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r11:start -->.*?<!-- r11:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r10:start -->" in h
h = h.replace("<!-- r10:start -->", block + "<!-- r10:start -->", 1)
h = h.replace("lists all 139 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight, 12 in round nine and 12 in round ten)",
              "lists all 151 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight, 12 in round nine, 12 in round ten and 12 in round eleven)")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count('id="delegation"'), sha[:12])
