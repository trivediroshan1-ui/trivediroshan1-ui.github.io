---
title: "PAM as an Identity: What Changes When the Vault Can Talk to Your Governance System"
layout: post
date: 2026-10-05
author: Roshan Trivedi
tags: [pam, iga, identity-governance, privileged-access, joiner-mover-leaver, access-certification]
description: "Why a privileged account should be managed as an identity with an owner and a lifecycle, what you have to build inside PAM when there is no IGA, and how the plan changes when PAM is linked to one."
---

# PAM as an Identity: What Changes When the Vault Can Talk to Your Governance System

Most PAM programs I have seen start from the vault: which systems go in, which passwords rotate, which sessions get recorded. Every account in the vault belongs to somebody, or used to, and the vault does not know who.

This post treats the privileged account as an identity, with an owner, a lifecycle and a reason to exist. Then it asks what changes if the PAM platform can be linked to an identity governance and administration (IGA) system. It is vendor-neutral. Any product mentioned comes from public documentation and is only an example.

## 1. What "treat it as an identity" means

A privileged account is a credential with a lot of power. An identity is the record of who or what that credential stands for, who answers for it, and when it should stop existing. NIST SP 800-63-4 uses similar language for its subscriber account: a record that identifies the subscriber, holds the authenticators bound to it, and has a status the provider maintains. That guideline is about identity proofing, authenticators and federation, and says it focuses on services for external users, so it does not tell you how to run admin account governance. The idea of an account as a managed record still applies. Before an account goes into a safe I want these answered:

- **Who is it for?** A named person, or a named owner where there is no person.
- **What kind is it?** Personal admin, shared, service, application, break-glass or vendor account.
- **Where does it sit in the person's lifecycle?** Joiner, mover, leaver, and odd cases such as long leave or suspension during an investigation.
- **What can it do, and why?** The entitlements, and the business reason for each.
- **What would make it end?** A date, an event, or a review nobody renewed.

### One person, two accounts

The first decision is separation. An administrator has a daily-use account for mail, chat and browsing, and a separate admin account for privileged work. NIST SP 800-53 Rev 5 AC-6(2) asks that users with privileged access use non-privileged accounts for non-security functions. AC-6(5) restricts privileged accounts to specific people or roles.

Once there are two accounts, the link between them matters. The admin account needs a reliable pointer to the person, held in an attribute and not in a naming habit. A convention such as `adm-` plus the username helps people reading logs, and breaks on the first name change or clash. The pointer I want is an immutable person identifier from the HR-fed identity record, stored on the admin account. SCIM's enterprise user extension carries `employeeNumber` and `manager` for this kind of purpose, and `externalId` exists so the client can keep its own key on the resource (RFC 7643).

Without it, "disable the leaver's admin accounts" is guesswork.

NIST IA-4 adds two points worth borrowing. Identifiers are authorized before they are assigned, and they are not reused for a defined period. Reusing `adm-jsmith` for a different John Smith two years later makes an old audit trail point at the wrong person. The IA-4 guidance also says individual identifier management does not apply to shared system accounts, which is why shared accounts need an owner record instead.

### Entitlements, resources and accounts with no person

Each privileged account carries entitlements: a directory role, a database group, a safe, rights on a cloud subscription. Each points at a resource. If you cannot list both per account, you cannot answer "who can reach production payments". A PAM safe is an entitlement too. Membership of the safe holding the domain admin password is domain admin by a longer route, and it needs the same description and review as the directory group.

Service, application and shared accounts have no manager who moves jobs, and they still need an identity record. I make three fields mandatory: an accountable owner with a named deputy, the system served, and a review date. When the owner leaves, the account is flagged. The [non-human identity case study](/case-studies/non-human-identity-at-scale/) covers discovery and ownership, and the [credential platform strategy](/case-studies/credential-platform/) covers the lifecycle after that. Vendor accounts add an internal sponsor and an end date, as in [third-party and vendor privileged access](/case-studies/vendor-privileged-access/).

### Joiner, mover, leaver for a privileged identity

The lifecycle has two layers, and people handle only one. The person's lifecycle covers the daily account and business roles. The admin account has its own: created when a privileged role is granted, changed when the role changes, ended when the role ends, which can be long before the person leaves.

The mover case is where I see most programs fail. A person moves from the database team to the cloud platform team. HR records the move and the daily account follows. The admin account and safe memberships were never part of that process, so they carry the old role forward. NIST PS-5 expects the opposite: on transfer, review and confirm the continuing need for logical access, and take the transfer actions within a defined time. Collecting new privileges while keeping the old ones is the pattern AC-5, separation of duties, exists to prevent.

The leaver case is simpler and still goes wrong. PS-4 requires disabling system access within a defined time and terminating or revoking the authenticators and credentials tied to the person. PS-4(2) adds automated mechanisms for notification and disabling, and it is required in the High baseline. Disabling the account is half the job. Any shared secret the person could read or had checked out needs to change. AC-2 asks for a process to change shared or group account authenticators when people leave the group, and that is a rotation task.

## 2. PAM without IGA: what you build yourself

With no governance system, or one that does not cover privileged access, the PAM team builds a small identity function inside the PAM platform. I have done this, and it works up to a point. You need:

- An account inventory with owners. Discovery finds accounts and a person decides who owns each, in a spreadsheet or a custom field.
- Owner maintenance. Nothing tells the PAM team when an owner leaves unless you build a report.
- Request, approval and joiner, mover, leaver by ticket. HR to service desk to PAM administrator, each hop a delay, and the ticket and the vault are two records that drift.
- Recertification from PAM reports sent by email, with replies actioned by hand. This is the rubber stamp described in [access recertification](/case-studies/access-recertification/), worse here because reviewers see safe names they do not recognise.
- A reconciliation job comparing HR leavers and movers to PAM accounts and memberships.

It breaks in predictable places:

| Where it breaks | What happens |
|---|---|
| HR to PAM drift | A leaver's admin account stays live for weeks, because the only link is a person reading a ticket |
| Movers | Old privileges stay and new ones are added, because mover events rarely produce PAM tickets |
| Ownership | Service accounts keep a stale owner or none, because no event fires when an owner leaves |
| Recertification | Reviews are approved in bulk, because reviewers see names with no context or usage |
| Separation of duties | Conflicts across systems go unseen, because PAM sees safes and not business roles elsewhere |

AC-5 guidance says separation of duties violations can span multiple systems. PAM sees one slice. It cannot tell you that the person approving payments in the finance application also belongs to the safe that rotates the finance database password.

None of this is a reason to wait for an IGA. Privileged accounts are the highest risk, so the vault goes first. Design it so its identity data can be connected later, and call the manual process a compensating control.

## 3. PAM with IGA: what changes

An IGA system records who is entitled to what, why, who approved it and when it is next reviewed. If PAM can link to it, the identity work moves into the system built for it, and the vault goes back to being a vault.

### Who owns what

| Stays in PAM | Moves to IGA |
|---|---|
| Secret storage and rotation | Who is entitled to a privileged role or safe |
| Checkout, session brokering and recording | Request and approval workflow for that entitlement |
| Just-in-time elevation and time-boxed access | Joiner, mover, leaver triggers from the HR record |
| Break-glass procedure and its alarms | Certification campaigns |
| Session and checkout telemetry | Separation of duties policy and checks |
| Runtime policy: which target, which hours, which approvals | Ownership of accounts, including orphan handling |

The line I use: PAM decides whether this person can use this credential right now. IGA decides whether this person should hold the right to ask.

### The integration patterns

Availability depends on the products. Prove each in a proof of concept.

**1. IGA as the authoritative identity source.** The HR-fed record, with manager, department, status and dates, is the source. The admin account carries the person's identifier from day one.

**2. IGA provisions into PAM.** PAM is a target. The IGA creates and disables PAM users and manages group or safe membership through a connector, SCIM or the PAM's REST API. RFC 7644 defines create, read, replace, an optional PATCH, delete, search and bulk. RFC 7643 defines the `active` flag and a Group resource with members. It also describes `entitlements` and `roles` on a user as values with no standard vocabulary, and makes `groups` on a user read-only, so membership changes go through the Group resource. SCIM gives you plumbing, and you still decide what an entitlement means. It does not say what a target does on deactivation. Whether `active=false` ends sessions or triggers rotation is product behaviour, so test it.

**3. PAM entitlements become IGA entitlements.** Safe membership, PAM roles and group-to-safe mappings are aggregated into the IGA catalog with descriptions, then requested, approved, certified and checked for separation of duties like any other entitlement. A SailPoint developer forum thread, a community discussion and not documentation, describes aggregating a vault by calling its REST API for each safe's members, and says different permission levels on one safe needed separate access profiles. Take it as a hint that per-safe permission levels need modelling.

**4. PAM discoveries feed IGA as accounts needing owners.** An unrecorded account found by discovery arrives in the IGA uncorrelated, and the orphan process finds an owner or retires it.

**5. Events drive PAM actions.** A leaver or mover event triggers revocation in PAM and, where the person could read shared secrets, rotation, with the result recorded in the IGA.

**6. PAM telemetry informs certification.** Checkouts and last session per account or safe member go to the IGA as evidence, so the reviewer sees "no checkout in 180 days" beside the line. Microsoft's public documentation for access reviews of Entra PIM roles shows the idea: reviewers can see a recommendation based on 30 days of sign-in activity, and denials can be applied automatically. That is sign-in activity in a different product and not vault checkouts.

### What must not be linked

- **IGA must not bypass PAM approval.** If an IGA-provisioned role gives standing access to a safe, the PAM-side approval, justification and time limit on checkout is meaningless. IGA grants the right to request. PAM grants the use.
- **Break-glass cannot depend on IGA.** Emergency access has to work when the IGA, the directory and the integration are down. Manage break-glass accounts in PAM or offline under their own procedure. The IGA can see them for ownership and review and stays out of the access path. NIST AC-2(2) expects emergency accounts to be removed or disabled automatically after a set time, which you design in the vault, not in the governance workflow.
- **No circular dependencies.** If the IGA's service credential lives in the vault and the vault needs the IGA to provision its administrators, a failure of either blocks recovery of the other. Break the loop with a documented bootstrap path.
- **An IGA outage must not block revocation.** PAM should accept a direct disable from an authorised person when the IGA is down, and reconcile when the link returns.
- **Scope the connector account.** One that can change safe membership is itself a path to everything. Give it minimum operations, monitor it, and review it like any privileged identity.
- **Secret values never move.** Only identity and entitlement data goes to the IGA.

## 4. Sequencing and the course of action

Vault the highest-risk accounts first, and settle the identity model at the start. What I build first, whatever the IGA situation:

1. A privileged account standard: admin account separate from daily account, link to the person's identifier, naming, owner rules for non-person accounts.
2. The inventory, with owners, from [the PAM program's discovery stage](/case-studies/privileged-access-program/).
3. Break-glass procedure, independent of everything else.
4. Joiner, mover, leaver rules for privileged roles written down, even if run by hand at first.

Then the course of action depends on the IGA situation:

| | No IGA | IGA planned | IGA mature |
|---|---|---|---|
| **Identity source** | HR export or directory, read by a script | Same, with a data model matching what IGA will use | IGA is authoritative |
| **Account owner** | Custom field in PAM | Same field, named so it can be mapped | Held in IGA, pushed or read by PAM |
| **Joiner, mover, leaver** | Ticket plus a weekly reconciliation job | Reconciliation job, with the mover rules written as policy | Event-driven from IGA to PAM |
| **Request and approval** | Service desk ticket | Ticket with consistent entitlement names | IGA request and approval, PAM enforces use |
| **Recertification** | PAM report to spreadsheet, quarterly | Same, but with usage data and owner column ready for import | IGA campaigns with PAM usage evidence |
| **SoD** | Manual list of known conflicts | List them now in the format IGA will need | Policy checks at request time |
| **Main risk** | Drift and manual error | PAM-only processes that must be redone | Over-linking, bypassing PAM approval |

When an IGA is coming, three things change in the plan. Entitlement names and descriptions become a deliverable, because IGA reviewers will read them. The integration becomes its own wave with its own test cycle. And the PAM owner takes a seat in the IGA design, because privileged roles are what auditors ask the IGA to prove first.

When a mature IGA exists, the PAM project starts by connecting to it. I would build only what must stay in PAM, and test the integration in a lower environment with go/no-go criteria like any other phase.

## 5. A mover and a leaver, end to end

Illustrative flows with invented details.

**Mover.** Priya is on the database team with an admin account and membership of two database safes. HR records a transfer to cloud platform, effective Monday.

1. The IGA receives the change and recalculates her business roles.
2. Because her department changed, it opens a review of her privileged entitlements. Her manager and each safe owner confirm or remove, with last checkout shown. After the deadline the default is removal.
3. Unconfirmed memberships are removed through the PAM connection.
4. The cloud admin role is requested through the normal workflow, with an SoD check against her remaining access.
5. The IGA grants the right to request the role. She still checks out and justifies each use in PAM.
6. The IGA reads PAM membership back and confirms the old safes are gone. A mismatch opens a task.

**Leaver.** Marcus, a platform engineer, resigns, with Friday as his last day. He has a daily account, an admin account, and checked out two shared credentials in the past 90 days.

1. HR sets the end date. On the day the IGA disables both accounts and removes his PAM user and safe memberships.
2. PAM ends open sessions and rotates the two credentials he used, plus any others in his safes that the rotation policy covers.
3. Service accounts he owned are flagged as ownerless and assigned to the team lead until a proper owner is named.
4. The IGA reads PAM state again and closes the record only after that check. The evidence holds the HR event time, disable time, rotation time and verification.
5. If the IGA is down, PAM staff disable him directly the same day and the IGA reconciles later.

Steps 2 and 3 set a privileged leaver apart. He leaves secrets behind as well as an account.

## 6. The audit angle

Auditors ask four things about privileged access: who has it, who approved it, was it reviewed, and what happens when someone leaves. With PAM alone the answers sit in different places. With the IGA link, one record can show request, approval, entitlement, review and removal.

The NIST SP 800-53 Rev 5 controls involved are AC-2 (with AC-2(1) automated account management, (2) automatic removal of temporary and emergency accounts, (3) disabling inactive accounts or accounts no longer tied to a user, (4) automated audit of account actions, (7) privileged user accounts and (13) high-risk individuals), AC-5, AC-6 (especially (2), (5), (7) and (9)), IA-4, PS-4 and PS-5.

I map each to a named owner and a piece of evidence in the register, as in [audit and control mapping](/case-studies/audit-mapping/). Two cautions. NIST leaves the time periods to the organization, so "within 24 hours" is your number and you will be held to it. And the evidence must come from systems the PAM and IGA administrators cannot edit.

## 7. Metrics

Define these in advance and measure them from system data:

- Privileged accounts with a named, active owner, and the count without one.
- Time from HR leaver or mover event to privileged access removed, median and worst case.
- Leaver accounts still enabled after the policy window. Track every exception.
- Privileged entitlements unused in the review window, and how many the last campaign revoked.
- Break-glass uses, each with a recorded reason and review.
- Mismatches between IGA and PAM per reconciliation run, and orphaned privileged accounts with their age.

Targets are yours to set. I left out benchmark figures because I could not trace any to a source I trust.

## 8. Mistakes I would avoid

- Starting the vault with no owner field. Adding owners to thousands of accounts later is its own project.
- Linking before cleaning. A messy PAM connected to a new IGA puts the mess into the system meant to fix it.
- Letting IGA grant standing access to safes, which turns a just-in-time control into a permanent one.
- Putting break-glass inside a workflow. Emergency access that waits for an approval chain is a delay.
- Treating certification as the control. Removal is the control, and it has to be checked in the target system.
- Ignoring non-person accounts. Leaver processes fire for people, so service accounts need an owner-change event.
- Never testing the failure path. Switch the IGA link off in a test and see what the PAM team can still do.

## Sources

Primary or near-primary, fetched during research:

- NIST SP 800-53 Rev 5: AC-2 and enhancements, AC-5, AC-6, IA-4, PS-4, PS-5. I read these on the CSF Tools mirror (csf.tools), a secondary copy of NIST's text. Check wording and baseline assignments at csrc.nist.gov before quoting.
- IETF RFC 7643, SCIM Core Schema, and RFC 7644, SCIM Protocol (rfc-editor.org).
- NIST SP 800-63-4, Digital Identity Guidelines (pages.nist.gov/800-63-4), for the subscriber account wording and its stated scope.
- NIST NCCoE SP 1800-9 draft, Access Rights Management for the Financial Services Sector (2017, development ceased July 2022). Dated. It describes automated joiner, mover and leaver provisioning from an HR feed, with PAM as a capability in the reference design.
- Microsoft Learn: Privileged Identity Management overview, and access reviews of roles in PIM. An example of usage-based recommendations only.

Secondary, treat accordingly:

- SailPoint Developer Community forum thread on integrating a vault with an IGA using REST APIs. A practitioner discussion, not documentation.

Not verified: I read no vendor documentation for any PAM to IGA connector. Nothing here states what a specific product does.

*Roshan Trivedi works on identity, access and privileged access security. More at [roshantrivedi.co.in](https://roshantrivedi.co.in).*
