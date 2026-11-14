/* CA lab hero animation: adds a Pause button and stops the loop while the figure is off screen.
   Without this script the figure is a still picture with every link lit. */
(function () {
  "use strict";
  var fig = document.querySelector(".ca-chain");
  if (!fig) return;
  var still = false;
  try { still = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  if (still) return;
  var b = document.createElement("button");
  b.type = "button"; b.className = "ca-ctl"; b.textContent = "Pause animation"; b.setAttribute("aria-pressed", "false");
  b.addEventListener("click", function () {
    var p = fig.classList.toggle("is-paused");
    b.textContent = p ? "Play animation" : "Pause animation";
    b.setAttribute("aria-pressed", p ? "true" : "false");
  });
  fig.appendChild(b);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { fig.classList.toggle("is-off", !e.isIntersecting); });
    }, { threshold: 0.1 }).observe(fig);
  }
})();
