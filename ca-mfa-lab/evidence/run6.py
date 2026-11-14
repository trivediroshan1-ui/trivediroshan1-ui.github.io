"""CA/MFA lab, Run 6 (AI agent identity). Made-up data. Models of rule logic, not of any vendor product.
Written AFTER guesses-run6.md (merged as d7183d5, pull request #110,
sha256 1abdbf110b58375570d3472f3aefc697b41931f236a53001c1f9d836f01ec22f).
Guess values are PARSED from that file, not retyped. Each case: sim(on, P) -> 'in' (bad outcome happens) or 'out'.
on = set of controls switched on. P = the assumptions (see PARAMS). The sensitivity section shows which cases flip.
E04 to E06 in the guess file are hand tests for other people; they have no model here.

Usage: python3 run6.py path/to/guesses-run6.md
"""
import re, json, sys, hashlib, copy

GUESS_FILE = sys.argv[1] if len(sys.argv) > 1 else "guesses-run6.md"
EXPECTED_SHA = "1abdbf110b58375570d3472f3aefc697b41931f236a53001c1f9d836f01ec22f"
got = hashlib.sha256(open(GUESS_FILE, "rb").read()).hexdigest()
if got != EXPECTED_SHA:
    sys.exit("Guess file hash does not match the locked file: " + got)

# ---- Assumptions from the guess file, plus the ones it leaves open (marked NEW)
PARAMS = {
    "threshold": 0.05,               # a path counts as open if the bad outcome happens more often than this
    "p_no_read": 0.30,               # G02: share of people who confirm without reading
    "assertion_hours": 24,           # G01: life of the agent's cached identity assertion
    "check_after_min": 60,           # G01: the question is asked 1 hour after revocation
    "default_token_min": 60,         # NEW (G01): second-app token life without B
    "orchestrator_own_identity": True,  # NEW (G03): the parent agent acts with its own broad identity, not the human's
    "review_interval_days": 90,      # G04: access review cycle
    "check_day_g04": 60,             # G04: the question is asked 60 days after the project ends
    "attacker_same_network": False,  # G07: the attacker replays from a different network
    "scanner_reads_logs": True,      # G09: secret scanning covers build logs
    "default_retention_days": 7,     # G10: log retention without C
}

S = {}
def case(cid):
    def d(f): S[cid] = f; return f
    return d
def r(b): return "in" if b else "out"

# ---------------- Agent sign-in across apps
@case("G01")
def _(on, P):
    t = P["check_after_min"]
    # Path 1: the token issued just before revocation. Revoked at once by A, otherwise lives its lifetime.
    life = 5 if "B" in on else P["default_token_min"]
    old_token_works = ("A" not in on) and life > t
    # Path 2: the agent exchanges its cached assertion for a new token. Only C checks the grant on exchange.
    new_token = ("C" not in on) and P["assertion_hours"] * 60 > t
    return r(old_token_works or new_token)

# ---------------- Agents acting for people
@case("G02")
def _(on, P):
    p = 1.0                                   # injected ticket text asks for a reset of another account
    if "A" in on: p = 0.0                     # the target was not named by the human
    if "B" in on: p *= P["p_no_read"]         # the human confirms without reading the target
    # C logs the reset; it does not stop it.
    return r(p > P["threshold"])

@case("G03")
def _(on, P):
    human = {"finance:read"}
    parent = {"finance:read", "finance:write"} if P["orchestrator_own_identity"] else set(human)
    task = {"finance:write"}                  # the human asked for an update
    child = (parent & (task | {"finance:read"})) if "A" in on else parent
    can_write = "finance:write" in child
    if "C" in on: can_write = can_write and "finance:write" in human   # resource checks the human's permissions
    # B shortens the token; the write happens within minutes, so B does not change reach.
    return r(can_write)

@case("G10")
def _(on, P):
    retention = 90 if "C" in on else P["default_retention_days"]
    logs_exist = retention >= 30
    human_in_logs = "A" in on                 # chain starts at a shared service account; only A records the human
    # B links the hops to each other, but every hop leads back to the service account without A.
    return r(not (logs_exist and human_in_logs))

# ---------------- Agent and workload lifecycle
@case("G04")
def _(on, P):
    if "A" in on: return r(False)             # identity expired at project end
    # B rotates the credential and hands the new one to the agent: still works.
    p = 1.0
    if "C" in on:
        p = max(0.0, 1 - P["check_day_g04"] / P["review_interval_days"])   # chance no review fell inside the window
    return r(p > P["threshold"])

@case("G05")
def _(on, P):
    sponsor_recorded = "A" in on
    fixed = sponsor_recorded and ("B" in on)  # departure of a recorded sponsor triggers reassignment within 7 days
    # C flags the agent; a flag does not reassign or disable it.
    return r(not fixed)

@case("G06")
def _(on, P):
    refresh_issued = "A" not in on            # unapproved personal agent gets a refresh token only without A
    if not refresh_issued: return r(False)    # access token alone ends within the hour
    alive_at_day7 = "B" not in on             # B ends refresh tokens 24 hours after sign-in, rotation or not
    usable_by_attacker = "C" not in on        # C binds tokens to the agent's device
    return r(alive_at_day7 and usable_by_attacker)

@case("G07")
def _(on, P):
    session_hours = 8 if "B" in on else 24
    alive = session_hours > 1
    if "A" in on and not P["attacker_same_network"]: alive = False
    if "C" in on: alive = False               # cookie is useless off the bound device
    return r(alive)

@case("G08")
def _(on, P):
    life_days = 1 if "B" in on else 365
    if life_days < 7: return r(False)
    revoked_and_checked = ("A" in on) and ("C" in on)
    return r(not revoked_and_checked)

@case("G09")
def _(on, P):
    if "A" in on: return r(False)             # nothing stored to leak; the copied token expired in an hour
    if "B" in on and P["scanner_reads_logs"]: return r(False)
    p = 1.0
    if "C" in on: p = 1 - 30 / 90             # chance the 90-day rotation has not happened yet
    return r(p > P["threshold"])

# ---------------- driver (same parse and layout as run5.py)
def parse():
    G = {}
    for line in open(GUESS_FILE, encoding="utf-8"):
        m = re.match(r"^(G\d{2}) \| (.*)$", line.strip())
        if not m: continue
        f = [x.strip() for x in m.group(2).split(" | ")]
        letters = re.findall(r"\b([ABC]) ", f[0])
        first = lambda s: (s.split()[0] if s else "-")
        G[m.group(1)] = {"letters": sorted(set(letters)), "g": [first(x) for x in f[2:7]]}
    return G

def run_all(G, P):
    rows = []
    for cid in sorted(S):
        fn = S[cid]; L = G[cid]["letters"]; allc = set(L)
        res = [fn(set(), P), fn(allc, P)] + [fn(allc - {c}, P) for c in "ABC"]
        g = G[cid]["g"]
        diffs = [n for n, a, b in zip(("none", "all", "offA", "offB", "offC"), res, g) if a != b]
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
    variants = {
        "p_no_read 0.02 (people almost always read the confirmation)": {"p_no_read": 0.02},
        "default_token_min 90 (second-app tokens outlive the hour)": {"default_token_min": 90},
        "orchestrator_own_identity False (the parent agent acts with the human's own token)": {"orchestrator_own_identity": False},
        "review_interval_days 30 (monthly access review)": {"review_interval_days": 30},
        "attacker_same_network True (attacker replays through a proxy on the victim's network)": {"attacker_same_network": True},
        "scanner_reads_logs False (secret scanning does not cover build logs)": {"scanner_reads_logs": False},
        "default_retention_days 45 (logs kept 45 days without C)": {"default_retention_days": 45},
    }
    sens = []; base = {rw["id"]: rw["result"] for rw in rows}
    for name, ch in variants.items():
        P2 = copy.deepcopy(PARAMS); P2.update(ch)
        flips = [{"id": rw["id"], "was": base[rw["id"]], "now": rw["result"]} for rw in run_all(G, P2) if rw["result"] != base[rw["id"]]]
        sens.append({"change": name, "flips": flips})
        print("SENS", name, "->", [(f["id"], f["was"], f["now"]) for f in flips] or "no change")
    json.dump({"params": PARAMS, "rows": rows, "sensitivity": sens}, open("results-run6.json", "w"), indent=1)
main()
