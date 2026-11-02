#!/usr/bin/env python3
"""Builds nhi-lab/nhi-lab-book.pdf from nhi-lab/evidence/results.json and the case texts
in scripts/build-nhi-lab.py. Run from the repo root: python3 scripts/build-nhi-book.py"""
import json, re, importlib.util, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, KeepTogether, NextPageTemplate, Flowable)

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('S', FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('SB', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('M', FD + 'DejaVuSansMono.ttf'))
pdfmetrics.registerFontFamily('S', normal='S', bold='SB', italic='S', boldItalic='SB')

# case texts from the website builder (T and GROUPS), without running it
src = open('scripts/build-nhi-lab.py').read()
ns = {}
exec(re.search(r"^T = \{.*?^\}", src, re.S | re.M).group(0), ns)
exec(re.search(r"^GROUPS = \{.*?^ '?shadow'?.*?\}", src, re.S | re.M).group(0), ns)
T, GROUPS = ns['T'], ns['GROUPS']
R = json.load(open('nhi-lab/evidence/results.json'))['rows']

NAVY = colors.HexColor('#0b1530'); INK = colors.HexColor('#16213e'); MUTED = colors.HexColor('#5b6785')
CYAN = colors.HexColor('#1aa6c9'); RED = colors.HexColor('#d6455d'); GREEN = colors.HexColor('#1f9d74')
SOFT = colors.HexColor('#f3f6fc'); AMBER = colors.HexColor('#d99a2b')
W, H = A4

def st(name, **k):
    base = dict(fontName='S', fontSize=10, leading=15, textColor=INK, spaceAfter=6)
    base.update(k); return ParagraphStyle(name, **base)
body = st('body'); small = st('small', fontSize=8.5, leading=12, textColor=MUTED)
h1 = st('h1', fontName='SB', fontSize=24, leading=29, spaceAfter=10, textColor=NAVY)
h2 = st('h2', fontName='SB', fontSize=14, leading=18, spaceBefore=8, spaceAfter=5, textColor=NAVY)
lbl = st('lbl', fontName='SB', fontSize=7.5, leading=10, textColor=MUTED, spaceAfter=2)
cell = st('cell', fontSize=9, leading=13, spaceAfter=0)

class Band(Flowable):
    def __init__(self, text, color, h=10*mm): super().__init__(); self.t, self.c, self.h = text, color, h
    def wrap(self, aw, ah): self.w = aw; return aw, self.h
    def draw(self):
        c = self.canv; c.setFillColor(self.c); c.roundRect(0, 0, self.w, self.h, 3, 0, 1)
        c.setFillColor(INK); c.setFont('SB', 9); c.drawString(4*mm, self.h/2 - 3, self.t)

def page_bg(canv, doc):
    canv.saveState(); canv.setFillColor(colors.white); canv.rect(0, 0, W, H, 0, 1)
    canv.setFillColor(CYAN); canv.rect(0, H-4*mm, W, 4*mm, 0, 1)
    canv.setFont('S', 8); canv.setFillColor(MUTED)
    canv.drawString(18*mm, 10*mm, 'Non-human identity lab  |  Roshan Trivedi  |  roshantrivedi.co.in/nhi-lab/')
    canv.drawRightString(W-18*mm, 10*mm, str(doc.page)); canv.restoreState()

def cover_bg(canv, doc):
    canv.saveState(); canv.setFillColor(NAVY); canv.rect(0, 0, W, H, 0, 1)
    cols = [g[1] for g in GROUPS.values()]
    for i, c in enumerate(cols):
        canv.setFillColor(colors.HexColor(c)); canv.rect(i*W/len(cols), H-12*mm, W/len(cols), 12*mm, 0, 1)
    # network of dots
    import random; random.seed(7)
    pts = [(random.uniform(20, W-20), random.uniform(30*mm, 120*mm)) for _ in range(34)]
    canv.setStrokeColor(colors.HexColor('#24407a')); canv.setLineWidth(.6)
    for i, a in enumerate(pts):
        for b in pts[i+1:]:
            if (a[0]-b[0])**2 + (a[1]-b[1])**2 < 70**2: canv.line(a[0], a[1], b[0], b[1])
    for i, p in enumerate(pts):
        canv.setFillColor(colors.HexColor(cols[i % len(cols)])); canv.circle(p[0], p[1], 2.6, 0, 1)
    canv.restoreState()

doc = BaseDocTemplate('nhi-lab/nhi-lab-book.pdf', pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                      topMargin=20*mm, bottomMargin=20*mm, title='I tested 27 machine identity cases',
                      author='Roshan Trivedi', subject='Non-human identity lab: cases, guesses and results')
fr = Frame(18*mm, 20*mm, W-36*mm, H-40*mm, id='f')
doc.addPageTemplates([PageTemplate('cover', frames=[Frame(22*mm, 20*mm, W-44*mm, H-40*mm)], onPage=cover_bg),
                      PageTemplate('page', frames=[fr], onPage=page_bg)])
S = []
# ---------- cover
S += [Spacer(1, 62*mm),
      Paragraph('NON-HUMAN IDENTITY LAB', st('c0', fontName='SB', fontSize=11, textColor=colors.HexColor('#4de2ff'), leading=14)),
      Paragraph('I tested 27 machine identity cases.<br/>My guesses were wrong in two places.',
                st('c1', fontName='SB', fontSize=27, leading=34, textColor=colors.white, spaceAfter=12)),
      Paragraph('Service accounts, API keys, CI tokens, break-glass accounts and AI tools with their own logins. '
                'Made-up data, guesses committed before the code, and every control switched off once to see if anything noticed.',
                st('c2', fontSize=11.5, leading=17, textColor=colors.HexColor('#c9d4f0'))),
      Spacer(1, 70*mm),
      Paragraph('Roshan Trivedi  |  November 2026<br/>roshantrivedi.co.in/nhi-lab/',
                st('c3', fontName='SB', fontSize=10, textColor=colors.HexColor('#8fa3d4'), leading=15)),
      NextPageTemplate('page'), PageBreak()]
# ---------- summary
S += [Paragraph('At a glance', h1)]
stats = [('27', 'cases', CYAN), ('25', 'guesses matched', GREEN), ('2', 'guesses wrong', RED), ('2', 'controls masked', AMBER)]
t = Table([[Paragraph(f'<font name="SB" size="26" color="{c.hexval()}">{n}</font><br/><font size="8.5" color="#5b6785">{l}</font>', st('x', leading=30, alignment=TA_CENTER)) for n, l, c in stats]],
          colWidths=[(W-36*mm)/4]*4, rowHeights=[26*mm])
t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), SOFT), ('BOX', (0,0), (-1,-1), .6, colors.HexColor('#d7deee')),
                       ('LINEAFTER', (0,0), (-2,-1), .6, colors.HexColor('#d7deee')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
S += [t, Spacer(1, 6*mm),
      Paragraph('What, why, how', h2),
      Paragraph('<b>What.</b> I ran 27 cases about machine identities: finding them, giving them owners, rotating their secrets, controlling privileged access and catching AI tools that quietly hold credentials. 24 were my must-run cases. 3 more came from a search for gaps, based on 2026 incident reports.', body),
      Paragraph('<b>Why.</b> Most companies have many more machine identities than people, and mapping sheets say a control exists without showing it holds. I wanted to see where a control stops, and to keep my own wrong guesses on the page.', body),
      Paragraph('<b>How.</b> Before any code, I wrote what I expected and committed the files. Then I wrote small models of each control and ran every case with the control off and on. Then I switched each control off by itself to see whether the result changed.', body),
      Paragraph('What I found', h2),
      Paragraph('<b>The secret scan missed two of eight fake secrets, not one.</b> It caught six. The two it missed were a secret split across two lines and a base64-encoded one. I had guessed one miss.', body),
      Paragraph('<b>Two controls showed no effect on their own, because another control already stopped the attack.</b> A 10-minute token lifetime changed nothing once the token was bound to the runner and revoked at job end. A vendor-breach revoke changed nothing once an app allowlist refused the grant. That is layering, and it also means a one-at-a-time switch-off can say "nothing happened" for a control that matters in a different scenario.', body),
      Paragraph('<b>Several controls stopped where I expected.</b> A made-up ticket number passed the break-glass review because nothing checks it against the ticket system. A false justification for break-glass use was accepted. A bound CI token still worked from inside the runner. An allowlisted app that is later breached works until someone revokes it. A false retirement sign-off left one identity active. A consumer missing from the list still broke after rotation.', body),
      Paragraph('One limit up front: I wrote both the guesses and the code, and every case is a small in-memory model, not a real vault, directory or cloud. A match proves little. The misses and the limits are the useful part.', small),
      PageBreak()]
# ---------- method
S += [Paragraph('The method', h1),
      Paragraph('The commit in step 3 is what makes the guesses honest: they cannot change after the result is known.', body)]
steps = ['Write the guess', 'Hash it (SHA-256)', 'Commit it', 'Write the code', 'Run it, control on and off', 'Switch each control off alone', 'Record every miss']
cols = [colors.HexColor(x) for x in ['#4de2ff','#4de2ff','#4de2ff','#7df2d0','#7df2d0','#f7c873','#ff8fa3']]
for i, (s_, c) in enumerate(zip(steps, cols), 1):
    S += [Table([[Paragraph(f'<font name="SB" size="16" color="#0b1530">{i}</font>', st('n', alignment=TA_CENTER, leading=20)),
                  Paragraph(f'<b>{s_}</b>', st('s', fontSize=11, leading=15, spaceAfter=0))]],
                colWidths=[14*mm, W-36*mm-14*mm], rowHeights=[11*mm],
                style=TableStyle([('BACKGROUND', (0,0), (0,0), c), ('BACKGROUND', (1,0), (1,0), SOFT), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                  ('LEFTPADDING', (1,0), (1,0), 8)])), Spacer(1, 2*mm)]
S += [Spacer(1, 4*mm), Paragraph('The life of a machine identity', h2),
      Paragraph('Every case sits on one stage of this loop: discover, own, credential, control, privileged access, retire. Retiring what is unused feeds the next discovery scan.', body)]
cnt = {}
for r in R: cnt[T[r['id']][0]] = cnt.get(T[r['id']][0], 0) + 1
cells = [[Paragraph(f'<font color="{'#ffffff' if g=='shadow' else '#0b1530'}"><b>{GROUPS[g][0]}</b><br/><font size="18">{cnt.get(g,0)}</font> {'case' if cnt.get(g,0)==1 else 'cases'}</font>', st('g', fontSize=8.5, leading=14, alignment=TA_CENTER))] for g in GROUPS]
gt = Table([cells[i:i+3] for i in range(0, 6, 3)] + [cells[6:]] if False else [[c[0] for c in cells[:4]], [c[0] for c in cells[4:]] + ['']],
           colWidths=[(W-36*mm)/4]*4, rowHeights=[22*mm, 22*mm])
sty = [('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOX', (0,0), (-1,-1), 1.5, colors.white), ('INNERGRID', (0,0), (-1,-1), 1.5, colors.white)]
for i, g in enumerate(GROUPS):
    r_, c_ = divmod(i, 4); sty.append(('BACKGROUND', (c_, r_), (c_, r_), colors.HexColor(GROUPS[g][1])))
gt.setStyle(TableStyle(sty)); S += [gt, PageBreak()]

# ---------- cases
S += [Paragraph('All 27 cases', h1),
      Paragraph('Each card shows one case. Red is what happens without the control, green is what happens with it. The last line says whether my guess matched and whether switching the control off alone changed the result.', body), Spacer(1, 3*mm)]
WRONG = {'S-R17-05': 'Guess wrong: 2 misses, not 1.', 'N-R14-25': 'Control-off guess wrong: the short lifetime was masked by binding and revoke.'}
MASK = {'N-R14-23': 'The vendor-breach revoke showed no effect alone, because the allowlist already refused the grant.',
        'N-R14-25': 'The 10-minute lifetime showed no effect alone.'}
for r in R:
    g, trig, wo, wi = T[r['id']]; gname, gcol = GROUPS[g]; gc = colors.HexColor(gcol)
    note = WRONG.get(r['id'], 'Guess matched.')
    if r['id'] in MASK: note += ' ' + MASK[r['id']]
    lim = r.get('limit')
    limtxt = ''
    if lim and lim.get('note'): limtxt = 'Limit found: ' + lim['note'] + '.'
    elif r['id'] == 'P-R15-05': limtxt = 'Limit found: 2 of the 8 who remain have broader access than the work needed.'
    elif r['id'] == 'N-R14-15': limtxt = 'Limit found: a consumer missing from the list still fails after rotation.'
    elif r['id'] == 'S-R17-05': limtxt = 'Misses: a secret split across two lines and a base64-encoded one.'
    tbl = Table([[Paragraph('TRIGGER', lbl), Paragraph(trig, cell)],
                 [Paragraph('<font color="#d6455d">WITHOUT</font>', lbl), Paragraph(wo, cell)],
                 [Paragraph('<font color="#1f9d74">WITH</font>', lbl), Paragraph(wi, cell)],
                 [Paragraph('RESULT', lbl), Paragraph(note + (' ' + limtxt if limtxt else ''), st('c9', fontSize=8.5, leading=12, textColor=MUTED, spaceAfter=0))]],
                colWidths=[22*mm, W-36*mm-22*mm])
    tbl.setStyle(TableStyle([('BACKGROUND', (0,1), (-1,1), colors.HexColor('#fdecef')), ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#e8f6f1')),
                             ('BACKGROUND', (0,0), (-1,0), SOFT), ('BACKGROUND', (0,3), (-1,3), SOFT), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                             ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                             ('LINEBELOW', (0,0), (-1,-2), .4, colors.white)]))
    S += [KeepTogether([Band(f'{r["id"]}   {r["title"]}   |   {gname}', gc), tbl, Spacer(1, 5*mm)])]
S += [PageBreak()]
# ---------- market, missing, help
S += [Paragraph('Where the market is', h1),
      Paragraph('I did not test any commercial product. This is how I read the categories, from public sources. Check each vendor\'s own documentation for what a product does today.', body)]
mk = [('PAM vaults and brokers', 'CyberArk, Delinea, BeyondTrust and others. Strong at vaulting and rotating privileged and service-account passwords, session recording and just-in-time access. In my cases: rotation, JIT windows, recording and break-glass.'),
      ('IGA', 'SailPoint, Saviynt and others. Built for owners, certification campaigns and joiner-mover-leaver. In my cases: ownership, retirement and sponsor reviews.'),
      ('Secrets managers', 'HashiCorp Vault and the cloud secret managers. Store and issue secrets, often short-lived. In my cases: short token lifetimes and per-job credentials.'),
      ('NHI-focused and cloud-risk platforms', 'Clutch, Wiz and similar. Newer products aimed at finding machine identities and their relationships across cloud, CI and SaaS. In my cases: discovery and the OAuth and CI paths.')]
for i, (a, b) in enumerate(mk):
    S += [KeepTogether([Band(a, [CYAN, GREEN, AMBER, RED][i], 8*mm), Spacer(1, 1.5*mm), Paragraph(b, body)])]
S += [Paragraph('What the sources say', h2),
      Paragraph('OWASP publishes a Top 10 for non-human identities (2025), with ten named risks including improper offboarding and human use of non-human identities. OWASP\'s agentic applications list for 2026 covers identity and privilege abuse, code execution, memory poisoning and inter-agent communication; I read a summary by Teleport, so check the OWASP original before quoting.', body),
      Paragraph('Tuhin Banerjee argues on the CSA blog (23 April 2026) that inventory-first discovery is losing ground to ephemeral identities, and that ownership and fast revocation are the neglected parts. It is an opinion piece built on named incidents, with no survey data.', body),
      Paragraph('Vercel confirmed unauthorized access in April 2026. Reports say it began with a third-party AI app that an employee had linked with broad permissions. Attribution and some details are unverified (I read a summary by Strapi).', body),
      Paragraph('GitGuardian\'s 2026 report (vendor research, 2025 data) counts 28,649,024 new secrets on public GitHub, 1,275,105 of them AI-service secrets, and 24,008 unique secrets in MCP configuration files. Quote with the name. NIST\'s NCCoE published a concept paper on software and AI agent identity and authorization on 5 February 2026; it is a concept paper only.', body),
      PageBreak(),
      Paragraph('What is missing', h1), Paragraph('In the market, as I see it (my view)', h2)]
for x in ['Checks that a sign-off is true. Owner attestations, break-glass justifications and ticket numbers are accepted as text in my models, and I suspect many real workflows are the same.',
          'Speed of revocation across companies. When a vendor is breached, the clock starts at their notice, not your inventory.',
          'Ephemeral identities that live for minutes. An inventory taken weekly cannot see them.',
          'One place that shows the agent, the person who set it up and the permissions it inherited.']:
    S += [Paragraph('&bull;&nbsp; ' + x, body)]
S += [Paragraph('In this lab', h2)]
for x in ['It is a model, not a real environment. Real vaults, directories and CI systems will behave differently.',
          'I wrote both the guesses and the code. An outside reader writing guesses first would be a stronger test.',
          '13 stretch cases and the round of chain tests are not run yet. Their guesses are written and waiting to be committed.',
          'AWS, Azure and Google Cloud each have their own key and role habits. These cases are generic.',
          'Indian rules (RBI, CERT-In, data protection) are not checked. I make no compliance claim.',
          'No cost data.']:
    S += [Paragraph('&bull;&nbsp; ' + x, body)]
S += [Paragraph('How this helps, and five questions to ask', h2),
      Paragraph('I work in identity and privileged access, and I publish the tests with the mistakes so readers can see how I think. If you run security or identity at a company, these are the questions the lab turns into:', body)]
for i, x in enumerate(['Can you list every service account across the directory, the cloud and CI, and does each one have a named owner?',
          'When a vendor you connected is breached, how many minutes until you can revoke their access?',
          'Which of your sign-offs (attestations, justifications, ticket numbers) is checked by anything other than a person reading it?',
          'Are secrets hidden by pattern only, and what is the secret that no pattern matches?',
          'If you switch one control off, does anything tell you? If not, is another control covering it, or nothing?'], 1):
    S += [Paragraph(f'<b>{i}.</b>&nbsp; {x}', body)]
S += [PageBreak(), Paragraph('Evidence you can check', h1),
      Paragraph('The guess files, the code and the results are public at roshantrivedi.co.in/nhi-lab/. The SHA-256 hash of each guess file was recorded when I committed it, before the code existed.', body)]
hs = [['Guess file', 'SHA-256'],
      ['Rounds 14 and 15 (20 cases)', 'f06f355eb80c151cb237ca4ef0c09dad9bc995fe5d395dca03f8756b0c69c784'],
      ['Round 17, shadow AI (4 cases)', '4e6dfc1a80b2fa1e0a0da0a129882e87fdd3be931b5dddafd018d92c05dc8b7c'],
      ['Gap cases (3 cases)', '7d3aee7a941b3915915690294e97ef22118957fc82b5505a1a0502d6e4bd5f8d']]
ht = Table([[Paragraph(a, cell), Paragraph(f'<font name="M" size="6.4">{b}</font>', cell)] for a, b in hs], colWidths=[50*mm, W-36*mm-50*mm])
ht.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), SOFT), ('LINEBELOW', (0,0), (-1,-1), .4, colors.HexColor('#d7deee')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
S += [ht, Spacer(1, 5*mm),
      Paragraph('If you think a case is wrong or can think of a variant that breaks a control, tell me. I will add it and keep the original on the page. Subscribe: buttondown.com/trivedi', small)]
doc.build(S)
print('built')
