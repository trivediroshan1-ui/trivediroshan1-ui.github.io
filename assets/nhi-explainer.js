/* Explainer player: six scenes, play and pause, step, replay. No sound, nothing flashes.
   With reduced motion it starts paused. Without scripts every scene is shown (the .nojs class). */
(function () {
  var root = document.getElementById('nex');
  if (!root) return;
  var scenes = Array.prototype.slice.call(root.querySelectorAll('.nex-scene'));
  var caps = null;
  var capEl = document.getElementById('nex-cap');
  var bar = document.getElementById('nex-bar');
  var ctl = document.getElementById('nex-ctl');
  var play = document.getElementById('nex-play');
  var dots = Array.prototype.slice.call(root.querySelectorAll('[data-go]'));
  var trans = Array.prototype.slice.call(document.querySelectorAll('.nex-trans li'));
  caps = trans.map(function (li) { return li.textContent.replace(/^[^.]*\.\s*/, ''); });
  var durs = scenes.map(function (s) { return parseFloat(s.dataset.d) || 8; });
  var total = durs.reduce(function (a, b) { return a + b; }, 0);
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur = 0, elapsed = 0, playing = false, timer = null, userMoved = false;

  root.classList.remove('nojs');
  ctl.hidden = false;

  function startOf(i) { var t = 0; for (var k = 0; k < i; k++) t += durs[k]; return t; }

  function show(i, fromUser) {
    cur = Math.max(0, Math.min(scenes.length - 1, i));
    scenes.forEach(function (s, k) { s.classList.toggle('on', k === cur); });
    dots.forEach(function (d, k) { if (k === cur) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
    if (caps[cur]) {
      if (fromUser && !userMoved) { capEl.setAttribute('aria-live', 'polite'); userMoved = true; }
      capEl.textContent = caps[cur];
    }
    elapsed = startOf(cur);
    paint();
  }
  function paint() { bar.style.width = Math.min(100, elapsed / total * 100) + '%'; }
  function tick() {
    elapsed += 0.1;
    if (elapsed >= startOf(cur) + durs[cur]) {
      if (cur >= scenes.length - 1) { setPlaying(false); elapsed = total; paint(); return; }
      show(cur + 1, false); return;
    }
    paint();
  }
  function setPlaying(on) {
    playing = on;
    clearInterval(timer);
    if (on) timer = setInterval(tick, 100);
    play.textContent = on ? 'Pause' : (elapsed >= total ? 'Play again' : 'Play');
    play.setAttribute('aria-pressed', on ? 'false' : 'true');
  }

  play.addEventListener('click', function () {
    if (!playing && elapsed >= total) show(0, true);
    setPlaying(!playing);
  });
  document.getElementById('nex-prev').addEventListener('click', function () { show(cur - 1, true); });
  document.getElementById('nex-next').addEventListener('click', function () { show(cur + 1, true); });
  document.getElementById('nex-replay').addEventListener('click', function () { show(0, true); setPlaying(true); });
  dots.forEach(function (d) { d.addEventListener('click', function () { show(parseInt(d.dataset.go, 10), true); }); });
  document.addEventListener('visibilitychange', function () { if (document.hidden && playing) setPlaying(false); });

  show(0, false);
  setPlaying(!reduce);
})();
