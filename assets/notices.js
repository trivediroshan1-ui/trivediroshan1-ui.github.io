/* Keeps the blinking notices directly under the fixed header, even when the
   dismissible announcement bar above it is showing, and leaves room for them
   at the top of the hero so they never cover the first line. */
(function () {
  var header = document.querySelector(".site-header");
  var box = document.querySelector(".lab-notices");
  if (!header || !box) return;
  function place() {
    box.style.top = header.getBoundingClientRect().bottom + "px";
    document.documentElement.style.setProperty("--notice-h", box.offsetHeight + "px");
  }
  place();
  window.addEventListener("load", place);
  window.addEventListener("resize", place);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(place);
  if (window.MutationObserver) {
    new MutationObserver(place).observe(header, { attributes: true, attributeFilter: ["style"] });
  }
  if (window.ResizeObserver) new ResizeObserver(place).observe(box);
})();
