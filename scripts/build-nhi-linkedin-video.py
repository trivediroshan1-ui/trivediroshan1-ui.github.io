#!/usr/bin/env python3
"""Renders the square social video of the NHI lab (1080x1080, 24 fps, about two minutes, silent, captioned).
Scenes: the problem, the seven step framework as a loop, the method, two cases as animated workflows,
the architecture, the results, and where to find it. Every number is read from
nhi-lab/audit/nhi-lab-audit.json at build time and checked below. Run from the repo root.
Usage: python3 scripts/build-nhi-linkedin-video.py [out.mp4]
ONLY=12,500 renders just those frames into ../nhi-linkedin-frames (for checking a layout)."""
import os, sys, json, math, http.server, socketserver, threading, functools, subprocess, shutil, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets/share/nhi-lab-square.mp4")
FPS, PORT, W, H = 24, 8774, 1080, 1080

# ---------------------------------------------------------------- data, read and checked
AUD = json.load(open(os.path.join(ROOT, "nhi-lab/audit/nhi-lab-audit.json")))
ROWS = AUD["rows"]; N = len(ROWS); BY = {r["id"]: r for r in ROWS}
MATCH = [r["guess_matched"] == "yes" for r in ROWS]
WRONG = [r for r in ROWS if r["guess_matched"] != "yes"]
MASKED = [bool(r["controls_not_noticed"]) for r in ROWS]
LIMITS = sum(1 for r in ROWS if r["limit"])
CONTROLS = sum(r["controls_checked"] for r in ROWS)
STEP_ORDER = ["Find", "Own", "Limit", "Store and issue", "Rotate and expire", "Watch", "Retire and respond"]
STEPS = collections.Counter(r["framework_step"] for r in ROWS)
FILES = {r["guess_file"] for r in ROWS}
assert (N, sum(MATCH), len(WRONG), sum(MASKED), LIMITS, CONTROLS) == (67, 57, 10, 20, 33, 133), "audit totals changed: re-check the script text"
assert [STEPS[s] for s in STEP_ORDER] == [6, 8, 18, 10, 10, 7, 8] and len(FILES) == 6
CI, VD = BY["N-R14-25"], BY["N-R14-23"]
assert (CI["without_control"], CI["with_control"], CI["controls_not_noticed"], CI["guess_matched"]) == ("Both replays work", "Both replays refused", "short_ttl", "no")
assert VD["without_control"] == "Grant accepted, replay reads files" and VD["controls_not_noticed"] == "breach_revoke"
assert VD["with_control"] == "Allowlist refuses the grant; revoke ends replays after 60 minutes"
assert AUD["meta"]["mac_commits"]["fourth_run_guesses"] == "a2dc1fd" and AUD["meta"]["mac_commits"]["fourth_run_code_and_results"] == "cbec7a8"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from nhi_data import STAGES  # noqa: E402

CYAN, GREEN, AMBER, PINK, VIOLET, MINT, LILAC = "#4de2ff", "#34d399", "#f7c873", "#ff7a93", "#a78bfa", "#7df2d0", "#c4b5fd"
STEP_COL = ["#4de2ff", "#7df2d0", "#f7c873", "#c4b5fd", "#34d399", "#ff8fa3", "#a78bfa"]

# scene timing (seconds)
S = dict(hook=0, loop=9, method=27, ci=44, vendor=66, arch=86, data=101, end=117)
DUR = 124
SCENES = [("loop", "Framework"), ("method", "Method"), ("ci", "Workflow 1"), ("vendor", "Workflow 2"), ("arch", "Architecture"), ("data", "Results")]

CSS = """
@font-face{font-family:'DM Sans';font-weight:400;src:url(/assets/dm-sans-latin-400-normal-CW0RaeGs.woff2)}
@font-face{font-family:'DM Sans';font-weight:500;src:url(/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2)}
@font-face{font-family:'DM Sans';font-weight:600;src:url(/assets/dm-sans-latin-600-normal-Aqo67rzb.woff2)}
@font-face{font-family:'DM Sans';font-weight:700;src:url(/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2)}
@font-face{font-family:'DM Sans';font-weight:800;src:url(/assets/dm-sans-latin-800-normal.woff2)}
@font-face{font-family:'JB';font-weight:600;src:url(/assets/jetbrains-mono-latin-semibold.woff2)}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1080px;background:#06071c;color:#e8eefc;font-family:'DM Sans',sans-serif;position:relative;overflow:hidden}
.bg{position:absolute;inset:-200px;background:radial-gradient(700px 600px at 85% 10%,rgba(77,226,255,.16),transparent 70%),radial-gradient(800px 700px at 5% 95%,rgba(139,92,246,.18),transparent 70%)}
.gridbg{position:absolute;inset:0;background-image:linear-gradient(rgba(167,139,250,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(167,139,250,.07) 1px,transparent 1px);background-size:54px 54px;-webkit-mask-image:radial-gradient(circle at 50% 45%,#000,transparent 78%)}
.eye{position:absolute;left:56px;top:40px;font-weight:700;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}
.who{position:absolute;right:56px;top:40px;font-weight:600;font-size:22px;color:#93a1bd}
.dots{position:absolute;right:56px;top:76px;display:flex;gap:8px}
.dots i{display:block;height:8px;width:26px;border-radius:4px;background:#26314d}
.foot{position:absolute;left:56px;right:56px;bottom:26px;display:flex;justify-content:space-between;align-items:center}
.foot b{font-weight:800;font-size:26px;color:#4de2ff}.foot span{font-size:21px;color:#93a1bd}
.prog{position:absolute;left:0;bottom:0;height:8px;background:linear-gradient(90deg,#22d3ee,#8b5cf6,#34d399,#f59e0b)}
.a{position:absolute;opacity:0;will-change:transform,opacity}
h1{font-weight:800;font-size:92px;line-height:1.04;color:#fff;letter-spacing:-.02em}
h1 em,h2 em,p em{font-style:normal;color:#4de2ff}
h2{font-weight:800;font-size:58px;line-height:1.08;color:#fff;letter-spacing:-.01em}
.kick{font-weight:800;font-size:20px;letter-spacing:.18em;text-transform:uppercase;color:var(--c,#4de2ff)}
p{font-size:40px;line-height:1.3;color:#c4cfe6}
.cap{left:56px;right:56px;top:880px;min-height:100px;border-left:8px solid #f7c873;background:rgba(247,200,115,.11);border-radius:14px;padding:16px 24px;display:flex;align-items:center;font-size:30px;font-weight:600;color:#fff;line-height:1.22}
.box{width:100%;height:100%;border:3px solid var(--c);border-radius:20px;background:rgba(12,14,40,.86);padding:12px 18px;color:#fff;box-shadow:0 0 42px -14px var(--c)}
.box i{font-style:normal;font-weight:800;font-size:17px;letter-spacing:.14em;color:var(--c);text-transform:uppercase;display:block;margin-bottom:3px}
.box b{display:block;font-weight:800;font-size:30px;line-height:1.08}
.box small{display:block;font-size:22px;line-height:1.2;font-weight:500;color:#b7c4df;margin-top:4px}
.pk{position:absolute;width:28px;height:28px;margin:-14px 0 0 -14px;border-radius:50%;background:#fff;box-shadow:0 0 26px 8px var(--c,#4de2ff);opacity:0}
.ln{position:absolute;background:var(--c,#4de2ff);opacity:0;border-radius:3px}
.icon{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-weight:800;color:var(--c)}
.ppl{display:grid;grid-template-columns:repeat(4,46px);gap:14px}
.ppl i,.mach i{display:block;width:46px;height:46px;border-radius:50%;background:#c4cfe6;opacity:.9}
.mach{display:grid;grid-template-columns:repeat(10,38px);gap:10px}
.mach i{width:38px;height:38px;border-radius:9px;background:var(--c);opacity:0}
.nd{width:176px;height:108px;border:3px solid var(--c);border-radius:22px;background:#0b0d29;text-align:center;padding-top:8px;box-shadow:0 0 36px -14px var(--c)}
.nd b{display:block;font-size:42px;font-weight:800;color:var(--c);line-height:1}
.nd span{display:block;font-size:19px;font-weight:700;color:#fff;margin-top:6px;line-height:1.1}
.step{display:flex;align-items:center;gap:22px;height:100%}
.step u{text-decoration:none;flex:0 0 68px;height:68px;border-radius:50%;border:3px solid var(--c);color:var(--c);font-weight:800;font-size:32px;line-height:62px;text-align:center;background:#0b0d29}
.step b{display:block;font-weight:800;font-size:36px;line-height:1.1;color:#fff}
.step small{display:block;font-size:25px;line-height:1.2;color:#b7c4df;margin-top:3px}
.log{font-family:'JB',monospace;font-size:27px;color:#dfe6f7;background:#0b0d29;border:2px solid #26314d;border-radius:14px;padding:14px 20px;width:100%}
.log b{font-weight:600;color:var(--c)}
.lane{font-weight:800;font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:var(--c)}
.chip{display:inline-flex;align-items:center;gap:12px;border:3px solid var(--c);border-radius:16px;background:rgba(12,14,40,.9);padding:12px 18px;font-size:25px;font-weight:700;color:#fff;line-height:1.15;width:100%;height:100%;box-shadow:0 0 34px -14px var(--c)}
.res{width:100%;height:100%;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:27px;font-weight:800;color:#06071c;background:var(--c);text-align:center;line-height:1.1;padding:0 10px}
.sw{display:flex;align-items:center;gap:14px;font-size:24px;font-weight:700;color:#fff}
.sw .t{width:76px;height:40px;border-radius:20px;background:#34d399;position:relative;transition:none}
.sw .t::after{content:'';position:absolute;top:5px;left:41px;width:30px;height:30px;border-radius:50%;background:#fff}
.sw.off .t{background:#3a4769}.sw.off .t::after{left:5px}
.tile{width:100%;height:100%;border:3px solid #26314d;border-radius:22px;background:rgba(12,14,40,.86);padding:16px 26px}
.tile b{display:block;font-size:84px;font-weight:800;line-height:1;color:var(--c)}
.tile span{display:block;font-size:26px;line-height:1.2;color:#c4cfe6;margin-top:6px}
.dot{position:absolute;width:52px;height:52px;border-radius:12px;opacity:0}
.leg{font-size:23px;color:#c4cfe6;display:inline-flex;align-items:center;gap:10px;margin-right:24px}
.leg i{display:inline-block;width:24px;height:24px;border-radius:7px}
.miss{width:100%;height:100%;border-left:8px solid #ff7a93;background:rgba(255,122,147,.11);border-radius:14px;padding:0 22px;display:flex;align-items:center;font-size:29px;font-weight:600;line-height:1.2;color:#fff}
.url{font-weight:800;font-size:66px;color:#4de2ff;line-height:1.1}
.clock{font-family:'JB',monospace;font-size:26px;color:#f7c873}
"""

els = []


def A(html, x, y, t_in, t_out, w=None, h=None, cls="", extra="", fx="up"):
    st = f"left:{x}px;top:{y}px;" + (f"width:{w}px;" if w else "") + (f"height:{h}px;" if h else "") + extra
    return f"<div class='a {cls}' data-in='{t_in}' data-out='{t_out}' data-fx='{fx}' style='{st}'>{html}</div>"


def LN(x, y, w, h, c, t_in, t_out):
    d = "x" if w >= h else "y"
    return f"<div class='ln' data-in='{t_in}' data-out='{t_out}' data-dir='{d}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{c}'></div>"


def CAP(text, t_in, t_out):
    return A(text, 56, 880, t_in, t_out, cls="cap")


def PK(keys, color=CYAN):
    return f"<div class='pk' data-keys='{json.dumps(keys)}' style='--c:{color}'></div>"


def BOX(x, y, w, h, c, head, title, sub, t_in, t_out, fx="pop"):
    return A(f"<div class='box' style='--c:{c}'><i>{head}</i><b>{title}</b>" + (f"<small>{sub}</small>" if sub else "") + "</div>", x, y, t_in, t_out, w=w, h=h, fx=fx)


def SW(label, x, y, t_in, t_out, flips, w=440):  # flips: [(time, on), ...]; the last flip at or before t wins
    return A(f"<div class='sw' data-flips='{json.dumps(flips)}'><div class='t'></div>{label}</div>", x, y, t_in, t_out, w=w)


# ---------------------------------------------------------------- 0. hook
t = S["hook"]; to = S["loop"]
els += [A("<div class='kick'>Machine identities</div>", 56, 150, t + 0.3, to),
        A("<h2 style='font-size:62px'>Most companies have far more of them than people.</h2>", 56, 196, t + 0.6, to, w=960)]
els.append(A("<div class='kick' style='--c:#c4cfe6'>People</div><div class='ppl' style='margin-top:14px'>" + "<i></i>" * 8 + "</div>", 56, 420, t + 1.6, to))
mach = "".join(f"<i data-pop='{t + 2.4 + k * 0.035:.2f}' style='--c:{[CYAN, MINT, VIOLET, AMBER][k % 4]}'></i>" for k in range(60))
els.append(A("<div class='kick'>Service accounts, keys, tokens, agents</div><div class='mach' style='margin-top:14px'>" + mach + "</div>", 330, 420, t + 2.2, to, w=700))
els.append(CAP("Many have no owner. Some never expire. I tested where the controls around them stop.", t + 4.6, to - 0.1))

# ---------------------------------------------------------------- 1. the framework loop
t = S["loop"]; to = S["method"]
els += [A("<div class='kick'>The framework</div>", 56, 118, t + 0.2, to),
        A(f"<h2>Seven steps hold all <em>{N}</em> cases</h2>", 56, 152, t + 0.4, to, w=960)]
CX, CY, R = 540, 560, 250
pts = []
for i in range(7):
    a = -math.pi / 2 + i * 2 * math.pi / 7
    pts.append((CX + R * math.cos(a), CY + R * math.sin(a)))
ring = (f"<svg width='1080' height='1080' viewBox='0 0 1080 1080'><circle cx='{CX}' cy='{CY}' r='{R}' fill='none' stroke='#2b3658' stroke-width='4' stroke-dasharray='8 12'/>"
        f"<circle id='ringfill' cx='{CX}' cy='{CY}' r='{R}' fill='none' stroke='#4de2ff' stroke-width='5' stroke-linecap='round' transform='rotate(-90 {CX} {CY})' "
        f"stroke-dasharray='{2 * math.pi * R:.1f}' stroke-dashoffset='{2 * math.pi * R:.1f}' data-draw-in='{t + 1.2}' data-draw-dur='12' opacity='.7'/></svg>")
els.append(A(ring, 0, 0, t + 0.8, to, fx="fade"))
for i, (key, name, desc) in enumerate(STAGES):
    x, y = pts[i]; ti = t + 1.2 + i * 1.7
    els.append(A(f"<div class='nd' style='--c:{STEP_COL[i]}'><b data-count='{STEPS[STEP_ORDER[i]]}' data-count-in='{ti + 0.2}'>0</b><span>{i + 1}. {name}</span></div>", x - 88, y - 54, ti, to, fx="pop"))
els.append(A(f"<div style='text-align:center'><b style='display:block;font-size:84px;font-weight:800;color:#fff;line-height:1' data-count='{N}' data-count-in='{t + 13.4}'>0</b><span style='font-size:26px;color:#b7c4df'>cases</span></div>", CX - 120, CY - 60, t + 13.2, to, w=240, fx="pop"))
loopkeys = [(t + 1.2 + i * 1.7, pts[i][0], pts[i][1]) for i in range(7)] + [(t + 1.2 + 7 * 1.7, pts[0][0], pts[0][1])]
els.append(PK(loopkeys, CYAN))
for i, (key, name, desc) in enumerate(STAGES):
    ti = t + 1.2 + i * 1.7
    els.append(CAP(f"<span><b style='color:{STEP_COL[i]}'>{i + 1}. {name}.</b> {desc}.</span>", ti + 0.1, ti + 1.7 if i < 6 else t + 13.2))
els.append(CAP("Retiring what is unused feeds the next discovery scan, so it is a loop.", t + 13.3, to - 0.1))

# ---------------------------------------------------------------- 2. the method
t = S["method"]; to = S["ci"]
els += [A("<div class='kick'>The method</div>", 56, 118, t + 0.2, to),
        A("<h2>The guess comes <em>first</em></h2>", 56, 152, t + 0.4, to, w=960)]
M = [("Write the guess", "What I expect, before any code", CYAN), ("Hash it", "SHA-256 of the guess file", CYAN),
     ("Commit it alone", "So it cannot change later", CYAN), ("Write the code", "A small model of each control", GREEN),
     ("Run it twice", "Control off, then on", GREEN), ("Switch each control off alone", "Does anything notice?", AMBER)]
for i, (h, d, c) in enumerate(M):
    ti = t + 1.0 + i * 1.5
    els.append(A(f"<div class='step' style='--c:{c}'><u>{i + 1}</u><div><b>{h}</b><small>{d}</small></div></div>", 56, 248 + i * 84, ti, to, w=960, h=76, fx="left"))
    if i:
        els.append(LN(89, 248 + i * 84 - 14, 4, 20, c, ti, to))
els.append(A("<div class='log' style='--c:#4de2ff'><b>a2dc1fd</b>&nbsp; guesses only</div>", 56, 770, t + 10.4, to, w=470, fx="left"))
els.append(A("<div class='log' style='--c:#34d399'><b>cbec7a8</b>&nbsp; code and results</div>", 550, 770, t + 11.6, to, w=474, fx="left"))
els.append(CAP("I wrote every guess down and committed it before any code existed. Here is the order for the last run, from git.", t + 0.6, t + 10.2))
els.append(CAP("Every run was repeated on a second machine. The output matched.", t + 10.3, to - 0.1))

# ---------------------------------------------------------------- 3. workflow 1: CI token replay
t = S["ci"]; to = S["vendor"]
els += [A("<div class='kick' style='--c:#f7c873'>Workflow 1 &middot; case N-R14-25</div>", 56, 118, t + 0.2, to),
        A("<h2>A token copied from a CI runner</h2>", 56, 152, t + 0.4, to, w=980)]
# lane without
yA, yB = 262, 560
els.append(A("<div class='lane' style='--c:#ff7a93'>Without the controls</div>", 56, yA, t + 1.0, to))
els += [A("<div class='chip' style='--c:#93a1bd'>Pipeline job</div>", 56, yA + 40, t + 1.2, to, w=230, h=86, fx="pop"),
        A("<div class='chip' style='--c:#ff7a93'>Token copied</div>", 330, yA + 40, t + 2.0, to, w=230, h=86, fx="pop"),
        A("<div class='chip' style='--c:#ff7a93'>Replayed twice</div>", 604, yA + 40, t + 2.8, to, w=230, h=86, fx="pop"),
        A("<div class='res' style='--c:#ff7a93'>Both work</div>", 870, yA + 40, t + 4.4, to, w=154, h=86, fx="pop"),
        LN(286, yA + 82, 44, 4, PINK, t + 1.8, to), LN(560, yA + 82, 44, 4, PINK, t + 2.6, to), LN(834, yA + 82, 36, 4, PINK, t + 3.6, to)]
els.append(PK([(t + 3.0, 720, yA + 83), (t + 4.3, 946, yA + 83)], PINK))
els.append(PK([(t + 3.5, 720, yA + 83), (t + 4.8, 946, yA + 83)], PINK))
# lane with
els.append(A("<div class='lane' style='--c:#34d399'>With the controls</div>", 56, yB - 120, t + 5.6, to))
els += [A("<div class='chip' style='--c:#34d399'>Bound to its runner</div>", 56, yB - 80, t + 5.8, to, w=230, h=86, fx="pop"),
        A("<div class='chip' style='--c:#34d399'>Revoked at job end</div>", 330, yB - 80, t + 6.6, to, w=230, h=86, fx="pop"),
        A("<div class='chip' style='--c:#93a1bd'>Replayed twice</div>", 604, yB - 80, t + 7.4, to, w=230, h=86, fx="pop"),
        A("<div class='res' style='--c:#34d399'>Both refused</div>", 870, yB - 80, t + 9.0, to, w=154, h=86, fx="pop"),
        LN(286, yB - 38, 44, 4, GREEN, t + 6.4, to), LN(560, yB - 38, 44, 4, GREEN, t + 7.2, to), LN(834, yB - 38, 36, 4, GREEN, t + 8.2, to)]
els.append(PK([(t + 7.6, 720, yB - 37), (t + 8.6, 846, yB - 37), (t + 9.0, 760, yB - 37)], GREEN))
# switch-off check
els.append(A("<div class='kick' style='--c:#f7c873'>Now switch each control off, alone</div>", 56, 640, t + 10.6, to))
els.append(SW("10 minute token lifetime", 56, 690, t + 11.0, to, [(0, True), (t + 12.6, False)]))
els.append(A("<div class='res' style='--c:#f7c873;font-size:25px'>Result: no change. Both still refused.</div>", 520, 680, t + 13.4, to, w=504, h=64, fx="pop"))
els.append(A("<p style='font-size:28px;line-height:1.3'><b style='color:#fff'>My guess was wrong here.</b> I expected the lifetime to matter. Binding and revocation had already stopped both replays.</p>", 56, 764, t + 14.6, to, w=968))
els.append(CAP("Same attack, run twice: once with the controls off, once with them on.", t + 0.8, t + 10.4))
els.append(CAP("The limit that stayed: a bound token still works from inside the runner while the job runs.", t + 17.0, to - 0.1))

# ---------------------------------------------------------------- 4. workflow 2: vendor breach, OAuth
t = S["vendor"]; to = S["arch"]
els += [A("<div class='kick' style='--c:#f7c873'>Workflow 2 &middot; case N-R14-23</div>", 56, 118, t + 0.2, to),
        A("<h2>A connected vendor is breached</h2>", 56, 152, t + 0.4, to, w=980)]
els.append(A("<p style='font-size:28px'>An AI office app was linked with \"allow all\". The attacker replays its refresh token. The vendor tells you at minute 0.</p>", 56, 236, t + 0.8, to, w=968))
els.append(SW("Only allowlisted apps can be granted", 56, 340, t + 2.0, to, [(0, False), (t + 14.8, True)], w=960))
els.append(SW("Revoke within 60 minutes of the notice", 56, 398, t + 2.4, to, [(0, False), (t + 9.6, True), (t + 16.6, False)], w=960))
# timeline
TX0, TX1, TY = 120, 960, 610
els.append(LN(TX0, TY, TX1 - TX0, 4, "#3a4769", t + 3.0, to))
for m, lab in [(0, "minute 0"), (30, "minute 30"), (60, "minute 60"), (90, "minute 90")]:
    x = TX0 + (TX1 - TX0) * m / 90
    els.append(A(f"<div class='clock' style='text-align:center'>{lab}</div>", x - 80, TY + 18, t + 3.2, to, w=160, fx="fade"))
    els.append(LN(x - 2, TY - 10, 4, 24, "#3a4769", t + 3.2, to))
x30, x90 = TX0 + (TX1 - TX0) / 3, TX1
# phase A: both off
els.append(A("<div class='res' style='--c:#ff7a93'>Reads files</div>", x30 - 90, TY - 110, t + 4.6, t + 9.4, w=180, h=70, fx="pop"))
els.append(A("<div class='res' style='--c:#ff7a93'>Reads files</div>", x90 - 150, TY - 110, t + 5.6, t + 9.4, w=180, h=70, fx="pop"))
els.append(PK([(t + 3.8, TX0, TY + 2), (t + 4.6, x30, TY + 2), (t + 5.6, x90, TY + 2)], PINK))
els.append(CAP("Both controls off: the replay reads files at minute 30 and still at minute 90.", t + 3.0, t + 9.4))
# phase B: revoke only
els.append(A("<div class='kick' style='--c:#93a1bd'>Revoke on, allowlist off</div>", 56, 680, t + 9.6, t + 14.6))
els.append(A("<div class='res' style='--c:#ff7a93'>Reads files</div>", x30 - 90, TY - 110, t + 10.6, t + 14.6, w=180, h=70, fx="pop"))
els.append(A("<div class='res' style='--c:#34d399'>Refused</div>", x90 - 150, TY - 110, t + 11.6, t + 14.6, w=180, h=70, fx="pop"))
els.append(PK([(t + 9.8, TX0, TY + 2), (t + 10.6, x30, TY + 2), (t + 11.6, x90, TY + 2)], AMBER))
els.append(CAP("With only the revoke, the attacker still has an hour. The clock starts at the vendor's notice.", t + 9.5, t + 14.6))
# phase C: allowlist on
els.append(A("<div class='kick' style='--c:#93a1bd'>Allowlist on</div>", 56, 680, t + 14.8, to))
els.append(A("<div class='res' style='--c:#34d399;font-size:30px'>Grant refused at consent. Nothing to replay.</div>", 120, TY - 120, t + 15.4, to, w=840, h=80, fx="pop"))
els.append(A("<p style='font-size:28px;line-height:1.3'>Now switch the revoke off: <b style='color:#fff'>nothing changes.</b> The allowlist hides it. A one-at-a-time test says the revoke did nothing, yet it is the only thing left on the day the allowlist is wrong.</p>", 56, 716, t + 16.6, to, w=968))
els.append(CAP("Layered controls hide each other. That is why I switched every control off on its own.", t + 14.7, to - 0.1))

# ---------------------------------------------------------------- 5. the architecture
t = S["arch"]; to = S["data"]
els += [A("<div class='kick'>How the lab is built</div>", 56, 118, t + 0.2, to),
        A("<h2>One reader, three outputs</h2>", 56, 152, t + 0.4, to, w=980)]
a0 = t + 1.0
els += [BOX(56, 250, 440, 120, CYAN, "Evidence", "guesses/", f"{len(FILES)} hashed guess files", a0, to),
        BOX(584, 250, 440, 120, MINT, "Check", "verify.py", f"Re-checks the {len(FILES)} hashes", a0 + 1.2, to),
        BOX(56, 410, 440, 120, GREEN, "Code", "run.py to run4.py", "Small models of each control", a0 + 2.4, to),
        BOX(584, 410, 440, 120, GREEN, "Evidence", "results", "4 JSON files, one per run", a0 + 3.6, to),
        BOX(56, 572, 968, 110, VIOLET, "Shared", "nhi_data.py", "One reader for the guesses and the results", a0 + 5.0, to),
        BOX(56, 724, 300, 120, AMBER, "Output", "Lab pages", f"{N} animated cases", a0 + 6.6, to),
        BOX(390, 724, 300, 120, AMBER, "Output", "Audit data", "CSV and JSON", a0 + 7.2, to),
        BOX(724, 724, 300, 120, AMBER, "Output", "PDF book", "83 pages", a0 + 7.8, to)]
els += [LN(496, 308, 88, 4, MINT, a0 + 1.4, to), LN(496, 468, 88, 4, GREEN, a0 + 3.8, to),
        LN(30, 308, 26, 4, CYAN, a0 + 5.1, to), LN(28, 308, 4, 320, CYAN, a0 + 5.2, to), LN(28, 626, 28, 4, CYAN, a0 + 5.3, to),
        LN(802, 530, 4, 42, GREEN, a0 + 5.2, to),
        LN(204, 682, 4, 42, AMBER, a0 + 6.8, to), LN(538, 682, 4, 42, AMBER, a0 + 7.4, to), LN(872, 682, 4, 42, AMBER, a0 + 8.0, to)]
els.append(PK([(a0 + 3.8, 496, 470), (a0 + 4.6, 584, 470), (a0 + 5.4, 804, 530), (a0 + 6.0, 804, 572), (a0 + 6.6, 540, 627), (a0 + 7.2, 540, 682), (a0 + 7.8, 540, 724), (a0 + 8.2, 540, 724)], GREEN))
els.append(PK([(a0 + 5.3, 30, 310), (a0 + 6.0, 30, 628), (a0 + 6.6, 56, 628)], CYAN))
els.append(CAP("Pages, audit files and the book all come from one reader. A check fails the build on any number the data does not hold.", t + 0.8, to - 0.1))

# ---------------------------------------------------------------- 6. the results
t = S["data"]; to = S["end"]
els += [A("<div class='kick'>What the data says</div>", 56, 118, t + 0.2, to),
        A("<h2>Where my guesses were wrong</h2>", 56, 152, t + 0.4, t + 8.2, w=980)]
GX, GY, CELL = 56, 246, 69
for i in range(N):
    r, c = divmod(i, 14)
    ti = t + 1.0 + i * 0.03
    fill = MINT if MATCH[i] else PINK
    ring = f"box-shadow:0 0 0 4px {AMBER};" if MASKED[i] else ""
    els.append(f"<div class='dot' data-in='{ti:.2f}' data-out='{t + 8.2}' style='left:{GX + c * CELL + 7}px;top:{GY + r * CELL + 7}px;background:{fill};{ring}'></div>")
els.append(A(f"<span class='leg'><i style='background:{MINT}'></i>matched</span><span class='leg'><i style='background:{PINK}'></i>wrong</span><span class='leg'><i style='box-shadow:0 0 0 4px {AMBER}'></i>a control no check noticed</span>", 58, 610, t + 3.4, t + 8.2, w=980))
els.append(A("<div class='miss'>The secret scan missed 2 of 8 fake secrets. I guessed 1.</div>", 56, 670, t + 4.2, t + 8.2, w=968, h=72))
els.append(A("<div class='miss'>5 alerts, not 4. I never wrote down what I was counting.</div>", 56, 756, t + 5.2, t + 8.2, w=968, h=72))
els.append(CAP(f"{sum(MATCH)} guesses matched and {len(WRONG)} did not. All {len(WRONG)} stay on the page.", t + 0.8, t + 8.2))
TL = [(N, "cases run", CYAN), (sum(MATCH), "guesses matched", MINT), (len(WRONG), "guesses wrong", PINK),
      (CONTROLS, "controls switched off, one at a time", VIOLET), (sum(MASKED), "cases where no check noticed", AMBER), (LIMITS, "cases with a recorded limit", LILAC)]
els.append(A("<h2>The totals</h2>", 56, 152, t + 8.4, to, w=980))
for i, (v, s_, c) in enumerate(TL):
    x = 56 + (i % 2) * 492; y = 246 + (i // 2) * 204; t0 = t + 8.6 + i * 0.6
    els.append(A(f"<div class='tile' style='--c:{c}'><b data-count='{v}' data-count-in='{t0 + 0.1}'>0</b><span>{s_}</span></div>", x, y, t0, to, w=476, h=186, fx="pop"))
els.append(CAP("I wrote both the guesses and the code, so a match proves little. The misses and the limits are the useful part.", t + 8.3, to - 0.1))

# ---------------------------------------------------------------- 7. end
t = S["end"]
els += [A("<h2 style='font-size:80px'>Free and public</h2>", 56, 220, t + 0.3, DUR + 1, w=968),
        A("<div class='url'>roshantrivedi.co.in/nhi-lab</div>", 56, 370, t + 0.9, DUR + 1, w=990),
        A(f"<p style='font-size:36px'>{N} cases with animated workflows, the framework, the audit data, the guess files and an 83 page book.</p>", 56, 500, t + 1.6, DUR + 1, w=968),
        A("<p style='font-size:28px;color:#93a1bd'>Made-up data only. Small models, written by the same person who wrote the guesses. No product was tested.</p>", 56, 720, t + 2.6, DUR + 1, w=968)]

dots = "".join(f"<i data-on='{S[k]},{[S[x] for x, _ in SCENES][j + 1] if j + 1 < len(SCENES) else S['end']}'></i>" for j, (k, _) in enumerate(SCENES))
HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bg' id='bg'></div><div class='gridbg'></div><div class='eye'>Non-human identity lab</div><div class='who'>Roshan Trivedi</div><div class='dots'>{dots}</div>
{''.join(els)}
<div class='foot'><b>roshantrivedi.co.in/nhi-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
function back(x){{x=x<0?0:x>1?1:x;var c=1.5;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}}
function lin(x){{return x<0?0:x>1?1:x}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.8),b=1-ease((t-(o-0.55))/0.55),fx=e.dataset.fx;
  var v=t>=i&&t<o?Math.min(a,b):0; e.style.opacity=v;
  if(fx==='pop'){{var s=0.86+0.14*back((t-i)/0.7);e.style.transform='scale('+s+')'}}
  else if(fx==='left'){{e.style.transform='translateX('+((1-a)*-40)+'px)'}}
  else if(fx==='fade'){{e.style.transform='none'}}
  else {{e.style.transform='translateY('+((1-a)*28)+'px)'}}
 }});
 document.querySelectorAll('.ln').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.6),b=1-ease((t-(o-0.55))/0.55);
  e.style.opacity=t>=i&&t<o?Math.min(1,b)*0.9:0;
  e.style.transformOrigin=e.dataset.dir==='x'?'left center':'center top';
  e.style.transform=e.dataset.dir==='x'?'scaleX('+a+')':'scaleY('+a+')';
 }});
 document.querySelectorAll('[data-pop]').forEach(function(e){{
  var a=ease((t-(+e.dataset.pop))/0.35);e.style.opacity=a;e.style.transform='scale('+(0.4+0.6*a)+')';
 }});
 document.querySelectorAll('.dot').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.4),b=1-ease((t-(o-0.55))/0.55);
  e.style.opacity=t>=i&&t<o?Math.min(a,b):0; e.style.transform='scale('+(0.5+0.5*back((t-i)/0.5))+')';
 }});
 document.querySelectorAll('[data-count]').forEach(function(e){{
  e.textContent=Math.round(+e.dataset.count*ease((t-(+e.dataset.countIn))/1.3));
 }});
 document.querySelectorAll('[data-flips]').forEach(function(e){{
  var f=JSON.parse(e.dataset.flips),on=f[0][1];for(var q=0;q<f.length;q++)if(t>=f[q][0])on=f[q][1];
  if(on) e.classList.remove('off'); else e.classList.add('off');
 }});
 var rf=document.getElementById('ringfill'); if(rf){{var L=+rf.getAttribute('stroke-dasharray');
  rf.setAttribute('stroke-dashoffset',L*(1-lin((t-(+rf.dataset.drawIn))/(+rf.dataset.drawDur))));}}
 document.querySelectorAll('.pk').forEach(function(e){{
  var k=JSON.parse(e.dataset.keys),n=k.length;
  if(t<k[0][0]||t>k[n-1][0]+0.3){{e.style.opacity=0;return}}
  var j=0;while(j<n-2&&t>k[j+1][0])j++;
  var u=lin((t-k[j][0])/(k[j+1][0]-k[j][0]||1));u=u*u*(3-2*u);
  e.style.left=(k[j][1]+(k[j+1][1]-k[j][1])*u)+'px';e.style.top=(k[j][2]+(k[j+1][2]-k[j][2])*u)+'px';
  e.style.opacity=Math.max(0,Math.min(1,(t-k[0][0])/0.3,(k[n-1][0]+0.3-t)/0.3));
 }});
 document.querySelectorAll('.dots i').forEach(function(e){{
  var r=e.dataset.on.split(',');var on=t>=+r[0]&&t<+r[1];e.style.background=on?'#4de2ff':(t>=+r[1]?'#3a6f8f':'#26314d');
 }});
 document.getElementById('bg').style.transform='translate('+(Math.sin(t/9)*30)+'px,'+(Math.cos(t/11)*24)+'px)';
 document.getElementById('prog').style.width=(1080*t/{DUR})+'px';
}};
</script></body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    work = os.path.abspath(os.path.join(ROOT, "..", "nhi-linkedin-frames")); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    page = os.path.join(ROOT, "assets", "_nhi_square.html"); open(page, "w").write(HTML)

    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_nhi_square.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
            only = os.environ.get("ONLY")
            frames = [int(x) for x in only.split(",")] if only else range(int(DUR * FPS))
            for n in frames:
                pg.evaluate(f"render({n / FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    if os.environ.get("ONLY"): print("frames in", work); return
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(work, "f%05d.png"),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT])
    print(OUT, os.path.getsize(OUT))


main()
