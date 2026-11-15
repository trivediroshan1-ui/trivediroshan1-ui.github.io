/* Privacy-safe event counts for roshantrivedi.co.in.
 *
 * Counts a few named actions so I can see which labs, books and downloads
 * people actually use. No cookies, no IDs, nothing stored in the browser,
 * no IP address kept by the counter (see workers/events/).
 * Respects Do Not Track and Global Privacy Control: if either is on,
 * nothing is sent.
 *
 * OFF until the counter is deployed: set ON to true in the same PR that
 * confirms /e answers 204. Event list and wording: /privacy/.
 */
(function () {
  "use strict";
  var ON = false;
  if (!ON || !navigator.sendBeacon) return;
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1" || navigator.globalPrivacyControl) return;

  var path = location.pathname.slice(0, 120);
  var sent = {};
  function send(e, p, once) {
    var key = e + "|" + (p || "");
    if (once && sent[key]) return;
    sent[key] = 1;
    try {
      navigator.sendBeacon("/e", JSON.stringify({ e: e, p: String(p || "").slice(0, 80), path: path }));
    } catch (err) { /* counting must never break the page */ }
  }

  var LAB = (path.match(/^\/(nhi-lab|ai-governance-lab|ca-mfa-lab|mcp-lab)\//) || [])[1];
  var FILE = /\.(pdf|csv|json|zip|vcf|txt)$|^\/assets\/qr\//i;

  // Downloads: books, papers, data files, the contact card, the QR codes.
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[href]");
    if (a) {
      var u;
      try { u = new URL(a.href, location.href); } catch (err) { return; }
      if (u.origin === location.origin && FILE.test(u.pathname)) send("download", u.pathname, true);
      return;
    }
    // Lab use: the first button pressed inside a lab page, once per lab.
    var b = LAB && ev.target.closest && ev.target.closest("main button");
    if (b) send("lab_use", LAB, true);
  }, true);

  // Subscribe clicks (the form itself goes to Buttondown, as before).
  document.addEventListener("submit", function (ev) {
    var f = ev.target;
    if (f && /buttondown\.com/.test(f.action || "")) send("subscribe", path, true);
  }, true);

  // Video plays, once per video.
  document.addEventListener("play", function (ev) {
    var v = ev.target;
    if (v && v.tagName === "VIDEO") {
      var src = (v.currentSrc || "").split("/").pop().split("?")[0];
      send("video_play", src, true);
    }
  }, true);

  // Reading: 75% of an article or case study, once per page.
  if (/^\/(writing|case-studies)\/./.test(path)) {
    var main = document.querySelector("main");
    if (main) {
      var onScroll = function () {
        var r = main.getBoundingClientRect();
        if (window.innerHeight - r.top >= r.height * 0.75) {
          send("read_75", path, true);
          window.removeEventListener("scroll", onScroll);
        }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
    }
  }

  // Search with no result (the palette or /search/): only the length of what was typed, never the words.
  var t;
  document.addEventListener("input", function (ev) {
    var i = ev.target;
    if (!i || !i.closest || !i.closest(".rt-box, [data-search]")) return;
    clearTimeout(t);
    t = setTimeout(function () {
      if (document.querySelector(".rt-empty, [data-search-empty]")) {
        var n = (i.value || "").trim().length;
        send("search_none", n < 4 ? "1-3" : n < 9 ? "4-8" : "9+", false);
      }
    }, 1500);
  }, true);
})();
