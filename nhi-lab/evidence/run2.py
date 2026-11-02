"""Runs the 13 stretch cases and 6 chain tests. Checks the committed guess file hash first.
Writes RESULTS-stretch.md and results-stretch.json."""
import hashlib, json, os, sys, datetime
from cases2 import CASES
HERE = os.path.dirname(os.path.abspath(__file__))
COMMITTED = {'guesses/guesses-stretch-and-chains.md': '40c2f87c9f3fa914b48a09c4abf016f1189b02ea91f07232e456275b842489ed'}
def sub(exp, got): return {k: (v, got.get(k, '<missing>')) for k, v in exp.items() if got.get(k, '<missing>') != v}
def main():
    for f, h in COMMITTED.items():
        got = hashlib.sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest()
        print(('guess file OK   ' if got == h else 'GUESS FILE CHANGED ') + f)
        if got != h: print('Stop: the guesses differ from what you committed.'); sys.exit(1)
    rows = []
    for c in CASES:
        allon = set(c['controls'])
        w = c['run'](set()); x = c['run'](allon)
        derived = {}
        if c['chain']:
            alone = {k: c['run']({k}) for k in c['controls']}
            stops = {k: v['stopped_at'] for k, v in alone.items() if v['stopped_at']}
            derived['alone_stopped_at'] = {k: v['stopped_at'] for k, v in alone.items()}
            derived['best_alone'] = min(stops, key=stops.get) if stops else None
            derived['short_lived_alone_stops'] = bool(alone.get('short_lived', {}).get('stopped_at'))
            derived['sponsor_review_alone_leaves_window'] = alone.get('sponsor_review', {}).get('stopped_at') is None
            x = {**x, **derived}
        mw, mx = sub(c['gw'], w), sub(c['gx'], x)
        noticed = {ctl: c['run'](allon - {ctl}) != c['run'](allon) for ctl in c['controls']}
        lim = c['limit']() if c['limit'] else None
        extras = []
        for label, on, exp in c['extras']:
            got = c['run'](set(on)); extras.append(dict(label=label, got=got, mismatch=sub(exp, got)))
        rows.append(dict(id=c['id'], title=c['title'], chain=c['chain'], without=w, with_=x, mismatch_without=mw, mismatch_with=mx,
                         noticed=noticed, limit=lim, extras=extras))
    json.dump(dict(run_at=datetime.datetime.now().isoformat(timespec='seconds'), rows=rows), open(os.path.join(HERE, 'results-stretch.json'), 'w'), indent=1)
    L = ['# Results: 13 stretch cases and 6 chain tests', '',
         'Made-up data. Guesses were hashed and committed (78d7e3e) before this code. Models are small in-memory simulations. The chain tests are rule models: each link is stopped by the controls I decided stop it, so their results follow from my rules.', '',
         '| Case | Guess, without | Guess, with | Every control noticed |', '|---|---|---|---|']
    mism = []
    for r in rows:
        nz = ', '.join(f"{k}: {'yes' if v else 'NO'}" for k, v in r['noticed'].items())
        L.append(f"| {r['id']} {r['title']} | {'match' if not r['mismatch_without'] else 'MISMATCH'} | {'match' if not r['mismatch_with'] else 'MISMATCH'} | {nz} |")
        for tag, m in (('without', r['mismatch_without']), ('with', r['mismatch_with'])):
            if m: mism.append((r['id'], tag, m))
    L += ['', '## Where my guess was wrong', '']
    L += [f"- **{i}** ({t}): " + '; '.join(f"expected {k}={e!r}, got {g!r}" for k, (e, g) in m.items()) for i, t, m in mism] or ['- None.']
    L += ['', '## Chains: how far each control gets alone', '']
    for r in rows:
        if r['chain']: L.append(f"- **{r['id']}**: all controls on -> stopped at link {r['with_']['stopped_at']}, detected at {r['with_']['detected_at']}; alone: {r['with_']['alone_stopped_at']}")
    L += ['', '## Extra scenarios', '']
    for r in rows:
        for e in r['extras']: L.append(f"- {r['id']} {e['label']}: got {e['got']}" + (' (matches my note)' if not e['mismatch'] else f" MISMATCH {e['mismatch']}"))
    L += ['', '## Limits probed', '']
    L += [f"- **{r['id']}**: {r['limit']}" for r in rows if r['limit']]
    L += ['', '## Not noticed (masked by another control)', '']
    L += [f"- {r['id']}: {k}" for r in rows for k, v in r['noticed'].items() if not v] or ['- None.']
    open(os.path.join(HERE, 'RESULTS-stretch.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
main()
