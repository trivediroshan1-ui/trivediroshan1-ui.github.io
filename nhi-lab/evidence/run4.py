"""Runs round 19 (19 queued cases). Checks the committed guess file hash first.
Writes RESULTS-round-19.md and results-round-19.json."""
import hashlib, json, os, sys, datetime
from cases4 import CASES
HERE = os.path.dirname(os.path.abspath(__file__))
COMMITTED = {'guesses/guesses-round-19.md': '729e16f25cf4a67e34ab87607b80ad59ae0935d4d72b1a087dfa0cb2bcec1b4b'}
def sub(exp, got): return {k: (v, got.get(k, '<missing>')) for k, v in exp.items() if got.get(k, '<missing>') != v}
def view(d, keys): return {k: d.get(k) for k in (keys or d.keys())}
def main():
    for f, h in COMMITTED.items():
        got = hashlib.sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest()
        print(('guess file OK   ' if got == h else 'GUESS FILE CHANGED ') + f)
        if got != h: print('Stop: the guesses differ from what you committed.'); sys.exit(1)
    rows = []
    for c in CASES:
        allon = set(c['controls'])
        w, x = c['run'](set()), c['run'](allon)
        base = view(x, c['watch'])
        noticed = {ctl: view(c['run'](allon - {ctl}), c['watch']) != base for ctl in c['controls']}
        notice_mis = {k: (c['notice'][k], noticed[k]) for k in c['notice'] if c['notice'][k] is not None and c['notice'][k] != noticed[k]}
        extras = []
        for label, on, exp in c['extras']:
            got = c['run'](set(on)); extras.append(dict(label=label, got=got, mismatch=sub(exp, got)))
        rows.append(dict(id=c['id'], title=c['title'], without=w, with_=x,
                         mismatch_without=sub(c['gw'], w), mismatch_with=sub(c['gx'], x),
                         noticed=noticed, notice_mismatch=notice_mis,
                         limit=c['limit']() if c['limit'] else None, extras=extras))
    json.dump(dict(run_at=datetime.datetime.now().isoformat(timespec='seconds'), rows=rows),
              open(os.path.join(HERE, 'results-round-19.json'), 'w'), indent=1, default=list)
    def wrong(r): return bool(r['mismatch_without'] or r['mismatch_with'] or r['notice_mismatch'] or any(e['mismatch'] for e in r['extras']))
    L = ['# Results: round 19, the queued cases', '',
         'Made-up data. Guesses were hashed and committed (a2dc1fd, sha256 729e16f2...) before this code. Models are small in-memory simulations written by the same person as the guesses.', '',
         '| Case | Guess, without | Guess, with | Control-off guesses | Noticed guesses | Every control noticed |', '|---|---|---|---|---|---|']
    for r in rows:
        nz = ', '.join(f"{k}: {'yes' if v else 'NO'}" for k, v in r['noticed'].items())
        eo = 'match' if not any(e['mismatch'] for e in r['extras']) else 'MISMATCH'
        L.append(f"| {r['id']} {r['title']} | {'match' if not r['mismatch_without'] else 'MISMATCH'} | {'match' if not r['mismatch_with'] else 'MISMATCH'} | {eo} | {'match' if not r['notice_mismatch'] else 'MISMATCH'} | {nz} |")
    L += ['', f"Cases with every guess matched: {sum(not wrong(r) for r in rows)} of {len(rows)}. Cases with at least one wrong guess: {sum(wrong(r) for r in rows)}.", '',
          '## Where my guess was wrong', '']
    n = 0
    for r in rows:
        for tag, m in (('without controls', r['mismatch_without']), ('all controls on', r['mismatch_with'])):
            if m: n += 1; L.append(f"- **{r['id']}** ({tag}): " + '; '.join(f"expected {k}={e!r}, got {g!r}" for k, (e, g) in m.items()))
        for e in r['extras']:
            if e['mismatch']: n += 1; L.append(f"- **{r['id']}** ({e['label']}): " + '; '.join(f"expected {k}={a!r}, got {g!r}" for k, (a, g) in e['mismatch'].items()))
        if r['notice_mismatch']:
            n += 1; L.append(f"- **{r['id']}** (noticed or not): " + '; '.join(f"{k}: expected {'noticed' if a else 'not noticed'}, got {'noticed' if g else 'not noticed'}" for k, (a, g) in r['notice_mismatch'].items()))
    L += [f"- None." if not n else f"- Total wrong claims: {n}."]
    L += ['', '## What each run returned', '']
    for r in rows: L += [f"- {r['id']} without controls: {r['without']}", f"- {r['id']} all controls on: {r['with_']}"]
    L += ['', '## Control-off checks and extra scenarios', '']
    for r in rows:
        for e in r['extras']: L.append(f"- {r['id']} {e['label']}: got { {k: e['got'][k] for k in e['got']} }" + (' (matches my note)' if not e['mismatch'] else ' (differs from my note)'))
    L += ['', '## Limits probed', '']
    L += [f"- **{r['id']}**: {r['limit']}" for r in rows if r['limit']]
    L += ['', '## Not noticed (masked by another control, or no effect on what the case counts)', '']
    L += [f"- {r['id']}: {k}" for r in rows for k, v in r['noticed'].items() if not v] or ['- None.']
    L += ['', f"Controls switched off alone: {sum(len(r['noticed']) for r in rows)}. Not noticed: {sum(not v for r in rows for v in r['noticed'].values())}.", f"Limits probed: {sum(1 for r in rows if r['limit'])}."]
    open(os.path.join(HERE, 'RESULTS-round-19.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
main()
