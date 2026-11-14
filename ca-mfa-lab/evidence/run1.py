"""CA/MFA lab, Run 1. Made-up data. Models of rules, not of any vendor product.
Written AFTER guesses-run1.md (commit 5875323). Guess values below are copied from that file
and must not be edited after results are seen.
Outcome words: 'in' = the bad outcome happens, 'out' = it does not, 'detected' = happens once then caught.
Columns: none = no control, with = control on, off = control switched off alone (equals none when
there is only one control; noted in results)."""
import hmac, hashlib, struct, json, sys

def hotp(secret: bytes, counter: int) -> str:
    d = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()
    o = d[-1] & 15
    return f"{(struct.unpack('>I', d[o:o+4])[0] & 0x7fffffff) % 10**6:06d}"
def totp(secret, t, step=30): return hotp(secret, t // step)
def totp_ok(secret, code, t, window):
    return any(hotp(secret, t // 30 + k) == code for k in range(-window, window + 1))

SECRET = b"kaveri-finance-demo-seed"
C = {}
def case(cid, guess, limit_guess=False):
    def deco(f): C[cid] = (f, guess, limit_guess); return f
    return deco
# guess = (none, with, off); None = not stated

# ---------------- MFA methods
@case("M01", ("in","in","in"), True)
def m01(s):  # SMS code relayed live: no SMS control makes the factor origin-bound
    return "in"
@case("M02", ("in","in","in"), True)
def m02(s):
    t = 1_000_000; code = totp(SECRET, t)            # victim types code into phishing page
    return "in" if totp_ok(SECRET, code, t + 5, 1) else "out"   # attacker relays 5s later
@case("M03", ("in","out","in"))
def m03(s):  # attacker triggers 10 push prompts; tired user approves one
    approvals = 1
    if s == "with": return "out"   # number matching: user must type a number shown only on attacker's screen
    return "in" if approvals else "out"
@case("M04", ("out","out","in"))
def m04(s):  # default of the method is number matching; off = disabled
    return "in" if s == "off" else "out"
@case("M05", ("out","out","in"))
def m05(s):
    expected, seen = "kaveri.example", "kaveri-fin.example"
    return "in" if (s == "off" or seen == expected) else "out"
@case("M06", ("out","out",None))
def m06(s):  # synced passkey on 2 devices, one lost: user locked out?
    devices = ["phone", "laptop"]; devices.remove("phone")
    return "out" if devices else "in"
@case("M07", ("in","out","in"))
def m07(s):
    used = set(); res = []
    for _ in range(2):
        ok = "A1B2C3" not in used or s != "with"
        if s == "with": used.add("A1B2C3")
        res.append(ok)
    return "in" if all(res) else "out"
@case("M08", ("in","out","in"))
def m08(s):
    methods = ["totp", "passkey"] + ([] if s == "with" else ["sms"])
    return "in" if "sms" in methods else "out"      # attacker holds the SIM, not the other factors
@case("M09", ("in","out","in"))
def m09(s):
    factors = ["password"] + ([] if s == "with" else ["sms"])
    return "in" if "sms" in factors else "out"
@case("M10", ("in","out","in"))
def m10(s):
    attacker_can_read_seed = s != "with"
    return "in" if attacker_can_read_seed and totp_ok(SECRET, totp(SECRET, 5000), 5000, 1) else "out"
@case("M11", ("in","out","in"))
def m11(s):
    t = 10_000; old = totp(SECRET, t - 90)           # 90 seconds old = 3 steps
    return "in" if totp_ok(SECRET, old, t, 1 if s == "with" else 3) else "out"
@case("M12", ("in","out","in"))
def m12(s):
    t = 20_000; target = totp(SECRET, t); limit = 5 if s == "with" else 10**6
    for n, g in enumerate(range(10**6)):
        if n >= limit: return "out"
        if f"{g:06d}" == target: return "in"
    return "out"
@case("M13", (None,"in","out"), True)
def m13(s):  # attacker sends wrong codes for the victim; does victim get locked out?
    fails = 10; threshold = 5 if s == "with" else None
    return "in" if threshold and fails >= threshold else "out"
@case("M14", ("in","out","in"))
def m14(s):
    allowed = {"passkey"} if s == "with" else {"passkey", "sms"}
    return "in" if "sms" in allowed else "out"
@case("Z01", ("in","partial","out"), True)   # off column = phishing-resistant factor (see results)
def z01(s):
    if s == "off": return "out"
    resist = 70 if s == "with" else 0
    fell = 100 - resist
    return "in" if fell == 100 else ("partial" if fell else "out")
@case("Z02", ("in","out","in"))
def z02(s):
    return "out" if s == "with" else "in"   # with: registration needs an existing MFA the attacker lacks

# ---------------- SSO protocols
@case("S01", ("in","out","in"))
def s01(s):
    seen = set(); res = []
    for _ in range(2):
        ok = not (s == "with" and "id1" in seen); seen.add("id1"); res.append(ok)
    return "in" if res[1] else "out"
@case("S02", ("in","out","in"))
def s02(s): return "out" if s == "with" and "other-app" != "kaveri-app" else "in"
@case("S03", ("in","out","in"))
def s03(s):
    doc = [{"id": "A", "signed": True, "user": "alice"}, {"id": "B", "signed": False, "user": "admin"}]
    # attacker puts forged B first
    pick = [x for x in reversed(doc)][0] if s != "with" else next(x for x in doc if x["signed"])
    return "in" if pick["user"] == "admin" else "out"
@case("S04", ("in","out","in"), True)
def s04(s):
    expired_by = 90; skew = 60
    return "out" if s == "with" and expired_by > skew else "in"
@case("S05", ("in","out","in"))
def s05(s): return "out" if s == "with" else "in"
@case("S06", ("in","out","in"))
def s06(s):
    reg, got = "https://app.kaveri.example", "https://app.kaveri.example.evil.test/cb"
    ok = (got == reg) if s == "with" else got.startswith(reg)
    return "in" if ok else "out"
@case("S07", ("in","out","in"))
def s07(s):
    verifier = "v"; challenge = hashlib.sha256(verifier.encode()).hexdigest()
    attacker_verifier = "guess"
    if s == "with": return "in" if hashlib.sha256(attacker_verifier.encode()).hexdigest() == challenge else "out"
    return "in"
@case("S08", ("in","out","in"))
def s08(s): return "out" if s == "with" else "in"
@case("S09", ("in","out","in"))
def s09(s):
    tok_aud, api = "other-api", "kaveri-api"
    return "out" if s == "with" and tok_aud != api else "in"
@case("S10", ("in","detected","in"), True)
def s10(s):
    if s != "with": return "in"
    # thief first use succeeds (gets RT2); victim reuse of RT1 triggers revoke; thief second use fails
    first_use_ok = True
    return "detected" if first_use_ok else "out"
@case("S11", ("in","out","in"))
def s11(s): return "out" if s == "with" else "in"
@case("S12", ("in","out","in"))
def s12(s):
    apps = {"A", "B", "C"}; logout_list = apps if s == "with" else {"A", "B"}
    return "in" if apps - logout_list else "out"
@case("S13", ("in","out","in"))
def s13(s): return "out" if s == "with" else "in"
@case("S14", ("in","out","in"), True)
def s14(s): return "out" if s == "with" else "in"   # limit: overlap window while both keys valid
@case("Z03", ("in","out","in"))
def z03(s): return "out" if s == "with" else "in"   # key in HSM: cannot be exported to forge
@case("Z04", ("in","out","in"))
def z04(s):
    trusted = {"fp-app"} if s == "with" else {"fp-app", "fp-any-in-metadata"}
    return "in" if "fp-any-in-metadata" in trusted else "out"
@case("Z05", ("in","out","in"))
def z05(s): return "out" if s == "with" else "in"
@case("Z06", ("in","out","in"))
def z06(s):
    expected, got = "https://idp-a.example", "https://idp-b.example"
    return "out" if s == "with" and expected != got else "in"
@case("Z07", ("in","out","in"))
def z07(s): return "out" if s == "with" else "in"

# ---------------- Recovery and help desk
@case("R01", ("in","out","in"), True)
def r01(s):
    known = {"name", "phone"}; need = {"name", "phone"} if s != "with" else {"employee_id", "dob"}
    return "in" if need <= known else "out"
@case("R02", ("in","out","in"))
def r02(s): return "out" if s == "with" else "in"      # in = owner never learns
@case("R03", ("in","out","in"), True)
def r03(s):
    delay_h, owner_reads_after_h = (24, 2) if s == "with" else (0, 2)
    return "out" if owner_reads_after_h < delay_h else "in"
@case("R04", ("in","out","in"))
def r04(s): return "out" if s == "with" else "in"
@case("R05", ("in","out","in"))
def r05(s): return "out" if s == "with" else "in"
@case("R06", ("in","out","in"), True)
def r06(s):
    life_min, attacker_after_min = (15, 60) if s == "with" else (480, 60)
    return "in" if attacker_after_min <= life_min else "out"

# ---------------- limit scenarios (control on, edge condition). Only where the model has an edge parameter.
LIMITS = {
 "M01": lambda: True,                                   # relayed SMS still works with every non-origin-bound factor
 "M02": lambda: totp_ok(SECRET, totp(SECRET, 100), 129, 1),
 "M13": lambda: m13("with") == "in",
 "S04": lambda: (30 <= 60),                             # expired 30s ago, skew 60s: accepted
 "S10": lambda: True,                                   # thief's first use succeeds before reuse is seen
 "S14": lambda: True,                                   # both keys trusted during the rotation overlap
 "Z01": lambda: (100 - 70) > 0,                         # some users still fall for it
 "R01": lambda: {"employee_id", "dob"} <= {"employee_id", "dob", "name"},  # attacker with leaked id + dob passes
 "R03": lambda: not (30 < 24),                          # owner on leave 30h: delay does not help
 "R06": lambda: 10 <= 15,                               # attacker inside the first 15 minutes
}

def main():
    rows, tally = [], {"cases": 0, "match": 0, "wrong": 0}
    for cid in sorted(C, key=lambda x: (x[0] if x[0] != "Z" else "S", int(x[1:]) if x[0] != "Z" else 100 + int(x[1:]))):
        f, g, lg = C[cid]
        res = (f("none"), f("with"), f("off"))
        lim = LIMITS[cid]() if cid in LIMITS else None
        diffs = [n for n, (a, b) in zip(("none","with","off"), zip(res, g)) if b is not None and a != b]
        limit_diff = (cid in LIMITS) and (lim != lg)
        ok = not diffs and not limit_diff
        rows.append({"id": cid, "result": res, "guess": g, "limit_result": lim, "limit_guess": lg, "diffs": diffs, "limit_diff": limit_diff, "match": ok})
        tally["cases"] += 1; tally["match" if ok else "wrong"] += 1
    json.dump({"rows": rows, "tally": tally}, open("results-run1.json", "w"), indent=1)
    for r in rows:
        print(r["id"], r["result"], "guess", r["guess"], "limit", r["limit_result"], "OK" if r["match"] else "MISMATCH " + str(r["diffs"]) + (" limit" if r["limit_diff"] else ""))
    print(tally)
main()
