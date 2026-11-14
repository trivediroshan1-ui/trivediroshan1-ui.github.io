/*
 * Site chatbot for roshantrivedi.co.in
 * Answers visitor questions from the site's own content, entirely in the browser:
 *  1. hand-written answers in chatbot-data.js (used first when a keyword matches), then
 *  2. passage search over chatbot-index.json, built from every page by scripts/build-chat-index.py.
 * No server, no API key and no cost. It quotes the site; it does not write new text.
 *
 * If AI_ENDPOINT below is set to a deployed Cloudflare Worker URL (see
 * worker/README.md), the bot calls it for natural, conversational Claude
 * answers grounded in the site content. If AI_ENDPOINT is empty, or the
 * Worker is ever unreachable, it automatically falls back to the built-in
 * free keyword-search engine — so the chatbot never breaks either way.
 */
(function () {
  "use strict";

  // Set this to your deployed Worker URL to enable AI-powered answers, e.g.
  // "https://roshantrivedi-chatbot.yoursubdomain.workers.dev". Leave "" to
  // use only the free local keyword-search bot.
  var AI_ENDPOINT = "";
  var AI_TIMEOUT_MS = 12000;

  // Inline SVG avatar — a shield + key motif matching the site's identity/security
  // theme, so the bot has a face without depending on an external image file.
  var AVATAR_SVG =
    '<svg viewBox="0 0 40 40" width="100%" height="100%" aria-hidden="true">' +
    '<circle cx="20" cy="20" r="20" fill="#0f1e2e"></circle>' +
    '<path d="M20 8 L30 12 V19 C30 26 26 30.5 20 33 C14 30.5 10 26 10 19 V12 Z" fill="none" stroke="#4de2ff" stroke-width="2" stroke-linejoin="round"></path>' +
    '<circle cx="20" cy="18.5" r="3.4" fill="none" stroke="#4de2ff" stroke-width="2"></circle>' +
    '<path d="M20 21.8 V26.5 M20 24 H23" fill="none" stroke="#4de2ff" stroke-width="2" stroke-linecap="round"></path>' +
    "</svg>";

  var STOPWORDS = new Set([
    "the","a","an","is","are","was","were","be","been","being","to","of","in","on","for",
    "and","or","with","this","that","it","its","what","who","how","do","does","did","can",
    "you","your","i","about","tell","me","please","there","here","site","website","page",
    "at","as","by","from","into","not","no","yes","my","his","he","him","she","her"
  ]);

  function tokenize(str) {
    return (str.toLowerCase().match(/[a-z0-9']+/g) || []).filter(function (w) {
      return w.length > 1 && !STOPWORDS.has(w);
    });
  }

  // Visitors may type British spellings; the site uses US ones.
  function usSpelling(t) {
    return t.replace(/(organ|author|minim|standard|recogn|summar|central|categor)is/g, "$1iz")
      .replace(/behaviour/g, "behavior").replace(/colour/g, "color").replace(/centre/g, "center")
      .replace(/licence/g, "license").replace(/programme/g, "program").replace(/enrol(?!l)/g, "enroll")
      .replace(/analys(e|ed|ing)\b/g, "analyz$1");
  }

  function hasPhrase(text, phrase) {
    var p = phrase.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp("(^|[^a-z0-9])" + p + "([^a-z0-9]|$)").test(text);
  }

  function scoreEntry(entry, queryTokens, rawQuery) {
    var score = 0;
    var haystack = (entry.title + " " + entry.keywords.join(" ") + " " + entry.answer).toLowerCase();

    // phrase / keyword substring matches (strong signal)
    entry.keywords.forEach(function (kw) {
      if (hasPhrase(rawQuery, kw)) score += 6;
    });
    if (hasPhrase(rawQuery, entry.title)) score += 8;

    // token overlap
    queryTokens.forEach(function (t) {
      if (hasPhrase(haystack, t)) score += 1;
    });

    return score;
  }

  function search(query) {
    var qTokens = tokenize(query);
    var rawQuery = usSpelling(query.toLowerCase());
    if (qTokens.length === 0) return [];

    var scored = (window.SITE_QA || []).map(function (entry) {
      return { entry: entry, score: scoreEntry(entry, qTokens, rawQuery) };
    });

    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.filter(function (s) { return s.score > 0; }).slice(0, 2);
  }


  // ---------- passage search over the whole site (loaded on first use) ----------
  var INDEX = null, INDEX_STATE = "idle", INDEX_WAITERS = [];
  var SYN = {
    pam: ["privileged", "access", "management"], nhi: ["non-human", "identity"], nhis: ["non-human", "identity"],
    mcp: ["model", "context", "protocol"], jit: ["just-in-time"], jea: ["just-enough-access"], zsp: ["zero", "standing", "privilege"],
    ciem: ["cloud", "entitlement"], iga: ["governance", "administration"], mfa: ["multi-factor", "authentication"],
    sso: ["single", "sign-on"], ai: ["artificial", "intelligence"], agent: ["agents", "agentic"], agents: ["agent", "agentic"],
    vault: ["vaulting", "secrets"], secret: ["secrets", "credential"], password: ["credential", "passwordless"],
    breakglass: ["break-glass", "emergency"], "break-glass": ["emergency"], audit: ["auditor", "evidence"],
    hire: ["role", "leadership"], experience: ["years", "career"], exams: ["exam", "nta"], nta: ["exam", "national"],
    privileged: ["pam"], "non-human": ["nhi"], machine: ["nhi", "non-human"], standing: ["zsp"], "just-in-time": ["jit"],
    secrets: ["vault", "credential"], certification: ["certified", "cyberark", "sailpoint"], certifications: ["certified", "cyberark", "sailpoint"],
    recruiter: ["resume", "role"], roles: ["experience", "career"], years: ["experience", "career"]
  };
  function stem(w) {
    w = w.replace(/'s$/, "");
    return w.length > 4 ? w.replace(/(ing|ed|es|s)$/, "") : w;
  }
  function terms(str) {
    return (str.toLowerCase().match(/[a-z0-9][a-z0-9-]*/g) || []).filter(function (w) {
      return w.length > 1 && !STOPWORDS.has(w);
    });
  }
  function buildIndex(raw) {
    var df = {}, total = 0;
    INDEX = raw.map(function (r) {
      var toks = terms(r.x).map(stem);
      var head = terms(r.h + " " + r.t).map(stem);
      var tf = {};
      toks.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
      head.forEach(function (t) { tf[t] = (tf[t] || 0) + 2; });
      Object.keys(tf).forEach(function (t) { df[t] = (df[t] || 0) + 1; });
      var len = toks.length + head.length;
      total += len;
      return { r: r, tf: tf, len: len, head: head };
    });
    INDEX.df = df;
    INDEX.avg = total / Math.max(1, INDEX.length);
  }
  function loadIndex(cb) {
    if (INDEX_STATE === "ready" || INDEX_STATE === "failed") { cb(); return; }
    INDEX_WAITERS.push(cb);
    if (INDEX_STATE === "loading") return;
    INDEX_STATE = "loading";
    fetch("/assets/chatbot-index.json?v=20261114a")
      .then(function (res) { if (!res.ok) throw new Error("status " + res.status); return res.json(); })
      .then(function (raw) { buildIndex(raw); INDEX_STATE = "ready"; })
      .catch(function () { INDEX_STATE = "failed"; })
      .then(function () { var w = INDEX_WAITERS; INDEX_WAITERS = []; w.forEach(function (f) { f(); }); });
  }
  function retrieve(query) {
    if (!INDEX || !INDEX.length) return [];
    var base = terms(query), q = {};
    base.forEach(function (t) {
      var st = stem(t);
      q[st] = Math.max(q[st] || 0, 1);
      (SYN[t] || []).forEach(function (x) { var sx = stem(x); q[sx] = Math.max(q[sx] || 0, 0.5); });
    });
    var qs = Object.keys(q);
    if (!qs.length) return [];
    var N = INDEX.length, k1 = 1.4, b = 0.75, hits = [];
    INDEX.forEach(function (d) {
      var score = 0, matched = 0;
      qs.forEach(function (t) {
        var f = d.tf[t];
        if (!f) return;
        var n = INDEX.df[t] || 0;
        var idf = Math.log(1 + (N - n + 0.5) / (n + 0.5));
        score += q[t] * idf * ((f * (k1 + 1)) / (f + k1 * (1 - b + (b * d.len) / INDEX.avg)));
        if (q[t] === 1) matched++;
      });
      if (!score) return;
      var needed = Math.min(2, base.length);
      if (matched < needed) return;
      hits.push({ d: d, score: score + matched * 0.6 });
    });
    hits.sort(function (a, b2) { return b2.score - a.score; });
    if (!hits.length || hits[0].score < 4.2) return [];
    var out = [hits[0]];
    for (var i = 1; i < hits.length && out.length < 3; i++) {
      var sameSpot = out.some(function (o) { return o.d.r.u === hits[i].d.r.u && o.d.r.h === hits[i].d.r.h; });
      if (!sameSpot && hits[i].score >= hits[0].score * 0.62) out.push(hits[i]);
    }
    return out;
  }
  function passageHtml(hits) {
    var top = hits[0].d.r;
    var html = escapeHtml(top.x);
    html += ' <a class="sc-link" href="' + top.u + (top.a ? "#" + top.a : "") + '">' +
      escapeHtml(top.t + (top.h && top.h !== top.t ? " › " + top.h : "")) + " →</a>";
    if (hits.length > 1) {
      html += '<br><span class="sc-more">Also relevant: ' + hits.slice(1).map(function (h) {
        var r = h.d.r;
        return '<a class="sc-link" href="' + r.u + (r.a ? "#" + r.a : "") + '">' +
          escapeHtml(r.h && r.h !== r.t ? r.t + " › " + r.h : r.t) + "</a>";
      }).join(" · ") + "</span>";
    }
    return html;
  }

  var FALLBACK =
    "I couldn't find anything about that on this site. Try asking about the conditional access and MFA lab, the case studies, the Secure India Exams project, Roshan's background, or how to contact him — or reach out directly at trivedi.roshan1@gmail.com.";

  var DEFAULT_SUGGESTIONS = [
    "What's new on the site?",
    "What did the sign-in lab find?",
    "Which free books are there?",
    "Who is Roshan?",
  ];

  // Page-aware suggestions: shown instead of the defaults when the visitor
  // opens the widget from a page this section matches (checked in order).
  var PAGE_SUGGESTIONS = [
    {
      test: /^\/ca-mfa-lab\/?/,
      suggestions: [
        "What did the sign-in lab find?",
        "What is the access chain?",
        "Which guesses were wrong?",
        "How do I run it myself?",
      ],
    },
    {
      test: /^\/book\/?/,
      suggestions: [
        "Which books are there?",
        "Which book should I read first?",
        "What is in the NHI book?",
        "Is there a printed edition?",
      ],
    },
    {
      test: /^\/(resume\/?)?$/,
      suggestions: [
        "Years and roles",
        "Certifications",
        "Where should I start?",
        "How do I contact him?",
      ],
    },
    {
      test: /^\/nhi-lab\/?/,
      suggestions: [
        "What did the NHI lab find?",
        "What is the NHI framework?",
        "Who bought whom in 2026?",
        "Where is the audit data?",
      ],
    },
    {
      test: /^\/ai-governance-lab\/?/,
      suggestions: [
        "What did the AI governance lab find?",
        "Why do you not trust the 100 percent?",
        "How do I run it myself?",
        "Which controls held up?",
      ],
    },
    {
      test: /^\/secure-india-exams\/?/,
      suggestions: [
        "What's the four-pillar architecture?",
        "How much would this cost?",
        "What happens if there's a breach?",
        "How is AI used and secured in this?",
      ],
    },
    {
      test: /^\/case-studies\/non-human-identity-at-scale\/?/,
      suggestions: [
        "How are non-human identities scored?",
        "What other case studies are here?",
        "Who is Roshan?",
      ],
    },
    {
      test: /^\/case-studies\//,
      suggestions: [
        "What case studies are here?",
        "What was the outcome of this one?",
        "Who is Roshan?",
        "How do I contact him?",
      ],
    },
    {
      test: /^\/writing\//,
      suggestions: [
        "What is this blog post about?",
        "What has Roshan written?",
        "Who is Roshan?",
      ],
    },
  ];

  function getSuggestions() {
    var path = window.location.pathname || "/";
    for (var i = 0; i < PAGE_SUGGESTIONS.length; i++) {
      if (PAGE_SUGGESTIONS[i].test.test(path)) return PAGE_SUGGESTIONS[i].suggestions;
    }
    return DEFAULT_SUGGESTIONS;
  }

  // Entries where it's worth offering one-tap contact actions alongside the answer.
  var CONTACT_ENTRY_IDS = { contact: true, resume: true, "experience-roles": true, "start-here": true };

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function linkify(answer, url) {
    var safe = escapeHtml(answer);
    if (url && url !== "/") {
      safe += ' <a class="sc-link" href="' + url + '">Open this page →</a>';
    }
    return safe;
  }

  function contactActionsHtml() {
    return (
      '<div class="sc-actions">' +
      '<a class="sc-action" href="mailto:trivedi.roshan1@gmail.com">Email</a>' +
      '<a class="sc-action" href="https://www.linkedin.com/in/roshan-trivedi-ciam/" target="_blank" rel="noopener">LinkedIn</a>' +
      '<a class="sc-action" href="/resume/">R\u00e9sum\u00e9</a>' +
      "</div>"
    );
  }

  /* The hand-written answers (chatbot-data.js, about 47 KB) load the first time the panel opens,
     not on every page view. Pages no longer include that script tag. */
  var DATA_STATE = window.SITE_QA ? "ready" : "idle", DATA_WAITERS = [];
  function loadData(cb) {
    if (DATA_STATE === "ready") { cb(); return; }
    DATA_WAITERS.push(cb);
    if (DATA_STATE === "loading") return;
    DATA_STATE = "loading";
    var s = document.createElement("script");
    s.src = "/assets/chatbot-data.js?v=20261114a";
    s.onload = s.onerror = function () { DATA_STATE = "ready"; var w = DATA_WAITERS; DATA_WAITERS = []; w.forEach(function (f) { f(); }); };
    document.head.appendChild(s);
  }

  // "What's new" doodle next to the chat button. Change NOTICE for the next
  // piece of news; a new id shows it again to people who closed the old one.
  // It stops showing after `until`, and never on the pages it points to.
  var NOTICE = {
    id: "ca-mfa-lab-2026-11",
    until: "2026-12-31",
    skip: /^\/(ca-mfa-lab\/.*)?$/, // the home page has its own banner
    kicker: "New",
    text: "I tested 130 conditional access, MFA and AI agent cases. Free book, video and a lab you can run.",
    href: "/ca-mfa-lab/",
    linkText: "See the lab",
    ask: "What did the sign-in lab find?",
  };

  var DOODLE_BOX =
    '<svg class="sc-nd-box" viewBox="0 0 300 150" preserveAspectRatio="none" aria-hidden="true">' +
    '<path pathLength="1" d="M8 12 C70 4 200 9 291 7 C296 50 293 100 294 141 C200 146 90 143 9 145 C5 100 7 50 8 12 Z"></path></svg>';
  var DOODLE_ARROW =
    '<svg class="sc-nd-arrow" viewBox="0 0 60 60" aria-hidden="true">' +
    '<path pathLength="1" d="M6 4 C10 24 26 38 46 44"></path><path pathLength="1" d="M36 47 L47 44 L42 34"></path></svg>';
  var DOODLE_LINE =
    '<svg class="sc-nd-line" viewBox="0 0 120 10" preserveAspectRatio="none" aria-hidden="true">' +
    '<path pathLength="1" d="M2 6 C20 2 34 9 52 5 C70 1 86 9 118 4"></path></svg>';

  function noticeWanted() {
    if (!NOTICE || !NOTICE.id) return false;
    if (new Date() > new Date(NOTICE.until + "T23:59:59")) return false;
    if (NOTICE.skip && NOTICE.skip.test(window.location.pathname || "/")) return false;
    try { if (window.localStorage.getItem("sc-notice-closed") === NOTICE.id) return false; } catch (e) {}
    return true;
  }

  function rememberNoticeClosed() {
    try { window.localStorage.setItem("sc-notice-closed", NOTICE.id); } catch (e) {}
  }

  function init() {
    if (document.getElementById("site-chatbot-root")) return;

    var root = el("div", "");
    root.id = "site-chatbot-root";

    var launcher = el(
      "button",
      "sc-launcher",
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
    );
    launcher.type = "button";
    launcher.setAttribute("aria-label", "Ask about this site");

    var panel = el("div", "sc-panel");
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Site assistant");
    panel.style.display = "none";

    panel.innerHTML =
      '<div class="sc-header">' +
      '<div class="sc-avatar" aria-hidden="true">' + AVATAR_SVG + "</div>" +
      '<div class="sc-header-text"><strong>Ask about this site</strong><small>Answers pulled straight from this site’s content</small></div>' +
      '<button type="button" class="sc-close" aria-label="Close">&#215;</button>' +
      "</div>" +
      '<div class="sc-messages" id="sc-messages"></div>' +
      '<div class="sc-suggestions" id="sc-suggestions"></div>' +
      '<form class="sc-form" id="sc-form">' +
      '<input class="sc-input" id="sc-input" type="text" autocomplete="off" placeholder="e.g. What case studies are here?" aria-label="Ask a question" />' +
      '<button class="sc-send" type="submit" aria-label="Send">&#8594;</button>' +
      "</form>";

    root.appendChild(panel);
    root.appendChild(launcher);
    document.body.appendChild(root);

    // Some pages do not link the widget's stylesheet. Without it the button
    // sits at the end of the page, so load the styles here when they are missing.
    if (window.getComputedStyle(root).position !== "fixed") {
      var wcss = document.createElement("link");
      wcss.rel = "stylesheet";
      wcss.href = "/assets/chatbot-widget.css?v=20261114a";
      document.head.appendChild(wcss);
    }

    var messagesEl = panel.querySelector("#sc-messages");
    var suggestionsEl = panel.querySelector("#sc-suggestions");
    var formEl = panel.querySelector("#sc-form");
    var inputEl = panel.querySelector("#sc-input");
    var closeBtn = panel.querySelector(".sc-close");
    var greeted = false;

    var history = []; // {role: "user"|"assistant", content: string} — used for AI follow-ups

    function addMessage(text, who) {
      var row = el("div", "sc-row sc-row-" + who);
      if (who === "bot") {
        row.appendChild(el("div", "sc-avatar-sm", AVATAR_SVG));
      }
      var bubble = el("div", "sc-bubble sc-bubble-" + who, text);
      row.appendChild(bubble);
      messagesEl.appendChild(row);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return row;
    }

    function addTyping() {
      var row = el("div", "sc-row sc-row-bot");
      row.appendChild(el("div", "sc-avatar-sm", AVATAR_SVG));
      row.appendChild(
        el(
          "div",
          "sc-bubble sc-bubble-bot sc-typing",
          "<span></span><span></span><span></span>"
        )
      );
      messagesEl.appendChild(row);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return row;
    }

    function renderSuggestions() {
      suggestionsEl.innerHTML = "";
      getSuggestions().forEach(function (s) {
        var chip = el("button", "sc-chip", escapeHtml(s));
        chip.type = "button";
        chip.addEventListener("click", function () {
          handleQuery(s);
        });
        suggestionsEl.appendChild(chip);
      });
    }

    function greet() {
      if (greeted) return;
      greeted = true;
      addMessage(
        "Hi, ask me anything about this site: the new conditional access and MFA lab, the case studies, the MCP lab, the AI governance lab, the writing, the Secure India Exams project, Roshan’s background, or how to get in touch. I answer from the text on the site, so I quote it rather than make anything up.",
        "bot"
      );
      renderSuggestions();
    }

    function answerLocally() {
      var lastUser = history.length ? history[history.length - 1].content : "";
      var results = search(lastUser);
      var strong = results.length && results[0].score >= 6;
      function showCurated() {
        results.filter(function (r, i) { return i === 0 || r.score >= results[0].score * 0.85; }).forEach(function (r) {
          var html = linkify(r.entry.answer, r.entry.url);
          if (CONTACT_ENTRY_IDS[r.entry.id]) html += contactActionsHtml();
          addMessage(html, "bot");
        });
      }
      if (strong) { showCurated(); return; }
      function viaIndex() {
        var hits = retrieve(lastUser);
        if (hits.length) { addMessage(passageHtml(hits), "bot"); return; }
        if (results.length && results[0].score >= 3) { showCurated(); return; }
        addMessage(FALLBACK, "bot");
      }
      if (INDEX_STATE === "ready" || INDEX_STATE === "failed") { viaIndex(); return; }
      var typingRow = addTyping();
      loadIndex(function () { typingRow.remove(); viaIndex(); });
    }

    function askAI(text) {
      var typingRow = addTyping();
      var controller = typeof AbortController !== "undefined" ? new AbortController() : null;
      var timer = setTimeout(function () {
        if (controller) controller.abort();
      }, AI_TIMEOUT_MS);

      fetch(AI_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller ? controller.signal : undefined,
        body: JSON.stringify({
          message: text,
          history: history.slice(0, -1), // everything before this turn
        }),
      })
        .then(function (res) {
          if (!res.ok) throw new Error("bad status " + res.status);
          return res.json();
        })
        .then(function (data) {
          clearTimeout(timer);
          typingRow.remove();
          if (!data || !data.reply) throw new Error("empty reply");
          addMessage(escapeHtml(data.reply), "bot");
          history.push({ role: "assistant", content: data.reply });
          if (/contact|email|linkedin|resume|reach|hire/i.test(text)) {
            addMessage(contactActionsHtml(), "bot");
          }
        })
        .catch(function () {
          clearTimeout(timer);
          typingRow.remove();
          // Silent fallback to the free local bot — visitor never sees an error.
          answerLocally();
        });
    }

    function handleQuery(text) {
      text = text.trim();
      if (!text) return;
      addMessage(escapeHtml(text), "user");
      suggestionsEl.innerHTML = "";
      history.push({ role: "user", content: text });

      loadData(function () {
        if (AI_ENDPOINT) {
          askAI(text);
        } else {
          answerLocally();
        }
      });
    }

    function openPanel() {
      loadData(function () {});
      loadIndex(function () {});
      hideNotice(false);
      panel.style.display = "flex";
      launcher.classList.add("sc-launcher-open");
      greet();
      setTimeout(function () { inputEl.focus(); }, 50);
    }

    function closePanel() {
      panel.style.display = "none";
      launcher.classList.remove("sc-launcher-open");
    }

    launcher.addEventListener("click", function () {
      if (panel.style.display === "none") openPanel();
      else closePanel();
    });
    closeBtn.addEventListener("click", closePanel);

    formEl.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = inputEl.value;
      inputEl.value = "";
      handleQuery(v);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.style.display !== "none") closePanel();
    });

    // The doodle notice: appears after a short pause, blinks gently, and goes
    // away for good once closed. Opening the chat also hides it for this visit.
    var notice = null;
    function hideNotice(forever) {
      if (!notice) return;
      notice.classList.add("sc-nd-out");
      launcher.classList.remove("sc-launcher-news");
      var n = notice; notice = null;
      setTimeout(function () { if (n.parentNode) n.parentNode.removeChild(n); }, 300);
      if (forever) rememberNoticeClosed();
    }
    if (noticeWanted()) {
      var showNotice = function () {
        if (panel.style.display !== "none") return;
        notice = el("aside", "sc-notice");
        notice.setAttribute("aria-label", "What's new on this site");
        notice.innerHTML =
          DOODLE_BOX + DOODLE_ARROW +
          '<p class="sc-nd-kicker"><span class="sc-nd-dot" aria-hidden="true"></span>' + escapeHtml(NOTICE.kicker) + "</p>" +
          '<p class="sc-nd-text">' + escapeHtml(NOTICE.text) + DOODLE_LINE + "</p>" +
          '<p class="sc-nd-actions"><a class="sc-nd-link" href="' + NOTICE.href + '">' + escapeHtml(NOTICE.linkText) + " &#8594;</a>" +
          '<button type="button" class="sc-nd-ask">Ask me about it</button></p>' +
          '<button type="button" class="sc-nd-close" aria-label="Close this notice">&#215;</button>';
        root.insertBefore(notice, launcher);
        launcher.classList.add("sc-launcher-news");
        notice.querySelector(".sc-nd-close").addEventListener("click", function () { hideNotice(true); });
        notice.querySelector(".sc-nd-link").addEventListener("click", function () { rememberNoticeClosed(); });
        notice.querySelector(".sc-nd-ask").addEventListener("click", function () {
          hideNotice(true);
          openPanel();
          handleQuery(NOTICE.ask);
        });
      };
      setTimeout(function () {
        var css = document.createElement("link");
        css.rel = "stylesheet";
        css.href = "/assets/sc-notice.css?v=20261114a";
        css.onload = showNotice;
        document.head.appendChild(css);
      }, 1800);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
