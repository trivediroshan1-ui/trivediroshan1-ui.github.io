#!/usr/bin/env python3
"""Architecture in motion for LinkedIn: 1080x1350, 24 fps, silent, every scene captioned.
Frames are drawn from a time function and joined with ffmpeg."""
import os, re, json, http.server, socketserver, threading, functools, subprocess, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, PORT = 24, 8791
src = open(os.path.join(ROOT, "scripts/build-agl-story-video.py")).read()
CSS = re.search(r'CSS = """(.*?)"""', src, re.S).group(1)
CSS += """
.a,.pk,.mv{display:none}
.title{position:absolute;left:70px;right:60px;top:112px;font-weight:800;font-size:60px;line-height:1.08;color:#fff;letter-spacing:-.015em}
.sub{position:absolute;left:70px;right:60px;top:196px;font-size:30px;color:#a9b6d3}
.n{position:absolute;width:280px;height:200px;border:3px solid var(--c);border-radius:22px;background:#0b1226;padding:18px 20px;opacity:0;z-index:2}
.n b{display:block;font-size:33px;line-height:1.1;color:#fff;margin-bottom:6px}
.n span{display:block;font-size:25px;line-height:1.22;color:#b4c0da}
.n.red{background:#1c0f1c}.n.green{background:#0c1c1b}
.cap{position:absolute;left:70px;right:60px;top:1040px;height:150px;border-left:8px solid #4de2ff;background:rgba(77,226,255,.07);border-radius:14px;padding:18px 26px;font-size:35px;line-height:1.28;font-weight:700;color:#fff;opacity:0;display:flex;align-items:center}
.chip2{position:absolute;right:60px;top:60px;font-weight:700;font-size:22px;letter-spacing:.14em;color:#c9b8ff}
svg.ln{position:absolute;left:0;top:0;width:1080px;height:1350px}
.dot{z-index:1;position:absolute;width:26px;height:26px;border-radius:50%;opacity:0;margin:-13px 0 0 -13px}
.bigurl{position:absolute;left:70px;right:60px;font-weight:800;font-size:64px;line-height:1.1;color:#4de2ff}
"""
COLS, ROWS = [60, 400, 740], [270, 530, 790]
def N(i, c, r, title, sub, color, t, kind="", pulse=()):
    return dict(id=i, x=COLS[c], y=ROWS[r], title=title, sub=sub, color=color, t=t, kind=kind, pulse=list(pulse))
CY, PU, GR, RE, AM = "#4de2ff", "#8b5cf6", "#34d399", "#ff7a93", "#f7c873"
scenes = []
def S(title, sub, dur, nodes, edges, packets, caps, extra=None):
    scenes.append(dict(title=title, sub=sub, dur=dur, nodes=nodes, edges=edges, packets=packets, caps=caps, extra=extra or []))
# 1 the gateway
S("The agent only proposes", "How a request reaches the identity system", 15,
  [N("ag",0,0,"AI agent","Fixed-shape request. No password or token",CY,.4,pulse=[.6]),
   N("gw",1,0,"Gateway","Who, what shape, policy, rate, approver",PU,2.2,pulse=[4.2]),
   N("dc",2,0,"Signed decision","Allow or refuse, signed",PU,3.6,pulse=[5.4]),
   N("lg",0,1,"Decision log","Each line is chained to the one before",AM,8.6,pulse=[9.0]),
   N("vl",1,1,"Vault","Lends a five-minute credential",GR,6.0,pulse=[7.4,8.4]),
   N("ex",2,1,"Executor","Plain code. Checks the signature first",CY,5.8,pulse=[6.8,9.6]),
   N("api",2,2,"Identity API","Disable this account",GR,9.0,pulse=[10.4])],
  [("ag","gw",1.9),("gw","dc",3.3),("dc","ex",5.5),("ex","vl",6.0),("gw","lg",8.4),("ex","api",9.0)],
  [dict(path=["ag","gw","dc","ex","api"],t0=3.0,t1=10.6,color=CY),dict(path=["ex","vl","ex"],t0=6.8,t1=8.6,color=GR),dict(path=["gw","lg"],t0=4.4,t1=5.4,color=AM)],
  [(.3,3.0,"The agent only proposes. It sends a request in a fixed shape: “disable this account”."),
   (3.0,6.2,"The gateway checks who is asking, the request shape, the policy, the rate, and whether a person must approve. Then it signs a decision."),
   (6.2,9.4,"A separate executor checks the signature and borrows a five-minute credential from the vault."),
   (9.4,12.2,"It makes the call. The agent never sees the credential."),
   (12.2,14.8,"Every decision is written to a log that shows any edited or removed line.")])
# 2 bypass: make it hard
S("What if the agent goes around?", "Layer 1 of 3: make it hard", 11,
  [N("ag",0,0,"AI agent","Finds a leaked token in a config file",RE,.4,pulse=[.6]),
   N("tk",1,0,"Leaked token","Long-lived, copied out of its place",AM,1.6),
   N("api",2,0,"Identity API","The direct call",GR,2.6),
   N("bd",1,1,"Bound to the caller","Works only from the caller it was lent to",CY,5.4,pulse=[6.0]),
   N("nr",2,1,"No network route","Agent’s runtime has no path to the API",CY,7.0,pulse=[7.6])],
  [("ag","tk",1.4),("tk","api",2.4)],
  [dict(path=["ag","tk","api"],t0=3.0,t1=5.0,color=RE)],
  [(.3,3.0,"Suppose the agent skips the gateway. It finds a long-lived token in a config file."),
   (3.0,5.4,"It calls the identity API directly."),
   (5.4,7.0,"The token only works from the caller it was lent to. Wrong caller: refused."),
   (7.0,10.6,"And the agent’s runtime has no network route to the API. The call goes nowhere.")],
  extra=[dict(kind="stop",t=5.0,x=688,y=270,w=44,h=200,label="STOP")])
# 3 notice
S("What if it still gets through?", "Layer 2 of 3: you notice", 10,
  [N("cl",0,0,"Identity system log","Every change it recorded",AM,.4),
   N("sd",2,0,"Signed decisions","Everything the gateway approved",PU,1.0),
   N("cm",1,1,"Daily comparison","Plain code. Cannot be talked round",CY,2.4,pulse=[3.6]),
   N("ok",0,2,"Matched","A decision stands behind it",GR,5.2,"green",pulse=[5.8]),
   N("al",2,2,"Bypass alert","A change with no decision behind it",RE,6.6,"red",pulse=[7.2,8.6])],
  [("cl","cm",2.2),("sd","cm",2.2),("cm","ok",5.0),("cm","al",6.4)],
  [dict(path=["cl","cm","ok"],t0=2.8,t1=5.8,color=GR),dict(path=["sd","cm"],t0=2.8,t1=3.8,color=PU),dict(path=["cl","cm","al"],t0=5.0,t1=7.4,color=RE)],
  [(.3,2.4,"Every change in the identity system’s own log must match a decision the gateway signed."),
   (2.4,5.2,"A scheduled job lines the two up. This is ordinary code."),
   (5.2,6.6,"A matched change is fine."),
   (6.6,9.6,"A change with no decision behind it is a bypass alert.")])
# 4 answer
S("Then you can answer", "Layer 3 of 3: switch off, keep evidence, a person decides", 13,
  [N("al",0,0,"Bypass alert","Traced to one agent",RE,.4,"red",pulse=[.6]),
   N("ks",1,0,"Agent switched off","Waiting approvals cancelled",AM,2.0,pulse=[2.4]),
   N("rv",2,0,"Credentials revoked","Leaked token and lent credentials",AM,3.6,pulse=[4.0]),
   N("ev",2,1,"Evidence copied","Copied, hashed, custody noted",CY,5.4,pulse=[5.8]),
   N("pr",1,1,"A person decides","Sponsor and head of IAM",GR,7.4,pulse=[7.8]),
   N("fx",0,1,"Close the hole","Rotate, bind caller, remove route",PU,9.4,pulse=[9.8])],
  [("al","ks",1.8),("ks","rv",3.4),("rv","ev",5.2),("ev","pr",7.2),("pr","fx",9.2)],
  [dict(path=["al","ks","rv","ev","pr","fx"],t0=1.2,t1=10.2,color=CY)],
  [(.3,2.0,"The alert is traced to one agent."),
   (2.0,5.4,"The policy switches that agent off and revokes what it could use."),
   (5.4,7.4,"Before anyone cleans up, the logs are copied and hashed."),
   (7.4,9.4,"A person decides what to undo. A machine does not roll it back."),
   (9.4,12.6,"Then close the hole, and add this case to the tests that run before every change.")])
# 5 HR lifecycle
S("An identity starts in HR", "The front of the chain", 13,
  [N("hr",0,0,"HR record","The person is real and hired",CY,.4,pulse=[.6]),
   N("ap",1,0,"Approved hire","A named manager approved it",PU,1.8,pulse=[2.2]),
   N("tw",2,0,"Two people","For the risky steps",AM,3.2,pulse=[3.6]),
   N("md",2,1,"Minimum data","Only what the job needs",GR,5.0,pulse=[5.4]),
   N("mf",1,1,"MFA from day one","Before first use",GR,6.6,pulse=[7.0]),
   N("dm",0,1,"Directory matches HR?","A check that runs again and again",CY,8.2,pulse=[8.6,10.6]),
   N("mm",0,2,"Mismatch flagged","Leaver still active, mover with old access",RE,10.4,"red",pulse=[10.8])],
  [("hr","ap",1.6),("ap","tw",3.0),("tw","md",4.8),("md","mf",6.4),("mf","dm",8.0),("dm","mm",10.2)],
  [dict(path=["hr","ap","tw","md","mf","dm","mm"],t0=1.0,t1=11.2,color=CY)],
  [(.3,3.0,"An identity does not start with an agent. It starts in HR."),
   (3.0,5.0,"An approved hire, and two people for the risky steps."),
   (5.0,8.2,"The minimum data, and MFA from day one."),
   (8.2,10.4,"Then a check that the directory matches HR."),
   (10.4,12.6,"A leaver who is still active, or a mover with old access, is flagged.")])
# 6 documents
S("Answering from documents", "Where the permission is checked", 14,
  [N("pe",0,0,"Support agent","Asks about pay in their own words",CY,.4,pulse=[.6]),
   N("pc",1,0,"Live permission check","Team today, not an old index copy",GR,2.2,pulse=[3.0]),
   N("ds",2,0,"Document store","Salary review, HR files, a support FAQ",PU,4.0,pulse=[4.6]),
   N("al",2,1,"Allowed text only","Restricted files never leave the store",GR,5.8,"green",pulse=[6.2]),
   N("md",1,1,"Model","Repeats whatever it is handed",AM,7.4,pulse=[7.8]),
   N("an",0,1,"Answer","Sources only what they may see",CY,9.0,pulse=[9.4]),
   N("pt",1,2,"“Do not reveal this”","A sentence in the prompt changed nothing",RE,10.6,"red",pulse=[11.0])],
  [("pe","pc",2.0),("pc","ds",3.8),("ds","al",5.6),("al","md",7.2),("md","an",8.8)],
  [dict(path=["pe","pc","ds","al","md","an"],t0=1.0,t1=10.0,color=CY)],
  [(.3,2.4,"A support agent asks a question about pay."),
   (2.4,5.6,"Their permissions are checked first, live, before any document is fetched."),
   (5.6,9.0,"The model only ever sees what they may read. It repeats what it is given."),
   (9.0,10.6,"The source list shows only what they may see."),
   (10.6,13.6,"Telling the model “do not reveal this” changed nothing. The check has to come before the documents.")])
# 7 delegation and approvals
S("Agents handing work to agents", "And a second person for risky actions", 14,
  [N("a1",0,0,"Agent A","Holds the user’s access",CY,.4,pulse=[.6]),
   N("tk",1,0,"Token cut to the job","Not everything A can do",GR,2.0,pulse=[2.6]),
   N("a2",2,0,"Agent B","Gets only the cut-down token",CY,3.6,pulse=[4.0]),
   N("hi",2,1,"High-risk action","Deleting a user",AM,5.2,pulse=[5.6]),
   N("sg",1,1,"Second signature","Separate approver, key and signature",PU,6.8,pulse=[7.2]),
   N("ex",0,1,"Executor","Checks the public-key proof",GR,8.6,pulse=[9.0]),
   N("lv",1,2,"The approver leaves","Waiting requests move to the manager",AM,10.4,pulse=[10.8])],
  [("a1","tk",1.8),("tk","a2",3.4),("a2","hi",5.0),("hi","sg",6.6),("sg","ex",8.4)],
  [dict(path=["a1","tk","a2","hi","sg","ex"],t0=1.2,t1=9.8,color=CY)],
  [(.3,3.6,"When one agent hands work to another, the second one inherited everything, until the token was cut down to the job."),
   (3.6,6.8,"Deleting a user is not decided by one signing point. It needs a second person."),
   (6.8,10.4,"A separate approver with a separate key. The proof is a public-key signature, so a compromised executor cannot forge it."),
   (10.4,13.6,"If the approver leaves, their waiting requests move to the manager.")])
DUR_END = 6
total = sum(s["dur"] for s in scenes) + DUR_END
t0 = 0
for s in scenes:
    s["t0"] = t0; t0 += s["dur"]
cta = t0
DUR = total
data = dict(scenes=scenes, cta=cta, dur=DUR, cols=COLS, rows=ROWS)
HTML = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='bar'></div><div class='glow'></div><div class='eye'>AI governance lab · architecture</div><div class='chip2' id='ch'></div>
<div class='title' id='ti'></div><div class='sub' id='su'></div>
<svg class='ln' id='ln'><defs><marker id='ah' markerWidth='10' markerHeight='10' refX='8' refY='5' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='#5d6f94'/></marker></defs></svg>
<div id='stage'></div><div class='cap' id='cap'></div>
<div id='end' style='opacity:0'><div class='title' style='top:300px;font-size:76px'>Every box here was tested, one control switched off at a time.</div>
<div class='sub' style='top:700px;font-size:36px;line-height:1.35;color:#c4cfe6'>Guesses hashed first. Made-up data. Every command and output is public.</div>
<div class='bigurl' style='top:900px'>roshantrivedi.co.in<br>/ai-governance-lab</div></div>
<div class='foot'><b>roshantrivedi.co.in/ai-governance-lab</b><span>Made-up data only</span></div><div class='prog' id='prog'></div>
<script>
var D={json.dumps(data)};
function ease(x){{return x<0?0:x>1?1:1-Math.pow(1-x,3)}}
var W=280,H=200, stage=document.getElementById('stage'), ln=document.getElementById('ln');
function box(n){{return {{x:n.x,y:n.y,cx:n.x+W/2,cy:n.y+H/2}}}}
function clip(a,b){{ // point on a's border toward b
 var dx=b.cx-a.cx,dy=b.cy-a.cy,sx=dx?(W/2+3)/Math.abs(dx):1e9,sy=dy?(H/2+3)/Math.abs(dy):1e9,s=Math.min(sx,sy);return [a.cx+dx*s,a.cy+dy*s];}}
D.scenes.forEach(function(s,si){{
 s.byId={{}};
 s.nodes.forEach(function(n){{
  var e=document.createElement('div'); e.className='n '+n.kind; e.style.setProperty('--c',n.color); e.style.left=n.x+'px'; e.style.top=n.y+'px';
  e.innerHTML='<b>'+n.title+'</b><span>'+n.sub+'</span>'; stage.appendChild(e); n.el=e; s.byId[n.id]=n;
 }});
 s.edgeEls=s.edges.map(function(ed){{
  var a=box(s.byId[ed[0]]),b=box(s.byId[ed[1]]),p=clip(a,b),q=clip(b,a);
  var l=document.createElementNS('http://www.w3.org/2000/svg','line');
  l.setAttribute('x1',p[0]);l.setAttribute('y1',p[1]);l.setAttribute('x2',q[0]);l.setAttribute('y2',q[1]);
  l.setAttribute('stroke','#5d6f94');l.setAttribute('stroke-width','4');l.setAttribute('marker-end','url(#ah)');l.style.opacity=0; ln.appendChild(l); return l;
 }});
 s.pkEls=s.packets.map(function(p){{var d=document.createElement('div');d.className='dot';d.style.background=p.color;d.style.boxShadow='0 0 24px '+p.color;stage.appendChild(d);return d}});
 s.exEls=s.extra.map(function(x){{var d=document.createElement('div');d.style.cssText='position:absolute;left:'+x.x+'px;top:'+x.y+'px;width:'+x.w+'px;height:'+x.h+'px;border:3px solid #ff7a93;border-radius:14px;background:rgba(255,122,147,.16);color:#ff9db0;font:800 14px DM Sans;display:flex;align-items:center;justify-content:center;opacity:0';d.textContent=x.label;stage.appendChild(d);return d}});
}});
var cap=document.getElementById('cap');
window.render=function(t){{
 var si=-1; D.scenes.forEach(function(s,i){{ if(t>=s.t0&&t<s.t0+s.dur) si=i; }});
 var inEnd=t>=D.cta;
 D.scenes.forEach(function(s,i){{
  var lt=t-s.t0, on=(i===si), fade=on?Math.min(ease(lt/0.4),1-ease((lt-(s.dur-0.45))/0.4)):0;
  s.nodes.forEach(function(n){{
   var a=on?ease((lt-n.t)/0.5):0, g=0; n.pulse.forEach(function(p){{ if(lt>=p) g=Math.max(g,Math.exp(-(lt-p)*1.6)); }});
   n.el.style.opacity=Math.min(a,fade||0); n.el.style.transform='translateY('+((1-a)*22)+'px) scale('+(1+0.03*g)+')';
   n.el.style.boxShadow=on?('0 0 '+(34*g)+'px '+n.color):'none';
  }});
  s.edges.forEach(function(ed,k){{ s.edgeEls[k].style.opacity=on?Math.min(ease((lt-ed[2])/0.4),fade):0; }});
  s.packets.forEach(function(p,k){{
   var d=s.pkEls[k]; if(!on||lt<p.t0||lt>=p.t1){{d.style.opacity=0;return}}
   var pts=p.path.map(function(id){{return box(s.byId[id])}}), u=(lt-p.t0)/(p.t1-p.t0)*(pts.length-1), j=Math.min(Math.floor(u),pts.length-2), f=ease(u-j);
   f=(u-j); f=f<.5?2*f*f:1-2*(1-f)*(1-f);
   d.style.left=(pts[j].cx+(pts[j+1].cx-pts[j].cx)*f)+'px'; d.style.top=(pts[j].cy+(pts[j+1].cy-pts[j].cy)*f)+'px';
   d.style.opacity=Math.min(fade,ease((lt-p.t0)/0.3));
  }});
  s.extra.forEach(function(x,k){{ s.exEls[k].style.opacity=on?Math.min(ease((lt-x.t)/0.4),fade):0; }});
 }});
 // titles
 var ti=document.getElementById('ti'),su=document.getElementById('su'),ch=document.getElementById('ch');
 if(si>=0){{var s=D.scenes[si],lt=t-s.t0,f=Math.min(ease(lt/0.4),1-ease((lt-(s.dur-0.45))/0.4));
  ti.textContent=s.title; su.textContent=s.sub; ch.textContent=(si+1)+' / '+D.scenes.length; ti.style.opacity=f; su.style.opacity=f; ch.style.opacity=1;
  var cp=null; s.caps.forEach(function(c){{ if(lt>=c[0]&&lt<c[1]) cp=c; }});
  if(cp){{cap.textContent=cp[2];cap.style.opacity=Math.min(ease((lt-cp[0])/0.35),1-ease((lt-(cp[1]-0.3))/0.3),f);}} else cap.style.opacity=0;
 }} else {{ ti.style.opacity=0;su.style.opacity=0;ch.style.opacity=0;cap.style.opacity=0; }}
 document.getElementById('end').style.opacity=inEnd?Math.min(ease((t-D.cta)/0.6),1):0;
 document.getElementById('prog').style.width=(1062*t/D.dur)+'px';
}};
</script></body></html>"""
def main():
    import sys
    from playwright.sync_api import sync_playwright
    work = os.path.abspath(os.path.join(ROOT, "..", "agl-arch-frames")); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    page = os.path.join(ROOT, "assets", "_arch_video.html"); open(page, "w").write(HTML)
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    only = os.environ.get("ONLY")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.on("pageerror", lambda e: print("PAGE ERROR", e))
            pg.goto(f"http://127.0.0.1:{PORT}/assets/_arch_video.html"); pg.wait_for_timeout(800)
            frames = [int(float(x)*FPS) for x in only.split(",")] if only else range(int(DUR*FPS))
            for n in frames:
                pg.evaluate(f"render({n/FPS})"); pg.screenshot(path=os.path.join(work, f"f{n:05d}.png"))
            b.close()
    finally:
        srv.shutdown(); os.remove(page)
    if only: print("frames in", work, "total", DUR); return
    out = os.path.join(ROOT, "assets/share/agl-architecture.mp4")
    subprocess.run(["ffmpeg","-v","error","-y","-framerate",str(FPS),"-i",os.path.join(work,"f%05d.png"),"-c:v","libx264","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",out],check=True)
    subprocess.run(["ffmpeg","-v","error","-y","-ss","12","-i",out,"-frames:v","1","-q:v","3",os.path.join(ROOT,"assets/share/agl-architecture-poster.jpg")],check=True)
    shutil.rmtree(work); print("done", out)
if __name__ == "__main__": main()
