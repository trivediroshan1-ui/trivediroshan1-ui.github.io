(function(){
  var root=document.getElementById('mcp-flow'); if(!root) return;
  var DATA=window.__FLOW; if(!DATA) return;
  var GL={pass:['✓','passed'],skip:['–','not needed'],stop:['✕','stopped here'],warn:['?','unknown']};
  var NAMES=['Request','Policy gate','A person','Grant','Execute','Audit'];
  var CLS=['hg-neutral','hg-policy','hg-person','hg-policy','hg-exec','hg-audit'];
  var OUT={exec:['hg-exec','Executed'],refuse:['hg-refuse','Refused'],unknown:['hg-audit','Unknown outcome']};
  var track=document.getElementById('fl-track'), res=document.getElementById('fl-result');
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function show(k){
    var d=DATA[k]; if(!d) return;
    track.innerHTML=d.st.map(function(s,i){var g=GL[s[0]];
      return '<li class="fl-stage '+CLS[i]+' is-'+s[0]+'"><span class="fl-n">0'+(i+1)+'</span><b>'+NAMES[i]+'</b><span class="fl-state"><i aria-hidden="true">'+g[0]+'</i><span>'+g[1]+'</span></span><span class="fl-note">'+esc(s[1])+'</span></li>'}).join('');
    var o=OUT[d.outcome];
    res.innerHTML='<span class="hg-badge '+o[0]+'">'+o[1]+'</span><h3>'+esc(d.title)+'</h3><p>'+esc(d.text)+'</p><p class="fl-tests">Tested as '+d.tests.map(function(t){return '<a href="'+t[1]+'">'+esc(t[0])+'</a>'}).join(' ')+'</p>';
  }
  root.querySelectorAll('.hg-chip').forEach(function(b){
    b.addEventListener('click',function(){
      root.querySelectorAll('.hg-chip').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
      show(b.getAttribute('data-s'));
    });
  });
})();
