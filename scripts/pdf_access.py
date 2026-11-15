#!/usr/bin/env python3
"""Accessibility finishing for the site's PDFs.

finalize(path, ...) rewrites a PDF in place with its text and pages untouched:
  - document language (default en-IN), so a screen reader picks the right voice
  - DisplayDocTitle, so the title (not the file name) shows in the window bar
  - Title, Author, Subject and Keywords when given
It keeps a tag tree and bookmarks if the file already has them. It never adds a tag tree:
only a Chromium render with tagged=True makes one.

  python3 scripts/pdf_access.py report            # which PDFs are tagged, have a language, bookmarks
  python3 scripts/pdf_access.py lang FILE...      # language + title bar only
"""
import glob, pathlib, sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DictionaryObject, NameObject, TextStringObject

ROOT = pathlib.Path(__file__).resolve().parent.parent


RIGHTS = ("(c) 2026 Roshan Trivedi. Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. "
          "How to credit: https://roshantrivedi.co.in/copyright/")
LICENSE_URL = "https://roshantrivedi.co.in/copyright/"


def _xmp(title, author, rights, url):
    from xml.sax.saxutils import escape as x
    return f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/">
<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{x(title or "")}</rdf:li></rdf:Alt></dc:title>
<dc:creator><rdf:Seq><rdf:li>{x(author or "")}</rdf:li></rdf:Seq></dc:creator>
<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">{x(rights)}</rdf:li></rdf:Alt></dc:rights>
<xmpRights:Marked>True</xmpRights:Marked><xmpRights:WebStatement>{x(url)}</xmpRights:WebStatement>
</rdf:Description></rdf:RDF></x:xmpmeta>
<?xpacket end="w"?>"""


def finalize(path, title=None, author=None, subject=None, keywords=None, lang="en-IN", rights=None):
    """Set metadata, language and title bar. With rights=..., also write a Copyright entry and
    XMP rights metadata (dc:rights, xmpRights:WebStatement), so the licence travels with the file (IP-02)."""
    path = pathlib.Path(path)
    r = PdfReader(str(path))
    w = PdfWriter(clone_from=r)
    md = dict(r.metadata or {})
    for k, v in (("/Title", title), ("/Author", author), ("/Subject", subject), ("/Keywords", keywords), ("/Copyright", rights)):
        if v:
            md[k] = v
    w.add_metadata(md)
    root = w._root_object
    if rights:
        from pypdf.generic import StreamObject
        xmp = StreamObject()
        xmp._data = _xmp(md.get("/Title"), md.get("/Author"), rights, LICENSE_URL).encode("utf-8")
        xmp[NameObject("/Type")] = NameObject("/Metadata")
        xmp[NameObject("/Subtype")] = NameObject("/XML")
        root[NameObject("/Metadata")] = w._add_object(xmp)
    root[NameObject("/Lang")] = TextStringObject(lang)
    vp = root.get("/ViewerPreferences")
    vp = DictionaryObject() if vp is None else vp.get_object()
    vp[NameObject("/DisplayDocTitle")] = BooleanObject(True)
    root[NameObject("/ViewerPreferences")] = vp
    tmp = path.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as f:
        w.write(f)
    tmp.replace(path)


def tag_counts(path):
    root = PdfReader(str(path)).trailer["/Root"]
    if "/StructTreeRoot" not in root:
        return {}
    out = {}

    def walk(n):
        n = n.get_object()
        if isinstance(n, dict):
            s = n.get("/S")
            if s:
                out[str(s)] = out.get(str(s), 0) + 1
            if n.get("/K") is not None:
                walk(n["/K"])
        elif isinstance(n, list):
            for x in n:
                walk(x)

    walk(root["/StructTreeRoot"])
    return out


def report():
    files = sorted(set(glob.glob(str(ROOT / "assets/*.pdf")) + glob.glob(str(ROOT / "*/*.pdf")) + glob.glob(str(ROOT / "*.pdf"))))
    for f in files:
        r = PdfReader(f)
        root = r.trailer["/Root"]
        tc = tag_counts(f)
        print(f"{pathlib.Path(f).name[:44]:44} lang={root.get('/Lang')!s:6} title-bar={(root.get('/ViewerPreferences') or {}).get('/DisplayDocTitle')!s:5} "
              f"tagged={'yes' if tc else 'no':3} headings={sum(v for k, v in tc.items() if k.startswith('/H') and k[2:].isdigit()):<3} bookmarks={len(r.outline)}")
    import hashlib
    groups = {}
    for f in files:
        groups.setdefault(hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(), []).append(pathlib.Path(f).relative_to(ROOT).as_posix())
    for h, fs in groups.items():
        if len(fs) > 1:
            print("same bytes:", " = ".join(fs))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        report()
    elif len(sys.argv) > 2 and sys.argv[1] == "lang":
        for f in sys.argv[2:]:
            finalize(f)
            print("ok", f)
    else:
        print(__doc__)
