/* Runs the lab's own Python scripts in the browser with Pyodide, hosted on this site. Nothing is sent anywhere. */
(function(){
"use strict";
var RUNS={
  "6":{label:"Run 6: AI agent identity (10 cases)",script:"run6.py",guess:"guesses/guesses-run6.md",results:"results-run6.json"},
  "5":{label:"Run 5: CI/CD, APIs, agents, recovery (12 cases)",script:"run5.py",guess:"guesses/guesses-run5.md",results:"results-run5.json"},
  "3":{label:"Run 3: step-up, federation, mobile, passkeys (16 cases)",script:"run3.py",guess:"guesses/guesses-run3.md",results:"results-run3.json"},
  "2":{label:"Run 2: controls working together (45 cases)",script:"run2.py",guess:"guesses/guesses-run2.md",results:"results-run2.json"},
  "1":{label:"Run 1: single controls (41 cases, guesses inside the script)",script:"run1.py",guess:null,results:"results-run1.json"}
};
var EV="/ca-mfa-lab/evidence/", py=null, loading=null;
function $(id){return document.getElementById(id)}
function txt(u){return fetch(u,{cache:"no-cache"}).then(function(r){if(!r.ok)throw new Error(u+" "+r.status);return r.text()})}
function hex(buf){return Array.prototype.map.call(new Uint8Array(buf),function(b){return("0"+b.toString(16)).slice(-2)}).join("")}
function sha(s){return crypto.subtle.digest("SHA-256",new TextEncoder().encode(s)).then(hex)}
function say(t){$("rn-status").textContent=t}
function load(){
  if(py)return Promise.resolve(py);
  if(loading)return loading;
  say("Loading Python in your browser (about 13 MB, once). Nothing is sent anywhere.");
  loading=loadPyodide({indexURL:"/assets/pyodide/"}).then(function(p){py=p;say("Python is ready.");return p});
  return loading;
}
function pick(){
  var k=$("rn-run").value,R=RUNS[k];
  say("Loading "+R.script+" from the evidence folder.");
  return Promise.all([txt(EV+R.script),R.guess?txt(EV+R.guess):Promise.resolve("")]).then(function(v){
    $("rn-script").value=v[0];$("rn-guess").value=v[1];$("rn-guess-wrap").hidden=!R.guess;$("rn-out").textContent="";
    say("Loaded. Press Run. You can edit PARAMS in the script, or a guess in the guess file, and run again.");updHash();
  });
}
function updHash(){var R=RUNS[$("rn-run").value];if(!R.guess){$("rn-hash").textContent="";return}
  sha($("rn-guess").value).then(function(h){$("rn-hash").textContent="SHA-256 of the guess file as it is now: "+h})}
function run(){
  var k=$("rn-run").value,R=RUNS[k],out=$("rn-out");out.textContent="";$("rn-cmp").textContent="";
  var btn=$("rn-go");btn.disabled=true;
  load().then(function(p){
    say("Running "+R.script+" ...");
    var buf=[];p.setStdout({batched:function(s){buf.push(s)}});p.setStderr({batched:function(s){buf.push(s)}});
    try{p.FS.mkdirTree("/lab/guesses")}catch(e){}
    p.FS.writeFile("/lab/"+R.script,$("rn-script").value);
    if(R.guess)p.FS.writeFile("/lab/"+R.guess,$("rn-guess").value);
    try{p.FS.unlink("/lab/"+R.results)}catch(e){}
    p.globals.set("ARGV",[R.script].concat(R.guess?[R.guess]:[]));
    return p.runPythonAsync("import os, sys, runpy\nos.chdir('/lab')\nsys.argv = list(ARGV)\ntry:\n    runpy.run_path(sys.argv[0], run_name='__main__')\nexcept SystemExit as e:\n    if e.code not in (None, 0): print('Stopped:', e.code)\n").then(function(){
      out.textContent=buf.join("\n");
      var made=null;try{made=p.FS.readFile("/lab/"+R.results,{encoding:"utf8"})}catch(e){}
      if(!made){$("rn-cmp").textContent="No results file was written.";say("Finished.");return}
      return txt(EV+R.results).then(function(pub){
        $("rn-cmp").textContent=made===pub?"Your results file is byte for byte identical to the published "+R.results+".":"Your results file differs from the published "+R.results+". That is expected if you changed PARAMS or a guess.";
        say("Finished.");
      });
    });
  }).catch(function(e){say("Something went wrong: "+e.message)}).then(function(){btn.disabled=false});
}
document.addEventListener("DOMContentLoaded",function(){
  if(!$("rn-run"))return;
  var s=$("rn-run");Object.keys(RUNS).forEach(function(k){var o=document.createElement("option");o.value=k;o.textContent=RUNS[k].label;s.appendChild(o)});
  s.value="6";
  s.addEventListener("change",pick);$("rn-go").addEventListener("click",run);
  $("rn-reset").addEventListener("click",pick);$("rn-guess").addEventListener("input",updHash);
  pick();
});
})();
