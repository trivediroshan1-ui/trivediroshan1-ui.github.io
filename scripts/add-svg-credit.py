#!/usr/bin/env python3
"""Add a small "roshantrivedi.co.in" credit inside every inline SVG diagram (IP-04).

A diagram copied as a screenshot loses the page around it; a credit inside the
drawing survives. The credit goes in a thin strip added below the drawing (the
viewBox grows by that strip), so it can never sit on top of the diagram itself.

- Only real diagrams: viewBox at least 300 wide (the phone versions of the case-study
  diagrams are 360 wide) and 200 tall, and not aria-hidden
  (the NHI explainer scenes are animation frames, not diagrams).
- The text is aria-hidden: screen readers get the diagram's own title and description.
- Safe to re-run: an SVG that already has class "svg-credit" inside is skipped.

Run after any script that regenerates pages with diagrams:
    python3 scripts/add-svg-credit.py
"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = ("archive/", "_layouts/", "_includes/", "node_modules/", "workers/")
OPEN = re.compile(r'<svg\b[^>]*>', re.S)

def fmt(x):
    return str(int(x)) if float(x).is_integer() else f"{x:.1f}"

def credit(svg_open, body):
    m = re.search(r'viewBox="([\d.\s-]+)"', svg_open)
    if not m or 'aria-hidden="true"' in svg_open or "svg-credit" in body:
        return None
    x, y, w, h = (float(v) for v in m.group(1).split())
    if w < 300 or h < 200:
        return None
    size = max(11, round(w * 0.016))
    strip = max(round(w * 0.04), size + 8)
    new_open = svg_open.replace(m.group(0), f'viewBox="{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h + strip)}"', 1)
    hm = re.search(r'\sheight="([\d.]+)"', new_open)
    if hm:  # a fixed height must grow with the viewBox, or the drawing shrinks
        ratio = (h + strip) / h
        new_open = new_open.replace(hm.group(0), f' height="{fmt(round(float(hm.group(1)) * ratio))}"', 1)
    text = (f'<text class="svg-credit" x="{fmt(x + w - size * 0.6)}" y="{fmt(y + h + strip * 0.68)}" '
            f'text-anchor="end" font-size="{size}" fill="currentColor" opacity=".8" aria-hidden="true">'
            f'roshantrivedi.co.in</text>')
    return new_open, body + text

total = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(SKIP_DIRS):
        continue
    s = p.read_text(encoding="utf-8")
    if "<svg" not in s:
        continue
    out, pos, n = [], 0, 0
    for m in OPEN.finditer(s):
        if m.start() < pos:
            continue
        end = s.find("</svg>", m.end())
        if end < 0:
            break
        body = s[m.end():end]
        r = credit(m.group(0), body)
        out.append(s[pos:m.start()])
        if r:
            out.append(r[0] + r[1]); n += 1
        else:
            out.append(m.group(0) + body)
        out.append("</svg>"); pos = end + len("</svg>")
    out.append(s[pos:])
    if n:
        p.write_text("".join(out), encoding="utf-8")
        total += n
        print(f"{rel}: {n}")
print("credited diagrams:", total)
