"""Score blind forecasts against the round 1 results.

Usage, after running round1.py:
    python3 pam-lab/evidence/ai-forecast/score_forecast.py pam-lab/evidence/ai-forecast/round-1-<model>.md [more files]
Roshan's own predictions are scored the same way from guesses/guesses-round-1.md.
A row counts as exact when all five numbers match the model. "Close" counts each of the five numbers separately.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results-round-1.json")
ROW = re.compile(r"\|\s*(PA-R1-\d\d)\s*\|([^|]*)\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|")


def rows(path):
    out = {}
    for m in ROW.finditer(open(path, encoding="utf-8").read()):
        out.setdefault(m.group(1), []).append([int(m.group(i)) for i in range(3, 8)])
    return out


def score(path, model):
    f = rows(path)
    exact = cells = total_rows = 0
    for cid, mrows in model.items():
        for i, m in enumerate(mrows):
            total_rows += 1
            g = f.get(cid, [])
            if i < len(g):
                exact += g[i] == m
                cells += sum(a == b for a, b in zip(g[i], m))
    return exact, total_rows, cells, total_rows * 5


def main():
    res = json.load(open(RESULTS))
    model = {}
    for r in res["rows"]:
        model.setdefault(r["id"], []).append(r["model"])
    files = [os.path.join(HERE, "..", "guesses", "guesses-round-1.md")] + sys.argv[1:]
    for p in files:
        e, n, c, cn = score(p, model)
        print("%-40s exact rows %2d of %d   matching numbers %3d of %d" % (os.path.basename(p), e, n, c, cn))


if __name__ == "__main__":
    main()
