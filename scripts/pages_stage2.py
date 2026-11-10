from nhi_site import *
from nhi_data import OWASP

R18 = {}

def link(cid):
    if cid.startswith('N-R18'):
        return f'<a href="/nhi-lab/round-18/#{cid.lower()}">{cid}</a>'
    return case_link(cid)

def build():
    fit = table(['Problem', 'Category that usually fits', 'Lab case that shows the risk'], [
        [th_row('Find identities nobody listed'), td('NHI discovery, cloud risk platforms'), td(f'{link("N-R14-01")}: a directory-only scan found 12 of 27')],
        [th_row('Owners, reviews and retirement'), td('Identity governance (IGA)'), td(f'{link("N-R14-09")}, {link("N-R14-11")}')],
        [th_row('Store, rotate and issue secrets'), td('Secrets managers, PAM vaults'), td(f'{link("N-R14-14")}, {link("N-R14-15")}')],
        [th_row('Time-limited privileged access and recording'), td('Privileged access management (PAM)'), td(f'{link("P-R15-02")}, {link("P-R15-03")}, {link("P-R15-07")}')],
        [th_row('Stop leaks before commit'), td('Secret scanning in the developer workflow'), td(f'{link("S-R17-05")}: 6 of 8 caught')],
        [th_row('Revoke third-party and AI app grants fast'), td('Identity provider app controls, SaaS security'), td(f'{link("N-R14-23")}, {link("S-R17-01")}')],
        [th_row('Tie a key to the workload that owns it'), td('Workload identity, mutual TLS, secrets managers'), td(f'{link("N-R18-01")}: a copied key from another network was refused')],
        [th_row('Keep test away from production'), td('Separate accounts or projects per environment, vault policy'), td(f'{link("N-R18-02")}: a wildcard path left 1 production secret readable')],
    ], 'Fit by problem. These are categories, not products')

    cap = table(['Capability', 'PAM', 'IGA', 'Secrets manager', 'NHI or cloud-risk platform'], [
        [th_row('Discover unknown machine identities'), td('Partly'), td('Rarely'), td('Rarely'), td('Usually')],
        [th_row('Named owner and review'), td('Partly'), td('Usually'), td('Rarely'), td('Partly')],
        [th_row('Vault and rotate secrets'), td('Usually'), td('Rarely'), td('Usually'), td('Rarely')],
        [th_row('Short-lived, per-workload credentials'), td('Partly'), td('Rarely'), td('Usually'), td('Partly')],
        [th_row('Session recording and time-limited access'), td('Usually'), td('Rarely'), td('Rarely'), td('Rarely')],
        [th_row('Retire unused identities'), td('Partly'), td('Usually'), td('Rarely'), td('Partly')],
        [th_row('Revoke third-party and AI app grants'), td('Rarely'), td('Partly'), td('Rarely'), td('Partly')],
        [th_row('Check that a sign-off is true'), td('Rarely'), td('Rarely'), td('Rarely'), td('Rarely')],
    ], 'Capability matrix. My reading of public material, not tested against any product')

    risk = table(['Risk', 'Likelihood', 'Impact', 'Score', 'Evidence from the lab'], [
        [th_row('Secret leaks into code or config'), td('4'), td('5'), td('<b>20</b>'), td('The scan missed 2 of 8')],
        [th_row('Identity nobody knows about'), td('4'), td('4'), td('<b>16</b>'), td('A directory-only scan saw 12 of 27')],
        [th_row('Third-party app breached, grant still valid'), td('3'), td('5'), td('<b>15</b>'), td('An allowlisted app still works until it is revoked')],
        [th_row('Test credential reaches production'), td('3'), td('5'), td('<b>15</b>'), td('Round 18: a wildcard path left 1 production secret readable from test')],
        [th_row('False sign-off accepted'), td('4'), td('3'), td('<b>12</b>'), td('A fake ticket and a false justification passed')],
        [th_row('Long-lived token or copied key reused'), td('3'), td('4'), td('<b>12</b>'), td('Binding and revoke masked each other. It matters if one is absent. A compromised host still passes the binding.')],
        [th_row('Leaver or retired app keeps access'), td('4'), td('3'), td('<b>12</b>'), td('90 days later all 3 still worked without the control')],
        [th_row('Break-glass used as a side door'), td('2'), td('5'), td('<b>10</b>'), td('4 days of routine use went unnoticed')],
        [th_row('Rotation causes an outage'), td('3'), td('3'), td('<b>9</b>'), td('A consumer missing from the list still broke')],
    ], 'Risk scores: likelihood times impact, each 1 to 5')

    br = table(['ID', 'Business requirement'], [
        [th_row('BR1'), td('The company can list every machine identity and show who owns it.')],
        [th_row('BR2'), td('Secrets are changed on a schedule, and a failed change is noticed within a day.')],
        [th_row('BR3'), td('Privileged access is time-limited and recorded.')],
        [th_row('BR4'), td('When a vendor or app is breached, its access can be cut within an hour.')],
        [th_row('BR5'), td('AI tools and agents have their own identity, a named owner and an end date.')],
        [th_row('BR6'), td('Anyone can see which controls were tested, how, and what failed.')],
        [th_row('BR7'), td('Sign-offs are checked against a source, not accepted as text.')],
        [th_row('BR8'), td('Test and production never share a credential or a vault path.')],
        [th_row('BR9'), td('A copied credential is useless away from the workload it belongs to.')],
    ], 'Business requirements')

    fr = table(['ID', 'Functional requirement', 'Traces to'], [
        [th_row('FR1'), td('Merge identity sources (directory, cloud, CI) into one list with the source shown.'), td(f'BR1, {link("N-R14-01")}')],
        [th_row('FR2'), td('Refuse creation of an identity without owner, scope and expiry.'), td(f'BR1, BR5, {link("N-R14-18")}')],
        [th_row('FR3'), td('Pause a credential with no owner after 30 days.'), td(f'BR1, {link("N-R14-09")}')],
        [th_row('FR4'), td('Rotate consumers first, then the secret, then prove the old one is dead.'), td(f'BR2, {link("N-R14-15")}')],
        [th_row('FR5'), td('Alert on a failed rotation on day 1.'), td(f'BR2, {link("N-R14-14")}')],
        [th_row('FR6'), td('Close privileged access by itself at the end of the window. Allow one extension, then a person approves.'), td(f'BR3, {link("P-R15-02")}, {link("P-R15-03")}')],
        [th_row('FR7'), td('Block direct login to vaulted targets.'), td(f'BR3, {link("P-R15-07")}')],
        [th_row('FR8'), td('Keep an app allowlist and a revoke action that works within 60 minutes.'), td(f'BR4, {link("N-R14-23")}')],
        [th_row('FR9'), td('Give each agent its own identity and tag its log lines.'), td(f'BR5, {link("S-R17-03")}')],
        [th_row('FR10'), td('Scan commits and configuration for secret patterns, and report what the scan cannot see.'), td(f'BR2, {link("S-R17-05")}')],
        [th_row('FR11'), td('Check a ticket number against the ticket system.'), td(f'BR7, {link("P-R15-13")}')],
        [th_row('FR12'), td('Bind a key to the workload that owns it, so a call must also carry that workload\'s certificate.'), td(f'BR9, {link("N-R18-01")}')],
        [th_row('FR13'), td('Give each environment its own identity. Close production paths to test identities, and read any wildcard path for what it lets through.'), td(f'BR8, {link("N-R18-02")}')],
        [th_row('FR14'), td('Raise an alert for each new network a key is used from, and also count repeated attempts from the same network, so 3 replays are not shown as 1.'), td(f'BR9, {link("N-R18-01")}')],
    ], 'Functional requirements')

    nfr = table(['ID', 'Non-functional requirement'], [
        [th_row('NFR1'), td('Every control action is logged with who, what and when, and the log cannot be edited by the person it records.')],
        [th_row('NFR2'), td('Revoke completes within 60 minutes of the decision.')],
        [th_row('NFR3'), td('Rotation does not cause an outage in the dry run before it runs for real.')],
        [th_row('NFR4'), td('The inventory is refreshed at least daily, because short-lived identities are missed by weekly scans.')],
        [th_row('NFR5'), td('Break-glass access is alerted in real time.')],
        [th_row('NFR6'), td('Test data is made up and no real secret is used in any test.')],
        [th_row('NFR7'), td('The results and the guess files can be re-run by someone else with Python 3.')],
    ], 'Non-functional requirements')

    sit = table(['Test', 'Parts', 'Pass when'], [
        [th_row('SIT1'), td('Directory, cloud and CI feed the inventory'), td('All three sources appear, each with its source')],
        [th_row('SIT2'), td('Inventory feeds the owner check and the ticket system'), td('An identity with no owner opens a ticket')],
        [th_row('SIT3'), td('Vault, rotation job and the consumer'), td('The consumer connects after rotation and the old secret is refused')],
        [th_row('SIT4'), td('Identity provider and PAM'), td('Direct login is refused and the brokered one is recorded')],
        [th_row('SIT5'), td('Alerting and SIEM'), td('Each control action appears in the log within 5 minutes')],
        [th_row('SIT6'), td('API gateway and workload certificates'), td('A replay of a valid key from a second network is refused, and one alert is raised')],
        [th_row('SIT7'), td('Vault policy and the test pipeline'), td('A test identity cannot read any production secret, including one under a wildcard path')],
    ], 'System integration tests')

    uat = table(['Test', 'Who', 'Pass when'], [
        [th_row('UAT1'), td('Identity owner'), td('Can find their identities and see what is overdue')],
        [th_row('UAT2'), td('Engineer'), td('Can get two hours of privileged access without asking a person twice')],
        [th_row('UAT3'), td('Approver'), td('Sees the risk first and can reject a request')],
        [th_row('UAT4'), td('Security analyst'), td('Can revoke a vendor app and see the effect within an hour')],
        [th_row('UAT5'), td('Auditor'), td('Can see the control, the evidence and its date')],
    ], 'User acceptance tests')

    rows = []
    status = {
        'NHI1': 'Tested', 'NHI2': 'Tested. 2 secrets of 8 missed in one case.', 'NHI3': 'Tested', 'NHI4': 'Tested in two cases. A compromised host still passes.',
        'NHI5': 'Tested', 'NHI6': 'Tested', 'NHI7': 'Tested', 'NHI8': 'Tested in two cases. A wildcard path leaked 1 secret.', 'NHI9': 'Tested', 'NHI10': 'Tested',
    }
    for code, name, ids, _ in OWASP:
        cases = ids.split() + R18.get(code, [])
        rows.append([th_row(f'{code} {name}'), td(', '.join(link(c) for c in cases)), td(status[code])])
    mapt = table(['OWASP item', 'Lab cases that touch it', 'Status'], rows, 'Mapping to the OWASP Non-Human Identities Top 10 (2025)')

    body = f'''<main id="main" class="nhi">
  {subnav('stage2')}
  {hero('Stage 2', 'From lab results to a plan: tool fit, risks, requirements and a test plan', 'The lab showed what controls do in small models. This page turns that into the documents a team needs to act on it: how to choose a tool, what to rank first, what to ask for and how to test it. It is a draft for discussion and ranks no products.',
        ['Last reviewed 10 November 2026', 'Built on 48 cases in three runs', 'No product tested'])}

  <section class="nsec" id="read" aria-labelledby="rd-h">
    <h2 id="rd-h">Read this first</h2>
    <ul>
      <li>No product was tested. Where I describe a category of tool, I am reading public material, and each claim needs checking against the vendor's own documents.</li>
      <li>The scores are my proposal for ranking a list. Treat the lab results behind them as evidence only, because every case is a small model that I wrote.</li>
      <li>Passing a test in this plan is not a compliance claim.</li>
      <li>All data is made up (Kaveri Finance). Case numbers link to the lab page, or to the <a href="/nhi-lab/round-18/">round 18 page</a>.</li>
    </ul>
  </section>

  <section class="nsec" id="fit" aria-labelledby="ft-h">
    <h2 id="ft-h">1. Tool fit</h2>
    <p>Ask these before looking at any tool: Which machine identities do we have, and where? Which can we rotate without an outage, and which need a code change first? Who owns each one, and where is that recorded? Which privileged sessions must be recorded or time-limited? How fast can we revoke a vendor or an app after a breach notice?</p>
    {fit}
  </section>

  <section class="nsec" id="matrix" aria-labelledby="mx-h">
    <h2 id="mx-h">2. Capability matrix</h2>
    <p>"Usually" means the category is built for it. "Partly" means some products do it. "Rarely" means it is not the usual job. The last row is the gap the lab found: owner attestations, break-glass justifications and ticket numbers were accepted as plain text in my models.</p>
    {cap}
  </section>

  <section class="nsec" id="risk" aria-labelledby="rk-h">
    <h2 id="rk-h">3. Risk scores</h2>
    <p>Likelihood and impact are each 1 to 5, multiplied. Two items with the same score can have different reach.</p>
    {risk}
  </section>

  <section class="nsec" id="req" aria-labelledby="rq-h">
    <h2 id="rq-h">4. Requirements</h2>
    <h3>Business</h3>
    {br}
    <h3>Functional</h3>
    {fr}
    <h3>Non-functional</h3>
    {nfr}
  </section>

  <section class="nsec" id="tests" aria-labelledby="ts-h">
    <h2 id="ts-h">5. Test plan: SIT and UAT</h2>
    <p>System integration testing asks whether each part works with the others. User acceptance testing asks whether the people who use it accept it.</p>
    {sit}
    {uat}
    <div class="nnote"><b>Entry and exit</b>Entry: made-up data only, all guess files hashed and committed, an environment copy that is not production. Exit: every test run with a recorded result, every failure listed with an owner, and a retest after fixes.</div>
  </section>

  <section class="nsec" id="mapping" aria-labelledby="mp-h">
    <h2 id="mp-h">6. Control mapping</h2>
    <p>This is my reading of the OWASP Non-Human Identities Top 10 (2025) against the lab cases. It is not an OWASP assessment. Every item now has at least one tested case. NHI4 and NHI8 were the thin ones until round 18.</p>
    {mapt}
    <p>The OWASP agentic risks ASI05, ASI06 and ASI07 have catalogue rows but no tested cases yet. Compliance mapping (RBI, CERT-In, data protection law) is not done, and I make no compliance claim.</p>
  </section>

  <section class="nsec" id="not" aria-labelledby="nt-h">
    <h2 id="nt-h">What this page does not do</h2>
    <ul>
      <li>It ranks no products and says nothing about what any vendor does today.</li>
      <li>The scores are a proposal, not a measured result.</li>
      <li>It is no substitute for a risk assessment of your own environment.</li>
    </ul>
    <p>See the <a href="/nhi-lab/framework/">framework</a>, the <a href="/nhi-lab/market/">market view</a> and the <a href="/nhi-lab/method/">method</a>.</p>
  </section>
</main>'''
    desc = 'Stage 2 of the non-human identity lab: tool fit, capability matrix, risk scores, business, functional and non-functional requirements, a SIT and UAT plan, and control mapping to the OWASP NHI Top 10.'
    write('nhi-lab/stage-2/index.html', shell('nhi-lab/stage-2/', 'Non-human identity lab: Stage 2 plan', desc,
          'NHI lab Stage 2: requirements and test plan', body, ld=ld_article('Non-human identity lab: Stage 2 plan', desc, 'nhi-lab/stage-2/', 'TechArticle', '2026-11-10')))

if __name__ == '__main__':
    build()
