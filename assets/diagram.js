(function () {
  document.querySelectorAll('.anim-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var card = b.closest('.diagram-card');
      var paused = card.classList.toggle('paused');
      b.setAttribute('aria-pressed', paused ? 'true' : 'false');
      b.textContent = paused ? 'Play animation' : 'Pause animation';
      card.querySelectorAll('svg').forEach(function (s) { if (s.pauseAnimations) { paused ? s.pauseAnimations() : s.unpauseAnimations(); } });
    });
  });
})();
