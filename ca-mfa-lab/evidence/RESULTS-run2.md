# CA/MFA lab, Run 2 results (45 cases, 2 to 3 controls each)

STATUS: DRAFT. Guesses committed first: 7d31554 (sha256 f7c8439b...). Code written after; guess values parsed from the committed file.

## Score
- 39 of 45 cases matched every guess. 6 did not: X07, A03, A05, C01, C03, Z21.
- First pass was 38 of 45 (7 mismatches). One was my own mistake: P11. In the first pass my model said approval stops an unauthorised console change. An unauthorised change skips approval by definition, so only the log can show it. I fixed the model and kept the first-pass files (run2-first-pass.py, results-run2-first-pass.json). The other 6 I did not touch.
- All controls on gave "out" in 44 of 45 (guessed 45). The one: A05.
- At least one single control off gave "in" in 35 of 45 (guessed about 33).

## The 6 wrong guesses, sorted the way the NHI lab sorts them
1. **Did not say what I was counting (C01, C03).** I defined the bad outcome as "taken and unnoticed". The change notice (C01) and the exclusion alert (C03) make any takeover noticed, so removing the SMS fallback or the exclusion review alone did not produce the bad outcome. If the bad outcome is only "account taken", both go back to "in". The notice is a detective control. It does not stop the attack.
2. **Controls treated as independent (A05).** Trusting the home tenant's MFA claim means a weak home MFA satisfies the requirement in our tenant, so adding our own guest MFA rule did not help. With the trust on, all controls on still gave "in". This depends on my assumption that the home claim is weak.
3. **Wrong control mattered (Z21).** I said refresh token lifetime (B) does not matter. The bad outcome was "attacker has access at 24 hours", which B decides. Blocking the flow and requiring a compliant device matter for the first hour; B decides the 24 hour question. The pair check (A and C off together) gave "out", not "in".
4. **Did not think through the control's own scope (X07).** With trusted locations limited to the managed office egress, guest wifi is not trusted, so MFA is required and the attacker (who has only the password) is stopped without the device rule.
5. **A convention counted as a control (A03).** Separate admin accounts are a convention, not enforcement. With only separate accounts, nothing stops the admin account from reaching a risky app. With only the group block, the daily account is blocked. I had the two reversed. The result depends on whether you call a convention a control.

## Predictions that held, and what that means
- Each control alone is enough (no single off gives "in"): P03, P10, X01, Z09, Z17, Z21, Z22, C05 all held. X07 and C01 also landed in this group for the reasons above.
- A control that protects nothing without a partner: P02, P05, X02, Z12 held. P05 is the clearest: report-only mode shows nothing about an emergency account that never signs in during the test week.
- Pair checks: C05 (SMS fallback and SIM swap check both off) gave "in". Z22 (registration protection and device rule both off) gave "in". Z21 did not (see item 3).

## Read this before trusting the score
1. Still models I wrote. Several results rest on assumptions I chose and wrote in code comments: the home tenant claim is weak (A05), the reviewer keeps at most 5 exclusions (P03), the log is read within 7 days (P11), 40 percent of users fall for a code lure (Z08). Change an assumption and the result changes.
2. Most single-control "off" checks are meaningful this time, but many cases are still two-path logic (either path open means "in"). That makes "any one control alone is enough" easy to get right.
3. Nothing here tests a real tenant. E01 to E03 are untested.
4. Run 1 and Run 2 together: 86 cases run, 80 matched, 6 wrong guesses (all in Run 2).
