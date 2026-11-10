from nhi_site import *
from nhi_data import load_cases, GUESS_FILES

def method_svg():
    o = ['<svg class="dg" viewBox="0 0 960 400" role="img" aria-label="How one case runs. On the Mac, which is the record: write the guess, hash it, commit it. In the build sandbox: write the model, run with the control off, run with it on, switch each control off alone, record misses and limits. Then run again on the Mac and compare.">', defs('ahm')]
    o.append('<rect class="zone" x="8" y="10" width="944" height="128" rx="14"/><text class="zl" x="24" y="32">Mac: the record</text>')
    o.append('<rect class="zone alt" x="8" y="170" width="944" height="150" rx="14"/><text class="zl" x="24" y="192">Build sandbox: the work</text>')
    top = [(30, 'Write the guess', 'Two lines per case: without the control, with it.'), (365, 'Hash the file', 'SHA-256 of the whole guess file.'), (700, 'Commit it', 'Before any code exists.')]
    for i, (x, n, sdesc) in enumerate(top):
        o.append(box(x, 48, 230, 76, n, sdesc, 'ok' if i == 2 else '', num=i + 1))
    o.append(arrow('M 262 86 L 363 86', label='file', lx=312, ly=76, mid='ahm'))
    o.append(arrow('M 597 86 L 698 86', label='hash recorded', lx=647, ly=76, mid='ahm'))
    row = [(26, 'Write the model', 'A small in-memory copy of the control.'), (214, 'Run, control off', 'Compare with the guess.'), (402, 'Run, control on', 'Compare with the guess.'),
           (590, 'Switch each control off alone', 'Did anything notice?'), (778, 'Record misses and limits', 'Wrong guesses stay on the page.')]
    for i, (x, n, sdesc) in enumerate(row):
        o.append(box(x, 216, 166, 84, n, sdesc, 't1' if i == 3 else '', num=i + 4))
        if i < 4:
            o.append(arrow(f'M {x + 166} 258 L {row[i + 1][0] - 2} 258', mid='ahm'))
    o.append(arrow('M 815 124 L 815 150 L 109 150 L 109 214', label='only now may the code be written', lx=460, ly=144, mid='ahm'))
    o.append(box(778, 340, 166, 48, 'Run again on the Mac', '', 'ok', num=9, tw=20))
    o.append(arrow('M 861 300 L 861 338', 'good', mid='ahm'))
    o.append('<text class="al" x="760" y="368" text-anchor="end">output must match the sandbox</text>')
    o.append('</svg>')
    return ''.join(o)

def build():
    cases = load_cases()
    n1 = [c for c in cases if c['run'] == 1]; n2 = [c for c in cases if c['run'] == 2]
    w1 = sum(c['wrong'] for c in n1); w2 = sum(c['wrong'] for c in n2)
    m_all = sum(bool(c['masked']) for c in cases)

    steps = [
        ('Pick the case.', 'Take a row from the catalogue and shrink it to one failure with a control that should stop it.', 'One sentence: what goes wrong, and which control should prevent it.'),
        ('Write the guess.', 'Write what you expect with no control and with the control. Be specific: numbers, not "better".', 'Two lines per case in a guess file. Nothing is run yet.'),
        ('Hash the guess file.', 'Run <code>shasum -a 256 guesses-file.md</code> on the Mac. Give it the file name; without one the command waits for input.', 'A 64-character hash.'),
        ('Commit the file, then note the hash.', 'Commit the guess file on its own, before any code.', 'A commit hash from before the code exists.'),
        ('Write the model.', 'A small in-memory simulation of the control. Made-up data only (a fictional bank, Kaveri Finance).', 'Code that runs without a network or a real system.'),
        ('Run with the control off, then on.', 'Compare each result with the guess.', 'A match, or a recorded mismatch with both numbers.'),
        ('Switch each control off alone.', 'If the result does not change, no check noticed that control. Another control may be covering it, or the control may not matter for this case.', 'A "noticed" or "NOT noticed" for each control.'),
        ('Write down the limit.', 'For every case, say what the control cannot see.', 'A limit line, or a note that none was found.'),
        ('Run it again on a second machine.', 'Run the same code on the Mac and compare the output with the sandbox.', 'Identical output. If it differs, stop and find out why.'),
    ]
    steps_html = '<ol class="nsteps">' + ''.join(
        f'<li><b class="t">{t}</b>{d}<span class="exp">{e}</span></li>' for t, d, e in steps) + '</ol>'

    tl = [
        ('31 October 2026', 'Catalogue and guesses drafted', 'The use-case catalogue reached 187 rows with the OWASP and MITRE tables (193 after six gap rows were added later). Draft guesses were written for rounds 14, 15 and 17. Nothing was hashed or run.'),
        ('2 November 2026', '1. First run: 27 cases', 'Guess files hashed and committed on the Mac, then the models were written and run. 24 must-run cases and 3 gap cases from 2026 incident reports.'),
        ('2 November 2026', '2. Second-run guesses', f'19 more cases: 13 stretch cases and 6 chain tests. Hashed on the Mac (<code>40c2f87c…</code>) and committed as <code>78d7e3e</code> before any code.'),
        ('2 November 2026', '3. Second run', f'Code and results committed as <code>05235fe</code>. The Mac output matched the sandbox exactly.'),
        ('2 November 2026', '4. Site, book, video', 'The lab page with 46 animated cases at launch, a PDF book, a 54-second silent video, and this set of pages.'),
        ('10 November 2026', '5. Round 18: two cases', 'Guesses committed as <code>e50df1b</code> before any code. Code and results committed as <code>ce3c57e</code>. The Mac output matched the sandbox.'),
        ('10 November 2026', '6. Round 19: the 19 queued cases', 'Guesses hashed on the Mac (<code>729e16f2…</code>) and committed as <code>a2dc1fd</code> before any code. Code and results committed as <code>cbec7a8</code>. The Mac output matched the sandbox, and the results file has the same SHA-256 on both (<code>86aa9d58…</code>). More on the <a href="/nhi-lab/round-19/">round 19 page</a>.'),
    ]
    tlh = '<ol class="tl">' + ''.join(f'<li><time>{d}</time><b>{E(t)}</b>{x}</li>' for d, t, x in tl) + '</ol>'

    slips = table(['What went wrong', 'Case', 'What I did'], [
        [th_row('Guess wrong: the scan missed 2 secrets, not 1'), td(case_links(['S-R17-05'])), td('Recorded. The 2 misses matched no pattern.')],
        [th_row('Guess wrong about which control mattered'), td(case_links(['N-R14-25'])), td('I expected a short token lifetime to change the replay result. Another control already blocked both replays, so it did not.')],
        [th_row('Guess wrong: the alert count'), td(case_links(['N-R18-01'])), td('Recorded with both numbers. Nothing was changed afterwards.')],
        [th_row('Guess wrong: I never said what I was counting'), td(case_links(['P-R15-22', 'S-R17-09'])), td('In one I guessed 0 events without controls, but the connector delivers 14 of 20 either way. In the other I guessed 4 alerts, and the model alerts on every creation attempt, which gives 5. Both left the thing counted open, so the model took the plain reading.')],
        [th_row('Guess wrong: I treated controls as independent'), td(case_links(['P-R15-06', 'P-R15-12', 'S-R17-08'])), td('One control covered another, or an earlier check had already caught the fault. Recorded, with the unnoticed controls split into masked and no effect on what the case counts.')],
        [th_row('Guess wrong: my own arithmetic'), td(case_links(['N-R14-07'])), td('Nine identities with two or three names each cannot make 51 entries; the count is 43. A rule that stripped trailing digits also merged two real accounts. Recorded.')],
        [th_row('Guess wrong: which control matters most'), td(case_links(['C-R16-C01'])), td('I expected the ticket scan to matter most. The owner rule did.')],
        [th_row('Bad test data on the first run'), td(case_links(['N-R14-07'])), td('I had given 21 identities one shared owner, so the merge collapsed them to 11. I fixed the data and kept the first-run file as <a href="/nhi-lab/evidence/RESULTS-stretch-first-run.md">RESULTS-stretch-first-run.md</a>.')],
        [th_row('Harness slip'), td(case_links(['C-R16-C04'])), td('An extra scenario ignored its "late" marker. I fixed it so the marker sets the attack day to 120, and re-ran.')],
    ], 'Mistakes, in the order they matter. Most rows are wrong guesses. The last two are mistakes in my own test harness.')

    defs_tbl = table(['Term', 'Meaning here'], [
        [th_row('Match'), td('The result equals what the guess said, in every run.')],
        [th_row('Wrong guess'), td('A number or a ranking in the guess did not equal the result. The page keeps both.')],
        [th_row('Noticed'), td('Switching that one control off changed a result.')],
        [th_row('Masked'), td('Switching it off changed nothing, because another control already stopped the same thing, or the control did not matter in that case.')],
        [th_row('Limit'), td('What the control cannot see. Every case should have one.')],
        [th_row('Chain test'), td('A series of links an attacker needs. The test records which link each control stops.')],
    ], 'Words used on these pages')

    body = f'''<main id="main" class="nhi">
  {subnav('method')}
  {hero('What we did', 'How the lab was run, step by step, with the mistakes', 'I wrote my guesses, locked them with a hash, then wrote the code and ran every case twice, once without the control and once with it. This page is the full procedure, the dates, and the places I got it wrong.',
        ['Last reviewed 2 November 2026', f'{len(cases)} cases in four runs', 'Made-up data only'])}

  <section class="nsec" id="question" aria-labelledby="q-h">
    <h2 id="q-h">The question</h2>
    <p class="lede">Do the controls people recommend for machine identities stop the failures they are meant to stop, and would anything tell you if one stopped working?</p>
    <div class="ngrid">
      <div class="ncard"><h3>In scope</h3><p>Finding service accounts, owners, rotation, front doors for new identities, just-in-time and recorded privileged access, break-glass, vendor access, and AI tools holding credentials. Chain tests that join several failures.</p></div>
      <div class="ncard"><h3>Out of scope</h3><p>Any real product, any real company's data, performance, cost, and legal or regulatory compliance. The models are small and run in memory.</p></div>
      <div class="ncard"><h3>Why guesses first</h3><p>A test you design after seeing the result will agree with you. A hashed guess file shows the guess was fixed first. It does not prove I did not cheat, but it makes cheating visible to anyone who checks.</p></div>
    </div>
  </section>

  <section class="nsec" id="time" aria-labelledby="t-h">
    <h2 id="t-h">When it happened</h2>
    {tlh}
    <p>I do not have the exact times of the Mac commits in this record. The commit hashes are on the <a href="/nhi-lab/audit/#custody">audit page</a>.</p>
  </section>

  <section class="nsec" id="flow" aria-labelledby="f-h">
    <h2 id="f-h">The procedure in one picture</h2>
    {figure(method_svg(), 'Nine steps in two places. The Mac holds the record. The sandbox does the work. The arrow between them is the rule that matters: code comes after the commit.', [('ok', 'Locks or confirms the record'), ('t1', 'Step that finds masked controls'), ('da', 'Rule')])}
  </section>

  <section class="nsec" id="steps" aria-labelledby="s-h">
    <h2 id="s-h">The procedure, as steps you could repeat</h2>
    <p>Each step says what you should see afterwards. The <code>shasum</code> and <code>git</code> steps I ran on my Mac. The Python commands I ran in the build machine, a cloud sandbox, on 2 November 2026 for the first runs and on 10 November for rounds 18 and 19. The Mac runs matched each time.</p>
    {steps_html}
    <div class="nnote"><b>Careful with the commit</b>Commit only the guess file before the code. On my Mac I ran <code>git add</code> with no paths once, and I ran a hash command with no file name, which waits for input. Both are harmless, and both cost time.</div>
  </section>

  <section class="nsec" id="terms" aria-labelledby="tm-h">
    <h2 id="tm-h">What the words mean</h2>
    {defs_tbl}
  </section>

  <section class="nsec" id="numbers" aria-labelledby="n-h">
    <h2 id="n-h">The numbers</h2>
    <div class="ntiles">
      <div class="ntile"><b>{len(n1)}</b><span>first-run cases ({len(n1) - w1} guesses matched, {w1} wrong)</span></div>
      <div class="ntile"><b>{len(n2)}</b><span>second-run cases ({len(n2) - w2} matched, {w2} wrong)</span></div>
      <div class="ntile warn"><b>{m_all}</b><span>cases with a control no check noticed</span></div>
      <div class="ntile good"><b>4 of 4</b><span>runs that matched on the Mac</span></div>
    </div>
    <p>The full table is on the <a href="/nhi-lab/audit/">audit page</a>, with downloads.</p>
  </section>

  <section class="nsec" id="mistakes" aria-labelledby="m-h">
    <h2 id="m-h">What went wrong</h2>
    {slips}
  </section>

  <section class="nsec" id="limits" aria-labelledby="l-h">
    <h2 id="l-h">What this method cannot tell you</h2>
    <ul>
      <li>I wrote the guesses and the code. A match shows my model agrees with my reasoning, not that a real product behaves that way.</li>
      <li>A hash proves the file did not change after I committed it. It does not prove when I wrote it, beyond the commit time.</li>
      <li>Chain tests are rule models. Each link is stopped by the controls I decided stop it, so their results follow from my rules.</li>
      <li>Three chain tests had an extra scenario written after the fact to probe a limit. I marked them as extras.</li>
    </ul>
    <p>For how I use AI tools in this kind of work, see <a href="/ai/">how I use AI</a>.</p>
  </section>

  <section class="nsec" id="repeat" aria-labelledby="r-h">
    <h2 id="r-h">Repeat it yourself</h2>
    <ol class="nsteps">
      <li><b class="t">Download the evidence folder.</b>It is in the repository under <code>nhi-lab/evidence/</code>.<span class="exp">A folder with <code>guesses/</code>, the case files <code>cases.py</code> to <code>cases4.py</code> and the runners <code>run.py</code> to <code>run4.py</code>.</span></li>
      <li><b class="t">Check the guess hashes.</b><code>python3 verify.py</code><span class="exp">"6 of 6 guess files match the recorded hash." Tested in the build sandbox on 10 November 2026.</span></li>
      <li><b class="t">Run all four runs.</b><code>python3 run.py</code>, <code>python3 run2.py</code>, <code>python3 run3.py</code> then <code>python3 run4.py</code>. They need only Python 3 and they check the hashes first.<span class="exp">The tables in <code>RESULTS.md</code>, <code>RESULTS-stretch.md</code>, <code>RESULTS-round-18.md</code> and <code>RESULTS-round-19.md</code>. The first two runs were identical to the committed files on 2 November 2026, except for the time stamp.</span></li>
    </ol>
  </section>
</main>'''
    desc = 'The full procedure for the 67-case non-human identity lab: guesses hashed before code, each control switched off alone, dates, steps with expected results, and every mistake.'
    write('nhi-lab/method/index.html', shell('nhi-lab/method/', 'How the lab was run', desc,
          'How I ran 67 non-human identity cases, and where I got it wrong', body, ld=ld_article('How the NHI lab was run', desc, 'nhi-lab/method/')))

if __name__ == '__main__':
    build()
