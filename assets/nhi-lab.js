/* Non-human identity lab: case filter and the in-browser scenarios. Made-up data, nothing leaves the page. */
(function () {
  'use strict';
  // ---- case filter ----
  var chips = document.querySelectorAll('.nhi .chip');
  var cases = document.querySelectorAll('.nhi .case');
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var f = c.getAttribute('data-f');
      chips.forEach(function (x) { x.classList.toggle('on', x === c); });
      cases.forEach(function (k) { k.hidden = !(f === 'all' || k.getAttribute('data-g') === f); });
    });
  });

  // ---- lab ----
  var lab = document.querySelector('[data-lab]');
  if (!lab) return;
  var story = lab.querySelector('[data-story]');
  var controlsEl = lab.querySelector('[data-controls]');
  var inputEl = lab.querySelector('[data-input]');
  var resultEl = lab.querySelector('[data-result]');
  var lessonEl = lab.querySelector('[data-lesson]');
  var textArea = lab.querySelector('#scan-text');
  var PATTERNS = [/AKIA[0-9A-Z]{16}/, /ghp_[A-Za-z0-9]{20,}/, /BEGIN [A-Z ]*PRIVATE KEY/, /sk-live-[A-Za-z0-9]{16,}/, /xox[bp]-[0-9A-Za-z-]{10,}/, /postgres:\/\/[^:\s]+:[^@\s]+@/];
  var ENV = [
    ['DB_URL', 'postgres://app:Pa55w0rd@db.example/prod', 1, 1], ['STRIPE_KEY', 'sk-live-x9Y8z7W6v5U4t3S2r1Q0', 1, 1],
    ['DEPLOY_TOKEN', 'ghp_a1B2c3D4e5F6g7H8i9J0k1L2m3', 1, 0], ['CFG_BLOB', '7f3a9c01b2d4e5f6a7b8c9d0e1f2a3b4', 1, 0],
    ['NODE_ENV', 'production', 0, 0], ['REGION', 'ap-south-1', 0, 0], ['LOG_LEVEL', 'info', 0, 0],
    ['APP_NAME', 'kaveri-pay', 0, 0], ['BUILD_ID', '20261102.4', 0, 0], ['FEATURE_FLAGS', 'a,b,c', 0, 0]
  ];
  var S = {
    oauth: {
      story: 'An employee linked an AI office app with "allow all" 20 days ago. The vendor is breached and an attacker replays the refresh token from their own network. The vendor tells you at minute 0.',
      controls: [['tenant_allowlist', 'Only allowlisted apps can be granted'], ['breach_revoke', 'Revoke within 60 minutes of a breach notice']],
      run: function (on) {
        if (on.tenant_allowlist) return [['Grant at consent', 'Refused: the app is not on the list', 1], ['Replay at minute 30', 'Nothing to replay', 1], ['Replay at minute 90', 'Nothing to replay', 1]];
        var rv = on.breach_revoke;
        return [['Grant at consent', 'Accepted', 0], ['Replay at minute 30', 'Reads files', 0], ['Replay at minute 90', rv ? 'Refused: revoked at minute 60' : 'Reads files', rv ? 1 : 0]];
      },
      lesson: 'Turn the allowlist on and the revoke does nothing. Turn it off and the revoke is the only thing between the attacker and the files. Layered controls hide each other in a one-at-a-time test.'
    },
    runner: {
      story: 'A CI job runs for 5 minutes with a deploy token. A malicious step copies it at minute 1. The attacker replays it from another network at minute 3 and at minute 8, after the job ended.',
      controls: [['short_ttl', 'Token lives 10 minutes'], ['bind_and_revoke', 'Bound to the runner network, revoked at job end']],
      run: function (on) {
        function works(t) { if (on.short_ttl && t > 10) return false; if (on.bind_and_revoke) return false; return true; }
        return [3, 8].map(function (t) { var w = works(t); return ['Replay at minute ' + t, w ? 'Works' : 'Refused', w ? 0 : 1]; });
      },
      lesson: 'The 10-minute lifetime alone still allows both replays, because both fall inside 10 minutes. Binding and revoking stops both. Known limit: the token still works from inside the runner during the job.'
    },
    envvars: {
      story: 'A project has 10 variables, 4 of them secrets. Two secrets are marked sensitive by hand. Someone with internal read access lists the variables.',
      controls: [['pattern_marking', 'Mark secrets by pattern when saved']],
      run: function (on) {
        return ENV.map(function (v) {
          var auto = on.pattern_marking && PATTERNS.some(function (p) { return p.test(v[1]); });
          var hidden = v[3] || auto;
          return [v[0] + (v[2] ? '  (secret)' : ''), hidden ? 'Hidden' : 'Readable: ' + v[1], v[2] ? (hidden ? 1 : 0) : 1];
        });
      },
      lesson: 'Pattern marking hides three of the four secrets. CFG_BLOB matches no pattern, so it stays readable. Every pattern-based control has its own CFG_BLOB.'
    },
    extend: {
      story: 'An engineer has a 2-hour window on a database. The job keeps running and they ask for more time four times.',
      controls: [['one_extension', 'One extension, then a person must approve']],
      run: function (on) {
        if (on.one_extension) return [['Extension 1', 'Granted: 2 more hours', 1], ['Extension 2', 'Waits for a person to approve', 1], ['Hours open without approval', '4', 1]];
        return [['Extensions 1 to 4', 'All granted automatically', 0], ['Hours open without approval', '10', 0]];
      },
      lesson: 'Without a limit, four requests leave the account open for ten hours. A limit moves the decision to a person.'
    },
    scan: {
      story: 'Paste made-up text with fake secrets. The scan looks for six known patterns. See what gets through.',
      controls: [['secret_scan', 'Run the secret scan before commit']],
      run: function (on) {
        var lines = textArea.value.split('\n').filter(function (l) { return l.trim(); });
        if (!lines.length) return [['Nothing to scan', 'Paste some text', 1]];
        return lines.map(function (l) {
          var hit = on.secret_scan && PATTERNS.some(function (p) { return p.test(l); });
          var shown = l.length > 60 ? l.slice(0, 57) + '...' : l;
          return [shown, !on.secret_scan ? 'Reaches the repository (scan off)' : (hit ? 'Blocked' : 'Not matched: passes'), hit ? 1 : 0];
        });
      },
      lesson: 'A secret split across two lines or encoded as base64 gets through. In the lab the scan caught 6 of 8 fake secrets.'
    }
  };
  var current = 'oauth', state = {};
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function render() {
    var s = S[current];
    story.textContent = s.story;
    lessonEl.textContent = s.lesson;
    inputEl.hidden = current !== 'scan';
    controlsEl.textContent = '';
    s.controls.forEach(function (c) {
      var l = el('label'), i = el('input');
      i.type = 'checkbox'; i.checked = !!state[c[0]];
      i.addEventListener('change', function () { state[c[0]] = i.checked; update(); });
      l.appendChild(i); l.appendChild(el('span', null, c[1])); controlsEl.appendChild(l);
    });
    update();
  }
  function update() {
    var rows = S[current].run(state);
    resultEl.textContent = '';
    rows.forEach(function (r) {
      var d = el('div', r[2] ? 'r-good' : 'r-bad');
      d.appendChild(el('b', null, r[0] + ': ')); d.appendChild(document.createTextNode(r[1]));
      resultEl.appendChild(d);
    });
  }
  lab.querySelectorAll('[data-s]').forEach(function (b) {
    b.addEventListener('click', function () {
      current = b.getAttribute('data-s'); state = {};
      lab.querySelectorAll('[data-s]').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      render();
    });
  });
  textArea.addEventListener('input', function () { if (current === 'scan') update(); });
  render();
})();
