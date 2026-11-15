#!/usr/bin/env python3
"""The sign-in lab book ("Who signs in?") as web chapters: /ca-mfa-lab/book/ and one page per chapter.

Runs scripts/ca/build_ca_book.py up to the point where it would make the PDF, reading the lab data
from this repository, then turns the same content into HTML. The PDF is not rebuilt.
  the access chain picture -> the seven links as a list, with their questions and case counts
  each case's output grid  -> a small table: output against my guess, wrong guesses marked
Run from the repo root after changing the book:  python3 scripts/build-ca-chapters.py
"""
import html, pathlib, re, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from page_shell import shell, write, ROOT
import web_book as WB

R = str(ROOT)
ns = WB.load_story(HERE / "ca" / "build_ca_book.py", "doc = CABook(OUT)", replace=[
    ('sys.path.insert(0, "/home/claude/work/site/scripts"); sys.path.insert(0, "/home/claude/work/fw")',
     f'sys.path.insert(0, "{R}/scripts"); sys.path.insert(0, "{R}/scripts/ca")'),
    ('"/home/claude/work/out/ca-mfa-lab/data/cases.js"', f'"{R}/ca-mfa-lab/data/cases.js"'),
    ('"/home/claude/work/book/sources.json"', f'"{R}/scripts/ca/sources.json"'),
    ('"/home/claude/ca-mfa-lab/evidence/', f'"{R}/ca-mfa-lab/evidence/'),
])
story, EDITION, STAGES = ns["story"], ns["EDITION"], ns["STAGES"]


def chain(fl, w):
    w.emit('<ol class="wb-steps">' + "".join(
        f'<li><b>{html.escape(s["name"])}</b> {html.escape(s["q"])} <i>{len(s["ids"])} cases.</i></li>' for s in STAGES) + "</ol>")


def grid(fl, w):
    cs, word = fl.c, {"in": "happens", "out": "stopped"}
    head = "".join(f'<th scope="col">{html.escape(h)}</th>' for h in cs["cols"])
    out = "".join(f"<td>{word.get(v, 'not tested')}</td>" for v in cs["res"])
    gs = []
    for i, v in enumerate(cs["guess"]):
        wrong = v in ("in", "out") and cs["res"][i] not in ("-", v)
        gs.append(f'<td class="wb-wrong">{word.get(v, "not tested")} <b>(wrong)</b></td>' if wrong else f"<td>{word.get(v, 'not tested')}</td>")
    w.emit('<div class="wb-tw"><table class="wb-grid"><thead><tr><td></td>' + head + "</tr></thead><tbody>"
           f'<tr><th scope="row">Output</th>{out}</tr><tr><th scope="row">My guess</th>{"".join(gs)}</tr></tbody></table></div>')


chapters = WB.Walker({"ChainDiagram": chain, "CaseGrid": grid}).run(story)
# case headings get an anchor and a link to the same row in the register
for c in chapters:
    c["html"] = [re.sub(r'^<h3 class="wb-case">([A-Z]{1,3}\d{2})\b',
                        lambda m: f'<h3 class="wb-case" id="{m.group(1).lower()}"><a href="/ca-mfa-lab/register/#{m.group(1)}">{m.group(1)}</a>', h)
                 for h in c["html"]]

BOOK = "/ca-mfa-lab/book/"
WB.write_book(chapters, book=BOOK, pdf="/ca-mfa-lab/ca-mfa-lab-book.pdf", title="Who signs in?",
              desc="The conditional access, MFA and AI agent lab book, chapter by chapter on the web: 130 cases along the access chain, the six wrong guesses and the hand tests.",
              lede=f"The whole book as web pages, one chapter per page: easier to read on a phone, to search and to use with a screen reader than the PDF. Edition 1, {EDITION}. The words are the same as in the PDF; each case links to its row in the register.",
              ey="Conditional access, MFA and AI agent lab · the book", short="sign-in lab book",
              crumb=[("Home", "/"), ("Labs and projects", "/labs/"), ("Conditional access, MFA and AI agent lab", "/ca-mfa-lab/")],
              shell=shell, write=write, head='    <link rel="stylesheet" href="/assets/web-book.css?v=20261116a">', root_dir=ROOT / "ca-mfa-lab" / "book")
print("chapters:", len(chapters))
