(function () {
  var TIERS = [
    { id: 't0', name: 'Tier 0 \u2014 identity control plane', color: '#ff7a93',
      fix: 'Tier 0 is the domain controllers, PKI, PAM vaults and the admin plane of your cloud identity provider. One admin acting alone here is the whole game.',
      qs: [
        ['Does any Tier 0 action need a second approver (dual control or M-of-N)?', 'Add dual or M-of-N authorization for Tier 0 actions.'],
        ['Do Tier 0 admins sign in with hardware keys (FIDO2) rather than SMS or push approval?', 'Move Tier 0 admins to phishing-resistant authentication such as FIDO2 keys.'],
        ['Are Tier 0 sessions recorded, with re-authentication every so often?', 'Record Tier 0 sessions and force periodic re-authentication.'],
        ['Is your cloud identity provider\u2019s global admin role governed as strictly as your domain admins?', 'Treat the cloud IdP global admin role as Tier 0, with the same review and controls.']
      ] },
    { id: 't1', name: 'Tier 1 \u2014 apps, cloud and CI/CD', color: '#f7c873',
      fix: 'Tier 1 is where service accounts, cloud roles and pipelines live, and where combinations of small permissions create big paths.',
      qs: [
        ['Can you see effective permissions across your cloud providers together, including combinations of roles?', 'Get a unified view of effective permissions, reasoning over combinations and not single roles.'],
        ['Does every non-human identity have a named owner and a risk score?', 'Discover non-human identities continuously and tie each one back to an owner.'],
        ['Does your pipeline block a commit that contains a hard-coded credential?', 'Make secret scanning a required pipeline check so it blocks the merge instead of reporting later.']
      ] },
    { id: 't2', name: 'Tier 2 \u2014 workstations and helpdesk', color: '#7df2d0',
      fix: 'Tier 2 is where most attacks begin, so what matters is what a stolen workstation credential can reach next.',
      qs: [
        ['Does each machine have its own unique, vaulted local-admin credential?', 'Vault a unique local-admin credential per machine.'],
        ['Is admin elevation just-in-time instead of standing admin rights?', 'Replace standing admin rights with just-in-time elevation.']
      ] },
    { id: 'x', name: 'Across the tiers', color: '#c4b5fd',
      fix: 'These decide whether the tiers actually hold under pressure.',
      qs: [
        ['Could a compromised Tier 2 credential reach Tier 0 through standing cross-tier access today?', 'Remove standing cross-tier access and put a just-in-time gate at each tier boundary.', true],
        ['Do access reviews use usage evidence, with dormant access pre-flagged for removal?', 'Drive certification from usage evidence so reviewers confirm instead of reconstructing.']
      ] }
  ];
  var LINKS = { t0: '/case-studies/credential-tiering-model/', t1: '/case-studies/non-human-identity-at-scale/', t2: '/case-studies/jit-jea-elevation/', x: '/case-studies/access-recertification/' };
  var qsEl = document.getElementById('tc-qs'), form = document.getElementById('tc-form'), go = document.getElementById('tc-go'), prog = document.getElementById('tc-prog'), res = document.getElementById('tc-res');
  if (!qsEl) return;
  var all = [];
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  TIERS.forEach(function (t) {
    t.qs.forEach(function (q) {
      var i = all.length; all.push({ tier: t, q: q });
      var fs = el('fieldset', 'q'); fs.appendChild(el('legend', '', t.name));
      fs.appendChild(el('p', '', q[0]));
      var row = el('div', 'opts');
      [['Yes', 2], ['Partly', 1], ['No', 0]].forEach(function (o) {
        var lab = document.createElement('label'), inp = document.createElement('input');
        inp.type = 'radio'; inp.name = 'q' + i; inp.value = o[1];
        lab.appendChild(inp); lab.appendChild(el('span', '', o[0])); row.appendChild(lab);
      });
      fs.appendChild(row); qsEl.appendChild(fs);
    });
  });
  function answered() { return form.querySelectorAll('input:checked').length; }
  function update() {
    var n = answered(); prog.textContent = n + ' of ' + all.length + ' answered';
    go.disabled = n < all.length;
  }
  form.addEventListener('change', update); update();
  form.addEventListener('submit', function (ev) {
    ev.preventDefault(); if (answered() < all.length) return;
    res.textContent = ''; res.hidden = false;
    res.appendChild(el('h2', '', 'Your read'));
    TIERS.forEach(function (t) {
      var got = 0, max = 0, gaps = [];
      all.forEach(function (a, i) {
        if (a.tier !== t) return;
        var v = +form.querySelector('input[name="q' + i + '"]:checked').value;
        if (a.q[2]) v = 2 - v;
        got += v; max += 2; if (v < 2) gaps.push(a.q[1]);
      });
      var pct = Math.round(100 * got / max);
      var box = el('div', 'tier'); box.style.setProperty('--c', t.color);
      box.appendChild(el('h3', '', t.name));
      box.appendChild(el('span', 'sc', pct + '% covered'));
      box.appendChild(el('p', 'note', t.fix));
      if (gaps.length) { var ul = el('ul'); gaps.forEach(function (g) { ul.appendChild(el('li', '', g)); }); box.appendChild(ul); }
      else box.appendChild(el('p', 'note', 'Nothing to flag here.'));
      res.appendChild(box);
    });
    var p = el('p', 'note', 'Where to read more: '), a1 = el('a', '', 'the tiering study'); a1.href = LINKS.t0;
    p.appendChild(a1); p.appendChild(document.createTextNode(', '));
    var a2 = el('a', '', 'non-human identity'); a2.href = LINKS.t1; p.appendChild(a2); p.appendChild(document.createTextNode(', '));
    var a3 = el('a', '', 'just-in-time elevation'); a3.href = LINKS.t2; p.appendChild(a3); p.appendChild(document.createTextNode('. Want to talk it through? '));
    var a4 = el('a', '', 'Email me'); a4.href = 'mailto:trivedi.roshan1@gmail.com'; p.appendChild(a4); p.appendChild(document.createTextNode('.'));
    res.appendChild(p);
    res.focus(); res.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
