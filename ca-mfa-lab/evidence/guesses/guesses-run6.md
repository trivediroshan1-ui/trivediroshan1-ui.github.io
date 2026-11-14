# Guesses: Run 6 (AI agent identity), written before any code

STATUS: LOCKED when committed (14 Nov 2026). Never edited after the hash is taken; any mistake is disclosed on the results page, not fixed here. Made-up data only (Kaveri Finance). 10 cases (G01 to G10) run on models, and 3 hand tests (E04 to E06) for other people to run.
Sources read on 14 Nov 2026 before writing: Okta press release "Okta brings first-class identity to AI agents with Agent SSO" (24 Aug 2026); Cloud Security Alliance, "Defining Non-Human Identity" (22 Jul 2026). Search excerpts only: Ping Identity agent announcements (Sep 2026, via Help Net Security and ITPro), IETF AIMS draft (via SecureW2), Zscaler on OIDC and SPIFFE.
Models of rule logic, not of any vendor product. Where a case rests on a mechanism the source does not describe, it is marked (verify).
Words: in = the bad outcome happens. out = it does not. "none" = all controls off. "all" = all on.
Format: ID | controls | bad outcome | none | all | off A | off B | off C   ("off A" means only A is off)

Lessons from Runs 1 to 5, applied before I guess:
1. I write down the bad outcome first, so I know what I am counting.
2. A notice, alert, flag or log does not block.
3. Rotation is not expiry: a rotated credential still works for whoever holds the new one.
4. I check which control actually decides the question, and whether controls depend on each other.
5. Perfect scores in Runs 1, 3 and 5 came from writing the models after the guesses. This run has the same weakness. The assumption tests at the end are where I expect to learn something.

## Agent sign-in across apps
G01 | A revoking the user's grant at the identity provider also revokes tokens already issued to the second app, B second-app access tokens last 5 minutes, C the agent's identity assertion is checked against the current grant every time it is exchanged | the agent still reaches the second app 1 hour after the user revokes its access (verify) | in | out | out | out | in (two paths: the token already issued, which A or B closes, and a new token from a cached assertion, which only C closes; Okta's release does not describe revocation, so the mechanism is my model)

## Agents acting for people
G02 | A the agent may act only on the account the human named in the request, B high-risk actions need the human to confirm with the target shown, C every action is logged | an admin agent resets another user's password after reading injected text in a ticket | in | out | in | out | out (C is a notice; B alone is not enough if the person confirms without reading; same assumption as W10)
G03 | A a sub-agent's token is narrowed to the parent's scope and the task (token exchange), B sub-agent tokens last 10 minutes, C the resource checks every delegated action against the human's own permissions | a sub-agent writes to a system the human who asked cannot write to | in | out | out | out | in (only C decides: the orchestrator has its own broad scope, so narrowing to the parent's scope still allows the write; B limits time, not reach)
G10 | A every agent call carries the delegating human in the token, B logs share a correlation ID across agent hops, C audit logs kept 90 days | 30 days later, an investigator cannot name the human who asked for an agent's action | in | out | in | out | in (B links the hops but the chain starts at a shared service account, so without A the human is never recorded; without C the logs are gone by day 30)

## Agent and workload lifecycle
G04 | A an agent identity expires when its task or project ends, B its credentials rotate every 30 days, C quarterly access review | an agent credential still works 60 days after its project ended | in | out | in | out | out (B gives the agent a new credential, it does not remove it; C finds it only if a review falls in the 60 days)
G05 | A every agent needs a named human sponsor at creation, B the sponsor leaving triggers reassignment or disable within 7 days, C a monthly scan flags agents with no owner | an agent with no owner is still working 30 days after the person who created it leaves | in | out | in | in | out (C is a notice; B needs the sponsor record from A to fire, and A needs B to act)
G06 | A the identity provider issues no refresh token to an agent client that is not registered and approved, B refresh tokens end 24 hours after sign-in even when rotated, C tokens bound to the device | a token stolen from an employee's personal AI agent still works 7 days later | in | out | out | out | out (each one alone closes it)
G07 | A continuous evaluation revokes the session within minutes when the network or device changes, B sessions last 8 hours, C session bound to the device | a stolen session cookie still works more than 1 hour after it was stolen | in | out | out | out | out (C or A alone closes it; assumes the attacker uses a different network, see assumptions)
G08 | A services check revocation for agent certificates, B agent certificates last 24 hours, C decommissioning an agent revokes its certificate | a decommissioned agent's certificate is still accepted 7 days later (verify) | in | out | out | out | out (B alone is enough; A and C only work together; based on a draft, so verify)
G09 | A the workload uses 1-hour federated tokens instead of a stored secret, B secret scanning revokes a leaked secret within 1 day, C stored secrets rotate every 90 days | a secret copied from a build log still works 30 days later | in | out | out | out | out (A or B alone closes it; assumes the scanner reads build logs)

## Hand tests for other people to run (no model; predictions only)
E04 | real cross-app agent access in a test tenant: revoke the user's grant and keep calling the second app with the token and with a fresh exchange | prediction: the token already issued keeps working until it expires unless the product revokes it at the second app; a fresh exchange is refused
E05 | real admin agent in a test tenant: put a reset instruction for another account inside a ticket and ask the agent to handle open tickets | prediction: the agent proposes the reset; whether it acts depends on whether it asks the human to confirm the target
E06 | real continuous access evaluation in a test tenant: copy a session to another network | prediction: the session is cut within minutes for apps that support it, and keeps working for apps that do not

## Assumptions I chose (write them in the code and on the page)
- G01: the cached identity assertion lasts 24 hours.
- G02: 30 percent of people confirm without reading (same as W10 and W11).
- G04: the quarterly review falls at a random point; a review inside the 60 days finds the agent.
- G07: the attacker replays the cookie from a different network.
- G09: the scanner reads build logs.
- G10: without C, logs are kept 7 days; the chain starts at a shared service account.
- Threshold: a path counts as open if the bad outcome happens more than 5 percent of the time.

## My own predictions before running
- All on is out in 10 of 10.
- At least one single control off lets the bad outcome in for: G01, G02, G03, G04, G05, G10 (6 cases).
- No single control off lets it in for: G06, G07, G08, G09 (4 cases).
- I expect 2 to 4 wrong. The ones I trust least: G03 (whether narrowing helps), G05 (how the three controls depend on each other), G07 (the network assumption), G01 (a mechanism the source does not describe).
- G04 and G05 are the cases most likely to surprise viewers: rotation and alerts look like controls but do not remove access.
