#!/usr/bin/env python3
"""Fail if a page quotes a lab number that disagrees with data/stats.json.

Checks "N cases", "N rounds" and "N pages" next to the lab's own words.
A different number is allowed when the same line says why (for example
"first four rounds"), when it belongs to another document listed in
stats.json (the MCP lab), or on a known dated page. Run from the repo root:

    python3 scripts/check-numbers.py
"""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "data" / "stats.json").read_text())
lab, book, mcp = S["ai_governance_lab"], S["who_approved_that_book"], S["mcp_lab"]
legacy = [w.lower() for w in S["legacy_context_words"]]
good_cases = {lab["cases"], lab["cases_rounds_1_to_4"], lab["cases_rounds_5_to_13"], mcp["cases"], mcp["round_one_cases"], mcp["round_one_first_run_cases"]}
good_pages = {lab["book_pages"], lab["addendum_pages"], book["pages"], book["print_interior_pages"], mcp["report_pages"]}
good_rounds = {lab["rounds"]}
SKIP_DIRS = {".git", "node_modules", "worker", "_posts"}
# Dated or recorded text that is true as written: a video transcript and the correction log.
SKIP_FILES = {"ai-governance-lab/story/index.html", "ai-governance-lab/what-i-got-wrong/index.html"}
bad = []
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix not in {".html", ".md", ".txt"}:
        continue
    rel = p.relative_to(ROOT).as_posix()
    if set(p.relative_to(ROOT).parts) & SKIP_DIRS or rel in SKIP_FILES:
        continue
    for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
        low = line.lower()
        if any(w in low for w in legacy):
            continue
        for m in re.finditer(r"\b(\d{1,3})(?:\s|&nbsp;)+(cases|rounds|pages)\b", line):
            num, kind = int(m.group(1)), m.group(2)
            ok = {"cases": good_cases, "rounds": good_rounds, "pages": good_pages}[kind]
            if kind == "cases" and num < 40:
                continue          # small counts such as "12 cases" in one round
            if kind == "rounds" and num <= 12:
                continue          # "rounds 5 to 13" style ranges, "two rounds"
            if kind == "pages" and num < 40:
                continue          # "21 pages", "15-page" and similar other documents
            if num not in ok:
                bad.append(f"{rel}:{n}: '{m.group(0)}' is not in data/stats.json")
for b in bad:
    print(b)
print(len(bad), "number mismatches")
sys.exit(1 if bad else 0)
