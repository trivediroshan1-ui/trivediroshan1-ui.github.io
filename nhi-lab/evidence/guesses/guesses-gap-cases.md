# Draft guesses: three gap cases (NHI), written before any code

STATUS: DRAFT until hashed and committed on the Mac. Made-up data only (Kaveri Finance). Each case runs without and with the controls, then each control is switched off alone.

Where these came from: the Vercel and Context.ai report (April 2026) and the CSA blog post of 23 April 2026. Both are secondary sources.

## N-R14-23 Vendor breached, OAuth refresh token still valid
Scenario: an employee linked an AI office app with "allow all" 20 days ago. The vendor is then breached. The attacker replays the refresh token from their own network.
- Without any control: the grant was accepted and the replay reads the employee's files.
- With the tenant app allowlist: the grant is refused at consent, because the app is not on the list.
- With the vendor-breach revoke (revoke within 60 minutes of the notice): if the app was already granted, the replay after minute 60 is refused. A replay at minute 30 still works.
- Control-off check: with the allowlist off, the grant is accepted. With the revoke off, the replay works at any time.
- Limit I expect: an app that is on the allowlist and later breached still works until someone revokes it.

## N-R14-24 Secrets in environment variables not marked sensitive
Scenario: a project has 10 variables. Four are secrets. Two of those are marked sensitive by hand. An attacker with internal read access lists the variables.
- Without the control: the two unmarked secrets are returned in plain text, the two marked ones are hidden.
- With (secrets found by pattern on save, and marked sensitive so the value cannot be read back): I expect three of the four secrets hidden. One secret has a name and value that match no pattern and stays readable. I will record that miss, not hide it.
- Control-off check: switch the pattern marking off. Two secrets become readable again.

## N-R14-25 Credential stolen from a CI runner, replayed minutes later
Scenario: a job runs for 5 minutes with a deploy token. A malicious step copies the token at minute 1. The attacker replays it at minute 3 from another network, and again at minute 8 after the job ended.
- Without controls (long-lived token): both replays work.
- With a 10-minute lifetime only: the replay at minute 3 works, the replay at minute 8 is refused only if the token is also revoked at job end. With lifetime alone, I expect minute 8 to still work, since the lifetime is 10 minutes.
- With the token bound to the runner network and revoked at job end: both replays are refused.
- Control-off check: each control, switched off alone, changes at least one replay result.
- Limit I expect: the stolen token still works from inside the runner during the job.
