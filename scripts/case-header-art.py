#!/usr/bin/env python3
"""Put each case study's story illustration at the top of its own page. Safe to re-run."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
ns = {"__file__": str(ROOT / "scripts" / "case-art.py")}
exec((ROOT / "scripts" / "case-art.py").read_text().split("p = ROOT /")[0], ns)
n = 0
for href, parts in ns["SCENES"].items():
    p = ROOT / href.strip("/") / "index.html"
    h = p.read_text()
    h = re.sub(r'\s*<div class="cs-art"[^>]*>.*?</svg></div>', "", h, flags=re.S)
    art = f'\n        <div class="cs-art" aria-hidden="true">{ns["scene"](parts)}</div>'
    h2, k = re.subn(r'(<header class="hero[^"]*">)', lambda m: m.group(1) + art, h, count=1)
    if k:
        p.write_text(h2); n += 1
print("header art on", n, "pages")
