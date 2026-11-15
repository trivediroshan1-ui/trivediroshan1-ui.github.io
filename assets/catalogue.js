/* Filters for /labs/cases/. Every row is already in the page; this only hides the ones that do not match.
   The filters are kept in the address (?lab=nhi&topic=...&q=...) so a filtered list can be shared. */
(function () {
  "use strict";
  var q = document.getElementById("cat-q"), lab = document.getElementById("cat-lab"),
      topic = document.getElementById("cat-topic"), guess = document.getElementById("cat-guess"),
      n = document.getElementById("cat-n");
  if (!q || !lab || !topic || !guess || !n) return;
  var rows = Array.prototype.slice.call(document.querySelectorAll(".cat-t tbody tr"));
  var text = rows.map(function (r) { return r.textContent.toLowerCase(); });
  var total = rows.length, t;

  function apply(push) {
    var words = q.value.toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
    rows.forEach(function (r, i) {
      var ok = (!lab.value || r.getAttribute("data-lab") === lab.value) &&
        (!topic.value || r.getAttribute("data-topics").split("|").indexOf(topic.value) >= 0) &&
        (!guess.value || r.getAttribute("data-guess") === guess.value) &&
        words.every(function (w) { return text[i].indexOf(w) >= 0; });
      r.hidden = !ok;
      if (ok) shown++;
    });
    n.textContent = shown === total ? "Showing all " + total + " cases." :
      shown === 0 ? "No case matches. Try fewer words, or set a filter back to all." :
      "Showing " + shown + " of " + total + " cases.";
    if (push && window.history && history.replaceState) {
      var p = new URLSearchParams();
      if (q.value.trim()) p.set("q", q.value.trim());
      if (lab.value) p.set("lab", lab.value);
      if (topic.value) p.set("topic", topic.value);
      if (guess.value) p.set("guess", guess.value);
      var s = p.toString();
      history.replaceState(null, "", location.pathname + (s ? "?" + s : ""));
    }
  }
  try {
    var p = new URLSearchParams(location.search);
    q.value = p.get("q") || "";
    [[lab, "lab"], [topic, "topic"], [guess, "guess"]].forEach(function (x) {
      var v = p.get(x[1]);
      if (v && Array.prototype.some.call(x[0].options, function (o) { return o.value === v; })) x[0].value = v;
    });
  } catch (e) {}
  q.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { apply(true); }, 120); });
  [lab, topic, guess].forEach(function (s) { s.addEventListener("change", function () { apply(true); }); });
  apply(false);
})();
