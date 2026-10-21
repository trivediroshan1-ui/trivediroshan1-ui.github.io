#!/usr/bin/env python3
"""Builds the small graphic assets the page themes and the menu use. Safe to re-run.

  assets/bg/*.svg       tileable background motifs (black strokes on transparent; the CSS colours them with a mask)
  assets/logos/*.svg    single-colour marks for the site and each lab (also used as CSS masks)
  assets/icons.svg      one sprite with the topic icons (<use href="/assets/icons.svg#i-key">)

Everything is drawn here, nothing is copied from a brand. Run from anywhere: python3 scripts/build-themes.py
"""
import math, random, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BG = ROOT / "assets" / "bg"; LOGOS = ROOT / "assets" / "logos"
BG.mkdir(parents=True, exist_ok=True); LOGOS.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- icons (reuse the case-study icon set)
ns = {"__file__": str(ROOT / "scripts" / "case-art.py")}
exec((ROOT / "scripts" / "case-art.py").read_text().split("p = ROOT /")[0], ns)
ICONS = ns["I"]
EXTRA = {
    "flask": '<path d="M9 3h6M10 3v6L4.5 19a1.6 1.6 0 0 0 1.4 2.4h12.2a1.6 1.6 0 0 0 1.4-2.4L14 9V3"/><path d="M7.5 15h9"/>',
    "pen": '<path d="M4 20l1-4L16.5 4.5a2.1 2.1 0 0 1 3 3L8 19z"/><path d="M14.5 6.5l3 3"/>',
    "book": '<path d="M4 5.5C7 4 10 4 12 6c2-2 5-2 8-.5V19c-3-1.5-6-1.5-8 .5-2-2-5-2-8-.5z"/><path d="M12 6v13.5"/>',
    "home": '<path d="M4 11l8-7 8 7"/><path d="M6 10v9h12v-9"/><path d="M10 19v-5h4v5"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-3.6 3.6-5.5 7-5.5s6.2 1.9 7 5.5"/>',
    "mail": '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="M4 7l8 6 8-6"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.5 16l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "plug": '<path d="M9 3v5M15 3v5"/><path d="M6 8h12v3a6 6 0 0 1-12 0z"/><path d="M12 17v4"/>',
    "map": '<path d="M9 4L3.5 6v14L9 18l6 2 5.5-2V4L15 6z"/><path d="M9 4v14M15 6v14"/>',
    "palette": '<path d="M12 3.5a8.5 8.5 0 1 0 0 17c1.5 0 2-1 1.4-2.1-.6-1.1.1-2.4 1.4-2.4H17a3.5 3.5 0 0 0 3.5-3.5C20.5 7 16.8 3.5 12 3.5z"/><circle cx="8" cy="11" r="1"/><circle cx="12" cy="8" r="1"/><circle cx="16" cy="11" r="1"/>',
    "india": '<path d="M12 3l2.2 4.5 5 .7-3.6 3.5.9 5-4.5-2.4-4.5 2.4.9-5L4.8 8.2l5-.7z"/>',
}
ALL = dict(ICONS); ALL.update(EXTRA)
sprite = ['<svg xmlns="http://www.w3.org/2000/svg" style="display:none">']
for k, v in sorted(ALL.items()):
    sprite.append(f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>')
sprite.append("</svg>")
(ROOT / "assets" / "icons.svg").write_text("\n".join(sprite))

# ---------------------------------------------------------------- logos (64x64, stroke only, no text)
def logo(name, body, extra=""):
    (LOGOS / f"{name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" stroke="#000" stroke-width="3.4" '
        f'stroke-linecap="round" stroke-linejoin="round">{body}{extra}</svg>')

# site mark: a rounded square holding R and T drawn as strokes
logo("rt", '<rect x="6" y="6" width="52" height="52" rx="14"/>'
           '<path d="M19 43V21h8.5a6 6 0 0 1 0 12H19M27.5 33L34 43"/><path d="M37 21h10M42 21v22"/>')
# HumanGate: a shield with a doorway, and a person standing in it
logo("humangate", '<path d="M32 6l20 7v16c0 14-8.5 23-20 29C20.500 52 12 43 12 29V13z"/>'
                  '<path d="M23.500 43V33a8.500 8.500 0 0 1 17 0v10"/>', '<circle cx="32" cy="34" r="3" fill="#000" stroke="none"/>')
# AI governance lab: three nodes held by a triangle, and a record at the centre
logo("ailab", '<path d="M32 13L15 45h34z"/><circle cx="32" cy="13" r="6" fill="#000" stroke="none"/>'
              '<circle cx="15" cy="45" r="6" fill="#000" stroke="none"/><circle cx="49" cy="45" r="6" fill="#000" stroke="none"/>'
              '<circle cx="32" cy="37" r="4.500"/>')
# book: Who Approved That?  an open book with a tick
logo("book", '<path d="M7 14c9-4 19-3 25 3 6-6 16-7 25-3v35c-9-4-19-3-25 3-6-6-16-7-25-3z"/><path d="M32 17v35"/>'
             '<path d="M40 27l4 4 7-8"/>')
# PAM vault wheel
logo("pam", '<circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="9"/>'
            '<path d="M32 8v15M32 41v15M8 32h15M41 32h15M15 15l11 11M38 38l11 11M49 15L38 26M26 38L15 49"/>')
# exams: a sheet with a seal
logo("exams", '<path d="M16 6h24l10 10v42H16z"/><path d="M40 6v10h10"/><path d="M24 28h18M24 36h18M24 44h10"/>',
              '<circle cx="42" cy="46" r="5"/>')
# writing: a pen nib
logo("writing", '<path d="M10 54l5-17L42 10a6 6 0 0 1 9 9L24 46z"/><path d="M38 14l12 12"/><path d="M10 54l14-8"/>')

# ---------------------------------------------------------------- motifs
def esc(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def motif(name, w, h, body, stroke=1.0):
    uses = "".join(f'<use href="#m" x="{esc(dx*w)}" y="{esc(dy*h)}"/>' for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    (BG / f"{name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {esc(w)} {esc(h)}" width="{esc(w)}" height="{esc(h)}">'
        f'<defs><g id="m" fill="none" stroke="#000" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{body}</g></defs>{uses}</svg>')

def sine(y0, amp, k, ph, w=360, step=6):
    pts = [(x, y0 + sum(a * math.sin(2 * math.pi * kk * x / w + p) for a, kk, p in zip(amp, k, ph))) for x in range(0, w + 1, step)]
    return "M" + " L".join(f"{esc(x)} {esc(y)}" for x, y in pts)

S = 360
# grid: blueprint
b = []
for i in range(0, S + 1, 30):
    op = .9 if i % 120 == 0 else .32
    b.append(f'<path d="M{i} 0V{S}M0 {i}H{S}" stroke-opacity="{op}"/>')
for x in range(0, S, 120):
    for y in range(0, S, 120):
        b.append(f'<path d="M{x-6} {y}H{x+6}M{x} {y-6}V{y+6}" stroke-width="1.6"/>')
motif("grid", S, S, "".join(b))
# dots
b = []
for gx in range(12, S, 24):
    for gy in range(12, S, 24):
        big = ((gx // 24) * 3 + (gy // 24) * 5) % 11 == 0
        b.append(f'<circle cx="{gx}" cy="{gy}" r="{2.2 if big else 1.1}" fill="#000" stroke="none"/>')
motif("dots", S, S, "".join(b))
# waves
b = [f'<path d="{sine(y, [5], [3], [y*0.09])}"/>' for y in range(0, S, 18)]
motif("waves", S, S, "".join(b))
# topo: contour-like lines
b = []
for y in range(0, S, 20):
    t = y / S * 2 * math.pi
    b.append(f'<path d="{sine(y, [15, 7], [1, 2], [t*2, t*3+1])}"/>')
motif("topo", S, S, "".join(b))
# circuit: right-angle traces and pads
rnd = random.Random(11); b = []
G = 24
for _ in range(15):
    x, y = rnd.randrange(0, S // G) * G, rnd.randrange(0, S // G) * G
    d = [(x, y)]; dirn = rnd.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
    for _ in range(rnd.randint(3, 6)):
        n = rnd.randint(1, 4) * G; x += dirn[0] * n; y += dirn[1] * n; d.append((x, y))
        dirn = rnd.choice([(0, 1), (0, -1)] if dirn[0] else [(1, 0), (-1, 0)])
    b.append('<path d="M' + " L".join(f"{p} {q}" for p, q in d) + '"/>')
    b.append(f'<circle cx="{d[0][0]}" cy="{d[0][1]}" r="3"/><circle cx="{d[-1][0]}" cy="{d[-1][1]}" r="2.2" fill="#000" stroke="none"/>')
motif("circuit", S, S, "".join(b))
# hex and cubes (pointy-top lattice, L = 24)
L = 24; hw = math.sqrt(3) * L; W, H = 6 * hw, 288
def hexes(spokes):
    out = []
    for row in range(-1, 9):
        for col in range(-1, 8):
            cx = col * hw + (row % 2) * hw / 2; cy = row * 1.5 * L
            pts = [(cx + L * math.cos(math.radians(60 * i - 30)), cy + L * math.sin(math.radians(60 * i - 30))) for i in range(6)]
            out.append('<path d="M' + " L".join(f"{esc(p)} {esc(q)}" for p, q in pts) + ' Z"/>')
            if spokes:
                for i in (0, 2, 4):
                    out.append(f'<path d="M{esc(cx)} {esc(cy)}L{esc(pts[i][0])} {esc(pts[i][1])}"/>')
    return "".join(out)
motif("hex", W, H, hexes(False), .9)
motif("cubes", W, H, hexes(True), .9)
# rings: two sets of range circles
b = []
for cx, cy in ((110, 110), (262, 250)):
    for i, r in enumerate(range(14, 100, 14)):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"' + (' stroke-dasharray="2 7"' if i % 3 == 2 else "") + '/>')
    for a in range(0, 360, 30):
        x1, y1 = cx + 100 * math.cos(math.radians(a)), cy + 100 * math.sin(math.radians(a))
        x2, y2 = cx + 106 * math.cos(math.radians(a)), cy + 106 * math.sin(math.radians(a))
        b.append(f'<path d="M{esc(x1)} {esc(y1)}L{esc(x2)} {esc(y2)}"/>')
    b.append(f'<path d="M{cx-5} {cy}h10M{cx} {cy-5}v10" stroke-width="1.5"/>')
motif("rings", S, S, "".join(b))
# nodes: a small network, wrap-aware
rnd = random.Random(5); pts = []
while len(pts) < 24:
    p = (rnd.uniform(0, S), rnd.uniform(0, S))
    if all(min(abs(p[0]-q[0]), S-abs(p[0]-q[0]))**2 + min(abs(p[1]-q[1]), S-abs(p[1]-q[1]))**2 > 58**2 for q in pts): pts.append(p)
def wrapd(a, b_):
    dx = b_[0] - a[0]; dy = b_[1] - a[1]
    dx -= S * round(dx / S); dy -= S * round(dy / S); return dx, dy
b = []
for i, p in enumerate(pts):
    near = sorted(((math.hypot(*wrapd(p, q)), j) for j, q in enumerate(pts) if j != i))[:2]
    for dist, j in near:
        if dist < 110:
            dx, dy = wrapd(p, pts[j]); b.append(f'<path d="M{esc(p[0])} {esc(p[1])}L{esc(p[0]+dx)} {esc(p[1]+dy)}" stroke-opacity=".7"/>')
    r = 4.5 if i % 5 == 0 else 2.6
    b.append(f'<circle cx="{esc(p[0])}" cy="{esc(p[1])}" r="{r}"' + ('' if i % 5 == 0 else ' fill="#000"') + '/>')
motif("nodes", S, S, "".join(b))
# keys: sparse identity glyphs
glyphs = ["key", "lock", "shield", "finger", "idcard", "eye", "vault", "gauge", "person"]
rnd = random.Random(3); b = []
for i, g in enumerate(glyphs):
    gx, gy = (i % 3) * 120 + 60 + rnd.randint(-18, 18), (i // 3) * 120 + 60 + rnd.randint(-18, 18)
    rot = rnd.randint(-14, 14)
    b.append(f'<g transform="translate({gx} {gy}) rotate({rot}) scale(1.9) translate(-12 -12)" stroke-width="0.8">{ICONS[g]}</g>')
motif("keys", S, S, "".join(b), 0.8)
# diag: hatch
b = ["".join(f'<path d="M{c-S} {S}L{c} 0" stroke-width="{1.6 if (c//18)%5==0 else .8}"/>' for c in range(0, 2*S+1, 18))]
motif("diag", S, S, "".join(b))
# chevrons
b = []
for y in range(0, S, 24):
    off = 12 if (y // 24) % 2 else 0
    for x in range(0, S, 24):
        b.append(f'<path d="M{x+off} {y+4}l7 8l-7 8"/>')
motif("chevrons", S, S, "".join(b))
# ledger: ruled paper
b = [f'<path d="M0 {y}H{S}" stroke-opacity="{.9 if y % 120 == 0 else .4}"/>' for y in range(0, S, 30)]
b += [f'<path d="M{x} 0v6" stroke-opacity=".6"/>' for x in range(0, S, 12)]
motif("ledger", S, S, "".join(b))

print("icons:", len(ALL), "| logos:", len(list(LOGOS.glob('*.svg'))), "| motifs:", len(list(BG.glob('*.svg'))))
