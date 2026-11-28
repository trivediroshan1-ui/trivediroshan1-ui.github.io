# Privileged access lab: who holds admin, and for how long?

Round 1: just-in-time access and zero standing privilege. 16 cases, made-up data (Kaveri Finance). Models of rule logic, not of any vendor product.

## What is here

- `guesses/guesses-round-1.md`: the predictions, written and merged before any code (pull request #186). Locked: never edited.
- `round1.py`: the 16 case models. It checks the guess file's SHA-256 before it runs, reads the guessed numbers from that file, runs every case with no controls, all controls and each control off alone, and compares.

## Run it yourself

You need Python 3.8 or later and nothing else.

```
git clone https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io.git
cd trivediroshan1-ui.github.io
shasum -a 256 pam-lab/evidence/guesses/guesses-round-1.md
python3 pam-lab/evidence/round1.py
```

The hash must be `6c3acc1c3da56c1c381ccec312205d55a15b23fdfd5c1791d8240e74890a80aa`. If you change one character of the guess file, the script refuses to run.

The script writes two files next to itself:

- `results-round-1.json`: every row, the guess, the model's numbers, any mismatch, and which controls were noticed.
- `RESULTS-round-1.md`: the same as tables, plus the joint checks and which cases move when an assumption changes.

To write them somewhere else, set `PAM_LAB_OUT=/some/folder` before the command.

## Change an assumption

Every number the guess file leaves open is in `PARAMS` at the top of `round1.py`, with a comment. Change one and run again. The "Assumptions that change results" table shows which cases move for six of them.

## Round 3: the gaps around the lane

10 cases, PA-R3-01 to PA-R3-10: help desk recovery, movers and contractors, outside vendors, sub-agents, signing keys, Kubernetes, OT while IT is down, two insiders together, and session recordings.

- `guesses/guesses-round-3.md`: the predictions, merged before any code (pull request #189). Locked: never edited.
- `round3.py`: the 10 case models, built the same way as round 1.

```
shasum -a 256 pam-lab/evidence/guesses/guesses-round-3.md
python3 pam-lab/evidence/round3.py
```

The hash must be `fa235a1b2f6d7269474346c29d76b09ffb270734c3689a30d8a313adb53082e8`. The script writes `results-round-3.json` and `RESULTS-round-3.md`. Joint checks compare only the numbers the guess file states.

## Round 4: on real software

5 cases, PA-R4-01 to PA-R4-05, measured (not modelled) on Keycloak, OpenBao with PostgreSQL, OpenSSH with sudo, and Kubernetes in kind.

- `guesses/guesses-round-4.md`: the predictions, merged before any code (pull request #194). Locked. sha256 `0a7cac425ed7d3b6a265e56dc69880eb130e6ab72cd8cd95b7be3823b4cb2381`.
- `round4/run_case.py`: measures one case under one setting. A setup failure is recorded as an error, never as a number.
- `round4/round4.py`: checks the guess file's hash and compares the measurements with the guesses.
- `.github/workflows/pam-lab-round4.yml`: runs all 27 measurements on GitHub Actions. Started by hand from the Actions tab; read-only, no secrets. The full log of every run is public, and the results appear on the run's summary page and as the `round-4-results` download.

The passwords in `run_case.py` are throwaway values for containers that exist only for the length of one job.
