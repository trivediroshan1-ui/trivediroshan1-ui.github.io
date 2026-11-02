# Results: rounds 14, 15 and 17, 27 cases (24 must + 3 gap)

Made-up data. Guesses were hashed and committed before this code. Models are small in-memory simulations of each control, not real systems.

| Case | Guess, without | Guess, with | Every control noticed |
|---|---|---|---|
| N-R14-01 Inventory misses a source | match | match | merge_sources: yes |
| N-R14-03 Long-lived CI variable read by another job | match | match | per_job_scope: yes |
| N-R14-04 Certificate with no owner expires | match | match | owner_required: yes, expiry_alert: yes |
| N-R14-05 Old OAuth grant, vendor breached | match | match | consent_expiry_90d: yes |
| N-R14-09 Identity with no owner | match | match | owner_or_pause: yes |
| N-R14-11 Application retired, identities remain | match | match | retire_attestation: yes |
| N-R14-14 Rotation fails silently | match | match | failure_alert: yes |
| N-R14-15 Rotate before consumer is updated | match | match | consumer_first: yes |
| N-R14-17 Loose federation trust | match | match | bind_to_workload: yes |
| N-R14-18 Front door for new identities | match | match | require_owner_scope_expiry: yes |
| P-R15-02 Just-in-time window | match | match | jit_window: yes |
| P-R15-03 Work runs past the window | match | match | one_extension_then_approval: yes |
| P-R15-05 Standing admin group membership | match | match | timebox_and_prune: yes |
| P-R15-07 Direct login still open | match | match | network_block: yes |
| P-R15-08 Recording gap on one target | match | match | coverage_check_block: yes |
| P-R15-09 Two approvers for Tier 0 | match | match | two_approvers: yes |
| P-R15-11 Break-glass used at 2 a.m. | match | match | alert_justify_rotate: yes |
| P-R15-13 Break-glass becomes a side door | match | match | monthly_report_flag: yes |
| P-R15-17 Vendor session | match | match | broker_record_expire: yes |
| P-R15-18 Vendor person leaves the vendor | match | match | sponsor_review_30d: yes |
| S-R17-01 Personal OAuth grant to an AI tool | match | match | revoke_on_leave: yes, grant_scan: yes |
| S-R17-03 Agent runs under a person's account | match | match | agent_identity: yes, log_tag: yes |
| S-R17-04 Ghost credential | match | match | owner_end_date_required: yes, weekly_sweep: yes |
| S-R17-05 Secrets in AI-assisted code and config | match | MISMATCH | secret_scan: yes |
| N-R14-23 Vendor breached, OAuth refresh token still valid | match | match | tenant_allowlist: yes, breach_revoke: NO |
| N-R14-24 Secrets in env variables not marked sensitive | match | match | pattern_marking: yes |
| N-R14-25 Credential stolen from a CI runner, replayed | match | match | short_ttl: NO, bind_and_revoke: yes |

## Where my guess was wrong

- **S-R17-05** (with): expected misses=1, got 2
- **N-R14-25** (control-off check): expected short_ttl='changes a replay result', got 'no change: the other control already blocks both replays'

## Extra scenarios

- N-R14-23 revoke only (app already granted): match
- N-R14-23 revoke off, allowlist off: match
- N-R14-25 10-minute lifetime only: match

## Limits probed

- **N-R14-11**: {'attested_all_disabled': True, 'still_active': 1, 'note': 'attestation signed against an incomplete list'}
- **N-R14-15**: {'app_fails': False, 'missed_consumer_fails': True, 'missed': ['report-job']}
- **P-R15-05**: {'remaining': 8, 'broader_than_needed': 2}
- **P-R15-11**: {'closed': True, 'note': 'the text is not checked for truth'}
- **P-R15-13**: {'missed_fake_tickets': 2, 'note': 'a ticket number is not checked against the ticket system'}
- **N-R14-23**: {'listed_app_breached': {'grant_accepted': True, 'replay_min30': True, 'replay_min90': True}, 'note': 'an allowlisted app that is breached still works until revoked'}
- **N-R14-25**: {'replay_from_inside_runner_min3': True, 'note': 'bound token still works from inside the runner during the job'}

## Not noticed

- N-R14-23: breach_revoke (masked: another control already stops the same attack)
- N-R14-25: short_ttl (masked: another control already stops the same attack)
