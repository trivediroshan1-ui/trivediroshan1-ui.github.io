#!/usr/bin/env python3
"""Put the same main menu on every page except the home page (which has its own header).
Replaces an existing <nav class="hg-sitenav"> or inserts one after the skip link / <body>.
Safe to re-run. Run from anywhere: python3 scripts/set-sitenav.py
"""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"index.html"}
# label, href, url prefixes that mark it as the current section
LINKS = [
    ("Work", "/case-studies/", ("/case-studies",)),
    ("Labs", "/labs/", ("/labs", "/mcp-lab", "/secure-india-exams", "/tools")),
    ("Book", "/book/", ("/book",)),
    ("Writing", "/writing/", ("/writing",)),
    ("About", "/about/", ("/about", "/now", "/ai")),
    ("Contact", "/#contact", ()),
]
STATIC = {"book/index.html", "mcp-lab-portal/index.html", "secure-india-exams/index.html", "tools/tier-check/index.html"}  # these keep their own sticky section bar
CSS = '<link rel="stylesheet" href="/assets/sitebar.css?v=20261019b">'

def nav(url, static):
    items = ""
    for label, href, prefixes in LINKS:
        cur = ' aria-current="page"' if any(url.startswith(p) for p in prefixes) else ""
        cls = ' class="ct"' if label == "Contact" else ""
        items += f'<li{cls}><a href="{href}"{cur}>{label}</a></li>'
    res_cur = ' aria-current="page"' if url.startswith("/resume") else ""
    items += f'<li class="res"><a href="/resume/"{res_cur}>R&eacute;sum&eacute;</a></li>'
    cls = "hg-sitenav is-static" if static else "hg-sitenav"
    return (f'<nav class="{cls}" aria-label="Main"><a class="brand" href="/"><i aria-hidden="true">RT</i>'
            f'<span>Roshan Trivedi</span></a><ul>{items}</ul></nav>')

n = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel in SKIP or rel.startswith(("worker/", ".git/", "node_modules/")):
        continue
    h = p.read_text()
    if rel == "_layouts/post.html":
        url = "/writing/x/"
    elif rel.endswith("index.html"):
        url = "/" + rel[: -len("index.html")]
    else:
        url = "/" + rel
    new = nav(url, rel in STATIC)
    if 'class="hg-sitenav' in h:
        h2 = re.sub(r'<nav class="hg-sitenav[^"]*"[^>]*>.*?</nav>', lambda m: new, h, count=1, flags=re.S)
    else:
        m = re.search(r'(<a class="skip"[^>]*>[^<]*</a>\s*)', h)
        if not m:
            m = re.search(r"<body[^>]*>\s*", h)
        h2 = h[: m.end()] + new + "\n" + h[m.end():]
    # one current stylesheet link
    h2 = re.sub(r'<link rel="stylesheet" href="/assets/sitebar\.css[^"]*">', CSS, h2)
    if CSS not in h2:
        h2 = h2.replace("</head>", "    " + CSS + "\n  </head>", 1)
    # old links that pointed at the home page's flow demo now go to the labs page
    h2 = h2.replace('href="/#mcp-flow"', 'href="/labs/#mcp-flow"')
    if h2 != h:
        p.write_text(h2)
        n += 1
print("pages updated:", n)
