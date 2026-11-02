# Results: 13 stretch cases and 6 chain tests

Made-up data. Guesses were hashed and committed (78d7e3e) before this code. Models are small in-memory simulations. The chain tests are rule models: each link is stopped by the controls I decided stop it, so their results follow from my rules.

| Case | Guess, without | Guess, with | Every control noticed |
|---|---|---|---|
| N-R14-07 One identity, three names | MISMATCH | MISMATCH | owner_match: yes, normalise_name: yes |
| N-R14-19 Scoring: rank so the top gets fixed first | match | match | reach_in_score: yes |
| N-R14-20 Close only when the old secret is dead | match | match | verify_old_dead: yes |
| N-R14-21 Agents share a team credential | match | match | key_per_agent: yes |
| N-R14-22 A person logs in with a service account | match | match | block_interactive: yes, checkout_names_person: yes |
| P-R15-10 Phishing-resistant MFA for admins | match | match | passkey: yes, no_sms_fallback: yes |
| P-R15-15 The vault, its backups and who can read them | match | match | same_rules: yes, alert_nonbackup: yes |
| P-R15-16 Help desk reset path | match | match | strong_proof: NO, notice_and_delay: NO |
| P-R15-19 A vendor is needed at 2 a.m. | match | match | approve_and_record: yes, auto_expiry: yes |
| P-R15-25 Mass rotation after a breach | match | match | consumer_first: yes, dry_run: yes |
| S-R17-02 AI tool inherits the full permissions of the person | match | match | scope_read_one: yes |
| S-R17-06 AI-service keys leak into repositories | match | match | scan_revoke: yes, rotate_90d: NO |
| S-R17-10 Scheduled automations outlive the test window | match | match | end_date_at_creation: yes, sweep: yes |
| C-R16-C01 The forgotten service account | match | MISMATCH | owner_required: yes, secret_scan_tickets: NO, rotation: NO |
| C-R16-C02 The token in the repository | match | match | commit_block: yes, short_lived: NO, revoke_on_find: NO |
| C-R16-C04 The contractor who never left | match | match | end_date_expiry: yes, sponsor_review: NO |
| C-R16-C05 The break-glass password everyone knows | match | match | alert_every_use: yes, rotate_on_return: yes |
| C-R16-C06 Approval fatigue | match | match | batch_limits: NO, risk_shown_first: yes, second_approver_high_risk: yes |
| C-R16-C17 The old door | match | match | block_direct_login: yes, checkin_alert: yes |

## Where my guess was wrong

- **N-R14-07** (without): expected count=51, got 43
- **N-R14-07** (with): expected count=30, got 29
- **C-R16-C01** (with): expected best_alone='secret_scan_tickets', got 'owner_required'

## Chains: how far each control gets alone

- **C-R16-C01**: all controls on -> stopped at link 1, detected at None; alone: {'owner_required': 1, 'secret_scan_tickets': 2, 'rotation': 4}
- **C-R16-C02**: all controls on -> stopped at link 1, detected at None; alone: {'commit_block': 1, 'short_lived': 4, 'revoke_on_find': None}
- **C-R16-C04**: all controls on -> stopped at link 3, detected at None; alone: {'end_date_expiry': 3, 'sponsor_review': None}
- **C-R16-C05**: all controls on -> stopped at link 3, detected at 4; alone: {'alert_every_use': None, 'rotate_on_return': 3}
- **C-R16-C06**: all controls on -> stopped at link 4, detected at 3; alone: {'batch_limits': None, 'risk_shown_first': None, 'second_approver_high_risk': 4}
- **C-R16-C17**: all controls on -> stopped at link 2, detected at 4; alone: {'block_direct_login': 2, 'checkin_alert': None}

## Extra scenarios

- C-R16-C01 account already exists (legacy), owner rule cannot apply: got {'stopped_at': 2, 'reached_end': False, 'detected_at': None} (matches my note)
- C-R16-C02 the finder is faster than the token lifetime (12 hours): got {'stopped_at': None, 'reached_end': True, 'detected_at': None} (matches my note)
- C-R16-C04 attack 120 days after contract end, sponsor review runs at 90: got {'stopped_at': 3, 'reached_end': False, 'detected_at': None} (matches my note)

## Limits probed

- **N-R14-07**: my arithmetic was wrong: 9 identities with 2 or 3 names each cannot give 51 entries; and stripping trailing digits merged two real accounts
- **N-R14-22**: {'copied_password_used_elsewhere_seen': False, 'note': 'a password copied during a checkout and used from another tool is not seen by the control'}
- **P-R15-16**: {'person_approves_the_notice_account_lost': True, 'note': 'if the real person is also tricked into approving the notice, the account is lost with both controls on'}
- **S-R17-10**: {'extension_reason_checked': False, 'note': 'an extension is accepted on any written reason'}
- **C-R16-C06**: the rule model says risk-first display only flags the request. Whether a tired approver acts on the flag is human behaviour, which this model does not test

## Not noticed (masked by another control)

- P-R15-16: strong_proof
- P-R15-16: notice_and_delay
- S-R17-06: rotate_90d
- C-R16-C01: secret_scan_tickets
- C-R16-C01: rotation
- C-R16-C02: short_lived
- C-R16-C02: revoke_on_find
- C-R16-C04: sponsor_review
- C-R16-C06: batch_limits
