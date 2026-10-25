#!/usr/bin/env python3
"""Build the list behind the Ctrl+K search box (assets/palette-data.js): every page, every post,
and a few actions. Run after adding a page or post: python3 scripts/build-palette.py"""
import re, html, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"design-system/index.html"}

def meta(h, prop):
    m = re.search(r'<meta[^>]+(?:property|name)="' + re.escape(prop) + r'"[^>]+content="([^"]*)"', h)
    return html.unescape(m.group(1)).strip() if m else ""

idx = (ROOT / "case-studies" / "index.html").read_text()
KW = {m.group(1): m.group(2) for m in re.finditer(r'<a class="card"[^>]*href="([^"]+)"[^>]*data-keywords="([^"]*)"', idx)}
KW.update({m.group(2): m.group(1) for m in re.finditer(r'<a class="card"[^>]*data-keywords="([^"]*)"[^>]*href="([^"]+)"', idx)})
BADGE = {m.group(1): html.unescape(m.group(2)) for m in re.finditer(r'<a class="card"[^>]*href="([^"]+)".*?<span class="badge"[^>]*>([^<]*)</span>', idx, re.S)}

items = []
for p in sorted(ROOT.rglob("index.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("worker/", ".git/", "_site/")) or rel in SKIP:
        continue
    h = p.read_text()
    url = "/" + rel[: -len("index.html")]
    t = re.sub(r"\s*[·|]\s*Roshan Trivedi.*$", "", meta(h, "og:title") or "").strip()
    if not t:
        m = re.search(r"<title>(.*?)</title>", h, re.S)
        t = re.sub(r"\s*[·|]\s*Roshan Trivedi.*$", "", html.unescape(m.group(1)).strip()) if m else url
    if url == "/":
        t = "Home"
    g = ("Case study" if url.startswith("/case-studies/") and url != "/case-studies/" else
         "Lab" if url.startswith(("/mcp-lab", "/labs", "/tools", "/secure-india")) else
         "Writing" if url.startswith("/writing") else "Page")
    items.append({"t": t, "u": url, "g": g, "d": (meta(h, "description") or meta(h, "og:description"))[:150],
                  "k": " ".join(filter(None, [KW.get(url, ""), BADGE.get(url, "")]))})

for f in sorted((ROOT / "_posts").glob("*.md")):
    fm = re.match(r"---\n(.*?)\n---", f.read_text(), re.S).group(1)
    get = lambda k: (re.search(r"^" + k + r':\s*"?(.*?)"?\s*$', fm, re.M) or [None, ""])[1]
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
    tags = get("tags").strip("[]").replace(",", " ").replace("-", " ")
    items.append({"t": get("title"), "u": f"/writing/{slug}/", "g": "Writing", "d": (get("description") or get("excerpt"))[:150], "k": tags})

EXTRA = {"/resume/": "cv cyberark sailpoint beyondtrust hashicorp vault entra delinea saviynt strongdm wiz clutch certifications",
         "/about/": "career background bio", "/labs/": "projects experiments demo", "/book/": "pdf free mcp human approval"}
for it in items:
    if it["u"] in EXTRA:
        it["k"] = (it["k"] + " " + EXTRA[it["u"]]).strip()
items += [
    {"t": "The approval gateway code", "u": "/mcp-human-approval-gateway/", "g": "Lab", "d": "Try the MCP human approval gateway yourself", "k": "mcp code github try demo"},
    {"t": "Download my résumé (PDF)", "u": "/Roshan_Trivedi_Resume.pdf", "g": "Action", "d": "", "k": "resume cv download"},
    {"t": "Download the book (PDF)", "u": "/assets/who-approved-that-book.pdf", "g": "Action", "d": "Who Approved That? 138 pages, free", "k": "book download pdf mcp"},
    {"t": "Email me", "u": "mailto:trivedi.roshan1@gmail.com", "g": "Action", "d": "trivedi.roshan1@gmail.com", "k": "contact mail hello"},
    {"t": "LinkedIn", "u": "https://www.linkedin.com/in/roshan-trivedi-ciam/", "g": "Action", "d": "", "k": "contact profile"},
    {"t": "GitHub", "u": "https://github.com/trivediroshan1-ui", "g": "Action", "d": "", "k": "code repositories"},
]
out = ROOT / "assets" / "palette-data.js"
out.write_text("window.RT_PALETTE=" + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("palette items:", len(items), "bytes:", out.stat().st_size)
