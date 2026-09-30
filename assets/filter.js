(function () {
  var chips = document.querySelectorAll('.chip');
  var cards = document.querySelectorAll('.card[data-group]');
  var count = document.getElementById('filter-count');
  if (!chips.length) return;
  function apply(key) {
    var n = 0;
    cards.forEach(function (c) {
      var show = key === 'all' || c.getAttribute('data-group') === key;
      c.hidden = !show;
      if (show) n++;
    });
    chips.forEach(function (b) {
      var on = b.getAttribute('data-filter') === key;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    count.textContent = key === 'all' ? '' : n + (n === 1 ? ' case study' : ' case studies');
    try { history.replaceState(null, '', key === 'all' ? location.pathname : '#' + key); } catch (e) {}
  }
  chips.forEach(function (b) {
    b.addEventListener('click', function () { apply(b.getAttribute('data-filter')); });
  });
  var h = location.hash.slice(1);
  if (h && document.querySelector('.chip[data-filter="' + h + '"]')) apply(h);
})();
