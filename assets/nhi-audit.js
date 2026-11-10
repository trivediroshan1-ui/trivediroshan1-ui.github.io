/* Filters the audit table. Works without scripts: all rows show by default. */
(function () {
  var box = document.getElementById('audit-filters');
  var table = document.getElementById('audit-table');
  if (!box || !table) return;
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);
  var count = document.getElementById('audit-count');
  var labels = { all: 'all', wrong: 'cases with a wrong guess', masked: 'cases with a control no check noticed', limit: 'cases with a recorded limit', r1: 'first-run cases', r2: 'second-run cases', r3: 'third-run cases', r4: 'fourth-run cases' };
  function match(row, f) {
    if (f === 'wrong') return row.dataset.wrong === '1';
    if (f === 'masked') return row.dataset.masked === '1';
    if (f === 'limit') return row.dataset.limit === '1';
    if (f === 'r1') return row.dataset.run === '1';
    if (f === 'r2') return row.dataset.run === '2';
    if (f === 'r3') return row.dataset.run === '3';
    if (f === 'r4') return row.dataset.run === '4';
    return true;
  }
  box.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-f]');
    if (!b) return;
    var f = b.dataset.f, shown = 0;
    Array.prototype.forEach.call(box.querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    rows.forEach(function (r) { var ok = match(r, f); r.hidden = !ok; if (ok) shown++; });
    if (count) count.textContent = f === 'all' ? 'Showing all ' + rows.length + ' cases.' : 'Showing ' + shown + ' ' + labels[f] + '.';
  });
})();
