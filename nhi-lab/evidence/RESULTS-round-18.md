# Results: round 18, two cases

Made-up data. Guesses were hashed and committed (e50df1b, sha256 9155e078...) before this code. Models are small in-memory simulations written by the same person as the guesses.

| Case | Guess, without | Guess, with | Every control noticed |
|---|---|---|---|
| N-R18-01 A copied key from another network | match | MISMATCH | workload_binding: yes, revoke_old: NO, alert_new_network: yes |
| N-R18-02 A test credential that opens production | match | match | separate_identity: yes, path_restriction: NO, alert_test_asks_prod: yes |

## Where my guess was wrong

- **N-R18-01** (with): expected alerts=3, got 1

## What each run returned

- N-R18-01 without controls: {'accepted': 12, 'refused': 0, 'alerts': 0, 'replays_accepted': 3, 'old_key_refused': 0, 'can_tell_apart': False}
- N-R18-01 all controls on: {'accepted': 6, 'refused': 6, 'alerts': 1, 'replays_accepted': 0, 'old_key_refused': 3, 'can_tell_apart': True}
- N-R18-02 without controls: {'normal_ok': 6, 'attacks_succeeded': 2, 'attacks_refused': 0, 'alerts': 0, 'readable_prod_secrets': 1}
- N-R18-02 all controls on: {'normal_ok': 6, 'attacks_succeeded': 0, 'attacks_refused': 2, 'alerts': 2, 'readable_prod_secrets': 0}

## Control-off checks and extra scenarios

- N-R18-01 binding off: got {'accepted': 9, 'refused': 3, 'alerts': 1, 'replays_accepted': 3, 'old_key_refused': 3, 'can_tell_apart': False} (matches my note)
- N-R18-01 revocation off: got {'accepted': 6, 'refused': 6, 'alerts': 1, 'replays_accepted': 0, 'old_key_refused': 3, 'can_tell_apart': True} (matches my note)
- N-R18-01 alert off: got {'accepted': 6, 'refused': 6, 'alerts': 0, 'replays_accepted': 0, 'old_key_refused': 3, 'can_tell_apart': True} (matches my note)
- N-R18-01 replays from three different networks, all controls on: got {'accepted': 6, 'refused': 6, 'alerts': 3, 'replays_accepted': 0, 'old_key_refused': 3, 'can_tell_apart': True} (matches my note)
- N-R18-02 separate identity off: got {'normal_ok': 6, 'attacks_succeeded': 2, 'attacks_refused': 0, 'alerts': 0, 'readable_prod_secrets': 1} (matches my note)
- N-R18-02 path restriction off: got {'normal_ok': 6, 'attacks_succeeded': 0, 'attacks_refused': 2, 'alerts': 2, 'readable_prod_secrets': 0} (matches my note)
- N-R18-02 alert off: got {'normal_ok': 6, 'attacks_succeeded': 0, 'attacks_refused': 2, 'alerts': 0, 'readable_prod_secrets': 0} (matches my note)
- N-R18-02 one production secret under a wildcard path, all controls on: got {'normal_ok': 6, 'attacks_succeeded': 1, 'attacks_refused': 1, 'alerts': 1, 'readable_prod_secrets': 1} (matches my note)

## Limits probed

- **N-R18-01**: {'call_from_inside_the_real_workload_accepted': True, 'note': 'a replay from inside the real billing workload carries the certificate, so the binding cannot see it'}
- **N-R18-02**: {'prod_data_copied_into_test_seen_by_controls': False, 'note': 'a refresh job copies production rows into the test database under the production identity. None of the three controls inspects data, so this is an assertion about my model, not a measurement'}

## Not noticed (masked by another control)

- N-R18-01: revoke_old
- N-R18-02: path_restriction
