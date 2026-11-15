#!/usr/bin/env python3
"""Add a 'What the video shows' list under each silent video that had no written version (A11Y-05).

The text is the video's own: round videos use the steps from the same page section their
video is built from (build-agl-round-video.py), the architecture video uses its scene captions
(build-agl-arch-video.py), and the agentic case-study video was read frame by frame.
Each block sits between <!-- vt:start --> and <!-- vt:end --> after the video, so re-running
replaces it. Run after any script that rebuilds these pages:  python3 scripts/add-video-text.py
"""
import html, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent


def esc(s):
    return html.escape(s, quote=False)


def block(items, intro=None):
    li = "".join(f"<li>{esc(i)}</li>" for i in items)
    head = f'<p>{esc(intro)}</p>' if intro else ""
    return ('<!-- vt:start -->\n        <details class="vid-text"><summary>What the video shows</summary>'
            f'{head}<ol>{li}</ol></details>\n        <!-- vt:end -->\n')


def put_after(path, marker_end, text):
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!-- vt:start -->.*?<!-- vt:end -->\n", "", s, flags=re.S)
    i = s.index(marker_end) + len(marker_end)
    s = s[:i] + "\n        " + text + s[i:].lstrip("\n")
    if "/assets/vid-text.css" not in s:
        s = s.replace("</head>", '  <link rel="stylesheet" href="/assets/vid-text.css?v=20261115a">\n  </head>', 1)
    p.write_text(s, encoding="utf-8")
    print("video text:", path)


def first_sentence(s):
    s = re.sub(r"\s+", " ", s).strip()
    return re.split(r"(?<=[.!?])\s", s)[0]


# Rounds 10 to 13: the steps on each round page, which the video is built from.
for n in (10, 11, 12, 13):
    seg = (ROOT / f"ai-governance-lab/round-{n}/index.html").read_text(encoding="utf-8")
    seg = seg[:seg.index(f"<!-- rv{n}:start -->")] if f"<!-- rv{n}:start -->" in seg else seg
    steps = []
    for blk in seg.split('<li class="lc-step"')[1:]:
        m = re.match(r' data-lane="\w+"><h[34]>(.*?) <span class="lc-who">.*?</span></h[34]><p>(.*?)</p>', blk, re.S)
        if m:
            t = html.unescape(re.sub("<.*?>", "", m.group(1)))
            w = html.unescape(re.sub("<.*?>", "", m.group(2)))
            steps.append(f"{t}: {first_sentence(w)}")
    items = ["The question for the round, and a note that all data is made up.",
             "Guesses first: when the expected results were saved, before any code, with the file's SHA-256."]
    items += steps
    items += ["How many cases came out as guessed, how many switched-off controls were noticed, and the run on my MacBook Air.",
              "What the round does not show."]
    put_after(f"ai-governance-lab/round-{n}/index.html", f"<!-- rv{n}:end -->",
              block(items, "Silent, with on-screen text. In order:"))

# The architecture video: its scene captions, from build-agl-arch-video.py.
arch = [
    "One picture of the whole lab, with numbers that match the seven diagrams.",
    "The agent only proposes: it sends a request in a fixed shape. The gateway checks who is asking, the shape, the policy, the rate and whether a person must approve, then signs a decision. A separate executor checks the signature, borrows a five-minute credential and makes the call. The agent never sees the credential, and every decision is logged.",
    "If the agent goes around the gateway (layer 1, make it hard): a token found in a config file only works from the caller it was lent to, and the agent has no network route to the API.",
    "If it still gets through (layer 2, notice): a scheduled job lines up every change in the identity system's log with a signed decision. A change with no decision behind it is a bypass alert.",
    "Then answer (layer 3): the alert is traced to one agent, which is switched off and its access revoked. Logs are copied and hashed before clean-up. A person decides what to undo, then the hole is closed and the case added to the tests.",
    "An identity starts in HR: an approved hire, two people for the risky steps, the minimum data, MFA from day one, then a check that the directory matches HR. Leavers still active and movers with old access are flagged.",
    "Answering from documents: the person's permissions are checked live before any document is fetched, so the model only sees what they may read. Telling the model not to reveal something changed nothing.",
    "Agents handing work to agents: the second agent inherited everything until the token was cut down to the job. Deleting a user needs a second person with a separate key and a public-key signature. If the approver leaves, their waiting requests move to the manager.",
    "All of it together: every box was tested with the expected result written first, then with the control switched off.",
]
put_after("ai-governance-lab/index.html", "<!-- archvid:end -->", block(arch, "Two minutes, silent, every scene captioned. In order:"))

# The agentic case-study video (55 seconds), read frame by frame.
mcp = [
    "Who is acting when an AI agent calls a tool? Rebuilt after feedback; open source; real-environment testing still pending.",
    "Four hops between a person and an account: person, host app, MCP client, MCP server, downstream API. The host runs one client per server, and the tool touches a real account.",
    "Three identities hide in one tool call: the user who authorises the client, the agent or client holding a token meant for one server, and the server with its own downstream credential. Tokens are audience-bound and never passed through.",
    "Authenticated is not the same as approved: agent, policy, a human who is not the requester, then a hash-bound, single-use, time-limited grant, then execute. The AI analyst is advisory only.",
    "What the gateway enforces: approval is tied to a hash of the exact request (a changed argument fails with binding_mismatch), a grant works once (replay_blocked), requesters cannot approve their own requests, unknown tools fail closed, and every step lands in a hash-chained audit log.",
    "What if the response is lost: reserve with an idempotency key, dispatch, and if the outcome is unknown, no blind retry; a reviewer reconciles after five minutes.",
    "What is tested and what is not: 203 automated tests pass; tools are synthetic and reviewers simulated; the prompt-injection check is a heuristic; a run in a real environment with a third-party MCP client is still pending.",
]
p = ROOT / "case-studies/agentic-ai-identity-governance/index.html"
s = p.read_text(encoding="utf-8")
if "<!-- mcpvid:end -->" not in s:
    i = s.index("/assets/mcp-workflow.mp4")
    j = s.index("</figure>", i) + len("</figure>")
    s = s[:j] + "\n        <!-- mcpvid:end -->" + s[j:]
    p.write_text(s, encoding="utf-8")
put_after("case-studies/agentic-ai-identity-governance/index.html", "<!-- mcpvid:end -->", block(mcp, "55 seconds, captioned. In order:"))
