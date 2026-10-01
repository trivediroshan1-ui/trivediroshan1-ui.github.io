#!/usr/bin/env python3
"""Builds assets/chatbot-index.json from the site's own pages and published posts.
The chatbot searches this file in the visitor's browser. Nothing is sent anywhere.
Run from the repo root:  python3 scripts/build-chat-index.py
"""
import glob, json, os, re, sys
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SKIP_TAGS = {"script", "style", "svg", "nav", "footer", "header", "noscript", "template", "form", "button", "select", "input", "video", "canvas"}
SKIP_CLASS = re.compile(r"(^|\s)(sc-|nhi-announce|skip|pager|rt-toc|hero-toc|filters|chip|cs-art|cs-more|path-card|stats|standards|themes)")
BLOCKS = {"p", "li", "tr", "figcaption", "blockquote", "dt", "dd"}
HEADS = {"h1", "h2", "h3", "h4"}

pages = [p for p in ["index.html", "about/index.html", "ai/index.html", "now/index.html", "resume/index.html",
                     "secure-india-exams/index.html", "tools/tier-check/index.html"]]
pages += sorted(glob.glob("case-studies/*/index.html"))

def url_of(path):
    return "/" if path == "index.html" else "/" + path[: -len("index.html")]

def clean(t):
    return re.sub(r"\s+", " ", t).strip()

def page_title(s):
    t = clean(s.title.get_text()) if s.title else ""
    return re.sub(r"\s*[·|\-–—]\s*Roshan Trivedi.*$", "", t)

def skipped(el):
    for p in [el] + list(el.parents):
        if getattr(p, "name", None) in SKIP_TAGS:
            return True
        cls = " ".join(p.get("class", [])) if hasattr(p, "get") else ""
        if cls and SKIP_CLASS.search(cls):
            return True
        if hasattr(p, "get") and (p.get("aria-hidden") == "true" or p.has_attr("hidden")):
            return True
    return False

def sentences(text):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])", text)

def split_passages(text, limit=105):
    out, cur, n = [], [], 0
    for sent in sentences(text):
        w = len(sent.split())
        if cur and n + w > limit:
            out.append(" ".join(cur)); cur, n = [], 0
        cur.append(sent); n += w
    if cur:
        out.append(" ".join(cur))
    return out

def extract(html, url):
    s = BeautifulSoup(html, "lxml")
    title = page_title(s)
    root = s.find("main") or s.body
    sections = []  # (heading, anchor, [texts])
    cur = [title, "", []]
    sections.append(cur)
    for el in root.find_all(list(HEADS | BLOCKS)):
        if skipped(el):
            continue
        if el.name in HEADS:
            h = clean(el.get_text(" "))
            if not h:
                continue
            anchor = el.get("id") or ""
            if not anchor:
                for p in el.parents:
                    if getattr(p, "get", None) and p.get("id") and p.name in ("section", "article", "div"):
                        anchor = p["id"]; break
            cur = [h, anchor, []]
            sections.append(cur)
        else:
            # skip block elements nested inside another collected block (avoid duplicates)
            if el.name == "p" and el.find_parent(["li", "td", "th", "blockquote", "dd"]) is not None:
                continue
            if el.name == "li" and el.find("li"):
                continue
            if el.name == "tr":
                cells = [clean(c.get_text(" ")) for c in el.find_all(["th", "td"])]
                t = " \u2014 ".join(c for c in cells if c)
            else:
                t = clean(el.get_text(" "))
            if len(t) >= 25:
                cur[2].append(t)
    recs = []
    for h, a, texts in sections:
        seen, joined = set(), []
        for t in texts:
            if t in seen:
                continue
            seen.add(t); joined.append(t)
        body = " ".join(joined)
        if len(body.split()) < 12:
            continue
        for chunk in split_passages(body):
            if len(chunk.split()) < 10:
                continue
            recs.append({"u": url, "a": a, "t": title, "h": h, "x": chunk})
    return recs

recs = []
for p in pages:
    if os.path.exists(p):
        recs += extract(open(p, encoding="utf-8").read(), url_of(p))

# Published posts (markdown). Hidden drafts live in _drafts and are never read.
for p in sorted(glob.glob("_posts/*.md")):
    raw = open(p, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        continue
    fm, body = m.groups()
    title = (re.search(r'^title:\s*"?(.*?)"?\s*$', fm, re.M) or [None, ""])[1]
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.basename(p)[:-3])
    url = "/writing/%s/" % slug
    body = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", "", body)
    sec_h, sec_txt, secs = title, [], []
    for line in body.splitlines():
        hm = re.match(r"^#{1,4}\s+(.*)", line)
        if hm:
            secs.append((sec_h, " ".join(sec_txt))); sec_h, sec_txt = hm.group(1).strip(), []
        elif line.strip() and not line.strip().startswith(("<", "|---", "```")):
            line = re.sub(r"[*_`>]|\[([^\]]*)\]\([^)]*\)", lambda mm: mm.group(1) or "", line)
            sec_txt.append(clean(line))
    secs.append((sec_h, " ".join(sec_txt)))
    for h, txt in secs:
        if len(txt.split()) < 12:
            continue
        for chunk in split_passages(txt):
            if len(chunk.split()) >= 10:
                recs.append({"u": url, "a": "", "t": title, "h": h, "x": chunk})

out = "assets/chatbot-index.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(recs, f, ensure_ascii=False, separators=(",", ":"))
print("passages:", len(recs), "bytes:", os.path.getsize(out))
