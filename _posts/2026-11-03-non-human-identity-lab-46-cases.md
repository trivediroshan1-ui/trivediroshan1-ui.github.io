---
title: "I Tested 46 Non-Human Identity Cases. My Guesses Were Wrong in Four."
layout: post
bg: post-plan
motif: grid
seo_title: "Non-Human Identity Controls: A 46 Case Public Test"
date: 2026-11-03 00:30:00 +0530
author: Roshan Trivedi
tags: [non-human-identity, nhi, pam, iam, service-accounts, security-testing]
share_title: "I tested 46 machine identity cases"
share_label: "Article · NHI lab"
share_accent: green
description: "46 machine identity cases on made-up data, with every guess hashed before the code ran. Four guesses were wrong, and in eight cases my tests could not see a control working."
---

# I Tested 46 Non-Human Identity Cases. My Guesses Were Wrong in Four.

*Filed under: Non-human identity · Privileged access*

*Independent practitioner write-up. Last reviewed 3 November 2026. Everything here comes from my own public lab on made-up data. It does not describe any employer's systems, data or projects.*

**Update, 10 November 2026.** A third run added 2 cases, on insecure authentication and on keeping test away from production. One guess was wrong, so the lab now has 48 cases and 5 wrong guesses. The numbers below are as I published them on 3 November. The new cases are on the [round 18 page](/nhi-lab/round-18/).

## The short version

- I built a small lab for non-human identities: service accounts, tokens, break-glass accounts, vendor access and AI tools that hold credentials. It has 46 cases.
- For every case I wrote down what I expected to happen, hashed the file with SHA-256 and committed it before running any code.
- 42 guesses matched. 4 were wrong, and I published all four.
- In 8 cases I switched a control off and no check noticed. In those cases my tests could not show the control was doing anything.
- 12 cases have a limit I recorded and could not remove.

## Why I built it

Most advice on machine identities is easy to nod along to and hard to check. I wanted to see what happens when that advice meets a test written before the result was known.

I had already done this for AI governance controls. The NHI lab uses the same method on a different subject.

## How it works

The company and its data are made up. Each model is a small in-memory simulation. Each case has a trigger, a run without the control, a run with it, and a written guess for both.

Then I switch each control off one at a time. A control that nobody would miss has not shown it works.

The 46 cases sit on a seven step framework: find, own, limit, store and issue, rotate and expire, watch, retire and respond. The cases also map to the OWASP Non-Human Identities Top 10: eight items are covered directly, one partly and one weakly.

| Run | Cases | What it covered |
| --- | --- | --- |
| First run | 27 | Discovery, privileged access, credentials, shadow AI, gaps from 2026 incident reports |
| Second run | 19 | Stretch cases and chain tests, where one failure leads to the next |

The four guess files have their own hashes, and the lab publishes them. A reader can check that a file was not changed after the result came in.

## What I got wrong

1. One identity with three names.: I expected 51 entries without the control and 30 with it. I got 43 and 29. My arithmetic was wrong: nine identities with two or three names each cannot give 51. My fix of stripping trailing digits also merged two real accounts.
2. A token stolen from a CI runner.: I expected a short token lifetime to change the replay result. Another control had already refused both replays, so the lifetime control changed nothing.
3. Secrets in AI-assisted code.: With the control on, I expected one miss and got two.
4. The forgotten service account.: I expected a secret scan on tickets to be the best single control. The owner requirement did better.

## Where my tests could not see a control

In eight cases, switching a control off changed no result. These include the help desk reset path, key rotation for AI services, and approval fatigue.

That is a gap in my test. Either another control covers the same step, or my test cannot see the difference, and the result alone does not say which.

## Limits that stayed

Some limits could not be tested away:

- A ticket number on a break-glass review is not checked against the ticket system, so a made-up number passes.
- An allowlisted app that is breached keeps working until someone revokes it.
- A token bound to a CI job still works from inside the runner while the job runs.
- A scheduled automation can be extended on any written reason, because nothing checks the reason.

One chain test shows the cost. If the finder gets to a leaked token faster than its 12 hour lifetime, the attacker reaches the end of the chain and nothing detects it. A short lifetime only helps if the token is not found first.

Three cases come from 2026 incident reports, including a third-party AI app that an employee had linked with broad permissions. Reports on incidents like these differ in detail, so I linked the sources on the lab's [market page](https://roshantrivedi.co.in/nhi-lab/market/#incident).

## What I would test first

1. Make the break-glass request check its ticket against the ticket system.
2. Know which of your controls nobody would miss if they were switched off.
3. Test token revocation for a breached vendor, not only token lifetime.
4. Give each AI tool its own identity and a named human owner.

## Limits of this lab

One author wrote the controls, the models and the guesses. The models are small simulations, and the chain tests are rule models whose results follow from my rules. The data is made up. The lab shows where I would look first in a real environment. It says nothing about how any product behaves, and it is not legal advice.

## Sources

All figures come from my own published lab. Read the [Non-human identity lab](https://roshantrivedi.co.in/nhi-lab/), the [method](https://roshantrivedi.co.in/nhi-lab/method/), the [audit data](https://roshantrivedi.co.in/nhi-lab/audit/) and the [framework](https://roshantrivedi.co.in/nhi-lab/framework/). The free 65 page book is on the [Book page](https://roshantrivedi.co.in/book/).

**Roshan Trivedi** writes about privileged access, identity and AI governance at [roshantrivedi.co.in](https://roshantrivedi.co.in). The lab, the animated workflows and the audit data are free to read and reuse.

*All data in the lab is made up. Nothing here relates to any employer or real company.*
