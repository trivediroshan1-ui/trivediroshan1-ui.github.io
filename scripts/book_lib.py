"""Drawing and layout helpers for the NHI lab book (reportlab).
Fonts: Carlito for text, Caladea Bold for headings, Liberation Mono for hashes. All are TrueType files
that ship with the build machine, so the PDF embeds them."""
import re, random, hashlib
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle,
                                KeepTogether, NextPageTemplate, Flowable, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents

FD = '/usr/share/fonts/truetype/crosextra/'
LM = '/usr/share/fonts/truetype/liberation/'
pdfmetrics.registerFont(TTFont('Body', FD + 'Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('BodyB', FD + 'Carlito-Bold.ttf'))
pdfmetrics.registerFont(TTFont('BodyI', FD + 'Carlito-Italic.ttf'))
pdfmetrics.registerFont(TTFont('BodyBI', FD + 'Carlito-BoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('Head', FD + 'Caladea-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Mono', LM + 'LiberationMono-Regular.ttf'))
pdfmetrics.registerFont(TTFont('MonoB', LM + 'LiberationMono-Bold.ttf'))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyB', italic='BodyI', boldItalic='BodyBI')
pdfmetrics.registerFontFamily('Mono', normal='Mono', bold='MonoB', italic='Mono', boldItalic='MonoB')

W, H = A4
LEFT = RIGHT = 18 * mm
CW = W - LEFT - RIGHT          # content width, 174 mm

NAVY = colors.HexColor('#0b1530'); INK = colors.HexColor('#16213e'); MUTED = colors.HexColor('#5b6785')
CYAN = colors.HexColor('#1aa6c9'); RED = colors.HexColor('#c93a53'); GREEN = colors.HexColor('#1a8a66')
AMBER = colors.HexColor('#c98a1b'); VIOLET = colors.HexColor('#6d5bd0'); LINE = colors.HexColor('#d5dcec')
SOFT = colors.HexColor('#f3f6fc'); SOFT2 = colors.HexColor('#e9eef8')
REDT = colors.HexColor('#fdecef'); GREENT = colors.HexColor('#e6f5ef'); AMBERT = colors.HexColor('#fcf1d9')
BLUET = colors.HexColor('#e4f4fa'); VIOLT = colors.HexColor('#eeeafc')

STAGE_COLOR = {'find': '#1aa6c9', 'own': '#1a8a66', 'limit': '#c98a1b', 'store': '#6d5bd0',
               'rotate': '#2d6fd4', 'watch': '#c93a53', 'retire': '#7a5a3a'}

def hexc(h): return colors.HexColor(h)

def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# ---------------------------------------------------------------- styles
def st(name, **k):
    base = dict(fontName='Body', fontSize=10.5, leading=15.4, textColor=INK, spaceAfter=6)
    base.update(k)
    return ParagraphStyle(name, **base)

S = dict(
    body=st('body'),
    lede=st('lede', fontSize=12.6, leading=18.4, textColor=INK, spaceAfter=9),
    small=st('small', fontSize=8.6, leading=11.8, textColor=MUTED, spaceAfter=3),
    tiny=st('tiny', fontSize=7.4, leading=9.6, textColor=MUTED, spaceAfter=0),
    h2=st('H2', fontName='Head', fontSize=18, leading=22, spaceBefore=14, spaceAfter=6, textColor=NAVY, keepWithNext=1),
    h3=st('H3', fontName='BodyB', fontSize=12.4, leading=16, spaceBefore=8, spaceAfter=3, textColor=NAVY, keepWithNext=1),
    cap=st('cap', fontName='BodyI', fontSize=8.8, leading=12, textColor=MUTED, spaceBefore=2, spaceAfter=8),
    cell=st('cell', fontSize=8.8, leading=11.6, spaceAfter=0),
    cellb=st('cellb', fontName='BodyB', fontSize=8.8, leading=11.6, spaceAfter=0),
    cellh=st('cellh', fontName='BodyB', fontSize=8.2, leading=10.4, spaceAfter=0, textColor=colors.white),
    mono=st('mono', fontName='Mono', fontSize=7.6, leading=10.4, textColor=INK, spaceAfter=0),
    bullet=st('bullet', leftIndent=13, bulletIndent=2, spaceAfter=3.5),
    num=st('num', leftIndent=17, bulletIndent=0, spaceAfter=4.5),
    tocL0=st('tocL0', fontName='BodyB', fontSize=10.8, leading=13.4, spaceBefore=4, spaceAfter=0, textColor=NAVY),
    tocL1=st('tocL1', fontSize=9, leading=11, leftIndent=12, spaceAfter=0, textColor=INK),
    casehead=st('CaseH', fontName='Head', fontSize=14, leading=17, spaceBefore=0, spaceAfter=2, textColor=NAVY, keepWithNext=1),
    note=st('note', fontSize=9.6, leading=13.6, spaceAfter=0),
)

def P(t, s='body'): return Paragraph(t, S[s] if isinstance(s, str) else s)
def bullets(items, s='bullet'):
    return [Paragraph(t, S[s], bulletText='•') for t in items]
def numbered(items):
    return [Paragraph(t, S['num'], bulletText=f'{i + 1}.') for i, t in enumerate(items)]

# ---------------------------------------------------------------- small flowables
class Callout(Flowable):
    """Boxed note with a coloured bar on the left."""
    def __init__(self, title, text, kind='info'):
        super().__init__()
        self.kind = kind; self.title = title; self.text = text
        self.col, self.tint = {'info': (CYAN, BLUET), 'good': (GREEN, GREENT), 'warn': (AMBER, AMBERT),
                               'bad': (RED, REDT), 'violet': (VIOLET, VIOLT)}[kind]
    def wrap(self, aw, ah):
        self.w = aw
        self.p = Paragraph(f'<font name="BodyB" color="{self.col.hexval()}">{esc(self.title)}</font><br/>{self.text}', S['note'])
        pw, ph = self.p.wrap(aw - 11 * mm, ah)
        self.h = ph + 7 * mm
        return aw, self.h + 3 * mm
    def split(self, aw, ah): return []
    def draw(self):
        c = self.canv; c.saveState()
        c.setFillColor(self.tint); c.roundRect(0, 1.5 * mm, self.w, self.h, 2 * mm, 0, 1)
        c.setFillColor(self.col); c.roundRect(0, 1.5 * mm, 1.8 * mm, self.h, 0.9 * mm, 0, 1)
        self.p.drawOn(c, 6 * mm, 1.5 * mm + 3.5 * mm)
        c.restoreState()

class Tiles(Flowable):
    """A row of big-number tiles."""
    def __init__(self, items, h=24 * mm):
        super().__init__(); self.items = items; self.h = h
    def wrap(self, aw, ah): self.w = aw; return aw, self.h + 3 * mm
    def draw(self):
        c = self.canv; n = len(self.items); gap = 3 * mm; bw = (self.w - gap * (n - 1)) / n
        for i, (num, label, col) in enumerate(self.items):
            x = i * (bw + gap)
            c.setFillColor(SOFT); c.roundRect(x, 1.5 * mm, bw, self.h, 2.4 * mm, 0, 1)
            c.setFillColor(col); c.roundRect(x, 1.5 * mm + self.h - 1.6 * mm, bw, 1.6 * mm, 0.8 * mm, 0, 1)
            c.setFont('Head', 22); c.drawString(x + 3.5 * mm, 1.5 * mm + self.h - 12.5 * mm, str(num))
            lines = simpleSplit(label, 'Body', 8.2, bw - 7 * mm)
            c.setFont('Body', 8.2); c.setFillColor(INK)
            for k, ln in enumerate(lines[:3]):
                c.drawString(x + 3.5 * mm, 1.5 * mm + self.h - 18.2 * mm - k * 3.7 * mm, ln)

class ChapterHead(Flowable):
    """Full-bleed band that opens a chapter."""
    def __init__(self, num, title, kicker, color=CYAN, sub=''):
        super().__init__(); self.num, self.title, self.kicker, self.color, self.sub = num, title, kicker, color, sub
        self.bookmark = None
    def wrap(self, aw, ah):
        self.w = aw; self.lines = simpleSplit(self.title, 'Head', 28, aw - 34 * mm)
        self.h = 36 * mm + 11 * mm * len(self.lines) / 1.0 - 6 * mm
        return aw, self.h + 6 * mm
    def draw(self):
        c = self.canv; c.saveState()
        x0 = -LEFT; ww = self.w + LEFT + RIGHT
        c.setFillColor(NAVY); c.rect(x0, 0, ww, self.h, 0, 1)
        c.setFillColor(self.color); c.rect(x0, 0, 4 * mm, self.h, 0, 1)
        c.setFont('Head', 62); c.setFillColor(self.color)
        if self.num != '':
            c.drawString(0, self.h - 27 * mm, str(self.num))
        tx = 26 * mm if self.num != '' else 0
        c.setFont('BodyB', 8.6); c.setFillColor(colors.HexColor('#9fb0d4'))
        c.drawString(tx, self.h - 10.5 * mm, self.kicker.upper())
        c.setFont('Head', 28); c.setFillColor(colors.white)
        y = self.h - 20.5 * mm
        for ln in self.lines:
            c.drawString(tx, y, ln); y -= 11 * mm
        if self.sub:
            c.setFont('Body', 10.5); c.setFillColor(colors.HexColor('#c8d3ee'))
            for j, ln in enumerate(simpleSplit(self.sub, 'Body', 10.5, self.w - tx - 6 * mm)[:2]):
                c.drawString(tx, y + 1 * mm - j * 4.6 * mm, ln)
        c.restoreState()

class ChapterMark(Flowable):
    def __init__(self, title): super().__init__(); self.title = title
    def wrap(self, aw, ah): return 0, 0
    def draw(self): pass

class Rule(Flowable):
    def __init__(self, color=LINE, w=None): super().__init__(); self.color = color
    def wrap(self, aw, ah): self.w = aw; return aw, 3 * mm
    def draw(self):
        self.canv.setStrokeColor(self.color); self.canv.setLineWidth(0.6); self.canv.line(0, 1.5 * mm, self.w, 1.5 * mm)

# ---------------------------------------------------------------- drawing primitives
def tri(c, x, y, ang, size=2.2 * mm):
    import math
    p = c.beginPath()
    a = math.radians(ang)
    pts = [(0, 0), (-size, size * 0.42), (-size, -size * 0.42)]
    for i, (px, py) in enumerate(pts):
        rx = x + px * math.cos(a) - py * math.sin(a); ry = y + px * math.sin(a) + py * math.cos(a)
        (p.moveTo if i == 0 else p.lineTo)(rx, ry)
    p.close(); c.drawPath(p, fill=1, stroke=0)

def arrow(c, pts, color=MUTED, lw=1.1, dash=None):
    """Polyline with an arrow head on the last segment. pts in points."""
    import math
    c.saveState(); c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(lw)
    if dash: c.setDash(*dash)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    hx, hy = x2 - 2.0 * mm * math.cos(math.radians(ang)), y2 - 2.0 * mm * math.sin(math.radians(ang))
    pp = list(pts[:-1]) + [(hx, hy)]
    p = c.beginPath(); p.moveTo(*pp[0])
    for q in pp[1:]: p.lineTo(*q)
    c.drawPath(p, fill=0, stroke=1)
    c.setDash(); tri(c, x2, y2, ang)
    c.restoreState()

def rbox(c, x, y, w, h, fill=SOFT, stroke=None, r=2 * mm, lw=0.8, dash=None):
    c.saveState(); c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
        if dash: c.setDash(*dash)
    c.roundRect(x, y, w, h, r, 1 if stroke is not None else 0, 1); c.restoreState()

def fit_text(c, x, y, w, h, text, font='Body', size=8.4, color=INK, leading=None, minsize=5.8, align='left', valign='top'):
    """Wrap text into the box and shrink until it fits."""
    s = size
    while True:
        ld = leading or s * 1.17
        lines = simpleSplit(text, font, s, w)
        if len(lines) * ld <= h + 0.3 or s <= minsize: break
        s -= 0.25
    ld = leading or s * 1.17
    c.saveState(); c.setFont(font, s); c.setFillColor(color)
    total = len(lines) * ld
    if valign == 'middle': ty = y + h / 2 + total / 2 - s * 0.82
    elif valign == 'bottom': ty = y + total - s * 0.82
    else: ty = y + h - s * 0.82
    for ln in lines:
        if align == 'center': c.drawCentredString(x + w / 2, ty, ln)
        else: c.drawString(x, ty, ln)
        ty -= ld
    c.restoreState()
    return s

def badge(c, x, y, n, color=NAVY, r=2.5 * mm):
    c.saveState(); c.setFillColor(color); c.circle(x, y, r, 0, 1); c.setFillColor(colors.white)
    c.setFont('BodyB', 7.6); c.drawCentredString(x, y - 2.5, str(n)); c.restoreState()

def pill(c, x, y, text, fill, fg=colors.white, size=6.6, padx=1.8 * mm, h=3.7 * mm):
    c.saveState(); c.setFont('BodyB', size); tw = pdfmetrics.stringWidth(text, 'BodyB', size)
    c.setFillColor(fill); c.roundRect(x, y, tw + 2 * padx, h, h / 2, 0, 1)
    c.setFillColor(fg); c.drawString(x + padx, y + h / 2 - size * 0.34, text); c.restoreState()
    return tw + 2 * padx

class Legend(Flowable):
    def __init__(self, items=None):
        super().__init__()
        self.items = items or [(BLUET, CYAN, 'Event'), (VIOLT, VIOLET, 'Control'), (REDT, RED, 'Result without the control'),
                               (GREENT, GREEN, 'Result with the control'), (AMBERT, AMBER, 'Nothing noticed, or a limit')]
    def wrap(self, aw, ah): self.w = aw; return aw, 7 * mm
    def draw(self):
        c = self.canv; x = 0
        for fill, stroke, label in self.items:
            rbox(c, x, 1.5 * mm, 4.4 * mm, 3.4 * mm, fill, stroke, r=0.9 * mm, lw=0.8)
            c.setFont('Body', 8); c.setFillColor(INK); c.drawString(x + 6 * mm, 2.4 * mm, label)
            x += 6 * mm + pdfmetrics.stringWidth(label, 'Body', 8) + 5 * mm

# ---------------------------------------------------------------- generic step-row diagram
class StepDiagram(Flowable):
    """A row (or rows) of numbered boxes joined by arrows, used for the method, retirement and leak figures.
    rows: list of rows; each row a list of (title, sub, kind) with kind in '', 'ok', 'warn', 'bad', 'violet'."""
    KINDS = {'': (SOFT, MUTED), 'ok': (GREENT, GREEN), 'warn': (AMBERT, AMBER), 'bad': (REDT, RED), 'violet': (VIOLT, VIOLET), 'info': (BLUET, CYAN)}
    def __init__(self, rows, box_h=26 * mm, gap=7 * mm, start=1, labels=None, row_gap=11 * mm, zones=None, row_titles=None, bw_max=None):
        super().__init__(); self.rows, self.box_h, self.gap, self.start = rows, box_h, gap, start
        self.labels = labels or {}; self.row_gap = row_gap; self.zones = zones or []
        self.row_titles = row_titles; self.bw_max = bw_max
    def wrap(self, aw, ah):
        self.w = aw; n = len(self.rows)
        self.tp = 6 * mm if self.row_titles else 0
        self.h = n * (self.box_h + self.tp) + (n - 1) * self.row_gap + 4 * mm
        return aw, self.h
    def draw(self):
        c = self.canv; n = 0; num = self.start
        for r, row in enumerate(self.rows):
            k = len(row); bw = (self.w - (k - 1) * self.gap) / k
            if self.bw_max: bw = min(bw, self.bw_max)
            y = self.h - 2 * mm - (r + 1) * (self.box_h + self.tp) - r * self.row_gap
            if self.row_titles:
                c.setFont('BodyB', 8); c.setFillColor(MUTED); c.drawString(0, y + self.box_h + 1.6 * mm, self.row_titles[r].upper())
            for i, (title, sub, kind) in enumerate(row):
                x = i * (bw + self.gap); fill, stroke = self.KINDS[kind]
                rbox(c, x, y, bw, self.box_h, fill, stroke)
                badge(c, x + 3.4 * mm, y + self.box_h - 3.4 * mm, num, stroke)
                fit_text(c, x + 7.2 * mm, y + self.box_h - 8.4 * mm, bw - 9 * mm, 6.5 * mm, title, 'BodyB', 8.8, INK, minsize=7)
                fit_text(c, x + 2.4 * mm, y + 1.6 * mm, bw - 4.8 * mm, self.box_h - 11.6 * mm, sub, 'Body', 7.8, MUTED, minsize=6)
                if i < k - 1:
                    lab = self.labels.get(num)
                    arrow(c, [(x + bw + 0.6 * mm, y + self.box_h / 2), (x + bw + self.gap - 0.6 * mm, y + self.box_h / 2)], MUTED, 1.0)
                num += 1

# ---------------------------------------------------------------- the per-case workflow diagram
CTRL = {
 'merge_sources': 'Merge every source', 'per_job_scope': 'One credential per job', 'owner_required': 'Owner required',
 'expiry_alert': 'Expiry alert at 30 and 7 days', 'consent_expiry_90d': 'Grants expire at 90 days',
 'owner_or_pause': 'Owner, or pause on day 30', 'retire_attestation': 'Retire with attestation', 'failure_alert': 'Alert on a failed rotation',
 'consumer_first': 'Update the consumer first', 'bind_to_workload': 'Bind trust to one workload',
 'require_owner_scope_expiry': 'Owner, scope and expiry at creation', 'jit_window': 'Just-in-time window',
 'one_extension_then_approval': 'One extension, then approval', 'timebox_and_prune': 'Time-box and prune members',
 'network_block': 'Block direct login at the network', 'coverage_check_block': 'Coverage check', 'two_approvers': 'Two approvers',
 'alert_justify_rotate': 'Alert, justify, rotate', 'monthly_report_flag': 'Monthly report flags', 'broker_record_expire': 'Broker records and expires',
 'sponsor_review_30d': 'Sponsor review every 30 days', 'revoke_on_leave': 'Revoke on leaving', 'grant_scan': 'Scan for AI grants',
 'agent_identity': 'Agent has its own identity', 'log_tag': 'Log tag for agents', 'owner_end_date_required': 'Owner and end date required',
 'weekly_sweep': 'Weekly sweep', 'secret_scan': 'Secret scan before commit', 'tenant_allowlist': 'Tenant allowlist',
 'breach_revoke': 'Revoke after the vendor notice', 'pattern_marking': 'Mark secrets by name pattern', 'short_ttl': 'Short token lifetime',
 'bind_and_revoke': 'Bind the token and revoke', 'owner_match': 'Match on owner', 'normalise_name': 'Normalise names',
 'reach_in_score': 'Reach in the score', 'verify_old_dead': 'Prove the old secret is dead', 'key_per_agent': 'One key per agent',
 'block_interactive': 'Block interactive sign-in', 'checkout_names_person': 'Checkout names the person', 'passkey': 'Passkey sign-in',
 'no_sms_fallback': 'No SMS fallback', 'same_rules': 'Same rules for backups', 'alert_nonbackup': 'Alert on non-backup reads',
 'strong_proof': 'Strong proof for a reset', 'notice_and_delay': 'Notice and delay', 'approve_and_record': 'Approve and record',
 'auto_expiry': 'Automatic expiry', 'dry_run': 'Dry run', 'scope_read_one': 'Scope: read one folder', 'scan_revoke': 'Scan and revoke on find',
 'rotate_90d': 'Rotate every 90 days', 'end_date_at_creation': 'End date at creation', 'sweep': 'Sweep for expired',
 'secret_scan_tickets': 'Secret scan on tickets', 'rotation': 'Rotation', 'commit_block': 'Block secrets at commit',
 'short_lived': 'Short-lived tokens', 'revoke_on_find': 'Revoke on find', 'end_date_expiry': 'Expire at the end date',
 'sponsor_review': 'Sponsor review', 'alert_every_use': 'Alert on every use', 'rotate_on_return': 'Rotate on return',
 'batch_limits': 'Batch limits', 'risk_shown_first': 'Show the risk first', 'second_approver_high_risk': 'Second approver for high risk',
 'block_direct_login': 'Block direct login', 'checkin_alert': 'Vault check-in alert',
}
def clabel(k): return CTRL.get(k, k.replace('_', ' ').capitalize())

class CaseDiagram(Flowable):
    """One case as a workflow. Non-chain: event -> control -> without / with. Chain: the attacker's links with the
    point where each control acts. Both end with 'each control switched off alone' and 'what it cannot see'."""
    def __init__(self, case, chain=None):
        super().__init__(); self.case = case; self.chain = chain
        self.top_h = 41 * mm if not chain else 48 * mm
        self.strip_h = 25 * mm
        self.h = self.top_h + self.strip_h + 3 * mm
    def wrap(self, aw, ah): self.w = aw; return aw, self.h
    def draw(self):
        c = self.canv; cs = self.case; w = self.w; sy = 0       # strip origin
        ty = self.strip_h + 3 * mm                                # top region origin
        if self.chain: self.draw_chain(c, w, ty)
        else: self.draw_flow(c, w, ty)
        self.draw_strip(c, w)

    # -- top region, ordinary case
    def draw_flow(self, c, w, ty):
        cs = self.case; th = self.top_h
        ex, ew, eh = 0, 38 * mm, 24 * mm
        ey = ty + th / 2 - eh / 2
        rbox(c, ex, ey, ew, eh, BLUET, CYAN); badge(c, ex + 3.4 * mm, ey + eh - 3.4 * mm, 1, CYAN)
        fit_text(c, ex + 7 * mm, ey + eh - 7.2 * mm, ew - 9 * mm, 5 * mm, 'Event', 'BodyB', 8.6, INK)
        fit_text(c, ex + 2.4 * mm, ey + 1.6 * mm, ew - 4.8 * mm, eh - 9.6 * mm, cs['short'], 'Body', 8, INK, minsize=6)
        gx, gw = 49 * mm, 44 * mm
        ctrls = list(cs['noticed'].keys()); gh = 14 * mm + 5.2 * mm * len(ctrls)
        gh = max(gh, 20 * mm); gy = ty + th / 2 - gh / 2
        rbox(c, gx, gy, gw, gh, VIOLT, VIOLET, lw=1.1); badge(c, gx + 3.4 * mm, gy + gh - 3.4 * mm, 2, VIOLET)
        fit_text(c, gx + 7 * mm, gy + gh - 7.2 * mm, gw - 9 * mm, 5 * mm, 'Control' if len(ctrls) == 1 else 'Controls', 'BodyB', 8.6, INK)
        yy = gy + gh - 12.2 * mm
        for k in ctrls:
            fit_text(c, gx + 2.8 * mm, yy - 4 * mm, gw - 5.6 * mm, 8.4 * mm, '+ ' + clabel(k), 'Body', 7.8, INK, minsize=6, leading=8.4)
            yy -= 5.2 * mm if len(simpleSplit('+ ' + clabel(k), 'Body', 7.8, gw - 5.6 * mm)) == 1 else 7.6 * mm
        ox, ow, oh = 112 * mm, w - 112 * mm, 19.5 * mm
        oy1 = ty + th - oh - 1 * mm; oy2 = ty + 1 * mm
        rbox(c, ox, oy1, ow, oh, REDT, RED); badge(c, ox + 3.4 * mm, oy1 + oh - 3.4 * mm, 3, RED)
        fit_text(c, ox + 7 * mm, oy1 + oh - 7.2 * mm, ow - 9 * mm, 5 * mm, 'Without the control', 'BodyB', 8.6, INK)
        fit_text(c, ox + 2.6 * mm, oy1 + 1.4 * mm, ow - 5.2 * mm, oh - 9.4 * mm, cs['without'], 'Body', 8, INK, minsize=6)
        rbox(c, ox, oy2, ow, oh, GREENT, GREEN); badge(c, ox + 3.4 * mm, oy2 + oh - 3.4 * mm, 4, GREEN)
        fit_text(c, ox + 7 * mm, oy2 + oh - 7.2 * mm, ow - 9 * mm, 5 * mm, 'With the control', 'BodyB', 8.6, INK)
        fit_text(c, ox + 2.6 * mm, oy2 + 1.4 * mm, ow - 5.2 * mm, oh - 9.4 * mm, cs['with_'], 'Body', 8, INK, minsize=6)
        my = ty + th / 2
        arrow(c, [(ex + ew + 0.5 * mm, my), (gx - 0.5 * mm, my)], MUTED, 1.1)
        arrow(c, [(gx + gw, my + 3 * mm), (gx + gw + 8 * mm, my + 3 * mm), (gx + gw + 8 * mm, oy1 + oh / 2), (ox - 0.5 * mm, oy1 + oh / 2)], RED, 1.1, dash=(3, 2))
        arrow(c, [(gx + gw, my - 3 * mm), (gx + gw + 8 * mm, my - 3 * mm), (gx + gw + 8 * mm, oy2 + oh / 2), (ox - 0.5 * mm, oy2 + oh / 2)], GREEN, 1.1)
        c.setFont('BodyI', 6.8); c.setFillColor(RED); c.drawString(gx + gw + 9.5 * mm, oy1 + oh / 2 + 1.2 * mm, 'off')
        c.setFillColor(GREEN); c.drawString(gx + gw + 9.5 * mm, oy2 + oh / 2 + 1.2 * mm, 'on')

    # -- top region, chain test
    def draw_chain(self, c, w, ty):
        links, rules, eff = self.chain['links'], self.chain['rules'], self.chain['effect']
        th = self.top_h; n = len(links); gap = 7 * mm; bw = (w - gap * (n - 1)) / n; bh = 19 * mm
        by = ty + th - bh - 7 * mm
        c.setFont('BodyB', 7.6); c.setFillColor(RED)
        c.drawString(0, ty + th - 3.6 * mm, 'Attacker path with no controls: reaches the last link')
        for i, ln in enumerate(links):
            x = i * (bw + gap)
            rbox(c, x, by, bw, bh, REDT if i == n - 1 else BLUET, RED if i == n - 1 else CYAN)
            badge(c, x + 3.4 * mm, by + bh - 3.4 * mm, i + 1, RED if i == n - 1 else CYAN)
            fit_text(c, x + 7 * mm, by + 1.4 * mm, bw - 9 * mm, bh - 3 * mm, ln, 'BodyB', 8.4, INK, minsize=6, valign='top')
            if i < n - 1:
                arrow(c, [(x + bw + 0.4 * mm, by + bh / 2), (x + bw + gap - 0.4 * mm, by + bh / 2)], RED, 1.2)
        stacks = {}
        for name, (idx, kind) in rules.items():
            k = eff.get(name, kind)
            stacks.setdefault(idx, []).append((name, k))
        for idx, items in stacks.items():
            x = (idx - 1) * (bw + gap); cx = x + bw / 2
            y = by - 1.5 * mm
            for j, (name, k) in enumerate(items):
                fh = 10.5 * mm; fy = y - fh - j * (fh + 1.6 * mm)
                fill, stroke, tag = {'stop': (GREENT, GREEN, 'STOPS HERE'), 'detect': (AMBERT, AMBER, 'REPORTS ONLY'),
                                     'none': (SOFT2, MUTED, 'NO EFFECT'), 'late': (AMBERT, AMBER, 'TOO LATE')}[k]
                rbox(c, x + 1 * mm, fy, bw - 2 * mm, fh, fill, stroke, dash=(2, 1.5) if k in ('none', 'late') else None)
                c.setFont('BodyB', 5.9); c.setFillColor(stroke); c.drawString(x + 2.6 * mm, fy + fh - 3.1 * mm, tag)
                fit_text(c, x + 2.6 * mm, fy + 0.8 * mm, bw - 5.2 * mm, fh - 4.6 * mm, clabel(name), 'Body', 7.3, INK, minsize=5.6)
                if j == 0: arrow(c, [(cx, fy + fh), (cx, by - 0.2 * mm)], stroke, 1.0)

    # -- bottom strip
    def draw_strip(self, c, w):
        cs = self.case; h = self.strip_h
        lw_ = w * 0.60
        rbox(c, 0, 0, lw_, h, AMBERT if cs['masked'] else SOFT, AMBER if cs['masked'] else LINE)
        badge(c, 3.6 * mm, h - 3.6 * mm, 5, AMBER if cs['masked'] else MUTED)
        fit_text(c, 7.6 * mm, h - 7.6 * mm, lw_ - 10 * mm, 5 * mm, 'Switch each control off alone', 'BodyB', 8.6, INK)
        yy = h - 12.6 * mm
        ctrls = list(cs['noticed'].items())
        for k, v in ctrls[:3]:
            txt = clabel(k)
            col = GREEN if v else AMBER
            tag = 'NOTICED' if v else 'MASKED'
            tw = pill(c, 3 * mm, yy - 0.6 * mm, tag, col)
            fit_text(c, 3 * mm + tw + 2 * mm, yy - 0.6 * mm - 0.9 * mm, lw_ - tw - 9 * mm, 4.8 * mm, txt, 'Body', 8, INK, minsize=6, valign='middle')
            yy -= 4.7 * mm
        rx = lw_ + 3 * mm; rw = w - rx
        rbox(c, rx, 0, rw, h, AMBERT if cs['limit'] else SOFT, AMBER if cs['limit'] else LINE)
        badge(c, rx + 3.6 * mm, h - 3.6 * mm, 6, AMBER if cs['limit'] else MUTED)
        fit_text(c, rx + 7.6 * mm, h - 7.6 * mm, rw - 10 * mm, 5 * mm, 'What it cannot see', 'BodyB', 8.6, INK)
        fit_text(c, rx + 2.6 * mm, 1.4 * mm, rw - 5.2 * mm, h - 10.4 * mm, cs['limit'] if cs['limit'] else 'No limit recorded for this case.', 'Body' if cs['limit'] else 'BodyI', 7.9, INK if cs['limit'] else MUTED, minsize=5.8)

# ---------------------------------------------------------------- document template
class Book(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=23 * mm, bottomMargin=20 * mm,
                         title='Machine identities, tested in public', author='Roshan Trivedi',
                         subject='A 67-case lab on service accounts, secrets, privileged access and AI tools',
                         keywords='non-human identity, machine identity, PAM, secrets, AI agents', creator='roshantrivedi.co.in', **kw)
        self.chapter = ''
        self._k = 0
        fr = Frame(LEFT, 20 * mm, CW, H - 43 * mm, id='main', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        fr_cover = Frame(LEFT, 20 * mm, CW, H - 43 * mm, id='cv', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id='cover', frames=[fr_cover], onPage=self.draw_cover),
                               PageTemplate(id='main', frames=[fr], onPage=self.draw_main),
                               PageTemplate(id='back', frames=[fr_cover], onPage=self.draw_back)])
    cover_art = None
    def draw_cover(self, c, doc): Book.cover_art(c, doc)
    def draw_back(self, c, doc): Book.back_art(c, doc)
    back_art = None
    def draw_main(self, c, doc):
        c.saveState()
        c.setFillColor(CYAN); c.rect(0, H - 3 * mm, W, 3 * mm, 0, 1)
        c.setFont('Body', 8); c.setFillColor(MUTED)
        c.drawString(LEFT, H - 11 * mm, 'Machine identities, tested in public')
        c.drawRightString(W - RIGHT, H - 11 * mm, getattr(doc, 'chapter', ''))
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(LEFT, H - 13 * mm, W - RIGHT, H - 13 * mm)
        c.line(LEFT, 14 * mm, W - RIGHT, 14 * mm)
        c.drawString(LEFT, 9.2 * mm, 'Roshan Trivedi  |  roshantrivedi.co.in/nhi-lab/  |  CC BY 4.0')
        c.setFont('BodyB', 9); c.setFillColor(NAVY); c.drawRightString(W - RIGHT, 9.2 * mm, str(doc.page))
        c.restoreState()
    def afterFlowable(self, f):
        lvl = None; text = None; toc = True
        if isinstance(f, ChapterMark): self.chapter = f.title; return
        if isinstance(f, ChapterHead):
            lvl, text = 0, ((f'{f.num}. {f.title}' if str(f.num).isdigit() else f'Appendix {f.num}: {f.title}') if f.num != '' else f.title); self.chapter = f.title
        elif isinstance(f, Paragraph) and f.style.name == 'H2':
            lvl, text = 1, f.getPlainText()
        elif isinstance(f, Paragraph) and f.style.name == 'CaseH':
            lvl, text = 1, f.getPlainText(); toc = False
        if lvl is None: return
        key = 'k' + hashlib.md5(f'{lvl}|{text}'.encode()).hexdigest()[:10]
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=lvl, closed=(lvl >= 1))
        if toc: self.notify('TOCEntry', (lvl, text, self.page, key))

def make_toc():
    t = TableOfContents()
    t.levelStyles = [S['tocL0'], S['tocL1']]
    t.dotsMinLevel = 0
    return t

# ---------------------------------------------------------------- tables
def table(rows, widths, head=True, zebra=True, font=None, col_styles=None, repeat=1, valign='TOP'):
    """rows: list of lists of str (markup allowed) or Flowables. First row is the header when head=True."""
    data = []
    for r, row in enumerate(rows):
        out = []
        for cidx, cell in enumerate(row):
            if isinstance(cell, str):
                sty = S['cellh'] if (head and r == 0) else (S['cellb'] if cidx == 0 and col_styles == 'first-bold' else S['cell'])
                out.append(Paragraph(cell, sty))
            else:
                out.append(cell)
        data.append(out)
    tw = [x * mm for x in widths]
    t = Table(data, colWidths=tw, repeatRows=repeat if head else 0)
    style = [('VALIGN', (0, 0), (-1, -1), valign), ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
             ('TOPPADDING', (0, 0), (-1, -1), 3.2), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.6),
             ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE)]
    if head:
        style += [('BACKGROUND', (0, 0), (-1, 0), NAVY)]
    if zebra:
        for r in range(1 if head else 0, len(rows)):
            if (r % 2) == 0: style.append(('BACKGROUND', (0, r), (-1, r), SOFT))
    t.setStyle(TableStyle(style))
    return t
