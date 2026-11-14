"""CA/MFA lab, Run 2. Made-up data. Models of rule logic, not of any vendor product.
Written AFTER guesses-run2.md (commit 7d31554, sha256 f7c8439b...). Guess values are PARSED from that file,
not retyped. Each case: sim(on) -> 'in' (bad outcome happens) or 'out'. on = set of controls that are switched on."""
import re, json, itertools, sys
GUESS_FILE = sys.argv[1] if len(sys.argv) > 1 else "../guesses-run2.md"
S = {}
def case(cid):
    def d(f): S[cid] = f; return f
    return d
def r(b): return "in" if b else "out"

# ---------------- Policy logic
@case("P01")
def _(on): return r("A" not in on)                      # grant listed last wins unless block overrides
@case("P02")
def _(on): return r(not ({"A","B"} <= on))              # unlisted app cannot be fronted; listing alone changes nothing
@case("P03")
def _(on):
    members = 3 + 6                                      # 3 at start, +1 a month for 6 months
    if "A" in on: members = 3                            # entries older than 3 months expire (owners renew none)
    if "B" in on: members = min(members, 5)              # assumption: reviewer keeps at most the 5 justified
    return r(members > 5)
@case("P04")
def _(on):
    locked = "A" not in on                               # misconfigured block-all rule hits an account not excluded
    unnoticed = ("A" in on) and ("B" not in on)
    return r(locked or unnoticed)
@case("P05")
def _(on):
    if "A" in on: return "out"                           # pre-enable check finds the account
    signins_in_report_week = 0                           # emergency account never signs in during the week
    caught = "B" in on and signins_in_report_week > 0
    return r(not caught)
@case("P06")
def _(on): return r(not ({"A","B"} <= on))               # need the data (A) and someone reading it (B)
@case("P07")
def _(on):
    blocked = 0.05 if "A" in on else 1.0                 # rule breaks for everyone it reaches
    return r(blocked > 0.05)
@case("P08")
def _(on): return r(("A" not in on) or ("B" not in on)) # two open paths: legacy and modern
@case("P09")
def _(on):
    outage = "A" not in on                               # user MFA rule applies to the service account
    unprotected = ("A" in on) and ("B" not in on)
    return r(outage or unprotected)
@case("P10")
def _(on): return r(not ({"A","B"} & on))                # planted error is caught by test plan or by review
@case("P11")
def _(on): return r("A" not in on)                       # an unauthorised change skips approval by definition, so only the log can show it (assumed read within 7 days)

# ---------------- Context signals
@case("X01")
def _(on):
    if "A" in on: return "out"                           # unmanaged device refused
    return r("B" not in on)                              # browser-only session blocks download
@case("X02")
def _(on):
    device_offline_days = 3
    stale_refused = "A" in on and device_offline_days * 24 > 24
    event_revoked = "B" in on and device_offline_days == 0   # offline device sends no event
    return r(not (stale_refused or event_revoked))
@case("X03")
def _(on): return r("A" in on and "B" not in on)         # traveller on the exception list
@case("X04")
def _(on): return r("B" not in on)                       # proxy is in an allowed country; only the device check stops it
@case("X05")
def _(on): return r("B" not in on)                       # risk score is low so step-up never fires
@case("X06")
def _(on): return r("A" in on and "B" not in on)         # false positive block; remediation clears it in 10 minutes
@case("X07")
def _(on): return r("A" not in on and "B" not in on)    # A off: guest wifi counts as trusted, MFA skipped; B still blocks unmanaged device
@case("X08")
def _(on): return r("A" not in on)                       # same country, so location revoke never fires
@case("X09")
def _(on): return r("A" not in on)                       # refresh tokens renew access tokens silently unless interactive reauth
# ---------------- Privileged roles
@case("A01")
def _(on): return r("B" not in on)                       # A covers portals only; SMS on another app needs B
@case("A02")
def _(on): return r("A" not in on)                       # a 1 hour limit does not stop activation
@case("A03")
def _(on): return r("B" not in on)                       # separate accounts do not stop an admin account browsing a risky app
@case("A04")
def _(on): return r(not ({"A","B"} <= on))
@case("A05")
def _(on):
    home_claim_trusted = "A" in on                       # home tenant claim is weak (SMS only) and trusted as MFA
    return r(home_claim_trusted or "B" not in on)
# ---------------- Chains
@case("C01")
def _(on):
    taken = ("A" not in on) or ("B" not in on)
    return r(taken and "C" not in on)                    # bad = taken AND unnoticed
@case("C02")
def _(on):
    works_30min = "A" not in on                          # same country: location revoke useless
    works_4h = "A" not in on and "B" not in on
    return r(works_30min or works_4h)
@case("C03")
def _(on):
    local_login = "A" not in on                          # not an exclusion, so alert C does not see it
    excluded_account_used = "B" not in on
    unnoticed = local_login or (excluded_account_used and "C" not in on)
    return r(unnoticed)
@case("C04")
def _(on): return r("B" not in on)                       # report-only never sees an account that does not sign in
@case("C05")
def _(on): return r(("A" not in on) and ("B" not in on)) # needs SMS fallback AND an uncaught swap
# ---------------- Auth flows and extras
@case("Z08")
def _(on):
    if "A" in on: return "out"
    fall = 40 if "B" in on else 100                      # of 100 users
    return r(fall > 0)
@case("Z09")
def _(on): return r(not ({"A","B"} & on))
@case("Z10")
def _(on): return r("A" not in on)                       # unverified apps cannot get user consent; workflow only matters if users can ask
@case("Z11")
def _(on): return r("B" not in on)
@case("Z12")
def _(on): return r("A" not in on)                       # B only alerts
@case("Z13")
def _(on): return r("A" not in on)
@case("Z14")
def _(on): return r("A" not in on)                       # B only alerts, registration still happens
@case("Z15")
def _(on):
    lasts_h = 7 * 24 if "A" in on else 10**6             # weekly apply
    if "B" in on: lasts_h = min(lasts_h, 24)             # detected and fixed at the daily check
    return r(lasts_h > 24)
@case("Z16")
def _(on): return r("A" not in on)
@case("Z17")
def _(on): return r(not ({"A","B","C"} & on))
@case("Z18")
def _(on):
    if "A" in on: return "out"
    return r(15 > 10)                                    # token lifetime 15 min: still works 10 min after revoke
@case("Z19")
def _(on): return r("A" not in on)
@case("Z20")
def _(on): return r("A" not in on)
@case("Z21")
def _(on):
    obtained = "A" not in on
    usable_at_24h = obtained and "B" not in on           # refresh token dies at 1 hour; C blocks only the unmanaged device
    return r(usable_at_24h)
@case("Z22")
def _(on):
    registers_own_mfa = "A" not in on
    passes_mfa = "C" not in on or registers_own_mfa
    return r(passes_mfa and "B" not in on)

PAIRS = {"C05": {"A","B"}, "Z21": {"A","C"}, "Z22": {"A","B"}}   # guess: these pairs OFF together give 'in'

def parse():
    G = {}
    for line in open(GUESS_FILE):
        m = re.match(r"^([A-Z]\d{2}) \| (.*)$", line.strip())
        if not m: continue
        f = [x.strip() for x in m.group(2).split(" | ")]
        letters = re.findall(r"\b([ABC]) ", f[0])
        first = lambda s: (s.split()[0] if s else "-")
        G[m.group(1)] = {"letters": sorted(set(letters)), "g": [first(x) for x in f[2:7]]}
    return G

def main():
    G = parse(); rows = []; mism = []
    for cid, fn in S.items():
        L = G[cid]["letters"]; allc = set(L)
        res = [fn(set()), fn(allc)] + [fn(allc - {c}) for c in "ABC"]
        res = [x if i < 2 or "ABC"[i-2] in L else "-" for i, x in enumerate(res)]
        g = G[cid]["g"]
        diffs = [n for n, a, b in zip(("none","all","offA","offB","offC"), res, g) if a != b]
        row = {"id": cid, "controls": L, "result": res, "guess": g, "diffs": diffs}
        if cid in PAIRS: row["pair_off"] = sorted(PAIRS[cid]); row["pair_result"] = fn(allc - PAIRS[cid]); row["pair_guess"] = "in"
        rows.append(row)
        if diffs or (cid in PAIRS and row["pair_result"] != "in"): mism.append((cid, diffs, row.get("pair_result")))
    json.dump(rows, open("results-run2.json", "w"), indent=1)
    for rw in rows: print(rw["id"], rw["result"], "guess", rw["guess"], "OK" if not rw["diffs"] else "MISMATCH " + ",".join(rw["diffs"]), ("pair " + str(rw["pair_result"])) if "pair_off" in rw else "")
    print("cases", len(rows), "full match", len(rows) - len(mism), "mismatched", [m[0] for m in mism])
    no_single_in = [rw["id"] for rw in rows if all(x != "in" for x in rw["result"][2:])]
    any_single_in = len(rows) - len(no_single_in)
    all_out = sum(1 for rw in rows if rw["result"][1] == "out")
    print("all-on out:", all_out, "of", len(rows), "| at least one single-off in:", any_single_in, "| no single-off in:", no_single_in)
main()
