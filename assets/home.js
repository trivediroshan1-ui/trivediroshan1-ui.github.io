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
