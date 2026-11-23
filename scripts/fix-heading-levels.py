#!/usr/bin/env python3
"""Checks that no page skips a heading level inside <main> (an h1 followed by an h3, say).
Screen reader users move through a page by heading level, so a skipped level hides part of the outline.

    python3 scripts/fix-heading-levels.py           # report skips
    python3 scripts/fix-heading-levels.py --fix     # repair the web books (the same rule web_book.py now applies)
"""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from web_book import fix_levels

SKIP = ("_site", "node_modules", "agent-skills", "_layouts", ".git")
fix, bad = "--fix" in sys.argv, []
for p in sorted(ROOT.rglob("*.html")):
    if any(x in p.parts for x in SKIP):
        continue
    s = p.read_text(encoding="utf-8", errors="ignore")
    if "<main" not in s or "</main>" not in s:
        continue
    a, b = s.index("<main"), s.index("</main>")
    rel = str(p.relative_to(ROOT))
    if fix and re.match(r"(ca-mfa-lab|nhi-lab)/book/", rel):
        h1 = s.find("</h1>", a, b)
        if h1 != -1:
            nav = s.find('<nav class="wb-pn"', h1, b)
            end = nav if nav != -1 else b
            new = s[:h1 + 5] + fix_levels(s[h1 + 5:end]) + s[end:]
            if new != s:
                p.write_text(new, encoding="utf-8"); s = new
                a, b = s.index("<main"), s.index("</main>")
    levels = [int(x) for x in re.findall(r"<h([1-6])\b", s[a:b])]
    if any(y > x + 1 for x, y in zip(levels, levels[1:])):
        bad.append(rel)
if bad:
    sys.exit(f"{len(bad)} page(s) skip a heading level: " + ", ".join(bad))
print("no skipped heading levels")
