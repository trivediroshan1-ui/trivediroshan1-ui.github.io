---
title: "A PAM Project Plan for Tier 1, 2 and 3 Organisations"
layout: post
date: 2026-10-03
author: Roshan Trivedi
tags: [pam, iam, privileged-access, project-planning, zero-standing-privilege]
description: "How I size a privileged access management project from readiness gates and capacity inputs, and turn that into a 90, 180 or 365 day plan with phases, exit criteria and deferrals."
---

# A PAM Project Plan for Tier 1, 2 and 3 Organisations

*Filed under: Privileged Access · Project Planning*

People ask me for the standard length of a PAM project. There isn't one. I looked in the NIST, NCSC and Microsoft guidance and found no published duration or effort benchmark. Those sources give an order of work and a way of thinking about risk. The numbers have to come from your own inventory.

This post is how I get from "we bought a tool" to a plan of 90 to 365 days: readiness, capacity, a sizing formula you can change, then the plan. Where a number is mine, I say so.

## What I mean by tier

I use tier for the size of the organisation.

- **Tier 1:** large enterprise. Many sites or regions, thousands of administrators and assets, several regulators.
- **Tier 2:** mid-size. One or two regions, a few hundred privileged users, a platform team that is also doing other things.
- **Tier 3:** small. A handful of administrators, one main environment, often one person who owns identity, infrastructure and security.

This is my assumption, and size is only one axis. Maturity is the other. A small company with a clean CMDB, SSO everywhere and an owner for every system can move faster than a large one with none of those. Read the tiers below as starting points, then adjust for maturity.

One naming clash to avoid. NCSC and others also use "tier" for the risk level of an administrative function, where Tier 0 is the root of trust such as domain admins and cloud root accounts ([NCSC, risk manage administration using tiers](https://www.ncsc.gov.uk/collection/secure-system-administration/risk-manage-administration-using-tiers)). In this post, tier means organisation size. When I mean risk, I say risk level or wave.

## Step 1: find out where the organisation actually is

A plan that assumes a signed contract when there isn't one is fiction. I put these questions to the sponsor in the first week. The earlier stages are in [how I run a privileged access program](/case-studies/privileged-access-program/) and [how I compare platforms](/case-studies/platform-evaluation/). This is the intake form.

| Gate | Question | If the answer is no |
|---|---|---|
| Business case | Is it approved, with a named budget holder? | Stop. Nothing below is funded. |
| RFC / change | Has the change been raised and approved, including freeze periods? | Plan can start, build cannot touch production. |
| POC | Is it complete, with written results signed off by security and the platform owner? | Treat the first phase as a POC. See the scenarios table. |
| Tool selected | Is the decision recorded, with the reasons? | Design work can start, product-specific work cannot. |
| Contract | Is it signed, with licence counts and dates? | No vendor support, no licence keys, no firm dates. |
| Professional services | Are PS hours bought, with named people and dates? | Internal team carries the build, and the plan stretches. |
| Licences | Do they cover privileged users, targets and any session or secrets modules in scope? | Scope shrinks to what is licensed. |
| Platform team | Are named people assigned, with time protected? | Hard blocker. See below. |
| Target owners | Does each in-scope system have a named owner who will answer? | Onboarding stalls at wave 2. |
| Asset source | Is there a CMDB, cloud inventory or discovery output I can trust? | Add a discovery phase and a reconciliation step. |
| IdP, SSO, MFA | Is the identity provider ready for the PAM front door, with MFA for privileged users? | Integrations phase moves to the critical path. |
| Ticketing | Is there an owner for the ITSM integration and a ticket type for access requests? | Approvals stay manual or use the tool's own workflow. |
| SIEM | Is there an owner for the log pipeline and a person to build detections? | Logs exist but nobody reads them. |

NCSC's PAM guidance ties administrator access to a recorded reason, ideally a support ticket, and lists rule-based approval through ticketing as one of three approval models ([NCSC](https://www.ncsc.gov.uk/collection/secure-system-administration/use-privileged-access-management)). Without a ticketing owner you lose that.

## Step 2: capture capacity

Readiness tells me whether I can start. Capacity tells me how long the work is. I collect these inputs in a spreadsheet, with the source of every number.

| Input | What I record | Why it drives effort |
|---|---|---|
| Privileged users | Humans with admin rights, split by function: infrastructure, database, cloud, network, security, helpdesk | Training, enrolment, MFA checks, access reviews. Also licence count. |
| Non-privileged users | Count only | Affects SSO load and the support desk. Little build effort. |
| Admin account types | Shared accounts, named admin accounts, break-glass, emergency, vendor, local admin | Each type needs a different onboarding rule. |
| Assets by platform | Windows, Linux, Unix, databases by engine, network devices, hypervisors, cloud accounts and subscriptions, SaaS admin consoles | Each platform is a pattern to build once, then repeat. |
| Service accounts | Count, owner known or unknown, interactive or not, used by scripts or services | The slowest part of most programs. |
| Applications | Apps with embedded credentials, apps needing a vault API or agent | Needs code or config change by someone else. |
| Use cases | A written list, each with a start and an end | The most useful single number. |
| Teams | Distinct teams who administer systems | Each one needs a conversation, training and an owner. |
| Change windows | Frequency and length, per platform | Caps how fast rotation and agent rollout can happen. |
| Vendor support | Hours, response times, named engineers, region | Sets how fast blocked issues clear. |
| Sites and regions | Count, plus data residency or network segmentation limits | Each adds gateways, HA and DR. |

A use case is one complete administrative job, written in one line. "Database admin connects to a production database through the broker, with approval, recorded." "Cloud root is checked out for break-glass, with two approvers, then rotated." "Pipeline fetches a database credential at runtime." Thirty-five of these is a very different project from six.

I reconcile users and assets against at least two sources each, for example directory and HR, CMDB and cloud inventory. They rarely agree, and the gap tells me how much discovery to plan.

## Step 3: turn capacity into effort

This is a planning model, not a benchmark. The unit costs are mine, chosen to be round and easy to challenge. Replace them with timings from your POC, your vendor's PS team and your own earlier projects.

The formula, in person-days:

```
Core        = 40 + 15 x (sites - 1) + 10 x max(0, integrations - 3)
Patterns    = 5 x number of onboarding patterns
Assets      = (servers x 0.5h + databases x 2h + network x 1h
               + cloud accounts x 4h) / 8
Service acc = 0.3 x service accounts in scope
Apps        = 3 x applications in scope
Use cases   = 3 x use cases
Teams       = 2 x teams
Users       = 0.1 x privileged users in scope

Subtotal    = sum of the above
Overhead    = 20% of subtotal (project management, change, rework)
Total       = Subtotal + Overhead
Person-weeks = Total / 5
Weeks to deliver = Person-weeks / (team size x focus factor)
```

What each term assumes:

- **Core** covers design, platform build, HA and the first three integrations (SSO/MFA, ticketing, SIEM). Extra sites add gateways and failover tests.
- **Patterns** are distinct combinations of platform and access method, for example Linux over SSH or one database engine. Five days covers the connection, policy, rotation script, test and runbook, once.
- **Assets** are hours per asset after the pattern works. Databases and cloud accounts cost more than servers because of owners, dependencies and roles.
- **Service accounts** at 0.3 days assumes a mix of simple and awkward ones. Raise it if many have unknown owners.
- **Applications** at 3 days is for apps that need a change to read from the vault. The cost is mostly coordination with another team.
- **Focus factor** of 0.7 allows for incidents, leave and meetings. Use less if the team also runs production.

### Worked example, small organisation

Inputs: 40 privileged users, 110 servers, 15 databases, 20 network devices, 5 cloud accounts, 25 service accounts, 3 applications in scope (the rest deferred), 6 use cases, 4 teams, 1 site, 3 integrations, 4 patterns.

| Term | Calculation | Person-days |
|---|---|---|
| Core | 40 + 0 + 0 | 40.0 |
| Patterns | 5 x 4 | 20.0 |
| Assets | (110 x 0.5 + 15 x 2 + 20 x 1 + 5 x 4) / 8 = 125 / 8 | 15.625 |
| Service accounts | 0.3 x 25 | 7.5 |
| Applications | 3 x 3 | 9.0 |
| Use cases | 3 x 6 | 18.0 |
| Teams | 2 x 4 | 8.0 |
| Users | 0.1 x 40 | 4.0 |
| Subtotal | | 122.125 |
| Overhead | 20% | 24.425 |
| **Total** | | **146.55 (29.3 person-weeks)** |

With a team of four (four full-time equivalents across two internal engineers, a PS engineer and a part-time owner) and a focus factor of 0.7, that is 29.3 / (4 x 0.7) = 10.5 weeks of delivery. Add two to three weeks for gates, change approval and slack, and you get the 13 weeks that make up the 90-day plan.

### The same method at the other two sizes

| | Small | Mid | Large |
|---|---|---|---|
| Privileged users | 40 | 250 | 1,500 |
| Servers / DBs / network / cloud accounts in scope | 110 / 15 / 20 / 5 | 1,500 / 150 / 120 / 30 | 7,000 / 800 / 800 / 200 |
| Service accounts in scope | 25 | 200 | 1,500 |
| Applications in scope | 3 | 15 | 80 |
| Use cases | 6 | 15 | 35 |
| Teams | 4 | 12 | 30 |
| Sites / integrations / patterns | 1 / 3 / 4 | 2 / 4 / 7 | 4 / 6 / 10 |
| Total person-days | 146.55 | 552.3 | 2,409.0 |
| Person-weeks | 29.3 | 110.5 | 481.8 |
| Team size (people) | 4 | 7 | 14 |
| Weeks of delivery at 0.7 focus | 10.5 | 22.5 | 49.2 |
| Plan length chosen | 90 days | 180 days | 365 days |

The large example is already trimmed to the part of a bigger estate that fits in twelve months. When the weeks come out longer than the sponsor will accept, the answer is a smaller first scope or a bigger team. The usual mistake is to squeeze the same scope into a shorter calendar and call it a plan.

## Step 4: the plan skeleton

Every plan I write has the same phases. The size of each one changes. This order follows the same logic as the published guidance. Microsoft's privileged access strategy asks for "ruthless prioritization", meaning the most effective actions with the fastest time to value first ([Microsoft, success criteria for privileged access strategy](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-success-criteria)). Its rapid modernization plan starts with separating and managing privileged accounts, including emergency access accounts, before it moves to credential experience and admin workstations ([Microsoft, RAMP](https://learn.microsoft.com/en-us/security/privileged-access-workstations/security-rapid-modernization-plan)).

1. **Foundation and design.** Confirm scope and use cases, agree account types, naming and ownership rules, choose the HA and DR pattern, write the onboarding standard per platform, name the owners and agree what "done" means for an account.
2. **Platform build and HA.** Non-production first, then production, with failover, backup and restore, and monitoring of the platform itself. NCSC says to treat the PAM system as a critical attack surface and to plan for outages and break-glass ([NCSC](https://www.ncsc.gov.uk/collection/secure-system-administration/use-privileged-access-management)). I test a restore before the first real secret goes in.
3. **Integrations.** SSO and MFA for the front door, ticketing for approvals and reasons, SIEM for logs. Add the directory and the inventory feed. Each integration gets an owner and a test.
4. **Pilot.** A few friendly administrators, a few systems per pattern, real work, long enough to see one change window and one failure.
5. **Onboarding waves, by risk.** Detailed below.
6. **Just-in-time access.** Move from standing membership of admin groups to requested, time-boxed access. This is the step covered in [PAM modernisation and zero standing privilege](/case-studies/pam-modernization/). NCSC describes JIT as using the credential to request access instead of to reach the interface directly.
7. **Session monitoring and recording.** Route sessions through the broker, record them, send the metadata to the SIEM, decide who reviews what and how often.
8. **Operations handover.** Runbooks, on-call, backup tests, upgrade plan, access review calendar and a named service owner. The project is finished when someone else runs it.
9. **Decommissioning.** Close direct paths, retire old vaults, spreadsheets and shared credentials, and remove the firewall rules for the old route. If you are replacing a tool, [the migration method](/case-studies/migration-planning/) covers cutover and rotation.

### Onboarding waves

I order waves by what an attacker would want first. NCSC puts the root of trust, such as root domain admins and cloud root accounts, at the top of its risk list, so those go first.

| Wave | Scope | Notes |
|---|---|---|
| 0 | Break-glass and emergency accounts, cloud root accounts, directory domain admins | Few accounts, highest impact. Test the emergency path before anything else. |
| 1 | Server administrators: Windows, Linux, Unix, hypervisors | Bulk onboarding once the pattern works. |
| 2 | Databases | Needs application owner sign-off. Rotation can break connection strings. |
| 3 | Network and security devices | Often a mix of local accounts and TACACS or RADIUS. Check what the vendor tooling supports. |
| 4 | Service accounts | Find consumers first. Rotate only after you know who breaks. |
| 5 | Applications and pipelines | Needs changes in code or config. See [the credential platform approach](/case-studies/credential-platform/). |
| 6 | Vendors and third parties | Needs contract terms, approvals, time-boxed access and a named internal sponsor. |

Wave 4 is where schedules slip. A service account is easy to vault and hard to rotate, and rotation is what breaks things. I vault first, find who uses the account, then rotate with a rollback plan.

## Step 5: three plans

All three assume the gates in Step 1 are closed before day 1. Each table shows the phase, exit criteria and what is deferred. The tables show what the team does in each phase, what has to be true to leave it, and what is left for later.

### 90 days: small organisation, few use cases

| Days | Phase | What happens | Exit criteria |
|---|---|---|---|
| 1 to 14 | Foundation | Confirm use cases, list privileged accounts, name owners, agree account rules | Use case list and account inventory signed by the sponsor |
| 15 to 35 | Build and integrations | Install, single-node plus tested backup restore or simple HA pair, SSO with MFA, ticketing, log forwarding | Admin can sign in with MFA, restore tested, logs visible in SIEM |
| 36 to 49 | Pilot | Three to five administrators, one system per pattern | Pilot users do real work with no direct fallback needed |
| 50 to 63 | Waves 0 and 1 | Break-glass, cloud root, domain admins, servers | Wave 0 accounts vaulted and rotated, emergency path tested |
| 64 to 77 | Waves 2 and 3, session recording | Databases, network, recording on for the broker | Sessions to these systems go through the broker |
| 78 to 90 | Handover and cleanup | Runbooks, access review set up, direct paths closed for onboarded systems | Service owner named, first access review done |

Deliberately deferred: most applications, vendor access, full JIT for every role, dynamic secrets, advanced reporting. Service accounts with unknown owners are listed and assigned, and not rotated yet.

### 180 days: mid-size organisation

| Days | Phase | What happens | Exit criteria |
|---|---|---|---|
| 1 to 21 | Foundation | Use cases, account taxonomy, discovery against the asset source, owner confirmation | Reconciled inventory, owners named for wave 0 to 2 systems |
| 22 to 56 | Build, HA and integrations | Two-site build, DR test, SSO/MFA, ticketing, SIEM, directory | Failover tested, restore tested, integrations signed off by their owners |
| 57 to 77 | Pilot | One team per pattern, real change window | Defects triaged, onboarding standard revised |
| 78 to 105 | Waves 0 and 1 | Break-glass, root, domain admins, servers in batches | Wave 0 rotated and tested, server batches reconciled against inventory |
| 106 to 133 | Waves 2 and 3 | Databases, network | Owners signed off, rotation tested in a window |
| 134 to 156 | Wave 4 and JIT for highest-risk roles | Service account discovery and vault, JIT for domain and cloud admin roles | Standing membership of the targeted groups removed |
| 157 to 170 | Session monitoring | Recording and SIEM alerts on broker sessions | Review process running with a named reviewer |
| 171 to 180 | Handover and decommissioning | Operations takeover, close old paths | Run team has done an upgrade or restore drill |

Deliberately deferred: applications beyond the first group, vendor access beyond a pilot, dynamic secrets, JIT for lower-risk roles.

### 270 to 365 days: large organisation, many use cases

At this size I divide work by region or business unit under a central design authority.

| Days | Phase | What happens | Exit criteria |
|---|---|---|---|
| 1 to 45 | Foundation and design authority | Use cases by business unit, account taxonomy, regional constraints, onboarding standards, vendor PS plan | Design signed by security, infrastructure, audit and regional leads |
| 46 to 110 | Build, HA, DR, integrations | Multi-site build, DR test, SSO/MFA, ITSM, SIEM, directory, CMDB feed | Cross-site failover tested, integration owners signed off |
| 111 to 150 | Pilot in one region | One team per pattern in one region, real change windows | Onboarding standard stable, runbooks drafted |
| 151 to 190 | Wave 0 and wave 1 | All break-glass, root, domain admins, servers by region | Wave 0 rotated, server batches reconciled |
| 191 to 290 | Waves 2 to 5 | Databases, network, service accounts, first group of applications, in regional batches | Owner sign-off per batch, consumers identified before rotation |
| 291 to 340 | JIT, session monitoring, wave 6 | JIT for high-risk roles, recording and review, then vendors by access level | Standing privilege removed for targeted roles, each vendor has a sponsor and a time limit |
| 341 to 365 | Handover and decommissioning | Operations takeover, close direct paths, retire old tools | Service owner accepts, old paths verified closed |

Deliberately deferred: the rest of the estate outside the scope numbers, long-tail applications, dynamic secrets beyond a first pipeline, JIT for lower-risk roles. The deferred list goes into the plan with an owner and a date.

## Step 6: what changes when the gates are not closed

| Situation | Effect on the plan |
|---|---|
| Contract not signed | Design, inventory, discovery and owner work can start. Anything that needs the product waits. I do not put dates on build tasks, and I say so. |
| POC incomplete | The first phase becomes the POC with the pass marks written first. Add the POC duration before day 1. Do not let the POC quietly turn into production. |
| No PS hours | The internal team carries the build. Use the formula with a lower focus factor and add a learning phase. Pay for a short, targeted PS engagement for HA design and the first pattern if the budget allows. |
| Platform team missing | Hard stop for anything past design. A PAM platform needs named people to run it. A project without them produces something nobody owns. |
| Asset source unreliable | Add a discovery phase. Use discovery output as the baseline and treat the CMDB as a claim to be checked. |
| IdP or MFA not ready | Fix it first. Putting a vault behind weak authentication moves the risk and does not remove it. |
| Target owners not named | Waves 2 to 6 slip. Escalate through the sponsor before the wave starts. |

## Risks and change management

- **The platform becomes the target.** It holds the keys to everything. Harden it, monitor it, patch it and test the restore.
- **Lockout.** A rotation fails or the broker is down at 2 a.m. Wave 0 includes a tested emergency path, and every wave has a rollback.
- **Workarounds.** If the broker is slow, administrators will use the old route. Close direct paths as each wave completes, and fix the friction that drove them there.

Administrators are the users. If they dislike the tool, the program fails quietly. I talk to each team twice before its wave, first to hear what they do and what worries them, then to show the workflow on their own systems. Training uses their real tasks. Each team gets a date when direct access closes, announced early and held. I also tell leadership plainly that standing admin rights go away. That is the point.

## How I measure progress

I measure coverage of the real population. Each of these is a ratio with a clear denominator from the inventory, reported by wave:

- **Privileged accounts vaulted** out of privileged accounts known.
- **Accounts with a named owner** out of accounts in scope.
- **Accounts rotated since onboarding** out of accounts vaulted.
- **Privileged sessions through the broker** out of all privileged sessions seen in logs on in-scope systems.
- **Standing privilege reduced.** Count of members in privileged groups and roles before and after, per group.
- **Direct paths closed** out of systems onboarded.
- **Access reviews completed** out of reviews due.

I do not set a target percentage in advance because I have no source for one. I agree targets with the sponsor after the first wave, when we can see the real numbers. The measures line up with the NIST SP 800-53 controls most auditors will ask about: restricting privileged accounts (AC-6(5)), reviewing user privileges (AC-6(7)) and logging the use of privileged functions (AC-6(9)).

## Common mistakes

- Starting the build before the gates are closed, or promising a date before the contract is signed.
- Sizing by asset count alone and ignoring use cases, service accounts and teams.
- Vaulting the account and leaving the direct login open.
- Rotating service account passwords before finding who uses them.
- Leaving break-glass for the end, or skipping the restore test.
- Treating the CMDB as correct without checking it.
- Declaring the project done before operations has taken over, and hiding the deferred list so "phase 2" never gets an owner.

## Sources

Primary, fetched and read for this post:

- NCSC, [Secure system administration](https://www.ncsc.gov.uk/collection/secure-system-administration), the collection and its six steps.
- NCSC, [Use privileged access management](https://www.ncsc.gov.uk/collection/secure-system-administration/use-privileged-access-management). Used for JIT, approval models, ticket-linked reasons, protecting the PAM system, HA and break-glass.
- NCSC, [Risk manage administration using tiers](https://www.ncsc.gov.uk/collection/secure-system-administration/risk-manage-administration-using-tiers). Used for risk tiers and the root-of-trust ordering.
- NCSC, [Principles for secure privileged access workstations](https://www.ncsc.gov.uk/collection/principles-for-secure-paws). Used for the point that high-risk access is determined by impact if misused.
- Microsoft Learn, [Rapidly modernize your security infrastructure](https://learn.microsoft.com/en-us/security/privileged-access-workstations/security-rapid-modernization-plan). The page names 90-day review checks for emergency access and privileged role identification. It gives no overall timeline.
- Microsoft Learn, [Success criteria for privileged access strategy](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-success-criteria). It gives principles and no numeric targets.

Secondary, flagged:

- [CSF Tools, NIST SP 800-53 Rev 5 AC-6](https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-6/), a mirror of the catalogue, used for the AC-6(5), (7) and (9) titles. Check against NIST before quoting in an audit document.

Every duration, unit cost and focus factor in the sizing section is my planning assumption. No source above publishes them.
