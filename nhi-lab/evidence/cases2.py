"""13 stretch cases and 6 chain tests (rounds 14, 15, 16, 17). Made-up data only (Kaveri Finance).
Written AFTER the guesses in guesses/guesses-stretch-and-chains.md were committed (78d7e3e).
`on` is the set of controls switched on. Names starting with '@' are scenario markers, not controls.
Chain tests are rule models: each link is stopped by the controls I decided stop it, so the results follow
from my rules. They are weak evidence and are labelled that way."""
CASES = []
def case(id, title, controls, gw, gx):
    def deco(fn):
        CASES.append(dict(id=id, title=title, controls=controls, run=fn, gw=gw, gx=gx, limit=None, extras=[], chain=False))
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

# ---------- N-R14-07 one identity, three names
import re
IDS = [f'svc-{c}{c}x' for c in 'bcdfghjklmnpqrstvwz']  # 19 single-name identities, each with its own owner
MULTI = [(f'billing{i}', 3) for i in range(4)] + [(f'ledger{i}', 2) for i in range(5)]  # 9 identities, 22 names
def _norm(name):
    n = name.lower().replace('@kaveri', '').replace('_', '-')
    n = re.sub(r'(^svc-|-svc$)', '', n)
    return re.sub(r'[-]?\d+$', '', n)  # drop trailing digits, a common normalising choice
@case('N-R14-07', 'One identity, three names', ['owner_match', 'normalise_name'],
      dict(count=51, split_findings=True), dict(count=30, wrong_merges=1))
def _(on):
    entries = [(n, 'owner-' + n) for n in IDS]
    for base, k in MULTI:
        names = [f'svc-{base}', f'{base}-svc@kaveri', base.upper().replace('-', '_')][:k]
        entries += [(n, f'owner-{base}') for n in names]
    # two different accounts that share an owner and differ only by a trailing digit
    entries += [('svc-report1', 'owner-r'), ('svc-report2', 'owner-r')]
    if not ({'owner_match', 'normalise_name'} <= on):
        return dict(count=len(entries), split_findings=True, wrong_merges=0)
    groups = {}
    for n, o in entries: groups.setdefault((o, _norm(n)), []).append(n)
    true_ids = len(IDS) + len(MULTI) + 2  # report1 and report2 are two real accounts
    return dict(count=len(groups), split_findings=False, wrong_merges=true_ids - len(groups))
@limit('N-R14-07')
def _(): return 'my arithmetic was wrong: 9 identities with 2 or 3 names each cannot give 51 entries; and stripping trailing digits merged two real accounts'

# ---------- N-R14-19 scoring
@case('N-R14-19', 'Scoring: rank so the top gets fixed first', ['reach_in_score'],
      dict(tie=True), dict(first='prod-payments', tie=False))
def _(on):
    ids = [('test-tool-key', 40, 1), ('prod-payments', 40, 5)]  # (name, age score, reach)
    sc = sorted(((a + (10*r if 'reach_in_score' in on else 0), n) for n, a, r in ids))
    tie = sc[0][0] == sc[1][0]
    return dict(tie=tie, first=None if tie else sc[-1][1], listed_first=sc[0][1] if tie else sc[-1][1])

# ---------- N-R14-20 verify then close
@case('N-R14-20', 'Close only when the old secret is dead', ['verify_old_dead'],
      dict(closed=5, old_live=2), dict(closed=3, open=2))
def _(on):
    still_live = {1, 4}; closed = open_ = live = 0
    for i in range(5):
        if 'verify_old_dead' in on and i in still_live: open_ += 1
        else:
            closed += 1; live += i in still_live
    return dict(closed=closed, open=open_, old_live=live) if 'verify_old_dead' not in on else dict(closed=closed, open=open_)

# ---------- N-R14-21 agent shares a team key
@case('N-R14-21', 'Agents share a team credential', ['key_per_agent'],
      dict(log_names_agent=False, revoke_hits=4), dict(log_names_agent=True, revoke_hits=1))
def _(on):
    own = 'key_per_agent' in on
    return dict(log_names_agent=own, revoke_hits=1 if own else 4)

# ---------- N-R14-22 person logs in with a service account
@case('N-R14-22', 'A person logs in with a service account', ['block_interactive', 'checkout_names_person'],
      dict(accountable=None, direct_allowed=True), dict(direct_allowed=False, accountable='asha'))
def _(on):
    direct = 'block_interactive' not in on
    acc = 'asha' if ('checkout_names_person' in on and not direct) else None
    return dict(direct_allowed=direct, accountable=acc if not direct else None)
@limit('N-R14-22')
def _(): return dict(copied_password_used_elsewhere_seen=False, note='a password copied during a checkout and used from another tool is not seen by the control')

# ---------- P-R15-10 phishing-resistant MFA
@case('P-R15-10', 'Phishing-resistant MFA for admins', ['passkey', 'no_sms_fallback'],
      dict(bad_through=6), dict(bad_through=0, genuine_ok=4))
def _(on):
    pk, nosms = 'passkey' in on, 'no_sms_fallback' in on
    fatigue = 4 if not pk else 0           # push prompts are accepted only when push is allowed
    sim = 2 if not nosms else 0            # SMS codes are accepted only when SMS is allowed
    return dict(bad_through=fatigue + sim, genuine_ok=4)

# ---------- P-R15-15 vault backups
@case('P-R15-15', 'The vault, its backups and who can read them', ['same_rules', 'alert_nonbackup'],
      dict(nonbackup_reads_ok=5), dict(nonbackup_reads_ok=0, alerts=5))
def _(on):
    return dict(nonbackup_reads_ok=0 if 'same_rules' in on else 5, alerts=5 if 'alert_nonbackup' in on else 0)

# ---------- P-R15-16 help-desk reset path
@case('P-R15-16', 'Help desk reset path', ['strong_proof', 'notice_and_delay'],
      dict(attacker_resets_ok=2), dict(attacker_resets_ok=0))
def _(on):
    ok = 0
    for attacker in (True, True, False, False, False, False):
        if not attacker: continue
        refused = 'strong_proof' in on                       # the attacker knows a name and a phone number only
        caught = 'notice_and_delay' in on                    # the real person sees the notice during the delay and says no
        ok += 0 if (refused or caught) else 1
    return dict(attacker_resets_ok=ok)
@limit('P-R15-16')
def _(): return dict(person_approves_the_notice_account_lost=True, note='if the real person is also tricked into approving the notice, the account is lost with both controls on')

# ---------- P-R15-19 vendor at 2 a.m.
@case('P-R15-19', 'A vendor is needed at 2 a.m.', ['approve_and_record', 'auto_expiry'],
      dict(active_after_3h=True, recorded=False), dict(active_after_3h=False, recorded=True))
def _(on):
    return dict(active_after_3h='auto_expiry' not in on, recorded='approve_and_record' in on)

# ---------- P-R15-25 mass rotation
@case('P-R15-25', 'Mass rotation after a breach', ['consumer_first', 'dry_run'],
      dict(outages=12), dict(outages=0, unrotated=2))
def _(on):
    known, unowned = 10, 2          # 12 consumers fail; 2 of them have no owner so nobody knows their consumers
    out = 0
    if 'consumer_first' not in on: out += known
    if 'dry_run' not in on: out += unowned        # without a dry run the unowned secrets are rotated blind
    unrot = 2 if 'dry_run' in on else 0
    return dict(outages=out, unrotated=unrot)

# ---------- S-R17-02 AI tool inherits full permissions
@case('S-R17-02', 'AI tool inherits the full permissions of the person', ['scope_read_one'],
      dict(writable=40), dict(readable=1, writable=0))
def _(on):
    return dict(readable=1, writable=0) if 'scope_read_one' in on else dict(readable=40, writable=40)

# ---------- S-R17-06 AI-service keys in repositories
@case('S-R17-06', 'AI-service keys leak into repositories', ['scan_revoke', 'rotate_90d'],
      dict(valid=6), dict(revoked_on_find=5, valid=1))
def _(on):
    keys = [dict(std=True, old=True), dict(std=True, old=True), dict(std=True, old=False), dict(std=True, old=False),
            dict(std=True, old=False), dict(std=False, old=False)]    # one non-standard prefix, not old
    valid = 0; found = 0
    for k in keys:
        gone = False
        if 'scan_revoke' in on and k['std']: gone = True; found += 1
        if 'rotate_90d' in on and k['old']: gone = True
        valid += not gone
    return dict(revoked_on_find=found, valid=valid)

# ---------- S-R17-10 automations outlive the test window
@case('S-R17-10', 'Scheduled automations outlive the test window', ['end_date_at_creation', 'sweep'],
      dict(running=5), dict(disabled=4, running=1))
def _(on):
    extended = 1   # one workflow was extended; the reason is text and is not checked
    if {'end_date_at_creation', 'sweep'} <= on: return dict(disabled=5 - extended, running=extended)
    return dict(disabled=0, running=5)
@limit('S-R17-10')
def _(): return dict(extension_reason_checked=False, note='an extension is accepted on any written reason')

# ---------------- chain tests (round 16): rule models ----------------
def chain(id, title, links, controls, gw, gx):
    """controls: name -> (link index it stops at, or None) ; 'stops' are rules I chose."""
    def deco(fn):
        CASES.append(dict(id=id, title=title, controls=list(controls), links=links, rules=controls, run=fn, gw=gw, gx=gx, limit=None, extras=[], chain=True))
        return fn
    return deco
def _walk(links, rules, on, skip=()):
    stop = None; detected = None
    for name, (idx, kind) in rules.items():
        if name not in on or name in skip: continue
        if kind == 'stop' and (stop is None or idx < stop): stop = idx
        if kind == 'detect' and (detected is None or idx < detected): detected = idx
    return dict(stopped_at=stop, reached_end=stop is None, detected_at=detected)

L1 = ['No owner', 'Password never rotated, copied to a ticket', 'Ticket export shared outside', 'Sign-in from a new network']
R1 = {'owner_required': (1, 'stop'), 'secret_scan_tickets': (2, 'stop'), 'rotation': (4, 'stop')}
@chain('C-R16-C01', 'The forgotten service account', L1, R1, dict(reached_end=True), dict(stopped_at=1, best_alone='secret_scan_tickets'))
def _(on):
    r = dict(R1)
    if '@legacy' in on: r['owner_required'] = (1, 'none')   # owner_required cannot fix an account that already exists
    return _walk(L1, r, on)
extra('C-R16-C01', 'account already exists (legacy), owner rule cannot apply', {'owner_required', 'secret_scan_tickets', 'rotation', '@legacy'}, dict(stopped_at=2))

L2 = ['Token committed', 'Repository cloned', 'Scanner finds it (7 days later)', 'Attacker calls the cloud API']
@chain('C-R16-C02', 'The token in the repository', L2, {'commit_block': (1, 'stop'), 'short_lived': (4, 'stop'), 'revoke_on_find': (4, 'stop')},
       dict(reached_end=True), dict(stopped_at=1, short_lived_alone_stops=True))
def _(on):
    delay = 0.5 if '@fast_finder' in on else 7; ttl = 1
    r = {'commit_block': (1, 'stop'), 'short_lived': (4, 'stop' if delay > ttl else 'none'), 'revoke_on_find': (4, 'stop' if delay < 0.25 else 'none')}
    return _walk(L2, r, on)
extra('C-R16-C02', 'the finder is faster than the token lifetime (12 hours)', {'short_lived', '@fast_finder'}, dict(reached_end=True))

L4 = ['No end date', 'Contract ends in agency records only', 'Account stays active', 'Phished credential used']
@chain('C-R16-C04', 'The contractor who never left', L4, {'end_date_expiry': (3, 'stop'), 'sponsor_review': (3, 'stop')},
       dict(reached_end=True), dict(stopped_at=3, sponsor_review_alone_leaves_window=True))
def _(on):
    attack_day_after_end = 120 if '@late' in on else 30; review_gap_max = 90
    r = {'end_date_expiry': (3, 'stop'), 'sponsor_review': (3, 'stop' if attack_day_after_end > review_gap_max else 'none')}
    return _walk(L4, r, on)
extra('C-R16-C04', 'attack 120 days after contract end, sponsor review runs at 90', {'sponsor_review', '@late'}, dict(stopped_at=3))

L5 = ['Break-glass used in an incident', 'Password pasted in chat', 'Not rotated', 'Reused with no emergency']
R5 = {'alert_every_use': (4, 'detect'), 'rotate_on_return': (3, 'stop')}
@chain('C-R16-C05', 'The break-glass password everyone knows', L5, R5, dict(reached_end=True), dict(stopped_at=3, detected_at=4))
def _(on): return _walk(L5, R5, on)

L6 = ['Many approvals a day', 'One-click approving', 'Hostile request among the routine ones', 'Change approved']
R6 = {'batch_limits': (1, 'none'), 'risk_shown_first': (3, 'detect'), 'second_approver_high_risk': (4, 'stop')}
@chain('C-R16-C06', 'Approval fatigue', L6, R6, dict(reached_end=True), dict(stopped_at=4))
def _(on): return _walk(L6, R6, on)
@limit('C-R16-C06')
def _(): return 'the rule model says risk-first display only flags the request. Whether a tired approver acts on the flag is human behaviour, which this model does not test'

L17 = ['Vault in place', 'Direct login still works', 'Old password known', 'Vault and recording bypassed']
R17 = {'block_direct_login': (2, 'stop'), 'checkin_alert': (4, 'detect')}
@chain('C-R16-C17', 'The old door', L17, R17, dict(reached_end=True), dict(stopped_at=2))
def _(on): return _walk(L17, R17, on)
