from nhi_site import *

def build():
    res = table(['Case', 'OWASP item', 'Without the controls', 'With all controls', 'My guess'], [
        [th_row('<a id="n-r18-01"></a>N-R18-01 A copied key from another network'), td('NHI4 Insecure Authentication'),
         td('12 calls accepted. The log says "billing key" 12 times, so the 6 genuine calls and the 6 bad ones look the same.'),
         td('6 accepted, 6 refused, <b>1 alert</b>.'), td('Without: matched. With: <b>wrong</b>. I guessed 3 alerts.')],
        [th_row('<a id="n-r18-02"></a>N-R18-02 A test credential that opens production'), td('NHI8 Environment Isolation'),
         td('All 8 runs succeed, including the 2 from the compromised test runner.'),
         td('6 normal runs succeed, 2 attempts refused, 2 alerts.'), td('Matched.')],
    ], 'Round 18 results next to the guesses')

    off1 = table(['Control switched off alone', 'What happened', 'Noticed?'], [
        [th_row('Workload binding'), td('The 3 replays succeed again. The 3 old-key calls are still refused by the revocation.'), td('Yes')],
        [th_row('Revoke the old key'), td('Nothing changed, because the binding already refuses the old key.'), td('<b>No</b>, masked')],
        [th_row('Alert on a new network'), td('All 6 refusals stay. Nobody is told.'), td('Yes')],
        [th_row('Replays from 3 different networks, everything on'), td('3 alerts, one per new network.'), td('Extra scenario')],
    ], 'N-R18-01: each control switched off alone')

    off2 = table(['Control switched off alone', 'What happened', 'Noticed?'], [
        [th_row('Separate identity per environment'), td('The 2 attempts succeed again.'), td('Yes')],
        [th_row('Production path closed to test identities'), td('Nothing changed, because the separate identity already refuses them.'), td('<b>No</b>, masked')],
        [th_row('Alert when test asks for production'), td('The 2 refusals stay. Nobody is told.'), td('Yes')],
        [th_row('One production secret under a wildcard path, everything on'), td('1 attempt succeeds. 1 production secret is readable from test. 1 alert.'), td('Extra scenario')],
    ], 'N-R18-02: each control switched off alone')

    body = f'''<main id="main" class="nhi">
  {subnav('round18')}
  {hero('Round 18', 'Two more cases: a copied key, and a test credential that opens production', 'Insecure authentication (NHI4) and environment isolation (NHI8) were the two OWASP items with the weakest coverage, so round 18 adds one case for each. I wrote, hashed and committed the guesses first. One was wrong, and it stays on the page.',
        ['Run 10 November 2026', '2 cases', '1 guess wrong', 'Made-up data only (Kaveri Finance)'])}

  <section class="nsec" id="result" aria-labelledby="r-h">
    <h2 id="r-h">The result</h2>
    <div class="ntiles">
      <div class="ntile"><b>2</b><span>cases (N-R18-01 and N-R18-02)</span></div>
      <div class="ntile warn"><b>1</b><span>guess wrong: the alert count</span></div>
      <div class="ntile warn"><b>2</b><span>controls no check noticed (masked by another control)</span></div>
      <div class="ntile good"><b>Same</b><span>output on the Mac and in the build sandbox</span></div>
    </div>
    {res}
    <p>Round 18 is the third run. With it the lab had 48 cases, 43 matched guesses and 5 wrong ones. Round 19 later brought the totals to 67 cases and 10 wrong guesses. The 46 cases from the first two runs are on the <a href="/nhi-lab/">lab page</a> and in the <a href="/nhi-lab/audit/">audit data</a>, which include these two and the round 19 cases.</p>
  </section>

  <section class="nsec" id="n1" aria-labelledby="n1-h">
    <h2 id="n1-h">N-R18-01: a copied key from another network</h2>
    <p>An internal payments API accepts a static key from the billing service. In one hour there are 12 calls: 6 genuine ones from the billing workload, 3 replays of a copied key from an unknown network, and 3 calls with the old key after it was rotated 2 days ago.</p>
    <p>Three controls: the key is bound to the workload, so a call must also carry the workload's own certificate. The old key is revoked at rotation. An alert fires when a key is used from a new network.</p>
    {off1}
    <div class="nnote"><b>Where my guess was wrong</b>I guessed 3 alerts. The model gave 1: it raises one alert per new network, and all 3 replays came from the same unknown network. My guess file even noted that a repeat from one network might be counted once, and I still wrote down 3. Replays from 3 different networks give 3 alerts. The "one alert per new network" rule is my own choice in the model, so this tells you how I built it and nothing about how a real product counts.</div>
    <p>Without a binding, a key looks the same as a copy of itself. With one, the copies are refused and the log shows which calls were bad. Revoking the old key at rotation changed nothing here, because the binding already refused it. It would matter in a setup with no binding.</p>
    <p>The limit: a replay made from inside the real billing workload carries the certificate and is accepted. The binding cannot see a compromised host.</p>
  </section>

  <section class="nsec" id="n2" aria-labelledby="n2-h">
    <h2 id="n2-h">N-R18-02: a test credential that opens production</h2>
    <p>The test pipeline and the production service share one service account and one vault path. Over a day there are 8 pipeline runs in the test environment. 2 of them come from a compromised test runner that tries the production database.</p>
    <p>Three controls: a separate identity per environment, the production secret path closed to every test identity, and an alert when a test identity asks for a production secret.</p>
    {off2}
    <div class="nnote"><b>The wildcard</b>I thought this guess was the most likely to be wrong, in either direction, and it held. A production secret stored under a path like <code>/kaveri/*/db</code> can be matched by a test identity, and the path restriction misses it. The separate identity stopped the other attempt. Path rules written with wildcards need to be read for what they let through.</div>
    <p>The separate identity did the work. The path restriction only showed up in the wildcard scenario, which the main case did not include.</p>
    <p>The limit: loading a real copy of production data into the test database for a refresh is not seen by any of the three controls. That is an assertion about my model, not something I measured. The model does not inspect data.</p>
  </section>

  <section class="nsec" id="custody" aria-labelledby="c-h">
    <h2 id="c-h">The record</h2>
    {table(['Item', 'Value', 'Where'], [
        [th_row('Guess file'), td('<code>9155e078…</code> (SHA-256 of the whole file)'), td('<a href="/nhi-lab/evidence/guesses/guesses-round-18.md">guesses-round-18.md</a>')],
        [th_row('Commit with the guesses only'), td('<code>e50df1b</code> on my Mac'), td('Before any code existed')],
        [th_row('Commit with code and results'), td('<code>ce3c57e</code> on my Mac'), td('<a href="/nhi-lab/evidence/cases3.py">cases3.py</a>, <a href="/nhi-lab/evidence/run3.py">run3.py</a>, <a href="/nhi-lab/evidence/RESULTS-round-18.md">RESULTS-round-18.md</a>, <a href="/nhi-lab/evidence/results-round-18.json">results-round-18.json</a>')],
        [th_row('Second machine'), td('Mac output equals the sandbox output'), td('Both runs also checked the committed hash before running')],
    ], 'Where to check round 18')}
    <p>To repeat it: download the evidence folder, run <code>python3 run3.py</code>, and compare with <code>RESULTS-round-18.md</code>. The script stops if the guess file no longer matches the hash. Method steps are on the <a href="/nhi-lab/method/">method page</a>.</p>
  </section>

  <section class="nsec" id="limits" aria-labelledby="l-h">
    <h2 id="l-h">What this cannot tell you</h2>
    <ul>
      <li>I wrote the guesses and the code. A match shows my model agrees with my reasoning. It says nothing about a real product.</li>
      <li>Both are small in-memory models with made-up data.</li>
      <li>Two cases say nothing about how common these failures are.</li>
      <li>No product was tested, so none is endorsed or criticised.</li>
    </ul>
    <p>Next: the <a href="/nhi-lab/stage-2/">Stage 2 pages</a> use these results in the control mapping and the test plan.</p>
  </section>
</main>'''
    desc = 'Round 18 of the non-human identity lab: a copied key from another network and a test credential that opens production. Guesses first, one wrong, two controls masked, with the record.'
    write('nhi-lab/round-18/index.html', shell('nhi-lab/round-18/', 'Non-human identity lab: round 18', desc,
          'NHI lab round 18: two more cases', body, ld=ld_article('Non-human identity lab: round 18', desc, 'nhi-lab/round-18/', 'TechArticle', '2026-11-10')))

if __name__ == '__main__':
    build()
