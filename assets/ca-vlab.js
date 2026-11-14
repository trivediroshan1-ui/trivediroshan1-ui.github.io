/* Virtual lab: replays the lab's real script output for any case.
   Nothing is simulated in your browser. The numbers come from ca-mfa-lab/data/cases.js,
   which is generated from the result files the scripts wrote. */
(function(){
"use strict";
function H(tag,props,kids){var e=document.createElement(tag);for(var k in props){if(k==="text")e.textContent=props[k];else if(k==="class")e.className=props[k];else e.setAttribute(k,props[k])}(kids||[]).forEach(function(c){e.appendChild(c)});return e}
var ALL=(window.CA_CASES||[]).filter(function(c){return c.res});
var SENS=window.CA_SENS||[];
var root=document.getElementById("vlab-root");if(!root)return;
var st={id:null,col:1};

function pyList(a){return "["+a.map(function(x){return "'"+x+"'"}).join(", ")+"]"}
function pyTuple(a){return "("+a.map(function(x){return "'"+x+"'"}).join(", ")+(a.length===1?",":"")+")"}
function pyBool(v){return v===true?"True":v===false?"False":"None"}
function termLine(c){
  if(c.run===1){return c.id+" "+pyTuple(c.res)+" guess "+pyTuple(c.guess)+" limit "+pyBool(c.limres)+" "+(c.match?"OK":"MISMATCH "+(c.diffs||"")+(c.limdiff?" limit":""))}
  var ok=c.match?"OK":"MISMATCH "+(c.diffs||[]).join(",");
  return c.id+" "+pyList(c.res)+" guess "+pyList(c.guess)+" "+ok;
}
function colorize(pre,text){
  pre.innerHTML="";
  text.split("\n").forEach(function(line,i){
    if(i)pre.appendChild(document.createTextNode("\n"));
    line.split(/(\bin\b|\bout\b)/).forEach(function(p){
      if(p==="in"||p==="out"){var s=H("span",{"class":p,text:p});pre.appendChild(s)}else pre.appendChild(document.createTextNode(p))});
  });
}

var s1=H("div",{"class":"vstep"}),s2=H("div",{"class":"vstep"}),s3=H("div",{"class":"vstep"}),s4=H("div",{"class":"vstep"}),s5=H("div",{"class":"vstep"});
function stepHead(n,t,d){var w=H("div");w.appendChild(H("h3",{text:t}));if(d)w.appendChild(H("p",{"class":"fnote",text:d}));return [H("b",{text:String(n)}),w]}

/* step 1: pick */
var groups=[];ALL.forEach(function(c){if(groups.indexOf(c.group)<0)groups.push(c.group)});groups.sort();
var gsel=H("select",{"aria-label":"Group"});gsel.appendChild(H("option",{value:"",text:"All groups"}));groups.forEach(function(g){gsel.appendChild(H("option",{value:g,text:g}))});
var csel=H("select",{"aria-label":"Use case"});
var q=H("input",{type:"search",placeholder:"Search words or an ID such as W06","aria-label":"Search use cases"});
var h1=stepHead(1,"Pick a use case","Every case in Runs 1, 2, 3, 5 and 6 is here: 124 of the 130. The six hand tests (E01 to E06) have no script output.");
s1.appendChild(h1[0]);var b1=h1[1];
var f1=H("div",{"class":"filters"});[["Group",gsel],["Search",q],["Use case",csel]].forEach(function(p){var l=H("label",{text:p[0]});l.appendChild(p[1]);f1.appendChild(l)});
b1.appendChild(f1);s1.appendChild(b1);

/* step 2: guess */
var h2=stepHead(2,"Read what I wrote before running anything","Guesses were committed and hashed before any code existed.");
s2.appendChild(h2[0]);var b2=h2[1];var guessBox=H("div");b2.appendChild(guessBox);s2.appendChild(b2);

/* step 3: toggle */
var h3=stepHead(3,"Switch the controls","Pick one state and read the output for it. “Off A” means only control A is off, the rest are on.");
s3.appendChild(h3[0]);var b3=h3[1];var opts=H("div",{"class":"vopts",role:"group","aria-label":"Control state"});b3.appendChild(opts);s3.appendChild(b3);

/* step 4: output */
var h4=stepHead(4,"The script output","This is the line the script prints for this case, rebuilt from its saved result file.");
s4.appendChild(h4[0]);var b4=h4[1];var term=H("pre",{"class":"term","aria-live":"polite"});var verdict=H("p",{"class":"big","aria-live":"polite"});b4.appendChild(term);b4.appendChild(verdict);s4.appendChild(b4);

/* step 5: compare */
var h5=stepHead(5,"Compare, then break an assumption","Some results depend on a number I chose. Where I tested that, it is listed here.");
s5.appendChild(h5[0]);var b5=h5[1];var cmp=H("div");b5.appendChild(cmp);s5.appendChild(b5);

[s1,s2,s3,s4,s5].forEach(function(s){root.appendChild(s)});

function fillCases(){
  var t=q.value.trim().toLowerCase(),g=gsel.value;
  csel.innerHTML="";var n=0;
  ALL.forEach(function(c){if(g&&c.group!==g)return;if(t&&(c.id+" "+c.use).toLowerCase().indexOf(t)<0)return;n++;csel.appendChild(H("option",{value:c.id,text:c.id+" "+c.use}))});
  if(!n)csel.appendChild(H("option",{value:"",text:"No match"}));
  if(csel.options.length&&csel.value)choose(csel.value);
}
function byId(id){return ALL.filter(function(c){return c.id===id})[0]}
function choose(id){st.id=id;var c=byId(id);if(!c)return;st.col=Math.min(1,c.res.length-1);renderGuess(c);renderOpts(c);renderOut(c)}
function renderGuess(c){
  guessBox.innerHTML="";
  var p=H("p",{});p.appendChild(H("b",{text:c.id+". "}));p.appendChild(document.createTextNode(c.use));guessBox.appendChild(p);
  if(c.bad)guessBox.appendChild(H("p",{text:"Bad outcome I was counting: "+c.bad}));
  if(c.ctl)guessBox.appendChild(H("p",{text:"Controls: "+c.ctl}));
  if(c.g1){guessBox.appendChild(H("p",{text:"What I wrote: no control, "+c.g1.none+". With the control, "+c.g1.with+". Control off, "+c.g1.off+"."}));if(c.g1.limit)guessBox.appendChild(H("p",{text:"The limit I expected: "+c.g1.limit}))}
  var gp=H("pre",{"class":"term"});colorize(gp,"My guess: "+pyList(c.guess)+"   columns: "+c.cols.join(" | "));guessBox.appendChild(gp);
  if(c.assumes)guessBox.appendChild(H("p",{"class":"fnote",text:"Assumes: "+c.assumes}));
}
function renderOpts(c){
  opts.innerHTML="";
  c.cols.forEach(function(name,i){
    var dis=c.res[i]==="-";
    var b=H("button",{type:"button","aria-pressed":i===st.col?"true":"false",text:name+(dis?" (no such control)":"")});
    if(dis)b.disabled=true;
    b.addEventListener("click",function(){st.col=i;renderOpts(c);renderOut(c)});opts.appendChild(b);
  });
}
function renderOut(c){
  colorize(term,"$ python3 "+(c.run===1?"run1.py":"run"+c.run+".py")+"\n"+termLine(c));
  var v=c.res[st.col],g=c.guess[st.col];
  verdict.textContent=c.cols[st.col]+": "+v+". I guessed "+g+". "+(v===g?"They agree.":"They differ.")+(v==="in"?" The bad outcome happens.":v==="out"?" The bad outcome does not happen.":"");
  cmp.innerHTML="";
  cmp.appendChild(H("p",{text:c.match?"Every column agreed with my guess for this case.":"At least one column differed from my guess (columns marked: "+(c.diffs||[]).join(", ")+")."}));
  if(c.note)cmp.appendChild(H("p",{text:"My reasoning: "+c.note}));
  var rel=SENS.filter(function(x){return x.flips.some(function(f){return f.id===c.id})});
  if(rel.length){
    cmp.appendChild(H("p",{text:"Assumptions that change this result when I vary them one at a time:"}));
    var ul=H("ul");rel.forEach(function(x){var f=x.flips.filter(function(y){return y.id===c.id})[0];ul.appendChild(H("li",{text:x.change+": "+pyList(f.was)+" becomes "+pyList(f.now)}))});cmp.appendChild(ul);
  }else if(c.run===5||c.run===6)cmp.appendChild(H("p",{"class":"fnote",text:"None of the assumption changes I tried for Run "+c.run+" alters this case."}));
  else cmp.appendChild(H("p",{"class":"fnote",text:"I only ran the assumption sensitivity test for Runs 5 and 6."}));
}
gsel.addEventListener("change",fillCases);q.addEventListener("input",fillCases);csel.addEventListener("change",function(){choose(csel.value)});
var start=ALL.filter(function(c){return c.id==="W06"})[0]||ALL[0];
fillCases();if(start){csel.value=start.id;choose(start.id)}
})();
