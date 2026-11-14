# CA/MFA lab, Run 1 results (41 cases)

STATUS: DRAFT. Guesses committed first: 5875323 (branch ca-mfa-lab-run1, sha256 2675a0ef...). Code written after.

## Score
- First pass: 39 of 41 matched, 2 mismatched (S06, Z01).
- Both mismatches were mistakes in my test code, not wrong guesses:
  - S06: the registered redirect address ended in /cb, so the attacker address could not match by prefix. Test data was bad. Fixed by registering the origin only.
  - Z01: I forgot to mark it as a limit case, although the committed guess file lists it as one.
- After the two fixes: 41 of 41 matched. First-pass files are kept (run1-first-pass.py, results-run1-first-pass.json).
- Counts guessed vs found: control fully stops the case, guessed about 28, found 31 of 41; limit cases, guessed 10, found 10 (the same 10 IDs). The guess of 'about 28' was 3 low because I expected 3 surprises and the models produced none.

## Read this before trusting the score
1. The models are small rules I wrote knowing my own guesses. A match shows my guesses and my models agree with each other. It does not show the real world behaves that way. The NHI lab had 10 wrong guesses in 67 cases mostly because the models contained things I had not thought of. This run found none, which says the cases were too simple, not that I was right.
2. For single-control cases, "control off alone" is the same as "no control" (35 of 41 cases). That column adds nothing there. Real interaction tests need two controls in one case.
3. Limit predictions were only testable in 10 cases that have an edge parameter (skew, overlap, delay, lifetime). For the other 31 the limit was not tested.
4. Z01 "off" means a phishing-resistant factor, and M04, M05, M06 use the method's default as "none". Those guesses were worded loosely.
5. The 'partial' and 'detected' outcomes (Z01, S10) are modelled with fixed numbers (70 percent of users resist; thief's first use succeeds). Those numbers are my assumptions.

## What to do next
- Run 2 needs two or more interacting controls per case so the control-off check means something. I will design it that way and write guesses first.
- Real-world checks (vendor behaviour, real tenant) remain the 3 E rows, not run.
