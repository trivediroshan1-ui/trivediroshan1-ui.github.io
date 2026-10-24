/* Cost estimator for the "use it in your organisation" page. Example values only; the person replaces them. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var ids = ["uses", "hrsUse", "build", "rate", "lic", "review"];
  function inr(n) { return "₹" + Math.round(n).toLocaleString("en-IN"); }
  function num(id) { var v = parseFloat($(id).value); return isFinite(v) && v >= 0 ? v : 0; }
  function calc() {
    var uses = num("uses"), hrsUse = num("hrsUse"), build = num("build"), rate = num("rate"), lic = num("lic"), review = num("review");
    var setup = (uses * hrsUse + build) * rate;
    var run = review * rate + lic;
    $("rSetup").textContent = inr(setup);
    $("rRun").textContent = inr(run);
    $("rFirst").textContent = inr(setup + run);
  }
  if (!$("uses")) return;
  ids.forEach(function (i) { $(i).addEventListener("input", calc); });
  calc();
})();
