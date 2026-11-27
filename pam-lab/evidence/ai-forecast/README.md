# Human against AI: who predicts control failures better?

Before round 1 is run, one or more AI models predict the same 21 counts from the scenarios alone. Their predictions are locked the same way as Roshan's: saved, hashed and committed before `round1.py` runs. After the run, everyone is scored against the models with `score_forecast.py`.

## Steps, before the run

1. Open a new chat in the AI you want to test, with no memory or other context switched on.
2. Paste everything below the line in `round-1-blind-prompt.md`.
3. Save the whole answer as `round-1-<model>.md` in this folder. At the top, write the model's name and version, the date and time, and the app or API used.
4. Hash it: `shasum -a 256 pam-lab/evidence/ai-forecast/round-1-<model>.md`.
5. Commit it, and only then run `python3 pam-lab/evidence/round1.py`.

## After the run

```
python3 pam-lab/evidence/ai-forecast/score_forecast.py pam-lab/evidence/ai-forecast/round-1-*.md
```

It prints, for Roshan and for each model: rows where all five numbers match, and how many of the 105 single numbers match.

## Limits

- One run of one prompt is one sample. Ask the same model twice and it may answer differently, so record every attempt, not the best one.
- The models score themselves against Roshan's code, written by the same person who wrote the human predictions. That favours the human. The page will say so.

## Round 3

The same steps, with `round-3-blind-prompt.md`. Save the answer as `round-3-<model>.md` and commit it before running `round3.py`. The prompt holds the scenarios, the controls and what is counted. It doesn't hold Roshan's predictions, joint checks or notes. Case 09 states one assumption, because the model needs it: the random reviewer catches exactly one collusive grant whenever at least one goes through.

After the run:

```
python3 pam-lab/evidence/ai-forecast/score_forecast.py --round 3 pam-lab/evidence/ai-forecast/round-3-*.md
```

Round 3 has 15 counted rows, so 75 single numbers.
