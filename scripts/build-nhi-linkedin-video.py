#!/usr/bin/env python3
"""Renders a slow, silent, captioned square video (1080x1080, 24 fps, 92 seconds) of the NHI lab for a
social feed: the method, the architecture, the framework and the results. Large type so it reads on a phone.
Every number is read from nhi-lab/audit/nhi-lab-audit.json at build time and checked below.
Run from the repo root. Usage: python3 scripts/build-nhi-linkedin-video.py [out.mp4]
ONLY=12,500 renders just those frames into ../nhi-linkedin-frames."""
import os, sys, json, http.server, socketserver, threading, functools, subprocess, shutil, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets/share/nhi-lab-square.mp4")
FPS, DUR, PORT, W, H = 24, 92, 8774, 1080, 1080

AUD = json.load(open(os.path.join(ROOT, "nhi-lab/audit/nhi-lab-audit.json")))
ROWS = AUD["rows"]
N = len(ROWS)
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
assert {r["id"] for r in WRONG} >= {"S-R17-05", "P-R15-12", "S-R17-09"}
RESULT_FILES = [f for f in os.listdir(os.path.join(ROOT, "nhi-lab/evidence")) if f.startswith("results") and f.endswith(".json")]
assert len(RESULT_FILES) == 4, RESULT_FILES
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from nhi_data import STAGES  # noqa: E402

CYAN, GREEN, AMBER, PINK, VIOLET, MINT = "#4de2ff", "#34d399", "#f7c873", "#ff7a93", "#8b5cf6", "#7df2d0"
STEP_COL = ["#4de2ff", "#7df2d0", "#f7c873", "#c4b5fd", "#34d399", "#ff8fa3", "#8b5cf6"]

CSS = """
@font-face{font-family:'DM Sans';font-weight:400;src:url(/assets/dm-sans-latin-400-normal-CW0RaeGs.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:500;src:url(/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:700;src:url(/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:800;src:url(/assets/dm-sans-latin-800-normal.woff2) format('woff2')}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1080px;background:#05061a;color:#e8eefc;font-family:'DM Sans',Arial,sans-serif;position:relative;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;width:14px;background:linear-gradient(180deg,#22d3ee,#8b5cf6 40%,#34d399 75%,#f59e0b)}
.glow{position:absolute;right:-300px;top:-320px;width:900px;height:900px;background:radial-gradient(circle,rgba(77,226,255,.17),transparent 65%)}
.glow2{position:absolute;left:-340px;bottom:-420px;width:1000px;height:1000px;background:radial-gradient(circle,rgba(139,92,246,.16),transparent 65%)}
.eye{position:absolute;left:60px;top:44px;font-weight:700;font-size:24px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}
.who{position:absolute;right:56px;top:44px;font-weight:600;font-size:24px;color:#93a1bd}
.foot{position:absolute;left:60px;right:56px;bottom:26px;display:flex;justify-content:space-between;align-items:center}
.foot b{font-weight:800;font-size:28px;color:#4de2ff}.foot span{font-size:22px;color:#93a1bd}
.prog{position:absolute;left:14px;bottom:0;height:10px;background:linear-gradient(90deg,#22d3ee,#8b5cf6,#34d399,#f59e0b)}
.a{position:absolute;opacity:0}
h1{font-weight:800;font-size:104px;line-height:1.04;color:#fff;letter-spacing:-.02em}
h1 em,p em{font-style:normal;color:#4de2ff;font-weight:800}
h2{font-weight:800;font-size:64px;line-height:1.08;color:#fff;letter-spacing:-.01em}
h3{font-weight:500;font-size:32px;line-height:1.25;color:#a9b6d3}
p{font-size:44px;line-height:1.3;color:#c4cfe6}
.cap{left:60px;right:56px;top:886px;height:96px;border-left:8px solid #f7c873;background:rgba(247,200,115,.10);border-radius:14px;padding:0 26px;display:flex;align-items:center;font-size:31px;font-weight:600;color:#fff;line-height:1.2}
.node{height:100%;border:3px solid var(--c);border-radius:22px;background:rgba(255,255,255,.05);padding:14px 22px;color:#fff;box-shadow:0 0 40px -12px var(--c)}
.node i{font-style:normal;font-weight:800;font-size:19px;letter-spacing:.14em;color:var(--c);text-transform:uppercase;display:block;margin-bottom:4px}
.node b{display:block;font-weight:800;font-size:35px;line-height:1.08}
.node small{display:block;font-size:25px;line-height:1.2;font-weight:500;color:#b7c4df;margin-top:5px}
.step{display:flex;align-items:center;gap:26px;height:100%}
.step u{text-decoration:none;flex:0 0 76px;height:76px;border-radius:50%;border:3px solid var(--c);color:var(--c);font-weight:800;font-size:38px;line-height:70px;text-align:center;background:rgba(255,255,255,.04);box-shadow:0 0 34px -10px var(--c)}
.step b{display:block;font-weight:800;font-size:41px;line-height:1.1;color:#fff}
.step small{display:block;font-size:28px;line-height:1.2;color:#b7c4df;margin-top:4px}
.pk{position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:#fff;box-shadow:0 0 28px 8px var(--c,#4de2ff);opacity:0}
.frow{display:flex;align-items:center;height:100%}
.frow .lab{width:400px;font-size:35px;font-weight:700;color:#fff;line-height:1.05}
.frow .lab small{display:block;font-size:22px;font-weight:500;color:#a9b6d3;margin-top:4px;line-height:1.15}
.fill{height:44px;border-radius:10px;width:0}
.num{font-weight:800;font-size:46px;color:#fff;margin-left:18px}
.tile{width:100%;height:100%;border:3px solid #1f2a40;border-radius:24px;background:rgba(255,255,255,.05);padding:20px 30px}
.tile b{display:block;font-size:100px;font-weight:800;line-height:1;color:var(--c)}
.tile span{display:block;font-size:30px;line-height:1.2;color:#c4cfe6;margin-top:8px}
.dot{position:absolute;width:52px;height:52px;border-radius:12px;opacity:0}
.miss{border-left:8px solid #ff7a93;background:rgba(255,122,147,.10);border-radius:14px;padding:0 24px;height:100%;display:flex;align-items:center;font-size:33px;font-weight:600;line-height:1.2;color:#fff}
.url{font-weight:800;font-size:68px;color:#4de2ff;line-height:1.1}
.ln{position:absolute;background:var(--c,#4de2ff);opacity:0;border-radius:3px}
.leg{font-size:26px;color:#c4cfe6;display:flex;align-items:center;gap:12px;margin-right:30px}
.leg i{display:inline-block;width:28px;height:28px;border-radius:8px}
.tag{font-size:25px;color:#93a1bd;font-weight:500}
"""

els = []


def A(html, x, y, t_in, t_out, w=None, h=None, cls="", extra=""):
    st = f"left:{x}px;top:{y}px;" + (f"width:{w}px;" if w else "") + (f"height:{h}px;" if h else "") + extra
    return f"<div class='a {cls}' data-in='{t_in}' data-out='{t_out}' style='{st}'>{html}</div>"


def LN(x, y, w, h, c, t_in, t_out):
    return f"<div class='ln' data-in='{t_in}' data-out='{t_out}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{c}'></div>"


def CAP(text, t_in, t_out):
    return A(text, 60, 886, t_in, t_out, cls="cap")


def PK(keys, color=CYAN):
    return f"<div class='pk' data-keys='{json.dumps(keys)}' style='--c:{color}'></div>"


# ---------------------------------------------------------------- 0. hook, 0 to 8
T0, T1, T2, T3, T4, T5, T6 = 0, 8, 28, 51, 63, 75, 85
els += [A("<h1>I wrote my guesses down <em>first</em>.</h1>", 60, 190, 0.4, T1, w=960),
        A(f"<p style='font-size:54px;color:#fff'>Then I tested <em>{N}</em> machine identity cases.</p>", 60, 560, 2.8, T1, w=960),
        A("<p style='font-size:36px'>Service accounts, tokens, break-glass access and AI tools that hold credentials. All of the data is made up.</p>", 60, 730, 4.6, T1, w=940)]

# ---------------------------------------------------------------- 1. the method, 8 to 28
els.append(A("<h2>How each case runs</h2>", 60, 112, T1 + 0.3, T2, w=960))
STEPS6 = [("Write the guess", "What I expect, before any code", CYAN),
          ("Hash it", "SHA-256 of the guess file", CYAN),
          ("Commit it", "Alone, so it cannot change later", CYAN),
          ("Write the code", "A small model of each control", GREEN),
          ("Run it twice", "Control off, then on", GREEN),
          ("Switch each control off alone", "Does any check notice?", AMBER)]
for i, (h, d, c) in enumerate(STEPS6):
    ti = T1 + 1.4 + i * 2.5
    els.append(A(f"<div class='step' style='--c:{c}'><u>{i + 1}</u><div><b>{h}</b><small>{d}</small></div></div>", 60, 214 + i * 108, ti, T2, w=960, h=96))
    if i:
        els.append(LN(96, 214 + i * 108 - 22, 4, 32, c, ti, T2))
els.append(PK([(T1 + 1.6, 98, 262)] + [(T1 + 1.9 + i * 2.5, 98, 262 + i * 108) for i in range(1, 6)] + [(T1 + 16.4, 98, 262 + 5 * 108)], CYAN))
els.append(CAP("The guess is committed before any code exists, so it cannot change after the result is known.", T1 + 0.6, T2 - 0.1))

# ---------------------------------------------------------------- 2. the architecture, 28 to 51
els.append(A("<h2>How the lab is built</h2>", 60, 112, T2 + 0.3, T3, w=960))
BX = {"A": (60, 232, 440, 132), "F": (580, 232, 440, 132), "B": (60, 398, 440, 132), "C": (580, 398, 440, 132),
      "D": (60, 564, 960, 124), "E1": (60, 728, 300, 132), "E2": (390, 728, 300, 132), "E3": (720, 728, 300, 132)}


def box(k, head, title, sub, c, t):
    x, y, w, h = BX[k]
    return A(f"<div class='node' style='--c:{c}'><i>{head}</i><b>{title}</b><small>{sub}</small></div>", x, y, t, T3, w=w, h=h)


a0 = T2 + 1.2
els += [box("A", "Evidence", "guesses/", f"{len(FILES)} hashed guess files", CYAN, a0),
        box("F", "Check", "verify.py", f"Re-checks the {len(FILES)} hashes", MINT, a0 + 2.2),
        box("B", "Code", "run.py to run4.py", "Small models of each control", GREEN, a0 + 4.6),
        box("C", "Evidence", "results", f"{len(RESULT_FILES)} JSON files, one per run", GREEN, a0 + 6.8),
        box("D", "Shared", "nhi_data.py", "One reader for the guesses and the results", VIOLET, a0 + 9.4),
        box("E1", "Output", "Lab pages", f"{N} animated cases", AMBER, a0 + 12.4),
        box("E2", "Output", "Audit data", "CSV and JSON", AMBER, a0 + 13.6),
        box("E3", "Output", "PDF book", "83 pages", AMBER, a0 + 14.8)]
els += [LN(500, 296, 80, 4, MINT, a0 + 2.4, T3),            # guesses -> verify
        LN(500, 462, 80, 4, GREEN, a0 + 7.0, T3),           # code -> results
        LN(36, 296, 24, 4, CYAN, a0 + 9.6, T3), LN(36, 296, 4, 328, CYAN, a0 + 9.7, T3), LN(36, 620, 24, 4, CYAN, a0 + 9.8, T3),  # guesses -> shared, left rail
        LN(798, 530, 4, 34, GREEN, a0 + 9.9, T3),           # results -> shared
        LN(208, 688, 4, 40, AMBER, a0 + 12.6, T3), LN(538, 688, 4, 40, AMBER, a0 + 13.8, T3), LN(868, 688, 4, 40, AMBER, a0 + 15.0, T3)]
els.append(PK([(a0 + 4.8, 500, 464), (a0 + 7.2, 500, 464), (a0 + 8.2, 580, 464), (a0 + 9.6, 800, 530), (a0 + 10.6, 800, 564),
               (a0 + 11.6, 540, 622), (a0 + 12.6, 540, 688), (a0 + 13.9, 540, 728), (a0 + 14.6, 540, 728)], GREEN))
els.append(CAP("Guesses and results go through one reader. The pages, the audit files and the book are all built from it.", T2 + 0.6, T3 - 0.1))

# ---------------------------------------------------------------- 3. the framework, 51 to 63
els.append(A(f"<h2>Seven steps hold all {N} cases</h2>", 60, 112, T3 + 0.3, T4, w=960))
for i, (key, name, desc) in enumerate(STAGES):
    t0 = T3 + 1.2 + i * 0.9
    els.append(A(f"<div class='frow'><div class='lab'>{i + 1}. {name}</div>"
                 f"<div class='fill' data-bar='{STEPS[STEP_ORDER[i]] * 24}' data-bar-in='{t0 + 0.3}' style='background:{STEP_COL[i]}'></div><div class='num'>{STEPS[STEP_ORDER[i]]}</div></div>", 60, 226 + i * 90, t0, T4, w=960, h=78))
els.append(CAP("Every case sits at exactly one step, from finding an identity to retiring it.", T3 + 0.6, T4 - 0.1))

# ---------------------------------------------------------------- 4. the numbers, 63 to 75
els.append(A("<h2>What the data says</h2>", 60, 112, T4 + 0.3, T5, w=960))
TILES = [(N, "cases run", CYAN), (sum(MATCH), "guesses matched", MINT), (len(WRONG), "guesses wrong", PINK),
         (CONTROLS, "controls switched off, one at a time", VIOLET), (sum(MASKED), "cases where no check noticed", AMBER), (LIMITS, "cases with a recorded limit", "#c4b5fd")]
for i, (v, s, c) in enumerate(TILES):
    x = 60 + (i % 2) * 492; y = 214 + (i // 2) * 216; t0 = T4 + 1.0 + i * 0.9
    els.append(A(f"<div class='tile' style='--c:{c}'><b data-count='{v}' data-count-in='{t0 + 0.1}'>0</b><span>{s}</span></div>", x, y, t0, T5, w=468, h=196))
els.append(CAP("I wrote both the guesses and the code, so a match proves little. The misses are the useful part.", T4 + 0.6, T5 - 0.1))

# ---------------------------------------------------------------- 5. the misses, 75 to 85
els.append(A("<h2>Where I was wrong</h2>", 60, 112, T5 + 0.3, T6, w=960))
GX, GY, CELL = 60, 212, 68
for i in range(N):
    r, c = divmod(i, 14)
    ti = T5 + 0.9 + i * 0.035
    fill = MINT if MATCH[i] else PINK
    ring = f"box-shadow:0 0 0 4px {AMBER};" if MASKED[i] else ""
    els.append(f"<div class='dot' data-in='{ti:.2f}' data-out='{T6}' style='left:{GX + c * CELL + 6}px;top:{GY + r * CELL + 6}px;background:{fill};{ring}'></div>")
els.append(A(f"<div style='display:flex;flex-wrap:wrap;gap:8px 0'><span class='leg'><i style='background:{MINT}'></i>matched</span><span class='leg'><i style='background:{PINK}'></i>wrong</span>"
             f"<span class='leg'><i style='background:transparent;box-shadow:0 0 0 4px {AMBER}'></i>a control no check noticed</span></div>", 62, 566, T5 + 3.4, T6, w=960))
MISSES = ["The secret scan missed 2 of 8 fake secrets. I guessed 1.",
          "A drill found 1 fault, not the 2 I guessed.",
          "5 alerts, not 4. I never said what I was counting."]
for i, m in enumerate(MISSES):
    els.append(A(f"<div class='miss'>{m}</div>", 60, 622 + i * 86, T5 + 4.4 + i * 1.3, T6, w=960, h=74))
els.append(CAP(f"All {len(WRONG)} wrong guesses stay on the page. In {sum(MASKED)} cases, one control could be switched off and no check noticed.", T5 + 0.6, T6 - 0.1))

# ---------------------------------------------------------------- 6. end, 85 to 92
els += [A("<h2 style='font-size:84px'>Free and public</h2>", 60, 230, T6 + 0.3, DUR, w=960),
        A("<div class='url'>roshantrivedi.co.in/nhi-lab</div>", 60, 390, T6 + 1.0, DUR, w=980),
        A(f"<p style='font-size:38px'>{N} animated cases, the framework, the audit data and an 83 page book.</p>", 60, 540, T6 + 1.8, DUR, w=940),
        A("<p style='font-size:30px;color:#93a1bd'>Made-up data only. The models are small simulations, written by the same person who wrote the guesses. No product was tested.</p>", 60, 730, T6 + 2.8, DUR, w=940)]

HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='glow2'></div><div class='eye'>Non-human identity lab</div><div class='who'>Roshan Trivedi</div>
{''.join(els)}
<div class='foot'><b>roshantrivedi.co.in/nhi-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
function lin(x){{return x<0?0:x>1?1:x}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.9),b=1-ease((t-(o-0.6))/0.6);
  e.style.opacity=t>=i&&t<o?Math.min(a,b):0; e.style.transform='translateY('+((1-ease((t-i)/0.9))*26)+'px)';
 }});
 document.querySelectorAll('.ln').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.7),b=1-ease((t-(o-0.6))/0.6);
  e.style.opacity=t>=i&&t<o?Math.min(a,b)*0.9:0;
 }});
 document.querySelectorAll('.dot').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.4),b=1-ease((t-(o-0.6))/0.6);
  e.style.opacity=t>=i&&t<o?Math.min(a,b):0; e.style.transform='scale('+(0.6+0.4*a)+')';
 }});
 document.querySelectorAll('[data-bar]').forEach(function(e){{
  e.style.width=(+e.dataset.bar*ease((t-(+e.dataset.barIn))/1.3))+'px';
 }});
 document.querySelectorAll('[data-count]').forEach(function(e){{
  e.textContent=Math.round(+e.dataset.count*ease((t-(+e.dataset.countIn))/1.4));
 }});
 document.querySelectorAll('.pk').forEach(function(e){{
  var k=JSON.parse(e.dataset.keys),n=k.length;
  if(t<k[0][0]||t>k[n-1][0]){{e.style.opacity=0;return}}
  var j=0;while(j<n-2&&t>k[j+1][0])j++;
  var u=lin((t-k[j][0])/(k[j+1][0]-k[j][0]||1));u=u*u*(3-2*u);
  e.style.left=(k[j][1]+(k[j+1][1]-k[j][1])*u)+'px';e.style.top=(k[j][2]+(k[j+1][2]-k[j][2])*u)+'px';
  e.style.opacity=Math.min(1,(t-k[0][0])/0.4,(k[n-1][0]-t)/0.4);
 }});
 document.getElementById('prog').style.width=(1066*t/{DUR})+'px';
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
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_nhi_square.html"); pg.wait_for_timeout(800)
            only = os.environ.get("ONLY")
            frames = [int(x) for x in only.split(",")] if only else range(int(DUR * FPS))
            for n in frames:
                pg.evaluate(f"render({n / FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    if os.environ.get("ONLY"): print("frames in", work); return
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(work, "f%05d.png"),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "veryfast", "-movflags", "+faststart", OUT])
    print(OUT, os.path.getsize(OUT))


main()
