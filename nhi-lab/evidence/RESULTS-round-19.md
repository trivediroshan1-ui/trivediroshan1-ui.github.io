# Results: round 19, the queued cases

Made-up data. Guesses were hashed and committed (a2dc1fd, sha256 729e16f2...) before this code. Models are small in-memory simulations written by the same person as the guesses.

| Case | Guess, without | Guess, with | Control-off guesses | Noticed guesses | Every control noticed |
|---|---|---|---|---|---|
| N-R14-02 Secrets in code, config, chat and tickets | match | match | match | match | repo_scan: yes, chat_scan: yes, ticket_scan: yes |
| N-R14-06 An identity created outside the normal process | match | match | match | match | cloud_policy: yes, weekly_sweep: NO, auto_expiry: NO |
| N-R14-10 The owning team is disbanded | match | match | match | match | orphan_queue: yes, limit_14_days: yes, attestation: NO |
| N-R14-12 Overprivileged identities | match | match | match | match | right_sizing_report: yes, person_approves: NO, wildcard_rule: yes |
| N-R14-13 Rotation on a schedule | match | match | match | match | schedule: yes, overlap_2h: yes, dead_secret_check: yes |
| N-R14-16 Retire before you rotate | match | match | match | match | use_check: yes, hold_30_days: yes, delete_after_hold: NO |
| P-R15-01 Request privileged access with a ticket and an end time | match | match | match | match | ticket_open: yes, end_time: yes, second_approver_tier0: yes |
| P-R15-04 The elevation path is down | match | match | match | match | second_node: yes, break_glass: NO, fallback_review: NO |
| P-R15-06 The person never sees the password | match | match | MISMATCH | MISMATCH | inject_credential: NO, reveal_disabled: NO, rotate_after_session: yes |
| P-R15-12 The break-glass drill | match | MISMATCH | MISMATCH | match | routing_check: yes, second_holder: yes, drill: yes |
| P-R15-14 Shared accounts: who did what | match | match | match | match | checkout_names_person: yes, session_log_tag: yes, password_change: NO |
| P-R15-20 Discover privileged accounts and assign owners | match | match | match | match | merge_sources: yes, propose_owner: yes, owner_confirms: yes |
| P-R15-21 Separation of duties inside privileged access | match | match | match | match | no_self_approval: yes, no_policy_approver: yes, no_audit_edit: yes |
| P-R15-22 Integration with ticket system, identity provider and SIEM | MISMATCH | match | match | match | ticket_link: yes, group_sync: yes, heartbeat: yes |
| P-R15-23 Endpoint privilege management | match | match | match | match | remove_local_admin: yes, allow_list: yes, log_elevations: NO |
| P-R15-24 Session analytics | match | match | match | match | off_hours_rule: yes, new_target_rule: yes, volume_threshold: NO |
| S-R17-07 AI features inside an approved SaaS app | match | match | match | match | scope_review: NO, file_limit: yes, read_log: NO |
| S-R17-08 An agent built in a low code tool and never registered | match | match | MISMATCH | MISMATCH | weekly_scan: yes, issue_rule: yes, expiry_30_days: yes |
| S-R17-09 An agent creates credentials and sub agents for itself | match | MISMATCH | match | match | no_credential_creation: yes, depth_limit_1: yes, alert_on_creation: yes |

Cases with every guess matched: 14 of 19. Cases with at least one wrong guess: 5.

## Where my guess was wrong

- **P-R15-06** (injection off): expected reveals=2, got 0
- **P-R15-06** (rotation off): expected direct_logins_refused=3, got 0
- **P-R15-06** (noticed or not): inject_credential: expected noticed, got not noticed; rotate_after_session: expected not noticed, got noticed
- **P-R15-12** (all controls on): expected faults_found=2, got 1; expected faults_fixed=2, got 1
- **P-R15-12** (drill off): expected faults_found=0, got 1
- **P-R15-22** (without controls): expected siem_events_arrived=0, got 14
- **S-R17-08** (issue rule off): expected unregistered_with_creds_day10=4, got 1
- **S-R17-08** (noticed or not): expiry_30_days: expected not noticed, got noticed
- **S-R17-09** (all controls on): expected alerts=4, got 5
- Total wrong claims: 9.

## What each run returned

- N-R14-02 without controls: {'found': 0, 'still_live': 20, 'missed_in_scanned_places': 0, 'missed_kinds': []}
- N-R14-02 all controls on: {'found': 17, 'still_live': 3, 'missed_in_scanned_places': 3, 'missed_kinds': ['base64', 'image', 'split']}
- N-R14-06 without controls: {'created': 10, 'refused': 0, 'ownerless_day_1': 3, 'first_found_day': None, 'removed_day': None, 'ownerless_day_30': 3}
- N-R14-06 all controls on: {'created': 7, 'refused': 3, 'ownerless_day_1': 0, 'first_found_day': None, 'removed_day': None, 'ownerless_day_30': 0}
- N-R14-10 without controls: {'queued_day0': 0, 'claimed_by_day14': 0, 'paused_day14': 0, 'outages': 0, 'active_with_old_owner_day90': 12}
- N-R14-10 all controls on: {'queued_day0': 12, 'claimed_by_day14': 9, 'paused_day14': 3, 'outages': 1, 'active_with_old_owner_day90': 0}
- N-R14-12 without controls: {'permissions': 120, 'unused_permissions': 82, 'removed': 0, 'broken_jobs': 0, 'wildcard_grants_ok': 2}
- N-R14-12 all controls on: {'permissions': 44, 'unused_permissions': 6, 'removed': 76, 'broken_jobs': 1, 'wildcard_grants_ok': 0}
- N-R14-13 without controls: {'rotated': 0, 'avg_age_days': 400, 'outages': 0, 'old_secrets_valid_after_2h': 0}
- N-R14-13 all controls on: {'rotated': 20, 'avg_age_days': 0, 'outages': 0, 'old_secrets_valid_after_2h': 0}
- N-R14-16 without controls: {'disabled': 0, 'rotated': 30, 'outages': 0, 'permanent_loss': 0}
- N-R14-16 all controls on: {'disabled': 12, 'rotated': 18, 'outages': 1, 'permanent_loss': 0}
- P-R15-01 without controls: {'granted': 10, 'refused': 0}
- P-R15-01 all controls on: {'granted': 6, 'refused': 4}
- P-R15-04 without controls: {'blocked': 5, 'break_glass_uses': 0, 'alerts': 0, 'reviews': 0, 'shared_password_used': 3}
- P-R15-04 all controls on: {'blocked': 0, 'break_glass_uses': 0, 'alerts': 0, 'reviews': 0, 'shared_password_used': 0}
- P-R15-06 without controls: {'sessions_ok': 10, 'reveals': 2, 'direct_logins_ok': 3, 'direct_logins_refused': 0}
- P-R15-06 all controls on: {'sessions_ok': 10, 'reveals': 0, 'direct_logins_ok': 0, 'direct_logins_refused': 3}
- P-R15-12 without controls: {'faults_found': 0, 'faults_fixed': 0, 'found_by': {'alert_routing': None, 'sealed_copy': None}, 'first_run_failures': None, 'steps_pass_second_run': None}
- P-R15-12 all controls on: {'faults_found': 1, 'faults_fixed': 1, 'found_by': {'alert_routing': 'routing_check', 'sealed_copy': None}, 'first_run_failures': 0, 'steps_pass_second_run': 4}
- P-R15-14 without controls: {'attributed': 0, 'ambiguous': 0, 'password_changes': 0, 'late_login_possible': True}
- P-R15-14 all controls on: {'attributed': 12, 'ambiguous': 0, 'password_changes': 4, 'late_login_possible': False}
- P-R15-20 without controls: {'found': 23, 'proposed': 0, 'confirmed': 0, 'wrong_owners_corrected': 0, 'wrong_owners_remaining': 0}
- P-R15-20 all controls on: {'found': 38, 'proposed': 38, 'confirmed': 33, 'wrong_owners_corrected': 5, 'wrong_owners_remaining': 0}
- P-R15-21 without controls: {'granted': 15, 'refused': 0}
- P-R15-21 all controls on: {'granted': 9, 'refused': 6}
- P-R15-22 without controls: {'tickets_linked': 0, 'siem_events_arrived': 14, 'lost_unnoticed': 6, 'heartbeat_alarmed': False, 'leaver_session_in_gap': 1, 'leaver_access_after_sync': True}
- P-R15-22 all controls on: {'tickets_linked': 20, 'siem_events_arrived': 20, 'lost_unnoticed': 0, 'heartbeat_alarmed': True, 'leaver_session_in_gap': 1, 'leaver_access_after_sync': False}
- P-R15-23 without controls: {'allowed': 40, 'refused_or_approval': 0, 'shells_allowed': 2, 'renamed_shell_allowed': True}
- P-R15-23 all controls on: {'allowed': 31, 'refused_or_approval': 9, 'shells_allowed': 0, 'renamed_shell_allowed': False}
- P-R15-24 without controls: {'odd_flagged': 0, 'odd_missed': 5, 'false_positives': 0}
- P-R15-24 all controls on: {'odd_flagged': 4, 'odd_missed': 1, 'false_positives': 10}
- S-R17-07 without controls: {'files_read_per_user': 100, 'hr_files_exposed': 100}
- S-R17-07 all controls on: {'files_read_per_user': 5, 'hr_files_exposed': 0}
- S-R17-08 without controls: {'found': 0, 'flagged': 0, 'registered_after_request': 0, 'disabled': 0, 'unregistered_with_creds_day10': 4, 'unregistered_with_creds_day31': 4}
- S-R17-08 all controls on: {'found': 6, 'flagged': 4, 'registered_after_request': 3, 'disabled': 1, 'unregistered_with_creds_day10': 0, 'unregistered_with_creds_day31': 0}
- S-R17-09 without controls: {'keys': 3, 'sub_agents': 2, 'refused': 0, 'alerts': 0, 'objects_without_owner': 5}
- S-R17-09 all controls on: {'keys': 0, 'sub_agents': 1, 'refused': 4, 'alerts': 5, 'objects_without_owner': 1}

## Control-off checks and extra scenarios

- N-R14-02 repo and config scan off: got {'found': 7, 'still_live': 13, 'missed_in_scanned_places': 1, 'missed_kinds': ['image']} (matches my note)
- N-R14-02 chat scan off: got {'found': 13, 'still_live': 7, 'missed_in_scanned_places': 3, 'missed_kinds': ['base64', 'image', 'split']} (matches my note)
- N-R14-02 ticket scan off: got {'found': 14, 'still_live': 6, 'missed_in_scanned_places': 2, 'missed_kinds': ['base64', 'split']} (matches my note)
- N-R14-06 policy off, sweep and expiry on: got {'created': 10, 'refused': 0, 'ownerless_day_1': 3, 'first_found_day': 7, 'removed_day': 14, 'ownerless_day_30': 0} (matches my note)
- N-R14-10 orphan queue off: got {'queued_day0': 0, 'claimed_by_day14': 0, 'paused_day14': 0, 'outages': 0, 'active_with_old_owner_day90': 12} (matches my note)
- N-R14-10 14 day limit off: got {'queued_day0': 12, 'claimed_by_day14': 9, 'paused_day14': 0, 'outages': 0, 'active_with_old_owner_day90': 3} (matches my note)
- N-R14-12 report off: got {'permissions': 120, 'unused_permissions': 82, 'removed': 0, 'broken_jobs': 0, 'wildcard_grants_ok': 0} (matches my note)
- N-R14-12 approval off: got {'permissions': 44, 'unused_permissions': 6, 'removed': 76, 'broken_jobs': 1, 'wildcard_grants_ok': 0} (matches my note)
- N-R14-12 wildcard rule off: got {'permissions': 44, 'unused_permissions': 6, 'removed': 76, 'broken_jobs': 1, 'wildcard_grants_ok': 2} (matches my note)
- N-R14-13 overlap off: got {'rotated': 20, 'avg_age_days': 0, 'outages': 3, 'old_secrets_valid_after_2h': 0} (matches my note)
- N-R14-13 dead-secret check off: got {'rotated': 20, 'avg_age_days': 0, 'outages': 0, 'old_secrets_valid_after_2h': 20} (matches my note)
- N-R14-13 schedule off: got {'rotated': 0, 'avg_age_days': 400, 'outages': 0, 'old_secrets_valid_after_2h': 0} (matches my note)
- N-R14-16 hold off: got {'disabled': 0, 'rotated': 18, 'outages': 1, 'permanent_loss': 1} (matches my note)
- N-R14-16 use check off: got {'disabled': 0, 'rotated': 30, 'outages': 0, 'permanent_loss': 0} (matches my note)
- P-R15-01 ticket check off: got {'granted': 8, 'refused': 2} (matches my note)
- P-R15-01 end time rule off: got {'granted': 7, 'refused': 3} (matches my note)
- P-R15-01 second approver off: got {'granted': 7, 'refused': 3} (matches my note)
- P-R15-01 open ticket of another system, all controls on: got {'granted': 7, 'refused': 4} (matches my note)
- P-R15-04 second node off: got {'blocked': 0, 'break_glass_uses': 5, 'alerts': 5, 'reviews': 5, 'shared_password_used': 0} (matches my note)
- P-R15-04 second node and break-glass off: got {'blocked': 5, 'break_glass_uses': 0, 'alerts': 0, 'reviews': 0, 'shared_password_used': 3} (matches my note)
- P-R15-06 injection off: got {'sessions_ok': 10, 'reveals': 0, 'direct_logins_ok': 0, 'direct_logins_refused': 3} (differs from my note)
- P-R15-06 rotation off: got {'sessions_ok': 10, 'reveals': 0, 'direct_logins_ok': 3, 'direct_logins_refused': 0} (differs from my note)
- P-R15-12 routing check off: got {'faults_found': 1, 'faults_fixed': 1, 'found_by': {'alert_routing': 'drill', 'sealed_copy': None}, 'first_run_failures': 1, 'steps_pass_second_run': 4} (matches my note)
- P-R15-12 second holder off: got {'faults_found': 2, 'faults_fixed': 2, 'found_by': {'alert_routing': 'routing_check', 'sealed_copy': 'drill'}, 'first_run_failures': 1, 'steps_pass_second_run': 4} (matches my note)
- P-R15-12 drill off: got {'faults_found': 1, 'faults_fixed': 1, 'found_by': {'alert_routing': 'routing_check', 'sealed_copy': None}, 'first_run_failures': None, 'steps_pass_second_run': None} (differs from my note)
- P-R15-14 log tag off: got {'attributed': 10, 'ambiguous': 2, 'password_changes': 4, 'late_login_possible': False} (matches my note)
- P-R15-14 password change off: got {'attributed': 12, 'ambiguous': 0, 'password_changes': 0, 'late_login_possible': True} (matches my note)
- P-R15-14 check-out off: got {'attributed': 0, 'ambiguous': 0, 'password_changes': 0, 'late_login_possible': False} (matches my note)
- P-R15-20 merge off: got {'found': 23, 'proposed': 23, 'confirmed': 21, 'wrong_owners_corrected': 2, 'wrong_owners_remaining': 0} (matches my note)
- P-R15-20 confirmation off: got {'found': 38, 'proposed': 38, 'confirmed': 0, 'wrong_owners_corrected': 0, 'wrong_owners_remaining': 5} (matches my note)
- P-R15-20 proposal off: got {'found': 38, 'proposed': 0, 'confirmed': 0, 'wrong_owners_corrected': 0, 'wrong_owners_remaining': 0} (matches my note)
- P-R15-21 self approval rule off: got {'granted': 12, 'refused': 3} (matches my note)
- P-R15-21 policy rule off: got {'granted': 11, 'refused': 4} (matches my note)
- P-R15-21 audit rule off: got {'granted': 10, 'refused': 5} (matches my note)
- P-R15-21 two people approve each other, all controls on: got {'granted': 11, 'refused': 6} (matches my note)
- P-R15-22 heartbeat off: got {'tickets_linked': 20, 'siem_events_arrived': 14, 'lost_unnoticed': 6, 'heartbeat_alarmed': False, 'leaver_session_in_gap': 1, 'leaver_access_after_sync': False} (matches my note)
- P-R15-22 sync off: got {'tickets_linked': 20, 'siem_events_arrived': 20, 'lost_unnoticed': 0, 'heartbeat_alarmed': True, 'leaver_session_in_gap': 1, 'leaver_access_after_sync': True} (matches my note)
- P-R15-22 ticket link off: got {'tickets_linked': 0, 'siem_events_arrived': 20, 'lost_unnoticed': 0, 'heartbeat_alarmed': True, 'leaver_session_in_gap': 1, 'leaver_access_after_sync': False} (matches my note)
- P-R15-23 local admin removal off: got {'allowed': 40, 'refused_or_approval': 0, 'shells_allowed': 2, 'renamed_shell_allowed': True} (matches my note)
- P-R15-23 allow list off: got {'allowed': 0, 'refused_or_approval': 40, 'shells_allowed': 0, 'renamed_shell_allowed': False} (matches my note)
- P-R15-23 list matches file name, not hash: got {'allowed': 32, 'refused_or_approval': 8, 'shells_allowed': 0, 'renamed_shell_allowed': True} (matches my note)
- P-R15-24 off hours rule off: got {'odd_flagged': 1, 'odd_missed': 4, 'false_positives': 4} (matches my note)
- P-R15-24 new target rule off: got {'odd_flagged': 3, 'odd_missed': 2, 'false_positives': 6} (matches my note)
- P-R15-24 volume threshold off: got {'odd_flagged': 4, 'odd_missed': 1, 'false_positives': 10} (matches my note)
- S-R17-07 file limit off: got {'files_read_per_user': 100, 'hr_files_exposed': 100} (matches my note)
- S-R17-08 scan off: got {'found': 0, 'flagged': 0, 'registered_after_request': 0, 'disabled': 4, 'unregistered_with_creds_day10': 0, 'unregistered_with_creds_day31': 0} (matches my note)
- S-R17-08 issue rule off: got {'found': 6, 'flagged': 4, 'registered_after_request': 3, 'disabled': 1, 'unregistered_with_creds_day10': 1, 'unregistered_with_creds_day31': 0} (differs from my note)
- S-R17-09 credential rule off: got {'keys': 3, 'sub_agents': 1, 'refused': 1, 'alerts': 5, 'objects_without_owner': 4} (matches my note)
- S-R17-09 depth limit off: got {'keys': 0, 'sub_agents': 2, 'refused': 3, 'alerts': 5, 'objects_without_owner': 2} (matches my note)
- S-R17-09 alert off: got {'keys': 0, 'sub_agents': 1, 'refused': 4, 'alerts': 0, 'objects_without_owner': 1} (matches my note)

## Limits probed

- **N-R14-02**: {'secret_in_an_image_seen': False, 'note': 'the screenshot secret sits in a scanned place and is still missed, because no scan reads images'}
- **N-R14-06**: {'account_with_unaware_owner_accepted': True, 'note': 'the tag names a real person who never agreed, so the policy, the sweep and the expiry all pass it'}
- **N-R14-10**: {'unread_mailing_list_accepted_as_owner': True, 'note': 'the claim check asks only that the owner resolves; a list nobody reads resolves'}
- **N-R14-12**: {'annual_job_broken': True, 'note': '90 days of use cannot see a job that runs once a year, so its permission is counted as unused'}
- **N-R14-13**: {'consumer_caching_3h_fails_despite_2h_overlap': True}
- **N-R14-16**: {'two_identities_missed_by_logs_were_retired': True, 'note': 'the use logs do not see an older sign-in route, so a used identity looks idle'}
- **P-R15-01**: {'ticket_for_other_system_accepted': True, 'note': 'the check asks whether the ticket is open, not whether it matches the task'}
- **P-R15-04**: {'second_node_helped': False, 'note': 'both nodes fail for the same reason, so the fallback is used even with the second node'}
- **P-R15-06**: {'keylogger_or_memory_on_target_seen_by_controls': False, 'note': 'an assertion about my model, not a measurement: none of the three controls inspects the user machine or target memory'}
- **P-R15-12**: {'announced_drill_flatters_result': True, 'note': 'an assertion about my model: the model has no people in it, so it cannot show that an announced drill is easier than a real night'}
- **P-R15-14**: {'handed_over_session_attributed_to_wrong_person': True}
- **P-R15-20**: {'wrong_owner_confirmed_anyway': True}
- **P-R15-21**: {'mutual_approval_accepted': True, 'note': 'each rule looks at one person at a time'}
- **P-R15-22**: {'heartbeat_missed_the_loss': True, 'note': 'the heartbeat message is dropped by the same full queue it is checking'}
- **P-R15-23**: {'shell_started_inside_an_allowed_app': True, 'note': 'elevation applies to the allowed application, and its child process inherits it'}
- **P-R15-24**: {'slow_copy_over_many_sessions_flagged': False, 'note': '20 sessions of 100 MB each stay under the 1000 MB per-session threshold'}
- **S-R17-07**: {'hr_file_pasted_by_hand_exposed': True, 'note': 'the limit applies to what the assistant fetches, not to what a user pastes in'}
- **S-R17-08**: {'agent_under_personal_account_found': False, 'note': 'the scan reads the tenant app list; an agent under a personal account is not in it'}
- **S-R17-09**: {'key_created_by_a_person_at_the_agents_request': True, 'note': 'the key is created under a person, outside all three agent-identity controls'}

## Not noticed (masked by another control, or no effect on what the case counts)

- N-R14-06: weekly_sweep
- N-R14-06: auto_expiry
- N-R14-10: attestation
- N-R14-12: person_approves
- N-R14-16: delete_after_hold
- P-R15-04: break_glass
- P-R15-04: fallback_review
- P-R15-06: inject_credential
- P-R15-06: reveal_disabled
- P-R15-14: password_change
- P-R15-23: log_elevations
- P-R15-24: volume_threshold
- S-R17-07: scope_review
- S-R17-07: read_log

Controls switched off alone: 57. Not noticed: 14.
Limits probed: 19.
