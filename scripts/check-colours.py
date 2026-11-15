#!/usr/bin/env python3
"""Colour check (ENG-02): new raw hex colours go in assets/tokens.css, not in other files.

The site has a few hundred hex colours spread across its stylesheets and pages from before the
tokens existed. They are recorded in data/colour-baseline.json, file by file. This check fails
only when a file gains a hex colour it did not have, and suggests the nearest token instead.
So the number can only go down.

    python3 scripts/check-colours.py                    # check
    python3 scripts/check-colours.py --update-baseline  # record today's colours (after removing some)
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "data" / "colour-baseline.json"
TOKENS = ROOT / "assets" / "tokens.css"
HEX = re.compile(r"(?<![\w&])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
SKIP = {".git", "node_modules", "_site", "archive", "worker", "workers", "pyodide"}


def norm(h):
    h = h.lower()
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    return "#" + h[:6]


def colours(path):
    s = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".html":  # only what styles the page: <style> blocks and style="" attributes
        parts = re.findall(r"<style[^>]*>(.*?)</style>", s, re.S) + re.findall(r'style="([^"]*)"', s)
        s = "\n".join(parts)
    else:
        s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return sorted({norm(m) for m in HEX.findall(s)})


def files():
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.suffix in (".css", ".html") and not (set(p.relative_to(ROOT).parts) & SKIP) and p != TOKENS \
                and not (p.parent == ROOT / "assets" and p.name.startswith("b-")):  # bundles are copies (bundle-css.py)
            yield p


def tokens():
    out = {}
    for name, val in re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b", TOKENS.read_text()):
        out.setdefault(norm(val[1:]), name)
    return out


def nearest(h, toks):
    rgb = lambda x: [int(x[i:i + 2], 16) for i in (1, 3, 5)]
    a = rgb(h)
    best = min(toks.items(), key=lambda kv: sum((p - q) ** 2 for p, q in zip(a, rgb(kv[0]))), default=None)
    return f"var({best[1]}) ({best[0]})" if best else "a token in assets/tokens.css"


def main(argv):
    found = {p.relative_to(ROOT).as_posix(): colours(p) for p in files()}
    found = {k: v for k, v in found.items() if v}
    if "--update-baseline" in argv:
        BASE.write_text(json.dumps(found, indent=1, sort_keys=True) + "\n")
        print(f"Baseline: {len({c for v in found.values() for c in v})} different colours in {len(found)} files.")
        return 0
    base = json.loads(BASE.read_text()) if BASE.exists() else {}
    toks = tokens()
    bad = {f: [c for c in v if c not in set(base.get(f, []))] for f, v in found.items()}
    bad = {f: v for f, v in bad.items() if v}
    total = len({c for v in found.values() for c in v})
    # every page loads the shared colours (secure-india-exams is a dated, light standalone document)
    no_tok = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.html")
              if not p.relative_to(ROOT).as_posix().startswith(("agent-skills/", "_site/", "node_modules/", ".git/", "scripts/", "_includes/"))
              and p.relative_to(ROOT).as_posix() != "secure-india-exams/index.html"
              and "<head" in (t := p.read_text(errors="ignore")) and 'http-equiv="refresh"' not in t and "/assets/tokens.css" not in t]
    for f in no_tok:
        print(f"NO TOKENS {f}: add <link rel=\"stylesheet\" href=\"/assets/tokens.css\"> as its first stylesheet")
    if not bad and not no_tok:
        print(f"No new raw colours. {total} different hex colours outside tokens.css, all known. Every page loads tokens.css.")
        return 0
    if not bad:
        return 1
    for f, v in bad.items():
        for c in v:
            print(f"NEW {f}: {c}  -> use {nearest(c, toks)}")
    print("\nNew colours belong in assets/tokens.css as a token. If this one is intended, run with --update-baseline.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
