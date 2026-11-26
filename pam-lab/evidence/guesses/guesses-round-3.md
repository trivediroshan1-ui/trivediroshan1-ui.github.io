# Guesses: Privileged access lab, round 3 (the gaps around the lane), written before any code

STATUS: LOCKED when committed (26 Nov 2026). Never edited after the hash is taken; any mistake is disclosed on the results page, not fixed here. Made-up data only (Kaveri Finance). 10 cases, PA-R3-01 to PA-R3-10, all run on models. Approved by Roshan Trivedi on 26 Nov 2026.
Lab name: Privileged access lab: who holds admin, and for how long?
Why this round: round 1 tested the activation lane itself. This round tests the seven gaps the round 1 white paper listed as not covered: help desk recovery, movers and contractors, outside vendors, sub-agents, signing keys with Kubernetes and OT, two insiders together, and session recordings. These are models of rule logic, not of any vendor product, help desk, cluster, PLC or hardware security module.
Words: "none" = all controls off. "all" = all on. "off a" means only control a is off. A control is "noticed" when switching it off alone changes a counted number compared with all controls on.
Format of the table: ID | what is counted (the bad outcome) | none | all | off a | off b | off c. A second line, where present, counts a second outcome the case also predicts.

Lessons from the earlier rounds, applied before I guess:
1. I write down the bad outcome first, so I know what I am counting.
2. A notice, alert, flag or log does not block.
3. I check which control actually decides the question, and whether controls cover for each other. Cases 01, 03, 05 and 08 expect several "not noticed" results for that reason.
4. Where a case needs a rate (a random sample, a masking rate), I fix it as a stated number so the model is deterministic, and say so.

| Gap | Cases |
|---|---|
| 1. Help desk and account recovery for admins | PA-R3-01 |
| 2. Movers who keep eligibility, contractors with no end date | PA-R3-02, PA-R3-03 |
| 3. Third-party vendor access | PA-R3-04 |
| 4. Sub-agents inheriting a parent agent's elevation | PA-R3-05 |
| 5. Signing keys, Kubernetes, OT | PA-R3-06, PA-R3-07, PA-R3-08 |
| 6. Two insiders working together | PA-R3-09 |
| 7. Session recordings and privacy | PA-R3-10 |

## The table

| ID | Counted | none | all | off a | off b | off c |
|---|---|---|---|---|---|---|
| PA-R3-01 | attacker admin activations within 24 hours | 3 | 0 | 0 | 0 | 0 |
| PA-R3-01 | second count: attacker authenticators enrolled | 3 | 0 | 2 | 1 | 0 |
| PA-R3-02 | movers holding eligibility they don't need, 30 days after the move | 4 | 0 | 4 | 0 | 0 |
| PA-R3-02 | second count: movers blocked from work they need | 0 | 0 | 0 | 2 | 0 |
| PA-R3-03 | ended contractors who can still activate admin 30 days after the end | 3 | 0 | 0 | 0 | 0 |
| PA-R3-04 | harmful Tier 0 commands run by the attacker | 1 | 0 | 1 | 0 | 0 |
| PA-R3-05 | sub-agents able to use the parent's database admin rights | 3 | 0 | 3 | 0 | 0 |
| PA-R3-06 | malicious artifacts signed | 2 | 0 | 1 | 1 | 0 |
| PA-R3-06 | second count: days until a malicious signature is found (-1 = never, 0 = none made) | -1 | 0 | 1 | 1 | 0 |
| PA-R3-07 | paths to cluster-admin from a developer's kubeconfig | 3 | 0 | 1 | 2 | 0 |
| PA-R3-08 | attacker writes to the PLC | 1 | 0 | 0 | 0 | 0 |
| PA-R3-08 | second count: urgent plant changes blocked | 0 | 0 | 0 | 1 | 0 |
| PA-R3-09 | collusive grants unnoticed after a week | 4 | 1 | 3 | 3 | 2 |
| PA-R3-10 | recordings with personal data still held after a year | 480 | 30 | 120 | 30 | 120 |
| PA-R3-10 | second count: recording views with no ticket | 6 | 0 | 0 | 6 | 0 |

Joint checks, also predicted:
- PA-R3-01: video check and 24 hour hold both off: 2 attacker activations.
- PA-R3-03: end date rule and vendor feed both off: 1 (a sponsor attests wrongly at day 30).
- PA-R3-08: broker rule and read-only rule both off: 1 attacker write.

## The cases

### PA-R3-01 The help desk resets an admin (gap 1)

Scenario: 10 admin recovery requests in a month. 2 come from attackers who call the help desk with personal details found online. 1 attacker has moved an admin's phone number to a new SIM and uses SMS recovery.

Controls: (a) admin recovery needs a video check against the HR photo and a callback to the manager on a number already on file; (b) no SMS or email recovery for admin accounts; (c) a newly enrolled authenticator can't activate admin for 24 hours, and the account owner and the SOC are told at once.

- Without any control: 3 attacker authenticators enrolled, 3 admin activations.
- With all three: 0 enrolled, 0 activations.
- Control-off checks: switch off the video check and the 2 callers enrol their own authenticators, but the 24 hour hold stops activation and the owner is told. Switch off the SMS ban and the SIM-swap attacker enrols 1, held the same way. Switch off the hold and nothing changes while (a) and (b) stop the enrolment. In the activation count, all three "not noticed"; in the enrolment count, (a) and (b) are noticed.
- Limit I expect: an attacker who also controls the manager's phone, or a deepfake on the video call.
- Where I may be wrong: whether the 24 hour hold is long enough for a real owner to notice.

### PA-R3-02 Movers keep old eligibility (gap 2)

Scenario: 20 people change teams in a quarter. 6 held admin eligibility in the old team; 2 of them need the same role in the new team.

Controls: (a) a mover event removes every eligibility that is not in the new role's model; (b) the new manager re-requests anything still needed, on the day of the move; (c) a quarterly review of eligibility against role.

- Without any control: all 6 keep eligibility; 4 don't need it.
- With all three: 0 unneeded; the 2 who need it are re-approved on the day.
- Control-off checks: switch off the mover rule and the 4 keep it until the quarterly review, so 4 at day 30. Switch off the re-request and the 2 who need the role are blocked until someone notices. Switch off the review and nothing changes at day 30.
- Limit I expect: a role model that is itself too broad.

### PA-R3-03 Contractors with no end date (gap 2)

Scenario: 15 contractors are eligible for admin. 5 contracts end this month. 3 of those 5 accounts have no end date in the identity system.

Controls: (a) every contractor account must carry an end date no later than the contract end; (b) the sponsor attests every 30 days; (c) the vendor management system sends the contract end and the account is disabled that day.

- Without any control: 3 can still activate admin at day 30.
- With all three: 0.
- Control-off checks: each of (a) and (c) alone disables all 5, so switching either off alone changes nothing. The attestation changes nothing while they work. All three "not noticed" alone; (a) and (c) off together leave 1, the one a sponsor attests to without checking.
- Limit I expect: a contractor rehired through a different vendor under a new account.

### PA-R3-04 A vendor's laptop is taken over (gap 3)

Scenario: 4 vendors, 12 sessions a month. One vendor's laptop is taken over, and the attacker uses the vendor's standing VPN account outside any planned session.

Controls: (a) vendors reach targets only through the access broker; no direct VPN accounts; (b) each session needs an approved ticket and lasts at most 2 hours; (c) sessions to Tier 0 targets are recorded and dangerous commands are blocked.

- Without any control: the attacker reaches a Tier 0 target and runs 1 harmful command.
- With all three: 0.
- Control-off checks: switch off the broker rule and the VPN path is open: 1. Noticed. Switch off per-session approval and the attacker opens a broker session, but the command block stops the harmful command: 0. Switch off the command block and the attacker can't get a session without an approved ticket: 0.
- Limit I expect: a harmful action that isn't on the blocked-command list.

### PA-R3-05 A sub-agent inherits the parent's admin (gap 4)

Scenario: a parent agent is elevated to database admin for a migration. It starts 3 sub-agents; one is a third-party summariser that receives the parent's token. One sub-agent tries to start its own sub-agent.

Controls: (a) each sub-agent gets its own identity and a narrower token through token exchange; the parent's token is never passed on; (b) a depth limit of 1; (c) a log naming which agent used each token.

- Without any control: all 3 sub-agents can use database admin.
- With all three: 0.
- Control-off checks: switch off the token rule and the 3 get the parent's token: 3. Noticed. Switch off the depth limit and the grandchild is created, but with its own narrowed token: 0. Switch off the log and nothing changes in the count.
- Limit I expect: a sub-agent that asks the parent to run a command for it. The parent's own rights are then used.

### PA-R3-06 Signing keys (gap 5)

Scenario: a code-signing key signs every release. Two attacks in a quarter: an insider tries to copy the key file, and an attacker changes the build settings on a side branch so that branch's build asks for a signature.

Controls: (a) the key lives in a hardware security module and can't be exported; (b) only builds from the protected main branch can call the signing service; (c) a daily review of the signing log against the release list.

- Without any control: 2 malicious artifacts signed, never found.
- With all three: 0.
- Control-off checks: switch off the hardware module and the insider copies the key and signs 1, found the next day. Switch off the branch rule and the side-branch build is signed, 1, found the next day. Switch off the review and nothing is signed, so nothing changes.
- Limit I expect: a malicious change merged into main through a reviewed pull request.

### PA-R3-07 Kubernetes cluster-admin (gap 5)

Scenario: an attacker holds a developer's kubeconfig. Three paths to cluster-admin exist: a standing cluster-admin binding for an engineer the developer can impersonate, a service account with cluster-admin whose token sits in a pod the developer can read, and a privileged pod the developer can start and escape.

Controls: (a) cluster-admin for people only through just-in-time activation, no standing bindings; (b) no service account holds cluster-admin, and admission policy refuses privileged pods; (c) an alert on exec into system namespaces.

- Without any control: 3 paths.
- With all three: 0.
- Control-off checks: switch off the JIT rule and the standing binding is back: 1. Switch off the service account and admission rule and 2 paths are back. Switch off the alert and nothing changes in the count.
- Limit I expect: a path through a node's own credentials, which none of the three controls covers.

### PA-R3-08 OT access while IT is down (gap 5)

Scenario: ransomware takes down the corporate identity provider and vault for 6 hours. The plant needs one urgent change to a PLC. An attacker inside the IT network tries to reach the same PLC.

Controls: (a) OT access only through a broker in the IT/OT boundary zone, with approval and a time limit; (b) a site-local break-glass account held at the plant, not in the corporate vault; (c) the PLC is read-only from remote sessions; writing needs a second person on site.

- Without any control: the attacker writes to the PLC; the plant is not blocked, because nothing controls access at all.
- With all three: the attacker can't reach the PLC; the plant makes its change through site-local break-glass.
- Control-off checks: switch off the broker rule and the attacker reaches the PLC, but read-only: 0 writes. Switch off site-local break-glass and the broker, which depends on the corporate identity provider, is down: the plant is blocked, 1. Switch off read-only and the broker still keeps the attacker out: 0. With (a) and (c) both off, 1 write.
- Limit I expect: the person on site is the one being tricked.

### PA-R3-09 Two insiders work together (gap 6)

Scenario: 20 Tier 0 requests in a week. Two admins plan to take data and approve each other's requests 4 times.

Controls: (a) no self-approval; (b) the same pair can't approve each other more than twice a month; (c) a third reviewer, picked at random, checks 20% of Tier 0 approvals within 24 hours.

- Without any control: 4 collusive grants, unnoticed.
- With all three: the pair rule stops the third and fourth; the sample catches 1 of the 2 that went through. 1 unnoticed after a week.
- Control-off checks: switch off self-approval and each approves their own: 4 grants, the sample catches 1, so 3 unnoticed. Switch off the pair rule and all 4 go through, the sample catches 1: 3. Switch off the sample and 2 go through unnoticed.
- Limit I expect: a third person joining them. Every rule that looks at one person or one pair misses a group.
- Where I may be wrong: the random sample. To keep the model deterministic, I've fixed it as catching exactly one collusive grant in the week whenever at least one goes through.

### PA-R3-10 Session recordings hold personal data (gap 7)

Scenario: 500 privileged sessions are recorded each month. 40 of them show personal data on screen (HR or customer records). 6 times a year someone watches a recording with no ticket.

Controls: (a) recordings are deleted after 90 days unless under investigation; (b) access to recordings is itself just-in-time, with a ticket, and logged; (c) known personal-data fields are masked automatically in recordings (I assume 30 of 40 a month are caught).

- Without any control: 480 recordings with personal data held after a year; 6 views with no ticket.
- With all three: 30 held at any time (10 unmasked a month for 3 months); 0 untracked views.
- Control-off checks: switch off retention and 10 unmasked a month build up to 120. Switch off JIT access and the holding count doesn't change, but the 6 views happen. Switch off masking and 40 a month for 3 months is 120.
- Limit I expect: personal data that isn't a known field, such as a name typed in a chat window during the session.
- Note: how long recordings may be kept depends on the law that applies (for example GDPR or India's DPDP Act). The 90 days here is a made-up figure, not legal advice.

## What this round can't tell you

- These are small models of rule logic with made-up data. No help desk, vendor, cluster, PLC or HSM is tested.
- Cases 01, 03, 05 and 08 expect controls to cover for each other, so several are "not noticed" alone.
- Case 09 fixes the random sample as a single outcome; case 10 assumes a masking rate. Both are stated assumptions, and the results page will show what changes if they move.
- Still not covered by any round: customer identity, passwordless rollout for people who aren't admins, and the legal answer on recording retention.
