---
title: "I Tested 130 Conditional Access, MFA and AI Agent Cases. Six of My Guesses Were Wrong."
layout: post
bg: post-plan
motif: grid
seo_title: "130 Conditional Access, MFA and AI Agent Cases: Six Wrong Guesses and What Decided the Outcome"
date: 2026-11-14 15:45:00 +0530
author: Roshan Trivedi
tags: [conditional-access, mfa, sso, ai-agents, identity, security-testing]
share_title: "I tested 130 conditional access, MFA and AI agent cases"
share_label: "Article · Conditional access lab"
share_accent: green
description: "I wrote every guess down before any code ran. 118 of 124 matched, 6 did not. MFA was often not the deciding control, and for AI agents the answer kept turning on one assumption."
---

# I Tested 130 Conditional Access, MFA and AI Agent Cases. Six of My Guesses Were Wrong.

*Filed under: Conditional access · MFA and single sign-on · AI agents*

*Independent work on my own time. All data is made up. Nothing here describes any employer's or client's systems.*

## The short version

I built a small lab for conditional access, MFA, 2FA, single sign-on and AI agent identity. It has 130 cases, and I ran 124 of them on small models of my own. For every case I wrote my guess first, hashed it and committed it before any code existed. 118 of the 124 matched. Six did not, and all six were in one run.

The score is the least useful part. In the cases I took from recent incidents, what decided the outcome was usually something other than MFA: how much a token could reach, how long it lived, whether it was tied to one machine, whether a password reset killed it, and whether recovery was weaker than sign-in. With AI agents, most results depended on one assumption I had chosen, such as whether the attacker looks like a local user.

## The rule: the guess comes first

For each case I did the same things in the same order. I picked a failure and the controls that should stop it. I wrote down what I expected with no controls, with all of them on, and with each one switched off on its own. I saved that as a guess file and committed it with its SHA-256 hash. Only then did I write the model and run it.

A guess committed first cannot be edited later without the hash changing, so anyone can see whether I moved the goalposts. The latest set, for 10 AI agent cases, went in with hash 1abdbf11 and was merged before a line of the model existed.

A case is a small rule model that runs in memory on a made-up company, with no real tenant or vendor product behind it. It shows whether my reasoning about a control holds together. How your product behaves is a separate question, and the last section says how to answer it.

## The six guesses I got wrong

All six were in Run 2, where each case had two or three controls. They fall into five kinds of mistake.

**I did not say what I was counting (C01, C03).** I defined the bad outcome as an account takeover that nobody notices. The change notice and the exclusion alert make any takeover noticed, so removing the SMS fallback or the exclusion review alone never produced the bad outcome. If I had defined "bad" first, I would not have guessed it.

**I treated controls as independent (A05).** For guest sign-ins, trusting the home tenant's MFA claim means a weak MFA at home satisfies the requirement in mine. Adding my own guest MFA rule did not help.

**I picked the wrong control as the one that mattered (Z21).** I said refresh token lifetime did not matter. The bad outcome was "the attacker still has access after 24 hours", and the refresh token lifetime decides exactly that. Blocking the flow and requiring a compliant device matter for the first hour only.

**I did not think through a control's own scope (X07).** The case was a trusted-network exception used from guest wifi in the same address range. I did not work out what the exception covered. It was limited to the managed office, so guest wifi was not trusted, MFA was required, and the attacker was stopped without the device rule.

**I counted a convention as a control (A03).** Separate admin accounts are a habit, not enforcement. I had the two cases reversed: with only separate accounts nothing stops the admin account reaching a risky app, while the group block does stop the daily account.

One more miss was mine alone. In my first pass the model said approval stops an unauthorised console change. An unauthorised change skips approval by definition, so only the log can show it. I fixed the model and kept the first-pass files in the repository.

## Why my perfect scores teach me less

Run 1 matched 41 of 41. Run 3 matched 16 of 16, Run 5 matched 12 of 12 and Run 6 matched 10 of 10. I do not trust those. I wrote the models after the guesses, so a perfect score only shows that my models and my reasoning agree with each other. Nothing outside me tested the guesses. Run 2 is the only run that caught me out, and it is the one I learned the most from.

## What the recent incidents showed

Run 5 has 12 cases built from recent events: cloud trust from CI/CD pipelines, stolen integration tokens, privileged API calls, agents and MCP sign-in, and a help desk recovery path. In 9 of the 12, switching off one control on its own let the bad outcome in.

In several of them MFA was not the deciding control. A stolen integration token never triggers a sign-in, so MFA played no part and an address allow-list decided the case. Token replay came down to whether the token was tied to the client. After a password reset, what mattered was whether the reset also killed the refresh token, and for account recovery, whether the recovery path was weaker than sign-in.

Then I changed one assumption at a time and re-ran. A few results flipped:

- If the cloud session lasts 25 hours instead of 1, a short-lived token stops helping.
- If the attacker replays a stolen token after 10 minutes instead of 2, a 5-minute token has already expired and the result flips.
- If the step-up check applies to API keys and service tokens as well as user tokens, two of the three paths close.
- If people almost always read the prompt, two agent cases flip, because the human habit is then doing the work of the control.

A pass in my table holds only while its assumption holds. Each assumption sits at the top of the script, so you can change it and run it again.

## What changed when AI agents were involved

Run 6 has 10 cases on how AI agents get access, pass it on and keep it. I built them from Okta's Agent SSO announcement and the Cloud Security Alliance paper on non-human identity, both read before I wrote a guess.

All 10 guesses matched, which by now tells me little. Six of the seven assumption changes I tried flipped a result:

- A sub-agent wrote where the person who asked could not. Narrowing the sub-agent's token did not stop it, because the parent agent ran with its own broad identity. Only a check against the person's own permissions held, and when the parent used the person's token instead, the problem went away.
- A session cookie was stolen after MFA. Continuous evaluation caught the network change until I let the attacker appear to be on the victim's network. After that, only binding the session to the device held.
- An agent outlived its project. Rotating its credential every 30 days changed nothing, because rotation hands the agent a new working credential. Expiring the identity with the project fixed it.
- An agent's owner left the company. A monthly scan flagged the agent, and it kept working.

If I were checking agents tomorrow, I would start with the boring controls: a named human owner, an expiry tied to the task, and a check at the resource against the human's own rights.

## The real events behind the cases

The cases come from public reports. The lab's sources page lists each one with its date, its source and how far I trust it. Three of them:

- **SonicWall, CVE-2026-19868.** A user with valid credentials for another login method can bypass SAML on the SSL VPN, including the MFA it enforces. It applies only when SAML is enabled for those logins. CISA lists it as exploited. SonicWall's advisory says it investigated a report indicating potential exploitation. It also added a workaround on 9 November for people who cannot upgrade yet.
- **Okta Threat Intelligence, January 2026.** Phishing kits built for phone callers defeat any MFA that is not phishing-resistant.
- **The MCP Python SDK, September 2026.** A malicious server could make a client send its OAuth credentials to an endpoint the server chose.

Companies appear because the sources name them, and a name on that page says nothing about that company's controls. Where I only read a summary of a source, the page says so.

## What I could not test

Six cases need a real tenant, a hardware key, a real AI agent product or real help desk calls, and I have none of those. They are in the register as "not run", with my predictions locked and the steps written out, so anyone with a test tenant can run them.

If you test any of the other cases in a real product and it behaves differently from my model, there is an exception form on GitHub. Accepted exceptions go next to my result with a date, and my result stays on the page.

## Everything is public

The 15 animated attack patterns, the virtual lab where you can replay any case and run the script yourself, the sources page and the full register are free to read:

roshantrivedi.co.in/ca-mfa-lab

If you can think of a case that would break one of these controls, tell me. I will add it, write the guess first, and keep the original on the page.
