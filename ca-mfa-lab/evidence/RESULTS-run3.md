# Run 3 results (14 Nov 2026)

STATUS: DRAFT. Made-up data only (Kaveri Finance). 16 cases, Y01 to Y16.
Guesses: guesses/guesses-run3.md, committed as f8d6676 before any code, sha256 a09daa459851a1d9628d21ceeb51c5fd11bd37c6481b39ec0ab9b2e20205cd98.
Code: run3.py (run from this folder: `python3 run3.py guesses/guesses-run3.md`). Raw output: results-run3.json.

## Score
- 16 of 16 guesses matched on every column (none, all, off A, off B, off C).
- All controls on stopped the bad outcome in 16 of 16.
- At least one single control off let it in: 9 cases (Y01, Y02, Y05, Y06, Y07, Y08, Y12, Y13, Y14).
- No single control off let it in: 7 cases (Y03, Y04, Y09, Y10, Y11, Y15, Y16).
- Every one of those counts matches what I wrote down before running.

## What this score does and does not say
I said I expected 2 to 4 wrong guesses and got none. I read that as a warning about the test, not as a result about the controls. I wrote the models after the guesses, and a model written by the person who guessed will tend to agree with the guess. Run 1 had the same pattern (41 of 41). Run 2 broke it only where the models had to answer a question I had not thought through.
What Run 3 does show is that the reasoning in each case holds together step by step. It does not show how any vendor product behaves. The three cases I trusted least (Y06, Y08, Y10) rest on search excerpts I have not read in full, and the model for each encodes the assumption I made, so a match there proves nothing about the real behaviour.

## Assumptions the results depend on (also in results-run3.json under "assumes")
- Y01: the attacker holds an old session and has no second factor.
- Y03: the second approver is a different, honest person; the alert is a notice and never blocks.
- Y05: a device with unknown state is refused, not waved through.
- Y06: the policy engine skips paths it does not target (not confirmed).
- Y08: the synced passkey path can be driven without the local prompt (not confirmed).
- Y09: the user acts on the alert.
- Y11: the victim declines consent for a client they do not know.
- Y10 and others: one provider fails at a time.

## Extra information (not guessed beforehand, so not scored)
Two controls off together, for the 10 cases with three controls. "in" means the bad outcome happens.
- Y02: in for every pair.
- Y03: A+B out, A+C out, B+C in. The alert (A) adds nothing, but B and C together carry the case.
- Y07: A+B out, A+C in, B+C in. Without the approved-extension rule (C) the other two do not help.
- Y09: A+B in, A+C in, B+C out. With a fresh sign-in required (A) and revoking (B) both off, the alert alone does not stop it.
- Y10: A+B out, A+C in, B+C out.
- Y11: A+B in, A+C out, B+C in.
- Y12: A+B out, A+C in, B+C out.
- Y14: in for every pair.
- Y15: out for every pair, so any one control stops it.
- Y16: A+B in, A+C in, B+C out.

## Not run
E01 to E03 (real tenant logs, a real hardware key, a real help desk call) still need real systems.

## Totals across the lab
105 cases in the register. 102 run (41 + 45 + 16). 3 not run. Wrong guesses: 6, all in Run 2.
