import json, os
from nhi_site import *
import nhi_data as D

MAC_GUESS_COMMIT = 'a2dc1fd'
MAC_CODE_COMMIT = 'cbec7a8'   # Mac run confirmed 10 Nov 2026

WRONG_NOTES = {
    'P-R15-06': 'Wrong in three places. I expected the injection to matter when switched off alone, but the reveal policy still stops both reveals. I expected rotation to be safe to drop, but without it all 3 remembered passwords still work. So the injection went unnoticed and the rotation did not.',
    'P-R15-12': 'I guessed the drill finds 2 faults. It finds 1. The routing check catches the alert fault before the drill runs, and the second holder makes the sealed copy fault harmless without removing it. I also guessed nothing finds a fault without the drill, but the routing check still does.',
    'P-R15-22': 'I guessed 0 events without controls. The connector delivers 14 of 20 and drops 6 whether or not a heartbeat exists. The heartbeat adds the alarm and the replay, not the delivery.',
    'S-R17-08': 'I guessed 4 agents would hold credentials at day 10 with the issue rule off. The scan had already flagged them and 3 owners had registered, so 1 does. I also guessed the 30 day expiry would go unnoticed, but it is what disables the last agent.',
    'S-R17-09': 'I guessed 4 alerts. The model alerts on each of the 5 creation attempts, refused or not. Alerting only on creations that succeed would give 1. I never wrote down which I meant.',
}

UNNOTICED = [
    ('N-R14-06', 'Weekly sweep', 'masked', 'The cloud policy already refuses the 3 console accounts, so the sweep finds nothing.'),
    ('N-R14-06', 'Automatic expiry', 'masked', 'Same reason: nothing is left to expire.'),
    ('N-R14-10', 'Quarterly attestation', 'effect', 'It records attestations. The case counts claims, pauses and outages, and it changes none of them.'),
    ('N-R14-12', 'Person approves each change', 'effect', 'In the model the approver approves everything, so the removals are the same with or without a person.'),
    ('N-R14-16', 'Delete after the hold', 'effect', 'The delete comes after the hold. The case counts what happens during it.'),
    ('P-R15-04', 'Break-glass fallback', 'masked', 'With the second node up, nobody needs the fallback.'),
    ('P-R15-04', 'Review of fallback use', 'masked', 'No fallback is used while the second node is up, so there is nothing to review.'),
    ('P-R15-06', 'Credential injection', 'masked', 'The reveal policy alone stops both reveals.'),
    ('P-R15-06', 'Reveal button disabled', 'masked', 'The injection alone stops both reveals.'),
    ('P-R15-14', 'Password change after check-out', 'effect', 'Attribution counts stay the same. What changes is that a person can still sign in after check-out, which the case records but does not count as attribution.'),
    ('P-R15-23', 'Log of every elevation', 'effect', 'A log changes no access count. It only gives evidence afterwards.'),
    ('P-R15-24', 'Volume threshold', 'effect', 'The large copy is 950 MB against a 1000 MB threshold, so the rule never fires.'),
    ('S-R17-07', 'Review of the feature scope', 'effect', 'A review is a process step. In the model it does not change what the assistant reads.'),
    ('S-R17-07', 'Log of what the assistant read', 'effect', 'A log changes no access count.'),
]


def build():
    assert MAC_CODE_COMMIT != 'PENDING', 'set MAC_CODE_COMMIT once the Mac run is confirmed'
    cs = [c for c in D.load_cases() if c['run'] == 4]
    assert len(cs) == 19
    rows = json.load(open(os.path.join(D.EV, 'results-round-19.json')))['rows']
    assert sum(len(r['noticed']) for r in rows) == 57
    assert sum(not v for r in rows for v in r['noticed'].values()) == len(UNNOTICED) == 14
    assert sum(c['wrong'] for c in cs) == len(WRONG_NOTES) == 5

    res = table(['Case', 'Without the controls', 'With all controls', 'My guesses'], [
        [th_row(f'<a id="{c["id"].lower()}"></a>{c["id"]} {E(c["title"])}'), td(E(c['without'])), td(E(c['with_'])),
         td('<b>Wrong in part.</b> See below.' if c['wrong'] else 'All matched.')] for c in cs],
        'Round 19 results next to the guesses')

    wrongs = ''.join(f'<li><b>{case_link(k)}</b> {E(v)}</li>' for k, v in WRONG_NOTES.items())

    off = table(['Case', 'Control switched off alone', 'Why nothing changed', 'Kind'], [
        [th_row(case_link(c)), td(E(n)), td(E(w)), td('Masked by another control' if k == 'masked' else 'No effect on what the case counts')]
        for c, n, k, w in UNNOTICED], 'Controls whose removal changed nothing the case counts')

    lim = table(['Case', 'What the controls cannot see'], [
        [th_row(case_link(c['id'])), td(E(D.LIMIT_R19[c['id']]))] for c in cs], 'Limits found in round 19')

    rec = table(['Item', 'Value', 'Where'], [
        [th_row('Guess file'), td('<code>729e16f2…</code> (SHA-256 of the whole file)'), td('<a href="/nhi-lab/evidence/guesses/guesses-round-19.md">guesses-round-19.md</a>')],
        [th_row('Commit with the guesses only'), td(f'<code>{MAC_GUESS_COMMIT}</code> on my Mac'), td('Before any code existed')],
        [th_row('Commit with code and results'), td(f'<code>{MAC_CODE_COMMIT}</code> on my Mac'),
         td('<a href="/nhi-lab/evidence/cases4.py">cases4.py</a>, <a href="/nhi-lab/evidence/run4.py">run4.py</a>, <a href="/nhi-lab/evidence/RESULTS-round-19.md">RESULTS-round-19.md</a>, <a href="/nhi-lab/evidence/results-round-19.json">results-round-19.json</a>')],
        [th_row('Second machine'), td('The Mac results file has the same SHA-256 as the sandbox one'), td('<code>86aa9d58…</code>. Both runs also checked the committed guess hash before running')],
    ], 'Where to check round 19')

    body = f'''<main id="main" class="nhi">
  {subnav('round19')}
  {hero('Round 19', 'The 19 queued cases: secrets, privileged access and shadow AI',
        'The catalogue had 19 cases that were designed and never run. This round runs them. I wrote, hashed and committed the guesses first. Five cases had at least one guess wrong, and every miss stays on the page.',
        ['Run 10 November 2026', '19 cases', '5 cases with a wrong guess', 'Made-up data only (Kaveri Finance)'])}

  <section class="nsec" id="result" aria-labelledby="r-h">
    <h2 id="r-h">The result</h2>
    <div class="ntiles">
      <div class="ntile"><b>19</b><span>cases: 6 on non-human identities, 10 on privileged access, 3 on shadow AI</span></div>
      <div class="ntile warn"><b>5</b><span>cases with a wrong guess (9 wrong claims in all)</span></div>
      <div class="ntile warn"><b>14</b><span>of 57 controls switched off alone changed nothing the case counts</span></div>
      <div class="ntile good"><b>19</b><span>limits written down, one for each case</span></div>
    </div>
    {res}
    <p>With round 19 the lab has 67 cases in four runs: 57 with every guess matched and 10 with at least one wrong. The earlier 48 are on the <a href="/nhi-lab/">lab page</a> and in the <a href="/nhi-lab/audit/">audit data</a>, which now include these 19.</p>
  </section>

  <section class="nsec" id="wrong" aria-labelledby="w-h">
    <h2 id="w-h">Where my guesses were wrong</h2>
    <ul>{wrongs}</ul>
    <p>Two patterns repeat. In P-R15-22 and S-R17-09 I did not say what I was counting, so the model answered a different question from the one in my head. In P-R15-06 and P-R15-12 I treated controls as independent when one covers another.</p>
  </section>

  <section class="nsec" id="off" aria-labelledby="o-h">
    <h2 id="o-h">Controls that changed nothing when switched off</h2>
    <p>In 10 of the 19 cases, at least one control could be switched off alone without changing anything the case counts. There are two different reasons, and they should not be mixed up.</p>
    <ul>
      <li><b>Masked by another control (6).</b> Another control already does the job, so the first one is a second line of defence. That is useful, but a check that only looks at the result cannot tell it is there.</li>
      <li><b>No effect on what the case counts (8).</b> These are logs, reviews, approvals and thresholds. They matter for evidence, for people and for later investigation. A model that counts access outcomes cannot see them. I do not read this as a sign that they are unnecessary.</li>
    </ul>
    {off}
  </section>

  <section class="nsec" id="limits" aria-labelledby="l-h">
    <h2 id="l-h">What the controls cannot see</h2>
    <p>Each case has one limit I probed. Where the model cannot measure a limit, the page says so.</p>
    {lim}
  </section>

  <section class="nsec" id="rules" aria-labelledby="ru-h">
    <h2 id="ru-h">Rules I fixed before the first run</h2>
    <ul>
      <li>Each case reports only the quantities its guess named. A control counts as noticed when switching it off alone changes one of them.</li>
      <li>Where a guess left the scenario open, the model takes the plain reading of the scenario text. A guess that disagrees is recorded as wrong. Nothing was changed afterwards to make a guess come out right.</li>
      <li>In P-R15-14 only the attribution counts decide whether a control is noticed, because that is what the guess talked about.</li>
    </ul>
  </section>

  <section class="nsec" id="custody" aria-labelledby="c-h">
    <h2 id="c-h">The record</h2>
    {rec}
    <p>To repeat it: download the evidence folder, run <code>python3 run4.py</code>, and compare with <code>RESULTS-round-19.md</code>. The script stops if the guess file no longer matches the hash. Method steps are on the <a href="/nhi-lab/method/">method page</a>.</p>
  </section>

  <section class="nsec" id="cannot" aria-labelledby="x-h">
    <h2 id="x-h">What this cannot tell you</h2>
    <ul>
      <li>I wrote the guesses and the code. A match shows my model agrees with my reasoning. It says nothing about a real product.</li>
      <li>All 19 are small in-memory models with made-up data.</li>
      <li>Some scenario numbers, such as the 10 false flags in P-R15-24, were set to match what my guess described. They show the shape of the effect, not a real rate.</li>
      <li>Process controls such as reviews and attestations cannot be measured by a model that only counts outcomes.</li>
      <li>No product was tested, so none is endorsed or criticised.</li>
    </ul>
    <p>Next: the <a href="/nhi-lab/stage-2/">Stage 2 pages</a> use these results in the control mapping and the test plan.</p>
    <p>Want the next lab's guesses before the results? <a href="https://buttondown.com/trivedi">Get them by email</a>. One or two emails a month.</p>
  </section>
</main>'''
    desc = 'Round 19 of the non-human identity lab: the 19 queued cases on secrets, privileged access and shadow AI. Guesses first, five cases with a wrong guess, 14 controls that changed nothing, with the record.'
    write('nhi-lab/round-19/index.html', shell('nhi-lab/round-19/', 'Non-human identity lab: round 19', desc,
          'NHI lab round 19: the 19 queued cases', body, ld=ld_article('Non-human identity lab: round 19', desc, 'nhi-lab/round-19/', 'TechArticle', '2026-11-10')))

if __name__ == '__main__':
    build()
