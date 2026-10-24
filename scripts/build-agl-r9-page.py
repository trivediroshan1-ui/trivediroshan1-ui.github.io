#!/usr/bin/env python3
"""Puts the round-nine section (an assistant that answers from documents, with the animated journey of one question) into
ai-governance-lab/index.html between markers, before the round-eight block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r9.js").read()
R9 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-9.json", "assets/ai-governance-lab-round-nine-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-nine-guesses.json", "rb").read()).hexdigest()
assert sha == R9["cases_sha256"], (sha, R9["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("bu", "The person asking"), ("iga", "Permissions and gateway"), ("dir", "Document store and index"),
         ("ai", "The assistant"), ("aud", "Logs and audit"), ("hr", "Privacy and data protection")]
STEPS = [
 ("bu", "A person asks a question", "A support agent, with their own identity",
  "The question reaches the assistant with the person's identity attached. The assistant is not asked to guess who is asking.",
  ["Question", "Person's identity"],
  "Receives the question. It acts for this person and for nobody else.", ["Q12"]),
 ("iga", "Permissions come from the live directory", "The directory, asked at the moment of the question",
  "The permission check asks the directory what this person may read right now. It does not use a copy made when the documents were indexed, and it does not rely on a sentence in the prompt.",
  ["Live permissions"],
  "None. A model cannot be trusted to keep a secret it can see.", ["Q1", "Q2", "Q3", "Q4"]),
 ("dir", "Only allowed chunks are retrieved", "The document index",
  "The search runs only over what the person may read. Personal numbers were masked when the documents were indexed, and a document deleted at the source has also been deleted from the index.",
  ["Allowed chunks", "Masked numbers", "Deleted documents gone"],
  "None. Retrieval is plain search.", ["Q3", "Q8", "Q9"]),
 ("ai", "The assistant writes the answer", "The AI model",
  "The model gets the question and the allowed chunks. Whatever it sees, it can repeat. So the whole design is about what it is allowed to see.",
  ["Question", "Allowed chunks"],
  "Writes the answer. It may be fooled by a hidden instruction in a document, so it cannot act on its own.", ["Q5", "Q10"]),
 ("iga", "Sources and cache follow the person", "The answer service",
  "Source titles are filtered like the text. A cached answer is kept per person and is never served to someone else.",
  ["Filtered sources", "Per-person cache"],
  "None.", ["Q6", "Q7"]),
 ("iga", "An instruction in a document goes to the gateway", "The gateway",
  "If a document tells the assistant to do something, such as send a file, that is only a request. The gateway checks it against the actions offered to agents and refuses what is not on the list.",
  ["Request", "Refusal"],
  "Can ask. Cannot do.", ["Q5"]),
 ("aud", "The log keeps ids and hashes, not text", "The retrieval trace",
  "The trace records which documents were used and a short hash of each, so you can answer 'what did it read?' without keeping a second copy of the data.",
  ["Document ids", "Hashes"],
  "None.", ["Q11"]),
 ("hr", "Deleting means deleting everywhere", "Privacy lead, with the platform team",
  "An erasure request reaches the source, the index and any cache. Until then, the text can still come out. The lab shows the gap; closing it is a process, not only code.",
  ["Erasure request", "Index rebuild"],
  "None.", ["Q9"]),
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
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R9["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R9["controls"])
m, fr = R9["mutations"], R9["first_run"]

block = f'''<!-- r9:start -->
      <section id="rag">
        <h2>An assistant that answers from documents (round nine)</h2>
        <p class="body-text">Most company assistants today do one thing: you ask, they search your documents, and a model writes the answer from what it found. That is called retrieval-augmented generation, or RAG. The question for governance is simple: where is the permission checked, and what still leaks? In round nine I built a small version and tried twelve ways it can go wrong.</p>
        <p class="body-text">The animation below follows one question from the person who asks it to the answer and the log. It is a design, tested here on a small model, and it says who does each step.</p>
        <div class="agl lc" aria-label="The journey of one question">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">I wrote the expected result for 12 new cases (Q1 to Q12) and saved them before writing any code, on 25 Oct 2026 at 02:26 IST. The first run gave {fr["as_expected"]} of {fr["total"]} as I guessed. The one that differed, Q8, was a fault in my own code: my masking of Aadhaar numbers only caught numbers written with spaces. I fixed the code, not the guess, ran it again and now all 12 come out as I guessed. Both result files are kept. I then switched off {m["total"]} controls one at a time in a copy of the code, and the matching case noticed {m["noticed"]} of {m["total"]}. Some of those checks are weaker than others: for Q1 and Q2 they only show the case reacts when the leaking mode is changed, and for Q5 the gateway crashes instead of accepting the request.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-nine-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>The search is plain keyword matching, not a vector database. Real embeddings, chunking and rerankers can leak in ways this does not test.</li>
          <li>The &ldquo;model&rdquo; is a stand-in that repeats whatever it is given. The AI model itself is not tested; each case assumes it was fooled or careless and tests the wall around it.</li>
          <li>Q10 is a limit, not a fix: two documents a person may read can combine into something they may not know, and no permission check stops that.</li>
          <li>Q5 relies on the gateway from the earlier rounds. There is no real mail system.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every case.</li>
          <li>This round first ran in a Linux sandbox with Python 3.11. I then ran it on my MacBook Air (Python 3.9.6) with the same verdicts: 12 of 12 as guessed and 12 of 12 control-off checks noticed. Both sets of files are on the run page.</li>
          <li>The mapping below is my own reading, not legal advice and not a certification.</li>
        </ul>
        <h3>Where the six new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#Q1">case explorer</a> (track Q). This round is in the addendum PDF (rounds five to ten), not in the book.</p>
      </section>
<!-- r9:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r9:start -->.*?<!-- r9:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r8:start -->" in h
h = h.replace("<!-- r8:start -->", block + "<!-- r8:start -->", 1)
h = h.replace("lists all 115 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven and 12 in round eight)",
              "lists all 127 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six, 12 in round seven, 12 in round eight and 12 in round nine)")
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count('id="rag"'), sha[:12])
