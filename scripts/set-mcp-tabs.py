#!/usr/bin/env python3
"""One tab bar across the MCP lab's pages, right under the main menu. Safe to re-run."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
TABS = [("Overview", "/mcp-lab-case-study/"), ("Results", "/mcp-lab-results/"), ("Use cases", "/mcp-lab-use-cases/"),
        ("In depth", "/mcp-lab-in-depth/"), ("Portal", "/mcp-lab-portal/")]
for _, href in TABS:
    p = ROOT / href.strip("/") / "index.html"
    h = p.read_text()
    cur = ' aria-current="page"'
    items = "".join(f'<li><a href="{u}"{cur if u == href else ""}>{l}</a></li>' for l, u in TABS)
    bar = (f'<nav class="hg-tabs" aria-label="MCP lab pages"><div><a class="lab" href="/labs/">HumanGate lab</a>'
           f'<ul>{items}</ul><a class="book" href="/book/">Read the book</a></div></nav>')
    h = re.sub(r'<nav class="hg-tabs".*?</nav>\n?', "", h, flags=re.S)
    h = re.sub(r'(<nav class="hg-sitenav[^"]*"[^>]*>.*?</nav>\n?)', lambda m: m.group(1).rstrip("\n") + "\n" + bar + "\n", h, count=1, flags=re.S)
    p.write_text(h)
print("tabs set on", len(TABS), "pages")
