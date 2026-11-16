#!/usr/bin/env python3
"""The NHI lab book as web chapters (PUB-03): /nhi-lab/book/ and one page per chapter.

Runs scripts/build-nhi-book.py up to the point where it would make the PDF, then turns the same
content into HTML, so the web chapters and the PDF say the same thing. The PDF is not rebuilt.
  headings, paragraphs, lists, tables, callouts  -> the same, as HTML
  number tiles, step diagrams, the market timeline -> lists with the same words
  case diagrams and the results map               -> a link to the same case or table on the lab pages
Run from the repo root after changing the book:  python3 scripts/build-nhi-chapters.py
"""
import html, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from page_shell import shell, write, ROOT

import web_book as WB

ns = WB.load_story(HERE / "build-nhi-book.py", "# ------------------------------------------------------------------ build")
story, EDITION = ns["story"], ns["EDITION_DATE"]


def case_link(c):
    cid = c.get("id", "") if isinstance(c, dict) else ""
    return (f'<p class="wb-fig">Diagram for case {html.escape(cid)}: <a href="/nhi-lab/#{cid.lower()}">see it on the lab page</a>.</p>'
            if cid else "")


def step_diagram(fl, w):
    rows = getattr(fl, "rows", None) or (fl.__dict__.get("rows_") or [])
    steps = [s for row in rows for s in row]
    if steps:
        w.emit('<ol class="wb-steps">' + "".join(f"<li><b>{WB.md(s[0])}</b> {WB.md(s[1])}</li>" for s in steps) + "</ol>")


HANDLERS = {
    "StepDiagram": step_diagram,
    "Timeline": lambda fl, w: w.emit('<ul class="wb-steps">' + "".join(f"<li><b>{html.escape(dl)}</b> {html.escape(lab)}</li>" for d, dl, lab, col, lvl in fl.EV) + "</ul>"),
    "CaseDiagram": lambda fl, w: w.emit(case_link(getattr(fl, "case", None) or {})),
    "ResultsMap": lambda fl, w: w.emit('<p class="wb-fig">The map of all 67 cases is a picture in the PDF. The same results are in <a href="/nhi-lab/audit/">the audit table</a> and <a href="/labs/cases/?lab=nhi">the case list</a>.</p>'),
}
chapters = WB.Walker(HANDLERS, layout_tables=("CaseDiagram", "ResultsMap")).run(story)
BOOK = "/nhi-lab/book/"
WB.write_book(chapters, book=BOOK, pdf="/nhi-lab/nhi-lab-book.pdf", title="Machine identities, tested in public",
              desc="The machine identity lab book, chapter by chapter on the web: 67 cases, a seven-step framework, the 2026 market and what is missing.",
              lede=f"The whole book as web pages, one chapter per page: easier to read on a phone, to search and to use with a screen reader than the PDF. Edition 2, {EDITION}. The words are the same as in the PDF; diagrams link to the same case on the lab pages.",
              ey="Machine identity lab · the book", short="NHI lab book",
              crumb=[("Home", "/"), ("Labs and projects", "/labs/"), ("Machine identity lab", "/nhi-lab/")],
              shell=shell, write=write, head='    <link rel="stylesheet" href="/assets/web-book.css?v=20261116b">', root_dir=ROOT / "nhi-lab" / "book")
print("chapters:", len(chapters))
