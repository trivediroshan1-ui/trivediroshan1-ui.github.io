"""Run every case: guess check (control off, control on), then switch each
control off alone and see whether the outcome changes (noticed)."""
import hashlib, json, os, sys, datetime
from cases import CASES
HERE = os.path.dirname(os.path.abspath(__file__))
COMMITTED = {'guesses/guesses-round-14-15.md': 'f06f355eb80c151cb237ca4ef0c09dad9bc995fe5d395dca03f8756b0c69c784',
             'guesses/guesses-round-17.md': '4e6dfc1a80b2fa1e0a0da0a129882e87fdd3be931b5dddafd018d92c05dc8b7c',
             'guesses/guesses-gap-cases.md': '7d3aee7a941b3915915690294e97ef22118957fc82b5505a1a0502d6e4bd5f8d'}
def sub(exp, got):  # every expected key must equal the observed value
    return {k: (v, got.get(k, '<missing>')) for k, v in exp.items() if got.get(k, '<missing>') != v}

def main():
    ok = True
    for f, h in COMMITTED.items():
        p = os.path.join(HERE, f)
        got = hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None
        print(('guess file OK   ' if got == h else 'GUESS FILE CHANGED ') + f)
        ok &= got == h
    if not ok: print('Stop: the guesses differ from what you committed.'); sys.exit(1)
    rows = []
    for c in CASES:
        allon = set(c['controls'])
        w = c['run'](set()); x = c['run'](allon)
        mw, mx = sub(c['gw'], w), sub(c['gx'], x)
        noticed = {}
        for ctl in c['controls']:
            off = c['run'](allon - {ctl})
            noticed[ctl] = off != x
        lim = c['limit']() if c['limit'] else None
        extras = [dict(label=l, mismatch=sub(e, c['run'](set(o))), got=c['run'](set(o))) for l, o, e in c.get('extras', [])]
        rows.append(dict(id=c['id'], title=c['title'], without=w, with_=x,
                         mismatch_without=mw, mismatch_with=mx, noticed=noticed, limit=lim, extras=extras))
    json.dump(dict(run_at=datetime.datetime.now().isoformat(timespec='seconds'), rows=rows),
              open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    L = ['# Results: rounds 14, 15 and 17, 27 cases (24 must + 3 gap)', '',
         'Made-up data. Guesses were hashed and committed before this code. Models are small in-memory simulations of each control, not real systems.', '',
         '| Case | Guess, without | Guess, with | Every control noticed |', '|---|---|---|---|']
    mism = []
    for r in rows:
        nz = ', '.join(f"{k}: {'yes' if v else 'NO'}" for k, v in r['noticed'].items())
        L.append(f"| {r['id']} {r['title']} | {'match' if not r['mismatch_without'] else 'MISMATCH'} | {'match' if not r['mismatch_with'] else 'MISMATCH'} | {nz} |")
        for tag, m in (('without', r['mismatch_without']), ('with', r['mismatch_with'])):
            if m: mism.append((r['id'], tag, m))
    for r in rows:  # N-R14-25's guess said every control would be noticed
        if r['id'] == 'N-R14-25':
            for k, v in r['noticed'].items():
                if not v: mism.append((r['id'], 'control-off check', {k: ('changes a replay result', 'no change: the other control already blocks both replays')}))
    L += ['', '## Where my guess was wrong', '']
    L += [f"- **{i}** ({t}): " + '; '.join(f"expected {k}={e!r}, got {g!r}" for k, (e, g) in m.items()) for i, t, m in mism] or ['- None. Treat that with suspicion: I wrote both the guesses and the code.']
    L += ['', '## Extra scenarios', '']
    for r in rows:
        for e in r['extras']:
            L.append(f"- {r['id']} {e['label']}: " + ('match' if not e['mismatch'] else 'MISMATCH ' + str(e['mismatch'])))
            if e['mismatch']: mism.append((r['id'], e['label'], e['mismatch']))
    L += ['', '## Limits probed', '']
    for r in rows:
        if r['limit']: L.append(f"- **{r['id']}**: {r['limit']}")
    L += ['', '## Not noticed', '']
    nn = [f"- {r['id']}: {k} (masked: another control already stops the same attack)" for r in rows for k, v in r['noticed'].items() if not v]
    L += nn or ['- Every control, switched off alone, changed its case outcome.']
    open(os.path.join(HERE, 'RESULTS.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
main()
