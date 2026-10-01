---
title: "PAM Framework and Design: What Sits Around the Vault"
layout: post
date: 2026-10-01 11:00:00 +0530
author: Roshan Trivedi
tags: [pam, iam, privileged-access, architecture, zero-trust, help-desk]
description: "A layered reference framework for privileged access management that covers discovery, tiering, SSO and MFA, authorization, vaulting, machine identities, help desk, monitoring, governance and resilience, with the design trade-offs I weigh."
diagrams: true
---

# PAM Framework and Design: What Sits Around the Vault

When people say they have a PAM tool, they usually mean they have a vault. Passwords go in, rotation runs, sessions get recorded. A common failure is a vault that works as designed inside a program with holes around it: a portal that accepts a password with no second factor, a help desk that can reset the vault admin's MFA on a phone call, one "IT" group that can check out everything. MITRE ATT&CK lists valid accounts (T1078) as a way in, because a stolen working credential looks like normal activity. The holes are where those credentials get used.

So I design PAM as ten layers, and the vault is one of them. This is the framework I use when I open a blank architecture document. It is a reference, so skip to the layer you are working on. Several layers have a longer case study, linked where they fit. Examples are illustrative.

## The architecture

The diagram shows the pieces and the order a request moves through them. The identity provider answers who you are. The portal and policy engine answer what you may do. The vault and session proxy do the work without handing over the password. Ticketing, the SIEM and the help desk sit around the platform, and break-glass sits outside it.

<figure class="diagram-card" style="--c:#7df2d0;margin-top:14px"><button type="button" class="anim-toggle" aria-pressed="false">Pause animation</button><svg class="d-wide" viewBox="0 0 960 560" role="img" aria-labelledby="pa1t pa1d"><title id="pa1t">PAM architecture</title><desc id="pa1d">An admin signs in through the identity provider with SSO and MFA, reaches the PAM portal and policy engine, which checks authorization and approval against ticketing. The vault holds the secret and the session proxy connects to target systems and records the session. Logs go to a SIEM outside the platform. The help desk handles user resets through the identity provider only, and a break-glass path reaches targets outside the normal path.</desc><text class="sub" style="font-size:12px;letter-spacing:.12em" x="105" y="30" text-anchor="middle">PEOPLE</text><text class="sub" style="font-size:12px;letter-spacing:.12em" x="345" y="30" text-anchor="middle">IDENTITY</text><rect x="470" y="14" width="250" height="360" rx="16" fill="none" stroke="#1f2a40" stroke-width="1.5" stroke-dasharray="4 6"/><text class="sub" style="font-size:12px;letter-spacing:.12em" x="595" y="34" text-anchor="middle">PAM PLATFORM</text><text class="sub" style="font-size:12px;letter-spacing:.12em" x="855" y="30" text-anchor="middle">AROUND IT</text><g class="node" style="--i:0"><rect x="20" y="50" width="170" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="105.0" y="74" text-anchor="middle">Admin</text><text class="sub" style="font-size:13px" x="105.0" y="93" text-anchor="middle">opens the portal</text><text class="sub" style="font-size:13px" x="105.0" y="110" text-anchor="middle">from a managed device</text></g><g class="node" style="--i:1"><rect x="250" y="50" width="190" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="345.0" y="74" text-anchor="middle">IdP: SSO + MFA</text><text class="sub" style="font-size:13px" x="345.0" y="93" text-anchor="middle">phishing-resistant for admins</text><text class="sub" style="font-size:13px" x="345.0" y="110" text-anchor="middle">conditional access</text></g><g class="node" style="--i:2"><rect x="490" y="50" width="210" height="100" rx="12"/><text class="ttl" style="font-size:16px" x="595.0" y="89" text-anchor="middle">Portal and policy</text><text class="sub" style="font-size:13px" x="595.0" y="108" text-anchor="middle">AuthN session, AuthZ roles</text><text class="sub" style="font-size:13px" x="595.0" y="125" text-anchor="middle">approval, JIT window</text></g><g class="node" style="--i:5"><rect x="490" y="190" width="210" height="64" rx="12"/><text class="ttl" style="font-size:16px" x="595.0" y="220" text-anchor="middle">Vault</text><text class="sub" style="font-size:13px" x="595.0" y="238" text-anchor="middle">secrets, rotation</text></g><g class="node" style="--i:3"><rect x="490" y="290" width="210" height="64" rx="12"/><text class="ttl" style="font-size:16px" x="595.0" y="320" text-anchor="middle">Session proxy</text><text class="sub" style="font-size:13px" x="595.0" y="338" text-anchor="middle">brokers and records</text></g><g class="node" style="--i:4"><rect x="760" y="50" width="180" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="850.0" y="74" text-anchor="middle">Ticketing</text><text class="sub" style="font-size:13px" x="850.0" y="93" text-anchor="middle">change or incident</text><text class="sub" style="font-size:13px" x="850.0" y="110" text-anchor="middle">approval record</text></g><g class="node" style="--i:6"><rect x="760" y="290" width="180" height="64" rx="12"/><text class="ttl" style="font-size:16px" x="850.0" y="320" text-anchor="middle">Target systems</text><text class="sub" style="font-size:13px" x="850.0" y="338" text-anchor="middle">servers, DB, cloud</text></g><g class="node" style="--i:7"><rect x="760" y="190" width="180" height="64" rx="12"/><text class="ttl" style="font-size:16px" x="850.0" y="220" text-anchor="middle">SIEM</text><text class="sub" style="font-size:13px" x="850.0" y="238" text-anchor="middle">logs and recordings</text></g><g class="node" style="--i:8"><rect x="250" y="190" width="190" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="345.0" y="214" text-anchor="middle">Help desk</text><text class="sub" style="font-size:13px" x="345.0" y="233" text-anchor="middle">user resets only</text><text class="sub" style="font-size:13px" x="345.0" y="250" text-anchor="middle">admin resets escalate</text></g><g class="node" style="--i:9"><rect x="20" y="420" width="420" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="230.0" y="444" text-anchor="middle">Break-glass</text><text class="sub" style="font-size:13px" x="230.0" y="463" text-anchor="middle">sealed credentials, two custodians</text><text class="sub" style="font-size:13px" x="230.0" y="480" text-anchor="middle">outside the normal path</text></g><path class="flow" d="M 190 85 L 250 85"/><path class="flow" d="M 440 85 L 490 85"/><path class="flow" d="M 595 150 L 595 190"/><path class="flow" d="M 595 254 L 595 290"/><path class="flow" d="M 700 322 L 760 322"/><path class="flow" d="M 700 80 L 760 80"/><path class="flow" d="M 345 190 L 345 120"/><path class="log" d="M 700 120 C 730 120 730 215 760 215"/><path class="log" d="M 700 330 C 730 330 735 240 760 235"/><path class="expire" d="M 440 455 L 850 455 L 850 354" stroke-dasharray="7 6"/><text class="sub" style="font-size:13px;" x="650" y="447" text-anchor="middle">emergency route, tested on a schedule</text><g class="badge"><circle cx="250" cy="50" r="11"/><text x="250" y="54">1</text></g><g class="badge"><circle cx="490" cy="50" r="11"/><text x="490" y="54">2</text></g><g class="badge"><circle cx="760" cy="50" r="11"/><text x="760" y="54">3</text></g><g class="badge"><circle cx="490" cy="190" r="11"/><text x="490" y="194">4</text></g><g class="badge"><circle cx="490" cy="290" r="11"/><text x="490" y="294">5</text></g><g class="badge"><circle cx="760" cy="290" r="11"/><text x="760" y="294">6</text></g><rect class="logbar" x="20" y="500" width="920" height="46" rx="10"/><text class="sub" style="font-size:14px;fill:#f7c873" x="480" y="529" text-anchor="middle">Every step above writes to a log store that PAM admins cannot edit</text><circle class="dot" r="5" opacity="0"><set attributeName="opacity" to="1" begin="0s"/><animateMotion dur="14s" begin="0s" repeatCount="indefinite" path="M 105 85 L 345 85 L 595 85 L 595 222 L 595 322 L 850 322"/></circle></svg><svg class="d-tall" viewBox="0 0 360 990" role="img" aria-labelledby="pa2t pa2d"><title id="pa2t">PAM architecture</title><desc id="pa2d">Stacked view: admin, identity provider with SSO and MFA, portal and policy, ticketing, vault, session proxy, target systems and SIEM, with the help desk path into the identity provider and a break-glass route that reaches targets outside the normal path.</desc><g class="node" style="--i:0.0"><rect x="30" y="16" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="44" text-anchor="middle">Admin</text><text class="sub" style="font-size:13px" x="180.0" y="62" text-anchor="middle">managed device</text></g><g class="node" style="--i:0.71"><rect x="30" y="104" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="132" text-anchor="middle">IdP: SSO + MFA</text><text class="sub" style="font-size:13px" x="180.0" y="150" text-anchor="middle">phishing-resistant for admins</text></g><g class="node" style="--i:1.42"><rect x="30" y="192" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="220" text-anchor="middle">Portal and policy</text><text class="sub" style="font-size:13px" x="180.0" y="238" text-anchor="middle">AuthN, AuthZ, approval, JIT</text></g><g class="node" style="--i:2.13"><rect x="30" y="280" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="308" text-anchor="middle">Ticketing</text><text class="sub" style="font-size:13px" x="180.0" y="326" text-anchor="middle">change or incident record</text></g><g class="node" style="--i:2.84"><rect x="30" y="368" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="396" text-anchor="middle">Vault</text><text class="sub" style="font-size:13px" x="180.0" y="414" text-anchor="middle">secrets and rotation</text></g><g class="node" style="--i:3.55"><rect x="30" y="456" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="484" text-anchor="middle">Session proxy</text><text class="sub" style="font-size:13px" x="180.0" y="502" text-anchor="middle">brokers and records</text></g><g class="node" style="--i:4.26"><rect x="30" y="544" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="572" text-anchor="middle">Target systems</text><text class="sub" style="font-size:13px" x="180.0" y="590" text-anchor="middle">servers, DB, cloud</text></g><g class="node" style="--i:4.97"><rect x="30" y="632" width="300" height="60" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="660" text-anchor="middle">SIEM</text><text class="sub" style="font-size:13px" x="180.0" y="678" text-anchor="middle">logs and recordings, off-platform</text></g><path class="flow" d="M 180 76 L 180 104"/><path class="flow" d="M 180 164 L 180 192"/><path class="flow" d="M 180 252 L 180 280"/><path class="flow" d="M 180 340 L 180 368"/><path class="flow" d="M 180 428 L 180 456"/><path class="flow" d="M 180 516 L 180 544"/><path class="flow" d="M 180 604 L 180 632"/><g class="badge"><circle cx="30" cy="104" r="11"/><text x="30" y="108">1</text></g><g class="badge"><circle cx="30" cy="192" r="11"/><text x="30" y="196">2</text></g><g class="badge"><circle cx="30" cy="280" r="11"/><text x="30" y="284">3</text></g><g class="badge"><circle cx="30" cy="368" r="11"/><text x="30" y="372">4</text></g><g class="badge"><circle cx="30" cy="456" r="11"/><text x="30" y="460">5</text></g><g class="badge"><circle cx="30" cy="544" r="11"/><text x="30" y="548">6</text></g><g class="node" style="--i:8"><rect x="30" y="728" width="300" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="752" text-anchor="middle">Help desk</text><text class="sub" style="font-size:13px" x="180.0" y="771" text-anchor="middle">user resets only</text><text class="sub" style="font-size:13px" x="180.0" y="788" text-anchor="middle">admin resets escalate to second line</text></g><path class="flow" d="M 180 728 L 180 700 L 345 700 L 345 85 L 330 85"/><g class="node" style="--i:9"><rect x="30" y="830" width="300" height="70" rx="12"/><text class="ttl" style="font-size:16px" x="180.0" y="854" text-anchor="middle">Break-glass</text><text class="sub" style="font-size:13px" x="180.0" y="873" text-anchor="middle">sealed, two custodians</text><text class="sub" style="font-size:13px" x="180.0" y="890" text-anchor="middle">outside the normal path</text></g><path class="expire" d="M 30 865 L 12 865 L 12 574 L 30 574" stroke-dasharray="7 6"/><rect class="logbar" x="30" y="920" width="300" height="56" rx="10"/><text class="sub" style="font-size:13px;fill:#f7c873" x="180" y="946" text-anchor="middle">Every step logs to a store</text><text class="sub" style="font-size:13px;fill:#f7c873" x="180" y="964" text-anchor="middle">PAM admins cannot edit</text><circle class="dot" r="5" opacity="0"><set attributeName="opacity" to="1" begin="0s"/><animateMotion dur="12s" begin="0s" repeatCount="indefinite" path="M 180 46 L 180 574"/></circle></svg><figcaption>The dots follow one admin session. Numbered badges show the order: sign in at the identity provider, policy at the portal, approval in ticketing, secret from the vault, session through the proxy, and the target. The dashed amber route is break-glass. Product names are left out on purpose; any equivalent identity provider, ticketing tool and SIEM fits each slot.</figcaption></figure>

The ten layers are: scope and discovery, account classes and tiers, authentication, authorization, vault and sessions, service and secrets path, help desk and operations, monitoring, governance, resilience.

## One request, start to finish

<figure class="diagram-card" style="--c:#7df2d0;margin-top:14px"><button type="button" class="anim-toggle" aria-pressed="false">Pause animation</button><svg class="d-wide" viewBox="0 0 960 400" role="img" aria-labelledby="wf1t wf1d"><title id="wf1t">Privileged request workflow</title><desc id="wf1d">Seven steps in order: sign in with SSO and MFA, request, authorize and approve, connect through a broker, monitor and record, check in and rotate, and collect the evidence.</desc><g class="node" style="--i:0.0"><rect x="20" y="40" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="105.0" y="78" text-anchor="middle">Sign in</text><text class="sub" style="font-size:13px" x="105.0" y="96" text-anchor="middle">SSO plus</text><text class="sub" style="font-size:13px" x="105.0" y="114" text-anchor="middle">phishing-resistant MFA</text></g><g class="node" style="--i:0.71"><rect x="270" y="40" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="355.0" y="78" text-anchor="middle">Request</text><text class="sub" style="font-size:13px" x="355.0" y="96" text-anchor="middle">target, reason,</text><text class="sub" style="font-size:13px" x="355.0" y="114" text-anchor="middle">ticket, duration</text></g><g class="node" style="--i:1.42"><rect x="520" y="40" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="605.0" y="78" text-anchor="middle">Authorize</text><text class="sub" style="font-size:13px" x="605.0" y="96" text-anchor="middle">policy first,</text><text class="sub" style="font-size:13px" x="605.0" y="114" text-anchor="middle">then an approver</text></g><g class="node" style="--i:2.13"><rect x="770" y="40" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="855.0" y="78" text-anchor="middle">Connect</text><text class="sub" style="font-size:13px" x="855.0" y="96" text-anchor="middle">brokered session,</text><text class="sub" style="font-size:13px" x="855.0" y="114" text-anchor="middle">no password shown</text></g><g class="node" style="--i:2.84"><rect x="770" y="210" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="855.0" y="248" text-anchor="middle">Monitor, record</text><text class="sub" style="font-size:13px" x="855.0" y="266" text-anchor="middle">SIEM alerts,</text><text class="sub" style="font-size:13px" x="855.0" y="284" text-anchor="middle">session recording</text></g><g class="node" style="--i:3.55"><rect x="520" y="210" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="605.0" y="248" text-anchor="middle">Check in, rotate</text><text class="sub" style="font-size:13px" x="605.0" y="266" text-anchor="middle">access expires,</text><text class="sub" style="font-size:13px" x="605.0" y="284" text-anchor="middle">secret changes</text></g><g class="node" style="--i:4.26"><rect x="270" y="210" width="170" height="96" rx="12"/><text class="ttl" style="font-size:17px" x="355.0" y="248" text-anchor="middle">Evidence</text><text class="sub" style="font-size:13px" x="355.0" y="266" text-anchor="middle">log, recording and</text><text class="sub" style="font-size:13px" x="355.0" y="284" text-anchor="middle">ticket linked</text></g><path class="flow" d="M 190 88 L 270 88"/><path class="flow" d="M 440 88 L 520 88"/><path class="flow" d="M 690 88 L 770 88"/><path class="flow" d="M 855 136 L 855 210"/><path class="flow" d="M 770 258 L 690 258"/><path class="flow" d="M 520 258 L 440 258"/><g class="badge"><circle cx="20" cy="40" r="11"/><text x="20" y="44">1</text></g><g class="badge"><circle cx="270" cy="40" r="11"/><text x="270" y="44">2</text></g><g class="badge"><circle cx="520" cy="40" r="11"/><text x="520" y="44">3</text></g><g class="badge"><circle cx="770" cy="40" r="11"/><text x="770" y="44">4</text></g><g class="badge"><circle cx="770" cy="210" r="11"/><text x="770" y="214">5</text></g><g class="badge"><circle cx="520" cy="210" r="11"/><text x="520" y="214">6</text></g><g class="badge"><circle cx="270" cy="210" r="11"/><text x="270" y="214">7</text></g><rect class="logbar" x="20" y="340" width="920" height="46" rx="10"/><text class="sub" style="font-size:14px;fill:#f7c873" x="480" y="369" text-anchor="middle">Steps 1 to 6 each write a record to the SIEM, outside the platform</text><circle class="dot" r="5" opacity="0"><set attributeName="opacity" to="1" begin="0s"/><animateMotion dur="14s" begin="0s" repeatCount="indefinite" path="M 105 88 L 855 88 L 855 258 L 355 258"/></circle></svg><svg class="d-tall" viewBox="0 0 360 815" role="img" aria-labelledby="wf2t wf2d"><title id="wf2t">Privileged request workflow</title><desc id="wf2d">Seven steps stacked in order: sign in, request, authorize, connect, monitor and record, check in and rotate, evidence.</desc><g class="node" style="--i:0.0"><rect x="30" y="10" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="40" text-anchor="middle">Sign in</text><text class="sub" style="font-size:13px" x="180.0" y="58" text-anchor="middle">SSO plus</text><text class="sub" style="font-size:13px" x="180.0" y="76" text-anchor="middle">phishing-resistant MFA</text></g><g class="badge"><circle cx="30" cy="10" r="11"/><text x="30" y="14">1</text></g><g class="node" style="--i:0.71"><rect x="30" y="114" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="144" text-anchor="middle">Request</text><text class="sub" style="font-size:13px" x="180.0" y="162" text-anchor="middle">target, reason,</text><text class="sub" style="font-size:13px" x="180.0" y="180" text-anchor="middle">ticket, duration</text></g><g class="badge"><circle cx="30" cy="114" r="11"/><text x="30" y="118">2</text></g><g class="node" style="--i:1.42"><rect x="30" y="218" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="248" text-anchor="middle">Authorize</text><text class="sub" style="font-size:13px" x="180.0" y="266" text-anchor="middle">policy first,</text><text class="sub" style="font-size:13px" x="180.0" y="284" text-anchor="middle">then an approver</text></g><g class="badge"><circle cx="30" cy="218" r="11"/><text x="30" y="222">3</text></g><g class="node" style="--i:2.13"><rect x="30" y="322" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="352" text-anchor="middle">Connect</text><text class="sub" style="font-size:13px" x="180.0" y="370" text-anchor="middle">brokered session,</text><text class="sub" style="font-size:13px" x="180.0" y="388" text-anchor="middle">no password shown</text></g><g class="badge"><circle cx="30" cy="322" r="11"/><text x="30" y="326">4</text></g><g class="node" style="--i:2.84"><rect x="30" y="426" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="456" text-anchor="middle">Monitor, record</text><text class="sub" style="font-size:13px" x="180.0" y="474" text-anchor="middle">SIEM alerts,</text><text class="sub" style="font-size:13px" x="180.0" y="492" text-anchor="middle">session recording</text></g><g class="badge"><circle cx="30" cy="426" r="11"/><text x="30" y="430">5</text></g><g class="node" style="--i:3.55"><rect x="30" y="530" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="560" text-anchor="middle">Check in, rotate</text><text class="sub" style="font-size:13px" x="180.0" y="578" text-anchor="middle">access expires,</text><text class="sub" style="font-size:13px" x="180.0" y="596" text-anchor="middle">secret changes</text></g><g class="badge"><circle cx="30" cy="530" r="11"/><text x="30" y="534">6</text></g><g class="node" style="--i:4.26"><rect x="30" y="634" width="300" height="80" rx="12"/><text class="ttl" style="font-size:17px" x="180.0" y="664" text-anchor="middle">Evidence</text><text class="sub" style="font-size:13px" x="180.0" y="682" text-anchor="middle">log, recording and</text><text class="sub" style="font-size:13px" x="180.0" y="700" text-anchor="middle">ticket linked</text></g><g class="badge"><circle cx="30" cy="634" r="11"/><text x="30" y="638">7</text></g><path class="flow" d="M 180 90 L 180 114"/><path class="flow" d="M 180 194 L 180 218"/><path class="flow" d="M 180 298 L 180 322"/><path class="flow" d="M 180 402 L 180 426"/><path class="flow" d="M 180 506 L 180 530"/><path class="flow" d="M 180 610 L 180 634"/><rect class="logbar" x="30" y="745" width="300" height="56" rx="10"/><text class="sub" style="font-size:13px;fill:#f7c873" x="180" y="770" text-anchor="middle">Steps 1 to 6 each log to</text><text class="sub" style="font-size:13px;fill:#f7c873" x="180" y="788" text-anchor="middle">a store outside the platform</text><circle class="dot" r="5" opacity="0"><set attributeName="opacity" to="1" begin="0s"/><animateMotion dur="12s" begin="0s" repeatCount="indefinite" path="M 180 50 L 180 690"/></circle></svg><figcaption>One request, start to finish. The dot travels the seven steps in order. Illustrative only.</figcaption></figure>

1. **Sign in.** The person signs in to the portal through the identity provider, with SSO and MFA. Admins and approvers use phishing-resistant MFA. *Guardrail: no MFA, no session, and a managed device is required.*
2. **Request.** They name the target, the reason, a ticket or change number and the length of time. "Admin on everything" is not a valid request. *Guardrail: no open ticket, no request.*
3. **Authorize and approve.** Policy checks the role, the target and the tier first. Low-risk roles can approve by policy. Production and Tier 0 need a named approver, and Tier 0 a second one. *Guardrail: nobody approves their own request.*
4. **Connect.** The proxy opens the session using the vaulted credential, or the person checks the credential out. The person never types the password into the target. *Guardrail: direct login to the target is blocked.*
5. **Monitor and record.** The session is recorded. Events go to the SIEM as they happen. Alerts fire on rules such as access with no ticket. *Guardrail: the user cannot switch off recording.*
6. **Check in and rotate.** The window ends on its own. The credential is changed so a copied value is useless. *Guardrail: expiry is enforced by the system, not by memory.*
7. **Evidence.** The request, approval, recording, rotation record and ticket are linked. *Guardrail: logs live where platform admins cannot edit them.*

## 1. Scope and discovery

You cannot protect what you have not found. Privilege covers local administrators, root, database owners, cloud roles, service accounts, SSH keys, API tokens, network device logins and AI agent credentials. I describe how I run this stage in [how I run a privileged access program](/case-studies/privileged-access-program/).

Discovery produces an inventory, and every line needs an owner. An account with no owner goes on an exception register with a reason and an end date. CIS Controls v8 asks for an inventory of accounts (5.1) and a separate one for service accounts (5.5).

Sources are directory queries, local admin enumeration, cloud role assignments, CMDB exports, secret scans of repositories and pipelines, and interviews with system owners. Interviews fill the gaps that tools leave.

## 2. Account classes and tiering

A help desk login and the account that administers the identity provider should not get the same friction. I place each credential in the highest tier of anything it can change. The full model is in the [credential tiering model](/case-studies/credential-tiering-model/).

The tier idea comes from Microsoft's Active Directory tier model. Microsoft's current guidance, the enterprise access model, builds on it and describes five planes: data and workload, management, control, user access pathways and application access pathways. The control plane is the centralized identity system, and Tier 0 thinking starts there. A cloud identity provider's global admin role belongs in it even with no server behind it.

Rules I keep:

- One person holds separate accounts for separate tiers. Admin work and email never share an account or device.
- A credential valid in one tier is never valid in another.
- The vault, its console and its recovery material are Tier 0. So are break-glass accounts.

CIS 5.4 says it plainly: restrict administrator privileges to dedicated administrator accounts.

## 3. Authentication: SSO and MFA

Two authentication events matter, and designs blur them. Authentication to PAM proves who is asking. Authentication to the target is done by the platform with the vaulted credential, on the person's behalf. The person should never need the second one.

**SSO into the portal.** People sign in through the corporate identity provider over SAML or OpenID Connect. The platform holds no second set of passwords for people. Remaining local accounts are documented and watched. Joiner, mover and leaver changes then flow through: when an identity provider group changes, PAM access changes with it.

**Which MFA.** For admins I want phishing-resistant MFA: FIDO2 keys or passkeys, or certificate-based authentication. CISA's Scattered Spider advisory says FIDO/WebAuthn and PKI-based MFA resist phishing and are not susceptible to push bombing or SIM swap. SMS, voice and push approvals do not earn that credit. NIST SP 800-63B-4 (final, July 2025) says AAL3 needs a phishing-resistant authenticator with a non-exportable key, and verifiers must offer a phishing-resistant option at AAL2. In SP 800-53 this is IA-2(1), and CIS 6.5 requires MFA for administrative access.

**Where MFA applies and why**

| Point | MFA | Why |
|---|---|---|
| Portal sign-in, every user | Yes, enforced at the identity provider | A stolen portal session reaches every credential that user may check out |
| Portal sign-in, admins and approvers | Phishing-resistant | These are the accounts attackers phone, phish and push-bomb |
| Platform administration console | Phishing-resistant, from a managed admin device | Tier 0 |
| Check-out of a Tier 0 credential, approval of a Tier 0 request | Ask again inside the platform | An open session or hijacked token should not be enough |
| Login to the target through the broker | The person is not asked again; they authenticated at the portal | The broker supplies the credential. Where a target enforces MFA on admin logins itself, check what your product supports before you design around it |
| Break-glass | Phishing-resistant, and a different method from daily admins | Microsoft's emergency access guidance asks for this so it does not share a failure with the normal path |
| Service accounts and applications | No MFA possible | Use narrow scope, short life, network limits and monitoring instead |

**Conditional checks.** Identity providers can add context to the decision at sign-in, such as the device, the location and a risk signal. For PAM I typically want a managed device and a block or step-up on risky sign-ins. Break-glass accounts are excluded from policies that block sign-in, and a test after each policy change proves they still work. The identity provider is now a dependency of PAM. Layer 10 covers what happens when it is down.

## 4. Authorization: who can do what, and for how long

Authentication says who you are. Authorization says what you may do. The two happen twice in a PAM design, once at the portal and once at the target, and they are different checks.

| | At the PAM portal | At the target |
|---|---|---|
| AuthN | SSO and MFA from the identity provider prove the person | The broker presents the vaulted credential, which proves the account to the target |
| AuthZ | Roles, safe or folder membership, ticket, approval, time window | The account's own rights: local groups, sudo rules, database roles, cloud role |
| Decided by | PAM policy owner | The target system's owner |
| Typical failure | One safe everyone can open | The vaulted account is a domain admin |
| Evidence | Portal log, approval record | The target's own audit log, still switched on |

Both checks must pass. PAM approved the request, and the target permits the action.

**Roles inside PAM.** Requester, approver, auditor (reads logs and recordings, changes nothing), safe or folder owner, policy administrator, platform administrator. No role can both administer the vault and read secrets.

**RBAC and ABAC.** Roles are easy to explain to an auditor and easy to review. They also multiply until nobody can reason about them. Attributes suit PAM for context: production database, open change ticket, requester in the owning team, business hours. I use roles for the broad shape and attributes for conditions. CSF 2.0 PR.AA-05 states the aim: permissions defined in policy, managed, enforced and reviewed, built on least privilege and separation of duties.

**Least privilege.** SP 800-53 AC-6 enhancements map to PAM directly: access to security functions (AC-6(1)), privileged accounts (AC-6(5)), review of user privileges (AC-6(7)), log use of privileged functions (AC-6(9)) and prohibit non-privileged users from executing privileged functions (AC-6(10)). Here is what I aim for on each platform. These are my design practices. The sources in this post support the principle, not these specific settings.

| Platform | What the person gets | What they do not get |
|---|---|---|
| Windows | A unique local admin credential per host, vaulted and rotated. Routine tasks such as restarting a service through a constrained endpoint (Microsoft JEA is the PowerShell feature for this) | A shared local admin password, or domain admin to fix one server |
| Linux | A named personal account with sudo rules that list the commands a role needs. Root only through a brokered, recorded session | A shared root password, or unrestricted sudo for a whole team |
| Database | Separate roles: read-only for support, schema change for the length of a change, superuser only brokered and recorded | Application logins used by humans, or standing DBA rights |
| Cloud | A role scoped to one account, subscription or project, activated for a window | Long-lived access keys for people, or a global admin role on standing basis |

**Approval, JIT and scope.** Low-risk, pre-agreed roles can be approved by policy. Production and identity systems need a named person, and Tier 0 a second one. The requester never approves their own request. The NCSC describes the pattern: the credential is used to request access, and approval can be rule-based, multi-party or by consensus. Just-in-time limits duration, and just enough limits scope. Detail is in [JIT and just-enough elevation](/case-studies/jit-jea-elevation/).

**Separation of duties.** AC-5 asks you to identify duties that must be split and define authorizations that enforce it. My list: vault administrators cannot read secrets; secret users cannot administer the vault; approvers are not requesters; platform admins do not administer the log store that records them.

## 5. Vaulting, rotation and sessions

This is the layer people mean when they say PAM.

- **Storage.** Encrypted at rest, keys in a key management service or HSM (SC-12 covers key management). Vault admins are separate from secret users.
- **Check-out and check-in.** A reason, and for sensitive accounts a ticket and approval. Exclusive check-out means one person at a time, with a change at check-in.
- **Rotation.** Onboard, verify the vault can log in, then rotate straight away so the old value stops working. Plan how vault and target get back in step if they drift.
- **Brokered sessions.** The person connects through a proxy that uses the credential for them. They never see the password, and the proxy records the session.
- **Command filtering.** Where supported, block or flag dangerous commands live. Treat it as a safety net and never as the boundary.
- **Closing the old door.** Direct login to the target must be blocked at the network or host. If admins can still use an old password, the vault is optional. Test it from an admin workstation.

AU-14 (session audit) sits behind recording, and it says to build session auditing in consultation with legal counsel. Recordings can hold personal data, so agree retention and reviewer access with legal and privacy before go-live. The full flow is in [moving to short, approved, recorded sessions](/case-studies/pam-modernization/).

**The platform's own admins and secrets.** The people who run PAM hold the most powerful access in the program, so they get the strictest version of the rules above.

- Split platform duties: infrastructure administrators patch and run the servers, policy administrators manage safes and roles, auditors read logs. Nobody holds all three.
- Platform admin accounts are Tier 0 accounts. They use phishing-resistant MFA from a managed admin device, and their elevated access is requested like anyone else's, with a second approver.
- Policy changes need a ticket and a second person. A policy admin cannot be the only reviewer of their own change.
- The integrations hold secrets too: the service accounts the platform uses to rotate passwords on targets, the identity provider client secret or signing certificate, the ticketing API token, the SIEM forwarding token. Each has an owner, an expiry date on a calendar, a rotation process and the narrowest scope that works. Rotation accounts are separated by tier, so a Tier 2 rotation account cannot reach Tier 0 targets.

## 6. Service, application and secrets path

Service accounts, application secrets, pipeline variables, cloud keys and agent tokens outnumber human admins and rarely have an owner. My order of preference:

1. Remove the credential where a short-lived identity will do, such as a workload identity or role assumption.
2. Generate it on demand and let it expire.
3. Fetch it from a store at runtime.
4. Vault and rotate it as a last resort, with the application change rotation needs.

IA-5(7) prohibits embedded unencrypted static authenticators, which is the rule behind scanning code and config. Every machine credential still needs an owner, a tier, a rotation rule and a record of where it is used. The [credential platform](/case-studies/credential-platform/) case study covers the catalog and lifecycle.

## 7. Help desk and operations

I put this layer next to authentication because it can undo it. If a phone call can reset an admin's password or MFA, the best second factor you bought is a polite request.

It is a documented attack pattern. CISA's Scattered Spider advisory describes actors who used social engineering to convince IT help desk personnel to reset passwords or MFA tokens, and who abused the trusted relationship of contracted help desks. BleepingComputer reported Okta's account of attacks in July and August 2023 where callers persuaded service desk agents to reset MFA for highly privileged users. The NCSC, in its blog on incidents affecting UK retailers, asks organizations to review how the help desk authenticates staff before resetting passwords, especially for accounts with escalated privileges.

**What the help desk may and may not do for a PAM admin.** This is my design position. The sources support the direction, with Okta's custom admin roles as one concrete example of limiting reset rights.

| First-line help desk may | First-line help desk may not |
|---|---|
| Open and route a case to second line | Reset the password or MFA of a PAM admin, a Tier 0 or Tier 1 account |
| Confirm a case status and point the person to self-service recovery | Read, check out or view any vaulted credential |
| Reset a standard user (Tier 3) under the normal verified process | Approve a PAM request or add anyone to a privileged group |
| Unlock a standard user's portal sign-in | Change the phone number, email or device used to recover a privileged account |
| Raise an alert if a caller seems wrong | Switch off alerts, logging or conditional access for anyone |

**Second line, for a privileged recovery.** A named second-line team handles it with a ticket, an approver who is independent of the requester, identity verified through a channel the attacker did not choose (a call-back to a number already on record, or a video check against a known face), a new authenticator issued with a short-lived, device-limited code in place of a spoken temporary password, existing sessions revoked, and the security team notified. Call-back and video checks are my default. Of the sources here, Okta's guidance covers time-bound recovery codes and role limits, and the reported 2023 mitigations include visual checks and manager approval.

**Contracted desks.** Same rules, tighter scope, no admin resets, and their logs shared with your SOC. The help desk's own tooling and local admin rights are Tier 2 credentials, vaulted and elevated on request.

**Support tiers and runbooks.** First line handles access requests, portal sign-in problems and how-do-I questions. Second line, the PAM operations team, handles onboarding, rotation failures, proxy faults and stalled approvals. Third line is engineering and the vendor. Each tier has runbooks for failures that repeat: rotation failed because the target was unreachable, a recording did not upload, a user is locked out of the portal, a credential is stuck checked out. Each says who is paged.

**Break-glass.** Emergency access has to work when the PAM platform, identity provider and MFA service are all down, so it cannot depend on any of them. Microsoft's guidance asks for at least two cloud-only accounts, phishing-resistant sign-in, alerts on every sign-in and validation at least every 90 days. Each use closes with a written justification and rotation. See [break-glass access](/case-studies/break-glass-access/).

**Incident procedures.** I add PAM steps to the response plan: disable an account and rotate every credential it could reach, pull recordings for a time window, freeze approvals, and decide what to do if the vault itself is suspected.

## 8. Monitoring and audit evidence

Logs help only if they sit outside the reach of the people being logged. Platform logs go to the SIEM in near real time. AU-2 and AU-12 cover choosing and generating events, and AC-6(9) asks for privileged function use to be logged.

Send portal sign-ins and failures, requests, approvals and denials, check-outs, session start and stop, rotations and failures, policy and role changes, and any break-glass use. Give each alert a named owner: break-glass use, privileged access with no ticket, after-hours access to the most sensitive systems, failed rotations, direct logins that bypass the broker, and MFA changes on admin accounts.

The test is whether an auditor can follow one session from request to approval to recording to closure without asking you to explain.

## 9. Governance

Governance gets skipped because it is not technical, and it decides whether the design survives its second year.

- **Owners.** Every privileged account, safe or folder and integration has a named owner. The platform has a product owner.
- **Recertification.** Privileged memberships are reviewed on a schedule (AC-6(7), AC-2). Reviewers see what the access does and when it was last used.
- **Policy.** Rotation rules, naming, tier definitions, break-glass and approval rules are written, approved by the business and versioned.
- **Change control.** Changes to policy, roles, connectors and the platform itself go through a ticket, a second reviewer, a test in a non-production copy and a rollback plan. Emergency changes are allowed and reviewed afterwards.
- **Testing on a schedule.** Direct login to a Tier 0 target should fail. The break-glass drill should work and the alert should fire. A restore from backup should succeed. DR failover should complete. A forced rotation should pass. A conditional access change should not lock out emergency accounts. A call-in test of the help desk, agreed with legal and HR first, shows whether the reset rules hold under pressure.
- **Exceptions.** Each has an owner, a reason and an end date.
- **Metrics.** Numbers read straight from the platform: share of in-scope accounts onboarded, rotation failures and their age, accounts without an owner, standing privileged membership, break-glass uses and their reviews, help desk resets of privileged accounts and how many followed the verified process. Targets only mean something against your own baseline.

## 10. Resilience

A PAM platform cannot be the thing that is down when something goes wrong.

- **High availability.** Redundant components across failure zones, with upgrades planned to keep the service up.
- **Disaster recovery.** A second site or region, with RTO and RPO agreed with the business.
- **Vault backup.** Encrypted backups (CP-9), a recovery process for the encryption keys, and restore tests. A backup nobody has restored is a hope.
- **Dependencies.** List what must work for a person to reach a password: identity provider, MFA service, DNS, network path, ticketing. Decide what happens when each fails.
- **Break-glass.** Sealed recovery material for the platform itself, two custodians, kept in step with rotation.

## Layer map

| Layer | Protects against | Evidence it produces |
|---|---|---|
| 1 Scope and discovery | Unknown privileged accounts, orphaned service accounts | Inventory with owners, exception register |
| 2 Tiering | One stolen credential working in many places | Tier register, tier-to-control matrix |
| 3 AuthN | Stolen passwords, phished or pushed MFA, unmanaged devices | Identity provider sign-in logs, conditional access policy export |
| 4 AuthZ | Excess rights, self-approval, conflicting duties | Role and policy export, approval records |
| 5 Vault and sessions | Password reuse, shared secrets, no record of actions | Check-out and rotation logs, session recordings |
| 6 Machine path | Hard-coded and long-lived secrets | Secret scan results, service account register |
| 7 Help desk and ops | Social engineering of resets, ad hoc fixes, unrehearsed emergencies | Reset tickets with verification record, runbooks, drill logs |
| 8 Monitoring | Misuse that goes unseen, tampered records | SIEM alerts and their handling, off-platform log store |
| 9 Governance | Access that never gets revoked, unowned policy, unreviewed changes | Recertification records, change tickets, test results, metrics reports |
| 10 Resilience | Loss of the platform or its dependencies, lost vault | DR and restore test reports, sealed storage custody log |

NIST CSF 2.0 PR.AA and CIS Controls 5 and 6 are my cross-check for coverage. They are not the design.

## Design decisions and trade-offs

None of these has one right answer for every estate.

**Proxy or agent on the target.**

| | Proxy or agentless | Agent on target |
|---|---|---|
| For | Nothing installed on targets, one place to patch | Works where the network path is awkward, can enforce local controls |
| Against | Needs a network path and protocol support for every target, and the proxy tier is a choke point | Software to deploy, patch and support everywhere, and a failed agent can break a login path |
| Fits | Servers, network gear and databases reachable from a central tier | Segmented estates, OT, endpoints off the corporate network |

Most estates end up with both. Choose per target class and write down why.

**Where the vault sits.** In the most protected zone, treated as Tier 0, with narrow inbound paths from the proxy and portal and outbound paths only to managed targets. Watch for circular dependency: a vault that authenticates through a directory it also protects.

**HA topology.** Active-passive is easier to reason about and test. Active-active adds capacity and removes failover delay, and brings replication and consistency questions. The failover test matters more than the diagram.

**Integration order.** Identity provider and SSO first, because every later control assumes a known person with enforced MFA. Ticketing next, so approvals work before anyone is onboarded. SIEM third, so logs flow before the first real privileged session. Target onboarding last, Tier 0 first. Reverse it and you onboard targets nobody can approve and nobody watches.

## Common design mistakes

- Vault with no front door: portal sign-in is a password, or MFA is SMS.
- The old path is open: direct logins to targets still work.
- The help desk can reset anything.
- Standing membership kept "just in case" next to a JIT process.
- One large safe everyone can open, because role design was skipped.
- A recorded session that runs as a domain admin.
- Break-glass that has never been tested, or that depends on the thing that is down.
- Logs held inside the platform where its admins can edit them.
- Integration secrets with no owner and no expiry reminder.
- No decommission plan for the old tool, so old logs and recordings have no reader.

## Sources

Primary or standards bodies:

- CISA, [Scattered Spider advisory AA23-320A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-320a) (help desk social engineering, phishing-resistant MFA).
- NCSC (UK), [Incidents impacting retailers](https://www.ncsc.gov.uk/blog-post/incidents-impacting-retailers) and [Use privileged access management](https://www.ncsc.gov.uk/collection/secure-system-administration/use-privileged-access-management).
- NIST, [SP 800-63B-4](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf).
- Microsoft, [Enterprise access model](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model) and [Emergency access accounts](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access).
- MITRE, [ATT&CK T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/).

Secondary, so treat them as pointers to the primary text:

- NIST SP 800-53 Rev. 5 control titles and CSF 2.0 PR.AA, read through [CSF Tools](https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-6/) and [PR.AA-05](https://csf.tools/reference/nist-cybersecurity-framework/v2-0/pr/pr-aa/pr-aa-05/).
- CIS Controls v8 safeguard titles, read through the CIS assessment specification for [Control 5](https://controls-assessment-specification.readthedocs.io/en/latest/control-5/) and [Control 6](https://cas.docs.cisecurity.org/en/latest/source/Controls6/).
- Okta, [Account recovery without password resets](https://sec.okta.com/articles/2025/12/account-recovery-without-password-resets/), vendor documentation used as an example of help desk role limits and time-bound recovery codes.
- BleepingComputer, [Okta: hackers target IT help desks](https://www.bleepingcomputer.com/news/security/okta-hackers-target-it-help-desks-to-gain-super-admin-disable-mfa/), a news report of Okta's 2023 advisory.

Not sourced here, and stated as my own practice: the per-platform least-privilege settings, the call-back and video verification steps, the RBAC and ABAC guidance, and the design trade-offs. I left PCI DSS v4.0.1 requirements 7 and 8 out because I could not confirm the requirement wording from the PCI Security Standards Council's own text.
