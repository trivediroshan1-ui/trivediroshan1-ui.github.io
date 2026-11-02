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


def tri(c, pts):
    p = c.beginPath(); p.moveTo(pts[0], pts[1]); p.lineTo(pts[2], pts[3]); p.lineTo(pts[4], pts[5]); p.close(); c.drawPath(p, fill=1, stroke=0)

class Lifecycle(Flowable):
    """Loop of six stages with the number of cases on each."""
    def __init__(self, counts): super().__init__(); self.counts = counts
    def wrap(self, aw, ah): self.w = aw; self.h = 62*mm; return aw, self.h
    def draw(self):
        c = self.canv; names = list(GROUPS)[:6]; n = len(names); bw, bh = 26*mm, 16*mm
        gap = (self.w - n*bw) / (n-1)
        for i, g in enumerate(names):
            x = i*(bw+gap); y = 36*mm
            c.setFillColor(colors.HexColor(GROUPS[g][1])); c.roundRect(x, y, bw, bh, 3*mm, 0, 1)
            c.setFillColor(INK); c.setFont('SB', 7)
            for k, line in enumerate(GROUPS[g][0].replace(' and ', ' & ').split(' ', 1) if len(GROUPS[g][0]) > 11 else [GROUPS[g][0]]):
                c.drawCentredString(x+bw/2, y+bh-6*mm-k*3.2*mm + (3*mm if len(GROUPS[g][0]) <= 11 else 0), line)
            c.setFont('SB', 9); c.drawCentredString(x+bw/2, y+2*mm, f"{self.counts.get(g,0)} case" + ('' if self.counts.get(g,0)==1 else 's'))
            if i < n-1:
                c.setStrokeColor(MUTED); c.setLineWidth(1); c.line(x+bw+1*mm, y+bh/2, x+bw+gap-1*mm, y+bh/2)
                c.setFillColor(MUTED); tri(c, [x+bw+gap-1*mm, y+bh/2, x+bw+gap-3*mm, y+bh/2+1.3*mm, x+bw+gap-3*mm, y+bh/2-1.3*mm])
        # return arrow under the row: retire feeds the next discovery
        c.setStrokeColor(colors.HexColor('#7df2d0')); c.setLineWidth(1.4)
        x0 = 0 + bw/2; x1 = (n-1)*(bw+gap) + bw/2
        c.line(x1, 36*mm, x1, 28*mm); c.line(x1, 28*mm, x0, 28*mm); c.line(x0, 28*mm, x0, 36*mm)
        c.setFillColor(colors.HexColor('#1f9d74')); tri(c, [x0, 36*mm, x0-1.4*mm, 33.5*mm, x0+1.4*mm, 33.5*mm])
        c.setFont('S', 8); c.setFillColor(MUTED)
        c.drawCentredString(self.w/2, 22*mm, 'What you retire is gone from the next discovery scan. The loop closes.')
        c.drawCentredString(self.w/2, 14*mm, 'The 3 gap cases (OAuth, environment variables, CI runner) sit across several stages.')

class CaseFlow(Flowable):
    """One case: a trigger splits into a red lane (without the control) and a green lane (with it)."""
    def wrap(self, aw, ah): self.w = aw; return aw, 52*mm
    def draw(self):
        c = self.canv; w = self.w
        def box(x, y, bw, bh, fill, txt, tc=INK):
            c.setFillColor(fill); c.roundRect(x, y, bw, bh, 2.5*mm, 0, 1); c.setFillColor(tc); c.setFont('SB', 8)
            for k, t in enumerate(txt): c.drawCentredString(x+bw/2, y+bh/2+1.2*mm - k*4.4*mm, t)
        box(0, 18*mm, 34*mm, 18*mm, SOFT, ['Trigger', '(the event)'])
        box(60*mm, 34*mm, 40*mm, 13*mm, colors.HexColor('#fdecef'), ['Without control', 'it goes through'])
        box(60*mm, 5*mm, 40*mm, 13*mm, colors.HexColor('#e8f6f1'), ['With control', 'it is stopped'])
        box(w-48*mm, 34*mm, 48*mm, 13*mm, colors.HexColor('#f8c9d2'), ['Harm happens', 'nobody notices'])
        box(w-48*mm, 5*mm, 48*mm, 13*mm, colors.HexColor('#b8e6d6'), ['Refused, logged', 'owner told'])
        c.setLineWidth(1.2)
        for (a, b, col) in [((34*mm, 31*mm), (60*mm, 40*mm), RED), ((34*mm, 23*mm), (60*mm, 11*mm), GREEN), ((100*mm, 40*mm), (w-48*mm, 40*mm), RED), ((100*mm, 11*mm), (w-48*mm, 11*mm), GREEN)]:
            c.setStrokeColor(col); c.line(a[0], a[1], b[0], b[1])
        c.setFont('S', 7.5); c.setFillColor(MUTED)
        c.drawString(0, 0, 'Then I switch the control off alone. If nothing notices, another control was already doing the job.')

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

S += [Paragraph('About this book', h1),
      Paragraph('<b>Title.</b> I tested 27 machine identity cases. My guesses were wrong in two places.<br/><b>Edition.</b> 1.0, 2 November 2026. Free to read and share; please credit the author.<br/><b>Author.</b> Roshan Trivedi, identity and privileged access, Bengaluru. roshantrivedi.co.in', body),
      Paragraph('Description', h2),
      Paragraph('A short lab notebook. It takes 27 situations in which a machine identity (a service account, an API key, a CI token, a break-glass account, an AI tool with its own login) can go wrong. For each one it records what I expected, what a small model of the control did with the control off and on, and whether anything noticed when I switched the control off by itself.', body),
      Paragraph('Problem statement', h2),
      Paragraph('Most companies have many more machine identities than people. Control mapping sheets say a control exists. They rarely show where it stops. Reports from 2026 describe breaches that began with a forgotten token, a leaked secret or an AI app that an employee linked with broad access. Nobody checks whether the usual controls would have held, and people seldom publish their own wrong guesses.', body),
      Paragraph('Scope', h2),
      Paragraph('<b>In scope:</b> 27 cases in six areas: discovering identities, giving them owners and retiring them, credentials and rotation, the front door and trust, privileged access, and shadow AI. Plus three cases from a search for gaps.<br/><b>Out of scope:</b> any commercial product, real vaults or directories, real cloud tenants, real AI models, cost, and Indian regulation (RBI, CERT-In, data protection). I make no compliance claim.<br/><b>Second run:</b> 13 stretch cases and 6 chain tests, with their guesses committed first (page 20). The headline numbers in this book are the first 27 cases.', body),
      Paragraph('All people, companies, numbers and data are made up. The company, Kaveri Finance, does not exist. Every secret in the tests is fake. This is not a product review and not legal advice. A pass shows the model did what I wrote it to do.', small),
      PageBreak(),
      Paragraph('Contents', h1)]
for a, b in [('1', 'At a glance'), ('2', 'The method and the workflow'), ('3', 'All 27 cases'), ('4', 'Where the market is'), ('5', 'What is missing, and what to ask'), ('6', 'Evidence you can check'),
             ('A', 'Appendix A: case index'), ('B', 'Appendix B: how to re-run the lab'), ('C', 'Appendix C: sources'), ('D', 'Glossary'), ('E', 'About the author')]:
    S += [Paragraph(f'<b>{a}</b>&nbsp;&nbsp;&nbsp;{b}', st('toc', fontSize=11, leading=19, spaceAfter=0))]
S += [PageBreak()]
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
gt.setStyle(TableStyle(sty)); S += [gt, Spacer(1, 5*mm), Lifecycle(cnt), PageBreak(),
      Paragraph('The workflow of one case', h1),
      Paragraph('Every one of the 27 cases follows the same path. A trigger happens. Without the control it goes through. With the control it is stopped. Then the control is switched off by itself to see whether anything notices.', body), Spacer(1, 3*mm), CaseFlow(), PageBreak()]

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
          'The 13 stretch cases and 6 chain tests ran in a second run. 21 queued cases and the Stage 2 testing are not run.',
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

S += [PageBreak(), Paragraph('Appendix A: case index', h1),
      Paragraph('Guess result: M means my guess matched, W means it was wrong.', small)]
rows = [['ID', 'Case', 'Group', 'Guess']]
for r in R:
    g = T[r['id']][0]; rows.append([r['id'], Paragraph(r['title'], cell), GROUPS[g][0], 'W' if r['id'] in WRONG else 'M'])
it = Table(rows, colWidths=[24*mm, 80*mm, 52*mm, 14*mm], repeatRows=1)
it.setStyle(TableStyle([('FONT', (0,0), (-1,-1), 'S', 8), ('FONT', (0,0), (-1,0), 'SB', 8), ('BACKGROUND', (0,0), (-1,0), SOFT),
                        ('LINEBELOW', (0,0), (-1,-1), .3, colors.HexColor('#d7deee')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
S += [it, PageBreak(),
      Paragraph('Appendix B: how to re-run the lab', h1),
      Paragraph('You need Python 3 and nothing else. The lab files are at roshantrivedi.co.in/nhi-lab/evidence/.', body),
      Paragraph('1. Download <font name="M">cases.py</font>, <font name="M">run.py</font> and the three guess files into one folder.<br/>2. Run <font name="M">python3 run.py</font>.<br/>3. The runner first checks the SHA-256 of each guess file against the hash recorded at commit time, and stops if one differs.<br/>4. It runs each case without and with the control, then switches each control off alone, and writes <font name="M">RESULTS.md</font> and <font name="M">results.json</font>.', body),
      Paragraph('Every secret in the cases is made up. Never paste a real secret into any test.', small),
      Paragraph('Appendix C: sources', h1),
      Paragraph('<b>OWASP Non-Human Identities Top 10 (2025).</b> Ten named risks, including improper offboarding and human use of non-human identities.<br/><b>OWASP Top 10 for Agentic Applications (2026).</b> I read a summary by Teleport; check the OWASP original before quoting.<br/><b>Tuhin Banerjee, Cloud Security Alliance blog, 23 April 2026.</b> An opinion piece built on named incidents.<br/><b>Vercel security incident, April 2026.</b> Read through a summary by Strapi; attribution and some details are unverified.<br/><b>GitGuardian State of Secrets Sprawl 2026.</b> Vendor research, 2025 data.<br/><b>NIST NCCoE concept paper on software and AI agent identity and authorization, 5 February 2026.</b> A concept paper only.<br/><b>Wiz blog, Non-Human Identities dashboard, February 2024; Clutch Security via Okta integrations page; SailPoint Entro documentation.</b> Vendor descriptions, not tested.', body),
      PageBreak(), Paragraph('Glossary', h1)]
GL = [('Non-human identity (NHI)', 'An account or credential used by software, not a person: a service account, API key, token, certificate or bot.'),
      ('Service account', 'A directory or cloud account that an application uses to sign in.'),
      ('Secret', 'A password, key or token that proves identity. Anyone who holds it can act as the identity.'),
      ('Rotation', 'Replacing a secret with a new one on a schedule or after a leak.'),
      ('Refresh token', 'A long-lived token that lets an app get new short-lived access without asking the person again.'),
      ('OAuth grant', 'The permission a person gives an app to act on their behalf.'),
      ('Allowlist', 'A list of apps or actions that are permitted. Anything not on it is refused.'),
      ('Revoke', 'End a credential or grant so it no longer works.'),
      ('Break-glass account', 'A powerful emergency account kept for incidents. Its use should be rare and always noticed.'),
      ('PAM', 'Privileged access management: control, time-limiting and recording of powerful access.'),
      ('IGA', 'Identity governance and administration: owners, reviews, and joining, moving and leaving.'),
      ('JIT access', 'Just-in-time access: given for a short window and removed after.'),
      ('CI/CD', 'The automated build and deploy pipeline, whose jobs hold credentials.'),
      ('Control-off check', 'Switching one control off alone to see whether anything notices. If nothing does, another control was covering it, or the control did nothing.'),
      ('Masked control', 'A control whose effect is hidden because another control already stopped the attack.'),
      ('SHA-256', 'A fingerprint of a file. If the file changes, the fingerprint changes. It proves the guesses were not edited later.'),
      ('Shadow AI', 'AI tools and agents that people connect to work systems without the company knowing.')]
S += [Table([[Paragraph(f'<b>{a}</b>', cell), Paragraph(b, cell)] for a, b in GL], colWidths=[42*mm, W-36*mm-42*mm],
            style=TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LINEBELOW', (0,0), (-1,-1), .3, colors.HexColor('#d7deee')),
                              ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)])), PageBreak(),
      Paragraph('About the author', h1),
      Paragraph('Roshan Trivedi works in identity and privileged access security in Bengaluru, India. He writes and tests work on AI governance, MCP security, non-human identity and privileged access, and publishes the tests with the mistakes.', body),
      Paragraph('Website: roshantrivedi.co.in<br/>Newsletter: buttondown.com/trivedi<br/>Other labs: AI governance lab (13 rounds, 164 cases) and the MCP lab.', body),
      Paragraph('If you think a case is wrong, tell me. I will add it and keep the original.', small)]


S += [PageBreak(), Paragraph('Second run: 13 stretch cases and 6 chain tests', h1),
      Paragraph('These ran after the first 27, with the same method. The guesses were committed first (commit 78d7e3e). The chain tests are rule models: I decided which control stops which link, so the results follow from my rules and are weak evidence.', body),
      Paragraph('<b>Three guesses were wrong.</b> I wrote that 9 identities with two or three names each would give 51 entries. That is impossible: it gives 43. After merging I expected 30 and got 29, because stripping trailing digits merged two real accounts into one. For the forgotten service account chain I guessed the secret scan on tickets was the most useful single control. In my rules the owner check stops it earliest, but only for accounts created after the rule. For an account that already exists the scan is the one that works.', body),
      Paragraph('<b>My first run of the matching case was wrong because of my own test data.</b> I had given 21 identities the same owner, so they merged into 11. I fixed the data and kept the first output.', body),
      Paragraph('<b>Controls that hid each other.</b> In the help-desk reset case, strong proof and the notice with a delay each stopped both attacker resets alone, so switching either off showed nothing. Rotating AI-service keys every 90 days changed nothing once the scan revoked the keys it could see.', body),
      Paragraph('<b>Limits.</b> A password copied during a checkout and used from another tool is not seen. If the real person approves the reset notice, the account is lost with both controls on. An extension of an automation is accepted on any written reason.', body)]

S += [PageBreak(), Paragraph('Evidence you can check', h1),
      Paragraph('The guess files, the code and the results are public at roshantrivedi.co.in/nhi-lab/. The SHA-256 hash of each guess file was recorded when I committed it, before the code existed.', body)]
hs = [['Guess file', 'SHA-256'],
      ['Rounds 14 and 15 (20 cases)', 'f06f355eb80c151cb237ca4ef0c09dad9bc995fe5d395dca03f8756b0c69c784'],
      ['Round 17, shadow AI (4 cases)', '4e6dfc1a80b2fa1e0a0da0a129882e87fdd3be931b5dddafd018d92c05dc8b7c'],
      ['Gap cases (3 cases)', '7d3aee7a941b3915915690294e97ef22118957fc82b5505a1a0502d6e4bd5f8d'],
      ['Stretch and chain tests (19 cases)', '40c2f87c9f3fa914b48a09c4abf016f1189b02ea91f07232e456275b842489ed']]
ht = Table([[Paragraph(a, cell), Paragraph(f'<font name="M" size="6.4">{b}</font>', cell)] for a, b in hs], colWidths=[50*mm, W-36*mm-50*mm])
ht.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), SOFT), ('LINEBELOW', (0,0), (-1,-1), .4, colors.HexColor('#d7deee')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
S += [ht, Spacer(1, 5*mm),
      Paragraph('If you think a case is wrong or can think of a variant that breaks a control, tell me. I will add it and keep the original on the page. Subscribe: buttondown.com/trivedi', small)]
doc.build(S)
print('built')
