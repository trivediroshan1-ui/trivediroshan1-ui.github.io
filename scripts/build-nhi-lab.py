#!/usr/bin/env python3
"""Builds nhi-lab/index.html from nhi-lab/evidence/results.json.
Run from the repo root: python3 scripts/build-nhi-lab.py"""
import json, html, textwrap, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
R = json.load(open('nhi-lab/evidence/results.json'))['rows']
E = html.escape

from nhi_data import T, T2, GROUPS


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
head = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="46 non-human identity cases on made-up data. Guesses written and hashed before the code, every control switched off once. A framework, a dated market view, downloadable audit data and animated workflows." />', head)
head = re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="https://roshantrivedi.co.in/nhi-lab/" />', head)
head = re.sub(r'<meta property="og:title"[^>]*>', '<meta property="og:title" content="I tested 46 non-human identity cases. My guesses were wrong in four places." />', head)
head = re.sub(r'<meta property="og:description"[^>]*>', '<meta property="og:description" content="Service accounts, tokens, break-glass and shadow AI, tested on made-up data with the guesses committed first." />', head)
head = re.sub(r'<meta property="og:url"[^>]*>', '<meta property="og:url" content="https://roshantrivedi.co.in/nhi-lab/" />', head)
head = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*(")', r'\g<1>https://roshantrivedi.co.in/assets/share/og-nhi-lab.png\g<2>', head)
head = re.sub(r'<title>.*?</title>', '<title>Non-human identity lab &middot; Roshan Trivedi</title>', head)
head = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
_dataset = {"@type":"Dataset","name":"Non-human identity lab: 46 cases","description":"46 non-human identity cases on made-up data, with guesses hashed before the code and control-off checks.","url":"https://roshantrivedi.co.in/nhi-lab/","creator":{"@type":"Person","name":"Roshan Trivedi","url":"https://roshantrivedi.co.in/"},"license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True,"keywords":["non-human identity","service accounts","PAM","IAM","OAuth"]}
_video = {"@type":"VideoObject","name":"Non-human identity lab in 60 seconds","description":"A silent, captioned 60 second video: how the lab runs, how it is built, and what the data says across 46 cases.","thumbnailUrl":"https://roshantrivedi.co.in/assets/share/nhi-lab-motion-poster.jpg","uploadDate":"2026-11-02","duration":"PT1M","contentUrl":"https://roshantrivedi.co.in/assets/share/nhi-lab-motion.mp4","embedUrl":"https://roshantrivedi.co.in/nhi-lab/","isAccessibleForFree":True,"author":{"@type":"Person","name":"Roshan Trivedi","url":"https://roshantrivedi.co.in/"}}
ld = '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@graph":[_dataset,_video]}, separators=(',',':'), ensure_ascii=False) + '</script>'
head = head.replace('</head>', '  <link rel="stylesheet" href="/assets/blinks.css?v=20261102d">\n  <link rel="stylesheet" href="/assets/nhi-lab.css?v=20261102d">\n  <link rel="stylesheet" href="/assets/nhi-site.css?v=20261102d">\n  ' + ld + '\n</head>')
nav = re.search(r'<nav class="hg-sitenav".*?</nav>', open('ai-governance-lab/index.html').read(), re.S).group(0)
foot = re.search(r'<footer class="hg-foot">.*?</footer>', open('ai-governance-lab/index.html').read(), re.S).group(0)

body = open('scripts/nhi-lab-body.html').read()
R2 = json.load(open('nhi-lab/evidence/results-stretch.json'))['rows']
r2 = ''
for r in R2:
    wrong = bool(r['mismatch_without'] or r['mismatch_with'])
    nz = ', '.join(f"{k.replace('_',' ')}: " + ('yes' if v else 'NO') for k, v in r['noticed'].items())
    r2 += f"<tr><th scope=\"row\">{E(r['id'])} {E(r['title'])}</th><td>{'wrong' if wrong else 'matched'}</td><td>{E(nz)}</td></tr>"
from nhi_site import subnav
body = body.replace('{{SUBNAV}}', subnav('overview')).replace('{{ROUND2}}', r2)
body = body.replace('{{CHIPS}}', chips).replace('{{CASES}}', '\n'.join(cards)).replace('{{METHOD}}', method_svg()).replace('{{LIFE}}', life_svg())
page = head + '  <body style="--c:#7df2d0">\n    <a class="skip" href="#main">Skip to content</a>\n    ' + nav + '\n' + body + '\n    ' + foot + '\n  <script src="/assets/nhi-lab.js?v=20261102a" defer></script>\n  <script defer src="/assets/chatbot-widget.js?v=20261105a"></script>\n  </body>\n</html>\n'
open('nhi-lab/index.html', 'w').write(page)
print('wrote nhi-lab/index.html', len(page))
