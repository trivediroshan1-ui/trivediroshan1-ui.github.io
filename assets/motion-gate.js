/* Pauses CSS animations that are scrolled out of view, so only what you can see is running.
 * Adds "in-view" to animated elements on screen and "mg-off" (paused, see sitebar.css) to the rest.
 * Does nothing to the pause button or to prefers-reduced-motion; those still win. */
(function () {
  "use strict";
  if (!("IntersectionObserver" in window) || !document.getAnimations) return;
  var watched = new WeakSet();
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      e.target.classList.toggle("in-view", e.isIntersecting);
      e.target.classList.toggle("mg-off", !e.isIntersecting);
    });
  }, { rootMargin: "80px 0px" });
  function scan() {
    document.getAnimations().forEach(function (a) {
      var t = a.effect && a.effect.target;
      if (!t || !t.nodeType || a.animationName === undefined || watched.has(t)) return;
      watched.add(t); io.observe(t);
    });
  }
  function start() { scan(); setTimeout(scan, 1500); setTimeout(scan, 5000); }
  if (document.readyState === "complete") start(); else window.addEventListener("load", start);
})();
