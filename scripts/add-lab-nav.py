#!/usr/bin/env python3
"""Put the shared lab sub-nav on every lab page, replacing the old per-lab navs. Safe to re-run."""
import re, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lab_nav
V = "20261114h"
LINK = f'<link rel="stylesheet" href="/assets/lab-nav.css?v={V}">'
n = 0
for lab, v in lab_nav.LABS.items():
    pages = {h.split("#")[0] for t, h in v["primary"] + v["more"] if h.endswith("/") and not t.startswith("Related") and h.split("#")[0] not in ("/method/", "/mcp-human-approval-gateway/")}
    if lab == "agl":
        pages |= {f"/ai-governance-lab/round-{i}/" for i in range(5, 14)}
    for path in sorted(pages):
        p = ROOT / path.strip("/") / "index.html"
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        nav = lab_nav.render(lab, path)
        if "/assets/lab-nav.css" in s:  # update in place, so indentation never drifts
            s = re.sub(r'<link rel="stylesheet" href="/assets/lab-nav\.css[^"]*">', LINK, s, count=1)
        else:
            s = s.replace("</head>", "  " + LINK + "\n  </head>", 1)
        if '<nav class="lab-nav"' in s:
            s = re.sub(r'<nav class="lab-nav".*?</nav>', lambda m: nav, s, count=1, flags=re.S)
        elif '<nav class="nsub"' in s:
            s = re.sub(r'<nav class="nsub".*?</nav>', lambda m: nav, s, count=1, flags=re.S)
        elif '<nav class="hg-tabs"' in s:
            s = re.sub(r'<nav class="hg-tabs".*?</nav>', lambda m: nav, s, count=1, flags=re.S)
        else:
            assert s.count('<main id="main">') == 1, p
            s = s.replace('<main id="main">', '<main id="main">\n      ' + nav, 1)
        p.write_text(s, encoding="utf-8")
        n += 1
print("lab nav set on", n, "pages")
