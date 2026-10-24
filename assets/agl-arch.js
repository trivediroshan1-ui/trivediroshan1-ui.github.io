/* Animated architecture: one request through the AI use gateway. */
(function(){
"use strict";
var A = window.AGL, reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function mountArch(root){
  root.classList.add("agl");
  var sc = A.scenarios, cur = sc[0], timer = null, runId = 0;
  var chips = el("div","agl-chips"); chips.setAttribute("role","group"); chips.setAttribute("aria-label","Pick a request");
  var bar = el("div","agl-bar"), play = el("button","agl-btn","Send this request"); play.type="button";
  var hint = el("span","agl-hint","Pick a request, then send it. Each one is a real case from the lab.");
  bar.append(play,hint);
  var stages = el("ol","agl-stages"); stages.setAttribute("aria-label","The eight steps a request takes");
  var cards = A.stages.map(function(s,i){var li=el("li","agl-stage"); var n=el("span","n","STEP "+(i+1)); li.append(n,el("b",null,s.n),el("span","t",s.t)); stages.append(li); return li;});
  var out = el("div","agl-out"); out.setAttribute("aria-live","polite");
  var left = el("div","agl-box"), right = el("div","agl-box");
  out.append(left,right);
  var mods = el("div","agl-mods"), modEls = {};
  A.modules.forEach(function(m){var d=el("div","agl-mod"); d.append(el("h3",null,m.t),el("p","s",m.s)); var u=el("ul"); m.b.forEach(function(x){u.append(el("li",null,x))}); d.append(u); mods.append(d); modEls[m.k]=d;});
  root.append(chips,bar,stages,out,mods);

  sc.forEach(function(s){
    var b = el("button","agl-chip",s.l); b.type="button"; b.setAttribute("aria-pressed", String(s===cur));
    b.append(el("small",null,s.c));
    b.addEventListener("click",function(){ cur=s; chips.querySelectorAll(".agl-chip").forEach(function(x){x.setAttribute("aria-pressed","false")}); b.setAttribute("aria-pressed","true"); run(true); });
    chips.append(b);
  });
  play.addEventListener("click",function(){ run(false); });

  function reset(){ cards.forEach(function(c){c.className="agl-stage"}); Object.keys(modEls).forEach(function(k){modEls[k].classList.remove("lit")}); }
  function showOut(){
    var s=cur;
    left.replaceChildren(); right.replaceChildren();
    left.append(el("h3",null,"What the gateway decided"));
    var p = el("p"); var cls = s.out==="allowed"?"ok":s.out==="blocked"?"bad":"warn";
    p.append(el("span","agl-pill "+cls,s.out), document.createTextNode("  "+s.why)); left.append(p);
    left.append(el("p","agl-hint",s.detail));
    left.append(el("p","agl-hint","Tested in the lab as "+s.c+"."));
    right.append(el("h3",null,"What goes in the log"));
    var r = el("p","agl-rec");
    r.append(el("i",null,"kind "),document.createTextNode("gateway   "),el("i",null,"outcome "),document.createTextNode(s.out+"   "),el("i",null,"reason "),document.createTextNode(s.why));
    right.append(r);
    var ch = el("div","agl-chain"); ch.append(el("span",null,"previous record"),document.createTextNode("→"),el("span","new","this record, linked to the one before"));
    right.append(ch);
    right.append(el("p","agl-hint","Each record is hashed together with the one before it. Edit any line later and the chain no longer checks out."));
    modEls.log.classList.add("lit");
  }
  function paintInstant(){
    reset();
    for(var i=0;i<cards.length;i++){
      if(cur.stop>=0 && i>cur.stop){cards[i].classList.add("skip");continue}
      if(i===cur.stop){cards[i].classList.add("stop-"+(cur.out==="held"?"held":"blocked"));continue}
      cards[i].classList.add(i===cur.mark?"mask":"pass");
    }
    if(cur.stop>=0 && A.stages[cur.stop].mod) modEls[A.stages[cur.stop].mod].classList.add("lit");
    else if(cur.mark>=0 && A.stages[cur.mark].mod) modEls[A.stages[cur.mark].mod].classList.add("lit");
    showOut();
  }
  function run(quiet){
    runId++; var id=runId; if(timer){clearTimeout(timer);timer=null}
    if(reduce){paintInstant();return}
    reset(); left.replaceChildren(el("h3",null,"What the gateway decided"),el("p","agl-hint","Working through the steps...")); right.replaceChildren(el("h3",null,"What goes in the log"));
    var i=0;
    (function next(){
      if(id!==runId) return;
      if(i>0){ var prev=cards[i-1]; prev.classList.remove("cur"); if(!prev.classList.contains("stop-blocked")&&!prev.classList.contains("stop-held")) prev.classList.add(i-1===cur.mark?"mask":"pass"); }
      if(i>=cards.length || (cur.stop>=0 && i>cur.stop)){
        for(var j=Math.max(i,0);j<cards.length;j++){ if(cur.stop>=0 && j>cur.stop) cards[j].classList.add("skip"); }
        showOut(); return;
      }
      var c=cards[i]; c.classList.add("cur");
      var m = A.stages[i].mod; if(m) modEls[m].classList.add("lit");
      if(cur.stop===i){
        timer=setTimeout(function(){ if(id!==runId)return; c.classList.remove("cur"); c.classList.add("stop-"+(cur.out==="held"?"held":"blocked")); i++; next(); },650);
      } else { timer=setTimeout(function(){ i++; next(); },520); }
    })();
  }
  paintInstant();
}
window.AGL_mountArch = mountArch;
})();
