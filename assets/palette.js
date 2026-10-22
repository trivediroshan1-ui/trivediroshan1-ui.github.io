/* Site search: press Ctrl+K (or Cmd+K, or /) or use the search button in the menu.
   Plain JavaScript, no libraries. The list comes from /assets/palette-data.js (scripts/build-palette.py). */
(function () {
  var V = "20261022b", data = null, dlg, input, list, status, opener, active = -1, shown = [];
  var css = ".rt-sbtn{display:inline-flex;align-items:center;gap:6px;min-height:40px;padding:0 12px;border-radius:999px;border:1px solid rgba(167,139,250,.35);background:transparent;color:inherit;font:600 14px/1 'DM Sans',system-ui,sans-serif;cursor:pointer;opacity:.9}" +
    ".rt-sbtn:hover{opacity:1;border-color:#a78bfa;background:rgba(124,58,237,.14)}.rt-sbtn svg{width:16px;height:16px}.rt-sbtn kbd{font:600 11px/1 'JetBrains Mono',monospace;padding:3px 5px;border-radius:5px;border:1px solid rgba(167,139,250,.35);opacity:.8}" +
    "@media (max-width:760px){.rt-sbtn kbd,.rt-sbtn .lbl{display:none}.rt-sbtn{width:40px;padding:0;justify-content:center;border-color:transparent}}.hg-sitenav li.srch{display:flex;align-items:center}@media (max-width:440px){.hg-sitenav li a{padding:0 .24rem}.rt-sbtn{width:30px}.rt-sbtn svg{width:17px;height:17px}}" +
    ".rt-pal{position:fixed;inset:0;z-index:1000;display:none;align-items:flex-start;justify-content:center;padding:12vh max(16px,env(safe-area-inset-left,0px)) 16px max(16px,env(safe-area-inset-right,0px));background:rgba(3,4,16,.62);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}" +
    ".rt-pal.on{display:flex}.rt-box{width:min(640px,100%);max-height:72vh;display:flex;flex-direction:column;border-radius:18px;border:1px solid rgba(167,139,250,.35);background:#0e0d2c;color:#f5f3ff;box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 60px rgba(124,58,237,.25);overflow:hidden;font-family:'DM Sans',system-ui,sans-serif}" +
    ".rt-in{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid rgba(167,139,250,.2)}.rt-in svg{width:20px;height:20px;flex:none;color:#a78bfa}" +
    ".rt-in input{flex:1;min-width:0;background:transparent;border:0;outline:0;color:inherit;font:500 17px/1.3 'DM Sans',system-ui,sans-serif}.rt-in input::placeholder{color:#9590b8}" +
    ".rt-in button{border:1px solid rgba(167,139,250,.35);background:transparent;color:#b9b4d8;border-radius:6px;font:600 12px/1 'JetBrains Mono',monospace;padding:6px 8px;cursor:pointer}" +
    ".rt-ls{list-style:none;margin:0;padding:6px;overflow-y:auto}.rt-ls li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 12px;padding:10px 12px;border-radius:12px;cursor:pointer}" +
    ".rt-ls li[aria-selected=true]{background:rgba(124,58,237,.24);box-shadow:inset 3px 0 0 #58e6f6}.rt-ls b{font-weight:600;font-size:15px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
    ".rt-ls small{grid-column:1;font-size:13px;color:#b9b4d8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.rt-ls i{grid-row:1;grid-column:2;font:600 12px/1.6 'JetBrains Mono',monospace;font-style:normal;color:#a78bfa}" +
    ".rt-ft .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.rt-ft{padding:9px 16px;border-top:1px solid rgba(167,139,250,.2);font-size:12px;color:#9590b8;display:flex;gap:14px;flex-wrap:wrap}.rt-empty{padding:18px 14px;color:#b9b4d8;font-size:14px}" +
    "@keyframes rt-read{from{transform:scaleX(0)}to{transform:scaleX(1)}}" +
    "@supports (animation-timeline:scroll()){:is(html:has(.cs-art),html:has(.post-glow),html:has(.hero-toc),html:has(.hg-tabs),html:has(.tl))::after{content:'';position:fixed;top:0;left:0;right:0;height:3px;z-index:1001;pointer-events:none;transform-origin:0 50%;background:linear-gradient(90deg,#58e6f6,#a78bfa);animation:rt-read linear both;animation-timeline:scroll(root)}}" +
    "html[data-theme=light] .rt-pal{background:rgba(21,18,46,.35)}html[data-theme=light] .rt-box{background:#fff;color:#15122e;border-color:rgba(76,52,160,.25);box-shadow:0 30px 80px rgba(21,18,46,.25)}" +
    "html[data-theme=light] .rt-ls small,html[data-theme=light] .rt-empty{color:#4a4470}html[data-theme=light] .rt-ls i,html[data-theme=light] .rt-in svg{color:#5b3cc4}html[data-theme=light] .rt-ls li[aria-selected=true]{background:rgba(124,58,237,.1);box-shadow:inset 3px 0 0 #5b3cc4}" +
    "html[data-theme=light] .rt-in input::placeholder,html[data-theme=light] .rt-ft{color:#5f5a85}html[data-theme=light] .rt-in button{color:#4a4470}";
  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>';
  var mac = /Mac|iPhone|iPad/.test(navigator.platform || "");

  function el(tag, attrs, htmlStr) { var e = document.createElement(tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (htmlStr) e.innerHTML = htmlStr; return e; }

  function build() {
    dlg = el("div", { "class": "rt-pal", role: "dialog", "aria-modal": "true", "aria-label": "Search this site" });
    dlg.innerHTML = '<div class="rt-box"><div class="rt-in">' + ICON +
      '<input type="text" role="combobox" aria-expanded="true" aria-controls="rt-ls" aria-autocomplete="list" aria-label="Search pages, case studies and writing" placeholder="Search: PAM, MCP, break-glass, résumé..." autocomplete="off" spellcheck="false">' +
      '<button type="button" aria-label="Close search">Esc</button></div>' +
      '<ul class="rt-ls" id="rt-ls" role="listbox" aria-label="Results"></ul>' +
      '<p class="rt-ft"><span>&uarr; &darr; to move</span><span>Enter to open</span><span>Esc to close</span><span class="sr" aria-live="polite"></span></p></div>';
    document.body.appendChild(dlg);
    input = dlg.querySelector("input"); list = dlg.querySelector(".rt-ls"); status = dlg.querySelector(".sr");
    dlg.addEventListener("mousedown", function (e) { if (e.target === dlg) close(); });
    dlg.querySelector("button").addEventListener("click", close);
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); move(e.key === "ArrowDown" ? 1 : -1); }
      else if (e.key === "Enter") { e.preventDefault(); go(active); }
      else if (e.key === "Escape") { e.preventDefault(); close(); }
      else if (e.key === "Tab") { e.preventDefault(); }
    });
    list.addEventListener("click", function (e) { var li = e.target.closest("li[data-i]"); if (li) go(+li.getAttribute("data-i")); });
    list.addEventListener("mousemove", function (e) { var li = e.target.closest("li[data-i]"); if (li && +li.getAttribute("data-i") !== active) select(+li.getAttribute("data-i")); });
  }

  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function score(it, words) {
    var t = norm(it.t), all = t + " " + norm(it.d) + " " + norm(it.k) + " " + norm(it.g), s = 0;
    for (var i = 0; i < words.length; i++) {
      var w = words[i]; if (all.indexOf(w) < 0) return -1;
      s += t.indexOf(w) === 0 ? 30 : t.indexOf(w) > 0 ? 18 : norm(it.k).indexOf(w) >= 0 ? 8 : 4;
    }
    return s;
  }
  function render() {
    var q = norm(input.value).trim(), words = q.split(/\s+/).filter(Boolean);
    if (!words.length) shown = data.filter(function (it) { return it.g === "Page" || it.g === "Action" || it.u === "/labs/"; });
    else shown = data.map(function (it) { return [score(it, words), it]; }).filter(function (p) { return p[0] >= 0; })
      .sort(function (a, b) { return b[0] - a[0]; }).map(function (p) { return p[1]; });
    shown = shown.slice(0, 30);
    list.innerHTML = shown.length ? shown.map(function (it, i) {
      return '<li role="option" id="rt-o' + i + '" data-i="' + i + '" aria-selected="false"><b>' + esc(it.t) + '</b><i>' + esc(it.g) + '</i>' + (it.d ? '<small>' + esc(it.d) + '</small>' : '') + '</li>';
    }).join("") : '<li class="rt-empty" role="option" aria-disabled="true">Nothing matches that. Try a shorter word, like PAM, agent or audit.</li>';
    status.textContent = shown.length ? shown.length + " results" : "No results";
    active = -1; if (shown.length) select(0); else input.removeAttribute("aria-activedescendant");
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function select(i) {
    var old = list.querySelector('[aria-selected="true"]'); if (old) old.setAttribute("aria-selected", "false");
    active = i; var li = document.getElementById("rt-o" + i); if (!li) return;
    li.setAttribute("aria-selected", "true"); input.setAttribute("aria-activedescendant", li.id); li.scrollIntoView({ block: "nearest" });
  }
  function move(d) { if (shown.length) select((active + d + shown.length) % shown.length); }
  function go(i) { var it = shown[i]; if (!it) return; close(true); if (/^https?:/.test(it.u)) window.open(it.u, "_blank", "noopener"); else location.href = it.u; }

  function load(cb) {
    if (data) return cb();
    var s = document.createElement("script"); s.src = "/assets/palette-data.js?v=" + V;
    s.onload = function () { data = window.RT_PALETTE || []; cb(); }; s.onerror = function () { data = []; cb(); };
    document.head.appendChild(s);
  }
  function open() {
    opener = document.activeElement; if (!dlg) build();
    load(function () { dlg.classList.add("on"); document.documentElement.style.overflow = "hidden"; input.value = ""; render(); input.focus(); });
  }
  function close(leaving) {
    if (!dlg) return; dlg.classList.remove("on"); document.documentElement.style.overflow = "";
    if (!leaving && opener && opener.focus) opener.focus();
  }

  document.addEventListener("keydown", function (e) {
    var k = (e.key || "").toLowerCase(), typing = /input|textarea|select/i.test((e.target.tagName || "")) || e.target.isContentEditable;
    if ((k === "k" && (e.metaKey || e.ctrlKey)) || (k === "/" && !typing && !e.metaKey && !e.ctrlKey && !e.altKey)) {
      e.preventDefault(); if (dlg && dlg.classList.contains("on")) close(); else open();
    }
  });

  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  function addButton() {
    var b = el("button", { type: "button", "class": "rt-sbtn", "aria-label": "Search this site", title: "Search (" + (mac ? "⌘" : "Ctrl") + " K)" },
      ICON + '<span class="lbl">Search</span><kbd>' + (mac ? "⌘K" : "Ctrl K") + "</kbd>");
    b.addEventListener("click", open);
    var res = document.querySelector("nav.hg-sitenav li.res");
    if (res) { var li = el("li", { "class": "srch" }); li.appendChild(b); res.parentNode.insertBefore(li, res); return; }
    var hb = document.querySelector("header.top .btn-res");
    if (hb) { hb.parentNode.insertBefore(b, hb); }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", addButton); else addButton();
})();
