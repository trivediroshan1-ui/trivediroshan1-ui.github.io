#!/usr/bin/env python3
"""Builds the LinkedIn / WhatsApp share images for the AI governance lab (1080 x 1350 PNG)."""
import os, http.server, socketserver, threading, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8769
URL = "roshantrivedi.co.in/ai-governance-lab"
CSS = """
@font-face{font-family:'DM Sans';font-weight:400;src:url(/assets/dm-sans-latin-400-normal-CW0RaeGs.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:500;src:url(/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:700;src:url(/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:800;src:url(/assets/dm-sans-latin-800-normal.woff2) format('woff2')}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1350px;background:#05061a;color:#e8eefc;font-family:'DM Sans',Arial,sans-serif;position:relative;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;width:18px;background:linear-gradient(180deg,#22d3ee,#8b5cf6 40%,#34d399 75%,#f59e0b)}
.glow{position:absolute;right:-200px;top:-200px;width:700px;height:700px;background:radial-gradient(circle,rgba(77,226,255,.18),transparent 65%)}
.wrap{position:absolute;left:70px;right:60px;top:56px;bottom:50px;display:flex;flex-direction:column}
.eye{font-weight:700;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:#4de2ff}
h1{font-weight:800;font-size:54px;line-height:1.08;margin:16px 0 8px;color:#fff;letter-spacing:-.01em}
h1 em{font-style:normal;color:#4de2ff}
.sub{font-size:25px;color:#a9b6d3;line-height:1.35;margin-bottom:26px}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;border-top:2px solid #1f2a40;padding-top:20px}
.foot .u{font-weight:800;font-size:30px;color:#4de2ff;white-space:nowrap}
.foot .s{font-size:18px;color:#93a1bd;text-align:right;line-height:1.3}
"""
def page(body, extra=""):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}{extra}</style></head><body><div class='bar'></div><div class='glow'></div><div class='wrap'>{body}</div></body></html>"

def workflow():
    steps = [("1","Ask","Which common AI governance controls hold up, and where do they fail?","#4de2ff"),
             ("2","Build","A made-up lender, Kaveri Finance. 40 staff, 200 customers. Aadhaar, PAN and card numbers invented, but they pass the real checksums.","#8b5cf6"),
             ("3","Guess first","Write the expected result for every case. Commit it to git. Then run.","#34d399"),
             ("4","Run 59 cases","Gateway 16 · Guardrail filter 17 · Agent identity 12 · Audit 14.","#f7c873"),
             ("5","Fix and run again","Filter v1 → v2 → v3 scored 20, 42, 45 of 53 variants. On 200 samples: 68%, 90%, 100%.","#4de2ff"),
             ("6","Test on unseen items","Items written after the fix. All three filters: 4 of 10. The 100% was tuned.","#ff7a93"),
             ("7","Test a real assistant","Nine requests under one made-up policy. It followed the policy in all nine.","#8b5cf6"),
             ("8","Publish it all","Data, output, every case, diagrams, a free book, and a lab you run in your browser.","#34d399")]
    cards = ""
    for i,(n,t,d,c) in enumerate(steps):
        cards += f"<div class='st' style='--c:{c}'><div class='n'>{n}</div><div><b>{t}</b><span>{d}</span></div></div>"
        if i < len(steps)-1: cards += "<div class='ar'>↓</div>" if i%2==1 else "<div class='ar r'>→</div>"
    # 2-column snake: odd rows reverse via grid order handled by simple 2-col grid
    grid = "<div class='g'>" + "".join(f"<div class='st' style='--c:{c}'><div class='n'>{n}</div><div><b>{t}</b><span>{d}</span></div></div>" for n,t,d,c in steps) + "</div>"
    res = """<div class='res'><div class='h'><h3>What held</h3><p>The register, approvals, expiry, kill switches, short-lived agent tokens and the tamper-evident log.</p></div>
    <div class='b'><h3>What broke</h3><p>A plain filter on anything that depends on meaning: Hinglish, numbers in Hindi words, split messages, quoted attacks.</p></div></div>"""
    extra = """
    .g{display:grid;grid-template-columns:1fr 1fr;gap:16px 16px}
    .st{background:#0b1220;border:2px solid var(--c);border-radius:18px;padding:18px 20px;display:flex;gap:16px;align-items:flex-start;position:relative}
    .st .n{flex:none;width:46px;height:46px;border-radius:50%;background:var(--c);color:#05061a;font-weight:800;font-size:24px;display:grid;place-items:center}
    .st b{display:block;font-size:27px;color:#fff;margin-bottom:5px}
    .st span{font-size:20.5px;line-height:1.35;color:#b6c3dd}
    .res{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}
    .res>div{border-radius:18px;padding:18px 22px}
    .res .h{background:rgba(125,242,208,.12);border:2px solid #7df2d0}.res .b{background:rgba(255,122,147,.12);border:2px solid #ff7a93}
    .res h3{font-size:27px;margin-bottom:6px}.res .h h3{color:#7df2d0}.res .b h3{color:#ff9db0}
    .res p{font-size:20.5px;line-height:1.35;color:#d6e0f5}
    """
    body = f"""<div class='eye'>AI governance lab</div><h1>How I tested AI governance <em>with Indian data</em></h1><p class='sub'>The workflow, start to finish. Every number is from the lab. All data is made up.</p>{grid}{res}
    <div class='foot'><div class='u'>{URL}</div><div class='s'>Free book · every use case ·<br>a lab you can run in your browser</div></div>"""
    return page(body, extra)

def gateway():
    st = [("Caller","An app or an agent sends a prompt, a model name and the tools it needs."),
          ("Register","Registered, approved, not killed, approved in the last 90 days? Otherwise a discovery ticket."),
          ("Model and paperwork","Same model version as approved? Supplier review and AI bill of materials on file?"),
          ("Guardrail scan","Masks secrets and personal data. Flags hidden instructions in the text."),
          ("Data and region rules","Allowed for this use and model? Personal data abroad is held."),
          ("Model","Only the masked prompt goes out."),
          ("Response screen","The answer is scanned too, so an earlier secret is masked on the way back."),
          ("Person","The answer arrives. A customer-facing use adds its AI notice.")]
    rows = ""
    for i,(t,d) in enumerate(st):
        hot = " hot" if i in (3,4) else ""
        stop = "<div class='stop'>Personal data for an unapproved model stops here</div>" if i==4 else ""
        rows += f"<div class='r{hot}'><div class='n'>{i+1}</div><div class='tx'><b>{t}</b><span>{d}</span></div></div>{stop}"
        if i < 7: rows += "<div class='a'></div>"
    extra = """
    .rail{position:absolute;left:0;top:0}
    .list{display:flex;flex-direction:column;position:relative;padding-left:0}
    .r{display:flex;gap:18px;align-items:center;background:#0b1220;border:2px solid #24324e;border-radius:16px;padding:12px 20px}
    .r.hot{border-color:#4de2ff;background:#0e2230}
    .r .n{flex:none;width:44px;height:44px;border-radius:50%;background:#1b2a46;color:#4de2ff;font-weight:800;font-size:23px;display:grid;place-items:center}
    .r b{display:block;font-size:26px;color:#fff}.r span{font-size:19.5px;color:#a9b6d3;line-height:1.3}
    .a{height:14px;width:3px;background:#3a4a6a;margin-left:41px}
    .stop{margin:6px 0 6px 80px;color:#ff9db0;font-weight:700;font-size:21px;border-left:4px solid #ff7a93;padding:2px 0 2px 14px}
    .leg{display:flex;gap:26px;margin:2px 0 16px;font-size:20px;font-weight:700}.leg .g{color:#7df2d0}.leg .rr{color:#ff9db0}
    """
    body = f"""<div class='eye'>AI governance lab</div><h1>One request through <em>the gateway</em></h1><p class='sub'>Every call to a model passes eight checks. Every decision is written to a log that shows if a line is edited.</p>
    <div class='leg'><span class='g'>● A good request passes all eight</span><span class='rr'>● Unsafe ones stop at the step that catches them</span></div>
    <div class='list'>{rows}</div>
    <div class='foot'><div class='u'>{URL}</div><div class='s'>59 cases tested · 3 filters ·<br>made-up Indian data</div></div>"""
    return page(body, extra)

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin","*"); super().end_headers()

def main():
    from playwright.sync_api import sync_playwright
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for name, h in (("agl-workflow", workflow()), ("agl-gateway", gateway())):
                p = b.new_page(viewport={"width":1080,"height":1350})
                p.set_content(h.replace("url(/assets/", f"url(http://localhost:{PORT}/assets/"), wait_until="networkidle")
                p.wait_for_timeout(600)
                out = os.path.join(ROOT, "assets", "share", name + ".png")
                p.screenshot(path=out)
                print(out, os.path.getsize(out))
            b.close()
    finally:
        srv.shutdown()
main()
