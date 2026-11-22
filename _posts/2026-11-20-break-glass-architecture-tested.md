---
title: "A Break-Glass Architecture, Tested: Six Cases and One Wrong Guess About the Drill"
layout: post
bg: post-plan
motif: grid
seo_title: "Break-Glass Architecture, Tested: What the Drill Missed"
date: 2026-11-20 10:00:00 +0530
author: Roshan Trivedi
tags: [break-glass, emergency-access, privileged-access, pam, security-testing]
diagrams: true
share_title: "Break-glass access, tested: six cases, one wrong guess"
share_label: "Article · Privileged access"
share_accent: green
description: "Six tested cases on break-glass access. Five matched my guess. The drill found one fault, not two, because another control made the second one harmless."
---

# A Break-Glass Architecture, Tested: Six Cases and One Wrong Guess About the Drill

*Filed under: Privileged access · Emergency access*

*Independent work on my own time. All data is made up. Nothing here describes any employer's or client's systems.*

## The short version

A break-glass account is the way back in when normal access has failed. The identity provider is down, or the approval tool is, or the vault cannot be reached. Many teams picture it as a password in an envelope. The password is the small part. Whether it works depends on who gets the alert, who holds the sealed copy, and what has to happen after someone uses it.

I tested six cases on this across two of my labs, all on small models with made-up data. I wrote my guess for each one before any code ran. Five matched. One did not: the quarterly drill. I guessed it would find two planted faults, and it found one. It passed all four steps on its first run while the second fault was still in place, because another control had made that fault harmless without removing it.

## What break-glass is, in plain words

It is a key kept for the day the normal door system fails. It exists so that work can carry on. It is also a standing risk, because whoever holds it can go around every control you have built.

So the design has to do three things together. It has to work when the systems around it are down. It has to be loud when it is used. And every use has to be closed out afterwards, with a reason, a review and a new secret. The rest of this post follows those three.

## The architecture, in one picture

<figure class="diagram-card" style="--c:#7df2d0;margin-top:14px"><button type="button" class="anim-toggle" aria-pressed="false">Pause animation</button><svg class="d-wide" viewBox="0 0 960 460" role="img" aria-labelledby="ba1t ba1d"><title id="ba1t">Break-glass architecture, with the lab case that tested each part</title><desc id="ba1d">One use of a break-glass account, left to right: get in through an approval path with a second node or through a sealed copy opened by two people; use it with a named person, a reason and an alert on every use; close out with a ticket, a justification, an independent review and rotation when the password returns; then it is dormant again with a new secret and a refreshed sealed copy. A drill every quarter checks the route. Three parts are marked as not tested yet.</desc><defs><marker id="bgaw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--c)"/></marker></defs><g class="node" style="--i:0.0"><rect x="30" y="30" width="180" height="130" rx="12"/><text class="ttl" x="120.0" y="62" text-anchor="middle">Get in</text><text class="sub" x="120.0" y="84" text-anchor="middle">approval path with a</text><text class="sub" x="120.0" y="101" text-anchor="middle">second node, or a sealed</text><text class="sub" x="120.0" y="118" text-anchor="middle">copy two people open</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="120.0" y="146" text-anchor="middle">P-R15-04</text></g><g class="badge"><circle cx="32" cy="32" r="11"/><text x="32" y="36">1</text></g><path class="flow" d="M 212 95 L 268 95" marker-end="url(#bgaw)"/><g class="node" style="--i:0.7"><rect x="270" y="30" width="180" height="130" rx="12"/><text class="ttl" x="360.0" y="62" text-anchor="middle">Use</text><text class="sub" x="360.0" y="84" text-anchor="middle">a named person, a reason,</text><text class="sub" x="360.0" y="101" text-anchor="middle">an alert on every use,</text><text class="sub" x="360.0" y="118" text-anchor="middle">the alert route checked</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="360.0" y="146" text-anchor="middle">P-R15-11 · C10</text></g><g class="badge"><circle cx="272" cy="32" r="11"/><text x="272" y="36">2</text></g><path class="flow" d="M 452 95 L 508 95" marker-end="url(#bgaw)"/><g class="node" style="--i:1.4"><rect x="510" y="30" width="180" height="130" rx="12"/><text class="ttl" x="600.0" y="62" text-anchor="middle">Close out</text><text class="sub" x="600.0" y="84" text-anchor="middle">ticket and justification,</text><text class="sub" x="600.0" y="101" text-anchor="middle">independent review,</text><text class="sub" x="600.0" y="118" text-anchor="middle">rotate when it returns</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="600.0" y="146" text-anchor="middle">P-R15-13 · C-R16-C05</text></g><g class="badge"><circle cx="512" cy="32" r="11"/><text x="512" y="36">3</text></g><path class="flow" d="M 692 95 L 748 95" marker-end="url(#bgaw)"/><g class="node" style="--i:2.1"><rect x="750" y="30" width="180" height="130" rx="12"/><text class="ttl" x="840.0" y="62" text-anchor="middle">Dormant again</text><text class="sub" x="840.0" y="84" text-anchor="middle">new secret set, sealed</text><text class="sub" x="840.0" y="101" text-anchor="middle">copy refreshed, back</text><text class="sub" x="840.0" y="118" text-anchor="middle">in the vault</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="840.0" y="146" text-anchor="middle">P-R15-11</text></g><g class="badge"><circle cx="752" cy="32" r="11"/><text x="752" y="36">4</text></g><rect class="logbar" x="30" y="196" width="900" height="76" rx="12"/><text class="ttl" x="480" y="222" text-anchor="middle">Drill every quarter and after changes</text><text class="sub" x="480" y="242" text-anchor="middle">Three separate checks: alert routing, two holders for the sealed copy, then the drill itself</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="480" y="261" text-anchor="middle">P-R15-12 · I guessed the drill would find 2 faults. It found 1.</text><rect x="30" y="302" width="900" height="124" rx="12" fill="none" style="stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 6"/><text class="ttl" x="480" y="330" text-anchor="middle">Not tested yet</text><text class="sub" x="480" y="354" text-anchor="middle">a sealed copy kept inside the system that is down</text><text class="sub" x="480" y="372" text-anchor="middle">the account's exclusion from sign-in blocking policies</text><text class="sub" x="480" y="390" text-anchor="middle">an alert sent through the service that has failed</text><text class="sub" x="480" y="412" text-anchor="middle">Everything tested is a small model on made-up data. No real product was tested.</text><text class="svg-credit" x="951" y="452" text-anchor="end" font-size="15" fill="currentColor" opacity=".8" aria-hidden="true">roshantrivedi.co.in</text></svg><svg class="d-tall" viewBox="0 0 360 1010" role="img" aria-labelledby="ba2t ba2d"><title id="ba2t">Break-glass architecture, with the lab case that tested each part</title><desc id="ba2d">One use of a break-glass account, top to bottom: get in through an approval path with a second node or through a sealed copy opened by two people; use it with a named person, a reason and an alert on every use; close out with a ticket, a justification, an independent review and rotation when the password returns; then it is dormant again with a new secret and a refreshed sealed copy. A drill every quarter checks the route. Three parts are marked as not tested yet.</desc><defs><marker id="bgat" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" style="fill:var(--c)"/></marker></defs><g class="node" style="--i:0.0"><rect x="30" y="10" width="300" height="130" rx="12"/><text class="ttl" x="180.0" y="42" text-anchor="middle">Get in</text><text class="sub" x="180.0" y="64" text-anchor="middle">approval path with a</text><text class="sub" x="180.0" y="81" text-anchor="middle">second node, or a sealed</text><text class="sub" x="180.0" y="98" text-anchor="middle">copy two people open</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="126" text-anchor="middle">P-R15-04</text></g><g class="badge"><circle cx="32" cy="12" r="11"/><text x="32" y="16">1</text></g><path class="flow" d="M 180 142 L 180 176" marker-end="url(#bgat)"/><g class="node" style="--i:0.7"><rect x="30" y="178" width="300" height="130" rx="12"/><text class="ttl" x="180.0" y="210" text-anchor="middle">Use</text><text class="sub" x="180.0" y="232" text-anchor="middle">a named person, a reason,</text><text class="sub" x="180.0" y="249" text-anchor="middle">an alert on every use,</text><text class="sub" x="180.0" y="266" text-anchor="middle">the alert route checked</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="294" text-anchor="middle">P-R15-11 · C10</text></g><g class="badge"><circle cx="32" cy="180" r="11"/><text x="32" y="184">2</text></g><path class="flow" d="M 180 310 L 180 344" marker-end="url(#bgat)"/><g class="node" style="--i:1.4"><rect x="30" y="346" width="300" height="130" rx="12"/><text class="ttl" x="180.0" y="378" text-anchor="middle">Close out</text><text class="sub" x="180.0" y="400" text-anchor="middle">ticket and justification,</text><text class="sub" x="180.0" y="417" text-anchor="middle">independent review,</text><text class="sub" x="180.0" y="434" text-anchor="middle">rotate when it returns</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="462" text-anchor="middle">P-R15-13 · C-R16-C05</text></g><g class="badge"><circle cx="32" cy="348" r="11"/><text x="32" y="352">3</text></g><path class="flow" d="M 180 478 L 180 512" marker-end="url(#bgat)"/><g class="node" style="--i:2.1"><rect x="30" y="514" width="300" height="130" rx="12"/><text class="ttl" x="180.0" y="546" text-anchor="middle">Dormant again</text><text class="sub" x="180.0" y="568" text-anchor="middle">new secret set, sealed</text><text class="sub" x="180.0" y="585" text-anchor="middle">copy refreshed, back</text><text class="sub" x="180.0" y="602" text-anchor="middle">in the vault</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:11px" x="180.0" y="630" text-anchor="middle">P-R15-11</text></g><g class="badge"><circle cx="32" cy="516" r="11"/><text x="32" y="520">4</text></g><rect class="logbar" x="30" y="684" width="300" height="110" rx="12"/><text class="ttl" x="180" y="712" text-anchor="middle">Drill every quarter</text><text class="sub" x="180" y="734" text-anchor="middle">Three separate checks: alert routing,</text><text class="sub" x="180" y="751" text-anchor="middle">two holders for the sealed copy,</text><text class="sub" x="180" y="768" text-anchor="middle">then the drill itself</text><text class="sub" style="fill:var(--c);font-family:var(--mono);font-size:10.5px" x="180" y="786" text-anchor="middle">P-R15-12 · guessed 2 faults, found 1</text><rect x="30" y="824" width="300" height="146" rx="12" fill="none" style="stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 6"/><text class="ttl" x="180" y="852" text-anchor="middle">Not tested yet</text><text class="sub" x="180" y="874" text-anchor="middle">a sealed copy kept inside the</text><text class="sub" x="180" y="889" text-anchor="middle">system that is down</text><text class="sub" x="180" y="904" text-anchor="middle">the account's exclusion from</text><text class="sub" x="180" y="919" text-anchor="middle">sign-in blocking policies</text><text class="sub" x="180" y="934" text-anchor="middle">an alert sent through the</text><text class="sub" x="180" y="949" text-anchor="middle">service that has failed</text><text class="svg-credit" x="353.4" y="1002" text-anchor="end" font-size="11" fill="currentColor" opacity=".8" aria-hidden="true">roshantrivedi.co.in</text></svg><figcaption>One use of the account, read in one direction. The case numbers under each box are the lab cases that tested that part, and the bar and dashed box under them show the drill and what I have not tested. Illustrative, drawn from my own made-up lab data.</figcaption></figure>

Under each box is the lab case that tested that part. The full design, with its steps and guardrails, is in my [break-glass case study](/case-studies/break-glass-access/). This post covers what happened when I tested it.

## What each part did when I tested it

Each case runs once with the controls off and once with them on.

| Part | Case | Without the controls | With the controls |
|---|---|---|---|
| Get in | [P-R15-04](/nhi-lab/#p-r15-04) | The tool that grants temporary admin rights is down for 2 hours. All 5 requests are blocked and 3 people use a shared admin password. | A second node takes over and nobody needs the fallback. With the second node off and break-glass on, all 5 get in through break-glass, with 5 alerts and 5 reviews. |
| Use | [P-R15-11](/nhi-lab/#p-r15-11) | The account is used at 2 a.m. Nobody notices and the password stays the same. | An alert fires and the password is rotated. |
| Use | [C10](/ai-governance-lab/round-10/) | The same question in my older AI governance lab: no alert and no password change afterwards. | An alert within a minute and a new password at check-in. |
| Close out | [P-R15-13](/nhi-lab/#p-r15-13) | The account is used for routine work over 4 days. No one notices. | The 2 uses with no ticket are flagged. |
| Return | [C-R16-C05](/nhi-lab/#c-r16-c05) | The password is pasted in a chat and reused with no emergency. Nobody notices. | Rotating on return stops the reuse. The alert only reports it. |
| Drill | [P-R15-12](/nhi-lab/#p-r15-12) | No drill, so 0 faults found. | The routing check finds 1 fault. The second holder hides the other. |

The two controls in the C-R16-C05 row do different jobs. The alert tells you the password was used. Rotation is what stops the next use.

## The one I got wrong: the drill

The case is a quarterly drill with four steps. The alert fires, an on-call person acknowledges within 15 minutes, the sealed copy is found, and the password is rotated afterwards. I planted two faults. The alert still goes to a person who left, and the sealed copy is held by a person on leave. There were three controls: a routing check against the current on-call list, a second holder for the sealed copy, and the drill itself.

I guessed that with all three on, the drill would find both faults and fix both. I also guessed that without the drill, nothing would find a fault. Both guesses were wrong.

- **All three on:** the routing check found the alert fault before the drill ran. The second holder meant the sealed copy step passed, so nothing showed that the first holder was away. The result was 1 fault found, all 4 steps passing first time, and 1 fault still there.
- **Drill off:** the routing check still found 1 fault. The drill was not the only thing that finds faults.
- **Second holder off:** the drill found the sealed copy fault, so both came up.

The second holder is a good control, and it did its job. It also hid a fault that the drill would otherwise have shown. The person on leave is still named as a holder.

My mistake was to treat the controls as if each one worked alone. When one control covers for another, a clean result stops being proof that nothing is wrong. If you run drills, record what each check found on its own as well as whether the drill passed.

*Why:* a pass can mean the route is sound, or it can mean one control is covering a fault you have not fixed.

## Where the controls stopped

These are limits of the models I wrote, recorded in the lab's audit. They are not findings about any product.

- **P-R15-04:** if both nodes fail for the same reason, such as a shared database, the second node does not help and the fallback is used even with it.
- **P-R15-11:** the justification is checked to exist. It is not checked to be true.
- **P-R15-13:** a ticket number is not checked against the ticket system, so 2 uses with made-up ticket numbers were not caught.
- **P-R15-12:** an announced drill probably runs better than a real night. My model has no people in it, so it cannot show that.

## What I have not tested

- **A sealed copy kept inside the system that is down.** No lab case covers it yet.
- **The sign-in policy exclusion.** My case study says the account should be excluded from policies that block or restrict sign-in, with a test after every policy change. That comes from Microsoft's emergency access guidance. The lab did not run it.
- **An alert sent through the service that has failed.** My case study says to use alert routes that do not share a failure. I have not tested a case where they do.
- **Any real product.** I have no real tenant or vault. Everything above shows whether my reasoning holds together, not how your product behaves.

## Five things to check this month

1. **Send a test alert and see who receives it.** *Why:* in P-R15-12 the alert pointed at a person who had left, and the routing check was what found it.
2. **Ask each holder of the sealed copy whether they can open it this week.** *Why:* the second holder hid a fault in the drill without removing it.
3. **Match every use to a ticket, and check the ticket exists.** *Why:* in P-R15-13 a ticket number alone was not enough, because made-up ones got through.
4. **Rotate after every use and sign in with the new secret.** *Why:* in C-R16-C05 rotation stopped the reuse. The alert only reported it.
5. **After any sign-in policy change, test that the account still signs in.** *Why:* this one comes from my case study and Microsoft's guidance, not from the lab. A policy that blocks sign-in can lock out the account meant for the emergency.

## Where to look

- [Break-glass emergency access](/case-studies/break-glass-access/), the full design with steps, guardrails and audit questions.
- [Machine identity lab](/nhi-lab/), where P-R15-04, P-R15-11, P-R15-12, P-R15-13 and C-R16-C05 sit, with the [round 19 write-up](/nhi-lab/round-19/) for the drill and the [audit data](/nhi-lab/audit/) for the limits.
- [AI governance lab, round 10](/ai-governance-lab/round-10/), where C10 sits.
- Microsoft Learn, [Manage emergency access admin accounts in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access), as I read it for the case study on 1 October 2026.

If you run break-glass and your drills behave differently from my model, I would like to hear how. You can [get in touch here](/contact/).
