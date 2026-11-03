// Home page: "What brings you here?" Shows one of three paths at a time and remembers the choice
// on this device. Without this script every path is visible, so nothing is lost.
(function () {
  var sec = document.getElementById('start-here');
  var bar = sec && sec.querySelector('.who');
  if (!bar) return;
  var tabs = [].slice.call(bar.querySelectorAll('[role="tab"]'));
  var KEY = 'rt-who';

  function pick(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
    if (focus) tab.focus();
    try { localStorage.setItem(KEY, tab.id); } catch (e) {}
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  var first = document.getElementById(saved) || tabs[0];
  if (tabs.indexOf(first) < 0) first = tabs[0];

  bar.hidden = false;
  sec.classList.add('who-on');
  pick(first, false);

  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { pick(t, false); });
    t.addEventListener('keydown', function (e) {
      var n = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = tabs[(i + 1) % tabs.length];
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === 'Home') n = tabs[0];
      else if (e.key === 'End') n = tabs[tabs.length - 1];
      if (n) { e.preventDefault(); pick(n, true); }
    });
  });
})();
