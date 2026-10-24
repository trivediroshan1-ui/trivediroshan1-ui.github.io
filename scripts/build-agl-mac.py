#!/usr/bin/env python3
"""Builds /ai-governance-lab/mac/index.html: every command run on the Mac, what it printed, and the Mac data files with SHA-256.
Sources: the three terminal transcripts in assets/agl-mac/, and the lab repo (branches origin/mac-run, mac-run-ten, mac-run-eleven; origin/main for 24 Oct).
Re-run: python3 scripts/build-agl-mac.py [lab_repo]"""
import hashlib, html, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/ai-governance-lab"
OUT = os.path.join(ROOT, "ai-governance-lab/mac/index.html")
E = html.escape

def git(*a):
    return subprocess.run(["git", "-C", LAB, *a], capture_output=True, text=True).stdout

def blob(ref, path):
    return subprocess.run(["git", "-C", LAB, "show", f"{ref}:{path}"], capture_output=True).stdout

# ---- Mac data files ----------------------------------------------------------------------------------------------------
def headline(path, data):
    t = data.decode("utf-8", "replace")
    if path.endswith(".json"):
        return ""
    if "-mutations" in path:
        rows = [l for l in t.splitlines() if l.startswith("| ") and not l.startswith("| Case") and not l.startswith("|---")]
        yes = sum(1 for l in rows if l.rstrip().endswith("| yes |"))
        return f"{yes} of {len(rows)} controls noticed"
    m = re.search(r"Verdicts: (.*)", t)
    if m:
        return m.group(1).strip()
    if "held-out" in path:
        return "v1 3, v2 2, v3 2, out of 8"
    if "compare-" in path:
        return " / ".join(re.findall(r"- ([\w-]+: \d+ of \d+)", t))
    if "track-p" in path:
        return "P1 to P9: 9 pass"
    return ""

FILES = []   # (group, commit, ref, path)
def add(group, ref, commit_label):
    for p in sorted(git("ls-tree", "-r", "--name-only", ref, "results/").split()):
        FILES.append((group, commit_label, ref, p))

SETS = [
    ("24 Oct, session 1 (Track P and held-out)", "17c2a87", ["results/track-p/20261024-091345-claude-sonnet-5-5--low-effort---paid-plan.md", "results/track-p/20261024-091345-claude-sonnet-5-5--low-effort---paid-plan.json"]),
    ("24 Oct, session 1 (Track P and held-out)", "7042781", ["results/held-out/held-out-20261024-095218.md"]),
    ("24 Oct, session 2 (Presidio)", "9441a2b", ["results/round-2/compare-20261024-102850.md"]),
    ("24 Oct, session 2 (Presidio)", "30e3120", ["results/round-2/compare-20261024-103001.md"]),
]
rows = []
for group, ref, paths in SETS:
    for p in paths:
        d = blob(ref, p)
        if d:
            rows.append((group, ref[:7], "main", p, d))
BR = [("25 Oct, session 3: rounds five to nine", "origin/mac-run", "mac-run", None),
      ("25 Oct, session 3: round ten", "origin/mac-run-ten", "mac-run-ten", "/20261024-2228"),
      ("25 Oct, session 3: round eleven", "origin/mac-run-eleven", "mac-run-eleven", "/20261024-2248")]
for group, ref, name, flt in BR:
    commit = git("rev-parse", "--short=7", ref).strip()
    ps = [p for p in git("ls-tree", "-r", "--name-only", ref, "results/").split() if (flt is None or flt in p)]
    if flt is None:   # mac-run holds only the Mac files for rounds 5-9, take the ones added by its own commit
        ps = [p for p in git("show", "--name-only", "--format=", ref).split() if p.startswith("results/")]
    elif name == "mac-run-eleven":
        ps = [p for p in git("show", "--name-only", "--format=", ref).split() if p.startswith("results/")]
    for p in sorted(ps):
        d = blob(ref, p)
        rows.append((group, commit, name, p, d))

def short(p): return p.replace("results/", "")
data_rows, glance = [], {}
for group, commit, branch, p, d in rows:
    sha = hashlib.sha256(d).hexdigest()
    h = headline(p, d)
    data_rows.append((group, commit, branch, short(p), len(d), sha, h))
    m = re.match(r"results/round-(\d+)/", p)
    if m and p.endswith(".md") and branch.startswith("mac-run"):
        r = int(m.group(1))
        glance.setdefault(r, {})["mut" if "mutations" in p else "v3"] = h
        glance[r]["when"] = re.search(r"/(\d{8}-\d{6})", p).group(1)

def table(head, body, cls="mac-t"):
    th = "".join(f"<th>{E(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body)
    return f'<div class="mac-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def code(s): return f"<code>{E(s)}</code>"

# ---- commands per session ------------------------------------------------------------------------------------------------
S1 = [
 ("`cd`, then `ai-governance-lab`", "<code>command not found</code>. I typed the folder name as a command by mistake."),
 ("`cd ai-governance-lab`", "<code>No such file or directory</code>. The lab was not in my home folder."),
 ('`find ~ -name run_p.py -not -path "*/Library/*" 2>/dev/null`', "Found an older copy at <code>/Users/roshan/ai-governance-lab-work/ai-governance-lab/run_p.py</code>."),
 ("`git clone https://github.com/trivediroshan1-ui/ai-governance-lab.git`", "Cloned: 144 objects. Then `cd ai-governance-lab`."),
 ("`python3 run_p.py --show P1`", "Printed case P1 (paste a made-up customer list and ask for analysis), with five made-up customer rows and the pass, partial and fail rules."),
 ("`cat docs/kaveri-ai-policy.md`", "Printed the eight-rule made-up policy for Kaveri Finance."),
 ("`loans_db.py`", "<code>command not found</code>. A stray paste."),
 ('`python3 run_p.py --record "Claude Sonnet 5.5 (Low effort), paid plan"`', "First attempt: answered P1 with <code>p</code>, left the note as the placeholder text, then pressed Ctrl-C at P2. A <code>KeyboardInterrupt</code> traceback printed. Nothing was saved."),
 ("the same `run_p.py --record` command again", "Recorded P1 to P9, all <code>p</code> (pass), with a note for each. A paste glitch merged the P6 note and the P7 prompt into one line and printed two <code>result</code> lines for P7. Saved to <code>results/track-p/20261024-091345-claude-sonnet-5-5--low-effort---paid-plan.md</code>."),
 ("`python3 -c '…'` (one line)", "Cleaned the saved file: set <code>policy_given</code> to “First message in a fresh claude.ai chat, paid plan, Sonnet 5.5 at Low effort, 24 Oct 2026” and replaced the P6 note. Rewrote the <code>.md</code> from the <code>.json</code>."),
 ("`cat results/track-p/*claude-sonnet*.md`", "Printed the table: nine rows, P1 to P9, all pass."),
 ('`git add results`, `git commit -m "Track P: Claude Sonnet 5.5 results"`, `git push`', "Commit <code>17c2a87</code>, pushed <code>c31f364..17c2a87</code>. Git warned that the committer name and email were set automatically."),
 ("`cd ai-governance-lab`", "<code>No such file or directory</code> (already inside it)."),
 ("`open -e cases/held-out.json`", "Opened the held-out cases file in TextEdit to add my own cases."),
 ('`git add cases/held-out.json && git commit -m "Held-out cases" && git push`', "<code>Author identity unknown</code>. Nothing committed."),
 ("`python3 heldout.py v1 v2 v3`", "<code>JSONDecodeError: Expecting ',' delimiter: line 75 column 5</code>. The file was no longer valid JSON."),
 ('`git config user.name "Roshan Trivedi"` and `git config user.email "…@users.noreply.github.com"`', "Set my name and a GitHub no-reply address for this repository only."),
 ("`python3 -m json.tool cases/held-out.json > /dev/null`", "Same error, line 75."),
 ('`git add`, `git commit -m "Held-out cases"`, `git push`', "Commit <code>b078a90</code> pushed, with the broken JSON in it."),
 ("`python3 heldout.py v1 v2 v3` (second time) and `cat -n cases/held-out.json | sed -n '60,80p'`", "Same error. The listing showed leftover lines from an older case (<code>D013</code>) after the closing braces."),
 ('`git add`, `git commit -m "Fix held-out JSON"`, `git push`', "<code>nothing to commit, working tree clean</code>. Nothing was fixed yet."),
 ("`sed -i '' '75,$d' cases/held-out.json`, then `python3 -m json.tool … && echo VALID`", "Deleted from line 75 to the end. Still invalid: <code>Expecting ',' delimiter: line 75 column 1</code>. I committed and pushed it anyway: <code>439ef31</code>."),
 ("`python3 heldout.py v1 v2 v3` (third time)", "Same error."),
 ("`cat > cases/held-out.json << 'EOF' … EOF`", "Rewrote the file whole with eight starter cases, H001 to H008."),
 ("`python3 -m json.tool … && echo VALID`", "<code>VALID</code>. Committed (<code>1f1af47</code>, “Held-out cases: eight starter items”) and pushed."),
 ("`python3 heldout.py v1 v2 v3`", "Printed the table. Right answers out of 8: <strong>v1 3, v2 2, v3 2</strong>. Saved to <code>results/held-out/held-out-20261024-095218.md</code>. Committed (<code>7042781</code>) and pushed."),
 ("`python3 run_p.py --show P7`", "Printed case P7 with the 30 chat turns to send before repeating P1."),
 ("`pip3 install presidio-analyzer`", "Failed. It tried to build <code>spacy 3.8.x</code> from source and stopped with <code>No matching distribution found for thinc&lt;8.4.0,&gt;=8.3.12</code> on Python 3.9. The fix is in session 2."),
]
S2 = [
 ("`cd ~/ai-governance-lab`", "Worked."),
 ("`python3 -m venv .venv-presidio`; `echo \".venv-presidio\" >> .git/info/exclude`; `source .venv-presidio/bin/activate`", "Made a clean virtual environment, kept it out of git, switched into it."),
 ("`pip install --upgrade pip`", "pip 21.2.4 to 26.0.1."),
 ('`pip install "numpy<2" "spacy<3.8" presidio-analyzer`', "Installed (spacy 3.7.5, numpy 1.26.4, thinc 8.2.5). Pinning older versions got around the build error from session 1."),
 ("`python -m spacy download en_core_web_lg`", "Started a 587.7 MB download, ETA about two and a half hours. I cancelled it: <code>ERROR: Operation cancelled by user</code>."),
 ("`python -m spacy download en_core_web_sm`", "Installed the small model (12.8 MB), version 3.7.1. This is why the comparison says “small model”."),
 ("`python - <<'E' … E` (patch <code>adapters/presidio_cmd.py</code>)", "Printed <code>patched</code>. Made the adapter use <code>en_core_web_sm</code>."),
 ('`python compare.py v3 "external:python3 adapters/presidio_cmd.py"`', "Presidio’s built-in entities in use: PHONE_NUMBER, EMAIL_ADDRESS, CREDIT_CARD. <strong>v3 handled 45 of 53, Presidio 15 of 33</strong>. Saved to <code>results/round-2/compare-20261024-102850.md</code>."),
 ('`git add results adapters`, `git commit -m "Presidio comparison, small model"`, `git push`', "Commit <code>9441a2b</code>, pushed <code>7042781..9441a2b</code>. Then <code>deactivate</code>."),
 ("`source .venv-presidio/bin/activate`; `cp adapters/presidio_cmd.py adapters/presidio_india_cmd.py`; `python - <<'E' … E`", "Copied the adapter and added Presidio’s India recognisers (<code>InPanRecognizer</code>, <code>InAadhaarRecognizer</code>). Printed <code>patched</code>."),
 ('`python compare.py v1 v3 "external:python3 adapters/presidio_cmd.py" "external:python3 adapters/presidio_india_cmd.py"`', "Entities in use for the second adapter: the three above plus IN_PAN and IN_AADHAAR. <strong>v1 20 of 53, v3 45 of 53, Presidio 15 of 33, Presidio with India recognisers 16 of 33.</strong> Saved to <code>results/round-2/compare-20261024-103001.md</code>."),
 ('`git add results adapters`, `git commit -m "Presidio comparison with India recognisers on"`, `git push`', "Commit <code>30e3120</code>, pushed <code>9441a2b..30e3120</code>. Then <code>deactivate</code>."),
 ('`python3 run_p.py --record "… clean re-run of P5 and P7"`', "I wanted to re-record only P5 and P7. The tool asks for every case, so I typed placeholder notes (“hello”, “run it”, “s”) and skipped most. It saved a record with those placeholders: <code>20261024-104042-…</code>."),
 ('`git add results/track-p`, `git commit -m "Track P: clean re-run of P5 and P7"`, `git push`', "Commit <code>661e52a</code>, pushed. This published a record with placeholder notes by mistake."),
 ("`git rm results/track-p/20261024-104042-*`, commit “Remove incomplete Track P re-run record (placeholder notes)”, `git push`", "Commit <code>efe55b9</code> removed it. The earlier commit stays in the repository history."),
 ('`grep -n "Kaveri@2026" loans_db.py`', "<code>No such file or directory</code>. A check for a made-up hard-coded password in a file that is not in this repository."),
]
S3 = [
 ("(start) `date …`, `cd ~/path/to/ai-governance-lab`, `git status`", "A restored terminal window replayed an old line: <code>date: illegal time format</code>. Then I typed a placeholder path from my own notes: <code>No such file or directory</code>; <code>fatal: not a git repository</code>."),
 ('`find ~ -maxdepth 4 -type d -name "ai-governance-lab*" 2>/dev/null`', "Found two copies: <code>/Users/roshan/ai-governance-lab</code> and <code>/Users/roshan/ai-governance-lab-work/ai-governance-lab</code>."),
 ('`cd "/Users/roshan/Documents/ai-governance-lab"` (three times)', "<code>No such file or directory</code> each time. A wrong guess at the location."),
 ('`find ~ -maxdepth 5 -name "run.py"`; a loop that listed each copy and its latest commit', "The folder in my home folder was at <code>efe55b9</code> (24 Oct). The older copy under <code>-work</code> was at <code>c31f364</code>. I used the first."),
 ("`cd /Users/roshan/ai-governance-lab`; `git status`; `python3 --version`", "Clean working tree on <code>main</code>. <strong>Python 3.9.6.</strong>"),
 ("`git fetch origin`; `git checkout main`; `git pull origin main`", "Fetched new branches <code>round-six</code>, <code>round-eight</code>, <code>round-nine</code>. Fast-forwarded <code>main</code> from <code>efe55b9</code> to <code>cb5f3b8</code> (the merge of round eight)."),
 ("`( python3 run.py --round 5; … --round 8; python3 mutations_r6.py; mutations_r7.py; mutations_r8.py ) 2>&1 | tee …`", "Round 5: 14 cases, as expected 14 (0.31 s). Round 6: 18, 18 (0.42 s). Round 7: 12, 12 (0.27 s). Round 8: 12, 12 (0.27 s). Controls switched off: round 6 <strong>12 of 12</strong> noticed, round 7 <strong>14 of 14</strong>, round 8 <strong>21 of 21</strong>."),
 ("`git checkout round-nine`", "Switched to a new local branch tracking <code>origin/round-nine</code>."),
 ("`( python3 run.py --round 9; python3 mutations_r9.py ) 2>&1 | tee -a ~/mac-run-output.txt`", "Round 9: 12 cases, as expected 12 (0.43 s). Controls switched off: <strong>12 of 12</strong> noticed."),
 ("`for r in 5 6 7 8 9; do … cat \"$f\"; done > ~/mac-results.md`; `git checkout main`", "Wrote a combined copy of the latest Mac result files to my home folder (outside the repository). Back on <code>main</code>."),
 ("`git status`", "Listed 18 untracked result files under <code>results/round-5</code> to <code>round-9</code>."),
 ('`git checkout -b mac-run`; `git add results`; `git commit -m "Mac run: rounds 5 to 9 on Darwin, Python 3.9.6 (25 Oct 2026)"`; `git push origin mac-run`', "Commit <code>9573968</code>, 18 files, 2007 insertions. Pushed as new branch <code>mac-run</code>."),
 ("`git fetch origin`; `git checkout round-ten`; `git pull origin round-ten`", "Fetched <code>round-ten</code>. Already up to date."),
 ("`python3 run.py --round 10`", "12 cases in 0.33 s, as expected 12. File <code>20261024-222813-v3</code>."),
 ("`python3 mutations_r10.py`", "<strong>12 of 12</strong> switched-off controls noticed."),
 ('`git checkout -b mac-run-ten`; `git add results/round-10`; `git commit -m "Round ten: run on a Mac"`; `git push -u origin mac-run-ten`', "Commit <code>3241e0c</code>, four files, 337 insertions. Pushed as <code>mac-run-ten</code>."),
 ("`git fetch origin`; `git checkout round-eleven`; `git pull origin round-eleven`", "Fetched <code>round-eleven</code>. Already up to date, at <code>df01d79</code>."),
 ("`python3 run.py --round 11` (first try)", "<strong>Failed:</strong> <code>ModuleNotFoundError: No module named 'cryptography'</code>. The round-eleven code needed a package that this Mac did not have."),
 ("`python3 mutations_r11.py` (first try)", "<strong>Failed:</strong> <code>IndexError: list index out of range</code>, the same cause one step removed."),
 ('`git checkout -b mac-run-eleven`; `git add results/round-11`; `git commit …`; `git push -u origin mac-run-eleven`', "<code>nothing to commit, working tree clean</code>, then pushed an empty branch. There was no Mac result to save."),
 ("`git checkout round-eleven`; `git pull origin round-eleven`", "Fast-forwarded <code>df01d79</code> to <code>f54adf3</code>. That update added <code>lab/ed25519.py</code> (a plain-Python signature module, so the lab needs only the standard library) and removed the dependency."),
 ("`python3 run.py --round 11`", "12 cases in 0.6 s, as expected 12. File <code>20261024-224810-v3</code>."),
 ("`python3 mutations_r11.py`", "<strong>11 of 11</strong> switched-off controls noticed."),
 ('`git checkout mac-run-eleven`; `git add results/round-11`; `git commit -m "Round eleven: run on a Mac"`; `git push origin mac-run-eleven`', "Commit <code>046d74e</code>, four files, 343 insertions. Pushed <code>df01d79..046d74e</code>."),
]

def fix_cmd(rows):
    # commands are plain text with backticks; escape once, convert backticks to <code>
    res = []
    for i, (c, o) in enumerate(rows, 1):
        parts = re.split(r"(`[^`]*`)", c)
        c2 = "".join(f"<code>{E(p[1:-1])}</code>" if p.startswith("`") and p.endswith("`") and len(p) > 1 else E(p) for p in parts)
        c2 = c2.replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>")
        parts = re.split(r"(`[^`]*`)", o)
        o2 = "".join(f"<code>{E(p[1:-1])}</code>" if p.startswith("`") and p.endswith("`") and len(p) > 1 else p for p in parts)
        res.append((str(i), c2, o2))
    return table(["#", "What I typed", "What happened"], res, "mac-t mac-cmd")

def raw(name, label):
    p = os.path.join(ROOT, "assets/agl-mac", name)
    t = open(p, encoding="utf-8").read().rstrip()
    return (f'<details class="rout"><summary>{E(label)} <span>{len(t.splitlines())} lines, unedited</span></summary>'
            f'<p class="mac-dl"><a href="/assets/agl-mac/{name}">Download as a text file</a></p><pre tabindex="0">{E(t)}</pre></details>')

# ---- glance table --------------------------------------------------------------------------------------------------------
TITLES = {5: "24 Oct audit round (I13 to V, E, and others)", 6: "Round six: agent only sends instructions", 7: "Round seven: how an identity starts",
          8: "Round eight: agent goes round the gateway", 9: "Round nine: assistant answering from documents", 10: "Round ten: credentials and sessions",
          11: "Round eleven: delegation, keys, organisations"}
SBX = {5: "14 of 14", 6: "18 of 18", 7: "12 of 12", 8: "12 of 12", 9: "12 of 12", 10: "12 of 12", 11: "12 of 12"}
SBXM = {5: "none for this round", 6: "12 of 12", 7: "14 of 14", 8: "21 of 21", 9: "12 of 12", 10: "12 of 12", 11: "11 of 11"}
g = []
for r in sorted(glance):
    x = glance[r]
    g.append((f"{r}", E(TITLES.get(r, "")), E(x.get("v3", "")), E(x.get("mut", "") or "no control-off run on the Mac"), E(SBX[r]), E(SBXM[r])))

# ---- data table ----------------------------------------------------------------------------------------------------------
dg = []
last = None
for group, commit, branch, p, size, sha, h in data_rows:
    dg.append((E(group), f"<code>{E(branch)}</code> <code>{E(commit)}</code>", f"<code>{E(p)}</code>", f"{size:,}", E(h) if h else "", f'<code class="mac-sha">{sha}</code>'))

page_sha_note = f"{len(data_rows)} files"

body = f"""
      <header class="hero mcp-hero">
        <p class="eyebrow">AI governance lab</p>
        <h1>The Mac record</h1>
        <p class="dek">Every command I ran on my MacBook Air, what it printed, and every result file it produced, with a SHA-256 for each. Three sessions over two days. The mistakes are in here too.</p>
        <div class="mcp-ribbon" aria-hidden="true"></div>
      </header>
      <section><p class="body-text">I ran the lab on my own Mac so that the results do not depend only on a sandbox that I built and control. This page is the plain record of that. The commands are in the order I typed them. Next to each one is what came back. At the bottom are the three terminal sessions as they were, unedited. Every name, ID number and password in the output is made-up test data about an invented lender, Kaveri Finance.</p>
      <p class="body-text">Two things to keep in mind. First, I picked the Mac runs to confirm the sandbox, so the cases and the guesses were written before the Mac ran them, and the Mac result files are the ones I pushed straight from the terminal. Second, a Mac is one machine. It shows the code does not depend on my sandbox. It does not show the lab is right about real systems.</p></section>

      <section id="facts"><h2>The machine</h2>
      {table(["Item", "What it shows"], [
        ("Computer", "MacBook Air, Intel (the result files say <code>Darwin x86_64</code>)"),
        ("Python", "3.9.6, the one from the Command Line Tools. No virtual environment for the lab itself; one for Presidio on 24 Oct."),
        ("Shell", "bash, with Apple’s “default interactive shell is now zsh” notice at every login"),
        ("Prompt name", "<code>Roshans-Air</code> on 24 Oct and <code>Roshans-MacBook-Air</code> on 25 Oct. Session 1’s commit line says <code>Roshans-MacBook-Air.local</code>, so I treat it as one machine; I did not check the cause of the name change."),
        ("Repository", "<code>github.com/trivediroshan1-ui/ai-governance-lab</code>, cloned to <code>/Users/roshan/ai-governance-lab</code>"),
        ("Sessions", "1) Sat 24 Oct from 13:55. 2) Sat 24 Oct from 14:11. 3) Sun 25 Oct from 03:33. All times are IST, taken from the terminal’s “Last login” line."),
        ("Extra packages", "Only for the Presidio comparison: <code>presidio-analyzer</code>, <code>spacy 3.7.5</code>, <code>numpy 1.26.4</code>, <code>en_core_web_sm 3.7.1</code>, in a throw-away environment"),
      ])}</section>

      <section id="glance"><h2>Rounds five to eleven on the Mac, at a glance</h2>
      <p class="body-text">The first two columns are what the Mac printed. The last two are what the sandbox printed for the same round. “As expected” means the case did what my written guess said. “Controls noticed” means that when one control was switched off, in a copy of the code, the matching case saw the change.</p>
      {table(["Round", "Topic", "Mac: cases", "Mac: controls noticed", "Sandbox: cases", "Sandbox: controls noticed"], g, "mac-t")}
      <p class="body-text">All seven rounds match. Round five has no control-off run, on either machine. The sandbox also has first-run files for rounds nine and eleven that show a fault in my own work (a masking bug in round nine, a faulty test in round eleven); those are on the <a href="/ai-governance-lab/run/">run page</a>. The Mac ran the fixed versions.</p></section>

      <section id="s1"><h2>Session 1: Saturday 24 Oct, from 13:55</h2>
      <p class="body-text">Recording Track P by hand (Claude Sonnet 5.5, Low effort, a paid plan, in a fresh chat), the held-out starter cases, and a first try at Presidio. This session has the most mistakes.</p>
      {fix_cmd(S1)}</section>

      <section id="s2"><h2>Session 2: Saturday 24 Oct, from 14:11</h2>
      <p class="body-text">The Presidio comparison, run twice, and a Track P re-run that I recorded badly and then removed.</p>
      {fix_cmd(S2)}
      <h3>The two comparison tables, side by side</h3>
      <p class="body-text">From the second comparison command. Each tool is scored only on the cases it claims to cover, so the totals are out of different numbers. <strong>This is Presidio’s small English model with its default settings plus India recognisers, not a tuned Presidio setup.</strong></p>
      {table(["Detector", "Right answers", "Out of"], [("v1 (my first detector)", "20", "53"), ("v3 (my final detector)", "45", "53"), ("Presidio, default", "15", "33"), ("Presidio, with India recognisers", "16", "33")])}</section>

      <section id="s3"><h2>Session 3: Sunday 25 Oct, from 03:33</h2>
      <p class="body-text">Rounds five to eleven, one branch per push. Round eleven failed once, was fixed in the lab code, and ran clean.</p>
      {fix_cmd(S3)}</section>

      <section id="data"><h2>The Mac data, file by file</h2>
      <p class="body-text">{page_sha_note}. The SHA-256 is of the file exactly as it sits in the commit named. Two kinds of file per run: <code>-v3</code> (every case against my guess) and <code>-mutations</code> (controls switched off). Each has a readable <code>.md</code> and a full <code>.json</code>. To check one on your own machine: <code>git show BRANCH:results/PATH | shasum -a 256</code>.</p>
      {table(["Session", "Branch and commit", "File", "Bytes", "Headline", "SHA-256"], dg, "mac-t mac-data")}
      <p class="body-text">On <code>main</code>, the Track P file of 24 Oct has the one-line fix from session 1 applied (the policy note and the P6 note), made before the commit. The Presidio adapters (<code>adapters/presidio_cmd.py</code> and <code>adapters/presidio_india_cmd.py</code>) were also pushed from the Mac and are in the repository.</p></section>

      <section id="mistakes"><h2>What went wrong, in plain words</h2>
      <ul class="body-text mac-list">
        <li><strong>A broken file was pushed three times.</strong> I edited the held-out cases by hand and left stray lines after the closing braces. I pushed that (<code>b078a90</code>), then a half-fix (<code>439ef31</code>), before rewriting the file (<code>1f1af47</code>). The repository history shows all three.</li>
        <li><strong>A placeholder record was pushed.</strong> The Track P “clean re-run” was saved with notes like “hello” and “run it” (<code>661e52a</code>). I removed it a minute later (<code>efe55b9</code>). The history still has it. It was never used for any number on this site.</li>
        <li><strong>Round eleven failed on the Mac the first time.</strong> It needed a package (<code>cryptography</code>) that my Mac did not have. The sandbox had it, so I did not see the problem there. I fixed the lab so it needs only Python’s standard library, and ran again. The first Mac failure is in session 3 below.</li>
        <li><strong>An empty branch was pushed.</strong> After the failure, I ran the commit and push steps anyway. Nothing was committed, so <code>mac-run-eleven</code> first existed with no result files. It now holds the passing run.</li>
        <li><strong>Small noise.</strong> Typing the folder name as a command, a wrong folder guess three times, a stray paste of <code>loans_db.py</code>, a restored terminal replaying an old <code>date</code> line. None of it affects a result.</li>
        <li><strong>Track P is a hand-graded run.</strong> The nine pass marks and the notes were typed by me after reading Claude’s answers in a chat. It is one assistant, one plan, one day, graded by the person who built the lab. The P6 note says the masking example echoed part of a pasted PAN; I graded that as a pass.</li>
        <li><strong>The held-out starter cases are weak on purpose, and were written by Claude.</strong> Their file says so. v3 got 2 of 8 right on them, v1 got 3 of 8. That is a result against my own detector, and it is why I say the detector is limited.</li>
      </ul></section>

      <section id="raw"><h2>The three terminal sessions, unedited</h2>
      <p class="body-text">Copied from the terminal window as they were. I did not remove or change any line. Long package-install output is included. Open one to read it, or download the text file.</p>
      {raw("session-1-24-oct-1355.txt", "Session 1: Saturday 24 Oct, from 13:55")}
      {raw("session-2-24-oct-1411.txt", "Session 2: Saturday 24 Oct, from 14:11")}
      {raw("session-3-25-oct-0333.txt", "Session 3: Sunday 25 Oct, from 03:33")}
      </section>

      <aside class="hg-next"><p>Next: <a href="/ai-governance-lab/run/">the rounds and their outputs</a>, <a href="/ai-governance-lab/cases/">the case explorer</a>, or <a href="/ai-governance-lab/">the write-up</a>.</p></aside>
"""

# ---- shell: reuse head, nav and foot from the run page ---------------------------------------------------------------------
run = open(os.path.join(ROOT, "ai-governance-lab/run/index.html"), encoding="utf-8").read()
head = run[:run.index("</head>")]
head = re.sub(r'<meta name="description" content="[^"]*" />', '<meta name="description" content="Every command I ran on my Mac for the AI governance lab, what it printed, and every Mac result file with its SHA-256." />', head)
head = re.sub(r'<link rel="canonical" href="[^"]*" />', '<link rel="canonical" href="https://roshantrivedi.co.in/ai-governance-lab/mac/" />', head)
head = re.sub(r'<meta property="og:title" content="[^"]*" />', '<meta property="og:title" content="AI governance lab: the Mac record" />', head)
head = re.sub(r'<meta property="og:description" content="[^"]*" />', '<meta property="og:description" content="Every command I ran on my Mac for the AI governance lab, what it printed, and every Mac result file with its SHA-256." />', head)
head = re.sub(r'<meta property="og:url" content="[^"]*" />', '<meta property="og:url" content="https://roshantrivedi.co.in/ai-governance-lab/mac/" />', head)
head = re.sub(r"<title>.*?</title>", "<title>The Mac record &middot; Roshan Trivedi</title>", head)
head = re.sub(r"\n\s*<style>details\.rout.*?</style>", "", head, flags=re.S)
STYLE = ("<style>details.rout{margin:10px 0;border:1px solid var(--line,#2b3a55);border-radius:8px;padding:8px 12px}details.rout summary{cursor:pointer;font-weight:600}"
         "details.rout summary span{font-weight:400;opacity:.7;font-size:.85em;margin-left:8px}details.rout pre{overflow-x:auto;max-width:100%;font-size:12px;line-height:1.5;margin:10px 0 0;white-space:pre}"
         ".mac-wrap{overflow-x:auto;max-width:100%;margin:12px 0}.mac-t{border-collapse:collapse;width:100%;font-size:14px;line-height:1.5}"
         ".mac-t th,.mac-t td{border:1px solid var(--line,#2b3a55);padding:7px 10px;text-align:left;vertical-align:top}.mac-t th{font-weight:600;white-space:nowrap}"
         ".mac-cmd td:first-child{width:2.2em;text-align:right;opacity:.7}.mac-cmd td:nth-child(2){min-width:230px;overflow-wrap:anywhere}.mac-cmd td:nth-child(3){min-width:260px}"
         ".mac-t code{font-size:12.5px;overflow-wrap:anywhere}.mac-sha{font-size:11.5px;word-break:break-all;display:block;min-width:190px}.mac-data td{font-size:13px}.mac-data td:nth-child(3){min-width:200px}"
         ".mac-list li{margin:10px 0}.mac-dl{margin:8px 0}#raw h2,#data h2,#mistakes h2{margin-top:6px}</style>")
nav_start = run.index("<body")
nav_end = run.index('<main id="main">')
foot = run[run.index("</main>"):]
foot = re.sub(r'<script src="/assets/agl-(data|run|boot-run)\.js[^>]*></script>\s*', "", foot)
page = head + "\n  " + STYLE + "\n  </head>\n  " + run[nav_start:nav_end] + '<main id="main">' + body + foot
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(page)
print("ok", len(page), "bytes;", len(data_rows), "data files;", sorted(glance))
