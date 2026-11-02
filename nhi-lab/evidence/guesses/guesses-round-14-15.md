# Draft guesses: rounds 14 (NHI) and 15 (PAM), the 20 "must" cases

STATUS: DRAFT. Not hashed, not committed. These are my predictions, written before any code exists. You change anything you disagree with. Then the file is hashed (SHA-256) and committed on your Mac before I write the code. Made-up data only (Kaveri Finance).

Each case has two runs: **without** the control and **with** it. "Noticed" means a check fails when the control is switched off.

## Round 14: non-human identity

**N-R14-01 Inventory misses a source.** Three sources hold service accounts: the directory (12), the cloud (9) and CI settings (6). A scan of the directory alone is run.
- Without the control (directory only): finds 12 of 27. The 15 others are missed, including every CI identity.
- With the control (all three sources merged): finds all 27, and reports which source each came from.

**N-R14-03 Long-lived CI variable.** A pipeline holds a cloud key that is 400 days old. A job from another project on the same runner reads the variable.
- Without: the other job reads it and deploys. The log shows only "pipeline".
- With (per-job scoped credential): the other job gets nothing. The log names the job that asked.

**N-R14-04 Certificate with no owner expires.** A certificate expires at midnight. The expiry is 30 days away in the inventory, with no owner on record.
- Without: no warning. Service stops. An engineer turns off a check to bring it back.
- With (owner required, expiry alert at 30 and 7 days): owner is warned twice. No outage, no check switched off.

**N-R14-05 Old OAuth grant, vendor breached.** A vendor app was granted wide read access 14 months ago and was last used 11 months ago. The vendor's tokens are then reported stolen.
- Without a review: the grant is still live. Replayed token reads mail.
- With (consent review and expiry at 90 days): the grant has already expired. Replayed token is refused.

**N-R14-09 No owner.** A key is found with no named owner.
- Without a rule: it stays in the list, and its score is raised by the ownership gap. Nothing else happens.
- With (owner required within 30 days, then the identity is paused): it is paused on day 31.

**N-R14-11 Application retired, identities remain.** An application is retired. Its service account, key and database user stay active.
- Without: all three still work 90 days later.
- With (retire before rotate, owner attestation): all three are disabled and a ticket records it. Limit: an attestation can be signed without being true.

**N-R14-14 Rotation fails silently.** A rotation job fails for one account for 60 days.
- Without an alert: the password is 60 days older than policy and nobody knows.
- With (alert on failure plus staleness in the score): alert on day one. The account's score rises each week.

**N-R14-15 Rotate before the consumer is updated.** A database password is rotated. The application still holds the old one.
- Without an order rule: the application fails at the next connection.
- With (update the consumer first, rotate second, verify the old one is dead): no failure. Limit: it depends on the list of consumers being complete.

**N-R14-17 Loose federation trust.** A cloud role trusts any workload in one account. A low-value workload asks for the high-value role.
- Without a narrow condition: it gets the role.
- With (trust bound to one named workload): refused.

**N-R14-18 Front door.** A developer creates a new service account with no owner, no scope and no expiry.
- Without a front door rule: created and active.
- With (owner, scope and expiry required): refused with a reason.

## Round 15: privileged access

**P-R15-02 Just-in-time window.** An engineer asks for 2 hours on one database with an open ticket.
- Without a time limit: access stays after the work.
- With (window of 2 hours, closes by itself, credential rotated): access is gone at the end.

**P-R15-03 Work runs past the window.** The job needs 90 more minutes.
- Without a limit on extensions: extended again and again. After four extensions it is open all day.
- With (one extension, then a new approval): one extension is allowed, the next needs a person.

**P-R15-05 Standing group membership.** An admin group has 40 members. Eight did privileged work last month.
- Without a review: 40 still have access.
- With (time-boxed access and removal of unused membership): 32 are removed. Limit: 8 may still be broader than needed.

**P-R15-07 Direct login still open.** The vault is in place. An engineer uses an old password to sign in directly.
- Without a block: login works. No recording.
- With (direct login blocked at the network): refused.

**P-R15-08 Recording gap.** Sessions to nine of ten targets are recorded. The tenth is not.
- Without a coverage check: nobody knows. Work on the tenth leaves no record.
- With (coverage report and block when recording is off): the tenth is found and blocked.

**P-R15-09 Two approvers for Tier 0.** A request to change the identity system is approved by one person.
- Without a second approver: runs.
- With (two named approvers, neither the requester): waits for the second. If both are the same person, refused.

**P-R15-11 Break-glass used at 2 a.m.** The sign-in service is down. The break-glass account is used.
- Without an alert or rotation: the use is unnoticed and the password stays the same.
- With (alert on use, justification within 24 hours, rotate on return): alert fires, password changed. Limit: the justification can still be a lie.

**P-R15-13 Break-glass becomes a side door.** The break-glass account is used for routine work on four days in a month.
- Without a review: no one notices.
- With (monthly use report, uses with no incident ticket flagged): flagged. Limit: a ticket number can be made up.

**P-R15-17 Vendor session.** A vendor engineer connects for a slow query. The sponsor approved 4 hours.
- Without recording and expiry: no record. Access stays after 4 hours.
- With (broker, recording, closes at 4 hours): recorded and closed.

**P-R15-18 Vendor person leaves the vendor.** A vendor engineer leaves their company. Their account on your side is still active.
- Without a periodic check: still active at 120 days.
- With (sponsor review every 30 days and an end date): disabled at the next review at the latest.

## Round 16: chains (stretch)

Each chain is run with every control on, then with one control off at a time. The guess is where the chain stops.

- **C01 Forgotten service account:** with all controls on, the chain stops at the owner rule. With the owner rule off, it stops at rotation. With both off, it reaches "sign-in from a new network with valid credentials".
- **C02 Token in a repository:** stops at the commit block. With it off, stops at short token life. With both off, the token works from the attacker's network.
- **C04 Contractor who never left:** stops at the end date. With it off, stops at the sponsor review. With both off, the account is active and usable.
- **C05 Break-glass password everyone knows:** stops at the alert. With it off, stops at rotation. With both off, a shared admin account is used with no name.
- **C06 Approval fatigue:** stops at the batch limit. With it off, stops at the second approver for high risk. With both off, the hostile request is approved.
- **C17 The old door:** stops at the network block. With it off, there is no recording. The login works.

## What these guesses assume

- I wrote both the guesses and, later, the code, so a match proves little. A mismatch is more interesting.
- Several "with" results are probably too easy. Tell me which ones you think are.
- Limits are marked where I expect a control to fall short.
