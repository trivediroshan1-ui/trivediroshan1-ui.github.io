STATUS: DRAFT. Correction to earlier notes on W05. 14 November 2026.

I read SonicWall's own advisory page for SNWLID-2026-0014 (SonicWall SonicOS Affected By Multiple Vulnerabilities) on 14 November. It was copied from the vendor page and pasted to me.

What the page says about CVE-2026-19868:
- Description: a user with valid credentials for an alternate authentication method may bypass SAML authentication controls, possibly including SAML-enforced MFA.
- IMPORTANT note: SonicWall PSIRT investigated a report indicating potential exploitation.
- NOTE: the flaw affects SSLVPN only if SAML is enabled for SSLVPN logins.
- CVSS 3.1 score 7.1. CWE-308, use of single-factor authentication.
- Affected: Gen7 7.3.3-7015 and older; Gen8 8.2.2-8015 and older. Fixed: 7.3.4-7013 and higher; 8.2.3-8015 and higher.
- Workaround, added in revision 1.1 on 9 November: if SAML is in use and the firmware cannot be upgraded, disable or delete any active LDAP, RADIUS and TACACS+ authentication servers on the firewall.
- Header: first published 2026-11-06, last updated 2026-11-09. The revision table dates version 1.0 as 05-Nov-2026.

What was wrong in my earlier files:
- source-check-run5-14-nov.md, the Run 5 results note (RESULTS-run5.md) and a comment in run5.py say SonicWall lists no workaround. That was true of the first release and was not true of the page on 14 November. Those files are kept as first written. RESULTS-run5.md has a dated update line added at the end.
- The sources page and catalogue v1.5 said the same. The sources page and catalogue v1.6 now carry the correction.

What did not change: the locked guesses, the W05 model, its results and the sensitivity runs. Control A in the model (every login method except SAML switched off) is close to what SonicWall now describes as the workaround. The vendor names LDAP, RADIUS and TACACS+ servers and does not say what else counts as an alternate method, so the match is close, not exact. The model was written before the vendor listed a workaround, so this is not evidence that the model is right.

Wording for the posts: CISA lists the flaw as exploited. SonicWall's advisory says it investigated a report indicating potential exploitation. Do not write that SonicWall confirmed attacks.
