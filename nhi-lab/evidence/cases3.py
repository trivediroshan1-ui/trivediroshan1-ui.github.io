"""Round 18: two cases. N-R18-01 insecure authentication (NHI4), N-R18-02 environment isolation (NHI8).
Made-up data only (Kaveri Finance). Written AFTER guesses/guesses-round-18.md was committed (e50df1b).
`on` is the set of controls switched on. Names starting with '@' are scenario markers, not controls.
Small in-memory models of the controls, written by the same person who wrote the guesses."""
from fnmatch import fnmatchcase
CASES = []
def case(id, title, controls, gw, gx):
    def deco(fn):
        CASES.append(dict(id=id, title=title, controls=controls, run=fn, gw=gw, gx=gx, limit=None, extras=[]))
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

# ---------- N-R18-01 a copied key from another network (NHI4)
# 12 calls: 6 genuine from the billing workload, 3 replays of the current key from an unknown network,
# 3 calls with the old key (rotated 2 days ago) from the same unknown network.
# workload_binding: a call must also carry the workload's own certificate.
# revoke_old: the old key is refused. alert_new_network: one alert the first time a network is seen using the key.
@case('N-R18-01', 'A copied key from another network', ['workload_binding', 'revoke_old', 'alert_new_network'],
      dict(accepted=12, refused=0, can_tell_apart=False),
      dict(accepted=6, refused=6, alerts=3))
def _(on):
    three = '@three_networks' in on
    calls = [dict(kind='genuine', key='current', cert=True, net='billing-net') for _ in range(6)]
    calls += [dict(kind='replay', key='current', cert=False, net=(f'net-{i}' if three else 'unknown-net')) for i in range(3)]
    calls += [dict(kind='old', key='old', cert=False, net=('net-0' if three else 'unknown-net')) for _ in range(3)]
    if '@compromised_host' in on:
        calls.append(dict(kind='host', key='current', cert=True, net='billing-net'))
    known, alerts, acc, ref, rep_acc, old_ref = {'billing-net'}, 0, 0, 0, 0, 0
    for c in calls:
        if 'alert_new_network' in on and c['net'] not in known:
            alerts += 1; known.add(c['net'])
        refused = ('workload_binding' in on and not c['cert']) or ('revoke_old' in on and c['key'] == 'old')
        if refused:
            ref += 1; old_ref += c['kind'] == 'old'
        else:
            acc += 1; rep_acc += c['kind'] == 'replay'
    return dict(accepted=acc, refused=ref, alerts=alerts, replays_accepted=rep_acc, old_key_refused=old_ref,
                can_tell_apart='workload_binding' in on)
extra('N-R18-01', 'binding off', {'revoke_old', 'alert_new_network'}, dict(replays_accepted=3, old_key_refused=3))
extra('N-R18-01', 'revocation off', {'workload_binding', 'alert_new_network'}, dict(accepted=6, refused=6))
extra('N-R18-01', 'alert off', {'workload_binding', 'revoke_old'}, dict(refused=6, alerts=0))
extra('N-R18-01', 'replays from three different networks, all controls on',
      {'workload_binding', 'revoke_old', 'alert_new_network', '@three_networks'}, dict(alerts=3))
@limit('N-R18-01')
def _():
    r = CASES[0]['run']({'workload_binding', 'revoke_old', 'alert_new_network', '@compromised_host'})
    return dict(call_from_inside_the_real_workload_accepted=(r['accepted'] == 7),
                note='a replay from inside the real billing workload carries the certificate, so the binding cannot see it')

# ---------- N-R18-02 a test credential that opens production (NHI8)
# 6 normal test runs and 2 attempts from a compromised test runner at the production database.
# separate_identity: test pipeline has its own identity with default deny on production.
# path_restriction: explicit deny on the production path prefix for test identities.
# alert_test_asks_prod: alert when a test identity asks for a path under the production prefix (needs a separate identity).
PROD = '/kaveri/prod/'
@case('N-R18-02', 'A test credential that opens production', ['separate_identity', 'path_restriction', 'alert_test_asks_prod'],
      dict(normal_ok=6, attacks_succeeded=2),
      dict(normal_ok=6, attacks_refused=2, alerts=2))
def _(on):
    legacy = '@legacy_wildcard' in on
    sep = 'separate_identity' in on
    grants = (['/kaveri/test/*'] + (['/kaveri/*/db'] if legacy else [])) if sep else ['/kaveri/*']
    deny = [PROD] if ('path_restriction' in on and sep) else []
    def allowed(p): return any(fnmatchcase(p, g) for g in grants) and not any(p.startswith(d) for d in deny)
    attacks = ['/kaveri/prod/db', '/kaveri/legacy/db'] if legacy else ['/kaveri/prod/db'] * 2
    normal_ok = sum(allowed('/kaveri/test/db') for _ in range(6))
    ok = [a for a in attacks if allowed(a)]
    alerts = sum(a.startswith(PROD) for a in attacks) if ('alert_test_asks_prod' in on and sep) else 0
    return dict(normal_ok=normal_ok, attacks_succeeded=len(ok), attacks_refused=len(attacks) - len(ok),
                alerts=alerts, readable_prod_secrets=len(set(ok)))
extra('N-R18-02', 'separate identity off', {'path_restriction', 'alert_test_asks_prod'}, dict(attacks_succeeded=2))
extra('N-R18-02', 'path restriction off', {'separate_identity', 'alert_test_asks_prod'}, dict(attacks_refused=2))
extra('N-R18-02', 'alert off', {'separate_identity', 'path_restriction'}, dict(attacks_refused=2, alerts=0))
extra('N-R18-02', 'one production secret under a wildcard path, all controls on',
      {'separate_identity', 'path_restriction', 'alert_test_asks_prod', '@legacy_wildcard'}, dict(readable_prod_secrets=1))
@limit('N-R18-02')
def _():
    return dict(prod_data_copied_into_test_seen_by_controls=False,
                note='a refresh job copies production rows into the test database under the production identity. None of the three controls inspects data, so this is an assertion about my model, not a measurement')
