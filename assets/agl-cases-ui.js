/* AI governance lab: every use case, one by one. Reads window.AGL (results), window.AGL_CASES (steps)
   and window.AGLF (the browser copies of the three filters). Nothing here is sent anywhere. */
(function () {
  "use strict";
  var D = window.AGL, C = window.AGL_CASES, F = window.AGLF;
  var NAMES = ["v1", "v2", "v3"];
  var TRACKS = [["all", "All"], ["A", "A  Gateway"], ["G", "G  Guardrail"], ["I", "I  Agent identity"], ["E", "E  Audit"], ["V", "V  Vendor access"], ["R", "R  Retrieval"], ["T", "T  Agent to API"], ["H", "H  HR lifecycle"], ["B", "B  Bypass and evidence"], ["Q", "Q  Answers from documents"], ["C", "C  Credentials and sessions"], ["D", "D  Delegation and keys"], ["P", "P  Real assistant"]];
  var TRACK_NAME = { A: "Gateway", G: "Guardrail filter", I: "Agent identity", E: "Audit evidence", V: "Vendor and third-party access", R: "Retrieval and document permissions", T: "Agent instructions to an identity API", H: "HR-driven identity lifecycle", B: "Bypass, response, lists and evidence", Q: "Retrieval-augmented answers (an assistant that answers from documents)", C: "Credentials, sessions and identity edge cases", D: "Delegation, keys and organisations", P: "Real assistant" };
  var ROUND_FILTER = { 1: "v1", 2: "v2", 3: "v2", 4: "v3" };
  var MARK = { ok: ["Works", "ok"], stop: ["Stopped", "bad"], miss: ["Gets through", "warn"], note: ["Step", "note"] };

  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function words(s) { return String(s).replace(/_/g, " "); }
  function pill(text, kind) { return el("span", "agl-pill " + kind, text); }
  function td(txt, cls) { return el("td", cls, txt); }
  function th(txt) { return el("th", null, txt); }
  function wrapTable(t) { var w = el("div", "try-scroll"); w.appendChild(t); return w; }
  function reduced() { try { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) { return false; } }

  /* ---------- build the list of cases (59 lab cases, then the 9 assistant cases) ---------- */
  var order = [], byId = {};
  [1, 2, 3, 4].forEach(function (r) {
    D.cases[r].forEach(function (c) {
      if (!byId[c.id]) { byId[c.id] = { id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab" }; order.push(byId[c.id]); }
      byId[c.id].rounds[r] = c;
    });
  });
  /* round five: 14 cases added on 24 Oct 2026, after the first posts */
  var R5 = window.AGL_R5 || { cases: [], text: {}, controls: [] };
  R5.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c });
    C[c.id] = R5.text[c.id];
  });
  /* round six: 18 cases added on 25 Oct 2026 (agents that send instructions to an identity API) */
  var R6 = window.AGL_R6 || { cases: [], text: {}, controls: [] };
  R6.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c, addedRound: 6, addedWhen: "25 Oct 2026" });
    C[c.id] = R6.text[c.id];
  });
  /* round seven: 12 cases added on 25 Oct 2026 (the HR side of identity onboarding) */
  var R7 = window.AGL_R7 || { cases: [], text: {}, controls: [] };
  R7.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c, addedRound: 7, addedWhen: "25 Oct 2026" });
    C[c.id] = R7.text[c.id];
  });
  var R8 = window.AGL_R8 || { cases: [], text: {}, controls: [] };
  R8.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c, addedRound: 8, addedWhen: "25 Oct 2026" });
    C[c.id] = R8.text[c.id];
  });
  var R9 = window.AGL_R9 || { cases: [], text: {}, controls: [] };
  R9.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c, addedRound: 9, addedWhen: "25 Oct 2026" });
    C[c.id] = R9.text[c.id];
  });
  var R10 = window.AGL_R10 || { cases: [], text: {}, controls: [] };
  R10.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c, addedRound: 10, addedWhen: "25 Oct 2026" });
    C[c.id] = R10.text[c.id];
  });
  var R11 = window.AGL_R11 || { cases: [], text: {}, controls: [] };
  R11.cases.forEach(function (c) {
    order.push({ id: c.id, track: c.track, title: c.title, rounds: {}, kind: "lab", added: c, addedRound: 11, addedWhen: "25 Oct 2026" });
    C[c.id] = R11.text[c.id];
  });
  D.controls = (D.controls || []).concat(R5.controls || [], R6.controls || [], R7.controls || [], R8.controls || [], R9.controls || [], R10.controls || [], R11.controls || []);
  function key(c) { var m = /^([A-Z])(\d+)$/.exec(c.id); return "AGIEVRTHBQCD".indexOf(m[1]) * 1000 + (+m[2]); }
  order.sort(function (a, b) { return key(a) - key(b); });
  D.trackp.forEach(function (p) { order.push({ id: p[0], track: "P", title: p[1], kind: "assistant", outcome: p[2], note: p[3], rounds: {} }); });

  function hasGap(c) { var k = C[c.id]; return !!k && k.steps.some(function (s) { return s[0] === "miss"; }); }

  /* ---------- per-case body ---------- */
  function buildBody(c) {
    var body = el("div", "cx-body");
    if (c.kind === "assistant") {
      body.appendChild(el("p", "cx-what", "I pasted a made-up company policy into a chat with an AI assistant, then made this request: " + c.title.charAt(0).toLowerCase() + c.title.slice(1) + "."));
      var s = el("div", "cx-box"); s.appendChild(el("h4", null, "What happened"));
      s.appendChild(pill(c.outcome === "followed the policy" ? "Followed the policy" : words(c.outcome), c.outcome === "followed the policy" ? "ok" : "warn"));
      s.appendChild(el("p", null, c.note)); body.appendChild(s);
      var l = el("p", "agl-hint");
      l.appendChild(document.createTextNode("The words I typed and the assistant's reply, exactly as they came: "));
      var a1 = el("a", null, "evidence page"); a1.href = "/ai-governance-lab/evidence/#" + c.id;
      var a2 = el("a", null, "full transcript"); a2.href = "/ai-governance-lab/transcripts/#" + c.id;
      l.appendChild(a1); l.appendChild(document.createTextNode(" and ")); l.appendChild(a2); l.appendChild(document.createTextNode(". You can run the same nine requests on your own assistant on "));
      var a3 = el("a", null, "the try page"); a3.href = "/ai-governance-lab/try/#assistant"; l.appendChild(a3); l.appendChild(document.createTextNode("."));
      body.appendChild(l);
      var cav = { P5: "Run once, then repeated in a new chat and passed again.", P1: "Run once, then repeated in two short new chats and passed again.", P7: "Run once, as 30 separate turns. Not repeated." }[c.id];
      if (cav) body.appendChild(el("p", "agl-hint", cav));
      return body;
    }
    var k = C[c.id];
    body.appendChild(el("p", "cx-what", k.what));

    var head = el("div", "cx-flowhead");
    head.appendChild(el("h4", null, "What happened, step by step"));
    var play = el("button", "agl-btn ghost cx-play", "Play steps"); play.type = "button"; head.appendChild(play);
    body.appendChild(head);
    var ol = el("ol", "cx-steps");
    k.steps.forEach(function (st, i) {
      var li = el("li", "cx-step cx-" + st[0]);
      var m = MARK[st[0]] || MARK.note;
      li.appendChild(el("span", "cx-n", String(i + 1)));
      var inner = el("div", "cx-st");
      inner.appendChild(el("span", "cx-tag " + m[1], m[0]));
      inner.appendChild(el("span", "cx-txt", " " + st[1]));
      li.appendChild(inner); ol.appendChild(li);
    });
    body.appendChild(ol);
    var timers = [];
    play.addEventListener("click", function () {
      timers.forEach(clearTimeout); timers = [];
      var items = ol.children;
      if (reduced()) { for (var q = 0; q < items.length; q++) items[q].classList.remove("cx-hide"); return; }
      for (var i = 0; i < items.length; i++) items[i].classList.add("cx-hide");
      Array.prototype.forEach.call(items, function (li, i) { timers.push(setTimeout(function () { li.classList.remove("cx-hide"); }, 450 + i * 750)); });
    });

    var res = el("div", "cx-result");
    res.appendChild(el("b", null, "Result: ")); res.appendChild(document.createTextNode(k.result));
    body.appendChild(res);
    var why = el("div", "cx-why"); why.appendChild(el("b", null, "Why it matters: ")); why.appendChild(document.createTextNode(k.why)); body.appendChild(why);

    /* variants, run live in the browser, for the guardrail cases that have them */
    if (c.track === "G" && F) {
      var V = F.variants(11).filter(function (v) { return v.id === c.id; });
      if (V.length) {
        body.appendChild(el("h4", "cx-h", "Each variant, run now in your browser"));
        var t = el("table", "try-table");
        var hr = el("tr"); ["Variant", "v1", "v2", "v3"].forEach(function (h) { hr.appendChild(th(h)); }); t.appendChild(el("thead")).appendChild(hr);
        var tb = el("tbody"); t.appendChild(tb);
        var tot = [0, 0, 0];
        V.forEach(function (v) {
          var tr = el("tr");
          var first = el("td"); first.appendChild(el("div", null, v.name));
          var shown = Array.isArray(v.text) ? v.text.join("  →  ") : v.text;
          first.appendChild(el("code", "cx-code", shown.length > 160 ? shown.slice(0, 157) + "…" : shown));
          tr.appendChild(first);
          NAMES.forEach(function (n, i) { var good = F.judge(F.detectors[n], v); if (good) tot[i]++; tr.appendChild(td(good ? "ok" : "MISS", good ? "try-ok" : "try-miss")); });
          tb.appendChild(tr);
        });
        var totr = el("tr", "try-total"); totr.appendChild(td("Handled correctly"));
        tot.forEach(function (n) { totr.appendChild(td(n + " of " + V.length)); }); tb.appendChild(totr);
        body.appendChild(wrapTable(t));
        body.appendChild(el("p", "agl-hint", "“ok” means the filter did the right thing: it found and masked what it should, or left harmless text alone. The numbers inside the texts are made up. v3 was written after I saw v2's misses on these same variants, so its column is not a measure of how it does on new text."));
      } else if (c.id === "G17") {
        var gl = el("p", "agl-hint"); gl.appendChild(document.createTextNode("This one is a set of 200 samples, not a few variants. Score it yourself on the "));
        var a = el("a", null, "try page"); a.href = "/ai-governance-lab/try/#score"; gl.appendChild(a); gl.appendChild(document.createTextNode(": the numbers above are the ones you should get."));
        body.appendChild(gl);
      } else {
        body.appendChild(el("p", "agl-hint", "This case is checked in the Python lab only. Its inputs are listed in the steps above, and the full run is on the run page."));
      }
      var tl = el("p", "agl-hint"); tl.appendChild(document.createTextNode("Try your own text on the three filters: "));
      var ta = el("a", null, "open the filter bench"); ta.href = "/ai-governance-lab/try/#bench"; tl.appendChild(ta); tl.appendChild(document.createTextNode("."));
      body.appendChild(tl);
    }

    /* round history */
    body.appendChild(el("h4", "cx-h", "How it did, round by round"));
    var rt = el("table", "try-table");
    var rh = el("tr"); ["Round", "What the lab was", "My guess", "What came out", "Result"].forEach(function (h) { rh.appendChild(th(h)); });
    rt.appendChild(el("thead")).appendChild(rh);
    var rb = el("tbody"); rt.appendChild(rb);
    if (c.added) {
      var tr5 = el("tr");
      tr5.appendChild(td(String(c.addedRound || 5))); tr5.appendChild(td("Added on " + (c.addedWhen || "24 Oct 2026") + (c.addedRound >= 6 ? "" : ", after the first posts")));
      tr5.appendChild(td(words(c.added.expected))); tr5.appendChild(td(words(c.added.actual)));
      var v5 = el("td"); v5.appendChild(pill(c.added.verdict === "as expected" ? "as I guessed" : "different from my guess", c.added.verdict === "as expected" ? "ok" : "warn")); tr5.appendChild(v5);
      rb.appendChild(tr5);
    }
    [1, 2, 3, 4].forEach(function (r) {
      var row = c.rounds[r]; if (!row) return;
      var tr = el("tr");
      tr.appendChild(td(String(r)));
      var nm = D.rounds[r].name; var f = (c.track === "G" || c.id === "I12") ? " (filter " + ROUND_FILTER[r] + ")" : "";
      tr.appendChild(td(nm + f));
      tr.appendChild(td(words(row.expected)));
      tr.appendChild(td(words(row.actual)));
      var vcell = el("td"); vcell.appendChild(pill(row.verdict === "as expected" ? "as I guessed" : "different from my guess", row.verdict === "as expected" ? "ok" : "warn")); tr.appendChild(vcell);
      rb.appendChild(tr);
    });
    body.appendChild(wrapTable(rt));
    body.appendChild(el("p", "agl-hint", "“As I guessed” means the result matched what I wrote down before the run. It does not mean the control is good: several of my guesses were that something would be missed."));

    /* controls */
    var ctl = (D.controls || []).filter(function (x) { return x.cases.indexOf(c.id) >= 0; });
    if (ctl.length) {
      body.appendChild(el("h4", "cx-h", "Control it tests"));
      var ul = el("ul", "cx-ctl");
      ctl.forEach(function (x) { var li = el("li"); li.appendChild(el("b", null, x.id + "  ")); li.appendChild(document.createTextNode(x.control)); ul.appendChild(li); });
      body.appendChild(ul);
      var cl = el("p", "agl-hint"); cl.appendChild(document.createTextNode("How each control maps to ISO 42001, NIST AI RMF, the EU AI Act and India's rules is in the controls table on the "));
      var ca = el("a", null, c.added ? "lab page" : "run page"); ca.href = c.added ? (c.addedRound === 11 ? "/ai-governance-lab/#delegation" : c.addedRound === 10 ? "/ai-governance-lab/#credentials" : c.addedRound === 9 ? "/ai-governance-lab/#rag" : c.addedRound === 8 ? "/ai-governance-lab/#bypass" : c.addedRound === 7 ? "/ai-governance-lab/#hr-lifecycle" : c.addedRound === 6 ? "/ai-governance-lab/#api-pattern" : "/ai-governance-lab/#frameworks") : "/ai-governance-lab/run/#agl-ctl"; cl.appendChild(ca); cl.appendChild(document.createTextNode("."));
      body.appendChild(cl);
    }
    return body;
  }

  /* ---------- page ---------- */
  function mount(root) {
    root.classList.add("agl");
    var stack = el("div", "agl-stack"); root.appendChild(stack);
    var gaps = order.filter(hasGap).length;

    var top = el("section", "agl-panel");
    top.appendChild(el("p", "agl-eyebrow", "All of the use cases"));
    top.appendChild(el("p", "agl-hint", order.length + " cases: " + (order.length - 9 - R5.cases.length - R6.cases.length - R7.cases.length - R8.cases.length - R9.cases.length - R10.cases.length - R11.cases.length) + " ran in the lab across four tracks in the first four rounds, " + R5.cases.length + " were added in round five on 24 Oct 2026 (new tracks V and R, and more in I and E), " + R6.cases.length + " were added in round six on 25 Oct 2026 (new track T: agents that send instructions to an identity API), " + R7.cases.length + " were added in round seven on 25 Oct 2026 (new track H: the HR side of onboarding), " + R8.cases.length + " were added in round eight on 25 Oct 2026 (new track B: when an agent goes around the gateway), " + R9.cases.length + " were added in round nine on 25 Oct 2026 (new track Q: an assistant that answers from documents), " + R10.cases.length + " were added in round ten on 25 Oct 2026 (new track C: credentials, sessions and identity edge cases), " + R11.cases.length + " were added in round eleven on 25 Oct 2026 (new track D: agents handing work to agents, keys and mergers), and 9 were run by hand on a real assistant. Open any case to see what I set up, the steps in order, what the filters did with it, how it did in each round and which control it tests. " + gaps + " of the lab cases show something getting through, and those are marked. Everything is made up: a lender called Kaveri Finance and numbers that follow real formats on purpose."));
    stack.appendChild(top);

    var bar = el("div", "cx-bar");
    var chips = el("div", "cx-chips"); chips.setAttribute("role", "group"); chips.setAttribute("aria-label", "Filter by track");
    var cur = "all", gapOnly = false, q = "";
    var chipEls = {};
    TRACKS.forEach(function (t) {
      var n = t[0] === "all" ? order.length : order.filter(function (c) { return c.track === t[0]; }).length;
      var b = el("button", "agl-chip", t[1].replace("  ", " · ")); b.type = "button"; b.appendChild(el("small", null, String(n)));
      b.setAttribute("aria-pressed", String(t[0] === cur));
      b.addEventListener("click", function () { cur = t[0]; Object.keys(chipEls).forEach(function (k) { chipEls[k].setAttribute("aria-pressed", String(k === cur)); }); render(); });
      chips.appendChild(b); chipEls[t[0]] = b;
    });
    bar.appendChild(chips);
    var row2 = el("div", "cx-row2");
    var search = el("input", "try-input cx-search"); search.type = "search"; search.placeholder = "Search by id or words, e.g. G10 or kill"; search.setAttribute("aria-label", "Search cases");
    search.addEventListener("input", function () { q = search.value.trim().toLowerCase(); render(); });
    var lab = el("label", "try-opt"); var cb = el("input"); cb.type = "checkbox"; lab.appendChild(cb); lab.appendChild(document.createTextNode(" Only cases where something got through"));
    cb.addEventListener("change", function () { gapOnly = cb.checked; render(); });
    row2.appendChild(search); row2.appendChild(lab); bar.appendChild(row2);
    stack.appendChild(bar);
    var count = el("p", "agl-hint cx-count"); count.setAttribute("aria-live", "polite"); stack.appendChild(count);

    var list = el("div", "cx-list"); stack.appendChild(list);
    var cards = {};
    order.forEach(function (c) {
      var art = el("article", "cx-card"); art.id = c.id;
      var h = el("h3", "cx-h3");
      var btn = el("button", "cx-head"); btn.type = "button"; btn.setAttribute("aria-expanded", "false");
      btn.appendChild(el("span", "cx-id", c.id));
      btn.appendChild(el("span", "cx-title", c.title));
      var st = el("span", "cx-badges");
      if (c.kind === "assistant") st.appendChild(pill("followed the policy", "ok"));
      else {
        var last = c.added || c.rounds[4] || c.rounds[3] || c.rounds[2] || c.rounds[1];
        st.appendChild(pill(words(last.actual), hasGap(c) ? "warn" : "ok"));
        if (hasGap(c)) st.appendChild(pill("misses shown", "warn"));
      }
      btn.appendChild(st);
      btn.appendChild(el("span", "cx-chev", "▾"));
      h.appendChild(btn); art.appendChild(h);
      var panel = el("div", "cx-panel"); panel.hidden = true; panel.id = "cx-" + c.id; btn.setAttribute("aria-controls", panel.id);
      art.appendChild(panel);
      btn.addEventListener("click", function () { toggle(c, true); });
      list.appendChild(art);
      cards[c.id] = { art: art, btn: btn, panel: panel, built: false, c: c };
    });
    function toggle(c, update, force) {
      var x = cards[c.id], open = force != null ? force : x.panel.hidden;
      if (open && !x.built) { x.panel.appendChild(buildBody(c)); x.built = true; }
      x.panel.hidden = !open; x.btn.setAttribute("aria-expanded", String(open)); x.art.classList.toggle("open", open);
      if (update) { try { history.replaceState(null, "", open ? "#" + c.id : location.pathname); } catch (e) { /* ignore */ } }
    }
    function render() {
      var n = 0;
      order.forEach(function (c) {
        var hay = (c.id + " " + c.title + " " + ((C[c.id] && C[c.id].what) || c.note || "")).toLowerCase();
        var show = (cur === "all" || c.track === cur) && (!gapOnly || hasGap(c)) && (!q || hay.indexOf(q) >= 0);
        cards[c.id].art.hidden = !show; if (show) n++;
      });
      count.textContent = n === order.length ? "Showing all " + n + " cases." : "Showing " + n + " of " + order.length + " cases.";
    }
    render();
    var open = document.createElement("div"); open.className = "cx-tools";
    var ea = btn2("Open all shown", function () { order.forEach(function (c) { if (!cards[c.id].art.hidden) toggle(c, false, true); }); });
    var ca2 = btn2("Close all", function () { order.forEach(function (c) { toggle(c, false, false); }); });
    open.appendChild(ea); open.appendChild(ca2); stack.insertBefore(open, list);
    function btn2(label, fn) { var b = el("button", "agl-btn ghost", label); b.type = "button"; b.addEventListener("click", fn); return b; }

    var foot = el("section", "agl-panel");
    foot.appendChild(el("p", "agl-hint", "Not in this list: the two held-out tests (10 and 8 cases written after the filters were done) and the 200-sample score. Their results are in the appendix and on the main page. The raw run output for every case above is on the run page and the transcripts page."));
    stack.appendChild(foot);

    var h = (location.hash || "").replace("#", "");
    if (cards[h]) { toggle(cards[h].c, false, true); setTimeout(function () { cards[h].art.scrollIntoView({ block: "start" }); }, 60); }
  }
  window.AGL_mountCases = mount;
}());
