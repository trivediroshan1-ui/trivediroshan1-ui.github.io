#!/usr/bin/env python3
"""Serve each page's stylesheets as one or two files instead of 9 to 20 (PERF-02).

How it works, so nothing about the look changes:
- On each page, a run of <link rel="stylesheet" href="/assets/NAME.css"> tags that only scripts,
  meta tags and other non-style tags separate becomes one link to /assets/b-HASH.css: the same
  files, in the same order, joined. A <style> block or any other stylesheet ends a run, so the
  cascade stays exactly as it was.
- The original tags stay in the page, inside a comment just above the bundle link. Edit them
  there as before (other scripts can find and change them too), then run this script again.
- The file name is a hash of the content, so a changed stylesheet gets a new name: no stamps needed.
- Bundles that no page uses any more are deleted.

    python3 scripts/bundle-css.py            # (re)build every bundle and update the pages
    python3 scripts/bundle-css.py --check    # fail if a page or bundle is out of date (CI)
    python3 scripts/bundle-css.py --unbundle # put the original tags back everywhere
Run it after changing any stylesheet in assets/ or any page's stylesheet links.
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SKIP = {".git", "_site", "archive", "worker", "workers", "pyodide", "node_modules"}
LINK = re.compile(r'<link rel="stylesheet" href="/assets/([a-z0-9-]+)\.css(?:\?v=[0-9a-z]+)?">')
BLOCK = re.compile(r"<!-- css-bundle: .*?\n(.*?)-->\s*<link rel=\"stylesheet\" href=\"/assets/b-[0-9a-f]{10}\.css\">", re.S)
# Tags that may sit between two stylesheet links without ending a run.
NEUTRAL = re.compile(r"\s*(?:<script\b[^>]*>.*?</script>|<meta\b[^>]*>|<link\b(?![^>]*rel=\"stylesheet\")[^>]*>|<!--(?!\s*css-bundle).*?-->)", re.S)
NOTE = "<!-- css-bundle: these stylesheets are served joined as {name}. Edit the tags here, then run scripts/bundle-css.py\n"


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if not (set(rel.parts) & SKIP):
            yield p


def unbundle(html):
    return BLOCK.sub(lambda m: m.group(1).rstrip("\n").replace("\n", "\n    ").strip(), html)


def runs(head):
    """Yield (start, end, [link match objects]) for each run of two or more bundleable links."""
    pos, cur = 0, []
    out = []
    while True:
        m = LINK.search(head, pos)
        if not m:
            break
        if cur:
            gap = head[cur[-1].end():m.start()]
            if NEUTRAL.sub("", gap).strip():  # something that is not neutral sits between them
                out.append(cur); cur = []
        cur.append(m)
        pos = m.end()
    if cur:
        out.append(cur)
    return [r for r in out if len(r) >= 2]


def bundle_text(names):
    parts = []
    for n in names:
        css = (ASSETS / f"{n}.css").read_text(encoding="utf-8")
        if "@import" in css:
            raise SystemExit(f"{n}.css uses @import; bundling would change it. Remove the @import first.")
        parts.append(f"/* {n}.css */\n" + re.sub(r'^@charset "[^"]*";\s*', "", css).rstrip() + "\n")
    return "\n".join(parts)


def process(html, made):
    html = unbundle(html)
    if "</head>" not in html:
        return html
    head, rest = html.split("</head>", 1)
    for run in reversed(runs(head)):
        names = []
        for m in run:
            if m.group(1) not in names:
                names.append(m.group(1))
        text = bundle_text(names)
        name = "b-" + hashlib.sha256(text.encode()).hexdigest()[:10] + ".css"
        made[name] = text
        original = "\n".join(m.group(0) for m in run)
        start, end = run[0].start(), run[-1].end()
        between = head[start:end]
        for m in reversed(run):  # take the links out, keep the scripts and meta tags that sat between them
            s, e = m.start() - start, m.end() - start
            between = between[:s] + between[e:]
        kept = "\n    ".join(x.strip() for x in NEUTRAL.findall(between) if x.strip())
        block = NOTE.format(name=name) + original + "\n-->\n    " + f'<link rel="stylesheet" href="/assets/{name}">'
        head = head[:start] + block + ("\n    " + kept if kept else "") + head[end:]
    return head + "</head>" + rest


def main(argv):
    if "--unbundle" in argv:
        for p in pages():
            s = p.read_text(encoding="utf-8")
            u = unbundle(s)
            if u != s:
                p.write_text(u, encoding="utf-8")
        for b in ASSETS.glob("b-*.css"):
            b.unlink()
        print("Original stylesheet links restored.")
        return 0
    check = "--check" in argv
    made, stale, n = {}, [], 0
    for p in pages():
        s = p.read_text(encoding="utf-8")
        new = process(s, made)
        if new != s:
            stale.append(p.relative_to(ROOT).as_posix())
            if not check:
                p.write_text(new, encoding="utf-8")
        if "css-bundle:" in new:
            n += 1
    old = {b.name for b in ASSETS.glob("b-*.css")}
    for name, text in made.items():
        f = ASSETS / name
        if not f.exists() or f.read_text(encoding="utf-8") != text:
            stale.append("assets/" + name)
            if not check:
                f.write_text(text, encoding="utf-8")
    unused = sorted(old - set(made))
    if check:
        if stale or unused:
            print("Stylesheet bundles are out of date. Run: python3 scripts/bundle-css.py")
            for x in stale[:20] + ["unused " + u for u in unused]:
                print("  ", x)
            return 1
        print(f"Bundles up to date: {len(made)} bundles on {n} pages.")
        return 0
    for u in unused:
        (ASSETS / u).unlink()
    print(f"{len(made)} bundles on {n} pages; {len(stale)} files written; {len(unused)} unused bundles removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
