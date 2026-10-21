/* The run loop, round by round: stepper, terminal with the Mac's real output, and the use-case tables. */
(function(){
"use strict";
var D = window.AGL, reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
var TRACK = {A:"AI use gateway",G:"Guardrail filter",I:"Agent identity",E:"Audit evidence",P:"Real assistants"};
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function mountRun(root){
  root.classList.add("agl");
  var round=1, step=-1, timer=null, filter="ALL";
  var stack = el("div","agl-stack"); root.append(stack);
  var tabs = el("div","agl-tabs"); tabs.setAttribute("role","tablist"); tabs.setAttribute("aria-label","Rounds");
  var head = el("section","agl-panel"); head.setAttribute("aria-live","polite");
  var rk=el("p","agl-eyebrow"), rt=el("h2"), ra=el("p","agl-hint"), rs=el("div","agl-stats"), rc=el("div","agl-commits");
  ra.style.maxWidth="70ch"; ra.style.margin="8px 0 0"; rt.style.margin="8px 0 0"; rt.style.fontSize="22px";
  head.append(rk,rt,ra,rs,rc);
  var flowP = el("section","agl-panel");
  flowP.append(el("h2",null,"The run loop, animated"));
  flowP.lastChild.style.fontSize="20px";
  var fh = el("p","agl-hint","Every round follows the same six steps. The expected result is committed before anything runs, so the record shows the guess came first. Play steps through the loop and lights up the matching lines in the terminal below. Click a step to jump to it."); fh.style.margin="6px 0 0";
  var fbar = el("div","agl-bar"), play=el("button","agl-btn","Play the run"), next=el("button","agl-btn ghost","Next step"), reset=el("button","agl-btn ghost","Show everything"), state=el("span","agl-hint");
  play.type=next.type=reset.type="button"; fbar.append(play,next,reset,state);
  var flow = el("ol","agl-flow");
  var term = el("div","agl-term"), tb=el("div","agl-termbar"), tname=el("span","sp"), copy=el("button",null,"Copy");
  copy.type="button"; var dots=el("span","dots"); dots.setAttribute("aria-hidden","true"); dots.append(el("i"),el("i"),el("i"));
  tb.append(dots,tname,copy);
  var body = el("div","agl-termbody"); body.tabIndex=0; body.setAttribute("role","log"); body.setAttribute("aria-label","Terminal output");
  term.append(tb,body);
  var tn = el("p","agl-hint","Lines starting with $ are commands you ran. Grey lines starting with # are my notes. Everything else is what Terminal printed. Where the lab prints a long list, it is shortened with an ellipsis."); tn.style.marginTop="10px";
  flowP.append(fh,fbar,flow,term,tn);
  var casesP = el("section","agl-panel"); var ch=el("h2",null,"Use cases and results"); ch.style.fontSize="20px";
  var cn=el("p","agl-hint"); cn.style.margin="6px 0 0";
  var filters=el("div","agl-chips"); filters.setAttribute("role","group"); filters.setAttribute("aria-label","Filter by track");
  var tw=el("div","agl-tw"), tbl=el("table"); tw.append(tbl);
  var lg=el("div","agl-legend");
  casesP.append(ch,cn,filters,tw,lg);
  var two = el("div","agl-two");
  var lp=el("section","agl-panel"); lp.append(el("h3",null,"What this round showed")); var ll=el("ul","agl-plain"); lp.append(ll);
  var vp=el("section","agl-panel"); vp.append(el("h3",null,"How to read the verdicts")); var vl=el("ul","agl-plain");
  ["As expected means my guess matched what happened. It does not mean the control passed.","Different means the lab surprised me. Those are the most useful rows.","The filter versions are mine and deliberately plain. The numbers describe a plain filter, not any vendor’s product.","A score on a set the filter was tuned to is not a detection rate."].forEach(function(t){vl.append(el("li",null,t))});
  vp.append(vl); two.append(lp,vp);
  stack.append(tabs,head,flowP,casesP,two);

  for(var n=1;n<=5;n++){(function(n){var r=D.rounds[n], b=el("button","agl-tab"); b.type="button"; b.setAttribute("role","tab"); b.dataset.n=n; b.append(el("span",null,"Round "+n),el("small",null,r.short)); b.addEventListener("click",function(){setRound(n)}); tabs.append(b)})(n)}

  function setRound(n,keep){
    stop(); round=n; step=-1; filter="ALL";
    tabs.querySelectorAll(".agl-tab").forEach(function(b){b.setAttribute("aria-selected",String(+b.dataset.n===n))});
    var r=D.rounds[n];
    rk.textContent="Round "+n+" · "+r.when; rt.textContent=r.name; ra.textContent=r.added;
    rs.replaceChildren(); r.stat.forEach(function(s){var d=el("div","agl-stat"); d.append(el("b",null,s[0]),el("span",null,s[1])); rs.append(d)});
    rc.replaceChildren(el("span","agl-hint","Commits:")); r.commits.forEach(function(h){rc.append(el("code",null,h))});
    ll.replaceChildren(); r.learned.forEach(function(x){ll.append(el("li",null,x))});
    buildFlow(); renderTerm(); renderCases(); paint(); label();
    if(!keep){try{history.replaceState(null,"","#round"+n)}catch(e){}}
  }
  function buildFlow(){
    flow.replaceChildren(); var r=D.rounds[round];
    r.steps.forEach(function(name,i){
      var li=el("li"); li.tabIndex=0; if(i===5&&round!==5) li.classList.add("off");
      li.append(el("span","n","STEP "+(i+1)),el("b",null,name),el("span","note",r.step_notes[i]),el("i","bar"));
      var go=function(){stop(); goStep(i,true); var x=flow.children[i]; if(x) x.classList.add("still")};
      li.addEventListener("click",go); li.addEventListener("keydown",function(e){if(e.key==="Enter"||e.key===" "){e.preventDefault();go()}});
      flow.append(li);
    });
  }
  function paint(){
    Array.prototype.forEach.call(flow.children,function(li,i){li.classList.toggle("on",i===step); li.classList.toggle("done",step>=0&&i<step); if(i!==step) li.classList.remove("still")});
    body.querySelectorAll(".blk").forEach(function(b){b.classList.toggle("hot",+b.dataset.step===step)});
    var hot=body.querySelector(".blk.hot");
    if(hot){ body.scrollTo({top:Math.max(0,hot.offsetTop-12),behavior:reduce?"auto":"smooth"}); }
  }
  function goStep(i,animate){
    step=i; paint();
    if(animate&&!reduce){ body.querySelectorAll(".blk.hot .ln").forEach(function(ln,k){ln.classList.remove("new"); void ln.offsetWidth; ln.style.animationDelay=Math.min(k*35,1400)+"ms"; ln.classList.add("new")}); }
    label();
  }
  function label(){
    var r=D.rounds[round];
    state.textContent = step<0 ? "Showing everything. Press Play to step through." : "Step "+(step+1)+" of 6: "+r.steps[step];
    play.textContent = timer ? "Pause" : (step>=0&&step<5 ? "Resume" : "Play the run");
  }
  function stop(){ if(timer){clearInterval(timer);timer=null} var on=flow.querySelector("li.on"); if(on) on.classList.add("still"); label(); }
  function playRun(){
    if(timer){stop();return}
    if(step>=5||step<0) step=-1;
    var adv=function(){ if(step>=5){stop();return} goStep(step+1,true); var li=flow.children[step]; if(li) li.classList.remove("still"); };
    adv(); timer=setInterval(adv, reduce?1800:2400); label();
  }
  function renderTerm(){
    body.replaceChildren(); tname.textContent="Terminal on the MacBook · round "+round;
    D.term[round].forEach(function(b){
      var blk=el("div","blk"); blk.dataset.step=b.step;
      b.lines.forEach(function(line){
        var cls="ln"; if(line.indexOf("$ ")===0) cls+=" cmd"; else if(line.charAt(0)==="#") cls+=" cmt"; else if(/MISS|different|fatal:|Invalid|Traceback|TypeError/.test(line)) cls+=" bad";
        blk.append(el("span",cls,line.length?line:" "));
      });
      body.append(blk);
    }); body.scrollTop=0;
  }
  function pill(v){var bad=/different|missed|wrongly/.test(v), info=/not run/.test(v); return el("span","agl-pill "+(bad?"bad":info?"warn":"ok"),v)}
  function renderCases(){
    tbl.replaceChildren(); filters.replaceChildren(); lg.replaceChildren();
    var th=el("thead"), hr=el("tr");
    if(round<5){
      var rows=D.cases[round], tracks=[]; rows.forEach(function(r){if(tracks.indexOf(r.track)<0)tracks.push(r.track)});
      cn.textContent=rows.length+" cases"+(round>1?" (some are earlier cases run again against the newer filter)":"")+". Expected and actual are the lab’s own labels.";
      ["ALL"].concat(tracks).forEach(function(k){var b=el("button","agl-chip",k==="ALL"?"All":k+" "+TRACK[k]); b.type="button"; b.setAttribute("aria-pressed",String(filter===k)); b.addEventListener("click",function(){filter=k;renderCases()}); filters.append(b)});
      ["ID","Case","I expected","It did","Verdict"].forEach(function(h){hr.append(el("th",null,h))}); th.append(hr); tbl.append(th);
      var tbd=el("tbody");
      rows.filter(function(r){return filter==="ALL"||r.track===filter}).forEach(function(r){
        var tr=el("tr"), id=el("td","id"); id.append(el("span","tk",r.track),document.createTextNode(r.id));
        tr.append(id,el("td",null,r.title),el("td","mono",r.expected),el("td","mono",r.actual)); var v=el("td"); v.append(pill(r.verdict)); tr.append(v); tbd.append(tr);
      }); tbl.append(tbd);
      tracks.forEach(function(k){lg.append(el("span",null,k+" = "+TRACK[k]))});
    } else {
      cn.textContent="Ten unseen items scored on all three filters, then the nine Track P cases that are still to run.";
      ["ID","Should be","Item","Result on v1, v2 and v3"].forEach(function(h){hr.append(el("th",null,h))}); th.append(hr); tbl.append(th);
      var tbd2=el("tbody");
      D.held.forEach(function(h){var tr=el("tr"), id=el("td","id"); id.append(el("span","tk","G"),document.createTextNode(h[0])); tr.append(id,el("td","mono",h[1]==="catch"?"caught":h[1]==="flag"?"flagged":"left alone"),el("td",null,h[2])); var v=el("td"); v.append(pill(h[4])); tr.append(v); tbd2.append(tr)});
      D.trackp.forEach(function(p){var tr=el("tr"), id=el("td","id"); id.append(el("span","tk","P"),document.createTextNode(p[0])); tr.append(id,el("td","mono","follows the policy"),el("td",null,p[1])); var v=el("td"); v.append(pill("not run yet")); tr.append(v); tbd2.append(tr)});
      tbl.append(tbd2);
      lg.append(el("span",null,"G = Guardrail filter"),el("span",null,"P = Real assistants, run by hand under a made-up policy"));
    }
  }
  play.addEventListener("click",playRun);
  next.addEventListener("click",function(){stop(); goStep(step>=5?0:step+1,true); var li=flow.children[step]; if(li) li.classList.add("still")});
  reset.addEventListener("click",function(){stop(); step=-1; paint(); label()});
  copy.addEventListener("click",function(){
    var text=D.term[round].reduce(function(a,b){return a.concat(b.lines)},[]).join("\n");
    var done=function(m){copy.textContent=m; setTimeout(function(){copy.textContent="Copy"},1600)};
    var sel=function(){var r=document.createRange(); r.selectNodeContents(body); var s=getSelection(); s.removeAllRanges(); s.addRange(r); done("Selected")};
    try{ navigator.clipboard.writeText(text).then(function(){done("Copied")},sel) }catch(e){ sel() }
  });
  var start=1; try{var m=/^#round([1-5])$/.exec(location.hash); if(m) start=+m[1]}catch(e){}
  setRound(start,true);
}
function mountControls(root){
  root.classList.add("agl");
  var wrap=el("div","agl-panel"); var h=el("h2",null,"Controls and the cases that test them"); h.style.fontSize="20px";
  var p=el("p","agl-hint","Sixteen controls, each mapped to the cases that test it and to where it lines up in ISO/IEC 42001 (Annex A numbers only), the NIST AI RMF, the EU AI Act and Indian rules. This is my own reading, not legal advice and not a certification."); p.style.margin="6px 0 12px";
  var tw=el("div","agl-tw"), t=el("table"); t.style.minWidth="860px"; var th=el("thead"), hr=el("tr");
  ["ID","Control","Tested by","ISO 42001","NIST AI RMF","EU AI Act","India"].forEach(function(x){hr.append(el("th",null,x))}); th.append(hr); t.append(th);
  var tb=el("tbody");
  D.controls.forEach(function(c){var tr=el("tr"); tr.append(el("td","id",c.id),el("td",null,c.control),el("td","mono",c.cases.length>8?c.cases[0]+" to "+c.cases[c.cases.length-1]+" ("+c.cases.length+" cases)":c.cases.join(", ")),el("td","mono",c.iso||"not yet mapped"),el("td","mono",c.nist||"not yet mapped"),el("td","mono",c.eu||"not yet mapped"),el("td","mono",c.india||"not yet mapped")); tb.append(tr)});
  t.append(tb); tw.append(t); wrap.append(h,p,tw); root.append(wrap);
}
window.AGL_mountRun=mountRun; window.AGL_mountControls=mountControls;
})();
