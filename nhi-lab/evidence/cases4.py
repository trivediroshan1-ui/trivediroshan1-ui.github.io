"""Round 19: the 19 queued cases. Made-up data only (Kaveri Finance).
Written AFTER guesses/guesses-round-19.md was committed (a2dc1fd, sha256 729e16f2...).

Modelling rules, fixed before the first run:
  1. Each case returns only the quantities its guess file names. A control is "noticed" when switching it off
     alone changes one of those quantities (or the case's `watch` keys, where the guess limits itself to some).
  2. Where the guess is silent or ambiguous about the scenario, the model takes the plain reading of the scenario text.
     A guess that disagrees with the model is recorded as wrong. Nothing is tuned afterwards.
  3. `on` is the set of controls switched on. Names starting with '@' are scenario markers, not controls.
Small in-memory models written by the same person who wrote the guesses."""
CASES = []
def case(id, title, controls, gw, gx, notice, watch=None):
    def deco(fn):
        CASES.append(dict(id=id, title=title, controls=controls, run=fn, gw=gw, gx=gx, notice=notice,
                          watch=watch, limit=None, extras=[]))
        return fn
    return deco
def limit(id):
    def deco(fn):
        for c in CASES:
            if c['id'] == id: c['limit'] = fn
        return fn
    return deco
def extra(id, label, on, expect):
    for c in CASES:
        if c['id'] == id: c['extras'].append((label, on, expect))
def ALL(id): return set(next(c for c in CASES if c['id'] == id)['controls'])
def run(id, on): return next(c for c in CASES if c['id'] == id)['run'](set(on))
def minus(id, ctl, plus=()): return (ALL(id) - {ctl}) | set(plus)

# ---------- N-R14-02 secrets in code, config, chat and tickets
# 20 planted secrets. A scan matches plain text only: it does not join split lines, decode base64 or read images.
@case('N-R14-02', 'Secrets in code, config, chat and tickets', ['repo_scan', 'chat_scan', 'ticket_scan'],
      dict(found=0, still_live=20),
      dict(found=17, missed_in_scanned_places=3, missed_kinds=['base64', 'image', 'split']),
      dict(repo_scan=True, chat_scan=True, ticket_scan=True))
def _(on):
    S = ([('repo', 'plain')] * 6 + [('repo', 'split'), ('repo', 'base64')] + [('config', 'plain')] * 4 +
         [('chat', 'plain')] * 4 + [('ticket', 'plain')] * 3 + [('ticket', 'image')])
    covered = set()
    if 'repo_scan' in on: covered |= {'repo', 'config'}
    if 'chat_scan' in on: covered |= {'chat'}
    if 'ticket_scan' in on: covered |= {'ticket'}
    found = [s for s in S if s[0] in covered and s[1] == 'plain']
    missed = [s for s in S if s[0] in covered and s[1] != 'plain']
    return dict(found=len(found), still_live=20 - len(found), missed_in_scanned_places=len(missed),
                missed_kinds=sorted(k for _, k in missed))
extra('N-R14-02', 'repo and config scan off', minus('N-R14-02', 'repo_scan'), dict(found=7))
extra('N-R14-02', 'chat scan off', minus('N-R14-02', 'chat_scan'), dict(found=13))
extra('N-R14-02', 'ticket scan off', minus('N-R14-02', 'ticket_scan'), dict(found=14))
@limit('N-R14-02')
def _():
    r = run('N-R14-02', ALL('N-R14-02'))
    return dict(secret_in_an_image_seen=('image' not in r['missed_kinds']),
                note='the screenshot secret sits in a scanned place and is still missed, because no scan reads images')

# ---------- N-R14-06 an identity created outside the normal process
# 7 accounts via the front door, 3 created in the console. Evaluated at day 30. The sweep finds untagged accounts
# on day 7. The expiry removes an untagged account 14 days after creation.
@case('N-R14-06', 'An identity created outside the normal process', ['cloud_policy', 'weekly_sweep', 'auto_expiry'],
      dict(created=10, ownerless_day_30=3),
      dict(refused=3, ownerless_day_1=0, ownerless_day_30=0),
      dict(cloud_policy=True, weekly_sweep=False, auto_expiry=False))
def _(on):
    console = 0 if 'cloud_policy' in on else 3
    return dict(created=7 + console, refused=3 - console, ownerless_day_1=console,
                first_found_day=7 if (console and 'weekly_sweep' in on) else None,
                removed_day=14 if (console and 'auto_expiry' in on) else None,
                ownerless_day_30=0 if (console and 'auto_expiry' in on) else console)
extra('N-R14-06', 'policy off, sweep and expiry on', minus('N-R14-06', 'cloud_policy'),
      dict(created=10, first_found_day=7, removed_day=14, ownerless_day_30=0))
@limit('N-R14-06')
def _():
    # The front door asks for an owner tag that resolves to a real person. It does not ask that person.
    owner_ok = True
    return dict(account_with_unaware_owner_accepted=owner_ok,
                note='the tag names a real person who never agreed, so the policy, the sweep and the expiry all pass it')

# ---------- N-R14-10 the owning team is disbanded
# 12 accounts. The orphan queue starts on day 0; 9 are claimed within 14 days; 3 are not. One unclaimed account
# serves a weekly job. The quarterly attestation produces nothing the case counts.
@case('N-R14-10', 'The owning team is disbanded', ['orphan_queue', 'limit_14_days', 'attestation'],
      dict(active_with_old_owner_day90=12),
      dict(queued_day0=12, claimed_by_day14=9, paused_day14=3, outages=1),
      dict(orphan_queue=True, limit_14_days=True, attestation=False))
def _(on):
    q = 'orphan_queue' in on
    claimed = 9 if q else 0
    paused = (12 - claimed) if (q and 'limit_14_days' in on) else 0
    still_active_old = 12 - claimed - paused
    unread_list = ('@mailing_list' in on) and q
    out = dict(queued_day0=12 if q else 0, claimed_by_day14=claimed, paused_day14=paused,
               outages=1 if paused else 0, active_with_old_owner_day90=still_active_old)
    if '@mailing_list' in on: out['unread_list_accepted_as_owner'] = unread_list
    return out
extra('N-R14-10', 'orphan queue off', minus('N-R14-10', 'orphan_queue'), dict(active_with_old_owner_day90=12))
extra('N-R14-10', '14 day limit off', minus('N-R14-10', 'limit_14_days'), dict(paused_day14=0, active_with_old_owner_day90=3))
@limit('N-R14-10')
def _():
    r = run('N-R14-10', ALL('N-R14-10') | {'@mailing_list'})
    return dict(unread_mailing_list_accepted_as_owner=r['unread_list_accepted_as_owner'],
                note='the claim check asks only that the owner resolves; a list nobody reads resolves')

# ---------- N-R14-12 overprivileged identities
# 120 permissions, 38 used in 90 days, 6 kept as buffer, so 76 can go. One removed permission serves a quarterly job.
@case('N-R14-12', 'Overprivileged identities', ['right_sizing_report', 'person_approves', 'wildcard_rule'],
      dict(permissions=120, unused_permissions=82),
      dict(permissions=44, removed=76, broken_jobs=1),
      dict(right_sizing_report=True, person_approves=False, wildcard_rule=True))
def _(on):
    removed = 76 if 'right_sizing_report' in on else 0
    broken = (1 if removed else 0) + (1 if (removed and '@annual_job' in on) else 0)
    return dict(permissions=120 - removed, unused_permissions=82 - removed, removed=removed, broken_jobs=broken,
                wildcard_grants_ok=0 if 'wildcard_rule' in on else 2)
extra('N-R14-12', 'report off', minus('N-R14-12', 'right_sizing_report'), dict(removed=0))
extra('N-R14-12', 'approval off', minus('N-R14-12', 'person_approves'), dict(removed=76, permissions=44))
extra('N-R14-12', 'wildcard rule off', minus('N-R14-12', 'wildcard_rule'), dict(wildcard_grants_ok=2))
@limit('N-R14-12')
def _():
    r = run('N-R14-12', ALL('N-R14-12') | {'@annual_job'})
    return dict(annual_job_broken=(r['broken_jobs'] == 2),
                note='90 days of use cannot see a job that runs once a year, so its permission is counted as unused')

# ---------- N-R14-13 rotation on a schedule
# 20 secrets average 400 days old. 3 consumers cache the secret for up to 1 hour. Overlap is 2 hours.
@case('N-R14-13', 'Rotation on a schedule', ['schedule', 'overlap_2h', 'dead_secret_check'],
      dict(rotated=0, avg_age_days=400, outages=0),
      dict(rotated=20, outages=0, old_secrets_valid_after_2h=0),
      dict(schedule=True, overlap_2h=True, dead_secret_check=True))
def _(on):
    rot = 20 if 'schedule' in on else 0
    cache_h = [1, 1, 1] + ([3] if '@long_cache' in on else [])
    if rot:
        overlap_h = 2 if 'overlap_2h' in on else 0
        outages = sum(1 for h in cache_h if h > overlap_h)
        old_valid = 20 if ('overlap_2h' in on and 'dead_secret_check' not in on) else 0
    else:
        outages, old_valid = 0, 0
    return dict(rotated=rot, avg_age_days=0 if rot else 400, outages=outages, old_secrets_valid_after_2h=old_valid)
extra('N-R14-13', 'overlap off', minus('N-R14-13', 'overlap_2h'), dict(outages=3))
extra('N-R14-13', 'dead-secret check off', minus('N-R14-13', 'dead_secret_check'), dict(old_secrets_valid_after_2h=20))
extra('N-R14-13', 'schedule off', minus('N-R14-13', 'schedule'), dict(rotated=0))
@limit('N-R14-13')
def _():
    r = run('N-R14-13', ALL('N-R14-13') | {'@long_cache'})
    return dict(consumer_caching_3h_fails_despite_2h_overlap=(r['outages'] == 1))

# ---------- N-R14-16 retire before you rotate
# 30 identities. 12 unused 90 days or more; 1 of those serves a quarterly job. Disable and hold 30 days, then delete.
# With no hold, retirement is an immediate delete. The use logs miss 2 identities on an older route (limit only).
@case('N-R14-16', 'Retire before you rotate', ['use_check', 'hold_30_days', 'delete_after_hold'],
      dict(rotated=30),
      dict(disabled=12, rotated=18, outages=1, permanent_loss=0),
      dict(use_check=True, hold_30_days=True, delete_after_hold=False))
def _(on):
    if 'use_check' not in on:
        return dict(disabled=0, rotated=30, outages=0, permanent_loss=0)
    retire = 12 + (2 if '@older_route' in on else 0)
    outage = 1 + (2 if '@older_route' in on else 0)
    hold = 'hold_30_days' in on
    return dict(disabled=retire if hold else 0, rotated=30 - retire, outages=outage,
                permanent_loss=0 if hold else outage)
extra('N-R14-16', 'hold off', minus('N-R14-16', 'hold_30_days'), dict(outages=1, permanent_loss=1))
extra('N-R14-16', 'use check off', minus('N-R14-16', 'use_check'), dict(rotated=30))
@limit('N-R14-16')
def _():
    r = run('N-R14-16', ALL('N-R14-16') | {'@older_route'})
    return dict(two_identities_missed_by_logs_were_retired=(r['outages'] == 3),
                note='the use logs do not see an older sign-in route, so a used identity looks idle')

# ---------- P-R15-01 request privileged access with a ticket and an end time
@case('P-R15-01', 'Request privileged access with a ticket and an end time', ['ticket_open', 'end_time', 'second_approver_tier0'],
      dict(granted=10),
      dict(granted=6, refused=4),
      dict(ticket_open=True, end_time=True, second_approver_tier0=True))
def _(on):
    R = [dict(t='open', end=True, tier0=False, second=False)] * 6
    R += [dict(t='closed', end=True, tier0=False, second=False)] * 2
    R += [dict(t='open', end=False, tier0=False, second=False)]
    R += [dict(t='open', end=True, tier0=True, second=False)]
    if '@other_system_ticket' in on: R += [dict(t='open_other_system', end=True, tier0=False, second=False)]
    ok = 0
    for r in R:
        bad = (('ticket_open' in on and r['t'] == 'closed') or ('end_time' in on and not r['end']) or
               ('second_approver_tier0' in on and r['tier0'] and not r['second']))
        ok += not bad
    return dict(granted=ok, refused=len(R) - ok)
extra('P-R15-01', 'ticket check off', minus('P-R15-01', 'ticket_open'), dict(granted=8))
extra('P-R15-01', 'end time rule off', minus('P-R15-01', 'end_time'), dict(granted=7))
extra('P-R15-01', 'second approver off', minus('P-R15-01', 'second_approver_tier0'), dict(granted=7))
extra('P-R15-01', 'open ticket of another system, all controls on', ALL('P-R15-01') | {'@other_system_ticket'}, dict(granted=7))
@limit('P-R15-01')
def _():
    r = run('P-R15-01', ALL('P-R15-01') | {'@other_system_ticket'})
    return dict(ticket_for_other_system_accepted=(r['granted'] == 7),
                note='the check asks whether the ticket is open, not whether it matches the task')

# ---------- P-R15-04 the elevation path is down
# Broker down 2 hours; 5 engineers. Without any fallback, 3 of the 5 use a shared admin password nobody logs.
@case('P-R15-04', 'The elevation path is down', ['second_node', 'break_glass', 'fallback_review'],
      dict(blocked=5, shared_password_used=3),
      dict(blocked=0, break_glass_uses=0, alerts=0),
      dict(second_node=True, fallback_review=False, break_glass=None))
def _(on):
    broker_ok = 'second_node' in on and '@shared_db_failure' not in on
    if broker_ok:
        return dict(blocked=0, break_glass_uses=0, alerts=0, reviews=0, shared_password_used=0)
    if 'break_glass' in on:
        return dict(blocked=0, break_glass_uses=5, alerts=5, reviews=5 if 'fallback_review' in on else 0, shared_password_used=0)
    return dict(blocked=5, break_glass_uses=0, alerts=0, reviews=0, shared_password_used=3)
extra('P-R15-04', 'second node off', minus('P-R15-04', 'second_node'), dict(break_glass_uses=5, alerts=5, reviews=5))
extra('P-R15-04', 'second node and break-glass off', ALL('P-R15-04') - {'second_node', 'break_glass'}, dict(blocked=5, shared_password_used=3))
@limit('P-R15-04')
def _():
    r = run('P-R15-04', ALL('P-R15-04') | {'@shared_db_failure'})
    return dict(second_node_helped=(r['break_glass_uses'] == 0),
                note='both nodes fail for the same reason, so the fallback is used even with the second node')

# ---------- P-R15-06 the person never sees the password
# 10 sessions, 2 users try to reveal, 3 users try a direct login with a password they remember from before.
# Rotation after each session kills that remembered password.
@case('P-R15-06', 'The person never sees the password', ['inject_credential', 'reveal_disabled', 'rotate_after_session'],
      dict(sessions_ok=10, reveals=2, direct_logins_ok=3),
      dict(reveals=0, direct_logins_refused=3),
      dict(inject_credential=True, reveal_disabled=False, rotate_after_session=False))
def _(on):
    reveals = 0 if ('inject_credential' in on or 'reveal_disabled' in on) else 2
    ok = 0 if 'rotate_after_session' in on else 3
    return dict(sessions_ok=10, reveals=reveals, direct_logins_ok=ok, direct_logins_refused=3 - ok)
extra('P-R15-06', 'injection off', minus('P-R15-06', 'inject_credential'), dict(reveals=2, direct_logins_refused=3))
extra('P-R15-06', 'rotation off', minus('P-R15-06', 'rotate_after_session'), dict(direct_logins_refused=3))
@limit('P-R15-06')
def _():
    return dict(keylogger_or_memory_on_target_seen_by_controls=False,
                note='an assertion about my model, not a measurement: none of the three controls inspects the user machine or target memory')

# ---------- P-R15-12 the break-glass drill
# Fault A: the alert routes to a person who left (step 2 fails). Fault B: the sealed copy is held by a person on leave
# (step 3 fails unless a second holder exists, which masks the fault without removing it).
# The routing check compares routing with the on-call list and finds A before any drill.
@case('P-R15-12', 'The break-glass drill', ['routing_check', 'second_holder', 'drill'],
      dict(faults_found=0),
      dict(faults_found=2, faults_fixed=2, steps_pass_second_run=4),
      dict(routing_check=True, second_holder=True, drill=True))
def _(on):
    found = {'alert_routing': None, 'sealed_copy': None}
    if 'routing_check' in on: found['alert_routing'] = 'routing_check'
    first = None
    if 'drill' in on:
        fail = 0
        if found['alert_routing'] is None:
            fail += 1; found['alert_routing'] = 'drill'
        if 'second_holder' not in on:
            fail += 1; found['sealed_copy'] = 'drill'
        first = fail
    n = sum(v is not None for v in found.values())
    return dict(faults_found=n, faults_fixed=n, found_by=found, first_run_failures=first,
                steps_pass_second_run=4 if 'drill' in on else None)
extra('P-R15-12', 'routing check off', minus('P-R15-12', 'routing_check'),
      dict(found_by={'alert_routing': 'drill', 'sealed_copy': None}))
extra('P-R15-12', 'second holder off', minus('P-R15-12', 'second_holder'), dict(first_run_failures=1))
extra('P-R15-12', 'drill off', minus('P-R15-12', 'drill'), dict(faults_found=0))
@limit('P-R15-12')
def _():
    return dict(announced_drill_flatters_result=True,
                note='an assertion about my model: the model has no people in it, so it cannot show that an announced drill is easier than a real night')

# ---------- P-R15-14 shared accounts: who did what
# 4 people, 12 actions, 2 of them inside the window where two sessions overlap. Without check-out the log cannot
# name anyone. The session tag needs a checked-out person to read. `watch` limits "noticed" to attribution,
# as the guess does.
@case('P-R15-14', 'Shared accounts: who did what', ['checkout_names_person', 'session_log_tag', 'password_change'],
      dict(attributed=0),
      dict(attributed=12, ambiguous=0, password_changes=4),
      dict(checkout_names_person=True, session_log_tag=True, password_change=False),
      watch=['attributed', 'ambiguous'])
def _(on):
    co = 'checkout_names_person' in on
    tag = co and 'session_log_tag' in on
    if not co: att, amb = 0, 0
    elif tag: att, amb = 12, 0
    else: att, amb = 10, 2
    out = dict(attributed=att, ambiguous=amb, password_changes=4 if (co and 'password_change' in on) else 0,
               late_login_possible='password_change' not in on)
    if '@handoff' in on: out['attributed_to_wrong_person'] = 1
    return out
extra('P-R15-14', 'log tag off', minus('P-R15-14', 'session_log_tag'), dict(attributed=10, ambiguous=2))
extra('P-R15-14', 'password change off', minus('P-R15-14', 'password_change'), dict(attributed=12, ambiguous=0, late_login_possible=True))
extra('P-R15-14', 'check-out off', minus('P-R15-14', 'checkout_names_person'), dict(attributed=0))
@limit('P-R15-14')
def _():
    r = run('P-R15-14', ALL('P-R15-14') | {'@handoff'})
    return dict(handed_over_session_attributed_to_wrong_person=(r['attributed_to_wrong_person'] == 1 and r['attributed'] == 12))

# ---------- P-R15-20 discover privileged accounts and assign owners
# 38 accounts: directory 14, local admins 6, cloud 9, database admins 5, network 4. The current inventory sees
# directory and cloud. One account per source has a wrong proposed owner (the last person to sign in is not responsible).
@case('P-R15-20', 'Discover privileged accounts and assign owners', ['merge_sources', 'propose_owner', 'owner_confirms'],
      dict(found=23),
      dict(found=38, proposed=38, confirmed=33, wrong_owners_corrected=5),
      dict(merge_sources=True, propose_owner=True, owner_confirms=True))
def _(on):
    src = {'directory': 14, 'local_admin': 6, 'cloud': 9, 'database': 5, 'network': 4}
    seen = src if 'merge_sources' in on else {k: v for k, v in src.items() if k in ('directory', 'cloud')}
    found = sum(seen.values()); wrong = len(seen)
    proposed = found if 'propose_owner' in on else 0
    wrong_p = wrong if proposed else 0
    if 'owner_confirms' in on and proposed:
        confirmed, corrected = proposed - wrong_p, wrong_p
        if '@wrong_confirmer' in on: confirmed, corrected = confirmed + 1, corrected - 1
    else: confirmed, corrected = 0, 0
    return dict(found=found, proposed=proposed, confirmed=confirmed, wrong_owners_corrected=corrected,
                wrong_owners_remaining=wrong_p - corrected)
extra('P-R15-20', 'merge off', minus('P-R15-20', 'merge_sources'), dict(found=23))
extra('P-R15-20', 'confirmation off', minus('P-R15-20', 'owner_confirms'), dict(wrong_owners_remaining=5))
extra('P-R15-20', 'proposal off', minus('P-R15-20', 'propose_owner'), dict(proposed=0))
@limit('P-R15-20')
def _():
    r = run('P-R15-20', ALL('P-R15-20') | {'@wrong_confirmer'})
    return dict(wrong_owner_confirmed_anyway=(r['wrong_owners_remaining'] == 1))

# ---------- P-R15-21 separation of duties inside privileged access
@case('P-R15-21', 'Separation of duties inside privileged access', ['no_self_approval', 'no_policy_approver', 'no_audit_edit'],
      dict(granted=15),
      dict(granted=9, refused=6),
      dict(no_self_approval=True, no_policy_approver=True, no_audit_edit=True))
def _(on):
    R = ['fine'] * 9 + ['self'] * 3 + ['policy'] * 2 + ['audit']
    if '@mutual' in on: R += ['mutual', 'mutual']
    rule = {'self': 'no_self_approval', 'policy': 'no_policy_approver', 'audit': 'no_audit_edit'}
    ok = sum(1 for r in R if not (r in rule and rule[r] in on))
    return dict(granted=ok, refused=len(R) - ok)
extra('P-R15-21', 'self approval rule off', minus('P-R15-21', 'no_self_approval'), dict(granted=12))
extra('P-R15-21', 'policy rule off', minus('P-R15-21', 'no_policy_approver'), dict(granted=11))
extra('P-R15-21', 'audit rule off', minus('P-R15-21', 'no_audit_edit'), dict(granted=10))
extra('P-R15-21', 'two people approve each other, all controls on', ALL('P-R15-21') | {'@mutual'}, dict(granted=11))
@limit('P-R15-21')
def _():
    r = run('P-R15-21', ALL('P-R15-21') | {'@mutual'})
    return dict(mutual_approval_accepted=(r['granted'] == 11), note='each rule looks at one person at a time')

# ---------- P-R15-22 integration with the ticket system, the identity provider and the SIEM
# 20 sessions. The connector drops 6 events when its queue is full (baseline, with or without controls).
# The leaver is removed at the identity provider 1 hour before the vault sync; one session falls in that hour.
@case('P-R15-22', 'Integration with ticket system, identity provider and SIEM', ['ticket_link', 'group_sync', 'heartbeat'],
      dict(tickets_linked=0, siem_events_arrived=0),
      dict(tickets_linked=20, siem_events_arrived=20, heartbeat_alarmed=True, leaver_session_in_gap=1),
      dict(ticket_link=True, group_sync=True, heartbeat=True))
def _(on):
    alarm = ('heartbeat' in on) and ('@heartbeat_shares_queue' not in on)
    return dict(tickets_linked=20 if 'ticket_link' in on else 0,
                siem_events_arrived=20 if alarm else 14, lost_unnoticed=0 if alarm else 6,
                heartbeat_alarmed=alarm, leaver_session_in_gap=1,
                leaver_access_after_sync=('group_sync' not in on))
extra('P-R15-22', 'heartbeat off', minus('P-R15-22', 'heartbeat'), dict(siem_events_arrived=14, lost_unnoticed=6))
extra('P-R15-22', 'sync off', minus('P-R15-22', 'group_sync'), dict(leaver_access_after_sync=True))
extra('P-R15-22', 'ticket link off', minus('P-R15-22', 'ticket_link'), dict(tickets_linked=0))
@limit('P-R15-22')
def _():
    r = run('P-R15-22', ALL('P-R15-22') | {'@heartbeat_shares_queue'})
    return dict(heartbeat_missed_the_loss=(not r['heartbeat_alarmed'] and r['lost_unnoticed'] == 6),
                note='the heartbeat message is dropped by the same full queue it is checking')

# ---------- P-R15-23 endpoint privilege management
# 40 requests: 31 for 3 allowed apps, 6 for 2 other apps that need approval, 2 for a command shell, 1 for a
# renamed copy of the shell. The allow list matches file hashes unless told otherwise.
@case('P-R15-23', 'Endpoint privilege management', ['remove_local_admin', 'allow_list', 'log_elevations'],
      dict(allowed=40),
      dict(allowed=31, refused_or_approval=9, shells_allowed=0, renamed_shell_allowed=False),
      dict(remove_local_admin=True, allow_list=True, log_elevations=False))
def _(on):
    if 'remove_local_admin' not in on:
        return dict(allowed=40, refused_or_approval=0, shells_allowed=2, renamed_shell_allowed=True)
    if 'allow_list' not in on:
        return dict(allowed=0, refused_or_approval=40, shells_allowed=0, renamed_shell_allowed=False)
    renamed = '@match_by_name' in on
    allowed = 31 + (1 if renamed else 0)
    out = dict(allowed=allowed, refused_or_approval=40 - allowed, shells_allowed=0, renamed_shell_allowed=renamed)
    if '@allowed_app_spawns_shell' in on: out['shells_started_by_allowed_apps'] = 1
    return out
extra('P-R15-23', 'local admin removal off', minus('P-R15-23', 'remove_local_admin'), dict(allowed=40))
extra('P-R15-23', 'allow list off', minus('P-R15-23', 'allow_list'), dict(refused_or_approval=40))
extra('P-R15-23', 'list matches file name, not hash', ALL('P-R15-23') | {'@match_by_name'}, dict(renamed_shell_allowed=True))
@limit('P-R15-23')
def _():
    r = run('P-R15-23', ALL('P-R15-23') | {'@allowed_app_spawns_shell'})
    return dict(shell_started_inside_an_allowed_app=(r['shells_started_by_allowed_apps'] == 1),
                note='elevation applies to the allowed application, and its child process inherits it')

# ---------- P-R15-24 session analytics
# 200 sessions: 5 odd (3 off hours, 1 new target, 1 large copy of 950 MB under a 1000 MB threshold) and 195 normal.
# Of the normal ones, 6 happen off hours (on call) and 4 touch a new target (a new project): 10 false flags.
@case('P-R15-24', 'Session analytics', ['off_hours_rule', 'new_target_rule', 'volume_threshold'],
      dict(odd_flagged=0),
      dict(odd_flagged=4, false_positives=10),
      dict(off_hours_rule=True, new_target_rule=True, volume_threshold=False))
def _(on):
    flagged = (3 if 'off_hours_rule' in on else 0) + (1 if 'new_target_rule' in on else 0)
    fp = (6 if 'off_hours_rule' in on else 0) + (4 if 'new_target_rule' in on else 0)
    out = dict(odd_flagged=flagged, odd_missed=5 - flagged, false_positives=fp)
    if '@slow_copy' in on:
        out['slow_copy_sessions_flagged'] = 0
    return out
extra('P-R15-24', 'off hours rule off', minus('P-R15-24', 'off_hours_rule'), dict(odd_flagged=1))
extra('P-R15-24', 'new target rule off', minus('P-R15-24', 'new_target_rule'), dict(odd_flagged=3))
extra('P-R15-24', 'volume threshold off', minus('P-R15-24', 'volume_threshold'), dict(odd_flagged=4))
@limit('P-R15-24')
def _():
    r = run('P-R15-24', ALL('P-R15-24') | {'@slow_copy'})
    return dict(slow_copy_over_many_sessions_flagged=(r['slow_copy_sessions_flagged'] > 0),
                note='20 sessions of 100 MB each stay under the 1000 MB per-session threshold')

# ---------- S-R17-07 AI features inside an approved SaaS app
# 10 users, each can open 100 files, 10 of them HR files, the task needs 5. The scope review and the log have no
# effect on what the assistant reads in this model; only the file limit does.
@case('S-R17-07', 'AI features inside an approved SaaS app', ['scope_review', 'file_limit', 'read_log'],
      dict(files_read_per_user=100, hr_files_exposed=100),
      dict(files_read_per_user=5, hr_files_exposed=0),
      dict(scope_review=False, file_limit=True, read_log=False))
def _(on):
    if 'file_limit' in on:
        hr = 1 if '@paste' in on else 0
        return dict(files_read_per_user=5, hr_files_exposed=hr)
    return dict(files_read_per_user=100, hr_files_exposed=100)
extra('S-R17-07', 'file limit off', minus('S-R17-07', 'file_limit'), dict(hr_files_exposed=100))
@limit('S-R17-07')
def _():
    r = run('S-R17-07', ALL('S-R17-07') | {'@paste'})
    return dict(hr_file_pasted_by_hand_exposed=(r['hr_files_exposed'] == 1),
                note='the limit applies to what the assistant fetches, not to what a user pastes in')

# ---------- S-R17-08 an agent built in a low code tool and never registered
# 6 agents: 2 registered, 4 not and holding live credentials. The scan runs weekly and flags the 4 by day 7.
# 3 owners register by day 10; 1 does not. The issue rule refuses credentials to unregistered agents. The expiry
# disables an agent still unregistered at day 30. Evaluated at day 10 and day 31.
@case('S-R17-08', 'An agent built in a low code tool and never registered', ['weekly_scan', 'issue_rule', 'expiry_30_days'],
      dict(unregistered_with_creds_day10=4),
      dict(found=6, flagged=4, registered_after_request=3, disabled=1),
      dict(weekly_scan=True, issue_rule=True, expiry_30_days=False))
def _(on):
    scan = 'weekly_scan' in on
    flagged = 4 if scan else 0
    registered = 3 if scan else 0
    left = 4 - registered
    c10 = 0 if 'issue_rule' in on else left
    exp = 'expiry_30_days' in on
    out = dict(found=6 if scan else 0, flagged=flagged, registered_after_request=registered,
               disabled=left if exp else 0, unregistered_with_creds_day10=c10,
               unregistered_with_creds_day31=0 if (exp or 'issue_rule' in on) else left)
    if '@personal_account' in on: out['agents_outside_tenant_found'] = 0
    return out
extra('S-R17-08', 'scan off', minus('S-R17-08', 'weekly_scan'), dict(found=0))
extra('S-R17-08', 'issue rule off', minus('S-R17-08', 'issue_rule'), dict(unregistered_with_creds_day10=4))
@limit('S-R17-08')
def _():
    r = run('S-R17-08', ALL('S-R17-08') | {'@personal_account'})
    return dict(agent_under_personal_account_found=(r['agents_outside_tenant_found'] > 0),
                note='the scan reads the tenant app list; an agent under a personal account is not in it')

# ---------- S-R17-09 an agent creates credentials and sub agents for itself
# Attempts: 3 keys and sub agent A by the agent (depth 1), and sub agent B by A (depth 2). The alert fires on each
# creation attempt, before the policy decision.
@case('S-R17-09', 'An agent creates credentials and sub agents for itself', ['no_credential_creation', 'depth_limit_1', 'alert_on_creation'],
      dict(keys=3, sub_agents=2, objects_without_owner=5),
      dict(keys=0, sub_agents=1, alerts=4),
      dict(no_credential_creation=True, depth_limit_1=True, alert_on_creation=True))
def _(on):
    keys = 0 if 'no_credential_creation' in on else 3
    subs = 1 + (0 if 'depth_limit_1' in on else 1)
    attempts = 3 + 1 + 1
    out = dict(keys=keys, sub_agents=subs, refused=attempts - keys - subs,
               alerts=attempts if 'alert_on_creation' in on else 0, objects_without_owner=keys + subs)
    if '@human_creates' in on and 'no_credential_creation' in on: out['keys_created_by_a_person_at_the_agents_request'] = 1
    return out
extra('S-R17-09', 'credential rule off', minus('S-R17-09', 'no_credential_creation'), dict(keys=3))
extra('S-R17-09', 'depth limit off', minus('S-R17-09', 'depth_limit_1'), dict(sub_agents=2))
extra('S-R17-09', 'alert off', minus('S-R17-09', 'alert_on_creation'), dict(refused=4, alerts=0))
@limit('S-R17-09')
def _():
    r = run('S-R17-09', ALL('S-R17-09') | {'@human_creates'})
    return dict(key_created_by_a_person_at_the_agents_request=(r['keys_created_by_a_person_at_the_agents_request'] == 1),
                note='the key is created under a person, outside all three agent-identity controls')
