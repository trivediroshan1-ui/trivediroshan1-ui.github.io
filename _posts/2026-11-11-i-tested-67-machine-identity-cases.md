---
title: "I Tested 67 Machine Identity Cases. Here Is Where the Controls Stopped."
layout: post
bg: post-plan
motif: grid
seo_title: "67 Machine Identity Cases: Where Controls Stopped, and 10 Wrong Guesses"
date: 2026-11-11 11:10:00 +0530
author: Roshan Trivedi
tags: [non-human-identity, nhi, pam, shadow-ai, security-testing]
share_title: "I tested 67 machine identity cases"
share_label: "Article · NHI lab"
share_accent: green
description: "I wrote every guess down before any code ran. 57 matched, 10 did not, and in 20 cases a control could be switched off with no change."
---

# I Tested 67 Machine Identity Cases. Here Is Where the Controls Stopped.

*Filed under: Non-human identity · Privileged access*

*Independent work on my own time. All data is made up. Nothing here describes any employer's or client's systems.*

## Why I did this

Most companies hold far more machine identities than people. A lot of them have no named owner, and some never expire. When a control mapping sheet says "service account passwords are rotated", it tells you a control exists. It does not tell you what happens when that control meets a real failure: a consumer that caches the old password, a vendor that gets breached, a token copied off a build runner.

The gap I wanted to test is simple. We review whether a control is present. We rarely test where it stops. I wanted to see where each control stops, and I wanted my wrong guesses on the record, not quietly fixed afterwards. So I set myself one rule before I started.

## The rule: the guess comes first

For each case I did the same six things, in this order:

1. Pick a row from the catalogue and shrink it to one failure with a control that should stop it.
2. Write down the result I expect with the control off and with it on, as numbers where I can.
3. Save that as a guess file, hash it with SHA-256, and commit that file on its own.
4. Write the model and run it, once with the controls off and once with them on.
5. Switch each control off on its own and see whether anything the case measures changes.
6. Compare the result to the guess, and record every miss and every limit.

The order is what makes the guesses honest. A test you design after seeing the result will agree with you. A guess that was committed first cannot be edited later without the hash changing, so anyone can see whether I moved the goalposts. It does not prove I never cheated. It makes cheating visible.

Each of the four runs has its guesses and its code in separate commits on my Mac. For the last run, the guesses went in as commit a2dc1fd and the code and results came after as cbec7a8. In total there are six guess files, each with a published hash, and a small script re-checks the hashes. Every run was repeated on a second machine and the output matched.

One more thing about what a case is. Each case is a small model of a control, running in memory, on a made-up company I called Kaveri Finance. It is not a real vault, directory or cloud tenant. I will come back to what that means for how far you can trust any of this.

## How the lab is built

The structure is deliberately plain:

- The guess files sit in one folder, next to the script that re-checks their hashes.
- Four run scripts hold the models. Each writes its results to a JSON file, one per run.
- One shared module reads the guesses and the results together. Everything a reader sees is built from it: the lab pages, each with an animated workflow for its case, the audit data as CSV and JSON, and an 83 page book.
- A separate check fails the build if any page quotes a number that the data does not hold.

That last check came out of a mistake. After the book grew, one page still gave the old page count, because my check looked for "N pages" and missed the hyphenated "N-page". It reads both forms now. It is a small fix, and it is the same lesson as the rest of the lab: a check that has never failed has not been tested.

## The framework: seven steps

Every case sits at exactly one of seven steps: find, own, limit, store and issue, rotate and expire, watch, and retire and respond. The loop matters because retiring what is unused feeds the next discovery scan.

Here is what each step looked like in the cases, with the case counts.

**Find (6 cases).** You cannot control what you cannot list. In one case, three places held service accounts: the directory, the cloud and the CI system. A directory-only scan found 12 of 27. Merging all three sources found 27 of 27, each with its source. Names are a problem too. In the case "one identity, three names", the same account appeared under different names, so a naive count gave 43 entries for 30 real identities and the findings were split across duplicates. Merging on owner plus name brought it to 29, and one of those merges was wrong. I will come back to that case, because it contains two of my mistakes.

This is the hardest step to model with made-up data. The interesting failures happen in systems nobody listed, and a model can only find what I put in it.

**Own (8 cases).** An identity with no owner cannot be reviewed, rotated or retired safely. With the control off, an identity with no owner was still active on day 31. With it on, it was paused on day 31. In the case where an owning team is disbanded, all 12 identities still showed the old team and stayed active at day 90. With an orphan queue, 9 were claimed, 3 were paused on day 14, and one weekly job broke. That broken job is the cost of the control, and I kept it in the results on purpose.

**Limit (18 cases).** The busiest step. It covers least privilege and a front door that refuses the wrong caller. Examples:

- With standing admin group membership, all 40 members kept access. After a review, 32 were removed and 8 remained, 2 of them broader than they needed.
- With phishing-resistant MFA for admins, 6 bad sign-ins got through. With passkeys and no SMS fallback, none did.
- An AI tool that inherits the full permissions of the person using it could write to all 40 items in the model. Limited to read on one folder, it could write to none.

**Store and issue (10 cases).** Where secrets live and how they are handed out. A long-lived CI variable could be read by another job, and the log said only "pipeline". With a per-job credential, the other job was refused and the log named the job. A secret scan over AI-assisted code and config blocked 6 of 8 fake secrets and let 2 through.

**Rotate and expire (10 cases).** The cases here are about what happens around the rotation, because the rotation itself is easy. When rotation fails silently, nobody knows and the password is 60 days stale. With an alert, the failure shows up on day 1. When you rotate before the consumer is updated, the application fails at its next connection. The control that worked was updating the consumer first, then rotating, then checking that the old secret is dead. A mass rotation after a breach caused 12 outages without a dry run and 0 with one, though 2 identities were left unrotated.

**Watch (7 cases).** Break-glass use, shared accounts and the pipes that carry the evidence. A break-glass account used at 2 a.m. went unnoticed and its password stayed unchanged. With an alert it fired and the password was rotated. In the shared account case, the log said "fw-admin" 12 times. With the control on, all 12 actions were tied to a person.

**Retire and respond (8 cases).** Offboarding things that are not people. After an application was retired, all 3 of its identities still worked 90 days later. Retiring them as part of the decommission disabled all 3 and recorded a ticket. A contractor who never left was a chain test, which I explain below.

The quietest step is find, with 6. The busiest is limit, with 18. That split is partly my own interest and partly because limiting is easy to model as a count of what was granted or refused.

## One case end to end

Here is one case start to finish, because it shows most of what the lab does.

A pipeline job runs and someone copies its token from the runner. They replay it from outside, twice. With the controls off, both replays work. With the controls on, the token is bound to that runner and revoked when the job ends, so both replays are refused.

Then comes the part that makes the lab useful. I switched each control off on its own. I had guessed that a short token lifetime, 10 minutes, would change the result too. It did not. Binding and revocation had already stopped both replays, so removing the lifetime changed nothing the case counts. The short lifetime is still a good idea. My test just could not show it doing anything, because another control was standing in front of it.

That is one of my 10 wrong guesses. I wrote it down as a miss, and I kept the case on the page.

The case also has a limit that stayed. A bound token still works from inside the runner while the job is running. Binding does nothing about that, and no control in my model does.

## What I got wrong

57 guesses matched. 10 did not. Here are all ten, grouped by what kind of mistake they were.

**I did not say what I was counting (2 cases).**

- In the case about a ticket system, an identity provider and a SIEM, I guessed that with the controls off, 0 events would reach the SIEM. The connector delivers 14 of 20 events either way. I never said what I meant by "arrived", so the model took the plain reading and I was wrong on the one in my head.
- In the case where an agent tries to create keys and sub-agents for itself, I guessed 4 alerts. The model gave 5, because it raises an alert on every attempt, including the ones it refuses.

**I treated two controls as independent when one covered the other (3 cases).**

- In the case about a person who never sees the password, I expected the injection of the credential to matter alone, and the rotation to be safe to drop. Neither held. The reveal policy already covers the injection, and without rotation all 3 remembered logins still work.
- In the break-glass drill, I guessed it would find 2 faults. It found 1. A second holder made the other fault harmless without removing it, so the drill never saw it.
- In a case about a low-code agent that nobody registered, I expected 4 agents to hold credentials with the issue rule off. The scan had already got 3 of them registered, so 1 does. I also expected the expiry to go unnoticed. It disables the last agent.

**I picked the wrong control as the one that mattered (2 cases).**

- In the CI runner case above, I expected a short token lifetime to change the replay result. Binding and revocation had already blocked both replays.
- In the forgotten service account chain, I expected the ticket scan to matter most. The owner rule did.

**I got a count wrong (2 cases).**

- In the secrets in AI-assisted code case, I expected the scan to miss 1 of 8 fake secrets. It missed 2. They matched no pattern the scan knew.
- In the copied key case, I guessed 3 alerts. The workload binding refused 6 calls and raised 1 alert.

**My own arithmetic was wrong (1 case).**

- In "one identity, three names", I guessed 51 entries. Nine identities with two or three names each cannot make 51. The count is 43. A rule that stripped trailing digits also merged two real accounts. On the first run I had also given 21 identities one shared owner by mistake, so the merge collapsed them to 11. I fixed the test data and kept the first-run file next to the corrected one.

I also had two mistakes in my test setup, not in the guesses. One was the bad test data I described above. The other was in a chain test: an extra scenario ignored its "late" marker, so I fixed it so the marker sets the attack day to 120, and re-ran. I list these separately because they are different from a wrong guess, and mixing them would flatter me.

Two patterns keep coming back. Twice I did not say what I was counting, so the model answered a different question from the one in my head. Four times, one control had already covered another and I had treated them as separate. Both happen in real control reviews. "The control works" means little until someone writes down what it should change, and by how much.

## Controls nobody would miss

For every case I also switched each control off on its own. That is 133 checks in total. The question for each was: does anything the case measures change?

In 20 cases, at least one control could be switched off with no change. That sounds like those controls are useless. They are not, and the reason matters, because the two reasons need different responses.

**Reason one: another control was already doing the job.** In the case where an identity is created outside the normal process, 10 identities existed with the controls off, 3 of them with no owner or expiry. With the controls on, the cloud policy refused the 3 console-created accounts. The weekly sweep and the automatic expiry then had nothing left to find, so switching them off changed nothing. They are a second line of defence for the day the policy fails. A test that only looks at the outcome cannot see that. Other cases in this group:

- The old-key revocation in the copied key case, because binding to the workload already refused the replays.
- The 90 day rotation in the case where AI-service keys leak into repositories, because revoking on find had already ended the keys.
- The short-lived token in the token-in-a-repository chain, because the commit block stops the attacker at link 1.

**Reason two: the control is not an access outcome at all.** A model that counts who got in cannot measure these controls:

- The log of every elevation in the endpoint privilege case.
- The volume threshold in the session analytics case.
- The scope review and the read log in the case about AI features inside an approved SaaS app.
- A person approving each change in the over-privileged identities case.
- The attestation in the case where an owning team is disbanded.

These still matter. They matter for evidence, for whoever investigates later, and for the day a person asks "who approved this?". My model just has no way to count them.

The practical point: if a control could be switched off tomorrow and none of your checks would notice, find out which of the two reasons it is. The first means you may be paying for something that duplicates another control, or that you are glad to have as a backup. The second means you have a control that nothing measures, and you would only find out it broke during an investigation.

## Chain tests: when one failure leads to the next

Six of the 67 cases are chain tests. An attacker needs a sequence of steps, and I ask which control breaks the chain and at which link.

Two examples:

- **The forgotten service account.** No owner, a password in a ticket, an export shared widely. The attacker signs in from a new network. With the controls on, the attack stops at link 1. For an old account, the ticket scan stops it at link 2.
- **The contractor who never left.** A phished credential gives production access. Expiry stops it at link 3. A sponsor review alone does not stop it at 30 days.

The point of a chain test is that a control can be present and still be at the wrong link. In the contractor case, the sponsor review was in place and did not stop the chain. Expiry did.

These tests are also the weakest evidence in the lab. They are rule models, so the result follows from the rules I wrote. They show that I thought about the links in order. They do not show how a real attacker would behave.

## Limits that stayed

33 cases carry a limit I recorded and could not test away. Rather than list all of them, here are the groups they fall into.

**A person is the control, and a person accepts text.** A made-up ticket number passed the break-glass review, because nothing checks it against the ticket system. A team mailing list that nobody reads was accepted as an owner. A scheduled automation was extended on any written reason. A ticket that was open but belonged to another system was accepted for privileged access. The common thread: justifications and attestations are text that a person reads, and a model, and often a real process, takes the text as given.

**The control stops the wrong thing at the wrong time.** An allowlisted app that is later breached keeps working until someone revokes it. In my model the replay ended after 60 minutes, which is when the revoke ran. When a vendor is breached, the clock starts at their notice, not at your next inventory. A rotation with a 2 hour overlap still fails for a consumer that caches for 3 hours.

**Something sits outside all the controls.** A bound CI token still works from inside the runner. A copied key replayed from inside the real billing workload carries the certificate, so the binding cannot see it. A recording tool on the user's machine sits outside the controls on password reveal. An allowed application that can start a shell passes its elevation on to the shell.

**The signal is too small, too big, or too late.** A large copy spread over many sessions stays under a per-session threshold. Ninety days of use cannot see a job that runs once a year, so its permission is removed too, and the job breaks. The heartbeat that checks a queue travels through the same queue, so a full queue can drop the heartbeat as well.

**Two people, one pattern.** In the separation of duties case, two people approving each other's requests both pass, because each rule looks at one person at a time.

Three of these I would check first, because they are easy to test in a real environment:

1. Does anything check a break-glass ticket number against the ticket system?
2. When a vendor you connected is breached, how long until you can revoke their access?
3. Can a CI token that is bound to its job still be used from inside the runner while the job runs?

## What I would ask on Monday

If I owned identity or security at a company, these are the questions I would ask my own team first. Each comes from a case in the lab.

1. **Can we list every service account across the directory, the cloud and CI, and does each one have a named owner?** In the discovery case, a directory-only scan found 12 of 27. An account with no owner cannot be reviewed, rotated or retired safely.
2. **When a vendor we connected is breached, how many minutes until we can revoke their access?** In the vendor breach case, a replayed token kept reading files until the revoke ran. The grant expiry, at 90 days, was a separate control that also worked.
3. **Which of our sign-offs (ticket numbers, justifications, attestations) is checked by anything other than a person reading it?** In my models, every one of them was accepted as text.
4. **If we switched one control off, would anything tell us?** If nothing would, either another control is covering it, or nothing is. Those need different answers.
5. **Would we know if a rotation silently failed?** In the rotation case, nobody knew and the password was 60 days stale. An alert on day 1 fixed it. And do we update the consumer before we rotate, or after?
6. **What does our AI assistant inherit?** In my model an assistant with a person's permissions could write to all 40 items, and an assistant inside an approved app read 100 files per user, including 100 HR files. Limiting it to one folder and five files per user closed both.

## How to check my work

You do not have to trust my summary. The guess files, the hashes, and the commit ids are public. To check one:

1. Open the audit page on the lab site and find the guess file and its published SHA-256.
2. On your own machine, run `shasum -a 256` on the guess file.
3. Compare the two. If they match, the file is the one I hashed before the code existed.
4. Compare the commit ids on the audit page with the order of the commits in the repository: guesses first, then code and results.

I do not have exact timestamps for the Mac commits in this record, so the order of commits is the evidence, not the clock.

## What this does not show

I wrote the guesses and I wrote the code. A match shows that my model agrees with my own reasoning. It says nothing about how any real product behaves, and I did not test, rate or endorse any product.

The models are small simulations on made-up data. The chain tests are rule models whose results follow from my rules. Some scenario numbers were set to match what a guess described, so they show the shape of an effect, not a real rate. Several of the limits above are assertions about my model, not measurements, and the page says so where it applies.

The catalogue behind the lab has 193 rows. Every row now has a final status, and each of the 46 technical rows I did not run has a reason. Most of those (31) need a real vault, directory or cloud tenant, which a model cannot stand in for.

If you run something like this in a real environment, the misses and the limits are where I would start. They are the part you will not find in a control mapping sheet.

## Everything is public

The 67 cases with their animated workflows, the framework, the audit data (CSV and JSON, CC BY 4.0), the guess files with their hashes, the code and the 83 page book are free to read and reuse:

roshantrivedi.co.in/nhi-lab

If you can think of a case that would break one of these controls, tell me. I will add it, run it with the guess written first, and keep the original on the page.
