# Guesses, round 18: insecure authentication and environment isolation

Written before any code. Made-up data only (Kaveri Finance). Each case runs without the controls, then with them, then each control is switched off alone. These are my expectations. Wrong ones will be recorded next to the right answer.

## N-R18-01 A copied key from another network (NHI4)

Scenario: an internal payments API accepts a static key from the billing service. In one hour there are 12 calls: 6 genuine from the billing workload, 3 replays of a copied key from an unknown network, and 3 calls with the old key after it was rotated 2 days ago.

Controls: (a) the key is bound to the workload, so a call must also come with the workload's own certificate; (b) the old key is revoked at rotation; (c) an alert fires on a key used from a new network.

- Without any control: all 12 calls are accepted. The log shows "billing key" 12 times and nobody can tell the 6 genuine calls from the 6 bad ones.
- With all three: 6 accepted, 6 refused. 3 alerts for the replays.
- Control-off checks:
  - Switch off the binding: the 3 replays succeed again, and the 3 old-key calls are still refused by the revocation.
  - Switch off the revocation: nothing changes, because the binding already refuses the 3 old-key calls. I expect the check to report this control as "not noticed".
  - Switch off the alert: all 6 refusals stay, and nobody is told.
- Limit I expect: a replay made from inside the real billing workload (a compromised host) carries the certificate and is accepted. The binding cannot see it.
- Where I think I may be wrong: the alert. I expect 3 alerts, but a new network seen twice in a row may be counted once.

## N-R18-02 A test credential that opens production (NHI8)

Scenario: the test pipeline and the production service share one service account and one vault path. Over a day there are 8 pipeline runs in the test environment. 2 of them come from a compromised test runner that tries the production database.

Controls: (a) a separate identity per environment; (b) the production secret path is not readable by any test identity; (c) an alert when a test identity asks for a production secret.

- Without any control: the 2 attempts succeed and the 6 normal runs succeed. Production is reachable from test.
- With all three: 6 normal runs succeed, 2 attempts refused, 2 alerts.
- Control-off checks:
  - Switch off the separate identity: the 2 succeed again.
  - Switch off the path restriction: the 2 are still refused, because the separate identity already stops them. I expect the check to report this control as "not noticed".
  - Switch off the alert: the refusals stay and nobody is told.
- Extra scenario: one production secret is stored under a wildcard path (/kaveri/*/db) that a test identity can match. I expect the path restriction to miss it, so 1 production secret is readable from test. This is the most likely place for my guess to be wrong, in either direction.
- Limit I expect: a real copy of production data loaded into the test database for a refresh is not seen by any of the three controls. The test environment then holds production data without any production credential.
