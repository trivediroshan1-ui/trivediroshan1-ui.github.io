/* Framework page: animated flows and the full case list.
   Flows are teaching sketches of the lab's cases. The numbers and outputs in the list below them
   come straight from the lab's result files (ca-mfa-lab/data/cases.js, generated, not hand edited). */
(function(){
"use strict";
var NS="http://www.w3.org/2000/svg";
var RM=window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* step: [from, to, label, caption, kind]  kind: a attack, n normal, c control point
   control point: label/caption are what happens without the control; lo/co are what happens with it */
var FLOWS=[
{id:"relay",known:true,title:"Phishing relay",short:"A look-alike page relays the code",cases:"M01 M02 M05 Z01",
 actors:["User","Look-alike page","Real sign-in"],
 steps:[
  [0,1,"Opens the link, types password","The user lands on a page that looks like the real one and types the password.","a"],
  [1,2,"Replays the password at once","The look-alike passes the password to the real site in real time.","a"],
  [2,1,"Real site asks for a second factor","The real site asks for a code or an approval. The look-alike shows the user the same prompt.","n"],
  [0,1,"Enters the code or taps approve","The user types the code or approves. Nothing in an SMS code, a TOTP code or a plain push tells the user which site asked.","c","Passkey: domain does not match","With a passkey the browser checks the page's domain first and signs nothing for a look-alike."],
  [1,2,"Replays the code, gets a session","The look-alike forwards the code inside its time window and the real site issues a session to the attacker.","a"]],
 offOut:"The attacker holds a valid session. SMS, voice, TOTP and push were all relayed in the models (M01, M02).",
 onOut:"The real site never receives a valid second factor (M05). In this lab's models only a phishing-resistant method stops a live relay.",
 note:"Okta's Threat Intelligence team described real-time phishing kits that defeat any MFA that is not phishing-resistant (22 January 2026)."},
{id:"push",known:true,title:"Push fatigue",short:"A tired user taps approve",cases:"M03 M04",
 actors:["Attacker","Sign-in service","User"],
 steps:[
  [0,1,"Signs in with a stolen password","The attacker has the password and starts a sign-in.","a"],
  [1,2,"Sends an approval prompt","The user's phone shows an Approve or Deny prompt.","n"],
  [2,1,"Taps Approve to stop the noise","A tired user approves a prompt they did not start.","c","Number match: user cannot answer","With number matching the user must type a number shown only on the attacker's screen, so a blind approve fails."],
  [1,0,"Issues the session","The service sees an approval and opens a session for the attacker.","a"]],
 offOut:"The attacker is in (M03).",
 onOut:"The blind approve fails (M04).",
 note:"Limit: if the attacker phones the user and asks for the number, it works again. Okta says number matching is not phishing-resistant by definition."},
{id:"saml",known:true,title:"Replayed sign-in assertion",short:"A signed SAML assertion is used twice",cases:"S01 S02 S03 S04",
 actors:["Identity provider","Attacker","Application"],
 steps:[
  [0,1,"Issues an assertion","The identity provider signs an assertion for a real user. The attacker captures a copy.","n"],
  [1,2,"Replays the copy","The attacker sends the same signed assertion to the application.","a"],
  [2,0,"App checks the assertion","The application decides whether to accept it.","c","One-time ID already used: refused","The application remembers the assertion ID and refuses a second use. Audience, time and signature-to-element checks close three other cases (S02 to S04)."],
  [2,1,"Opens a session","The application accepts the assertion and opens a session.","a"]],
 offOut:"Replay, a wrong audience, a wrapped signature and an expired assertion each get through when their own check is missing (S01 to S04).",
 onOut:"Each check closes one case. They are separate switches. One does not imply the others.",
 note:"Run 1 modelled these as single controls."},
{id:"consent",known:false,title:"Consent and redirect abuse",short:"An app nobody approved gets a code",cases:"S06 Y11",
 actors:["User","Attacker's app","Authorization server"],
 steps:[
  [1,0,"Sends a normal-looking sign-in link","The attacker's app builds a sign-in link that looks routine.","a"],
  [0,2,"User opens it","The user lands on the real authorization server.","n"],
  [2,0,"Consent for an unknown app","The authorization server asks the user to consent to an app they have never heard of.","c","Per-client consent: user declines","A consent screen owned by the server names the client. A user who does not know it declines (Y11). A pre-registered redirect list stops the code going elsewhere."],
  [2,1,"Sends the code to the attacker","The code goes to the attacker's redirect address.","a"],
  [1,2,"Swaps the code for a token","The attacker's app exchanges the code for an access token.","a"]],
 offOut:"The attacker gets an authorization code with no real consent (Y11).",
 onOut:"Any one of the three controls in Y11 breaks the path on its own in the model.",
 note:"This is consent phishing. The user never types a password to the attacker."},
{id:"binding",known:false,title:"Stolen token, bound token",short:"A copied session token used elsewhere",cases:"Z17 X08 Y07 W09",
 actors:["Victim device","Attacker device","Application"],
 steps:[
  [0,1,"Token copied out of the session","Malware or a relay proxy copies the session or access token.","a"],
  [1,2,"Attacker presents the token","The attacker's machine sends the copied token to the application.","a"],
  [2,1,"Application checks the token","The application decides what proves the sender is the right one.","c","Key signature demanded: none","A token bound to a device key (DPoP, mutual TLS or token protection) needs a signature only the victim's device can make. Replay from another machine fails."],
  [2,1,"Returns the data","The application treats the token as the user.","a"]],
 offOut:"The copied token works from another machine (W09 off A, Z17).",
 onOut:"Replay from another machine fails.",
 note:"Limit: code running inside the victim's own device can still use the key (Y07). RFC 9449 says the same about browser-based clients."},
{id:"policy",known:false,title:"The app nobody listed",short:"A rule that never applies",cases:"P01 P02 P04 P05",
 actors:["User","Policy engine","Old application"],
 steps:[
  [0,2,"Signs in to an app outside the rules","An old app sits next to the identity provider but was never listed.","a"],
  [2,1,"Which rules apply?","The application asks the policy engine for a decision.","n"],
  [1,2,"Rules cover listed apps only","The policy covers what has been inventoried.","c","Inventoried and behind the IdP: rule applies","Two controls are needed: list the app, then put it behind the identity provider (P02). Either alone does nothing."],
  [2,0,"Password alone is enough","No MFA rule matched, so the password is enough.","a"]],
 offOut:"The app is reachable with no rule (P02).",
 onOut:"The rule applies. Listing the app without fronting it, or fronting it without listing it, changes nothing.",
 note:"The fix needs two steps: know the app exists, then put it behind the identity provider."},
{id:"helpdesk",known:true,title:"Help desk reset",short:"Someone phones and asks for an MFA reset",cases:"R01 R02 W12 E03",
 actors:["Caller","Help desk","Identity provider"],
 steps:[
  [0,1,"Calls, says they are the employee","The caller has researched the employee and the usual script.","a"],
  [1,0,"Asks for identifying details","The caller answers with details found online or from earlier calls.","n"],
  [1,2,"Resets the password, moves the MFA","The agent resets the password and enrols a new authenticator.","c","Callback to the number on file: waits","The reset waits for a callback to the number on file. In W12, self-service recovery is a second path and both must be closed."],
  [0,2,"Signs in with the new method","The caller signs in with the new authenticator.","a"]],
 offOut:"A working new authenticator is enrolled for the attacker (W12).",
 onOut:"Closing the help desk path alone is not enough if self-service recovery is also weak.",
 note:"CISA and the FBI describe this pattern in advisory AA23-320A. E03 tests it by role play and is still recruiting volunteers."},
{id:"federation",known:false,title:"Rogue identity provider",short:"A federated domain says MFA was done",cases:"Z03 Y03 Y04",
 actors:["Attacker","Cloud tenant","Rogue IdP"],
 steps:[
  [0,1,"Adds a federated domain","An admin right or a stolen signing key lets the attacker make the tenant trust their own IdP.","a"],
  [2,1,"Sends a sign-in saying MFA is done","The rogue IdP signs an assertion for any user, claiming MFA happened.","a"],
  [1,2,"Tenant weighs the claim","The tenant decides whether to trust the claim or ask for MFA itself.","c","Cloud MFA always required: claim ignored","If the cloud asks for MFA whatever the federated IdP claims, the forged claim is worth nothing (Y03 C)."],
  [1,0,"Accepts it, issues a session","The tenant accepts the claim and issues a session.","a"]],
 offOut:"The attacker signs in as any user with MFA treated as done (Y03).",
 onOut:"The claim is ignored. A second approver on federation changes also stops it. An alert alone does not.",
 note:"An alert is a notice. It tells you after the fact; it does not block."},
{id:"oidc",known:false,title:"CI/CD cloud trust",short:"A pipeline in the wrong repository gets a role",cases:"W01 W02 W03",
 actors:["Attacker's workflow","Cloud trust policy","Production role"],
 steps:[
  [0,1,"Asks for a token for the role","A workflow in the attacker's own repository asks the cloud for a role. Its token says repo:attacker/x.","a"],
  [1,0,"Checks the token","The cloud trust policy compares the token with its conditions.","c","Pinned to repository and branch: no match","Pin the repository and branch in the trust policy. GitHub's docs say at least one condition must be set so untrusted repositories cannot get tokens."],
  [1,2,"Role assumed","The trust policy allows the role.","a"],
  [2,0,"Production credentials issued","The workflow now holds production cloud credentials.","a"]],
 offOut:"A workflow in someone else's repository gets production credentials (W01).",
 onOut:"The trust policy rejects the foreign repository (W01 control A). Controls B and C do not touch this path.",
 note:"This flow shows W01 only. In W02 and W03 the path is a poisoned action or a pull request, and different controls decide."},
{id:"integration",known:false,title:"The token that never signs in",short:"A stolen integration token reads the data",cases:"W06 W07",
 actors:["Attacker","Customer data app","Vendor integration"],
 steps:[
  [0,2,"Steals the vendor's integration token","The token is taken from the vendor, not from a user.","a"],
  [0,1,"Calls the API from their own address","No sign-in happens. No password. No MFA prompt.","a"],
  [1,0,"Checks the token","The token is valid and in scope.","c","Address not on the vendor's list: refused","If the token works only from the vendor's addresses, the attacker's address is refused. Narrowing scope does not help when the integration legitimately reads those records (W06)."],
  [1,0,"Returns customer records","The app returns what the integration is allowed to read.","a"]],
 offOut:"The attacker exports customer records (W06). MFA was never asked, so it could not help.",
 onOut:"Refused at the address check (W06 control B).",
 note:"In August 2025 Google's threat team reported stolen OAuth tokens from the Salesloft Drift integration used against Salesforce instances."},
{id:"agent",known:false,title:"Injected agent",short:"Hidden text tells an agent to act",cases:"W10 Y12 Y14",
 actors:["Web page","Agent","Records"],
 steps:[
  [0,1,"Page carries hidden instructions","Text on a page the agent reads tells it to change other records.","a"],
  [1,2,"Agent asks to change records","The agent asks to change records outside its task.","a"],
  [2,1,"Scope check on the task token","The system decides whether the token allows it.","c","Narrow task token: no scope, refused","A token issued for this task alone has no scope for the other records. A person approving every write helps only if they read it (the model assumes 30 percent do not). Logging tells you afterwards."],
  [2,1,"Change goes through","The records are changed or deleted.","a"]],
 offOut:"Records the agent was not asked to touch are changed (W10).",
 onOut:"The write is refused at the token. Logging alone does not stop it.",
 note:"Run 5's sensitivity test shows this result depends on human habit: if people almost always read, approval alone is enough."},
{id:"mcp",known:false,title:"MCP discovery data",short:"A server names its own sign-in server",cases:"W11 Y11 Y12",
 actors:["MCP client","Rogue MCP server","Rogue sign-in server"],
 steps:[
  [0,1,"Connects to the server","The client connects and asks how to sign in.","n"],
  [1,0,"Metadata names the rogue sign-in server","The server's own metadata points to the attacker's authorization server.","a"],
  [0,2,"Client sends the user's login there","The client trusts the metadata and sends the user to sign in.","c","Not on the client's allow-list: refused","The client keeps its own allow-list of authorization servers. Comparing the issuer with the server's metadata is not enough, because a rogue server names itself as the issuer."],
  [2,0,"Attacker holds the login","The rogue server receives the user's login.","a"]],
 offOut:"The user's login goes to an attacker-controlled endpoint (W11).",
 onOut:"The allow-list refuses it. The issuer check alone passes.",
 note:"The MCP authorization specification leaves choosing the authorization server to the client. The related mcp-remote flaw (CVE-2025-6514) came from trusting server-supplied OAuth metadata."},
{id:"stepup",known:false,title:"Privileged call with an old session",short:"No fresh MFA at the sensitive step",cases:"Y01 Y02 W08",
 actors:["Attacker","Privileged API","Identity provider"],
 steps:[
  [0,1,"Calls a privileged endpoint","The attacker holds a session opened six hours ago with MFA. They have no second factor.","a"],
  [1,2,"API trusts the old session","The API does not look for a recent MFA claim, so the six-hour-old session is enough.","c","API demands fresh MFA: attacker has none","The app checks the token for a recent MFA claim and asks the identity provider for step-up. The attacker has no second factor, so it is denied (Y01)."],
  [1,0,"Action runs","The privileged action runs.","a"]],
 offOut:"A privileged action runs with no fresh MFA (Y01).",
 onOut:"The attacker cannot complete step-up.",
 note:"W08 adds three other paths that skip the check: an API key, a replayed refresh token and a service token with user-level scope. Run 5 shows the result flips if the check also applies to keys."}
];

function E(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(t!=null)e.textContent=t;return e}
function H(tag,props,kids){var e=document.createElement(tag);for(var k in props){if(k==="text")e.textContent=props[k];else if(k==="class")e.className=props[k];else e.setAttribute(k,props[k])}(kids||[]).forEach(function(c){e.appendChild(c)});return e}

function stepLabel(s,mode){ if(s[4]==="c"){ if(mode==="on") return s[5]; if(s[7]) return s[7]; } return s[2]; }
function stepCap(s,mode){ if(s[4]==="c"&&mode==="on") return s[6]; return s[3]; }
function stepKind(s,mode){ return (s[4]==="c"&&mode==="on")?"blk":(s[4]==="c"?"a":s[4]); }
function visibleSteps(f,mode){ var out=[]; for(var i=0;i<f.steps.length;i++){ out.push(i); if(mode==="on"&&f.steps[i][4]==="c") break; } return out; }

function wrap(text,max){ var w=text.split(" "),lines=[],cur=""; w.forEach(function(x){ if((cur+" "+x).trim().length>max){lines.push(cur.trim());cur=x}else cur=cur+" "+x }); if(cur.trim())lines.push(cur.trim()); return lines; }

function draw(f,mode,n,narrow){
  var W=narrow?420:860,top=narrow?96:78,row=narrow?100:78,N=f.actors.length,fs=narrow?13:12.5;
  var vis=visibleSteps(f,mode);
  var H_=top+row*vis.length+40;
  var svg=E("svg",{"class":"fsvg",viewBox:"0 0 "+W+" "+H_,role:"img","aria-label":f.title+": "+f.steps.length+" step flow, "+(mode==="on"?"with":"without")+" the control. The full steps are listed as text below."});
  var xs=f.actors.map(function(_,i){return Math.round(W*(i+.5)/N)});
  f.actors.forEach(function(a,i){
    svg.appendChild(E("line",{"class":"life",x1:xs[i],y1:narrow?62:50,x2:xs[i],y2:H_-20}));
    var bw=narrow?Math.floor(W/N)-10:180,al=narrow?wrap(a,Math.floor(bw/8)):[a],bh=narrow?18+al.length*15:40;
    var g=E("g",{"class":"actor"}); g.appendChild(E("rect",{x:xs[i]-bw/2,y:8,width:bw,height:bh,rx:10}));
    al.forEach(function(L,j){g.appendChild(E("text",{x:xs[i],y:(narrow?26:33)+j*15,"text-anchor":"middle"},L))}); svg.appendChild(g);
  });
  vis.forEach(function(si,k){
    var s=f.steps[si],kind=stepKind(s,mode),y=top+row*k+30,x1=xs[s[0]],x2=xs[s[1]],dir=x2>x1?1:-1;
    var g=E("g",{"class":"st"+(k<n?" on":"")+(k===n-1?" cur":""),"data-k":k});
    var cls=kind==="blk"?"ar blk":"ar "+kind;
    g.appendChild(E("line",{"class":cls,x1:x1,y1:y,x2:x2-dir*10,y2:y}));
    g.appendChild(E("polygon",{"class":"ah "+(kind==="blk"?"a":kind),points:(x2)+","+y+" "+(x2-dir*12)+","+(y-6)+" "+(x2-dir*12)+","+(y+6)}));
    var mid=(x1+x2)/2,lines=wrap(stepLabel(s,mode),Math.max(narrow?16:26,Math.round(Math.abs(x2-x1)/(narrow?6.6:7.2))));
    lines.forEach(function(L,j){g.appendChild(E("text",{"class":"lb",x:mid,y:y-10-(lines.length-1-j)*15,"text-anchor":"middle","font-size":fs},L))});
    var bx=Math.min(x1,x2)+14;
    g.appendChild(E("circle",{"class":"badge "+(kind==="blk"?"a":kind),cx:bx,cy:y+16,r:10}));
    g.appendChild(E("text",{"class":"num",x:bx,y:y+20,"text-anchor":"middle"},String(k+1)));
    if(kind==="blk") g.appendChild(E("text",{"class":"stop",x:mid,y:y+22,"text-anchor":"middle"},"✕ BLOCKED"));
    svg.appendChild(g);
  });
  return svg;
}

function mountFlows(root){
  var state={f:FLOWS[0],mode:"off",n:0,timer:null,filter:"all"};
  var pick=H("div",{"class":"fpick",role:"group","aria-label":"Choose a flow"});
  var filt=H("div",{"class":"fpick",role:"group","aria-label":"Filter flows"});
  [["all","All 13"],["known","Well known"],["less","Less talked about"]].forEach(function(p){
    var b=H("button",{type:"button","aria-pressed":p[0]==="all"?"true":"false","data-f":p[0],text:p[1]});
    b.addEventListener("click",function(){state.filter=p[0];[].forEach.call(filt.children,function(c){c.setAttribute("aria-pressed",c===b?"true":"false")});buildPick()});
    filt.appendChild(b)});
  var card=H("div",{"class":"fcard"}), stage=H("div"), cap=H("div",{"class":"fcap","aria-live":"polite"}), out=H("div",{"class":"fout"}), note=H("p",{"class":"fnote"}), txt=H("details",{"class":"ftext"});
  var title=H("h3"), meta=H("p",{"class":"fnote"});
  var bar=H("div",{"class":"fbar"}), playB=H("button",{type:"button","class":"fbtn",text:"Play"}), stepB=H("button",{type:"button","class":"fbtn",text:"Next step"}), rstB=H("button",{type:"button","class":"fbtn",text:"Restart"});
  var mode=H("div",{"class":"fmode",role:"group","aria-label":"Show the flow"});
  var mOff=H("button",{type:"button","aria-pressed":"true",text:"Without the control"}), mOn=H("button",{type:"button","aria-pressed":"false",text:"With the control"});
  mode.appendChild(mOff);mode.appendChild(mOn);
  [playB,stepB,rstB].forEach(function(b){bar.appendChild(b)});bar.appendChild(H("span",{"class":"sp"}));bar.appendChild(mode);
  [title,meta,bar,stage,cap,out,note,txt].forEach(function(c){card.appendChild(c)});
  root.appendChild(filt);root.appendChild(pick);root.appendChild(card);

  function total(){return visibleSteps(state.f,state.mode).length}
  function stop(){ if(state.timer){clearInterval(state.timer);state.timer=null} playB.textContent=state.n>=total()?"Play again":"Play" }
  function fillText(){
    txt.innerHTML="";var s=H("summary",{text:"Read the steps as text"});txt.appendChild(s);
    ["off","on"].forEach(function(m){
      txt.appendChild(H("p",{"class":"fnote",text:m==="off"?"Without the control":"With the control"}));
      var ol=H("ol");visibleSteps(state.f,m).forEach(function(i){var st=state.f.steps[i];ol.appendChild(H("li",{text:(m==="on"&&st[4]==="c"?"BLOCKED. ":"")+stepLabel(st,m)+". "+stepCap(st,m)}))});txt.appendChild(ol)});
  }
  function render(){
    stage.innerHTML="";state.narrow=(root.clientWidth||900)<640;stage.appendChild(draw(state.f,state.mode,state.n,state.narrow));
    var f=state.f,t=total();
    if(state.n>0){var vi=visibleSteps(f,state.mode)[state.n-1];cap.textContent=state.n+". "+stepCap(f.steps[vi],state.mode)}else cap.textContent="Press Play, or Next step, to walk through the flow.";
    var done=state.n>=t;out.className="fout"+(done?(state.mode==="on"?" good":" bad"):"");
    out.innerHTML="";if(done){out.appendChild(H("b",{text:state.mode==="on"?"With the control":"Without the control"}));out.appendChild(H("span",{text:state.mode==="on"?f.onOut:f.offOut}))}else out.style.display="none";
    out.style.display=done?"":"none";
    playB.textContent=done?"Play again":(state.timer?"Pause":"Play");
  }
  function load(f){state.f=f;state.n=RM?visibleSteps(f,state.mode).length:0;stop();
    title.textContent=f.title;
    meta.textContent="Cases: "+f.cases.split(" ").join(", ")+". "+(f.known?"Well known pattern.":"Less talked about.");
    note.textContent=f.note;fillText();render();
    [].forEach.call(pick.children,function(b){b.setAttribute("aria-pressed",b.getAttribute("data-id")===f.id?"true":"false")})}
  function buildPick(){pick.innerHTML="";FLOWS.filter(function(f){return state.filter==="all"||(state.filter==="known"?f.known:!f.known)}).forEach(function(f,i){
    var b=H("button",{type:"button","data-id":f.id,"aria-pressed":f.id===state.f.id?"true":"false"});b.appendChild(document.createTextNode(f.title));b.appendChild(H("small",{text:f.short}));
    b.addEventListener("click",function(){load(f)});pick.appendChild(b)})}
  function tick(){ if(state.n<total()){state.n++} if(state.n>=total()&&state.timer){clearInterval(state.timer);state.timer=null} render(); }
  playB.addEventListener("click",function(){ if(state.timer){stop();render();return} if(RM){state.n=total();render();return} if(state.n>=total())state.n=0; tick(); if(state.n<total())state.timer=setInterval(tick,1500); render(); });
  stepB.addEventListener("click",function(){stop();if(state.n>=total())state.n=0;state.n++;render()});
  rstB.addEventListener("click",function(){stop();state.n=0;render()});
  function setMode(m){state.mode=m;mOff.setAttribute("aria-pressed",m==="off"?"true":"false");mOn.setAttribute("aria-pressed",m==="on"?"true":"false");stop();state.n=RM?total():0;render()}
  mOff.addEventListener("click",function(){setMode("off")});mOn.addEventListener("click",function(){setMode("on")});
  buildPick();load(FLOWS[0]);
  var rt=null;window.addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(function(){var nw=(root.clientWidth||900)<640;if(nw!==state.narrow)render()},200)});
}

/* ---------- case list ---------- */
function resultCell(v,diff){var td=H("td",{"class":(v==="in"||v==="out")?v:"x",text:v==="-"?"n/a":v});if(diff)td.className+=" diff";return td}
function runLabel(r){return r===4?"Run 4 (hand tests)":"Run "+r}
function caseBody(c){
  var b=H("div",{"class":"cbody"});
  var dl=H("dl");
  function row(k,v){if(!v)return;dl.appendChild(H("dt",{text:k}));dl.appendChild(H("dd",{text:v}))}
  row("Bad outcome",c.bad);row("Controls",c.ctl);
  if(c.g1){row("What I wrote first",c.g1.none+" / "+c.g1.with+" / "+c.g1.off);row("Limit I expected",c.g1.limit)}
  b.appendChild(dl);
  if(c.res){
    b.appendChild(H("p",{"class":"fnote",text:"Output as produced by the script. “in” means the bad outcome happens. “out” means it does not."}));
    var t=H("table",{"class":"out"});var th=H("tr");th.appendChild(H("th",{text:""}));c.cols.forEach(function(x){th.appendChild(H("th",{text:x}))});t.appendChild(th);
    var r1=H("tr");r1.appendChild(H("th",{text:"Output"}));c.res.forEach(function(v,i){r1.appendChild(resultCell(v,false))});t.appendChild(r1);
    var r2=H("tr");r2.appendChild(H("th",{text:"My guess"}));c.guess.forEach(function(v,i){r2.appendChild(resultCell(v,c.res[i]!==v&&c.res[i]!=="-"))});t.appendChild(r2);
    b.appendChild(t);
    if(c.pair)b.appendChild(H("p",{"class":"fnote",text:"Two controls off together ("+c.pair.off.join(" and ")+"): output "+c.pair.result+", I guessed "+c.pair.guess+"."+(c.pair.result!==c.pair.guess?" This was the wrong guess.":"")}));
    if(c.match===false)b.appendChild(H("p",{"class":"fnote",text:(c.diffs&&c.diffs.length)?"At least one of my guesses was wrong here. The marked cells are where the output and my guess differ.":"My single-control guesses held here, but the guess for two controls off together was wrong."}));
    else b.appendChild(H("p",{"class":"fnote",text:"Guess and output agree."}));
  }else b.appendChild(H("p",{"class":"fnote",text:"Not run. This case needs a real tenant, a hardware key or a person. See the Run 4 page."}));
  if(c.note)b.appendChild(H("p",{"class":"fnote",text:"Why: "+c.note}));
  if(c.assumes)b.appendChild(H("p",{"class":"fnote",text:"Assumes: "+c.assumes}));
  var d2=H("dl");function row2(k,v){if(!v)return;d2.appendChild(H("dt",{text:k}));d2.appendChild(H("dd",{text:v}))}
  row2("Source",c.src);row2("Source read",c.check==="Not part of this check"?"Not read yet":c.check);row2("Source note",c.snote);
  b.appendChild(d2);return b;
}
function mountCases(root){
  var all=window.CA_CASES||[];
  var groups=[];all.forEach(function(c){if(groups.indexOf(c.group)<0)groups.push(c.group)});groups.sort();
  var fl=H("div",{"class":"filters"});
  function sel(label,opts){var s=H("select");opts.forEach(function(o){s.appendChild(H("option",{value:o[0],text:o[1]}))});var l=H("label",{text:label});l.appendChild(s);fl.appendChild(l);return s}
  var sRun=sel("Run",[["","All runs"],["1","Run 1: single controls"],["2","Run 2: controls working together"],["3","Run 3: new areas"],["4","Run 4: hand tests (not run)"],["5","Run 5: CI/CD, APIs, agents"]]);
  var sGrp=sel("Group",[["","All groups"]].concat(groups.map(function(g){return[g,g]})));
  var sRes=sel("Result",[["","Any"],["wrong","My guess was wrong"],["single","One control off lets it in"],["nosingle","No single control off lets it in"],["notrun","Not run"]]);
  var q=H("input",{type:"search",placeholder:"Search ID or words","aria-label":"Search cases"});var ql=H("label",{text:"Search"});ql.appendChild(q);fl.appendChild(ql);
  var cnt=H("p",{"class":"count","aria-live":"polite"}),list=H("div",{"class":"clist"});
  root.appendChild(fl);root.appendChild(cnt);root.appendChild(list);
  var items=all.map(function(c){
    var d=H("details",{"class":"citem"});var s=H("summary");
    s.appendChild(H("span",{"class":"cid",text:c.id}));s.appendChild(H("span",{text:c.use}));
    var tg=H("span",{"class":"tagrow"});tg.style.margin="0";
    tg.appendChild(H("span",{"class":"tag",text:runLabel(c.run)}));
    if(!c.res)tg.appendChild(H("span",{"class":"tag warn",text:"Not run"}));else if(c.match===false)tg.appendChild(H("span",{"class":"tag bad",text:"Guess wrong"}));else tg.appendChild(H("span",{"class":"tag good",text:"Guess matched"}));
    s.appendChild(tg);d.appendChild(s);
    var done=false;d.addEventListener("toggle",function(){if(d.open&&!done){d.appendChild(caseBody(c));done=true}});
    list.appendChild(d);return {c:c,d:d};
  });
  function singleIn(c){return c.res&&c.res.length===5&&c.res.slice(2).some(function(x){return x==="in"})}
  function apply(){var n=0,t=q.value.trim().toLowerCase();
    items.forEach(function(it){var c=it.c,ok=true;
      if(sRun.value&&String(c.run)!==sRun.value)ok=false;
      if(sGrp.value&&c.group!==sGrp.value)ok=false;
      if(sRes.value==="wrong"&&c.match!==false)ok=false;
      if(sRes.value==="notrun"&&c.res)ok=false;
      if(sRes.value==="single"&&!(c.res&&c.res.length===5&&singleIn(c)))ok=false;
      if(sRes.value==="nosingle"&&!(c.res&&c.res.length===5&&!singleIn(c)))ok=false;
      if(t&&(c.id+" "+c.use+" "+c.group).toLowerCase().indexOf(t)<0)ok=false;
      it.d.hidden=!ok;if(ok)n++});
    cnt.textContent=n+" of "+items.length+" cases shown"}
  [sRun,sGrp,sRes].forEach(function(s){s.addEventListener("change",apply)});q.addEventListener("input",apply);apply();
}
window.CAFW={mountFlows:mountFlows,mountCases:mountCases,FLOWS:FLOWS};
document.addEventListener("DOMContentLoaded",function(){
  var a=document.getElementById("flows-root");if(a)mountFlows(a);
  var b=document.getElementById("cases-root");if(b&&window.CA_CASES)mountCases(b);
});
})();
