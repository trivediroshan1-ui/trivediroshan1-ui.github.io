/* Home page: a small button that stops or restarts the page's animations (WCAG 2.2.2).
   The choice is remembered on this device. Hidden when the device already asks for reduced motion. */
(function () {
  "use strict";
  var root = document.documentElement, KEY = "rt-motion";
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  if (read() === "off") root.classList.add("motion-off");
  var PAUSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/></svg>';
  var PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>';
  function init() {
    if (document.querySelector(".motion-toggle")) return;
    var b = document.createElement("button");
    b.type = "button";
    b.className = "motion-toggle";
    function label() {
      var off = root.classList.contains("motion-off");
      b.setAttribute("aria-pressed", off ? "true" : "false");
      b.setAttribute("aria-label", off ? "Play animations" : "Pause animations");
      b.title = off ? "Play animations" : "Pause animations";
      b.innerHTML = off ? PLAY : PAUSE;
    }
    b.addEventListener("click", function () {
      var off = root.classList.toggle("motion-off");
      save(off ? "off" : "on");
      label();
    });
    label();
    document.body.appendChild(b);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
