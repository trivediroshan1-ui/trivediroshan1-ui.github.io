// Home page only. Shows a small dock with the three ways to reach me once the
// hero is out of view, and hides it again while the contact section is on screen.
(function () {
  var hero = document.querySelector('.hero');
  var contact = document.getElementById('contact');
  if (!hero || !contact || !('IntersectionObserver' in window)) return;
  try { if (sessionStorage.getItem('nextstep-off') === '1') return; } catch (e) {}

  var bar = document.createElement('aside');
  bar.className = 'nextstep';
  bar.setAttribute('aria-label', 'Next step');
  bar.innerHTML =
    '<span class="ns-q">Hiring or curious?</span>' +
    '<a class="ns-p" href="https://www.linkedin.com/in/roshan-trivedi-ciam/">Message me</a>' +
    '<a class="ns-s" href="/resume/">Résumé</a>' +
    '<button type="button" class="ns-x" aria-label="Hide this bar">×</button>';
  document.body.appendChild(bar);

  var heroGone = false, atContact = false;
  function update() { bar.classList.toggle('on', heroGone && !atContact); }
  new IntersectionObserver(function (e) { heroGone = !e[0].isIntersecting; update(); }).observe(hero);
  new IntersectionObserver(function (e) { atContact = e[0].isIntersecting; update(); }).observe(contact);
  bar.querySelector('.ns-x').addEventListener('click', function () {
    bar.remove();
    try { sessionStorage.setItem('nextstep-off', '1'); } catch (e) {}
  });
})();
