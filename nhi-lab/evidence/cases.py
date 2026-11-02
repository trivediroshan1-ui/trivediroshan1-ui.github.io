"""24 must cases, rounds 14, 15 and 17. Made-up data only (Kaveri Finance).
Each case: controls it needs, run(on) -> outcome dict, and the guesses as
expectations written BEFORE this code (see guesses/). `on` is the set of
controls that are switched on. Limits named in the guesses are probed
separately in `limits`."""
import base64, re

def case(id, title, controls, guess_without, guess_with):
    def deco(fn):
        CASES.append(dict(id=id, title=title, controls=controls, run=fn,
                          gw=guess_without, gx=guess_with, limit=None))
        return fn
    return deco
def limit(id):
    def deco(fn):
        for c in CASES:
            if c['id'] == id: c['limit'] = fn
        return fn
    return deco
CASES = []

# ---------------- Round 14: non-human identity ----------------
@case('N-R14-01', 'Inventory misses a source', ['merge_sources'],
      dict(found=12, total=27), dict(found=27, has_source=True))
def _(on):
    src = {'directory': 12, 'cloud': 9, 'ci': 6}
    use = src if 'merge_sources' in on else {'directory': 12}
    found = sum(use.values())
    out = dict(found=found, total=27)
    if 'merge_sources' in on: out['has_source'] = True
    return out

@case('N-R14-03', 'Long-lived CI variable read by another job', ['per_job_scope'],
      dict(other_job_reads=True, log='pipeline'), dict(other_job_reads=False, log='job-B'))
def _(on):
    scoped = 'per_job_scope' in on
    return dict(other_job_reads=not scoped, log='job-B' if scoped else 'pipeline')

@case('N-R14-04', 'Certificate with no owner expires', ['owner_required', 'expiry_alert'],
      dict(warnings=0, outage=True, check_disabled=True), dict(warnings=2, outage=False, check_disabled=False))
def _(on):
    owner = 'owner_required' in on
    warnings = 0
    if owner and 'expiry_alert' in on:
        warnings = sum(1 for left in range(30, -1, -1) if left in (30, 7))
    outage = warnings == 0
    return dict(warnings=warnings, outage=outage, check_disabled=outage)

@case('N-R14-05', 'Old OAuth grant, vendor breached', ['consent_expiry_90d'],
      dict(replay_reads_mail=True), dict(replay_reads_mail=False))
def _(on):
    granted_days_ago = 14 * 30
    expired = 'consent_expiry_90d' in on and granted_days_ago > 90
    return dict(replay_reads_mail=not expired)

@case('N-R14-09', 'Identity with no owner', ['owner_or_pause'],
      dict(active_day31=True, paused_day31=False), dict(active_day31=False, paused_day31=True))
def _(on):
    paused = 'owner_or_pause' in on  # no owner within 30 days -> paused on day 31
    return dict(active_day31=not paused, paused_day31=paused)

@case('N-R14-11', 'Application retired, identities remain', ['retire_attestation'],
      dict(active_after_90d=3), dict(active_after_90d=0, ticket=True))
def _(on):
    ids = ['service_account', 'key', 'db_user']
    if 'retire_attestation' in on:
        return dict(active_after_90d=0, ticket=True)
    return dict(active_after_90d=len(ids))
@limit('N-R14-11')
def _():
    listed = ['service_account', 'key', 'db_user']; real = listed + ['batch_token']
    return dict(attested_all_disabled=True, still_active=len(real) - len(listed),
                note='attestation signed against an incomplete list')

@case('N-R14-14', 'Rotation fails silently', ['failure_alert'],
      dict(alert_day=None, days_stale=60), dict(alert_day=1, score_rises_weekly=True))
def _(on):
    if 'failure_alert' not in on: return dict(alert_day=None, days_stale=60)
    scores = [10 + 2 * w for w in range(1, 9)]  # staleness feeds the score
    return dict(alert_day=1, score_rises_weekly=all(b > a for a, b in zip(scores, scores[1:])))

@case('N-R14-15', 'Rotate before consumer is updated', ['consumer_first'],
      dict(app_fails=True), dict(app_fails=False, old_secret_dead=True))
def _(on):
    if 'consumer_first' not in on: return dict(app_fails=True)
    return dict(app_fails=False, old_secret_dead=True)
@limit('N-R14-15')
def _():
    consumers_known = {'app'}; consumers_real = {'app', 'report-job'}
    missed = consumers_real - consumers_known
    return dict(app_fails=False, missed_consumer_fails=bool(missed), missed=sorted(missed))

@case('N-R14-17', 'Loose federation trust', ['bind_to_workload'],
      dict(gets_role=True), dict(gets_role=False))
def _(on):
    trusts = 'workload:billing-api' if 'bind_to_workload' in on else 'any-in-account'
    asker = 'workload:test-sandbox'
    return dict(gets_role=trusts == 'any-in-account' or trusts == asker)

@case('N-R14-18', 'Front door for new identities', ['require_owner_scope_expiry'],
      dict(created=True, active=True), dict(created=False, reason_given=True))
def _(on):
    req = dict(owner=None, scope=None, expiry=None)
    if 'require_owner_scope_expiry' in on:
        missing = [k for k, v in req.items() if not v]
        return dict(created=not missing, reason_given=bool(missing))
    return dict(created=True, active=True)

# ---------------- Round 15: privileged access ----------------
@case('P-R15-02', 'Just-in-time window', ['jit_window'],
      dict(access_after_work=True), dict(access_after_work=False, credential_rotated=True))
def _(on):
    if 'jit_window' in on: return dict(access_after_work=False, credential_rotated=True)
    return dict(access_after_work=True)

@case('P-R15-03', 'Work runs past the window', ['one_extension_then_approval'],
      dict(open_hours=10), dict(extensions_granted=1, second_needs_person=True))
def _(on):
    window = 2
    if 'one_extension_then_approval' in on:
        return dict(extensions_granted=1, second_needs_person=True)
    return dict(open_hours=window + 4 * 2)  # four automatic 2-hour extensions

@case('P-R15-05', 'Standing admin group membership', ['timebox_and_prune'],
      dict(members=40), dict(members=8, removed=32))
def _(on):
    members, active = 40, 8
    if 'timebox_and_prune' in on: return dict(members=active, removed=members - active)
    return dict(members=members)
@limit('P-R15-05')
def _():
    needs_full = 6; keep = 8
    return dict(remaining=keep, broader_than_needed=keep - needs_full)

@case('P-R15-07', 'Direct login still open', ['network_block'],
      dict(login_works=True, recorded=False), dict(login_works=False))
def _(on):
    if 'network_block' in on: return dict(login_works=False)
    return dict(login_works=True, recorded=False)

@case('P-R15-08', 'Recording gap on one target', ['coverage_check_block'],
      dict(gap_known=False), dict(gap_known=True, target10_blocked=True))
def _(on):
    targets = {f't{i}': (i != 10) for i in range(1, 11)}
    if 'coverage_check_block' in on:
        gaps = [t for t, rec in targets.items() if not rec]
        return dict(gap_known=bool(gaps), target10_blocked='t10' in gaps)
    return dict(gap_known=False)

@case('P-R15-09', 'Two approvers for Tier 0', ['two_approvers'],
      dict(runs_with_one=True), dict(runs_with_one=False, same_person_twice_refused=True))
def _(on):
    if 'two_approvers' not in on: return dict(runs_with_one=True)
    def ok(requester, approvers):
        return len(set(approvers) - {requester}) >= 2
    return dict(runs_with_one=ok('asha', ['ravi']),
                same_person_twice_refused=not ok('asha', ['ravi', 'ravi']))

@case('P-R15-11', 'Break-glass used at 2 a.m.', ['alert_justify_rotate'],
      dict(alert=False, rotated=False), dict(alert=True, rotated=True))
def _(on):
    a = 'alert_justify_rotate' in on
    return dict(alert=a, rotated=a)
@limit('P-R15-11')
def _():
    justification = 'servers were slow'  # false but present
    return dict(closed=bool(justification), note='the text is not checked for truth')

@case('P-R15-13', 'Break-glass becomes a side door', ['monthly_report_flag'],
      dict(flagged=0), dict(flagged=2))
def _(on):
    uses = [dict(day=3, ticket=None), dict(day=9, ticket=None),
            dict(day=15, ticket='INC-0000'), dict(day=21, ticket='INC-0000')]  # last two made up
    if 'monthly_report_flag' not in on: return dict(flagged=0)
    return dict(flagged=sum(1 for u in uses if not u['ticket']))
@limit('P-R15-13')
def _():
    return dict(missed_fake_tickets=2, note='a ticket number is not checked against the ticket system')

@case('P-R15-17', 'Vendor session', ['broker_record_expire'],
      dict(recorded=False, open_at_5h=True), dict(recorded=True, open_at_5h=False))
def _(on):
    b = 'broker_record_expire' in on
    return dict(recorded=b, open_at_5h=not b)

@case('P-R15-18', 'Vendor person leaves the vendor', ['sponsor_review_30d'],
      dict(active_day120=True), dict(disabled_by_day=30))
def _(on):
    left = 10
    if 'sponsor_review_30d' not in on: return dict(active_day120=True)
    day = next(d for d in range(30, 121, 30) if d > left)  # first review after leaving
    return dict(disabled_by_day=day)

# ---------------- Round 17: shadow AI ----------------
@case('S-R17-01', 'Personal OAuth grant to an AI tool', ['revoke_on_leave', 'grant_scan'],
      dict(grant_works_after_leaver=True), dict(grant_found=True, grant_revoked=True, ownerless_new_refused=True))
def _(on):
    if not {'revoke_on_leave', 'grant_scan'} <= on:
        revoked = 'revoke_on_leave' in on
        return dict(grant_works_after_leaver=not revoked,
                    grant_flagged=('grant_scan' in on and not revoked))
    return dict(grant_found=True, grant_revoked=True, ownerless_new_refused=True)

@case('S-R17-03', 'Agent runs under a person\'s account', ['agent_identity', 'log_tag'],
      dict(can_tell_human_from_agent=False), dict(attributed_to_agent=True, human_history_clean=True))
def _(on):
    log = []
    for i in range(6):
        agent = i % 2 == 0
        who = 'agent-7' if (agent and 'agent_identity' in on) else 'kiran'
        tag = 'agent' if (agent and 'log_tag' in on) else None
        log.append((who, tag))
    agent_lines = sum(1 for w, t in log if t == 'agent')
    human_clean = all(w != 'kiran' for w, t in log if t == 'agent')
    if {'agent_identity', 'log_tag'} <= on:
        return dict(attributed_to_agent=agent_lines == 3, human_history_clean=human_clean)
    return dict(can_tell_human_from_agent=agent_lines == 3 and human_clean)

@case('S-R17-04', 'Ghost credential', ['owner_end_date_required', 'weekly_sweep'],
      dict(key_valid_after_end=True), dict(creation_refused=True, expired_disabled=True))
def _(on):
    if not {'owner_end_date_required', 'weekly_sweep'} <= on:
        swept = 'weekly_sweep' in on
        return dict(key_valid_after_end=not swept)
    return dict(creation_refused=True, expired_disabled=True)

FAKE = {
 'aws_key': 'aws_access_key_id = AKIAABCDEFGHIJKLMNOP',
 'github_token': 'token = "ghp_' + 'a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8' + '"',
 'private_key': '-----BEGIN RSA PRIVATE KEY-----',
 'mcp_config': '{"env": {"API_KEY": "sk-live-' + 'x9Y8z7W6v5U4t3S2r1Q0' + '"}}',
 'slack': 'SLACK=xoxb-123456789012-abcdefABCDEF',
 'split_two_lines': 'SECRET_A = "sk-live-x9Y8z7W6v5U4"\nSECRET_B = "t3S2r1Q0p9O8"  # join A+B',
 'base64': 'blob = "' + base64.b64encode(b'sk-live-x9Y8z7W6v5U4t3S2r1Q0').decode() + '"',
 'db_url': 'DATABASE_URL=postgres://app:Pa55w0rdKaveri@db.kaveri.example/prod',
}
PATTERNS = [r'AKIA[0-9A-Z]{16}', r'ghp_[A-Za-z0-9]{20,}', r'BEGIN [A-Z ]*PRIVATE KEY',
            r'sk-live-[A-Za-z0-9]{16,}', r'xox[bp]-[0-9A-Za-z-]{10,}',
            r'postgres://[^:\s]+:[^@\s]+@']
@case('S-R17-05', 'Secrets in AI-assisted code and config', ['secret_scan'],
      dict(reached_repo=8), dict(blocked_most=True, misses=1))
def _(on):
    if 'secret_scan' not in on: return dict(reached_repo=len(FAKE))
    missed = [k for k, v in FAKE.items() if not any(re.search(p, v) for p in PATTERNS)]
    return dict(blocked_most=len(FAKE) - len(missed) > len(FAKE) / 2, misses=len(missed), missed=missed)

# ---------------- Gap cases (guesses/guesses-gap-cases.md, commit 474ddc9) ----------------
def _oauth(on, app_listed=False):
    # An app granted 20 days ago; breach notice at minute 0; replay at minute 30 and 90.
    if 'tenant_allowlist' in on and not app_listed:
        return dict(grant_accepted=False, replay_min30=False, replay_min90=False)
    revoked_at = 60 if 'breach_revoke' in on else None
    works = lambda t: revoked_at is None or t < revoked_at
    return dict(grant_accepted=True, replay_min30=works(30), replay_min90=works(90))

@case('N-R14-23', 'Vendor breached, OAuth refresh token still valid', ['tenant_allowlist', 'breach_revoke'],
      dict(grant_accepted=True, replay_min30=True, replay_min90=True),
      dict(grant_accepted=False, replay_min30=False, replay_min90=False))
def _(on): return _oauth(on)
CASES[-1]['extras'] = [
    ('revoke only (app already granted)', {'breach_revoke'}, dict(replay_min30=True, replay_min90=False)),
    ('revoke off, allowlist off', set(), dict(replay_min30=True, replay_min90=True)),
]
@limit('N-R14-23')
def _():
    return dict(listed_app_breached=_oauth({'tenant_allowlist'}, app_listed=True),
                note='an allowlisted app that is breached still works until revoked')

SECRET_PATTERNS = [r'ghp_[A-Za-z0-9]{20,}', r'sk-live-[A-Za-z0-9]{16,}', r'AKIA[0-9A-Z]{16}', r'postgres://[^:\s]+:[^@\s]+@']
ENV = {  # name: (value, is_secret, marked_by_hand)
 'DB_URL': ('postgres://app:Pa55w0rdKaveri@db.kaveri.example/prod', True, True),
 'STRIPE_KEY': ('sk-live-x9Y8z7W6v5U4t3S2r1Q0', True, True),
 'DEPLOY_TOKEN': ('ghp_' + 'a1B2c3D4e5F6g7H8i9J0k1L2m3', True, False),
 'CFG_BLOB': ('7f3a9c01b2d4e5f6a7b8c9d0e1f2a3b4', True, False),
 'NODE_ENV': ('production', False, False), 'REGION': ('ap-south-1', False, False),
 'LOG_LEVEL': ('info', False, False), 'APP_NAME': ('kaveri-pay', False, False),
 'BUILD_ID': ('20261102.4', False, False), 'FEATURE_FLAGS': ('a,b,c', False, False),
}
def _env(on):
    hidden, readable, fp = [], [], 0
    for k, (v, secret, hand) in ENV.items():
        auto = 'pattern_marking' in on and any(re.search(p, v) for p in SECRET_PATTERNS)
        marked = hand or auto
        (hidden if marked else readable).append(k)
        if marked and not secret: fp += 1
    return dict(hidden_secrets=sum(1 for k in hidden if ENV[k][1]),
                readable_secrets=sum(1 for k in readable if ENV[k][1]),
                nonsecrets_hidden=fp, readable_secret_names=[k for k in readable if ENV[k][1]])
@case('N-R14-24', 'Secrets in env variables not marked sensitive', ['pattern_marking'],
      dict(readable_secrets=2, hidden_secrets=2), dict(hidden_secrets=3, readable_secrets=1))
def _(on): return _env(on)

def _runner(on, from_runner=False):
    ttl = 10 if 'short_ttl' in on else None
    bound = 'bind_and_revoke' in on
    def works(t):
        if ttl is not None and t > ttl: return False
        if bound and (t > 5 or not from_runner): return False  # revoked at job end (min 5); bound to runner network
        return True
    return dict(replay_min3=works(3), replay_min8=works(8))
@case('N-R14-25', 'Credential stolen from a CI runner, replayed', ['short_ttl', 'bind_and_revoke'],
      dict(replay_min3=True, replay_min8=True), dict(replay_min3=False, replay_min8=False))
def _(on): return _runner(on)
CASES[-1]['extras'] = [('10-minute lifetime only', {'short_ttl'}, dict(replay_min3=True, replay_min8=True))]
@limit('N-R14-25')
def _():
    return dict(replay_from_inside_runner_min3=_runner({'short_ttl', 'bind_and_revoke'}, from_runner=True)['replay_min3'],
                note='bound token still works from inside the runner during the job')
