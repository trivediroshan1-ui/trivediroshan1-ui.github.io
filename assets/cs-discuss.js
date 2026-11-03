// Case studies: a "Working on this?" panel at the end of the article. Both buttons open the
// message builder on /talk/ with this case study already filled in. Without this script the
// page keeps its existing "Where next" links.
(function () {
  var main = document.querySelector('main');
  var h1 = main && main.querySelector('h1');
  if (!h1 || document.querySelector('.csd')) return;
  var title = h1.textContent.replace(/\s+/g, ' ').trim();
  if (title.length > 90) title = title.slice(0, 87).replace(/\s+\S*$/, '') + '...';
  var after = main.querySelector('nav.pager') || main.querySelector('.hg-next');

  function link(q) {
    var s = Object.keys(q).map(function (k) { return k + '=' + encodeURIComponent(q[k]); }).join('&');
    return '/talk/?' + s + '#cmp-t';
  }

  var box = document.createElement('aside');
  box.className = 'csd';
  box.setAttribute('aria-labelledby', 'csd-t');
  var k = document.createElement('p'); k.className = 'csd-k'; k.textContent = 'Working on this?';
  var t = document.createElement('p'); t.className = 'csd-t'; t.id = 'csd-t';
  t.textContent = 'If this is a problem you have right now, tell me where you are stuck.';
  var d = document.createElement('p'); d.className = 'csd-d';
  d.textContent = 'Both buttons open a short message with this page already named, so you only add what is yours.';
  var acts = document.createElement('div'); acts.className = 'csd-acts';
  var a1 = document.createElement('a'); a1.className = 'csd-b csd-1';
  a1.href = link({ why: 'problem', ref: title }); a1.textContent = 'I have this problem';
  var a2 = document.createElement('a'); a2.className = 'csd-b csd-2';
  a2.href = link({ why: 'feedback', which: 'your case study "' + title + '"' }); a2.textContent = 'Something here is wrong or missing';
  acts.appendChild(a1); acts.appendChild(a2);
  box.appendChild(k); box.appendChild(t); box.appendChild(d); box.appendChild(acts);

  if (after) after.parentNode.insertBefore(box, after); else main.appendChild(box);
})();
