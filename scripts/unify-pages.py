#!/usr/bin/env python3
"""Give inner pages the October 2026 look: refresh.css, breadcrumbs instead of "back to" links,
one footer, and no old button row on the MCP lab pages. Safe to re-run."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"index.html", "labs/index.html", "book/index.html", "mcp-lab-portal/index.html",
        "secure-india-exams/index.html", "design-system/index.html"}
CSS = '<link rel="stylesheet" href="/assets/refresh.css?v=20261019c">'
FOOT = ('<footer class="hg-foot"><div><span>&copy; 2026 Roshan Trivedi &middot; Bengaluru, India &middot; Privacy-safe portfolio</span>'
        '<nav aria-label="Footer"><a href="/case-studies/">Work</a><a href="/labs/">Labs</a><a href="/book/">Book</a>'
        '<a href="/writing/">Writing</a><a href="/about/">About</a><a href="/now/">Now</a><a href="/ai/">How I use AI</a>'
        '<a href="/#contact">Contact</a><a href="/feed.xml">RSS</a></nav></div></footer>')
NAMES = {"all case studies": "Work", "case studies": "Work", "writing": "Writing"}

def crumbs(m):
    links = re.findall(r'<a class="back" href="([^"]*)"[^>]*>(.*?)</a>', m.group(0))
    parents = [(h, NAMES.get(t.strip(), t.strip())) for h, t in links if h != "/"]
    if not parents:
        return ""
    out = '<a href="/">Home</a>' + "".join(f'<span aria-hidden="true">/</span><a href="{h}">{t}</a>' for h, t in parents)
    return f'<nav class="crumbs" aria-label="Breadcrumb">{out}</nav>'

n = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel in SKIP or rel.startswith(("worker/", ".git/")):
        continue
    h = p.read_text(); o = h
    h = re.sub(r'<link rel="stylesheet" href="/assets/refresh\.css[^"]*">\s*', "", h)
    h = re.sub(r'(<link rel="stylesheet" href="/assets/sitebar\.css[^"]*">)', lambda m: m.group(1) + "\n    " + CSS, h, count=1)
    h = re.sub(r'<nav class="back-row"[^>]*>.*?</nav>', crumbs, h, flags=re.S)
    h = re.sub(r'\s*<nav class="mcp-tabs"[^>]*>.*?</nav>', "", h, flags=re.S)
    h = re.sub(r'\s*<footer class="page-footer">.*?</footer>', "", h, flags=re.S)
    if 'class="hg-foot"' not in h:
        if "</main>" in h:
            h = h.replace("</main>", "</main>\n    " + FOOT, 1)
        else:
            h = h.replace("</body>", "    " + FOOT + "\n  </body>", 1)
    if h != o:
        p.write_text(h); n += 1
print("pages updated:", n)
