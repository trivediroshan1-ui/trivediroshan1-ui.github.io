/*
 * Site chatbot for roshantrivedi.co.in
 * A free, client-side "ask the site" widget. It answers ONLY from the
 * content in chatbot-data.js (window.SITE_QA), which is written from the
 * site's own published text — so it can't invent facts about the site.
 * No API key, no backend, no cost.
 */
(function () {
  "use strict";

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

  function scoreEntry(entry, queryTokens, rawQuery) {
    var score = 0;
    var haystack = (entry.title + " " + entry.keywords.join(" ") + " " + entry.answer).toLowerCase();

    // phrase / keyword substring matches (strong signal)
    entry.keywords.forEach(function (kw) {
      if (rawQuery.indexOf(kw.toLowerCase()) !== -1) score += 6;
    });
    if (rawQuery.indexOf(entry.title.toLowerCase()) !== -1) score += 8;

    // token overlap
    queryTokens.forEach(function (t) {
      if (haystack.indexOf(t) !== -1) score += 1;
    });

    return score;
  }

  function search(query) {
    var qTokens = tokenize(query);
    var rawQuery = query.toLowerCase();
    if (qTokens.length === 0) return [];

    var scored = window.SITE_QA.map(function (entry) {
      return { entry: entry, score: scoreEntry(entry, qTokens, rawQuery) };
    });

    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.filter(function (s) { return s.score > 0; }).slice(0, 2);
  }

  var FALLBACK =
    "I couldn't find anything about that on this site. Try asking about the case studies, the Secure India Exams project, the MCP Human Approval Gateway lab, Roshan's background, or how to contact him — or reach out directly at trivedi.roshan1@gmail.com.";

  var DEFAULT_SUGGESTIONS = [
    "Who is Roshan?",
    "What case studies are here?",
    "Tell me about Secure India Exams",
    "How do I contact him?",
  ];

  // Page-aware suggestions: shown instead of the defaults when the visitor
  // opens the widget from a page this section matches (checked in order).
  var PAGE_SUGGESTIONS = [
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
        "What's the interactive sandbox?",
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
        "What case studies are here?",
        "Who is Roshan?",
      ],
    },
    {
      test: /^\/mcp-human-approval-gateway\/?/,
      suggestions: [
        "What is the MCP Human Approval Gateway?",
        "How does this relate to Agentic AI Identity Governance?",
        "What case studies are here?",
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
  var CONTACT_ENTRY_IDS = { contact: true, resume: true };

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
      '<a class="sc-action" href="https://www.linkedin.com/in/roshan-trivedi-ciam-49413a54/" target="_blank" rel="noopener">LinkedIn</a>' +
      '<a class="sc-action" href="/Roshan_Trivedi_Resume.pdf" target="_blank" rel="noopener">Resume</a>' +
      "</div>"
    );
  }

  function init() {
    if (!window.SITE_QA || !window.SITE_QA.length) return;
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

    var messagesEl = panel.querySelector("#sc-messages");
    var suggestionsEl = panel.querySelector("#sc-suggestions");
    var formEl = panel.querySelector("#sc-form");
    var inputEl = panel.querySelector("#sc-input");
    var closeBtn = panel.querySelector(".sc-close");
    var greeted = false;

    function addMessage(text, who) {
      var row = el("div", "sc-row sc-row-" + who);
      var bubble = el("div", "sc-bubble sc-bubble-" + who, text);
      row.appendChild(bubble);
      messagesEl.appendChild(row);
      messagesEl.scrollTop = messagesEl.scrollHeight;
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
        "Hi — ask me anything about this site: the case studies, the Secure India Exams project, the MCP lab, Roshan’s background, or how to get in touch.",
        "bot"
      );
      renderSuggestions();
    }

    function handleQuery(text) {
      text = text.trim();
      if (!text) return;
      addMessage(escapeHtml(text), "user");
      suggestionsEl.innerHTML = "";

      var results = search(text);
      if (!results.length) {
        addMessage(FALLBACK, "bot");
      } else {
        results.forEach(function (r) {
          var html = linkify(r.entry.answer, r.entry.url);
          if (CONTACT_ENTRY_IDS[r.entry.id]) html += contactActionsHtml();
          addMessage(html, "bot");
        });
      }
    }

    function openPanel() {
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
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
