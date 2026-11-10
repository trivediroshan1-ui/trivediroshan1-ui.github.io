"""Runs round 18 (N-R18-01, N-R18-02). Checks the committed guess file hash first.
Writes RESULTS-round-18.md and results-round-18.json."""
import hashlib, json, os, sys, datetime
from cases3 import CASES
HERE = os.path.dirname(os.path.abspath(__file__))
COMMITTED = {'guesses/guesses-round-18.md': '9155e0783c997589bc8daf2a6bc2dad4afa1cec0a2e183f9254665f847404180'}
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
        mw, mx = sub(c['gw'], w), sub(c['gx'], x)
        noticed = {ctl: c['run'](allon - {ctl}) != c['run'](allon) for ctl in c['controls']}
        lim = c['limit']() if c['limit'] else None
        extras = []
        for label, on, exp in c['extras']:
            got = c['run'](set(on)); extras.append(dict(label=label, got=got, mismatch=sub(exp, got)))
        rows.append(dict(id=c['id'], title=c['title'], without=w, with_=x, mismatch_without=mw, mismatch_with=mx,
                         noticed=noticed, limit=lim, extras=extras))
    json.dump(dict(run_at=datetime.datetime.now().isoformat(timespec='seconds'), rows=rows),
              open(os.path.join(HERE, 'results-round-18.json'), 'w'), indent=1, default=list)
    L = ['# Results: round 18, two cases', '',
         'Made-up data. Guesses were hashed and committed (e50df1b, sha256 9155e078...) before this code. Models are small in-memory simulations written by the same person as the guesses.', '',
         '| Case | Guess, without | Guess, with | Every control noticed |', '|---|---|---|---|']
    mism = []
    for r in rows:
        nz = ', '.join(f"{k}: {'yes' if v else 'NO'}" for k, v in r['noticed'].items())
        L.append(f"| {r['id']} {r['title']} | {'match' if not r['mismatch_without'] else 'MISMATCH'} | {'match' if not r['mismatch_with'] else 'MISMATCH'} | {nz} |")
        for tag, m in (('without', r['mismatch_without']), ('with', r['mismatch_with'])):
            if m: mism.append((r['id'], tag, m))
    L += ['', '## Where my guess was wrong', '']
    L += [f"- **{i}** ({t}): " + '; '.join(f"expected {k}={e!r}, got {g!r}" for k, (e, g) in m.items()) for i, t, m in mism] or ['- None.']
    L += ['', '## What each run returned', '']
    for r in rows: L += [f"- {r['id']} without controls: {r['without']}", f"- {r['id']} all controls on: {r['with_']}"]
    L += ['', '## Control-off checks and extra scenarios', '']
    for r in rows:
        for e in r['extras']: L.append(f"- {r['id']} {e['label']}: got {e['got']}" + (' (matches my note)' if not e['mismatch'] else f" MISMATCH {e['mismatch']}"))
    L += ['', '## Limits probed', '']
    L += [f"- **{r['id']}**: {r['limit']}" for r in rows if r['limit']]
    L += ['', '## Not noticed (masked by another control)', '']
    L += [f"- {r['id']}: {k}" for r in rows for k, v in r['noticed'].items() if not v] or ['- None.']
    open(os.path.join(HERE, 'RESULTS-round-18.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
main()
