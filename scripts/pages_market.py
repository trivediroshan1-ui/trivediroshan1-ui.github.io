from nhi_site import *
from nhi_data import load_cases, OWASP

# id: (title, publisher, published, url, kind, confidence, note)
SRC = {
 'S1': ('Palo Alto Networks completes acquisition of CyberArk to secure the AI era', 'Palo Alto Networks (press release)', '11 Feb 2026',
        'https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-cyberark-to-secure-the-ai-era', 'primary', 'high', 'Read in full. Statistics in it are the company\'s own.'),
 'S2': ('Delinea completes StrongDM acquisition', 'Delinea (press release)', '5 Mar 2026',
        'https://delinea.com/news/delinea-acquires-strongdm-to-secure-ai-with-continuous-authorization', 'primary', 'med', 'I read the opening of the release in a search result, not the whole page.'),
 'S3': ('SailPoint completes acquisition of Entro Security', 'SailPoint (press release)', '29 Jun 2026',
        'https://www.sailpoint.com/press-releases/sailpoint-closes-entro-security-acquisition', 'primary', 'high', 'Read in full. Terms not disclosed.'),
 'S4': ('Cisco announces intent to acquire Astrix Security (updated 29 June 2026)', 'Cisco (blog)', 'Updated 29 Jun 2026',
        'https://blogs.cisco.com/news/cisco-announces-intent-to-acquire-astrix-security', 'primary', 'med', 'I read the update line in a search result: "We have completed the acquisition of Astrix Security."'),
 'S5': ('AI agent identity consolidation: NHI market concentration risk', 'Cloud Security Alliance, research note', '2026',
        'https://labs.cloudsecurityalliance.org/research/csa-research-note-cisco-astrix-ai-agent-identity-market-cons/', 'secondary', 'med', 'Source for the 4 May 2026 announcement date and the reported price of about $400 million.'),
 'S6': ('Acquisitions by Delinea', 'Tracxn (data aggregator)', 'Oct 2026',
        'https://tracxn.com/d/acquisitions/acquisitions-by-delinea/__DzlU08UU7RvDXZaudojanTD-ON4-E98muPzCw2I441s', 'secondary', 'low', 'Lists 15 Jan 2026. Disagrees with Delinea\'s release (5 Mar 2026). I used the release.'),
 'S7': ('Overview of agent identities in Microsoft Entra Agent ID', 'Microsoft Learn', 'Page updated 1 May 2026',
        'https://learn.microsoft.com/en-us/entra/agent-id/agent-identities', 'primary', 'high', 'Vendor documentation. Describes the product, not how well it works.'),
 'S8': ('OWASP Non-Human Identities Top 10, 2025', 'OWASP', '2025',
        'https://owasp.github.io/www-project-non-human-identities-top-10/2025/top-10-2025/', 'primary', 'high', 'Names and descriptions of the ten risks.'),
 'S9': ('Accelerating the adoption of software and AI agent identity and authorization (concept paper)', 'NIST NCCoE / CSRC', '5 Feb 2026',
        'https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd', 'primary', 'high', 'Comments closed 2 April 2026. A concept paper only, not guidance.'),
 'S10': ('Comments on software and agentic AI identity concept paper', 'NIST news', 'Sep 2026',
         'https://www.nist.gov/news-events/news/2026/09/comments-software-and-agentic-ai-identity-concept-paper', 'primary', 'high', 'Source for 600+ commenters and the DevSecOps first use case.'),
 'S11': ('Widespread data theft targets Salesforce instances via Salesloft Drift', 'Google Cloud Threat Intelligence Group', 'Aug 2025, updated 28 Aug 2025',
         'https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift', 'primary', 'high', 'Source for the dates and the advice to treat connected tokens as compromised.'),
 'S12': ('Salesloft Drift-Salesforce breach (UNC6395)', 'AppOmni (vendor blog)', '2025',
         'https://appomni.com/blog/drift-breach-salesforce-unc6395-saas-prevention/', 'secondary', 'med', 'Relays "over 700 organizations" and cites FBI advisory CSA-2025-250912. I did not open the FBI document.'),
 'S13': ('Salesloft Drift OAuth token breach (Icarus campaign)', 'Rescana (vendor blog)', 'undated in my copy',
         'https://www.rescana.com/post/salesloft-drift-oauth-token-breach-enables-salesforce-data-theft-in-unc6395-icarus-attack-campaign-august-2026', 'secondary', 'low', 'Gives June 2026 dates that contradict Google\'s own advisory (August 2025). I did not use it.'),
 'S14': ('We are fixing the wrong problem in non-human identity security', 'Tuhin Banerjee, Cloud Security Alliance blog', '23 Apr 2026',
         'https://cloudsecurityalliance.org/blog/2026/04/23/we-are-fixing-the-wrong-problem-in-non-human-identity-security', 'opinion', 'med', 'An opinion built on named incidents, with no survey data.'),
 'S15': ('Vercel security breach, April 2026', 'Strapi (blog summary)', 'Apr 2026',
         'https://strapi.io/blog/vercel-security-breach-april-2026', 'secondary', 'low', 'Summary only. Attribution and some details are unverified.'),
 'S16': ('The State of Secrets Sprawl 2026', 'GitGuardian', '2026',
         None, 'vendor', 'med', 'Vendor research on 2025 data. Figures carried from my earlier read; I did not re-fetch the report in this pass.'),
}

def s(i):
    t, p, d, u, k, c, n = SRC[i]
    return f'<sup><a href="#src-{i.lower()}" aria-label="Source {i}">[{i[1:]}]</a></sup>'

def build():
    cases = load_cases()
    prim = sum(1 for v in SRC.values() if v[4] == 'primary')

    deals = table(['Closed', 'Buyer', 'Bought', 'What the target did', 'Terms', 'How I know'], [
        [th_row('11 Feb 2026'), td('Palo Alto Networks'), td('CyberArk'), td('Privileged access and machine identity'),
         td('$45.00 cash plus 2.2005 Palo Alto shares per CyberArk share'), td(f'Buyer\'s release {s("S1")} {badge("primary")}')],
        [th_row('5 Mar 2026'), td('Delinea'), td('StrongDM'), td('Access for engineering, DevOps and AI environments'),
         td('Not read'), td(f'Buyer\'s release {s("S2")} {badge("primary")}. A data aggregator says 15 Jan {s("S6")}; I used the release.')],
        [th_row('29 Jun 2026'), td('SailPoint'), td('Entro Security'), td('Non-human identity and credentials security, Tel Aviv'),
         td('Not disclosed'), td(f'Buyer\'s release {s("S3")} {badge("primary")}')],
        [th_row('29 Jun 2026'), td('Cisco'), td('Astrix Security'), td('Non-human identity security'),
         td('Not stated in what I read. About $400 million is reported.'), td(f'Closing: Cisco\'s blog update {s("S4")} {badge("primary")}. Announcement on 4 May and the price: CSA note {s("S5")} {badge("secondary")}')],
    ], 'Four acquisitions of identity and non-human identity companies that closed in 2026.')

    owasp_short = ''.join(f'<li><b>{c}</b> {E(n)}</li>' for c, n, _, _ in OWASP)

    src_rows = []
    for i, (t, p, d, u, k, c, n) in SRC.items():
        link = f'<a href="{u}" rel="noopener">{E(t)}</a>' if u else E(t)
        src_rows.append(f'<tr id="src-{i.lower()}"><th scope="row">{i[1:]}</th><td>{link}<br><small>{E(n)}</small></td><td>{E(p)}</td><td>{E(d)}</td><td>{badge(k)}</td><td>{badge(c)}</td></tr>')
    srctab = (f'<div class="twrap" tabindex="0" role="region" aria-label="Sources"><table class="ntable"><caption>Every source on this page. Retrieved 2 November 2026 unless noted.</caption>'
              '<thead><tr><th scope="col">#</th><th scope="col">Title and note</th><th scope="col">Publisher</th><th scope="col">Date</th><th scope="col">Type</th><th scope="col">Trust</th></tr></thead><tbody>'
              + ''.join(src_rows) + '</tbody></table></div>')

    gaps = table(['Gap (my view)', 'What the lab saw', 'Cases'], [
        [th_row('Checks that a sign-off is true'), td('Owner attestations, break-glass justifications and ticket numbers were accepted as text in my models. I suspect many real workflows are the same.'), td(case_links(['N-R14-11', 'P-R15-11', 'P-R15-13']))],
        [th_row('Speed of revocation across companies'), td('After a vendor breach the clock starts at their notice, not at your inventory. In the model, a replay at minute 30 still worked.'), td(case_links(['N-R14-23', 'N-R14-05']))],
        [th_row('Identities that live for minutes'), td('A weekly inventory cannot see a token that lasts an hour. The lab\'s short lifetime did not matter once binding and revoke were on, which is a reminder to test it alone.'), td(case_links(['N-R14-25']))],
        [th_row('One view of agent, person and inherited permissions'), td('An AI tool inherited 40 folders when it needed one. An automation using a person\'s login made the log unreadable.'), td(case_links(['S-R17-02', 'S-R17-03']))],
    ], 'Where I think the market still has a gap. This is my reading of the lab, not a survey.')

    notread = ['Analyst reports (Gartner, Forrester, KuppingerCole). They are licensed and I did not read them.',
               'Any product. I tested none, so I make no claim about what a product does today.',
               'Pricing beyond what the press releases state. Cisco and Astrix is reported, not confirmed.',
               'Okta, Microsoft Defender, Ping and the secrets managers, beyond one Microsoft document.',
               'The FBI advisory on the Salesloft Drift campaign. I only saw it cited.']

    body = f'''<main id="main" class="nhi">
  {subnav('market')}
  {hero('Market', 'Four deals, one new identity type and a standards project', f'In the first half of 2026, four deals closed in which larger security companies bought privileged access, machine access or non-human identity specialists. Microsoft documented identity objects for AI agents. NIST asked the public how to identify and authorize them. Each fact below has a date, a source and a trust label. Checked on 2 November 2026.',
        ['Last checked 2 November 2026', f'{len(SRC)} sources, {prim} primary', 'No product tested'])}

  <div class="ntiles" role="list" aria-label="Summary numbers">
    <div class="ntile" role="listitem"><b>4</b><span>acquisitions closed, 11 Feb to 29 Jun 2026</span></div>
    <div class="ntile" role="listitem"><b>600+</b><span>commenters on NIST's agent identity concept paper</span></div>
    <div class="ntile" role="listitem"><b>10</b><span>risks in the OWASP NHI Top 10 (2025)</span></div>
    <div class="ntile warn" role="listitem"><b>0</b><span>products I tested</span></div>
  </div>

  <section class="nsec" id="read" aria-labelledby="rd-h">
    <h2 id="rd-h">How to read the labels</h2>
    <p>{badge('primary')} the party's own page or document. {badge('secondary')} someone else reporting or analysing it. {badge('vendor')} a sales or press statement I could not check. {badge('opinion')} a view, not a measurement. The trust label next to it says how much I would rely on it: {badge('high')}, {badge('med')} or {badge('low')}.</p>
    <p>Prices, ownership and roadmaps are the facts most likely to be wrong or to change. For any of them, check the vendor's own document before you quote.</p>
  </section>

  <section class="nsec" id="deals" aria-labelledby="dl-h">
    <h2 id="dl-h">Who bought whom in 2026</h2>
    {deals}
    <p><b>What I take from it (my view).</b> The platform vendors want machine identity inside their platform. Two of the four targets, Entro and Astrix, were non-human identity specialists. StrongDM sold access for engineering teams, and CyberArk sold privileged access. If you chose a specialist a year ago, ask the new owner for the product roadmap in writing. I have not seen any of those roadmaps.</p>
    <div class="nnote"><b>Where sources disagree</b>A data aggregator lists the Delinea and StrongDM deal on 15 January 2026 {s('S6')}. Delinea's own release says it completed on 5 March 2026 {s('S2')}. Delinea's earlier release said it expected to close in the first quarter. I used the company's release.</div>
  </section>

  <section class="nsec" id="agents" aria-labelledby="ag-h">
    <h2 id="ag-h">AI agents get their own identity objects</h2>
    <p>Microsoft's documentation for Entra Agent ID, last updated 1 May 2026, describes an agent identity as a special service principal. It has no credentials of its own. A reusable template called a blueprint creates it and acquires tokens for it. It can record a <em>sponsor</em>, the person or group accountable for the agent, who is contacted if there is an incident {s('S7')} {badge('primary')}.</p>
    <p>Why it matters here: in the lab, four agents shared one team key, so the log said only "team key" and a revoke hit all four (<a href="/nhi-lab/#n-r14-21">N-R14-21</a>). With one key per agent, the log named the agent and the revoke hit one. A sponsor plus an identity per agent is the product-side version of that control. I tested a model of the idea. I did not test Entra.</p>
  </section>

  <section class="nsec" id="standards" aria-labelledby="st-h">
    <h2 id="st-h">Standards and guidance</h2>
    <h3>OWASP Non-Human Identities Top 10, 2025 {badge('primary')}</h3>
    <p>The ten risks, in OWASP's order {s('S8')}:</p>
    <ol>{owasp_short}</ol>
    <p>I mapped each one to the lab cases that touch it on the <a href="/nhi-lab/framework/#owasp">framework page</a>. Environment isolation and insecure authentication are thinly covered.</p>
    <h3>NIST NCCoE: software and AI agent identity and authorization {badge('primary')}</h3>
    <p>NIST's National Cybersecurity Center of Excellence published a concept paper on 5 February 2026 and took comments until 2 April 2026 {s('S9')}. In September 2026 NIST said it had heard from more than 600 commenters, and that its DevSecOps project will provide the first implementation use case: showing how AI agents can be identified, authenticated and authorized in the software development lifecycle {s('S10')}. A concept paper is not guidance. No control in it is yet something you can be audited against.</p>
  </section>

  <section class="nsec" id="incident" aria-labelledby="in-h">
    <h2 id="in-h">The incident behind two lab cases: Salesloft Drift</h2>
    <p>Google's threat intelligence group reported that, from as early as 8 August 2025 through at least 18 August 2025, an actor it tracks as UNC6395 used stolen OAuth tokens tied to the Salesloft Drift app to read data in customers' Salesforce accounts. Google saw the actor look for AWS access keys, passwords and Snowflake tokens. Salesloft and Salesforce revoked all active access and refresh tokens on 20 August 2025. On 28 August Google added that tokens for Drift's email integration were also compromised and advised customers to treat every token connected to Drift as potentially compromised {s('S11')} {badge('primary')}.</p>
    <p>An AppOmni post says more than 700 organizations were affected and points to an FBI advisory {s('S12')} {badge('secondary')}. I have not seen the FBI document.</p>
    <p>The lab cases built on this pattern are <a href="/nhi-lab/#n-r14-05">N-R14-05</a> (an old grant, a breached vendor) and <a href="/nhi-lab/#n-r14-23">N-R14-23</a> (a refresh token still valid after the notice).</p>
    <div class="nnote"><b>Where sources disagree</b>One vendor blog dates the same campaign to June 2026 {s('S13')}. Google's advisory says August 2025 {s('S11')}. I used Google and left the other out of the facts above.</div>
  </section>

  <section class="nsec" id="other" aria-labelledby="ot-h">
    <h2 id="ot-h">Other things I read</h2>
    <ul>
      <li>Tuhin Banerjee argues on the Cloud Security Alliance blog (23 April 2026) that inventory-first discovery is losing ground to short-lived identities, and that ownership and fast revocation are the neglected parts {s('S14')} {badge('opinion')}.</li>
      <li>Vercel confirmed unauthorized access in April 2026. Reports say it began with a third-party AI app that an employee had linked with broad permissions {s('S15')} {badge('secondary')} {badge('low')}.</li>
      <li>GitGuardian's 2026 report counts 28,649,024 new secrets on public GitHub, 1,275,105 of them AI-service secrets, and 24,008 unique secrets in MCP configuration files {s('S16')} {badge('vendor')}.</li>
      <li>Palo Alto Networks says machine identities outnumber human identities by more than 80 to 1, and that nearly 90% of organizations have suffered an identity-centric breach {s('S1')} {badge('vendor')}. These are the company's statistics in a press release. I did not find the underlying study.</li>
    </ul>
  </section>

  <section class="nsec" id="gaps" aria-labelledby="gp-h">
    <h2 id="gp-h">What I think the market still misses</h2>
    {gaps}
  </section>

  <section class="nsec" id="notread" aria-labelledby="nr-h">
    <h2 id="nr-h">What I did not check</h2>
    <ul>{''.join(f'<li>{E(x)}</li>' for x in notread)}</ul>
  </section>

  <section class="nsec" id="sources" aria-labelledby="sr-h">
    <h2 id="sr-h">Sources</h2>
    {srctab}
    <p>I plan to re-check this page every quarter. See the <a href="/nhi-lab/roadmap/">roadmap</a>. If something here is wrong, <a href="/#contact">tell me</a> and I will fix it and note the change.</p>
  </section>
</main>'''
    desc = 'Four identity and NHI acquisitions closed in 2026, Microsoft documented agent identity objects, and NIST opened a project. Each fact is dated, sourced and labelled by how far I trust it.'
    write('nhi-lab/market/index.html', shell('nhi-lab/market/', 'Non-human identity market, 2026', desc,
          'Four deals, one new identity type and a standards project', body, ld=ld_article('Non-human identity market, 2026', desc, 'nhi-lab/market/')))

if __name__ == '__main__':
    build()
