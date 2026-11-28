# Guesses: Privileged access lab, round 4 (on real software), written before any code

STATUS: LOCKED when committed (28 Nov 2026). Never edited after the hash is taken; any mistake is disclosed on the results page, not fixed here. Made-up data only (Kaveri Finance). 5 cases, PA-R4-01 to PA-R4-05. Approved by Roshan Trivedi on 28 Nov 2026.
Lab name: Privileged access lab: who holds admin, and for how long?
Why this round: rounds 1 and 3 modelled rule logic. This round measures the same ideas on real open-source software: Keycloak, OpenBao (the open-source fork of Vault), PostgreSQL, OpenSSH with sudo, and Kubernetes in Docker (kind). It runs on a GitHub Actions runner, so the full log is public. Exact versions are pinned in the workflow and recorded with the results. No commercial PAM product is tested: trial licences often forbid publishing results.
Words: "none" = all controls off. "all" = all on. "off a" means only control a is off. A control is "noticed" when switching it off alone changes a counted number compared with all controls on.
Format of the table: ID | what is counted (the bad outcome) | none | all | off a | off b | off c.

Lessons from rounds 1 and 3, applied before I guess:
1. I write down the bad outcome first, and exactly how it is measured.
2. A notice, alert or log does not block.
3. Controls cover for each other. Cases 04 and 05 expect "not noticed" results for that reason; joint checks are listed.
4. Delegation goes more than one level deep. Round 3 case 05 missed that; case 02 here counts direct sub-agents only, and says so.
5. One correction made before locking: in the draft, case 03 had 5 for "off c". Its lease starts with the task, and the task lasts 2 minutes, so the right guess is 3.

## The table

| ID | Counted | none | all | off a | off b | off c |
|---|---|---|---|---|---|---|
| PA-R4-01 | first check, in seconds after the role is removed, at which the API refuses the admin token (checked every 15 s from 0; 600 if never refused) | 300 | 0 | 60 | 0 | 60 |
| PA-R4-02 | direct sub-agents (3 tried) that reach the database API's admin endpoint | 3 | 0 | 3 | 0 | 0 |
| PA-R4-03 | first check, in minutes after the task ends, at which a login with the copied database credential fails (checked every minute from 0; 30 if it never fails) | 30 | 0 | 30 | 0 | 3 |
| PA-R4-04 | sudo commands (5 tried over 2 minutes) that succeed in an already-open SSH session after the user is removed from the admin group | 5 | 0 | 0 | 0 | 0 |
| PA-R4-05 | paths (3 tried) that reach cluster-admin from a developer's kubeconfig | 3 | 0 | 1 | 2 | 0 |

Joint checks, also predicted:
- PA-R4-01: online check and session logout both off: 60.
- PA-R4-04: group re-read and session end both off: 5.

Notes on the table:
- PA-R4-01: the token is issued, then the role is removed within a second, then checking starts at 0. Keycloak's default access token life is 5 minutes, so with no controls the first refused check is at 300.
- PA-R4-05: a path counts when the credentials it yields pass `kubectl auth can-i '*' '*' --all-namespaces`.

## The cases

### PA-R4-01 The token outlives the role (Keycloak)

Scenario: an admin user gets an access token with the admin role from Keycloak. The role is removed in Keycloak. A test API is then called with the same token every 15 seconds.

Controls: (a) the API checks every token online with Keycloak (token introspection) instead of only checking its signature and expiry; (b) the access token lives 60 seconds instead of Keycloak's default of 5 minutes; (c) when the role is removed, the user's sessions are logged out through Keycloak's admin API.

- Without any control: the token works until it expires: 300.
- With all three: 0.
- Control-off checks: switch off the online check and logout can't recall a token the API checks on its own, so it works until its 60 s expiry: 60. Switch off the short life and the online check sees the logged-out session: 0. Switch off the logout and the online check still reports the token active, with the roles it was issued with, until expiry: 60.
- What this guess bets: an online check alone does not help unless the session is also ended.
- Where I may be wrong: whether Keycloak's introspection re-reads roles; the 15 s step around the expiry.

### PA-R4-02 A sub-agent and the parent's token (Keycloak token exchange)

Scenario: a parent agent holds a token that may call the database API's admin endpoint. It starts 3 sub-agents; each tries the admin endpoint.

Controls: (a) each sub-agent gets its own token through token exchange, for its own service and without the admin scope; the parent's token is never passed on; (b) the API accepts only tokens whose audience is the API; (c) the API requires the admin scope, not just a valid token.

- Without any control: the parent's token is passed on: 3.
- With all three: 0.
- Control-off checks: switch off the exchange and the parent's token has the right audience and scope: 3. Noticed. Switch off the audience check and the exchanged tokens still lack the admin scope: 0. Switch off the scope check and the exchanged tokens have the wrong audience: 0.
- Where I may be wrong: how standard token exchange in the pinned Keycloak version sets audience and scope.

### PA-R4-03 Short-lived database credentials (OpenBao and PostgreSQL)

Scenario: a task needs database admin for 2 minutes. The credential it used is copied. From the end of the task, a login with it is tried every minute for 30 minutes.

Controls: (a) the credential is created per task by OpenBao's database engine, instead of one stored password; (b) the lease lasts 5 minutes from creation, instead of OpenBao's default; (c) the task revokes its lease when it finishes.

- Without any control: the stored password works throughout: 30.
- With all three: 0.
- Control-off checks: switch off per-task credentials and the stored password works throughout; lease and revoke don't apply: 30. Switch off the short lease and the lease is revoked at the end: 0. Switch off the revoke and the 5-minute lease, started with the 2-minute task, runs out 3 minutes after it ends: 3.
- Where I may be wrong: how quickly OpenBao acts on an expired lease.

### PA-R4-04 The open session survives (OpenSSH and sudo)

Scenario: an admin is logged in over SSH, with passwordless sudo through the admin group. The user is removed from the admin group. Over the next 2 minutes, 5 sudo commands are tried in the session that is already open.

Controls: (a) sudo reads group membership from the system on every command (`group_source=dynamic`), instead of using the groups the session started with; (b) the user's open sessions are ended when they are removed; (c) every sudo command raises an alert.

- Without any control: the session keeps the groups it started with: 5.
- With all three: 0.
- Control-off checks: switch off the group re-read and the session is ended: 0. Switch off the session end and sudo sees the removal: 0. Switch off the alert: 0. None is noticed alone; (a) and (b) off together give 5. The alert never blocks.
- Where I may be wrong: the default group handling in the pinned sudo version.

### PA-R4-05 Kubernetes cluster-admin (kind)

Scenario: a developer's kubeconfig on a kind cluster. Three paths to cluster-admin: impersonating an engineer who holds a standing cluster-admin binding; reading the token of a service account bound to cluster-admin from a namespace the developer can read; starting a privileged pod that mounts the node's files and reading the node's admin kubeconfig.

Controls: (a) no standing cluster-admin binding for people; (b) no service account holds cluster-admin, and Pod Security "restricted" is enforced on the developer's namespace; (c) an audit rule logs exec into system namespaces.

- Without any control: 3.
- With all three: 0.
- Control-off checks: switch off (a) and the impersonation path is back: 1. Switch off (b) and the service account and privileged pod paths are back: 2. Switch off (c) and nothing changes: 0.
- Where I may be wrong: whether every form of the privileged pod is refused by Pod Security admission in the pinned Kubernetes version.

## What this round can't tell you

- How commercial PAM products behave. Only the open-source software named above, at the pinned versions and settings, is measured.
- Anything about other versions or other settings.
- The AI approver. That belongs in round 2, with local models and repeated runs.
