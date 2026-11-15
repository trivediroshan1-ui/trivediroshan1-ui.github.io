#!/usr/bin/env python3
"""Add "Last reviewed <date>" to the footer of every page that shows no date yet.

Pages built by page_shell.shell() get it automatically; this covers the hand-written ones.
Usage: python3 scripts/add-reviewed.py [--date "16 Nov 2026"] [--check]
"""
import argparse, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from page_shell import ROOT, REVIEWED, add_reviewed

SKIP = ("agent-skills/", "_site/", "node_modules/", ".git/")
ap = argparse.ArgumentParser()
ap.add_argument("--date", default=REVIEWED)
ap.add_argument("--check", action="store_true", help="list pages with no date and exit 1 if any")
a = ap.parse_args()
missing = []
for p in sorted(ROOT.rglob("index.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(SKIP):
        continue
    t = p.read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in t or re.search(r"Last (reviewed|updated)|and not updated since", t):
        continue
    if a.check:
        missing.append(rel)
        continue
    n = add_reviewed(t, a.date)
    if n != t:
        p.write_text(n, encoding="utf-8")
        print("dated", rel)
    else:
        missing.append(rel)
if missing:
    print("no date and no footer to put it in:" if not a.check else "pages with no date:", *missing, sep="\n  ")
    sys.exit(1 if a.check else 0)
