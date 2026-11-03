// Talk page: builds a first message from a few fields. Nothing is sent anywhere by this script;
// the visitor copies it into LinkedIn or opens it in their own email app.
(function () {
  var form = document.getElementById('cmp');
  if (!form) return;
  var out = document.getElementById('cmp-msg');
  var mail = document.getElementById('cmp-mail');
  var done = document.getElementById('cmp-done');
  var LI = 'https://www.linkedin.com/in/roshan-trivedi-ciam/';
  var EMAIL = 'trivedi.roshan1@gmail.com';

  function v(n) { return (form.elements[n].value || '').trim().replace(/[.\s]+$/, ''); }
  function why() { return form.querySelector('input[name="why"]:checked').value; }
  // Each part is [text, isPlaceholder]; placeholders show highlighted so the gap is visible.
  function f(n, ph) { var x = v(n); return x ? [x, false] : ['[' + ph + ']', true]; }

  function parts() {
    var w = why(), p = [['Hi Roshan,\n\n', false]];
    if (w === 'role') {
      p.push(['I am hiring for the role of ', false], f('role', 'role title'));
      if (v('team')) p.push([' in ', false], [v('team'), false]);
      p.push(['. Location: ', false], f('where', 'location'),
        ['.\n\nWould you be open to a conversation about it?', false]);
    } else if (w === 'problem') {
      if (REF) p.push(['I read your case study "' + REF + '". ', false]);
      p.push(['I am working on a PAM or credential problem: ', false], f('fix', 'what you are trying to fix'), ['.', false]);
      if (v('tools')) p.push([' Platforms involved: ', false], [v('tools'), false], ['.', false]);
      p.push(['\n\nCould we talk it through?', false]);
    } else {
      p.push(['I read ', false], f('which', 'which lab or book'), ['. ', false], f('gap', 'what looks wrong or missing'), ['.', false]);
    }
    var n = v('name');
    p.push(['\n\n' + (n ? 'Thanks,\n' + n : 'Thanks'), false]);
    return p;
  }
  function text() { return parts().map(function (x) { return x[0]; }).join(''); }
  function subject() {
    var w = why();
    return w === 'role' ? 'Role: ' + (v('role') || 'identity security')
      : w === 'problem' ? 'A PAM or credential problem'
      : 'Feedback: ' + (v('which') || 'a lab or book');
  }

  function render() {
    var w = why();
    [].forEach.call(form.querySelectorAll('.cmp-fields'), function (d) { d.hidden = d.getAttribute('data-for') !== w; });
    out.textContent = '';
    parts().forEach(function (x) {
      if (x[1]) { var m = document.createElement('mark'); m.textContent = x[0]; out.appendChild(m); }
      else out.appendChild(document.createTextNode(x[0]));
    });
    mail.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject()) + '&body=' + encodeURIComponent(text());
    done.textContent = '';
  }

  function copy(s) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(s);
    return new Promise(function (ok, no) {
      var t = document.createElement('textarea');
      t.value = s; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy') ? ok() : no(); } catch (e) { no(e); }
      t.remove();
    });
  }

  document.getElementById('cmp-li').addEventListener('click', function () {
    // Start the copy first, while this page still has focus, then open LinkedIn in a new tab.
    copy(text()).then(function () {
      done.textContent = 'Copied. Paste it into a LinkedIn message.';
    }, function () {
      done.textContent = 'Could not copy. Select the message above and copy it, then open LinkedIn.';
    });
    var win = window.open(LI, '_blank');
    if (win) win.opener = null;
  });

  form.addEventListener('input', render);
  form.addEventListener('change', render);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  // A link from a case study can open a path with its page already named:
  // /talk/?why=problem&ref=<title> or /talk/?why=feedback&which=<text>. Plain text only, capped.
  var REF = '';
  try {
    var q = new URLSearchParams(location.search);
    var cap = function (x) { return (x || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, 120); };
    var w = q.get('why');
    if (w === 'role' || w === 'problem' || w === 'feedback') form.querySelector('input[name="why"][value="' + w + '"]').checked = true;
    REF = cap(q.get('ref'));
    if (q.get('which')) form.elements.which.value = cap(q.get('which'));
  } catch (e) {}
  form.hidden = false;
  form.closest('.cmp').classList.add('cmp-on');
  render();
})();
