/* Homepage extras. The page works without this file; it only tidies the phone menu. */
(function () {
  var menu = document.querySelector(".menu");
  if (!menu) return;
  function close() { menu.removeAttribute("open"); }
  // Close after choosing a link, on Escape, and when tapping outside the menu.
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  document.addEventListener("click", function (e) { if (menu.open && !menu.contains(e.target)) close(); });
})();

/* Count-up for the stats strip. Without JavaScript the final numbers are already in the page. */
(function () {
  var nodes = document.querySelectorAll(".stats b[data-count]");
  if (!nodes.length || !("IntersectionObserver" in window)) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  function run(el) {
    var end = parseInt(el.getAttribute("data-count"), 10);
    var suffix = el.getAttribute("data-suffix") || "";
    var start = null, dur = 1100;
    function step(t) {
      if (start === null) start = t;
      var p = Math.min((t - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(end * eased) + (p === 1 ? suffix : "");
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); run(e.target); } });
  }, { threshold: 0.6 });
  nodes.forEach(function (n) { io.observe(n); });
})();
