#!/usr/bin/env python3
"""Build the three knowledge pages: /topics/, /glossary/ and /start/.
They reuse the shell of /now/ (head, navigation, footer) so they look like the rest of the site.
Edit the lists below, then run from the repo root:  python3 scripts/build-hub.py
Every link is to a page that already exists. scripts/check-links.py will fail if one does not."""
import re, html, pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent
SHELL = (ROOT / "now" / "index.html").read_text(encoding="utf-8")
REVIEWED = "14 November 2026"

CS = "/case-studies/"
# (topic id, name, one line, [(url, label, kind)])   kind: Lab, Case study, Article, Book, Tool, Paper
TOPICS = [
 ("pam", "Privileged access (PAM)", "Who can use powerful accounts, how they get them, and what is recorded.", [
    (CS + "privileged-access-program/", "Running a privileged access program", "Case study"),
    (CS + "pam-modernization/", "PAM modernization and zero standing privilege", "Case study"),
    (CS + "credential-platform/", "Credential management platform strategy", "Case study"),
    (CS + "credential-tiering-model/", "The credential tiering model", "Case study"),
    (CS + "vendor-privileged-access/", "Vendor privileged access", "Case study"),
    (CS + "migration-planning/", "Privileged access migration planning", "Case study"),
    (CS + "platform-evaluation/", "PAM, NHI and cloud platform evaluation", "Case study"),
    ("/writing/pam-framework-and-design/", "PAM series 1: framework and design", "Article"),
    ("/writing/pam-project-plan-by-organization-tier/", "PAM series 2: project plan by tier", "Article"),
    ("/writing/pam-as-an-identity/", "PAM series 3: PAM as an identity", "Article"),
    ("/tools/tier-check/", "Credential tier self-check", "Tool")]),
 ("jit", "Just-in-time access, PIM and break-glass", "Access that is granted for a task and removed on its own, and the emergency path when that fails.", [
    (CS + "jit-jea-elevation/", "Just-in-time and just-enough elevation", "Case study"),
    (CS + "break-glass-access/", "Break-glass access", "Case study"),
    ("/writing/pam-modernization-and-zero-standing-privilege/", "PAM modernization and zero standing privilege", "Article")]),
 ("nhi", "Non-human identity (NHI) and secrets", "Service accounts, API keys, tokens and workloads: who owns them, what they reach and when they end.", [
    ("/nhi-lab/", "Non-human identity lab: 67 cases", "Lab"),
    ("/nhi-lab/framework/", "The seven-step framework", "Lab"),
    ("/nhi-lab/market/", "The market in 2026", "Lab"),
    ("/nhi-lab/nhi-lab-book.pdf", "Machine identities, tested in public (83 pages)", "Book"),
    (CS + "non-human-identity-at-scale/", "Non-human identity at scale", "Case study"),
    (CS + "secrets-consolidation/", "Secrets sprawl and consolidation", "Case study"),
    ("/writing/i-tested-67-machine-identity-cases/", "I tested 67 machine identity cases", "Article")]),
 ("signin", "MFA, SSO and conditional access", "How people prove who they are, who vouches for them, and what the rules decide at sign-in.", [
    ("/ca-mfa-lab/", "Conditional access, MFA and AI agent lab: 130 cases", "Lab"),
    ("/ca-mfa-lab/framework/", "The access chain: seven links, 15 animated patterns", "Lab"),
    ("/ca-mfa-lab/virtual-lab/run/", "Run the lab in your browser", "Lab"),
    ("/ca-mfa-lab/ca-mfa-lab-book.pdf", "Who signs in? (72 pages)", "Book"),
    (CS + "conditional-access-mfa-sso/", "Conditional access, MFA and SSO", "Case study"),
    (CS + "passwordless-authentication/", "Passwordless authentication rollout", "Case study"),
    ("/writing/130-conditional-access-mfa-and-ai-agent-cases/", "130 cases and six wrong guesses", "Article")]),
 ("agents", "AI agents and MCP", "An agent is an identity that acts. Who approved the action, with what credential, and what was recorded?", [
    ("/mcp-lab/", "HumanGate MCP lab: a person in the loop", "Lab"),
    ("/mcp-lab/portal/", "MCP lab portal: 161 case cards", "Lab"),
    ("/assets/who-approved-that-book.pdf", "Who Approved That? (138 pages)", "Book"),
    (CS + "agentic-ai-identity-governance/", "Agentic AI identity governance", "Case study"),
    (CS + "ai-agent-credential-sharing/", "One key, every agent", "Case study"),
    (CS + "shadow-ai-discovery-gap/", "The shadow AI discovery gap", "Case study"),
    ("/writing/can-a-person-stay-in-control-of-an-ai-agent/", "Can a person stay in control of an AI agent?", "Article"),
    ("/writing/openai-huggingface-breach-cybersecurity-analysis/", "The Hugging Face intrusion, as an identity incident", "Article")]),
 ("aigov", "AI governance", "Whether the controls written for AI hold when someone tests them.", [
    ("/ai-governance-lab/", "AI governance lab: 13 rounds, 164 cases", "Lab"),
    ("/ai-governance-lab/what-i-got-wrong/", "What I got wrong", "Lab"),
    ("/assets/ai-governance-lab-book.pdf", "Does AI Governance Hold? (69 pages)", "Book"),
    (CS + "ai-coworker/", "AI as a security product co-worker", "Case study"),
    (CS + "ai-processing-tax/", "The AI processing tax", "Case study"),
    ("/writing/do-ai-governance-controls-hold/", "Do AI governance controls hold?", "Article"),
    ("/ai/", "How I use AI", "Article")]),
 ("iga", "Access reviews and governance (IGA)", "Who has what, who agreed to it, and how that is checked again.", [
    (CS + "access-recertification/", "Access recertification and IGA automation", "Case study"),
    (CS + "audit-mapping/", "IAM audit and control mapping", "Case study")]),
 ("cloud", "Cloud entitlements (CIEM)", "What identities can do in a cloud account, as opposed to what they were meant to do.", [
    (CS + "ciem-at-scale/", "Cloud entitlement management at scale", "Case study")]),
 ("zt", "Zero trust in practice", "Decide each request on identity, device and context. Applied here to one hard problem.", [
    ("/secure-india-exams/", "Securing India's national exams: a zero trust architecture", "Paper")]),
]
NOT_YET = ["Customer identity (CIAM)", "Certificates and PKI", "Identity threat detection and response", "Directories: Active Directory and Entra ID in depth",
           "Federation protocols in depth: SAML, OpenID Connect, OAuth", "Joiner, mover and leaver automation"]

# (term, plain definition, optional link)
GLOSSARY = [
 ("Access chain", "My name for the seven steps every sign-in passes through: enroll and recover, prove, trust, decide, issue, act, watch and end. A weak step lets an attacker in even when the others are strong.", "/ca-mfa-lab/framework/"),
 ("Access review (recertification)", "A regular check where an owner confirms that each person or account still needs the access it has. Access nobody confirms is removed.", CS + "access-recertification/"),
 ("AI agent", "Software that takes actions for a person or a team using a model, tools and credentials. For access purposes it is an identity: it needs an owner, a scope and an end date.", CS + "agentic-ai-identity-governance/"),
 ("API key", "A long secret string that lets a program call a service. It usually has no expiry and no second factor, so who holds it and what it can reach matter a great deal.", "/nhi-lab/"),
 ("Authentication", "Proving who you are. Passwords, passkeys and one-time codes are ways to authenticate.", None),
 ("Authorization", "Deciding what an authenticated identity is allowed to do.", None),
 ("Blast radius", "How much damage one stolen credential could do. It is the main input when ranking which credentials to fix first.", CS + "credential-tiering-model/"),
 ("Break-glass account", "An emergency account used when normal access has failed. It should be separate, watched, tested, and rotated after every use.", CS + "break-glass-access/"),
 ("CIEM", "Cloud infrastructure entitlement management. Tools and practice for finding and reducing what identities can do in cloud accounts.", CS + "ciem-at-scale/"),
 ("Conditional access", "Rules that decide at sign-in whether to allow, block or ask for more proof, based on the user, device, location, app and risk.", "/ca-mfa-lab/"),
 ("Continuous access evaluation", "Checking a session again while it is running, so that a change such as a disabled account or a new network takes effect in minutes instead of when the token expires.", "/ca-mfa-lab/framework/"),
 ("Credential", "Anything that proves an identity: a password, key, token, certificate or passkey.", None),
 ("Credential tiering", "Sorting credentials into levels by what they can reach, so the most powerful ones get the strictest handling.", "/tools/tier-check/"),
 ("Default deny", "A rule set where a request that matches no rule is refused. Without it, the gaps between rules are open.", "/ca-mfa-lab/framework/"),
 ("Federation", "One system trusting another to say who a user is. Single sign-on is built on it.", None),
 ("Human in the loop", "A design where a person must approve a step before it runs. It only helps if the person sees exactly what will happen.", "/mcp-lab/"),
 ("IAM", "Identity and access management. The whole field: who people and machines are, and what they may do.", None),
 ("Identity provider (IdP)", "The system that signs users in and tells other apps who they are.", None),
 ("IGA", "Identity governance and administration. Requests, approvals, reviews and the records that show access was granted for a reason.", CS + "access-recertification/"),
 ("Just-enough access (JEA)", "Granting only the specific rights a task needs, not a broad role.", CS + "jit-jea-elevation/"),
 ("Just-in-time access (JIT)", "Granting access when it is needed and removing it automatically afterwards, so nothing powerful sits idle.", CS + "jit-jea-elevation/"),
 ("Least privilege", "Give each identity the smallest set of rights that lets it do its job.", None),
 ("MCP", "Model Context Protocol. A standard way for an AI application to call tools and reach data. Each tool call is an action someone should be able to approve and trace.", "/mcp-lab/"),
 ("MFA", "Multi-factor authentication. Signing in with two or more different kinds of proof. Not all methods are equal: codes and push prompts can be relayed by a phishing page.", "/ca-mfa-lab/"),
 ("Non-human identity (NHI)", "Any identity that is not a person: service accounts, API keys, workloads, bots and agents.", "/nhi-lab/"),
 ("OAuth and OpenID Connect", "OAuth lets an app act with limited rights without seeing the password. OpenID Connect adds sign-in on top of it.", None),
 ("PAM", "Privileged access management. Controlling, recording and limiting the use of powerful accounts.", CS + "privileged-access-program/"),
 ("Passkey", "A sign-in credential tied to the real site and held on a device or security key. A fake site cannot reuse it, which is what phishing-resistant means.", CS + "passwordless-authentication/"),
 ("Phishing-resistant MFA", "Methods such as passkeys and FIDO2 security keys, where the proof only works on the genuine site.", "/ca-mfa-lab/framework/"),
 ("PIM", "Privileged identity management. Used mainly for time-limited activation of admin roles in a directory or cloud.", CS + "jit-jea-elevation/"),
 ("Refresh token", "A long-lived token used to get new short-lived access tokens without signing in again. If it survives a password reset, so does the attacker.", "/ca-mfa-lab/framework/"),
 ("Rotation", "Replacing a secret with a new one. It limits how long a stolen secret works. It does not remove access from something that should not have it.", "/nhi-lab/"),
 ("SAML", "An older, widely used standard for single sign-on between an identity provider and an app.", None),
 ("Secret", "A credential used by software: a password, key or token stored in a vault, a pipeline or, too often, in code.", CS + "secrets-consolidation/"),
 ("Service account", "An account used by software, not a person. It often has broad rights, no MFA and no clear owner.", "/nhi-lab/"),
 ("SSO", "Single sign-on. Sign in once at the identity provider and reach many apps.", CS + "conditional-access-mfa-sso/"),
 ("Standing privilege", "Powerful access that is always on, whether or not it is being used.", "/writing/pam-modernization-and-zero-standing-privilege/"),
 ("Step-up authentication", "Asking for stronger or fresh proof at the moment of a sensitive action. It only works if the server checks for it.", "/ca-mfa-lab/framework/"),
 ("Token binding", "Tying a token to the device or client that received it, so a copy used elsewhere is refused.", "/ca-mfa-lab/framework/"),
 ("Vault", "A system that stores secrets, controls who can read them, and records each use.", CS + "secrets-consolidation/"),
 ("Zero standing privilege", "A target state where no one holds powerful access by default. It is granted for a task and expires.", CS + "pam-modernization/"),
 ("Zero trust", "Do not trust a request because of where it comes from. Decide each one on identity, device and context.", "/secure-india-exams/"),
]

# (reader, one line, [(url, label, why)])
PATHS = [
 ("If you lead a security or identity team", "Fifteen minutes. The findings, and what they change.", [
    ("/ca-mfa-lab/", "Do sign-in controls hold up?", "130 cases. Most weak points sat after the MFA prompt."),
    ("/nhi-lab/", "Machine identities, tested", "67 cases. Ten of my own guesses were wrong, and which ones."),
    ("/mcp-lab/", "A person in the loop for AI agents", "What an approval step stops, and what it does not."),
    (CS + "privileged-access-program/", "Running a privileged access program", "How I structure the work and the evidence."),
    ("/resume/", "R&eacute;sum&eacute;", "Roles, dates and certifications.")]),
 ("If you design identity systems", "The models and the reasoning behind them.", [
    ("/ca-mfa-lab/framework/", "The access chain", "Seven links, with 15 attack patterns you can play."),
    ("/nhi-lab/framework/", "A seven-step framework for machine identity", "From inventory to retirement."),
    (CS + "credential-tiering-model/", "The credential tiering model", "Rank credentials by what they can reach."),
    ("/writing/pam-framework-and-design/", "PAM framework and design", "Part one of a three-part series."),
    (CS + "agentic-ai-identity-governance/", "Agentic AI identity governance", "A target state for agents that change shape at run time.")]),
 ("If you build and run it", "Things you can run, change and break.", [
    ("/ca-mfa-lab/virtual-lab/run/", "Run the conditional access, MFA and AI agent lab in your browser", "Nothing to install. Change an assumption and rerun."),
    ("/ai-governance-lab/try/", "Try the AI governance lab", "The same cases, in your own hands."),
    ("/mcp-lab/portal/", "MCP lab portal", "161 case cards with the request, the decision and the receipt."),
    ("/nhi-lab/audit/", "Audit data as CSV and JSON", "Every case, machine readable."),
    ("/tools/tier-check/", "Credential tier self-check", "Three minutes, runs in your browser.")]),
 ("If you audit or assess controls", "Evidence first: what was claimed, what was tested, what failed.", [
    (CS + "audit-mapping/", "IAM audit and control mapping", "From control intent to evidence and owner."),
    ("/ca-mfa-lab/register/", "Conditional access, MFA and AI agent lab register", "All 130 cases with status and source."),
    ("/nhi-lab/register/", "Machine identity register", "Every catalogue row with its result."),
    ("/ai-governance-lab/", "AI governance lab", "Controls mapped to ISO 27001, NIST, PCI and HIPAA, then tested."),
    (CS + "access-recertification/", "Access recertification", "Reviews backed by usage, not habit.")]),
]

def page(path, title, desc, eyebrow, h1, dek, body, ld_type="CollectionPage"):
    s = SHELL
    url = "https://roshantrivedi.co.in" + path
    s = re.sub(r'<html lang="en"[^>]*>', '<html lang="en" data-bg="work" data-m="grid">', s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc, quote=True), s, count=1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title, quote=True), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc, quote=True), s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, s, count=1)
    s = s.replace("https://roshantrivedi.co.in/assets/og-post-page-now.png", "https://roshantrivedi.co.in/assets/og-roshan-trivedi-2026.png")
    s = re.sub(r"<title>.*?</title>", "<title>" + html.escape(title) + " &middot; Roshan Trivedi</title>", s, count=1, flags=re.S)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://roshantrivedi.co.in/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": url}]},
        {"@type": ld_type, "name": title, "description": desc, "url": url, "dateModified": "2026-11-14",
         "author": {"@type": "Person", "name": "Roshan Trivedi", "url": "https://roshantrivedi.co.in/"}}]}
    s = re.sub(r'<script type="application/ld\+json" id="ld-site">.*?</script>',
               lambda m: '<script type="application/ld+json" id="ld-site">' + json.dumps(ld) + "</script>", s, count=1, flags=re.S)
    s = s.replace('<link rel="stylesheet" href="/assets/site-2026.css', '<link rel="stylesheet" href="/assets/hub.css?v=20261115b">\n    <link rel="stylesheet" href="/assets/site-2026.css', 1)
    s = s.replace(' aria-current="page"', '')
    a = s.index('<header class="hero">'); b = s.index('<aside class="hg-next"')
    hub = ('<nav class="hub-nav" aria-label="Knowledge pages"><a href="/start/">Start here</a><a href="/topics/">Topics</a><a href="/glossary/">Glossary</a></nav>\n      ')
    head = (f'<header class="hero">\n        <p class="eyebrow">{eyebrow}</p>\n        <h1>{h1}</h1>\n        <p class="dek">{dek}</p>\n'
            f'        <p class="dek hub-rev">Last reviewed {REVIEWED}. Lab data is made up; nothing here describes an employer or a client.</p>\n      </header>\n      ')
    s = s[:a] + hub + head + body + "\n      " + s[b:]
    out = ROOT / path.strip("/") / "index.html"; out.parent.mkdir(exist_ok=True); out.write_text(s, encoding="utf-8")
    return out

# ---------- topics
jump = '<p class="hub-jump">' + "".join(f'<a href="#{i}">{html.escape(n)}</a>' for i, n, _, _ in TOPICS) + "</p>"
secs = []
for i, n, line, links in TOPICS:
    kinds = {}
    for u, l, k in links: kinds[k] = kinds.get(k, 0) + 1
    plural = {"Case study": "case studies"}
    count = ", ".join(f"{v} {(plural.get(k, k.lower() + 's') if v > 1 else k.lower())}" for k, v in kinds.items())
    items = "".join(f'<li><a href="{u}"><span class="hub-k hub-k-{k.split()[0].lower()}">{k}</span><b>{html.escape(l)}</b></a></li>' for u, l, k in links)
    secs.append(f'<section class="hub-topic" id="{i}" aria-labelledby="{i}-h"><h2 id="{i}-h">{html.escape(n)}</h2><p class="body-text">{html.escape(line)}</p><p class="hub-count">{count}</p><ul class="hub-list">{items}</ul></section>')
noty = ('<section class="hub-topic" id="not-yet" aria-labelledby="ny-h"><h2 id="ny-h">Not covered yet</h2><p class="body-text">I would sooner show a gap than fill it with something thin. '
        'These are on my list. Nothing on this site tests them yet.</p><ul class="hub-gaps">' + "".join(f"<li>{html.escape(x)}</li>" for x in NOT_YET) +
        '</ul><p class="body-text">Want one of them sooner? <a href="/talk/?why=feedback">Tell me which</a>.</p></section>')
n_links = sum(len(t[3]) for t in TOPICS)
page("/topics/", "Topics: everything here, by subject",
     "Every lab, case study, article and book on this site, sorted by subject: privileged access, non-human identity, MFA and SSO, AI agents, governance and more.",
     "Topics", "Everything here, by subject.",
     f"{len(TOPICS)} subjects and {n_links} links to labs, case studies, articles and books. Pick a subject, or see what is not covered yet.",
     jump + "\n      " + "\n      ".join(secs) + "\n      " + noty)

# ---------- glossary
letters = sorted({t[0][0].upper() for t in GLOSSARY})
jump = '<p class="hub-jump">' + "".join(f'<a href="#g-{c.lower()}">{c}</a>' for c in letters) + "</p>"
rows, last = [], ""
for term, d, link in sorted(GLOSSARY, key=lambda t: t[0].lower()):
    c = term[0].upper()
    if c != last:
        if last: rows.append("</dl></section>")
        rows.append(f'<section class="hub-gl" aria-labelledby="g-{c.lower()}"><h2 id="g-{c.lower()}">{c}</h2><dl>'); last = c
    more = f' <a href="{link}">See it used</a>' if link else ""
    rows.append(f'<div><dt id="{re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")}">{html.escape(term)}</dt><dd>{html.escape(d)}{more}</dd></div>')
rows.append("</dl></section>")
page("/glossary/", "Identity and access glossary in plain words",
     f"{len(GLOSSARY)} identity and access terms in plain words, from PAM and MFA to MCP and zero standing privilege, each linked to where this site uses it.",
     "Glossary", "Identity and access terms, in plain words.",
     f"{len(GLOSSARY)} terms. Each one says what the thing is, and where it matters links to a page that uses or tests it. These are my working definitions, written to be understood, not to replace a standard.",
     jump + "\n      " + "\n      ".join(rows), "DefinedTermSet")

# ---------- start here
secs = []
for k, (who, line, links) in enumerate(PATHS):
    items = "".join(f'<li><a href="{u}"><b>{l}</b><span>{html.escape(w)}</span></a></li>' for u, l, w in links)
    secs.append(f'<section class="hub-path" aria-labelledby="p{k}-h"><h2 id="p{k}-h">{html.escape(who)}</h2><p class="body-text">{html.escape(line)}</p><ol class="hub-steps">{items}</ol></section>')
how = ('<section class="hub-topic" aria-labelledby="how-h"><h2 id="how-h">How the labs work</h2><p class="body-text">Each lab asks a plain question about a control. '
       'I write down what I expect before I build anything, hash that file and commit it in public. Then I run the cases on made-up data and publish every result, '
       'including the guesses I got wrong. The models test my reasoning about a rule. They do not show how any vendor product behaves.</p>'
       '<p class="body-text">Looking for a subject? See <a href="/topics/">Topics</a>. Stuck on a term? See the <a href="/glossary/">Glossary</a>.</p></section>')
page("/start/", "Start here",
     "New to this site? Four short reading paths: for security leaders, identity architects, engineers and auditors. Five links each.",
     "Start here", "Pick the path that fits you.",
     "Four short paths through four labs, 22 case studies and four free books. Five links each.",
     "\n      ".join(secs) + "\n      " + how)
print("hub pages: topics", len(TOPICS), "subjects,", n_links, "links; glossary", len(GLOSSARY), "terms; start", len(PATHS), "paths")
