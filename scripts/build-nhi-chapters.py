#!/usr/bin/env python3
"""The NHI lab book as web chapters (PUB-03): /nhi-lab/book/ and one page per chapter.

Runs scripts/build-nhi-book.py up to the point where it would make the PDF, then turns the same
content into HTML, so the web chapters and the PDF say the same thing. The PDF is not rebuilt.
  headings, paragraphs, lists, tables, callouts  -> the same, as HTML
  number tiles, step diagrams, the market timeline -> lists with the same words
  case diagrams and the results map               -> a link to the same case or table on the lab pages
Run from the repo root after changing the book:  python3 scripts/build-nhi-chapters.py
"""
import html, os, pathlib, re, shutil, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from page_shell import shell, write, ROOT

src = (HERE / "build-nhi-book.py").read_text(encoding="utf-8")
src = src.split("# ------------------------------------------------------------------ build")[0]
ns = {"__file__": str(HERE / "build-nhi-book.py"), "__name__": "nhi_book_story"}
exec(compile(src, "build-nhi-book.py", "exec"), ns)
story, EDITION = ns["story"], ns["EDITION_DATE"]
from reportlab.platypus import Paragraph, Table, KeepTogether  # noqa: E402

TAG_OK = {"b", "i", "u", "br", "sup", "sub", "strong", "em"}


def md(t):
    """ReportLab paragraph markup to HTML."""
    t = str(t)
    t = re.sub(r'<link href="([^"]+)"[^>]*>', lambda m: f'<a href="{html.escape(m.group(1), quote=True)}">', t)
    t = t.replace("</link>", "</a>")
    t = re.sub(r"<super>", "<sup>", t); t = t.replace("</super>", "</sup>")
    t = re.sub(r"<br\s*/?>", "<br>", t)

    def tag(m):
        name = m.group(2).lower()
        if name == "a" or name in TAG_OK:
            return m.group(0)
        return ""
    t = re.sub(r"<(/?)([a-zA-Z]+)\b[^>]*>", tag, t)
    t = t.replace("&nbsp;&nbsp;", " ")
    return t.strip()


def cell(c):
    if isinstance(c, Paragraph):
        return md(c.text)
    if isinstance(c, (list, tuple)):
        return " ".join(cell(x) for x in c)
    if isinstance(c, str):
        return md(c)
    return ""


chapters, cur, listbuf = [], None, []


def emit(s):
    cur["html"].append(s)


def flush():
    global listbuf
    if listbuf:
        tag = listbuf[0][0]
        emit(f"<{tag}>" + "".join(f"<li>{x}</li>" for _, x in listbuf) + f"</{tag}>")
        listbuf = []


def case_link(c):
    cid = c.get("id", "") if isinstance(c, dict) else ""
    return (f'<p class="wb-fig">Diagram for case {html.escape(cid)}: <a href="/nhi-lab/#{cid.lower()}">see it on the lab page</a>.</p>'
            if cid else "")


def walk(fl):
    global cur
    name = type(fl).__name__
    if isinstance(fl, KeepTogether):
        for x in fl._content:
            walk(x)
        return
    if isinstance(fl, (list, tuple)):
        for x in fl:
            walk(x)
        return
    if name == "ChapterHead":
        if cur:
            flush()
        cur = {"num": str(fl.num), "title": fl.title, "kicker": fl.kicker, "sub": fl.sub, "html": []}
        chapters.append(cur)
        return
    if cur is None:
        return
    if isinstance(fl, Paragraph):
        sty = fl.style.name.lower()
        bt = getattr(fl, "bulletText", None)
        if bt:
            listbuf.append(("ol" if sty == "num" else "ul", md(fl.text)))
            return
        flush()
        tx = md(fl.text)
        if not tx:
            return
        if sty == "h2":
            emit(f"<h2>{tx}</h2>")
        elif sty == "h3":
            emit(f"<h3>{tx}</h3>")
        elif sty in ("caseh", "casehead"):
            emit(f'<h3 class="wb-case">{tx}</h3>')
        else:
            cls = {"lede": "lede", "small": "wb-small", "tiny": "wb-small", "note": "wb-small", "cap": "wb-small"}.get(sty)
            emit(f'<p class="{cls}">{tx}</p>' if cls else f"<p>{tx}</p>")
        return
    flush()
    if isinstance(fl, Table):
        rows = fl._cellvalues
        if not rows:
            return
        # A table holding a case diagram is a layout table: show what it holds in order.
        if any(type(c).__name__ in ("CaseDiagram", "ResultsMap") for r in rows for c in r):
            for r in rows:
                for c in r:
                    walk(c) if not isinstance(c, (str, Paragraph)) else emit(f"<p>{cell(c)}</p>")
            return
        first = rows[0]
        has_head = all(isinstance(c, Paragraph) and c.style.name.lower() == "cellh" for c in first if c not in ("", None))
        if has_head:
            t = '<div class="wb-tw"><table><thead><tr>' + "".join(f'<th scope="col">{cell(c)}</th>' for c in first) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
        else:  # a label column and its values (the case summaries)
            t = '<div class="wb-tw"><table><tbody>'
            t += "".join("<tr>" + "".join((f'<th scope="row">{cell(c)}</th>' if j == 0 else f"<td>{cell(c)}</td>") for j, c in enumerate(r)) + "</tr>" for r in rows)
        emit(t + "</tbody></table></div>")
        return
    if name == "Callout":
        emit(f'<aside class="wb-note wb-{fl.kind}"><p><b>{md(fl.title)}</b></p><p>{md(fl.text)}</p></aside>')
    elif name == "Tiles":
        emit('<ul class="wb-tiles">' + "".join(f"<li><b>{html.escape(str(n))}</b> {html.escape(l)}</li>" for n, l, _ in fl.items) + "</ul>")
    elif name == "StepDiagram":
        rows = getattr(fl, "rows", None) or (fl.__dict__.get("rows_") or [])
        steps = [s for row in rows for s in row]
        if steps:
            emit('<ol class="wb-steps">' + "".join(f"<li><b>{md(s[0])}</b> {md(s[1])}</li>" for s in steps) + "</ol>")
    elif name == "Timeline":
        emit('<ul class="wb-steps">' + "".join(f"<li><b>{html.escape(dl)}</b> {html.escape(lab)}</li>" for d, dl, lab, col, lvl in fl.EV) + "</ul>")
    elif name == "CaseDiagram":
        emit(case_link(getattr(fl, "case", None) or {}))
    elif name == "ResultsMap":
        emit('<p class="wb-fig">The map of all 67 cases is a picture in the PDF. The same results are in <a href="/nhi-lab/audit/">the audit table</a> and <a href="/labs/cases/?lab=nhi">the case list</a>.</p>')
    elif name == "Rule":
        emit("<hr>")


for fl in story:
    walk(fl)
flush()
chapters = [c for c in chapters if c["title"] not in ("Contents",) and c["html"]]


def slug(c):
    n, t = c["num"], c["title"]
    if n.isdigit():
        return f"chapter-{n}"
    if len(n) == 1 and n.isalpha():
        return f"appendix-{n.lower()}"
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def label(c):
    n = c["num"]
    return (f"Chapter {n}: " if n.isdigit() else f"Appendix {n}: " if n else "") + c["title"]


BOOK = "/nhi-lab/book/"
PDF = "/nhi-lab/nhi-lab-book.pdf"
HEAD = '    <link rel="stylesheet" href="/assets/web-book.css?v=20261115a">'
CRUMB = [("Home", "/"), ("Labs and projects", "/labs/"), ("Machine identity lab", "/nhi-lab/"), ("The book on the web", BOOK)]
out = ROOT / "nhi-lab" / "book"
if out.exists():
    shutil.rmtree(out)
toc = "".join(f'<li><a href="{BOOK}{slug(c)}/">{html.escape(label(c))}</a>' + (f"<span>{html.escape(c['sub'])}</span>" if c["sub"] else "") + "</li>" for c in chapters)
body = f'''      <section class="sec wb" aria-labelledby="wb-h">
        <div class="wrap wb-wrap">
          <p class="ey">Machine identity lab · the book</p>
          <h1 id="wb-h">Machine identities, tested in public</h1>
          <p class="lede">The whole book as web pages, one chapter per page: easier to read on a phone, to search and to use with a screen reader than the PDF. Edition 2, {EDITION}. The words are the same as in the PDF; diagrams link to the same case on the lab pages.</p>
          <p class="wb-pdf"><a href="{PDF}">Download the PDF</a> · <a href="/nhi-lab/">The lab</a> · Creative Commons Attribution 4.0</p>
          <h2>Contents</h2>
          <ol class="wb-toc">{toc}</ol>
        </div>
      </section>'''
write(BOOK, shell(BOOK, "Machine identities, tested in public: the book on the web",
                  "The machine identity lab book, chapter by chapter on the web: 67 cases, a seven-step framework, the 2026 market and what is missing.",
                  body, CRUMB, nav_current="/labs/", head_extra=HEAD))
for i, c in enumerate(chapters):
    prev_c = chapters[i - 1] if i else None
    next_c = chapters[i + 1] if i + 1 < len(chapters) else None
    nav = '<nav class="wb-pn" aria-label="Chapters">' + \
        (f'<a rel="prev" href="{BOOK}{slug(prev_c)}/"><span>Previous</span>{html.escape(label(prev_c))}</a>' if prev_c else "<span></span>") + \
        (f'<a rel="next" href="{BOOK}{slug(next_c)}/"><span>Next</span>{html.escape(label(next_c))}</a>' if next_c else "<span></span>") + "</nav>"
    body = f'''      <article class="sec wb" aria-labelledby="wb-h">
        <div class="wrap wb-wrap">
          <p class="ey"><a href="{BOOK}">Machine identities, tested in public</a> · {html.escape(c["kicker"])}</p>
          <h1 id="wb-h">{html.escape(c["title"])}</h1>
          {f'<p class="lede">{html.escape(c["sub"])}</p>' if c["sub"] else ""}
          {"".join(c["html"])}
          {nav}
          <p class="wb-pdf"><a href="{BOOK}">Contents</a> · <a href="{PDF}">The PDF</a> · All data in this book is made up.</p>
        </div>
      </article>'''
    url = f"{BOOK}{slug(c)}/"
    desc = (c["sub"] or c["title"]) + " From the machine identity lab book."
    write(url, shell(url, f"{label(c)} · Machine identity lab book", desc, body,
                     CRUMB + [(label(c), url)], nav_current="/labs/", head_extra=HEAD))
print("chapters:", len(chapters))
