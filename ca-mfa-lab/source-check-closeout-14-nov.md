STATUS: DRAFT. Follow-up to source-check-run5-14-nov.md. 14 November 2026.

Seven register rows were re-checked. The catalogue moves to v1.5; v1.4 is kept as published. Only the source, source_check and source_note columns changed, for these rows: M06, Z20, Y06, Y10, W01, W05, W11. No guess, model or result changed.

How each source was read: "fetch summary" means the page was fetched and summarised by a tool, not read line by line by me. "Excerpt" means search result text only.

| Row | Before | After | What was read | How |
|---|---|---|---|---|
| W01 | Confirmed | Confirmed | GitHub Docs OIDC reference. Repositories created after 15 July 2026 get the immutable subject (owner and repository IDs) by default; older ones can opt in; renames and transfers after that date also move. Not on GitHub Enterprise Server. | fetch summary, live page |
| W05 | Confirmed with a qualifier | Confirmed with a qualifier | SonicWall advisory SNWLID-2026-0014 as quoted by several outlets, CISA KEV. SonicWall's own page was not opened: the request needed approval and was not answered. One outlet quoting the advisory says SonicWall investigated reports of potential exploitation; CISA lists it as exploited. | excerpts |
| W11 | Partly confirmed | Confirmed with a qualifier | MCP Python SDK advisory GHSA-qx49-fqc8-xw99 (28 Sep 2026, CVSS 7.5) through the CSA note, The Hacker News, WorkOS and others. GitHub advisory not opened. No attacks reported. | excerpts |
| M06 | Open | Confirmed with a qualifier | NIST SP 800-63B-4 Appendix B. It does not directly cover losing one device. Table 5 covers recovery, binding several authenticators at AAL2 and above, and AAL2 to add authenticators. Not usable at AAL3. The one-device-loss behaviour is my model. FIDO Alliance not read. | fetch summary |
| Z20 | Partly confirmed | Confirmed | Exchange Team blog of 27 Jan 2026 (updated 29 Jan). Unchanged until December 2026; end of December 2026 disabled by default for existing tenants, unavailable by default for new ones; final removal date to be announced in the second half of 2027. | fetch summary |
| Y06 | Partly confirmed | Confirmed with a qualifier | NetSPI reported to Microsoft on 17 Mar 2026, rated medium, fixed; retest shows blocking errors. Further nested app paths were presented at TROOPERS 2026. Microsoft's own statement not read. | excerpts |
| Y10 | Confirmed with a qualifier | Confirmed with a qualifier | Duo release notes and FAQ: Windows Logon defaults to fail closed from 4.3.0; Legacy AD Protection fails open by default; a Duo blog describes a customer proxy set to fail open. | excerpts |

Sources page: added the MCP Python SDK advisory (28 Sep 2026), the NetSPI finding (reported 17 Mar 2026) and the Exchange timeline (27 Jan 2026). Corrected the GitHub row. Now 11 dated events.

Still open: SonicWall's own advisory page; GitHub advisory for the Python SDK; Microsoft's own statement for Y06; the FIDO Alliance text for M06.

Disclosure for the sources page: the MCP project was created by Anthropic, whose Claude model helped draft this lab. Roshan decides whether that line stays.
