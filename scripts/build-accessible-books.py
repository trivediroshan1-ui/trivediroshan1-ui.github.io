#!/usr/bin/env python3
"""Build a tagged, screen-reader friendly PDF of each book that has a web edition.

The designed PDFs are drawn with ReportLab, which cannot write a tag tree, so a screen reader
gets no headings, lists or table structure from them. The web editions (made by web_book.py from
the same story) carry the same text and tables as plain HTML. This script joins a book's web
chapters in reading order into one page and prints it with Chromium (tagged=True, outline=True),
which writes a tag tree and bookmarks. pdf_access.finalize then sets the language, title and
rights. The designed PDFs are not touched, so their published SHA-256 values stay valid.

  python3 scripts/build-accessible-books.py            # build both
  python3 scripts/build-accessible-books.py ca         # one book
"""
import html, pathlib, re, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://roshantrivedi.co.in"
sys.path.insert(0, str(ROOT / "scripts"))
import pdf_access

BOOKS = {
    "ca": dict(index="ca-mfa-lab/book/index.html", out="ca-mfa-lab/ca-mfa-lab-book-accessible.pdf",
               designed="/ca-mfa-lab/ca-mfa-lab-book.pdf", subject="Conditional access, MFA and AI agent lab, accessible edition",
               keywords="conditional access, MFA, SSO, AI agents, identity, test lab, made-up data, accessible, CC BY 4.0"),
    "nhi": dict(index="nhi-lab/book/index.html", out="nhi-lab/nhi-lab-book-accessible.pdf",
                designed="/nhi-lab/nhi-lab-book.pdf", subject="Machine identity lab, accessible edition",
                keywords="non-human identity, machine identity, service accounts, secrets, break-glass, test lab, made-up data, accessible, CC BY 4.0"),
}

CSS = """
@page { size: A4; margin: 22mm 20mm 24mm 20mm; }
html { font-family: "DM Sans", "Liberation Sans", Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #111; background: #fff; }
body { margin: 0; }
h1 { font-size: 24pt; line-height: 1.2; margin: 0 0 8pt; }
h2 { font-size: 17pt; line-height: 1.25; margin: 0 0 10pt; break-before: page; }
h3 { font-size: 13pt; margin: 16pt 0 6pt; break-after: avoid; }
h4 { font-size: 11.5pt; margin: 12pt 0 4pt; break-after: avoid; }
p, li { margin: 0 0 7pt; orphans: 3; widows: 3; }
a { color: #0b4f9c; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0 12pt; font-size: 9.5pt; }
th, td { border: 0.6pt solid #888; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #eee; }
tr { break-inside: avoid; }
code { font-family: "JetBrains Mono", "Liberation Mono", monospace; font-size: 9.5pt; }
.cover { min-height: 230mm; display: flex; flex-direction: column; justify-content: center; }
.cover .sub { font-size: 14pt; margin: 0 0 18pt; }
.note { border-left: 3pt solid #0b4f9c; padding: 4pt 0 4pt 10pt; }
nav.toc ol { padding-left: 18pt; }
"""


def absolute(body):
    """Make site links absolute so they work from a downloaded file."""
    return re.sub(r'href="/(?!/)', f'href="{SITE}/', body)


def chapter(path):
    h = (ROOT / path).read_text(encoding="utf-8")
    m = re.search(r'<h1 id="wb-h">(.*?)</h1>(.*?)<nav class="wb-pn"', h, re.S)
    if not m:
        raise SystemExit(f"no chapter body in {path}")
    title, body = m.group(1).strip(), m.group(2).strip()
    # The chapter title becomes h2 under the book's h1, so every heading inside moves down one level.
    for n in (5, 4, 3, 2):
        body = re.sub(rf"<(/?)h{n}\b", rf"<\1h{n + 1}", body)
    body = re.sub(r'\s(id|aria-labelledby)="[^"]*"', "", body)
    return title, absolute(body)


def build(key):
    cfg = BOOKS[key]
    idx = (ROOT / cfg["index"]).read_text(encoding="utf-8")
    book_dir = "/" + cfg["index"][: -len("index.html")]
    title = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', idx, re.S).group(1)).strip()
    title = re.sub(r"<[^>]+>", "", title)
    ey = re.search(r'<p class="ey">(.*?)</p>\s*<h1', idx, re.S)
    lede = re.sub(r"\s*·\s*the book$", "", ey.group(1).strip()) if ey else ""
    order = []
    for u in re.findall(rf'href="({re.escape(book_dir)}[^"#]+/)"', idx):
        if u not in order:
            order.append(u)
    chapters = [chapter(u.strip("/") + "/index.html") for u in order]

    toc = "".join(f"<li>{t}</li>" for t, _ in chapters)
    parts = [f"""<section class="cover"><h1>{html.escape(title)}</h1>
<p class="sub">{lede}</p>
<p>Roshan Trivedi &middot; roshantrivedi.co.in</p>
<p class="note">Accessible edition. The same text and tables as the designed PDF, laid out for screen readers:
tagged headings, lists and tables, bookmarks, and the language set. The diagrams of the designed edition are left out.
The designed edition is at <a href="{SITE}{cfg['designed']}">{SITE}{cfg['designed']}</a>, and the web edition at
<a href="{SITE}{book_dir}">{SITE}{book_dir}</a>. All data in this book is made up.</p>
<p>&copy; 2026 Roshan Trivedi. Licensed under Creative Commons Attribution 4.0.</p></section>
<nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>{toc}</ol></nav>"""]
    for t, body in chapters:
        parts.append(f"<section><h2>{t}</h2>\n{body}</section>")

    fonts = (ROOT / "assets" / "fonts.css").as_uri()
    doc = (f'<!doctype html><html lang="en-IN"><head><meta charset="utf-8"><title>{html.escape(title)}: accessible edition</title>'
           f'<link rel="stylesheet" href="{fonts}"><style>{CSS}</style></head><body>{"".join(parts)}</body></html>')
    tmp = ROOT / "assets" / f"_access_{key}.html"
    tmp.write_text(doc, encoding="utf-8")
    out = ROOT / cfg["out"]
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page()
            pg.goto(tmp.as_uri(), wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True,
                   tagged=True, outline=True, display_header_footer=True,
                   header_template="<span></span>",
                   footer_template='<div style="font-size:8pt;width:100%;text-align:center;color:#555">'
                                   '<span class="pageNumber"></span> of <span class="totalPages"></span></div>')
            b.close()
    finally:
        tmp.unlink(missing_ok=True)
    pdf_access.finalize(out, title=f"{title}: accessible edition", author="Roshan Trivedi",
                        subject=cfg["subject"], keywords=cfg["keywords"], rights=pdf_access.RIGHTS)
    print(f"{cfg['out']}: {len(chapters)} chapters")


if __name__ == "__main__":
    for k in (sys.argv[1:] or BOOKS):
        build(k)
