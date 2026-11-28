"""Privileged access lab, round 1: just-in-time access and zero standing privilege.

Made-up data (Kaveri Finance). Models of rule logic, not of any vendor product.
Written AFTER guesses/guesses-round-1.md, merged as accc68f (pull request #186),
sha256 6c3acc1c3da56c1c381ccec312205d55a15b23fdfd5c1791d8240e74890a80aa.
Guess values are PARSED from that file, not retyped. The script refuses to run if the file has changed.

Each case is a function sim(on, P) that returns a tuple of counts, one per row of the guess table for that case.
on = the set of controls switched on ("a", "b", "c"). P = the assumptions (PARAMS), each one stated so you can change it.

Usage, from the root of the site repository:
    python3 pam-lab/evidence/round1.py
It writes results-round-1.json and RESULTS-round-1.md next to this file. Standard library only, Python 3.8 or later.
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUESS_FILE = os.path.join(HERE, "guesses", "guesses-round-1.md")
EXPECTED_SHA = "6c3acc1c3da56c1c381ccec312205d55a15b23fdfd5c1791d8240e74890a80aa"
OUT_DIR = os.environ.get("PAM_LAB_OUT", HERE)

# ---- Assumptions. The guess file fixes most numbers; the ones it leaves open are marked NEW.
PARAMS = {
    "used_in_90_days": 22,            # 01: of 36 standing admins, how many used their rights
    "heavy_extenders_approved": 2,     # 03: of 3 heavy extenders, how many get a second extension approved
    "person_approves_injected": 2,     # 07: of 3 injected requests a person sees with no scope rule
    "alert_response_min": 120,         # 06: minutes before anyone acts on an alert (longer than the 90 minute outage)
    "token_life_default_min": 60,      # 02: cloud token life without control c
    "token_life_short_min": 15,        # 02: token life with control c
    "diff_after_min": 60,              # 09: the diff arrives at the end of the 1 hour window
    "alert_after_min": 5,              # 09: the persistence alert fires within 5 minutes
    "insider_activation_approved": True,  # NEW (13): an approver approves a tool admin's own activation of the tool admin role
    "approver_capacity_per_hour": 30,  # 16
    "backlog_flip_threshold": 60,      # NEW (16): queue size at which the team switches to auto-approve for everything
    "exception_expiry_hours": 72,      # 15
}

CASES = {}
def case(cid):
    def deco(f):
        CASES[cid] = f
        return f
    return deco


@case("PA-R1-01")
def c01(on, P):
    standing_others = 36
    if "a" not in on:
        return (standing_others,)                     # still standing, whatever the use rule says
    eligible = P["used_in_90_days"] if "b" in on else standing_others
    # c, the weekly check, only matters if someone drifts back to standing; nobody does in this run.
    return (eligible,)


@case("PA-R1-02")
def c02(on, P):
    ssh_open, token_holders, finished = 4, 3, 3
    if "a" not in on:
        return (ssh_open + token_holders + finished,)  # the role never goes
    ssh = 0 if "b" in on else ssh_open
    life = P["token_life_short_min"] if "c" in on else P["token_life_default_min"]
    tok = token_holders if life > 15 else 0
    return (ssh + tok,)


@case("PA-R1-03")
def c03(on, P):
    heavy, daily = 3, 1
    if "a" in on:
        all_day = 0                                    # nobody passes 8 hours in one activation
    else:
        all_day = P["heavy_extenders_approved"] if "b" in on else heavy
    daily_unseen = 0 if "c" in on else daily           # every one of their activations is within the rules
    return (all_day + daily_unseen,)


@case("PA-R1-04")
def c04(on, P):
    second_role_active = "a" not in on                 # the pair rule refuses the second activation
    admin_in_group = "c" not in on                     # the Tier 0 admin is moved out of the lower-tier group
    # b, the quarterly review, flags people; it removes nothing in this run.
    return (1 if (second_role_active and admin_in_group) else 0,)


@case("PA-R1-05")
def c05(on, P):
    sees_few = "a" in on                               # routine requests auto-approved, a person sees 5 not 50
    mismatches = 0 if "c" in on else 2                 # approvers do not compare the ticket's system themselves
    night = 0 if (sees_few and "b" in on) else 1       # caught only when the person sees few requests AND the risk is shown
    return (mismatches + night,)


@case("PA-R1-06")
def c06(on, P):
    people = 6
    if "a" in on:                                      # fail closed
        unchecked = 0
        blocked = 0 if "b" in on else people           # break-glass is the only way through
    else:
        unchecked = people                             # fail-open setting reuses the last approval
        # c raises an alert, but nobody acts within the 90 minute outage
        if "c" in on and P["alert_response_min"] < 90:
            unchecked = 0
        blocked = 0
    return (unchecked, blocked)


@case("PA-R1-07")
def c07(on, P):
    legit, injected, retry = 26, 3, 1
    if "b" in on:
        injected_granted = 0                           # finance-admin is not the database in the ticket
    elif "a" in on:
        injected_granted = P["person_approves_injected"]
    else:
        injected_granted = injected
    retry_granted = 0 if "c" in on else retry          # task-bound token folds the retry into the open task
    activations = legit + injected_granted + retry_granted
    hours_after = 0 if "c" in on else activations      # without c each activation holds a fixed hour
    return (injected_granted, hours_after)


@case("PA-R1-08")
def c08(on, P):
    tier0_ok = tier1_ok = False
    if "a" not in on:
        # No MFA at activation: the attacker activates with the stolen session on their own device.
        tier1_ok = True
        tier0_ok = "c" not in on                       # the step-up asks for MFA the attacker can't pass
    else:
        # The attacker waits for the victim's activation and replays the elevated token elsewhere.
        if "b" not in on:                              # no device binding
            tier1_ok = True
            tier0_ok = "c" not in on
    return (int(tier0_ok) + int(tier1_ok),)


@case("PA-R1-09")
def c09(on, P):
    items = 1 + (0 if "c" in on else 1)                # the secret is always created; c refuses the ownership change
    if "a" in on:
        found = P["alert_after_min"]
    elif "b" in on:
        found = P["diff_after_min"]
    else:
        found = -1
    return (items, found)


@case("PA-R1-10")
def c10(on, P):
    forgotten = 2
    if "a" in on and "b" in on:
        return (0,)                                    # found within the hour and removed
    return (forgotten,)                                # an alert (c) removes nothing


@case("PA-R1-11")
def c11(on, P):
    if "a" in on:
        return (0,)                                    # only a passkey can activate; the relay page can't use it
    relay = 2 + 2                                      # SMS users (or, with c, the same people on the code app) and TOTP users
    sim_swap = 0 if "c" in on else 1
    push = 0 if "b" in on else 1
    return (relay + sim_swap + push,)


@case("PA-R1-12")
def c12(on, P):
    # Planted: 2 ticket mismatches (Tier 1), 1 at 3 a.m. (Tier 1, risky), 1 out-of-role Tier 0 (risky),
    # 2 injected authority claims (Tier 1, first-time access to that secret, which the AI scores as risky).
    recommend = "a" in on
    approved = 0
    approved += 0 if "b" in on else 2                  # the AI reads the reason, not the ticket's system
    approved += 0 if "c" in on else 2                  # the authority claim outweighs the risk signal
    # The 3 a.m. and out-of-role requests are refused on their signals in both modes.
    reads = (3 + 1 + 1) if recommend else 0            # 4 Tier 0 requests plus the 3 a.m. one marked unsure
    return (approved, reads)


@case("PA-R1-13")
def c13(on, P):
    changes = 0
    # Change 1: the attacker, through a taken-over tool admin account.
    attacker_is_admin = "c" not in on                  # with c the role must be activated, and the attacker can't get approval
    if attacker_is_admin and "a" not in on:
        changes += 1
    # Change 2: a tool admin making themselves eligible for Tier 0.
    insider_is_admin = ("c" not in on) or P["insider_activation_approved"]
    if insider_is_admin and "a" not in on:
        changes += 1
    # b alerts; it does not block.
    return (changes,)


@case("PA-R1-14")
def c14(on, P):
    missed = (0 if "a" in on else 3) + (0 if "b" in on else 2) + (0 if "c" in on else 1)
    return (missed,)


@case("PA-R1-15")
def c15(on, P):
    incident = 2
    if "a" in on:
        return (0, 0)
    if "b" in on:
        return (0, 30)
    left = 0 if ("c" in on and P["exception_expiry_hours"] < 168) else incident
    return (left, -1)


@case("PA-R1-16")
def c16(on, P):
    if "a" in on:
        return (0,)                                    # the destructive step is outside every approved plan
    to_person = 20 if "b" in on else 120               # per hour
    backlog_after_hour_1 = max(0, to_person - P["approver_capacity_per_hour"])
    # c pauses an agent above 60 requests an hour; each agent asks 40, so it never fires here.
    if backlog_after_hour_1 > P["backlog_flip_threshold"]:
        return (1,)                                    # the team switches to auto-approve for everything before hour 2
    return (0,)


# Joint checks stated in the "Joint checks" section of the locked file.
JOINT = [
    ("PA-R1-04", "pair rule and group rule both off", {"b"}, (1,)),
    ("PA-R1-13", "two-person rule and the tool admin's own JIT both off", {"b"}, (2,)),
    ("PA-R1-15", "rota and escalation both off", {"c"}, (0, -1)),
    ("PA-R1-16", "plan approval and policy both off", {"c"}, (1,)),
]
JOINT_NOTE = {"PA-R1-15": "the guess says 2 exception assignments are made and removed after 72 hours: 0 left after a week"}


def parse_guesses(text):
    rows = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*(PA-R1-\d\d)\s*\|([^|]*)\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|", line)
        if m:
            rows.setdefault(m.group(1), []).append((m.group(2).strip(), [int(m.group(i)) for i in range(3, 8)]))
    return rows


SETTINGS = [("none", set()), ("all", {"a", "b", "c"}), ("off a", {"b", "c"}), ("off b", {"a", "c"}), ("off c", {"a", "b"})]


def run(P):
    out = []
    for cid in sorted(CASES):
        got = [CASES[cid](on, P) for _, on in SETTINGS]
        out.append((cid, got))
    return out


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
        for i, (label, g) in enumerate(guesses[cid]):
            model = [vals[i] for vals in got]
            diffs = [SETTINGS[k][0] for k in range(5) if model[k] != g[k]]
            total += 1
            matched += not diffs
            all_on = model[1]
            noticed = [SETTINGS[k][0][-1] for k in (2, 3, 4) if model[k] != all_on]
            rows.append({"id": cid, "counted": label, "guess": g, "model": model, "mismatch": diffs, "noticed": noticed})

    joint = []
    for cid, what, on, expect in JOINT:
        got = CASES[cid](on, PARAMS)
        joint.append({"id": cid, "check": what, "guess": list(expect), "model": list(got), "match": tuple(got) == expect,
                      "note": JOINT_NOTE.get(cid, "")})

    # Sensitivity: change one assumption at a time and list the rows that move.
    flips = {
        "person_approves_injected": 0, "heavy_extenders_approved": 3, "alert_response_min": 30,
        "insider_activation_approved": False, "backlog_flip_threshold": 200, "token_life_short_min": 30,
    }
    base = {cid: got for cid, got in run(PARAMS)}
    sens = []
    for k, v in flips.items():
        P2 = dict(PARAMS); P2[k] = v
        moved = [cid for cid, got in run(P2) if got != base[cid]]
        sens.append({"param": k, "was": PARAMS[k], "now": v, "cases_that_move": moved})

    result = {"guess_file": os.path.relpath(GUESS_FILE, HERE), "sha256": sha, "params": PARAMS, "rows": rows,
              "joint": joint, "sensitivity": sens,
              "summary": {"rows": total, "matched": matched, "mismatched": total - matched,
                          "joint_matched": sum(j["match"] for j in joint), "joint_total": len(joint)}}
    json.dump(result, open(os.path.join(OUT_DIR, "results-round-1.json"), "w"), indent=1)

    md = ["# Results: Privileged access lab, round 1", "",
          "Generated by `round1.py`. Guesses: `guesses/guesses-round-1.md`, sha256 " + sha + ".",
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
    open(os.path.join(OUT_DIR, "RESULTS-round-1.md"), "w").write("\n".join(md) + "\n")

    print("Guess file hash OK.")
    print("Rows matched: %d of %d. Joint checks matched: %d of %d." % (matched, total, result["summary"]["joint_matched"], len(joint)))
    print("Wrote results-round-1.json and RESULTS-round-1.md in", OUT_DIR)


if __name__ == "__main__":
    main()
