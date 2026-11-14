"""CA/MFA lab, Run 5. Made-up data. Models of rule logic, not of any vendor product.
Written AFTER guesses-run5.md (merged as b184994, sha256 bc344bbd00d01d169c0dbde94d83fc628ec973dcbbb067d1c2cad3f74a65e63a).
Guess values are PARSED from that file, not retyped. Each case: sim(on, P) -> 'in' (bad outcome happens) or 'out'.
on = set of controls switched on. P = the assumptions (see PARAMS). Change a parameter and the result can change;
the sensitivity section at the end shows which cases flip.

Usage: python3 run5.py path/to/guesses-run5.md
"""
import re, json, sys, hashlib, copy

GUESS_FILE = sys.argv[1] if len(sys.argv) > 1 else "guesses-run5.md"
EXPECTED_SHA = "bc344bbd00d01d169c0dbde94d83fc628ec973dcbbb067d1c2cad3f74a65e63a"
got = hashlib.sha256(open(GUESS_FILE, "rb").read()).hexdigest()
if got != EXPECTED_SHA:
    sys.exit("Guess file hash does not match the locked file: " + got)

# ---- Assumptions written down in the guess file (and two the file leaves open, marked NEW)
PARAMS = {
    "p_no_read": 0.30,          # share of people who approve or accept without reading (W10, W11)
    "threshold": 0.05,          # a path counts as open if the bad outcome happens more often than this
    "session_hours": 1,         # cloud session from a short-lived token (W02)
    "poison_wait_hours": 24,    # the bad outcome is a credential still working this long after the run (W02)
    "attacker_delay_min": 2,    # minutes between theft and replay of an access token (W09)
    "short_token_min": 5,       # lifetime of the short access token (W09)
    "default_token_min": 60,    # lifetime without the short setting (W09)
    "b_covers_all_credentials": False,  # NEW (W08): step-up check B also applies to keys and service tokens
}

S = {}
def case(cid):
    def d(f): S[cid] = f; return f
    return d
def r(b): return "in" if b else "out"

# ---------------- CI/CD and DevOps
@case("W01")
def _(on, P):
    # Attacker's own repository asks the cloud for a role. Without A the trust policy only checks the issuer.
    attacker_sub = "repo:attacker/x:ref:refs/heads/main"
    allowed_sub = "repo:kaveri/deploy:ref:refs/heads/main"
    granted = (attacker_sub == allowed_sub) if "A" in on else True
    # B only blocks workflows triggered by pull requests; the attacker's run is a push in its own repository.
    # C narrows what the role can do; the credential is still a production credential.
    return r(granted)

@case("W02")
def _(on, P):
    poisoned_run = "A" not in on                      # unpinned action runs attacker code and steals what the run holds
    # B limits the workflow token; the cloud credential is a different secret, so B does not change this outcome.
    lifetime = P["session_hours"] if "C" in on else float("inf")   # stored cloud key never expires
    return r(poisoned_run and lifetime > P["poison_wait_hours"])

@case("W03")
def _(on, P):
    # The real cases chained mistakes: code runs from the pull request, secrets reach it, and the token request is allowed.
    runs_pr_code = "A" not in on
    secrets_reach_fork = "B" not in on
    token_on_unprotected_ref = "C" not in on
    return r(runs_pr_code and secrets_reach_fork and token_on_unprotected_ref)

@case("W04")
def _(on, P):
    paths = {
        "phished approver": "A" not in on,        # approval given by someone whose MFA was relayed
        "self approval": "B" not in on,
        "swap after approval": "C" not in on,     # approval not tied to the exact commit
    }
    return r(any(paths.values()))

# ---------------- APIs and integrations
@case("W05")
def _(on, P):
    # Needs the alternate login method to be enabled (A off) and the flaw unpatched (B off).
    # C is an alert; it does not block. Vendor lists no workaround for A: A is my own mitigation (see source note).
    alternate_method_enabled = "A" not in on
    flaw_present = "B" not in on
    return r(alternate_method_enabled and flaw_present)

@case("W06")
def _(on, P):
    all_objects = {"customers", "contacts", "invoices", "files"}
    needed = {"customers", "contacts"}                # the integration legitimately reads customer records
    scope = needed if "A" in on else all_objects
    from_vendor_address = False                      # the attacker uses the token from their own address
    blocked_by_allowlist = ("B" in on) and not from_vendor_address
    token_valid = True                               # attacker uses it within the day, so C's daily rotation has not run yet
    return r(token_valid and not blocked_by_allowlist and "customers" in scope)

@case("W07")
def _(on, P):
    refresh_alive_at_24h = "A" not in on             # only A revokes the refresh token on a password reset
    # B never fires (no MFA method changed). C only ends the access token; the refresh token mints a new one.
    return r(refresh_alive_at_24h)

@case("W08")
def _(on, P):
    both = P["b_covers_all_credentials"]
    paths = {
        "api key": ("A" not in on) and not (both and "B" in on),
        "replayed user token without step-up": "B" not in on,
        "service token with user-level scope": ("C" not in on) and not (both and "B" in on),
    }
    return r(any(paths.values()))

@case("W09")
def _(on, P):
    lifetime = P["short_token_min"] if "B" in on else P["default_token_min"]
    bound = "A" in on                                 # replay from another machine fails the proof of possession
    still_valid = P["attacker_delay_min"] < lifetime
    return r(still_valid and not bound)              # C (refresh rotation) does not touch an access token

# ---------------- Agents and MCP
@case("W10")
def _(on, P):
    p = 1.0                                           # injected text asks for a write the person did not ask for
    if "A" in on: p = 0.0                             # the task token has no scope for those records
    if "B" in on: p *= P["p_no_read"]                 # a person approves it without reading
    return r(p > P["threshold"])                      # C only logs

@case("W11")
def _(on, P):
    p = 1.0                                           # attacker's server names its own authorization server
    if "A" in on: p = 0.0                             # not on the client's allow-list
    # B: the attacker's metadata names itself as issuer, so the match passes; B changes nothing.
    if "C" in on: p *= P["p_no_read"]                 # the user fails to notice the odd sign-in address
    return r(p > P["threshold"])

# ---------------- Recovery
@case("W12")
def _(on, P):
    self_service_path = "A" not in on
    help_desk_path = "B" not in on
    return r(self_service_path or help_desk_path)    # C limits use of the new method, not whether it is enrolled

# ---------------- driver (same parse and layout as run2.py)
def parse():
    G = {}
    for line in open(GUESS_FILE, encoding="utf-8"):
        m = re.match(r"^(W\d{2}) \| (.*)$", line.strip())
        if not m: continue
        f = [x.strip() for x in m.group(2).split(" | ")]
        letters = re.findall(r"\b([ABC]) ", f[0])
        first = lambda s: (s.split()[0] if s else "-")
        G[m.group(1)] = {"letters": sorted(set(letters)), "g": [first(x) for x in f[2:7]]}
    return G

def run_all(G, P):
    rows = []
    for cid, fn in S.items():
        L = G[cid]["letters"]; allc = set(L)
        res = [fn(set(), P), fn(allc, P)] + [fn(allc - {c}, P) for c in "ABC"]
        res = [x if i < 2 or "ABC"[i-2] in L else "-" for i, x in enumerate(res)]
        g = G[cid]["g"]
        diffs = [n for n, a, b in zip(("none","all","offA","offB","offC"), res, g) if a != b]
        rows.append({"id": cid, "controls": L, "result": res, "guess": g, "diffs": diffs})
    return rows

def main():
    G = parse()
    assert sorted(G) == sorted(S), (sorted(G), sorted(S))
    rows = run_all(G, PARAMS)
    for rw in rows:
        print(rw["id"], rw["result"], "guess", rw["guess"], "OK" if not rw["diffs"] else "MISMATCH " + ",".join(rw["diffs"]))
    full = [rw for rw in rows if not rw["diffs"]]
    print("cases", len(rows), "full match", len(full), "mismatched", [rw["id"] for rw in rows if rw["diffs"]])
    no_single_in = [rw["id"] for rw in rows if all(x != "in" for x in rw["result"][2:])]
    print("all-on out:", sum(1 for rw in rows if rw["result"][1] == "out"), "of", len(rows),
          "| at least one single-off in:", len(rows) - len(no_single_in), "| no single-off in:", no_single_in)

    # ---- Sensitivity: change one assumption at a time and list the cases whose result changes
    variants = {
        "p_no_read 0.02 (people almost always read)": {"p_no_read": 0.02},
        "p_no_read 0.60": {"p_no_read": 0.60},
        "session_hours 25 (cloud session outlasts the wait)": {"session_hours": 25},
        "attacker_delay_min 10 (replay after the short token ends)": {"attacker_delay_min": 10},
        "b_covers_all_credentials True (step-up check applies to keys and service tokens)": {"b_covers_all_credentials": True},
    }
    sens = []
    base = {rw["id"]: rw["result"] for rw in rows}
    for name, ch in variants.items():
        P2 = copy.deepcopy(PARAMS); P2.update(ch)
        flips = []
        for rw in run_all(G, P2):
            if rw["result"] != base[rw["id"]]:
                flips.append({"id": rw["id"], "was": base[rw["id"]], "now": rw["result"]})
        sens.append({"change": name, "flips": flips})
        print("SENS", name, "->", [(f["id"], f["was"], f["now"]) for f in flips] or "no change")
    json.dump({"params": PARAMS, "rows": rows, "sensitivity": sens}, open("results-run5.json", "w"), indent=1)
main()
