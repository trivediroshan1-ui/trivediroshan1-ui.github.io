/* Case-study pages: reading time and a floating "On this page" list on wide screens.
   The pages read fine without this file. */
(function () {
  var main = document.querySelector("main");
  if (!main) return;
  var heads = Array.prototype.slice.call(main.querySelectorAll("h2")).filter(function (h) {
    return !h.closest("footer") && h.textContent.trim().length > 0;
  });

  // Reading time, added to the existing meta line
  var meta = main.querySelector(".meta");
  if (meta && !meta.querySelector(".rt-read")) {
    var words = (main.innerText || "").trim().split(/\s+/).length;
    var mins = Math.max(1, Math.round(words / 220));
    var span = document.createElement("span");
    span.className = "rt-read";
    span.textContent = " · " + mins + " min read";
    meta.appendChild(span);
  }

  if (heads.length < 4) return;
  var used = {};
  heads.forEach(function (h) {
    var host = h.closest("section[id]");
    if (host) { h.dataset.tocTarget = host.id; return; }
    if (!h.id) {
      var base = h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "section";
      var id = base, n = 2;
      while (used[id] || document.getElementById(id)) id = base + "-" + n++;
      h.id = id;
    }
    h.dataset.tocTarget = h.id;
    used[h.id] = true;
  });

  var nav = document.createElement("nav");
  nav.className = "rt-toc";
  nav.setAttribute("aria-label", "On this page");
  var title = document.createElement("p");
  title.textContent = "On this page";
  var list = document.createElement("ol");
  var links = {};
  heads.forEach(function (h) {
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = "#" + h.dataset.tocTarget;
    a.textContent = h.textContent.trim();
    li.appendChild(a);
    list.appendChild(li);
    links[h.dataset.tocTarget] = a;
  });
  nav.appendChild(title);
  nav.appendChild(list);
  document.body.appendChild(nav);

  function place() {
    var r = main.getBoundingClientRect();
    var left = r.right + 36;
    var room = window.innerWidth - left - 24;
    nav.style.left = left + "px";
    nav.style.width = Math.min(220, room) + "px";
    nav.hidden = room < 150;
  }
  place();
  window.addEventListener("resize", place);

  var current = null, ticking = false;
  function mark() {
    ticking = false;
    var line = window.innerHeight * 0.3, best = null;
    heads.forEach(function (h) { if (h.getBoundingClientRect().top <= line) best = h; });
    var a = best ? links[best.dataset.tocTarget] : null;
    if (a === current) return;
    if (current) current.removeAttribute("aria-current");
    if (a) a.setAttribute("aria-current", "true");
    current = a;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(mark); }
  }, { passive: true });
  mark();
})();
