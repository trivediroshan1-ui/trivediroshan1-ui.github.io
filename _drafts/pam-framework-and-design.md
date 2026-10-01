---
title: "PAM Framework and Design: What Sits Around the Vault"
layout: post
date: 2026-10-02
author: Roshan Trivedi
tags: [pam, iam, privileged-access, architecture, zero-trust, help-desk]
description: "A layered reference framework for privileged access management that covers discovery, tiering, SSO and MFA, authorization, vaulting, machine identities, help desk, monitoring, governance and resilience, with the design trade-offs I weigh."
---

# PAM Framework and Design: What Sits Around the Vault

When people say they have a PAM tool, they usually mean they have a vault. Passwords go in, rotation runs, sessions get recorded. I have seen that fail anyway. The vault portal accepted a password and no second factor. The help desk could reset the vault admin's MFA on a phone call. Everyone in the "IT" group could check out everything. The tool worked as designed and the program still had holes.

So I design PAM as ten layers, and the vault is one of them. This is the framework I use when I open a blank architecture document. It is a reference, so skim to the layer you are working on. Several layers have a longer case study, and I link them where they fit. Examples are illustrative.

```
 1 Scope and discovery         6 Service, app and secrets path
 2 Account classes and tiers   7 Help desk and operations
 3 Authentication (AuthN)      8 Monitoring and audit evidence
 4 Authorization (AuthZ)       9 Governance
 5 Vault, sessions, rotation  10 Resilience
```

Layers 3 and 4 are where designs are thin. Layer 7 is where they get attacked.

## 1. Scope and discovery

You cannot protect what you have not found. Privilege covers local administrators, root, database owners, cloud roles, service accounts, SSH keys, API tokens, network device logins and now AI agent credentials. I describe how I run this stage in [how I run a privileged access program](/case-studies/privileged-access-program/).

Discovery produces an inventory, and every line needs an owner. An account with no owner goes on an exception register with a reason and an end date. CIS Controls v8 asks for an inventory of accounts (5.1) and a separate one for service accounts (5.5).

Sources are directory queries, local admin enumeration, cloud role assignments, CMDB exports, secret scans of repositories and pipelines, and conversations with system owners. The conversations find the most.

## 2. Account classes and tiering

A help desk login and the account that administers the identity provider should not get the same friction. I place each credential in the highest tier of anything it can change. The full model is in the [credential tiering model](/case-studies/credential-tiering-model/).

The tier idea comes from Microsoft's Active Directory tier model. Microsoft's current guidance, the enterprise access model, builds on it and describes five planes: data and workload, management, control, user access pathways and application access pathways. The control plane is the centralized identity system, and Tier 0 thinking starts there. A cloud identity provider's global admin role belongs in it even with no server behind it.

Rules I keep:

- One person holds separate accounts for separate tiers. Admin work and email never share an account or device.
- A credential valid in one tier is never valid in another.
- The vault, its console and its recovery material are Tier 0. So are break-glass accounts.

CIS 5.4 says it plainly: restrict administrator privileges to dedicated administrator accounts.

## 3. Authentication: SSO, MFA and conditional checks

Two authentication events matter, and designs blur them. Authentication to PAM proves who is asking. Authentication to the target is done by the platform with the vaulted credential, on the person's behalf. The person should never need the second one.

**SSO into the portal.** People sign in through the corporate identity provider over SAML or OpenID Connect. The platform holds no second set of passwords for people. Remaining local accounts are documented and watched. Joiner, mover and leaver changes then flow through: when an identity provider group changes, PAM access changes with it.

**Which MFA.** For admins I want phishing-resistant MFA: FIDO2 keys or passkeys, or certificate-based authentication. CISA's Scattered Spider advisory says FIDO/WebAuthn and PKI-based MFA resist phishing and are not susceptible to push bombing or SIM swap. SMS, voice and push approvals do not earn that credit. NIST SP 800-63B-4 (final, July 2025) says AAL3 needs a phishing-resistant authenticator with a non-exportable key, and verifiers must offer a phishing-resistant option at AAL2. In SP 800-53 this is IA-2(1), and CIS 6.5 requires MFA for administrative access.

**Conditional and risk checks.** The identity provider can look at user, device, location and sign-in risk. For PAM I usually want a managed device, a block on countries where the business has no presence, a block or step-up on risky sign-ins, and short re-authentication intervals. New policies run in report-only mode first. Break-glass accounts are excluded from policies that block sign-in, and a test after each policy change proves they still work.

Check-out of the most sensitive credential, and approval of a high-risk request, should ask for MFA again inside the platform.

The identity provider is now a dependency of PAM. Layer 10 covers what happens when it is down.

## 4. Authorization: who can do what, and for how long

Authentication says who you are. Authorization says what you may do. A PAM design has three AuthZ decisions, and I write each one down.

1. **Who can use PAM, in which role.** Requester, approver, auditor, safe or folder owner, platform administrator.
2. **Who can check out or connect to which credential or target.** Membership in a safe or folder, plus policy.
3. **What the person can do on the target.** Decided by the target, by the account the broker uses, and by any command filtering.

**RBAC and ABAC.** Roles are easy to explain to an auditor and easy to review. They also multiply until nobody can reason about them. Attributes suit PAM for context: production database, open change ticket, requester in the owning team, business hours. I use roles for the broad shape and attributes for conditions. CSF 2.0 PR.AA-05 states the aim: permissions defined in policy, managed, enforced and reviewed, built on least privilege and separation of duties.

**Least privilege.** SP 800-53 AC-6 enhancements map to PAM directly: access to security functions (AC-6(1)), privileged accounts (AC-6(5)), review of user privileges (AC-6(7)), log use of privileged functions (AC-6(9)) and prohibit non-privileged users from executing privileged functions (AC-6(10)).

**Approval.** Low-risk, pre-agreed roles can be approved by policy. Production and identity systems need a named person, and Tier 0 a second one. The requester never approves their own request. The NCSC describes the pattern: the credential is used to request access, and approval can be rule-based, multi-party or by consensus.

**JIT and scope.** Just-in-time limits duration. Just enough limits scope. JEA is Microsoft's PowerShell feature, and I use the word only for that. Detail is in [JIT and just-enough elevation](/case-studies/jit-jea-elevation/).

**Separation of duties.** AC-5 asks you to identify duties that must be split and define authorizations that enforce it. My list: vault administrators cannot read secrets; secret users cannot administer the vault; approvers are not requesters; platform admins do not administer the log store that records them.

**AuthZ at the target versus in PAM.** PAM can only narrow what the target allows. If the brokered account is a domain admin, command filtering is a speed bump. So the vaulted account should be the smallest one that does the job, and both checks must pass: PAM approved it, and the target permits it.

## 5. Vaulting, rotation and sessions

This is the layer people mean when they say PAM.

- **Storage.** Encrypted at rest, keys in a key management service or HSM (SC-12 covers key management). Vault admins are separate from secret users.
- **Check-out and check-in.** A reason, and for sensitive accounts a ticket and approval. Exclusive check-out means one person at a time, with a change at check-in.
- **Rotation.** Onboard, verify the vault can log in, then rotate straight away so the old value stops working. Plan how vault and target get back in step if they drift.
- **Brokered sessions.** The person connects through a proxy that uses the credential for them. They never see the password, and the proxy records the session.
- **Command filtering.** Where supported, block or flag dangerous commands live. I treat it as a safety net and never as the boundary.
- **Closing the old door.** Direct login to the target must be blocked at the network or host. If admins can still use an old password, the vault is optional. I test from an admin workstation.

AU-14 (session audit) sits behind recording, and it says to build session auditing in consultation with legal counsel. Recordings can hold personal data, so agree retention and reviewer access with legal and privacy before go-live. The full flow is in [moving to short, approved, recorded sessions](/case-studies/pam-modernization/).

## 6. Service, application and secrets path

Service accounts, application secrets, pipeline variables, cloud keys and agent tokens outnumber human admins and rarely have an owner. My order of preference:

1. Remove the credential where a short-lived identity will do, such as a workload identity or role assumption.
2. Generate it on demand and let it expire.
3. Fetch it from a store at runtime.
4. Vault and rotate it as a last resort, with the application change rotation needs.

IA-5(7) prohibits embedded unencrypted static authenticators, which is the rule behind scanning code and config. Every machine credential still needs an owner, a tier, a rotation rule and a record of where it is used. Applications cannot answer an MFA prompt, so their controls are narrow scope, short life, network restriction and monitoring. I write those down as compensating controls. The [credential platform](/case-studies/credential-platform/) case study covers the catalog and lifecycle.

## 7. Help desk and operations

I put this layer next to authentication because it can undo it. If a phone call can reset an admin's password or MFA, the best second factor you bought is a polite request.

It is a documented attack pattern. CISA's Scattered Spider advisory describes actors who used social engineering to convince IT help desk personnel to reset passwords or MFA tokens, and who abused the trusted relationship of contracted help desks. Okta reported attacks between 29 July and 19 August 2023 where callers persuaded service desk agents to reset MFA for highly privileged users. The NCSC, after the 2025 UK retail incidents, asked organizations to review how the help desk authenticates staff before resetting passwords, especially for accounts with escalated privileges.

| Question | My default |
|---|---|
| Who resets what | Tier 2 and 3 user resets can sit with the front line. Resets of a Tier 0 or Tier 1 admin password or MFA need a second-line team and a separate approval. |
| Can the front line touch admin MFA | No. Okta documents custom admin roles that cannot reset passwords or factors, a good example of the idea. |
| How callers are verified | Never by details an attacker can look up. Call-back to a number on record, manager approval through another channel, or a video or in-person check for privileged users. |
| What gets issued | A time-limited access code that works only from a managed device, in place of a temporary password read out loud. |
| Contracted desks | Same rules, tighter scope, no admin resets, logs shared with your SOC. |
| Alerts | Any MFA method change or reset on a privileged account alerts security. |

The help desk's own tooling and local admin rights are Tier 2 credentials, so they are vaulted and elevated on request.

**Support tiers and runbooks.** First line handles access requests, portal sign-in problems and how-do-I questions. Second line, the PAM operations team, handles onboarding, rotation failures, proxy faults and stalled approvals. Third line is engineering and the vendor. Each tier has runbooks for failures that repeat: rotation failed because the target was unreachable, a recording did not upload, a user is locked out of the portal, a credential is stuck checked out. Each says who is paged.

**Break-glass.** Emergency access has to work when the PAM platform, identity provider and MFA service are all down, so it cannot depend on any of them. Microsoft's guidance asks for at least two cloud-only accounts, phishing-resistant sign-in, alerts on every sign-in and validation at least every 90 days. Each use closes with a written justification and rotation. See [break-glass access](/case-studies/break-glass-access/).

**Incident procedures.** I add PAM steps to the response plan: disable an account and rotate every credential it could reach, pull recordings for a time window, freeze approvals, and what to do if the vault itself is suspected.

## 8. Monitoring and audit evidence

Logs help only if they sit outside the reach of the people being logged. Platform logs go to the SIEM in near real time. AU-2 and AU-12 cover choosing and generating events, and AC-6(9) asks for privileged function use to be logged.

I send portal sign-ins and failures, requests, approvals and denials, check-outs, session start and stop, rotations and failures, policy and role changes, and any break-glass use. A named person owns each alert: break-glass use, privileged access with no ticket, after-hours access to the most sensitive systems, failed rotations, direct logins that bypass the broker, and MFA changes on admin accounts.

The test is whether an auditor can follow one session from request to approval to recording to closure without asking me to explain.

## 9. Governance

Governance gets skipped because it is not technical, and it decides whether the design survives its second year.

- **Owners.** Every privileged account, safe or folder and integration has a named owner. The platform has a product owner.
- **Recertification.** Privileged memberships are reviewed on a schedule (AC-6(7), AC-2). Reviewers see what the access does and when it was last used.
- **Policy.** Rotation rules, naming, tier definitions, break-glass and approval rules are written, approved by the business and versioned.
- **Exceptions.** Each has an owner, a reason and an end date.
- **Metrics.** Numbers read straight from the platform: share of in-scope accounts onboarded, rotation failures and their age, accounts without an owner, standing privileged membership, break-glass uses and their reviews. Targets only mean something against your own baseline.

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
| 9 Governance | Access that never gets revoked, unowned policy | Recertification records, policy versions, metrics reports |
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
- No decommission plan for the old tool, so old logs and recordings have no reader.

## Sources

Primary or standards bodies:

- CISA, [Scattered Spider advisory AA23-320A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-320a) (help desk social engineering, phishing-resistant MFA).
- NCSC (UK), [Incidents impacting retailers](https://www.ncsc.gov.uk/blog-post/incidents-impacting-retailers) and [Use privileged access management](https://www.ncsc.gov.uk/collection/secure-system-administration/use-privileged-access-management).
- NIST, [SP 800-63B-4](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf).
- Microsoft, [Enterprise access model](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model) and [Emergency access accounts](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access).

Secondary, so treat them as pointers to the primary text:

- NIST SP 800-53 Rev. 5 control titles and CSF 2.0 PR.AA, read through [CSF Tools](https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-6/) and [PR.AA-05](https://csf.tools/reference/nist-cybersecurity-framework/v2-0/pr/pr-aa/pr-aa-05/).
- CIS Controls v8 safeguard titles, read through the CIS assessment specification for [Control 5](https://controls-assessment-specification.readthedocs.io/en/latest/control-5/) and [Control 6](https://cas.docs.cisecurity.org/en/latest/source/Controls6/).
- Okta, [Account recovery without password resets](https://sec.okta.com/articles/2025/12/account-recovery-without-password-resets/), vendor documentation used as an example of help desk role limits.
- BleepingComputer, [Okta: hackers target IT help desks](https://www.bleepingcomputer.com/news/security/okta-hackers-target-it-help-desks-to-gain-super-admin-disable-mfa/), a news report of Okta's 2023 advisory.

I left PCI DSS v4.0.1 requirements 7 and 8 out. I could not confirm the requirement wording from the PCI Security Standards Council's own text.
