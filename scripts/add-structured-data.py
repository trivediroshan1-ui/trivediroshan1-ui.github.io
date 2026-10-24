#!/usr/bin/env python3
"""Adds schema.org structured data that the audit found missing (October 2026), and removes the
obsolete <meta name="keywords"> tag. Safe to re-run: it rewrites one block marked id="ld-site" per page.

  * every page: BreadcrumbList (Home > section > page)
  * home: Person (expanded) + WebSite
  * /book/: Book          * /labs/: CollectionPage + SoftwareSourceCode (HumanGate)
  * /resume/: ProfilePage  * /tools/tier-check/: WebApplication
  * MCP lab pages, /ai/, /now/, /design-system/: WebPage with author

Run from anywhere:  python3 scripts/add-structured-data.py
"""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://roshantrivedi.co.in"
PERSON_ID = SITE + "/#person"
AUTHOR = {"@id": PERSON_ID}

CREDS = [  # current credentials only; lapsed ones stay on the résumé page, not in structured data
    ("SailPoint Identity Security Leader Credential", "SailPoint", "https://api.badgr.io/public/assertions/H46D7mXzQ7edGUcrimvcXg"),
    ("CyberArk Certified Delivery Engineer - CPC", "CyberArk", "https://www.credly.com/badges/1e903be6-002b-48c5-9cc4-e5c262cb8bd7/public_url"),
    ("CyberArk Certified Delivery Engineer - PAM", "CyberArk", None),
    ("CyberArk Defender - Endpoint Privilege Manager", "CyberArk", "https://www.credly.com/badges/7dbad883-a2a5-40f9-9d82-4e3020097527/public_url"),
    ("CyberArk Sentry PAM", "CyberArk", "https://www.credly.com/badges/dfad80fe-b79e-4265-aac8-2941b2819d06/public_url"),
    ("CyberArk Defender PAM", "CyberArk", "https://www.credly.com/badges/515ffd75-1db0-4571-b725-6f2fdf693601/public_url"),
]

PERSON = {
    "@type": "Person", "@id": PERSON_ID, "name": "Roshan Trivedi", "url": SITE + "/",
    "image": SITE + "/assets/roshan-trivedi-520.webp",
    "jobTitle": "Credential Management Platform Owner",
    "description": "Identity security product leader working on privileged access, Zero Standing Privilege, non-human identity and human approval for AI agents.",
    "address": {"@type": "PostalAddress", "addressLocality": "Bengaluru", "addressCountry": "IN"},
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Asansol Engineering College"},
    "knowsLanguage": ["en", "hi"],
    "sameAs": ["https://www.linkedin.com/in/roshan-trivedi-ciam-49413a54/", "https://github.com/trivediroshan1-ui"],
    "knowsAbout": ["Identity and Access Management", "Privileged Access Management", "Credential Management",
                   "Zero Standing Privilege", "Non-Human Identity", "IAM Audit and Control Mapping",
                   "Model Context Protocol", "Agentic AI"],
    "hasCredential": [dict({"@type": "EducationalOccupationalCredential", "name": n, "credentialCategory": "certification",
                            "recognizedBy": {"@type": "Organization", "name": o}}, **({"url": u} if u else {})) for n, o, u in CREDS],
}

SECTIONS = {"case-studies": ("Work", "/case-studies/"), "writing": ("Writing", "/writing/"), "tools": ("Labs", "/labs/"),
            "mcp-lab-case-study": ("Labs", "/labs/"), "mcp-lab-in-depth": ("Labs", "/labs/"), "mcp-lab-results": ("Labs", "/labs/"),
            "mcp-lab-use-cases": ("Labs", "/labs/"), "mcp-lab-portal": ("Labs", "/labs/"), "secure-india-exams": ("Labs", "/labs/"),
            "book": ("Labs", "/labs/")}

def meta(h, key):
    m = re.search(r'<meta\s+(?:name|property)="' + re.escape(key) + r'"\s+content="([^"]*)"', h)
    return html.unescape(m.group(1)).strip() if m else ""

def title_of(h):
    t = meta(h, "og:title") or re.sub(r"\s+", " ", html.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))).strip()
    return re.sub(r"\s*[·|]\s*(Roshan Trivedi|RT)\s*$", "", t)

def crumbs(url, name):
    parts = [l for l in url.strip("/").split("/") if l]
    items = [("Home", "/")]
    if parts:
        sec = SECTIONS.get(parts[0])
        if sec and sec[1] != url:
            items.append(sec)
        if url not in [i[1] for i in items]:
            items.append((name, url))
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

def graph_for(rel, h):
    url = "/" + rel[: -len("index.html")]
    name = title_of(h); desc = meta(h, "description")
    g = []
    if rel == "index.html":
        g += [PERSON, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Roshan Trivedi",
                       "description": desc, "inLanguage": "en", "publisher": AUTHOR}]
        return g
    g.append(crumbs(url, name))
    if rel == "book/index.html":
        g.append({"@type": "Book", "name": "Who Approved That?", "author": AUTHOR, "url": SITE + "/book/", "inLanguage": "en",
                  "numberOfPages": 138, "bookFormat": "https://schema.org/EBook", "isAccessibleForFree": True,
                  "datePublished": "2026-10", "image": SITE + "/assets/who-approved-that-cover-640.webp",
                  "description": desc, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR", "availability": "https://schema.org/InStock", "url": SITE + "/assets/who-approved-that-book.pdf"}})
    elif rel == "labs/index.html":
        g.append({"@type": "CollectionPage", "name": name, "url": SITE + url, "description": desc, "author": AUTHOR})
        g.append({"@type": "SoftwareSourceCode", "name": "HumanGate: MCP human approval gateway", "author": AUTHOR,
                  "codeRepository": "https://github.com/trivediroshan1-ui/mcp-human-approval-gateway",
                  "programmingLanguage": "JavaScript", "license": "https://opensource.org/licenses/MIT",
                  "description": "Privacy-safe research prototype for deterministic policy and human approval of AI-agent tool actions."})
    elif rel == "resume/index.html":
        g.append({"@type": "ProfilePage", "name": name, "url": SITE + url, "mainEntity": PERSON})
    elif rel == "tools/tier-check/index.html":
        g.append({"@type": "WebApplication", "name": name, "url": SITE + url, "description": desc, "applicationCategory": "SecurityApplication",
                  "operatingSystem": "Any (runs in the browser)", "isAccessibleForFree": True, "author": AUTHOR})
    elif not re.search(r'"@type"\s*:\s*"(Article|BlogPosting|CollectionPage|ProfilePage|TechArticle)"', h):
        g.append({"@type": "WebPage", "name": name, "url": SITE + url, "description": desc, "author": AUTHOR, "inLanguage": "en"})
    return g

n = 0
for p in sorted(ROOT.rglob("index.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("worker/", ".git/", "_site/", "assets/")):
        continue
    h = p.read_text(encoding="utf-8"); o = h
    h = re.sub(r'\s*<meta\s+name="keywords"\s+content="[^"]*"\s*/?>', "", h, flags=re.S)
    h = re.sub(r'\s*<script type="application/ld\+json" id="ld-site">.*?</script>', "", h, flags=re.S)
    if rel == "index.html":  # the home page's old Person block is replaced by the richer graph
        h = re.sub(r'\s*<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "Person".*?</script>', "", h, count=1, flags=re.S)
    g = graph_for(rel, h)
    block = '<script type="application/ld+json" id="ld-site">' + json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False) + "</script>"
    h = h.replace("</head>", "    " + block + "\n  </head>", 1)
    if h != o:
        p.write_text(h, encoding="utf-8"); n += 1
# 404 and the post layout lose the keywords tag too
for extra in ["404.html", "_layouts/post.html"]:
    f = ROOT / extra
    t = f.read_text(encoding="utf-8"); t2 = re.sub(r'\s*<meta\s+name="keywords"\s+content="[^"]*"\s*/?>', "", t, flags=re.S)
    if t2 != t: f.write_text(t2, encoding="utf-8")
print("pages with structured data updated:", n)
