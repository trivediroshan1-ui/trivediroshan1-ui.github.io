#!/usr/bin/env python3
"""Builds nhi-lab/nhi-lab-book.pdf (edition 2) from the lab evidence and the shared data module.
Run from the repo root:  python3 scripts/build-nhi-book.py
Reads nhi-lab/evidence (guess files, results), scripts/nhi_data.py, scripts/book_text.py, scripts/book_lib.py,
and the market sources and roadmap lanes used by the website pages."""
import sys, os, io, json, math, random, hashlib, contextlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from book_lib import *
import nhi_data as D
from book_text import *
from pages_market import SRC
from pages_roadmap import LANES

ROOT = D.ROOT
OUT = os.path.join(ROOT, 'nhi-lab', 'nhi-lab-book.pdf')
EDITION_DATE = '2 November 2026'

# ------------------------------------------------------------------ data
CASES = D.load_cases()
BYID = {c['id']: c for c in CASES}
N = len(CASES)
WRONG_N = sum(c['wrong'] for c in CASES)
MASKED_N = sum(bool(c['masked']) for c in CASES)
LIMIT_N = sum(bool(c['limit']) for c in CASES)
assert (N, WRONG_N, MASKED_N, LIMIT_N) == (48, 5, 10, 14), (N, WRONG_N, MASKED_N, LIMIT_N)

cwd = os.getcwd(); os.chdir(os.path.join(ROOT, 'nhi-lab', 'evidence')); sys.path.insert(0, '.')
with contextlib.redirect_stdout(io.StringIO()):
    import cases2
os.chdir(cwd)
CHAINS = {x['id']: x for x in cases2.CASES if x.get('chain')}
EFFECT = {'C-R16-C02': {'revoke_on_find': 'late'}, 'C-R16-C04': {'sponsor_review': 'late'}, 'C-R16-C06': {'batch_limits': 'none'}}
RES = {r['id']: r for r in json.load(open(os.path.join(D.EV, 'results.json')))['rows']}
RES.update({r['id']: r for r in json.load(open(os.path.join(D.EV, 'results-stretch.json')))['rows']})
RES.update({r['id']: r for r in json.load(open(os.path.join(D.EV, 'results-round-18.json')))['rows']})

STEPS = {k: (n, sub) for k, n, sub in D.STAGES}
STEP_NO = {k: i + 1 for i, (k, _, _) in enumerate(D.STAGES)}
SHORT = lambda cid: cid[0] + cid[-2:]

# ------------------------------------------------------------------ helpers
def humanize(k): return k.replace('_', ' ')
def fmtv(v):
    if v is True: return 'yes'
    if v is False: return 'no'
    if v is None: return 'none'
    if isinstance(v, list): return ', '.join(humanize(str(x)) for x in v) if v else 'none'
    return str(v)
def fmt_flat(d):
    return ', '.join(f'{humanize(k)} {fmtv(v)}' for k, v in d.items() if not isinstance(v, dict))
def fmt_chain(r, links):
    def where(i): return 'does not stop it' if i is None else f'stops it at link {i}'
    o = []
    w = r['without']; wi = r['with_']
    o.append('Without controls: ' + ('the attacker reaches the last link.' if w.get('reached_end') else f'stopped at link {w.get("stopped_at")}.'))
    s = f'With all controls: stopped at link {wi.get("stopped_at")}.' if wi.get('stopped_at') else 'With all controls: not stopped.'
    if wi.get('detected_at'): s += f' Reported at link {wi["detected_at"]}.'
    o.append(s)
    al = wi.get('alone_stopped_at')
    if al: o.append('Each control alone: ' + '; '.join(f'{clabel(k)} {where(v)}' for k, v in al.items()) + '.')
    if wi.get('best_alone'): o.append(f'Best single control: {clabel(wi["best_alone"])}.')
    return ' '.join(o)

def case_notes(c):
    r = RES[c['id']]
    rows = []
    if c['wrong']:
        said, got = WRONG[c['id']]
        g = f'<font color="#c93a53"><b>Wrong.</b></font> {esc(said)} {esc(got)}'
    else:
        g = '<font color="#1a8a66"><b>Matched</b></font> in both runs (control off, control on).'
    rows.append(('Guess', g))
    if c['id'] in CHAINS: rows.append(('Measured', esc(fmt_chain(r, CHAINS[c['id']]['links']))))
    else: rows.append(('Measured', f'Without: {esc(fmt_flat(r["without"]))}. With: {esc(fmt_flat(r["with_"]))}.'))
    for e in c['extras']:
        mis = e.get('mismatch')
        t = f'{esc(e["label"].capitalize())}. ' + ('Result matched my guess.' if not mis else f'Result differs from my guess: {esc(str(mis))}.')
        rows.append(('Extra scenario', t))
    rows.append(('Take-away', esc(TAKE[c['id']])))
    data = [[Paragraph(f'<font name="BodyB" color="#5b6785" size="8">{k.upper()}</font>', S['cell']), Paragraph(v, S['cell'])] for k, v in rows]
    t = Table(data, colWidths=[24 * mm, CW - 24 * mm])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                           ('TOPPADDING', (0, 0), (-1, -1), 1.6), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6),
                           ('LINEABOVE', (0, 0), (-1, 0), 0.5, LINE)]))
    return t

def case_block(c):
    ch = None
    if c['id'] in CHAINS:
        x = CHAINS[c['id']]; ch = dict(links=x['links'], rules=x['rules'], effect=EFFECT.get(c['id'], {}))
    col = STAGE_COLOR[c['stage']]
    bits = [f'Step {STEP_NO[c["stage"]]}: {STEPS[c["stage"]][0]}', f'Run {c["run"]}', c['group_name']]
    if c['owasp']: bits.append('OWASP ' + ', '.join(c['owasp']))
    tags = []
    tags.append('<font color="#c93a53"><b>Guess wrong</b></font>' if c['wrong'] else '<font color="#1a8a66"><b>Guess matched</b></font>')
    if c['masked']: tags.append('<font color="#c98a1b"><b>Control masked</b></font>')
    if c['limit']: tags.append('<font color="#c98a1b"><b>Limit recorded</b></font>')
    meta = Paragraph(f'<font color="{col}"><b>{esc(bits[0])}</b></font>  ·  ' + '  ·  '.join(esc(b) for b in bits[1:]) + '  ·  ' + '  ·  '.join(tags), S['small'])
    head = Paragraph(f'<font color="{col}">{esc(c["id"])}</font>&nbsp;&nbsp;{esc(c["title"])}', S['casehead'])
    setup = Paragraph(esc(c['setup'][:1].upper() + c['setup'][1:]) if c['setup'] else '', S['body'])
    return [KeepTogether([head, meta, setup, Spacer(1, 1.5 * mm), CaseDiagram(c, ch), Spacer(1, 1 * mm)]), case_notes(c), Spacer(1, 7 * mm)]

# ------------------------------------------------------------------ figures
class ResultsMap(Flowable):
    """One square per case, one row per framework step."""
    def wrap(self, aw, ah):
        self.w = aw; self.sq = 9.2 * mm; self.gap = 1.6 * mm; self.rh = self.sq + 3.4 * mm
        self.h = 7 * self.rh + 14 * mm
        return aw, self.h
    def draw(self):
        c = self.canv; y = self.h
        for i, (k, name, sub) in enumerate(D.STAGES):
            y -= self.rh
            col = hexc(STAGE_COLOR[k])
            c.setFillColor(col); c.roundRect(0, y, 1.8 * mm, self.sq, 0.9 * mm, 0, 1)
            c.setFont('BodyB', 9); c.setFillColor(NAVY); c.drawString(4 * mm, y + self.sq / 2 + 0.6 * mm, f'{i + 1}. {name}')
            c.setFont('Body', 7.2); c.setFillColor(MUTED)
            cs = [x for x in CASES if x['stage'] == k]; c.drawString(4 * mm, y + self.sq / 2 - 3 * mm, f'{len(cs)} case' + ('s' if len(cs) != 1 else ''))
            for j, cc in enumerate(cs):
                x = 52 * mm + j * (self.sq + self.gap)
                c.setFillColor(RED if cc['wrong'] else GREEN); c.roundRect(x, y, self.sq, self.sq, 1.4 * mm, 0, 1)
                c.setFillColor(colors.white); c.setFont('BodyB', 6.8); c.drawCentredString(x + self.sq / 2, y + self.sq / 2 - 2.2, SHORT(cc['id']))
                if cc['masked']:
                    c.setFillColor(AMBER); c.setStrokeColor(colors.white); c.setLineWidth(0.8); c.circle(x + self.sq - 0.6 * mm, y + self.sq - 0.6 * mm, 1.7 * mm, 1, 1)
                if cc['limit']:
                    c.setFillColor(NAVY); p = c.beginPath(); p.moveTo(x, y); p.lineTo(x + 3.0 * mm, y); p.lineTo(x, y + 3.0 * mm); p.close(); c.drawPath(p, fill=1, stroke=0)
        y -= 7 * mm
        lx = 0
        for kind, label in (('g', 'Guess matched'), ('r', 'Guess wrong'), ('a', 'A control nothing noticed'), ('n', 'A limit is recorded')):
            if kind in 'gr':
                c.setFillColor(GREEN if kind == 'g' else RED); c.roundRect(lx, y, 4.4 * mm, 4.4 * mm, 0.9 * mm, 0, 1)
            elif kind == 'a':
                c.setFillColor(AMBER); c.circle(lx + 2.2 * mm, y + 2.2 * mm, 1.9 * mm, 0, 1)
            else:
                c.setFillColor(NAVY); p = c.beginPath(); p.moveTo(lx, y); p.lineTo(lx + 4 * mm, y); p.lineTo(lx, y + 4 * mm); p.close(); c.drawPath(p, fill=1, stroke=0)
            c.setFont('Body', 8.2); c.setFillColor(INK); c.drawString(lx + 6.2 * mm, y + 0.9 * mm, label)
            lx += 6.2 * mm + pdfmetrics.stringWidth(label, 'Body', 8.2) + 7 * mm

class Timeline(Flowable):
    """Market events, August 2025 to October 2026."""
    EV = [((2025, 8, 8), 'Aug 2025', 'Drift tokens stolen', RED, 1),
          ((2026, 2, 5), '5 Feb', 'NIST concept paper', CYAN, 2),
          ((2026, 2, 11), '11 Feb', 'Palo Alto closes CyberArk', GREEN, 1),
          ((2026, 3, 5), '5 Mar', 'Delinea closes StrongDM', GREEN, 3),
          ((2026, 4, 2), '2 Apr', 'NIST comments close', CYAN, 1),
          ((2026, 5, 1), '1 May', 'Entra Agent ID page updated', VIOLET, 2),
          ((2026, 6, 29), '29 Jun', 'SailPoint closes Entro; Cisco closes Astrix', GREEN, 1),
          ((2026, 9, 15), 'Sep 2026', 'NIST: 600+ commenters', CYAN, 2)]
    def wrap(self, aw, ah): self.w = aw; self.h = 58 * mm; return aw, self.h
    def draw(self):
        c = self.canv; ax = 22 * mm; y0 = 26 * mm
        def pos(d):
            m = (d[0] - 2025) * 12 + d[1] - 8 + (d[2] - 1) / 30.0
            return ax + (self.w - ax - 12 * mm) * m / 14.8
        c.setStrokeColor(MUTED); c.setLineWidth(1.4); c.line(ax - 6 * mm, y0, self.w - 4 * mm, y0)
        c.setFont('Body', 7); c.setFillColor(MUTED)
        for yy, mm_, lab in ((2025, 8, 'Aug 25'), (2025, 11, 'Nov'), (2026, 2, 'Feb 26'), (2026, 5, 'May'), (2026, 8, 'Aug')):
            x = pos((yy, mm_, 1)); c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(x, y0 - 2.5 * mm, x, y0 + 2.5 * mm); c.drawCentredString(x, y0 - 6.5 * mm, lab)
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.setDash(2, 2); c.line(pos((2025, 9, 1)) + 3 * mm, y0 + 2 * mm, pos((2026, 1, 20)) - 3 * mm, y0 + 2 * mm); c.setDash()
        c.setFont('BodyI', 6.8); c.setFillColor(MUTED); c.drawCentredString((pos((2025, 9, 1)) + pos((2026, 1, 20))) / 2, y0 + 3.2 * mm, 'axis shortened between Sep 2025 and Jan 2026')
        for d, dl, lab, col, lvl in self.EV:
            x = pos(d)
            if d[0] == 2025: x = ax
            top = lvl in (1, 3)
            ly = y0 + (9 + (0 if lvl == 1 else 15) * (1 if lvl == 3 else 0)) * mm if top else y0 - (11 * mm) / mm * mm * 0 - 12 * mm
            if lvl == 3: ly = y0 + 24 * mm
            elif lvl == 1: ly = y0 + 11 * mm
            elif lvl == 2: ly = y0 - 14 * mm
            c.setStrokeColor(col); c.setLineWidth(0.9); c.line(x, y0, x, ly + (0 if ly > y0 else 4.5 * mm))
            c.setFillColor(col); c.circle(x, y0, 1.8 * mm, 0, 1)
            c.setFont('BodyB', 7.4); c.setFillColor(col)
            tw = pdfmetrics.stringWidth(lab, 'BodyB', 7.4); tx = min(max(x - tw / 2, 0), self.w - tw)
            c.drawString(tx, ly + (1.2 * mm if ly > y0 else 0), lab)
            c.setFont('Body', 7); c.setFillColor(MUTED); c.drawString(tx, ly + (-2.6 * mm if ly > y0 else -3.2 * mm) + (0 if ly > y0 else 0), dl)

def cover_art(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, 0, 1)
    rnd = random.Random(46)
    nodes = [(rnd.uniform(0.04, 0.96) * W, rnd.uniform(0.40, 0.98) * H) for _ in range(66)]
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            if d < 34 * mm:
                c.setStrokeColor(colors.Color(0.45, 0.55, 0.8, alpha=max(0.05, 0.35 - d / (34 * mm) * 0.3))); c.setLineWidth(0.5); c.line(a[0], a[1], b[0], b[1])
    palette = [CYAN, GREEN, AMBER, VIOLET, RED]
    for i, (x, y) in enumerate(nodes):
        col = colors.HexColor('#7287b8') if i % 7 else palette[(i // 7) % 5]
        c.setFillColor(colors.Color(col.red, col.green, col.blue, alpha=0.9)); c.circle(x, y, (1.1 if i % 7 else 2.2) * mm, 0, 1)
    c.setFillColor(colors.Color(0.04, 0.08, 0.19, alpha=0.92)); c.rect(0, 0, W, 0.5 * H, 0, 1)
    c.setFillColor(CYAN); c.rect(LEFT, 0.455 * H, 16 * mm, 1.4 * mm, 0, 1)
    c.setFont('BodyB', 10); c.setFillColor(colors.HexColor('#9fb0d4')); c.drawString(LEFT, 0.43 * H, 'NON-HUMAN IDENTITY LAB  ·  EDITION 2')
    c.setFont('Head', 40); c.setFillColor(colors.white)
    c.drawString(LEFT, 0.365 * H, 'Machine identities,'); c.drawString(LEFT, 0.365 * H - 16 * mm, 'tested in public')
    c.setFont('Body', 14); c.setFillColor(colors.HexColor('#c8d3ee'))
    y = 0.365 * H - 29 * mm
    for ln in simpleSplit('48 cases on service accounts, secrets, privileged access and AI tools, with the guesses, the mistakes and the market in 2026', 'Body', 14, CW - 20 * mm):
        c.drawString(LEFT, y, ln); y -= 6.4 * mm
    bx = LEFT; by = 0.17 * H
    for num, lab, col in ((str(N), 'cases', CYAN), (str(N - WRONG_N), 'guesses matched', GREEN), (str(WRONG_N), 'guesses wrong', RED), (str(MASKED_N), 'controls nothing noticed', AMBER)):
        c.setFillColor(col); c.setFont('Head', 28); c.drawString(bx, by, num)
        c.setFont('Body', 8.6); c.setFillColor(colors.HexColor('#c8d3ee')); c.drawString(bx, by - 5.2 * mm, lab)
        bx += 40 * mm
    c.setStrokeColor(colors.HexColor('#2a3a66')); c.setLineWidth(0.6); c.line(LEFT, 0.115 * H, W - RIGHT, 0.115 * H)
    c.setFont('BodyB', 13); c.setFillColor(colors.white); c.drawString(LEFT, 0.088 * H, 'Roshan Trivedi')
    c.setFont('Body', 9.4); c.setFillColor(colors.HexColor('#9fb0d4'))
    c.drawString(LEFT, 0.088 * H - 5.4 * mm, f'{EDITION_DATE}  ·  roshantrivedi.co.in/nhi-lab/  ·  CC BY 4.0  ·  All data is made up')
    c.restoreState()

def back_art(c, doc):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, 0, W, H, 0, 1); c.setFillColor(CYAN); c.rect(0, H - 4 * mm, W, 4 * mm, 0, 1)
    c.setFont('Head', 24); c.setFillColor(colors.white); c.drawString(LEFT, H * 0.62, 'Check my work.')
    c.setFont('Body', 12); c.setFillColor(colors.HexColor('#c8d3ee'))
    y = H * 0.62 - 10 * mm
    for ln in simpleSplit('Every guess file, hash, result and script is in the public repository. The audit page lets you filter the 48 cases and download them as CSV or JSON. If a case is wrong, tell me. I will fix it and keep the original on the page.', 'Body', 12, CW):
        c.drawString(LEFT, y, ln); y -= 5.8 * mm
    c.setFont('BodyB', 12); c.setFillColor(colors.white)
    for k, t in enumerate(('roshantrivedi.co.in/nhi-lab/', 'roshantrivedi.co.in/nhi-lab/audit/', 'roshantrivedi.co.in/nhi-lab/framework/')):
        c.drawString(LEFT, y - 8 * mm - k * 7 * mm, t)
    c.setFont('Body', 9); c.setFillColor(colors.HexColor('#9fb0d4')); c.drawString(LEFT, 22 * mm, 'Roshan Trivedi  ·  Machine identities, tested in public  ·  Edition 2, ' + EDITION_DATE)
    c.restoreState()

Book.cover_art = staticmethod(cover_art); Book.back_art = staticmethod(back_art)

def src_ref(i): return f'[{i}]'
def link(u, t=None): return f'<link href="{u}" color="#1a7fa0">{esc(t or u)}</link>'

# ------------------------------------------------------------------ story
story = []
def chapter(num, title, kicker, color=CYAN, sub=''):
    story.extend([ChapterMark(title), PageBreak(), ChapterHead(num, title, kicker, color, sub), Spacer(1, 7 * mm)])
def h2(t): story.append(Paragraph(esc(t), S['h2']))
def h3(t): story.append(Paragraph(esc(t), S['h3']))
def p(t, s='body'): story.append(Paragraph(t, S[s]))
def add(*fl): story.extend(fl)

# cover
add(NextPageTemplate('main'), Spacer(1, 1), ChapterMark('Before you start'), PageBreak())

# ---- before you start
story.append(ChapterMark('Before you start'))
add(ChapterHead('', 'Before you start', 'Read this first', CYAN, 'Who it is for, how to read it, and how to read a case diagram.'), Spacer(1, 7 * mm))
h2('Who this is for')
add(*bullets(['Platform owners and IAM or PAM engineers who run service accounts, vaults, pipelines and AI integrations.',
              'Security architects who need to choose controls and explain the choice.',
              'Auditors and risk owners who want to see what was tested and what was not.',
              'Anyone who has been told that machine identities outnumber people and wants to know what to do about it.']))
h2('How to read it')
add(table([['If you have', 'Read', 'You will get'],
           ['10 minutes', 'Chapter 2', 'The findings in plain words and one picture of all 48 cases.'],
           ['An hour', 'Chapters 1 to 4, then the cases for the step you care about', 'The method, the framework and the evidence for one step.'],
           ['An afternoon', 'The whole book', 'Every case with its own workflow diagram, the market in 2026, what is missing and what comes next.']],
          [28, 62, 84], col_styles='first-bold'))
story.append(Spacer(1, 4 * mm))
story.append(KeepTogether([Paragraph('How to read a case diagram', S['h2']),
    Paragraph('Each of the 48 cases has the same kind of picture, so once you have read one you can read them all. The numbers on the boxes match the numbers below. This example is case N-R14-15, which is about rotating a password in the wrong order.', S['body']),
    Legend(), CaseDiagram(BYID['N-R14-15'], None), Spacer(1, 2 * mm)]))
add(*numbered(['<b>Event.</b> What happens in the case, in one line.',
               '<b>Control.</b> The rule or check being tested. Some cases test more than one.',
               '<b>Without the control.</b> What the model did when the control was off. The dashed red line shows the path.',
               '<b>With the control.</b> What it did when the control was on.',
               '<b>Switch each control off alone.</b> If switching one control off changes the result, a check noticed it (green). If nothing changes, the control was masked by another or did not matter in this case (amber).',
               '<b>What it cannot see.</b> The limit I recorded. Grey and empty means I found none, which is not the same as there being none.']))
p('Chain tests look a little different. The top row shows the attacker\'s links. A flag under a link shows where a control acts: it stops the attacker there, only reports, arrives too late, or has no effect.', 'body')
story.append(Spacer(1, 3 * mm))
add(Callout('A note on the data', 'Every account, bank and number in this book is made up. The bank is called Kaveri Finance and does not exist. Nothing relates to any employer, client or real company. The models are small and run in memory.', 'info'))
add(Callout('What changed since edition 1', 'The first edition had 27 cases and 21 pages. This one has 48 cases, a workflow diagram for each, the framework, a dated market chapter, a method chapter that lists my mistakes, an audit appendix, a roadmap and a glossary.', 'violet'))

# ---- contents
story.append(ChapterMark('Contents'))
add(PageBreak(), Paragraph('Contents', ParagraphStyle('ContentsH', parent=S['h2'])))
toc = make_toc(); add(toc)

# ================================================================== 1 THE PROBLEM
chapter(1, 'The problem and what I tested', 'Chapter 1', CYAN, 'Why machine identities, what I asked, and what is in and out of scope.')
h2('Why machine identities')
p('Ask a security team how many people have accounts and you will get a number. Ask how many service accounts, API keys, CI tokens, certificates and AI-tool grants they have, who owns each one and when each stops working, and the room goes quiet.', 'lede')
p(f'Palo Alto Networks says in a 2026 press release that machine identities outnumber human ones by more than 80 to 1 {src_ref("S1")}. That is a vendor statistic, and I could not find the study behind it. I use it as a reason to look, and I do not rely on the number.')
p(f'A real case shows why it matters. Google\'s threat intelligence group reported that from 8 August 2025 an actor used stolen OAuth tokens tied to the Salesloft Drift app to read data in customers\' Salesforce accounts. Salesloft and Salesforce revoked all active tokens on 20 August 2025 {src_ref("S11")}. Nobody had to guess a password. Someone held a token that still worked.')
h2('The question')
add(Callout('What I set out to test', 'Do the controls people recommend for machine identities stop the failures they are meant to stop, and would anything tell you if one stopped working?', 'violet'))
h2('Why a lab, and why guesses first')
p('I cannot test a vendor\'s product on a vendor\'s data. What I can test is the reasoning behind a control. If this rule exists, does this failure stop? And if I switch the rule off, does anything notice?')
p('So each case is a small model of one control and one failure. I write down what I expect with the control off and on. I lock the file with a SHA-256 hash and commit it before any code exists. Then I write the model, run it, and compare. A test you design after seeing the result will agree with you. A committed guess file makes it visible if I changed my mind.')
h2('What is in scope and what is not')
add(table([['In scope', 'Out of scope'],
           ['Finding service accounts, owners, rotation, front doors for new identities, just-in-time and recorded privileged access, break-glass accounts, vendor access, and AI tools that hold credentials. Chain tests that join several failures.',
            'Any real product. Any real company\'s data. Performance and cost. Legal or regulatory compliance. Kubernetes workload identity. Cloud-specific key habits.']],
          [87, 87], zebra=False))
story.append(Spacer(1, 3 * mm))
h2('What you will find in the book')
add(*bullets(['<b>Chapter 2</b> gives the findings and a one-page map of all 48 cases.',
              '<b>Chapter 3</b> says exactly what I did, in order, with dates and the mistakes I made.',
              '<b>Chapter 4</b> turns the evidence into a seven-step framework you can use on your own estate.',
              '<b>Chapters 5 to 11</b> hold the cases, one workflow diagram each, grouped by framework step.',
              '<b>Chapter 12</b> gives the results, the wrong guesses, the controls nothing noticed and the limits.',
              '<b>Chapter 13</b> covers the market in 2026, with a date and a source for every fact.',
              '<b>Chapters 14 and 15</b> say what is missing and what comes next.']))

# ================================================================== 2 THE SHORT VERSION
chapter(2, 'The short version', 'Chapter 2', GREEN, 'The findings in plain words, and a map of every case.')
add(Tiles([(str(N), 'cases in two runs', CYAN), (str(N - WRONG_N), 'guesses matched', GREEN), (str(WRONG_N), 'guesses wrong', RED),
           (str(MASKED_N), 'cases with a control nothing noticed', AMBER), (str(LIMIT_N), 'cases with a recorded limit', VIOLET)]))
story.append(Spacer(1, 3 * mm))
h2('What I found')
for i, (hd, tx) in enumerate(FINDINGS):
    add(KeepTogether([Paragraph(f'<font color="#1aa6c9">{i + 1}.</font>&nbsp;&nbsp;{esc(hd)}', S['h3']), Paragraph(esc(tx), S['body'])]))
story.append(CondPageBreak(110 * mm))
h2('All 48 cases on one page')
p('One square per case, grouped by the framework step it tests. Green means my guess matched. Red means it was wrong. An amber dot means a control in that case was one nothing noticed. A dark corner means I recorded a limit.')
add(ResultsMap(), Spacer(1, 2 * mm))
story.append(Paragraph('Figure 2.1  The 48 cases by framework step. Letters and numbers match the case ids in Chapters 5 to 11 (N01 is N-R14-01).', S['cap']))
h2('What I would do on Monday')
p('If you take only one page from the book, take this one. Each line is a check you can do without buying anything.')
add(*numbered(MONDAY))
story.append(Spacer(1, 2 * mm))
add(Callout('How far to trust all of this', 'The guesses and the models are mine. The results show that my reasoning holds together. They do not show that a product behaves this way. Chapter 3 says what the method cannot tell you.', 'warn'))

# ================================================================== 3 WHAT WE DID
chapter(3, 'What we did', 'Chapter 3', VIOLET, 'The procedure, the dates and the mistakes. Enough detail to repeat it.')
h2('The approach in one paragraph')
p('Pick a failure and a control that should stop it. Write what I expect with the control off and on. Hash the guess file and commit it. Only then write a small in-memory model of the control, run it twice, and compare. Switch each control off alone to see whether anything notices. Write down what the control cannot see. Run it again on a second machine and compare the output.')
h2('When it happened')
add(table([['Date', 'What happened'],
           ['31 October 2026', 'The use-case catalogue reached 187 rows (193 after six gap rows were added later). Draft guesses were written for rounds 14, 15 and 17. Nothing was hashed or run.'],
           ['2 November 2026, first run', 'Guess files hashed and committed on the Mac, then the models were written and run. 24 must-run cases and 3 gap cases from 2026 incident reports: 27 in all.'],
           ['2 November 2026, second-run guesses', '19 more cases: 13 stretch cases and 6 chain tests. Hashed on the Mac (40c2f87c…) and committed as 78d7e3e before any code.'],
           ['2 November 2026, second run', 'Code and results committed as 05235fe. The Mac output matched the build sandbox exactly.'],
           ['10 November 2026, third run', '2 more cases, NHI4 and NHI8. Guesses committed as e50df1b, code and results as ce3c57e. The Mac output matched the sandbox.'],
           ['2 November 2026, publishing', 'The lab page with 46 animated cases, this book, a 54-second silent video, and the framework, market, method, audit, roadmap and explainer pages.']],
          [46, 128], col_styles='first-bold'))
story.append(Spacer(1, 4 * mm))
h2('The procedure in one picture')
add(StepDiagram([
    [('Write the guess', 'Two lines per case: without the control, with it.', 'ok'), ('Hash the file', 'SHA-256 of the whole guess file.', 'ok'), ('Commit it', 'On its own, before any code exists.', 'ok')],
    [('Write the model', 'A small in-memory copy of the control.', ''), ('Run, control off', 'Compare with the guess.', ''), ('Run, control on', 'Compare with the guess.', ''),
     ('Switch each control off alone', 'Did anything notice?', 'violet'), ('Record misses and limits', 'Wrong guesses stay on the page.', '')],
    [('Run again on the Mac', 'Output must match the sandbox.', 'ok')]],
    box_h=24 * mm, gap=6 * mm, row_titles=['On the Mac: the record', 'In the build sandbox: the work', 'Back on the Mac: the check'], row_gap=5 * mm, bw_max=62 * mm))
story.append(Paragraph('Figure 3.1  Nine steps in three places. The rule that matters is that code comes after the commit. The numbers match the table below.', S['cap']))
h2('The steps, with what you should see')
add(table([['#', 'Step', 'Expected result'],
           ['1', '<b>Write the guess.</b> Numbers, not "better". Two lines per case.', 'A guess file. Nothing has been run.'],
           ['2', '<b>Hash the guess file.</b> <font name="Mono" size="7.8">shasum -a 256 guesses.md</font> on the Mac. Give it a file name, or the command waits for input.', 'A 64-character hash.'],
           ['3', '<b>Commit the file alone</b>, then note the commit.', 'A commit from before the code exists.'],
           ['4', '<b>Write the model.</b> In memory, made-up data only (a fictional bank, Kaveri Finance).', 'Code that runs with no network and no real system.'],
           ['5', '<b>Run with the control off.</b> Compare each result with the guess.', 'A match, or a mismatch recorded with both numbers.'],
           ['6', '<b>Run with the control on.</b> Compare.', 'A match, or a recorded mismatch.'],
           ['7', '<b>Switch each control off alone.</b> If the result does not change, no check noticed that control.', '"Noticed" or "masked" for each control.'],
           ['8', '<b>Write down the limit.</b> What can the control not see?', 'A limit line, or a note that I found none.'],
           ['9', '<b>Run again on a second machine</b> and compare the output.', 'Identical output. If not, stop and find out why.']],
          [8, 98, 68]))
story.append(Spacer(1, 3 * mm))
add(Callout('Careful with the commit', 'Commit only the guess file before the code. On my Mac I once ran git add with no paths, and I ran a hash command with no file name, which waits for input. Both were harmless and both cost time.', 'warn'))
h2('What the words mean')
add(table([['Term', 'Meaning in this book'],
           ['Match', 'The result equals what the guess said, in both runs.'],
           ['Wrong guess', 'A number or a ranking in the guess did not equal the result. The book keeps both.'],
           ['Noticed', 'Switching that one control off changed a result.'],
           ['Masked', 'Switching it off changed nothing, because another control covered it or the control did not matter in that case.'],
           ['Limit', 'What the control cannot see. Every case should have one.'],
           ['Chain test', 'A series of links an attacker needs. The test records which link each control stops.']],
          [32, 142], col_styles='first-bold'))
h2('The numbers')
add(Tiles([('27', 'first run: 25 matched, 2 wrong', CYAN), ('19', 'second run: 17 matched, 2 wrong', GREEN), ('2', 'third run: 1 matched, 1 wrong', CYAN), (str(MASKED_N), 'cases with a control nothing noticed', AMBER), ('3 of 3', 'runs that matched on the Mac', VIOLET)]))
story.append(Spacer(1, 3 * mm))
h2('What went wrong')
p('These are the mistakes, in the order they matter. The first five are wrong guesses. The last two are mistakes in my own test harness.')
add(table([['What went wrong', 'Case', 'What I did'],
           ['I guessed the scan would miss 1 secret. It missed 2.', 'S-R17-05', 'Recorded. The 2 misses were a secret split over two lines and one in base64.'],
           ['I guessed a short token lifetime would change the replay result.', 'N-R14-25', 'It did not. Binding and revoking already refused both replays. Recorded.'],
           ['My own arithmetic was wrong.', 'N-R14-07', 'Nine identities with two or three names each cannot make 51 entries. The count is 43. A rule that stripped trailing digits also merged two real accounts. Recorded.'],
           ['I guessed the ticket scan would matter most.', 'C-R16-C01', 'The owner rule did. Recorded.'],
           ['I guessed 3 alerts for 3 replays of a copied key.', 'N-R18-01', 'The model gave 1, because it raises one alert per new network and all 3 replays came from one network. Recorded.'],
           ['Bad test data on the first run.', 'N-R14-07', 'I had given 21 identities one shared owner, so the merge collapsed them to 11. I fixed the data and kept the first-run file as RESULTS-stretch-first-run.md.'],
           ['A harness slip.', 'C-R16-C04', 'An extra scenario ignored its "late" marker. I fixed it so the marker sets the attack day to 120, and re-ran.']],
          [58, 22, 94]))
story.append(Spacer(1, 3 * mm))
h2('Checking it again on 2 November 2026')
p('After the second run I re-ran everything in the build sandbox. The verify script printed 5 of 5 guess files match their recorded hash. Running run.py and run2.py gave results identical to the committed ones, except for the time stamp. The Mac output of the second run had already matched the sandbox.')
h2('What this method cannot tell you')
add(*bullets(['I wrote the guesses and the code. A match shows my model agrees with my reasoning. It does not show that a real product behaves that way.',
              'A hash proves the file did not change after I committed it. It does not prove when I wrote it, beyond the commit time.',
              'Chain tests are rule models. Each link is stopped by the controls I decided stop it, so the results follow from my rules.',
              'Three chain tests have an extra scenario I wrote after the fact to probe a limit. Each is marked as an extra.']))

# ================================================================== 4 FRAMEWORK
chapter(4, 'A framework for machine identities', 'Chapter 4', AMBER, 'Seven steps, drawn from what the cases showed. Targets and thresholds are yours to set.')
p('This framework is a draft method tested only on made-up data. Every one of the 48 cases sits in exactly one step. Where a number depends on your organisation, the book says so and leaves it for you to set.', 'lede')
h2('The seven steps')
rowsA = [[(f'{i + 1}. {n}', sub, 'info' if i % 2 == 0 else 'violet') for i, (k, n, sub) in enumerate(D.STAGES[:4])],
         [(f'{i + 5}. {n}', sub, 'bad' if k == 'retire' else ('info' if (i + 4) % 2 == 0 else 'violet')) for i, (k, n, sub) in enumerate(D.STAGES[4:])]]
add(StepDiagram(rowsA, box_h=27 * mm, gap=7 * mm, row_gap=6 * mm))
story.append(Paragraph('Figure 4.1  The seven steps in order. What you retire drops out of the next discovery scan, so step 7 feeds step 1 again.', S['cap']))
cnt = {k: sum(1 for c in CASES if c['stage'] == k) for k, _, _ in D.STAGES}
add(table([['Step', 'What to do', 'What you should see', 'Cases'],
           ['1. Find', 'One list from every source: directory, cloud, CI, SaaS, repositories, AI tools.', 'One list. Each row shows its source.', str(cnt['find'])],
           ['2. Own', 'A named person, a purpose and an end date for each identity. No owner means escalate, then stage for disable.', 'Every row has a person who can say what it is for.', str(cnt['own'])],
           ['3. Limit', 'Tier by blast radius. Least privilege. A front door that refuses the wrong caller.', 'A caller with the wrong identity or too much reach is refused, and the log says who asked.', str(cnt['limit'])],
           ['4. Store and issue', 'Values in the approved vault. Prefer short-lived and per-job credentials. Scan before commit.', 'No value in code, tickets or chat.', str(cnt['store'])],
           ['5. Rotate and expire', 'Update the consumer, rotate, then prove the old value is dead. Close the ticket after that.', 'The old value is refused and no application fails.', str(cnt['rotate'])],
           ['6. Watch', 'Log every use. Alert on the odd one: break-glass at 2 a.m., a grant used from a new place.', 'Someone is told the same day.', str(cnt['watch'])],
           ['7. Retire and respond', 'Monitor, disable with a rollback window, delete after a hold. After a vendor breach, revoke their grants.', 'Nothing deleted that someone needs. Access to a breached vendor ends inside your target time.', str(cnt['retire'])]],
          [30, 66, 66, 12], col_styles='first-bold'))
h2('Step 1 in detail: the inventory')
p('One row per identity. Keep the inventory out of wide circulation. It is a map of targets.')
add(table([['Field', 'Why it is there', 'Example (made up)'],
           ['Identity', 'The thing you can point at.', 'svc-billing-export'],
           ['Type', 'Service account, API key, token, certificate, workload or agent credential.', 'Service account'],
           ['Owner', 'One named person who answers for it. A team alias nobody reads does not count.', 'A person, with a backup'],
           ['Purpose', 'Lets a reviewer say yes or no without guessing.', 'Nightly billing export'],
           ['Tier', 'How much damage it can do. Decides review order.', 'Tier 1'],
           ['Permissions', 'What it can reach, and what it actually used.', 'Read on one database'],
           ['Secret type and location', 'Where the value lives and who can read it.', 'Password, in the approved vault'],
           ['Created, last used, expires', 'Age, idle time and end date. Missing last-use data is itself a finding.', 'Created 14 months ago, last used yesterday, no expiry'],
           ['Consumers', 'Who breaks if you change it.', 'Billing job, reporting app']],
          [38, 82, 54], col_styles='first-bold'))
h3('Flag these gaps')
add(*bullets(GAP_FLAGS))
p('Order the review by tier: Tier 0 and Tier 1 first. Tiers are a proposal. Tier 0 can control identity systems or all of production, Tier 1 reaches production data or systems, Tier 2 reaches little. Your organisation sets the real thresholds.')
h2('Deciding what to do with each credential')
p('Disabling can break something, so it needs the owner. Deleting or revoking cannot be undone, so list first, get approval and wait out a hold period.')
add(table([['Situation', 'Decision', 'Who approves', 'Flag'],
           ['No owner', 'Cannot be kept. Escalate, then stage for disable.', 'Platform owner', 'High impact'],
           ['Owner known, no expiry', 'Keep, and set an end date.', 'Owner', ''],
           ['Idle past the limit', 'Stage for disable. Do not delete yet. A quarterly job can look idle for months.', 'Owner, platform owner', 'High impact'],
           ['Broader than its use', 'Reduce permissions, or replace with a short-lived or workload identity.', 'Owner', ''],
           ['Long-lived key in CI', 'Replace with a per-job, short-lived credential.', 'Pipeline owner', ''],
           ['Secret outside the approved store', 'Move it, then rotate it. Copies elsewhere may already exist.', 'Owner', ''],
           ['Secret exposed', 'Treat as compromised. Follow the leak steps below.', 'Security lead', 'High impact'],
           ['Signing or CA key', 'Roll forward only. Revoking first breaks everything it signed.', 'Platform owner', 'Irreversible']],
          [40, 76, 34, 24], col_styles='first-bold'))
h2('Retire in stages')
p('Turn it off before you throw it away. If someone shouts, turn it back on. Delete only after the hold period.')
add(StepDiagram([[('Monitor', 'Watch for any use. Change nothing yet.', ''), ('Disable', 'Turn it off, keep it. Rollback ready. Owner approves.', 'warn'),
                  ('Hold', 'Wait. The owner sets the length. Re-enable if someone needs it.', ''), ('Delete', 'Cannot be undone. Owner approves, backup taken.', 'bad')]],
                box_h=30 * mm, gap=7 * mm))
story.append(Paragraph('Figure 4.2  Four stages. Only the last cannot be reversed. I have not set a hold length. That is your decision.', S['cap']))
h2('When a secret leaks')
p('Do not wait for proof of misuse. Assume somebody copied it.')
add(StepDiagram([[('Treat as exposed', 'Do not wait for proof of misuse.', 'bad'), ('Find the users', 'List every app, job and person that uses it.', ''), ('Issue a new value', 'Roll forward. The old one still works.', 'warn')],
                 [('Update the users', 'Each one confirmed on the new value.', ''), ('Revoke the old value', 'Only after every user is confirmed.', 'bad'), ('Check the logs', 'Look for use since the day it leaked.', 'ok')]],
                box_h=25 * mm, gap=7 * mm, row_gap=6 * mm))
story.append(Paragraph('Figure 4.3  Six steps. Step 5 cannot be undone, so it comes after every user has moved. Signing keys and CA keys are roll-forward only.', S['cap']))
add(Callout('Never do this', 'Rotate the leaked key and leave the old one valid. The lab showed the same mistake in another form: 5 rotation tickets were closed while 2 old secrets still worked (N-R14-20).', 'bad'))
h2('Standards for new credentials')
p('Start clean and you do not have to clean up later.')
add(*numbered(STANDARDS))
p('In the lab, a front door that refused new identities without an owner, scope and expiry (N-R14-18) stopped the problem at creation. A weekly sweep also disabled expired keys (S-R17-04).')
h2('Metrics')
p('Count from your own data. I have left the targets for you.')
add(table([['Metric', 'How to count it', 'Target', 'Lab example'],
           ['Identities with a named owner', 'Owned identities divided by all identities', 'You set it', 'A key with no owner was paused on day 31 (N-R14-09)'],
           ['Identities with an end date', 'Identities with an expiry divided by all', 'You set it', 'Ghost credential refused at creation (S-R17-04)'],
           ['Time to cut a breached vendor', 'Minutes from notice to revoked grants', 'You set it', '60 minutes in the model; a replay at minute 30 still worked (N-R14-23)'],
           ['Failed rotations noticed within a day', 'Alerts raised divided by failures', 'You set it', 'Alert on day 1 instead of day 60 (N-R14-14)'],
           ['Secrets caught before commit', 'Blocked divided by planted', 'You set it', '6 of 8 blocked; 2 got through (S-R17-05)']],
          [42, 48, 20, 64], col_styles='first-bold'))
story.append(Paragraph('The lab numbers come from small models and prove nothing about your estate.', S['cap']))
h2('OWASP Non-Human Identities Top 10 (2025)')
p(f'OWASP publishes a Top 10 for non-human identities {src_ref("S8")}. I mapped each risk to the lab cases that touch it. Two have thin coverage: insecure authentication (NHI4) and environment isolation (NHI8). They are the next cases to write.')
add(table([['OWASP risk', 'Lab cases', 'Coverage']] + [[f'<b>{code}</b> {esc(name)}', esc(', '.join(ids.split())), esc(cov)] for code, name, ids, cov in D.OWASP],
          [58, 74, 42]))
story.append(Paragraph('I read OWASP\'s risk names for this mapping. The mapping is mine and is not an OWASP endorsement.', S['cap']))
h2('What is left for you to set')
add(*bullets(['Tier thresholds, idle limits and the hold period. Your organisation sets them. They are not set here.',
              'Reference points I read while building the method: the OWASP list above, and the identity and access controls in NIST SP 800-53 and ISO/IEC 27001. I name them as reading. I do not quote their text and I do not claim alignment.',
              'Not yet tested: cloud-specific key habits, Kubernetes workload identity, and any real product.']))

# ================================================================== 5 to 11 CASES
for i, (k, name, sub) in enumerate(D.STAGES):
    cs = [c for c in CASES if c['stage'] == k]
    intro, shows, ask = STEP_INTRO[k]
    chapter(5 + i, f'Step {i + 1}: {name}', f'Chapter {5 + i}  ·  Framework step {i + 1} of 7', hexc(STAGE_COLOR[k]), sub + '.')
    p(esc(intro), 'lede')
    h3('What the cases in this step showed')
    add(*bullets([esc(x) for x in shows]))
    add(Callout('A question to ask', ask, 'info'))
    story.append(Spacer(1, 2 * mm))
    p(f'{len(cs)} case' + ('s' if len(cs) != 1 else '') + ' follow. ' + ('Guesses that were wrong: ' + ', '.join(c['id'] for c in cs if c['wrong']) + '. ' if any(c['wrong'] for c in cs) else 'All guesses in this step matched. ') + ('Controls nothing noticed: ' + ', '.join(c['id'] for c in cs if c['masked']) + '.' if any(c['masked'] for c in cs) else ''), 'small')
    add(Legend(), Spacer(1, 3 * mm))
    for c in cs:
        blk = case_block(c); story.extend(blk if c is not cs[-1] else blk[:-1])

# ================================================================== 12 RESULTS
chapter(12, 'Results', 'Chapter 12', RED, 'What matched, what was wrong, what nothing noticed, and what each control cannot see.')
h2('By framework step')
rows = [['Step', 'Cases', 'Matched', 'Wrong', 'Control masked', 'Limit recorded']]
for k, n, _ in D.STAGES:
    cs = [c for c in CASES if c['stage'] == k]
    rows.append([n, str(len(cs)), str(sum(not c['wrong'] for c in cs)), str(sum(c['wrong'] for c in cs)), str(sum(bool(c['masked']) for c in cs)), str(sum(bool(c['limit']) for c in cs))])
rows.append(['<b>All</b>', f'<b>{N}</b>', f'<b>{N - WRONG_N}</b>', f'<b>{WRONG_N}</b>', f'<b>{MASKED_N}</b>', f'<b>{LIMIT_N}</b>'])
add(table(rows, [54, 24, 24, 24, 24, 24], col_styles='first-bold'))
story.append(Spacer(1, 4 * mm))
h2('The five wrong guesses')
p('A wrong guess is the most useful thing the lab produced. Each is recorded with what I wrote and what happened.')
add(table([['Case', 'What I wrote', 'What happened']] + [[f'<b>{cid}</b><br/>{esc(BYID[cid]["title"])}', esc(a), esc(b)] for cid, (a, b) in WRONG.items()], [42, 60, 72]))
story.append(Spacer(1, 4 * mm))
h2('Controls that nothing noticed')
p(f'In {MASKED_N} cases at least one control could be switched off alone and nothing changed. That means another control was doing the same job, or this control did not matter in that case. In both cases you cannot tell it is working by looking at the result.')
mrows = [['Case', 'Control(s) masked', 'Switched off alone, noticed instead']]
for c in CASES:
    if c['masked']:
        seen = [clabel(k) for k, v in c['noticed'].items() if v]
        mrows.append([f'<b>{c["id"]}</b><br/>{esc(c["title"])}', esc('; '.join(clabel(k) for k in c['masked'])), esc('; '.join(seen) if seen else 'None. Every control was masked by another.')])
add(table(mrows, [52, 62, 60]))
story.append(Spacer(1, 4 * mm))
h2('Limits I recorded')
p('A limit is what the control cannot see. These 14 are written down. The other 34 cases have no limit recorded, which is not the same as having none.')
lrows = [['Case', 'What the control cannot see']] + [[f'<b>{c["id"]}</b><br/>{esc(c["title"])}', esc(c['limit'][:1].upper() + c['limit'][1:] + ('' if c['limit'].endswith('.') else '.'))] for c in CASES if c['limit']]
add(table(lrows, [60, 114]))
h2('What the numbers do not say')
add(*bullets(['That any product passes or fails. I tested none.',
              'That a control is worth its cost. I have no cost data.',
              'That 43 of 48 is a good score. The guesses and models are mine, so it is a consistency check.',
              'That the 34 cases with no recorded limit have no limit.']))

# ================================================================== 13 MARKET
chapter(13, 'The market in 2026', 'Chapter 13', CYAN, 'Four deals, one new identity type and a standards project. Checked on 2 November 2026.')
p('In the first half of 2026, four deals closed in which larger security companies bought privileged access, machine access or non-human identity specialists. Microsoft documented identity objects for AI agents. NIST asked the public how to identify and authorize agents. Each fact below has a date, a source and a label for how far I trust it.', 'lede')
add(Tiles([('4', 'acquisitions closed, 11 Feb to 29 Jun 2026', GREEN), ('600+', 'commenters on NIST\'s agent identity concept paper', CYAN), ('10', 'risks in the OWASP NHI Top 10 (2025)', VIOLET), ('0', 'products I tested', AMBER)]))
story.append(Spacer(1, 3 * mm))
h2('How to read the labels')
p('<b>Primary</b>: the party\'s own page or document. <b>Secondary</b>: someone else reporting or analysing it. <b>Vendor</b>: a sales or press statement I could not check. <b>Opinion</b>: a view and not a measurement. The trust label (high, medium or low) says how much I would rely on it. Prices, ownership and roadmaps are the facts most likely to be wrong or to change. Check the vendor\'s own document before you quote any of them.')
h2('The timeline')
add(Timeline())
story.append(Paragraph('Figure 13.1  Events in this chapter. Green: deals. Cyan: NIST. Violet: Microsoft. Red: the Drift incident.', S['cap']))
h2('Who bought whom in 2026')
add(table([['Closed', 'Buyer', 'Bought', 'What the target did', 'Terms', 'How I know'],
           ['11 Feb 2026', 'Palo Alto Networks', 'CyberArk', 'Privileged access and machine identity', '$45.00 cash plus 2.2005 Palo Alto shares per CyberArk share', 'Buyer\'s release [S1], primary'],
           ['5 Mar 2026', 'Delinea', 'StrongDM', 'Access for engineering, DevOps and AI environments', 'Not read', 'Buyer\'s release [S2], primary. A data aggregator says 15 Jan [S6]. I used the release.'],
           ['29 Jun 2026', 'SailPoint', 'Entro Security', 'Non-human identity and credentials security, Tel Aviv', 'Not disclosed', 'Buyer\'s release [S3], primary'],
           ['29 Jun 2026', 'Cisco', 'Astrix Security', 'Non-human identity security', 'Not stated in what I read. About $400 million is reported.', 'Closing: Cisco blog update [S4], primary. Announcement 4 May and the price: CSA note [S5], secondary.']],
          [20, 24, 22, 34, 36, 38]))
story.append(Spacer(1, 3 * mm))
p('<b>What I take from it (my view).</b> The platform vendors want machine identity inside their platform. Two of the four targets, Entro and Astrix, were non-human identity specialists. StrongDM sold access for engineering teams, and CyberArk sold privileged access. If you chose a specialist a year ago, ask the new owner for the product roadmap in writing. I have not seen any of those roadmaps.')
add(Callout('Where sources disagree', 'A data aggregator lists the Delinea and StrongDM deal on 15 January 2026 [S6]. Delinea\'s own release says it completed on 5 March 2026 [S2]. I used the company\'s release.', 'warn'))
h2('AI agents get their own identity objects')
p(f'Microsoft\'s documentation for Entra Agent ID, last updated 1 May 2026, describes an agent identity as a special service principal. It has no credentials of its own. A reusable template called a blueprint creates it and acquires tokens for it. It can record a sponsor, the person or group accountable for the agent, who is contacted if there is an incident {src_ref("S7")}. This is vendor documentation: it describes the product and not how well it works.')
p('Why it matters here: in the lab, four agents shared one team key, so the log said only "team key" and a revoke hit all four (N-R14-21). With one key per agent, the log named the agent and the revoke hit one. A sponsor plus an identity per agent is the product-side version of that control. I tested a model of the idea. I did not test Entra.')
h2('Standards and guidance')
h3('OWASP Non-Human Identities Top 10, 2025')
p(f'The ten risks, in OWASP\'s order {src_ref("S8")}: ' + '; '.join(f'{c} {n}' for c, n, _, _ in D.OWASP) + '. Chapter 4 maps each one to the lab cases.')
h3('NIST NCCoE: software and AI agent identity and authorization')
p(f'NIST\'s National Cybersecurity Center of Excellence published a concept paper on 5 February 2026 and took comments until 2 April 2026 {src_ref("S9")}. In September 2026 NIST said it had heard from more than 600 commenters, and that its DevSecOps project will provide the first implementation use case: showing how AI agents can be identified, authenticated and authorized in the software development lifecycle {src_ref("S10")}. A concept paper is not guidance. No control in it is yet something you can be audited against.')
h2('The Salesloft Drift incident')
p(f'Google\'s threat intelligence group reported that, from as early as 8 August 2025 through at least 18 August 2025, an actor it tracks as UNC6395 used stolen OAuth tokens tied to the Salesloft Drift app to read data in customers\' Salesforce accounts. Google saw the actor look for AWS access keys, passwords and Snowflake tokens. Salesloft and Salesforce revoked all active access and refresh tokens on 20 August 2025. On 28 August Google added that tokens for Drift\'s email integration were also compromised and advised customers to treat every token connected to Drift as potentially compromised {src_ref("S11")}. An AppOmni post says more than 700 organizations were affected and cites an FBI advisory {src_ref("S12")}. I have not seen the FBI document.')
add(Callout('Where sources disagree', 'One vendor blog dates the same campaign to June 2026 [S13]. Google\'s advisory says August 2025 [S11]. I used Google and left the other out of the facts.', 'warn'))
h2('Other signals, with lower weight')
add(*bullets([f'Tuhin Banerjee argues on the Cloud Security Alliance blog (23 April 2026) that inventory-first discovery is losing ground to short-lived identities, and that ownership and fast revocation are the neglected parts {src_ref("S14")}. Opinion.',
              f'Vercel confirmed unauthorized access in April 2026. Reports say it began with a third-party AI app that an employee had linked with broad permissions {src_ref("S15")}. Secondary, low trust.',
              f'GitGuardian\'s 2026 report counts 28,649,024 new secrets on public GitHub, 1,275,105 of them AI-service secrets, and 24,008 unique secrets in MCP configuration files {src_ref("S16")}. Vendor research.',
              f'Palo Alto Networks says machine identities outnumber human identities by more than 80 to 1, and that nearly 90% of organizations have suffered an identity-centric breach {src_ref("S1")}. These are the company\'s statistics in a press release. I did not find the underlying study.']))
h2('What I think the market still misses')
p('This is my reading of the lab and not a survey.')
add(table([['Gap', 'What the lab saw', 'Cases'],
           ['Checks that a sign-off is true', 'Owner attestations, break-glass justifications and ticket numbers were accepted as text in my models. I suspect many real workflows are the same.', 'N-R14-11, P-R15-11, P-R15-13'],
           ['Speed of revocation across companies', 'After a vendor breach the clock starts at their notice and not at your inventory. In the model, a replay at minute 30 still worked.', 'N-R14-23, N-R14-05'],
           ['Identities that live for minutes', 'A weekly inventory cannot see a token that lasts an hour. The short lifetime did not matter once binding and revoke were on, which is a reminder to test it alone.', 'N-R14-25'],
           ['One view of agent, person and inherited permissions', 'An AI tool inherited 40 folders when it needed one. An automation using a person\'s login made the log unreadable.', 'S-R17-02, S-R17-03']],
          [44, 92, 38], col_styles='first-bold'))
h2('What I did not check')
add(*bullets(['Analyst reports (Gartner, Forrester, KuppingerCole). They are licensed and I did not read them.',
              'Any product. I tested none, so I make no claim about what a product does today.',
              'Pricing beyond what the press releases state. Cisco and Astrix is reported and not confirmed.',
              'Okta, Microsoft Defender, Ping and the secrets managers, beyond one Microsoft document.',
              'The FBI advisory on the Salesloft Drift campaign. I only saw it cited.']))
p('The full source list is in Appendix C. I plan to re-check this chapter every quarter.')

# ================================================================== 14 MISSING
chapter(14, 'What is missing', 'Chapter 14', AMBER, 'The gaps I know about. A book that hid them would be weaker.')
add(table([['Gap', 'Detail']] + [[f'<b>{esc(a)}</b>', esc(b)] for a, b in MISSING], [58, 116]))
story.append(Spacer(1, 4 * mm))
add(Callout('Where you can help', 'If you work on identity or privileged access and you think a case is wrong, or you can think of a variant that breaks a control, tell me. I will add it and keep the original on the page. If you would like to write guesses for a case before you see mine, I would like that most of all.', 'violet'))

# ================================================================== 15 ROADMAP
chapter(15, 'Roadmap', 'Chapter 15', GREEN, 'What is done, what I am checking, and what comes next. No invented deadlines.')
p('I have not put dates on the future items. A date I cannot keep is a claim I cannot back, so the order is the plan. Posting anything publicly waits for my own go.', 'lede')
LANE_COL = {'done': GREEN, 'now': CYAN, 'next': AMBER, 'later': VIOLET}
for key, title, items in LANES:
    h3(f'{title}  ({len(items)})')
    add(table([['When', 'Item', 'Detail']] + [[esc(w), f'<b>{esc(t.replace(chr(82)+"oshan"+chr(39)+"s read", "My read"))}</b>', esc(d)] for w, t, d in items], [28, 52, 94], zebra=True))
    story.append(Spacer(1, 2 * mm))
h2('Rules I follow for every item')
add(*numbered(['Guesses first. Write what I expect, hash it, commit it, then write the code.',
               'Wrong guesses stay on the page next to the right answer.',
               'Every case gets a limit: what the control cannot see.',
               'Market facts get a date, a source and a trust label. If I cannot check one, I say so.',
               'No product is tested, so none is endorsed or criticised.']))

# ================================================================== APPENDICES
chapter('A', 'Guess files and hashes', 'Appendix A', NAVY, 'The evidence that the guesses came first.')
p('Each guess file was hashed with SHA-256 on the Mac and committed before the code for those cases existed. The hashes below are the ones recorded at the time. You can recompute them yourself.')
hrows = [['File', 'Cases', 'SHA-256']]
for key, (fn, label, h) in D.GUESS_FILES.items():
    n = sum(1 for c in CASES if c['guess_file'] == fn)
    hrows.append([f'<font name="Mono" size="7.4">{esc(fn)}</font><br/>{esc(label)}', str(n), f'<font name="Mono" size="6.9">{h[:32]}<br/>{h[32:]}</font>'])
add(table(hrows, [56, 14, 104]))
story.append(Spacer(1, 3 * mm))
h3('Commits on the Mac')
add(table([['Commit', 'What it holds'],
           ['<font name="Mono" size="8">7737a2c</font>, <font name="Mono" size="8">314d4ee</font>', 'First run: guess files and code.'],
           ['<font name="Mono" size="8">474ddc9</font>', 'The three gap-case guesses.'],
           ['<font name="Mono" size="8">f902ea8</font>', 'First run. I did not record which file it holds.'],
           ['<font name="Mono" size="8">78d7e3e</font>', 'Second-run guesses (13 stretch cases and 6 chain tests), before any code.'],
           ['<font name="Mono" size="8">05235fe</font>', 'Second-run code and results.'],
           ['<font name="Mono" size="8">e50df1b</font>', 'Round 18 guesses (2 cases), before any code.'],
           ['<font name="Mono" size="8">ce3c57e</font>', 'Round 18 code and results.']], [40, 134]))
story.append(Paragraph('A hash proves a file did not change after the commit. It does not prove when I wrote it. The commit time is the only date evidence, and I did not record those times.', S['cap']))
h3('Check them yourself')
add(table([['Step', 'Do this', 'You should see'],
           ['1', 'Download <font name="Mono" size="7.8">nhi-lab/evidence/</font> from the repository.', 'A folder with guesses/, cases.py, run.py, cases2.py, run2.py, cases3.py, run3.py and verify.py.'],
           ['2', 'Run <font name="Mono" size="7.8">python3 verify.py</font> in that folder.', '"5 of 5 guess files match the recorded hash." Tested in the build sandbox on 2 November 2026.'],
           ['3', 'Run <font name="Mono" size="7.8">python3 run.py</font> <font name="Mono" size="7.8">python3 run2.py</font> then <font name="Mono" size="7.8">python3 run3.py</font>. They need only Python 3 and check the hashes first.', 'The tables in RESULTS.md and RESULTS-stretch.md. On 2 November 2026 the results were identical to the committed ones except for the time stamp.']],
          [12, 74, 88]))

chapter('B', 'Audit table', 'Appendix B', NAVY, 'All 48 cases in one table. The same data is on the website as CSV and JSON.')
arows = [['Case', 'Title', 'Step', 'Run', 'Guess', 'Masked', 'Limit']]
for c in CASES:
    arows.append([f'<font name="Mono" size="7.4">{c["id"]}</font>', esc(c['title']), esc(STEPS[c['stage']][0]), str(c['run']),
                  '<font color="#c93a53"><b>wrong</b></font>' if c['wrong'] else 'matched', ('yes' if c['masked'] else ''), ('yes' if c['limit'] else '')])
add(table(arows, [24, 66, 30, 9, 17, 14, 14]))
story.append(Paragraph('Masked: at least one control could be switched off alone with no change. Limit: a limit is written down for the case. Download the full table, with 16 columns, from roshantrivedi.co.in/nhi-lab/audit/.', S['cap']))

chapter('C', 'Sources', 'Appendix C', NAVY, 'Every source used in the market chapter. Retrieved 2 November 2026 unless noted.')
srows = [['#', 'Title and note', 'Publisher and date', 'Type', 'Trust']]
for i, (t, pub, d, u, k, cf, n) in SRC.items():
    ln = link(u, t) if u else esc(t)
    srows.append([i[1:], f'{ln}<br/><font size="7.6" color="#5b6785">{esc(n)}</font>', f'{esc(pub)}<br/>{esc(d)}', k, {'med': 'medium'}.get(cf, cf)])
add(table(srows, [8, 92, 42, 17, 15]))
story.append(Spacer(1, 3 * mm))
h3('Other reading')
add(*bullets(['OWASP Top 10 for Agentic Applications (2026). I read a summary by Teleport, so check the OWASP original before quoting.',
              'Wiz blog on a Non-Human Identities dashboard (February 2024), the Clutch Security page on Okta integrations, and SailPoint\'s Entro documentation. These are vendor descriptions and I did not test any of them.']))

chapter('D', 'Glossary', 'Appendix D', NAVY, 'The words used in this book.')
add(table([['Term', 'Meaning']] + [[f'<b>{esc(a)}</b>', esc(b)] for a, b in GLOSSARY], [46, 128]))

chapter('', 'About the author', 'Author', CYAN, 'Roshan Trivedi, Bengaluru.')
p('I make secure access something people can actually use. I have spent fourteen years in identity and privileged access, and I now own an enterprise credential-management platform and its privileged access product. In practice that means architecture, service design, standards and the roadmap, and just as much the work of getting teams to adopt it and being able to show an auditor how it works.', 'lede')
p('Most of my thinking lately goes into one question: what happens to identity when the user is a service account, a pipeline or an AI agent? This lab is one answer, tested in public, with the mistakes left in.')
p('The case studies and labs on my site are anonymised. They leave out employers, clients and internal data on purpose.')
add(Callout('How to cite this book', 'Roshan Trivedi, "Machine identities, tested in public", edition 2, ' + EDITION_DATE + '. roshantrivedi.co.in/nhi-lab/. Creative Commons Attribution 4.0 (CC BY 4.0). You may share and adapt it, including commercially, if you credit "Roshan Trivedi, roshantrivedi.co.in" and link to the licence.', 'info'))
story.append(Spacer(1, 2 * mm))
add(Callout('What this book is not', 'It is not legal advice, a compliance claim or a product review. Mappings to OWASP, NIST and ISO are my own reading. All data is made up.', 'warn'))

add(NextPageTemplate('back'), PageBreak(), Spacer(1, 1))

# ------------------------------------------------------------------ build
doc = Book(OUT)
doc.multiBuild(story)
print('wrote', OUT, os.path.getsize(OUT), 'bytes')
