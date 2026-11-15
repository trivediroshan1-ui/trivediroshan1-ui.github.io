"""Sources for the AI governance lab books and the frameworks page (CONT-02).

One list, used by build-agl-book.py, build-agl-addendum2.py and the frameworks page,
so the books and the website always cite the same thing.

Every row says what the source is, what the lab uses it for, and how far I checked it
on the date below. Mappings in the books are my own reading; they are not legal advice
and not a claim of compliance.
"""
import html

CHECKED = "15 November 2026"

# How far each source was checked. Shown in full in the table.
OPENED = "Official text opened"
PAGE = "Official page opened (title, number and date)"
VIA = "Official link as given by {}; it did not open for me"
PAID = "Paid standard; the publisher page did not load for me, so the mapping rests on my own reading"
SUMMARY = "Official summary opened; full text is on the ministry site"

S = {
  "iso42001": dict(name="ISO/IEC 42001:2023, Artificial intelligence: Management system", by="ISO and IEC", date="2023",
                   url="https://www.iso.org/standard/81230.html", use="The ISO column of the control table", how=PAID),
  "airmf": dict(name="Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1", by="NIST", date="January 2023",
                url="https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf", use="The NIST AI RMF column of the control table", how=OPENED),
  "euaia": dict(name="Regulation (EU) 2024/1689, the Artificial Intelligence Act", by="European Parliament and Council", date="13 June 2024",
                url="https://eur-lex.europa.eu/eli/reg/2024/1689/oj", use="The EU AI Act column of the control table", how=PAGE),
  "gdpr": dict(name="Regulation (EU) 2016/679, the General Data Protection Regulation", by="European Parliament and Council", date="27 April 2016",
               url="https://eur-lex.europa.eu/eli/reg/2016/679/oj", use="C4: personal data sent outside India", how=PAGE),
  "meity": dict(name="India AI Governance Guidelines: Enabling Safe and Trusted AI Innovation", by="Ministry of Electronics and Information Technology (MeitY)", date="5 November 2025",
                url="https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc2025115685601.pdf", use="C1: a named owner for every AI use", how=OPENED),
  "freeai": dict(name="Framework for Responsible and Ethical Enablement of Artificial Intelligence (FREE-AI), committee report", by="Reserve Bank of India", date="13 August 2025",
                 url="https://rbi.org.in/Scripts/PublicationReportDetails.aspx?ID=1306", use="C2, C3, C13, C15 and C16: approval, monitoring, disclosure, consumer protection and continuity", how=PAGE),
  "certin_ai": dict(name="Blueprint for Reducing Exposure and Defending against AI-Assisted Vulnerabilities Exploitation in Digital Infrastructure (the table calls it the CERT-In AI blueprint)",
                    by="CERT-In", date="25 May 2026", url="https://www.cert-in.org.in/PDF/Blueprint_for_Defending_against_AI_Assisted_Exploitataion.pdf",
                    use="C1, C5, C6, C9 and C16: AI inventory, data in prompts, emergency shutdown, agent identity, fallbacks", how=VIA.format("JSA (June 2026)")),
  "certin_bom": dict(name="Technical Guidelines on SBOM, QBOM and CBOM, AIBOM and HBOM, version 2.0", by="CERT-In", date="9 July 2025",
                     url="https://cert-in.org.in/PDF/TechnicalGuidelines-on-SBOM,QBOM&CBOM,AIBOM_and_HBOM_ver2.0.pdf", use="C8: an AI bill of materials for every use", how=VIA.format("Khaitan &amp; Co (July 2025)")),
  "certin_dir": dict(name="Directions under section 70B(6) of the IT Act, 2000 (No. 20(3)/2022-CERT-In)", by="CERT-In", date="28 April 2022",
                     url="https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf", use="C7 and C12: 180 days of logs, and reporting within 6 hours", how=OPENED),
  "dpdp": dict(name="Digital Personal Data Protection Act, 2023, and Digital Personal Data Protection Rules, 2025 (notified 14 November 2025)", by="Government of India (MeitY)", date="11 August 2023 and 14 November 2025",
               url="https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf", use="C4, C5 and C12: minimisation, safeguards and breach notice", how=SUMMARY),
  "sebi": dict(name="Safer participation of retail investors in Algorithmic trading, circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013", by="SEBI", date="4 February 2025",
               url="https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html", use="C6: the kill switch", how=PAGE),
  "owasp_asi": dict(name="OWASP Top 10 for Agentic Applications for 2026 (ASI01 to ASI10)", by="OWASP GenAI Security Project", date="9 December 2025",
                    url="https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/", use="I5 and C10: ASI03 identity and privilege abuse, ASI07 insecure agent-to-agent messages", how=PAGE),
  "iso27001": dict(name="ISO/IEC 27001:2022, Information security management systems: Requirements (Annex A)", by="ISO and IEC", date="2022",
                   url="https://www.iso.org/standard/27001", use="The ISO 27001 column of the control table", how=PAID),
  "sp80053": dict(name="NIST SP 800-53 Revision 5, Security and Privacy Controls for Information Systems and Organizations", by="NIST", date="September 2020, with later updates",
                  url="https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf", use="The NIST 800-53 column of the control table", how=OPENED),
  "pcidss": dict(name="PCI Data Security Standard. The table was written against v4.0; the library now lists v4.0.1 as current", by="PCI Security Standards Council", date="v4.0.1 current on the check date",
                 url="https://www.pcisecuritystandards.org/document_library/", use="The PCI DSS column of the control table", how=PAGE),
  "hipaa": dict(name="45 CFR Part 164, Security and Privacy (HIPAA)", by="US Department of Health and Human Services, via the eCFR", date="current eCFR text",
                url="https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164", use="The HIPAA column of the control table", how=PAGE),
  "rbi_it": dict(name="Master Direction on Outsourcing of Information Technology Services (RBI/2023-24/102)", by="Reserve Bank of India", date="10 April 2023",
                 url="https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12486", use="Vendor and outsourcing cases in the later rounds", how=PAGE),
  "rpwd": dict(name="The Rights of Persons with Disabilities Act, 2016 (Act 49 of 2016)", by="Government of India", date="27 December 2016",
               url="https://www.indiacode.nic.in/handle/123456789/2155", use="Accessible sign-in in the later rounds", how=PAGE),
}

BOOK = ["iso42001", "airmf", "euaia", "meity", "freeai", "certin_ai", "certin_bom", "certin_dir", "dpdp", "sebi", "owasp_asi", "gdpr"]
ADDENDUM = ["iso27001", "sp80053", "pcidss", "hipaa", "dpdp", "rbi_it", "certin_dir", "rpwd"]

INTRO = (f"Every standard, law and guideline the control tables mention, with a link to the official text. I checked each link on {CHECKED}. "
         "The last column says how far: whether I opened the official text, only its official page, or could not open it. "
         "The mappings are my own reading. They are not legal advice and not a claim of compliance. Check each one against the current official text.")


def table(keys, for_print=True):
    """An HTML table of sources. for_print shows the full URL so it survives on paper."""
    rows = []
    for k in keys:
        s = S[k]
        link = (f'<br><span class="url">{html.escape(s["url"])}</span>' if for_print
                else f'<br><a href="{html.escape(s["url"])}">Official link</a>')
        rows.append(f'<tr><td><b>{s["name"]}</b><br>{s["by"]}, {s["date"]}{link}</td><td>{s["use"]}</td><td>{s["how"]}</td></tr>')
    return ('<table class="plain tiny sources"><thead><tr><th>Source</th><th>Used for</th><th>How far I checked it</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table>")
