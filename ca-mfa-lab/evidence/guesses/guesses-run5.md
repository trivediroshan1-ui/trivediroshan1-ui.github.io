# Draft guesses: Run 5 (CI/CD and DevOps, APIs and integrations, agents and MCP, recovery), written before any code

STATUS: LOCKED when committed (14 Nov 2026). Never edited after the hash is taken; any mistake is disclosed on the results page, not fixed here. Made-up data only (Kaveri Finance). 12 cases (W01 to W12).
Source rows: catalogue v1.4 additions, from the November 2026 search and incident reading. Models of rule logic, not of any vendor product. Where a case relies on one thin source or an assumption I chose, it is marked (verify) or listed under Assumptions.
Words: in = the bad outcome happens. out = it does not. "none" = all controls off. "all" = all on.
Format: ID | controls | bad outcome | none | all | off A | off B | off C   ("off A" means only A is off)

Lessons from Runs 1 to 3, applied before I guess:
1. I write down the bad outcome first, so I know what I am counting.
2. A notice or alert tells you. It does not block. Any alert is marked as not stopping the bad outcome.
3. A habit is not enforcement.
4. I check which control actually decides the question.
5. I do not assume controls work independently.
6. Perfect scores in Runs 1 and 3 came from writing the models after the guesses. This run will have the same weakness, so I say so up front.

## CI/CD and DevOps
W01 | A cloud trust policy pins the repository and branch (not just the identity provider), B workflows from pull requests cannot request a cloud token, C deploy role has narrow permissions | a workflow in someone else's repository gets production cloud credentials | in | out | in | out | out (only A decides; B covers pull requests but not a workflow in another repository, C limits damage but not the grant)
W02 | A third-party actions pinned to a commit, B workflow token has the minimum permissions, C short-lived cloud tokens instead of stored cloud keys | an attacker holds a cloud credential that still works 24 hours after a poisoned action ran | in | out | out | out | out (each one alone leaves no 24-hour credential; assumes the cloud session lasts at most 1 hour and cannot mint new credentials)
W03 | A privileged triggers never check out or run code from a pull request, B secrets not exposed to workflows from forks, C cloud token request allowed only on protected branches | code from an outside pull request gets a cloud or publish token | in | out | out | out | out (each one alone breaks the path; the real cases chained two mistakes)
W04 | A approver must use phishing-resistant MFA, B requester cannot approve their own change, C approval tied to the exact commit | a malicious change deploys to production with an approval on record | in | out | in | in | in (three different paths: a phished approver, a self-approval, and a swap after approval; no control is redundant)

## APIs and integrations
W05 | A every login method except SAML is switched off on the gateway, B vendor fix applied, C alert on sessions with no matching identity provider sign-in | remote access session that never touched the identity provider's MFA (verify) | in | out | out | out | out (C is a notice, it never stops it; A or B alone closes the path; one source only, a blog)
W06 | A integration token scoped to only the objects it needs, B token usable only from the vendor's addresses, C tokens expire daily and rotate | attacker exports customer records using a stolen integration token | in | out | out | in | out (only B stops use from the attacker's address; A limits what is lost, but the integration legitimately reads those records; C does nothing against use within a day; allow-listing as a control is (verify))
W07 | A password reset revokes refresh tokens and sessions, B changing an MFA method revokes sessions, C access tokens last 1 hour | a stolen session still works 24 hours after the user resets the password (the user does nothing else) | in | out | in | out | out (only A applies here; B is never triggered by a password reset; C only ends the access token)
W08 | A API keys not accepted on privileged endpoints, B privileged calls need a fresh step-up claim, C client-credentials tokens limited to service scopes | a privileged API call made with a credential that skipped step-up | in | out | in | in | in (three paths: a key, a replayed refresh token, a service token with user-level scope; each control closes a different one)
W09 | A access tokens bound to the client (DPoP or mutual TLS), B access tokens last 5 minutes, C refresh tokens rotate | a stolen access token replayed from another machine within its lifetime | in | out | in | out | out (assumes the attacker uses it within minutes of stealing it, so B does not help; C is irrelevant to an access token)

## Agents and MCP
W10 | A each task gets its own narrow token, B a person approves every write, C every tool call is logged | an agent changes or deletes records it was not asked to touch, after reading injected text | in | out | in | out | out (C is a notice and never stops it; B alone is not enough if the person approves without reading; assumption below)
W11 | A the client accepts only authorization servers from its own allow-list, B the client checks that the issuer in the discovery data matches the server it connected to, C the user checks the sign-in address | the client sends the user's login to an attacker-controlled authorization endpoint (verify) | in | out | in | out | out (B alone is not enough: a malicious server's own metadata names itself as the issuer, so it matches; C alone is not enough, see assumption)

## Recovery
W12 | A self-service recovery needs a phishing-resistant method, B help desk reset needs a callback to the number on file, C a new method cannot be used on privileged apps for 24 hours | attacker gets a working new authenticator enrolled on the account | in | out | in | in | out (two paths into enrolment, A and B; C limits what the new method can do, not whether it is enrolled)

## Assumptions I chose (write them in the code and on the page)
- A cloud session from a short-lived token lasts at most 1 hour and cannot create credentials (W02).
- In W09, an attacker who steals an access token uses it within minutes.
- In W10 and W11, 30 percent of people approve or accept without reading. This is the same kind of assumption as the 40 percent code-lure rate in Run 2. Change it and the result can change.
- The model of W05 assumes the gateway offers several login methods and the flaw only works while another method is enabled.

## My own predictions before running
- All on is out in 12 of 12.
- At least one single control off lets the bad outcome in for: W01, W04, W06, W07, W08, W09, W10, W11, W12 (9 cases).
- No single control off lets it in for: W02, W03, W05 (3 cases).
- I expect 2 to 4 of my guesses to be wrong. The ones I trust least: W05 and W11 (thin sources), W10 and W11 (the 30 percent assumption), W02 (the 1-hour assumption).
- In W06 and W08, the notes say MFA is not what decides the outcome. If that holds, those are the cases that will surprise viewers most.
