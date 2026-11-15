#!/usr/bin/env python3
"""The library (STR-01): every page as one record in data/library.json, and /library/ built from it.

Each record: url, title, summary, type, collection, published (articles), reviewed, updated.
- Title, summary and kind come from the command palette's list (assets/palette-data.js).
- 'updated' is the sitemap's lastmod; 'reviewed' is the page's own "Last reviewed" line, if it has one.
- The collection comes from the address first (each lab belongs to one), then from the words
  in the title and summary, using the keyword lists below. It is a finding aid: check it when
  adding a page, and set an override in OVERRIDE if a page lands in the wrong place.
Run after build-palette.py and build-sitemap.py:  python3 scripts/build-library.py
"""
import html, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from page_shell import shell, write, set_stat, ROOT

COLLECTIONS = [
    ("pam", "Privileged access and credentials", "Vaults, admin accounts, break-glass, just-in-time access and the programmes around them."),
    ("nhi", "Machine identity", "Service accounts, API keys, tokens and secrets: finding them, owning them and retiring them."),
    ("signin", "Sign-in and MFA", "Single sign-on, MFA, passkeys, conditional access and account recovery."),
    ("ai", "AI agents and governance", "AI agents acting with real access, approvals for tool calls, and governing AI use."),
    ("site", "About me and finding your way", "Who I am, how I work, and the pages that help you find things."),
]
PREFIX = [("/ca-mfa-lab/", "signin"), ("/nhi-lab/", "nhi"), ("/ai-governance-lab/", "ai"), ("/mcp-lab/", "ai"),
          ("/mcp-human-approval-gateway/", "ai"), ("/writing/pam-", "pam"), ("/tools/tier-check/", "pam")]
SITE_PAGES = {"/", "/about/", "/resume/", "/ai/", "/talk/", "/speaking/", "/now/", "/writing/", "/case-studies/", "/book/",
              "/labs/", "/labs/cases/", "/design-system/", "/start/", "/topics/", "/glossary/", "/privacy/", "/method/",
              "/contact/", "/copyright/", "/search/", "/library/"}
OVERRIDE = {"/secure-india-exams/": "pam", "/case-studies/credential-tiering-model/": "pam", "/case-studies/platform-evaluation/": "pam",
            "/case-studies/ai-coworker/": "ai", "/case-studies/ai-processing-tax/": "ai", "/case-studies/shadow-ai-discovery-gap/": "ai",
            "/case-studies/non-human-identity-at-scale/": "nhi", "/writing/130-conditional-access-mfa-and-ai-agent-cases/": "signin"}
WORDS = {  # checked in this order; the first collection with a match wins
    "ai": ["ai agent", "agentic", "mcp", "shadow ai", "ai governance", "llm", "ai co", "ai processing", "openai", "hugging"],
    "nhi": ["non-human", "machine identit", "service account", "secret", "api key", "workload", "ciem", "token"],
    "signin": ["mfa", "passwordless", "passkey", "conditional access", "sign-in", "sso", "authentication"],
    "pam": ["privileg", "pam", "vault", "break-glass", "credential", "jit", "recertif", "audit", "vendor", "migration", "platform"],
}
TYPES = [("/labs/cases/", "Catalogue"), ("/case-studies/", "Case study"), ("/writing/", "Article"), ("/book/", "Books"),
         ("/tools/", "Tool"), ("/nhi-lab/book/", "Books"), ("/ca-mfa-lab/", "Lab"), ("/nhi-lab/", "Lab"), ("/ai-governance-lab/", "Lab"), ("/mcp-lab/", "Lab"),
         ("/mcp-human-approval-gateway/", "Lab"), ("/secure-india-exams/", "Research")]

pal = (ROOT / "assets/palette-data.js").read_text(encoding="utf-8")
items = json.loads(pal[pal.index("["):pal.rstrip().rstrip(";").rindex("]") + 1])
meta = {}
for it in items:
    u = it["u"].split("#")[0]
    if u.endswith("/") and u not in meta:
        meta[u] = it
sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
lastmod = {re.sub(r"^https://roshantrivedi\.co\.in", "", a): b for a, b in re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", sm)}
posts = {}
for f in (ROOT / "_posts").glob("*.md"):
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", f.stem)
    if m:
        posts["/writing/" + m.group(2) + "/"] = m.group(1)


def own_meta(u):
    p = ROOT / u.strip("/") / "index.html"
    if not p.exists():
        return {}
    h = p.read_text(encoding="utf-8")
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    r = re.search(r"Last reviewed (\d{1,2} [A-Z][a-z]+ 20\d\d)", h)
    return {"t": html.unescape(re.sub(r"\s*[·|]\s*Roshan Trivedi.*$", "", t.group(1))).strip() if t else "",
            "d": html.unescape(d.group(1)) if d else "", "r": r.group(1) if r else ""}


def collection(u, text):
    if u in OVERRIDE:
        return OVERRIDE[u]
    if u in SITE_PAGES:
        return "site"
    for pre, c in PREFIX:
        if u.startswith(pre):
            return c
    t = text.lower()
    for c, ws in WORDS.items():
        if any(w in t for w in ws):
            return c
    return "pam"


def kind(u):
    if u in SITE_PAGES:
        return "Page"
    for pre, k in TYPES:
        if u.startswith(pre):
            return k
    return "Page"


recs = []
for u, mod in lastmod.items():
    if not u.endswith("/"):
        continue  # files such as the CA book PDF are reached from their lab
    o, p = own_meta(u), meta.get(u, {})
    title = p.get("t") or o.get("t") or u
    summary = p.get("d") or o.get("d") or ""
    rec = {"url": u, "title": title, "summary": summary, "type": kind(u),
           "collection": collection(u, title + " " + summary + " " + u), "updated": mod}
    if o.get("r"):
        rec["reviewed"] = o["r"]
    if u in posts:
        rec["published"] = posts[u]
    recs.append(rec)
for extra in ("/labs/cases/", "/search/", "/library/"):
    if extra not in lastmod:
        o = own_meta(extra)
        recs.append({"url": extra, "title": o.get("t") or extra, "summary": o.get("d", ""), "type": kind(extra),
                     "collection": "site", "updated": "2026-11-15"})
recs.sort(key=lambda r: r["url"])
out = {"about": "Every page on roshantrivedi.co.in with its type, collection and dates. Generated by scripts/build-library.py.",
       "collections": [{"id": c, "name": n, "about": a} for c, n, a in COLLECTIONS], "pages": recs}
(ROOT / "data/library.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
set_stat("library_pages", len(recs))
print("library:", len(recs), {c: sum(1 for r in recs if r["collection"] == c) for c, _, _ in COLLECTIONS})

# The page
esc = html.escape
ORDER = ["Lab", "Catalogue", "Case study", "Article", "Books", "Research", "Tool", "Page"]
LABEL = {"Lab": "Labs", "Catalogue": "Catalogue", "Case study": "Case studies", "Article": "Articles", "Books": "Books",
         "Research": "Research", "Tool": "Tools", "Page": "Pages"}
secs = []
for cid, name, about in COLLECTIONS:
    mine = [r for r in recs if r["collection"] == cid]
    groups = []
    for k in ORDER:
        rs = sorted([r for r in mine if r["type"] == k], key=lambda r: (r["url"].count("/"), r["title"].lower()))
        if not rs:
            continue
        li = "".join(f'<li><a href="{r["url"]}">{esc(r["title"])}</a>' + (f'<span>{esc(r["summary"])}</span>' if r["summary"] else "") + "</li>" for r in rs)
        groups.append(f'<h3>{LABEL[k]} <small>{len(rs)}</small></h3><ul class="lib-l">{li}</ul>')
    secs.append(f'<section class="lib-c" id="{cid}" aria-labelledby="h-{cid}"><h2 id="h-{cid}">{esc(name)} <small>{len(mine)} entries</small></h2>'
                f'<p>{esc(about)}</p>{"".join(groups)}</section>')
toc = "".join(f'<li><a href="#{c}">{esc(n)}</a></li>' for c, n, _ in COLLECTIONS)
body = f'''      <section class="sec cat lib" aria-labelledby="lib-h">
        <div class="wrap">
          <p class="ey">Library</p>
          <h1 id="lib-h">Everything on the site, by subject</h1>
          <p class="lede">{len(recs)} pages in four collections, plus the pages about me. Each collection holds its lab, case studies, articles and tools. To search the words inside the pages, use <a href="/search/">search</a>; for single lab cases, <a href="/labs/cases/">every case in one list</a>.</p>
          <nav aria-label="Collections"><ul class="lib-toc">{toc}</ul></nav>
          {"".join(secs)}
          <p class="cat-note">The same list as data: <a href="/data/library.json">library.json</a>, with each page's type, collection and dates.</p>
        </div>
      </section>'''
page = shell("/library/", "Library", "Every page on roshantrivedi.co.in by subject: privileged access, machine identity, sign-in and MFA, and AI agents.",
             body, [("Home", "/"), ("Library", "/library/")],
             head_extra='    <link rel="stylesheet" href="/assets/catalogue.css?v=20261115a">')
write("/library/", page)
