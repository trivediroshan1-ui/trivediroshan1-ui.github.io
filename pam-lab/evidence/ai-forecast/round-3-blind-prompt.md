# Blind forecast prompt: Privileged access lab, round 3

Paste everything below the line into the AI model you are testing, in a new chat with no other context. Save its full answer as `round-3-<model>.md` in this folder, record the model name, version and date at the top, hash the file with SHA-256, and commit it BEFORE running `round3.py`.

This prompt holds the scenarios, the controls and what is counted. It does not hold Roshan's predictions, his joint checks or his notes on where he may be wrong.

---

You are a privileged access management architect. For each case below, predict the counted number(s) under five settings: no controls (none), all three controls on (all), and each control switched off alone while the other two stay on (off a, off b, off c). These are simple rule models with made-up data, not real products. Use only the scenario text. Where something is not stated, make the most reasonable assumption and say what you assumed in one line.

Answer with one table, one row per counted outcome, in exactly this format, and nothing else except the one-line assumptions after it:

| ID | Counted | none | all | off a | off b | off c |
|---|---|---|---|---|---|---|

## PA-R3-01 The help desk resets an admin

Scenario: 10 admin recovery requests in a month. 2 come from attackers who call the help desk with personal details found online. 1 attacker has moved an admin's phone number to a new SIM and uses SMS recovery.

Controls: (a) admin recovery needs a video check against the HR photo and a callback to the manager on a number already on file; (b) no SMS or email recovery for admin accounts; (c) a newly enrolled authenticator can't activate admin for 24 hours, and the account owner and the SOC are told at once.

Counted: attacker admin activations within 24 hours
Also counted: attacker authenticators enrolled

## PA-R3-02 Movers keep old eligibility

Scenario: 20 people change teams in a quarter. 6 held admin eligibility in the old team; 2 of them need the same role in the new team.

Controls: (a) a mover event removes every eligibility that is not in the new role's model; (b) the new manager re-requests anything still needed, on the day of the move; (c) a quarterly review of eligibility against role.

Counted: movers holding eligibility they don't need, 30 days after the move
Also counted: movers blocked from work they need

## PA-R3-03 Contractors with no end date

Scenario: 15 contractors are eligible for admin. 5 contracts end this month. 3 of those 5 accounts have no end date in the identity system.

Controls: (a) every contractor account must carry an end date no later than the contract end; (b) the sponsor attests every 30 days; (c) the vendor management system sends the contract end and the account is disabled that day.

Counted: ended contractors who can still activate admin 30 days after the end

## PA-R3-04 A vendor's laptop is taken over

Scenario: 4 vendors, 12 sessions a month. One vendor's laptop is taken over, and the attacker uses the vendor's standing VPN account outside any planned session.

Controls: (a) vendors reach targets only through the access broker; no direct VPN accounts; (b) each session needs an approved ticket and lasts at most 2 hours; (c) sessions to Tier 0 targets are recorded and dangerous commands are blocked.

Counted: harmful Tier 0 commands run by the attacker

## PA-R3-05 A sub-agent inherits the parent's admin

Scenario: a parent agent is elevated to database admin for a migration. It starts 3 sub-agents; one is a third-party summariser that receives the parent's token. One sub-agent tries to start its own sub-agent.

Controls: (a) each sub-agent gets its own identity and a narrower token through token exchange; the parent's token is never passed on; (b) a depth limit of 1; (c) a log naming which agent used each token.

Counted: sub-agents able to use the parent's database admin rights

## PA-R3-06 Signing keys

Scenario: a code-signing key signs every release. Two attacks in a quarter: an insider tries to copy the key file, and an attacker changes the build settings on a side branch so that branch's build asks for a signature.

Controls: (a) the key lives in a hardware security module and can't be exported; (b) only builds from the protected main branch can call the signing service; (c) a daily review of the signing log against the release list.

Counted: malicious artifacts signed
Also counted: days until a malicious signature is found (-1 = never, 0 = none made)

## PA-R3-07 Kubernetes cluster-admin

Scenario: an attacker holds a developer's kubeconfig. Three paths to cluster-admin exist: a standing cluster-admin binding for an engineer the developer can impersonate, a service account with cluster-admin whose token sits in a pod the developer can read, and a privileged pod the developer can start and escape.

Controls: (a) cluster-admin for people only through just-in-time activation, no standing bindings; (b) no service account holds cluster-admin, and admission policy refuses privileged pods; (c) an alert on exec into system namespaces.

Counted: paths to cluster-admin from a developer's kubeconfig

## PA-R3-08 OT access while IT is down

Scenario: ransomware takes down the corporate identity provider and vault for 6 hours. The plant needs one urgent change to a PLC. An attacker inside the IT network tries to reach the same PLC.

Controls: (a) OT access only through a broker in the IT/OT boundary zone, with approval and a time limit; (b) a site-local break-glass account held at the plant, not in the corporate vault; (c) the PLC is read-only from remote sessions; writing needs a second person on site.

Counted: attacker writes to the PLC
Also counted: urgent plant changes blocked

## PA-R3-09 Two insiders work together

Scenario: 20 Tier 0 requests in a week. Two admins plan to take data and approve each other's requests 4 times.

Controls: (a) no self-approval; (b) the same pair can't approve each other more than twice a month; (c) a third reviewer, picked at random, checks 20% of Tier 0 approvals within 24 hours.

Stated assumption: to keep the model fixed, the random third reviewer catches exactly one collusive grant in the week whenever at least one goes through.

Counted: collusive grants unnoticed after a week

## PA-R3-10 Session recordings hold personal data

Scenario: 500 privileged sessions are recorded each month. 40 of them show personal data on screen (HR or customer records). 6 times a year someone watches a recording with no ticket.

Controls: (a) recordings are deleted after 90 days unless under investigation; (b) access to recordings is itself just-in-time, with a ticket, and logged; (c) known personal-data fields are masked automatically in recordings (I assume 30 of 40 a month are caught).

Counted: recordings with personal data still held after a year
Also counted: recording views with no ticket
