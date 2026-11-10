from nhi_site import *

LANES = [
 ('done', 'Done', [
   ('31 Oct 2026', 'Use-case catalogue and test plan', 'Rows for non-human identity, privileged access and shadow AI, with business use cases, a test plan and a retro. Six gap rows were added later.'),
   ('2 Nov 2026', 'First run: 27 cases', 'Guesses hashed and committed first. 25 matched, 2 wrong.'),
   ('2 Nov 2026', 'Second run: 19 cases', '13 stretch cases and 6 chain tests. Mac and sandbox output matched.'),
   ('2 Nov 2026', 'Lab page, PDF book, video', '46 animated case cards at launch, a book, and a 54-second silent video. Rebuilt on 10 November with all 67 cases.'),
   ('2 Nov 2026', 'Framework, market, method, audit, roadmap, explainer', 'This set of pages, with downloadable audit data.'),
   ('10 Nov 2026', 'Round 18: two cases', 'NHI4 and NHI8, the two thin OWASP items. 1 guess wrong (the alert count) and 2 controls masked. Mac and sandbox output matched.'),
   ('10 Nov 2026', 'Round 19: the 19 queued cases', 'Guesses committed first as a2dc1fd. 14 matched in full, 5 had a wrong guess, and 14 of 57 controls changed nothing the case counts.'),
   ('10 Nov 2026', 'Completeness register', 'Every one of the 193 catalogue rows has a final status. Rows that need a real environment were not run, and each has a reason.'),
   ('10 Nov 2026', 'Counts brought to 67 cases and 10 wrong guesses', 'Lab page, audit data and files, framework, method, explainer, the PDF book and the video all rebuilt from the same data.'),
   ('10 Nov 2026', 'Stage 2 pages', 'Tool fit, capability matrix, risk scores, requirements, SIT and UAT plan and control mapping, now updated with rounds 18 and 19.'),
 ]),
 ('now', 'Now', [
   ('Not run', 'Lighthouse and a screen-reader pass', 'On 10 November I checked headings, table captions, image text and phone width on the new and changed pages. Lighthouse and a screen reader are still to do, in a normal browser.'),
 ]),
 ('next', 'Next', [
   ('Parked', 'Rows that need a real environment', 'The catalogue rows that cannot be modelled in memory are listed in the completeness register with a reason for each.'),
   ('Parked', 'Read ATT&CK campaign C0064', 'I noted it but have not read it.'),
   ('Parked', 'Check vendor wording', 'The PAM and secrets-manager descriptions on the market page. Product claims need the vendor\'s own documents.'),
 ]),
 ('later', 'Later', [
   ('No date set', 'An outside reader writes guesses first', 'A stronger test than my own: someone else guesses a few cases before seeing mine.'),
   ('No date set', 'Cloud-specific variants', 'AWS, Azure and Google Cloud each have their own key and role habits.'),
   ('No date set', 'Indian rules check', 'RBI, CERT-In and the data protection law. I will make no compliance claim.'),
   ('No date set', 'Cost data', 'None yet.'),
   ('Every quarter', 'Re-check the market page', 'Prices, ownership and roadmaps change fastest. Watch the NIST agent identity project, whose first use case is in DevSecOps.'),
   ('Series', 'Next topics', 'Conditional access, MFA, 2FA and SSO.'),
 ]),
]

def build():
    cols = ''
    n = 0
    for k, title, items in LANES:
        cards = ''.join(f'<div class="rcard"><span class="when">{E(w)}</span><b>{E(t)}</b><p>{E(d)}</p></div>' for w, t, d in items)
        n += len(items)
        cols += f'<section class="lane {k}" aria-labelledby="ln-{k}"><h3 id="ln-{k}">{title} <span>{len(items)}</span></h3>{cards}</section>'
    body = f'''<main id="main" class="nhi">
  {subnav('roadmap')}
  {hero('Roadmap', 'What is done, what I am checking now, and what comes next', 'I have not put dates on the future items. A date I cannot keep is a claim I cannot back, so the order is the plan. Posting anything publicly waits for my own go.',
        ['Last reviewed 10 November 2026', f'{n} items', 'Dates only where work is done'])}

  <section class="nsec" id="board" aria-labelledby="bd-h">
    <h2 id="bd-h">The board</h2>
    <div class="road">{cols}</div>
  </section>

  <section class="nsec" id="rules" aria-labelledby="rl-h">
    <h2 id="rl-h">Rules I follow for every item</h2>
    <ol>
      <li>Guesses first. Write what I expect, hash it, commit it, then write the code.</li>
      <li>Wrong guesses stay on the page next to the right answer.</li>
      <li>Every case gets a limit: what the control cannot see.</li>
      <li>Market facts get a date, a source and a trust label. If I cannot check one, I say so.</li>
      <li>No product is tested, so none is endorsed or criticised.</li>
    </ol>
  </section>

  <section class="nsec" id="ask" aria-labelledby="ak-h">
    <h2 id="ak-h">Where you can help</h2>
    <p>If you work on identity or privileged access and you think a case is wrong, or you can think of a variant that breaks a control, <a href="/#contact">tell me</a>. I will add it and keep the original on the page. If you would like to write guesses for a case before you see mine, I would like that most of all.</p>
    <p>See the <a href="/nhi-lab/method/">method</a> and the <a href="/nhi-lab/audit/">audit data</a>.</p>
  </section>
</main>'''
    desc = 'The non-human identity lab roadmap: what is done with dates, what is being checked now, and the next and later items, without invented deadlines.'
    write('nhi-lab/roadmap/index.html', shell('nhi-lab/roadmap/', 'Non-human identity lab roadmap', desc,
          'The NHI lab roadmap', body, ld=ld_article('Non-human identity lab roadmap', desc, 'nhi-lab/roadmap/', 'WebPage')))

if __name__ == '__main__':
    build()
