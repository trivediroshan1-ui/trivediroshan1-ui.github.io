#!/usr/bin/env python3
"""Renders the NHI lab as a silent captioned MP4 (1080x1350, 24 fps, 54 s) for LinkedIn and WhatsApp.
Frames are drawn by a time function, then joined with ffmpeg. Run from the repo root."""
import os, sys, http.server, socketserver, threading, functools, subprocess, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets/share/nhi-lab.mp4")
FPS, DUR, PORT = 24, 54, 8772
CSS = """
@font-face{font-family:'DM Sans';font-weight:400;src:url(/assets/dm-sans-latin-400-normal-CW0RaeGs.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:500;src:url(/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:700;src:url(/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:800;src:url(/assets/dm-sans-latin-800-normal.woff2) format('woff2')}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1350px;background:#05061a;color:#e8eefc;font-family:'DM Sans',Arial,sans-serif;position:relative;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;width:18px;background:linear-gradient(180deg,#22d3ee,#8b5cf6 40%,#34d399 75%,#f59e0b)}
.glow{position:absolute;right:-200px;top:-200px;width:760px;height:760px;background:radial-gradient(circle,rgba(77,226,255,.18),transparent 65%)}
.eye{position:absolute;left:70px;top:56px;font-weight:700;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}
.foot{position:absolute;left:70px;right:60px;bottom:44px;border-top:2px solid #1f2a40;padding-top:18px;display:flex;justify-content:space-between;align-items:center}
.foot b{font-weight:800;font-size:28px;color:#4de2ff}.foot span{font-size:18px;color:#93a1bd}
.prog{position:absolute;left:18px;bottom:0;height:8px;background:#4de2ff}
.a{position:absolute;left:70px;right:60px;opacity:0}
h1{font-weight:800;font-size:76px;line-height:1.06;color:#fff;letter-spacing:-.015em}
h1 em{font-style:normal;color:#4de2ff}
h2{font-weight:800;font-size:56px;line-height:1.1;color:#fff;letter-spacing:-.01em}
p{font-size:36px;line-height:1.35;color:#c4cfe6}
.box{border:3px solid var(--c,#4de2ff);border-radius:22px;background:rgba(255,255,255,.04);padding:22px 28px;font-size:36px;font-weight:700;color:#fff}
.box small{display:block;font-size:26px;font-weight:500;color:#a9b6d3;margin-top:4px}
.q{border-left:8px solid #f7c873;background:rgba(247,200,115,.10);border-radius:14px;padding:18px 26px;font-size:38px;font-weight:700;color:#fff}
.q.big{font-size:44px;line-height:1.25}
.card{border:3px solid var(--c);border-radius:22px;background:rgba(255,255,255,.04);padding:22px 26px;width:470px}
.card i{font-style:normal;font-weight:700;font-size:20px;letter-spacing:.14em;text-transform:uppercase;color:var(--c)}
.card b{display:block;font-size:34px;color:#fff;margin:6px 0 6px}.card span{font-size:27px;line-height:1.35;color:#c4cfe6}
.st{border:3px solid #1f2a40;border-radius:22px;background:rgba(255,255,255,.04);padding:20px 24px;width:470px}
.st b{display:block;font-size:50px;font-weight:800;color:var(--c)}.st span{font-size:25px;color:#a9b6d3;line-height:1.3}
.held{border:3px solid #34d399;background:rgba(52,211,153,.10);border-radius:22px;padding:20px 26px;font-size:29px;line-height:1.4;color:#e8eefc}
.broke{border:3px solid #ff7a93;background:rgba(255,122,147,.10);border-radius:22px;padding:20px 26px;font-size:29px;line-height:1.4;color:#e8eefc}
.held strong{color:#7df2d0}.broke strong{color:#ff9db0}
.ar{color:#4de2ff;font-size:48px;font-weight:800;text-align:center}
.pk{position:absolute;width:26px;height:26px;border-radius:50%;background:#4de2ff;box-shadow:0 0 22px #4de2ff;opacity:0}
.chip{display:inline-block;border:2px solid #4de2ff;border-radius:999px;padding:8px 20px;font-size:26px;font-weight:700;color:#4de2ff;margin-right:10px}
.sg{border:3px solid var(--c,#4de2ff);border-radius:18px;background:rgba(255,255,255,.04);padding:0 24px;height:90px;display:flex;flex-direction:column;justify-content:center;font-size:32px;font-weight:700;color:#fff}
.sg small{font-size:22px;font-weight:500;color:#a9b6d3;margin-top:2px}
.lg{border:2px dashed #8b5cf6;border-radius:14px;height:70px;padding:0 16px;display:flex;flex-direction:column;justify-content:center;font:600 21px/1.25 'DM Sans',monospace;color:#c9b8ff;background:rgba(139,92,246,.08)}
.lg small{font:500 17px/1.2 ui-monospace,Menlo,monospace;color:#8b7bd0}
.stop{font-weight:800;font-size:34px;color:#ff7a93;border:3px solid #ff7a93;border-radius:14px;padding:6px 18px;background:rgba(255,122,147,.12)}
.mv{position:absolute;left:34px;width:26px;height:26px;border-radius:50%;opacity:0}
.url{font-weight:800;font-size:60px;color:#4de2ff;line-height:1.1}
"""
def A(html, top, t_in, t_out, left=None, width=None, extra=""):
    st = f"top:{top}px;" + (f"left:{left}px;" if left is not None else "") + (f"width:{width}px;right:auto;" if width else "") + extra
    return f"<div class='a' data-in='{t_in}' data-out='{t_out}' style='{st}'>{html}</div>"
els = []
# S1 0-6
els += [A("<h1>I tested <em>27 machine identity</em> cases</h1>", 330, 0.3, 6.0),
        A("<p>Service accounts, API keys, CI tokens, break-glass accounts and AI tools. Made-up data.</p>", 700, 1.4, 6.0),
        A("<div class='q big'>My guesses were wrong in two places.</div>", 960, 3.0, 6.0)]
# S2 6-16 method
S2o = 16.0
els += [A("<h2>How I kept myself honest</h2>", 130, 6.2, S2o)]
steps = [("1", "Write the guess", "what I expect, before any code", "#4de2ff"), ("2", "Hash and commit it", "SHA-256, so it cannot change later", "#4de2ff"),
         ("3", "Write the code", "a small model of each control", "#34d399"), ("4", "Run it twice", "control off, then on", "#34d399"),
         ("5", "Switch each control off alone", "does anything notice?", "#f7c873")]
for i, (n, h, d, c) in enumerate(steps):
    els.append(A(f"<div class='box' style='--c:{c}'>{n}. {h}<small>{d}</small></div>", 290 + i*150, 7.0 + i*1.3, S2o))
els.append(A("<p style='font-size:30px'>I wrote both the guesses and the code. A match proves little. The misses are the useful part.</p>", 1060, 13.2, S2o))
# S3 16-28 two cases
S3o = 28.0
els += [A("<h2>Two cases</h2>", 130, 16.2, S3o),
        A("<div class='card' style='--c:#4de2ff;width:940px'><i>Vendor breached</i><b>Token still valid</b><span>An AI office app was linked with broad access. The vendor is breached.</span></div>", 280, 17.0, S3o, left=70, width=940),
        A("<div class='broke'><strong>Without a control.</strong> The replayed token reads the employee's files.</div>", 520, 19.0, S3o),
        A("<div class='held'><strong>With an app allowlist.</strong> The grant is refused. With revoke only: replays stop after 60 minutes.</div>", 690, 21.0, S3o),
        A("<div class='card' style='--c:#8b5cf6;width:940px'><i>Secrets in AI-written code</i><b>The scan caught 6 of 8</b><span>It missed a secret split across two lines and a base64-encoded one. I had guessed one miss.</span></div>", 900, 23.5, S3o, left=70, width=940)]
# S4 28-39 stats
S4o = 39.0
els += [A("<h2>What I found</h2>", 130, 28.2, S4o)]
stats = [("27", "cases run", "#4de2ff"), ("25", "guesses matched", "#7df2d0"), ("2", "guesses wrong", "#ff7a93"), ("2", "controls masked by another", "#f7c873")]
for i, (b, s, c) in enumerate(stats):
    els.append(A(f"<div class='st' style='--c:{c}'><b>{b}</b><span>{s}</span></div>", 290 + (i//2)*240, 29.0 + i*0.9, S4o, left=70 if i % 2 == 0 else 560, width=450))
els += [A("<p>A 10-minute token lifetime changed nothing once the token was bound and revoked. Layering hides a control that matters elsewhere.</p>", 800, 33.0, S4o)]
# S5 39-48 broke
S5o = 48.0
els += [A("<h2>What did not hold</h2>", 130, 39.2, S5o)]
for i, q in enumerate(["A made-up ticket number passed the break-glass review", "A false justification was accepted", "A false retirement sign-off left one identity active", "An allowlisted app, later breached, works until someone revokes it"]):
    els.append(A(f"<div class='q'>{q}</div>", 290 + i*150, 40.0 + i*1.2, S5o))
els.append(A("<p>Nothing checks that the sign-off is true.</p>", 920, 44.5, S5o))
# S6 48-54
els += [A("<h2>Free and public</h2>", 250, 48.2, DUR),
        A("<p>27 cases with animated workflows, a lab you can run in your browser, and a free PDF book.</p>", 400, 48.8, DUR),
        A("<div class='url'>roshantrivedi.co.in<br>/nhi-lab</div>", 700, 49.6, DUR),
        A("<p>Think a case is wrong? Tell me. I will add it.</p>", 960, 51.0, DUR)]
HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='eye'>Non-human identity lab</div>
{''.join(els)}
<div class='foot'><b>roshantrivedi.co.in/nhi-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.55),b=1-ease((t-(o-0.45))/0.45);
  e.style.opacity=t>=i&&t<o?Math.min(a,b):0; e.style.transform='translateY('+((1-ease((t-i)/0.55))*26)+'px)';
 }});
 document.getElementById('prog').style.width=(1062*t/{DUR})+'px';
}};
</script></body></html>"""

def main():
    from playwright.sync_api import sync_playwright
    work = os.path.abspath(os.path.join(ROOT, "..", "nhi-video-frames")); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    page = os.path.join(ROOT, "assets", "_nhi_video.html"); open(page, "w").write(HTML)
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_nhi_video.html"); pg.wait_for_timeout(800)
            only = os.environ.get("ONLY")
            frames = [int(x) for x in only.split(",")] if only else range(int(DUR*FPS))
            for n in frames:
                pg.evaluate(f"render({n/FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    if os.environ.get("ONLY"): print("frames in", work); return
    subprocess.check_call(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",os.path.join(work,"f%05d.png"),
        "-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-preset","veryfast","-movflags","+faststart",OUT])
    print(OUT, os.path.getsize(OUT))
main()
