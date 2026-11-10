---
title: "I Ran the 19 Cases I Had Been Putting Off. Five Guesses Were Wrong."
layout: post
bg: post-plan
motif: grid
seo_title: "Non-Human Identity Lab Round 19: 19 More Cases, 5 Wrong Guesses"
date: 2026-11-10 22:50:00 +0530
author: Roshan Trivedi
tags: [non-human-identity, nhi, pam, shadow-ai, security-testing]
share_title: "I ran the 19 cases I had been putting off"
share_label: "Article · NHI lab"
share_accent: green
description: "19 more machine identity cases on made-up data. Five guesses were wrong, and in 14 control checks nothing changed."
---

# I Ran the 19 Cases I Had Been Putting Off. Five Guesses Were Wrong.

*Filed under: Non-human identity · Privileged access*

*Independent practitioner write-up. Last reviewed 10 November 2026. Everything here comes from my own public lab on made-up data. It does not describe any employer's systems, data or projects.*

## The short version

- My non-human identity lab had 19 cases that I had designed and never run. I ran them today as round 19: 6 on non-human identities, 10 on privileged access and 3 on shadow AI.
- Same method as before. I wrote the guesses, hashed the file and committed it before any code existed.
- Five of the 19 cases had at least one wrong guess.
- In 14 of 57 control-off checks, switching the control off changed nothing the case counts.
- The lab now has 67 cases. 57 matched every guess and 10 did not. All 10 are on the page.

## Three of the misses

**A drill.** I guessed it would find two faults. It found one. A routing check catches the alert fault before the drill runs, and a second holder makes the sealed copy fault harmless without removing it.

**A connector.** I guessed that 0 events would get through without controls. The connector delivers 14 of 20 and drops 6 whether or not a heartbeat exists. The heartbeat adds the alarm and the replay. It does not change delivery.

**An alert count.** I guessed 4 alerts. The model alerts on each of the 5 creation attempts, refused or not. Alerting only on the ones that succeed would give 1. I never wrote down which I meant.

Two of the five misses are the same mistake: I did not say what I was counting. In the other two I treated controls as independent when one of them covers the other.

## Controls that changed nothing

In 10 of the 19 cases, at least one control could be switched off alone without changing anything the case counts. There are two reasons.

For 6 of them, another control already does the job. The cloud policy refused the 3 console accounts, so my weekly sweep had nothing left to find. That makes the sweep a second line of defence, and a check that only looks at the result cannot tell it is there.

For the other 8, the control is a log, a review, an approval or a threshold. A model that counts access outcomes cannot see those. They still matter for evidence and for the people who investigate later.

## Every catalogue row now has a status

The catalogue has 193 rows. Of the 147 technical rows, 60 were run in this lab, 35 were tested in an earlier lab, 6 were partly tested and 46 were not run. Each of those 46 has a reason:

- 31 need a real product or environment.
- 8 are plans or process.
- 5 are covered by a nearby case.
- 1 cannot be tested with made-up data.
- 1 is a signal list.

The other rows are 20 chains (6 run, 14 documented only) and 26 business use cases. Of those, 10 are supported by a case, 11 partly, 3 have no case and 2 are not tested here. I would rather show a row as not run, with the reason, than let a gap look like coverage.

## What I would take from it

1. When you write an expected result, write what is being counted.
2. Before you call a control redundant, check whether another control is hiding it.
3. Keep the logs and reviews. A test that counts outcomes cannot measure them.

## Limits of this lab

One author wrote the controls, the models and the guesses. The models are small simulations on made-up data. Some scenario numbers were set to match what my guess described, so they show the shape of an effect and not a real rate. No product was tested, so none is endorsed or criticised.

## Sources

All figures come from my own published lab. Read the [round 19 results](https://roshantrivedi.co.in/nhi-lab/round-19/), the [register of all 193 rows](https://roshantrivedi.co.in/nhi-lab/register/), the [method](https://roshantrivedi.co.in/nhi-lab/method/) and the [audit data](https://roshantrivedi.co.in/nhi-lab/audit/). The free 83 page book is on the [Book page](https://roshantrivedi.co.in/book/).

**Roshan Trivedi** writes about privileged access, identity and AI governance at [roshantrivedi.co.in](https://roshantrivedi.co.in). The lab, the animated workflows and the audit data are free to read and reuse. Newsletter: [buttondown.com/trivedi](https://buttondown.com/trivedi).

*All data in the lab is made up. Nothing here relates to any employer or real company.*
