from nhi_site import *
from nhi_data import load_cases, STAGES, STAGE_OF, OWASP, GROUPS

def lifecycle_svg(counts):
    W, bw, gap, x0, y = 944, 116, 22, 8, 62
    out = [f'<svg class="dg" viewBox="0 0 960 250" role="img" aria-label="The seven steps of the framework: find, own, limit, store and issue, rotate and expire, watch, retire and respond. A dashed arrow leads from the last step back to the first.">', defs('ahf')]
    for i, (key, name, sub) in enumerate(STAGES):
        x = x0 + i * (bw + gap)
        short = {'find': 'Every identity, every source', 'own': 'Named person, purpose, end date',
                 'limit': 'Least privilege, front door', 'store': 'Approved vault, short-lived',
                 'rotate': 'Consumers first, old value dead', 'watch': 'Log use, notice the odd one',
                 'retire': 'Disable, hold, delete; cut access fast'}[key]
        cls = 'irr' if key == 'retire' else ''
        out.append(box(x, y, bw, 118, name, short, 't1' if key == 'retire' else '', num=i + 1))
        out.append(f'<text class="ts" x="{x + bw / 2}" y="{y + 136}" text-anchor="middle">{counts[key]} lab cases</text>')
        if i < 6:
            out.append(arrow(f'M {x + bw} {y + 59} L {x + bw + gap - 2} {y + 59}', mid='ahf'))
    out.append(arrow(f'M {x0 + 6 * (bw + gap) + bw / 2} {y + 144} L {x0 + 6 * (bw + gap) + bw / 2} 226 L {x0 + bw / 2} 226 L {x0 + bw / 2} {y + 144}', 'dash', None, mid='ahf'))
    out.append(f'<text class="al" x="480" y="220" text-anchor="middle">what is left feeds the next scan</text>')
    out.append('<path class="ar" d="M 10 42 L 950 42" style="stroke-opacity:.25;stroke-width:1.2"/>')
    out.append('<circle class="pulse" r="6" style="offset-path:path(\'M 10 42 L 950 42\')"/>')
    out.append('</svg>')
    return ''.join(out)

def retire_svg():
    o = ['<svg class="dg" viewBox="0 0 960 190" role="img" aria-label="Staged retirement: monitor, disable with a rollback window, hold period, delete. Delete cannot be undone. A dashed arrow shows re-enable if someone asks for it back during the hold.">', defs('ahr')]
    xs = [10, 264, 518, 772]
    w = 176
    names = [('Monitor', 'Watch for any use. Change nothing yet.', ''), ('Disable', 'Turn it off, keep it. Rollback ready.', 't1'),
             ('Hold', 'Wait. Length is set by the owner.', 'mut'), ('Delete', 'Cannot be undone.', 't0')]
    for i, (x, (n, sd, c)) in enumerate(zip(xs, names)):
        o.append(box(x, 44, w, 92, n, sd, c, num=i + 1))
    for i, lab in enumerate(['no use seen', 'nothing broke', 'nobody asked']):
        x1 = xs[i] + w; x2 = xs[i + 1]
        o.append(arrow(f'M {x1 + 2} 90 L {x2 - 2} 90', mid='ahr', label=lab, lx=(x1 + x2) / 2, ly=76))
    o.append(arrow(f'M {xs[2] + w / 2} 136 L {xs[2] + w / 2} 170 L {xs[1] + w / 2} 170 L {xs[1] + w / 2} 138', 'dash', 'someone needs it: re-enable', (xs[1] + xs[2] + w) / 2, 164, mid='ahr'))
    o.append(f'<text class="ts" x="{xs[1] + w / 2}" y="28" text-anchor="middle">owner approves</text><text class="ts" x="{xs[3] + w / 2}" y="28" text-anchor="middle">owner approves, backup taken</text>')
    o.append('</svg>')
    return ''.join(o)

def leak_svg():
    o = ['<svg class="dg" viewBox="0 0 960 330" role="img" aria-label="Leak response in six steps: treat the secret as exposed, find who uses it, issue a new value, update the users, revoke the old value, check the logs for use since the leak.">', defs('ahl')]
    xs = [10, 360, 710]
    w = 240
    top = [('Treat as exposed', 'Do not wait for proof of misuse.', 't0'), ('Find the users', 'List every app, job and person that uses it.', ''), ('Issue a new value', 'Roll forward. The old one still works.', 't1')]
    for i, (x, (n, sd, c)) in enumerate(zip(xs, top)):
        o.append(box(x, 40, w, 84, n, sd, c, num=i + 1))
    o.append(arrow(f'M {xs[0] + w + 2} 82 L {xs[1] - 2} 82', label='assume copied', lx=(xs[0] + w + xs[1]) / 2, ly=68, mid='ahl'))
    o.append(arrow(f'M {xs[1] + w + 2} 82 L {xs[2] - 2} 82', label='users known', lx=(xs[1] + w + xs[2]) / 2, ly=68, mid='ahl'))
    bot = [('Update the users', 'Each one confirmed on the new value.', ''), ('Revoke the old value', 'Only after every user is confirmed.', 't0'), ('Check the logs', 'Look for use since the day it leaked.', 'ok')]
    for i, (x, (n, sd, c)) in enumerate(zip(xs, bot)):
        o.append(box(x, 200, w, 84, n, sd, c, num=i + 4))
    o.append(arrow(f'M {xs[2] + w / 2} 124 L {xs[2] + w / 2} 162 L {xs[0] + w / 2} 162 L {xs[0] + w / 2} 198', label='new value ready', lx=480, ly=154, mid='ahl'))
    o.append(arrow(f'M {xs[0] + w + 2} 242 L {xs[1] - 2} 242', label='tested', lx=(xs[0] + w + xs[1]) / 2, ly=228, mid='ahl'))
    o.append(arrow(f'M {xs[1] + w + 2} 242 L {xs[2] - 2} 242', label='old one dead', lx=(xs[1] + w + xs[2]) / 2, ly=228, mid='ahl'))
    o.append('<text class="ts" x="480" y="316" text-anchor="middle">Signing keys and CA keys are roll-forward only: never revoke first.</text>')
    o.append('</svg>')
    return ''.join(o)

def build():
    cases = load_cases()
    byid = {c['id']: c for c in cases}
    counts = {k: sum(1 for c in cases if c['stage'] == k) for k, _, _ in STAGES}

    inv = table(['Field', 'Why it is there', 'Example (made up)'], [
        [th_row('Identity'), td('The thing you can point at.'), td('<code>svc-billing-export</code>')],
        [th_row('Type'), td('Service account, API key, token, certificate, workload or agent credential.'), td('Service account')],
        [th_row('Owner'), td('One named person who answers for it. A team alias nobody reads does not count.'), td('A person, with a backup')],
        [th_row('Purpose'), td('Lets a reviewer say yes or no without guessing.'), td('Nightly billing export')],
        [th_row('Tier'), td('How much damage it can do. Decides review order.'), td('Tier 1')],
        [th_row('Permissions'), td('What it can reach, and what it actually used.'), td('Read on one database')],
        [th_row('Secret type and location'), td('Where the value lives and who can read it.'), td('Password, in the approved vault')],
        [th_row('Created, last used, expires'), td('Age, idle time and end date. Missing last-use data is itself a finding.'), td('Created 14 months ago, last used yesterday, no expiry')],
        [th_row('Consumers'), td('Who breaks if you change it.'), td('Billing job, reporting app')],
    ], 'Inventory fields. One row per identity.')

    gaps = ['No owner.', 'No purpose.', 'No expiry.', 'Last use older than your limit (you set the limit).', 'Permissions broader than the use.',
            'Secret held outside the approved store.']

    dec = table(['Situation', 'Decision', 'Who approves', 'Flag', 'Why'], [
        [th_row('No owner'), td('Cannot be kept. Escalate, then stage for disable.'), td('Platform owner'), td(badge('hi')), td('Nobody can answer for it.')],
        [th_row('Owner known, no expiry'), td('Keep, and set an end date.'), td('Owner'), td(''), td('An open-ended credential is a long-lived breach path.')],
        [th_row('Idle past the limit'), td('Stage for disable. Do not delete yet.'), td('Owner, platform owner'), td(badge('hi')), td('A quarterly job looks idle for months.')],
        [th_row('Broader than its use'), td('Reduce permissions, or replace with a short-lived or workload identity.'), td('Owner'), td(''), td('Less reach means less damage if it leaks.')],
        [th_row('Long-lived key in CI'), td('Replace with a per-job, short-lived credential.'), td('Pipeline owner'), td(''), td('Another job on the same runner can read a shared key.')],
        [th_row('Secret outside the approved store'), td('Move it, then rotate it.'), td('Owner'), td(''), td('Copies elsewhere may already exist.')],
        [th_row('Secret exposed'), td('Treat as compromised. Follow the leak steps below.'), td('Security lead'), td(badge('hi')), td('A copy may exist already.')],
        [th_row('Signing or CA key'), td('Roll forward only. Never revoke first.'), td('Platform owner'), td(badge('irr')), td('Revoking first breaks everything it signed.')],
    ], 'Decision matrix. These are proposals; your organisation sets the thresholds.')

    std = ['An owner is named when the credential is created.', 'An end date is set when it is created.', 'Permissions are the least that do the job.',
           'The value is stored in the approved vault, never in code, tickets or chat.', 'Use is logged and someone is told when the pattern changes.',
           'AI agents get their own identity, a named human owner and short-lived tokens. No shared agent identity.']

    metrics = table(['Measure', 'How to count it', 'Target', 'Lab number, as an illustration only'], [
        [th_row('Identities with a named owner'), td('Owned identities divided by all identities'), td('<em>You set it</em>'), td('A key with no owner was paused on day 31 (N-R14-09)')],
        [th_row('Identities with an end date'), td('Identities with an expiry divided by all'), td('<em>You set it</em>'), td('Ghost credential refused at creation (S-R17-04)')],
        [th_row('Time to cut a breached vendor'), td('Minutes from notice to revoked grants'), td('<em>You set it</em>'), td('60 minutes in the model; a replay at minute 30 still worked (N-R14-23)')],
        [th_row('Failed rotations noticed within a day'), td('Alerts raised divided by failures'), td('<em>You set it</em>'), td('Alert on day 1 instead of day 60 (N-R14-14)')],
        [th_row('Secrets caught before commit'), td('Blocked divided by planted'), td('<em>You set it</em>'), td('6 of 8 blocked; 2 got through (S-R17-05)')],
    ], 'Metrics, from your own data only. The lab numbers are from small models and prove nothing about your estate.')

    # stage detail blocks
    detail = {
        'find': ('Build one list from every source: the directory, the cloud, the CI settings, the SaaS apps, the repositories and the AI tools people have connected.',
                 'One list. Each row shows which source it came from.',
                 'A directory-only scan found 12 of 27 identities. Merging all three sources found 27.'),
        'own': ('Give each identity a named person, a purpose and an end date. If there is no owner, escalate, then stage the identity for disable.',
                'Every row has a person who can say what it is for.',
                'A key with no owner stayed active on day 31 without a rule. With the rule it was paused on day 31.'),
        'limit': ('Tier by blast radius, give each identity the least that works, and put a front door in front of new and privileged ones.',
                  'A caller with the wrong identity or too much reach is refused, and the log says who asked.',
                  'A low-value workload asked for a high-value role and got it. With trust bound to one workload it was refused.'),
        'store': ('Keep values in the approved vault. Prefer short-lived and per-job credentials. Scan code and config before commit.',
                  'No value in code, tickets or chat. A planted secret is blocked before it reaches the repository.',
                  'The scan blocked 6 of 8 planted secrets. The 2 it missed matched no pattern.'),
        'rotate': ('Update the consumer first, then rotate, then prove the old value is dead. Close the ticket only after that.',
                   'The old value is refused. No application fails at the next connection.',
                   'Closing 5 rotation tickets without the check left 2 old secrets live.'),
        'watch': ('Log every use. Alert on the odd one: break-glass at 2 a.m., a grant used from a new place, a job that never ran before.',
                  'Someone is told the same day, and the account is rotated after break-glass use.',
                  'Break-glass used at 2 a.m. went unnoticed. With the alert it fired and the password was rotated.'),
        'retire': ('Monitor, then disable with a rollback window, then delete only after a hold period. After a vendor breach, revoke their grants.',
                   'Nothing deleted that someone still needs. Access to a breached vendor ends within your target time.',
                   'After an app was retired, all 3 of its identities still worked 90 days later. With the rule all 3 were disabled.'),
    }
    stage_html = ''
    for i, (key, name, sub) in enumerate(STAGES):
        do, exp, ev = detail[key]
        ids = [c['id'] for c in cases if c['stage'] == key]
        stage_html += (f'<li id="s-{key}"><b class="t">{E(name)}: {E(sub.lower())}</b>{E(do)}'
                       f'<span class="exp">{E(exp)}</span>'
                       f'<span class="exp" style="margin-top:4px"><b>Lab evidence.</b> {E(ev)} Cases: {case_links(ids)}.</span></li>')
    stage_html = f'<ol class="nsteps">{stage_html}</ol>'
    stage_html = stage_html.replace('<span class="exp" style="margin-top:4px"><b>Lab evidence.</b>', '<span style="display:block;margin-top:6px;color:var(--mut);font-size:.9rem"><b>Lab evidence.</b>')

    owasp_rows = []
    for code, name, ids, cover in OWASP:
        idl = ids.split()
        weak = cover.startswith(('weak', 'partial'))
        owasp_rows.append([th_row(f'{code}: {E(name)}'), td(case_links(idl)), td(E(cover), 'wn' if weak else 'ok')])
    owasp = table(['OWASP NHI Top 10 (2025) risk', 'Lab cases that touch it', 'Coverage'], owasp_rows,
                  'My mapping of the lab cases to the OWASP list. It is my reading, not OWASP\'s.')

    sg = ''.join(
        f'<div class="stage"><h3>{i + 1}. {E(n)}</h3><p>{E(sub)}</p><ul>' +
        ''.join(f'<li><a href="/nhi-lab/#{c["id"].lower()}">{c["id"]}</a></li>' for c in cases if c['stage'] == k) + '</ul></div>'
        for i, (k, n, sub) in enumerate(STAGES))

    body = f'''<main id="main" class="nhi">
  {subnav('framework')}
  {hero('Framework', 'A lifecycle for machine identities and their secrets', 'Seven steps from finding an identity to retiring it, with the decision each step needs and the lab case that tested it. Draft v0.1, 2 November 2026. It is a working method, not a standard, and it was tested only on made-up data.',
        ['Last reviewed 2 November 2026', 'Built from the lab\'s 46 cases', 'For security and identity leads'])}

  <section class="nsec" id="use" aria-labelledby="use-h">
    <h2 id="use-h">Who this is for and how to use it</h2>
    <p class="lede">You run identity, privileged access or cloud security and you want one method for the credentials nobody talks about: service accounts, API keys, tokens, certificates, workload identities and the logins AI tools now hold.</p>
    <p>Use it in this order. Build the inventory, find the gaps, tier what you found, decide per credential, retire in stages, and set standards so new ones start clean. Where the page says <em>you set it</em>, the number depends on your organisation and I have not guessed it.</p>
    <div class="nnote"><b>Limits</b>This framework came out of 46 cases on made-up data. The models are small and I wrote both the guesses and the code. Treat the lab results as examples of what to check, and test each control in your own environment before relying on it. Kubernetes and cloud workload identity design, and vault onboarding, are outside this page.</div>
  </section>

  <section class="nsec" id="lifecycle" aria-labelledby="lc-h">
    <h2 id="lc-h">The seven steps</h2>
    {figure(lifecycle_svg(counts), 'The seven steps in order. The number under each box is how many of the 46 lab cases test that step. The dot travels left to right; with reduced motion it rests on the last step.', [('', 'Step'), ('t1', 'Step that deletes or revokes'), ('da', 'Feedback')])}
    {stage_html}
  </section>

  <section class="nsec" id="inventory" aria-labelledby="inv-h">
    <h2 id="inv-h">Step 1 in detail: the inventory</h2>
    <p>One row per identity. Keep the inventory out of wide circulation: it is a map of targets.</p>
    {inv}
    <h3>Flag these gaps</h3>
    <ul>{''.join(f'<li>{E(g)}</li>' for g in gaps)}</ul>
    <p>Order the review by tier: Tier 0 and Tier 1 first. I use tiers as a proposal: Tier 0 can control identity systems or all of production, Tier 1 reaches production data or systems, Tier 2 reaches little. Your organisation sets the real thresholds.</p>
  </section>

  <section class="nsec" id="decide" aria-labelledby="dec-h">
    <h2 id="dec-h">Deciding what to do with each credential</h2>
    <p>Disabling can break something, so it needs the owner. Deleting or revoking cannot be undone, so list first, get approval and wait out a hold period.</p>
    {dec}
  </section>

  <section class="nsec" id="retire" aria-labelledby="ret-h">
    <h2 id="ret-h">Retire in stages</h2>
    <p>Turn it off before you throw it away. If someone shouts, turn it back on. Only delete after the hold period ends.</p>
    {figure(retire_svg(), 'Four stages. Only the last one cannot be reversed. The length of the hold is your decision; I have not set one.', [('', 'Safe step'), ('t1', 'Can break something'), ('t0', 'Cannot be undone')])}
  </section>

  <section class="nsec" id="leak" aria-labelledby="leak-h">
    <h2 id="leak-h">When a secret leaks</h2>
    <p>Do not wait for proof of misuse. Assume somebody copied it.</p>
    {figure(leak_svg(), 'Six steps. Step 5 is the one that cannot be undone, so it comes after every user has moved to the new value.', [('t0', 'Cannot be undone'), ('t1', 'Needs a change window'), ('ok', 'Check step')])}
    <div class="nnote bad"><b>Never do this</b>Rotating the leaked key and leaving the old one valid. The lab showed the same mistake in another form: 5 rotation tickets closed while 2 old secrets still worked (N-R14-20).</div>
  </section>

  <section class="nsec" id="standards" aria-labelledby="std-h">
    <h2 id="std-h">Standards for new credentials</h2>
    <p>Start clean and you do not have to clean up later.</p>
    <ol>{''.join(f'<li>{E(s)}</li>' for s in std)}</ol>
    <p>In the lab, a front door that refused new identities without an owner, scope and expiry (N-R14-18) stopped the problem at creation. A weekly sweep also disabled expired keys (S-R17-04).</p>
  </section>

  <section class="nsec" id="metrics" aria-labelledby="met-h">
    <h2 id="met-h">Metrics</h2>
    <p>Count from your own data. I have left the targets for you.</p>
    {metrics}
  </section>

  <section class="nsec" id="owasp" aria-labelledby="ow-h">
    <h2 id="ow-h">How it lines up with the OWASP list</h2>
    <p>OWASP publishes a Top 10 for non-human identities (2025). I mapped each risk to the lab cases that touch it. Two risks have thin coverage: insecure authentication (NHI4) and environment isolation (NHI8). Those are the next cases to write; they are on the <a href="/nhi-lab/roadmap/">roadmap</a>.</p>
    {owasp}
    <p>Source: <a href="https://owasp.github.io/www-project-non-human-identities-top-10/2025/top-10-2025/" rel="noopener">OWASP Non-Human Identities Top 10, 2025</a> {badge('primary')}</p>
  </section>

  <section class="nsec" id="cases" aria-labelledby="cs-h">
    <h2 id="cs-h">Which lab cases test which step</h2>
    <p>Each of the 46 cases sits in one step. Chain tests cross several steps, so I placed each one where its first link is stopped.</p>
    <div class="stages">{sg}</div>
  </section>

  <section class="nsec" id="open" aria-labelledby="op-h">
    <h2 id="op-h">Open items</h2>
    <ul>
      <li>Tier thresholds, idle limits and hold period: your organisation sets them. Not set here.</li>
      <li>Reference points I used for the method: OWASP NHI Top 10, and the identity and access controls in NIST SP 800-53 and ISO/IEC 27001. I name them as reading, and I do not quote their text or claim alignment.</li>
      <li>Not yet tested: cloud-specific key habits, Kubernetes workload identity, and any real product.</li>
    </ul>
    <p>Back to the <a href="/nhi-lab/">lab overview</a>, the <a href="/nhi-lab/audit/">audit data</a> or the <a href="/nhi-lab/method/">method</a>.</p>
  </section>
</main>'''
    desc = 'A seven-step lifecycle for non-human identities and secrets: inventory, owners, tiers, decisions, staged retirement, leak response and metrics, each tied to the lab cases that tested it.'
    write('nhi-lab/framework/index.html', shell('nhi-lab/framework/', 'Non-human identity lifecycle framework', desc,
          'A lifecycle for machine identities and their secrets', body, ld=ld_article('A lifecycle for machine identities and their secrets', desc, 'nhi-lab/framework/')))

if __name__ == '__main__':
    build()
