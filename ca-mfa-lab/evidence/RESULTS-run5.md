# Run 5 results (14 Nov 2026)

STATUS: DRAFT, not on the site yet. Made-up data. Models of rule logic, not of any vendor product.
Guesses: `guesses/guesses-run5.md`, merged as b184994, SHA-256 bc344bbd00d01d169c0dbde94d83fc628ec973dcbbb067d1c2cad3f74a65e63a. The script checks that hash before it runs.
Models: `run5.py`, written after the guesses. Output: `results-run5.json`.

## Score

12 of 12 cases match my guesses (60 of 60 cells). All on is out in 12 of 12. One control off lets the bad outcome in for 9 cases (W01, W04, W06, W07, W08, W09, W10, W11, W12). No single control off lets it in for 3 cases (W02, W03, W05).

This is the same weakness as Runs 1 and 3. I wrote the models after the guesses, so a perfect score shows the models and my reasoning agree, not that the guesses were tested against something outside me. Run 2 was the only run that caught me out (6 wrong guesses in 45). The more useful result in this run is the table below: what happens when one assumption changes.

## Results

| ID | none | all | off A | off B | off C | Deciding control |
|---|---|---|---|---|---|---|
| W01 | in | out | in | out | out | A (trust pinned to repository and branch) |
| W02 | in | out | out | out | out | A or C alone is enough |
| W03 | in | out | out | out | out | any one of A, B, C breaks the chain |
| W04 | in | out | in | in | in | all three, three different paths |
| W05 | in | out | out | out | out | A or B alone; C is an alert |
| W06 | in | out | out | in | out | B (address allow-list); MFA plays no part |
| W07 | in | out | in | out | out | A (reset revokes refresh tokens) |
| W08 | in | out | in | in | in | all three, three different paths |
| W09 | in | out | in | out | out | A (token bound to the client) |
| W10 | in | out | in | out | out | A (narrow token per task) |
| W11 | in | out | in | out | out | A (allow-list of authorization servers) |
| W12 | in | out | in | in | out | A and B, two paths into enrolment |

## What changes the answer

I changed one assumption at a time and re-ran. These are the only changes that flip a result.

- **People read less carefully (30 percent to 60 percent):** no change. **People read almost always (2 percent):** W10 and W11 flip. A person who always reads makes "a person approves every write" and "the user checks the sign-in address" enough on their own, so off A is then out. The result depends on a human habit, not a control.
- **Cloud session lasts 25 hours instead of 1 (W02):** off A now lets the bad outcome in. Short-lived tokens only help if they are short.
- **Attacker replays the token after 10 minutes, not 2 (W09):** off A flips to out, because the 5-minute token has already ended. The 5-minute lifetime only protects against an attacker who is slow.
- **The step-up check also applies to API keys and service tokens (W08):** off A and off C flip to out. My model assumes the check applies to user tokens only, because keys and client-credentials tokens carry no step-up claim. A gateway that applies it to every credential closes two of the three paths.

## Notes on specific cases

- W05: SonicWall lists no workaround for CVE-2026-19868. Control A (switch off every other login method) is my own mitigation, not a vendor-supported one. The model treats it as removing the path, as the advisory describes the flaw.
- W06 and W08: neither is decided by MFA. W06 is decided by where the token can be used from, W08 by whether the API enforces step-up on every credential type.
- W09: binding the token to the client stops replay from another machine. It does not stop code running inside the compromised client (RFC 9449 says so).
- W11: the issuer check passes when the attacker's own server names itself as the issuer, so B does nothing here (MCP authorization spec, 2026-07-28 text).

## Limits

- The scores are not independent of me. The models encode my reading of each case.
- W05 and W11 still carry (verify): the SonicWall page itself and the research notes on the MCP SDK flaw were not read in full.
- Every attacker behaviour (the 2-minute delay, the 1-hour session, the 30 percent) is an assumption I chose. The sensitivity list above shows which ones matter.
