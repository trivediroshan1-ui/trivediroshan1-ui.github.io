#!/usr/bin/env python3
"""Renders the story as a silent captioned MP4 (1080x1350, 24 fps) for LinkedIn and WhatsApp.
Frames are drawn by a time function (no real-time recording), then joined with ffmpeg."""
import os, sys, http.server, socketserver, threading, functools, subprocess, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets/share/agl-story.mp4")
FPS, DUR, PORT = 24, 63, 8771
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
.url{font-weight:800;font-size:60px;color:#4de2ff;line-height:1.1}
"""
# (id, html, absolute left/top/width in px via style, in, out)
def A(html, top, t_in, t_out, left=None, width=None, extra=""):
    st = f"top:{top}px;" + (f"left:{left}px;" if left is not None else "") + (f"width:{width}px;right:auto;" if width else "") + extra
    return f"<div class='a' data-in='{t_in}' data-out='{t_out}' style='{st}'>{html}</div>"

els = []
# S1
els += [A("<h1>Why I built an <em>AI governance lab</em> on my own laptop</h1>", 330, 0.3, 5.0),
        A("<p>My story. All data is made up.</p>", 720, 1.4, 5.0)]
# S2
S2o = 14.0
els += [A("<h2>For years, I mapped controls</h2>", 130, 5.2, S2o),
        A("<span class='chip'>Finance</span><span class='chip'>Healthcare</span><span class='chip'>InfoSec</span>", 270, 5.8, S2o),
        A("<div class='box' style='--c:#4de2ff'>Vendor control<small>from the PAM or access tool</small></div>", 380, 6.2, S2o),
        A("<div class='ar'>↓</div>", 500, 6.8, S2o),
        A("<div class='box' style='--c:#8b5cf6'>IAM policy<small>written by the organisation</small></div>", 570, 7.2, S2o),
        A("<div class='ar'>↓</div>", 690, 7.8, S2o),
        A("<div class='box' style='--c:#34d399'>External auditor<small>NIST · PCI · HIPAA · ISO 27001</small></div>", 760, 8.2, S2o),
        A("<div class='q big'>Are we serious about these controls? Do they really follow the organisation’s policy?</div>", 980, 10.5, S2o)]
# S3
S3o = 23.0
els += [A("<h2>Then the AI era started</h2>", 130, 14.2, S3o),
        A("<div class='box' style='--c:#4de2ff'>“AI hooks will help”</div>", 300, 15.0, S3o),
        A("<div class='box' style='--c:#4de2ff'>“Agents will map policies”</div>", 420, 16.4, S3o),
        A("<div class='box' style='--c:#4de2ff'>“AI will automate identity”</div>", 540, 17.8, S3o),
        A("<div class='box' style='--c:#8b5cf6'>“A Centre of Excellence will set each agent’s access”</div>", 660, 19.2, S3o),
        A("<p>Later: agents will call PAM and identity APIs and still meet compliance.</p>", 900, 21.0, S3o)]
# S4
S4o = 32.0
qs = ["Which use cases?", "Which policy is each agent bound to?", "How is governance aligned to a real control?", "Who is the certifier for an agent’s decision?", "If an agent goes off script, what stops it, and what proves it?"]
els += [A("<h2>What I never heard</h2>", 130, 23.2, S4o)]
for i, q in enumerate(qs):
    els.append(A(f"<div class='q'>{q}</div>", 300 + i*150, 24.0 + i*1.2, S4o))
# S5
S5o = 41.0
els += [A("<h2>Why “read access” is not a small thing</h2>", 130, 32.2, S5o)]
cards = [("Bank", "The support bot", "Sees PAN, Aadhaar and transactions. Repeats them in a chat. Nobody was hacked.", "#4de2ff"),
         ("Corporate", "The assistant", "Reads mail and drives. Surfaces salary or legal files to the wrong person.", "#8b5cf6"),
         ("Tools and apps", "The one-time Allow", "A plugin reads the whole workspace, every day, as you.", "#f7c873"),
         ("Bots and agents", "The shared token", "Looks exactly like a real employee in the log.", "#ff7a93")]
for i, (tag, h, d, c) in enumerate(cards):
    left = 70 if i % 2 == 0 else 560
    top = 360 + (i // 2) * 360
    els.append(A(f"<div class='card' style='--c:{c}'><i>{tag}</i><b>{h}</b><span>{d}</span></div>", top, 33.2 + i*1.6, S5o, left=left, width=450))
# S6
S6o = 49.0
els += [A("<h2>So I read first, then built a test</h2>", 130, 41.2, S6o),
        A("<span class='chip'>NIST</span><span class='chip'>ISO</span><span class='chip'>IGA and PAM papers</span>", 330, 42.0, S6o),
        A("<p>Identity life cycle, accounts linked to a person, non-human identities, agents.</p>", 420, 42.6, S6o),
        A("<div class='ar'>↓</div>", 600, 43.8, S6o),
        A("<div class='box' style='--c:#f7c873'>Kaveri Finance, made up<small>40 staff · 200 customers · invented Aadhaar, PAN, cards</small></div>", 690, 44.4, S6o),
        A("<div class='ar'>↓</div>", 850, 45.6, S6o),
        A("<div class='box' style='--c:#34d399'>59 cases on a private laptop<small>expected results written down first</small></div>", 940, 46.2, S6o)]
# S7
S7o = 57.0
stats = [("59", "cases run", "#4de2ff"), ("20 · 42 · 45", "of 53 attack variants, filters v1 v2 v3", "#ff7a93"), ("4 of 10", "unseen items caught by all three", "#ff7a93"), ("9 of 9", "requests a real assistant kept to policy", "#7df2d0")]
els += [A("<h2>What I found</h2>", 130, 49.2, S7o)]
for i, (b, s, c) in enumerate(stats):
    left = 70 if i % 2 == 0 else 560
    top = 290 + (i // 2) * 230
    els.append(A(f"<div class='st' style='--c:{c}'><b>{b}</b><span>{s}</span></div>", top, 50.0 + i*0.9, S7o, left=left, width=450))
els += [A("<div class='held'><strong>What held.</strong> Access register, approvals, expiry, kill switches, short-lived agent tokens, the tamper-evident log.</div>", 790, 53.8, S7o),
        A("<div class='broke'><strong>What broke.</strong> A plain text filter. Hinglish, numbers in Hindi words, split messages, quoted attacks.</div>", 1010, 55.0, S7o)]
# S8
els += [A("<h2>Everything is free and public</h2>", 250, 57.2, DUR),
        A("<p>The data, every use case, animated diagrams, a lab you can run in your browser and a 67-page book.</p>", 400, 58.0, DUR),
        A("<div class='url'>roshantrivedi.co.in<br>/ai-governance-lab</div>", 700, 59.0, DUR),
        A("<p>If you work in IAM, PAM or audit, tell me where my tests are weak.</p>", 960, 60.6, DUR)]
# packets for S2: travel down the arrows
pk = ("<div class='pk' data-in='6.6' data-out='%s' data-y0='440' data-y1='575' style='left:60px'></div>"
      "<div class='pk' data-in='7.6' data-out='%s' data-y0='640' data-y1='765' style='left:60px'></div>") % (S2o, S2o)

HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='eye'>My story · AI governance lab</div>
{''.join(els)}{pk}
<div class='foot'><b>roshantrivedi.co.in/ai-governance-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.55),b=1-ease((t-(o-0.45))/0.45);
  var v=t>=i&&t<o?Math.min(a,b):0; e.style.opacity=v; e.style.transform='translateY('+((1-ease((t-i)/0.55))*26)+'px)';
 }});
 document.querySelectorAll('.pk').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,p=((t-i)%1.4)/1.4;
  if(t<i||t>=o){{e.style.opacity=0;return}}
  e.style.opacity=1; e.style.top=(+e.dataset.y0+(+e.dataset.y1-+e.dataset.y0)*p)+'px'; e.style.left='532px';
 }});
 document.getElementById('prog').style.width=(1062*t/{DUR})+'px';
}};
</script></body></html>"""

def main():
    from playwright.sync_api import sync_playwright
    work = os.path.join(ROOT, "..", "agl-story-frames")
    work = os.path.abspath(work); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    open(os.path.join(ROOT, "assets", "_story_video.html"), "w").write(HTML)
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    class Q(H.func):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_story_video.html"); pg.wait_for_timeout(800)
            only = os.environ.get("ONLY")
            frames = [int(x) for x in only.split(",")] if only else range(int(DUR*FPS))
            for n in frames:
                pg.evaluate(f"render({n/FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(os.path.join(ROOT, "assets", "_story_video.html"))
    if os.environ.get("ONLY"): print("frames in", work); return
    subprocess.check_call(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",os.path.join(work,"f%05d.png"),
        "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-preset","medium","-movflags","+faststart",OUT])
    print(OUT, os.path.getsize(OUT))
main()
