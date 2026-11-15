#!/usr/bin/env python3
"""Add optional topic choices to every Buttondown signup form (AN-02).

Each ticked box is sent as a Buttondown tag (input name="tag"); Buttondown creates a tag the
first time it sees it, so nothing has to be set up there first. Leaving every box unticked
means 'send me everything'. Re-running replaces the block between the markers.
    python3 scripts/add-signup-topics.py
"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "ca-mfa-lab/index.html", "_layouts/post.html", "writing/index.html",
         "book/index.html", "ai-governance-lab/index.html", "nhi-lab/index.html"]
TOPICS = [("pam", "Privileged access and credentials"), ("nhi", "Machine identities and secrets"),
          ("ai-agents", "AI agents and AI governance"), ("sign-in", "Sign-in, MFA and conditional access")]
CSS = '<link rel="stylesheet" href="/assets/signup-topics.css?v=20261115a">'


def block():
    boxes = "".join(f'<label><input type="checkbox" name="tag" value="{v}"> {t}</label>' for v, t in TOPICS)
    return ('<!-- topics:start --><fieldset class="su-topics"><legend>Which topics? Optional. '
            'Leave them all unticked to get everything.</legend>' + boxes + '</fieldset><!-- topics:end -->')


for rel in PAGES:
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!-- topics:start -->.*?<!-- topics:end -->\s*", "", s, flags=re.S)
    i = s.index("embed-subscribe/trivedi")
    j = s.index("<small>", i)
    s = s[:j] + block() + "\n              " + s[j:]
    if "/assets/signup-topics.css" not in s:
        s = s.replace("</head>", "  " + CSS + "\n  </head>", 1)
    p.write_text(s, encoding="utf-8")
    print("topics:", rel)
