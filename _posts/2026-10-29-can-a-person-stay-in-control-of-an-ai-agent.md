---
title: "Can a Person Stay in Control of an AI Agent? I Tried to Break an Approval Gate 76 Ways"
layout: post
bg: post-plan
motif: grid
seo_title: "Can a Person Control an AI Agent? An MCP Approval Gate Test"
date: 2026-10-29 12:00:00 +0530
author: Roshan Trivedi
tags: [mcp, ai-agents, human-approval, audit, agentic-ai, security-testing]
share_title: "Can a Person Stay in Control of an AI Agent?"
share_label: "Article · MCP lab"
share_accent: violet
description: "I built a small approval gate for MCP tool calls and tried to break it 76 ways. What held, what did not, and the one gap that matters."
---

# Can a Person Stay in Control of an AI Agent? I Tried to Break an Approval Gate 76 Ways

*Filed under: MCP · Agent Governance*

*Independent practitioner write-up. Last reviewed 29 October 2026. Everything here comes from my own public lab, which uses synthetic tools only. It does not describe any employer's systems, data or projects.*

## The short version

- I built a small open-source gateway that sits between an AI agent and its tools, using MCP (Model Context Protocol). Risky calls wait for a person. The approval is tied to the exact request, works once and expires.
- I then tried to break it. The first round was 76 scripted cases against the real endpoint. Three rounds ran 210 scripted checks in total.
- A changed target, an extra argument, a look-alike letter and an invisible character were all refused. Reusing an approval was refused. An expired approval was refused, including after a real 11-minute wait.
- The one real gap: if someone could write to the database and flip a request to approved, it ran, and the audit log still looked valid. I fixed it, and a test now covers it.
- What a gateway cannot fix is the person. I approved 40 production deploys in under half a second with the same reason each time, and nothing slowed me down.

## The question

An AI agent can now search docs, read a repository, change a role and deploy to production. Some of those calls matter. When a person says yes to one of them, can the agent do exactly what was approved, once, and can anyone prove it afterwards?

Why: "human in the loop" is easy to say. It only means something if the approval is bound to one specific action and leaves a record that survives an argument.

## What I built

The gateway scores every tool call with fixed rules. Low-risk calls run. Risky ones wait for a person with the right role. The approval is tied to a hash of the exact request, so a changed target or an extra argument no longer matches. It works once, and it expires. Every decision, including every refusal, goes into a hash-chained audit log, so an edited event shows up.

An AI analyst can write advice for the reviewer. It cannot approve, deny or change the score.

Why: if the model that proposes an action can also approve it, the approval is decoration.

## How I tested it

Three ways: a real MCP client (the official Inspector) clicked by hand, a script that runs the cases against the real endpoint, and a browser lab where I can make a tool lose its reply. Every case has a line saying what I expected before I ran it. 81 use cases are documented, and six are marked not done. The repository has 213 automated tests.

Three numbers on my site count different things, so here is how they fit. 210 is the scripted checks across the three rounds (76, 88 and 46). 161 is the case cards in the portal, which are fewer because some cards cover a few related checks. 213 is the gateway's own test suite. They are not the same 210.

## What held

- A changed target, an extra argument, a look-alike letter or an invisible character: refused.
- Reusing an approval, or two runs at the same instant: one runs, the other is blocked.
- An expired approval, including after a real 11-minute wait: refused.
- Editing a stored request or one audit event in the database: caught.
- A lost reply: the work ran once, no second run was possible, and only a person who was not the requester could settle it.

## What I got wrong

Six of my guesses were off on the first run.

- A trailing space did not matter.
- Hostile text was denied before a person saw it.
- A made-up reviewer was accepted.
- The status tool lagged behind the result tool.
- An expired queue entry still looked pending.
- One database edit let a request skip the human decision altogether.

The last one is the real gap. The execute step trusted the status field, so flipping a request to approved in the database ran it, and the audit log still looked valid because nothing had been removed. Now an approved request needs a stored human approval behind it. I closed the other open findings the same way, and each has a test.

## What stays unsolved

People. When a reply is lost, a person settles the outcome, and the log holds whatever they say. I recorded "it ran" for something that never ran, and it was written down under my name. I approved 40 production deploys in under half a second with the same reason each time. A gateway cannot make a careless approver careful.

Reviewer identity is only partly addressed. An optional allowlist limits which typed names count, but the names are still not proven.

## Where it sits against the OWASP MCP Top 10

This is my own reading, not an OWASP assessment and not a claim of coverage. "Tested" means a case in the lab, on synthetic tools only.

| Area | Status in the lab |
| --- | --- |
| Privilege escalation via scope creep | Tested: the scenario is denied, and scopes are in the request hash |
| Tool poisoning | Tested: a tool loosened after approval still ran in round two. The tool definition is now in the hash, and the same case is refused |
| Intent flow subversion | Tested: hostile instructions in request text are denied before a person sees them. It is a phrase heuristic, and only text payloads were tried |
| Lack of audit and telemetry | Tested: the hash-chained log catches an edited event. Unsigned chains now warn |
| Insufficient authentication and authorization | Partly: roles and self-approval are enforced, but reviewer names are typed, not proven |
| Supply chain and shadow MCP servers | Out of scope, not examined |

## What I would take from this

1. Bind every approval to the exact request, make it single-use, and give it an expiry.
2. Make the execute step check for a stored human approval, not a status field someone can edit.
3. Keep the model that advises separate from the person who approves.
4. Test the people side. Put a reviewer under volume and see how fast they approve.

## Limits

One run each, on my machines, with synthetic tools. This shows what this gateway did on these cases. It does not prove it secure. Not tested: a second MCP client at scale, many real people reviewing at volume, and a real sign-in.

## Read more, free

The gateway, the 122-page report and the 138-page book *Who Approved That?* are all on my site: [the MCP approval lab](https://roshantrivedi.co.in/mcp-lab-case-study/), [the in-depth write-up](https://roshantrivedi.co.in/mcp-lab-in-depth/), and the source on [GitHub](https://github.com/trivediroshan1-ui/mcp-human-approval-gateway). If you see a weak case, tell me which one.

**Roshan Trivedi** writes about privileged access, identity and AI governance at [roshantrivedi.co.in](https://roshantrivedi.co.in). Newsletter: [buttondown.com/trivedi](https://buttondown.com/trivedi).

*All data in the lab is made up. Nothing here relates to any employer or real company.*
