/* Home page only: once the hero has scrolled away, calm the moving background behind the reading sections.
   Pure presentation; the page works the same without it. */
(function () {
  "use strict";
  var hero = document.querySelector(".hero");
  if (!hero || !("IntersectionObserver" in window)) return;
  var root = document.documentElement;
  new IntersectionObserver(function (entries) {
    root.classList.toggle("past-hero", !entries[0].isIntersecting);
  }, { rootMargin: "-35% 0px 0px 0px" }).observe(hero);
})();
