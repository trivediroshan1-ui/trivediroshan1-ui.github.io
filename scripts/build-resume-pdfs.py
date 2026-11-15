#!/usr/bin/env python3
"""Build the résumé and cover letter PDFs from scripts/resume/*.html (tagged, with metadata).

Edit the HTML, then run:  python3 scripts/build-resume-pdfs.py
The web pages /resume/ and /cover-letter/ are separate; keep the facts in step.
"""
import pathlib, sys
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import pdf_access

JOBS = [("resume/resume.html", "Roshan_Trivedi_Resume.pdf", "Roshan Trivedi, Résumé",
         "IAM and PAM platform owner and architect: credential management, Zero Standing Privilege, non-human identity."),
        ("resume/cover-letter.html", "Roshan_Trivedi_Cover_Letter.pdf", "Roshan Trivedi, Cover letter",
         "Cover letter for senior IAM and PAM roles.")]
FOOT = ('<div style="font:7.5pt Manrope,sans-serif;color:#6b7089;width:100%;padding:0 14mm;display:flex;justify-content:space-between">'
        '<span>Roshan Trivedi | roshantrivedi.co.in</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    for src, out, title, subject in JOBS:
        pg.goto((HERE / src).as_uri(), wait_until="load")
        pg.evaluate("document.fonts.ready")
        two = src.endswith("resume.html")
        pg.pdf(path=str(ROOT / out), format="A4", print_background=True, prefer_css_page_size=True, tagged=True, outline=True,
               display_header_footer=two, header_template="<span></span>", footer_template=FOOT if two else "<span></span>")
        pdf_access.finalize(ROOT / out, title=title, author="Roshan Trivedi", subject=subject, lang="en-IN")
        print("wrote", out)
    b.close()
