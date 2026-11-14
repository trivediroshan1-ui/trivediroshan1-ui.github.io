# Draft guesses: Run 2 (policy logic, context signals, privileged roles, auth flows, chains), written before any code

STATUS: DRAFT until hashed and committed on the Mac. Made-up data only (Kaveri Finance). 45 cases.
Run 1 lesson, applied here: every case now has 2 to 3 interacting controls, so "one control off alone" means something.
Models of rule logic, not of any vendor product. Where a case relies on a vendor behaviour I am not sure of, it is marked (verify).
Words: in = the bad outcome happens. out = it does not. "none" = all controls off. "all" = all on.
Format: ID | controls | bad outcome | none | all | off A | off B | off C

## Policy logic
P01 | A block overrides grant (verify), B alert on policy change | user allowed who should be blocked | in | out | in | out | -
P02 | A app inventory, B put app behind the IdP | app reachable with no rule | in | out | in | in | - (B cannot protect an app nobody listed)
P03 | A exclusions need owner and end date, B monthly review | exclusion group above 5 members after 6 months | in | out | out | out | - (either alone is enough)
P04 | A emergency accounts excluded from every rule, B alert on their use | lockout or unnoticed use | in | out | in | in | - (off B: signs in, nobody told)
P05 | A check exclusion before enabling a rule, B report-only week | emergency account locked out | in | out | in | out | - (report-only misses an account that never signs in)
P06 | A report-only 7 days, B someone reads the log | legit users blocked at enforcement | in | out | in | in | -
P07 | A pilot group first, B rollback switch | more than 5 percent of users blocked at any time | in | out | in | out | - (off B: pilot stays blocked but stays under 5 percent)
P08 | A block legacy sign-in, B MFA on modern sign-in | attacker in with password only | in | out | in | in | -
P09 | A exclude service accounts from the user MFA rule, B IP-restricted rule for service accounts | outage or unprotected service account | in | out | in | in | - (off A: outage; off B: unprotected)
P10 | A written test plan with expected results, B peer review | policy gives weaker control than intended | in | out | out | out | - (either alone catches it)
P11 | A change log, B approval before change | unauthorised console change unseen for 7 days | in | out | in | out | -

## Context signals
X01 | A managed device required, B browser-only session on unmanaged devices | data downloaded to unmanaged device | in | out | out | out | -
X02 | A compliance freshness check (24 hours), B event-based revoke | device non-compliant for 3 days still allowed | in | out | in | out | - (off A: offline device sends no event)
X03 | A country block, B named traveller exception with end date | real traveller wrongly blocked | out | out | out | in | - (off B in means: block on, no exception)
X04 | A country block, B device compliance | attacker in via proxy in an allowed country | in | out | out | in | -
X05 | A risk-based step-up, B phishing-resistant MFA on sensitive apps | attacker in sensitive app with low risk score | in | out | out | in | -
X06 | A risk-based block, B self-service remediation | real travelling user blocked over 1 hour | out | out | out | in | -
X07 | A trusted location = managed office egress only, B device compliance | attacker on guest wifi skips MFA | in | out | out | in | -
X08 | A compliant device at token use, B location-based revoke | stolen token replayed from the same country | in | out | in | out | -
X09 | A sign-in frequency 1 hour, B access token lifetime 1 hour | stolen session works after 8 hours | in | out | in | out | - (refresh tokens renew quietly without A)

## Privileged roles
A01 | A phishing-resistant rule on admin portals only, B remove SMS from admin methods | admin phished via SMS on any app | in | out | out | in | -
A02 | A fresh MFA at role activation, B activation limited to 1 hour | attacker activates admin role from stolen session | in | out | in | out | -
A03 | A separate admin accounts, B block admin group on non-admin apps | admin session on a risky app | in | out | in | out | - (off A: daily account is not in the admin group)
A04 | A workload identity rule (location), B exclude workloads from user rules | outage or unprotected workload | in | out | in | in | -
A05 | A trust home-tenant MFA claim for guests, B guest MFA in our tenant | guest in without real MFA | in | out | out | in | - (off B: a weak home tenant claim is accepted)

## Chain tests
C01 | A remove SMS recovery, B strong help desk proof, C method-change notice | account taken and unnoticed | in | out | in | in | out
C02 | A compliant device at token use, B session lifetime 1 hour, C location revoke | stolen token works at 30 minutes or at 4 hours | in | out | in | out | out
C03 | A put the app behind SSO, B review exclusions, C alert on exclusion use | attacker in via local login or excluded account, unnoticed | in | out | in | in | out
C04 | A report-only, B automatic exclusion of emergency accounts, C alert | lockout at enforcement | in | out | out | in | out
C05 | A remove SMS fallback, B SIM swap check, C method-change notice | takeover via SIM swap | in | out | out | out | out (I expect any two of A and B off together to give in)

## Authentication flows and extra cases
Z08 | A block device code flow, B prompt "only enter codes you started" (assume 60 percent resist) | attacker gets tokens | in | out | in | out | - (off A: 40 of 100 users still fall)
Z09 | A block legacy and ROPC in policy, B disable ROPC on app registrations, C alert on ROPC use | password-only token | in | out | out | out | out
Z10 | A user consent limited to verified publishers, B admin consent workflow, C app governance alert | malicious app reads mail | in | out | in | out | out
Z11 | A block one named client, B block the whole flow | same flow via another client | in | out | out | in | -
Z12 | A reduce to one condition, B alert on sign-ins no policy covered | attack sign-in outside the policy | in | out | in | out | - (B only alerts, does not fix)
Z13 | A baseline MFA for all users and apps, B block unknown client types | sign-in matching no policy allowed | in | out | in | out | -
Z14 | A dedicated registration policy, B alert on new method registration | attacker registers own MFA | in | out | in | out | -
Z15 | A policy as code applied weekly, B daily drift detection | console edit lasts over 24 hours | in | out | out | in | - (A alone: edit survives up to 7 days, so I expect off B in)
Z16 | A device compliance, B platform condition | spoofed platform string bypasses a block | in | out | in | out | -
Z17 | A compliant device at replay, B token protection, C phishing-resistant MFA | AiTM session replay works | in | out | out | out | out (I expect any one control alone is enough)
Z18 | A continuous access evaluation, B 15 minute token lifetime | stolen token works 10 minutes after revoke | in | out | in | out | -
Z19 | A revoke sessions on password reset, B sign-in frequency 8 hours | attacker token works 1 hour after reset | in | out | in | out | -
Z20 | A legacy exception limited to the printer IP, B exception has an end date | attacker uses the exception from outside | in | out | in | out | -
Z21 | A block device code flow, B refresh token 1 hour, C compliant device at use | attacker has access at 24 hours | in | out | out | out | out (I expect A and C off together to give in; B does not matter)
Z22 | A registration protection, B device rule on access, C MFA required | stolen password plus own MFA gets in | in | out | out | out | out (I expect A and B off together to give in)

## Predictions on the whole run
- All controls on: out in all 45.
- Cases where at least one single control off gives in: about 33 of 45.
- Cases where I expect each control alone to be enough (no single off gives in): P03, P10, X01, Z09, Z17, Z21, Z22, C05, and maybe 2 more.
- Cases where I expect a control to be useless without another (it protects nothing alone): P02, P05, X02, Z12, Z15.
- Where I expect to be wrong: how timing works (P05, X02, X09, Z18, Z19) and where two controls overlap (P10, X01, Z17). I cannot say which.
- Pair checks (C05, Z21, Z22) will test the any-two-off statements.
