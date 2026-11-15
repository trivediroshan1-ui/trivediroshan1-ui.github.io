"""Wrap new page content in the site's current head, navigation and footer, taken from /labs/.

Used by build-catalogue.py, build-search.py and build-library.py so new pages match the rest
of the site without copying the shell by hand.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://roshantrivedi.co.in"
REVIEWED = "16 Nov 2026"  # bump when the generated pages are re-checked
FOOT_MARK = "Privacy-safe portfolio</span>"


def add_reviewed(page, date=REVIEWED):
    """Put "Last reviewed <date>" in the footer line, once. Pages that already show a date are left alone."""
    if re.search(r"Last (reviewed|updated)|and not updated since", page) or FOOT_MARK not in page:
        return page
    return page.replace(FOOT_MARK, f'Privacy-safe portfolio &middot; <span class="reviewed">Last reviewed {date}</span></span>', 1)


def shell(url, title, desc, body, crumbs, nav_current=None, head_extra="", foot_extra="", og_image=None, brand=True):
    src = (ROOT / "labs" / "index.html").read_text(encoding="utf-8")
    head, rest = src.split('<main id="main">', 1)
    foot = rest.split("</main>", 1)[1]
    t, d = html.escape(title + (" · Roshan Trivedi" if brand else "")), html.escape(desc)
    lit = lambda pat, rep, s: re.sub(pat, lambda m: rep, s)
    head = lit(r"<title>.*?</title>", f"<title>{t}</title>", head)
    head = lit(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{d}">', head)
    head = lit(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{SITE}{url}">', head)
    head = lit(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">', head)
    head = lit(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{d}">', head)
    head = lit(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{SITE}{url}">', head)
    if og_image:
        head = lit(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE}{og_image}">', head)
    head = re.sub(r'<meta name="twitter:(title|description)" content="[^"]*">',
                  lambda m: f'<meta name="twitter:{m.group(1)}" content="{t if m.group(1) == "title" else d}">', head)
    # the labs page's own scripts and styles
    head = re.sub(r'\s*<script defer src="/assets/flow(-data)?\.js"></script>', "", head)
    head = re.sub(r'\s*<link rel="stylesheet" href="/assets/(flow|coming-soon)\.css[^"]*">', "", head)
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": items},
        {"@type": "CollectionPage", "name": title, "url": SITE + url, "description": desc}]}
    ldtag = '<script type="application/ld+json" id="ld-site">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    head = re.sub(r'<script type="application/ld\+json" id="ld-site">.*?</script>', lambda m: ldtag, head, flags=re.S)
    head = head.replace("</head>", head_extra + "\n  </head>", 1)
    head = head.replace(' aria-current="page"', "")
    if nav_current:
        head = head.replace(f'<a href="{nav_current}">', f'<a href="{nav_current}" aria-current="page">', 1)
    foot = foot.replace("</body>", foot_extra + "\n  </body>", 1)
    return add_reviewed(head + '<main id="main">\n' + body + "\n    </main>" + foot)


def write(url, page):
    p = ROOT / url.strip("/") / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(page, encoding="utf-8")
    print("wrote", p.relative_to(ROOT))


def set_stat(key, value):
    """Record a count in data/stats.json (the single source check-numbers.py reads)."""
    p = ROOT / "data" / "stats.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    s.setdefault("catalogue", {})[key] = value
    p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
