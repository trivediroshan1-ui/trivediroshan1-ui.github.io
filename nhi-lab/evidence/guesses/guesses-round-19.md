# Guesses, round 19: the queued cases

Written before any code. Made-up data only (Kaveri Finance). Each case runs without the controls, then with them, then each control is switched off alone. These are my expectations. Wrong ones will be recorded next to the right answer.

This round runs the 19 cases that were queued in the catalogue and never run. Two queued cases are not repeated: N-R14-08 (test credentials that work in production) and N-R14-23 (one identity across dev, test, staging and production) are covered by N-R18-02.

## N-R14-02 Secrets in code, config, chat and tickets

Scenario: 20 fake secrets are planted. 8 in repository files (one split over two lines, one in base64), 4 in config files, 4 in a chat export, 4 in tickets (one only in an attached screenshot).

Controls: (a) a scan of repositories and config; (b) a scan of chat; (c) a scan of tickets.

- Without any control: 0 found, all 20 stay live.
- With all three: 17 found, 3 missed (the split secret, the base64 one, the screenshot).
- Control-off checks: each scan covers a different place, so switching any one off lowers the count. I expect all three to be noticed: repo and config off gives 7 found, chat off gives 13, tickets off gives 14.
- Limit I expect: a secret inside an image or an attachment is not seen by any scan.
- Where I may be wrong: the number missed in repositories.

## N-R14-06 An identity created outside the normal process

Scenario: 10 service accounts are created in a month. 7 go through the front door (owner, scope, expiry). 3 are created straight in the cloud console by developers to unblock a release.

Controls: (a) a cloud policy that refuses creation outside the front door; (b) a weekly sweep that opens a ticket for any account with no owner tag; (c) automatic expiry of an untagged account after 14 days.

- Without any control: 10 exist, 3 have no owner and no expiry.
- With all three: the 3 console creations are refused. 0 ownerless accounts.
- Control-off checks: switch off the policy and the 3 are created, found by the sweep on day 7 and removed by the expiry on day 14. Switch off the sweep and nothing changes, because the policy already refuses them. I expect the sweep to be reported as "not noticed". Switch off the expiry and nothing changes either, for the same reason. I expect it to be "not noticed" too.
- Limit I expect: an administrator can create an account with a tag that names an owner who does not know about it. The tag passes every check.

## N-R14-10 The owning team is disbanded

Scenario: 12 service accounts are owned by a team called Payments Ops. The team is disbanded on day 0.

Controls: (a) a disband event moves the team's identities to an orphan queue; (b) the queue has a 14 day limit, after which an unclaimed identity is paused; (c) a quarterly attestation.

- Without any control: all 12 still show the old team as owner and stay active at day 90. Nobody answers for them.
- With all three: 12 go to the queue on day 0. 9 are claimed within 14 days. 3 are paused on day 14.
- One of the 3 paused identities is used by a weekly job, so 1 outage on day 14 or 15.
- Control-off checks: switch off the queue and the 12 stay active, so it is noticed. Switch off the 14 day limit and the 3 stay active, noticed. Switch off the attestation and nothing changes in the first 90 days. I expect "not noticed".
- Limit I expect: a team mailing list that nobody reads counts as an owner.

## N-R14-12 Overprivileged identities

Scenario: 15 service accounts hold 120 permissions in total. Over 90 days only 38 are used.

Controls: (a) a right-sizing report based on use; (b) a person approves each change before it is applied; (c) a rule that refuses wildcard grants on new accounts.

- Without any control: 120 permissions stay. 82 are unused.
- With all three: permissions fall to 44 (the 38 used plus 6 kept as buffer). 76 are removed.
- 1 removal breaks a quarterly job, because 90 days of use did not include it.
- Control-off checks: switch off the report and nothing is removed, so it is noticed. Switch off the approval and the changes still apply, so I expect "not noticed" in the counts. Switch off the wildcard rule and new accounts can again be granted wildcards: 2 test grants succeed.
- Limit I expect: use data over 90 days cannot see an annual job.

## N-R14-13 Rotation on a schedule

Scenario: 20 secrets are due for rotation. 3 of their consumers cache the secret for up to an hour.

Controls: (a) a rotation schedule; (b) two secrets valid at once during a 2 hour overlap; (c) a check that the old secret is dead after the overlap.

- Without any control: 20 secrets average 400 days old. 0 outages.
- With all three: all 20 rotated. 0 outages. The old secrets are refused after 2 hours.
- Control-off checks: switch off the overlap and the 3 caching consumers fail, so 3 outages. Switch off the dead-secret check and the 20 old secrets stay valid, noticed. Switch off the schedule and nothing rotates, noticed.
- Limit I expect: a consumer that caches for longer than the overlap still fails.

## N-R14-16 Retire before you rotate

Scenario: 30 identities are due for rotation. 12 have not been used for 90 days or more. 1 of those 12 is used by a quarterly job.

Controls: (a) a use check; (b) disable first and hold for 30 days; (c) delete after the hold.

- Without any control: 30 rotations.
- With all three: 12 are disabled, 18 rotated. The quarterly job breaks once in the hold period and the identity is switched back on. 1 outage, no permanent loss.
- Control-off checks: switch off the hold and the 12 are deleted at once. The quarterly job breaks and the identity is gone. That is 1 permanent loss. Noticed. Switch off the use check and all 30 are rotated, noticed. Switch off the delete and the 12 stay disabled forever, which does not change the counts. I expect "not noticed".
- Limit I expect: the use logs miss 2 identities that log in through an older route.

## P-R15-01 Request privileged access with a ticket and an end time

Scenario: 10 requests. 6 are valid. 2 name a closed ticket. 1 has no end time. 1 asks for a Tier 0 system without a second approver.

Controls: (a) the ticket must be open; (b) an end time is required, 8 hours at most; (c) Tier 0 needs a second approver.

- Without any control: all 10 granted.
- With all three: 6 granted, 4 refused.
- Control-off checks: switch off the ticket check and the 2 closed tickets are granted. Switch off the end time rule and the request with no end is granted. Switch off the second approver and the Tier 0 request is granted. I expect all three to be noticed.
- Extra scenario: a request names a ticket that is open but belongs to another system. I expect it to be accepted, because the check only asks whether the ticket is open.
- Limit I expect: nothing checks that the ticket matches the task.

## P-R15-04 The elevation path is down

Scenario: the just in time broker is down for 2 hours. 5 engineers need access to fix an incident.

Controls: (a) a second broker node; (b) a break-glass fallback with an alert; (c) a review of every fallback use.

- Without any control: all 5 are blocked, and 3 use a shared admin password that nobody logs.
- With all three: 0 blocked, 0 alerts, because the second node takes over.
- Control-off checks: switch off the second node and all 5 use break-glass, giving 5 alerts and 5 reviews. Switch off both the second node and break-glass and the 5 are blocked, with 3 using the shared password. Switch off the review alone and nothing changes while the second node is up. I expect "not noticed".
- Limit I expect: both nodes fail for the same reason, such as a shared database, and the second node does not help.

## P-R15-06 The person never sees the password

Scenario: 10 privileged sessions go through a broker. 2 users try to reveal the password in the console. 3 users later try to log in directly with a password they remember.

Controls: (a) the broker injects the credential and never shows it; (b) the reveal button is disabled by policy; (c) the password is rotated after each session.

- Without any control: 10 sessions work, 2 users see the password, and 3 direct logins succeed.
- With all three: 0 reveals, 3 direct logins refused.
- Control-off checks: switch off the injection and the 2 reveals succeed, but rotation still refuses the 3 direct logins. Switch off the rotation alone and no password was shown, so the 3 logins still fail. I expect the rotation to be "not noticed" and the reveal policy to be "not noticed" as well, because each covers the other.
- Limit I expect: a screen recording or a keylogger on the user's own machine, and the credential held in memory on the target.

## P-R15-12 The break-glass drill

Scenario: a quarterly drill with 4 steps: the alert fires, an on-call person acknowledges within 15 minutes, the sealed copy is found, and the password is rotated afterwards. Two faults are planted: the alert still goes to a person who left, and the sealed copy is with a person on leave.

Controls: (a) alert routing checked against the current on-call list; (b) two holders for the sealed copy; (c) the drill itself.

- Without any control: the drill is not run. 0 faults found for the next 6 months.
- With all three: the drill finds 2 faults and fixes both. 4 of 4 steps pass on the second run.
- Control-off checks: switch off the routing check and the drill still finds the alert fault, but only because it ran. Switch off the second holder and the sealed copy step fails once. Switch off the drill and nothing finds either fault. I expect all three to be noticed.
- Limit I expect: the drill is announced, so people behave better than they would on a real night.

## P-R15-14 Shared accounts: who did what

Scenario: one shared firewall account is used by 4 people. 12 actions in a day. 2 sessions overlap.

Controls: (a) check-out names the person; (b) the session log tags the person; (c) the password is changed after each check-out.

- Without any control: the log says "fw-admin" 12 times. Who did what is unknown.
- With all three: 12 actions, each tied to a person. 4 password changes.
- Control-off checks: switch off the tag in the log and 10 of 12 are tied to a person by time window. The 2 in the overlap are ambiguous. Switch off the password change and attribution is unchanged. I expect "not noticed" in the attribution count, though one person can still log in after check-out. Switch off check-out and no one is named at all.
- Limit I expect: a person hands their session to a colleague.

## P-R15-20 Discover privileged accounts and assign owners

Scenario: 38 privileged accounts across 5 places: directory (14), local administrators on servers (6), cloud roles (9), database administrators (5), network devices (4). The current inventory covers the directory and the cloud only.

Controls: (a) merge all 5 sources; (b) propose an owner from the last person to sign in; (c) the proposed owner must confirm.

- Without any control: 23 of 38 found.
- With all three: 38 found, 38 owners proposed, 33 confirmed, 5 owners are wrong and corrected by the confirmation.
- Control-off checks: switch off the merge and 23 are found. Switch off the confirmation and the 5 wrong owners stay. Switch off the proposal and nobody is named until a manual step. I expect all three to be noticed.
- Limit I expect: the last person to sign in is often not the one responsible. A confirmation from the wrong person passes.

## P-R15-21 Separation of duties inside privileged access

Scenario: 15 requests. 3 approve their own request. 2 are by a person who changed the vault policy and now approves access to the same vault. 1 is an administrator deleting their own audit log. 9 are fine.

Controls: (a) no self approval; (b) no approving access to a policy you changed; (c) no editing your own audit trail.

- Without any control: 15 granted.
- With all three: 9 granted, 6 refused.
- Control-off checks: switch off self approval and 3 more succeed. Switch off the policy rule and 2 succeed. Switch off the audit rule and 1 succeeds. All three noticed.
- Extra scenario: two people approve each other's requests. I expect both to succeed, because each rule looks at one person at a time.
- Limit I expect: collusion between two people.

## P-R15-22 Integration with the ticket system, the identity provider and the SIEM

Scenario: 20 privileged sessions in a day. The ticket system links each session to a ticket. The identity provider syncs group changes. The SIEM receives an event per session. The SIEM connector drops events when its queue is full. One leaver is removed at the identity provider 1 hour before the sync reaches the vault.

Controls: (a) the ticket link; (b) the group sync every hour; (c) a heartbeat that alarms when the SIEM count does not match the session count.

- Without any control: 0 tickets linked, 0 events.
- With all three: 20 linked, 14 events arrive and 6 are lost, the heartbeat alarms and the 6 are replayed so 20 arrive. The leaver's session in the 1 hour gap is accepted, so 1.
- Control-off checks: switch off the heartbeat and the 6 lost events stay lost and nobody knows. Switch off the sync and the leaver keeps access. Switch off the ticket link and 0 sessions are linked. All three noticed.
- Limit I expect: the heartbeat runs through the same queue it is checking.

## P-R15-23 Endpoint privilege management

Scenario: 30 workstations, each user a local administrator. 40 elevation requests over a week for 6 applications. 3 applications are allowed. 3 need approval. 2 requests are for a command shell. A renamed copy of a command shell is used once.

Controls: (a) remove local administrator; (b) elevate single applications from an allow list; (c) log every elevation.

- Without any control: all 40 succeed.
- With all three: 31 allowed, 9 refused or sent to approval. The 2 shell requests are refused. The renamed shell is refused if the list matches the file hash.
- Control-off checks: switch off the removal of local administrator and all 40 succeed. Switch off the allow list and everything needs approval. Switch off the log and nothing changes in the counts. I expect "not noticed".
- Extra scenario: the list matches the file name, not the hash. I expect the renamed shell to be accepted.
- Limit I expect: an allowed application that can start a shell.

## P-R15-24 Session analytics

Scenario: 200 privileged sessions. 5 are odd: 3 outside working hours, 1 to a target the person never used, 1 that copies a large amount of data.

Controls: (a) a rule for off hours; (b) a rule for a new target; (c) a volume threshold.

- Without any control: 0 of 5 flagged.
- With all three: 4 of 5 flagged. The large copy is just under the threshold and is missed. About 10 normal sessions are flagged too.
- Control-off checks: switch off the off hours rule and 3 are missed. Switch off the new target rule and 1 is missed. Switch off the threshold and nothing changes, because the large copy was already missed. I expect "not noticed".
- Limit I expect: a slow copy of data over many sessions.

## S-R17-07 AI features inside an approved SaaS app

Scenario: a SaaS app that was approved adds an AI assistant. 10 users turn it on. Each user can open about 100 files. The task needs 5. 10 of those files are HR files that the users can technically open.

Controls: (a) a review of the feature's own scope; (b) a limit of the assistant to the files in the task; (c) a log of what the assistant read.

- Without any control: the assistant reads up to 100 files per user, including the 10 HR files, so 10 users times 10 HR files are exposed.
- With all three: the assistant reads 5 per user. 0 HR files.
- Control-off checks: switch off the file limit and the exposure returns. Switch off the scope review and nothing changes while the limit is on. I expect "not noticed". Switch off the log and nothing changes in the counts. I expect "not noticed" as well.
- Limit I expect: the user pastes a file into the assistant by hand.

## S-R17-08 An agent built in a low code tool and never registered

Scenario: 6 agents are built by business users. 2 are registered. 4 are not and hold live credentials.

Controls: (a) a weekly scan of the tenant's app list; (b) a credential is issued only to a registered agent; (c) a 30 day expiry on any unregistered agent.

- Without any control: 4 unregistered agents run with live credentials.
- With all three: the scan finds all 6. The 4 are flagged. 3 are registered after a request and 1 is disabled.
- Control-off checks: switch off the scan and the 4 are not found, so noticed. Switch off the issue rule and the 4 hold credentials until day 30. Switch off the expiry and nothing changes while the issue rule is on. I expect "not noticed".
- Limit I expect: an agent that runs under a personal account outside the tenant.

## S-R17-09 An agent creates credentials and sub agents for itself

Scenario: an agent with wide rights creates 3 new keys and 2 sub agents in one run. One sub agent tries to create another.

Controls: (a) agent identities may not create credentials; (b) a depth limit of 1 for sub agents; (c) an alert on any creation.

- Without any control: 3 keys and 2 sub agents exist, none with an owner.
- With all three: 0 keys, 1 sub agent. The second sub agent is refused by the depth limit. 4 alerts.
- Control-off checks: switch off the credential rule and 3 keys exist. Switch off the depth limit and 2 sub agents exist. Switch off the alert and the refusals stay but nobody is told. All three noticed.
- Limit I expect: the agent asks a person to create the key, and the person does.
