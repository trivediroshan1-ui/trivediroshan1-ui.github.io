#!/usr/bin/env python3
"""Rebuilds sitemap.xml with a real <lastmod> for every URL (October 2026 audit: every entry used to say 2026-10-20,
which teaches search engines to ignore the field). <priority> is dropped; Google ignores it.

Order of evidence for each URL's lastmod:
  1. the file has uncommitted changes            -> today
  2. a post's front matter (last_modified_at, then date)
  3. the page's own JSON-LD "dateModified"
  4. the date of the last git commit that touched the file
  5. whatever the old sitemap said
Run from anywhere:  python3 scripts/build-sitemap.py
New pages and posts are added automatically. With --check it changes nothing and exits 1
if a public page or post is missing from sitemap.xml (CI runs this).
"""
import datetime, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://roshantrivedi.co.in"
old = (ROOT / "sitemap.xml").read_text()
urls = re.findall(r"<loc>(.*?)</loc>(?:<priority>[^<]*</priority>)?(?:<lastmod>([^<]*)</lastmod>)?", old)
today = datetime.date.today().isoformat()

def git(*a):
    try: return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception: return ""
dirty = set(git("status", "--porcelain").splitlines())
dirty = {l[3:].strip() for l in dirty}

def visible_text(h):
    h = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()

def content_changed(rel):
    """Only count a page as changed when its visible text changed, not when a script only touched <head>."""
    if rel not in dirty: return False
    before = git("show", "HEAD:" + rel)
    if not before: return True
    return visible_text(before) != visible_text((ROOT / rel).read_text(encoding="utf-8"))
many_commits = git("rev-list", "--count", "HEAD") not in ("", "0", "1")

POSTS = {re.sub(r"^\d{4}-\d{2}-\d{2}-", "", p.stem): p for p in (ROOT / "_posts").glob("*.md")}

def lastmod(loc, prev):
    path = loc.replace(SITE, "").strip("/")
    if path.startswith("writing/") and path.split("/")[-1] in POSTS:
        f = POSTS[path.split("/")[-1]]; rel = f.relative_to(ROOT).as_posix()
        before = git("show", "HEAD:" + rel)
        body = lambda s: s.split("---", 2)[-1].strip()
        if rel in dirty and (not before or body(before) != body(f.read_text())): return today
        fm = f.read_text().split("---")[1]
        m = re.search(r"^last_modified_at:\s*(\d{4}-\d{2}-\d{2})", fm, re.M) or re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
        return m.group(1) if m else prev
    f = ROOT / (path + "/index.html" if path else "index.html")
    if not f.exists(): return prev or today
    rel = f.relative_to(ROOT).as_posix()
    if content_changed(rel): return today
    m = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})"', f.read_text(encoding="utf-8"))
    if m: return m.group(1)
    if many_commits:
        d = git("log", "-1", "--format=%cs", "--", rel)
        if d: return d
    return prev or today

def public_pages():
    """Every page a visitor can reach: index.html files outside build folders, minus noindex pages, plus posts."""
    skip = ("archive/", "scripts/", "assets/", "_site/", "node_modules/", "_layouts/", "_includes/", ".git/")
    found = []
    for f in sorted(ROOT.glob("**/index.html")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(skip): continue
        h = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'<meta name="robots" content="[^"]*noindex', h): continue
        found.append(SITE + "/" + rel[: -len("index.html")])
    found += [SITE + "/writing/" + slug + "/" for slug in sorted(POSTS)]
    return found

known = {loc for loc, _ in urls}
missing = [u for u in public_pages() if u not in known]
if "--check" in sys.argv:
    if missing:
        print("Missing from sitemap.xml (run python3 scripts/build-sitemap.py):"); [print("  " + u) for u in missing]
        sys.exit(1)
    print("sitemap complete:", len(urls), "urls"); sys.exit(0)
urls += [(u, "") for u in missing]
if missing: print("added:", *missing, sep="\n  ")

out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, prev in urls:
    out.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod(loc, prev)}</lastmod></url>")
out.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(out) + "\n")
print("sitemap urls:", len(urls))
