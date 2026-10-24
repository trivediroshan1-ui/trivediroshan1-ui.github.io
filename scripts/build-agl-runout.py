#!/usr/bin/env python3
"""Puts the real run output of the 24 Oct audit round and rounds six to nine (made-up Kaveri Finance data) on /ai-governance-lab/run/.
Sandbox files come from the lab repo's results folder; the Mac files come from the lab repo branch origin/mac-run.
Re-run after any new run: python3 scripts/build-agl-runout.py [lab_repo]"""
import glob, html, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/ai-governance-lab"
PAGE = os.path.join(ROOT, "ai-governance-lab/run/index.html")
ROUNDS = [(5, "The 24 Oct audit round: 14 extra cases"), (6, "Round six: the agent only sends instructions (T1 to T18)"),
          (7, "Round seven: how an identity starts (H1 to H12)"), (8, "Round eight: when an agent goes round the gateway (B1 to B12)"),
          (9, "Round nine: an assistant that answers from documents (Q1 to Q12)"),
          (10, "Round ten: credentials, sessions and identity edge cases (C1 to C12)"),
          (11, "Round eleven: delegation, keys and organisations (D1 to D12)")]

def details(label, name, text):
    return f'<details class="rout"><summary>{html.escape(label)} <span>{html.escape(name)}</span></summary><pre tabindex="0">{html.escape(text.strip())}</pre></details>'

def sandbox(r, kind, label, first=False):
    fs = sorted(glob.glob(f"{LAB}/results/round-{r}/*-{kind}.md"))
    if not fs: return ""
    f = fs[0] if first else fs[-1]
    return details(label, os.path.basename(f), open(f, encoding="utf-8").read())

def mac(r, kind, label):
    br = {10: "origin/mac-run-ten", 11: "origin/mac-run-eleven"}.get(r, "origin/mac-run")
    names = subprocess.run(["git", "-C", LAB, "ls-tree", "-r", "--name-only", br, f"results/round-{r}/"], capture_output=True, text=True).stdout.split()
    names = [n for n in names if ("/20261024-2228" in n if r == 10 else "/20261024-2248" in n)] if r in (10, 11) else names     # the Mac files only
    names = sorted(n for n in names if n.endswith(f"-{kind}.md"))
    if not names: return ""
    t = subprocess.run(["git", "-C", LAB, "show", f"{br}:{names[-1]}"], capture_output=True, text=True).stdout
    return details(label, os.path.basename(names[-1]), t)

out = ['<!--runout-->', '<section id="real-output"><h2>Rounds five to eleven: the real output, on a Mac and in a sandbox</h2>',
       '<p class="body-text">The 24 Oct audit round and rounds six to eleven were first run in a Linux sandbox (Python 3.11). On 25 Oct I ran all of them again on my MacBook Air (Darwin, Python 3.9.6). The verdicts are the same on both machines. Below, each round shows the Mac files first and the sandbox files after them, unedited. In each pair, one file is every case against my written guess, and the other is the control-off run: one control switched off at a time, in a copy of the code, to see whether the matching case noticed. Every name and ID number is made-up test data about an invented lender.</p>']
for r, title in ROUNDS:
    out.append(f"<h3>{html.escape(title)}</h3>")
    out += [mac(r, "v3", "On my Mac: all cases against my guesses"), mac(r, "mutations", "On my Mac: controls switched off, one at a time")]
    if r == 9:
        out.append(sandbox(9, "v3", "In the sandbox, first run: 11 of 12 (Q8 was a fault in my masking code, fixed afterwards)", first=True))
    if r == 11:
        out.append(sandbox(11, "v3", "In the sandbox, first run: 11 of 12 (D11 was a fault in my test, fixed afterwards)", first=True))
    out += [sandbox(r, "v3", "In the sandbox: all cases against my guesses"), sandbox(r, "mutations", "In the sandbox: controls switched off, one at a time")]
out.append('<p class="body-text">The Mac files are also on the lab repository, on the branches <code>mac-run</code> (rounds five to nine) and <code>mac-run-ten</code> (round ten) and <code>mac-run-eleven</code> (round eleven). The guesses, with their SHA-256 hashes, are under <code>cases/</code>. The step-by-step version of each case is in the <a href="/ai-governance-lab/cases/">case explorer</a>. Every command I typed, with its output and a SHA-256 for each Mac file, is on <a href="/ai-governance-lab/mac/">the Mac record</a>.</p></section><!--/runout-->')
block = "\n      ".join(x for x in out if x)
s = open(PAGE, encoding="utf-8").read()
s = re.sub(r"\n?\s*<!--runout-->.*?<!--/runout-->", "", s, flags=re.S)
s = s.replace('<div id="agl-ctl" style="margin-top:22px"></div>', '<div id="agl-ctl" style="margin-top:22px"></div>\n      ' + block, 1)
if "details.rout" not in s:
    s = s.replace("</head>", '<style>details.rout{margin:8px 0;border:1px solid var(--line,#2b3a55);border-radius:8px;padding:8px 12px}details.rout summary{cursor:pointer;font-weight:600}details.rout summary span{font-weight:400;opacity:.7;font-size:.85em;margin-left:8px}details.rout pre{overflow-x:auto;max-width:100%;font-size:12.5px;line-height:1.5;margin:10px 0 0;white-space:pre}#real-output h3{margin-top:22px}</style></head>', 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("ok", s.count("<details"))
