(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }
  function verdictClass(v) { return v === "as expected" ? "ok" : v === "info" ? "info" : "diff"; }
  function verdictText(v) { return v === "as expected" ? "As expected" : v === "info" ? "For information" : "Not what I guessed"; }
  function fmt(iso) { try { return new Date(iso).toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" }); } catch (e) { return iso; } }
  function stepText(s) {
    var parts = [];
    Object.keys(s).forEach(function (k) {
      if (k === "note") return;
      var v = s[k]; if (v === undefined || v === null || v === "") return;
      var sv = typeof v === "object" ? JSON.stringify(v) : String(v); if (sv.length > 240) sv = sv.slice(0, 240) + "…"; parts.push(k + ": " + sv);
    });
    return parts.join(" · ");
  }
  function render(d) {
    var meta = $("res-meta"); meta.textContent = "";
    var env = d.environment || {};
    meta.appendChild(el("p", "body-text", "Run on " + fmt(d.startedAt) + ". Node " + (env.node || "?") + ", " + (env.os || "?") + ", gateway commit " + (env.gatewayCommit || "?") + "."));
    if (d.runBy) meta.appendChild(el("p", "res-line", d.runBy));
    if (d.preview) { var b = $("res-banner"); b.hidden = false; b.textContent = d.previewNote || "Preview data from a cloud test run. This will be replaced by the run on my own laptop."; }

    var t = $("res-tally"); t.hidden = false; t.textContent = "";
    var tl = d.tally || {};
    [["Cases run", d.total, ""], ["As expected", tl["as expected"] || 0, ""], ["Not what I guessed", tl["different from prediction"] || 0, "diff"], ["For information", tl.info || 0, ""]].forEach(function (x) {
      var tile = el("div", "res-tile " + x[2]); tile.appendChild(el("b", "", String(x[1]))); tile.appendChild(el("span", "", x[0])); t.appendChild(tile);
    });

    var bar = $("res-bar"); if (bar) { bar.hidden = false; [["as expected", "#059669"], ["different from prediction", "#d97706"], ["info", "#64748b"]].forEach(function (p) { var n = tl[p[0]] || 0; if (!n) return; var s = el("div"); s.style.cssText = "background:" + p[1] + ";width:" + (100 * n / d.total) + "%"; s.title = n + " " + p[0]; bar.appendChild(s); }); }
    var diffs = d.cases.filter(function (c) { return c.verdict === "different from prediction"; });
    if (diffs.length && $("res-findings")) {
      $("res-findings").hidden = false; var ul = $("res-findings-list");
      diffs.forEach(function (c) { var li = el("li"); li.appendChild(el("strong", "", c.id + " " + c.title + ". ")); li.appendChild(document.createTextNode("I expected " + c.expected + ". It gave " + c.observed + ".")); ul.appendChild(li); });
    }

    var groups = []; d.cases.forEach(function (c) { if (groups.indexOf(c.group) < 0) groups.push(c.group); });
    var current = "All"; var list = $("res-list"); var filters = $("res-filters");
    function draw() {
      list.textContent = ""; var last = null;
      d.cases.forEach(function (c) {
        if (current !== "All" && c.group !== current) return;
        if (c.group !== last) { list.appendChild(el("h3", "res-group", c.group)); last = c.group; }
        var det = el("details", "res-case"); var sm = el("summary");
        sm.appendChild(el("span", "res-id", c.id)); sm.appendChild(el("span", "res-title", c.title));
        sm.appendChild(el("span", "res-badge " + verdictClass(c.verdict), verdictText(c.verdict))); det.appendChild(sm);
        var body = el("div", "res-body"); var dl = el("dl");
        [["Expected", c.expected], ["Got", c.observed]].forEach(function (p) { dl.appendChild(el("dt", "", p[0])); dl.appendChild(el("dd", "", String(p[1]))); });
        body.appendChild(dl);
        var steps = (c.steps || []).filter(function (s) { return s && typeof s === "object"; });
        if (steps.length) { var ol = el("ol", "res-steps"); steps.forEach(function (s) { var li = el("li"); if (s.note) li.appendChild(el("strong", "", s.note + ". ")); li.appendChild(el("code", "", stepText(s))); ol.appendChild(li); }); body.appendChild(ol); }
        det.appendChild(body); list.appendChild(det);
      });
    }
    ["All"].concat(groups).forEach(function (g) {
      var btn = el("button", "", g); btn.type = "button"; btn.setAttribute("aria-pressed", g === current ? "true" : "false");
      btn.addEventListener("click", function () { current = g; Array.prototype.forEach.call(filters.children, function (x) { x.setAttribute("aria-pressed", x === btn ? "true" : "false"); }); draw(); });
      filters.appendChild(btn);
    });
    draw();
  }
  fetch("/assets/data/mcp-usecase-results.json", { cache: "no-cache" }).then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); }).then(render).catch(function () { var m = $("res-meta"); m.textContent = ""; m.appendChild(el("p", "body-text", "The results file could not be loaded. Please try again in a minute.")); });
})();
