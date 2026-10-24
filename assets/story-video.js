/* Story video: chapters you can tap, a caption that changes as the video plays, a thin progress bar. */
(function () {
  var v = document.getElementById("sv-video");
  if (!v) return;
  var cap = document.getElementById("sv-cap"), bar = document.getElementById("sv-bar");
  var btns = [].slice.call(document.querySelectorAll(".sv-ch button"));
  var starts = btns.map(function (b) { return +b.dataset.t; });
  var cur = -1;
  function show(i) {
    if (i === cur) return;
    cur = i;
    btns.forEach(function (b, k) { b.setAttribute("aria-current", k === i ? "true" : "false"); });
    cap.textContent = btns[i].dataset.d;
    cap.classList.remove("in"); void cap.offsetWidth; cap.classList.add("in");
  }
  function idx(t) { var k = 0; for (var i = 0; i < starts.length; i++) if (t >= starts[i]) k = i; return k; }
  v.addEventListener("timeupdate", function () {
    show(idx(v.currentTime));
    if (bar && v.duration) bar.style.width = (100 * v.currentTime / v.duration) + "%";
  });
  btns.forEach(function (b) {
    b.addEventListener("click", function () {
      v.currentTime = +b.dataset.t;
      var p = v.play(); if (p && p.catch) p.catch(function () {});
      show(idx(+b.dataset.t));
    });
  });
  show(0);
})();
