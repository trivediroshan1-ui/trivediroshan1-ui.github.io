/* AI governance lab: plays the identity lifecycle step by step. Without script, or with reduced motion, all steps stay visible. */
(function () {
  "use strict";
  function reduced() { try { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) { return false; } }
  function btn(label, fn) { var b = document.createElement("button"); b.type = "button"; b.className = "agl-btn ghost"; b.textContent = label; b.addEventListener("click", fn); return b; }

  function init(root) {
    var ol = root.querySelector(".lc-steps");
    if (!ol) return;
    var steps = Array.prototype.slice.call(ol.querySelectorAll(".lc-step"));
    if (!steps.length) return;
    root.setAttribute("data-js", "1");
    var dot = document.createElement("span"); dot.className = "lc-dot"; dot.setAttribute("aria-hidden", "true"); ol.insertBefore(dot, ol.firstChild);
    var i = -1, timer = null, playing = false, visible = false, still = reduced();

    var bar = document.createElement("div"); bar.className = "lc-bar";
    var now = document.createElement("span"); now.className = "lc-now"; now.setAttribute("aria-live", "polite");
    var play = btn(still ? "Play" : "Pause", function () { toggle(); });
    var back = btn("Back", function () { stop(); go(Math.max(0, i - 1)); });
    var next = btn("Next", function () { stop(); go(Math.min(steps.length - 1, i + 1)); });
    var all = btn("Show all", function () { var on = root.getAttribute("data-all") === "1"; if (on) { root.removeAttribute("data-all"); all.textContent = "Show all"; } else { stop(); root.setAttribute("data-all", "1"); all.textContent = "Collapse"; } go(i < 0 ? 0 : i); });
    bar.appendChild(play); bar.appendChild(back); bar.appendChild(next); bar.appendChild(all); bar.appendChild(now);
    root.insertBefore(bar, ol);

    function go(n) {
      i = n;
      steps.forEach(function (s, k) { s.classList.toggle("cur", k === i); s.classList.toggle("done", k < i); });
      var s = steps[i];
      dot.style.transform = "translateY(" + (s.offsetTop + 14) + "px)";
      var h = s.querySelector("h4");
      now.textContent = "Step " + (i + 1) + " of " + steps.length + (h ? ": " + h.firstChild.textContent.trim() : "");
    }
    function tick() {
      if (!playing) return;
      go((i + 1) % steps.length);
      timer = setTimeout(tick, i === steps.length - 1 ? 4200 : 3600);
    }
    function start() { if (playing) return; root.removeAttribute("data-all"); all.textContent = "Show all"; playing = true; root.setAttribute("data-play", "1"); play.textContent = "Pause"; timer = setTimeout(tick, i < 0 ? 300 : 1200); }
    function stop() { playing = false; clearTimeout(timer); root.removeAttribute("data-play"); play.textContent = "Play"; }
    function toggle() { if (playing) stop(); else start(); }
    steps.forEach(function (s, k) { s.addEventListener("click", function (e) { if (e.target.closest && e.target.closest("a")) return; stop(); go(k); }); });
    window.addEventListener("resize", function () { if (i >= 0) go(i); });

    if (still) { play.textContent = "Play"; go(0); return; }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { visible = e.isIntersecting; if (visible && !playing && i < 0) start(); else if (!visible && playing) { stop(); } });
      }, { threshold: 0.25 }).observe(root);
    } else { start(); }
  }
  function boot() { Array.prototype.forEach.call(document.querySelectorAll(".lc"), init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
}());
