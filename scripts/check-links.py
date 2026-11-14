#!/usr/bin/env python3
"""Fail if an internal link points at a file or folder that is not in the repo.

Project-page paths served from other repos under the same domain are listed
in EXTERNAL_PATHS. Posts under /writing/ come from _posts (Jekyll)."""
import os, re, sys
from urllib.parse import urlparse

EXTERNAL_PATHS = {"/mcp-human-approval-gateway/"}
skip_dirs = {".git", "_site", "node_modules", "worker", "archive"}
pages = {}
for dp, dn, fn in os.walk("."):
    dn[:] = [d for d in dn if d not in skip_dirs]
    for f in fn:
        if f.endswith(".html"):
            p = os.path.join(dp, f)
            pages[p] = open(p, encoding="utf-8", errors="ignore").read()

def exists(u):
    p = u.lstrip("/")
    if u.startswith("/writing/"):
        return True
    return any(os.path.isfile(c) for c in (p, os.path.join(p, "index.html"), p + ".html"))

bad = set()
for f, t in pages.items():
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', t):
        u = m.group(1)
        if u.startswith(("mailto:", "tel:", "data:", "{{", "javascript:")):
            continue
        if u.startswith("http"):
            if not u.startswith("https://roshantrivedi.co.in"):
                continue
            u = urlparse(u).path or "/"
        if not u.startswith("/"):
            u = "/" + os.path.normpath(os.path.join(os.path.dirname(f), u)).lstrip("./")
        if u == "/" or u in EXTERNAL_PATHS:
            continue
        if not exists(u):
            bad.add((f, u))
# Share images: every og:image and twitter:image must exist, and so must the
# image each post will ask for (assets/og-post-<slug>.png when it has share_title).
for f, t in pages.items():
    for m in re.finditer(r'<meta[^>]+(?:og:image|twitter:image)"[^>]+content="https://roshantrivedi\.co\.in(/[^"{?]+)', t):
        if not os.path.isfile(m.group(1).lstrip("/")):
            bad.add((f, m.group(1) + " (share image)"))
if os.path.isdir("_posts"):
    for name in sorted(os.listdir("_posts")):
        if name.endswith(".md") and re.search(r"^share_title:", open(os.path.join("_posts", name), encoding="utf-8").read(), re.M):
            img = "assets/og-post-" + re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name[:-3]) + ".png"
            if not os.path.isfile(img):
                bad.add(("_posts/" + name, "/" + img + " (share image)"))

# One version stamp per file: the same /assets/ file must not appear with two different ?v= values
# (or with and without one) across pages, or visitors get mixed cached copies.
stamps = {}
for f, t in pages.items():
    for m in re.finditer(r'(?:href|src)="(/assets/[^"?#]+)(\?v=[^"]*)?"', t):
        stamps.setdefault(m.group(1), {}).setdefault(m.group(2) or "(none)", f)
for a, v in sorted(stamps.items()):
    if len(v) > 1:
        bad.add((next(iter(v.values())), a + " (different ?v= values: " + ", ".join(sorted(v)) + ")"))

for f, u in sorted(bad):
    print(f"broken: {f} -> {u}")
print(len(bad), "broken internal links")
sys.exit(1 if bad else 0)
