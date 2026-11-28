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

## Round 2: fool the approver (open to readers)

7 guesses, PA-R2-01 to PA-R2-07, about real small open AI models acting as the approver for 120 made-up requests. Anyone can run it against their own model.

- `guesses/guesses-round-2.md`: the predictions, locked before any model runs. sha256 `576b334e62bd9b9c1659efab64d97c14e83a9f3ff7df169bc778b9f207857a2c`. It also lists the hashes of the four files below, so they are locked too.
- `round2/policy.json`: Kaveri Finance's made-up access policy. The approver sees it; the code checks use it.
- `round2/test-set.jsonl`: the 120 requests. Each has a `label` the harness removes before the approver sees anything.
- `round2/make_test_set.py`: rebuilds the test set from a fixed seed. `--check` confirms the committed file matches.
- `round2/approver-instructions.md`: the exact instructions the approver gets, and how its answers are read.

The script that runs a model, and the reference runs, come after the guesses are merged.

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

Results, from run 46133108171 on 28 Nov 2026:

- `RESULTS-round-4.md` and `results-round-4.json`: copied unchanged from that run's `round-4-results` download (sha256 `40e530e2…` and `ab26c366…`). 4 of 5 rows matched, both joint checks matched, no harness errors.
- `FINDINGS-round-4.md`: what the run shows, including the one miss.
- `round4/HARNESS-CHANGES.md`: the two setup fixes made before this run.
