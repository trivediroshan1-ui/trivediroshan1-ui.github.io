# Build scripts for the conditional access, MFA and AI agent lab

These made the pages, data, book and video under `/ca-mfa-lab/`. They were written in a
working session and are kept here so the lab can be rebuilt. They are a record first:
the paths inside them point at the working folder they ran in (`/home/claude/...`), so
change the paths at the top of each file before running.

| File | What it makes |
|---|---|
| `build_data.py` | `ca-mfa-lab/data/cases.js` and the catalogue CSV, from the catalogue, the results files and `stages.py` |
| `stages.py` | The seven links of the access chain and which case sits at which link |
| `build_pages.py` | The framework, virtual lab, sources and run-in-browser pages |
| `build_ca_book.py`, `sources.json` | The book, `ca-mfa-lab-book.pdf` (uses `scripts/book_lib.py`) |
| `build_video.py` | The 96-second video and its poster |

The evidence (guesses, run scripts, results) is in `ca-mfa-lab/evidence/` and is not made by these scripts.
Do not edit a locked guess file: each run script checks its SHA-256 and refuses to run if it changed.

Last reviewed 14 November 2026.
