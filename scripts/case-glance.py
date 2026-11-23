#!/usr/bin/env python3
"""Give each case study its own "at a glance" flow at the top and one "if you remember one thing"
callout halfway down. This replaced the shared three-icon header art, which looked the same on
every study.

Every flow step comes from that study's own short version and section headings. Every callout
is a sentence copied word for word from the same page: the script stops if the sentence is not
found there, so the callout can never say something the study does not.

    python3 scripts/case-glance.py           # rewrite the case study pages
    python3 scripts/case-glance.py --check   # fail if a page is out of date (CI)
"""
import html, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

STUDIES = {
    "access-recertification": (
        ["Evidence on every line", "The reviewer decides", "The decision runs itself", "Check the access is gone"],
        "A certification is only finished when the access is gone and you can show it."),
    "agentic-ai-identity-governance": (
        ["Own identity, named owner", "One credential per task", "Decide on every action", "Costly actions wait for a person", "Record who it acted for"],
        "Record who the agent acted for, not only that it acted."),
    "ai-agent-credential-sharing": (
        ["The agent has its own identity", "A broker issues a short-lived credential", "One task, one target", "Logs name the agent and the person"],
        "Every record then shows two names: the agent that acted and the person it acted for."),
    "ai-coworker": (
        ["A job and a named owner", "Its own identity, limited access", "A broker and policy on every tool", "A person checks writes and sends", "All of it logged"],
        "Every connection to a company tool is an access decision."),
    "ai-processing-tax": (
        ["The agent produces the work", "The decision-package gate", "Completeness checked, not correctness", "The person decides"],
        "It checks completeness, never correctness, so the human keeps the judgment."),
    "audit-mapping": (
        ["A plain objective", "One owner, one system setting", "Evidence collected on a schedule", "Stored where the audited cannot edit", "Gaps with an owner and end date"],
        "Audit wording and platform settings describe the same risk in different languages."),
    "break-glass-access": (
        ["Normal access fails", "Sealed credential, no dependencies", "Alert and written justification", "Rotate the same day", "Drill on a calendar"],
        "An emergency account nobody has tried since it was set up is a guess, and a guess is a poor control."),
    "ciem-at-scale": (
        ["Granted", "Effective", "Used", "Owner-approved cut with rollback", "Guardrails stop it growing back"],
        "Cloud identities hold far more access than they use."),
    "conditional-access-mfa-sso": (
        ["Admins first", "Phishing-resistant methods", "Every rule report-only first", "Plan the recovery path"],
        "The rollout fails at recovery, not at sign-in."),
    "credential-platform": (
        ["A short service catalog", "One owner per credential", "One lifecycle for all", "Short-lived identity before a vault"],
        "The best credential is one that does not exist."),
    "credential-tiering-model": (
        ["Classify by blast radius", "Place in a tier", "Apply the tier's controls", "Review"],
        "A tier describes blast radius."),
    "jit-jea-elevation": (
        ["Request with a reason", "Approve scope and window", "Elevate", "The window closes on its own"],
        "Each request opens a window, and the window closes on its own."),
    "migration-planning": (
        ["Analyse the current tool", "Discovery", "Plan signed off", "Waves by dependency and risk", "Cutover: rotate every secret"],
        "A migration moves more than accounts."),
    "non-human-identity-at-scale": (
        ["One inventory", "An owner on every entry", "Score it into a queue", "Remove the secret where you can", "Rotate what is left"],
        "The best fix removes the secret."),
    "pam-modernization": (
        ["Vault the secret", "Rotate it", "Record the session", "Access only for the task"],
        "The risk that is left is access that never expires."),
    "passwordless-authentication": (
        ["Privileged users", "People on high-risk apps", "Everyone else", "Retire the fallback when stable"],
        "Recovery decides whether the program works."),
    "platform-evaluation": (
        ["Scenarios, weights, pass marks", "Same scripts for every candidate", "Score before the argument", "A decision record"],
        "Feature lists do not settle a platform decision."),
    "privileged-access-program": (
        ["Find the first pain", "Talk to people", "Requirements", "Proof of concept", "Write it all down"],
        "That starts with talking to people, not with a product demo."),
    "secrets-consolidation": (
        ["Scan", "Rotate first", "Clean the history", "Move to a governed store", "Block new secrets"],
        "Anything a scan finds is treated as compromised."),
    "shadow-ai-discovery-gap": (
        ["Signals from many sources", "Classify by the data it touches", "Allow, control, replace or block", "Make the approved route quicker"],
        "A block on its own moves the use somewhere you cannot see."),
    "vendor-privileged-access": (
        ["Named account and sponsor", "MFA and an end date", "A broker records the session", "Expiry ends the access"],
        "Expiry does the offboarding."),
}

ART = re.compile(r'\s*<div class="cs-art"[^>]*>.*?</svg></div>', re.S)
GLANCE = re.compile(r'\s*<!-- cs-glance:start -->.*?<!-- cs-glance:end -->', re.S)
REMEMBER = re.compile(r'\s*<!-- cs-remember:start -->.*?<!-- cs-remember:end -->', re.S)


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def build(slug, h):
    steps, quote = STUDIES[slug]
    h = REMEMBER.sub("", GLANCE.sub("", ART.sub("", h)))
    body = re.search(r"<main.*?</main>", h, re.S).group(0)
    if quote not in text(body):
        sys.exit(f"{slug}: the callout sentence is not on the page word for word: {quote}")
    esc = lambda s: html.escape(s, quote=False).replace("'", "&rsquo;")
    glance = ('\n        <!-- cs-glance:start --><figure class="cs-glance"><figcaption>At a glance</figcaption><ol>'
              + "".join(f"<li><span>{esc(s)}</span></li>" for s in steps)
              + "</ol></figure><!-- cs-glance:end -->")
    h, k = re.subn(r"(<header class=\"hero[^\"]*\">.*?)(\n\s*</header>)", lambda m: m.group(1) + glance + m.group(2), h, count=1, flags=re.S)
    if not k:
        sys.exit(f"{slug}: no hero header")
    # The callout goes before the section that starts nearest the middle of the article.
    sections = [m.start() for m in re.finditer(r"\n\s*<section\b", h)]
    main_s, main_e = h.index("<main"), h.index("</main>")
    sections = [s for s in sections if main_s < s < main_e]
    words_before = lambda pos: len(text(h[main_s:pos]).split())
    total = words_before(main_e)
    candidates = sections[2:-1] or sections
    at = min(candidates, key=lambda s: abs(words_before(s) - total / 2))
    callout = ('\n      <!-- cs-remember:start --><aside class="cs-remember" aria-label="If you remember one thing">'
               f'<p class="k">If you remember one thing</p><p>{esc(quote)}</p></aside><!-- cs-remember:end -->')
    return h[:at] + callout + h[at:]


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
