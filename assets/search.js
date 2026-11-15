/* Full-text search for /search/. Loads the passage index the chat uses (assets/chatbot-index.json)
   and searches it here in the browser. Every word must appear; titles and headings count more.
   Results are grouped by page and link to the passage. The query is kept in the address (?q=). */
(function () {
  "use strict";
  var me = document.currentScript || document.querySelector('script[src*="search.js"]');
  var SRC = (me && me.getAttribute("data-index")) || "/assets/chatbot-index.json";
  var form = document.querySelector("form[data-search]"), q = document.getElementById("sr-q"),
      out = document.getElementById("sr-res"), n = document.getElementById("sr-n");
  if (!form || !q || !out || !n) return;
  var data = null, loading = null, t;

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function words(s) { return (s.toLowerCase().match(/[a-z0-9][a-z0-9'-]*/g) || []).filter(function (w) { return w.length > 1 || /\d/.test(w); }); }
  function load() {
    if (loading) return loading;
    n.textContent = "Loading the index…";
    loading = fetch(SRC).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
      data = d.map(function (p) {
        return { u: p.u, a: p.a, t: p.t || "", h: p.h || "", x: p.x || "", lt: (p.t || "").toLowerCase(), lh: (p.h || "").toLowerCase(), lx: (p.x || "").toLowerCase() };
      });
    }).catch(function () { n.textContent = "The search index did not load. Try again, or use the topics page."; });
    return loading;
  }
  function count(hay, w) { var c = 0, i = hay.indexOf(w); while (i >= 0 && c < 5) { c++; i = hay.indexOf(w, i + w.length); } return c; }
  function snippet(p, ws) {
    var i = -1;
    ws.some(function (w) { i = p.lx.indexOf(w); return i >= 0; });
    var start = Math.max(0, i - 90), s = p.x.slice(start, start + 260);
    var html = (start > 0 ? "…" : "") + esc(s) + (start + 260 < p.x.length ? "…" : "");
    ws.forEach(function (w) {
      html = html.replace(new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi"), "<mark>$1</mark>");
    });
    return html;
  }
  function run(push) {
    var raw = q.value.trim(), ws = words(raw);
    if (push && history.replaceState) history.replaceState(null, "", location.pathname + (raw ? "?q=" + encodeURIComponent(raw) : ""));
    out.innerHTML = "";
    form.removeAttribute("data-search-empty");
    if (!ws.length) { n.textContent = raw ? "Type at least two letters." : ""; return; }
    load().then(function () {
      if (!data || q.value.trim() !== raw) return;
      var phrase = ws.join(" "), pages = {}, order = [];
      data.forEach(function (p) {
        var s = 0;
        for (var i = 0; i < ws.length; i++) {
          var w = ws[i], c = count(p.lx, w), inT = p.lt.indexOf(w) >= 0, inH = p.lh.indexOf(w) >= 0;
          if (!c && !inT && !inH) return;
          s += c + (inT ? 4 : 0) + (inH ? 3 : 0);
        }
        if (ws.length > 1 && (p.lx.indexOf(phrase) >= 0 || p.lh.indexOf(phrase) >= 0)) s += 6;
        var g = pages[p.u];
        if (!g) { g = pages[p.u] = { best: p, score: s, hits: 0 }; order.push(g); }
        g.hits++;
        if (s > g.score) { g.best = p; g.score = s; }
      });
      order.forEach(function (g) { g.rank = g.score + Math.min(g.hits - 1, 4); });
      order.sort(function (a, b) { return b.rank - a.rank; });
      if (!order.length) {
        n.textContent = "Nothing matches “" + raw + "”. Try fewer or shorter words.";
        form.setAttribute("data-search-empty", "");
        return;
      }
      var top = order.slice(0, 40);
      n.textContent = order.length + (order.length === 1 ? " page matches." : " pages match.") + (order.length > 40 ? " Showing the first 40." : "");
      out.innerHTML = top.map(function (g) {
        var p = g.best, href = p.u + (p.a ? "#" + encodeURIComponent(p.a) : "");
        return '<li><h2><a href="' + esc(href) + '">' + esc(p.h && p.h !== p.t ? p.t + ": " + p.h : p.t) + "</a></h2>" +
          '<div class="u">' + esc(p.u) + "</div><p>" + snippet(p, ws) + "</p>" +
          (g.hits > 1 ? '<p class="more">' + (g.hits - 1) + " more " + (g.hits === 2 ? "match" : "matches") + ' on this page. <a href="' + esc(p.u) + '">Open the page</a></p>' : "") + "</li>";
      }).join("");
    });
  }
  form.addEventListener("submit", function (e) { e.preventDefault(); run(true); });
  q.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { run(true); }, 200); });
  q.addEventListener("focus", load, { once: true });
  try { var v = new URLSearchParams(location.search).get("q"); if (v) { q.value = v; run(false); } } catch (e) {}
})();
