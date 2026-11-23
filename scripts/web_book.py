"""Turn a ReportLab book story into web chapters. Shared by build-nhi-chapters.py and build-ca-chapters.py.

A book script is run up to the point where it would build the PDF (see load_story), then each flowable
becomes HTML: headings, paragraphs, lists, tables and callouts as they are; drawings through the
handlers a book passes in, so a diagram turns into words or a link to the same thing on the lab pages.
"""
import html, re

TAG_OK = {"b", "i", "u", "br", "sup", "sub", "strong", "em"}


def load_story(path, marker, ns_extra=None, replace=()):
    """Run a book script up to `marker` (or a line starting with it) and return its namespace."""
    src = path.read_text(encoding="utf-8")
    for a, b in replace:
        src = src.replace(a, b)
    i = src.find(marker)
    if i < 0:
        raise SystemExit(f"{path.name}: marker {marker!r} not found")
    ns = {"__file__": str(path), "__name__": "web_book_story", **(ns_extra or {})}
    exec(compile(src[:i], path.name, "exec"), ns)
    return ns


def md(t):
    """ReportLab paragraph markup to HTML."""
    t = str(t)
    t = re.sub(r'<link href="([^"]+)"[^>]*>', lambda m: f'<a href="{html.escape(m.group(1), quote=True)}">', t)
    t = t.replace("</link>", "</a>")
    t = re.sub(r"<super>", "<sup>", t); t = t.replace("</super>", "</sup>")
    t = re.sub(r"<br\s*/?>", "<br>", t)

    def tag(m):
        name = m.group(2).lower()
        return m.group(0) if name == "a" or name in TAG_OK else ""
    t = re.sub(r"<(/?)([a-zA-Z]+)\b[^>]*>", tag, t)
    return t.replace("&nbsp;&nbsp;", " ").strip()


class Walker:
    """Collect chapters from a story. handlers maps a flowable class name to fn(flowable, walker)."""

    def __init__(self, handlers=None, layout_tables=()):
        from reportlab.platypus import Paragraph, Table, KeepTogether
        self.P, self.T, self.K = Paragraph, Table, KeepTogether
        self.handlers = handlers or {}
        self.layout_tables = set(layout_tables)
        self.chapters, self.cur, self.listbuf = [], None, []

    def emit(self, s):
        if self.cur is not None:
            self.cur["html"].append(s)

    def flush(self):
        if self.listbuf:
            tag = self.listbuf[0][0]
            self.emit(f"<{tag}>" + "".join(f"<li>{x}</li>" for _, x in self.listbuf) + f"</{tag}>")
            self.listbuf = []

    def cell(self, c):
        if isinstance(c, self.P):
            return md(c.text)
        if isinstance(c, (list, tuple)):
            return " ".join(self.cell(x) for x in c)
        if isinstance(c, str):
            return md(c)
        return ""

    def walk(self, fl):
        name = type(fl).__name__
        if isinstance(fl, self.K):
            for x in fl._content:
                self.walk(x)
            return
        if isinstance(fl, (list, tuple)):
            for x in fl:
                self.walk(x)
            return
        if name == "ChapterHead":
            self.flush()
            self.cur = {"num": str(fl.num), "title": fl.title, "kicker": fl.kicker, "sub": fl.sub, "html": []}
            self.chapters.append(self.cur)
            return
        if self.cur is None:
            return
        if isinstance(fl, self.P):
            sty = fl.style.name.lower()
            if getattr(fl, "bulletText", None):
                self.listbuf.append(("ol" if sty == "num" else "ul", md(fl.text)))
                return
            self.flush()
            tx = md(fl.text)
            if not tx:
                return
            if sty in ("h2", "h2front"):
                self.emit(f"<h2>{tx}</h2>")
            elif sty == "h3":
                self.emit(f"<h3>{tx}</h3>")
            elif sty in ("caseh", "casehead"):
                self.emit(f'<h3 class="wb-case">{tx}</h3>')
            else:
                cls = {"lede": "lede", "small": "wb-small", "tiny": "wb-small", "note": "wb-small", "cap": "wb-small"}.get(sty)
                self.emit(f'<p class="{cls}">{tx}</p>' if cls else f"<p>{tx}</p>")
            return
        self.flush()
        if isinstance(fl, self.T):
            self.table(fl)
            return
        if name in self.handlers:
            self.handlers[name](fl, self)
        elif name == "Callout":
            self.emit(f'<aside class="wb-note wb-{fl.kind}"><p><b>{md(fl.title)}</b></p><p>{md(fl.text)}</p></aside>')
        elif name == "Tiles":
            self.emit('<ul class="wb-tiles">' + "".join(f"<li><b>{html.escape(str(it[0]))}</b> {html.escape(str(it[1]))}</li>" for it in fl.items) + "</ul>")
        elif name == "Rule":
            self.emit("<hr>")

    def table(self, fl):
        rows = fl._cellvalues
        if not rows:
            return
        if any(type(c).__name__ in self.layout_tables for r in rows for c in r):
            for r in rows:
                for c in r:
                    self.walk(c) if not isinstance(c, (str, self.P)) else self.emit(f"<p>{self.cell(c)}</p>")
            return
        first = rows[0]
        has_head = all(isinstance(c, self.P) and c.style.name.lower() == "cellh" for c in first if c not in ("", None))
        if has_head:
            t = '<div class="wb-tw"><table><thead><tr>' + "".join(f'<th scope="col">{self.cell(c)}</th>' for c in first) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{self.cell(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
        else:  # a label column and its values
            t = '<div class="wb-tw"><table><tbody>'
            t += "".join("<tr>" + "".join((f'<th scope="row">{self.cell(c)}</th>' if j == 0 else f"<td>{self.cell(c)}</td>")
                                          for j, c in enumerate(r)) + "</tr>" for r in rows)
        self.emit(t + "</tbody></table></div>")

    def run(self, story):
        for fl in story:
            self.walk(fl)
        self.flush()
        return [c for c in self.chapters if c["title"] not in ("Contents",) and c["html"]]


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


def fix_levels(body):
    """Keep the heading outline unbroken under the chapter's h1 (screen readers navigate by level).
    Headings at level 3 before the first h2 move up to h2; with no h2 at all, every heading moves up one."""
    import re as _re
    levels = [int(x) for x in _re.findall(r"<h([2-6])\b", body)]
    if not levels or levels[0] <= 2:
        return body
    if 2 not in levels:
        return _re.sub(r"<(/?)h([3-6])\b", lambda m: f"<{m.group(1)}h{int(m.group(2)) - 1}", body)
    first_h2 = _re.search(r"<h2\b", body).start()
    head = _re.sub(r"<(/?)h3\b", r"<\1h2", body[:first_h2])
    return head + body[first_h2:]


def write_book(chapters, *, book, pdf, title, desc, lede, ey, short, crumb, shell, write, head, root_dir):
    """Write the contents page and one page per chapter."""
    import shutil
    if root_dir.exists():
        shutil.rmtree(root_dir)
    toc = "".join(f'<li><a href="{book}{slug(c)}/">{html.escape(label(c))}</a>' + (f"<span>{html.escape(c['sub'])}</span>" if c["sub"] else "") + "</li>"
                  for c in chapters)
    body = f'''      <section class="sec wb" aria-labelledby="wb-h">
        <div class="wrap wb-wrap">
          <p class="ey">{ey}</p>
          <h1 id="wb-h">{html.escape(title)}</h1>
          <p class="lede">{lede}</p>
          <p class="wb-pdf"><a href="{pdf}">Download the PDF</a> · <a href="{pdf[:-4]}-accessible.pdf">Screen reader PDF (tagged)</a> · <a href="{crumb[-1][1]}">The lab</a> · Creative Commons Attribution 4.0</p>
          <h2>Contents</h2>
          <ol class="wb-toc">{toc}</ol>
        </div>
      </section>'''
    write(book, shell(book, f"{title}: the book on the web", desc, body, crumb + [("The book on the web", book)], nav_current="/labs/", head_extra=head))
    for i, c in enumerate(chapters):
        prev_c = chapters[i - 1] if i else None
        next_c = chapters[i + 1] if i + 1 < len(chapters) else None
        nav = '<nav class="wb-pn" aria-label="Chapters">' + \
            (f'<a rel="prev" href="{book}{slug(prev_c)}/"><span>Previous</span>{html.escape(label(prev_c))}</a>' if prev_c else "<span></span>") + \
            (f'<a rel="next" href="{book}{slug(next_c)}/"><span>Next</span>{html.escape(label(next_c))}</a>' if next_c else "<span></span>") + "</nav>"
        body = f'''      <article class="sec wb" aria-labelledby="wb-h">
        <div class="wrap wb-wrap">
          <p class="ey"><a href="{book}">{html.escape(title)}</a> · {html.escape(c["kicker"])}</p>
          <h1 id="wb-h">{html.escape(c["title"])}</h1>
          {f'<p class="lede">{html.escape(c["sub"])}</p>' if c["sub"] else ""}
          {fix_levels("".join(c["html"]))}
          {nav}
          <p class="wb-pdf"><a href="{book}">Contents</a> · <a href="{pdf}">The PDF</a> · All data in this book is made up.</p>
        </div>
      </article>'''
        url = f"{book}{slug(c)}/"
        write(url, shell(url, label(c) if len(label(c)) > 52 else f"{label(c)} · {short}", (c["sub"] or c["title"]) + f" From the {short}.", body,
                         crumb + [("The book on the web", book), (label(c), url)], nav_current="/labs/", head_extra=head, brand=False))
