/* Book page: copy buttons, link copy, toast. Nothing is sent anywhere. */
(function () {
  "use strict";
  var toastT;
  function $(s) { return document.querySelector(s); }
  function toast(msg) {
    var t = $("#toast"); if (!t) return;
    t.textContent = msg; t.classList.add("on");
    clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 1800);
  }
  function copy(text, msg) {
    function fallback() {
      var ta = document.createElement("textarea"); ta.value = text; ta.setAttribute("readonly", "");
      ta.style.position = "fixed"; ta.style.opacity = "0"; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); toast(msg || "Copied"); } catch (e) { toast("Select and copy by hand"); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast(msg || "Copied"); }, fallback);
    else fallback();
  }
  Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (b) {
    b.addEventListener("click", function () { copy(b.getAttribute("data-copy"), "Checksum copied"); });
  });
  var cl = $("#copyLink");
  if (cl) cl.addEventListener("click", function () { copy("https://roshantrivedi.co.in/book/", "Link copied"); });
})();
