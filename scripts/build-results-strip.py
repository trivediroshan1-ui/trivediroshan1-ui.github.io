#!/usr/bin/env python3
"""Draw each lab's results as a strip: one mark per case, in catalogue order.

Short green mark: the result matched my written guess. Tall red mark: my guess was wrong.
Hollow mark: the case was not run here. The marks differ in height as well as colour, so the
strip reads without colour too. Data: data/catalogue.json (built by scripts/build-catalogue.py).

Pages opt in with a marker pair, for example:
    <!-- rstrip:ca:start --><!-- rstrip:ca:end -->
Add "compact" for the short caption used on the home page cards:
    <!-- rstrip:ca:compact:start --><!-- rstrip:ca:compact:end -->

    python3 scripts/build-results-strip.py           # rewrite the strips
    python3 scripts/build-results-strip.py --check   # fail if a strip is out of date (CI)
"""
import json, math, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
cat = json.loads((ROOT / "data/catalogue.json").read_text(encoding="utf-8"))
WRONG_URL = {"ca": "/ca-mfa-lab/what-i-got-wrong/", "agl": "/ai-governance-lab/what-i-got-wrong/", "nhi": "/nhi-lab/audit/#wrong"}
KIND = {"As guessed": "ok", "Guess was wrong": "bad", "Not run here": "off"}
SHORT, TALL = 10, 20              # mark heights


def strip(lab, compact):
    cases = [c for c in cat["cases"] if c["lab"] == lab]
    kinds = [KIND.get(c["guess"]) for c in cases]
    if None in kinds:
        sys.exit(f"{lab}: a case has no recorded guess outcome; this lab cannot be drawn as a strip")
    n = len(kinds)
    # Home cards: one thin row. Lab pages: rows of up to 60 marks.
    PITCH, W, ROW = (3, 2, 24) if compact else (5, 3, 26)
    rows = 1 if compact else math.ceil(n / 60)
    cols = math.ceil(n / rows)
    groups = {"ok": [], "bad": [], "off": []}
    for i, k in enumerate(kinds):
        x, y0 = (i % cols) * PITCH, (i // cols) * ROW
        if k == "ok":
            groups[k].append(f'<rect x="{x}" y="{y0 + TALL - SHORT}" width="{W}" height="{SHORT}" rx="1"/>')
        elif k == "bad":
            groups[k].append(f'<rect x="{x}" y="{y0}" width="{W}" height="{TALL}" rx="1"/>')
        else:
            groups[k].append(f'<rect x="{x + .5}" y="{y0 + TALL - SHORT + .5}" width="{W - 1}" height="{SHORT - 1}" rx="1"/>')
    ok, bad, off = (len(groups[k]) for k in ("ok", "bad", "off"))
    width, height = cols * PITCH - (PITCH - W), rows * ROW - (ROW - TALL)
    label = f"{n} cases: {ok} as guessed, {bad} where my guess was wrong" + (f", {off} not run" if off else "")
    svg = (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{label}" '
           f'style="display:block;width:100%;max-width:{'100%' if compact else str(round(width * 1.5)) + 'px'};height:auto">'
           f'<g style="fill:var(--hg-exec)">{"".join(groups["ok"])}</g>'
           f'<g style="fill:var(--hg-refuse)">{"".join(groups["bad"])}</g>'
           + (f'<g style="fill:none;stroke:var(--hg-ink-3);stroke-width:1">{"".join(groups["off"])}</g>' if off else "")
           + '</svg>')
    if compact:
        cap = f'One mark per case. The tall red ones are where I guessed wrong.'
    else:
        cap = (f'Each mark is one of the {n} cases, in order. Short green: the result matched the guess I wrote down first. '
               f'Tall red: my guess was wrong ({bad}).' + (f' Hollow: not run here ({off}).' if off else "")
               + f' <a href="{WRONG_URL[lab]}">See what I got wrong</a>')
    return (f'<figure class="rstrip" style="margin:16px 0 0">{svg}'
            f'<figcaption style="margin-top:8px;font-size:13px;line-height:1.5;color:var(--hg-ink-2)">{cap}</figcaption></figure>')


MARK = re.compile(r"(<!-- rstrip:(\w+)(:compact)?:start -->).*?(<!-- rstrip:\2(?:\3)?:end -->)", re.S)
check, stale = "--check" in sys.argv, []
for page in sorted(ROOT.rglob("*.html")):
    if any(p in page.parts for p in ("node_modules", "_site", ".git")):
        continue
    h = page.read_text(encoding="utf-8")
    if "<!-- rstrip:" not in h:
        continue
    new = MARK.sub(lambda m: m.group(1) + strip(m.group(2), bool(m.group(3))) + m.group(4), h)
    if new != h:
        stale.append(str(page.relative_to(ROOT)))
        if not check:
            page.write_text(new, encoding="utf-8")
if check and stale:
    sys.exit("results strips out of date, run python3 scripts/build-results-strip.py: " + ", ".join(stale))
print(("results strips up to date" if check else "results strips written") + (f": {', '.join(stale)}" if stale and not check else ""))
