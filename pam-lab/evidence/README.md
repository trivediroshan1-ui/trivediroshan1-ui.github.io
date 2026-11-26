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
