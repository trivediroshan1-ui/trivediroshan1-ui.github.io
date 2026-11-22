---
title: "Break Glass: Eight Ways to Build It, and What to Do When the Tool Is the Thing That Is Down"
layout: post
bg: post-plan
motif: grid
seo_title: "Break-Glass Emergency Access: Eight Ways to Build It"
date: 2026-11-20 11:30:00 +0530
last_modified_at: 2026-11-22
author: Roshan Trivedi
tags: [break-glass, emergency-access, privileged-access, pam, ai-agents]
diagrams: true
share_title: "Break glass: eight ways to build it, and when the tool is down"
share_label: "Guide · Privileged access"
share_accent: green
description: "Eight ways to build break-glass access, what to do when the PAM tool is down, what four vendors document, what auditors need, and where AI agents fit."
---

# Break Glass: Eight Ways to Build It, and What to Do When the Tool Is the Thing That Is Down

*Filed under: Privileged access · Emergency access*

*Independent practitioner guide, last reviewed 22 November 2026. Written on my own time. Lab data is made up. Nothing here describes any employer's or client's systems. Vendor details come from each vendor's own pages as I read them on 20 November 2026, and pages change.*

On this page: [the short version](#the-short-version) · [the question to ask first](#the-question-to-ask-first) · [eight ways](#eight-ways) · [three people](#three-people) · [when things are down](#when-things-are-down) · [guardrails and approval](#guardrails-and-approval) · [who owns it](#who-owns-it) · [four vendors](#four-vendors) · [three cloud platforms](#cloud-platforms) · [business, governance and audit](#business-governance-audit) · [AI](#ai) · [out of the box](#out-of-the-box) · [start here](#start-here)

## The short version {#the-short-version}

- Break-glass is one idea built in at least eight ways. Which one saves you depends on a single question: what has to be working when you reach for it?
- Three people carry it: the user who needs in, the custodian who holds the key, and the administrator who builds and tests it. A fourth, the reviewer, closes every use.
- Each vendor I read gives you parts, such as a vaulted account, a replica, an offline cache or a sealed recovery key. None of them supplies the owner, the drill or the review. Those stay with you.
- AI can help prepare, watch and write up. In my design it never holds, releases, approves or uses the credential. That part is a proposal and I have not tested it.

## The question to ask first {#the-question-to-ask-first}

The failure that worries me most is one the design builds in: the way in depends on the system that is down. A sealed password that is stored in the vault. An alert that goes through the chat tool that has failed. An emergency account that sits under the same sign-in policy as everyone else.

So before choosing a method, write down for each one what has to be working for it to work. If the answer includes the thing the method is meant to cover, it is a normal path with a different name.

## Eight ways to build it {#eight-ways}

These are the patterns I know. They are meant to be layered, not chosen one at a time.

| Way | What it is | Still works when | Stops working when |
|---|---|---|---|
| 1. Vaulted emergency account | A pre-created account whose password sits in the PAM tool and is checked out in an emergency | Normal approval or your own access is blocked, but the vault is up | The vault, its database or its sign-in is down |
| 2. Self-approved request | The responder approves their own access request, with a written reason, when no approver can be reached | The request tool is up and nobody can approve in time | The tool is down, or it becomes a shortcut and nobody reviews it |
| 3. Replica or second site | A read-only copy of the secrets, sometimes with emergency accounts, on a second instance | One site or instance fails | Both fail for the same cause, such as a shared database or identity provider |
| 4. Offline cache or export | An encrypted export, or a cache on a device, holding the last known passwords | The tool cannot be reached but the file or device can | The copy is stale after a rotation, or the device is lost |
| 5. Sealed physical copy | Credentials or recovery media in a safe, split between two custodians | Nothing digital works | A custodian cannot be reached, or the copy was not refreshed after the last rotation |
| 6. Local emergency account | An account on the server or device itself, kept for when central tools cannot be reached | The machine is up and the central tools are not | The password is stale, a clean-up job removed the account, or a login redirect sends it to the failed service |
| 7. Cloud-only account at the identity provider | An account that lives in the tenant itself, not synchronised or federated | Federation or on-premises sign-in fails | A sign-in policy blocks it, or the tenant is unavailable |
| 8. Vendor-assisted recovery | You ask the vendor's support to help you back in | You have lost everything you own and can prove who you are | It is 2 a.m., or you cannot prove it |

Think of them as a ladder, and give it one rule: each rung must not depend on the one above it.

<figure class="diagram-card" style="--c:var(--pal-mint);margin-top:14px"><button type="button" class="anim-toggle" aria-pressed="false">Pause animation</button><svg class="d-wide" viewBox="0 0 960 460" role="img" aria-labelledby="ladwt ladwd"><title id="ladwt">The ladder of ways in, from the normal path to the vendor</title><desc id="ladwd">Five ways in, left to right, tried in order. One: the normal path, which needs everything working. Two: an emergency path inside the tool, a vaulted account or a self-approved request. Three: another copy of the tool, a second site, a replica or an offline cache, which fails together with the first if the cause is shared. Four: outside the tool, a sealed copy held by two custodians, local accounts and cloud-only accounts. Five: the vendor's support or recovery media. The rule under the boxes is that each rung must not depend on the one above it. Three things are marked as not tested yet.</desc><defs><marker id="ladaw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--c)"/></marker></defs><g class="node" style="--i:0.0"><rect x="50" y="30" width="152" height="150" rx="12"/><text class="ttl" x="126.0" y="62" text-anchor="middle">Normal path</text><text class="sub" x="126.0" y="84" text-anchor="middle">request and approval</text><text class="sub" x="126.0" y="101" text-anchor="middle">inside the tool</text><text class="sub" x="126.0" y="118" text-anchor="middle">needs everything up</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="126.0" y="166" text-anchor="middle">daily use</text></g><g class="badge"><circle cx="52" cy="32" r="11"/><text x="52" y="36">1</text></g><path class="flow" d="M 204 105 L 225 105" marker-end="url(#ladaw)"/><g class="node" style="--i:0.7"><rect x="227" y="30" width="152" height="150" rx="12"/><text class="ttl" x="303.0" y="62" text-anchor="middle">Emergency path</text><text class="sub" x="303.0" y="84" text-anchor="middle">vaulted account or</text><text class="sub" x="303.0" y="101" text-anchor="middle">self-approved request</text><text class="sub" x="303.0" y="118" text-anchor="middle">needs the tool up</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="303.0" y="166" text-anchor="middle">P-R15-11 · 13</text></g><g class="badge"><circle cx="229" cy="32" r="11"/><text x="229" y="36">2</text></g><path class="flow" d="M 381 105 L 402 105" marker-end="url(#ladaw)"/><g class="node" style="--i:1.4"><rect x="404" y="30" width="152" height="150" rx="12"/><text class="ttl" x="480.0" y="62" text-anchor="middle">Another copy</text><text class="sub" x="480.0" y="84" text-anchor="middle">second site, replica</text><text class="sub" x="480.0" y="101" text-anchor="middle">or offline cache</text><text class="sub" x="480.0" y="118" text-anchor="middle">fails with the first</text><text class="sub" x="480.0" y="135" text-anchor="middle">if cause is shared</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="480.0" y="166" text-anchor="middle">P-R15-04</text></g><g class="badge"><circle cx="406" cy="32" r="11"/><text x="406" y="36">3</text></g><path class="flow" d="M 558 105 L 579 105" marker-end="url(#ladaw)"/><g class="node" style="--i:2.1"><rect x="581" y="30" width="152" height="150" rx="12"/><text class="ttl" x="657.0" y="62" text-anchor="middle">Outside the tool</text><text class="sub" x="657.0" y="84" text-anchor="middle">sealed copy, two</text><text class="sub" x="657.0" y="101" text-anchor="middle">custodians, local and</text><text class="sub" x="657.0" y="118" text-anchor="middle">cloud-only accounts</text><text class="sub" x="657.0" y="135" text-anchor="middle">needs people, a safe</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="657.0" y="166" text-anchor="middle">P-R15-12</text></g><g class="badge"><circle cx="583" cy="32" r="11"/><text x="583" y="36">4</text></g><path class="flow" d="M 735 105 L 756 105" marker-end="url(#ladaw)"/><g class="node" style="--i:2.8"><rect x="758" y="30" width="152" height="150" rx="12"/><text class="ttl" x="834.0" y="62" text-anchor="middle">The vendor</text><text class="sub" x="834.0" y="84" text-anchor="middle">support procedure or</text><text class="sub" x="834.0" y="101" text-anchor="middle">recovery media</text><text class="sub" x="834.0" y="118" text-anchor="middle">needs a contract and</text><text class="sub" x="834.0" y="135" text-anchor="middle">proof of who you are</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="834.0" y="166" text-anchor="middle">not tested</text></g><g class="badge"><circle cx="760" cy="32" r="11"/><text x="760" y="36">5</text></g><rect class="logbar" x="30" y="210" width="900" height="76" rx="12"/><text class="ttl" x="480" y="236" text-anchor="middle">The rule: each rung must not depend on the one above it</text><text class="sub" x="480" y="256" text-anchor="middle">Ask of every rung: what has to be working for this to work?</text><text class="sub" x="480" y="274" text-anchor="middle">If the answer names the thing the rung is meant to cover, it is a normal path with a new name.</text><rect x="30" y="316" width="900" height="110" rx="12" fill="none" style="stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 6"/><text class="ttl" x="480" y="342" text-anchor="middle">Not tested yet</text><text class="sub" x="480" y="364" text-anchor="middle">any real product's behaviour on any rung</text><text class="sub" x="480" y="382" text-anchor="middle">both sites failing for the same cause, with the sealed copy as the way back</text><text class="sub" x="480" y="400" text-anchor="middle">the path of a remote user to the sealed copy</text><text class="svg-credit" x="951" y="452" text-anchor="end" font-size="15" fill="currentColor" opacity=".8" aria-hidden="true">roshantrivedi.co.in</text></svg><svg class="d-tall" viewBox="0 0 360 1285" role="img" aria-labelledby="ladtt ladtd"><title id="ladtt">The ladder of ways in, from the normal path to the vendor</title><desc id="ladtd">Five ways in, left to right, tried in order. One: the normal path, which needs everything working. Two: an emergency path inside the tool, a vaulted account or a self-approved request. Three: another copy of the tool, a second site, a replica or an offline cache, which fails together with the first if the cause is shared. Four: outside the tool, a sealed copy held by two custodians, local accounts and cloud-only accounts. Five: the vendor's support or recovery media. The rule under the boxes is that each rung must not depend on the one above it. Three things are marked as not tested yet.</desc><defs><marker id="ladat" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--c)"/></marker></defs><g class="node" style="--i:0.0"><rect x="30" y="10" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="42" text-anchor="middle">Normal path</text><text class="sub" x="180.0" y="64" text-anchor="middle">request and approval</text><text class="sub" x="180.0" y="81" text-anchor="middle">inside the tool</text><text class="sub" x="180.0" y="98" text-anchor="middle">needs everything up</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="142" text-anchor="middle">daily use</text></g><g class="badge"><circle cx="32" cy="12" r="11"/><text x="32" y="16">1</text></g><path class="flow" d="M 180 158 L 180 194" marker-end="url(#ladat)"/><g class="node" style="--i:0.7"><rect x="30" y="196" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="228" text-anchor="middle">Emergency path</text><text class="sub" x="180.0" y="250" text-anchor="middle">vaulted account or</text><text class="sub" x="180.0" y="267" text-anchor="middle">self-approved request</text><text class="sub" x="180.0" y="284" text-anchor="middle">needs the tool up</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="328" text-anchor="middle">P-R15-11 · 13</text></g><g class="badge"><circle cx="32" cy="198" r="11"/><text x="32" y="202">2</text></g><path class="flow" d="M 180 344 L 180 380" marker-end="url(#ladat)"/><g class="node" style="--i:1.4"><rect x="30" y="382" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="414" text-anchor="middle">Another copy</text><text class="sub" x="180.0" y="436" text-anchor="middle">second site, replica</text><text class="sub" x="180.0" y="453" text-anchor="middle">or offline cache</text><text class="sub" x="180.0" y="470" text-anchor="middle">fails with the first</text><text class="sub" x="180.0" y="487" text-anchor="middle">if cause is shared</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="514" text-anchor="middle">P-R15-04</text></g><g class="badge"><circle cx="32" cy="384" r="11"/><text x="32" y="388">3</text></g><path class="flow" d="M 180 530 L 180 566" marker-end="url(#ladat)"/><g class="node" style="--i:2.1"><rect x="30" y="568" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="600" text-anchor="middle">Outside the tool</text><text class="sub" x="180.0" y="622" text-anchor="middle">sealed copy, two</text><text class="sub" x="180.0" y="639" text-anchor="middle">custodians, local and</text><text class="sub" x="180.0" y="656" text-anchor="middle">cloud-only accounts</text><text class="sub" x="180.0" y="673" text-anchor="middle">needs people, a safe</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="700" text-anchor="middle">P-R15-12</text></g><g class="badge"><circle cx="32" cy="570" r="11"/><text x="32" y="574">4</text></g><path class="flow" d="M 180 716 L 180 752" marker-end="url(#ladat)"/><g class="node" style="--i:2.8"><rect x="30" y="754" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="786" text-anchor="middle">The vendor</text><text class="sub" x="180.0" y="808" text-anchor="middle">support procedure or</text><text class="sub" x="180.0" y="825" text-anchor="middle">recovery media</text><text class="sub" x="180.0" y="842" text-anchor="middle">needs a contract and</text><text class="sub" x="180.0" y="859" text-anchor="middle">proof of who you are</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="886" text-anchor="middle">not tested</text></g><g class="badge"><circle cx="32" cy="756" r="11"/><text x="32" y="760">5</text></g><rect class="logbar" x="30" y="940" width="300" height="157" rx="12"/><text class="ttl" x="180" y="968" text-anchor="middle">The rule: each rung must not</text><text class="ttl" x="180" y="986" text-anchor="middle">depend on the one above it</text><text class="sub" x="180" y="1010" text-anchor="middle">Ask of every rung: what has to be working</text><text class="sub" x="180" y="1027" text-anchor="middle">for this to work?</text><text class="sub" x="180" y="1044" text-anchor="middle">If the answer names the thing the rung is</text><text class="sub" x="180" y="1061" text-anchor="middle">meant to cover, it is a normal path with a</text><text class="sub" x="180" y="1078" text-anchor="middle">new name.</text><rect x="30" y="1127" width="300" height="118" rx="12" fill="none" style="stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 6"/><text class="ttl" x="180" y="1155" text-anchor="middle">Not tested yet</text><text class="sub" x="180" y="1177" text-anchor="middle">any real product's behaviour on any rung</text><text class="sub" x="180" y="1193" text-anchor="middle">both sites failing for the same cause, with</text><text class="sub" x="180" y="1209" text-anchor="middle">the sealed copy as the way back</text><text class="sub" x="180" y="1225" text-anchor="middle">the path of a remote user to the sealed copy</text><text class="svg-credit" x="353.4" y="1277" text-anchor="end" font-size="11" fill="currentColor" opacity=".8" aria-hidden="true">roshantrivedi.co.in</text></svg><figcaption>Read in one direction: try the first rung that does not depend on what has failed. The tags under the boxes are the lab cases that touched that rung, on made-up data. The dashed box shows what I have not tested.</figcaption></figure>

Here is what my labs touched, and it is a small part of the ladder. In P-R15-04, the tool that grants temporary admin rights is down for 2 hours. With no controls, [5 requests were blocked and 3 people used a shared admin password](/nhi-lab/#p-r15-04). With a second node, none were blocked. With the second node off and break-glass on, all 5 got in through break-glass, with 5 alerts and 5 reviews. The limit is in the lab's own audit: if both nodes fail for the same reason, such as a shared database, the second node does not help. That is rung 3 failing together with rung 2.

In [P-R15-12](/nhi-lab/#p-r15-12), a second holder for the sealed copy made one fault harmless without removing it. I cover that in my [earlier post on the drill](/writing/break-glass-architecture-tested/). Everything else on the ladder, including every real product, is untested by me.

*Why:* a ladder tells you which rung to reach for when the one above has failed, and it shows which rungs share a cause.

## Three people, and a fourth {#three-people}

I call the person who holds the key the custodian. You may hear the break-glass master instead, and "master" already means something else in one product: CyberArk's built-in vault user called Master, a recovery identity that signs in only with the Master CD that carries the Private Recovery Key. Keep the two meanings apart in your documents.

| Role | Before | During | After |
|---|---|---|---|
| The user, who needs in. Usually the on-call engineer. | Knows the trigger list, where the card is and who to call. Has done a drill. | Says why in plain words. Uses only the named path. Keeps notes. Shares nothing. | Returns it. Writes up the use in the ticket the same day. Expects questions. |
| The custodian, who holds the key | Is a named person with a backup. Has confirmed they can open the safe or reach the copy. Is removed when they move or leave. | Checks who is asking and why against the trigger list. Releases only by the agreed route. Never releases alone where the design asks for two. | Confirms the return and reseals. Hands over for rotation. Reports anything odd. |
| The administrator, who builds and tests it | Maps what each way depends on. Sets the alert and a heartbeat on its route. Excludes the account from policies that would block it. Runs the drills. | Is not the approver of their own use. Helps restore the main service. Does not edit the emergency account. | Rotates. Refreshes the sealed copy. Files the evidence. Fixes what the drill found. |
| The reviewer, who closes it | Is independent of the user and of whoever rotated. | Watches the alert. | Reviews every use against its ticket and its reason. Signs off or raises it. |

*Why:* when one person plays several of these roles in the same event, nobody is checking anyone. In my lab, the 5 uses in P-R15-04 each got an alert and a review. The review is the part that someone has to do by hand.

## When things are down {#when-things-are-down}

### The physical safe

A safe is rung 4. It works when nothing digital does, and it fails for dull reasons.

- Two custodians, so no one person opens it alone, and a copy in a second location. Microsoft's guidance, as I recorded it in my [case study](/case-studies/break-glass-access/), calls for fireproof safes in separate secure places, with combinations changed regularly and whenever someone with access leaves.
- Refresh the sealed copy after every rotation. A copy that still holds the old password is an easy way for this to fail, and my drill case tested the holders, not the freshness.
- Keep a card in the safe with what to try first, in what order and whom to call. It must not need any system to read.
- If you run a self-hosted vault, the media that restores it belongs in this plan. In my view the custodians for it should not all sit in the team that runs the vault, so no single group can both run and recover it.

### The person is remote

The safe is in an office and the engineer is at home, possibly with the remote-access service down as well. These are my options, all untested.

- A custodian on site releases the secret over a call. Verify the caller by ringing back on a number from an independent directory, not the number they give. Rotate when it returns.
- Remote hands at the data centre or office, with the same call-back check.
- A hardened jump host reachable by a path that does not use your normal remote-access service, such as a different provider. It is a dependency, so it goes on the ladder with its own "what has to work" line.
- A hardware key held by a duty manager, handed over in person. Slow, and sometimes right.

*Why:* the remote path is another thing that can be down. Treat it as a rung, and test it.

### Both PAM sites are down

1. Check that it is both, and find out why. If both depend on one database, one identity provider or one network link, the second site was never a second path.
2. Declare it, and page the custodian pair by a route that does not need the vault.
3. Open the smallest door that restores the normal path. For a self-hosted vault that is the recovery media and the account that restores the vault. For the systems whose outage is the emergency, it is their local accounts. Nothing more.
4. Restore the vault, then return to the normal path for everything else.
5. Rotate every secret that was opened, refresh the sealed copy, and have the reviewer go through every use.

*Why:* the glass exists to get the normal way back. Doing the day's work through it keeps the widest account open for longer.

### A tool linked to the PAM is down

Decide the answers before the day. A list for yours:

| If this is down | What breaks | Decide in advance |
|---|---|---|
| Ticketing | The ticket check cannot run | Allow the use, record "ticket pending", and have the reviewer chase it the same day. In my lab a ticket number was never checked against the ticket system, so 2 made-up numbers got through, so the reviewer has to check. |
| MFA or the identity provider | Sign-in to the emergency account fails | Give the account a sign-in method that does not depend on the daily provider. My case study records Microsoft's ask for a phishing-resistant method for these accounts. |
| Alerts, SIEM, email, chat | The use goes unseen | A second route, such as a phone call to a named person, and a heartbeat that tells you when the first route stops. In P-R15-12 a routing check found the dead route before the drill did. |
| Session recording or proxy | The use is not recorded | Decide whether to fail closed or open, and who may override. A proxy in the path can refuse everyone when it cannot reach its control plane, so ask your vendor what yours does. |
| Directory or DNS | Names and group lookups fail | Local accounts on the systems that must come back first. |
| Remote access or ZTNA | The user cannot reach anything | A second path, on the ladder. |
| Any AI helper you added | It stops, or it misleads | The process must work with it fully off. |

One hidden dependency in a vendor's own documentation is worth copying as a habit. Delinea's break-glass page says that if Secret Server is integrated with its platform and "Force Platform Only Login" is on, every login page redirects to the platform, including the page for local break-glass accounts. It tells you to confirm your emergency path while the platform is available. Do the equivalent test for your own product, on a day when nothing is wrong.

## Guardrails and approval {#guardrails-and-approval}

### Guardrails

The full list, with audit questions, is in the [case study](/case-studies/break-glass-access/). The ones I would not drop:

1. **An alert on every use, to more than one person, with a heartbeat on its route.** *Why:* in P-R15-11 the 2 a.m. use went unnoticed without it.
2. **Rotation when it returns, then a sign-in test with the new secret.** *Why:* in C-R16-C05, rotating on return stopped a pasted password from being reused. The alert only reported it.
3. **A reason, a ticket and an independent review for every use.** *Why:* in P-R15-13 four days of routine use went unnoticed, and with controls the 2 uses with no ticket were flagged.
4. **Two or more accounts, tied to no individual, no personal device and no personal MFA.** *Why:* this is Microsoft's guidance as I read it for the case study. An account tied to a person leaves when they do.
5. **An exclusion from sign-in blocking policies and stale-account clean-up, tested after every change to either.** *Why:* a policy meant to protect the tenant can lock out the account meant for the emergency.
6. **Logs kept outside the platform the account covers.** *Why:* the record of the use must survive the outage.
7. **A drill each quarter, recording what each check found on its own.** *Why:* in P-R15-12 I guessed the drill would find 2 faults and it found 1, because another control had made the second harmless.

### Approval

| Pattern | Good for | Weakness | Where I saw it |
|---|---|---|---|
| Review after, no approval before | Speed at any hour | Everything rests on the review | BeyondTrust's break-glass process notifies an Emergency Account Manager, who cannot approve or stop the checkout. Infisical lets the responder approve their own request, with a reason of at least 10 characters. |
| One approver | Business hours | Fails at night, or when the approver is the user's boss on leave | Common practice |
| Two-person release | The account that rebuilds the vault | The slowest | Delinea's August 2026 community post says Unlimited Vault Access needs dual control |
| A delay with a fast lane | Giving the alert time to matter | Mine, untested | Release after a short wait for one person, at once for two. The alert fires at the start of the wait. |

My view: match the approval to what the account can do and to how many minutes you can afford. A broad account with a 10 character reason and no review is a standing back door. In P-R15-11 the justification is checked to exist and not to be true, so the reviewer still has to read it.

## Who owns it {#who-owns-it}

My view, and your organisation decides:

| Role | Owns |
|---|---|
| Policy owner, one named senior role such as the head of security | The policy, the trigger list and any risk acceptance |
| Platform owner | The design, the dependency map, rotation, the drills and the evidence |
| Custodians, named people with backups | Holding the key and releasing it by the rules |
| Reviewer, independent of the user and of the person who rotated | Reviewing every use |
| Internal audit or GRC | Testing all of the above by sampling |

The account itself belongs to no individual. The custodian role does, and it moves with joiners, movers and leavers. Two ownership mistakes to avoid: a team alias nobody reads, and "the vendor looks after it".

## Four vendors, by what their own pages say {#four-vendors}

This is not a test of any product and it ranks no one. It records what each vendor's pages describe, with one dependency to check on your side.

| Vendor | What its pages describe | A dependency to check |
|---|---|---|
| CyberArk, now sold with the Idira name by Palo Alto Networks | Palo Alto Networks, which bought CyberArk earlier in 2026, launched Idira on 12 May 2026 using CyberArk's technology. The PAM Self-Hosted pages describe the built-in Master user for full recovery, which signs in only with the Master CD that holds the Private Recovery Key, and a non-interactive DR user that replicates safes to the Disaster Recovery Vault. For Privilege Cloud, a community article on the Palo Alto Networks site (page date 11-05-2026) says to keep one or more break-glass accounts in the cloud directory, so administrators can still sign in when your SAML or identity provider is down. It says to add them to the safes that hold what you need to rebuild, with List, Retrieve and Use as the minimum, to use them only with a ticket and approvals, and to protect the account with a split password: segments in separate physical places, or one half offline in the mobile app and the other half a separate one-time code. The product docs add a fallback order for the cloud access services: a break-glass credential in Privilege Cloud or PAM Self-Hosted, then offline access in the mobile app, with fewer than 20 accounts suggested. | The docs warn that rotating a credential makes the offline copy invalid without telling the user, and the user must have pulled it before the outage. The article says to avoid automatic password management during a DR event. Where the Master CD is, who can reach it, and when you last tested a restore. The failover steps for your version, which I did not confirm. |
| BeyondTrust | A blog post describes a break-glass checkout: a notice goes to an Emergency Account Manager, who cannot approve or stop it, the password has a time window, and a security administrator closes the account and sets up a replacement. The Password Safe 25.2 documentation describes Secrets Cache: if communication with Password Safe is lost, the last known good managed account credentials are served from the local cache, even if the request has expired. | Who holds the cache role, how fresh the cache is, and whether your support route works at night. A September 2024 community thread has one user reporting that the cache can hold the old password for a while after a rotation, so test it after a rotation. The blog post shows no date. |
| Delinea | The Secret Server documentation lists four options: export secrets to an encrypted file, Resilient Secrets, mobile offline caching, and agent offline operation with machine-specific one-time passwords. An August 2026 community post layers them, adds Unlimited Vault Access with dual control, and suggests a primary and a secondary emergency cloud admin account protected by the highest assurance sign-in, AAL3. | The "Force Platform Only Login" redirect above, and how stale the offline caches are. |
| StrongDM, part of Delinea since 5 March 2026 | Delinea's press page says it completed the acquisition on 5 March 2026. I could not confirm anything about break-glass on StrongDM's own pages: both addresses I had from search results now land on Delinea pages that do not cover it. | What the gateway does when its control plane cannot be reached, and whether a dedicated emergency admin exists and still signs in. Ask the vendor, because I have no confirmed answer. |

I read the Delinea documentation page, the Delinea community post, the Palo Alto Networks page, the BeyondTrust blog post and the Infisical page in full, read CyberArk's break-glass docs page and its Privilege Cloud DR article, and checked the BeyondTrust Secrets Cache page and Delinea's acquisition page for the statements I use. StrongDM is the gap. On 20 November both StrongDM addresses I had, the break-glass blog and the onboarding guide, landed on Delinea pages that do not contain what a search excerpt had shown me, so I removed those claims. Product names and ownership are moving this year, so confirm them before you quote any of this.

## Three cloud platforms {#cloud-platforms}

These are not PAM products. They are the places where the emergency account lives when your estate sits on a cloud tenant. Microsoft is covered in my [case study](/case-studies/break-glass-access/). Here are three more, from their own pages as I read them on 20 November.

| Platform | What its pages describe | A dependency to check |
| --- | --- | --- |
| AWS | The IAM Identity Center guide describes an emergency setup in which emergency users sign in by direct federation from your identity provider into IAM roles, so it still works if Identity Center or its Region is disrupted. It says this needs the IAM data plane and your external identity provider to be up, and points to AWS break-glass access if you do not want to depend on the provider. It says to build it before a disruption, because you cannot create the roles if your access to create them is also disrupted, and to test it. The DevOps guidance (AG.SAD.5) says break-glass roles and users should use hardware-based MFA and raise alerts when used, and be tied to incident response. | The first design still needs your external identity provider, so decide what you do if that is the thing that is down. I read the guide's landing page, not its setup sub-pages. |
| Okta | Okta's security team, in an article of 21 March 2024, says you may need a break-glass super administrator account, protected by policies that assume your trusted network or PAM tool is not available. It suggests limiting it by network location with a second or third range for redundancy, requiring MFA, for example one of several physical FIDO2 keys plus a machine-generated password, and treating any use as an alarm for the SOC. | The article is from 2024, so check Okta's current admin documentation. Whether your network ranges still include a place you can reach in an outage, and where the FIDO2 keys are kept. |
| Google Cloud | The guide (last updated 10 November 2026) says to create emergency access users in Cloud Identity or Google Workspace for each environment, with super admin rights, tied to no employee and exempt from SSO. It suggests two to five of them, in their own organisational unit, each with two or more FIDO security keys, credentials kept in physical safes in more than one place and not in a software password manager, an exclusion from context-aware access policies, and an alert on any activity from them. | It says not to automate password rotation for these accounts, because the automation would need super admin rights and become a target. Rotate by hand, which fits rotating on return in this guide, and keep the manual step on the checklist. |

The three agree with Microsoft on two points. The emergency account must not depend on the sign-in path it covers, and any use raises an alert. Only AWS says outright to test the setup, which is why the drill in this guide matters. They differ on where the secret lives. Google says physical controls and no software password manager. CyberArk's article offers both a physical split and a vaulted split. Each is defensible, and the choice is yours to make on the ladder, with the "what has to be working" question.

I did not read AWS's guidance on the root user. I tested none of these platforms.

## Business, governance and audit {#business-governance-audit}

### The business view

Break-glass buys time at the price of a standing risk, and the business has two questions only it can answer. What does an hour of the systems this restores cost, and who may declare an emergency? I have no figures to offer and I will not make any up.

One signal belongs to the business too. In P-R15-13 an account used for routine work over 4 days went unnoticed without controls. If the glass is used often, the normal path is broken, and fixing that is cheaper than accepting it.

### Governance

The policy says what counts as an emergency, who may use the glass and who may release it, for how long, how every use is reviewed, how often it is tested, and what happens when it fails a test. The measures I would track are below. The targets are yours to set, and I have none to offer.

- Uses per quarter, and how many had a ticket that exists.
- Time from use to an acknowledged alert, and from return to rotation.
- Custodians who confirmed they can reach the key this quarter.
- Drill findings, by check.

*Why:* a number without an owner and a target is decoration. These four each point at something someone can fix.

### Audit clarity

A guardrail with no evidence is a hope. Here is what I would expect an auditor to ask, and what to put in front of them.

| The auditor asks | Show |
|---|---|
| Who can use it, and who holds it? | The named custodian list, its last review date, and the match against leavers |
| Was every use justified and reviewed? | The use log, the ticket, and a sign-off by someone other than the user |
| Was the secret changed afterwards? | The rotation record and the sign-in test |
| Do you know it still works? | The drill report with each check's findings, and the validation date |
| Does an alert reach a person? | The route test and the heartbeat history |
| Is it excluded from blocking policies? | The policy export and the test after the last change |

I read the standards as a direction, not as a checklist: NIST SP 800-53 AC-2, AU-2 and AU-12, IA-5 and CP-2; ISO/IEC 27001:2022 A.8.2 and A.5.18; PCI DSS v4.0.1 requirement 8.2.2. The detail and sources are in the [case study](/case-studies/break-glass-access/).

### What regulators say

I checked one Indian regulator's own text. The Reserve Bank of India's Cyber Resilience and Digital Payment Security Controls for non-bank PSOs Master Directions, 2024, apply to non-bank payment system operators. As I read the page, they ask for controls over access privileges and how they are administered, access on a need-to-know and least-privilege basis, privileged accounts used with multi-factor authentication, tight monitoring and a rotation policy, and logs that identify who did what and are kept for at least five years.

I did not see a separate rule for break-glass in the lines the page returned. An emergency account is a privileged account, so those lines apply to it. That is my reading and not RBI's statement. If it is right, the use log and the reviews need to be kept as long as your other privileged logs.

I have not read RBI's rules for banks, or SEBI's Cybersecurity and Cyber Resilience Framework (circular of 20 August 2024), so I say nothing about them. Ask your compliance team which text applies to you, and ask your auditor how they read emergency accounts.

## How AI can help, and where it must not {#ai}

Everything in this section is my proposal. No lab case of mine has put an agent inside a break-glass event.

### Where it can help

- **Before:** keep the dependency map and the card current. Draft the drill scenario. Compare the custodian list with leavers, and compare rotation dates with sealed-copy dates, using read-only data.
- **During:** gather what is failing and what changed. Check the request against the trigger list. Draft the reason for the user to confirm and correct. Page the right people. Keep the timeline.
- **After:** assemble the review pack. Flag uses with no ticket or odd timing, as in P-R15-13. Draft the audit evidence.

### Where it must not

It must not hold, release, approve or use the credential. It must not approve its own proposals. It must not rotate or change the emergency account. Infisical's documentation draws the same line in one product: only users and groups can be break-glass users, so a machine identity or an AI agent cannot use break-glass.

### What keeps an agent from going on its own

A better prompt will not make a model obey. A prompt is a request. What holds is what the agent is able to do. This is the order I would build it in.

<figure class="diagram-card" style="--c:var(--pal-cyan);margin-top:14px"><button type="button" class="anim-toggle" aria-pressed="false">Pause animation</button><svg class="d-wide" viewBox="0 0 960 460" role="img" aria-labelledby="agtwt agtwd"><title id="agtwt">Where an AI agent sits in a break-glass event</title><desc id="agtwd">Where an AI agent sits in a break-glass event, left to right. Signals such as alerts, logs, tickets and chat are treated as untrusted text. The agent has read-only tools, its own identity and a named human owner, and it gathers context and drafts. A policy gate outside the model checks every call against an allow-list and logs it. Two people approve in their own channel, not in the agent's chat. A human then uses the access, time-boxed, recorded and rotated on return. Under the boxes: the agent never holds, releases, approves or uses the credential, and one action revokes its identity. Everything in the figure is a proposal and has not been tested.</desc><defs><marker id="agtaw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--c)"/></marker></defs><g class="node" style="--i:0.0"><rect x="50" y="30" width="152" height="150" rx="12"/><text class="ttl" x="126.0" y="62" text-anchor="middle">Signals</text><text class="sub" x="126.0" y="84" text-anchor="middle">alerts, logs, tickets,</text><text class="sub" x="126.0" y="101" text-anchor="middle">chat. All untrusted</text><text class="sub" x="126.0" y="118" text-anchor="middle">text, never orders</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="126.0" y="166" text-anchor="middle">input</text></g><g class="badge"><circle cx="52" cy="32" r="11"/><text x="52" y="36">1</text></g><path class="flow" d="M 204 105 L 225 105" marker-end="url(#agtaw)"/><g class="node" style="--i:0.7"><rect x="227" y="30" width="152" height="150" rx="12"/><text class="ttl" x="303.0" y="62" text-anchor="middle">Agent</text><text class="sub" x="303.0" y="84" text-anchor="middle">read-only tools,</text><text class="sub" x="303.0" y="101" text-anchor="middle">its own identity and</text><text class="sub" x="303.0" y="118" text-anchor="middle">a named human owner</text><text class="sub" x="303.0" y="135" text-anchor="middle">gathers and drafts</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="303.0" y="166" text-anchor="middle">proposes</text></g><g class="badge"><circle cx="229" cy="32" r="11"/><text x="229" y="36">2</text></g><path class="flow" d="M 381 105 L 402 105" marker-end="url(#agtaw)"/><g class="node" style="--i:1.4"><rect x="404" y="30" width="152" height="150" rx="12"/><text class="ttl" x="480.0" y="62" text-anchor="middle">Policy gate</text><text class="sub" x="480.0" y="84" text-anchor="middle">allow-list of calls,</text><text class="sub" x="480.0" y="101" text-anchor="middle">enforced outside the</text><text class="sub" x="480.0" y="118" text-anchor="middle">model and logged</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="480.0" y="166" text-anchor="middle">enforces</text></g><g class="badge"><circle cx="406" cy="32" r="11"/><text x="406" y="36">3</text></g><path class="flow" d="M 558 105 L 579 105" marker-end="url(#agtaw)"/><g class="node" style="--i:2.1"><rect x="581" y="30" width="152" height="150" rx="12"/><text class="ttl" x="657.0" y="62" text-anchor="middle">Two people</text><text class="sub" x="657.0" y="84" text-anchor="middle">approve in their own</text><text class="sub" x="657.0" y="101" text-anchor="middle">channel, not in the</text><text class="sub" x="657.0" y="118" text-anchor="middle">agent's chat</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="657.0" y="166" text-anchor="middle">decides</text></g><g class="badge"><circle cx="583" cy="32" r="11"/><text x="583" y="36">4</text></g><path class="flow" d="M 735 105 L 756 105" marker-end="url(#agtaw)"/><g class="node" style="--i:2.8"><rect x="758" y="30" width="152" height="150" rx="12"/><text class="ttl" x="834.0" y="62" text-anchor="middle">A human acts</text><text class="sub" x="834.0" y="84" text-anchor="middle">time-boxed, recorded,</text><text class="sub" x="834.0" y="101" text-anchor="middle">rotated on return</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="834.0" y="166" text-anchor="middle">uses</text></g><g class="badge"><circle cx="760" cy="32" r="11"/><text x="760" y="36">5</text></g><rect class="logbar" x="30" y="210" width="900" height="76" rx="12"/><text class="ttl" x="480" y="236" text-anchor="middle">The agent never holds, releases, approves or uses the credential</text><text class="sub" x="480" y="256" text-anchor="middle">One action revokes the agent's identity, and that action works with the agent platform down.</text><rect x="30" y="316" width="900" height="110" rx="12" fill="none" style="stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 6"/><text class="ttl" x="480" y="342" text-anchor="middle">Not tested yet</text><text class="sub" x="480" y="364" text-anchor="middle">every control here, a proposal</text><text class="sub" x="480" y="382" text-anchor="middle">an agent inside a break-glass event, in any lab case</text><text class="sub" x="480" y="400" text-anchor="middle">planted instructions in logs and tickets, to see whether the agent refuses them</text><text class="svg-credit" x="951" y="452" text-anchor="end" font-size="15" fill="currentColor" opacity=".8" aria-hidden="true">roshantrivedi.co.in</text></svg><svg class="d-tall" viewBox="0 0 360 1285" role="img" aria-labelledby="agttt agttd"><title id="agttt">Where an AI agent sits in a break-glass event</title><desc id="agttd">Where an AI agent sits in a break-glass event, left to right. Signals such as alerts, logs, tickets and chat are treated as untrusted text. The agent has read-only tools, its own identity and a named human owner, and it gathers context and drafts. A policy gate outside the model checks every call against an allow-list and logs it. Two people approve in their own channel, not in the agent's chat. A human then uses the access, time-boxed, recorded and rotated on return. Under the boxes: the agent never holds, releases, approves or uses the credential, and one action revokes its identity. Everything in the figure is a proposal and has not been tested.</desc><defs><marker id="agtat" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--c)"/></marker></defs><g class="node" style="--i:0.0"><rect x="30" y="10" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="42" text-anchor="middle">Signals</text><text class="sub" x="180.0" y="64" text-anchor="middle">alerts, logs, tickets,</text><text class="sub" x="180.0" y="81" text-anchor="middle">chat. All untrusted</text><text class="sub" x="180.0" y="98" text-anchor="middle">text, never orders</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="142" text-anchor="middle">input</text></g><g class="badge"><circle cx="32" cy="12" r="11"/><text x="32" y="16">1</text></g><path class="flow" d="M 180 158 L 180 194" marker-end="url(#agtat)"/><g class="node" style="--i:0.7"><rect x="30" y="196" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="228" text-anchor="middle">Agent</text><text class="sub" x="180.0" y="250" text-anchor="middle">read-only tools,</text><text class="sub" x="180.0" y="267" text-anchor="middle">its own identity and</text><text class="sub" x="180.0" y="284" text-anchor="middle">a named human owner</text><text class="sub" x="180.0" y="301" text-anchor="middle">gathers and drafts</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="328" text-anchor="middle">proposes</text></g><g class="badge"><circle cx="32" cy="198" r="11"/><text x="32" y="202">2</text></g><path class="flow" d="M 180 344 L 180 380" marker-end="url(#agtat)"/><g class="node" style="--i:1.4"><rect x="30" y="382" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="414" text-anchor="middle">Policy gate</text><text class="sub" x="180.0" y="436" text-anchor="middle">allow-list of calls,</text><text class="sub" x="180.0" y="453" text-anchor="middle">enforced outside the</text><text class="sub" x="180.0" y="470" text-anchor="middle">model and logged</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="514" text-anchor="middle">enforces</text></g><g class="badge"><circle cx="32" cy="384" r="11"/><text x="32" y="388">3</text></g><path class="flow" d="M 180 530 L 180 566" marker-end="url(#agtat)"/><g class="node" style="--i:2.1"><rect x="30" y="568" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="600" text-anchor="middle">Two people</text><text class="sub" x="180.0" y="622" text-anchor="middle">approve in their own</text><text class="sub" x="180.0" y="639" text-anchor="middle">channel, not in the</text><text class="sub" x="180.0" y="656" text-anchor="middle">agent's chat</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="700" text-anchor="middle">decides</text></g><g class="badge"><circle cx="32" cy="570" r="11"/><text x="32" y="574">4</text></g><path class="flow" d="M 180 716 L 180 752" marker-end="url(#agtat)"/><g class="node" style="--i:2.8"><rect x="30" y="754" width="300" height="146" rx="12"/><text class="ttl" x="180.0" y="786" text-anchor="middle">A human acts</text><text class="sub" x="180.0" y="808" text-anchor="middle">time-boxed, recorded,</text><text class="sub" x="180.0" y="825" text-anchor="middle">rotated on return</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="886" text-anchor="middle">uses</text></g><g class="badge"><circle cx="32" cy="756" r="11"/><text x="32" y="760">5</text></g><rect class="logbar" x="30" y="940" width="300" height="141" rx="12"/><text class="ttl" x="180" y="968" text-anchor="middle">The agent never holds,</text><text class="ttl" x="180" y="986" text-anchor="middle">releases, approves or uses the</text><text class="ttl" x="180" y="1004" text-anchor="middle">credential</text><text class="sub" x="180" y="1028" text-anchor="middle">One action revokes the agent's identity, and</text><text class="sub" x="180" y="1045" text-anchor="middle">that action works with the agent platform</text><text class="sub" x="180" y="1062" text-anchor="middle">down.</text><rect x="30" y="1111" width="300" height="134" rx="12" fill="none" style="stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 6"/><text class="ttl" x="180" y="1139" text-anchor="middle">Not tested yet</text><text class="sub" x="180" y="1161" text-anchor="middle">every control here, a proposal</text><text class="sub" x="180" y="1177" text-anchor="middle">an agent inside a break-glass event, in any</text><text class="sub" x="180" y="1193" text-anchor="middle">lab case</text><text class="sub" x="180" y="1209" text-anchor="middle">planted instructions in logs and tickets, to</text><text class="sub" x="180" y="1225" text-anchor="middle">see whether the agent refuses them</text><text class="svg-credit" x="353.4" y="1277" text-anchor="end" font-size="11" fill="currentColor" opacity=".8" aria-hidden="true">roshantrivedi.co.in</text></svg><figcaption>Read in one direction. The agent proposes and a policy gate it cannot change enforces. People decide, and a person uses the access. My design, not a tested result.</figcaption></figure>

1. **Its own identity and a named human owner.** *Why:* NIST's NCCoE concept paper of February 2026 is about identification and authorization controls for AI agents, with auditing and non-repudiation among its questions, and a log is only useful if it says which one acted.
2. **Least agency: read-only tools by default, and no break-glass operations among them.** *Why:* OWASP's 2026 Top 10 for Agentic Applications, as Auth0 summarises it, calls this least agency, and the safest action is the one the agent cannot call.
3. **A policy gate outside the model.** *Why:* every call is checked against an allow-list by code the model cannot edit or talk around.
4. **People approve in their own channel.** *Why:* an approval typed into the agent's chat can be forged by the agent, or by whatever it has read.
5. **Everything it reads is untrusted.** *Why:* during an incident the agent reads logs, tickets and chat that someone may have shaped. Auth0's summary of OWASP's list puts agent goal hijack first, and the NCCoE paper asks about controls against prompt injection.
6. **Two agents are not two people.** *Why:* separation of duties needs separate accountable humans.
7. **Short-lived, task-scoped tokens, a step limit and a time box.** *Why:* the damage from a hijack is capped by what it was given.
8. **Logs kept outside the agent platform, and a kill switch that works without it.** *Why:* you need to stop it and to reconstruct what it did, even if it is the thing that failed.
9. **A drill for the agent, with planted instructions in the logs.** *Why:* record what each control caught on its own. The lesson of P-R15-12 applies: a clean pass can hide a fault that another control is covering.

And the process must still work with the agent switched off. If it cannot, the agent is on the dependency list, and it belongs on the ladder.

## Out of the box {#out-of-the-box}

You asked for a seamless process. The most seamless break-glass is the one people already know how to use, so I would start by tying it to the incident process they already follow. These are my ideas, and none is tested.

1. **Let the incident open the glass.** Declaring a major incident gives the on-call a time-boxed emergency role, starts the alert and schedules the rotation. Nobody hunts for a password, and the record writes itself. The incident tool becomes a dependency, so keep the sealed rung underneath it.
2. **Glass in tiers.** Look first with a read-only role, then roll back with a configuration role, then full admin only if needed. Each tier has its own credential and a shorter time limit. Most emergencies should end early, and the widest account stays nearly unused.
3. **A twin for the drill.** An identical account with no privileges, used for drills so the real one is never exercised. It proves routing and holders. It does not prove the real account works, so keep the scheduled validation too.
4. **A delay with a fast lane**, as in the approval table.
5. **Rotation as the default.** Check-in rotates, and re-sealing refreshes the sealed copy in the same step. Drill the loop.
6. **A game day that cuts a dependency for real**, in a test environment. Turn off the alert route and see who notices. In my lab the routing check found a dead route before the drill ran.

## Start here {#start-here}

1. Write down, for each way you use, what has to be working for it to work.
2. Send a test alert and see who receives it.
3. Ask each custodian whether they can reach the key this week.
4. Check that the sealed copy matches the last rotation.
5. Test a sign-in to the emergency account after the last policy change.
6. Run one drill, and record what each check found by itself.

## What I have and have not tested

I tested six cases on small models with made-up data, and the limits are in the lab's audit. I tested no real product. The vendor rows come from each vendor's own pages as I read them on 20 November, except StrongDM, where I could not confirm anything. Check them against the current documentation. The three platform rows and the regulator paragraph come from the pages named in Sources, which I read on 20 November, and I tested none of them. The AI controls and the ideas in the last section are untested proposals.

## Sources {#sources}

Read on 20 November 2026 unless noted.

- [Delinea: Break Glass Scenarios (Secret Server documentation)](https://docs.delinea.com/online-help/secret-server/backup-and-disaster-recovery/break-glass/index.htm)
- [Delinea community: Establish the right break-glass emergency access for your situation](https://community.delinea.com/best-practices-for-maturing-your-security-program-56/establish-the-right-break-glass-emergency-access-for-your-situation-865) (posted 4 August 2026)
- [Palo Alto Networks: Built-In Users and Groups (PAM Self-Hosted)](https://live.paloaltonetworks.com/t5/pam-self-hosted-articles/built-in-users-and-groups/ta-p/1427665) (no date shown)
- [SiliconANGLE: Idira launches as Palo Alto Networks extends CyberArk tech to machine and agentic identities](https://siliconangle.com/2026/05/12/idira-launches-palo-alto-networks-extends-cyberark-tech-machine-agentic-identities/) (12 May 2026)
- [BeyondTrust: Using a Break Glass Process to Provide Security for Privileged Accounts](https://www.beyondtrust.com/blog/entry/provide-security-privileged-accounts-with-break-glass-process) (no date shown)
- [BeyondTrust: Secrets Cache (Password Safe 25.2 documentation)](https://docs.beyondtrust.com/bips/v25.2/docs/ps-cache) (page last modified 18 December 2025)
- [BeyondTrust community: Secrets Cache with Password Safe for DR and break-glass scenarios](https://beekeepers.beyondtrust.com/general-40/are-you-taking-advantage-of-secrets-cache-with-password-safe-for-dr-break-glass-scenarios-5477) (thread posted 12 September 2024; search excerpt)
- [Delinea: completes StrongDM acquisition](https://delinea.com/news/delinea-acquires-strongdm-to-secure-ai-with-continuous-authorization) (5 March 2026)
- [CyberArk (Idira) docs: Break-glass access best practices](https://docs.cyberark.com/manage/latest/en/sca/dpaforcloud/breakglass/) (no date shown)
- [Palo Alto Networks community: Disaster Recovery (DR) Planning For Idira Privilege Cloud](https://live.paloaltonetworks.com/t5/idira-success-blogs/disaster-recovery-dr-planning-for-idira-privilege-cloud/ba-p/1430445) (page date 11-05-2026)
- [AWS: Set up emergency access to the AWS Management Console (IAM Identity Center)](https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access.html) and [AWS DevOps guidance AG.SAD.5: Implement break-glass procedures](https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/ag.sad.5-implement-break-glass-procedures.html)
- [Okta Security: Protecting Administrative Sessions in Okta](https://sec.okta.com/articles/protectingadminsessions/) (21 March 2024)
- [Google Cloud: Ensure continuous access to Google Cloud](https://docs.cloud.google.com/docs/security/best-practices-continuous-access-to-google-cloud) (last updated 10 November 2026)
- [Reserve Bank of India: Cyber Resilience and Digital Payment Security Controls for non-bank PSOs, Master Directions 2024](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12715)
- [SEBI: Cybersecurity and Cyber Resilience Framework (CSCRF) circular, 20 August 2024](https://www.sebi.gov.in/legal/circulars/aug-2024/cybersecurity-and-cyber-resilience-framework-cscrf-for-sebi-regulated-entities-res-_85964.html) (circular page only; I did not read the framework text)
- [Infisical: Break-glass access](https://infisical.com/docs/documentation/platform/pam/access-requests/break-glass.md)
- [NIST CSRC: Accelerating the Adoption of Software and AI Agent Identity and Authorization](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd) (draft concept paper published 5 February 2026, comments closed 2 April 2026; I read the page text, not the PDF)
- [OWASP GenAI Security Project: Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (the official page; I have not read the list itself)
- [Auth0: Lessons from OWASP Top 10 for Agentic Applications](https://auth0.com/blog/owasp-top-10-agentic-applications-lessons/) (search excerpt only; my source for "least agency" and goal hijack as the first risk)
- [Microsoft Learn: Manage emergency access admin accounts in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access) (page last updated 5 June 2026; re-read on 20 November 2026)
- My own: the [break-glass case study](/case-studies/break-glass-access/), the [machine identity lab](/nhi-lab/) with its [audit data](/nhi-lab/audit/), and the [post on the drill](/writing/break-glass-architecture-tested/).

If your break-glass works differently from anything here, or I have a vendor detail wrong, I would like to hear it. You can [get in touch here](/contact/).
