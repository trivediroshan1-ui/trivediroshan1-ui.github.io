#!/usr/bin/env python3
"""Put the same Content-Security-Policy and Referrer-Policy meta tags on every page.
GitHub Pages cannot send security headers, so the browser gets them from these tags instead.
Keep POLICY in step with the Content-Security-Policy line in _headers (which adds frame-ancestors,
a rule that only works as a real header). No page may have an inline <script> that runs code:
put scripts in /assets/*.js. Safe to re-run: python3 scripts/set-security-meta.py"""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
POLICY = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
          "script-src 'self' https://static.cloudflareinsights.com; "
          "connect-src 'self' https://*.workers.dev https://cloudflareinsights.com; "
          "object-src 'none'; base-uri 'self'; form-action 'self' https://buttondown.com; upgrade-insecure-requests")
TAGS = (f'<meta http-equiv="Content-Security-Policy" content="{POLICY}">\n'
        '    <meta name="referrer" content="strict-origin-when-cross-origin">')
n = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("worker/", ".git/", "assets/")):
        continue
    h = p.read_text(); o = h
    h = re.sub(r'\s*<meta http-equiv="Content-Security-Policy"[^>]*>', "", h)
    h = re.sub(r'\s*<meta name="referrer"[^>]*>', "", h)
    m = re.search(r'<meta charset="?[^>]*>', h, re.I)
    if not m:
        print("no charset meta:", rel); continue
    h = h[: m.end()] + "\n    " + TAGS + h[m.end():]
    bad = [s for s in re.findall(r"<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>", h)]
    if bad:
        print("inline script left in", rel, bad[:2])
    if h != o:
        p.write_text(h); n += 1
print("pages updated:", n)
