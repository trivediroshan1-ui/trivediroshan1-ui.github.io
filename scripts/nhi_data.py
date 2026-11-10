"""Shared data for the NHI lab pages, the audit files and the PDF book.
Everything here is read from nhi-lab/evidence (results and guess files) or typed once below."""
import json, os, re, hashlib, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, 'nhi-lab', 'evidence')

# id: (group, short trigger, without, with)
T = {
'N-R14-01': ('discover','Three places hold service accounts','Directory-only scan finds 12 of 27','All three sources merged: 27 of 27, each with its source'),
'N-R14-03': ('control','Another job reads a 400-day-old CI key','The other job reads it. Log says only "pipeline"','Per-job credential: refused, log names the job'),
'N-R14-04': ('credential','A certificate with no owner expires','No warning, outage, someone switches a check off','Owner warned at 30 and 7 days, no outage'),
'N-R14-05': ('credential','Vendor tokens stolen; grant is 14 months old','Replayed token still reads mail','Grant had expired at 90 days: refused'),
'N-R14-09': ('own','A key with no named owner','Still active on day 31','Paused on day 31'),
'N-R14-11': ('own','App retired, its identities stay','All 3 still work 90 days later','All 3 disabled, ticket recorded'),
'N-R14-14': ('credential','Rotation job fails for 60 days','Nobody knows; password 60 days stale','Alert on day 1, score rises weekly'),
'N-R14-15': ('credential','Password rotated before the app is updated','The application fails at next connection','Consumer first, then rotate, old secret verified dead'),
'N-R14-17': ('control','Low-value workload asks for a high-value role','Gets the role','Trust bound to one workload: refused'),
'N-R14-18': ('control','New service account, no owner, scope or expiry','Created and active','Refused, with the reason'),
'P-R15-02': ('privileged','Engineer needs 2 hours on one database','Access stays after the work','Closes by itself, credential rotated'),
'P-R15-03': ('privileged','The job needs 90 more minutes','Extended again and again: 10 hours','One extension, then a person must approve'),
'P-R15-05': ('privileged','Admin group of 40, 8 did privileged work','All 40 keep access','32 removed, 8 remain'),
'P-R15-07': ('privileged','Engineer signs in directly with an old password','Login works, nothing recorded','Blocked at the network'),
'P-R15-08': ('privileged','Nine of ten targets are recorded','Nobody knows about the tenth','Tenth found and blocked'),
'P-R15-09': ('privileged','Change to the identity system, one approver','Runs','Waits for a second, different person'),
'P-R15-11': ('privileged','Break-glass account used at 2 a.m.','Unnoticed, password unchanged','Alert fires, password rotated'),
'P-R15-13': ('privileged','Break-glass used for routine work, 4 days','No one notices','2 uses with no ticket flagged'),
'P-R15-17': ('privileged','Vendor engineer connects for 4 hours','No record, access stays','Recorded and closed at 4 hours'),
'P-R15-18': ('privileged','Vendor person leaves their company','Account still active at 120 days','Disabled at the next 30-day review'),
'S-R17-01': ('shadow','Employee grants an AI tool access, then leaves','Grant keeps working','Found and revoked; ownerless grants refused'),
'S-R17-03': ('shadow','An automation uses a person\'s login','Log cannot tell human from agent','Agent has its own identity and log tag'),
'S-R17-04': ('shadow','AI workflow makes a key with no owner','Key stays valid forever','Refused at creation; sweep disables expired keys'),
'S-R17-05': ('shadow','AI-written code and MCP config hold secrets','All 8 fake secrets reach the repository','6 of 8 blocked; 2 get through'),
'N-R14-23': ('gap','Vendor breached; refresh token still valid','Grant accepted, replay reads files','Allowlist refuses the grant; revoke ends replays after 60 minutes'),
'N-R14-24': ('gap','Secrets in environment variables not marked sensitive','2 secrets readable in plain text','3 of 4 hidden; 1 odd one missed'),
'N-R14-25': ('gap','Token copied from a CI runner, replayed','Both replays work','Both replays refused'),
}
GROUPS = {
 'discover':('Discover','#4de2ff'),'own':('Own and retire','#7df2d0'),'credential':('Credentials','#c4b5fd'),
 'control':('Front door and trust','#f7c873'),'privileged':('Privileged access','#ff8fa3'),
 'shadow':('Shadow AI','#8b5cf6'),'gap':('Gap cases from 2026 incidents','#34d399')}


T2 = {
'N-R14-07': ('discover','One account, three names','43 entries for 30 identities, findings split','Merged on owner plus name: 29, one wrong merge'),
'N-R14-19': ('credential','Two identities, same age score','Tie, the test tool can be fixed first','Reach in the score: production ranks first'),
'N-R14-20': ('credential','Rotation ticket, old secret still accepted','All 5 close, 2 old secrets live','3 close, 2 stay open until the old secret is dead'),
'N-R14-21': ('own','4 agents share one team key','Log says "team key", revoke hits all 4','One key per agent: log names it, revoke hits 1'),
'N-R14-22': ('control','Engineer signs in as a service account','Logged under the account, nobody accountable','Direct sign-in refused, checkout names the person'),
'P-R15-10': ('privileged','Push fatigue and SIM-swap against admins','6 bad sign-ins get through','Passkey, no SMS fallback: 0 get through'),
'P-R15-15': ('privileged','Vault backup on a weaker share','5 non-backup reads succeed','Same rules and an alert: 5 refused, 5 alerts'),
'P-R15-16': ('privileged','Attacker calls the help desk for a reset','Both attacker resets succeed','Proof, or notice with a delay: both stopped'),
'P-R15-19': ('privileged','Vendor needed at 2 a.m.','Shared password, stays on, no record','Approved, recorded, closes at 2 hours'),
'P-R15-25': ('privileged','Rotate 200 secrets after a breach','12 outages','Consumers first and a dry run: 0 outages, 2 left unrotated'),
'S-R17-02': ('shadow','AI tool needs one folder, inherits 40','Can write to all 40','Read on one folder, 0 writable'),
'S-R17-06': ('shadow','AI-service keys in 6 repositories','All 6 stay valid','5 revoked on find, 1 odd prefix missed'),
'S-R17-10': ('shadow','5 automations outlive a test','All 5 still run','4 disabled, 1 extended on any written reason'),
'C-R16-C01': ('chain','No owner, password in a ticket, export shared','Attacker signs in from a new network','Stopped at link 1; for an old account the ticket scan stops it at link 2'),
'C-R16-C02': ('chain','Token committed, repo cloned, found 7 days later','Attacker calls the cloud API','Commit block stops at link 1; a 1-day token alone also stops it'),
'C-R16-C04': ('chain','Contractor with no end date','Phished credential gives production access','Expiry stops at link 3; sponsor review alone does not at 30 days'),
'C-R16-C05': ('chain','Break-glass password pasted in chat','Reused with no emergency, unnoticed','Rotate on return stops it; the alert only reports it'),
'C-R16-C06': ('chain','Many approvals, one hostile among them','The hostile change is approved','A second approver stops it; showing the risk only flags it'),
'C-R16-C17': ('chain','Vault in place, direct login still works','Vault and recording bypassed','Blocking direct login stops it; the alert only reports it'),
}
GROUPS['chain'] = ('Chain tests', '#fbbf24')

T3 = {
'N-R18-01': ('control','A key copied to another network','12 calls accepted; the log cannot tell genuine from copied','Bound to the workload: 6 refused, 1 alert'),
'N-R18-02': ('control','A test credential that opens production','All 8 runs succeed, 2 from a compromised runner','2 refused, 2 alerts; a wildcard path still leaks 1 secret'),
}

# ---- framework stages: every case sits in exactly one -------------------------------------------
STAGES = [
    ('find',   'Find',             'List every machine identity and where it lives'),
    ('own',    'Own',              'A named person, a purpose and an end date for each'),
    ('limit',  'Limit',            'Least privilege and a front door that refuses the wrong caller'),
    ('store',  'Store and issue',  'Secrets in an approved place, short-lived, never in code'),
    ('rotate', 'Rotate and expire','Change on a schedule, consumers first, old value proven dead'),
    ('watch',  'Watch',            'Use is logged and the odd use is noticed'),
    ('retire', 'Retire and respond','Remove what is unused, cut access fast after a breach'),
]
STAGE_OF = {}
for _s, _ids in {
    'find':   'N-R14-01 N-R14-07 P-R15-08 S-R17-06',
    'own':    'N-R14-09 N-R14-18 N-R14-21 S-R17-03 S-R17-04 P-R15-18',
    'limit':  'N-R18-02 N-R14-17 N-R14-22 P-R15-05 P-R15-07 P-R15-09 S-R17-02 C-R16-C17 C-R16-C06 P-R15-10 P-R15-16',
    'store':  'N-R18-01 S-R17-05 N-R14-24 N-R14-03 P-R15-15 N-R14-25 C-R16-C02 C-R16-C01',
    'rotate': 'N-R14-04 N-R14-05 N-R14-14 N-R14-15 N-R14-19 N-R14-20 P-R15-02 P-R15-03 P-R15-25',
    'watch':  'P-R15-11 P-R15-13 C-R16-C05',
    'retire': 'N-R14-11 S-R17-01 S-R17-10 P-R15-17 P-R15-19 N-R14-23 C-R16-C04',
}.items():
    for _i in _ids.split():
        STAGE_OF[_i] = _s

# ---- OWASP NHI Top 10 (2025) names, from owasp.github.io/www-project-non-human-identities-top-10 ---
OWASP = [
    ('NHI1',  'Improper Offboarding',               'N-R14-11 P-R15-18 S-R17-01 S-R17-10', 'direct'),
    ('NHI2',  'Secret Leakage',                     'S-R17-05 S-R17-06 N-R14-24 C-R16-C02', 'direct'),
    ('NHI3',  'Vulnerable Third-Party NHI',         'N-R14-05 N-R14-23 S-R17-01', 'direct'),
    ('NHI4',  'Insecure Authentication',            'N-R14-25 N-R18-01', 'direct'),
    ('NHI5',  'Overprivileged NHI',                 'P-R15-05 S-R17-02 N-R14-17', 'direct'),
    ('NHI6',  'Insecure Cloud Deployment Configurations', 'N-R14-03 N-R14-25 C-R16-C02', 'direct'),
    ('NHI7',  'Long-Lived Secrets',                 'N-R14-05 N-R14-14 N-R14-25', 'direct'),
    ('NHI8',  'Environment Isolation',              'N-R14-17 N-R18-02', 'direct'),
    ('NHI9',  'NHI Reuse',                          'N-R14-21 P-R15-19', 'direct'),
    ('NHI10', 'Human Use of NHI',                   'N-R14-22 S-R17-03 C-R16-C17', 'direct'),
]

# ---- which guess file holds each case ---------------------------------------------------------------
GUESS_FILES = {
    'r1415': ('guesses-round-14-15.md', 'Rounds 14 and 15 (20 cases)', 'f06f355eb80c151cb237ca4ef0c09dad9bc995fe5d395dca03f8756b0c69c784'),
    'r17':   ('guesses-round-17.md', 'Round 17, shadow AI (4 cases)', '4e6dfc1a80b2fa1e0a0da0a129882e87fdd3be931b5dddafd018d92c05dc8b7c'),
    'gap':   ('guesses-gap-cases.md', 'Gap cases (3 cases)', '7d3aee7a941b3915915690294e97ef22118957fc82b5505a1a0502d6e4bd5f8d'),
    'r2':    ('guesses-stretch-and-chains.md', 'Stretch cases and chain tests (19 cases)', '40c2f87c9f3fa914b48a09c4abf016f1189b02ea91f07232e456275b842489ed'),
    'r18':   ('guesses-round-18.md', 'Round 18, NHI4 and NHI8 (2 cases)', '9155e0783c997589bc8daf2a6bc2dad4afa1cec0a2e183f9254665f847404180'),
}
GAP_IDS = {'N-R14-23', 'N-R14-24', 'N-R14-25'}

def guess_key(cid):
    if cid in T3: return 'r18'
    if cid in T2: return 'r2'
    if cid in GAP_IDS: return 'gap'
    if cid.startswith('S-R17'): return 'r17'
    return 'r1415'

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

# ---- scenario text, read from the guess files -----------------------------------------------------
def _scenarios():
    out = {}
    idre = re.compile(r'^(?:#{2,4}\s+|\*\*)([NPSC]-R1[4-8]-C?\d+)\s+(.*)$')
    for key, (fn, _, _) in GUESS_FILES.items():
        lines = open(os.path.join(EV, 'guesses', fn), encoding='utf-8').read().split('\n')
        for i, ln in enumerate(lines):
            m = idre.match(ln.strip())
            if not m:
                continue
            cid, rest = m.group(1), m.group(2)
            setup = ''
            if ln.strip().startswith('**'):
                # "**ID Title.** Scenario sentence(s)."
                mm = re.match(r'^(.*?)\*\*\s*(.*)$', rest)
                title = (mm.group(1) if mm else rest).strip().rstrip('.')
                setup = (mm.group(2) if mm else '').strip()
            else:
                title = rest.strip()
                for nxt in lines[i + 1:i + 6]:
                    if nxt.startswith('Scenario:'):
                        setup = nxt[len('Scenario:'):].strip()
                        break
                    if nxt.startswith('Chain:'):
                        setup = 'Chain of links: ' + nxt[len('Chain:'):].strip()
                        break
            out[cid] = (title, setup)
    return out

SCEN = _scenarios()

def _limit_text(cid, lim):
    if isinstance(lim, dict):
        if lim.get('note'):
            return lim['note']
        if cid == 'N-R14-15':
            return 'a consumer missing from the list still fails (report-job)'
        if cid == 'P-R15-05':
            return '8 members remain and 2 of them are broader than they need'
        return ''
    return lim or ''

def _wrong_detail(cid, mw, mi):
    parts = []
    for tag, d in (('without control', mw), ('with control', mi)):
        for k, v in (d or {}).items():
            if isinstance(v, list) and len(v) == 2:
                parts.append(f'{tag}: expected {k} = {v[0]}, got {v[1]}')
    if cid == 'N-R14-25':
        parts.append('control-off check: expected a short lifetime to change a replay result; another control already blocked both replays')
    return '; '.join(parts)

def load_cases():
    """One dict per case, in the order the page shows them."""
    r1 = {r['id']: r for r in json.load(open(os.path.join(EV, 'results.json')))['rows']}
    r2 = {r['id']: r for r in json.load(open(os.path.join(EV, 'results-stretch.json')))['rows']}
    r3 = {r['id']: r for r in json.load(open(os.path.join(EV, 'results-round-18.json')))['rows']}
    out = []
    for cid, (g, trig, wo, wi) in list(T.items()) + list(T2.items()) + list(T3.items()):
        run = 3 if cid in T3 else (2 if cid in T2 else 1)
        r = {1: r1, 2: r2, 3: r3}[run][cid]
        wrong = bool(r['mismatch_without'] or r['mismatch_with']) or cid == 'N-R14-25'
        masked = [k for k, v in r['noticed'].items() if not v]
        title, setup = SCEN.get(cid, (r['title'], ''))
        out.append(dict(
            id=cid, run=run, group=g, group_name=GROUPS[g][0], color=GROUPS[g][1], stage=STAGE_OF[cid],
            title=r['title'], short=trig, without=wo, with_=wi, setup=setup,
            mismatch_without=r['mismatch_without'], mismatch_with=r['mismatch_with'],
            wrong=wrong, noticed=r['noticed'], masked=masked, limit=_limit_text(cid, r.get('limit')), wrong_detail=_wrong_detail(cid, r['mismatch_without'], r['mismatch_with']),
            extras=r.get('extras') or [], guess_file=GUESS_FILES[guess_key(cid)][0],
            owasp=[o[0] for o in OWASP if cid in o[2].split()],
        ))
    return out

if __name__ == '__main__':
    cs = load_cases()
    assert len(cs) == 48, len(cs)
    assert set(STAGE_OF) == {c['id'] for c in cs}, set(STAGE_OF) ^ {c['id'] for c in cs}
    print('cases', len(cs), 'wrong', sum(c['wrong'] for c in cs), 'with masked control', sum(bool(c['masked']) for c in cs))
    print('setup missing:', [c['id'] for c in cs if not c['setup']])
    for c in cs[:3] + cs[-2:]:
        print(c['id'], '|', c['title'], '|', c['setup'][:90])
