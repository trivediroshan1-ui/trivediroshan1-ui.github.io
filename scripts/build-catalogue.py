#!/usr/bin/env python3
"""One catalogue of every case in the four labs (LAB-02): data/catalogue.json and /labs/cases/.

Reads each lab's own published data, so nothing is retyped:
  CA lab   ca-mfa-lab/data/cases.js            (130 rows; guess matched or not, or not run)
  NHI lab  nhi-lab/audit/nhi-lab-audit.json    (67 cases; guess matched yes or no)
  AI governance  assets/agl-data.js and agl-r5.js to agl-r13.js (expected, actual, verdict)
  MCP lab  mcp-lab/use-cases/index.html        (the use cases; what I expected and what happened)
Topics are matched from the case's own words with the keyword list below, so they are a
finding aid, not a judgement. Needs node. Run:  python3 scripts/build-catalogue.py
"""
import html, json, pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from page_shell import shell, write, set_stat, ROOT

LABS = {
    "ca": ("Conditional access, MFA and AI agent lab", "/ca-mfa-lab/"),
    "nhi": ("Machine identity lab", "/nhi-lab/"),
    "agl": ("AI governance lab", "/ai-governance-lab/"),
    "mcp": ("HumanGate MCP lab", "/mcp-lab/"),
}
TOPICS = [  # (topic, words that put a case in it; matched on whole-word starts, case ignored)
    ("Recovery and help desk", ["recover", "help desk", "helpdesk", "reset", "lost phone", "backup code", "lockout"]),
    ("MFA and passkeys", ["mfa", "passkey", "fido", "otp", "sms", "push", "authenticator", "phishing-resistant", "factor", "number match"]),
    ("Sign-in, sessions and policy", ["conditional access", "session", "sign-in", "signin", "device", "location", "risk", "policy", "sso", "saml", "oidc", "oauth", "federation", "cookie"]),
    ("Secrets, keys and tokens", ["secret", "key", "token", "credential", "password", "certificate", "rotat", "vault", "bearer"]),
    ("Ownership and inventory", ["owner", "inventory", "orphan", "unowned", "discover", "register", "shadow", "unknown"]),
    ("Approvals and separation of duties", ["approv", "second person", "two people", "self-approv", "four-eyes", "separation", "signoff", "sign-off"]),
    ("AI agents, models and tools", ["agent", "tool", "mcp", "prompt", "model", "llm", "delegat", "assistant", "embedding", "rag"]),
    ("Privileged access", ["privileg", "admin", "root", "break-glass", "break glass", "jit", "just-in-time", "standing", "elevat", "pam"]),
    ("Logs, audit and detection", ["log", "audit", "evidence", "alert", "detect", "tamper", "monitor", "trace"]),
    ("Personal and sensitive data", ["personal data", "pii", "mask", "salary", "pay", "leak", "sensitive", "redact", "health"]),
    ("Joiners, movers and leavers", ["joiner", "mover", "leaver", "hire", "rehire", "leaves", "offboard", "contractor", "hr "]),
]
GUESS = {"match": "As guessed", "wrong": "Guess was wrong", "notrun": "Not run here", "none": "No guess recorded"}


def topics_for(text):
    t = " " + text.lower() + " "
    out = [name for name, words in TOPICS if any(re.search(r"(?<![a-z])" + re.escape(w), t) for w in words)]
    return out or ["Other"]


def node_json(js):
    return json.loads(subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, check=True).stdout)


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


rows = []

# Conditional access, MFA and SSO lab
ca = node_json('global.window={};eval(require("fs").readFileSync("ca-mfa-lab/data/cases.js","utf8"));'
               'process.stdout.write(JSON.stringify(window.CA_CASES))')
for c in ca:
    g = "match" if c.get("match") is True else "wrong" if c.get("match") is False else "notrun"
    result = c["status"]
    cols, res = c.get("cols") or [], c.get("res") or []
    on = next((i for i, h in enumerate(cols) if h.lower() in ("all on", "control on", "controls on")), None)
    if on is not None and on < len(res) and res[on] in ("in", "out"):
        result = "With the controls on, the failure " + ("is stopped" if res[on] == "out" else "still happens")
        if c.get("note"):
            result += ". " + c["note"][0].upper() + c["note"][1:]
    elif c.get("note"):
        result = c["note"][0].upper() + c["note"][1:]
    rows.append({"lab": "ca", "id": c["id"], "title": c["use"], "group": c["group"],
                 "result": result, "guess": GUESS[g], "url": f"/ca-mfa-lab/register/#{c['id']}"})

# Machine identity lab
for r in json.loads((ROOT / "nhi-lab/audit/nhi-lab-audit.json").read_text(encoding="utf-8"))["rows"]:
    rows.append({"lab": "nhi", "id": r["id"], "title": r["title"], "group": r["group"],
                 "result": r["with_control"] or r["without_control"],
                 "guess": GUESS["match" if r["guess_matched"] == "yes" else "wrong"],
                 "url": f"/nhi-lab/#{r['id'].lower()}", "extra": r["what_goes_wrong"]})

# AI governance lab, rounds 1 to 13
files = ["assets/agl-data.js"] + [f"assets/agl-r{n}.js" for n in range(5, 14)]
agl = node_json('global.window={};const fs=require("fs");' + "".join(f'eval(fs.readFileSync("{f}","utf8"));' for f in files) +
                'const out=[];for(const [r,l] of Object.entries(window.AGL.cases)) l.forEach(c=>out.push([+r,c]));'
                'for(let n=5;n<=13;n++){const R=window["AGL_R"+n]; if(R) R.cases.forEach(c=>out.push([n,c]));}'
                'process.stdout.write(JSON.stringify(out))')
seen = {}  # some cases were run again in later rounds: one row each, with every round listed
for rnd, c in agl:
    v = (c.get("verdict") or "").lower()
    g = "match" if v == "as expected" else "wrong" if v else "none"
    actual = str(c.get("actual") or "").replace("_", " ")
    if c["id"] in seen:
        r = seen[c["id"]]
        r["rounds"].append(rnd)
        r["result"] = actual  # the latest run
        if g == "wrong":
            r["guess"] = GUESS["wrong"]
        continue
    r = {"lab": "agl", "id": c["id"], "title": c["title"], "group": "", "rounds": [rnd],
         "result": actual, "guess": GUESS[g], "url": f"/ai-governance-lab/cases/#{c['id']}"}
    seen[c["id"]] = r
    rows.append(r)
for r in seen.values():
    rs = r.pop("rounds")
    r["group"] = f"Round {rs[0]}" + (f", run again in round{'s' if len(rs) > 2 else ''} " + " and ".join(map(str, rs[1:])) if len(rs) > 1 else "")

# HumanGate MCP lab: the use cases page
mcp = (ROOT / "mcp-lab/use-cases/index.html").read_text(encoding="utf-8")
section = "Use cases"
for m in re.finditer(r'<h2[^>]*>(.*?)</h2>|<article class="uc" id="([^"]+)"><h3><code>[^<]*</code>\s*(.*?)</h3>(.*?)</article>', mcp, re.S):
    if m.group(1):
        section = clean(m.group(1)); continue
    dl = dict(zip([clean(x) for x in re.findall(r"<dt>(.*?)</dt>", m.group(4), re.S)],
                  [clean(x) for x in re.findall(r"<dd>(.*?)</dd>", m.group(4), re.S)]))
    rows.append({"lab": "mcp", "id": m.group(2), "title": clean(m.group(3)), "group": section,
                 "result": dl.get("What happened", ""), "guess": GUESS["none"], "url": f"/mcp-lab/use-cases/#{m.group(2)}"})

for r in rows:
    r["topics"] = topics_for(" ".join([r["title"], r["group"], r.get("extra", "")]))
    r.pop("extra", None)

out = {"about": "Every case in the four labs. Generated by scripts/build-catalogue.py from each lab's own data. "
                "Topics are matched from the case's words, as a finding aid.",
       "labs": {k: {"name": v[0], "url": v[1]} for k, v in LABS.items()},
       "topics": [t for t, _ in TOPICS] + ["Other"], "cases": rows}
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data/catalogue.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
counts = {k: sum(1 for r in rows if r["lab"] == k) for k in LABS}
print("catalogue:", len(rows), counts)
set_stat("cases", len(rows))

# The page: every row is in the HTML, so it works and is searchable without JavaScript.
esc = html.escape
opt = lambda v, t: f'<option value="{esc(v)}">{esc(t)}</option>'
trs = "".join(
    f'<tr data-lab="{r["lab"]}" data-topics="{esc("|".join(r["topics"]))}" data-guess="{esc(r["guess"])}">'
    f'<th scope="row"><a href="{r["url"]}">{esc(r["id"])}</a></th><td>{esc(r["title"])}<small>{esc(r["group"])}</small></td>'
    f'<td data-label="Lab">{esc(LABS[r["lab"]][0])}</td><td data-label="Result">{esc(r["result"])}</td><td data-label="My guess">{esc(r["guess"])}</td><td data-label="Topics">{esc(", ".join(r["topics"]))}</td></tr>'
    for r in rows)
labs_sum = " · ".join(f'<a href="{v[1]}">{esc(v[0])}</a>: {counts[k]}' for k, v in LABS.items())
body = f'''      <section class="sec cat" aria-labelledby="cat-h">
        <div class="wrap">
          <p class="ey">All labs</p>
          <h1 id="cat-h">Every case, in one list</h1>
          <p class="lede">{len(rows)} cases from the four labs, side by side. Filter by lab, topic or how my guess did, or type a word such as recovery, help desk or token. Each ID opens the case in its own lab.</p>
          <p class="cat-sum">{labs_sum}. <a href="/data/catalogue.json">Download the list (JSON)</a></p>
          <form class="cat-f" role="search" aria-label="Filter the cases" onsubmit="return false">
            <label>Words<input type="search" id="cat-q" autocomplete="off" placeholder="recovery, token, approver"></label>
            <label>Lab<select id="cat-lab"><option value="">All four labs</option>{"".join(opt(k, v[0]) for k, v in LABS.items())}</select></label>
            <label>Topic<select id="cat-topic"><option value="">All topics</option>{"".join(opt(t, t) for t in out["topics"])}</select></label>
            <label>My guess<select id="cat-guess"><option value="">Any</option>{"".join(opt(g, g) for g in GUESS.values())}</select></label>
          </form>
          <p class="cat-n" id="cat-n" role="status" aria-live="polite">Showing all {len(rows)} cases.</p>
          <div class="cat-wrap"><table class="cat-t">
            <caption class="sr-only">All lab cases</caption>
            <thead><tr><th scope="col">ID</th><th scope="col">Case</th><th scope="col">Lab</th><th scope="col">Result</th><th scope="col">My guess</th><th scope="col">Topics</th></tr></thead>
            <tbody>{trs}</tbody>
          </table></div>
          <p class="cat-note">Topics come from the words in each case, matched against a short keyword list in <a href="https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/blob/main/scripts/build-catalogue.py">the build script</a>, so a case can sit under more than one topic and a few will sit in the wrong one. A case run again in a later round shows its latest result, and counts as a wrong guess if any run missed. For the MCP lab the list holds the use cases written up on <a href="/mcp-lab/use-cases/">its use-cases page</a>; every scripted check is in <a href="/mcp-lab/portal/">the portal</a>. That lab did not lock guesses case by case, so its rows say "No guess recorded". All data in the labs is made up.</p>
        </div>
      </section>'''
page = shell("/labs/cases/", "Every lab case in one list",
             f"All {len(rows)} cases from the four identity security labs, filterable by lab, topic and whether my locked guess was right.",
             body, [("Home", "/"), ("Labs and projects", "/labs/"), ("Every case", "/labs/cases/")], nav_current="/labs/",
             head_extra='    <link rel="stylesheet" href="/assets/catalogue.css?v=20261115a">\n    <script defer src="/assets/catalogue.js?v=20261115a"></script>')
write("/labs/cases/", page)
