#!/usr/bin/env python3
"""Renders a short silent captioned MP4 (1080x1350) for one lab round, for the website, LinkedIn and WhatsApp.
The text comes from the round's page section and data file, so the video says what the page says.
Usage: python3 scripts/build-agl-round-video.py 13   (writes assets/share/agl-round-13.mp4 and a poster)"""
import os, re, sys, json, html, http.server, socketserver, threading, functools, subprocess, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(sys.argv[1]); FPS = 20; PORT = 8780 + N
OUT = os.path.join(ROOT, f"assets/share/agl-round-{N}.mp4"); POSTER = os.path.join(ROOT, f"assets/share/agl-round-{N}-poster.jpg")
CSS = re.search(r'CSS = """(.*?)"""', open(os.path.join(ROOT, "scripts/build-agl-story-video.py")).read(), re.S).group(1)
CSS += ".mono{font:600 30px/1.3 ui-monospace,Menlo,monospace;color:#7df2d0;word-break:break-all}.warn{border:3px solid #f7c873;background:rgba(247,200,115,.10);border-radius:22px;padding:20px 26px;font-size:29px;line-height:1.4;color:#e8eefc}.warn strong{color:#f7c873}ul.lm{list-style:none;padding:0}ul.lm li{font-size:33px;line-height:1.3;color:#e8eefc;border-left:6px solid #4de2ff;padding:8px 0 8px 22px;margin-bottom:18px}"
def data(n):
    s = open(os.path.join(ROOT, f"assets/agl-r{n}.js")).read(); return json.loads(s[s.index("{"):s.rindex("}") + 1])
D = data(N)
LANE = {"bu": "#fb923c", "ai": "#4de2ff", "dir": "#a78bfa", "aud": "#ff7a93", "iga": "#34d399", "hr": "#f7c873"}
SECTION = {10: "credentials", 11: "delegation", 12: "approvals", 13: "meaning"}[N]
h = open(os.path.join(ROOT, "ai-governance-lab/index.html")).read()
i = h.index(f'<section id="{SECTION}"'); seg = h[i:h.index("</section>", i)]
steps = []
for blk in seg.split('<li class="lc-step"')[1:]:
    m = re.match(r' data-lane="(\w+)"><h4>(.*?) <span class="lc-who">(.*?)</span></h4><p>(.*?)</p>', blk, re.S)
    lane, t, w, x = m.groups(); c = re.findall(r">([A-Z]\d+)</a>", blk)
    steps.append(dict(lane=lane, title=html.unescape(re.sub("<.*?>", "", t)), who=html.unescape(w), what=html.unescape(re.sub("<.*?>", "", x)), cases=c))
k = seg.index("What this does not show"); lis = [html.unescape(re.sub("<.*?>", "", x)) for x in re.findall(r"<li>(.*?)</li>", seg[k:k + 6000], re.S)]
def first(s, lim=165):
    s = s.strip(); p = re.split(r"(?<=[.!?])\s", s)[0]
    if len(p) <= lim: return p
    cut = p[:lim].rsplit(" ", 1)[0]; return cut.rstrip(",;:") + "…"
def short(s, lim=150):
    p = first(s, lim); return p
CFG = {
 10: dict(eye="Round ten · 25 Oct 2026", title="Credentials, sessions and <em>identity edge cases</em>", q="A copied token, a person who leaves mid-session, a sync that switches a disabled account back on: does anything stop them?",
          t="03:53", first="12 of 12", ctl=f'{D["mutations"]["noticed"]} of {D["mutations"]["total"]}', ctlnote="C2 is a limit, so it has no switch-off check",
          mac=("held", "Same verdicts on my MacBook Air: 12 of 12 as guessed, 12 of 12 controls noticed."), honest=("warn", "All 12 matched on the first run. <strong>That says my guesses were easy,</strong> not that the controls are strong.")),
 11: dict(eye="Round eleven · 25 Oct 2026", title="Agents handing work to agents, <em>keys and mergers</em>", q="When one agent hands work to another, what can a compromised executor or gateway sign, and what does a merger do to staff IDs?",
          t="04:10", first="11 of 12", ctl=f'{D["mutations"]["noticed"]} of {D["mutations"]["total"]}', ctlnote="D12 is a limit, so it has no switch-off check",
          mac=("warn", "<strong>First run on my Mac failed:</strong> it needed a package my Mac lacked. I fixed the lab, ran again, and it matched."), honest=("warn", "One case differed first time (D11). The fault was <strong>in my test,</strong> so I fixed the test, not the guess.")),
 12: dict(eye="Round twelve · 25 Oct 2026", title="Who approved it, <em>what exactly, and when?</em>", q="Self-approval, an edit after approval, one-click batches, stale approvals, an approver who leaves, split votes.",
          t="04:58", first="7 of 7", ctl=f'{D["mutations"]["noticed"]} of {D["mutations"]["total"]}', ctlnote="F7 is a limit, so it has no switch-off check",
          mac=("held", "Same verdicts on my MacBook Air: 7 of 7 as guessed, 6 of 6 controls noticed."), honest=("warn", "All 7 matched on the first run. <strong>That says my guesses were easy.</strong> F7 (two people approving each other) is not caught.")),
 13: dict(eye="Round thirteen · 25 Oct 2026", title="Finding documents <em>by meaning</em>", q="Do the permission checks still hold when a document is found without sharing a single word with the question?",
          t="05:14", first="6 of 6", ctl=f'{D["mutations"]["noticed"]} of {D["mutations"]["total"]}', ctlnote="S6 is a limit, so it has no switch-off check",
          mac=("held", "Run on my MacBook Air with a real model (all-MiniLM-L6-v2): 6 of 6 as guessed."), honest=("warn", "<strong>My first Mac run failed</strong> (a NumPy clash) and my own check wrongly said “5 of 5”. I fixed the check and ran again.")),
}[N]
els = []; t = 0.3
def A(html_, top, t_in, t_out, left=None, width=None, extra=""):
    st = f"top:{top}px;" + (f"left:{left}px;" if left is not None else "") + (f"width:{width}px;right:auto;" if width else "") + extra
    els.append(f"<div class='a' data-in='{t_in:.2f}' data-out='{t_out:.2f}' style='{st}'>{html_}</div>")
# intro
e = 6.2
A(f"<h1>{CFG['title']}</h1>", 300, t, e); A(f"<p>{CFG['q']}</p>", 700, t + 1.2, e); A("<p style='font-size:28px;color:#93a1bd'>All data is made up.</p>", 1060, t + 2.0, e)
t = e + 0.2; e = t + 6.0
A("<h2>Guesses first</h2>", 150, t, e)
A(f"<p>I wrote what I expected for each of the {len(D['cases'])} cases, and saved it before writing any code.</p>", 330, t + 0.6, e)
A(f"<div class='box' style='--c:#34d399'>Saved at {CFG['t']} IST<small>25 October 2026, in the lab repository</small></div>", 640, t + 1.8, e)
A(f"<p style='font-size:28px'>SHA-256 of the guesses file</p><div class='mono'>{D['cases_sha256'][:32]}<br>{D['cases_sha256'][32:]}</div>", 840, t + 2.8, e)
t = e + 0.2
A("<h2 style='font-size:44px'>One run through, step by step</h2>", 130, t, t + 1.5)  # brief header
t += 1.0
for s in steps:
    what = first(s["what"], 175); words = len(what.split()); d = max(4.6, 1.8 + words / 3.0); e = t + d; c = LANE.get(s["lane"], "#4de2ff")
    A(f"<span class='chip' style='border-color:{c};color:{c}'>{html.escape(s['who'])}</span>", 190, t, e)
    A(f"<h2>{html.escape(s['title'])}</h2>", 300, t + 0.3, e)
    A(f"<p>{html.escape(what)}</p>", 560, t + 0.9, e)
    if s["cases"]: A(f"<span class='chip'>Lab cases: {' · '.join(s['cases'])}</span>", 1040, t + 1.5, e)
    t = e + 0.1
e = t + 8.4
A("<h2>What came out</h2>", 130, t, e)
A(f"<div class='st' style='--c:#34d399;width:470px'><b>{CFG['first']}</b><span>cases as I guessed, first run</span></div>", 300, t + 0.7, e, left=70)
A(f"<div class='st' style='--c:#4de2ff;width:470px'><b>{CFG['ctl']}</b><span>controls noticed when switched off, one at a time</span></div>", 300, t + 1.3, e, left=560)
A(f"<p style='font-size:27px;color:#93a1bd'>{CFG['ctlnote']}.</p>", 540, t + 1.8, e)
kind, txt = CFG["mac"]
A(f"<div class='{kind}'>{txt}</div>", 650, t + 2.6, e)
kind, txt = CFG["honest"]
A(f"<div class='{kind}'>{txt}</div>", 880, t + 4.0, e)
t = e + 0.2; e = t + 9.0
A("<h2>What this does not show</h2>", 130, t, e)
bul = [short(x, 135) for x in lis[:4] if "mapping below" not in x][:3]
A("<ul class='lm'>" + "".join(f"<li>{html.escape(b)}</li>" for b in bul) + "</ul>", 330, t + 0.8, e)
t = e + 0.2; e = t + 5.0
A("<h2>Everything is free</h2>", 380, t, e); A("<div class='url'>roshantrivedi.co.in<br>/ai-governance-lab</div>", 560, t + 0.8, e); A("<p>Tell me where my tests are weak.</p>", 880, t + 1.8, e)
DUR = e + 0.2
HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='eye'>{CFG['eye']} · AI governance lab</div>
{''.join(els)}
<div class='foot'><b>roshantrivedi.co.in/ai-governance-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.5),b=1-ease((t-(o-0.4))/0.4);
  var v=t>=i&&t<o?Math.min(a,b):0; e.style.opacity=v; e.style.transform='translateY('+((1-ease((t-i)/0.5))*22)+'px)';
 }});
 document.getElementById('prog').style.width=(1062*t/{DUR:.2f})+'px';
}};
</script></body></html>"""
def main():
    from playwright.sync_api import sync_playwright
    work = os.path.abspath(os.path.join(ROOT, "..", f"agl-round{N}-frames")); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    page = os.path.join(ROOT, "assets", f"_round{N}_video.html"); open(page, "w").write(HTML)
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_round{N}_video.html"); pg.wait_for_timeout(800)
            for n in range(int(DUR * FPS)):
                pg.evaluate(f"render({n / FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            pg.evaluate("render(2.6)"); pg.screenshot(path=POSTER.replace(".jpg", ".png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(work, "f%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium", "-movflags", "+faststart", OUT])
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", POSTER.replace(".jpg", ".png"), "-q:v", "4", POSTER]); os.remove(POSTER.replace(".jpg", ".png"))
    shutil.rmtree(work, ignore_errors=True)
    print(OUT, os.path.getsize(OUT), f"{DUR:.1f}s", len(steps), "steps")
main()
