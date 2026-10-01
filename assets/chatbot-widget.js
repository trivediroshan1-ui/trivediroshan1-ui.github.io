/*
 * Site chatbot for roshantrivedi.co.in
 * Answers visitor questions from the site's own content (chatbot-data.js).
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
    "I couldn't find anything about that on this site. Try asking about the case studies, the Secure India Exams project, Roshan's background, or how to contact him — or reach out directly at trivedi.roshan1@gmail.com.";

  var DEFAULT_SUGGESTIONS = [
    "Who is Roshan?",
    "What case studies are here?",
    "What is the MCP lab?",
    "Tell me about Secure India Exams",
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
        "Hi — ask me anything about this site: the case studies, the MCP lab, the writing, the Secure India Exams project, Roshan’s background, or how to get in touch.",
        "bot"
      );
      renderSuggestions();
    }

    function answerLocally() {
      var lastUser = history.length ? history[history.length - 1].content : "";
      var results = search(lastUser);
      if (!results.length) {
        addMessage(FALLBACK, "bot");
        return;
      }
      results.forEach(function (r) {
        var html = linkify(r.entry.answer, r.entry.url);
        if (CONTACT_ENTRY_IDS[r.entry.id]) html += contactActionsHtml();
        addMessage(html, "bot");
      });
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

      if (AI_ENDPOINT) {
        askAI(text);
      } else {
        answerLocally();
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
