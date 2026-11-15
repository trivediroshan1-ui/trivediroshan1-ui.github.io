/* Keeps looping animations from running when nobody is looking (PERF-03).
 * - Animations are grouped by the diagram they belong to (a .diagram-card, the CA chain figure,
 *   a figure, or the outermost svg), so the parts of one diagram stay in step.
 * - A diagram starts from the beginning when it first scrolls into view, plays three times, then stops.
 *   Off screen it is paused (class "mg-off", see sitebar.css).
 * - A diagram's own Pause button turns into "Play again" when it has stopped (event "mg:done");
 *   window.mgRestart(container) plays it three more times.
 * - The site-wide pause button and prefers-reduced-motion still win: they remove the animations.
 * - Leave an element looping with data-loop, e.g. the chat's typing dots. */
(function () {
  "use strict";
  if (!("IntersectionObserver" in window) || !document.getAnimations) return;
  var LOOPS = 3, KEEP = { "sc-typing-bounce": 1 };
  var groups = new Map(), byAnim = new WeakSet();

  function outerSvg(t) {
    var s = t.closest && t.closest("svg"), up;
    while (s && s.parentElement && (up = s.parentElement.closest("svg"))) s = up;
    return s;
  }
  function containerOf(t) {
    return t.closest(".diagram-card, .ca-chain, figure") || outerSvg(t) || t;
  }
  function endless(a) {
    try { return a.effect && a.effect.getTiming().iterations === Infinity; } catch (e) { return false; }
  }
  function prime(a) {
    try { a.effect.updateTiming({ iterations: LOOPS }); a.currentTime = 0; } catch (e) {}
  }
  function finish(c, g) {
    var live = g.anims.filter(function (a) { return a.playState !== "idle"; });
    Promise.all(live.map(function (a) { return a.finished.catch(function () {}); })).then(function () {
      if (g.run !== live.run) return;
      c.setAttribute("data-mg-done", "");
      c.dispatchEvent(new CustomEvent("mg:done", { bubbles: true }));
    });
    live.run = g.run;
  }
  function start(c) {
    var g = groups.get(c);
    if (!g) return;
    g.started = true; g.run = (g.run || 0) + 1;
    c.removeAttribute("data-mg-done");
    g.anims = g.anims.filter(function (a) { return a.playState !== "idle"; });
    g.anims.forEach(prime);
    finish(c, g);
  }
  window.mgRestart = start;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var g = groups.get(e.target);
      if (!g) return;
      g.visible = e.isIntersecting;
      g.targets.forEach(function (t) {
        t.classList.toggle("in-view", e.isIntersecting);
        t.classList.toggle("mg-off", !e.isIntersecting);
      });
      if (e.isIntersecting && !g.started) start(e.target);
    });
  }, { rootMargin: "80px 0px" });

  function scan() {
    document.getAnimations().forEach(function (a) {
      var t = a.effect && a.effect.target;
      if (!t || !t.nodeType || a.animationName === undefined || byAnim.has(a) || !endless(a)) return;
      if (KEEP[a.animationName] || t.closest("[data-loop]")) return;
      byAnim.add(a);
      var c = containerOf(t), g = groups.get(c);
      if (!g) {
        g = { anims: [], targets: [], started: false, visible: false };
        groups.set(c, g); io.observe(c);
      }
      g.anims.push(a);
      try { a.effect.updateTiming({ iterations: LOOPS }); } catch (e) {}
      if (g.targets.indexOf(t) < 0) { g.targets.push(t); t.classList.add(g.visible ? "in-view" : "mg-off"); }
      if (g.started) { prime(a); finish(c, g); }
    });
  }
  // The site-wide Play button brings the animations back as new ones: give them three more loops.
  var root = document.documentElement, wasOff = root.classList.contains("motion-off");
  new MutationObserver(function () {
    var off = root.classList.contains("motion-off");
    if (off === wasOff) return;
    wasOff = off;
    if (off) return;
    setTimeout(function () {
      groups.forEach(function (g) { g.started = false; });
      scan();
      groups.forEach(function (g, c) { if (g.visible) start(c); });
    }, 60);
  }).observe(root, { attributes: true, attributeFilter: ["class"] });

  // Animations that begin later (a diagram revealed on scroll, a tab switched) are picked up as they start.
  var pending = 0;
  document.addEventListener("animationstart", function () {
    if (!pending) pending = setTimeout(function () { pending = 0; scan(); }, 50);
  }, true);
  function go() { scan(); setTimeout(scan, 1500); setTimeout(scan, 5000); }
  if (document.readyState === "complete") go(); else window.addEventListener("load", go);
})();
