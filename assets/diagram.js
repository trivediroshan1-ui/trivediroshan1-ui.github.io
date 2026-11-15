(function () {
  document.querySelectorAll('.anim-toggle').forEach(function (b) {
    var card = b.closest('.diagram-card');
    // motion-gate.js stops a diagram after three loops; then this button plays it again.
    card.addEventListener('mg:done', function () {
      b.setAttribute('aria-pressed', 'true');
      b.textContent = 'Play again';
    });
    b.addEventListener('click', function () {
      if (card.hasAttribute('data-mg-done') && window.mgRestart) {
        card.classList.remove('paused');
        window.mgRestart(card);
        b.setAttribute('aria-pressed', 'false');
        b.textContent = 'Pause animation';
        return;
      }
      var paused = card.classList.toggle('paused');
      b.setAttribute('aria-pressed', paused ? 'true' : 'false');
      b.textContent = paused ? 'Play animation' : 'Pause animation';
      card.querySelectorAll('svg').forEach(function (s) { if (s.pauseAnimations) { paused ? s.pauseAnimations() : s.unpauseAnimations(); } });
    });
  });
})();
