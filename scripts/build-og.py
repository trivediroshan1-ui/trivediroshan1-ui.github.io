#!/usr/bin/env python3
"""Share images (1200 x 630) for every page in the October 2026 look. Reads each page's og:image file name,
title and description, and draws the page's story illustration on the right. Run from anywhere:
    python3 scripts/build-og.py
"""
import re, html, pathlib, base64
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
ns = {"__file__": str(ROOT / "scripts" / "case-art.py")}
exec((ROOT / "scripts" / "case-art.py").read_text().split("p = ROOT /")[0], ns)
SCENES, scene = ns["SCENES"], ns["scene"]

PAGE_SCENES = {  # pages that are not case studies
    "about": ("person", "list", "shieldok"), "ai": ("person", "robot", "check"), "now": ("clock", "list", "check"),
    "resume": ("idcard", "list", "docok"), "writing": ("doc", "list", "check"), "pam-series": ("vault", "doc", "doc"),
    "case-studies": ("grid", "search", "doc"), "tier-check": ("key", "pyramid", "shield"), "labs": ("robot", "person", "tool"),
    "mcp-lab-case-study": ("robot", "person", "tool"), "mcp-lab-results": ("list", "check", "doc"),
    "mcp-lab-use-cases": ("robot", "list", "check"), "mcp-lab-in-depth": ("robot", "search", "doc"),
    "mcp-lab-portal": ("grid", "gauge", "doc"),
}
LABELS = {"about": "About", "ai": "How I use AI", "now": "Now", "resume": "Résumé", "writing": "Writing",
          "pam-series": "The PAM series", "case-studies": "Work · 20 case studies", "tier-check": "Tool · self-check",
          "labs": "Labs and projects", "mcp-lab-case-study": "HumanGate MCP lab", "mcp-lab-results": "HumanGate MCP lab · results",
          "mcp-lab-use-cases": "HumanGate MCP lab · use cases", "mcp-lab-in-depth": "HumanGate MCP lab · in depth",
          "mcp-lab-portal": "HumanGate MCP lab · portal"}
FONTS = "".join(f"@font-face{{font-family:'{f}';font-weight:{w};src:url(file://{ROOT}/assets/{n})}}" for f, w, n in [
    ("DM Sans", 700, "dm-sans-latin-700-normal-DvUfVpUG.woff2"), ("DM Sans", 500, "dm-sans-latin-500-normal-B9HHJjqV.woff2"),
    ("Manrope", 500, "manrope-latin-500-normal-BYYD-dBL.woff2")])
PATH = (ROOT / "assets" / "bg-path.svg").read_text()
PATH_URI = "data:image/svg+xml;base64," + base64.b64encode(PATH.encode()).decode()

def card(label, title, desc, art_svg, accent, photo=None):
    t = html.escape(title); d = html.escape(desc)
    size = 64 if len(title) < 34 else 54 if len(title) < 56 else 46
    right = (f'<img class="ph" src="{photo}">' if photo else f'<div class="art" style="color:{accent}">{art_svg}</div>')
    return f"""<!doctype html><meta charset=utf-8><style>{FONTS}
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;overflow:hidden;position:relative;background:#05061a;color:#f5f3ff;font-family:'DM Sans',sans-serif}}
.bg{{position:absolute;inset:0;background:radial-gradient(620px 460px at 92% 20%,rgba(124,58,237,.42),transparent 70%),radial-gradient(520px 400px at 0% 100%,rgba(76,29,149,.35),transparent 70%)}}
.path{{position:absolute;inset:0;background:url({PATH_URI}) center/cover;opacity:1.6}}
.l{{position:absolute;left:80px;top:78px;width:570px}}
.k{{display:inline-block;font:700 19px 'DM Sans';letter-spacing:.16em;text-transform:uppercase;color:{accent};margin-bottom:26px}}
h1{{font-weight:700;font-size:{size}px;line-height:1.04;letter-spacing:-.035em}}
p{{font:500 23px/1.45 'Manrope';color:#c4bfe0;margin-top:22px;max-width:600px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.by{{position:absolute;left:80px;bottom:62px;display:flex;align-items:center;gap:16px;font-size:22px}}
.by i{{width:46px;height:46px;border-radius:12px;background:linear-gradient(135deg,#58e6f6,#a78bfa);color:#070a1f;display:grid;place-items:center;font-style:normal;font-weight:700;font-size:18px}}
.by span{{color:#9590b8}}
.art{{position:absolute;right:20px;top:170px;width:540px}}
.art svg{{width:540px;height:auto}}
.ph{{position:absolute;right:90px;top:110px;width:340px;height:340px;border-radius:40px;object-fit:cover;border:2px solid rgba(88,230,246,.5);box-shadow:0 30px 80px rgba(0,0,0,.5)}}
</style><div class="bg"></div><div class="path"></div>
<div class="l"><span class="k">{html.escape(label)}</span><h1>{t}</h1><p>{d}</p></div>
{right}<div class="by"><i>RT</i><b>Roshan Trivedi</b><span>roshantrivedi.co.in</span></div>"""

def meta(h, prop):
    m = re.search(r'<meta[^>]+(?:property|name)="' + re.escape(prop) + r'"[^>]+content="([^"]*)"', h) or \
        re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="' + re.escape(prop) + r'"', h)
    return html.unescape(m.group(1)).strip() if m else ""

# badges from the Work page
idx = (ROOT / "case-studies" / "index.html").read_text()
BADGE = {m.group(1): (html.unescape(m.group(3)), m.group(2)) for m in re.finditer(
    r'<a class="card"[^>]*href="([^"]+)"[^>]*style="--c:([^"]+)">.*?<span class="badge"[^>]*>([^<]*)</span>', idx, re.S)}

jobs = []
for p in sorted(ROOT.rglob("index.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("worker/", ".git/")):
        continue
    h = p.read_text()
    img = meta(h, "og:image")
    m = re.search(r"/assets/(og-[a-z0-9-]+\.png)$", img)
    if not m or m.group(1) in ("og-post-page-book.png",):
        continue
    out = m.group(1)
    title = re.sub(r"\s*[·|]\s*Roshan Trivedi.*$", "", meta(h, "og:title")) or "Roshan Trivedi"
    desc = meta(h, "og:description") or meta(h, "description")
    url = "/" + rel[: -len("index.html")]
    key = url.strip("/").split("/")[-1] or "home"
    if url == "/":
        jobs.append((out, card("Identity security · product leadership", "Security starts with identity.",
                     "Credential management, PAM, non-human identity, and a person in the loop when an AI agent acts.",
                     "", "#a78bfa", photo=f"file://{ROOT}/assets/roshan-trivedi.webp")))
        continue
    if url in BADGE:
        label, accent = BADGE[url]
        label = "Case study · " + label
        parts = SCENES[url]
    else:
        label, accent = LABELS.get(key, "Roshan Trivedi"), "#a78bfa"
        parts = PAGE_SCENES.get(key, ("person", "shield", "check"))
    if url.startswith("/case-studies/") and url != "/case-studies/" and url not in BADGE:
        continue
    jobs.append((out, card(label, title, desc, scene(parts), accent)))

# blog posts: front matter share_title / share_label / description
POST_SCENES = {"pam": ("vault", "doc", "shieldok")}
for f in sorted((ROOT / "_posts").glob("*.md")):
    fm = re.match(r"---\n(.*?)\n---", f.read_text(), re.S).group(1)
    get = lambda k: (re.search(r"^" + k + r":\s*\"?(.*?)\"?\s*$", fm, re.M) or [None, ""])[1]
    if not get("share_title"):
        continue
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
    desc = get("description") or get("excerpt") or get("title")
    parts = POST_SCENES.get(get("series"), ("robot", "warn", "shield"))
    jobs.append((f"og-post-{slug}.png", card(get("share_label") or "Article", get("share_title") or get("title"), desc if desc != get("title") else "", scene(parts), "#7df2d0" if get("series") == "pam" else "#58e6f6")))

# the research paper
jobs.append(("og-post-page-secure-india-exams.png", card("Public research · Zero Trust", "Securing India's National Exams",
    "A Zero Trust architecture for high-stakes exams, from AI-assisted paper creation to verified destruction.", scene(("doc", "shield", "check")), "#fbbf24")))

with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    tmp = ROOT / "assets" / "_og_tmp.html"
    for out, doc in jobs:
        tmp.write_text(doc); pg.goto(tmp.as_uri(), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
        pg.screenshot(path=str(ROOT / "assets" / out))
    b.close(); tmp.unlink()
print("share images:", len(jobs))
