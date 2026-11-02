# Draft guesses: 13 stretch cases and 6 chain tests (NHI and PAM), written before any code

STATUS: DRAFT until hashed and committed on the Mac. Made-up data only (Kaveri Finance). Each case runs without and with the controls, then each control is switched off alone. These are my expectations. Some will be wrong, and I will record that.

## Stretch cases

### N-R14-07 One identity, three names
Scenario: the same service account appears as `svc-billing` in the directory, `billing-svc@kaveri` in the cloud and `BILLING_SVC` in the vault. 30 identities, 9 of them appear under two or three names.
- Without matching: 30 are counted as 51 separate identities and 9 real findings are split in two.
- With matching on owner plus normalised name: I expect 9 of 9 merged and the count back to 30. I expect one wrong merge when two different accounts share an owner and a similar name. I will record it.
- Control-off check: switch off owner matching and the count rises again.

### N-R14-19 Scoring: top gets fixed first
Scenario: two identities with the same age score, one reaches production data and one reaches a test tool.
- Without reach in the score: they tie and the test tool can be fixed first.
- With reach added: the production one ranks first in every run.
- Control-off check: remove reach and the tie returns.

### N-R14-20 Close only when the old secret is dead
Scenario: a rotation ticket for 5 secrets. Two old secrets are still accepted by the target.
- Without verification: all 5 tickets close, 2 old secrets live on.
- With a check that the old secret is refused: 3 close and 2 stay open.
- Control-off check: switch the check off and all 5 close again.

### N-R14-21 Agent shares a team credential
Scenario: 4 agents use one shared key. One agent misbehaves.
- Without per-agent keys: the log shows only "team key" and the key must be revoked for all 4.
- With one key per agent: the log names the agent and only that key is revoked.
- Control-off check: go back to one key and the log cannot name the agent.

### N-R14-22 A person logs in with a service account
Scenario: an engineer signs in interactively with a service account to fix a problem.
- Without control: the action is logged under the service account and nobody is accountable.
- With interactive sign-in blocked for service accounts and a checkout with a ticket: the direct sign-in is refused and the checkout names the person.
- Limit I expect: if the person copies the password during a checkout and uses it from another tool, the control does not see it.

### P-R15-10 Phishing-resistant MFA for admins
Scenario: 10 admin sign-in attempts: 4 genuine, 4 push-fatigue prompts accepted by a tired admin, 2 SIM-swap codes.
- Without phishing-resistant MFA (push and SMS only): the 4 fatigue prompts and 2 SIM-swap codes succeed. 6 bad sign-ins get through.
- With a hardware-bound passkey: all 6 refused, all 4 genuine accepted.
- Control-off check: allow SMS as a fallback and the SIM-swap ones get through again.

### P-R15-15 The vault, its backups and who can read them
Scenario: the vault backup is on a share with weaker rules. 6 accounts try to read it, 1 is the backup job.
- Without same controls on the backup: 5 non-backup reads succeed.
- With the same rules and an alert on non-backup reads: 5 refused and 5 alerts.
- Control-off check: switch off the alert and the 5 refusals stay but nobody is told.

### P-R15-16 Help desk reset path
Scenario: 6 reset requests for admin accounts, 2 from an attacker using a known name and phone number.
- Without strong proof: both attacker resets succeed.
- With proof of identity plus a notice to the person and a 1-hour delay for admins: both refused or caught in the delay.
- Limit I expect: a real person who is also tricked into approving the notice still loses the account.

### P-R15-19 A vendor is needed at 2 a.m.
Scenario: a vendor engineer needs access for an emergency.
- Without a process: the access is given by a shared password and stays on.
- With a time-limited, recorded session approved by the on-call manager: the access closes by itself at 2 hours, with a recording.
- Control-off check: switch off the expiry and the access stays on.

### P-R15-25 Mass rotation after a breach
Scenario: 200 secrets must be rotated. 12 consumers fail if rotated before their app is updated.
- Without ordering: 12 outages.
- With consumers-first ordering and a dry run: 0 outages, 2 secrets left unrotated for lack of an owner. I expect those 2 and will record them.
- Control-off check: remove the ordering and the 12 outages return.

### S-R17-02 AI tool inherits full permissions
Scenario: an AI tool needs to read one folder, but inherits the person's write access to 40 folders.
- Without scoping: the tool can write to all 40.
- With scope limited to read on one folder: 1 readable, 0 writable.
- Control-off check: remove the scope and 40 writable return.

### S-R17-06 AI-service API keys leak into repositories
Scenario: 6 AI-service keys appear in 6 repositories. 2 are older than 90 days.
- Without scanning and rotation: all 6 stay valid.
- With scan, revoke on find and 90-day rotation: 5 revoked on find, 1 missed because its prefix is non-standard. I expect that miss.
- Control-off check: switch off the scan and the rotation catches only the 2 old ones.

### S-R17-10 Scheduled automations outlive the test window
Scenario: 5 scheduled workflows were created for a test that ended 30 days ago.
- Without expiry: all 5 still run.
- With an end date set at creation and a sweep: 4 disabled and 1 kept because someone extended it with a reason. I expect one extension to be accepted.
- Control-off check: switch off the sweep and all 5 keep running.

## Chain tests (round 16)

Each chain runs with no controls, then with one control per link, then with each control switched off alone, to see which link matters most.

### C-R16-C01 The forgotten service account
Chain: no owner, password never rotated, copied to a ticket, ticket export shared, sign-in from a new network.
- No controls: the attacker signs in.
- All controls: stopped at the first link (owner required).
- I expect the single most useful control is the secret scan on tickets, because the first link is only a symptom.

### C-R16-C02 The token in the repository
Chain: token committed, repo cloned, scanner finds it, attacker calls the cloud API.
- No controls: the attacker reads secrets.
- With the commit block: stopped at link 1. With only short-lived tokens: the token has expired by the time it is found, 7 days later.
- I expect short-lived tokens alone stop the chain when the finder is slower than the lifetime.

### C-R16-C04 The contractor who never left
Chain: no end date, contract ends in agency records, account stays, phished credential used.
- No controls: access to production.
- With the end date control only: account closes. With the sponsor review only: closes at the next review, up to 90 days late.
- I expect expiry alone to be enough and the sponsor review to leave a window.

### C-R16-C05 The break-glass password everyone knows
Chain: used in an incident, pasted in chat, not rotated, reused with no emergency.
- No controls: the reuse is unnoticed.
- With alert on every use: caught at link 4. With rotate on return only: the pasted password no longer works, so link 4 fails.
- I expect rotate-on-return to be the stronger single control.

### C-R16-C06 Approval fatigue
Chain: many approvals a day, one-click approving, a hostile request hidden among routine ones, change approved.
- No controls: the hostile change passes.
- With a second approver for high-risk requests: stopped. With risk shown first but no second approver: I expect the tired approver still approves it.
- I expect the second approver to be the one that matters.

### C-R16-C17 The old door
Chain: vault in place, direct login still works, old password known, vault bypassed.
- No controls: bypassed and nothing recorded.
- With the direct-login block: stopped. With only a vault check-in alert: not stopped, only noticed after.
- I expect the block to stop it and the alert only to report it.
