"""Score blind forecasts against the round 1 or round 3 results.

Usage, after running round1.py (round 1 is the default):
    python3 pam-lab/evidence/ai-forecast/score_forecast.py pam-lab/evidence/ai-forecast/round-1-<model>.md [more files]
After running round3.py:
    python3 pam-lab/evidence/ai-forecast/score_forecast.py --round 3 pam-lab/evidence/ai-forecast/round-3-<model>.md [more files]
Roshan's own predictions are scored the same way from guesses/guesses-round-N.md.
A row counts as exact when all five numbers match the model. "Close" counts each of the five numbers separately.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = "1"
ROW = re.compile(r"\|\s*(PA-R\d-\d\d)\s*\|([^|]*)\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|")


def rows(path):
    out = {}
    for m in ROW.finditer(open(path, encoding="utf-8").read()):
        out.setdefault(m.group(1), []).append([int(m.group(i)) for i in range(3, 8)])
    return out


def score(path, model):
    f = {k: v for k, v in rows(path).items() if k.startswith("PA-R" + ROUND + "-")}
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
    global ROUND
    args = sys.argv[1:]
    if args[:1] == ["--round"]:
        ROUND, args = args[1], args[2:]
    if ROUND not in ("1", "3"):
        sys.exit("Round must be 1 or 3.")
    res = json.load(open(os.path.join(HERE, "..", "results-round-%s.json" % ROUND)))
    model = {}
    for r in res["rows"]:
        model.setdefault(r["id"], []).append(r["model"])
    files = [os.path.join(HERE, "..", "guesses", "guesses-round-%s.md" % ROUND)] + args
    for p in files:
        e, n, c, cn = score(p, model)
        print("%-40s exact rows %2d of %d   matching numbers %3d of %d" % (os.path.basename(p), e, n, c, cn))


if __name__ == "__main__":
    main()
