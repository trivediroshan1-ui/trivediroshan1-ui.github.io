---
title: "From Permanent Admin Rights to Zero Standing Privilege: A Practical PAM Modernization Path"
layout: post
bg: post-plan
motif: grid
seo_title: "PAM Modernization and Zero Standing Privilege: A Practical Path"
date: 2026-10-29 13:00:00 +0530
author: Roshan Trivedi
series: pam
tags: [pam, zero-standing-privilege, privileged-access, iam, just-in-time]
share_title: "From Permanent Admin Rights to Zero Standing Privilege"
share_label: "Article · Privileged access"
share_accent: green
description: "Most PAM programs stop once passwords are in a vault. Here is the path from standing admin rights to short, approved, recorded sessions, and how to prove it to an auditor."
---

# From Permanent Admin Rights to Zero Standing Privilege: A Practical PAM Modernization Path

*Filed under: Privileged Access · Zero Standing Privilege*

*Independent practitioner guide. Last reviewed 29 October 2026. A general guide from my own practice and public sources. Not a description of any employer's systems, data or projects.*

## The short version

Most PAM programs stop once the passwords are in a vault. The risk that is left is access that never expires. Modernizing means four things working together: vault the secret, rotate it, put a recorded session in front of it, and grant access only for the length of the task. Each of those steps has to leave evidence an auditor can check without asking you to explain it.

## The problem

Privileged accounts are the ones that can change the system itself: domain admins, database owners, root on servers, cloud administrators and service accounts with wide rights. Attackers want them because a valid account looks like normal activity. MITRE ATT&CK tracks this as Valid Accounts (T1078).

Standing privilege makes it worse. If an admin group has forty members, then forty people, and any malware running as them, can reach every system that group covers, at any hour, whether or not they are doing admin work. When an admin signs in interactively to a workstation, credential material can stay in that machine's memory. That is why credential dumping (T1003) is such a common step right after the first foothold.

## Where PAM programs stall

- **The vault is there, but the old door is still open.** Passwords are stored centrally, yet admins can still log in directly because nobody closed the direct path.
- **Rotation skips the hard accounts.** The accounts nobody dares touch are the ones hard-coded in scripts or shared between teams.
- **Session recording is patchy.** Some systems are covered and some are not, so a reviewer cannot answer what someone actually did.
- **"Temporary" access is never taken back.** Nobody owns the expiry.

## How the controls fit together

A privileged session passes five checkpoints in order. If one is missing, the others can be walked around. The audit store sits outside the systems being administered, so the people being recorded cannot change the record. Products split the work differently, but the functions are the same. In CyberArk's self-hosted architecture, for example, the Vault stores the secrets, the Central Policy Manager (CPM) generates new passwords and replaces them on the target machines, and the Privileged Session Manager (PSM) records sessions and can restrict commands. Other platforms combine or separate those roles.

Why: what matters is that every function exists and none can be skipped.

## A privileged request, start to finish

1. **Ask for a specific thing.** The engineer names the target, the reason, a ticket or change number and how long they need. "Admin on everything" is not a valid request.
   Guardrail: the ticket must exist and be open.
   Evidence: the request record.
2. **Prove who they are.** Sign-in goes through single sign-on with multi-factor authentication. For the most sensitive systems, use phishing-resistant methods such as FIDO2 keys, not SMS or push approvals.
   Guardrail: no MFA, no request.
   Evidence: the sign-in log.
3. **Approve by policy, or by a person.** Low-risk, pre-agreed roles can be approved automatically. Access to production or to the identity systems themselves needs a named human, and for the most critical, two.
   Guardrail: the requester cannot approve their own request.
   Evidence: approver, time and reason.
4. **Connect through the broker.** The broker uses the credential on the engineer's behalf, so the person never sees or types the password.
   Guardrail: direct login to the target is blocked at the network.
   Evidence: the full session recording.
5. **Work, and be recorded.** Commands and screens are recorded. Where the platform supports it, dangerous commands can be blocked or flagged in real time.
   Guardrail: the user cannot turn recording off.
   Evidence: a searchable recording tied to the ticket.
6. **Access ends on its own.** When the time runs out or the session closes, access is removed and the secret is changed, so a copied password is worthless.
   Guardrail: expiry is enforced by the system, not by memory.
   Evidence: the rotation log.

## Example: a database fix at 2 a.m.

This is an illustration with invented details, not a specific event.

**Before.** One shared database admin password, known to a whole team and not changed for over a year because changing it might break a script. The engineer logs in directly and nothing records what they ran. After an incident, nobody can say who did what.

**After.** The engineer asks for two hours on that database and cites the incident ticket. The on-call manager approves from their phone. The session runs through the broker and is recorded. At the end, access closes and the credential is rotated. The recording is linked to the ticket.

## What "zero standing" changes

Zero Standing Privilege means nobody holds admin rights by default. Access is created for a task and removed when it ends. This lines up with a tenet in NIST's Zero Trust Architecture (SP 800-207): access to each resource is granted per session, with the least privilege needed to finish the task. With standing access, the attack surface is the whole week. With just-in-time access, it is only the short windows when someone had an approved reason to be there.

## How to get there without stalling

The order matters. Finish each phase, and prove it, before starting the next.

1. **Find every privileged account.** Human admins, service accounts, cloud roles, SSH keys and shared logins. You cannot protect an account you have not found.
   Done when every privileged account has a named owner.
2. **Vault and rotate the most critical first.** Start with the identity systems, domain admins and vault administrators, then work outward.
   Done when critical accounts rotate automatically and no one knows the current password.
3. **Put sessions behind a broker.** Route admin access through a proxy that records it.
   Done when direct admin login to those targets is blocked, not just discouraged.
4. **Remove standing access for people.** Replace permanent admin group membership with approved, time-boxed access. Keep one tested break-glass path.
   Done when standing membership of privileged groups is close to zero, with every exception owned.
5. **Extend to machines.** Applications and pipelines that use secrets move to a secrets manager or short-lived credentials, so nothing important is hard-coded.
   Done when scans of code and configuration find no live credentials.

## Guardrails you can check

| Guardrail | What it stops | How you check it |
| --- | --- | --- |
| Direct login to targets is blocked | Walking around the broker with an old password | Try it from an admin workstation. It should fail |
| Two approvers for the identity systems | One person, or one stolen account, changing the core | Review approvals for the last quarter |
| Phishing-resistant MFA for admins | Push-fatigue and SIM-swap takeovers | Sample admin sign-ins and check the method used |

## Read more

The full case study, with the diagrams and the audit questions, is on my site: [PAM Modernization and Zero Standing Privilege](https://roshantrivedi.co.in/case-studies/pam-modernization/). The earlier posts in this series cover [PAM as an identity](https://roshantrivedi.co.in/writing/pam-as-an-identity/) and a [project plan by organization tier](https://roshantrivedi.co.in/writing/pam-project-plan-by-organization-tier/).

**Roshan Trivedi** writes about privileged access, identity and AI governance at [roshantrivedi.co.in](https://roshantrivedi.co.in). Newsletter: [buttondown.com/trivedi](https://buttondown.com/trivedi).
