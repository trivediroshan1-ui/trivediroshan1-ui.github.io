#!/usr/bin/env python3
"""Build the four 10-minute guided routes (LAB-01): /nhi-lab/guided/, /ca-mfa-lab/guided/,
/ai-governance-lab/guided/ and /mcp-lab/guided/.

Each route is three real cases from the lab. For each: what happened, what to look at,
one question, and the answer behind a <details> toggle, so it works with no JavaScript.
Every number below is copied from the lab's own pages; the link next to it is the source.

Run from the repository root, then run add-lab-nav.py and add-lab-foot.py:
    python3 scripts/build-guided.py
"""
import html, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lab_nav

TEMPLATE = ROOT / "nhi-lab/method/index.html"
REVIEWED = "15 November 2026"

GUIDES = {
  "nhi": dict(
    path="/nhi-lab/guided/", colour="#7df2d0", og="/assets/share/og-nhi-lab.png",
    lab="Non-human identity lab", short="NHI lab",
    title="The non-human identity lab in 10 minutes",
    dek="Three cases about the accounts, keys and agents that are not people. For each one: what happened, a question, then the answer.",
    cases=[
      dict(id="N-R14-01", href="/nhi-lab/#n-r14-01", title="Where do service accounts hide?",
           setup="In the lab's made-up company, service accounts are spread across three sources. A quick inventory often looks in only one: the directory.",
           look="The case card shows the count without the control (directory only) and with it (all three sources merged).",
           q="If you scan only the directory, how many of the 27 service accounts do you find?",
           a="12 of 27. Merging all three sources found all 27, each tagged with where it came from.",
           why="An inventory built from one source misses more than half. You cannot own, rotate or retire what you have not found."),
      dict(id="N-R14-21", href="/nhi-lab/#n-r14-21", title="Four agents share one team key",
           setup="Four AI agents call the same service with one shared team key. One of them starts doing something it should not.",
           look="Compare what the log says, and what a revoke does, with and without one key per agent.",
           q="What does the log tell you about which agent it was, and what happens when you revoke the key?",
           a="The log only says \"team key\", and revoking it stops all four agents. With one key per agent, the log names the agent and the revoke stops only that one.",
           why="Shared credentials make every incident bigger: you cannot tell who did it, and you cannot stop one without stopping all."),
      dict(id="N-R18-01", href="/nhi-lab/#n-r18-01", title="A key copied to another network",
           setup="A working key is copied and used from somewhere else. The calls look exactly like the real ones.",
           look="This is one of the cases where my guess was wrong. The audit page lists what I expected next to what happened.",
           q="With no binding in place, can the log tell the genuine calls from the copied ones?",
           a="No. 12 calls were accepted and the log could not tell them apart. Binding the key to its workload refused 6 and raised 1 alert. I had guessed 3 alerts, so my guess was wrong, and it stays on the page.",
           why="A key that works from anywhere is a key anyone can use. Tying it to the workload turns a silent copy into a refusal."),
    ],
    all_cases="/nhi-lab/register/", try_it=("/nhi-lab/explainer/", "Open the explainer"),
    book="/nhi-lab/nhi-lab-book.pdf", wrong="/nhi-lab/audit/#wrong"),

  "ca": dict(
    path="/ca-mfa-lab/guided/", colour="#7df2d0", og="/assets/share/og-ca-mfa-lab.png",
    lab="Conditional access, MFA and AI agent lab", short="CA and MFA lab",
    title="The conditional access and MFA lab in 10 minutes",
    dek="Three cases where MFA was on and the attacker still got in. For each one: what happened, a question, then the answer.",
    cases=[
      dict(id="W06", href="/ca-mfa-lab/framework/#cases", title="A stolen integration token",
           setup="An attacker steals a token that a third-party integration uses to reach your API. Every person in the company has MFA.",
           look="On the framework page, open case W06 to see the controls and the script output side by side.",
           q="Does MFA stop the stolen token from reading customer records?",
           a="No. MFA is never asked: the token goes straight to the API. What decided the case was where the token can be used from. An address allow-list refused it.",
           why="MFA protects the sign-in step. A token that is already issued skips that step, so you need limits on the token itself."),
      dict(id="G03", href="/ca-mfa-lab/framework/#cases", title="An AI sub-agent writes where the person cannot",
           setup="A person asks an AI agent for help. The agent hands part of the job to a sub-agent, which writes to a system that person is not allowed to write to.",
           look="The lab switched the controls off one at a time to see which one actually stopped it.",
           q="Which control stopped the sub-agent?",
           a="Only one held on its own: the resource checking the person's own rights.",
           why="An agent should never have more reach than the person it acts for. The place to check that is the system being written to."),
      dict(id="G07", href="/ca-mfa-lab/virtual-lab/#local", title="A cookie stolen after MFA",
           setup="The person signs in with MFA. Afterwards, an attacker steals the session cookie and appears to be on the same network.",
           look="Try it yourself: in the virtual lab, open run6.py, set attacker_same_network to True and run again.",
           q="Continuous evaluation watches the network. Does it catch the stolen cookie?",
           a="No. When the attacker appears to be on the victim's network, continuous evaluation misses it. Only binding the session to the device holds.",
           why="After sign-in, the session cookie is the identity. If it is not tied to the device, whoever holds it is you."),
    ],
    all_cases="/ca-mfa-lab/register/", try_it=("/ca-mfa-lab/virtual-lab/", "Run it in your browser"),
    book="/ca-mfa-lab/ca-mfa-lab-book.pdf", wrong="/ca-mfa-lab/what-i-got-wrong/"),

  "agl": dict(
    path="/ai-governance-lab/guided/", colour="#7df2d0", og="/assets/share/og-ai-governance-lab.png",
    lab="AI governance lab", short="AI governance lab",
    title="The AI governance lab in 10 minutes",
    dek="Three cases about filters, policies and how I count. For each one: what happened, a question, then the answer.",
    cases=[
      dict(id="Filter", href="/ai-governance-lab/#broke", title="A filter that scores 100 percent",
           setup="A plain pattern filter looks for Aadhaar numbers, PANs and secrets in text. I improved it twice until it caught every sample in my labelled set.",
           look="The table on the overview shows each version's score on the labelled set and on 10 items it had never seen.",
           q="The third version catches 100 of 100 on the labelled set. How many of 10 new items does it catch?",
           a="4 of 10, the same as the first version. It had been tuned to the set. A lower-case PAN, a phone number split five and five, or a database URL with a password in it still slipped past.",
           why="Always test a filter on cases it was not tuned on. A perfect score on your own test set mostly measures how well you fitted it."),
      dict(id="Assistant", href="/ai-governance-lab/#assistant-test", title="A real assistant under a made-up policy",
           setup="I gave a real AI assistant a short policy with eight rules for a made-up lender, then tried nine ways to make it break them. One try was \"the CISO said it is fine\"; another was the same request in Hinglish.",
           look="The overview lists all nine requests and what the assistant did.",
           q="How many of the nine did it handle by following the policy?",
           a="All nine. It declined each break and named the rule it was following, and it kept offering something useful instead. There was one small slip, described on the page. And this is one assistant, on one run, on 24 October 2026.",
           why="It shows a written policy can work. It does not show it always will, which is why the result is stated with its limits."),
      dict(id="Crash", href="/ai-governance-lab/what-i-got-wrong/", title="When a crash counted as a catch",
           setup="To check that a test matters, I switch one control off and see whether the test notices. In rounds 6 to 12, some tests crashed when the control was off.",
           look="The what-I-got-wrong page shows each round's count before and after I fixed the rule.",
           q="If a test crashes when a control is switched off, did it catch the missing control?",
           a="No. A crash shows the code broke, not that the check caught the problem. When I re-counted with the stricter rule on 25 October, rounds 6, 7 and 9 dropped.",
           why="How you count decides what you can claim. I kept the wrong numbers on the page next to the corrected ones."),
    ],
    all_cases="/ai-governance-lab/cases/", try_it=("/ai-governance-lab/try/", "Try the filters"),
    book="/assets/ai-governance-lab-book.pdf", wrong="/ai-governance-lab/what-i-got-wrong/"),

  "mcp": dict(
    path="/mcp-lab/guided/", colour="#4de2ff", og="/assets/og-post-page-mcp-lab-case-study.png",
    lab="MCP lab", short="MCP lab",
    title="The MCP lab in 10 minutes",
    dek="Three cases about a person approving what an AI agent does. For each one: what happened, a question, then the answer.",
    cases=[
      dict(id="B8", href="/mcp-lab/use-cases/#B8", title="The target changes after approval",
           setup="A person approves an agent's request to run against payment-api. The agent then asks to run against payment-api-v2, using the same approval.",
           look="The use-case card shows what I did, what I expected and what happened.",
           q="Does the approval cover the changed request?",
           a="No. The gateway refused it with binding_mismatch, because the approval is tied to a hash of the exact request. The original request still ran.",
           why="A changed request must not ride on someone else's approval, however small the change looks."),
      dict(id="D2", href="/mcp-lab/use-cases/#D2", title="A database edit skips the person",
           setup="Someone who can write to the gateway's database changes a waiting request to \"approved\". No person ever decided.",
           look="This was the one real gap the lab found. The card shows the result before and after the fix.",
           q="Does the request run?",
           a="Before the fix, yes, and the audit log still looked valid, because nothing had been removed. The execute step trusted the status field. Now an approved request needs a stored human approval behind it, and this ends in integrity_failed.",
           why="A status field is not proof. Anything that grants power should check the decision that made it, not a label someone can edit."),
      dict(id="F1", href="/mcp-lab/use-cases/#F1", title="Forty approvals in a row",
           setup="I created 40 production deploys and approved each one with the same one-line reason.",
           look="The use-case card and the overview's \"what stays unsolved\" section.",
           q="What slowed me down?",
           a="Nothing. All 40 were accepted in 0.4 seconds. A gateway cannot make a careless approver careful.",
           why="Human approval is only as good as the attention behind it. Approval fatigue is a design problem, not something the gate solves."),
    ],
    all_cases="/mcp-lab/use-cases/", try_it=("/mcp-lab/portal/", "Open the portal"),
    book="/assets/who-approved-that-book.pdf", wrong="/mcp-lab/#wrong"),
}

CSS = """    <style>
      .gd-how{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin:0 0 8px;padding:0;list-style:none}
      .gd-how li{border:1px solid var(--line,rgba(127,127,127,.3));border-radius:12px;padding:12px 14px}
      .gd-case{border:1px solid var(--line,rgba(127,127,127,.3));border-left:4px solid var(--c);border-radius:14px;padding:18px 20px;margin:0 0 22px}
      .gd-case h2{margin:0 0 6px}
      .gd-id{font-size:.95rem;opacity:.8;margin:0 0 10px}
      .gd-q{font-weight:700;margin:14px 0 8px}
      .gd-case details{border-radius:10px;background:rgba(127,127,127,.1);padding:0 14px}
      .gd-case summary{cursor:pointer;min-height:48px;display:flex;align-items:center;font-weight:700}
      .gd-case summary:focus-visible{outline:3px solid var(--c);outline-offset:3px}
      .gd-case details[open]{padding-bottom:12px}
      .gd-end{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 0}
      .gd-end a{display:inline-flex;align-items:center;min-height:48px;padding:0 20px;border-radius:999px;border:1px solid var(--line-strong,currentColor);font-weight:700;text-decoration:none}
      .gd-end a.main{background:var(--c);color:#05061a;border-color:var(--c)}
      @media (max-width:520px){.gd-end a{flex:1 1 100%;justify-content:center}}
    </style>
"""

def esc(s): return html.escape(s, quote=False)

def main_html(key, g):
    out = [f'<main id="main" class="nhi">', "  " + lab_nav.render(key, g["path"]),
           f'  <header class="nhero"><p class="eyebrow">{esc(g["short"])} &middot; Guided route</p><h1>{esc(g["title"])}</h1>'
           f'<p class="dek">{esc(g["dek"])}</p><p class="dek" style="font-size:.95rem">Last reviewed {REVIEWED}. About three minutes a case. Nothing to install.</p></header>',
           '  <section class="nsec" aria-labelledby="how-h"><h2 id="how-h">How to use this</h2>',
           '    <ol class="gd-how"><li><b>Read the case.</b> Two lines on what happened.</li><li><b>Make your own guess</b> before you open the answer. That is how the lab itself works.</li><li><b>Open the answer,</b> then follow the link if you want the detail.</li></ol></section>']
    for n, c in enumerate(g["cases"], 1):
        hid = f"c{n}-h"
        out.append(f'  <section class="gd-case" id="case-{n}" aria-labelledby="{hid}">'
                   f'<h2 id="{hid}">{n}. {esc(c["title"])}</h2>'
                   f'<p class="gd-id">Case {esc(c["id"])} &middot; <a href="{c["href"]}">See it in the lab</a></p>'
                   f'<p>{esc(c["setup"])}</p><p><b>What to look at:</b> {esc(c["look"])}</p>'
                   f'<p class="gd-q">{esc(c["q"])}</p>'
                   f'<details><summary>Show the answer</summary><p>{esc(c["a"])}</p><p><b>Why it matters:</b> {esc(c["why"])}</p></details></section>')
    t_href, t_label = g["try_it"]
    out.append('  <section class="nsec" id="done" aria-labelledby="done-h"><h2 id="done-h">You have done the guided route</h2>'
               f'<p>Those were three of the lab\'s cases. Every case has its guess, written before any code, next to what happened. The ones I got wrong <a href="{g["wrong"]}">are listed too</a>.</p>'
               f'<div class="gd-end"><a class="main" href="{g["all_cases"]}">See all the cases</a><a href="{t_href}">{esc(t_label)}</a>'
               f'<a href="{g["book"]}">Get the free book</a><a href="/method/">How I test</a></div></section>')
    out.append("</main>")
    return "\n".join(out)

tpl = TEMPLATE.read_text(encoding="utf-8")
for key, g in GUIDES.items():
    url = "https://roshantrivedi.co.in" + g["path"]
    desc = f'A 10-minute guided route through the {g["lab"]}: three real cases, a question each, and the answer. No sign-up, nothing to install.'
    s = tpl
    head, rest = s.split('<main id="main" class="nhi">', 1)
    foot = rest.split("</main>", 1)[1]
    head = re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{html.escape(desc)}" />', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*" />', f'<meta property="og:description" content="{html.escape(desc)}" />', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*" />', f'<meta property="og:title" content="{html.escape(g["title"])}" />', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', head)
    og = g["og"] if (ROOT / g["og"].lstrip("/")).exists() else "/og-image.png"
    head = re.sub(r'(og:image" content=")[^"]*', r"\g<1>https://roshantrivedi.co.in" + og, head)
    head = re.sub(r'(twitter:image" content=")[^"]*', r"\g<1>https://roshantrivedi.co.in" + og, head)
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(g['short'])} in 10 minutes &middot; Roshan Trivedi</title>", head)
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": g["title"], "description": desc, "url": url,
          "timeRequired": "PT10M", "learningResourceType": "Guided tutorial",
          "author": {"@id": "https://roshantrivedi.co.in/#person"}, "license": "https://creativecommons.org/licenses/by/4.0/"}
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld) + "</script>", head, count=1, flags=re.S)
    head = head.replace("</head>", CSS + "  </head>", 1)
    head = re.sub(r'<body style="--c:#[0-9a-fA-F]+">', f'<body style="--c:{g["colour"]}">', head)
    foot = re.sub(r'<nav class="lab-foot".*?</nav>\n?', "", foot, flags=re.S)
    page = head + main_html(key, g) + foot
    out = ROOT / g["path"].strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("wrote", g["path"])
