import re, json, html, os
SITE="/home/claude/work/site"; OUT="/home/claude/work/out"
tpl=open(SITE+"/ca-mfa-lab/run-4/index.html",encoding="utf-8").read()
HEAD=tpl[:tpl.index("<main")]
FOOT=tpl[tpl.index("</main>")+len("</main>"):]
CSS='  <link rel="stylesheet" href="/assets/ca-fw.css?v=20261114a">\n'
def head(title,desc,path,headline):
    h=HEAD
    url="https://roshantrivedi.co.in"+path
    h=re.sub(r'<meta name="description" content="[^"]*" />','<meta name="description" content="%s" />'%html.escape(desc,quote=True),h)
    h=re.sub(r'<link rel="canonical" href="[^"]*" />','<link rel="canonical" href="%s" />'%url,h)
    h=re.sub(r'<meta property="og:title" content="[^"]*" />','<meta property="og:title" content="%s" />'%html.escape(headline,quote=True),h)
    h=re.sub(r'<meta property="og:description" content="[^"]*" />','<meta property="og:description" content="%s" />'%html.escape(desc,quote=True),h)
    h=re.sub(r'<meta property="og:url" content="[^"]*" />','<meta property="og:url" content="%s" />'%url,h)
    h=re.sub(r'<title>[^<]*</title>','<title>%s &middot; Roshan Trivedi</title>'%html.escape(title),h)
    ld={"@context":"https://schema.org","@type":"TechArticle","headline":headline,"description":desc,"url":url,"datePublished":"2026-11-14","dateModified":"2026-11-14","author":{"@type":"Person","name":"Roshan Trivedi","url":"https://roshantrivedi.co.in/"},"license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True}
    h=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps(ld)+'</script>',h,flags=re.S)
    assert h.count("</head>")==1
    return h.replace("</head>",CSS+"</head>")
def nsub(cur):
    items=[("/ca-mfa-lab/","Overview"),("/ca-mfa-lab/framework/","Framework"),("/ca-mfa-lab/virtual-lab/","Virtual lab"),("/ca-mfa-lab/register/","Register"),("/ca-mfa-lab/run-4/","Run 4"),("/ca-mfa-lab/sources/","Sources and events"),("/nhi-lab/method/","How the method works"),("/nhi-lab/","NHI lab")]
    return '<nav class="nsub" aria-label="Conditional access, MFA and AI agent lab sections">'+"".join('<a href="%s"%s>%s</a>'%(u,' aria-current="page"' if u==cur else "",t) for u,t in items)+'</nav>'
def page(path,title,desc,headline,body,scripts):
    return head(title,desc,path,headline)+'<main id="main" class="nhi fw">\n  '+nsub(path)+"\n"+body+"\n</main>"+FOOT.replace('  <script defer src="/assets/chatbot-widget.js',scripts+'  <script defer src="/assets/chatbot-widget.js',1)

# ---------------- Framework
fw_body='''  <header class="nhero"><p class="eyebrow">Lab</p><h1>The conditional access and MFA framework, animated</h1>
  <p class="dek">Fifteen attack patterns you can play step by step, with the control and without it. Below them, every one of the 130 cases in the lab with the output my scripts produced, exactly as saved.</p>
  <ul class="nmeta"><li>Last reviewed 14 November 2026</li><li>130 cases, 124 run on models</li><li>15 animated flows</li><li>7-link framework</li><li><a href="/ca-mfa-lab/ca-mfa-lab-book.pdf">Download the book (PDF)</a></li><li>Made-up data only</li></ul></header>

  <section class="nsec" id="read" aria-labelledby="rd-h">
    <h2 id="rd-h">How to read this page</h2>
    <p class="lede">Each case asks one question: does a bad outcome happen? <b>in</b> means it happens. <b>out</b> means it does not. I switch the controls on and off and write down what comes out.</p>
    <p>The animated flows are teaching sketches. They show the order of events and where one control stops the attack. The list at the bottom is the evidence: the numbers come straight from the files my scripts wrote. Models are small rule simulations I wrote. They show whether a rule as written lets a case through. They do not show how any vendor product behaves.</p>
    <div class="ntiles">
      <div class="ntile good"><b>130</b><span>cases in the register, in 18 groups</span></div>
      <div class="ntile good"><b>124</b><span>run: Run 1 (41), Run 2 (45), Run 3 (16), Run 5 (12), Run 6 (10)</span></div>
      <div class="ntile warn"><b>6</b><span>guesses wrong, all of them in Run 2</span></div>
      <div class="ntile warn"><b>6</b><span>not run: they need a real tenant, a hardware key, a real agent product or a person</span></div>
    </div>
  </section>

  <section class="nsec" id="flows" aria-labelledby="fl-h">
    <h2 id="fl-h">Play a pattern</h2>
    <p class="lede">Pick a flow. Press Play, or step through it. Switch between <b>without the control</b> and <b>with the control</b> to see where the attack stops. Every flow also has a plain text version.</p>
    <div id="flows-root"></div>
    <noscript><p class="note">The animated flows need JavaScript. The full list of cases further down is also built with JavaScript. The raw result files are linked at the end of this page.</p></noscript>
  </section>

%%CHAIN%%
  <section class="nsec" id="known" aria-labelledby="kn-h">
    <h2 id="kn-h">Well known, and less talked about</h2>
    <div class="ngrid">
      <div class="ncard"><h3>What most teams already know</h3><p>Phishing that relays a code, push approvals a tired user taps, replayed sign-in assertions, and help desk resets. Each has a clear fix in the models: a phishing-resistant method, number matching, one-time assertion IDs, a callback.</p></div>
      <div class="ncard"><h3>What gets less attention</h3><p>An app that no rule ever covered. A token that never signs in, so MFA has nothing to check. A cloud trust policy that accepts any repository. A privileged call that never asks for fresh MFA. A client that trusts the sign-in server its own server names.</p></div>
      <div class="ncard"><h3>Where MFA is not the deciding control</h3><p>In Run 5, the stolen integration token (W06) is decided by where the token can be used from. The privileged API call (W08) is decided by whether the check applies to every credential type, keys and service tokens included. Password reset (W07) is decided by whether it revokes refresh tokens.</p></div>
      <div class="ncard"><h3>What changes with AI agents</h3><p>In Run 6, a sub-agent writing beyond the human&rsquo;s rights (G03) is stopped only when the resource checks the human&rsquo;s own permissions. An agent that outlives its project (G04) keeps working through credential rotation. An agent whose owner leaves (G05) is flagged but not removed. A cookie stolen after MFA (G07) gets past network checks if the attacker looks local.</p></div>
    </div>
  </section>

  <section class="nsec" id="cases" aria-labelledby="cs-h">
    <h2 id="cs-h">Every case, with the output as produced</h2>
    <p class="lede">Open any case to see the bad outcome, the controls, the script output and my guess side by side. Cells where my guess was wrong are outlined.</p>
    <div id="cases-root"></div>
  </section>

  <section class="nsec" id="files" aria-labelledby="fi-h">
    <h2 id="fi-h">The raw files</h2>
    <ul>
      <li>Results: <a href="/ca-mfa-lab/evidence/results-run1.json">run 1</a>, <a href="/ca-mfa-lab/evidence/results-run2.json">run 2</a>, <a href="/ca-mfa-lab/evidence/results-run3.json">run 3</a>, <a href="/ca-mfa-lab/evidence/results-run5.json">run 5</a></li>
      <li>Written results: <a href="/ca-mfa-lab/evidence/RESULTS-run1.md">run 1</a>, <a href="/ca-mfa-lab/evidence/RESULTS-run2.md">run 2</a>, <a href="/ca-mfa-lab/evidence/RESULTS-run3.md">run 3</a>, <a href="/ca-mfa-lab/evidence/RESULTS-run5.md">run 5</a></li>
      <li>Locked guesses: <a href="/ca-mfa-lab/evidence/guesses/guesses-run1.md">run 1</a>, <a href="/ca-mfa-lab/evidence/guesses/guesses-run2.md">run 2</a>, <a href="/ca-mfa-lab/evidence/guesses/guesses-run3.md">run 3</a>, <a href="/ca-mfa-lab/evidence/guesses/guesses-run4.md">run 4</a>, <a href="/ca-mfa-lab/evidence/guesses/guesses-run5.md">run 5</a></li>
      <li>Scripts: <a href="/ca-mfa-lab/evidence/run1.py">run1.py</a>, <a href="/ca-mfa-lab/evidence/run2.py">run2.py</a>, <a href="/ca-mfa-lab/evidence/run3.py">run3.py</a>, <a href="/ca-mfa-lab/evidence/run5.py">run5.py</a>, <a href="/ca-mfa-lab/evidence/run6.py">run6.py</a></li>
      <li>Catalogue: <a href="/ca-mfa-lab/ca-mfa-catalogue-v1.7.csv">v1.7 (130 rows)</a></li>
    </ul>
  </section>

  <section class="nsec" id="limits" aria-labelledby="li-h">
    <h2 id="li-h">What this does not show</h2>
    <ul>
      <li>The models are mine. I wrote them after the guesses, so a match shows my reasoning agrees with itself. Run 2 is the only run that caught me out.</li>
      <li>Nothing here says how Okta, Entra, Ping or any other product behaves. It says whether a rule, as written, lets a case through.</li>
      <li>The flows simplify. Real sign-ins have more steps than five arrows.</li>
      <li>The three hand tests (E01 to E03) are not run. See <a href="/ca-mfa-lab/run-4/">Run 4</a>.</li>
    </ul>
  </section>'''
import json as _j, re as _re, sys as _sys
_sys.path.insert(0,"/home/claude/work/fw"); import stages as _st
_txt=open(OUT+"/ca-mfa-lab/data/cases.js",encoding="utf-8").read()
_cases=_j.loads(_re.search(r"window.CA_CASES=(\[.*?\]);\n",_txt,_re.S).group(1))
_cols=["#a78bfa","#4de2ff","#60a5fa","#f59e0b","#34d399","#f472b6","#f87171"]
_cards=""
for _i,(_k,_n,_q,_c,_ids) in enumerate(_st.STAGES):
    _cs=[x for x in _cases if x["stage"]==_k]; _run=[x for x in _cs if x.get("res")]
    _single=[x for x in _run if (len(x["res"])==5 and "in" in x["res"][2:]) or (len(x["res"])==3 and x["res"][1]=="out" and x["res"][2]=="in")]
    _wrong=[x for x in _run if x.get("match") is False]
    _cards+='<a class="link" style="--c:%s" href="#stage=%s"><b>%s</b><p class="q">%s</p><p class="n">%d cases, %d run. One control off lets it in: %d. Wrong guesses: %d.</p><p class="n">Controls that decide it: %s.</p></a>'%(_cols[_i],_k,_n,_q,len(_cs),len(_run),len(_single),len(_wrong),_c)
CHAIN='''  <section class="nsec" id="chain" aria-labelledby="ch-h">
    <h2 id="ch-h">The access chain: seven links</h2>
    <p class="lede">This is the framework the lab is built on. Every sign-in, and every action an agent takes for a person, passes through seven links. A case belongs to the link where its control sits. A weak link anywhere lets the bad outcome through, however strong MFA is at link 2.</p>
    <div class="chain">'''+_cards+'''</div>
    <p class="fnote">Pick a link to filter the case list below. Each case can be played one column at a time, with its controls switching on and off.</p>
  </section>'''
fw_body=fw_body.replace("%%CHAIN%%",CHAIN)
open(OUT+"/ca-mfa-lab/framework/index.html","w",encoding="utf-8").write(page("/ca-mfa-lab/framework/","Conditional access and MFA framework","15 animated attack patterns and all 130 conditional access and MFA cases with the output my scripts produced. Made-up data only.","The conditional access and MFA framework, animated",fw_body,'  <script src="/ca-mfa-lab/data/cases.js?v=20261114a"></script>\n  <script defer src="/assets/ca-fw.js?v=20261114a"></script>\n'))

# ---------------- Virtual lab
sens=json.load(open("/home/claude/ca-mfa-lab/evidence/results-run5.json"))["sensitivity"]
rows="".join("<tr><td>%s</td><td>%s</td></tr>"%(html.escape(s["change"]),html.escape(", ".join(f["id"] for f in s["flips"]) or "No case changes")) for s in sens)
vl_body='''  <header class="nhero"><p class="eyebrow">Lab</p><h1>The virtual lab</h1>
  <p class="dek">Pick any case. Read the guess I locked before running anything. Switch the controls. See the output my script produced. Then run the same script on your own computer.</p>
  <ul class="nmeta"><li>Last reviewed 14 November 2026</li><li>124 cases replayed</li><li>Python 3, no packages</li><li>Made-up data only</li></ul></header>

  <section class="nsec" id="how" aria-labelledby="hw-h">
    <h2 id="hw-h">What this is, and is not</h2>
    <p class="lede">This page replays saved output. Nothing is simulated in your browser. The numbers below are the ones my scripts wrote to their result files on 14 November 2026.</p>
    <p>If you want to see a script run, the second half of this page has the steps for your own computer. It takes a few minutes.</p>
  </section>

  <section class="nsec" id="replay" aria-labelledby="rp-h">
    <h2 id="rp-h">Replay a case</h2>
    <div class="vlab" id="vlab-root"></div>
    <noscript><p class="note">The replay needs JavaScript. The raw result files are linked on the <a href="/ca-mfa-lab/framework/#files">framework page</a>.</p></noscript>
  </section>

  <section class="nsec steps" id="local" aria-labelledby="lo-h">
    <h2 id="lo-h">Run it yourself</h2>
    <p class="lede"><b>Fastest way:</b> <a href="/ca-mfa-lab/virtual-lab/run/">run the scripts in your browser</a>. Nothing to install. Or follow the steps below to run them on your own computer.</p>
    <p class="fnote"><b>Reproduced on a second machine.</b> On 14 November 2026 I reran all five scripts on my own Mac (macOS, x86_64, Python 3.9.6). Every results file came out byte for byte identical to the one published here: the log has 119 lines that end in OK and 5 that end in MISMATCH; those five are the Run 2 cases where my guess was wrong. The sixth wrong guess, Z21, is in a pair test that the per-case line does not show.</p>
    <p class="lede">Run 6, on AI agent identity, is the newest. It uses only Python 3&rsquo;s standard library. The other runs work the same way.</p>
    <ol>
      <li><b>Check Python.</b> <code>python3 --version</code> should print a version that starts with 3.</li>
      <li><b>Make a folder and download two files.</b>
<pre class="term">mkdir ca-lab &amp;&amp; cd ca-lab
curl -O https://roshantrivedi.co.in/ca-mfa-lab/evidence/run6.py
curl -O https://roshantrivedi.co.in/ca-mfa-lab/evidence/guesses/guesses-run6.md</pre></li>
      <li><b>Check that the guesses are the locked ones.</b>
<pre class="term">shasum -a 256 guesses-run6.md</pre>
        It should print <code>1abdbf110b58375570d3472f3aefc697b41931f236a53001c1f9d836f01ec22f</code>. The script checks this itself and refuses to run if the file differs.</li>
      <li><b>Run it.</b>
<pre class="term">python3 -I run6.py guesses-run6.md</pre>
        You should see 10 lines that end in OK, two summary lines, and seven lines that start with SENS. It writes <code>results-run6.json</code> next to the script.</li>
      <li><b>Break an assumption.</b> Open <code>run6.py</code> and find <code>PARAMS</code> near the top. Change <code>attacker_same_network</code> from False to True and run again. G07 changes: watching the network no longer catches the attacker, and only the device binding holds. Because the script checks the guess file&rsquo;s hash, the guesses cannot be quietly changed to match.</li>
      <li><b>Try the older runs.</b> They live in the same <a href="https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/tree/main/ca-mfa-lab/evidence">evidence folder</a>. From inside that folder: <code>python3 run1.py</code>, <code>python3 run2.py guesses/guesses-run2.md</code>, <code>python3 run3.py guesses/guesses-run3.md</code>, <code>python3 run5.py guesses/guesses-run5.md</code>.</li>
      <li><b>Write your own guess first.</b> Pick a case, write what you expect for each switch, save it, hash it, and only then look at the output. That order is the whole method. <a href="/nhi-lab/method/">How the method works</a>.</li>
    </ol>
  </section>

  <section class="nsec" id="sens" aria-labelledby="se-h">
    <h2 id="se-h">What changes when one assumption changes (Run 5)</h2>
    <p class="lede">I changed one assumption at a time and re-ran all 12 cases. These are the only changes that flip any result.</p>
    <div class="twrap"><table class="srctable"><thead><tr><th>Assumption changed</th><th>Cases that change</th></tr></thead><tbody>'''+rows+'''</tbody></table></div>
    <p class="fnote">The 30 percent, the 2 minutes and the 1 hour are numbers I chose. They are written at the top of the script so you can change them.</p>
  </section>

  <section class="nsec" id="hand" aria-labelledby="ha-h">
    <h2 id="ha-h">Tests you can only do by hand</h2>
    <p>Three cases need a real tenant, a hardware key or a person: sign-in logs and a report-only policy, a lost hardware key, and a help desk call. They are on the <a href="/ca-mfa-lab/run-4/">Run 4 page</a> with setup and safety notes. If you run one, tell me what you saw.</p>
  </section>

  <section class="nsec" id="limits" aria-labelledby="li-h">
    <h2 id="li-h">Limits</h2>
    <ul>
      <li>The replay shows my models. Your product may behave differently.</li>
      <li>Run 1 stored three columns (no control, control on, control off alone). Runs 2, 3, 5 and 6 store five (none, all, off A, off B, off C).</li>
      <li>The assumption test was only run for Runs 5 and 6.</li>
    </ul>
  </section>'''
open(OUT+"/ca-mfa-lab/virtual-lab/index.html","w",encoding="utf-8").write(page("/ca-mfa-lab/virtual-lab/","The virtual lab","Replay any of 124 conditional access and MFA cases, switch controls on and off, then run the same Python script yourself.","The virtual lab",vl_body,'  <script src="/ca-mfa-lab/data/cases.js?v=20261114a"></script>\n  <script defer src="/assets/ca-vlab.js?v=20261114a"></script>\n'))

# ---------------- Sources and events
EVENTS=[
("6 Nov 2026","SonicWall SSLVPN: a user with valid credentials for another login method can bypass SAML, including SAML-enforced MFA (CVE-2026-19868). Applies only when SAML is on for VPN logins. SonicWall&rsquo;s advisory says it investigated a report indicating potential exploitation, and CISA added the flaw to its Known Exploited Vulnerabilities list the same day. Fixed in 7.3.4-7013 (Gen7) and 8.2.3-8015 (Gen8). Revision 1.1 on 9 November added a workaround: if SAML is in use and you cannot upgrade, disable or delete the active LDAP, RADIUS and TACACS+ servers.","W05","SonicWall advisory SNWLID-2026-0014, revision 1.1; CISA KEV entry",'<a href="https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2026-0014">SonicWall advisory</a>, <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-19868">CISA KEV</a>, <a href="https://securityweek.com/sonicwall-patches-exploited-sonicos-bug-that-weakens-vpn-logins">SecurityWeek</a>',"Confirmed against SonicWall&rsquo;s own page on 14 November. My earlier note said there was no workaround; that was true until revision 1.1. The page&rsquo;s revision table dates version 1.0 as 5 November, its header says 6 November."),
("28 Sep 2026","The official MCP Python SDK did not check the issuer on a fallback discovery path. A malicious MCP server could make an SDK-based client send its client secret, authorization code and PKCE verifier to an endpoint the server chose (GHSA-qx49-fqc8-xw99, CVSS 7.5). Fixed in 1.30.0 and 2.2.0. No attacks have been reported.","W11","Project security advisory, read through a Cloud Security Alliance note (30 Sep 2026) and The Hacker News",'<a href="https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-python-sdk-oauth-flaw-20260930-csa-sty/">CSA note</a>, <a href="https://thehackernews.com/2026/09/official-mcp-python-sdk-flaw-can-let.html">The Hacker News</a>',"Confirmed, with a qualifier: I did not open the GitHub advisory. MCP was created by Anthropic, whose Claude model helped me draft this lab."),
("24 Aug 2026","Okta made Agent SSO generally available. It registers AI agents as identities, issues short-lived tokens in place of stored credentials, and moves agent authorization to the identity provider using Cross App Access. The release does not say how revocation works.","G01 E04","Vendor press release",'<a href="https://www.okta.com/newsroom/press-releases/okta-brings-first-class-identity-to-ai-agents-with-agent-sso/">Okta newsroom</a>',"Confirmed as Okta&rsquo;s own announcement, read through a page summary on 14 November. Product claims are the vendor&rsquo;s."),
("15 Jul 2026","GitHub moves new repositories, and repositories that opt in, to an immutable subject claim in OIDC tokens. Cloud trust policies must include the numeric owner and repository IDs.","W01","Vendor documentation","<a href=\"https://docs.github.com/en/actions/reference/security/oidc\">GitHub Docs: OIDC reference</a>","Confirmed against GitHub&rsquo;s live docs on 14 November, through a page summary. Repositories created after the date use the new format by default, older ones can opt in, and renames and transfers after it also move. Not available on GitHub Enterprise Server."),
("Reported 17 Mar 2026","Researchers at NetSPI showed that certain nested app authentication flows could return Microsoft Graph tokens without Conditional Access being applied. They told Microsoft on 17 March, Microsoft rated it medium and deployed a fix, and a retest returned Conditional Access blocking errors. Other researchers presented further nested app paths at TROOPERS 2026.","Y06","Researcher write-up",'<a href="https://www.netspi.com/blog/technical-blog/cloud-pentesting/bypassing-microsoft-entra-conditional-access-policies-via-nested-app-authentication/">NetSPI blog</a>',"Partly confirmed: I read excerpts of the NetSPI post and a news write-up, not Microsoft&rsquo;s own statement. The fix covers the flows NetSPI named, not every nested app path."),
("27 Jan 2026","Microsoft revised the Exchange Online timeline for ending Basic authentication on SMTP AUTH (the path older printers and scanners use). It stays unchanged until December 2026, is then disabled by default for existing tenants and unavailable by default for new ones, and a final removal date is due in the second half of 2027. The earlier March to April 2026 dates were put on hold.","Z20","Vendor announcement (Exchange Team blog, updated 29 Jan)",'<a href="https://techcommunity.microsoft.com/blog/exchange/updated-exchange-online-smtp-auth-basic-authentication-deprecation-timeline/4489835">Exchange Team blog</a>',"Confirmed, through a page summary. Dates have moved before, so check Microsoft&rsquo;s page before you act."),
("22 Jan 2026","Okta Threat Intelligence described phishing kits built for phone callers. The caller steers what the user sees in step with their script, which defeats any MFA that is not phishing-resistant. Okta says number matching is not phishing-resistant by definition.","M01 M03 M04 Z01 W12","Vendor research by the identity provider; primary for what Okta observed",'<a href="https://www.okta.com/blog/threat-intelligence/phishing-kits-adapt-to-the-script-of-callers/">Okta blog</a>',"Confirmed as Okta&rsquo;s own finding. The full advisory is for Okta customers only."),
("1 Oct 2025","Microsoft began enforcing MFA for Azure resource management at the Azure Resource Manager layer (Phase 2), for CLI, PowerShell, SDKs and REST calls. Tenants could postpone to 1 July 2026. Workload identities such as managed identities and service principals are not covered.","Y01 Y02 W08","Vendor documentation and announcement",'<a href="https://learn.microsoft.com/entra/identity/authentication/concept-mandatory-multifactor-authentication">Microsoft Learn</a>, <a href="https://azure.microsoft.com/blog/azure-mandatory-multifactor-authentication-phase-2-starting-in-october-2025/">Azure blog</a>',"Confirmed. Enforcement is gradual by tenant, so your tenant may differ."),
("8 to 20 Aug 2025","Stolen OAuth and refresh tokens from the Salesloft Drift integration were used to read data from many customers&rsquo; Salesforce instances between 8 and 18 August. Salesloft and Salesforce revoked all Drift tokens on 20 August. Google later confirmed Drift Email tokens were also compromised.","W06 W07","Google Threat Intelligence Group report, 26 Aug 2025",'<a href="https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift">Google Cloud blog</a>',"Confirmed by the investigating team. My reading: tokens like these are used without a fresh sign-in, so MFA had nothing to check."),
("9 Jul 2025","mcp-remote, a tool that connects AI clients to remote MCP servers, ran operating system commands from a crafted authorization endpoint sent by a malicious server (CVE-2025-6514, CVSS 9.6). Fixed in 0.1.16.","W11","Researcher advisory and CVE record",'<a href="https://research.jfrog.com/vulnerabilities/mcp-remote-command-injection-rce-jfsa-2025-001290844/">JFrog advisory</a>',"Confirmed. A related lesson to W11, not the same flaw: the client trusted values the server supplied. W11 matches the Python SDK advisory above."),
("14 to 18 Mar 2025","The GitHub Action tj-actions/changed-files was compromised and leaked CI/CD secrets through workflow logs (CVE-2025-30066). CISA added it to its Known Exploited Vulnerabilities list.","W02 W03","Government alert",'<a href="https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066">CISA alert</a>',"Confirmed."),
("16 Nov 2023, updated 29 Jul 2025","CISA and the FBI described a group that phones IT help desks, poses as an employee and has the password reset and MFA moved to a device they control.","W12 E03","Government advisory AA23-320A",'<a href="https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-320a">CISA advisory</a>',"Confirmed."),
]
STDS=[
("RFC 9449: OAuth 2.0 Demonstrating Proof of Possession (DPoP), September 2023","W09 Y07","Standard","Binds a token to a key so a copied token fails from another machine. Does not help against code inside the client.",'<a href="https://www.rfc-editor.org/rfc/rfc9449">rfc-editor.org</a>'),
("MCP authorization specification, 2026-07-28 revision","W11 Y11 Y12","Specification","Clients use protected resource metadata to find the authorization server, and check the issuer value on the response. The check gives no protection if the expected issuer came from an unvalidated source.",'<a href="https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization">modelcontextprotocol.io</a>'),
("Cloud Security Alliance, Defining Non-Human Identity, 22 July 2026","G03 G04 G05 G10","Industry research","Names six risk areas for all non-human identities, including missing owners, missing decommissioning triggers and access that grows through delegation. For agents it advises a human sponsor for each agent, sub-agents with minimal short-lived access limited to the human&rsquo;s own permissions, and logs that record the delegator, the agent and the intent.",'<a href="https://cloudsecurityalliance.org/artifacts/defining-non-human-identity">cloudsecurityalliance.org</a>'),
("GitHub Docs: OpenID Connect reference","W01","Vendor documentation","At least one condition must be set on the cloud role so untrusted repositories cannot get tokens.",'<a href="https://docs.github.com/en/actions/reference/security/oidc">docs.github.com</a>'),
]
ev_rows="".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s<br><small>%s</small></td><td>%s</td></tr>"%(d,t,c,s,l,v) for d,t,c,s,l,v in EVENTS)
sd_rows="".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(a,b,c,d,e) for a,b,c,d,e in STDS)
src_body='''  <header class="nhero"><p class="eyebrow">Lab</p><h1>Sources and recent events</h1>
  <p class="dek">What happened to real companies and products, which lab case each event relates to, and how far I trust each source. Checked on 14 November 2026.</p>
  <ul class="nmeta"><li>Last reviewed 14 November 2026</li><li>12 dated events</li><li>4 standards and specifications</li><li>Each one labelled</li></ul></header>

  <section class="nsec" id="how" aria-labelledby="hw-h">
    <h2 id="hw-h">How to use this page</h2>
    <p class="lede">The lab runs on made-up data. These events are why the cases exist. Each row says what was reported, who reported it, and how well I could confirm it.</p>
    <p>I name an event only when I read a primary or near-primary source for it: a vendor advisory, a government alert, a standard, or the investigating team&rsquo;s own report. News coverage is labelled as news. Where I read a report quoting a vendor page but not the page itself, I say so. Company names appear because the sources name them, and a name here is not a finding about that company&rsquo;s controls.</p>
  </section>

  <section class="nsec" id="events" aria-labelledby="ev-h">
    <h2 id="ev-h">Recent events, newest first</h2>
    <div class="twrap"><table class="srctable"><thead><tr><th>Date</th><th>What was reported</th><th>Lab case</th><th>Source</th><th>How far I trust it</th></tr></thead><tbody>'''+ev_rows+'''</tbody></table></div>
  </section>

  <section class="nsec" id="standards" aria-labelledby="sd-h">
    <h2 id="sd-h">Standards and documentation I used</h2>
    <div class="twrap"><table class="srctable"><thead><tr><th>Document</th><th>Lab case</th><th>Kind</th><th>What it says that matters here</th><th>Link</th></tr></thead><tbody>'''+sd_rows+'''</tbody></table></div>
    <p>The catalogue&rsquo;s own source column, with the result of my 14 November source check for 57 rows, is on the <a href="/ca-mfa-lab/register/">register page</a>.</p>
  </section>

  <section class="nsec" id="left" aria-labelledby="lf-h">
    <h2 id="lf-h">What I left out, and why</h2>
    <ul>
      <li>Claims that a hacking group stole data from named companies through Okta sign-ins. They rest on the group&rsquo;s own statements or one blog, and the companies did not confirm them.</li>
      <li>A report of one company&rsquo;s breach through single sign-on followed by its CRM, from a single blog.</li>
      <li>Several 2026 reports of CI/CD and MCP package compromises that I could find in one blog each. I will add them when I can read the maintainers&rsquo; own notice.</li>
      <li>Anything about the internal workings of a product I have not read the vendor&rsquo;s documentation for.</li>
    </ul>
  </section>

  <section class="nsec" id="limits" aria-labelledby="li-h">
    <h2 id="li-h">Limits</h2>
    <ul>
      <li>Dates and fixed versions change. Check the source before you act on any row.</li>
      <li>I used search results and excerpts for several rows and opened few pages in full. The &ldquo;how far I trust it&rdquo; column says which.</li>
      <li>This is not legal advice, and it is not a vulnerability scanner. If you run a SonicWall device with SAML on, read the vendor advisory and patch.</li>
    </ul>
  </section>'''
open(OUT+"/ca-mfa-lab/sources/index.html","w",encoding="utf-8").write(page("/ca-mfa-lab/sources/","Sources and recent events","Dated real-world events behind the conditional access, MFA and AI agent lab, each linked to a lab case and labelled for how far the source can be trusted.","Sources and recent events",src_body,""))
print("pages written")

# ---------------- Run in the browser
rn_body='''  <header class="nhero"><p class="eyebrow">Lab</p><h1>Run the lab in your browser</h1>
  <p class="dek">The same Python scripts that produced every result in this lab, running on this page. Change an assumption, run again, and see which cases change. Nothing is installed and nothing leaves your browser.</p>
  <ul class="nmeta"><li>Real scripts, unchanged</li><li>Python runs on your device</li><li>Made-up data only</li></ul></header>

  <section class="nsec" id="how" aria-labelledby="rh-h">
    <h2 id="rh-h">How it works</h2>
    <p class="lede">The page loads Python (Pyodide, about 13 MB the first time) from this website, then runs the script you pick from the <a href="https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/tree/main/ca-mfa-lab/evidence">evidence folder</a> exactly as published. Runs 5 and 6 check the guess file&rsquo;s SHA-256 before they start, so if you edit a guess they refuse to run. That refusal is the point of locking guesses before any code.</p>
    <ol>
      <li>Pick a run and press <b>Run</b>. You should see one line per case ending in OK, or MISMATCH where my guess was wrong.</li>
      <li>Under the output, the page compares your results file with the published one.</li>
      <li>Find <code>PARAMS</code> near the top of Run 5 or Run 6, change one value, and run again. Run 6&rsquo;s <code>attacker_same_network</code> is a good one to try.</li>
      <li>Change one word in the guess file and run again. The script stops and says the hash does not match.</li>
    </ol>
  </section>

  <section class="nsec" id="runner" aria-labelledby="rr-h">
    <h2 id="rr-h">Run a script</h2>
    <div class="vlab">
      <div class="filters"><label>Run<select id="rn-run" aria-label="Choose a run"></select></label></div>
      <div class="swbtns"><button type="button" class="fbtn" id="rn-go">Run</button><button type="button" class="fbtn" id="rn-reset">Reset to the published files</button></div>
      <p class="fnote" id="rn-status" aria-live="polite">Loading.</p>
      <h3>Output</h3>
      <pre class="term" id="rn-out" aria-live="polite" tabindex="0"></pre>
      <p class="fnote" id="rn-cmp" aria-live="polite"></p>
      <details><summary>The script (you can edit it)</summary><label class="rnlab" for="rn-script">Script</label><textarea id="rn-script" class="rnta" rows="20" spellcheck="false"></textarea></details>
      <div id="rn-guess-wrap"><details><summary>The locked guess file (edit it to see the hash check stop the run)</summary><label class="rnlab" for="rn-guess">Guess file</label><textarea id="rn-guess" class="rnta" rows="14" spellcheck="false"></textarea><p class="fnote" id="rn-hash"></p></details></div>
    </div>
  </section>

  <section class="nsec" id="limits" aria-labelledby="rl-h">
    <h2 id="rl-h">Limits</h2>
    <ul>
      <li>These are models of rule logic on made-up data. They do not test any vendor&rsquo;s product.</li>
      <li>Your edits stay in your browser and disappear when you reload.</li>
      <li>To test a real product, use the <a href="/ca-mfa-lab/run-4/">hand tests</a> in a throwaway tenant and report anything different with the exception form.</li>
    </ul>
  </section>'''
_rn=page("/ca-mfa-lab/virtual-lab/run/","Run the lab in your browser","Run the conditional access, MFA and AI agent lab's own Python scripts in your browser, change an assumption and see which cases change.","Run the lab in your browser",rn_body,'  <script src="/assets/pyodide/pyodide.js"></script>\n  <script defer src="/assets/ca-run.js?v=20261114a"></script>\n')
_a="script-src 'self' https://static.cloudflareinsights.com;"
assert _rn.count(_a)==1
_rn=_rn.replace(_a,"script-src 'self' 'wasm-unsafe-eval' https://static.cloudflareinsights.com;")
os.makedirs(OUT+"/ca-mfa-lab/virtual-lab/run",exist_ok=True)
open(OUT+"/ca-mfa-lab/virtual-lab/run/index.html","w",encoding="utf-8").write(_rn)
print("run page written")

