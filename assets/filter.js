(function () {
  var chips = document.querySelectorAll('.chip');
  var cards = document.querySelectorAll('.card[data-group]');
  var count = document.getElementById('filter-count');
  var box = document.getElementById('cs-search');
  var none = document.getElementById('no-results');
  if (!chips.length) return;
  var group = 'all';
  var query = '';
  var texts = [];
  cards.forEach(function (c, i) { texts[i] = ((c.textContent || '') + ' ' + (c.getAttribute('data-keywords') || '')).toLowerCase().replace(/\s+/g, ' '); });
  function render() {
    var n = 0;
    var words = query.split(/\s+/).filter(Boolean);
    cards.forEach(function (c, i) {
      var okGroup = group === 'all' || c.getAttribute('data-group') === group;
      var okText = words.every(function (w) { return texts[i].indexOf(w) !== -1; });
      var show = okGroup && okText;
      c.hidden = !show;
      if (show) n++;
    });
    chips.forEach(function (b) {
      var on = b.getAttribute('data-filter') === group;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    var filtered = group !== 'all' || words.length > 0;
    count.textContent = filtered ? n + (n === 1 ? ' case study' : ' case studies') : '';
    if (none) none.hidden = n !== 0;
  }
  function apply(key) {
    group = key;
    render();
    try { history.replaceState(null, '', key === 'all' ? location.pathname : '#' + key); } catch (e) {}
  }
  chips.forEach(function (b) {
    b.addEventListener('click', function () { apply(b.getAttribute('data-filter')); });
  });
  if (box) {
    box.addEventListener('input', function () { query = box.value.toLowerCase().trim(); render(); });
    box.addEventListener('keydown', function (e) { if (e.key === 'Escape') { box.value = ''; query = ''; render(); } });
  }
  var h = location.hash.slice(1);
  if (h && document.querySelector('.chip[data-filter="' + h + '"]')) apply(h);
})();
