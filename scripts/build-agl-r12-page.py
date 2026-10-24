#!/usr/bin/env python3
"""Puts the round-twelve section (an assistant that answers from documents, with the animated journey of one question) into
ai-governance-lab/index.html between markers, before the round-eleven block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r12.js").read()
R12 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-12.json", "assets/ai-governance-lab-round-twelve-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-twelve-guesses.json", "rb").read()).hexdigest()
assert sha == R12["cases_sha256"], (sha, R12["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("bu", "The requester"), ("iga", "Approval rules"), ("hr", "HR and departures"),
         ("aud", "Logs and audit"), ("ai", "Agents"), ("dir", "Directory")]
STEPS = [
 ("bu", "A person raises a request", "The requester",
  "A payment change is raised. The system records who raised it and a fingerprint of exactly what was asked.",
  ["Request", "Requester", "Fingerprint"],
  "None. An AI model is not involved in this round.", ["F1", "F2"]),
 ("iga", "Someone else approves it", "An approver",
  "The approver must be a different person. What they approve is the exact content they were shown, not just a request number.",
  ["Approver", "Approved fingerprint"],
  "None.", ["F1", "F2"]),
 ("iga", "A single denial stops it", "Any approver",
  "If one approver says no and another says yes, the request does not run. Disagreement means stop and talk.",
  ["Votes"],
  "None.", ["F6"]),
 ("iga", "Batches leave out the big ones", "An approver",
  "Twenty small requests can be approved in one click. A request over the high-risk limit cannot be in the batch and needs its own look.",
  ["Batch", "High-risk limit"],
  "None.", ["F3"]),
 ("iga", "The approval lapses", "The approval queue",
  "An approval is good for 24 hours. A request run on Thursday under a Monday approval is refused and asked for again.",
  ["Approved at", "24-hour lapse"],
  "None.", ["F4"]),
 ("hr", "The approver leaves, and the queue moves", "HR and the approval queue",
  "Requests waiting for a person who has left move to their manager, so nothing waits for someone who no longer exists.",
  ["Departure", "Reassignment"],
  "None.", ["F5"]),
 ("aud", "What nobody can see", "Nobody, today",
  "Two people can approve each other's requests and meet every rule above. The lab cannot see that arrangement. A person who looks at patterns can.",
  ["Approver pairs"],
  "None.", ["F7"]),
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
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R12["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R12["controls"])
m, fr = R12["mutations"], R12["first_run"]

block = f'''<!-- r12:start -->
      <section id="approvals">
        <h2>Who approved, what exactly, and when (round twelve)</h2>
        <p class="body-text">Round twelve is about approvals, the human step that every earlier round assumed. Who approved? Was it the person who asked? Did they approve what finally ran, or something changed afterwards? Was it still true when it ran? What if the approver left, or two approvers disagreed? It uses a small approval queue I wrote for the lab. It is not a real approval product, and no AI model is involved.</p>
        <p class="body-text">The animation below follows one request from the person who raises it to the approval, and shows where each case sits.</p>
        <div class="agl lc" aria-label="The journey of one approval request">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">I wrote the expected result for 7 new cases (F1 to F7) and saved them before writing any code, on 25 Oct 2026 at 04:58 IST. The first run gave {fr["as_expected"]} of {fr["total"]} as I guessed. That is a warning about my guesses, not good news about the controls: they were easy. Switching off one control at a time, in a copy of the code, was noticed by the matching case {m["noticed"]} of {m["total"]} times. F7 is a limit, so it has no control to switch off. The files are on the <a href="/ai-governance-lab/run/#real-output">run page</a>.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-twelve-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>The approval queue is a small model I wrote. There is no real approval product, no real people and no AI model.</li>
          <li>F7 is a limit, not a fix: two people who approve each other's requests meet every rule, and the lab cannot see the pattern.</li>
          <li>F5 is a thin check: it only shows that waiting requests move to the manager when the approver leaves.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every case.</li>
          <li>This round ran in a Linux sandbox with Python 3.11 and on my MacBook Air (Python 3.9.6) with the same verdicts: 7 of 7 as guessed and 6 of 6 control-off checks noticed. Both sets of files are on the run page.</li>
          <li>The mapping below is my own reading, not legal advice and not a certification.</li>
        </ul>
        <h3>Where the five new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#F1">case explorer</a> (track F). This round is in the addendum PDF (rounds five to twelve), not in the book.</p>
      </section>
<!-- r12:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r12:start -->.*?<!-- r12:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r11:start -->" in h
h = h.replace("<!-- r11:start -->", block + "<!-- r11:start -->", 1)
h = h.replace("lists all 151 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight, 12 in round nine, 12 in round ten and 12 in round eleven)",
              "lists all 158 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight, 12 in round nine, 12 in round ten, 12 in round eleven and 7 in round twelve)")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count('id="approvals"'), sha[:12])
