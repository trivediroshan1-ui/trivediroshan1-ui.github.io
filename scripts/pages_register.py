import csv, io, re
from nhi_site import *
import nhi_register as R

STATUS = {'R': 'Run in this lab', 'E': 'Tested in an earlier lab', 'P': 'Partly tested', 'X': 'Not run'}
KIND = {'env': 'Needs a real product or environment', 'plan': 'A plan or process, not a control to switch off',
        'near': 'A nearby case covers the mechanism', 'data': 'Cannot be tested with made-up data', 'signal': 'A list of signals, not a control'}
CASE_RE = re.compile(r'^([A-Z]-R\d+-[A-Z]?\d+)(.*)$')

def rank(s):
    return {'R': 'ok', 'E': 'ok', 'P': 'mid', 'X': 'no'}[s]

def status_cell(row):
    _, _, _, s, k, _ = row
    label = STATUS[s] + (f': {KIND[k].lower()}' if k else '')
    return td(f'<span class="nb {"high" if s in "RE" else ("med" if s == "P" else "low")}">{E(STATUS[s])}</span>' + (f'<br><small>{E(KIND[k])}</small>' if k else ''))

def ref_cell(row):
    _, _, _, s, _, ref = row
    if s == 'R':
        m = CASE_RE.match(ref)
        if m: return td(case_link(m.group(1)) + E(m.group(2)))
    return td(E(ref))

def group_table(group, caption):
    rows = [r for r in R.ALL if r[1] == group]
    return table(['Row', 'Use case', 'Final status', 'Case, or why it was not run'],
                 [[th_row(f'<a id="{r[0].lower()}"></a>{r[0]}'), td(E(r[2])), status_cell(r), ref_cell(r)] for r in rows], caption)

def link_counts(ids):
    done = sum(R.BY[i][3] in 'RE' for i in ids if i in R.BY)
    part = sum(R.BY[i][3] == 'P' for i in ids if i in R.BY)
    no = sum(R.BY[i][3] == 'X' for i in ids if i in R.BY)
    return done, part, no

def chain_status(cid, links, case):
    ids = [x.strip() for x in links.split(',')]
    d, p, n = link_counts(ids)
    return d, p, n, len(ids)

def export_csv():
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['row', 'group', 'use_case', 'final_status', 'reason_kind', 'case_or_reason'])
    for r in R.ALL:
        w.writerow([r[0], r[1], r[2], STATUS[r[3]], KIND.get(r[4], ''), r[5]])
    for cid, title, links, case in R.CH:
        w.writerow([cid, 'Chains', title, 'Run in this lab' if case else 'Documented only, not run', '', case or f'Links to {links}'])
    for bid, title, links, note in R.BIZ:
        d, p, n = link_counts(links)
        w.writerow([bid, 'Business use cases', title, 'Roll-up of linked rows', '', f'{d} run or tested, {p} partly, {n} not run. {note}'.strip()])
    return buf.getvalue()

def build():
    tech = R.ALL
    cnt = {s: sum(r[3] == s for r in tech) for s in 'REPX'}
    kinds = {k: sum(r[4] == k for r in tech) for k in KIND}
    nch_run = sum(1 for c in R.CH if c[3]); nch_doc = len(R.CH) - nch_run
    nrows = len(tech) + len(R.CH) + len(R.BIZ)
    assert nrows == 193 and sum(cnt.values()) == 147 and nch_run == 6

    # chains
    crow = []
    for cid, title, links, case in R.CH:
        d, p, n, t = chain_status(cid, links, case)
        if case: st = '<span class="nb high">Run in this lab</span>'; ref = case_link(case) + f'. Links: {E(links)}.'
        else:
            st = '<span class="nb low">Documented only</span>'
            ref = f'Not run as a chain. Links: {E(links)}. Run or tested one at a time: {d} of {t}' + (f', partly {p}' if p else '') + (f', not run {n}' if n else '') + '.'
        crow.append([th_row(cid), td(E(title)), td(st), td(ref)])
    ch = table(['Chain', 'Title', 'Final status', 'Case, or what stands behind it'], crow, 'The 20 risk-to-threat chains')

    brow = []
    for bid, title, links, note in R.BIZ:
        d, p, n = link_counts(links)
        if not links: lab = 'Not a lab control'
        elif n == 0: lab = 'Supported by lab cases'
        elif d + p == 0: lab = 'No case behind it'
        else: lab = 'Partly supported'
        cls = {'Supported by lab cases': 'high', 'Partly supported': 'med'}.get(lab, 'low')
        counts = f'{len(links)} linked rows: {d} run or tested, {p} partly, {n} not run.' if links else ''
        brow.append([th_row(bid), td(E(title)), td(f'<span class="nb {cls}">{lab}</span>'), td(E((counts + ' ' + note).strip()))])
    biz = table(['Use case', 'Title', 'Final status', 'Rows behind it'], brow, 'The 26 business use cases, rolled up from the technical rows they link to')
    nb_sup = sum(1 for b in R.BIZ if b[2] and link_counts(b[2])[2] == 0)
    nb_part = sum(1 for b in R.BIZ if b[2] and link_counts(b[2])[2] > 0 and sum(link_counts(b[2])[:2]) > 0)
    nb_no = sum(1 for b in R.BIZ if b[2] and sum(link_counts(b[2])[:2]) == 0)
    nb_na = sum(1 for b in R.BIZ if not b[2])

    reasons = table(['Why it was not run', 'Rows', 'What that means'], [
        [th_row(KIND['env']), td(str(kinds['env'])), td('Vaults, fleets, tenants, servers, devices and databases cannot be stood up in a small in-memory model. I wrote no guesses and ran no code for these.')],
        [th_row(KIND['plan']), td(str(kinds['plan'])), td('Platform evaluation, migration, audit mapping, training and architecture. The Stage 2 pages hold the paper side of some of them.')],
        [th_row(KIND['near']), td(str(kinds['near'])), td('A control in a case I already ran does the same job, so a separate case would repeat it.')],
        [th_row(KIND['data']), td(str(kinds['data'])), td('Personal AI accounts used for work. There is nothing to simulate with made-up data.')],
        [th_row(KIND['signal']), td(str(kinds['signal'])), td('A list of signals to watch. There is no control to switch off.')],
    ], 'Reasons for the rows that were not run')

    csv_text = export_csv()
    write('nhi-lab/register/nhi-lab-register.csv', csv_text)

    body = f'''<main id="main" class="nhi">
  {subnav('register')}
  {hero('Register', 'Every catalogue row, with a final status and a reason',
        f'The catalogue has {nrows} rows. This page gives each one a final status. Where a row was not run, it says why. I ran nothing for the rows that need a real environment.',
        ['Checked 10 November 2026', f'{nrows} rows', f'{cnt["R"] + nch_run} run in this lab', 'Made-up data only (Kaveri Finance)'])}

  <section class="nsec" id="result" aria-labelledby="r-h">
    <h2 id="r-h">The result</h2>
    <div class="ntiles">
      <div class="ntile good"><b>{cnt["R"] + nch_run}</b><span>rows run in this lab: {cnt["R"]} technical rows and {nch_run} chain tests</span></div>
      <div class="ntile good"><b>{cnt["E"]}</b><span>rows tested in an earlier lab, not re-run here</span></div>
      <div class="ntile warn"><b>{cnt["P"]}</b><span>rows partly tested, with the missing part stated</span></div>
      <div class="ntile warn"><b>{cnt["X"] + nch_doc}</b><span>rows not run: {cnt["X"]} technical rows and {nch_doc} documented chains</span></div>
    </div>
    <p>The 147 technical rows are the non-human identity, shadow AI and privileged access rows plus six gap rows. The 20 chains and the 26 business use cases make up the rest. Business use cases are not tested directly. Each one is rolled up from the technical rows it links to: {nb_sup} are supported by lab cases, {nb_part} partly, {nb_no} have no case behind them and {nb_na} are not tested here (a reporting use, and joiners and movers, which the AI governance lab tested).</p>
    <p>The lab itself has 67 cases. Sixty of them map to catalogue rows, six are chain tests, and N-R18-01 (round 18, insecure authentication) extends rows N34 and N36 without being a row of its own.</p>
    <p><a href="/nhi-lab/register/nhi-lab-register.csv" download>Download the register as CSV</a> ({nrows} rows).</p>
  </section>

  <section class="nsec" id="meaning" aria-labelledby="m-h">
    <h2 id="m-h">What each status means</h2>
    <ul>
      <li><b>Run in this lab.</b> A case exists, with guesses written and hashed first and a result recorded.</li>
      <li><b>Tested in an earlier lab.</b> The AI governance lab or the MCP lab tested it. I list their case ids and did not run them again.</li>
      <li><b>Partly tested.</b> Part of the row was tested. The page says which part was not.</li>
      <li><b>Not run.</b> No case exists. The reason is one of five kinds, below.</li>
    </ul>
  </section>

  <section class="nsec" id="why" aria-labelledby="w-h">
    <h2 id="w-h">Why some rows were not run</h2>
    <p>{cnt["X"]} technical rows were not run. Most need something a small model cannot hold. I would rather say so than write a model that looks like evidence.</p>
    {reasons}
  </section>

  <section class="nsec" id="nhi" aria-labelledby="n-h">
    <h2 id="n-h">Non-human identity rows (64)</h2>
    {group_table('Non-human identity', 'Non-human identity rows and their final status')}
  </section>

  <section class="nsec" id="shadow" aria-labelledby="s-h">
    <h2 id="s-h">Shadow AI rows (18)</h2>
    {group_table('Shadow AI accounts', 'Shadow AI rows and their final status')}
  </section>

  <section class="nsec" id="pam" aria-labelledby="p-h">
    <h2 id="p-h">Privileged access rows (59)</h2>
    {group_table('Privileged access', 'Privileged access rows and their final status')}
  </section>

  <section class="nsec" id="gap" aria-labelledby="g-h">
    <h2 id="g-h">Gap rows (6)</h2>
    <p>Three came from 2026 incident reports and were run in the first run. Three are the OWASP agentic items ASI05, ASI06 and ASI07, which the catalogue had no rows for.</p>
    {group_table('Gap rows', 'Gap rows and their final status')}
  </section>

  <section class="nsec" id="chains" aria-labelledby="c-h">
    <h2 id="c-h">Chains (20)</h2>
    <p>Six chains were run as tests. The other {nch_doc} are written out and not run. Their single links were run or tested one at a time where the table says so. That shows each link, and it does not show that the chain holds.</p>
    {ch}
  </section>

  <section class="nsec" id="business" aria-labelledby="b-h">
    <h2 id="b-h">Business use cases (26)</h2>
    {biz}
  </section>

  <section class="nsec" id="cannot" aria-labelledby="x-h">
    <h2 id="x-h">What this cannot tell you</h2>
    <ul>
      <li>The statuses are my reading of the catalogue. I wrote the catalogue, the guesses and the models.</li>
      <li>Rows marked as tested in an earlier lab rest on that lab, with the same limits. I did not re-run them.</li>
      <li>The two queued cases N-R14-08 and N-R14-23 were not run under those ids. Round 18 case N-R18-02 tested a test credential that reaches production and stands for rows N17 and N64. N-R14-23 is now the vendor refresh token case from the first run.</li>
      <li>The catalogue has no rows for conditional access, MFA, 2FA and SSO. Those are the next series.</li>
      <li>No product was tested, so none is endorsed or criticised.</li>
    </ul>
    <p>See the <a href="/nhi-lab/round-19/">round 19 page</a> for the last 19 cases, the <a href="/nhi-lab/audit/">audit data</a> for every case, and the <a href="/nhi-lab/roadmap/">roadmap</a> for what comes next.</p>
  </section>
</main>'''
    desc = 'The non-human identity lab catalogue, row by row: 193 rows, each with a final status. Run, tested in an earlier lab, partly tested, or not run with a reason.'
    write('nhi-lab/register/index.html', shell('nhi-lab/register/', 'Non-human identity lab: register', desc,
          'NHI lab register: every catalogue row and its final status', body, ld=ld_article('Non-human identity lab: register', desc, 'nhi-lab/register/', 'TechArticle', '2026-11-10')))

if __name__ == '__main__':
    build()
