# Run 6 results: AI agent identity (14 Nov 2026)

STATUS: DRAFT until merged. Made-up data. Models of rule logic, not of any vendor product.
Guesses: `guesses/guesses-run6.md`, merged as d7183d5 (pull request #110), SHA-256 1abdbf110b58375570d3472f3aefc697b41931f236a53001c1f9d836f01ec22f. The script checks that hash before it runs.
Models: `run6.py`, written after the guesses. Output: `results-run6.json`.
Sources read before the guesses: Okta's Agent SSO press release (24 Aug 2026) and the Cloud Security Alliance paper "Defining Non-Human Identity" (22 Jul 2026). The rest were search excerpts.

## Score

10 of 10 cases match my guesses (50 of 50 cells). All on is out in 10 of 10. One control off lets the bad outcome in for 6 cases (G01, G02, G03, G04, G05, G10). No single control off lets it in for 4 (G06, G07, G08, G09).

Same weakness as Runs 1, 3 and 5: I wrote the models after the guesses, so the score shows that my models and my reasoning agree, nothing more. The assumption tests below are the useful part.

## Results

| ID | none | all | off A | off B | off C | Deciding control |
|---|---|---|---|---|---|---|
| G01 | in | out | out | out | in | C (the grant is re-checked on every exchange) |
| G02 | in | out | in | out | out | A (act only on the account the human named) |
| G03 | in | out | out | out | in | C (the resource checks the human's own permissions) |
| G04 | in | out | in | out | out | A (identity expires with the project) |
| G05 | in | out | in | in | out | A and B together (sponsor recorded, and leaving triggers action) |
| G06 | in | out | out | out | out | any one of A, B, C |
| G07 | in | out | out | out | out | A or C |
| G08 | in | out | out | out | out | B alone, or A and C together |
| G09 | in | out | out | out | out | A or B |
| G10 | in | out | in | out | in | A and C (the human in the token, and logs kept long enough) |

## What changes the answer

I changed one assumption at a time and re-ran. Six of the seven changes flip a result.

- **People almost always read the confirmation (2 percent confirm blindly, not 30):** G02 off A flips to out. The confirmation step works only as well as the person reading it.
- **The parent agent acts with the human's own token, not its own identity:** G03 flips to out in every column, including none. The whole problem in G03 comes from the orchestrator holding broader rights than the human. Remove that and narrowing is enough.
- **Monthly access review instead of quarterly:** G04 off A flips to out. A review only helps if it comes round faster than the window you care about.
- **The attacker replays the cookie through a proxy on the victim's network:** G07 off C flips to in. Continuous evaluation that watches the network does not see an attacker who looks local. Binding the session to the device still holds.
- **Secret scanning does not read build logs:** G09 off A flips to in. Scanning helps only where it looks.
- **Logs kept 45 days without the 90-day setting:** G10 off C flips to out. The question was asked on day 30, so any retention past 30 days is enough.
- **Second-app tokens last 90 minutes:** no change. At one hour after revocation, G01 is decided by whether the cached assertion is re-checked, not by how long the old token lives.

## Notes on specific cases

- G01: Okta's release says Agent SSO issues short-lived tokens and moves agent authorization to the identity provider. It does not describe what happens on revocation. My model of two paths (the token already issued, and a new token from a cached assertion) is my own and stays (verify). E04 asks someone with a tenant to test it.
- G03 and G10 follow the Cloud Security Alliance advice to limit delegated actions to the human's own permissions and to log the delegator, the agent and the intent. CSA lists six risk areas for all non-human identities and names impersonation, excessive action authority, scope creep, multi-step chaining and incomplete audit attribution as agent-specific.
- G04 and G05 are the two I expect people to argue with. Rotation keeps an unused agent working, and a flag on an ownerless agent does not remove it.
- G08 rests on an IETF draft I read only through a vendor summary. (verify)
- E04, E05 and E06 are hand tests for people with a test tenant. They are not counted as run.

## Totals after Run 6

130 cases in the register. 124 run on models (41 + 45 + 16 + 12 + 10). 6 hand tests not run (E01 to E06). Wrong guesses: 6, all in Run 2.
