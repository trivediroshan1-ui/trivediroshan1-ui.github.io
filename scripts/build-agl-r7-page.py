#!/usr/bin/env python3
"""Puts the round-seven section (the HR side of identity onboarding, with the animated lifecycle) into ai-governance-lab/index.html
between markers, before the round-six block. Safe to re-run. Also copies the guesses file next to the site."""
import re, json, html, hashlib, shutil
LAB = "/home/claude/ai-governance-lab"
src = open("assets/agl-r7.js").read()
R7 = json.loads(src[src.index("{"):src.rindex("}") + 1])
shutil.copyfile(f"{LAB}/cases/round-7.json", "assets/ai-governance-lab-round-seven-guesses.json")
sha = hashlib.sha256(open("assets/ai-governance-lab-round-seven-guesses.json", "rb").read()).hexdigest()
assert sha == R7["cases_sha256"], (sha, R7["cases_sha256"])
e = html.escape
def words(s): return e(str(s).replace("_", " "))

LANES = [("hr", "HR: talent acquisition and operations"), ("bu", "BU HR"), ("iga", "Identity governance, gateway, executor"), ("ai", "AI agent"),
         ("dir", "Directory: Active Directory or Entra"), ("aud", "Auditor")]
STEPS = [
 ("hr", "Offer accepted", "Talent acquisition HR",
  "Creates the pre-hire record in the HR system. The HR system is the source of truth for who works here, not IT and not an AI.",
  ["Name", "Date of birth", "Address", "Contact", "Job code", "Manager", "Start date"],
  "None. It may check the form for gaps.", []),
 ("hr", "Checks and paperwork", "HR operations and a background-check vendor",
  "Verifies identity and history, collects payroll and tax details, and files the signed offer and policies. The firm's HR policy and privacy notice say what is collected and why. The employee is told; the legal basis for employment data is usually the job, not consent (ask your legal team).",
  ["PAN", "Aadhaar (limited)", "Bank details", "Education and employment checks"],
  "Flags gaps and duplicates, such as the same PAN on two records, and holds them for a person.", ["H3", "H12"]),
 ("bu", "Two HR approvals", "Talent acquisition HR and BU HR, two different people",
  "Both approve. Only then does a hire event exist. That event is the one trigger for an identity. Consent is not the trigger: the HR approval is the authorisation.",
  ["Approval 1", "Approval 2", "Hire event"],
  "Cannot approve, and cannot start the process without the event.", ["H4", "H2"]),
 ("iga", "Only the minimum goes to identity", "HR system to the identity governance tool",
  "The event carries only what identity needs. PAN, Aadhaar and bank details stay in HR.",
  ["Employee ID", "Name", "Email", "Team", "Job code", "Manager", "Start date"],
  "None.", ["H5"]),
 ("ai", "The agent prepares and proposes", "AI agent with its own identity and a named sponsor",
  "Checks the event, drafts the create request and the access package, and sends a fixed-shape request to the gateway. It holds no credential and cannot choose where the call goes.",
  ["Request", "Hire event number"],
  "Its whole role: prepare and propose, never decide.", ["T3", "T6", "H2"]),
 ("iga", "Gateway checks, executor acts", "Gateway and executor (ordinary code)",
  "The gateway refuses a request with no approved event, checks policy and rate, asks a person for risky actions and signs a decision. The executor takes a 5-minute credential from the vault and calls the SCIM or Graph API.",
  ["Signed decision", "5-minute lease"],
  "Never sees the credential.", ["T1", "T8", "T14"]),
 ("dir", "Account created, switched off", "Directory: Active Directory or Entra",
  "The account is created through the API and stays off until the start date. If the offer is withdrawn it never turns on.",
  ["Account", "Off until start date"],
  "None.", ["H1", "H7"]),
 ("dir", "Day one", "New hire and the identity provider",
  "On the start date the account turns on with only the access that goes with the job code. Identity proofing, MFA enrolment and the signed acceptable-use policy come before single sign-on into sensitive apps.",
  ["Birthright access", "MFA", "Signed policy", "SSO"],
  "None. This is activation, not provisioning.", ["H1", "H8"]),
 ("ai", "Extra access", "AI proposes, the manager decides",
  "The agent suggests what peers in the same job code hold. A suggestion grants nothing. The manager or data owner approves each item, and toxic combinations are refused.",
  ["Proposal", "Manager approval"],
  "Learns the pattern, but a peer pattern is not a permission.", ["H6"]),
 ("aud", "It keeps being checked", "Auditor and the identity governance tool",
  "A daily job compares HR with the directory and flags any account with no HR record. Vendor accounts switch off on their end date. Access reviews follow, and leavers go the same way in reverse.",
  ["Reconciliation", "End dates", "Access reviews"],
  "Reports. A person decides what to do.", ["H11", "H10"]),
]
legend = "".join(f'<li data-lane="{k}"><i></i>{e(n)}</li>' for k, n in LANES)
def step(s):
    lane, title, who, what, data, ai, cases = s
    links = "".join(f'<a href="/ai-governance-lab/cases/#{c}">{c}</a>' for c in cases)
    return (f'<li class="lc-step" data-lane="{lane}"><h4>{e(title)} <span class="lc-who">{e(who)}</span></h4><p>{e(what)}</p>'
            f'<ul class="lc-data" aria-label="Data">{"".join(f"<li>{e(d)}</li>" for d in data)}</ul>'
            f'<p class="lc-ai"><b>AI&rsquo;s part:</b> {e(ai)}</p>' + (f'<p class="lc-cases">Lab cases: {links}</p>' if links else "") + '</li>')
steps_html = "".join(step(s) for s in STEPS)
rows = "".join(
    f'<tr><td data-label="Case"><a href="/ai-governance-lab/cases/#{c["id"]}">{c["id"]}</a></td><td data-label="What I tested">{e(c["title"])}</td>'
    f'<td data-label="My guess">{words(c["expected"])}</td><td data-label="What came out">{words(c["actual"])}</td></tr>' for c in R7["cases"])
ctl_rows = "".join(
    f'<tr><td data-label="Control"><b>{c["id"]}</b> {e(c["control"])} <small>({", ".join(c["cases"])})</small></td><td data-label="ISO 27001:2022">{e(c["iso27001"])}</td>'
    f'<td data-label="NIST 800-53">{e(c["nist80053"])}</td><td data-label="PCI DSS 4.0">{e(c["pci"]) or "—"}</td><td data-label="HIPAA">{e(c["hipaa"])}</td></tr>' for c in R7["controls"])
m = R7["mutations"]

block = f'''<!-- r7:start -->
      <section id="hr-lifecycle">
        <h2>From HR to the directory: how an identity should start</h2>
        <p class="body-text">My first diagram of the agent pattern began in the middle: an agent sends a request. In a real firm the story starts earlier, in HR. This is the order I think an auditor, an IAM engineer, an API engineer and a BU HR lead would all accept. Tap a step, or let it play.</p>
        <div class="agl lc" aria-label="The identity lifecycle from offer to reconciliation">
          <ul class="lc-legend" aria-label="Who does each step">{legend}</ul>
          <ol class="lc-steps">{steps_html}</ol>
        </div>
        <p class="body-text">Three points. First, <b>HR approval is the trigger</b>. The agent can prepare the paperwork and propose the request, but the gateway refuses a create request that no approved HR event backs. Second, <b>consent and approval are different things</b>: the employee gets a notice and the processing rests on the job, while HR approval is the business authorisation. Third, <b>MFA and single sign-on belong to day one</b>, after the account turns on, not to the provisioning call.</p>
        <p class="body-text">I wrote the expected result for 12 new cases (H1 to H12) and saved them before writing any code, on 25 Oct 2026 at 00:43 IST. All 12 came out as I guessed. I then switched off {m["total"]} controls one at a time in a copy of the code. The first time, {m["first_run_noticed"]} of {m["first_run_total"]} were noticed: my MFA test could not tell a missing MFA step from a missing signed policy, because the policy check caught both. I rebuilt that test with two people, each missing one step, and now {m["noticed"]} of {m["total"]} are noticed. I kept both result files.</p>
        <p class="body-text">The SHA-256 of the guesses file is <code style="word-break:break-all">{sha}</code>. You can <a href="/assets/ai-governance-lab-round-seven-guesses.json">download the file</a> and check it.</p>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Case</th><th>What I tested</th><th>My guess</th><th>What came out</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <h3>What this does not show</h3>
        <ul class="approach-list">
          <li>HR, the identity governance tool and the directory are small models I wrote. They are not Workday, SailPoint, Entra or Active Directory, and real tools will differ.</li>
          <li>The &ldquo;learning from peers&rdquo; is a plain majority count, not a trained model. The AI model itself is not tested.</li>
          <li>I wrote the guesses and the code, so &ldquo;as expected&rdquo; shows the rules do what I intended, not that I thought of every case.</li>
          <li>Not tested in this round: background-check vendors, movers and leavers triggered from HR, and real approval screens used by real people. Rehires, name changes and agency contractors are in round ten.</li>
          <li>The mapping below, and the legal comments above, are my own reading and not legal advice.</li>
        </ul>
        <h3>Where the four new controls sit</h3>
        <div class="tbl-wrap">
          <table class="tbl wrap-first stack">
            <thead><tr><th>Control</th><th>ISO 27001:2022</th><th>NIST 800-53</th><th>PCI DSS 4.0</th><th>HIPAA</th></tr></thead>
            <tbody>{ctl_rows}</tbody>
          </table>
        </div>
        <p class="body-text">Every case has a step-by-step page in the <a href="/ai-governance-lab/cases/#H1">case explorer</a> (track H). This round is not in the book or the round-five addendum.</p>
      </section>
<!-- r7:end -->

      '''
h = open("ai-governance-lab/index.html").read()
h = re.sub(r"<!-- r7:start -->.*?<!-- r7:end -->\n\n      ", "", h, flags=re.S)
assert "<!-- r6:start -->" in h
h = h.replace("<!-- r6:start -->", block + "<!-- r6:start -->", 1)
h = h.replace("lists all 91 lab cases (59 from the first four rounds, 14 added in round five and 18 in round six)",
              "lists all 103 lab cases (59 from the first four rounds, 14 added in round five, 18 in round six and 12 in round seven)")
if "agl-lifecycle.css" not in h:
    h = h.replace('<link rel="stylesheet" href="/assets/agl.css?v=20261024f">', '<link rel="stylesheet" href="/assets/agl.css?v=20261024f">\n    <link rel="stylesheet" href="/assets/agl-lifecycle.css?v=20261025a">', 1)
if "agl-lifecycle.js" not in h:
    h = h.replace('<script defer src="/assets/chatbot-widget.js', '<script src="/assets/agl-lifecycle.js?v=20261025a" defer></script>\n  <script defer src="/assets/chatbot-widget.js', 1)
open("ai-governance-lab/index.html", "w").write(h)
print("ok", h.count("hr-lifecycle"), sha[:12])
