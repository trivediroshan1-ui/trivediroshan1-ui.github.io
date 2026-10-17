/* HumanGate MCP lab portal. No inline script on the page; data comes from /assets/data/portal.json. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var toastT;
  function toast(msg) { var t = $("#toast"); t.textContent = msg; t.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 1800); }
  function copy(text, msg) {
    function fallback() {
      var ta = el("textarea"); ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0"; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); toast(msg || "Copied"); } catch (e) { toast("Select and copy by hand"); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast(msg || "Copied"); }, fallback); else fallback();
  }

  /* ---------- the policy, as the lab gateway reads it ---------- */
  var ORDER = ["public", "internal", "confidential", "restricted"], CLS = [0, 8, 16, 26];
  var LCOL = { critical: "var(--ro)", high: "var(--vi)", medium: "var(--am)", low: "var(--em)" };
  var LSOFT = { critical: "var(--ro-s)", high: "var(--vi-s)", medium: "var(--am-s)", low: "var(--em-s)" };
  function evaluate(p) {
    var parts = [];
    function add(k, label, v, col) { if (v) parts.push({ k: k, label: label, v: v, col: col }); }
    var cls = Math.max(ORDER.indexOf(p.sens), ORDER.indexOf(p.req));
    add("base", "Base risk of the tool", p.base, "#60a5fa");
    add("cls", "Data class (" + ORDER[cls] + ")", CLS[cls], "#4de2ff");
    add("prod", "Production", (p.env === "production" || p.fProd) ? 18 : 0, "#a78bfa");
    add("sc", "Scopes (" + p.scopes + " x 6, at most 18)", Math.min(18, 6 * p.scopes), "#34d399");
    add("sh", "Short justification", p.short ? 15 : 0, "#fbbf24");
    add("fl", "Flags", (p.fCred ? 12 : 0) + (p.fPriv ? 12 : 0) + (p.fProd ? 10 : 0) + (p.fDest ? 14 : 0), "#fb7185");
    var raw = parts.reduce(function (a, b) { return a + b.v; }, 0), score = Math.min(100, raw);
    var level = score >= 85 ? "critical" : score >= 65 ? "high" : score >= 35 ? "medium" : "low";
    var role = null;
    if (level !== "low") role = (level === "critical" || p.fDest || p.fPriv || p.fProd) ? "security-lead" : (level === "high" || p.fCred) ? "security-analyst" : "resource-owner";
    var win = { low: 60, medium: 30, high: 15, critical: 10 }[level];
    return { parts: parts, raw: raw, score: score, level: level, role: role, win: win };
  }

  /* ---------- stages ---------- */
  var STAGES = [
    { n: 1, name: "Request", c: "#60a5fa", what: "The agent asks for a tool, an action and a resource. The input rules run first: shape, length, tool known, action and resource allowed.",
      held: ["An approval id of 5,000 characters is refused as invalid_arguments (it used to give the wrong error; fixed).", "A tool that is not in the list is unknown, so an agent cannot reach it."],
      broke: ["Only three actor types exist: ai-agent, service-account and human-user. A robot or an RPA bot is denied, not mapped."], ids: ["B1", "B7", "T22", "E1", "U11i", "I3", "I4"] },
    { n: 2, name: "Policy", c: "#4de2ff", what: "The gateway scores the request, picks a risk level, runs the hostile-text check and the scope check. Low risk runs at once. Anything higher waits for a person with the right role.",
      held: ["A low-risk call ran at once and did not wait for anyone.", "Asking a low-risk tool for secrets:read was denied.", "Hostile instructions in the request text were denied before a person saw them."],
      broke: ["The hostile-text check is a phrase heuristic. It only catches the phrases it knows.", "A tool defined carelessly scores in the middle: the same action, a lower tier."], ids: ["B2", "B3", "B7", "T22", "S1 to S3", "S9 to S10", "S19 to S21"] },
    { n: 3, name: "Person", c: "#a78bfa", what: "A reviewer sees the request and decides. The gateway checks the decision against the required role and an optional allowlist.",
      held: ["Self-approval, the wrong role and another agent's approval were refused.", "An optional REVIEWER_ALLOWLIST narrows who counts."],
      broke: ["Reviewer names are typed in, not proven. A made-up reviewer was accepted.", "MFA and SSO claims in the context are ignored and not recorded.", "One approver is enough, even at the top tier."], ids: ["G1", "T24", "T25", "T31", "G5", "G6", "I9", "I11"] },
    { n: 4, name: "Binding", c: "#4de2ff", what: "The hash is rebuilt from the stored request and compared with the one the person approved. The tool's own definition and the rules version are part of it.",
      held: ["A new resource, an extra argument, a look-alike letter or a changed context after approval was refused with binding_mismatch.", "A changed rules version closed the old approvals."],
      broke: ["Before the fix, a loosened tool definition left the old approval alive (U16a). Now it is in the hash."], ids: ["B8", "T15", "T18", "T19", "T30", "U16a"] },
    { n: 5, name: "Guard", c: "#34d399", what: "Single use, expiry and reservation. The approval is marked as used before the tool is called, so two runs at the same moment cannot both win.",
      held: ["A second run of the same approval was refused as a replay.", "Two runs fired at once: one executed, one blocked.", "Expired approvals were refused, also in a real 11-minute wait."],
      broke: ["A restored backup can revive a used approval, so the downstream system has to remember the key too."], ids: ["B5", "B6", "T20", "T21", "U5b"] },
    { n: 6, name: "Tool", c: "#34d399", what: "The call itself, its answer, and the awkward cases: a lost reply, a timeout, a retry.",
      held: ["A lost reply left the outcome as unknown. A retry with the same key was safe and a new key was refused.", "A person who is not the requester settles an unknown outcome."],
      broke: ["The tool receives five fields and no permit, no hash and no approver. It cannot check that anyone approved."], ids: ["U1", "U2", "U3", "U4", "P3"] },
    { n: 7, name: "Record", c: "#fbbf24", what: "The hash-chained audit log, and what anyone can check about it afterwards.",
      held: ["An edited event was caught. With a key, a rewritten chain was caught too.", "A short script can recompute the chain without the gateway."],
      broke: ["A cut-off end is only caught if you saved the head hash elsewhere.", "Unsigned unless a key is set. The agent's receipt carries no approver and no policy version."], ids: ["B9", "D3", "G27", "G28", "P1", "P5a"] }
  ];
  var cases = [], tools = [], rows = [];

  function goCases(q) {
    var input = $("#q"); input.value = q; state.q = q; state.round = 0; state.verd = ""; state.shown = 24; syncFilters(); renderCases();
    $("#cases").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function buildStages() {
    var rail = $("#rail"), panel = $("#stagePanel");
    STAGES.forEach(function (s, i) {
      var b = el("button", "", "<i>" + s.n + "</i><b>" + s.name + "</b>");
      b.type = "button"; b.setAttribute("role", "tab"); b.id = "st" + s.n; b.style.setProperty("--c", s.c); b.setAttribute("aria-selected", i === 0 ? "true" : "false"); b.setAttribute("aria-controls", "stagePanel");
      b.addEventListener("click", function () { show(i); });
      b.addEventListener("keydown", function (e) {
        var k = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (!k) return;
        e.preventDefault(); var j = (i + k + STAGES.length) % STAGES.length; show(j); $("#st" + STAGES[j].n).focus();
      });
      rail.appendChild(b);
    });
    function show(i) {
      var s = STAGES[i]; $$("button", rail).forEach(function (b, j) { b.setAttribute("aria-selected", j === i ? "true" : "false"); });
      panel.setAttribute("aria-labelledby", "st" + s.n);
      panel.innerHTML = "";
      var a = el("div", "card"); a.style.setProperty("--c", s.c);
      a.innerHTML = "<h3><i></i>" + s.n + ". " + esc(s.name) + "</h3><p style=\"color:var(--mut)\">" + esc(s.what) + "</p><p class=\"note\" style=\"margin-bottom:0\">Cases that act here. Click one to read it.</p>";
      var chips = el("div", "chips");
      s.ids.forEach(function (id) { var c = el("button", "chip", esc(id)); c.type = "button"; c.addEventListener("click", function () { goCases(id); }); chips.appendChild(c); });
      a.appendChild(chips); panel.appendChild(a);
      var b = el("div", "card");
      b.innerHTML = "<h3 style=\"font-size:1rem\">What the lab found here</h3><ul class=\"holds\">" + s.held.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + s.broke.map(function (x) { return "<li class=\"no\">" + esc(x) + "</li>"; }).join("") + "</ul>";
      panel.appendChild(b);
    }
    show(0);
  }

  /* ---------- score explorer ---------- */
  var P = { env: "production", req: "internal", sens: "internal", base: 40, scopes: 1, short: false, fCred: false, fPriv: false, fProd: false, fDest: false, tool: "" };
  function buildScore() {
    var sel = $("#tool"); sel.innerHTML = "<option value=\"\">Build your own</option>";
    tools.forEach(function (t) { var o = el("option", "", esc(t.label + " (" + t.sector + ", " + t.system + ")" + (/\.loose$/.test(t.id) ? " - defined carelessly" : ""))); o.value = t.id; sel.appendChild(o); });
    var req = $("#req"); ORDER.forEach(function (c) { var b = el("button", "", c); b.type = "button"; b.dataset.v = c; b.setAttribute("aria-pressed", c === P.req ? "true" : "false"); req.appendChild(b); });
    function pressed(group, v) { $$("button", group).forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.v === v ? "true" : "false"); }); }
    $("#env").addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; P.env = b.dataset.v; pressed($("#env"), P.env); draw(); });
    req.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; P.req = b.dataset.v; pressed(req, P.req); draw(); });
    $("#base").addEventListener("input", function () { P.base = +this.value; draw(); });
    $("#scopes").addEventListener("input", function () { P.scopes = +this.value; draw(); });
    [["fCred", "fCred"], ["fPriv", "fPriv"], ["fProd", "fProd"], ["fDest", "fDest"], ["short", "short"]].forEach(function (m) { $("#" + m[0]).addEventListener("change", function () { P[m[1]] = this.checked; draw(); }); });
    sel.addEventListener("change", function () { loadTool(this.value); });
    window.loadToolRow = function (toolId, env, requested) { loadTool(toolId); P.env = env; P.req = requested; pressed($("#env"), env); pressed(req, requested); $("#tool").value = toolId; draw(); $("#score").scrollIntoView({ behavior: "smooth", block: "start" }); };
    function loadTool(id) {
      P.tool = id; var t = tools.filter(function (x) { return x.id === id; })[0]; if (!t) { draw(); return; }
      P.sens = t.sensitivity; P.base = t.baseRisk; P.fCred = !!t.credentialAccess; P.fPriv = !!t.privilegeChange; P.fProd = !!t.productionChange; P.fDest = !!t.destructive; P.scopes = 1; P.short = false;
      if (ORDER.indexOf(P.req) < ORDER.indexOf(P.sens)) { P.req = P.sens; pressed(req, P.req); }
      $("#base").value = P.base; $("#scopes").value = 1; $("#fCred").checked = P.fCred; $("#fPriv").checked = P.fPriv; $("#fProd").checked = P.fProd; $("#fDest").checked = P.fDest; $("#short").checked = false; draw();
    }
    loadTool(tools[0].id); sel.value = tools[0].id;
  }
  var C = 2 * Math.PI * 62;
  function draw() {
    var r = evaluate(P); $("#baseV").textContent = P.base; $("#scopesV").textContent = P.scopes;
    var arc = $("#arc"); arc.style.stroke = LCOL[r.level]; arc.style.strokeDashoffset = (C * (1 - r.score / 100)).toFixed(1);
    $("#gNum").textContent = r.score;
    var lv = $("#lvl"); lv.textContent = r.level; lv.style.setProperty("--lc", LCOL[r.level]); lv.style.setProperty("--lc-s", LSOFT[r.level]);
    $("#lvlTxt").textContent = r.level === "low" ? "Low risk: it runs at once. No person is asked." : r.level === "medium" ? "Medium risk: it waits for a person, and the approval stays alive for a short time." : r.level === "high" ? "High risk: it waits for an analyst or a lead, with a shorter window." : "Critical: it waits for a security lead, and the approval is alive for only a few minutes.";
    $("#resList").innerHTML = "<div><dt>Score</dt><dd>" + r.score + (r.raw > 100 ? " <span style=\"color:var(--dim);font-weight:500\">(" + r.raw + " before the cap)</span>" : "") + "</dd></div><div><dt>Who must approve</dt><dd>" + (r.role || "nobody, it runs at once") + "</dd></div><div><dt>How long the approval lives</dt><dd>" + r.win + " minutes</dd></div><div><dt>Environment</dt><dd>" + esc(P.env) + "</dd></div>";
    var stack = $("#stack"), legend = $("#legend"); stack.innerHTML = ""; legend.innerHTML = "";
    var tot = Math.max(100, r.raw);
    r.parts.forEach(function (p) { var s = el("span"); s.style.width = (p.v / tot * 100) + "%"; s.style.background = p.col; s.title = p.label + ": " + p.v; stack.appendChild(s); legend.appendChild(el("span", "", "<i style=\"background:" + p.col + "\"></i>" + esc(p.label) + " <b style=\"color:var(--ink)\">+" + p.v + "</b>")); });
    var m = rows.filter(function (x) { return x.tool === P.tool && x.env === P.env && x.requested === P.req; })[0];
    var same = m && P.scopes === 1 && !P.short && m.predicted.score === r.score;
    $("#match").textContent = same ? "This is one of the 21 rows the lab ran in round three, and the gateway agreed with it." : "";
  }

  /* ---------- sector chart ---------- */
  function buildChart() {
    var box = $("#chart"); var T = {}; tools.forEach(function (t) { T[t.id] = t; });
    var z = el("div", "zrow", "<span></span><div class=\"zones\"><span style=\"background:var(--em-s);color:var(--em)\">low</span><span style=\"background:var(--am-s);color:var(--am)\">medium</span><span style=\"background:var(--vi-s);color:var(--vi)\">high</span><span style=\"background:var(--ro-s);color:var(--ro)\">critical</span></div>");
    box.appendChild(z);
    rows.forEach(function (r) {
      var t = T[r.tool], loose = /\.loose$/.test(r.tool), lv = r.predicted.level;
      var row = el("div", "crow" + (loose ? " loose" : "")); row.tabIndex = 0; row.setAttribute("role", "button");
      row.setAttribute("aria-label", t.label + ", " + r.env + ", score " + r.predicted.score + ", " + lv + ". Load into the score box.");
      row.innerHTML = "<span class=\"nm\">" + esc(t.label) + (loose ? " <small>(careless)</small>" : "") + (r.env === "staging" ? " <small>(staging)</small>" : "") + "</span><span class=\"tr\"><i style=\"width:" + r.predicted.score + "%;--c:" + LCOL[lv] + "\"></i><b style=\"left:calc(" + r.predicted.score + "% - 34px)\">" + r.predicted.score + "</b></span>";
      function go() { window.loadToolRow(r.tool, r.env, r.requested); }
      row.addEventListener("click", go); row.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      box.appendChild(row);
    });
  }

  /* ---------- cases ---------- */
  var state = { q: "", round: 0, verd: "", wrong: false, shown: 24 };
  var VCLS = { "as expected": "ok", "different from prediction": "diff", "for information": "info", "by hand": "hand" };
  function syncFilters() {
    $$("#fRound .fb").forEach(function (b) { b.setAttribute("aria-pressed", (+b.dataset.v === state.round) ? "true" : "false"); });
    $$("#fVerd .fb").forEach(function (b) { var on = b.dataset.k === "wrong" ? state.wrong : (b.dataset.v === state.verd && !state.wrong); b.setAttribute("aria-pressed", on ? "true" : "false"); });
  }
  function buildCaseFilters() {
    var fr = $("#fRound"), fv = $("#fVerd");
    [[0, "All"], [1, "One"], [2, "Two"], [3, "Three"]].forEach(function (x) {
      var n = x[0] ? cases.filter(function (c) { return c.r === x[0]; }).length : cases.length;
      var b = el("button", "fb", x[1] + " <small>" + n + "</small>"); b.type = "button"; b.dataset.v = x[0]; b.addEventListener("click", function () { state.round = x[0]; state.shown = 24; syncFilters(); renderCases(); }); fr.appendChild(b);
    });
    var vs = [["", "All"], ["as expected", "As expected"], ["for information", "For information"], ["different from prediction", "Different from prediction"]];
    vs.forEach(function (x) {
      var n = x[0] ? cases.filter(function (c) { return c.v === x[0]; }).length : cases.length;
      var b = el("button", "fb", x[1] + " <small>" + n + "</small>"); b.type = "button"; b.dataset.v = x[0]; b.addEventListener("click", function () { state.verd = x[0]; state.wrong = false; state.shown = 24; syncFilters(); renderCases(); }); fv.appendChild(b);
    });
    var nw = cases.filter(function (c) { return c.wrong; }).length;
    var w = el("button", "fb", "My guess was wrong <small>" + nw + "</small>"); w.type = "button"; w.dataset.k = "wrong"; w.addEventListener("click", function () { state.wrong = !state.wrong; state.verd = ""; state.shown = 24; syncFilters(); renderCases(); }); fv.appendChild(w);
    syncFilters();
    var t; $("#q").addEventListener("input", function () { var v = this.value; clearTimeout(t); t = setTimeout(function () { state.q = v; state.shown = 24; renderCases(); }, 120); });
    $("#moreBtn").addEventListener("click", function () { state.shown += 30; renderCases(); });
  }
  function matches(c) {
    if (state.round && c.r !== state.round) return false;
    if (state.wrong && !c.wrong) return false;
    if (state.verd && c.v !== state.verd) return false;
    var q = state.q.trim().toLowerCase(); if (!q) return true;
    var hay = (c.id + " " + c.t + " " + c.g + " " + c.do + " " + c.ex + " " + c.hp + " " + c.why).toLowerCase();
    return q.split(/\s+/).every(function (w) { return hay.indexOf(w) > -1; });
  }
  function renderCases() {
    var list = $("#caseList"), all = cases.filter(matches); list.innerHTML = "";
    var q = state.q.trim().toLowerCase();
    if (q) all.sort(function (a, b) { return (b.id.toLowerCase() === q) - (a.id.toLowerCase() === q) || (b.id.toLowerCase().indexOf(q) === 0) - (a.id.toLowerCase().indexOf(q) === 0); });
    $("#count").textContent = all.length + " of " + cases.length + " cases" + (all.length > state.shown ? ", showing " + state.shown : "");
    if (!all.length) list.appendChild(el("div", "empty", "No case matches. Try a shorter word, or clear the filters."));
    all.slice(0, state.shown).forEach(function (c) {
      var d = el("details", "case"), vc = VCLS[c.v] || "info";
      d.innerHTML = "<summary><span class=\"id\">" + esc(c.id) + "</span><span class=\"ti\">" + esc(c.t) + "<span class=\"gp\">Round " + ["", "one", "two", "three"][c.r] + " &middot; " + esc(c.g) + "</span></span><span class=\"badge-wrap\"><span class=\"badge " + vc + "\">" + esc(c.v || "recorded") + "</span>" + (c.wrong ? "<span class=\"badge wrong\">my guess was wrong</span>" : "") + "</span></summary>" +
        "<dl><dt>What I did</dt><dd>" + esc(c.do) + "</dd><dt>I expected</dt><dd>" + esc(c.ex) + "</dd><dt>What happened</dt><dd>" + esc(c.hp) + "</dd>" + (c.why ? "<dt>Why it matters</dt><dd>" + esc(c.why) + "</dd>" : "") + "</dl>";
      list.appendChild(d);
    });
    if (all.length === 1 || (q && all.length && all[0].id.toLowerCase() === q)) { var f = $("details", list); if (f) f.open = true; }
    $("#moreBtn").hidden = all.length <= state.shown;
  }

  /* ---------- findings ---------- */
  function buildFindings(f) {
    var KIND = { fixed: ["Fixed", "var(--em)"], part: ["Partly fixed", "var(--am)"], doc: ["Documented", "var(--bl)"], lim: ["Limit", "var(--ro)"] };
    var bar = $("#fFind"), grid = $("#fgrid"), cur = "all";
    function btn(k, label, n) { var b = el("button", "fb", label + " <small>" + n + "</small>"); b.type = "button"; b.dataset.k = k; b.setAttribute("aria-pressed", k === cur ? "true" : "false"); b.addEventListener("click", function () { cur = k; $$(".fb", bar).forEach(function (x) { x.setAttribute("aria-pressed", x.dataset.k === k ? "true" : "false"); }); render(); }); bar.appendChild(b); }
    btn("all", "All", f.length); Object.keys(KIND).forEach(function (k) { btn(k, KIND[k][0], f.filter(function (x) { return x.k === k; }).length); });
    function render() {
      grid.innerHTML = "";
      f.filter(function (x) { return cur === "all" || x.k === cur; }).forEach(function (x) {
        var c = el("article", "fnd"); c.style.setProperty("--fc", KIND[x.k][1]);
        c.innerHTML = "<div class=\"hd\"><span class=\"fid\">" + esc(x.id) + "</span><span class=\"fs\">" + KIND[x.k][0] + "</span></div><h3>" + esc(x.t) + "</h3><p><b>What I saw.</b> " + esc(x.what) + "</p><p><b>Now.</b> " + esc(x.now) + "</p><span class=\"cs\">Case: " + esc(x.case) + "</span>";
        grid.appendChild(c);
      });
    }
    render();
  }

  /* ---------- OWASP ---------- */
  function buildOwasp(o) {
    var COL = { tested: "var(--em)", partly: "var(--am)", limited: "var(--bl)", "out of scope": "var(--dim)" };
    var g = $("#og"), d = $("#odet");
    o.forEach(function (x) {
      var b = el("button", "ot", "<b>" + esc(x.id) + "</b><span>" + esc(x.t) + "</span><em>" + esc(x.st) + "</em>"); b.type = "button"; b.style.setProperty("--oc", COL[x.st] || "var(--dim)"); b.setAttribute("aria-expanded", "false");
      b.addEventListener("click", function () { $$(".ot", g).forEach(function (y) { y.setAttribute("aria-expanded", y === b ? "true" : "false"); }); d.innerHTML = "<h3>" + esc(x.id) + " &middot; " + esc(x.t) + " <span style=\"color:" + (COL[x.st] || "var(--dim)") + ";font-size:.8rem;text-transform:uppercase;letter-spacing:.1em\">" + esc(x.st) + "</span></h3><p>" + esc(x.x) + "</p>"; });
      g.appendChild(b);
    });
  }

  /* ---------- checklist ---------- */
  function buildCheck(ch) {
    var box = $("#chk"), done = 0;
    function upd() { $("#prog").style.width = (done / ch.length * 100) + "%"; $("#progTxt").textContent = done + " of " + ch.length + " answered"; }
    ch.forEach(function (x, i) {
      var q = el("div", "q"); q.dataset.done = "0";
      var lab = el("label"); lab.setAttribute("aria-label", "Question " + (i + 1) + " answered for my system"); var inp = el("input"); inp.type = "checkbox"; lab.appendChild(inp); lab.appendChild(el("span"));
      inp.addEventListener("change", function () { q.dataset.done = inp.checked ? "1" : "0"; done += inp.checked ? 1 : -1; upd(); });
      var body = el("div", "", "<h3>" + esc(x.q) + "</h3><p>" + esc(x.a) + "</p>" + (x.seen ? "<small>Seen in: " + esc(x.seen) + "</small>" : ""));
      q.appendChild(lab); q.appendChild(body); box.appendChild(q);
    });
    upd();
    $("#copyChk").addEventListener("click", function () { copy("Thirteen questions for any approval step (Roshan Trivedi, HumanGate MCP lab, roshantrivedi.co.in/mcp-lab-portal/)\n\n" + ch.map(function (x, i) { return (i + 1) + ". " + x.q + "\n   " + x.a; }).join("\n\n"), "Questions copied"); });
  }

  /* ---------- small things ---------- */
  function counters() {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches; if (reduce || !("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (!e.isIntersecting) return; io.unobserve(e.target); var n = +e.target.dataset.n, t0 = performance.now(); (function tick(t) { var k = Math.min(1, (t - t0) / 900); e.target.textContent = Math.round(n * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(tick); })(t0); }); }, { threshold: .6 });
    $$("[data-n]").forEach(function (b) { io.observe(b); });
  }
  function spy() {
    var links = $$("#nav a"), map = {}; links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    if (!("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (a) { a.classList.remove("on"); }); var a = map[e.target.id]; if (a) { a.classList.add("on"); a.scrollIntoView({ block: "nearest", inline: "center" }); } } }); }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
  }
  $$("[data-copy]").forEach(function (b) { b.addEventListener("click", function () { copy(b.dataset.copy, "Checksum copied"); }); });
  $("#copyLink").addEventListener("click", function () { copy("https://roshantrivedi.co.in/mcp-lab-portal/", "Link copied"); });
  $("#copyCmd").addEventListener("click", function () { copy($("#cmd").textContent.replace(/^\$ /gm, ""), "Commands copied"); });
  counters(); spy();

  fetch("/assets/data/portal.json", { cache: "default" }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) {
    cases = d.cases; tools = d.tools; rows = d.rows;
    buildStages(); buildScore(); buildChart(); buildCaseFilters(); renderCases(); buildFindings(d.findings); buildOwasp(d.owasp); buildCheck(d.check);
  }).catch(function () {
    ["#stagePanel", "#caseList", "#fgrid", "#og", "#chk", "#chart"].forEach(function (s) { var n = $(s); if (n) n.innerHTML = "<div class=\"empty\">The data could not be loaded. The report in the download section has all of it.</div>"; });
  });
})();
