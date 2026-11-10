#!/usr/bin/env python3
"""Checks that each guess file still has the SHA-256 recorded when it was committed.
Needs only Python 3. Run it from the folder that holds guesses/:   python3 verify.py
Exit code 0 means every hash matched. Exit code 1 means a file changed since it was committed."""
import hashlib, os, sys

RECORDED = {
    'guesses-round-14-15.md': 'f06f355eb80c151cb237ca4ef0c09dad9bc995fe5d395dca03f8756b0c69c784',
    'guesses-round-17.md': '4e6dfc1a80b2fa1e0a0da0a129882e87fdd3be931b5dddafd018d92c05dc8b7c',
    'guesses-gap-cases.md': '7d3aee7a941b3915915690294e97ef22118957fc82b5505a1a0502d6e4bd5f8d',
    'guesses-stretch-and-chains.md': '40c2f87c9f3fa914b48a09c4abf016f1189b02ea91f07232e456275b842489ed',
    'guesses-round-18.md': '9155e0783c997589bc8daf2a6bc2dad4afa1cec0a2e183f9254665f847404180',
}
here = os.path.dirname(os.path.abspath(__file__))
bad = 0
for name, want in RECORDED.items():
    path = os.path.join(here, 'guesses', name)
    with open(path, 'rb') as f:
        got = hashlib.sha256(f.read()).hexdigest()
    ok = got == want
    bad += 0 if ok else 1
    print(('MATCH   ' if ok else 'DIFFERS ') + name + '  ' + got)
print('\n%d of %d guess files match the recorded hash.' % (len(RECORDED) - bad, len(RECORDED)))
sys.exit(1 if bad else 0)
