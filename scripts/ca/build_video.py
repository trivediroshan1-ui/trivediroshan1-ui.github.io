#!/usr/bin/env python3
"""Square video of the CA/MFA lab (1080x1080, 30 fps, silent, on-screen text).
Every frame is a pure function of time: render(t) sets the page state, the browser takes a screenshot, ffmpeg encodes.
Numbers are read from the lab's own data and checked. Usage: python3 build_video.py OUT.mp4  [ONLY=t1,t2 for stills]"""
import os, sys, json, re, shutil, subprocess, http.server, socketserver, threading, functools
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else "ca-mfa-lab.mp4"
FPS, W, H, PORT = 30, 1080, 1080, 8790
SITE = "/tmp/m8"; ROOTD = "/tmp/vroot"
txt = open("/home/claude/work/out/ca-mfa-lab/data/cases.js", encoding="utf-8").read()
CASES = json.loads(re.search(r"window.CA_CASES=(\[.*?\]);\n", txt, re.S).group(1))
SENS = json.loads(re.search(r"window.CA_SENS=(\[.*?\]);", txt, re.S).group(1))
BY = {c["id"]: c for c in CASES}
RUN = [c for c in CASES if c.get("res")]; WRONG = [c for c in RUN if c.get("match") is False]
assert (len(CASES), len(RUN), len(WRONG)) == (130, 124, 6)
assert BY["W06"]["res"] == ["in", "out", "out", "in", "out"]
assert BY["G03"]["res"] == ["in", "out", "out", "out", "in"] and BY["G03"]["controls"] == ["A", "B", "C"]
g07 = [f for x in SENS if x["change"].startswith("attacker_same_network") for f in x["flips"] if f["id"] == "G07"][0]
assert g07["was"] == ["in", "out", "out", "out", "out"] and g07["now"] == ["in", "out", "out", "out", "in"]
STG = [("1", "Enrol and recover", "#a78bfa"), ("2", "Prove", "#4de2ff"), ("3", "Trust", "#60a5fa"), ("4", "Decide", "#f59e0b"),
       ("5", "Issue", "#34d399"), ("6", "Act", "#f472b6"), ("7", "Watch and end", "#f87171")]
CNT = {}
for c in CASES: CNT[c["stage"]] = CNT.get(c["stage"], 0) + 1
STG_IDS = ["enrol", "prove", "trust", "decide", "issue", "act", "watch"]
assert [CNT[s] for s in STG_IDS] == [17, 14, 21, 33, 16, 14, 15]
TALLY = [("Run 1", 41, 41), ("Run 2", 39, 45), ("Run 3", 16, 16), ("Run 5", 12, 12), ("Run 6", 10, 10)]
DATA = dict(stages=[dict(n=a, name=b, col=c, cases=CNT[STG_IDS[i]]) for i, (a, b, c) in enumerate(STG)], tally=TALLY)

# scene start times (seconds) and total
T = dict(hook=0, method=8, chain=18, w06=34, g03=47, g07=60, numbers=72, run=82, end=90)
DUR = 96

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/fonts.css">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1080px;overflow:hidden;background:#030712;color:#f1f5f9;font-family:'DM Sans',sans-serif}
#bg{position:absolute;inset:0;background:radial-gradient(1200px 800px at 20% 10%,#0f1d3d 0%,#030712 60%)}
.sc{position:absolute;inset:0;padding:96px 90px;opacity:0}
h1,.h{font-family:'Manrope',sans-serif;font-weight:800;letter-spacing:-.02em}
.kick{font:700 22px 'Manrope';letter-spacing:.18em;text-transform:uppercase;color:#93a1bd}
.big{font-size:92px;line-height:1.02}
.mid{font-size:60px;line-height:1.08}
.cap{font-size:34px;line-height:1.3;color:#c8d3ee}
.mono{font-family:'JetBrains Mono',monospace}
.red{color:#ff6b81}.grn{color:#34d399}.cy{color:#4de2ff}
.card{border:2px solid #1f2a40;border-radius:22px;background:#0b1428}
.pill{display:inline-grid;place-items:center;min-width:86px;height:64px;border-radius:999px;font:800 30px 'Manrope';border:3px solid #33415f}
.cell{display:inline-grid;place-items:center;width:150px;height:64px;border-radius:14px;font:700 24px 'DM Sans';color:#fff}
.in{background:#c93a53}.out{background:#1a8a66}.na{background:#334155}
#brand{position:absolute;left:90px;bottom:46px;font:600 22px 'DM Sans';color:#6b7a99;letter-spacing:.02em}
#prog{position:absolute;left:0;bottom:0;height:6px;background:#4de2ff}
</style></head><body><div id="bg"></div>

<div class="sc" id="s-hook">
  <p class="kick" id="hk0">Conditional access · MFA · SSO · AI agents</p>
  <h1 class="big" id="hk1" style="margin-top:150px">MFA was on.</h1>
  <h1 class="big red" id="hk2" style="margin-top:18px">The attacker still got in.</h1>
  <p class="cap" id="hk3" style="margin-top:64px;max-width:860px">I tested 130 sign-in cases to find where each control actually stops.</p>
</div>

<div class="sc" id="s-method">
  <p class="kick">The rule</p>
  <h1 class="mid" style="margin-top:40px">Write the guess first.</h1>
  <div class="card mono" id="mf" style="margin-top:50px;padding:34px 38px;font-size:24px;line-height:1.7;color:#c8d3ee">
    <div>G03 | sub-agent writes where the human cannot</div>
    <div>none <b class="red">in</b> · all <b class="grn">out</b> · off C <b class="red">in</b></div>
    <div id="mh" style="margin-top:22px;color:#4de2ff">sha256 1abdbf11...01ec22f</div>
    <div id="mc" style="margin-top:8px;color:#34d399">committed before any code existed</div>
  </div>
  <p class="cap" id="mt" style="margin-top:52px">Change one word and the hash breaks. When I was wrong, it stays wrong.</p>
</div>

<div class="sc" id="s-chain">
  <p class="kick">The framework</p>
  <h1 class="mid" style="margin-top:34px">Seven links every sign-in passes through</h1>
  <div id="links" style="position:absolute;left:90px;top:330px;width:900px;height:520px"></div>
  <p class="cap" id="chcap" style="position:absolute;left:90px;top:880px;width:900px">A weak link anywhere lets the attacker through, however strong MFA is at link 2.</p>
</div>

<div class="sc" id="s-w06">
  <p class="kick">Case W06 · stolen integration token</p>
  <h1 class="mid" style="margin-top:34px">MFA never got asked.</h1>
  <div style="position:absolute;left:90px;top:360px;width:900px;height:360px">
    <div class="card h" id="wa" style="position:absolute;left:0;top:120px;width:230px;height:120px;display:grid;place-items:center;font-size:30px">Attacker</div>
    <div class="card h" id="wb" style="position:absolute;left:335px;top:120px;width:230px;height:120px;display:grid;place-items:center;font-size:30px">API</div>
    <div class="card h" id="wc" style="position:absolute;left:670px;top:120px;width:230px;height:120px;display:grid;place-items:center;font-size:30px">Customer<br>records</div>
    <div class="card h" id="wm" style="position:absolute;left:335px;top:0;width:230px;height:70px;display:grid;place-items:center;font-size:24px;color:#6b7a99">MFA</div>
    <div id="wt" class="mono" style="position:absolute;left:30px;top:270px;font-size:22px;color:#f7c873">token</div>
    <div id="w1" style="position:absolute;left:235px;top:176px;height:6px;width:0;background:#ff6b81"></div>
    <div id="w2" style="position:absolute;left:570px;top:176px;height:6px;width:0;background:#ff6b81"></div>
    <div id="wx" class="h" style="position:absolute;left:400px;top:262px;font-size:28px;color:#34d399;opacity:0">Address allow-list: refused</div>
  </div>
  <p class="cap" id="wcap" style="position:absolute;left:90px;top:800px;width:900px">A stolen token never triggers a sign-in. Where the token can be used from decided it.</p>
</div>

<div class="sc" id="s-g03">
  <p class="kick">Case G03 · AI sub-agent</p>
  <h1 class="mid" style="margin-top:34px">The sub-agent wrote where the person could not.</h1>
  <div style="position:absolute;left:90px;top:360px;width:900px">
    <div style="display:flex;gap:18px;align-items:center"><span class="pill" id="ga">A</span><span class="pill" id="gb">B</span><span class="pill" id="gc">C</span><span style="font-size:40px;color:#6b7a99;margin:0 10px">→</span><span class="cell" id="gr" style="width:300px">-</span></div>
    <div class="cap" id="gl" style="margin-top:28px;font-size:30px">None on</div>
    <div class="cap" style="margin-top:34px;font-size:26px;color:#93a1bd;line-height:1.55">A&nbsp; narrow the sub-agent's token<br>B&nbsp; tokens last 10 minutes<br>C&nbsp; resource checks the person's own rights</div>
  </div>
  <p class="cap" id="gcap" style="position:absolute;left:90px;top:860px;width:900px">Only C held. The script's own output, column by column.</p>
</div>

<div class="sc" id="s-g07">
  <p class="kick">Case G07 · cookie stolen after MFA</p>
  <h1 class="mid" style="margin-top:34px">Change one assumption.</h1>
  <div class="card" style="position:absolute;left:90px;top:330px;width:900px;padding:36px 40px">
    <div class="mono" style="font-size:26px;color:#93a1bd">attacker_same_network = <b id="g7v" style="color:#4de2ff">False</b></div>
    <div style="margin-top:34px;display:flex;gap:14px" id="g7row"></div>
    <div style="margin-top:16px;display:flex;gap:14px;font:600 20px 'DM Sans';color:#6b7a99"><span style="width:150px;text-align:center">none</span><span style="width:150px;text-align:center">all</span><span style="width:150px;text-align:center">off A</span><span style="width:150px;text-align:center">off B</span><span style="width:150px;text-align:center">off C</span></div>
  </div>
  <p class="cap" id="g7cap" style="position:absolute;left:90px;top:760px;width:900px">If the attacker looks local, continuous evaluation misses it. Only binding the session to the device holds.</p>
</div>

<div class="sc" id="s-num">
  <p class="kick">What came out</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:40px">
    <div class="card" style="padding:28px 32px"><div class="h big cy" id="n1">0</div><div class="cap">cases</div></div>
    <div class="card" style="padding:28px 32px"><div class="h big grn" id="n2">0</div><div class="cap">run on models</div></div>
    <div class="card" style="padding:28px 32px"><div class="h big" id="n3" style="color:#c4b5fd">0</div><div class="cap">guesses matched</div></div>
    <div class="card" style="padding:28px 32px"><div class="h big red" id="n4">0</div><div class="cap">guesses wrong</div></div>
  </div>
  <div id="bars" style="margin-top:40px"></div>
</div>

<div class="sc" id="s-run">
  <p class="kick">Your turn</p>
  <h1 class="mid" style="margin-top:34px">Run it in your browser.</h1>
  <div class="card mono" style="margin-top:44px;padding:28px 30px;font-size:16.5px;line-height:1.85;height:330px;overflow:hidden;white-space:nowrap" id="term"></div>
  <p class="cap" style="margin-top:40px">The real scripts. Change an assumption. Break a guess and watch the hash stop it.</p>
</div>

<div class="sc" id="s-end" style="display:grid;align-content:center">
  <h1 class="mid">Who signs in?</h1>
  <p class="cap" style="margin-top:26px">130 cases · the 72-page book · the browser lab · everything public</p>
  <p class="h cy" style="margin-top:60px;font-size:46px">roshantrivedi.co.in/ca-mfa-lab</p>
  <div id="endlinks" style="margin-top:70px;display:flex;gap:14px"></div>
  <p class="cap" style="margin-top:70px;font-size:24px;color:#6b7a99">Made-up data. Independent work. Nothing about any employer or client.</p>
</div>

<div id="brand">Roshan Trivedi · Conditional access lab</div><div id="prog"></div>
<script>
const D=__DATA__, T=__T__, DUR=__DUR__;
const $=id=>document.getElementById(id);
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const e=x=>{x=cl(x);return 1-Math.pow(1-x,3)};          // ease out cubic
const io=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
function seg(t,a,d){return e((t-a)/d)}
function show(el,o,dy){el.style.opacity=o;el.style.transform='translateY('+((1-o)*(dy||24))+'px)'}
const ORDER=['hook','method','chain','w06','g03','g07','numbers','run','end'];
const SC={hook:'s-hook',method:'s-method',chain:'s-chain',w06:'s-w06',g03:'s-g03',g07:'s-g07',numbers:'s-num',run:'s-run',end:'s-end'};
// build static parts once
(function(){
  const L=$('links');
  D.stages.forEach((s,i)=>{const r=Math.floor(i/4),c=i%4;const x=r?c*230+115:c*230,y=r*240;
    L.insertAdjacentHTML('beforeend',`<div id="lk${i}" class="card" style="position:absolute;left:${x}px;top:${y}px;width:205px;height:190px;border:3px solid ${s.col};padding:18px 18px;opacity:0">
      <div class="h" style="font-size:44px;color:${s.col}">${s.n}</div><div class="h" style="font-size:24px;margin-top:6px;line-height:1.15">${s.name}</div>
      <div style="font-size:20px;color:#93a1bd;margin-top:10px">${s.cases} cases</div></div>`)});
  const R=$('g7row');for(let i=0;i<5;i++)R.insertAdjacentHTML('beforeend',`<span class="cell" id="g7c${i}">-</span>`);
  const B=$('bars');D.tally.forEach((t,i)=>B.insertAdjacentHTML('beforeend',`<div style="display:flex;align-items:center;gap:18px;margin:12px 0"><span style="width:110px;font:600 24px 'DM Sans';color:#93a1bd">${t[0]}</span><div style="flex:1;height:30px;background:#111a2e;border-radius:8px;position:relative"><div id="bar${i}" style="position:absolute;left:0;top:0;bottom:0;width:0;border-radius:8px;background:${t[1]<t[2]?'#f59e0b':'#34d399'}"></div></div><span id="bl${i}" style="width:120px;text-align:right;font:700 26px 'Manrope'">${t[1]} of ${t[2]}</span></div>`));
  const EL=$('endlinks');D.stages.forEach(s=>EL.insertAdjacentHTML('beforeend',`<span style="flex:1;height:10px;border-radius:5px;background:${s.col}"></span>`));
})();
const G03={res:__G03__}; const G07={was:__G07W__,now:__G07N__};
const TERM=__TERM__;
function setCell(el,v){el.className='cell '+(v==='in'?'in':v==='out'?'out':'na');el.textContent=v==='in'?'gets in':v==='out'?'stopped':'-'}
window.render=function(t){
  // scene visibility with 0.5 s cross-fades
  ORDER.forEach((k,i)=>{const a=T[k],b=i<ORDER.length-1?T[ORDER[i+1]]:DUR+1;const o=cl((t-a)/.5)*cl((b-t)/.5);$(SC[k]).style.opacity=o});
  $('prog').style.width=(t/DUR*1080)+'px';
  let u;
  // hook
  u=t-T.hook; show($('hk0'),seg(u,.2,.6)); show($('hk1'),seg(u,.6,.7),40); show($('hk2'),seg(u,2.0,.7),40); show($('hk3'),seg(u,4.0,.8));
  // method
  u=t-T.method; show($('mf'),seg(u,.6,.7)); $('mh').style.opacity=seg(u,2.4,.5); $('mc').style.opacity=seg(u,3.6,.5); show($('mt'),seg(u,5.2,.7));
  // chain
  u=t-T.chain; for(let i=0;i<7;i++){const o=seg(u,.6+i*.55,.5);const el=$('lk'+i);el.style.opacity=o;el.style.transform='scale('+(.85+.15*o)+')';}
  const brk=seg(u,6.4,.6); const d=$('lk3'); if(u>6.4){d.style.transform='translateY('+(24*brk)+'px) rotate('+(-6*brk)+'deg)'; d.style.boxShadow='0 0 0 '+(6*brk)+'px rgba(245,158,11,.35)';}
  show($('chcap'),seg(u,7.2,.7));
  // w06
  u=t-T.w06; ['wa','wb','wc','wm'].forEach((id,i)=>show($(id),seg(u,.4+i*.25,.5)));
  $('wt').style.transform='translateX('+(io((u-2.2)/1.6)*360)+'px)'; $('wt').style.opacity=seg(u,2,.3)*(1-seg(u,7.2,.3));
  $('w1').style.width=(io((u-2.2)/1.2)*100)+'px'; $('w2').style.width=(io((u-3.6)/1.2)*(1-io((u-7.4)/.6))*100)+'px';
  $('wm').style.borderColor=u>3?'#33415f':'#1f2a40'; $('wm').style.textDecoration=u>4.6?'line-through':'none';
  $('wx').style.opacity=seg(u,7.4,.5); $('wc').style.borderColor=(u>4.8&&u<7.4)?'#ff6b81':'#1f2a40'; $('wb').style.borderColor=u>7.4?'#34d399':'#1f2a40';
  show($('wcap'),seg(u,8.6,.7));
  // g03: step through five columns
  u=t-T.g03; const cols=[['None on',[]],['All on',['A','B','C']],['Off A',['B','C']],['Off B',['A','C']],['Off C',['A','B']]];
  const k=Math.max(0,Math.min(4,Math.floor((u-1)/1.9)));
  ['A','B','C'].forEach(L=>{const on=cols[k][1].includes(L);const p=$('g'+L.toLowerCase());p.style.background=on?'#34d399':'transparent';p.style.color=on?'#04110a':'#6b7a99';p.style.borderColor=on?'#34d399':'#33415f';p.style.textDecoration=on?'none':'line-through'});
  setCell($('gr'),G03.res[k]); $('gr').textContent=G03.res[k]==='in'?'writes: gets in':'refused';
  $('gl').textContent=cols[k][0]+(k===4?': only C was off, and the write went through':'');
  show($('gcap'),seg(u,10.6,.7));
  // g07
  u=t-T.g07; const flip=u>5.2; $('g7v').textContent=flip?'True':'False'; $('g7v').style.color=flip?'#ff6b81':'#4de2ff';
  for(let i=0;i<5;i++){const v=(flip?G07.now:G07.was)[i];setCell($('g7c'+i),v);const pulse=(flip&&i===4)?seg(u,5.2,.4):0;$('g7c'+i).style.transform='scale('+(1+.12*pulse*(1-seg(u,5.8,.4)))+')'}
  show($('g7cap'),seg(u,6.4,.7));
  // numbers
  u=t-T.numbers; const n=(id,v,a)=>{$(id).textContent=Math.round(v*e((u-a)/1.4))};
  n('n1',130,.3); n('n2',124,.6); n('n3',118,.9); n('n4',6,1.2);
  D.tally.forEach((x,i)=>{$('bar'+i).style.width=(e((u-2.6-i*.3)/1)*x[1]/x[2]*100)+'%';$('bl'+i).style.opacity=seg(u,2.8+i*.3,.4)});
  // terminal
  u=t-T.run; const lines=Math.floor(cl((u-.8)/5.5)*TERM.length); $('term').innerHTML=TERM.slice(Math.max(0,lines-8),lines).map(l=>l.replace(/ OK$/,' <b class="grn">OK</b>').replace(/MISMATCH.*/,m=>'<b class="red">'+m+'</b>')).join('<br>');
};
</script></body></html>"""

r6 = json.load(open("/home/claude/ca-mfa-lab/evidence/results-run6.json"))["rows"]
fmt = lambda xs: "[" + ", ".join("'%s'" % x for x in xs) + "]"
TERM = ["$ python3 -I run6.py guesses-run6.md"] + [f'{r["id"]} {fmt(r["result"])} guess {fmt(r["guess"])} OK' for r in r6] + ["cases 10 full match 10 mismatched []"]
html = (HTML.replace("__DATA__", json.dumps(DATA)).replace("__T__", json.dumps(T)).replace("__DUR__", str(DUR))
        .replace("__G03__", json.dumps(BY["G03"]["res"])).replace("__G07W__", json.dumps(g07["was"])).replace("__G07N__", json.dumps(g07["now"]))
        .replace("__TERM__", json.dumps(TERM)))
shutil.rmtree(ROOTD, ignore_errors=True); os.makedirs(ROOTD + "/assets")
shutil.copy(SITE + "/assets/fonts.css", ROOTD + "/assets/")
for f in os.listdir(SITE + "/assets"):
    if f.endswith((".woff2", ".woff")): shutil.copy(SITE + "/assets/" + f, ROOTD + "/assets/")
open(ROOTD + "/v.html", "w", encoding="utf-8").write(html)

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=ROOTD)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
only = os.environ.get("ONLY")
frames = [float(x) for x in only.split(",")] if only else [i / FPS for i in range(int(DUR * FPS))]
FD = "/tmp/vframes"; shutil.rmtree(FD, ignore_errors=True); os.makedirs(FD)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
    pg.goto(f"http://127.0.0.1:{PORT}/v.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(600)
    for i, t in enumerate(frames):
        pg.evaluate(f"render({t})")
        pg.screenshot(path=f"{FD}/f{i:05d}.png" if not only else f"{FD}/t{t:06.2f}.png")
    b.close()
srv.shutdown()
if not only:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FD}/f%05d.png", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], check=True)
    print("wrote", OUT)
else:
    print("stills in", FD)
