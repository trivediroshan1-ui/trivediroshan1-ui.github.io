// Hiring brief: switch between the four role panels, keep the choice in the address so the link can be forwarded,
// and copy that link. Nothing is sent anywhere.
(function () {
  var tabs = [].slice.call(document.querySelectorAll('.hr-tabs [role="tab"]'));
  if (!tabs.length) return;
  var done = document.getElementById('hr-done');

  function show(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
    if (focus) tab.focus();
    if (done) done.textContent = '';
  }
  function fromHash() {
    var id = (location.hash || '').slice(1);
    var t = tabs.filter(function (x) { return x.getAttribute('aria-controls') === id; })[0];
    if (t) show(t, false);
  }

  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () {
      show(t, false);
      try { history.replaceState(null, '', '#' + t.getAttribute('aria-controls')); } catch (e) {}
    });
    t.addEventListener('keydown', function (e) {
      var k = e.key, j = -1;
      if (k === 'ArrowRight' || k === 'ArrowDown') j = (i + 1) % tabs.length;
      else if (k === 'ArrowLeft' || k === 'ArrowUp') j = (i + tabs.length - 1) % tabs.length;
      else if (k === 'Home') j = 0;
      else if (k === 'End') j = tabs.length - 1;
      if (j < 0) return;
      e.preventDefault();
      show(tabs[j], true);
      try { history.replaceState(null, '', '#' + tabs[j].getAttribute('aria-controls')); } catch (e2) {}
    });
  });
  window.addEventListener('hashchange', fromHash);
  fromHash();

  var btn = document.getElementById('hr-copy');
  if (btn) btn.addEventListener('click', function () {
    var url = location.href;
    var ok = function () { if (done) done.textContent = 'Link copied.'; };
    var no = function () { if (done) done.textContent = 'Could not copy. Copy the address from your browser instead.'; };
    var old = function () {
      var t = document.createElement('textarea');
      t.value = url; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy') ? ok() : no(); } catch (e) { no(); }
      t.remove();
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(ok, old);
    else old();
  });
})();
