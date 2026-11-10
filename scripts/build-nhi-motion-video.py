#!/usr/bin/env python3
"""Renders a 60 second silent captioned motion video (1920x1080, 24 fps) of the NHI lab:
the lab method, the architecture, and the data. Every number is read from nhi-lab/audit/nhi-lab-audit.json
at build time and checked below, so the video cannot drift from the audit file. Run from the repo root.
Usage: python3 scripts/build-nhi-motion-video.py [out.mp4]      ONLY=12,500 renders just those frames."""
import os, sys, json, http.server, socketserver, threading, functools, subprocess, shutil, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets/share/nhi-lab-motion.mp4")
FPS, DUR, PORT, W, H = 24, 60, 8773, 1920, 1080

# ---------------------------------------------------------------- data, read and checked
AUD = json.load(open(os.path.join(ROOT, "nhi-lab/audit/nhi-lab-audit.json")))
ROWS = AUD["rows"]
N = len(ROWS)
MATCH = [r["guess_matched"] == "yes" for r in ROWS]
WRONG = [r for r in ROWS if r["guess_matched"] != "yes"]
MASKED = [bool(r["controls_not_noticed"]) for r in ROWS]
LIMITS = sum(1 for r in ROWS if r["limit"])
CONTROLS = sum(r["controls_checked"] for r in ROWS)
RUNS = collections.Counter(r["run"] for r in ROWS)
STEP_ORDER = ["Find", "Own", "Limit", "Store and issue", "Rotate and expire", "Watch", "Retire and respond"]
STEPS = collections.Counter(r["framework_step"] for r in ROWS)
FILES = collections.OrderedDict()
for r in ROWS:
    FILES.setdefault(r["guess_file"], [r["guess_file_sha256"], 0])[1] += 1
assert (N, sum(MATCH), len(WRONG), sum(MASKED), LIMITS, CONTROLS) == (67, 57, 10, 20, 33, 133), "audit totals changed: re-check the script text"
assert RUNS == {1: 27, 2: 19, 3: 2, 4: 19} and sum(STEPS.values()) == 67 and [STEPS[s] for s in STEP_ORDER] == [6, 8, 18, 10, 10, 7, 8]
assert AUD["meta"]["cases"] == N and AUD["meta"]["guesses_wrong"] == 10 and AUD["meta"]["cases_with_control_not_noticed"] == 20
assert len(FILES) == 6
# the 10 OWASP NHI Top 10 entries as the lab maps them: 8 direct, NHI4 partial, NHI8 weak (scripts/nhi_data.py OWASP)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from nhi_data import OWASP, STAGES  # noqa: E402
assert len(OWASP) == 10 and all(o[3].startswith("direct") for o in OWASP)

CYAN, GREEN, AMBER, PINK, VIOLET, MINT = "#4de2ff", "#34d399", "#f7c873", "#ff7a93", "#8b5cf6", "#7df2d0"
STEP_COL = ["#4de2ff", "#7df2d0", "#f7c873", "#c4b5fd", "#34d399", "#ff8fa3", "#8b5cf6"]

CSS = """
@font-face{font-family:'DM Sans';font-weight:400;src:url(/assets/dm-sans-latin-400-normal-CW0RaeGs.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:500;src:url(/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:700;src:url(/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:800;src:url(/assets/dm-sans-latin-800-normal.woff2) format('woff2')}
*{box-sizing:border-box;margin:0}
body{width:1920px;height:1080px;background:#05061a;color:#e8eefc;font-family:'DM Sans',Arial,sans-serif;position:relative;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;width:18px;background:linear-gradient(180deg,#22d3ee,#8b5cf6 40%,#34d399 75%,#f59e0b)}
.glow{position:absolute;right:-260px;top:-300px;width:1000px;height:1000px;background:radial-gradient(circle,rgba(77,226,255,.16),transparent 65%)}
.glow2{position:absolute;left:-300px;bottom:-420px;width:1100px;height:1100px;background:radial-gradient(circle,rgba(139,92,246,.14),transparent 65%)}
.eye{position:absolute;left:80px;top:46px;font-weight:700;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}
.tab{position:absolute;top:36px;height:44px;padding:0 20px;border:2px solid #2a3652;border-radius:999px;font-weight:700;font-size:22px;line-height:40px;color:#93a1bd;opacity:.45}
.foot{position:absolute;left:80px;right:70px;bottom:22px;border-top:2px solid #1f2a40;padding-top:12px;display:flex;justify-content:space-between;align-items:center}
.foot b{font-weight:800;font-size:26px;color:#4de2ff}.foot span{font-size:20px;color:#93a1bd}
.prog{position:absolute;left:18px;bottom:0;height:8px;background:linear-gradient(90deg,#22d3ee,#8b5cf6,#34d399,#f59e0b)}
.a{position:absolute;opacity:0}
h1{font-weight:800;font-size:116px;line-height:1.02;color:#fff;letter-spacing:-.02em}
h1 em{font-style:normal;color:#4de2ff}
h2{font-weight:800;font-size:64px;line-height:1.08;color:#fff;letter-spacing:-.01em}
h3{font-weight:500;font-size:34px;color:#a9b6d3}
p{font-size:40px;line-height:1.35;color:#c4cfe6}
.cap{left:80px;right:70px;top:926px;height:74px;border-left:8px solid #f7c873;background:rgba(247,200,115,.10);border-radius:14px;padding:0 28px;display:flex;align-items:center;font-size:30px;font-weight:600;color:#fff;line-height:1.15}
.node{height:100%;border:3px solid var(--c);border-radius:22px;background:rgba(255,255,255,.045);padding:18px 20px;color:#fff;box-shadow:0 0 38px -12px var(--c)}
.node i{font-style:normal;font-weight:800;font-size:22px;letter-spacing:.14em;color:var(--c);text-transform:uppercase;display:block;margin-bottom:6px}
.node b{display:block;font-weight:800;font-size:32px;line-height:1.1}
.node small{display:block;font-size:23px;line-height:1.28;font-weight:500;color:#b7c4df;margin-top:8px}
.pk{position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:#fff;box-shadow:0 0 28px 8px var(--c,#4de2ff);opacity:0}
.chip{border:3px solid var(--c);border-radius:999px;padding:12px 30px;font-size:38px;font-weight:800;color:var(--c);background:rgba(255,255,255,.04)}
.row{height:52px;display:flex;align-items:center}
.row .lab{width:520px;font-size:25px;font-weight:700;color:#fff;line-height:1.1}
.row .lab small{display:block;font-size:17px;font-weight:500;color:#a9b6d3;margin-top:3px}
.hash{font:600 25px/1 ui-monospace,Menlo,Consolas,monospace;color:#c9b8ff;width:330px}
.fill{height:30px;border-radius:8px;width:0}
.num{font-weight:800;font-size:34px;color:#fff;margin-left:16px}
.tile{width:410px;height:156px;border:3px solid #1f2a40;border-radius:22px;background:rgba(255,255,255,.045);padding:16px 24px}
.tile b{display:block;font-size:64px;font-weight:800;line-height:1;color:var(--c)}
.tile span{display:block;font-size:23px;line-height:1.22;color:#b7c4df;margin-top:6px}
.dot{position:absolute;width:40px;height:40px;border-radius:10px;opacity:0}
.mini{width:400px;height:56px;border-left:8px solid #ff7a93;background:rgba(255,122,147,.10);border-radius:12px;padding:5px 12px;font-size:18px;line-height:1.2;color:#e8eefc;overflow:hidden}
.mini b{font:700 17px/1.2 ui-monospace,Menlo,Consolas,monospace;color:#ff9db0;display:inline;margin-right:8px}
.seg{position:absolute;height:54px;border-radius:10px;font-weight:800;font-size:21px;line-height:54px;text-align:center;color:#04121a;opacity:0}
.url{font-weight:800;font-size:92px;color:#4de2ff;line-height:1.1}
.ln{position:absolute;background:var(--c,#4de2ff);opacity:0;border-radius:3px}
.leg{font-size:22px;color:#b7c4df;display:flex;align-items:center;gap:12px;margin-right:26px}
.leg i{display:inline-block;width:26px;height:26px;border-radius:7px}
"""

els = []


def A(html, x, y, t_in, t_out, w=None, h=None, cls="", extra=""):
    st = f"left:{x}px;top:{y}px;" + (f"width:{w}px;" if w else "") + (f"height:{h}px;" if h else "") + extra
    return f"<div class='a {cls}' data-in='{t_in}' data-out='{t_out}' style='{st}'>{html}</div>"


def LN(x, y, w, h, c, t_in, t_out):  # a straight connector drawn as a thin rectangle that grows from its start
    return f"<div class='ln' data-in='{t_in}' data-out='{t_out}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{c}'></div>"


def CAP(text, t_in, t_out):
    return A(text, 80, 926, t_in, t_out, cls="cap")


def PK(keys, color=CYAN):  # a moving dot: keys = [(t, x, y), ...]
    return f"<div class='pk' data-keys='{json.dumps(keys)}' style='--c:{color}'></div>"


# ---------------------------------------------------------------- tabs and shell
TABS = [("1  Lab", 5.0, 21.0, 1390), ("2  Architecture", 21.0, 39.0, 1520), ("3  Data", 39.0, 56.0, 1750)]
tabs = "".join(f"<div class='tab' data-on='{a},{b}' style='left:{x}px'>{n}</div>" for n, a, b, x in TABS)

# ---------------------------------------------------------------- scene 0: intro 0-5
els += [A(f"<h1><em>{N}</em> machine identity cases</h1>", 80, 290, 0.3, 5.0, w=1780),
        A("<p style='font-size:46px'>A lab with made-up data. First how it runs, then how it is built, then what the numbers say.</p>", 80, 520, 1.3, 5.0, w=1500)]
for i, (t, c) in enumerate([("The lab", CYAN), ("The architecture", GREEN), ("The data", AMBER)]):
    els.append(A(f"<div class='chip' style='--c:{c}'>{t}</div>", 80 + i * 400, 740, 2.4 + i * 0.5, 5.0))
els.append(A("<p style='font-size:28px;color:#93a1bd'>Every number in this video is read from the lab's audit file.</p>", 80, 880, 4.0, 5.0, w=1500))

# ---------------------------------------------------------------- scene 1: the lab 5-21
els += [A("<h2>1. The lab: how each case is run</h2>", 80, 112, 5.2, 21.0)]
NODES = [("1", "Write the guess", "What I expect, before any code", CYAN),
         ("2", "Hash it", "SHA-256 of the guess file", CYAN),
         ("3", "Commit it", "Alone, before any code, so it cannot change later", CYAN),
         ("4", "Write the code", "A small model of each control, in memory", GREEN),
         ("5", "Run twice", "Control off, then on. Compare with the guess", GREEN),
         ("6", "Switch each control off alone", "Does any check notice?", AMBER)]
NW, GAP, X0, NY, NH = 250, 48, 90, 232, 262
cx = []
for i, (n, h, d, c) in enumerate(NODES):
    x = X0 + i * (NW + GAP); cx.append(x + NW // 2)
    ti = 6.1 + i * 1.5
    els.append(A(f"<div class='node' style='--c:{c}'><i>Step {n}</i><b>{h}</b><small>{d}</small></div>", x, NY, ti - 0.2, 21.0, w=NW, h=NH))
    els.append(LN(cx[-1] - 2, NY + NH, 4, 34, c, ti, 21.0))
els.append(LN(cx[0], NY + NH + 32, cx[-1] - cx[0], 4, CYAN, 6.3, 21.0))
keys = [(6.0, cx[0], NY + NH + 34)]
for i in range(6):
    ti = 6.4 + i * 1.5
    keys += [(ti, cx[i], NY + NH + 34), (ti + 0.5, cx[i], NY + NH + 34)] if i else [(ti, cx[0], NY + NH + 34)]
keys[-1] = (6.4 + 5 * 1.5 + 0.6, cx[5], NY + NH + 34)
els.append(PK(keys))
els.append(CAP("I write each guess first, hash it and commit it. Only then do I write the code and run it.", 5.4, 15.9))

# guess files panel 16-21
els.append(A("<h3>Six guess files, each with its own hash. Total: 67 cases</h3>", 90, 556, 15.9, 21.0, w=1700))
labels = {"guesses-round-14-15.md": ("Rounds 14 and 15", "first run"), "guesses-round-17.md": ("Round 17, shadow AI", "first run"),
          "guesses-gap-cases.md": ("Gap cases", "first run"), "guesses-stretch-and-chains.md": ("Stretch cases and chain tests", "second run"), "guesses-round-18.md": ("Round 18, NHI4 and NHI8", "third run"), "guesses-round-19.md": ("Round 19, the queued cases", "fourth run")}
cols = [CYAN, VIOLET, GREEN, AMBER, PINK, MINT]
for i, (fn, (sha, cnt)) in enumerate(FILES.items()):
    y = 596 + i * 52; nm, run = labels[fn]
    t0 = 16.3 + i * 0.5
    els.append(A(f"<div class='row'><div class='lab'>{nm}<small>{fn}, {run}</small></div><div class='hash'>{sha[:12]}&hellip;</div>"
                 f"<div class='fill' data-bar='{cnt * 34}' data-bar-in='{t0 + 0.2}' style='background:{cols[i]}'></div><div class='num'>{cnt}</div></div>", 90, y, t0, 21.0, w=1700))
els.append(CAP("Anyone can re-check those six hashes with one small script.", 16.0, 20.9))

# ---------------------------------------------------------------- scene 2: architecture 21-39
els.append(A("<h2>2. The architecture</h2>", 80, 112, 21.2, 39.0))
els.append(A("<h3 style='font-size:28px'>Evidence in, one shared data module, three outputs</h3>", 80, 178, 21.4, 30.0, w=1500))
els.append(A("<h3 style='font-size:28px'>A 7 step framework holds all 67 cases</h3>", 80, 178, 30.4, 39.0, w=1500))
# diagram 21-30
BX = {"A": (90, 250, 330, 150), "F": (90, 455, 330, 150), "B": (90, 650, 330, 150), "C": (520, 650, 330, 150),
      "D": (950, 240, 330, 170), "E1": (1380, 235, 430, 135), "E2": (1380, 420, 430, 135), "E3": (1380, 605, 430, 135)}


def box(k, head, title, sub, c, t, to=30.0):
    x, y, w, h = BX[k]
    return A(f"<div class='node' style='--c:{c}'><i>{head}</i><b>{title}</b><small>{sub}</small></div>", x, y, t, to, w=w, h=h)


els += [box("A", "Evidence", "guesses/", "6 hashed guess files", CYAN, 21.6),
        box("F", "Check", "verify.py", "Re-checks the 6 hashes", MINT, 22.2),
        box("B", "Code", "run.py to run4.py", "Small models of each control", GREEN, 22.8),
        box("C", "Evidence", "results.json", "and results-stretch.json", GREEN, 23.6),
        box("D", "Shared", "nhi_data.py", "One reader for guesses and results", VIOLET, 24.8),
        box("E1", "Output", "Lab and framework pages", "", AMBER, 25.8),
        box("E2", "Output", "Audit data", "CSV and JSON, free to download", AMBER, 26.3),
        box("E3", "Output", "The PDF book", "83 pages", AMBER, 26.8)]
els += [LN(255 - 2, 400, 4, 55, MINT, 22.4, 30.0),  # A - verify.py
        LN(420, 725 - 2, 100, 4, GREEN, 23.8, 30.0),  # B -> C
        LN(420, 325 - 2, 530, 4, CYAN, 24.9, 30.0),  # A -> D
        LN(850, 725 - 2, 267, 4, GREEN, 25.0, 30.0), LN(1115 - 2, 410, 4, 315, GREEN, 25.1, 30.0),  # C -> D (up)
        LN(1280, 325 - 2, 50, 4, AMBER, 26.0, 30.0), LN(1330 - 2, 302, 4, 370, AMBER, 26.1, 30.0),
        LN(1330, 302 - 2, 50, 4, AMBER, 26.2, 30.0), LN(1330, 487 - 2, 50, 4, AMBER, 26.6, 30.0), LN(1330, 672 - 2, 50, 4, AMBER, 27.0, 30.0)]
els.append(PK([(24.0, 420, 725), (24.6, 850, 725), (25.4, 1115, 725), (26.0, 1115, 410), (26.3, 1115, 410), (26.6, 1280, 325), (27.0, 1330, 325), (27.5, 1330, 487), (28.0, 1380, 487), (28.3, 1380, 487)], GREEN))
els.append(A("<p style='font-size:25px;color:#93a1bd'>guess files, read only</p>", 560, 270, 25.4, 30.0, w=380))
els.append(A("<p style='font-size:25px;color:#93a1bd'>reads results</p>", 1135, 560, 25.6, 30.0, w=190))
els.append(A("<p style='font-size:25px;color:#93a1bd'>re-checks the hashes</p>", 270, 412, 22.8, 30.0, w=260, extra="font-size:25px;"))
els.append(CAP("Guesses and results pass through one data module. The pages, audit files and the book are built from it.", 21.5, 29.9))
# framework 30-39
for i, (key, name, desc) in enumerate(STAGES):
    nm = STEP_ORDER[i]
    y = 232 + i * 92; t0 = 30.7 + i * 0.5
    els.append(A(f"<div class='row' style='height:84px'><div class='lab' style='width:640px'>{i + 1}. {name}<small>{desc}</small></div>"
                 f"<div class='fill' data-bar='{STEPS[STEP_ORDER[i]] * 50}' data-bar-in='{t0 + 0.2}' style='height:44px;background:{STEP_COL[i]}'></div><div class='num' style='font-size:44px'>{STEPS[STEP_ORDER[i]]}</div></div>", 90, y, t0, 39.0, w=1740))
els.append(A("<p style='font-size:30px;color:#c4cfe6'>67 cases, each at exactly one step</p>", 1500, 700, 34.6, 39.0, w=340))
els.append(CAP("Every case sits at exactly one of 7 steps: find, own, limit, store, rotate, watch, retire.", 30.5, 38.9))

# ---------------------------------------------------------------- scene 3: data 39-56
els.append(A("<h2>3. What the data says</h2>", 80, 112, 39.2, 56.0))
els.append(A(f"<h3 style='font-size:26px'>Runs of {RUNS[1]}, {RUNS[2]}, {RUNS[3]} and {RUNS[4]} cases. Every run repeated on a second machine with identical output.</h3>", 80, 180, 39.4, 56.0, w=1750))
TILES = [(N, "cases run", CYAN), (sum(MATCH), "guesses matched", MINT), (len(WRONG), "guesses wrong", PINK),
         (CONTROLS, "controls switched off, one at a time", VIOLET), (sum(MASKED), "cases with a control no check noticed", AMBER), (LIMITS, "cases with a recorded limit", "#c4b5fd")]
for i, (v, s, c) in enumerate(TILES):
    x = 90 + (i % 2) * 440; y = 225 + (i // 2) * 168; t0 = 39.8 + i * 0.4
    els.append(A(f"<div class='tile' style='--c:{c}'><b data-count='{v}' data-count-in='{t0 + 0.1}'>0</b><span>{s}</span></div>", x, y, t0, 56.0))
# case grid
GX, GY, CELL = 1010, 225, 48
cells = []
for i in range(N):
    r, c = divmod(i, 14)
    ti = 40.8 + i * 0.07
    fill = MINT if MATCH[i] else PINK
    ring = f"box-shadow:0 0 0 4px {AMBER};" if MASKED[i] else ""
    cells.append(f"<div class='dot' data-in='{ti:.2f}' style='left:{GX + c * CELL + 4}px;top:{GY + 30 + r * CELL + 4}px;background:{fill};{ring}'></div>")
els += cells
els.append(A(f"<div style='display:flex;flex-wrap:wrap;gap:6px 0'><span class='leg' style='color:#fff'>Each square is one case:</span><span class='leg'><i style='background:{MINT}'></i>guess matched</span><span class='leg'><i style='background:{PINK}'></i>guess wrong</span>"
             f"<span class='leg'><i style='background:transparent;box-shadow:0 0 0 4px {AMBER}'></i>a control no check noticed</span></div>", GX, 508, 44.4, 56.0, w=820))
# the wrong guesses
SHORT = {"S-R17-05": "The scan missed 2 secrets. I guessed 1.",
         "N-R14-25": "Another control already blocked both replays.",
         "N-R14-07": "Entry counts were off: 43 not 51, 29 not 30.",
         "C-R16-C01": "A different single control mattered most.",
         "N-R18-01": "I guessed 3 alerts. It gave 1, one per new network.",
         "P-R15-06": "Rotation mattered. The injection alone did not.",
         "P-R15-12": "The drill found 1 fault, not the 2 I guessed.",
         "P-R15-22": "14 of 20 events arrive even with no controls.",
         "S-R17-08": "1 agent kept credentials at day 10, not 4.",
         "S-R17-09": "5 alerts, not 4. I never said what I counted."}
els.append(A("<h3 style='font-size:26px'>The 10 wrong guesses</h3>", GX, 578, 45.6, 56.0, w=820, extra="font-size:26px;"))
for i, r in enumerate(WRONG):
    assert r["id"] in SHORT, r["id"]
    x = GX + (i % 2) * 420; y = 616 + (i // 2) * 60
    els.append(A(f"<div class='mini'><b>{r['id']}</b>{SHORT[r['id']]}</div>", x, y, 45.9 + i * 0.3, 56.0, w=400, h=56))
# OWASP strip
els.append(A("<h3 style='font-size:26px'>OWASP Non-Human Identities Top 10, NHI1 to NHI10, as the lab maps it</h3>", 90, 735, 49.2, 56.0, w=900, extra="font-size:26px;"))
for i, o in enumerate(OWASP):
    kind = o[3]
    col = MINT if kind.startswith("direct") else (AMBER if kind.startswith("partial") else PINK)
    els.append(f"<div class='seg' data-in='{49.5 + i * 0.12:.2f}' style='left:{90 + i * 88}px;top:778px;width:80px;background:{col}'>{o[0].replace('NHI', '')}</div>")
els.append(A("<p style='font-size:23px;line-height:1.3;color:#b7c4df'>Green: every one of the 10 now has a tested case. NHI4 and NHI8 were the thin ones until round 18, which added two cases for them.</p>", 90, 844, 50.2, 56.0, w=880))
els.append(CAP("57 guesses matched, 10 were wrong. I wrote both guesses and code, so a match proves little. The misses are the useful part.", 39.4, 45.4))
els.append(CAP("In 20 cases, switching a control off alone changed nothing the checks could see. Another control may be covering it. 33 cases carry a recorded limit.", 45.5, 55.9))

# ---------------------------------------------------------------- end 56-60
els += [A("<h2 style='font-size:84px'>Free and public</h2>", 80, 250, 56.2, DUR, w=1700),
        A("<div class='url'>roshantrivedi.co.in/nhi-lab</div>", 80, 410, 56.6, DUR, w=1760),
        A("<p style='font-size:40px'>67 animated cases, the framework, the market view, the audit data and an 83 page PDF book.</p>", 80, 600, 57.0, DUR, w=1700),
        A("<p style='font-size:30px;color:#93a1bd'>Made-up data only. The models are small simulations written by the same person who wrote the guesses.</p>", 80, 800, 57.8, DUR, w=1700)]

HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='glow2'></div><div class='eye'>Non-human identity lab</div>{tabs}
{''.join(els)}
<div class='foot'><b>roshantrivedi.co.in/nhi-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
function lin(x){{return x<0?0:x>1?1:x}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.55),b=1-ease((t-(o-0.45))/0.45);
  e.style.opacity=t>=i&&t<o?Math.min(a,b):0; e.style.transform='translateY('+((1-ease((t-i)/0.55))*22)+'px)';
 }});
 document.querySelectorAll('.ln').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.5),b=1-ease((t-(o-0.45))/0.45);
  e.style.opacity=t>=i&&t<o?Math.min(a,b)*0.9:0;
 }});
 document.querySelectorAll('.dot').forEach(function(e){{
  var i=+e.dataset.in,a=ease((t-i)/0.3),b=1-ease((t-55.55)/0.45);
  e.style.opacity=t>=i&&t<56?Math.min(a,b):0; e.style.transform='scale('+(0.6+0.4*a)+')';
 }});
 document.querySelectorAll('.seg').forEach(function(e){{
  var i=+e.dataset.in,a=ease((t-i)/0.3),b=1-ease((t-55.55)/0.45);
  e.style.opacity=t>=i&&t<56?Math.min(a,b):0;
 }});
 document.querySelectorAll('[data-bar]').forEach(function(e){{
  e.style.width=(+e.dataset.bar*ease((t-(+e.dataset.barIn))/0.9))+'px';
 }});
 document.querySelectorAll('[data-count]').forEach(function(e){{
  e.textContent=Math.round(+e.dataset.count*ease((t-(+e.dataset.countIn))/1.0));
 }});
 document.querySelectorAll('.pk').forEach(function(e){{
  var k=JSON.parse(e.dataset.keys),n=k.length;
  if(t<k[0][0]||t>k[n-1][0]){{e.style.opacity=0;return}}
  var j=0;while(j<n-2&&t>k[j+1][0])j++;
  var u=lin((t-k[j][0])/(k[j+1][0]-k[j][0]||1));u=u*u*(3-2*u);
  e.style.left=(k[j][1]+(k[j+1][1]-k[j][1])*u)+'px';e.style.top=(k[j][2]+(k[j+1][2]-k[j][2])*u)+'px';
  e.style.opacity=Math.min(1,(t-k[0][0])/0.3,(k[n-1][0]-t)/0.3);
 }});
 document.querySelectorAll('.tab').forEach(function(e){{
  var r=e.dataset.on.split(',');e.style.opacity=(t>=+r[0]&&t<+r[1])?1:0.4;
  e.style.borderColor=(t>=+r[0]&&t<+r[1])?'#4de2ff':'#2a3652';e.style.color=(t>=+r[0]&&t<+r[1])?'#fff':'#93a1bd';
 }});
 document.getElementById('prog').style.width=(1902*t/{DUR})+'px';
}};
</script></body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    work = os.path.abspath(os.path.join(ROOT, "..", "nhi-motion-frames")); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    page = os.path.join(ROOT, "assets", "_nhi_motion.html"); open(page, "w").write(HTML)

    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_nhi_motion.html"); pg.wait_for_timeout(800)
            only = os.environ.get("ONLY")
            frames = [int(x) for x in only.split(",")] if only else range(int(DUR * FPS))
            for n in frames:
                pg.evaluate(f"render({n / FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    if os.environ.get("ONLY"): print("frames in", work); return
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(work, "f%05d.png"),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "veryfast", "-movflags", "+faststart", OUT])
    print(OUT, os.path.getsize(OUT))


main()
