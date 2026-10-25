#!/usr/bin/env python3
"""A 48-second silent motion video for LinkedIn (1080x1350, 24 fps). Frames come from a time function, joined with ffmpeg."""
import os, re, sys, http.server, socketserver, threading, functools, subprocess, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, DUR, PORT = 24, 48, 8790
src = open(os.path.join(ROOT, "scripts/build-agl-story-video.py")).read()
CSS = re.search(r'CSS = """(.*?)"""', src, re.S).group(1)
CSS += """
.a{opacity:0}
.big{font-weight:800;font-size:96px;line-height:1.04;color:#fff;letter-spacing:-.02em}
.big em{font-style:normal;color:#4de2ff}
.num{font-weight:800;font-size:210px;line-height:1;color:#4de2ff;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.cell{position:absolute;width:46px;height:46px;border-radius:9px;background:#4de2ff;opacity:0}
.step{border:3px solid var(--c);border-radius:22px;background:rgba(255,255,255,.04);padding:22px 28px;display:flex;align-items:center;gap:26px}
.step i{font-style:normal;font-weight:800;font-size:54px;color:var(--c);width:60px}
.step b{display:block;font-size:40px;color:#fff}.step span{font-size:26px;color:#a9b6d3}
.hash{font:600 30px ui-monospace,Menlo,monospace;color:#c9b8ff;letter-spacing:.04em}
.brow{position:absolute;left:70px;width:940px}
.brow label{display:block;font-size:30px;font-weight:700;color:#e8eefc;margin-bottom:10px}
.track{height:54px;border-radius:14px;background:#10162c;border:2px solid #1f2a40;overflow:hidden;position:relative}
.fill{height:100%;width:0;border-radius:12px;background:var(--c)}
.track b{position:absolute;right:18px;top:7px;font-size:32px;color:#fff}
.lim{border-left:8px solid #f7c873;background:rgba(247,200,115,.10);border-radius:14px;padding:16px 26px;font-size:34px;font-weight:700;color:#fff}
"""
els = []
def A(html, top, i, o, left=70, width=940, extra=""):
    return f"<div class='a' data-in='{i}' data-out='{o}' style='top:{top}px;left:{left}px;width:{width}px;{extra}'>{html}</div>"
# 1 hook
els += [A("<div class='big'>A Teams meeting.<br>A colleague explaining <em>AI governance</em>.</div>", 300, .3, 5.6),
        A("<div class='big' style='color:#f7c873'>I was not convinced.</div>", 760, 2.6, 5.6)]
# 2 2017
els += [A("<h2>Since 2017, I map controls</h2>", 150, 5.8, 12.4),
        A("<div class='box' style='--c:#4de2ff'>Vendor control<small>CyberArk · BeyondTrust</small></div>", 330, 6.4, 12.4),
        A("<div class='ar'>↓</div>", 470, 7.0, 12.4),
        A("<div class='box' style='--c:#8b5cf6'>IAM policy<small>written by the organisation</small></div>", 540, 7.4, 12.4),
        A("<div class='ar'>↓</div>", 680, 8.0, 12.4),
        A("<div class='box' style='--c:#34d399'>External auditor<small>NIST · PCI DSS · HIPAA · ISO 27001</small></div>", 750, 8.4, 12.4),
        A("<div class='q big' style='font-size:42px'>Does the control do what the policy says, or does it only look right on paper?</div>", 960, 9.8, 12.4)]
# 3 method
els += [A("<h2>So I built my own lab</h2>", 150, 12.6, 19.0),
        A("<div class='step' style='--c:#4de2ff'><i>1</i><div><b>Write the expected result</b><span>for every case, before any code</span></div></div>", 330, 13.2, 19.0),
        A("<div class='step' style='--c:#8b5cf6'><i>2</i><div><b>Hash it and commit it</b><span class='hash' id='hs'>sha256 9fd8ab82…</span></div></div>", 500, 14.2, 19.0),
        A("<div class='step' style='--c:#34d399'><i>3</i><div><b>Run the code</b><span>then keep every result file</span></div></div>", 670, 15.2, 19.0),
        A("<div class='step' style='--c:#ff7a93'><i>4</i><div><b>Switch each control off</b><span>did a check notice? If not, it was weak</span></div></div>", 840, 16.2, 19.0),
        A("<p>Made-up lender. Invented Aadhaar, PAN and cards.</p>", 1060, 17.4, 19.0)]
# 4 counter
els += [A("<h2>A month later</h2>", 150, 19.2, 26.6),
        A("<div class='num' id='cnt'>0</div>", 250, 19.6, 26.6),
        A("<p style='font-size:40px'>cases across <b style='color:#fff'>13 rounds</b></p>", 470, 20.4, 26.6)]
# 5 held / broke
els += [A("<h2>What held. What broke.</h2>", 150, 26.8, 34.2),
        A("<div class='held'><strong>Held.</strong> Approvals, expiry, kill switches, short-lived agent tokens, tamper-evident log, permission checks before documents are fetched.</div>", 300, 27.4, 34.2),
        A("<div class='broke'><strong>Broke.</strong> A plain text filter. Three versions caught 20, 42 and 45 of 53 attack variants.</div>", 560, 28.4, 34.2)]
for k, (lab, pct, c, v, t0) in enumerate([("Filter v1", 20/53, "#ff7a93", "20 / 53", 29.4), ("Filter v2", 42/53, "#f7c873", "42 / 53", 30.0), ("Filter v3", 45/53, "#f7c873", "45 / 53", 30.6)]):
    top = 800 + k*120
    els.append(A(f"<div class='brow' style='position:static'><label>{lab}</label><div class='track'><div class='fill' data-p='{pct}' data-t='{t0}' style='--c:{c}'></div><b>{v}</b></div></div>", top, t0 - .3, 34.2))
els.append(A("<p style='font-size:30px'>On 10 new items, all three caught 4.</p>", 1160, 32.0, 34.2))
# 6 limits
els += [A("<h2>What this does not show</h2>", 150, 34.4, 41.0)]
for i, t in enumerate(["I wrote both the guesses and the code.", "The vault and the queue are small models, not products.", "One real assistant, a small test. No real tenant yet.", "My own mistakes are on the site, with the files."]):
    els.append(A(f"<div class='lim'>{t}</div>", 330 + i*165, 35.0 + i*.9, 41.0))
# 7 cta
els += [A("<div class='big' style='font-size:84px'>Free, public, <em>checkable</em>.</div>", 250, 41.2, DUR),
        A("<p>Every round has a video, the guesses with their hash, and every command I ran.</p>", 520, 42.0, DUR),
        A("<div class='url'>roshantrivedi.co.in<br>/ai-governance-lab</div>", 740, 43.0, DUR),
        A("<p>Tell me where my tests are weak.</p>", 1000, 44.4, DUR)]
cols = 17
cells = []
for n in range(164):
    r, c = divmod(n, cols)
    cells.append(f"<div class='cell' data-n='{n}' style='left:{82+c*54}px;top:{640+r*54}px'></div>")
HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='eye'>AI governance lab · my story</div>
{''.join(els)}{''.join(cells)}
<div class='foot'><b>roshantrivedi.co.in/ai-governance-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
window.render=function(t){{
 document.querySelectorAll('.a').forEach(function(e){{
  var i=+e.dataset.in,o=+e.dataset.out,a=ease((t-i)/0.6),b=1-ease((t-(o-0.45))/0.45);
  e.style.opacity=(t>=i&&t<o)?Math.min(a,b):0; e.style.transform='translateY('+((1-ease((t-i)/0.6))*34)+'px)';
 }});
 document.querySelectorAll('.fill').forEach(function(e){{ e.style.width=(100*+e.dataset.p*ease((t-+e.dataset.t)/1.4))+'%'; }});
 var c=Math.round(164*ease((t-19.8)/4.5)); document.getElementById('cnt').textContent=c;
 var vis=t>=19.6&&t<26.6, fade=Math.min(ease((t-19.6)/.5),1-ease((t-26.2)/.4));
 document.querySelectorAll('.cell').forEach(function(e){{
  var n=+e.dataset.n, lit=n<c; var hue=(n*2.2)%80;
  e.style.opacity=vis&&lit?fade*(0.55+0.45*Math.abs(Math.sin(t*2+n*.3))):0;
  e.style.background='hsl('+(185+hue)+',85%,62%)';
 }});
 var hs=document.getElementById('hs'); if(hs){{var h='9fd8ab82ea341b13390cb49e518dacbbe8c1d335e391641a098dd9e1302e6f7d';var k=Math.min(h.length,Math.floor(Math.max(0,t-14.4)*14));hs.textContent='sha256 '+h.slice(0,Math.min(k,24))+(k<24?'▌':'…');}}
 document.getElementById('prog').style.width=(1062*t/{DUR})+'px';
}};
</script></body></html>"""
def main():
    from playwright.sync_api import sync_playwright
    work = os.path.abspath(os.path.join(ROOT, "..", "agl-linkedin-frames")); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    page = os.path.join(ROOT, "assets", "_linkedin_video.html"); open(page, "w").write(HTML)
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    only = os.environ.get("ONLY")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_linkedin_video.html"); pg.wait_for_timeout(800)
            frames = [int(float(x)*FPS) for x in only.split(",")] if only else range(DUR*FPS)
            for n in frames:
                pg.evaluate(f"render({n/FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    if only: print("frames in", work); return
    out = os.path.join(ROOT, "assets/share/agl-linkedin.mp4")
    subprocess.run(["ffmpeg","-v","error","-y","-framerate",str(FPS),"-i",os.path.join(work,"f%05d.png"),"-c:v","libx264","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",out],check=True)
    subprocess.run(["ffmpeg","-v","error","-y","-ss","24","-i",out,"-frames:v","1","-q:v","3",os.path.join(ROOT,"assets/share/agl-linkedin-poster.jpg")],check=True)
    shutil.rmtree(work); print("done", out)
if __name__ == "__main__": main()
