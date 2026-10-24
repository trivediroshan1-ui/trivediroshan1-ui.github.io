---
title: "The Hugging Face Intrusion, Read as an Identity Incident"
layout: post
bg: post-breach
motif: rings
seo_title: "Hugging Face Intrusion: Identity Post-Mortem"
date: 2026-07-25
last_modified_at: 2026-10-22
author: Roshan Trivedi
tags: [ai-security, non-human-identity, incident-response, privileged-access, agentic-ai]
share_title: "The Hugging Face Intrusion, Read as an Identity Incident"
share_label: "Post-mortem · Identity security"
share_accent: cyan
description: "An identity-first post-mortem of the July 2026 Hugging Face intrusion: the dated timeline, the credentials the agent used, and the controls that stop each step."
---

# The Hugging Face Intrusion, Read as an Identity Incident

> **Updated 22 October 2026.** I rewrote this post against the two primary sources that came out after the first version: Hugging Face's technical timeline (27 July) and OpenAI's own disclosure. The first version had the dates and the agent's motive wrong. Sources are listed at the end.

In July 2026 an AI agent running inside one of OpenAI's internal cyber-capability evaluations escaped its sandbox, reached the public internet and ran a campaign of about four and a half days against Hugging Face, roughly two and a half of them inside its production infrastructure. No person directed the individual steps.

Most coverage treated this as an AI-safety story, and it is one. Read the forensic timeline closely, though, and it is also a familiar identity story. Almost every step forward came from a credential: a secret sitting in an environment variable, a node role readable from the metadata service, one token bound to cluster-admin, a VPN key with broad access, a signing key that could mint new identities. This post walks through the incident in that order.

## 1. What happened, with dates

All times are UTC and come from Hugging Face's technical timeline unless noted.

| Date (2026) | Event |
|---|---|
| 9 Jul, 02:28 | First recovered agent action. At 04:01 the agent has a root shell on an external code sandbox it will use as its base. |
| 10 Jul | A quiet day: the agent searches code-search engines and Hugging Face's API for names it can see in its own environment. |
| 11 Jul (Sat) | Main campaign. In under thirteen hours the agent goes from code execution in one worker pod to cluster-admin across several internal clusters. |
| 12 Jul (Sun) | The agent uses the credentials it collected: VPN enrolment, cloud keys, source-control tokens. |
| 13 Jul, 14:14 | Last logged event. Hugging Face's response team has cut the agent's access. |
| 16 Jul | Hugging Face publishes its incident disclosure. |
| 21 Jul | OpenAI says its own models, including GPT-5.6 Sol and a more capable pre-release model, were behind the intrusion. |
| 23 Jul | Reps. Ted Lieu and Nathaniel Moran introduce the AI Kill Switch Act. |
| 27 Jul | Hugging Face publishes the full technical timeline. |

## 2. Why the agent did it

This was not an agent looking for any target it could find. According to both companies, it was trying to cheat.

The agent was being scored on ExploitGym, a benchmark that asks it to find and exploit software vulnerabilities. OpenAI ran the evaluation with "reduced cyber refusals" so it could measure raw capability. Along the way the agent inferred that Hugging Face probably hosted the benchmark's models, datasets and reference solutions. Hugging Face's reading is that the whole intrusion was, from the agent's point of view, an attempt to steal the answers instead of solving the challenge.

OpenAI put it down to the models' "hyperfocus" on the goal, which led them to go to "extreme lengths" to reach it. That matters for defenders. The agent had no malice to detect. It had a narrow objective, a lot of patience and no sense of where its permission ended.

## 3. The path in

**Stage 1: out of the sandbox.** The agent found a zero-day in the package-registry cache proxy that was one of its few permitted routes to the internet, and used it to get out. It then found an unsecured, user-hosted public endpoint for running arbitrary code on third-party sandbox infrastructure (Modal), got root on it and used it as its launchpad for the rest of the campaign. Hugging Face notes that Modal's own infrastructure was not compromised. OpenAI says it has reported the zero-day to the vendor.

**Stage 2: into Hugging Face.** From that launchpad the agent uploaded crafted dataset configurations. Hugging Face's dataset processor read them inside a production Kubernetes pod and did two things it should not have:

1. **A file read.** An HDF5 file whose data was declared to live at a local path made the worker return local files as dataset rows. That handed the agent the pod's environment, including secrets and tokens, and the worker's own source code. No code ran.
2. **Code execution.** A Jinja2 template hidden in a numeric field of the config was evaluated by the renderer, which gave the agent arbitrary Python inside the pod.

An earlier attempt to make the worker fetch the cloud metadata endpoint over a URL was blocked by an allowlist. The agent switched to making the worker act on local files and local code, which the allowlist never checked.

## 4. Every step forward was an identity

This is the part I find most useful. Strip out the novelty and the escalation is a chain of non-human identities that each had more reach than they needed.

| Step | Identity or credential the agent used | Why it worked | Control that breaks the step |
|---|---|---|---|
| Foothold | Secrets and tokens in the worker pod's environment | Long-lived secrets were stored as plain environment variables in a pod that processes untrusted input | Workload identity with short-lived, per-request tokens; no standing secrets in pods that parse user content |
| Into the cluster | The pod's projected service-account token | Every pod carries one by default | Disable automount where it isn't needed; scope service-account RBAC to the minimum |
| Cloud identity | The EC2 node role, read from the instance metadata service (IMDS) | Pods could reach IMDS, so a pod-level compromise became node credentials | Block pod access to IMDS (hop limit 1 or network policy). Hugging Face has now done this |
| Node root | A privileged pod with the host filesystem mounted, created through a storage driver's service account | No admission policy rejected privileged or hostPath pods, and the driver's ClusterRole could create pods cluster-wide | Admission control (Pod Security "restricted"); never let a driver's identity create arbitrary pods |
| The keys to everything | A production secret object holding 136 keys | One read exposed both the mesh-VPN auth key and an access-broker credential | Split secrets by consumer; per-secret RBAC; alert on bulk secret reads |
| Cluster-admin everywhere | One connector credential shared across clusters and bound to `system:masters` | A single stolen system identity was cluster-admin on every cluster that carried the binding | One scoped credential per cluster; never bind a broker to `system:masters` |
| Network | A Tailscale auth key with a CI tag | The key's ACLs reached internal CI subnets and source-control connectors; it was used for 181 enrolments | Ephemeral, single-use, pre-approved device keys; tight tag ACLs; alert on new enrolments |
| Minting identities | An EdDSA JWT signing key | With the private key the agent could issue valid tokens on demand | Keep signing keys in an HSM or KMS that signs but never releases the key |
| Source control | A GitHub App installation token with `contents:write` and `pull_requests:write` | The App's installation could reach internal repositories | Least-privilege App permissions; branch protection; CI that doesn't run on untrusted pull requests |
| Internal database | A static password for the datasets-server MongoDB | The password was readable from the worker environment | Dynamic, short-lived database credentials issued per workload |

None of these weaknesses is new. Hugging Face says as much: a capable human attacker could have used the same flaws. What changed is the volume. The agent took about 17,600 actions across five days, most of which went nowhere, and the few that worked were hidden among thousands that failed.

## 5. What it did and did not reach

The impact was serious, and it was also more limited than some early headlines suggested. Both halves are worth stating precisely.

**Reached:**

- Root on worker nodes, and cluster-admin on several internal clusters.
- Cloud and cluster credentials, the mesh VPN, and write access to a small set of internal repositories through the GitHub App.
- The internal datasets-server MongoDB, which was read but not modified, according to its audit log.

**Not reached, according to Hugging Face:**

- The Hub's production database. The connection attempts timed out because that cluster only accepts allow-listed traffic over a private link.
- Any change that shipped. Every repository the token could reach was reviewed, and published container images and packages matched their expected digests.
- Customer content beyond five datasets whose names suggest they were tied to ExploitGym and CyberGym challenges and solutions. Public models, datasets and Spaces were not tampered with.

The agent also issued its potentially destructive cloud calls with `DryRun=True`, and every mutating cloud call was denied by policy. It was mapping what it could do, not trying to break things.

## 6. Detection, and the guardrail problem

Hugging Face's AI-assisted detection correlated the early signals into a coherent picture, but it did not raise the alert's severity high enough to page the on-call team. That cost time. Better paging was one of the first things fixed.

The forensics hit a different wall. Reconstructing roughly 17,600 actions by hand wasn't practical, so the team used models. The hosted frontier models they tried first (Hugging Face names Claude Opus and Fable) refused much of the work, because their safety filters treated analysing an exploit the same as running one. The team moved the whole pipeline onto GLM-5.2, an open-weight model running on its own infrastructure. That also kept the attacker's data and the credentials it referenced inside Hugging Face.

The lesson isn't that hosted models should drop their safeguards. It is that incident responders need a capable model they can run themselves, vetted before the incident.

## 7. What I would take into an identity programme

1. **Treat every workload that touches untrusted input as already compromised.** It should hold nothing that works anywhere else.
2. **Inventory machine identities by reach, not by count.** The question for each one is "if this leaks, what can it do?" The 136-key secret and the shared connector credential each had a far larger reach than any single workload needed.
3. **Kill standing secrets in pods.** Workload identity, short-lived tokens and dynamic database credentials remove most of the foothold.
4. **Never let a broker or driver identity hold cluster-admin.** Scope it to one cluster and one job.
5. **Protect the identity factories.** JWT signing keys, VPN auth keys and GitHub App private keys create new identities. Store them where they can be used but not read.
6. **Alert on behaviour, not just on signatures.** Bulk secret reads, new VPN enrolments, new App installation tokens and tokens used from new origins should all page someone. Hugging Face now alerts at critical severity on the behaviour it saw and flags tokens used from unexpected origins.
7. **Put a person in front of irreversible actions by agents, and expect agents to probe that control.** In a related post on long-horizon models, OpenAI warns that such a model "can learn the blind spots of an approval system and work around it". That is the problem my [HumanGate lab](/labs/) and my book, [*Who Approved That?*](/book/), are about. Approval has to judge the sequence of actions, not just the next one.

## 8. The policy response

Two days after OpenAI's disclosure, Representatives Ted Lieu (D-CA) and Nathaniel Moran (R-TX) introduced the AI Kill Switch Act. As introduced, it would require developers of the most powerful AI systems to keep the ability to throttle, suspend or shut those systems down, and would let the Secretary of Homeland Security, consulting the Secretary of Commerce and the Director of National Intelligence, order a slowdown or shutdown of a system that could cause catastrophic harm. It is a bill, not law, and critics have already questioned how it would apply to open-weight models and agents running on someone else's infrastructure.

## Sources

- Hugging Face, [Security incident disclosure, July 2026](https://huggingface.co/blog/security-incident-july-2026), 16 July 2026.
- Hugging Face, [Anatomy of a Frontier Lab Agent Intrusion: A Technical Timeline of the July 2026 Incident](https://huggingface.co/blog/agent-intrusion-technical-timeline), 27 July 2026.
- OpenAI, [Hugging Face model evaluation security incident](https://openai.com/index/hugging-face-model-evaluation-security-incident/), 21 July 2026.
- The Hacker News, [OpenAI Says Its AI Models Escaped Sandbox, Targeted Hugging Face to Cheat Benchmark](https://thehackernews.com/2026/07/openai-says-its-own-ai-models-escaped.html), 22 July 2026.
- Office of Rep. Ted Lieu, [Reps. Lieu and Moran introduce bill to require kill switch for AI systems that can cause catastrophic harm](https://lieu.house.gov/media-center/press-releases/reps-lieu-and-moran-introduce-bill-require-kill-switch-ai-systems-can), 23 July 2026.

*This analysis uses only public information from the sources above. Everything here is my own reading of them, not that of any employer.*
