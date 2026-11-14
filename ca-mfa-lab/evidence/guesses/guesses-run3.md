# Draft guesses: Run 3 (PAM step-up, federation, mobile and native apps, passkeys, resilience, agents and MCP, chains), written before any code

STATUS: DRAFT until hashed and committed on the Mac. Made-up data only (Kaveri Finance). 16 cases (Y01 to Y16).
Source rows: catalogue v1.2, second search pass. Models of rule logic, not of any vendor product. Where a case relies on a vendor behaviour I am not sure of, it is marked (verify).
Words: in = the bad outcome happens. out = it does not. "none" = all controls off. "all" = all on.
Format: ID | controls | bad outcome | none | all | off A | off B | off C   ("off A" means only A is off)

Lessons from Run 2, applied before I guess:
1. I write down what the bad outcome is first, because I got C01 and C03 wrong by not saying what I was counting.
2. A notice or alert tells you; it does not block. I mark every alert as not stopping the bad outcome.
3. A habit is not enforcement.
4. I check which control actually decides the question, because I got Z21 wrong on that.
5. I do not assume controls work independently, because I got A05 wrong on that.

## PAM and step-up
Y01 | A app checks the token for fresh MFA, B IdP forces step-up when the app asks | privileged action done with no fresh MFA | in | out | in | out | - (off B: the app refuses, which is not the bad outcome; the check lives in the app)
Y02 | A step-up on interactive sessions, B background jobs run as a service identity with its own scope, C user-delegated background tokens blocked for privileged scopes | privileged action with no step-up by any path | in | out | in | out | out (B or C alone closes the background path; only A covers interactive)

## Federation
Y03 | A alert on federation change, B federation change needs a second approver, C cloud MFA required whatever the federated IdP claims | attacker signs in as any user with MFA treated as done | in | out | out | out | out (A is a notice, it never stops it; B or C alone is enough)
Y04 | A cloud MFA required whatever the claim says, B IdP stops skipping MFA for internal addresses | password-only sign-in from a compromised internal workstation | in | out | out | out | - (either alone is enough)

## Mobile and native apps
Y05 | A require a compliant device, B require the broker (approved client) | sign-in from an unmanaged personal phone | in | out | in | out | - (assumes an app with no device identity is refused, not waved through)
Y06 | A policy covers all resources and client paths, B compliant device checked at token issue | attacker with password and relayed MFA gets a token from an unmanaged host through the nested path (verify) | in | out | in | in | - (B is part of the policy A decides the reach of)
Y07 | A compliant device at token use, B token bound to the device, C only approved browser extensions | attacker uses the session from inside the compliant device | in | out | out | out | in (only C stops it; A and B protect against replay from elsewhere)

## Passkeys and recovery
Y08 | A user verification on every use, B device-bound passkeys only (no synced passkeys) | assertion produced with no user action (verify) | in | out | in | in | - (both needed, because the research describes the synced path skipping the prompt)
Y09 | A fresh strong sign-in to add a method, B revoke methods added since compromise, C alert on a new method | attacker still has access 24 hours after sessions are revoked | in | out | out | out | out (C is a notice but it triggers B; assume the user acts on it)

## Resilience
Y10 | A fail closed when the provider is unreachable, B emergency accounts outside the MFA path, C second MFA provider | password-only sign-in accepted during an outage of the main provider | in | out | out | out | out (A or C alone; B only prevents lockout, it does not touch this outcome)

## Agents and MCP
Y11 | A per-client consent screen owned by the MCP server, B redirect URIs limited to a pre-registered list, C consent cookie set only after consent | attacker gets an authorization code with no user consent | in | out | out | out | out (each one alone breaks the attack)
Y12 | A token audience checked by the MCP server, B downstream call uses the server's own exchanged token, C downstream API checks audience | attacker acts as the user at the downstream API with a token issued for another service | in | out | in | out | out (only A stops it; B and C see a valid token once the server has accepted it)
Y13 | A short token life (under 1 hour), B narrow scope for the task | a leaked token is still useful after 1 hour or outside the task | in | out | in | in | - (the leak is assumed; both limits are needed)
Y14 | A per-call permission check, B person confirms irreversible actions, C server marks which actions are irreversible | irreversible action runs on injected text | in | out | out | in | in (A allows it, so it does not help; B needs C to know what to ask about)

## Chains
Y15 | A approved browser extensions only, B fresh strong sign-in to add a method, C revoke methods added since compromise | attacker still has access 24 hours after the user reports and sessions are revoked | in | out | out | out | out (A stops the theft; B or C alone stops the persistence)
Y16 | A per-client consent, B narrow token scope, C short token life | attacker holds a token that is broad or lasts over 1 hour | in | out | out | out | out (A stops it; if A fails, B and C together make the token small)

## My own predictions before running
- All on is out in 16 of 16.
- At least one single control off lets the bad outcome in for: Y01, Y02, Y05, Y06, Y07, Y08, Y12, Y13, Y14 (9 cases).
- No single control off lets it in for: Y03, Y04, Y09, Y10, Y11, Y15, Y16 (7 cases).
- I expect 2 to 4 of my guesses to be wrong. The ones I trust least: Y06, Y08 and Y10 (thin sources), and Y09 (I assumed the user acts on an alert).
