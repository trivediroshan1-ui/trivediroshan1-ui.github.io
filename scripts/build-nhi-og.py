#!/usr/bin/env python3
"""Renders assets/share/og-nhi-lab.png (1200x630), the link preview image for the NHI lab pages.
Numbers come from nhi-lab/audit/nhi-lab-audit.json. Run from the repo root."""
import os, json, http.server, socketserver, threading, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = json.load(open(os.path.join(ROOT, "nhi-lab/audit/nhi-lab-audit.json")))["rows"]
N, M, W = len(A), sum(r["guess_matched"] == "yes" for r in A), sum(r["guess_matched"] != "yes" for r in A)
U = sum(bool(r["controls_not_noticed"]) for r in A)
assert (N, M, W, U) == (67, 57, 10, 20)
HTML = f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'DM Sans';font-weight:500;src:url(/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2) format('woff2')}}
@font-face{{font-family:'DM Sans';font-weight:700;src:url(/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2) format('woff2')}}
@font-face{{font-family:'DM Sans';font-weight:800;src:url(/assets/dm-sans-latin-800-normal.woff2) format('woff2')}}
*{{box-sizing:border-box;margin:0}}body{{width:1200px;height:630px;background:#05061a;color:#e8eefc;font-family:'DM Sans',Arial,sans-serif;position:relative;overflow:hidden}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:14px;background:linear-gradient(180deg,#22d3ee,#8b5cf6 40%,#34d399 75%,#f59e0b)}}
.glow{{position:absolute;right:-220px;top:-260px;width:800px;height:800px;background:radial-gradient(circle,rgba(77,226,255,.2),transparent 65%)}}
.eye{{position:absolute;left:70px;top:52px;font-weight:700;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}}
h1{{position:absolute;left:70px;top:112px;width:1080px;font-weight:800;font-size:60px;line-height:1.05;letter-spacing:-.02em;color:#fff}}h1 em{{font-style:normal;color:#4de2ff}}
.st{{position:absolute;left:70px;top:310px;display:flex;gap:20px}}
.t{{width:250px;height:170px;border:3px solid #1f2a40;border-radius:20px;background:rgba(255,255,255,.045);padding:16px 22px}}
.t b{{display:block;font-size:64px;font-weight:800;line-height:1;color:var(--c)}}.t span{{display:block;font-size:23px;color:#b7c4df;margin-top:6px;line-height:1.2}}
.foot{{position:absolute;left:70px;right:60px;bottom:34px;display:flex;justify-content:space-between;align-items:center;border-top:2px solid #1f2a40;padding-top:16px}}
.foot b{{font-size:28px;font-weight:800;color:#4de2ff}}.foot span{{font-size:21px;color:#93a1bd}}
</style><div class=bar></div><div class=glow></div><div class=eye>Non-human identity lab</div>
<h1>I tested <em>{N}</em> machine identity cases.<br>My guesses were wrong in <em>{W}</em>.</h1>
<div class=st><div class=t style="--c:#4de2ff"><b>{N}</b><span>cases run</span></div><div class=t style="--c:#7df2d0"><b>{M}</b><span>guesses matched</span></div><div class=t style="--c:#ff7a93"><b>{W}</b><span>guesses wrong</span></div><div class=t style="--c:#f7c873"><b>{U}</b><span>cases with an unnoticed control</span></div></div>
<div class=foot><b>roshantrivedi.co.in/nhi-lab</b><span>Free audit data and an 83 page book. Made-up data only.</span></div>"""
def main():
    from playwright.sync_api import sync_playwright
    p = os.path.join(ROOT, "assets", "_og.html"); open(p, "w").write(HTML)
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.TCPServer(("127.0.0.1", 8781), functools.partial(Q, directory=ROOT)); threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630}); pg.goto("http://127.0.0.1:8781/assets/_og.html"); pg.wait_for_timeout(700)
            pg.screenshot(path=os.path.join(ROOT, "assets/share/og-nhi-lab.png")); b.close()
    finally:
        s.shutdown(); os.remove(p)
main()
