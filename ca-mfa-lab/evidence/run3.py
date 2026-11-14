"""CA/MFA lab, Run 3. Made-up data (Kaveri Finance). Small models of rule logic, not of any vendor product.
Written AFTER guesses-run3.md (committed on the Mac as f8d6676, sha256 a09daa45...). Guess values are PARSED from
that file, not retyped. Each case: sim(on) -> 'in' (bad outcome happens) or 'out'. on = set of controls switched on.
Unlike Run 2, each model here walks the attack step by step over small token, claim and policy objects, so the
result comes from the steps and not from one boolean line. The assumptions each model rests on are in ASSUME."""
import re, json, sys

GUESS_FILE = sys.argv[1] if len(sys.argv) > 1 else "../guesses-run3.md"
S, ASSUME = {}, {}
def case(cid, assume):
    def d(f): S[cid] = f; ASSUME[cid] = assume; return f
    return d
def r(b): return "in" if b else "out"

H = 3600

# ---------------- PAM and step-up
@case("Y01", "attacker holds a session opened 6 hours ago with MFA; he has no second factor; the app asks the IdP for step-up")
def _(on):
    token = {"amr": ["pwd", "mfa"], "age": 6 * H}
    fresh = token["age"] <= 900
    if "A" in on and not fresh:                       # app inspects the token and asks for step-up
        stepped_up = "B" in on and False              # the IdP can ask, but only the real user can answer
        return r(stepped_up)
    return r(True)                                    # app never looks: the privileged action runs on the old session

@case("Y02", "privileged scopes exist; a background job holds a user-delegated token; step-up needs a live session")
def _(on):
    interactive_bad = "A" not in on                   # no step-up challenge on live sessions
    bg_scopes = {"read", "privileged"}
    if "B" in on: bg_scopes = {"read"}                # service identity gets only what the job needs
    if "C" in on: bg_scopes -= {"privileged"}         # user-delegated tokens lose privileged scopes
    background_bad = "privileged" in bg_scopes        # no live session, so no challenge can fire
    return r(interactive_bad or background_bad)

# ---------------- Federation
@case("Y03", "attacker has a Global Admin session; second approver is a different, honest person; alert is read after the fact")
def _(on):
    alerts = []
    domain_added = True
    if "A" in on: alerts.append("federation change")  # a notice, nothing is stopped
    if "B" in on: domain_added = False                # approval refused
    if not domain_added: return "out"
    forged_claim = {"amr": ["mfa"], "issuer": "attacker-domain"}
    mfa_prompt = "C" in on                            # cloud asks for its own MFA whatever the claim says
    attacker_has_factor = False
    treated_as_done = (not mfa_prompt) and "mfa" in forged_claim["amr"]
    return r(treated_as_done or (mfa_prompt and attacker_has_factor))

@case("Y04", "attacker is on a compromised internal workstation with the user's password only")
def _(on):
    idp_requires_mfa = "B" in on                      # without B the IdP skips MFA for internal addresses
    claim_mfa = True                                  # the IdP stamps 'mfa' on the token either way
    cloud_requires_mfa = "A" in on
    if cloud_requires_mfa: return "out"               # cloud asks again; attacker has no factor
    if idp_requires_mfa: return "out"                 # the IdP asked; attacker has no factor
    return r(claim_mfa)                               # claim accepted: password alone got in

# ---------------- Mobile and native apps
@case("Y05", "attacker's own unmanaged phone; Authenticator broker can be installed by anyone; unknown device state = refuse")
def _(on):
    for client in ("browser", "native_no_broker", "native_broker"):
        if "B" in on and client != "native_broker": continue   # only the broker is an allowed client
        device_state = "unknown" if client != "native_broker" else "registered_not_compliant"
        if "A" in on and device_state != "compliant": continue # compliant device rule refuses
        return "in"                                            # some path got through
    return "out"

@case("Y06", "attacker has password and relayed MFA; unmanaged host; policy engine skips paths it does not target (verify)")
def _(on):
    for path in ("direct", "nested"):
        policy_reaches = ("A" in on) or path == "direct"
        if policy_reaches and "B" in on: continue      # compliant-device check refuses the unmanaged host
        return "in"                                    # either no policy reached the path, or it asked for MFA only and MFA was relayed
    return "out"

@case("Y07", "attacker code runs inside the user's browser on the compliant, managed device")
def _(on):
    extension_installs = "C" not in on
    if not extension_installs: return "out"
    token_from_same_device = True                     # the extension acts in place, it does not export the token
    device_compliant = True
    bound_ok = True                                   # token binding is satisfied from the bound device
    return r(device_compliant and bound_ok and token_from_same_device)

# ---------------- Passkeys and recovery
@case("Y08", "malware already on the endpoint; synced passkey path can be driven without the local prompt (verify)")
def _(on):
    paths = []
    paths.append({"name": "device_bound", "uv_needed": "A" in on})
    if "B" not in on: paths.append({"name": "synced", "uv_needed": False})   # cloud authenticator path
    for p in paths:
        if not p["uv_needed"]: return "in"             # assertion made with no user action
    return "out"

@case("Y09", "attacker has a stolen session; the user reports within the day; reporting revokes sessions; the user acts on an alert")
def _(on):
    registered = "A" not in on                         # no fresh strong sign-in required to add a method
    alert_seen = "C" in on
    revoked_methods = "B" in on and alert_seen         # revoke runs when someone acts on the alert
    return r(registered and not revoked_methods)

# ---------------- Resilience
@case("Y10", "main MFA provider is down; attacker has the password; second provider is up if it exists")
def _(on):
    main_up = False
    second_up = "C" in on
    mfa_available = main_up or second_up
    if mfa_available: return "out"
    fail_closed = "A" in on
    return r(not fail_closed)                          # fail open = password alone accepted

# ---------------- Agents and MCP
@case("Y11", "victim declines consent for a client they do not know; attacker registers a client with his own redirect URI")
def _(on):
    attacker_registers = "B" not in on                 # redirect URIs not limited to a pre-registered list
    if not attacker_registers: return "out"
    mcp_consent_shown = "A" in on
    crafted_request_with_cookie = "C" not in on        # cookie already set before consent lets a crafted request skip it
    if mcp_consent_shown and not crafted_request_with_cookie: return "out"   # victim says no
    return "in"                                        # third-party cookie or early cookie skips consent

@case("Y12", "attacker holds a token issued for another service (audience = 'payroll-api'); downstream is 'ledger-api'")
def _(on):
    tok = {"aud": "payroll-api", "sub": "user1"}
    if "A" in on and tok["aud"] != "mcp-server": return "out"
    if "B" in on:
        downstream_tok = {"aud": "ledger-api", "sub": tok["sub"]}   # exchange, valid for the downstream
    else:
        downstream_tok = tok                                        # passthrough
    if "C" in on and downstream_tok["aud"] != "ledger-api": return "out"
    return "in"

@case("Y13", "the leak happens; attacker uses the token 2 hours later and tries data outside the task")
def _(on):
    token = {"ttl": 0.75 * H if "A" in on else 24 * H, "scope": {"task:report"} if "B" in on else {"task:report", "all:data"}}
    useful_late = token["ttl"] > H
    useful_wide = len(token["scope"] - {"task:report"}) > 0
    return r(useful_late or useful_wide)

@case("Y14", "prompt injection in a document tells the agent to delete records; the token allows delete")
def _(on):
    token_allows = True
    per_call_ok = token_allows                         # a permission check passes for an allowed action
    action_is_irreversible = True
    marked = "C" in on and action_is_irreversible      # the server knows this action needs a person
    person_asked = "B" in on and marked
    person_declines = True
    if person_asked and person_declines: return "out"
    return r(per_call_ok)

# ---------------- Chains
@case("Y15", "extension steals a session; attacker tries to register a passkey; user reports; sessions are revoked")
def _(on):
    if "A" in on: return "out"                         # no extension, no stolen session
    can_register = "B" not in on
    if not can_register: return "out"
    revoked_recent = "C" in on
    return r(not revoked_recent)

@case("Y16", "malicious MCP client tries to get a token; if it gets one, it is judged broad or long")
def _(on):
    if "A" in on: return "out"                         # per-client consent: victim refuses the unknown client
    token = {"scope": "narrow" if "B" in on else "broad", "ttl": 0.5 * H if "C" in on else 24 * H}
    return r(token["scope"] == "broad" or token["ttl"] > H)

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
        diffs = [n for n, a, b in zip(("none", "all", "offA", "offB", "offC"), res, g) if a != b]
        row = {"id": cid, "controls": L, "result": res, "guess": g, "diffs": diffs, "assumes": ASSUME[cid]}
        # not guessed beforehand, reported only as extra information: two controls off together
        if len(L) == 3:
            row["extra_two_off_not_guessed"] = {"".join(sorted(p)): fn(allc - set(p)) for p in (("A","B"),("A","C"),("B","C"))}
        rows.append(row)
        if diffs: mism.append((cid, diffs))
    json.dump(rows, open("results-run3.json", "w"), indent=1)
    for rw in rows: print(rw["id"], rw["result"], "guess", rw["guess"], "OK" if not rw["diffs"] else "MISMATCH " + ",".join(rw["diffs"]))
    print("cases", len(rows), "full match", len(rows) - len(mism), "mismatched", [m[0] for m in mism])
    no_single_in = [rw["id"] for rw in rows if all(x != "in" for x in rw["result"][2:])]
    any_single_in = len(rows) - len(no_single_in)
    all_out = sum(1 for rw in rows if rw["result"][1] == "out")
    print("all-on out:", all_out, "of", len(rows), "| at least one single-off in:", any_single_in, "| no single-off in:", no_single_in)
main()
