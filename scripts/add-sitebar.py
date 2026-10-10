#!/usr/bin/env python3
"""Add the shared slim nav and the 'where next' band to inner pages. Safe to re-run."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"index.html", "404.html", "design-system/index.html", "secure-india-exams/index.html", "worker"}
LINKS = [("Case studies", "/case-studies/", "/case-studies"), ("Writing", "/writing/", "/writing"),
         ("MCP lab", "/mcp-lab-case-study/", "/mcp-lab"), ("About", "/about/", "/about"),
         ("R&eacute;sum&eacute;", "/resume/", "/resume")]
def nav(path):
    items = ""
    for label, href, prefix in LINKS:
        cur = ' aria-current="page"' if path.startswith(prefix) else ""
        items += f'<li><a href="{href}"{cur}>{label}</a></li>'
    return ('<nav class="hg-sitenav" aria-label="Main"><a class="brand" href="/"><i aria-hidden="true"></i><span>Roshan Trivedi</span></a>'
            f'<ul>{items}</ul></nav>\n')
NEXT = '''<aside class="hg-next" aria-labelledby="hg-next-t">
        <p class="eyebrow">Where next</p>
        <p class="ttl" id="hg-next-t">Keep reading, or get in touch</p>
        <p class="lede">Everything here is written to be useful on its own. If it matches a problem you are working on, I would like to hear how you handle it.</p>
        <div class="grid">
          <a href="/case-studies/" style="--k:#7df2d0"><b>All case studies</b><span>Privileged access, credentials, governance and agent identity.</span></a>
          <a href="/#mcp-flow" style="--k:#4de2ff"><b>The MCP approval lab</b><span>Follow one request through the gateway, with the tests behind it.</span></a>
          <a href="/Roshan_Trivedi_Resume.pdf" style="--k:#c4b5fd"><b>R&eacute;sum&eacute;</b><span>Roles, focus areas and background (PDF).</span></a>
          <a href="/#contact" style="--k:#f7c873"><b>Contact</b><span>LinkedIn, GitHub and email, all in one place.</span></a>
        </div>
      </aside>
      '''
n = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel in SKIP or rel.startswith(("worker/", "_", "tools/")): continue
    h = p.read_text()
    if "hg-sitenav" in h or 'class="page-footer"' not in h: continue
    url = "/" + rel[:-10] if rel.endswith("index.html") else "/" + rel
    h = re.sub(r'(</head>)', '    <link rel="stylesheet" href="/assets/sitebar.css?v=20261010b">\n  \\1', h, count=1)
    m = re.search(r'(<a class="skip"[^>]*>[^<]*</a>\s*)', h)
    if m: h = h[:m.end()] + nav(url) + h[m.end():]
    else:
        m = re.search(r'<body[^>]*>\s*', h); h = h[:m.end()] + nav(url) + h[m.end():]
    h = h.replace('<footer class="page-footer">', NEXT + '<footer class="page-footer">', 1)
    p.write_text(h); n += 1
print("updated", n)
