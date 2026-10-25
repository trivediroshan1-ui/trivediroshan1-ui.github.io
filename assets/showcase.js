/* Case-study showcase pieces, built from what is already on the page (nothing is invented):
   a facts strip, key-takeaway cards, a contents list for narrow screens and an author card.
   Every page reads fine without this file. */
(function () {
  var main = document.querySelector("main");
  if (!main || !document.body.classList.contains("read")) return;
  var hero = main.querySelector("header.hero");
  if (!hero) return;

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function pad(n) { return (n < 10 ? "0" : "") + n; }

  /* ---- Facts strip ---- */
  var eyebrow = hero.querySelector(".eyebrow");
  var meta = hero.querySelector(".meta");
  var reviewed = hero.querySelector(".reviewed");
  var topic = eyebrow ? eyebrow.textContent.split("·").map(function (s) { return s.trim(); }).filter(function (s) { return s && !/^case study$/i.test(s); }).join(" · ") : "";
  var role = "";
  if (meta) {
    var first = meta.firstChild;
    role = (first && first.nodeType === 3 ? first.textContent : "").replace(/[·\s]+$/, "").trim();
  }
  var chapters = main.querySelectorAll("main > section[id]:not(#sources):not(#tags):not(#references), main > section:not([id])");
  var chapterCount = 0;
  Array.prototype.forEach.call(chapters, function (s) { if (s.querySelector("h2")) chapterCount++; });
  var words = (main.innerText || "").trim().split(/\s+/).length;
  var mins = Math.max(1, Math.round(words / 220));
  var sources = main.querySelectorAll("#sources ol.sources > li, #sources ul.sources > li").length;

  var rows = [];
  if (topic) rows.push(["Topic", topic]);
  if (role) rows.push(["Perspective", role]);
  if (reviewed) rows.push(["Last reviewed", reviewed.textContent.replace(/^Last reviewed\s*/i, "")]);
  rows.push(["Length", mins + " min read", chapterCount ? chapterCount + " chapters" : ""]);
  if (sources) rows.push(["Sources", sources + " primary references"]);
  if (rows.length >= 2) {
    var dl = el("dl", "facts");
    rows.forEach(function (r) {
      var d = el("div"); d.appendChild(el("dt", null, r[0]));
      var dd = el("dd", null, r[1]);
      if (r[2]) dd.appendChild(el("small", null, r[2]));
      d.appendChild(dd); dl.appendChild(d);
    });
    hero.appendChild(dl);
  }

  /* ---- Key takeaways: first sentence becomes the card headline ---- */
  var tl = main.querySelector(".tldr");
  if (tl) {
    var h = tl.querySelector("h2"); if (h) h.textContent = "Key takeaways";
    Array.prototype.forEach.call(tl.querySelectorAll("li"), function (li) {
      if (li.querySelector("strong")) return;
      var m = li.innerHTML.match(/^([\s\S]{12,230}?[.!?])\s+(?=[A-Z“"&])([\s\S]+)$/);
      if (m) { li.innerHTML = "<strong>" + m[1] + "</strong>" + m[2]; return; }
      if (li.textContent.length <= 230) li.innerHTML = "<strong>" + li.innerHTML + "</strong>"; // one sentence: it is the headline
    });
  }

  /* ---- Contents (shown on narrow screens only, the rail covers wide ones) ---- */
  var secs = Array.prototype.filter.call(main.querySelectorAll("main > section"), function (s) { return s.querySelector("h2"); });
  if (secs.length >= 4) {
    var det = el("details", "rt-contents");
    det.appendChild(el("summary", null, "Contents · " + chapterCount + " chapters"));
    var ol = el("ol"), n = 0, used = {};
    secs.forEach(function (s) {
      var h2 = s.querySelector("h2");
      var id = s.id || h2.id;
      if (!id) {
        id = h2.textContent.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "section";
        var base = id, k = 2; while (used[id] || document.getElementById(id)) id = base + "-" + k++;
        h2.id = id;
      }
      used[id] = 1;
      var a = el("a", null, h2.textContent.trim()); a.href = "#" + id;
      if (s.id !== "sources" && s.id !== "references") { n++; a.dataset.n = pad(n); }
      var li = el("li"); li.appendChild(a); ol.appendChild(li);
    });
    det.appendChild(ol);
    var anchor = tl || hero;
    anchor.parentNode.insertBefore(det, anchor.nextSibling);
  }

  /* ---- Author card, before the previous/next pager ---- */
  var pager = main.querySelector(".pager");
  var next = main.querySelector(".hg-next");
  var slot = pager || next;
  if (slot && !main.querySelector(".byline")) {
    var by = el("aside", "byline"); by.setAttribute("aria-label", "About the author");
    var img = new Image(); img.src = "/assets/roshan-trivedi-520.webp"; img.alt = ""; img.width = 72; img.height = 72; img.loading = "lazy";
    var p = el("p");
    p.innerHTML = "<b>Written by Roshan Trivedi</b>I work on privileged access, credentials and, lately, how a person stays in control when an AI agent acts. These pages are my own notes, written to be useful on their own. " +
      '<a href="/about/">More about me</a> &middot; <a href="https://www.linkedin.com/in/roshan-trivedi-ciam/" rel="noopener">LinkedIn</a>';
    by.appendChild(img); by.appendChild(p);
    slot.parentNode.insertBefore(by, slot);
  }
})();
