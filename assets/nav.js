/* Mega menus for Work, Labs, Writing and About.
   The plain links in the bar keep working without this file. With it, each of those links gets a small
   button beside it that opens a panel of everything inside that section.
   Pattern: a real <button> with aria-expanded and aria-controls (a disclosure, not an ARIA menu bar), so
   Tab, Enter, Space and Escape do what people expect. Hover opens it for mouse users; touch and keyboard use the button. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var wide = window.matchMedia("(min-width: 900px)");
  var hover = window.matchMedia("(hover: hover) and (pointer: fine)");

  var MENUS = {
    "/case-studies/": {
      id: "work", title: "Work",
      feature: { kicker: "Start here", title: "Agentic AI identity governance", text: "Who an agent is, what it may do, and who answers for what it did.", href: "/case-studies/agentic-ai-identity-governance/", cta: "Read the case study", icons: ["robot", "shield", "key"] },
      groups: [
        { title: "AI and agents", k: "ai", items: [
          ["/case-studies/agentic-ai-identity-governance/", "Agentic AI identity governance", "robot"],
          ["/case-studies/ai-agent-credential-sharing/", "AI agent credential sharing", "chain"],
          ["/case-studies/ai-coworker/", "AI as a coworker", "people"],
          ["/case-studies/shadow-ai-discovery-gap/", "The shadow AI discovery gap", "eye"],
          ["/case-studies/non-human-identity-at-scale/", "Non-human identity at scale", "server"],
          ["/case-studies/ai-processing-tax/", "The AI decision tax", "coin"],
          ["/mcp-lab-case-study/", "Can a person stay in control?", "shield"]] },
        { title: "Privileged access", k: "pam", items: [
          ["/case-studies/credential-platform/", "Credential platform strategy", "vault"],
          ["/case-studies/pam-modernization/", "PAM modernization and ZSP", "key"],
          ["/case-studies/privileged-access-program/", "Running a PAM program", "list"],
          ["/case-studies/credential-tiering-model/", "Credential tiering", "pyramid"],
          ["/case-studies/jit-jea-elevation/", "Just-in-time elevation", "clock"],
          ["/case-studies/break-glass-access/", "Break-glass access", "bell"],
          ["/case-studies/vendor-privileged-access/", "Vendor privileged access", "building"]] },
        { title: "Governance", k: "gov", items: [
          ["/case-studies/audit-mapping/", "Control-to-audit mapping", "scale"],
          ["/case-studies/access-recertification/", "Access recertification", "rotate"]] },
        { title: "Platform and architecture", k: "plat", items: [
          ["/case-studies/migration-planning/", "Migration planning", "truck"],
          ["/case-studies/platform-evaluation/", "Platform evaluation", "gauge"],
          ["/case-studies/secrets-consolidation/", "Secrets consolidation", "locks"],
          ["/case-studies/passwordless-authentication/", "Passwordless rollout", "finger"],
          ["/case-studies/ciem-at-scale/", "Cloud entitlements (CIEM)", "cloud"]] }
      ],
      all: ["/case-studies/", "Browse all case studies"]
    },
    "/labs/": {
      id: "labs", title: "Labs",
      feature: { kicker: "Try it", title: "Pick a request. See where it stops.", text: "Follow one AI agent request through the approval gateway, stage by stage.", href: "/labs/#mcp-flow", cta: "Open the walkthrough", icons: ["plug", "person", "shield"] },
      groups: [
        { title: "HumanGate MCP lab", k: "ai", logo: "humangate", items: [
          ["/mcp-lab-case-study/", "Overview: what held, what did not", "flask"],
          ["/mcp-lab-results/", "Results", "check"],
          ["/mcp-lab-use-cases/", "Use cases", "list"],
          ["/mcp-lab-in-depth/", "In depth", "doc"],
          ["/mcp-lab-portal/", "Portal: 161 case cards", "search"]] },
        { title: "Read and try", k: "plat", items: [
          ["/book/", "The book: Who Approved That?", "book"],
          ["/tools/tier-check/", "Credential tier self-check", "pyramid"],
          ["/secure-india-exams/", "Securing India's national exams", "india"],
          ["/design-system/", "The design system", "palette"]] }
      ],
      all: ["/labs/", "See all labs and projects"]
    },
    "/writing/": {
      id: "writing", title: "Writing",
      feature: { kicker: "Series", title: "The PAM series", text: "Three connected articles on privileged access, from the framework to the project plan.", href: "/writing/pam-series/", cta: "About the series", icons: ["vault", "list", "people"] },
      groups: [
        { title: "The PAM series", k: "pam", logo: "pam", items: [
          ["/writing/pam-framework-and-design/", "Part 1: Framework and design", "layers"],
          ["/writing/pam-project-plan-by-organization-tier/", "Part 2: Project plan by tier", "calendar"],
          ["/writing/pam-as-an-identity/", "Part 3: PAM as an identity", "idcard"]] },
        { title: "Analysis", k: "gov", items: [
          ["/writing/openai-huggingface-breach-cybersecurity-analysis/", "The OpenAI and Hugging Face breach", "warn"],
          ["/feed.xml", "Subscribe by RSS", "arrow"]] }
      ],
      all: ["/writing/", "All writing"]
    },
    "/about/": {
      id: "about", title: "About",
      feature: { kicker: "Hello", title: "Fourteen years in identity and security", text: "Privileged access, credentials, and now a person in the loop when an AI agent acts.", href: "/about/", cta: "Read my story", portrait: true },
      groups: [
        { title: "Know more", k: "plat", items: [
          ["/about/", "About me", "user"],
          ["/now/", "What I am doing now", "clock"],
          ["/ai/", "How I use AI, and where I stop", "spark"],
          ["/resume/", "Résumé", "doc"]] },
        { title: "Get in touch", k: "gov", items: [
          ["/#contact", "LinkedIn, GitHub and email", "mail"],
          ["/Roshan_Trivedi_Resume.pdf", "Résumé (PDF)", "arrow"]] }
      ],
      all: ["/#contact", "Say hello"]
    }
  };

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function icon(name, cls) {
    var s = document.createElementNS(NS, "svg"); s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("aria-hidden", "true"); s.setAttribute("focusable", "false");
    if (cls) s.setAttribute("class", cls);
    var u = document.createElementNS(NS, "use"); u.setAttribute("href", "/assets/icons.svg#i-" + name); s.appendChild(u); return s;
  }
  function logoChip(name) { var i = el("i", "nv-logo"); i.style.setProperty("--logo", "url(/assets/logos/" + name + ".svg)"); i.setAttribute("aria-hidden", "true"); return i; }

  /* A small line-drawn mark in front of each page's first label (the "eyebrow" above a title). Decorative, so hidden from screen readers. */
  (function marks() {
    var bg = document.documentElement.getAttribute("data-bg") || "", name = null;
    var by = { about: "rt", now: "rt", ai: "ailab", resume: "rt", labs: "ailab", book: "book", writing: "writing", series: "pam", designsys: "rt", tiercheck: "pam", exams: "exams", work: "rt", notfound: "rt",
      "post-breach": "writing", "post-framework": "pam", "post-plan": "pam", "post-identity": "pam" };
    if (by[bg]) name = by[bg];
    else if (/^mcp/.test(bg)) name = "humangate";
    else if (/^cs-/.test(bg)) name = /(ai-|agentic|shadow|non-human)/.test(bg) ? "ailab" : /(pam|credential|privileged|break-glass|jit|secrets|vendor|passwordless)/.test(bg) ? "pam" : "rt";
    function put(target, n) { if (!target || target.querySelector(".lg")) return; var i = document.createElement("i"); i.className = "lg lg-" + n; i.setAttribute("aria-hidden", "true"); target.insertBefore(i, target.firstChild); }
    if (name) put(document.querySelector("main .eyebrow, main .ey, .eyebrow"), name);
    if (bg === "home") {
      var home = { "work-title": "rt", "feat-title": "humangate", "cs-title": "pam", "wr-title": "writing", "contact-title": "rt" };
      Object.keys(home).forEach(function (id) { var h = document.getElementById(id); if (h && h.parentNode) put(h.parentNode.querySelector(".ey"), home[id]); });
    }
  })();

  var root = document.querySelector(".hg-sitenav") || document.querySelector("header.top");
  if (!root) return;
  var isHome = root.matches("header.top");
  var links = isHome ? root.querySelectorAll("nav.nav > a") : root.querySelectorAll("ul > li > a");
  var panels = [], items = [], current = null, closeTimer = null, openTimer = null;

  function build(menu) {
    var p = el("div", "nv-panel"); p.id = "nvp-" + menu.id; p.hidden = true; p.setAttribute("role", "region"); p.setAttribute("aria-label", menu.title + " menu");
    var inner = el("div", "nv-inner");
    // feature card on the left
    var f = menu.feature, card = el("a", "nv-feature"); card.href = f.href;
    var art = el("div", "nv-art"); art.setAttribute("aria-hidden", "true");
    if (f.portrait) { var img = new Image(); img.src = "/assets/roshan-trivedi-520.webp"; img.alt = ""; img.width = 64; img.height = 64; img.className = "nv-portrait"; art.appendChild(img); }
    else {
      (f.icons || []).forEach(function (n, i) { art.appendChild(icon(n, "nv-art-i")); if (i < 2) art.appendChild(el("span", "nv-art-line")); });
      art.appendChild(el("span", "nv-art-dot"));
    }
    card.appendChild(art); card.appendChild(el("span", "nv-kicker", f.kicker)); card.appendChild(el("strong", "nv-ftitle", f.title));
    card.appendChild(el("span", "nv-ftext", f.text));
    var cta = el("span", "nv-cta", f.cta + " "); cta.appendChild(icon("arrow", "nv-cta-i")); card.appendChild(cta);
    inner.appendChild(card);
    // groups
    var cols = el("div", "nv-cols"); var n = 0;
    // governance + platform share a column on the Work menu so the columns stay even
    var groups = menu.groups, merged = [];
    if (menu.id === "work") merged = [[groups[0]], [groups[1]], [groups[2], groups[3]]]; else groups.forEach(function (g) { merged.push([g]); });
    merged.forEach(function (stack) {
      var col = el("div", "nv-col");
      stack.forEach(function (g) {
        var sec = el("section", "nv-group k-" + g.k); var hid = "nvh-" + menu.id + "-" + (n++);
        var h = el("p", "nv-gtitle"); /* a label, not a page heading: keeps each page's outline starting at its own h1 */ h.id = hid; if (g.logo) h.appendChild(logoChip(g.logo)); h.appendChild(document.createTextNode(g.title)); sec.appendChild(h);
        sec.setAttribute("aria-labelledby", hid);
        var ul = el("ul", "nv-list");
        g.items.forEach(function (it) {
          var li = el("li"); var a = el("a", "nv-tile"); a.href = it[0]; a.style.setProperty("--i", String(n++));
          var chip = el("span", "nv-ic"); chip.appendChild(icon(it[2])); a.appendChild(chip);
          a.appendChild(el("span", "nv-label", it[1])); a.appendChild(icon("arrow", "nv-go"));
          if (location.pathname === it[0]) a.setAttribute("aria-current", "page");
          li.appendChild(a); ul.appendChild(li);
        });
        sec.appendChild(ul); col.appendChild(sec);
      });
      cols.appendChild(col);
    });
    inner.appendChild(cols);
    var foot = el("div", "nv-foot"); var all = el("a", "nv-all", menu.all[1] + " "); all.href = menu.all[0]; all.appendChild(icon("arrow", "nv-cta-i")); foot.appendChild(all);
    inner.appendChild(foot); p.appendChild(inner);
    return p;
  }

  Array.prototype.forEach.call(links, function (a) {
    var key = a.getAttribute("href"); var menu = MENUS[key]; if (!menu) return;
    var host = isHome ? null : a.parentNode;
    var wrap;
    if (isHome) { wrap = el("span", "nv-has"); a.parentNode.insertBefore(wrap, a); wrap.appendChild(a); }
    else { wrap = host; wrap.classList.add("nv-has"); }
    var btn = el("button", "nv-toggle"); btn.type = "button"; btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-controls", "nvp-" + menu.id); btn.setAttribute("aria-label", menu.title + " menu");
    btn.appendChild(el("span", "nv-chev")); wrap.appendChild(btn);
    var panel = build(menu); root.appendChild(panel);
    var item = { wrap: wrap, btn: btn, panel: panel, menu: menu };
    items.push(item); panels.push(panel);

    btn.addEventListener("click", function (e) {
      if (current === item) { close(true); } else { open(item); if (e.detail === 0) { var f = panel.querySelector("a.nv-tile"); if (f) f.focus(); } }
    });
    btn.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); open(item); var f = panel.querySelector("a.nv-tile"); if (f) f.focus(); }
    });
    panel.addEventListener("keydown", function (e) {
      var f = Array.prototype.slice.call(panel.querySelectorAll("a[href]"));
      var i = f.indexOf(document.activeElement); if (i < 0) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); var n = f[Math.max(0, Math.min(f.length - 1, i + (e.key === "ArrowDown" ? 1 : -1)))]; if (n) n.focus(); }
      else if (e.key === "Tab" && e.shiftKey && i === 0) { e.preventDefault(); btn.focus(); }
      else if (e.key === "Tab" && !e.shiftKey && i === f.length - 1) {
        // leave the panel for the next link in the bar, the way a reader expects
        var bar = Array.prototype.slice.call(root.querySelectorAll("a[href], button")).filter(function (n) { return !panel.contains(n) && !n.closest(".nv-panel"); });
        var at = bar.indexOf(btn); close(false); if (bar[at + 1]) { e.preventDefault(); bar[at + 1].focus(); }
      }
    });
    if (hover.matches) {
      wrap.addEventListener("pointerenter", function (e) { if (e.pointerType !== "mouse") return; clearTimeout(closeTimer); clearTimeout(openTimer); openTimer = setTimeout(function () { open(item); }, current ? 40 : 110); });
      wrap.addEventListener("pointerleave", function (e) { if (e.pointerType !== "mouse") return; clearTimeout(openTimer); closeTimer = setTimeout(function () { close(false); }, 260); });
      panel.addEventListener("pointerenter", function () { clearTimeout(closeTimer); });
      panel.addEventListener("pointerleave", function (e) { if (e.pointerType !== "mouse") return; closeTimer = setTimeout(function () { close(false); }, 260); });
    }
    // other links in the bar close an open menu when hovered, so two never overlap
    panel.addEventListener("pointermove", function (e) {
      var t = e.target.closest && e.target.closest(".nv-tile, .nv-feature"); if (!t) return;
      var r = t.getBoundingClientRect(); t.style.setProperty("--mx", (e.clientX - r.left) + "px"); t.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });
  if (!items.length) return;
  root.classList.add("nv-ready");

  var scrim = el("div", "nv-scrim"); scrim.setAttribute("aria-hidden", "true"); document.body.appendChild(scrim);
  function place(item) {
    var b = item.btn.getBoundingClientRect(), r = root.getBoundingClientRect();
    var card = Math.min(1080, r.width - 32), left = r.left + (r.width - card) / 2;
    var x = Math.max(34, Math.min(card - 34, b.left + b.width / 2 - left));
    item.panel.style.setProperty("--nv-x", Math.round(x) + "px");
  }
  function open(item) {
    if (!wide.matches) return;
    if (current && current !== item) { hide(current); }
    clearTimeout(closeTimer);
    place(item);
    item.panel.hidden = false;
    item.btn.setAttribute("aria-expanded", "true");
    item.wrap.classList.add("is-open");
    root.classList.add("nv-open"); scrim.classList.add("is-on");
    requestAnimationFrame(function () { requestAnimationFrame(function () { item.panel.classList.add("is-open"); }); });
    current = item;
  }
  function hide(item) {
    item.panel.classList.remove("is-open"); item.btn.setAttribute("aria-expanded", "false"); item.wrap.classList.remove("is-open");
    var p = item.panel; var done = function () { if (!p.classList.contains("is-open")) p.hidden = true; };
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) done(); else setTimeout(done, 260);
  }
  function close(refocus) {
    if (!current) return;
    var it = current; current = null; hide(it); root.classList.remove("nv-open"); scrim.classList.remove("is-on");
    if (refocus) it.btn.focus();
  }

  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && current) { var inside = root.contains(document.activeElement); close(inside); } });
  document.addEventListener("click", function (e) { if (current && !root.contains(e.target)) close(false); });
  root.addEventListener("focusout", function (e) {
    if (!current) return; var n = e.relatedTarget; if (n && root.contains(n)) { if (!(current.panel.contains(n) || current.wrap.contains(n))) close(false); return; }
    if (n) close(false);
  });
  window.addEventListener("resize", function () { if (current) { if (!wide.matches) close(false); else place(current); } });
  window.addEventListener("pagehide", function () { close(false); });

  /* A soft pill follows the pointer or keyboard focus along the bar (not on the home page's own header) */
  if (!isHome) {
    var ul = root.querySelector("ul"); if (ul) {
      var pill = el("span", "nv-pill"); pill.setAttribute("aria-hidden", "true"); ul.insertBefore(pill, ul.firstChild);
      var cur = ul.querySelector('a[aria-current="page"]');
      function to(li) {
        if (!li) { pill.style.opacity = "0"; return; }
        var a = li.querySelector("a"), r = a.getBoundingClientRect(), u = ul.getBoundingClientRect();
        var w = li.classList.contains("nv-has") ? li.getBoundingClientRect().width : r.width;
        pill.style.width = w + "px"; pill.style.transform = "translate3d(" + (li.getBoundingClientRect().left - u.left + ul.scrollLeft) + "px,0,0)"; pill.style.opacity = "1";
      }
      Array.prototype.forEach.call(ul.children, function (li) {
        if (li === pill || li.classList.contains("res")) return;
        li.addEventListener("pointerenter", function () { to(li); });
        li.addEventListener("focusin", function () { to(li); });
      });
      ul.addEventListener("pointerleave", function () { pill.style.opacity = "0"; });
      ul.addEventListener("focusout", function () { pill.style.opacity = "0"; });
    }
  }
})();
