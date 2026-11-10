import csv, io, json
from nhi_site import *
from pages_round19 import MAC_CODE_COMMIT
from nhi_data import load_cases, GUESS_FILES, STAGES, STAGE_OF, GROUPS, OWASP

STAGE_NAME = {k: n for k, n, _ in STAGES}

def exports(cases):
    cols = ['id', 'run', 'group', 'framework_step', 'title', 'what_goes_wrong', 'without_control', 'with_control', 'guess_file',
            'guess_file_sha256', 'guess_matched', 'wrong_guess_detail', 'controls_checked', 'controls_not_noticed', 'owasp_nhi', 'limit']
    rows = []
    for c in cases:
        gf = [v for v in GUESS_FILES.values() if v[0] == c['guess_file']][0]
        rows.append({
            'id': c['id'], 'run': c['run'], 'group': c['group_name'], 'framework_step': STAGE_NAME[c['stage']], 'title': c['title'],
            'what_goes_wrong': c['short'], 'without_control': c['without'], 'with_control': c['with_'], 'guess_file': c['guess_file'],
            'guess_file_sha256': gf[2], 'guess_matched': 'no' if c['wrong'] else 'yes', 'wrong_guess_detail': c['wrong_detail'],
            'controls_checked': len(c['noticed']), 'controls_not_noticed': ' '.join(c['masked']), 'owasp_nhi': ' '.join(c['owasp']),
            'limit': c['limit'],
        })
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator='\n')
    w.writeheader(); w.writerows(rows)
    meta = {
        'title': 'Non-human identity lab: audit data, 67 cases',
        'generated': '2026-11-02', 'author': 'Roshan Trivedi', 'licence': 'CC BY 4.0',
        'note': 'Made-up data. Models are small in-memory simulations written by the same author as the guesses.',
        'cases': len(rows), 'guesses_wrong': sum(1 for r in rows if r['guess_matched'] == 'no'),
        'cases_with_control_not_noticed': sum(1 for r in rows if r['controls_not_noticed']),
        'guess_files': [{'file': v[0], 'label': v[1], 'sha256': v[2]} for v in GUESS_FILES.values()],
        'mac_commits': {'first_run': ['7737a2c', '314d4ee', '474ddc9', 'f902ea8'], 'second_run_guesses': '78d7e3e', 'second_run_code_and_results': '05235fe', 'third_run_guesses': 'e50df1b', 'third_run_code_and_results': 'ce3c57e', 'fourth_run_guesses': 'a2dc1fd', 'fourth_run_code_and_results': MAC_CODE_COMMIT},
    }
    return buf.getvalue(), json.dumps({'meta': meta, 'rows': rows}, indent=1, ensure_ascii=False) + '\n', rows

def build():
    cases = load_cases()
    csv_text, json_text, rows = exports(cases)
    write('nhi-lab/audit/nhi-lab-audit.csv', csv_text)
    write('nhi-lab/audit/nhi-lab-audit.json', json_text)

    n = len(cases)
    wrong = [c for c in cases if c['wrong']]
    masked = [c for c in cases if c['masked']]
    lim = [c for c in cases if c['limit']]

    trs = []
    for c in cases:
        ck = len(c['noticed']); nn = len(c['masked'])
        ctl = f'{ck - nn} of {ck}' if ck else 'none'
        g = '<span class="no">wrong</span>' if c['wrong'] else '<span class="ok">matched</span>'
        cn = f'<span class="{"wn" if nn else "ok"}">{ctl}</span>'
        trs.append(f'<tr data-run="{c["run"]}" data-wrong="{int(c["wrong"])}" data-masked="{int(bool(nn))}" data-limit="{int(bool(c["limit"]))}">'
                   f'<th scope="row"><a href="/nhi-lab/#{c["id"].lower()}">{c["id"]}</a></th><td>{E(c["title"])}</td><td>{E(STAGE_NAME[c["stage"]])}</td>'
                   f'<td>{c["run"]}</td><td>{g}</td><td>{cn}</td><td>{E(c["limit"]) if c["limit"] else "&ndash;"}</td></tr>')
    full = ('<div class="twrap" tabindex="0" role="region" aria-label="All 67 cases"><table class="ntable" id="audit-table"><caption>All 67 cases. '
            '"Controls noticed" counts the controls whose removal changed a result.</caption><thead><tr><th scope="col">Case</th><th scope="col">Title</th>'
            '<th scope="col">Framework step</th><th scope="col">Run</th><th scope="col">Guess</th><th scope="col">Controls noticed</th><th scope="col">Limit</th></tr></thead><tbody>'
            + ''.join(trs) + '</tbody></table></div>')

    wr = table(['Case', 'What my guess said', 'What happened'], [
        [th_row(case_link(c['id'])), td(E(c['title'])), td(E(c['wrong_detail']))] for c in wrong], f'The {len(wrong)} wrong guesses. Each is also on the case card.')

    mr = table(['Case', 'Control whose removal changed nothing'], [
        [th_row(case_link(c['id'])), td(', '.join(f'<code>{E(m)}</code>' for m in c['masked']))] for c in masked],
        f'{len(masked)} cases with at least one control no check noticed.')

    cust = table(['Item', 'Recorded value', 'Where to check'], [
        [th_row('Guess file: rounds 14 and 15'), td('<code>f06f355e…</code> (20 cases)'), td('<a href="/nhi-lab/evidence/guesses/guesses-round-14-15.md">file</a>')],
        [th_row('Guess file: round 17'), td('<code>4e6dfc1a…</code> (4 cases)'), td('<a href="/nhi-lab/evidence/guesses/guesses-round-17.md">file</a>')],
        [th_row('Guess file: gap cases'), td('<code>7d3aee7a…</code> (3 cases)'), td('<a href="/nhi-lab/evidence/guesses/guesses-gap-cases.md">file</a>')],
        [th_row('Guess file: stretch and chains'), td('<code>40c2f87c…</code> (19 cases)'), td('<a href="/nhi-lab/evidence/guesses/guesses-stretch-and-chains.md">file</a>')],
        [th_row('Guess file: round 18'), td('<code>9155e078…</code> (2 cases)'), td('<a href="/nhi-lab/evidence/guesses/guesses-round-18.md">file</a>')],
        [th_row('Guess file: round 19'), td('<code>729e16f2…</code> (19 cases)'), td('<a href="/nhi-lab/evidence/guesses/guesses-round-19.md">file</a>')],
        [th_row('Mac commits, first run'), td('<code>7737a2c</code>, <code>314d4ee</code>, <code>474ddc9</code>, <code>f902ea8</code>'), td('Commit <code>474ddc9</code> is the gap-case guesses. I did not record which of the others holds which file.')],
        [th_row('Mac commit, second-run guesses'), td('<code>78d7e3e</code>'), td('Before any second-run code.')],
        [th_row('Mac commit, second-run code and results'), td('<code>05235fe</code>'), td('The Mac output matched the sandbox.')],
        [th_row('Mac commit, third-run guesses'), td('<code>e50df1b</code>'), td('Before any round 18 code.')],
        [th_row('Mac commit, third-run code and results'), td('<code>ce3c57e</code>'), td('The Mac output matched the sandbox.')],
        [th_row('Mac commit, fourth-run guesses'), td('<code>a2dc1fd</code>'), td('Before any round 19 code.')],
        [th_row('Mac commit, fourth-run code and results'), td(f'<code>{MAC_CODE_COMMIT}</code>'), td('The Mac results file has the same SHA-256 as the sandbox one.')],
    ], 'Chain of custody. Full hashes are in the CSV and on the overview page.')

    body = f'''<main id="main" class="nhi">
  {subnav('audit')}
  {hero('Audit data', 'Every case, every guess, every miss, in one table you can download', f'{n} cases, six hashed guess files, {len(wrong)} wrong guesses and {len(masked)} cases where a control was never noticed. The data is a CSV and a JSON file. A small script checks the guess hashes on your own machine.',
        ['Last reviewed 10 November 2026', 'CC BY 4.0', 'Made-up data'])}

  <div class="ntiles" role="list" aria-label="Audit summary">
    <div class="ntile" role="listitem"><b>{n}</b><span>cases</span></div>
    <div class="ntile good" role="listitem"><b>{n - len(wrong)}</b><span>guesses matched</span></div>
    <div class="ntile bad" role="listitem"><b>{len(wrong)}</b><span>guesses wrong</span></div>
    <div class="ntile warn" role="listitem"><b>{len(masked)}</b><span>cases with a control no check noticed</span></div>
    <div class="ntile" role="listitem"><b>{len(lim)}</b><span>cases with a recorded limit</span></div>
  </div>

  <section class="nsec" id="download" aria-labelledby="dl-h">
    <h2 id="dl-h">Download the data</h2>
    <div class="dl">
      <a href="/nhi-lab/audit/nhi-lab-audit.csv" download>CSV <small>67 rows, 16 columns, opens in any spreadsheet</small></a>
      <a href="/nhi-lab/audit/nhi-lab-audit.json" download>JSON <small>the same rows plus the commit and hash record</small></a>
      <a href="/nhi-lab/evidence/verify.py" download>verify.py <small>checks the six guess hashes</small></a>
    </div>
  </section>

  <section class="nsec" id="check" aria-labelledby="ck-h">
    <h2 id="ck-h">Check it yourself</h2>
    <ol class="nsteps">
      <li><b class="t">Get the evidence folder.</b>Download <code>nhi-lab/evidence/</code> from the repository.<span class="exp">A folder containing <code>guesses/</code>, <code>verify.py</code>, <code>run.py</code>, <code>run2.py</code>, <code>run3.py</code> and <code>run4.py</code>.</span></li>
      <li><b class="t">Check the hashes.</b><code>python3 verify.py</code><span class="exp">Six lines starting with MATCH, then "6 of 6 guess files match the recorded hash." Exit code 0. Tested in the build sandbox on 10 November 2026.</span></li>
      <li><b class="t">Re-run all four runs.</b><code>python3 run.py</code>, <code>python3 run2.py</code>, <code>python3 run3.py</code> and <code>python3 run4.py</code><span class="exp">The same tables as <code>RESULTS.md</code> and <code>RESULTS-stretch.md</code>. In the build sandbox on 2 November 2026 the two <code>results*.json</code> files were identical to the committed ones except for the <code>run_at</code> time stamp.</span></li>
    </ol>
    <div class="nnote"><b>What a pass tells you</b>The guess files are the ones I committed and the code gives the same answers twice. It does not tell you the models are right.</div>
  </section>

  <section class="nsec" id="custody" aria-labelledby="cu-h">
    <h2 id="cu-h">Chain of custody</h2>
    {cust}
  </section>

  <section class="nsec" id="table" aria-labelledby="tb-h">
    <h2 id="tb-h">All {n} cases</h2>
    <div class="nfilters" role="group" aria-label="Filter the table" id="audit-filters">
      <button type="button" aria-pressed="true" data-f="all">All {n}</button>
      <button type="button" aria-pressed="false" data-f="wrong">Wrong guesses ({len(wrong)})</button>
      <button type="button" aria-pressed="false" data-f="masked">Control not noticed ({len(masked)})</button>
      <button type="button" aria-pressed="false" data-f="limit">Has a limit ({len(lim)})</button>
      <button type="button" aria-pressed="false" data-f="r1">First run (27)</button>
      <button type="button" aria-pressed="false" data-f="r2">Second run (19)</button>
      <button type="button" aria-pressed="false" data-f="r3">Third run (2)</button>
      <button type="button" aria-pressed="false" data-f="r4">Fourth run (19)</button>
    </div>
    <p id="audit-count" aria-live="polite" class="lede">Showing all {n} cases.</p>
    {full}
    <p>In chain tests, "not noticed" means that control on its own did not stop the chain.</p>
  </section>

  <section class="nsec" id="wrong" aria-labelledby="wr-h">
    <h2 id="wr-h">Where my guesses were wrong</h2>
    {wr}
  </section>

  <section class="nsec" id="masked" aria-labelledby="ms-h">
    <h2 id="ms-h">Controls nothing noticed</h2>
    <p>If you switch a control off and no result changes, one of two things is true: another control was covering it, or the control did not matter for that case. The lab cannot tell which. That is the point of the check, and it is why I kept these on the page.</p>
    {mr}
  </section>

  <section class="nsec" id="cannot" aria-labelledby="cn-h">
    <h2 id="cn-h">What this audit cannot tell you</h2>
    <ul>
      <li>It is not independent. I wrote the guesses and the models, and a match shows my reasoning is consistent, not that a product behaves this way.</li>
      <li>The hash proves a file did not change after I committed it. It does not prove when I wrote it.</li>
      <li>I did not record which of the four first-run Mac commits holds which guess file.</li>
      <li>A second person writing guesses for a few cases before seeing mine would be a stronger check. It is on the <a href="/nhi-lab/roadmap/">roadmap</a>.</li>
    </ul>
    <p>The procedure is on the <a href="/nhi-lab/method/">method page</a>.</p>
  </section>
</main>'''
    desc = 'All 67 non-human identity lab cases in one table with downloads: guess hashes, commit record, wrong guesses, controls no check noticed, and a script to verify the hashes yourself.'
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'Dataset', 'name': 'Non-human identity lab: audit data, 67 cases', 'description': desc,
                     'url': f'{BASE}/nhi-lab/audit/', 'license': 'https://creativecommons.org/licenses/by/4.0/', 'isAccessibleForFree': True,
                     'creator': {'@type': 'Person', 'name': 'Roshan Trivedi', 'url': f'{BASE}/'},
                     'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': f'{BASE}/nhi-lab/audit/nhi-lab-audit.csv'},
                                      {'@type': 'DataDownload', 'encodingFormat': 'application/json', 'contentUrl': f'{BASE}/nhi-lab/audit/nhi-lab-audit.json'}]}, separators=(',', ':'))
    write('nhi-lab/audit/index.html', shell('nhi-lab/audit/', 'Non-human identity lab: audit data', desc,
          'The lab\'s audit data: 67 cases, 10 wrong guesses, downloadable', body, js='nhi-audit.js', ld=ld))

if __name__ == '__main__':
    build()
