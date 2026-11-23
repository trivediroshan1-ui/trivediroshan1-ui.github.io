#!/usr/bin/env python3
"""Give each case study its own "at a glance" flow at the top and two "if you remember one thing"
callouts, about a third and two thirds of the way down. This replaced the shared three-icon header art, which looked the same on
every study.

Every flow step comes from that study's own short version and section headings. Every callout
is a sentence copied word for word from the body of the same page: the script stops if the sentence
is not found there, so a callout can never say something the study does not. It also stops if the
sentence is in the short version at the top, so a callout never just repeats the summary.

    python3 scripts/case-glance.py           # rewrite the case study pages
    python3 scripts/case-glance.py --check   # fail if a page is out of date (CI)
"""
import html, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

STUDIES = {
    "access-recertification": (
        ["Evidence on every line", "The reviewer decides", "The decision runs itself", "Check the access is gone"],
        ["No sign of whether the access was ever used, so “keep” is the safe guess.", "A campaign cannot be closed with open lines."]),
    "agentic-ai-identity-governance": (
        ["Own identity, named owner", "One credential per task", "Decide on every action", "Hard-to-undo actions wait for a person", "Record who it acted for"],
        ["This is the zero standing privilege starting point: the agent holds no access between tasks.", "The target still runs its own authorization, so a confused or manipulated agent meets a second check."]),
    "ai-agent-credential-sharing": (
        ["The agent has its own identity", "A broker issues a short-lived credential", "One task, one target", "Logs name the agent and the person"],
        ["If three agents share one key, even the agent’s own team cannot tell them apart.", "A key in the system prompt can be repeated back by the model."]),
    "ai-coworker": (
        ["A job and a named owner", "Its own identity, limited access", "A broker and policy on every tool", "A person checks writes and sends", "All of it logged"],
        ["If nobody will put their name on it, it does not start.", "It does not use the owner’s login."]),
    "ai-processing-tax": (
        ["The agent produces the work", "The decision-package gate", "Completeness checked, not correctness", "The person decides"],
        ["It does not judge whether the recommendation is good.", "The approval is time-boxed, so a stale request lapses instead of waiting to be approved by habit."]),
    "audit-mapping": (
        ["A plain objective", "One owner, one system setting", "Evidence collected on a schedule", "Stored where the audited cannot edit", "Gaps with an owner and end date"],
        ["If the owner cannot read the sentence and say whether it is true, rewrite it.", "A committee is not an owner, and neither is a team mailbox."]),
    "break-glass-access": (
        ["Normal access fails", "Sealed credential, no dependencies", "Alert and written justification", "Rotate the same day", "Drill on a calendar"],
        ["Nobody is handed break-glass access because they asked politely.", "A missing justification becomes an open finding that somebody chases."]),
    "ciem-at-scale": (
        ["Granted", "Effective", "Used", "Owner approves the cut, with a rollback", "Guardrails stop it growing back"],
        ["An identity with no owner is the first thing to review, because nobody else can speak for it.", "Add by hand any permission the logs cannot show."]),
    "conditional-access-mfa-sso": (
        ["Admins first", "Phishing-resistant methods", "Every rule report-only first", "Plan the recovery path"],
        ["SMS kept “just for recovery”, which becomes the way in.", "No exception without an owner and an end date."]),
    "credential-platform": (
        ["A short service catalog", "One owner per credential", "One lifecycle for all", "Short-lived identity before a vault"],
        ["A credential without an owner is not issued.", "Only what cannot avoid a secret goes into the vault."]),
    "credential-tiering-model": (
        ["Classify by blast radius", "Place in a tier", "Apply the tier's controls", "Review"],
        ["What it can change decides the class.", "Review on a rhythm, using usage evidence instead of memory."]),
    "jit-jea-elevation": (
        ["Request with a reason", "Approve scope and window", "Elevate", "The window closes on its own"],
        ["I apply the same rule to every platform: the requester is never the approver.", "The window carries its own end time from the first second."]),
    "migration-planning": (
        ["Analyze the current tool", "Discovery", "Plan signed off", "Waves by dependency and risk", "Cutover: rotate every secret"],
        ["Every difference is either fixed or logged.", "Hard-coded uses become tasks for their owners."]),
    "non-human-identity-at-scale": (
        ["One inventory", "An owner on every entry", "Score it into a queue", "Remove the secret where you can", "Rotate what is left"],
        ["Ownership has to be accepted, because being named by someone else does not make a person accountable.", "A half-filled record is still better than no record."]),
    "pam-modernization": (
        ["Vault the secret", "Rotate it", "Record the session", "Access only for the task"],
        ["The broker uses the credential on their behalf, so the person never sees or types the password.", "The vault is there, but the old door is still open."]),
    "passwordless-authentication": (
        ["Privileged users", "People on high-risk apps", "Everyone else", "Retire the fallback when stable"],
        ["Registration is a sign-in that matters, so it needs a strong prior sign-in.", "Recovery must end in a strong method again."]),
    "platform-evaluation": (
        ["Scenarios, weights, pass marks", "Same scripts for every candidate", "Score before anyone argues", "A decision record"],
        ["Every bit of vendor help is logged, because help during a trial may not exist in production.", "Where scores differ by two points or more, we go back to the evidence and not to opinion."]),
    "privileged-access-program": (
        ["Find the first pain", "Talk to people", "Requirements", "Proof of concept", "Write it all down"],
        ["Weak security and heavy friction both cost money, through incidents and through lost revenue.", "A backup that has never been restored is only a hope."]),
    "secrets-consolidation": (
        ["Scan", "Rotate first", "Clean the history", "Move to a governed store", "Block new secrets"],
        ["History matters because a secret deleted last year is still readable in an old commit.", "The secret is never copied back into code, config or a pipeline variable."]),
    "shadow-ai-discovery-gap": (
        ["Signals from many sources", "Classify by the data it touches", "Allow, control, replace or block", "Make the approved route quicker"],
        ["Each source misses something the others catch, so no single one counts as discovery.", "A record with no owner stays open until someone is named."]),
    "vendor-privileged-access": (
        ["Named account and sponsor", "MFA and an end date", "A broker records the session", "Expiry ends the access"],
        ["Nobody gets a shared login, including the team that “only ever needs one”.", "The vendor has no VPN account and no inbound route to the network."]),
}

ART = re.compile(r'\s*<div class="cs-art"[^>]*>.*?</svg></div>', re.S)
GLANCE = re.compile(r'\s*<!-- cs-glance:start -->.*?<!-- cs-glance:end -->', re.S)
REMEMBER = re.compile(r'\s*<!-- cs-remember:start -->.*?<!-- cs-remember:end -->', re.S)


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def build(slug, h):
    steps, quotes = STUDIES[slug]
    h = REMEMBER.sub("", GLANCE.sub("", ART.sub("", h)))
    body = re.search(r"<main.*?</main>", h, re.S).group(0)
    tldr = re.search(r'<div class="tldr">(.*?)</div>', body, re.S)
    for q in quotes:
        if q not in text(body):
            sys.exit(f"{slug}: the callout sentence is not on the page word for word: {q}")
        if tldr and q in text(tldr.group(1)):
            sys.exit(f"{slug}: the callout only repeats the short version: {q}")
    esc = lambda s: html.escape(s, quote=False).replace("'", "&rsquo;")
    glance = ('\n        <!-- cs-glance:start --><figure class="cs-glance"><figcaption>At a glance</figcaption><ol>'
              + "".join(f"<li><span>{esc(s)}</span></li>" for s in steps)
              + "</ol></figure><!-- cs-glance:end -->")
    h, k = re.subn(r"(<header class=\"hero[^\"]*\">.*?)(\n\s*</header>)", lambda m: m.group(1) + glance + m.group(2), h, count=1, flags=re.S)
    if not k:
        sys.exit(f"{slug}: no hero header")
    # Each callout goes before the section that starts nearest a third, and two thirds, of the way down.
    main_s, main_e = h.index("<main"), h.index("</main>")
    sections = [m.start() for m in re.finditer(r"\n\s*<section\b", h) if main_s < m.start() < main_e]
    words_before = lambda pos: len(text(h[main_s:pos]).split())
    total = words_before(main_e)
    candidates = sections[2:-1] or sections
    spots = []
    for frac in (1 / 3, 2 / 3):
        left = [s for s in candidates if s not in spots]
        spots.append(min(left, key=lambda s: abs(words_before(s) - total * frac)))
    for at, q in sorted(zip(spots, quotes), reverse=True):
        callout = ('\n      <!-- cs-remember:start --><aside class="cs-remember" aria-label="If you remember one thing">'
                   f'<p class="k">If you remember one thing</p><p>{esc(q)}</p></aside><!-- cs-remember:end -->')
        h = h[:at] + callout + h[at:]
    return h


check, stale = "--check" in sys.argv, []
for slug in STUDIES:
    p = ROOT / "case-studies" / slug / "index.html"
    h = p.read_text(encoding="utf-8")
    new = build(slug, h)
    if new != h:
        stale.append(slug)
        if not check:
            p.write_text(new, encoding="utf-8")
missing = sorted(d.name for d in (ROOT / "case-studies").iterdir() if (d / "index.html").exists() and d.name not in STUDIES)
if missing:
    sys.exit("case studies with no glance entry: " + ", ".join(missing))
if check and stale:
    sys.exit("case study glance or callout out of date, run python3 scripts/case-glance.py: " + ", ".join(stale))
print("case study glance up to date" if check else f"case study glance written on {len(stale)} pages")
