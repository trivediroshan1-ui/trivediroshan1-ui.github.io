#!/usr/bin/env python3
"""Builds the animated SVG architecture diagrams for the AI governance lab.
Writes assets/diagrams/*.svg (standalone, light and dark by the viewer's setting)
and ai-governance-lab/diagrams/index.html (the same SVGs inline, themed by the site)."""
import html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 640

CSS = """
.dg{background:var(--d-bg,#ffffff);--d-ink:#0f172a;--d-mut:#52617a;--d-line:#b7c3d4;--d-panel:#f1f5fa;--d-acc:#0a7285;--d-accs:rgba(10,114,133,.12);--d-ok:#0b7a5b;--d-oks:rgba(11,122,91,.12);--d-bad:#c0264a;--d-bads:rgba(192,38,74,.12);--d-warn:#8a5208;--d-warns:rgba(138,82,8,.14);font-family:var(--a-fb,system-ui,-apple-system,"Segoe UI",sans-serif)}
@media (prefers-color-scheme:dark){.dg{background:var(--d-bg,#0b1220);--d-ink:#f1f5f9;--d-mut:#93a1bd;--d-line:#2c3a55;--d-panel:#101a2c;--d-acc:#4de2ff;--d-accs:rgba(77,226,255,.12);--d-ok:#7df2d0;--d-oks:rgba(125,242,208,.12);--d-bad:#ff7a93;--d-bads:rgba(255,122,147,.14);--d-warn:#f7c873;--d-warns:rgba(247,200,115,.14)}}
.dg text{fill:var(--d-ink)}
.dg .dg-t{font-weight:700;font-size:14px}
.dg .dg-s{font-size:12px;fill:var(--d-mut)}
.dg .dg-n{font:600 11px/1 var(--a-fm,ui-monospace,Menlo,monospace);fill:var(--d-mut)}
.dg .dg-h{font-weight:700;font-size:15px}
.dg .dg-node{fill:var(--d-panel);stroke:var(--d-line);stroke-width:1.5}
.dg .dg-acc{stroke:var(--d-acc);fill:var(--d-accs)}
.dg .dg-okb{stroke:var(--d-ok);fill:var(--d-oks)}
.dg .dg-badb{stroke:var(--d-bad);fill:var(--d-bads)}
.dg .dg-warnb{stroke:var(--d-warn);fill:var(--d-warns)}
.dg .dg-ln{stroke:var(--d-line);stroke-width:2;fill:none}
.dg .dg-dash{stroke-dasharray:5 5}
.dg .dg-ar{fill:var(--d-line)}
.dg .dg-lbl{font-size:12px;font-weight:600}
.dg .dg-good{fill:var(--d-ok)}.dg .dg-bd{fill:var(--d-bad)}.dg .dg-wn{fill:var(--d-warn)}
.dg text.dg-good,.dg text.dg-bd,.dg text.dg-wn{font-size:12px;font-weight:700}
.dg text.dg-good{fill:var(--d-ok)}.dg text.dg-bd{fill:var(--d-bad)}.dg text.dg-wn{fill:var(--d-warn)}
.dg .dg-pkt{offset-rotate:0deg;opacity:0}
@media (prefers-reduced-motion:reduce){.dg *{animation:none!important}.dg .dg-pkt{opacity:0}.dg .dg-badge{opacity:1!important}}
"""

def esc(s): return html.escape(s, quote=True)

class D:
    def __init__(self, name, title, desc, h):
        self.name, self.title, self.desc, self.h = name, title, desc, h
        self.b, self.kf = [], []
    def add(self, s): self.b.append(s)
    def node(self, x, y, w, h, title, sub=None, cls="", num=None):
        self.add(f'<rect class="dg-node {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>')
        tx = x + 14
        if num is not None:
            self.add(f'<text class="dg-n" x="{x+14}" y="{y+22}">{esc(str(num))}</text>'); tx = x + 38
        self.add(f'<text class="dg-t" x="{tx}" y="{y+22}">{esc(title)}</text>')
        if sub: self.add(f'<text class="dg-s" x="{tx}" y="{y+41}">{esc(sub)}</text>')
    def text(self, x, y, s, cls="dg-s", anchor="start", extra=""):
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')
    def line(self, d, dash=False, arrow=None):
        self.add(f'<path class="dg-ln{" dg-dash" if dash else ""}" d="{d}"/>')
        if arrow: self.arrow(*arrow)
    def arrow(self, x, y, dirn="d"):
        pts = {"d": f"{x-5},{y-8} {x+5},{y-8} {x},{y}", "r": f"{x-8},{y-5} {x-8},{y+5} {x},{y}", "l": f"{x+8},{y-5} {x+8},{y+5} {x},{y}", "u": f"{x-5},{y+8} {x+5},{y+8} {x},{y}"}[dirn]
        self.add(f'<polygon class="dg-ar" points="{pts}"/>')
    def packet(self, pid, path, kind, dur, keys, r=7):
        """keys: list of (percent, offset_percent, opacity)."""
        steps = "".join(f"{p}%{{offset-distance:{o}%;opacity:{op}}}" for p, o, op in keys)
        self.kf.append(f"@keyframes {pid}{{{steps}}}")
        self.kf.append(f".dg #{pid}{{offset-path:path('{path}');animation:{pid} {dur}s linear infinite}}")
        self.add(f'<circle id="{pid}" class="dg-pkt dg-{kind}" r="{r}" cx="0" cy="0"/>')
    def badge(self, bid, x, y, s, kind, dur, on, off):
        self.kf.append(f"@keyframes {bid}{{0%,{on}%{{opacity:0}}{on+2}%,{off}%{{opacity:1}}{off+3}%,100%{{opacity:0}}}}")
        self.kf.append(f".dg #{bid}{{animation:{bid} {dur}s linear infinite}}")
        self.add(f'<text id="{bid}" class="dg-badge dg-{kind}" x="{x}" y="{y}" opacity="0">{esc(s)}</text>')
    def svg(self, inline=False, prefix=""):
        body = "\n".join(self.b)
        kf = "\n".join(self.kf)
        s = (f'<svg class="dg" viewBox="0 0 {W} {self.h}" xmlns="http://www.w3.org/2000/svg" role="img" '
             f'aria-labelledby="{self.name}-t {self.name}-d" width="{W}" height="{self.h}" preserveAspectRatio="xMidYMin meet">'
             f'<title id="{self.name}-t">{esc(self.title)}</title><desc id="{self.name}-d">{esc(self.desc)}</desc>'
             f'<style>{CSS if not inline else ""}{kf}</style>\n{body}\n</svg>')
        return s

def keys_go(frac_end=100, hold_to=92):
    return [(0, 0, 0), (4, 0, 1), (int(hold_to*0.85), frac_end, 1), (hold_to, frac_end, 1), (hold_to+4, frac_end, 0), (100, 0, 0)]

# ---------------------------------------------------------------- 1. one request through the gateway
def d_flow():
    stages = [("Caller", "An app or an agent sends a prompt, the model it wants and the tools it needs."),
              ("Register", "Is this use registered, approved, not killed, and approved in the last 90 days?"),
              ("Model and paperwork", "Same model version as approved? Supplier review and AI bill of materials on file?"),
              ("Guardrail scan", "Masks secrets and personal data. Flags hidden instructions in the text."),
              ("Data and region rules", "Is this data allowed for this use and model? Personal data abroad is held."),
              ("Model", "Only the masked prompt goes out. The lab uses a stand-in model."),
              ("Response screen", "The answer is scanned too, so a secret from earlier is masked on the way back."),
              ("Person", "The answer reaches the person. A customer-facing use adds its AI notice.")]
    top, step, bh = 34, 88, 64
    h = top + len(stages) * step + 24
    d = D("agl-flow", "One request through the gateway", "Eight stages from caller to person. A good request passes every stage. A request with personal data for a model that is not approved stops at the data and region rules.", h)
    for i, (t, s) in enumerate(stages):
        y = top + i * step
        cls = "dg-acc" if i in (3, 4) else ""
        d.node(96, y, 524, bh, t, s, cls, num=f"{i+1}")
        if i < len(stages) - 1:
            d.line(f"M 358 {y+bh} L 358 {y+step}", arrow=(358, y + step - 1, "d"))
    y0, y1 = top + bh // 2, top + 7 * step + bh // 2
    d.line(f"M 30 {y0} L 30 {y1}", dash=True); d.line(f"M 62 {y0} L 62 {y1}", dash=True)
    d.text(30, 20, "pass", "dg-lbl dg-good", "middle"); d.text(62, 20, "stop", "dg-lbl dg-bd", "middle")
    stop = (4 * step) / (7 * step)
    d.packet("agl-flow-a", f"M 30 {y0} L 30 {y1}", "good", 10, keys_go(100, 90))
    d.packet("agl-flow-b", f"M 62 {y0} L 62 {y1}", "bd", 10, [(0, 0, 0), (4, 0, 1), (46, round(stop*100, 1), 1), (86, round(stop*100, 1), 1), (92, round(stop*100, 1), 0), (100, 0, 0)])
    d.badge("agl-flow-bg", 372, top + 4 * step + bh + 16, "Personal data for an unapproved model stops here", "bd", 10, 44, 86)
    return d

# ---------------------------------------------------------------- 2. where the filters plug in
def d_filters():
    d = D("agl-filters", "Where the filters plug in", "The guardrail scan is one slot. Filter v1, v2, v3 or an outside tool such as Presidio plugs into it through the same small interface. The same test set is run through each.", 560)
    d.node(120, 20, 400, 56, "A prompt or an answer", "Text with made-up personal data, secrets or a hidden instruction.", "")
    d.line("M 320 76 L 320 112", arrow=(320, 111, "d"))
    d.node(40, 112, 560, 56, "The guardrail scan", "One slot. It asks a filter: what did you find, and what should be masked?", "dg-acc")
    xs = [20, 175, 330, 485]
    names = [("v1", "Plain patterns", "Regex and checksums"), ("v2", "Tidies text first", "Adds a look-back"), ("v3", "Fixes the misses", "Written after v2"), ("Outside tool", "Presidio, through", "an adapter")]
    for i, (x, (a, b, c)) in enumerate(zip(xs, names)):
        d.add("<g>")
        d.node(x, 214, 135, 96, a, None, "")
        d.text(x + 14, 258, b, "dg-s"); d.text(x + 14, 276, c, "dg-s")
        d.add('</g>')
        d.line(f"M {x+67} 168 L {x+67} 214", dash=True)
    # rotating highlight
    for i, x in enumerate(xs):
        on = i * 25
        d.kf.append(f"@keyframes agl-filters-h{i}{{0%,{on}%{{opacity:0}}{on+1}%,{on+23}%{{opacity:1}}{on+25}%,100%{{opacity:0}}}}")
        d.kf.append(f".dg #agl-filters-h{i}{{animation:agl-filters-h{i} 12s linear infinite}}")
        d.add(f'<rect id="agl-filters-h{i}" x="{x-3}" y="211" width="141" height="102" rx="12" fill="none" stroke="var(--d-acc)" stroke-width="3" opacity="0"/>')
    d.line("M 320 330 L 320 366", arrow=(320, 365, "d"))
    d.node(40, 366, 560, 56, "The same questions every time", "53 variants, 200 labelled samples, then held-out items the author had not seen.", "")
    d.line("M 320 422 L 320 458", arrow=(320, 457, "d"))
    d.node(40, 458, 560, 80, "Two numbers per filter", None, "dg-okb")
    d.text(60, 506, "How much it catches, and how often it raises a false alarm.", "dg-s")
    d.text(60, 524, "v3 is 100% on the set it was fixed on. On items it had not seen it scored like v1.", "dg-s")
    d.packet("agl-filters-p", "M 320 76 L 320 112 L 320 168 L 320 214 L 320 366 L 320 458", "good", 12, [(0, 0, 0), (3, 0, 1), (96, 100, 1), (99, 100, 0), (100, 0, 0)])
    return d

# ---------------------------------------------------------------- 3. agent identity
def d_agent():
    d = D("agl-agent", "How an agent gets and uses access", "A person sponsors an agent. The agent gets a token that lasts 15 minutes and only the scopes it was registered with. A privileged action needs a short grant from someone else. One kill switch revokes everything.", 640)
    d.node(20, 20, 280, 62, "A human sponsor", "Named, active, answers for the agent.", "")
    d.node(340, 20, 280, 62, "The agent", "Registered with its own identity.", "")
    d.line("M 300 51 L 336 51", arrow=(338, 51, "r")); d.text(318, 44, "registers", "dg-s", "middle")
    d.line("M 480 82 L 480 130", arrow=(480, 129, "d")); d.text(490, 110, "asks for a token", "dg-s")
    d.node(340, 130, 280, 62, "Token service", "15-minute token. Only the agent's scopes.", "dg-acc")
    d.line("M 480 192 L 480 240", arrow=(480, 239, "d")); d.text(490, 222, "short-lived token", "dg-s")
    d.node(340, 240, 280, 62, "A tool or data store", "Checks the scope on every call.", "")
    d.line("M 400 302 L 400 350 L 150 350 L 150 372", arrow=(150, 371, "d")); d.text(275, 342, "crm.read: in scope", "dg-lbl dg-good", "middle")
    d.line("M 560 302 L 560 350 L 505 350 L 505 372", arrow=(505, 371, "d")); d.text(585, 342, "vault.read", "dg-lbl dg-bd", "middle")
    d.node(20, 372, 260, 54, "Allowed", "The call is logged.", "dg-okb")
    d.node(380, 372, 240, 54, "Denied", "Scope not granted. Logged.", "dg-badb")
    d.node(20, 466, 300, 80, "Privileged action", None, "dg-warnb")
    d.text(34, 512, "Needs a 30-minute grant from someone other than", "dg-s"); d.text(34, 530, "the sponsor. The session is recorded.", "dg-s")
    d.node(340, 466, 280, 80, "Kill switch", None, "dg-badb")
    d.text(354, 512, "One call stops the agent and every", "dg-s"); d.text(354, 530, "token it holds.", "dg-s")
    d.text(320, 580, "A sponsor who leaves disables the agent. Idle agents are flagged.", "dg-s", "middle")
    d.packet("agl-agent-p1", "M 480 82 L 480 130 L 480 192 L 480 240 L 400 302 L 400 350 L 150 350 L 150 372", "good", 9, [(0, 0, 0), (4, 0, 1), (92, 100, 1), (96, 100, 0), (100, 0, 0)])
    d.packet("agl-agent-p2", "M 480 82 L 480 130 L 480 192 L 480 240 L 560 302 L 560 350 L 505 350 L 505 372", "bd", 9, [(0, 0, 0), (4, 0, 1), (92, 100, 1), (96, 100, 0), (100, 0, 0)])
    return d

# ---------------------------------------------------------------- 4. audit trail
def d_audit():
    d = D("agl-audit", "The tamper-evident log", "Each log line includes a fingerprint of the line before it. Editing or deleting a line breaks the chain from that point. Cutting lines off the end is only visible against an anchor kept somewhere else.", 620)
    ys = [20, 100, 180, 260, 340]
    labs = [("Line 1", "A call allowed for use U1"), ("Line 2", "A call blocked: personal data"), ("Line 3", "Approval recorded"), ("Line 4", "A call allowed for use U1"), ("Line 5", "Kill switch pulled on U2")]
    for i, (y, (a, b)) in enumerate(zip(ys, labs)):
        d.node(20, y, 360, 56, a, b, "")
        d.text(366, y + 22, "fingerprint of line " + str(i) if i else "start", "dg-n", "end")
        if i < 4: d.line(f"M 200 {y+56} L 200 {y+80}", arrow=(200, y + 79, "d"))
    # tamper highlight on line 3
    d.kf.append("@keyframes agl-audit-t{0%,30%{opacity:0}34%,70%{opacity:1}74%,100%{opacity:0}}")
    d.kf.append(".dg #agl-audit-t{animation:agl-audit-t 10s linear infinite}")
    d.add('<g id="agl-audit-t" opacity="0"><rect x="17" y="177" width="366" height="62" rx="12" fill="none" stroke="var(--d-bad)" stroke-width="3"/>')
    d.add('<text class="dg-bd" x="394" y="212">edited</text><rect x="17" y="257" width="366" height="62" rx="12" fill="none" stroke="var(--d-bad)" stroke-width="2" stroke-dasharray="5 5"/><rect x="17" y="337" width="366" height="62" rx="12" fill="none" stroke="var(--d-bad)" stroke-width="2" stroke-dasharray="5 5"/><text class="dg-bd" x="394" y="292">chain breaks</text><text class="dg-bd" x="394" y="372">from here on</text></g>')
    d.node(440, 20, 180, 120, "Anchor", None, "dg-okb")
    d.text(454, 66, "A copy of where the", "dg-s"); d.text(454, 84, "log ended, kept", "dg-s"); d.text(454, 102, "somewhere else.", "dg-s")
    d.text(454, 126, "Catches cut-off lines.", "dg-lbl dg-good", "start")
    d.node(20, 430, 600, 70, "What a chain cannot see on its own", None, "dg-warnb")
    d.text(34, 478, "Lines cut off the end still verify. That needs the anchor.", "dg-s")
    d.node(20, 520, 600, 80, "Retention and incidents", None, "")
    d.text(34, 568, "Logs are kept 180 days, then pruned, and the chain still verifies.", "dg-s")
    d.text(34, 586, "An incident timeline and a draft report are built from these lines.", "dg-s")
    d.packet("agl-audit-p", "M 200 20 L 200 380", "good", 10, [(0, 0, 0), (4, 0, 1), (28, 100, 1), (30, 100, 0), (100, 100, 0)])
    return d

# ---------------------------------------------------------------- 5. the lab as a whole
def d_lab():
    d = D("agl-lab", "The lab as a whole", "Four tracks of cases, run in rounds on three filters, then tested on unseen items, then on a real assistant. Results go into what held and what broke.", 640)
    tr = [("A", "Gateway", "16 cases"), ("G", "Guardrail", "17 cases"), ("I", "Agent identity", "12 cases"), ("E", "Audit", "14 cases")]
    d.text(20, 16, "Four tracks, 59 cases, all made-up data", "dg-h")
    for i, (a, b, c) in enumerate(tr):
        x = 20 + i * 150
        d.node(x, 30, 140, 66, f"{a}  {b}", c, "")
    d.line("M 320 96 L 320 128", arrow=(320, 127, "d"))
    d.text(20, 150, "Run in rounds. Guesses written first and committed to git.", "dg-h")
    rs = [("1", "v1"), ("2", "v2"), ("3", "v2"), ("4", "v3"), ("5", "unseen")]
    d.line("M 60 190 L 580 190")
    for i, (a, b) in enumerate(rs):
        x = 60 + i * 130
        d.add(f'<circle cx="{x}" cy="190" r="16" class="dg-node dg-acc"/>')
        d.text(x, 195, a, "dg-t", "middle"); d.text(x, 226, b, "dg-s", "middle")
    d.kf.append("@keyframes agl-lab-d{0%{offset-distance:0%;opacity:0}5%{opacity:1}90%{offset-distance:100%;opacity:1}96%{opacity:0}100%{offset-distance:0%;opacity:0}}")
    d.kf.append(".dg #agl-lab-d{offset-path:path('M 60 190 L 580 190');animation:agl-lab-d 10s linear infinite}")
    d.add('<circle id="agl-lab-d" class="dg-pkt dg-good" r="7" cx="0" cy="0"/>')
    d.line("M 320 240 L 320 268", arrow=(320, 267, "d"))
    d.node(20, 268, 290, 76, "Then a real assistant", "Nine requests under one made-up policy.", "")
    d.node(330, 268, 290, 76, "And a held-out test", "Items the filters had never seen.", "")
    d.line("M 165 344 L 165 384 L 320 384 L 320 396", arrow=(320, 395, "d")); d.line("M 475 344 L 475 384 L 320 384")
    d.node(20, 396, 290, 120, "What held", None, "dg-okb")
    for j, s in enumerate(["The register and approvals", "The audit trail", "Kill switches and tokens", "Checksums with fixed shapes"]): d.text(34, 440 + j * 20, "• " + s, "dg-s")
    d.node(330, 396, 290, 120, "What broke", None, "dg-badb")
    for j, s in enumerate(["Anything that depends on meaning", "Hinglish and new wordings", "Data split across messages", "A score on a set I tuned to"]): d.text(344, 440 + j * 20, "• " + s, "dg-s")
    d.text(320, 560, "One laptop, made-up data, my own cases. A data point, not a guarantee.", "dg-s", "middle")
    return d

DIAGS = [
    ("flow", d_flow, "One request through the gateway", "Eight stages from caller to person. Watch a good request pass, and one with personal data stop at the data and region rules."),
    ("filters", d_filters, "Where the filters plug in", "The guardrail scan is one slot. v1, v2, v3 or an outside tool plugs in, and the same tests run on each."),
    ("agent", d_agent, "How an agent gets and uses access", "Sponsor, short-lived token, scope checks, a just-in-time grant for privileged actions, and one kill switch."),
    ("audit", d_audit, "The tamper-evident log", "Each line carries a fingerprint of the one before. Edit one and the chain breaks. Cut lines off the end and you need an anchor."),
    ("lab", d_lab, "The lab as a whole", "Four tracks, five rounds, an unseen-items test and a real assistant, and what came out of it."),
]

def main():
    os.makedirs(os.path.join(ROOT, "assets", "diagrams"), exist_ok=True)
    inl = []
    for key, fn, title, cap in DIAGS:
        d = fn()
        open(os.path.join(ROOT, "assets", "diagrams", f"agl-{key}.svg"), "w", encoding="utf-8").write(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + d.svg(inline=False) + "\n")
        inl.append((key, title, cap, d.svg(inline=True)))
    # inline css once
    sections = []
    for key, title, cap, svg in inl:
        sections.append(f'''      <section id="{key}">
        <h2>{esc(title)}</h2>
        <p class="body-text">{esc(cap)}</p>
        <figure class="dg-fig"><div class="dg-wrap">{svg}</div>
          <figcaption><a href="/assets/diagrams/agl-{key}.svg">Open the SVG file</a>. It switches between light and dark by your device setting and stops moving if your device asks for less motion. On a small screen, swipe sideways inside the picture.</figcaption></figure>
      </section>''')
    tpl = open(os.path.join(ROOT, "ai-governance-lab", "try", "index.html"), encoding="utf-8").read()
    a = tpl.index('<main id="main">'); b = tpl.index('<aside class="hg-next"')
    head = tpl[:a]; tail = tpl[b:]
    head = head.replace("/ai-governance-lab/try/", "/ai-governance-lab/diagrams/")
    head = re.sub(r'content="Run the AI governance lab in your browser[^"]*"', 'content="Animated architecture diagrams for the AI governance lab, as SVG: the request flow, where the filters plug in, agent access, the audit log and the lab as a whole."', head)
    head = head.replace('content="AI governance lab: try it yourself"', 'content="AI governance lab: architecture diagrams"')
    head = head.replace("<title>Try the AI governance lab &middot; Roshan Trivedi</title>", "<title>Architecture diagrams &middot; AI governance lab</title>")
    head = head.replace("agl.css?v=20261024d", "agl.css?v=20261024f")
    css = CSS.replace(".dg{--d-ink", ".dg{--d-ink")
    main_html = f'''<main id="main">
      <header class="hero mcp-hero">
        <p class="eyebrow">AI governance lab</p>
        <h1>Architecture diagrams</h1>
        <p class="dek">Five animated diagrams of how the lab works: the request flow, where the filters plug in, how an agent gets access, the tamper-evident log, and the lab as a whole. Each one is an SVG file you can reuse.</p>
        <div class="mcp-ribbon" aria-hidden="true"></div>
      </header>
      <section><p class="body-text">These are drawn from the lab&rsquo;s own code, not from a vendor diagram. Everything in them is made up: a lender called Kaveri Finance and test data that follows real formats on purpose. For the cases behind each diagram, see <a href="/ai-governance-lab/cases/">every use case, one by one</a>.</p></section>
      <style>{css}</style>
      <div class="agl dg-page">
{chr(10).join(sections)}
      </div>
      '''
    tail = tail.replace('<a href="/ai-governance-lab/" style="--k:#4de2ff">', '<a href="/ai-governance-lab/cases/" style="--k:#7df2d0"><b>Every use case</b><span>The 59 cases behind these diagrams.</span></a>\n          <a href="/ai-governance-lab/" style="--k:#4de2ff">', 1)
    out = head + main_html + tail
    out = re.sub(r'  <script src="/assets/agl-try-filters.js[^\n]*\n  <script src="/assets/agl-try.js[^\n]*\n  <script src="/assets/agl-boot-try.js[^\n]*\n', "", out)
    os.makedirs(os.path.join(ROOT, "ai-governance-lab", "diagrams"), exist_ok=True)
    open(os.path.join(ROOT, "ai-governance-lab", "diagrams", "index.html"), "w", encoding="utf-8").write(out)

if __name__ == "__main__":
    main()
