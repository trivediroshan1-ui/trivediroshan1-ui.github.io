#!/usr/bin/env python3
"""Adds (or refreshes) the footer at the end of <main> on every lab page: previous page, next page, the lab's book,
and a link to /topics/. The order is the order of each lab's own page list below.
Run after any script that regenerates lab pages:  python3 scripts/add-lab-foot.py"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
V = "20261114f"
LABS = {
  "ca": {"dir": "ca-mfa-lab", "book": "/ca-mfa-lab/ca-mfa-lab-book.pdf",
         "order": [("/ca-mfa-lab/", "Overview"), ("/ca-mfa-lab/framework/", "Framework"), ("/ca-mfa-lab/virtual-lab/", "Virtual lab"),
                   ("/ca-mfa-lab/register/", "Register"), ("/ca-mfa-lab/run-4/", "Run 4"), ("/ca-mfa-lab/sources/", "Sources and events")]},
  "nhi": {"dir": "nhi-lab", "book": "/nhi-lab/nhi-lab-book.pdf",
          "order": [("/nhi-lab/", "Overview"), ("/nhi-lab/framework/", "Framework"), ("/nhi-lab/market/", "Market"), ("/nhi-lab/method/", "What I did"),
                    ("/nhi-lab/audit/", "Audit data"), ("/nhi-lab/round-18/", "Round 18"), ("/nhi-lab/round-19/", "Round 19"),
                    ("/nhi-lab/register/", "Register"), ("/nhi-lab/stage-2/", "Stage 2"), ("/nhi-lab/roadmap/", "Roadmap"), ("/nhi-lab/explainer/", "Explainer")]},
  "agl": {"dir": "ai-governance-lab", "book": "/assets/ai-governance-lab-book.pdf",
          "order": [("/ai-governance-lab/", "Overview"), ("/ai-governance-lab/run/", "Run it"), ("/ai-governance-lab/try/", "Try it"),
                    ("/ai-governance-lab/cases/", "Every case"), ("/ai-governance-lab/diagrams/", "Diagrams"), ("/ai-governance-lab/evidence/", "Evidence"),
                    ("/ai-governance-lab/what-i-got-wrong/", "What I got wrong"), ("/ai-governance-lab/story/", "The story"), ("/ai-governance-lab/mac/", "Real assistant tests"),
                    ("/ai-governance-lab/transcripts/", "Transcripts"), ("/ai-governance-lab/implement/", "Implement it"), ("/ai-governance-lab/appendix/", "Appendix")]},
  "mcp": {"dir": None, "book": "/assets/who-approved-that-book.pdf",
          "order": [("/mcp-lab-case-study/", "Overview"), ("/mcp-lab-results/", "Results"), ("/mcp-lab-use-cases/", "Use cases"),
                    ("/mcp-lab-in-depth/", "In depth"), ("/mcp-lab-portal/", "Portal")]},
}
CSS = f'<link rel="stylesheet" href="/assets/lab-foot.css?v={V}">'

def url_of(p): return "/" + p.relative_to(ROOT).as_posix()[: -len("index.html")]

def pages_for(lab):
    if lab["dir"]:
        return sorted((ROOT / lab["dir"]).rglob("index.html"))
    return [ROOT / (u.strip("/") + "/index.html") for u, _ in lab["order"]]

def foot(lab, url):
    order = lab["order"]; urls = [u for u, _ in order]
    if url in urls:
        i = urls.index(url)
        prev = order[i - 1] if i > 0 else None
        nxt = order[i + 1] if i + 1 < len(order) else None
    else:  # a sub-page that is not in the list: back to the overview
        prev, nxt = order[0], None
    def link(cls, pair, word):
        if not pair: return f'<span class="{cls} off"></span>'
        return f'<a class="{cls}" href="{pair[0]}"><small>{word}</small><b>{pair[1]}</b></a>'
    return ('<nav class="lab-foot" aria-label="More in this lab">'
            + link("lf-prev", prev, "Previous" if url in urls else "Back to")
            + link("lf-next", nxt, "Next")
            + f'<span class="lf-extra"><a href="{lab["book"]}">Get the book</a><a href="/topics/">Browse by topic</a></span></nav>\n')

count = 0
for lab in LABS.values():
    for p in pages_for(lab):
        if not p.exists(): continue
        h = p.read_text(encoding="utf-8"); url = url_of(p)
        if "</main>" not in h: print("no main:", url); continue
        h = re.sub(r'<nav class="lab-foot".*?</nav>\n?', "", h, flags=re.S)
        h = h.replace("</main>", foot(lab, url) + "</main>", 1)
        if "lab-foot.css" not in h: h = h.replace("</head>", "  " + CSS + "\n  </head>", 1)
        else: h = re.sub(r"lab-foot\.css\?v=[0-9a-z]+", f"lab-foot.css?v={V}", h)
        p.write_text(h, encoding="utf-8"); count += 1
print("lab footers:", count)
