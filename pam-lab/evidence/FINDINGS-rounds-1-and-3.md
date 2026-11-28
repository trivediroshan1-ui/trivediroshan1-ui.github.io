# Findings: privileged access lab, rounds 1 and 3

Run by Roshan Trivedi on his own Mac on 28 Nov 2026 (Python 3.9.6), against guesses locked before any code was written. Round 1 guesses: sha256 6c3acc1c…a80aa. Round 3 guesses: sha256 fa235a1b…082e8. A second run of the same scripts gave identical numbers. Made-up data (Kaveri Finance); these are models of rule logic, not of any product.

## The short version

- 33 of 36 counted rows matched the locked guesses exactly (round 1: 19 of 21, round 3: 14 of 15). All 7 joint checks matched.
- The three misses are explained below. Two were disclosed as likely before the run.
- The most useful result isn't the score. In six rows, switching off any one control changes nothing; switching off two does. Testing controls one at a time would call them useless. They are layered.

## The three misses

| Case | Count | Setting | Guess | Model | Why |
|---|---|---|---|---|---|
| PA-R1-07 | hours of admin the agent holds after its tasks end | task-bound tokens (c) off | 30 | 27 | With the scope rule (b) still on, the 3 injected requests are refused, so only 27 activations happen. The guess counted all 30 tasks. |
| PA-R1-13 | rule changes the attacker makes | two-person rule (a) off | 0 | 1 | JIT on the PAM tool's admin role stops an outsider who can't get approval. A real tool admin's activation is approved, and nothing then stops them making themselves eligible for Tier 0. Flagged before the run as likely to mismatch. |
| PA-R3-05 | sub-agents able to use the parent's database admin rights | no controls | 3 | 4 | One sub-agent starts its own. With no token rule and no depth limit, that grandchild gets the parent's token too. The guess missed it. It was found while writing the model and disclosed before the run. |

What each miss teaches:

1. **Controls shrink each other's damage.** The scope rule wasn't built to cut leftover admin hours, but it did, by refusing requests before they could hold anything.
2. **JIT protects the PAM rules from outsiders, not from their own admins.** Only a second person on every rule change stops an insider. If approvers refused tool admins' own activations, this row would match (see the sensitivity table in RESULTS-round-1.md).
3. **Count delegation chains, not direct children.** Agents start agents. The parent's admin reaches every level unless each hop gets its own narrower token.

## What the run shows beyond the score

- **Layered controls hide in single-control tests.** No single control is noticed in PA-R1-04, PA-R1-15 (first count), PA-R1-16, PA-R3-01 (activations), PA-R3-03 and PA-R3-08 (writes). In each one the joint check shows the effect when two are off together. Test controls in pairs, not only alone.
- **The AI approver's mode didn't stop anything; plain code did.** In PA-R1-12 the planted requests were stopped by the code checks (b) and by limiting the AI to structured fields (c). Recommend mode (a) only changed how many requests a person reads: 5 a week.
- **Alerts don't block.** In PA-R1-06 the alert is never noticed, because nobody acts within the 90-minute outage. In PA-R1-10 an alert removes nothing; only removal does.
- **The weakest control is the sponsor's attestation.** In PA-R3-03 changing how often sponsors attest wrongly moves nothing, because end dates and the vendor feed decide the outcome.
- **For session recordings, retention and masking decide what's held.** In PA-R3-10, JIT access to recordings only changes who watches them.

## Limits

- The same person wrote the guesses and the models. That favours the guesses. The blind AI forecast prompts exist so a model can be scored the same way.
- Rule logic with made-up numbers, not products. Each assumption the guesses left open is listed in the scripts' PARAMS, and the sensitivity tables show which cases move when one changes.
- One display fix after the run: the results table used "none" both for "no mismatch" and for a mismatch in the no-controls column (PA-R3-05). The label now reads "no controls" and "match". No number changed.
