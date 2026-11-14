#!/usr/bin/env python3
"""Build /ai-governance-lab/errata/ and assets/ai-governance-lab-errata.pdf from one set of facts.

The numbers come from the site's own correction at /ai-governance-lab/what-i-got-wrong/#recount.
The PDFs themselves are not changed, so their checksums do not move.

Usage: python3 scripts/build_agl_errata.py [--pdf]   (--pdf also renders the one-page PDF with Chromium)
"""
import html, pathlib, re, sys, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHELL = ROOT / "ai-governance-lab" / "what-i-got-wrong" / "index.html"
OUT = ROOT / "ai-governance-lab" / "errata" / "index.html"
PDF = ROOT / "assets" / "ai-governance-lab-errata.pdf"
URL = "https://roshantrivedi.co.in/ai-governance-lab/errata/"
REVIEWED = "15 November 2026"

TITLE = "Errata for the AI governance book and addendum"
DEK = ("Three rounds changed after the PDFs were made. This page says which numbers to read instead, "
       "page by page.")

SHORT = [
    "On 25 October 2026 I re-counted rounds 6 to 12 with the stricter rule from round 13. Rounds 6, 7 and 9 dropped. "
    "The book, the addendum and the round videos were made before that, so they still show the older numbers.",
    "The PDFs have not changed, so the checksums on the Book page still match the files. This page is the fix.",
    "Nothing else moved. Every &ldquo;as guessed&rdquo; result, every guess hash and rounds 8, 10, 11, 12 and 13 are as printed. "
    "The round five PDF is not affected, because round five has no control-off checks.",
]

ROUNDS = [
    ("6", "12 of 12", "11 of 12", "T5: the agent&rsquo;s own sponsor may approve"),
    ("7", "14 of 14", "12 of 14", "H4: the same person may give both approvals. H8: the signed policy is not required"),
    ("9", "12 of 12 (addendum page 46 says 14 of 15)", "13 of 15",
     "Q5, twice: the gateway check for unknown actions is switched off. The 15 includes three stronger checks added later"),
]

WHY = [
    "The stricter rule says a case notices a missing control only if it passes normally and then gives a different result that is not an error. "
    "In these three rounds the case crashed with the control off. A crash shows the code broke. It does not show the check caught the problem.",
    "Q5 is a different case. With the gateway check off, the executor still refuses the request, so nothing changes. That is a second layer doing its job, "
    "and it means Q5 cannot show the gateway check matters on its own.",
]

PAGES = [
    ("Addendum", "2", "Round 6: &ldquo;12 of 12 control-off checks noticed&rdquo;", "11 of 12. T5 did not."),
    ("Addendum", "2", "Round 7: &ldquo;14 of 14 after I fixed a weak test&rdquo;", "12 of 14. H4 and H8 did not."),
    ("Addendum", "2", "Round 9: &ldquo;12 of 12 control-off checks noticed&rdquo;", "13 of 15. Q5 did not, twice."),
    ("Addendum", "17", "Round 6: &ldquo;12 of 12 controls switched off were noticed&rdquo;", "11 of 12. T5 did not."),
    ("Addendum", "26", "Round 7: &ldquo;I rebuilt it and 14 of 14 were noticed&rdquo;", "12 of 14 under the strict rule. H4 and H8 crashed."),
    ("Addendum", "40", "Round 9: &ldquo;12 of 12 controls switched off were noticed&rdquo;", "13 of 15 (see page 46). Q5 crashed."),
    ("Addendum", "46", "Round 9: &ldquo;14 of 15 noticed&rdquo;", "13 of 15."),
    ("Book", "61", "Chapter 15 table, printed page 60: round 6 &ldquo;12 of 12&rdquo;, round 7 &ldquo;14 of 14&rdquo;, round 9 &ldquo;12 of 12&rdquo;",
     "11 of 12, 12 of 14 and 13 of 15."),
]

VIDEOS = ("The round videos were also made before the re-count and show the older numbers. "
          "The Mac record shows what the Mac printed at the time and is not edited.")


TH = '<th style="letter-spacing:0;text-transform:none;overflow-wrap:normal">'


def th(t):
    return f"{TH}{t}</th>"


def rounds_table():
    rows = "".join(f"<tr><td>{r}</td><td>{p}</td><td><strong>{n}</strong></td><td>{w}</td></tr>" for r, p, n, w in ROUNDS)
    return ('<div class="table-wrap" style="overflow-x:auto"><table style="table-layout:fixed;width:100%;min-width:0;overflow-wrap:anywhere">'
            '<colgroup><col style="width:15%"><col style="width:29%"><col style="width:18%"><col style="width:38%"></colgroup>'
            "<thead><tr>" + th("Round") + th("Printed") + th("Read") + th("Not noticed") + "</tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")


def pages_table():
    rows = "".join(f"<tr><td>{d}</td><td>{p}</td><td>{a}</td><td>{b}</td></tr>" for d, p, a, b in PAGES)
    return ('<div class="table-wrap" style="overflow-x:auto"><table style="table-layout:fixed;width:100%;min-width:0;overflow-wrap:anywhere">'
            '<colgroup><col style="width:28%"><col style="width:12%"><col style="width:32%"><col style="width:28%"></colgroup>'
            "<thead><tr>" + th("PDF") + th("Page") + th("It says") + th("Read") + "</tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")


def body(pdf_sha):
    lis = "\n".join(f"          <li>{t}</li>" for t in SHORT)
    why = "\n".join(f'        <p class="body-text">{t}</p>' for t in WHY)
    dl = ""
    if pdf_sha:
        dl = (f'\n      <section aria-labelledby="print">\n        <h2 id="print">Keep a copy with your PDF</h2>\n'
              f'        <p class="body-text">The same corrections on one page, to print or save next to the book: '
              f'<a href="/assets/ai-governance-lab-errata.pdf">Errata (PDF, 1 page)</a>.</p>\n'
              f'        <p class="body-text" style="font-size:.9em">SHA-256 so you can check your copy: '
              f'<code style="word-break:break-all;font-size:1.08em">{pdf_sha}</code></p>\n      </section>')
    return f'''      <section aria-labelledby="short">
        <h2 id="short">The short version</h2>
        <ul class="body-text">
{lis}
        </ul>
      </section>
      <section aria-labelledby="read">
        <h2 id="read">What to read instead</h2>
        {rounds_table()}
{why}
        <p class="body-text">The full account, with the pull request and the dates, is in <a href="/ai-governance-lab/what-i-got-wrong/#recount">What I got wrong</a>.</p>
      </section>
      <section aria-labelledby="pages">
        <h2 id="pages">Page by page</h2>
        <p class="body-text">Page numbers are the PDF page numbers. Everything not listed here is as printed.</p>
        {pages_table()}
        <p class="body-text">{VIDEOS}</p>
        <p class="body-text"><small>All data is made up. Nothing here relates to any employer or real company.</small></p>
      </section>{dl}
'''


def build_page(pdf_sha):
    s = SHELL.read_text(encoding="utf-8")
    desc = ("Which numbers to read instead in the AI governance book and addendum: rounds 6, 7 and 9 were re-counted on 25 Oct 2026. "
            "Page by page.")
    s = re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{desc}" />', s, 1)
    s = s.replace("https://roshantrivedi.co.in/ai-governance-lab/what-i-got-wrong/", URL)
    s = re.sub(r'<meta property="og:title" content="[^"]*" />', f'<meta property="og:title" content="{TITLE}" />', s, 1)
    s = re.sub(r'<meta property="og:description" content="[^"]*" />', f'<meta property="og:description" content="{desc}" />', s, 1)
    s = re.sub(r"<title>[^<]*</title>", "<title>Errata · AI governance lab · Roshan Trivedi</title>", s, 1)
    s = re.sub(r'<h1>[^<]*</h1>', f"<h1>{TITLE}</h1>", s, 1)
    s = re.sub(r'<p class="dek">.*?</p><p class="lastrev">[^<]*</p>',
               f'<p class="dek">{DEK}</p><p class="lastrev">Last reviewed {REVIEWED}</p>', s, 1, flags=re.S)
    a = s.index('<div class="agl story">') + len('<div class="agl story">')
    b = s.index("      </div>\n    <nav class=\"lab-foot\"")
    s = s[:a] + "\n" + body(pdf_sha) + s[b:]
    s = re.sub(r'<nav class="lab-foot".*?</nav>',
               '<nav class="lab-foot" aria-label="More in this lab"><a class="lf-prev" href="/ai-governance-lab/what-i-got-wrong/"><small>Previous</small><b>What I got wrong</b></a>'
               '<a class="lf-next" href="/ai-governance-lab/story/"><small>Next</small><b>The story</b></a>'
               '<span class="lf-extra"><a href="/assets/ai-governance-lab-book.pdf">Get the book</a><a href="/topics/">Browse by topic</a></span></nav>',
               s, 1, flags=re.S)
    s = re.sub(r'"headline":"[^"]*","datePublished":"[^"]*","dateModified":"[^"]*"',
               f'"headline":"{TITLE}","datePublished":"2026-11-15","dateModified":"2026-11-15"', s, 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(s, encoding="utf-8")


def pdf_html():
    rt = re.sub(r'<colgroup>.*?</colgroup>', '', rounds_table().replace(' style="overflow-x:auto"', ""))
    rt = rt.replace(' style="table-layout:fixed;width:100%;min-width:0;overflow-wrap:anywhere"', "")
    pt = re.sub(r'<colgroup>.*?</colgroup>', '', pages_table().replace(' style="overflow-x:auto"', ""))
    pt = pt.replace(' style="table-layout:fixed;width:100%;min-width:0;overflow-wrap:anywhere"', "")
    short = "".join(f"<li>{t}</li>" for t in SHORT)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{TITLE}</title>
<style>
@page{{size:A4;margin:16mm 15mm}}
body{{font:9.6pt/1.4 Georgia,'Times New Roman',serif;color:#111}}
h1{{font:700 17pt/1.2 Helvetica,Arial,sans-serif;margin:0 0 3pt}}
h2{{font:700 10.5pt/1.2 Helvetica,Arial,sans-serif;margin:11pt 0 3pt}}
.k{{font:700 8pt Helvetica,Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#555}}
p{{margin:3pt 0}} ul{{margin:3pt 0 3pt 14pt;padding:0}} li{{margin:2pt 0}}
table{{border-collapse:collapse;width:100%;font:8.6pt/1.3 Helvetica,Arial,sans-serif;margin:4pt 0}}
th,td{{border:1px solid #bbb;padding:3pt 5pt;vertical-align:top;text-align:left}} th{{background:#eee}}
.f{{margin-top:10pt;font:8pt Helvetica,Arial,sans-serif;color:#444;border-top:1px solid #bbb;padding-top:4pt}}
</style></head><body>
<div class="k">AI governance lab &middot; Errata</div><h1>{TITLE}</h1>
<p>{DEK} Last reviewed {REVIEWED}.</p>
<h2>The short version</h2><ul>{short}</ul>
<h2>What to read instead</h2>{rt}{"".join(f"<p>{t}</p>" for t in WHY)}
<h2>Page by page</h2><p>Page numbers are the PDF page numbers. Everything not listed is as printed.</p>{pt}<p>{VIDEOS}</p>
<div class="f">Roshan Trivedi &middot; {URL} &middot; CC BY 4.0 &middot; All data is made up.</div>
</body></html>'''


def render_pdf():
    from playwright.sync_api import sync_playwright
    import pypdf
    tmp = pathlib.Path("/tmp/agl-errata.html")
    tmp.write_text(pdf_html(), encoding="utf-8")
    raw = pathlib.Path("/tmp/agl-errata-raw.pdf")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto(f"file://{tmp}")
        pg.pdf(path=str(raw), format="A4", print_background=True, prefer_css_page_size=True); b.close()
    r = pypdf.PdfReader(str(raw))
    assert len(r.pages) == 1, f"errata PDF is {len(r.pages)} pages, expected 1"
    w = pypdf.PdfWriter(clone_from=r)
    w.add_metadata({"/Title": TITLE, "/Author": "Roshan Trivedi",
                    "/Subject": "Corrections to the control-off numbers for rounds 6, 7 and 9",
                    "/Keywords": "AI governance, errata, control-off checks, made-up data"})
    w.write(str(PDF))


if __name__ == "__main__":
    if "--pdf" in sys.argv:
        render_pdf()
    sha = hashlib.sha256(PDF.read_bytes()).hexdigest() if PDF.exists() else None
    build_page(sha)
    print("page written;", "pdf sha " + sha if sha else "no pdf yet")
