#!/usr/bin/env python3
"""Puts the round-thirteen section (an assistant that answers from documents, with the animated journey of one question) into
ai-governance-lab/index.html between markers, before the round-twelve block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r13.js").read()
R13 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-13.json", "assets/ai-governance-lab-round-thirteen-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-thirteen-guesses.json", "rb").read()).hexdigest()
assert sha == R13["cases_sha256"], (sha, R13["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("bu", "The person asking"), ("ai", "The assistant"), ("dir", "Directory and permissions"),
         ("aud", "Sources and logs"), ("iga", "Masking")]
STEPS = [
 ("bu", "A person asks a question", "The person asking",
  "A support agent or a former HR person asks about pay, in their own words. The words need not match any document.",
  ["Question", "Person", "Team"],
  "None yet.", ["S1", "S5"]),
 ("ai", "The question and the documents become numbers", "The embedding model",
  "A small model turns the question and each document into numbers, so that similar meanings sit close together. It finds the HR salary document even when no word matches.",
  ["Embedding", "Closest matches"],
  "The embedding model only measures closeness. It does not know who may read what.", ["S1"]),
 ("dir", "Permissions are checked before the ranking", "The live directory",
  "The person's team is read from the live directory, and restricted documents are removed before the best matches are chosen. Done after, a restricted match can crowd out everything the person may read.",
  ["Live team", "Document team"],
  "None.", ["S1", "S3", "S5"]),
 ("aud", "Sources show only what the person may see", "The answer and its source list",
  "A title is not shown if the text is not. The source list follows the same permissions as the answer.",
  ["Sources shown"],
  "None.", ["S2"]),
 ("iga", "Personal numbers were masked when the text went in", "Indexing",
  "An Aadhaar-format number was replaced with a mask when the note was indexed, so it stays hidden however the note is found.",
  ["Masked text"],
  "None.", ["S4"]),
 ("aud", "What nobody checks", "Nobody, today",
  "Two documents that anyone may read can add up to a fact that is restricted. Permissions are checked one document at a time, so the lab cannot see it.",
  ["Joined facts"],
  "None.", ["S6"]),
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
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R13["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R13["controls"])
m, T_, F, B = R13["mutations"], R13["toy"], R13["failed_first"], R13["bad_mutations"]

block = f'''<!-- r13:start -->
      <section id="meaning">
        <h2>Finding documents by meaning (round thirteen)</h2>
        <p class="body-text">Round nine's assistant found documents by matching words. Real assistants usually find them by meaning, using an embedding model. The question for round thirteen: do the permission controls from round nine still hold when a document can be found without sharing a single word with the question? The answer model is still a stand-in that repeats what it is given, so no AI model that writes answers is tested. This round tests the wall around the search.</p>
        <p class="body-text">The animation below follows one question from the person asking to the answer, and shows where each case sits.</p>
        <div class="agl lc" aria-label="The journey of one question when documents are found by meaning">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">I wrote the expected result for 6 new cases (S1 to S6) and saved them before writing any code, on 25 Oct 2026 at 05:14 IST. I ran them with a real embedding model on my MacBook Air: <b>{e(R13["embedder"])}</b>, about 90 MB, run locally. The cases came out {R13["counts"]["as expected"]} of 6 as I guessed. Switching off one control at a time, in a copy of the code, was noticed by the matching case {m["noticed"]} of {m["total"]} times. S6 is a limit, so it has no control to switch off. In the sandbox, which cannot download a real model, a toy stand-in gave the same verdicts ({T_["as_expected"]} of 6 and {T_["noticed"]} of {T_["total"]}); the toy is not a real model and proves only that the code works.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-thirteen-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>My mistakes in this round</h3>
        <ul class="approach-list">
          <li>My first pay question contained the word &ldquo;and&rdquo;, which sits inside &ldquo;band&rdquo;, so keyword search would have found the HR document too. That would have spoiled the point of S1. I changed the question before any recorded run.</li>
          <li>My first run on the Mac had all six cases &ldquo;not run&rdquo;. The install put NumPy 2 next to a torch built for NumPy 1, and every case failed with &ldquo;Numpy is not available&rdquo;. It also took {F["seconds"]:.0f} seconds because my code reloaded the model for every case. I fixed that, pinned NumPy below 2, and the next run took {F["good_seconds"]:.0f} seconds.</li>
          <li>The control-off check from that broken run said &ldquo;{B["claimed"]} of {B["total"]} noticed&rdquo;, but every case had failed with and without the control, and my checker counted an error as noticing. That number was meaningless. I fixed the checker so an error never counts and an invalid run is announced, and ran it again. The wrong file is kept next to the right one, on the <a href="/ai-governance-lab/mac/">Mac page</a>.</li>
        </ul>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>One small embedding model, one question per case, and the best one to four matches. Another model or a different cut-off could rank differently, and S1 and S3 depend on the ranking.</li>
          <li>S6 is a limit, not a fix: two documents anyone may read can add up to a secret, and the lab cannot see it.</li>
          <li>With the real model, the top four for S6 included the document that carries a hidden instruction. This round did not test what happens next; round nine did, with keywords.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the controls do what I intended, not that I thought of every case. All six matched, which suggests my guesses were easy.</li>
          <li>The mapping below is my own reading, not legal advice and not a certification.</li>
        </ul>
        <h3>Where the four new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#S1">case explorer</a> (track S). The files are on the <a href="/ai-governance-lab/run/#real-output">run page</a>. This round is in the addendum PDF (rounds five to thirteen), not in the book.</p>
      </section>
<!-- r13:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r13:start -->.*?<!-- r13:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r12:start -->" in h
h = h.replace("<!-- r12:start -->", block + "<!-- r12:start -->", 1)
h = h.replace("12 in round eleven and 7 in round twelve)", "12 in round eleven, 7 in round twelve and 6 in round thirteen)").replace("lists all 158 lab cases", "lists all 164 lab cases")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count('id="meaning"'), sha[:12])
