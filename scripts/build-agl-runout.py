#!/usr/bin/env python3
"""Puts the real run output of rounds six to eight (made-up Kaveri Finance data) on /ai-governance-lab/run/.
Reads the newest result files in the lab repo. Re-run after any new run: python3 scripts/build-agl-runout.py [lab_repo]"""
import glob, html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/ai-governance-lab"
PAGE = os.path.join(ROOT, "ai-governance-lab/run/index.html")
ROUNDS = [(6, "Round six: the agent only sends instructions", "T1 to T18"), (7, "Round seven: how an identity starts", "H1 to H12"), (8, "Round eight: when an agent goes round the gateway", "B1 to B12")]
def newest(r, pat):
    fs = sorted(glob.glob(f"{LAB}/results/round-{r}/*{pat}.md")); return fs[-1]
def block(path, label):
    t = open(path, encoding="utf-8").read().strip()
    return f'<details class="rout"><summary>{html.escape(label)} <span>{html.escape(os.path.basename(path))}</span></summary><pre tabindex="0">{html.escape(t)}</pre></details>'
out = ['<!--runout-->', '<section id="real-output"><h2>Rounds six to eight: the real output</h2>',
       '<p class="body-text">Rounds six to eight ran later, in a Linux sandbox rather than on the MacBook, with Python 3.11, like the 24 Oct audit round. These are the files the run wrote, unedited. The first is the result of every case against my written guess. The second is the control-off run: one control switched off at a time, in a copy of the code, to see whether the matching case noticed. Every name and ID number is made-up test data about an invented lender.</p>']
for r, title, ids in ROUNDS:
    out.append(f'<h3>{title} ({ids})</h3>')
    out.append(block(newest(r, "-v3"), "All cases against my guesses"))
    out.append(block(newest(r, "-mutations"), "Controls switched off, one at a time"))
out.append('<p class="body-text">The guesses themselves, with their SHA-256 hashes, are in the lab repository under <code>cases/</code>. The step-by-step version of each case is in the <a href="/ai-governance-lab/cases/">case explorer</a>.</p></section><!--/runout-->')
s = open(PAGE, encoding="utf-8").read()
s = re.sub(r"<!--runout-->.*?<!--/runout-->\n?", "", s, flags=re.S)
s = s.replace('<div id="agl-ctl" style="margin-top:22px"></div>', '<div id="agl-ctl" style="margin-top:22px"></div>\n      ' + "\n".join(out), 1)
if "details.rout" not in s:
    s = s.replace("</head>", '<style>details.rout{margin:8px 0;border:1px solid var(--line,#2b3a55);border-radius:8px;padding:8px 12px}details.rout summary{cursor:pointer;font-weight:600}details.rout summary span{font-weight:400;opacity:.7;font-size:.85em;margin-left:8px}details.rout pre{overflow-x:auto;max-width:100%;font-size:12.5px;line-height:1.5;margin:10px 0 0;white-space:pre}#real-output h3{margin-top:22px}</style></head>', 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("ok")
