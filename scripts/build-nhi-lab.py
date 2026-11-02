#!/usr/bin/env python3
"""Builds nhi-lab/index.html from nhi-lab/evidence/results.json.
Run from the repo root: python3 scripts/build-nhi-lab.py"""
import json, html, textwrap
R = json.load(open('nhi-lab/evidence/results.json'))['rows']
E = html.escape

# id: (group, short trigger, without, with)
T = {
'N-R14-01': ('discover','Three places hold service accounts','Directory-only scan finds 12 of 27','All three sources merged: 27 of 27, each with its source'),
'N-R14-03': ('control','Another job reads a 400-day-old CI key','The other job reads it. Log says only "pipeline"','Per-job credential: refused, log names the job'),
'N-R14-04': ('credential','A certificate with no owner expires','No warning, outage, someone switches a check off','Owner warned at 30 and 7 days, no outage'),
'N-R14-05': ('credential','Vendor tokens stolen; grant is 14 months old','Replayed token still reads mail','Grant had expired at 90 days: refused'),
'N-R14-09': ('own','A key with no named owner','Still active on day 31','Paused on day 31'),
'N-R14-11': ('own','App retired, its identities stay','All 3 still work 90 days later','All 3 disabled, ticket recorded'),
'N-R14-14': ('credential','Rotation job fails for 60 days','Nobody knows; password 60 days stale','Alert on day 1, score rises weekly'),
'N-R14-15': ('credential','Password rotated before the app is updated','The application fails at next connection','Consumer first, then rotate, old secret verified dead'),
'N-R14-17': ('control','Low-value workload asks for a high-value role','Gets the role','Trust bound to one workload: refused'),
'N-R14-18': ('control','New service account, no owner, scope or expiry','Created and active','Refused, with the reason'),
'P-R15-02': ('privileged','Engineer needs 2 hours on one database','Access stays after the work','Closes by itself, credential rotated'),
'P-R15-03': ('privileged','The job needs 90 more minutes','Extended again and again: 10 hours','One extension, then a person must approve'),
'P-R15-05': ('privileged','Admin group of 40, 8 did privileged work','All 40 keep access','32 removed, 8 remain'),
'P-R15-07': ('privileged','Engineer signs in directly with an old password','Login works, nothing recorded','Blocked at the network'),
'P-R15-08': ('privileged','Nine of ten targets are recorded','Nobody knows about the tenth','Tenth found and blocked'),
'P-R15-09': ('privileged','Change to the identity system, one approver','Runs','Waits for a second, different person'),
'P-R15-11': ('privileged','Break-glass account used at 2 a.m.','Unnoticed, password unchanged','Alert fires, password rotated'),
'P-R15-13': ('privileged','Break-glass used for routine work, 4 days','No one notices','2 uses with no ticket flagged'),
'P-R15-17': ('privileged','Vendor engineer connects for 4 hours','No record, access stays','Recorded and closed at 4 hours'),
'P-R15-18': ('privileged','Vendor person leaves their company','Account still active at 120 days','Disabled at the next 30-day review'),
'S-R17-01': ('shadow','Employee grants an AI tool access, then leaves','Grant keeps working','Found and revoked; ownerless grants refused'),
'S-R17-03': ('shadow','An automation uses a person\'s login','Log cannot tell human from agent','Agent has its own identity and log tag'),
'S-R17-04': ('shadow','AI workflow makes a key with no owner','Key stays valid forever','Refused at creation; sweep disables expired keys'),
'S-R17-05': ('shadow','AI-written code and MCP config hold secrets','All 8 fake secrets reach the repository','6 of 8 blocked; 2 get through'),
'N-R14-23': ('gap','Vendor breached; refresh token still valid','Grant accepted, replay reads files','Allowlist refuses the grant; revoke ends replays after 60 minutes'),
'N-R14-24': ('gap','Secrets in environment variables not marked sensitive','2 secrets readable in plain text','3 of 4 hidden; 1 odd one missed'),
'N-R14-25': ('gap','Token copied from a CI runner, replayed','Both replays work','Both replays refused'),
}
GROUPS = {
 'discover':('Discover','#4de2ff'),'own':('Own and retire','#7df2d0'),'credential':('Credentials','#c4b5fd'),
 'control':('Front door and trust','#f7c873'),'privileged':('Privileged access','#ff8fa3'),
 'shadow':('Shadow AI','#8b5cf6'),'gap':('Gap cases from 2026 incidents','#34d399')}


T2 = {
'N-R14-07': ('discover','One account, three names','43 entries for 30 identities, findings split','Merged on owner plus name: 29, one wrong merge'),
'N-R14-19': ('credential','Two identities, same age score','Tie, the test tool can be fixed first','Reach in the score: production ranks first'),
'N-R14-20': ('credential','Rotation ticket, old secret still accepted','All 5 close, 2 old secrets live','3 close, 2 stay open until the old secret is dead'),
'N-R14-21': ('own','4 agents share one team key','Log says "team key", revoke hits all 4','One key per agent: log names it, revoke hits 1'),
'N-R14-22': ('control','Engineer signs in as a service account','Logged under the account, nobody accountable','Direct sign-in refused, checkout names the person'),
'P-R15-10': ('privileged','Push fatigue and SIM-swap against admins','6 bad sign-ins get through','Passkey, no SMS fallback: 0 get through'),
'P-R15-15': ('privileged','Vault backup on a weaker share','5 non-backup reads succeed','Same rules and an alert: 5 refused, 5 alerts'),
'P-R15-16': ('privileged','Attacker calls the help desk for a reset','Both attacker resets succeed','Proof, or notice with a delay: both stopped'),
'P-R15-19': ('privileged','Vendor needed at 2 a.m.','Shared password, stays on, no record','Approved, recorded, closes at 2 hours'),
'P-R15-25': ('privileged','Rotate 200 secrets after a breach','12 outages','Consumers first and a dry run: 0 outages, 2 left unrotated'),
'S-R17-02': ('shadow','AI tool needs one folder, inherits 40','Can write to all 40','Read on one folder, 0 writable'),
'S-R17-06': ('shadow','AI-service keys in 6 repositories','All 6 stay valid','5 revoked on find, 1 odd prefix missed'),
'S-R17-10': ('shadow','5 automations outlive a test','All 5 still run','4 disabled, 1 extended on any written reason'),
'C-R16-C01': ('chain','No owner, password in a ticket, export shared','Attacker signs in from a new network','Stopped at link 1; for an old account the ticket scan stops it at link 2'),
'C-R16-C02': ('chain','Token committed, repo cloned, found 7 days later','Attacker calls the cloud API','Commit block stops at link 1; a 1-day token alone also stops it'),
'C-R16-C04': ('chain','Contractor with no end date','Phished credential gives production access','Expiry stops at link 3; sponsor review alone does not at 30 days'),
'C-R16-C05': ('chain','Break-glass password pasted in chat','Reused with no emergency, unnoticed','Rotate on return stops it; the alert only reports it'),
'C-R16-C06': ('chain','Many approvals, one hostile among them','The hostile change is approved','A second approver stops it; showing the risk only flags it'),
'C-R16-C17': ('chain','Vault in place, direct login still works','Vault and recording bypassed','Blocking direct login stops it; the alert only reports it'),
}
GROUPS['chain'] = ('Chain tests', '#fbbf24')

def wrap(s, n):
    return textwrap.wrap(s, n) or ['']
def tspans(lines, x, y, dy=15):
    return ''.join(f'<tspan x="{x}" y="{y + i*dy}">{E(l)}</tspan>' for i, l in enumerate(lines))

def case_svg(cid, trig, wo, wi, color):
    # Left: trigger. Top lane (red): without control. Bottom lane (green): with control, passes a shield.
    return f'''<svg class="nflow" viewBox="0 0 700 170" role="img" aria-label="{E(cid)}: {E(trig)}. Without the control: {E(wo)}. With the control: {E(wi)}.">
<rect x="4" y="40" width="160" height="90" rx="10" class="nd" style="stroke:{color}"/><text class="tx" x="84" y="66" text-anchor="middle">{tspans(wrap(trig,17)[:4],84,66,15)}</text>
<path class="ln bad" d="M 164 85 L 190 42 L 360 42"/><path class="ln good" d="M 164 85 L 190 128 L 360 128"/>
<rect x="225" y="108" width="84" height="40" rx="8" class="shield"/><text class="tx sm" x="267" y="133" text-anchor="middle">control</text>
<circle class="ndot bad" r="6" style="offset-path:path('M 164 85 L 190 42 L 360 42')"/>
<circle class="ndot good" r="6" style="offset-path:path('M 164 85 L 190 128 L 360 128')"/>
<rect x="364" y="8" width="332" height="68" rx="10" class="out bad"/><text class="tx" x="376" y="26"><tspan class="lbl" x="376" y="26">WITHOUT</tspan>{tspans(wrap(wo,36)[:2],376,46,17)}</text>
<rect x="364" y="94" width="332" height="68" rx="10" class="out good"/><text class="tx" x="376" y="112"><tspan class="lbl" x="376" y="112">WITH</tspan>{tspans(wrap(wi,36)[:2],376,132,17)}</text>
</svg>'''

def method_svg():
    steps = ['Write the guess','Hash it (SHA-256)','Commit it','Write the code','Run it, control on and off','Record every miss']
    out = ['<svg class="nflow wide" viewBox="0 0 900 130" role="img" aria-label="Method: write the guess, hash it, commit it, then write the code, run each case with the control on and off, and record every miss.">']
    for i, s in enumerate(steps):
        x = 8 + i*148
        out.append(f'<rect x="{x}" y="34" width="130" height="62" rx="12" class="nd" style="stroke:#4de2ff"/><text class="tx" x="{x+65}" y="60" text-anchor="middle">{tspans(wrap(s,16)[:3],x+65,60,14)}</text><text class="num" x="{x+10}" y="28">{i+1}</text>')
        if i < 5: out.append(f'<path class="ln" d="M {x+130} 65 L {x+148} 65"/>')
    out.append('<circle class="ndot good" r="6" style="offset-path:path(\'M 20 65 L 890 65\');animation-duration:9s"/></svg>')
    return ''.join(out)

def life_svg():
    st = [('Discover','Find every identity',4),('Own','A named person',2),('Credential','Rotate, expire, scope',7),('Control','Front door and trust',3),('Privileged','JIT, recording, break-glass',10),('Retire','Remove what is unused',1)]
    out = ['<svg class="nflow wide" viewBox="0 0 900 190" role="img" aria-label="The life of a non-human identity: discover, own, credential, control, privileged access, retire. A pulse travels along the loop.">']
    for i, (n, sub, c) in enumerate(st):
        x = 8 + i*148
        out.append(f'<rect x="{x}" y="50" width="130" height="86" rx="14" class="nd" style="stroke:#7df2d0"/><text class="tx b" x="{x+65}" y="80" text-anchor="middle">{n}</text><text class="tx sm" x="{x+65}" y="100" text-anchor="middle">{E(sub)}</text><text class="tx sm" x="{x+65}" y="122" text-anchor="middle">{c} cases</text>')
        if i < 5: out.append(f'<path class="ln" d="M {x+130} 93 L {x+148} 93"/>')
    out.append('<path class="ln dash" d="M 818 140 L 818 175 L 73 175 L 73 140"/><text class="tx sm" x="450" y="170" text-anchor="middle">retire feeds the next discovery scan</text>')
    out.append('<circle class="ndot good" r="7" style="offset-path:path(\'M 20 93 L 880 93\');animation-duration:12s"/></svg>')
    return ''.join(out)

rows = {r['id']: r for r in R}
cards = []
R2ROWS = {r['id']: r for r in json.load(open('nhi-lab/evidence/results-stretch.json'))['rows']}
for cid, (g, trig, wo, wi) in list(T.items()) + list(T2.items()):
    second = cid in T2
    r = R2ROWS[cid] if second else rows[cid]
    wrong = bool(r['mismatch_without'] or r['mismatch_with'])
    masked = [k for k, v in r['noticed'].items() if not v]
    tags = []
    tags.append('<span class="pill bad">guess wrong</span>' if wrong or (cid == 'N-R14-25') else '<span class="pill ok">guess matched</span>')
    if masked: tags.append('<span class="pill warn">control masked by another</span>')
    if second: tags.append('<span class="pill grp" style="--k:#94a3b8">second run</span>')
    cards.append(f'''<article class="case" data-g="{g}" id="{cid.lower()}"><header><h3>{cid} <span>{E(trig)}</span></h3><p class="ntags"><span class="pill grp" style="--k:{GROUPS[g][1]}">{GROUPS[g][0]}</span>{''.join(tags)}</p></header>{case_svg(cid, trig, wo, wi, GROUPS[g][1])}</article>''')

chips = '<button class="chip on" data-f="all" type="button">All 46</button>' + ''.join(
    f'<button class="chip" data-f="{k}" type="button">{v[0]}</button>' for k, v in GROUPS.items())

head = open('ai-governance-lab/index.html').read().split('<body')[0]
# reuse the site head (CSP, fonts, theme) and replace the page-specific parts
import re
head = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="27 non-human identity cases on made-up data. Guesses written and hashed before the code, every control switched off once. Animated workflows, a lab you can run in the browser, and what the market still misses." />', head)
head = re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="https://roshantrivedi.co.in/nhi-lab/" />', head)
head = re.sub(r'<meta property="og:title"[^>]*>', '<meta property="og:title" content="I tested 27 non-human identity cases. My guesses were wrong in two places." />', head)
head = re.sub(r'<meta property="og:description"[^>]*>', '<meta property="og:description" content="Service accounts, tokens, break-glass and shadow AI, tested on made-up data with the guesses committed first." />', head)
head = re.sub(r'<meta property="og:url"[^>]*>', '<meta property="og:url" content="https://roshantrivedi.co.in/nhi-lab/" />', head)
head = re.sub(r'<title>.*?</title>', '<title>Non-human identity lab &middot; Roshan Trivedi</title>', head)
head = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
ld = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Dataset","name":"Non-human identity lab: 27 cases","description":"27 non-human identity cases on made-up data, with guesses hashed before the code and control-off checks.","url":"https://roshantrivedi.co.in/nhi-lab/","creator":{"@type":"Person","name":"Roshan Trivedi","url":"https://roshantrivedi.co.in/"},"license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":true,"keywords":["non-human identity","service accounts","PAM","IAM","OAuth"]}</script>'
head = head.replace('</head>', '  <link rel="stylesheet" href="/assets/blinks.css?v=20261102b">\n  <link rel="stylesheet" href="/assets/nhi-lab.css?v=20261102b">\n  ' + ld + '\n</head>')
nav = re.search(r'<nav class="hg-sitenav".*?</nav>', open('ai-governance-lab/index.html').read(), re.S).group(0)
foot = re.search(r'<footer class="hg-foot">.*?</footer>', open('ai-governance-lab/index.html').read(), re.S).group(0)

body = open('scripts/nhi-lab-body.html').read()
R2 = json.load(open('nhi-lab/evidence/results-stretch.json'))['rows']
r2 = ''
for r in R2:
    wrong = bool(r['mismatch_without'] or r['mismatch_with'])
    nz = ', '.join(f"{k.replace('_',' ')}: " + ('yes' if v else 'NO') for k, v in r['noticed'].items())
    r2 += f"<tr><th scope=\"row\">{E(r['id'])} {E(r['title'])}</th><td>{'wrong' if wrong else 'matched'}</td><td>{E(nz)}</td></tr>"
body = body.replace('{{ROUND2}}', r2)
body = body.replace('{{CHIPS}}', chips).replace('{{CASES}}', '\n'.join(cards)).replace('{{METHOD}}', method_svg()).replace('{{LIFE}}', life_svg())
page = head + '  <body style="--c:#7df2d0">\n    <a class="skip" href="#main">Skip to content</a>\n    ' + nav + '\n' + body + '\n    ' + foot + '\n  <script src="/assets/nhi-lab.js?v=20261102a" defer></script>\n  </body>\n</html>\n'
open('nhi-lab/index.html', 'w').write(page)
print('wrote nhi-lab/index.html', len(page))
