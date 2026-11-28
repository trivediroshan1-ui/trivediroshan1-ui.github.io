"""Privileged access lab, round 3: the gaps around the lane.

Made-up data (Kaveri Finance). Models of rule logic, not of any vendor product, help desk, cluster, PLC or HSM.
Written AFTER guesses/guesses-round-3.md, merged as 6fe7cba (pull request #189),
sha256 fa235a1b2f6d7269474346c29d76b09ffb270734c3689a30d8a313adb53082e8.
Guess values are PARSED from that file, not retyped. The script refuses to run if the file has changed.

Each case is a function sim(on, P) that returns a tuple of counts, one per row of the guess table for that case.
on = the set of controls switched on ("a", "b", "c"). P = the assumptions (PARAMS), each one stated so you can change it.
The models follow each case's scenario and controls as written in the locked file, not the guessed numbers.

Usage, from the root of the site repository:
    python3 pam-lab/evidence/round3.py
It writes results-round-3.json and RESULTS-round-3.md next to this file. Standard library only, Python 3.8 or later.
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = "3"
GUESS_FILE = os.path.join(HERE, "guesses", "guesses-round-3.md")
EXPECTED_SHA = "fa235a1b2f6d7269474346c29d76b09ffb270734c3689a30d8a313adb53082e8"
OUT_DIR = os.environ.get("PAM_LAB_OUT", HERE)

# ---- Assumptions. The guess file fixes most numbers; the ones it leaves open are marked NEW.
PARAMS = {
    "hold_hours": 24,                  # 01: a new authenticator can't activate admin for this long
    "review_day": 90,                  # NEW (02): the quarterly eligibility review lands after day 30
    "sponsor_wrong_attestations": 1,   # 03: of the ended contractors still active, how many a sponsor attests without checking
    "grandchild_gets_token": True,     # NEW (05): with no token rule, a sub-agent passes the parent's token on to its own sub-agent
    "sample_catches": 1,               # 09: the random third reviewer catches exactly this many collusive grants, if any go through
    "masked_per_month": 30,            # 10: of 40 recordings with personal data a month, how many the masking catches
    "retention_months": 3,             # 10: 90 days
}

CASES = {}
def case(cid):
    def deco(f):
        CASES[cid] = f
        return f
    return deco


@case("PA-R3-01")
def c01(on, P):
    callers, sim_swap = 2, 1
    enrolled = 0
    enrolled += 0 if "a" in on else callers            # video check and callback stop the help desk callers
    enrolled += 0 if "b" in on else sim_swap           # no SMS recovery for admins stops the SIM swap; the help desk check does not
    # c: a new authenticator can't activate admin within the hold, and the owner and SOC are told.
    activations = 0 if ("c" in on and P["hold_hours"] >= 24) else enrolled
    return (activations, enrolled)


@case("PA-R3-02")
def c02(on, P):
    with_old_eligibility, need_it = 6, 2
    unneeded = with_old_eligibility - need_it
    if "a" in on:                                      # mover event removes everything outside the new role
        left_day30 = 0
        blocked = 0 if "b" in on else need_it          # nobody re-requests, so the 2 who need it wait
    else:
        left_day30 = unneeded if P["review_day"] > 30 else 0   # c only helps if the review lands by day 30
        blocked = 0
    return (left_day30, blocked)


@case("PA-R3-03")
def c03(on, P):
    ended, no_end_date = 5, 3
    if "a" in on or "c" in on:
        return (0,)                                    # an end date or the vendor feed disables all 5 on the day
    still_active = no_end_date                         # the 2 with an end date are disabled by it anyway
    if "b" in on:                                      # the sponsor check catches all but the wrong attestations
        still_active = min(still_active, P["sponsor_wrong_attestations"])
    return (still_active,)


@case("PA-R3-04")
def c04(on, P):
    if "a" not in on:
        return (1,)                                    # the standing VPN account goes straight to the target; no broker, no recording
    if "b" in on:
        return (0,)                                    # no approved ticket, no broker session
    return (0 if "c" in on else 1,)                    # in a session, the command block decides


@case("PA-R3-05")
def c05(on, P):
    children = 3
    grandchild = 0 if "b" in on else 1                 # depth limit of 1 stops the sub-agent's own sub-agent
    if "a" in on:
        return (0,)                                    # every agent gets its own narrower token; the parent's is never passed
    holders = children + (grandchild if P["grandchild_gets_token"] else 0)
    # c names which agent used each token; it blocks nothing.
    return (holders,)


@case("PA-R3-06")
def c06(on, P):
    signed = 0
    signed += 0 if "a" in on else 1                    # the insider copies an exportable key and signs
    signed += 0 if "b" in on else 1                    # the side-branch build calls the signing service
    if signed == 0:
        return (0, 0)
    return (signed, 1 if "c" in on else -1)            # the daily log review finds it the next day


@case("PA-R3-07")
def c07(on, P):
    paths = 0
    paths += 0 if "a" in on else 1                     # standing cluster-admin binding the developer can impersonate
    paths += 0 if "b" in on else 2                     # service account token in a readable pod, and a privileged pod escape
    # c alerts on exec into system namespaces; it removes no path.
    return (paths,)


@case("PA-R3-08")
def c08(on, P):
    idp_down = True
    attacker_reaches = "a" not in on                   # with the broker rule, the attacker in IT has no route
    attacker_writes = 1 if (attacker_reaches and "c" not in on) else 0
    if "a" in on and idp_down:
        plant_blocked = 0 if "b" in on else 1          # the broker depends on the corporate IdP; only site-local break-glass gets through
    else:
        plant_blocked = 0                              # no broker in the way; the second person on site satisfies c
    return (attacker_writes, plant_blocked)


@case("PA-R3-09")
def c09(on, P):
    planned = 4
    if "a" not in on:
        grants = planned                               # each approves their own; the pair rule never applies
    else:
        grants = min(planned, 2) if "b" in on else planned
    caught = min(P["sample_catches"], grants) if "c" in on else 0
    return (grants - caught,)


@case("PA-R3-10")
def c10(on, P):
    per_month, views = 40, 6
    unmasked = per_month - P["masked_per_month"] if "c" in on else per_month
    months_held = P["retention_months"] if "a" in on else 12
    held = unmasked * months_held
    untracked_views = 0 if "b" in on else views
    return (held, untracked_views)


# Joint checks stated in the "Joint checks" section of the locked file.
JOINT = [
    ("PA-R3-01", "video check and 24 hour hold both off", {"b"}, (2, None)),
    ("PA-R3-03", "end date rule and vendor feed both off", {"b"}, (1,)),
    ("PA-R3-08", "broker rule and read-only rule both off", {"b"}, (1, None)),
]
# None = the guess file states no number for that count, so it is not compared.
JOINT_NOTE = {
    "PA-R3-01": "only the activation count is stated in the guess",
    "PA-R3-08": "only the write count is stated in the guess",
}


def parse_guesses(text):
    rows = {}
    pat = r"\|\s*(PA-R" + ROUND + r"-\d\d)\s*\|([^|]*)\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|"
    for line in text.splitlines():
        m = re.match(pat, line)
        if m:
            rows.setdefault(m.group(1), []).append((m.group(2).strip(), [int(m.group(i)) for i in range(3, 8)]))
    return rows


SETTINGS = [("none", set()), ("all", {"a", "b", "c"}), ("off a", {"b", "c"}), ("off b", {"a", "c"}), ("off c", {"a", "b"})]


def run(P):
    return [(cid, [CASES[cid](on, P) for _, on in SETTINGS]) for cid in sorted(CASES)]


def main():
    data = open(GUESS_FILE, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA:
        sys.exit("The guess file has changed since it was locked (sha256 " + sha + "). Not running.")
    guesses = parse_guesses(data.decode("utf-8"))
    if sorted(guesses) != sorted(CASES):
        sys.exit("Cases in the guess file and the models differ.")

    rows, matched, total = [], 0, 0
    for cid, got in run(PARAMS):
        if len(got[0]) != len(guesses[cid]):
            sys.exit("Row count differs for " + cid + ".")
        for i, (label, g) in enumerate(guesses[cid]):
            model = [vals[i] for vals in got]
            diffs = [SETTINGS[k][0] for k in range(5) if model[k] != g[k]]
            total += 1
            matched += not diffs
            noticed = [SETTINGS[k][0][-1] for k in (2, 3, 4) if model[k] != model[1]]
            rows.append({"id": cid, "counted": label, "guess": g, "model": model, "mismatch": diffs, "noticed": noticed})

    joint = []
    for cid, what, on, expect in JOINT:
        got = CASES[cid](on, PARAMS)
        joint.append({"id": cid, "check": what, "guess": list(expect), "model": list(got), "match": all(e is None or e == m for e, m in zip(expect, got)),
                      "note": JOINT_NOTE.get(cid, "")})

    # Sensitivity: change one assumption at a time and list the cases that move.
    flips = {
        "review_day": 20, "sponsor_wrong_attestations": 0, "grandchild_gets_token": False,
        "sample_catches": 0, "masked_per_month": 20, "retention_months": 1,
    }
    base = dict(run(PARAMS))
    sens = []
    for k, v in flips.items():
        P2 = dict(PARAMS); P2[k] = v
        moved = [cid for cid, got in run(P2) if got != base[cid]]
        sens.append({"param": k, "was": PARAMS[k], "now": v, "cases_that_move": moved})

    result = {"guess_file": os.path.relpath(GUESS_FILE, HERE), "sha256": sha, "params": PARAMS, "rows": rows,
              "joint": joint, "sensitivity": sens,
              "summary": {"rows": total, "matched": matched, "mismatched": total - matched,
                          "joint_matched": sum(j["match"] for j in joint), "joint_total": len(joint)}}
    json.dump(result, open(os.path.join(OUT_DIR, "results-round-3.json"), "w"), indent=1)

    md = ["# Results: Privileged access lab, round 3", "",
          "Generated by `round3.py`. Guesses: `guesses/guesses-round-3.md`, sha256 " + sha + ".",
          "Made-up data. Models of rule logic, not of any product. A row matches when all five numbers equal the guess.", "",
          "Rows matched: %d of %d. Joint checks matched: %d of %d." % (matched, total, result["summary"]["joint_matched"], len(joint)), "",
          "| ID | Counted | Guess (none, all, off a, off b, off c) | Model | Mismatch (column that differs) | Controls noticed |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], r["counted"], r["guess"], r["model"],
                                                     ", ".join("no controls" if m == "none" else m for m in r["mismatch"]) or "match", ", ".join(r["noticed"]) or "none"))
    md += ["", "## Joint checks", "", "| ID | Check | Guess | Model | Match | Note |", "|---|---|---|---|---|---|"]
    for j in joint:
        md.append("| %s | %s | %s | %s | %s | %s |" % (j["id"], j["check"], j["guess"], j["model"], "yes" if j["match"] else "no", j["note"]))
    md += ["", "## Assumptions that change results", "", "| Assumption | Was | Changed to | Cases that move |", "|---|---|---|---|"]
    for s in sens:
        md.append("| %s | %s | %s | %s |" % (s["param"], s["was"], s["now"], ", ".join(s["cases_that_move"]) or "none"))
    open(os.path.join(OUT_DIR, "RESULTS-round-3.md"), "w").write("\n".join(md) + "\n")

    print("Guess file hash OK.")
    print("Rows matched: %d of %d. Joint checks matched: %d of %d." % (matched, total, result["summary"]["joint_matched"], len(joint)))
    print("Wrote results-round-3.json and RESULTS-round-3.md in", OUT_DIR)


if __name__ == "__main__":
    main()
