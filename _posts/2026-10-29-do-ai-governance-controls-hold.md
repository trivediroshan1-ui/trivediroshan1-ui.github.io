---
title: "Do AI Governance Controls Hold? What I Found in 13 Rounds and 164 Cases"
layout: post
bg: post-plan
motif: grid
seo_title: "Do AI Governance Controls Hold? A Public Test"
date: 2026-10-29 11:00:00 +0530
author: Roshan Trivedi
tags: [ai-governance, ai-agents, guardrails, iam, non-human-identity, security-testing]
share_title: "Do AI Governance Controls Hold? 13 rounds, 164 cases"
share_label: "Article · AI governance"
share_accent: cyan
description: "I tested the standard AI governance controls on made-up Indian data and published every guess, result and mistake. Here is what held and what did not."
---

# Do AI Governance Controls Hold? What I Found in 13 Rounds and 164 Cases

*Filed under: AI Governance · Identity Security*

*Independent practitioner write-up. Last reviewed 29 October 2026 (final). Everything here comes from my own public lab on made-up data. It does not describe any employer's systems, data or projects.*

## The short version

- I built a small lab to test whether common AI governance controls hold up when pushed. It now has 13 rounds and 164 cases.
- The register, the approvals, the kill switch and the audit trail did what they were built to do.
- A plain pattern filter for personal data and secrets did not. It scored 100 percent on the samples I tuned it on and 4 out of 10 on inputs I wrote afterwards.
- The method matters more than the scores. I write my expected result first, hash it, commit it, and only then run the test. Where the result differs from my guess, I publish both.

## Why I did this

For years my work was mapping vendor access controls to IAM policy. External auditors then checked that policy against NIST, PCI DSS, HIPAA and ISO 27001, depending on the project. One question stayed with me through all of it: do the controls really follow the policy?

Then AI agents arrived with the same promises. Agents would map policies. A central team would decide what permission each agent gets. Agents would use PAM and identity APIs to stay inside governance. What I never heard was which use cases, which policy, who certifies an agent's decision, and what stops an agent that goes off script.

So I stopped waiting for an answer and built a test.

Why: a test shows what a control actually does under pressure.

## The problem, in everyday terms

None of these needs an attacker.

- A support bot with "read access" can see PAN, Aadhaar and transactions. If it repeats them in a chat or sends them to an outside model, nobody was hacked. It did what it was allowed to do.
- An assistant that reads mail and shared drives can surface a salary file to someone who was never meant to see it.
- A plugin approved once can read the whole workspace every day, with the same rights as the person who clicked.
- A bot on a shared token looks exactly like an employee in the log. After a mistake, nobody can tell who did what.

A register, a filter, agent identity and an audit trail are meant to stop these. The lab asks whether they do.

## How the lab works

The company is made up: Kaveri Finance, a small lender with 40 staff and 200 customers. Every name, Aadhaar number, PAN and card number is invented. The Aadhaar numbers pass the real Verhoeff check and the card numbers pass the Luhn check, so a filter cannot succeed on format alone. The code uses only the Python standard library and runs in under a second.

The first four rounds were 59 cases in four areas.

| Area | What it tests | What usually goes wrong |
| --- | --- | --- |
| AI use gateway | Who registered which model, who approved it, when the approval expires | Approvals with no expiry date |
| Guardrail filter | Secrets and Indian personal data in prompts, instructions hidden in documents | Matching the textbook form and missing how people type |
| Agent identity | Named owners, short-lived tokens, privilege on request, kill switches | Shared tokens and no named owner |
| Audit evidence | Logs, notices, AI labels, explaining a declined loan in plain words | A log nobody can trust after the fact |

Rounds five to thirteen added 105 more cases.

## The method, step by step

1. **Write the expected result.** For every case, I write what I think will happen before I run anything.
   Guardrail: the guess is written before the code is run.
   Evidence: the guesses file is hashed with SHA-256 and committed to git, and the results file records the same hash.
   Why: without it, a reader cannot tell a prediction from a story told afterwards.
2. **Run it and keep every result file.** If a test crashes, I fix the test and keep both result files.
   Evidence: both files are in the lab repository.
   Why: the runs where something went wrong are the useful ones.
3. **Switch each control off.** If nothing notices, the control was not doing the job.
   Why: a control nobody would miss is not evidence.
4. **Test on inputs written after the fix.** When a number looks too good, check it on new inputs.
   Why: this is what exposed the filter.

## What held

The register, the approvals, the kill switch and the audit trail behaved as designed. The audit trail is chained line to line, so an edited line shows up. I wrote both the controls and the tests, so matching my own guesses proves little. A real AI assistant, given one short made-up company policy, followed it in all nine requests I sent. That is one assistant and one run.

## What broke

The guardrail filter. A plain pattern filter caught the textbook form of an Aadhaar, a PAN or a secret and missed the way people really type them: a lower-case PAN, a phone number split five and five, a database URL with a password in it, an instruction hidden in a document in a reworded form.

| Filter | Variants caught (of 53) | Caught, 200-sample set | Caught, 10 unseen items |
| --- | --- | --- | --- |
| v1, plain patterns | 20 | 68 of 100 | 4 of 10 |
| v2, after round one | 42 | 90 of 100 | 4 of 10 |
| v3, fixed on that set | 45 | 100 of 100 | 4 of 10 |

I do not trust the 100. I wrote each fix for v3 after seeing which samples v2 had missed, so of course it passes them. That score measures how well I fixed a list I was staring at.

So I wrote ten new inputs after the filter was finished and committed them before running anything. All three versions got 4 out of 10. What they missed was telling: a database password on a plain line, a bank account number with an IFSC code (no filter had a detector for it), a Hinglish "ignore the rules", and a note aimed at AI systems telling them to forward the user's messages. A training slide that quotes "ignore all previous instructions" was flagged as an attack. False alarms stayed at 5 percent in every version, mostly a laptop asset tag that looks like a PAN.

Pattern filters handle things with a fixed shape and struggle with anything that depends on meaning.

## The "read access" round

After the first posts, I audited my own lab from an identity-governance angle. The biggest gap was the sentence vendors use: "our AI only needs read access on your domain." Round five added 14 cases on this. I committed my expected results at 23:38 on 24 October 2026, then wrote the code. All 14 came out as I guessed, which says the controls do what I built them to do. It does not say they are enough, because I wrote both sides.

## What I got wrong

- I predicted that one phone format, a number starting 91 without a plus, would be caught. It was not.
- On 25 October I recounted rounds six to twelve with the stricter rule from round 13, where a crash no longer counts as noticing. Rounds six, seven and nine dropped. The rest held.

## What I would do on Monday

1. Ask for the detection rate on samples written after the filter was finished.
2. Do not trust a pattern filter with instructions, other languages or numbers spelled out.
3. Add a detector for every identifier your customers actually have.
4. Replace "read access" with a named data owner, a narrow scope and an expiry date.
5. Give each agent its own short-lived identity and a named human owner.

## Limits

One author wrote the controls, the tests and the guesses. The unseen sets are small and were written by me with an AI assistant. The data is made up. Nothing here proves that any product is secure, and it is not legal advice. If you see a weak test, tell me which one, or propose a case on GitHub. Write what you expect before you look at my code, and I will credit you.

## Sources

All figures come from my own published lab. Read them at [the AI Governance Lab](https://roshantrivedi.co.in/ai-governance-lab/), the [story behind it](https://roshantrivedi.co.in/ai-governance-lab/story/), the [lab repository](https://github.com/trivediroshan1-ui/ai-governance-lab) and the free book *Does AI Governance Hold?* (69 pages).

**Roshan Trivedi** writes about privileged access, identity and AI governance at [roshantrivedi.co.in](https://roshantrivedi.co.in). The lab, both free books and every case are at [roshantrivedi.co.in/ai-governance-lab](https://roshantrivedi.co.in/ai-governance-lab/). Newsletter: [buttondown.com/trivedi](https://buttondown.com/trivedi).

*All data in the lab is made up. Nothing here relates to any employer or real company.*
