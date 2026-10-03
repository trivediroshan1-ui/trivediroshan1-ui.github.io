#!/usr/bin/env python3
"""Make a 1200x630 share image for every article, in the same style as the
case-study images. Reads share_title / share_label / share_accent from each
post's front matter (in _posts and _drafts) and writes
assets/og-post-<slug>.png. Run from the repo root:

    python3 scripts/build-share-images.py            # published posts
    python3 scripts/build-share-images.py --drafts   # preview drafts too

Fonts are the site's own DM Sans and JetBrains Mono files in assets/.
Needs Playwright with Chromium.
"""
import re, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
ACCENTS = {"cyan": "#4de2ff", "green": "#7ee8c0", "amber": "#ffc857", "violet": "#b8aef0"}

def front(path):
    m = re.match(r"---\n(.*?)\n---", path.read_text(), re.S)
    out = {}
    for line in (m.group(1) if m else "").splitlines():
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip('"')
    return out

def slug(path):
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)

HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{font-family:'DM Sans';font-weight:700;src:url(file://@@r@@/assets/dm-sans-latin-700-normal-DvUfVpUG.woff2)}
@font-face{font-family:'DM Sans';font-weight:500;src:url(file://@@r@@/assets/dm-sans-latin-500-normal-B9HHJjqV.woff2)}
@font-face{font-family:'DM Sans';font-weight:600;src:url(file://@@r@@/assets/dm-sans-latin-600-normal-Aqo67rzb.woff2)}
@font-face{font-family:'JetBrains Mono';font-weight:700;src:url(file://@@r@@/assets/jetbrains-mono-latin-bold.woff)}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#04060c;position:relative;overflow:hidden;font-family:'DM Sans',sans-serif;color:#fff}
.glow{position:absolute;inset:0;background:radial-gradient(ellipse 520px 380px at 1010px 90px,@@a@@22,transparent 70%),radial-gradient(ellipse 420px 300px at 90px 600px,@@a@@14,transparent 70%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:60px 60px;mask-image:linear-gradient(115deg,transparent 30%,#000 100%)}
.bar{position:absolute;left:72px;top:72px;bottom:72px;width:6px;border-radius:3px;background:@@a@@}
.label{position:absolute;left:112px;top:72px;font:700 24px 'JetBrains Mono',monospace;letter-spacing:.14em;color:@@a@@;text-transform:uppercase}
.title{position:absolute;left:112px;right:90px;top:140px;bottom:150px;display:flex;align-items:center;font-weight:700;font-size:@@fs@@px;line-height:1.12;letter-spacing:-.01em;text-wrap:balance}
.by{position:absolute;left:112px;bottom:72px;font-size:24px;font-weight:600}
.by span{color:#9fb0cf;font-weight:500}
.url{position:absolute;right:80px;bottom:72px;font-size:24px;color:#9fb0cf;font-weight:500}
</style><div class=glow></div><div class=grid></div><div class=bar></div>
<div class=label>@@label@@</div><div class=title>@@title@@</div>
<div class=by>Roshan Trivedi <span>&middot; Identity security</span></div><div class=url>roshantrivedi.co.in</div>"""

# Section pages: name -> (title, label, accent). Home keeps the profile card.
PAGES = {
    "about": ("About Roshan Trivedi", "About", "cyan"),
    "ai": ("AI and Agentic Security", "AI · Identity security", "violet"),
    "now": ("What I'm working on now", "Now", "green"),
    "resume": ("Resume: Roshan Trivedi", "Resume", "amber"),
    "writing": ("Writing on identity and privileged access", "Writing", "green"),
    "case-studies": ("Case Studies", "Case studies", "cyan"),
    "tier-check": ("PAM Tier Check", "Tool · Privileged access", "amber"),
}

def main():
    # Drafts are skipped on purpose: an image file is public, so a draft's
    # title would be visible before the post is. The image is made when the
    # post moves to _posts. Pass --drafts to preview them locally.
    posts = sorted((ROOT / "_posts").glob("*.md"))
    if "--drafts" in sys.argv:
        posts += sorted((ROOT / "_drafts").glob("*.md"))
    todo = []
    for p in posts:
        fm = front(p)
        if "share_title" not in fm:
            print("skip (no share_title):", p.name); continue
        todo.append((slug(p), fm))
    for n, (t, l, a) in PAGES.items():
        todo.append(("page-" + n, {"share_title": t, "share_label": l, "share_accent": a}))
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
        for s, fm in todo:
            title = fm["share_title"]
            fs = 72 if len(title) <= 34 else 62 if len(title) <= 60 else 54
            vals = dict(r=str(ROOT), a=ACCENTS.get(fm.get("share_accent", "cyan"), "#4de2ff"),
                        label=fm.get("share_label", "Article"), title=title.replace("&", "&amp;"), fs=str(fs))
            html = HTML
            for k, v in vals.items():
                html = html.replace("@@" + k + "@@", v)
            tmp = ROOT / "scripts" / ".share-tmp.html"
            tmp.write_text(html)
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            out = ROOT / "assets" / f"og-post-{s}.png"
            pg.screenshot(path=str(out)); print("wrote", out.relative_to(ROOT))
        b.close()
    (ROOT / "scripts" / ".share-tmp.html").unlink(missing_ok=True)

if __name__ == "__main__":
    sys.exit(main())
