#!/usr/bin/env python3
"""Draws the images for the long-form NHI lab article (cover 1920x1080, figures 1600x900, saved at 1.5x).
Every number is read from nhi-lab/audit/nhi-lab-audit.json and checked. Run from the repo root.
Output: assets/share/article/*.png"""
import os, sys, json, collections, http.server, socketserver, threading, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "share", "article")
PORT = 8775
AUD = json.load(open(os.path.join(ROOT, "nhi-lab/audit/nhi-lab-audit.json")))
ROWS = AUD["rows"]; N = len(ROWS)
MATCH = [r["guess_matched"] == "yes" for r in ROWS]
WRONG = [r for r in ROWS if r["guess_matched"] != "yes"]
MASKED = [bool(r["controls_not_noticed"]) for r in ROWS]
LIMITS = sum(1 for r in ROWS if r["limit"])
CONTROLS = sum(r["controls_checked"] for r in ROWS)
STEP_ORDER = ["Find", "Own", "Limit", "Store and issue", "Rotate and expire", "Watch", "Retire and respond"]
STEPS = collections.Counter(r["framework_step"] for r in ROWS)
FILES = {r["guess_file"] for r in ROWS}
BY = {r["id"]: r for r in ROWS}
assert (N, sum(MATCH), len(WRONG), sum(MASKED), LIMITS, CONTROLS) == (67, 57, 10, 20, 33, 133)
assert [STEPS[s] for s in STEP_ORDER] == [6, 8, 18, 10, 10, 7, 8] and len(FILES) == 6
ci = BY["N-R14-25"]
assert ci["without_control"] == "Both replays work" and ci["with_control"] == "Both replays refused" and ci["controls_not_noticed"] == "short_ttl"
assert BY["N-R14-06"]["controls_not_noticed"] == "weekly_sweep auto_expiry"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from nhi_data import STAGES  # noqa: E402

C = dict(cyan="#4de2ff", mint="#7df2d0", green="#34d399", amber="#f7c873", pink="#ff7a93", violet="#a78bfa", lilac="#c4b5fd")
STEP_COL = ["#4de2ff", "#7df2d0", "#f7c873", "#c4b5fd", "#34d399", "#ff8fa3", "#a78bfa"]
FONT = "".join(f"@font-face{{font-family:'DM Sans';font-weight:{w};src:url(/assets/{f})}}" for w, f in [
    (400, "dm-sans-latin-400-normal-CW0RaeGs.woff2"), (500, "dm-sans-latin-500-normal-B9HHJjqV.woff2"),
    (600, "dm-sans-latin-600-normal-Aqo67rzb.woff2"), (700, "dm-sans-latin-700-normal-DvUfVpUG.woff2"), (800, "dm-sans-latin-800-normal.woff2")]) + \
    "@font-face{font-family:'JB';font-weight:600;src:url(/assets/jetbrains-mono-latin-semibold.woff2)}"
BASE = FONT + """
*{box-sizing:border-box;margin:0}
body{width:var(--w);height:var(--h);overflow:hidden;position:relative;background:#06071c;color:#e8eefc;font-family:'DM Sans',sans-serif}
.bg{position:absolute;inset:0;background:radial-gradient(900px 640px at 92% 8%,rgba(77,226,255,.13),transparent 70%),radial-gradient(800px 640px at 0% 100%,rgba(139,92,246,.16),transparent 70%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(167,139,250,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(167,139,250,.06) 1px,transparent 1px);background-size:48px 48px;mask-image:radial-gradient(circle at 50% 40%,#000,transparent 80%)}
.wrap{position:absolute;inset:64px 72px 56px 72px;display:flex;flex-direction:column}
.k{font-weight:700;font-size:20px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}
.k span{color:#93a1bd}
h1{font-weight:800;font-size:52px;line-height:1.08;color:#fff;letter-spacing:-.01em;margin-top:12px;max-width:1300px}
h1 em{font-style:normal;color:#4de2ff}
.sub{font-size:25px;line-height:1.35;color:#b7c4df;margin-top:12px;max-width:1300px}
.foot{position:absolute;left:72px;right:72px;bottom:26px;display:flex;justify-content:space-between;font-size:18px;color:#7d8aa8}
.foot b{color:#4de2ff;font-weight:700}
.card{border:2px solid var(--c,#26314d);border-radius:20px;background:rgba(255,255,255,.04);box-shadow:0 0 40px -18px var(--c,transparent)}
.mono{font-family:'JB',ui-monospace,monospace}
"""


def page(w, h, body, css=""):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>:root{{--w:{w}px;--h:{h}px}}{BASE}{css}</style></head><body><div class='bg'></div><div class='grid'></div>{body}</body></html>"


def foot(fig):
    return f"<div class='foot'><span>{fig}</span><span><b>roshantrivedi.co.in/nhi-lab</b> &middot; made-up data only</span></div>"


IMGS = {}

# ---------------------------------------------------------------- cover
sq = "".join(f"<i style='background:{C['mint'] if MATCH[i] else C['pink']};{'box-shadow:0 0 0 4px ' + C['amber'] + ';' if MASKED[i] else ''}'></i>" for i in range(N))
IMGS["00-cover"] = (1920, 1080, page(1920, 1080, f"""
<div class='wrap' style='inset:96px 110px 80px 110px'>
 <div class='k'>Non-human identity lab <span>&middot; Roshan Trivedi</span></div>
 <h1 style='font-size:92px;max-width:1040px;margin-top:26px'>I tested <em>{N}</em> machine identity cases.</h1>
 <p class='sub' style='font-size:38px;max-width:980px;margin-top:22px;color:#dfe6f7'>I wrote every guess down before any code ran. Here is where the controls stopped.</p>
 <div style='display:flex;gap:18px;margin-top:auto'>
  {''.join(f"<div class='chip' style='--c:{c}'><b>{v}</b>{t}</div>" for v, t, c in [(sum(MATCH), 'guesses matched', C['mint']), (len(WRONG), 'guesses wrong', C['pink']), (sum(MASKED), 'cases where no check noticed', C['amber'])])}
 </div>
</div>
<div class='sq'>{sq}</div>
<div class='foot' style='left:110px;right:110px;bottom:36px;font-size:22px'><span>Service accounts, tokens, break-glass, vendor access and AI tools</span><span><b>roshantrivedi.co.in/nhi-lab</b></span></div>
""", """
.sq{position:absolute;right:110px;top:150px;width:560px;display:grid;grid-template-columns:repeat(8,1fr);gap:14px}
.sq i{display:block;aspect-ratio:1;border-radius:12px}
.chip{border:2px solid var(--c);border-radius:999px;padding:12px 28px;font-size:26px;color:#dfe6f7;background:rgba(255,255,255,.04);display:flex;gap:12px;align-items:baseline}
.chip b{font-size:40px;font-weight:800;color:var(--c)}
"""))

# ---------------------------------------------------------------- figure 1: method
steps = [("1", "Write the guess", "What I expect to happen, for each case", C["cyan"]),
         ("2", "Hash it", "SHA-256 of the whole guess file", C["cyan"]),
         ("3", "Commit it alone", "Before any code exists", C["cyan"]),
         ("4", "Write the code", "A small model of each control", C["green"]),
         ("5", "Run it twice", "Control off, then on, compared with the guess", C["green"]),
         ("6", "Switch each control off alone", "Does anything the case counts change?", C["amber"])]
st = "".join(f"<div class='st card' style='--c:{c}'><u style='--c:{c}'>{n}</u><b>{h}</b><small>{d}</small></div>" for n, h, d, c in steps)
IMGS["01-method"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 1 <span>&middot; the method</span></div>
 <h1>The guess is committed before the code exists</h1>
 <p class='sub'>So it cannot change after the result is known. The order is on record in git.</p>
 <div class='row'>{st}</div>
 <div class='rec'>
  <div class='card' style='--c:#4de2ff;padding:18px 26px'><i>Round 19, on my Mac</i><div class='mono'><span style='color:#4de2ff'>a2dc1fd</span> guesses only <span class='ar'>&rarr;</span> <span style='color:#34d399'>cbec7a8</span> code and results</div></div>
  <div class='card' style='padding:18px 26px'><i>Then</i><div>Every run repeated on a second machine. The output matched.</div></div>
 </div>
</div>{foot('Figure 1')}""", """
.row{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;margin-top:44px}
.st{padding:26px 20px 24px;min-height:330px;position:relative}
.st u{text-decoration:none;display:block;width:58px;height:58px;border-radius:50%;border:3px solid var(--c);color:var(--c);font-weight:800;font-size:28px;line-height:52px;text-align:center;margin-bottom:18px}
.st b{display:block;font-size:30px;line-height:1.12;color:#fff;font-weight:800}
.st small{display:block;font-size:22px;line-height:1.3;color:#b7c4df;margin-top:10px}
.st:not(:last-child)::after{content:'';position:absolute;right:-17px;top:50px;width:18px;height:3px;background:#3a4769}
.rec{display:grid;grid-template-columns:1.6fr 1fr;gap:16px;margin-top:34px;font-size:26px;color:#dfe6f7}
.rec i{display:block;font-style:normal;font-size:16px;letter-spacing:.16em;text-transform:uppercase;color:#93a1bd;font-weight:700;margin-bottom:8px}
.rec .mono{font-size:24px}.ar{color:#93a1bd;margin:0 8px}
"""))

# ---------------------------------------------------------------- figure 2: architecture
def bx(x, y, w, h, c, head, title, sub):
    return f"<div class='bx card' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{c}'><i style='color:{c}'>{head}</i><b>{title}</b><small>{sub}</small></div>"


def ln(x, y, w, h, c):
    return f"<div class='ln' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{c}'></div>"


arch = "".join([
    bx(0, 0, 330, 132, C["cyan"], "Evidence", "guesses/", f"{len(FILES)} guess files, each hashed"),
    bx(0, 176, 330, 132, C["mint"], "Check", "verify.py", f"Re-checks the {len(FILES)} hashes"),
    bx(0, 352, 330, 132, C["green"], "Code", "run.py to run4.py", "Small models of each control"),
    bx(430, 352, 330, 132, C["green"], "Evidence", "results", "4 JSON files, one per run"),
    bx(860, 150, 300, 160, C["violet"], "Shared", "nhi_data.py", "One reader for the guesses and the results"),
    bx(1250, 0, 206, 132, C["amber"], "Output", "Lab pages", f"{N} animated cases"),
    bx(1250, 176, 206, 132, C["amber"], "Output", "Audit data", "CSV and JSON"),
    bx(1250, 352, 206, 132, C["amber"], "Output", "PDF book", "83 pages"),
    ln(163, 132, 4, 44, C["mint"]), ln(330, 418, 100, 4, C["green"]),
    ln(330, 64, 380, 4, C["cyan"]), ln(708, 64, 4, 166, C["cyan"]), ln(708, 228, 152, 4, C["cyan"]),
    ln(760, 418, 250, 4, C["green"]), ln(1008, 310, 4, 112, C["green"]),
    ln(1160, 228, 40, 4, C["amber"]), ln(1198, 64, 4, 356, C["amber"]),
    ln(1198, 64, 52, 4, C["amber"]), ln(1198, 240, 52, 4, C["amber"]), ln(1198, 418, 52, 4, C["amber"]),
    "<div class='lb' style='left:420px;top:30px'>guess files, read only</div>",
    "<div class='lb' style='left:780px;top:384px'>reads results</div>",
    "<div class='lb' style='left:180px;top:140px'>re-checks</div>"])
IMGS["02-architecture"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 2 <span>&middot; how the lab is built</span></div>
 <h1>Evidence in, one reader, three outputs</h1>
 <p class='sub'>The pages, the audit files and the book all read the same data. A check fails the build if a page quotes a number the data does not hold.</p>
 <div class='arch'>{arch}</div>
</div>{foot('Figure 2')}""", """
.arch{position:relative;margin-top:44px;height:490px}
.bx{position:absolute;padding:16px 20px}
.bx i{display:block;font-style:normal;font-weight:800;font-size:16px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px}
.bx b{display:block;font-weight:800;font-size:27px;color:#fff;line-height:1.1}
.bx small{display:block;font-size:19px;line-height:1.25;color:#b7c4df;margin-top:6px}
.ln{position:absolute;border-radius:2px;opacity:.85}
.lb{position:absolute;font-size:18px;color:#93a1bd;background:#06071c;padding:0 8px}
"""))

# ---------------------------------------------------------------- figure 3: framework loop
import math
R, CX, CY = 262, 520, 300
nodes = ""
for i, (key, name, desc) in enumerate(STAGES):
    a = -math.pi / 2 + i * 2 * math.pi / 7
    x, y = CX + R * math.cos(a), CY + R * math.sin(a)
    nodes += f"<div class='nd' style='left:{x - 92:.0f}px;top:{y - 56:.0f}px;--c:{STEP_COL[i]}'><b>{STEPS[STEP_ORDER[i]]}</b><span>{i + 1}. {name}</span></div>"
legend = "".join(f"<li><i style='background:{STEP_COL[i]}'></i><b>{name}</b> {desc}</li>" for i, (k, name, desc) in enumerate(STAGES))
IMGS["03-framework"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 3 <span>&middot; the framework</span></div>
 <h1>Seven steps, from finding an identity to retiring it</h1>
 <p class='sub'>Each of the {N} cases sits at exactly one step. The number is how many cases test that step.</p>
</div>
<svg class='ring' width='1040' height='720' viewBox='0 0 1040 720'><circle cx='{CX}' cy='{CY}' r='{R}' fill='none' stroke='#2b3658' stroke-width='3' stroke-dasharray='6 10'/>
<path d='M {CX + 40} {CY - R - 2} a 6 6 0 0 1 0 0' /></svg>
<div class='loop'>{nodes}<div class='mid'><b>{N}</b><span>cases</span><small>Retiring what is unused feeds the next discovery scan</small></div></div>
<ul class='leg'>{legend}</ul>
{foot('Figure 3')}""", """
.ring{position:absolute;left:0;top:262px}
.loop{position:absolute;left:0;top:262px;width:1040px;height:720px}
.nd{position:absolute;width:184px;height:112px;border:3px solid var(--c);border-radius:22px;background:#0b0d29;text-align:center;padding-top:10px;box-shadow:0 0 36px -14px var(--c)}
.nd b{display:block;font-size:42px;font-weight:800;color:var(--c);line-height:1}
.nd span{display:block;font-size:19px;font-weight:700;color:#fff;margin-top:8px;line-height:1.1}
.mid{position:absolute;left:400px;top:200px;width:240px;text-align:center}
.mid b{display:block;font-size:86px;font-weight:800;color:#fff;line-height:1}
.mid span{display:block;font-size:24px;color:#b7c4df}
.mid small{display:block;font-size:17px;color:#93a1bd;margin-top:14px;line-height:1.3}
.leg{position:absolute;left:1000px;top:280px;width:540px;list-style:none;padding:0}
.leg li{font-size:19px;line-height:1.3;color:#b7c4df;margin-bottom:16px;padding-left:34px;position:relative}
.leg li i{position:absolute;left:0;top:4px;width:20px;height:20px;border-radius:6px}
.leg li b{color:#fff;display:block;font-size:21px}
"""))

# ---------------------------------------------------------------- figure 4: one case as a workflow
def lane(title, col, steps_, end, endcol):
    s = "".join(f"<div class='ws'>{t}</div><div class='wa' style='background:{col}'></div>" for t in steps_)
    return f"<div class='lane' style='--c:{col}'><div class='lt'>{title}</div><div class='wf'>{s}<div class='we' style='--c:{endcol}'>{end}</div></div></div>"


IMGS["04-workflow"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 4 <span>&middot; one case, as a workflow</span></div>
 <h1>A token copied from a CI runner, then replayed</h1>
 <p class='sub'>Case {ci['id']}. The same attack runs twice: once with the controls off, once with them on.</p>
 {lane('Without the controls', C['pink'], ['Pipeline job runs', 'Token copied from the runner', 'Replayed from outside, twice'], 'Both replays work', C['pink'])}
 {lane('With the controls', C['green'], ['Token bound to that runner', 'Revoked when the job ends', 'Replayed from outside, twice'], 'Both replays refused', C['green'])}
 <div class='notes'>
  <div class='card' style='--c:{C['amber']};padding:18px 24px'><i style='color:{C['amber']}'>My wrong guess</i>I expected a 10 minute token lifetime to change the result. It changed nothing: binding and revocation had already stopped both replays.</div>
  <div class='card' style='--c:{C['lilac']};padding:18px 24px'><i style='color:{C['lilac']}'>The limit that stayed</i>A bound token still works from inside the runner while the job is running.</div>
 </div>
</div>{foot('Figure 4')}""", """
.lane{margin-top:30px}
.lt{font-weight:800;font-size:19px;letter-spacing:.14em;text-transform:uppercase;color:var(--c);margin-bottom:12px}
.wf{display:flex;align-items:center}
.ws{flex:0 0 300px;height:92px;border:2px solid #2b3658;border-radius:16px;background:rgba(255,255,255,.04);display:flex;align-items:center;padding:0 22px;font-size:24px;font-weight:600;color:#fff;line-height:1.15}
.wa{flex:0 0 40px;height:4px;border-radius:2px;position:relative}
.wa::after{content:'';position:absolute;right:-2px;top:-7px;border:9px solid transparent;border-left:12px solid;border-left-color:inherit;border-right:0;border-left-color:var(--c)}
.we{flex:1;height:92px;border:3px solid var(--c);border-radius:16px;background:rgba(255,255,255,.05);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:800;color:var(--c);box-shadow:0 0 40px -14px var(--c)}
.notes{display:grid;grid-template-columns:1.3fr 1fr;gap:18px;margin-top:34px;font-size:22px;line-height:1.35;color:#dfe6f7}
.notes i{display:block;font-style:normal;font-weight:800;font-size:16px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:8px}
"""))

# ---------------------------------------------------------------- figure 5: results
cells = "".join(f"<i style='background:{C['mint'] if MATCH[i] else C['pink']};{'box-shadow:0 0 0 4px ' + C['amber'] + ';' if MASKED[i] else ''}'></i>" for i in range(N))
tiles = "".join(f"<div class='tl card'><b style='color:{c}'>{v}</b><span>{t}</span></div>" for v, t, c in [
    (sum(MATCH), "guesses matched", C["mint"]), (len(WRONG), "guesses wrong", C["pink"]),
    (CONTROLS, "controls switched off, one at a time", C["violet"]), (sum(MASKED), "cases where one control changed nothing", C["amber"]),
    (LIMITS, "cases with a limit I could not test away", C["lilac"]), (len(FILES), "guess files, each hashed before the code", C["cyan"])])
IMGS["05-results"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 5 <span>&middot; the results</span></div>
 <h1>{sum(MATCH)} guesses matched. {len(WRONG)} did not, and they stay on the page.</h1>
 <div class='res'>
  <div><div class='cells'>{cells}</div>
   <div class='lg'><span><i style='background:{C['mint']}'></i>guess matched</span><span><i style='background:{C['pink']}'></i>guess wrong</span><span><i style='box-shadow:0 0 0 4px {C['amber']}'></i>a control no check noticed</span></div></div>
  <div class='tiles'>{tiles}</div>
 </div>
</div>{foot('Figure 5 &middot; each square is one case, in the order they ran')}""", """
.res{display:grid;grid-template-columns:690px 1fr;gap:40px;margin-top:36px}
.cells{display:grid;grid-template-columns:repeat(10,1fr);gap:12px}
.cells i{display:block;aspect-ratio:1;border-radius:10px}
.lg{display:flex;gap:26px;margin-top:22px;font-size:19px;color:#b7c4df}
.lg i{display:inline-block;width:20px;height:20px;border-radius:6px;vertical-align:-4px;margin-right:10px}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.tl{padding:18px 22px;height:150px}
.tl b{display:block;font-size:58px;font-weight:800;line-height:1}
.tl span{display:block;font-size:19px;line-height:1.25;color:#c4cfe6;margin-top:8px}
"""))

# ---------------------------------------------------------------- figure 6: controls nobody would miss
IMGS["06-nobody-would-miss"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 6 <span>&middot; switching controls off</span></div>
 <h1>When switching a control off changes nothing</h1>
 <p class='sub'>{CONTROLS} controls switched off, one at a time. In {sum(MASKED)} cases at least one changed nothing the case counts. There are two reasons, and they mean different things.</p>
 <div class='two'>
  <div class='card col' style='--c:{C['amber']}'><i style='color:{C['amber']}'>Another control already does the job</i>
   <div class='flow v'><div class='f'>3 accounts made in the cloud console</div><div class='dn'></div><div class='f hit'>The cloud policy refuses them</div><div class='dn'></div><div class='f dim'>The weekly sweep has nothing left to find</div></div>
   <p>The sweep is a second line of defence. A test that only looks at the outcome cannot see it.</p></div>
  <div class='card col' style='--c:{C['lilac']}'><i style='color:{C['lilac']}'>The control is not an access outcome</i>
   <div class='flow g'><div class='f'>A log of every elevation</div><div class='f'>A review of a feature's scope</div><div class='f'>A person approving each change</div><div class='f'>A volume threshold the copy stays under</div></div>
   <p>A model that counts who got in cannot measure these. They still matter for evidence and for whoever investigates later.</p></div>
 </div>
</div>{foot('Figure 6 &middot; examples from cases N-R14-06, P-R15-23, S-R17-07, N-R14-12 and P-R15-24')}""", """
.two{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:40px}
.col{padding:26px 28px}
.col>i{display:block;font-style:normal;font-weight:800;font-size:18px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:22px}
.flow{display:flex;flex-wrap:wrap;align-items:center;gap:12px;min-height:150px}
.f{border:2px solid #2b3658;border-radius:14px;padding:16px 18px;font-size:22px;font-weight:700;color:#fff;background:rgba(255,255,255,.04)}
.f.hit{border-color:#34d399;color:#7df2d0}.f.dim{opacity:.55;border-style:dashed}
.flow.v{flex-direction:column;align-items:stretch;gap:0}.dn{width:3px;height:26px;background:#3a4769;margin-left:40px}.flow.g{display:grid;grid-template-columns:1fr 1fr;gap:12px}.flow.g .f{font-size:21px}
.col p{font-size:24px;line-height:1.4;color:#c4cfe6;margin-top:22px}
"""))

# ---------------------------------------------------------------- figure 7: limits
LIM = [("A made-up ticket number passes the break-glass review", "Nothing checks it against the ticket system.", C["pink"]),
       ("An allowlisted app that is later breached keeps working", "Until someone revokes it. The clock starts at the vendor's notice.", C["amber"]),
       ("A bound CI token still works from inside the runner", "While the job is running, binding does not help.", C["lilac"])]
IMGS["07-limits"] = (1600, 900, page(1600, 900, f"""
<div class='wrap'>
 <div class='k'>Figure 7 <span>&middot; limits that stayed</span></div>
 <h1>{LIMITS} cases carry a limit I could not test away</h1>
 <p class='sub'>Three I would check first in a real environment.</p>
 <div class='lims'>{''.join(f"<div class='card lm' style='--c:{c}'><u style='background:{c}'>{i + 1}</u><b>{t}</b><span>{d}</span></div>" for i, (t, d, c) in enumerate(LIM))}</div>
</div>{foot('Figure 7')}""", """
.lims{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:48px}
.lm{padding:30px 30px 32px;min-height:440px}
.lm u{text-decoration:none;display:block;width:56px;height:56px;border-radius:16px;color:#06071c;font-weight:800;font-size:30px;line-height:56px;text-align:center;margin-bottom:26px}
.lm b{display:block;font-size:34px;line-height:1.18;color:#fff;font-weight:800}
.lm span{display:block;font-size:26px;line-height:1.38;color:#c4cfe6;margin-top:16px}
"""))


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)

    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = os.path.join(ROOT, "assets", "_article_fig.html")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for name, (w, h, html) in IMGS.items():
                pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1.5)
                open(tmp, "w").write(html)
                pg.goto(f"http://127.0.0.1:{PORT}/assets/_article_fig.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
                out = os.path.join(OUT, f"{name}.png"); pg.screenshot(path=out); pg.close()
                print(out, os.path.getsize(out))
            b.close()
    finally:
        srv.shutdown()
        if os.path.exists(tmp): os.remove(tmp)


main()
