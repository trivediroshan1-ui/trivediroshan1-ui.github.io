# Run 4: real-world tests E01 to E03, predictions

STATUS: LOCKED when committed. Written 14 Nov 2026, before any test was run. The SHA-256 of this file is recorded in the commit message and on the lab page. Results go in a separate file; this file is never edited after the commit.

Why this run is different: Runs 1 to 3 are code models. These three are done by hand against a real test tenant, a real hardware key and a real person on the phone, so the answers are what happened, not what a model says.

## Flagged first

- HIGH-IMPACT, E01: an enforced Conditional Access policy can lock you out of the tenant. Use a throwaway test tenant only, never the one your job uses. Keep one admin account excluded from every policy and write its sign-in details somewhere you can reach if you are locked out.
- HIGH-IMPACT, E03: do not call a real help desk, yours or anyone's. The friend plays the desk from a written script, in a made-up company, with made-up staff. No employer data, no real accounts.
- IRREVERSIBLE, E02: resetting a security key erases every passkey on it. Use a spare key that holds nothing you need.
- Credentials: no passwords, codes or tokens in notes, screenshots or commits. Blur or leave out the tenant name.

## How to read a prediction

Each check is a yes or no question. "Yes" is my prediction, and the line after it is why. After the test, you write what happened and whether it surprised you. Anything I got wrong stays on the page.

## E01: sign-in logs and report-only export (real test tenant)

Setup: one test tenant with Conditional Access available (a trial or developer tenant; availability and licence terms change, check before you start). One test user with MFA registered. One policy "require MFA for all users, all apps, all client apps (modern and legacy)", set to report-only, with the excluded admin account.

| Check | Prediction | Why I think so |
|---|---|---|
| E01a. A normal browser sign-in shows the report-only result for the policy on that sign-in row | Yes | Report-only is meant to log what would have happened. |
| E01b. A silent token renewal (a non-interactive sign-in) also carries a report-only result, but sits in a different log view from the interactive one | Yes | I expect the portal to split interactive and non-interactive sign-ins. Not verified. |
| E01c. The portal's CSV download has the per-policy result, so you can answer "who would have been blocked" from it alone | No | I expect the policy detail to be in the JSON or API export only. Not verified. |
| E01d. The interactive sign-in appears in the log within 5 minutes | Yes | Expected delay of a few minutes. Not verified. |
| E01e. A sign-in with a legacy-style client (for example an old mail protocol) is visible in the log with the report-only result | Yes | The policy covers all client apps, so the legacy sign-in is evaluated too (P08 source note). |

Record: the export file name (no tenant data in the repo), what each log row showed, how long it took.

## E02: hardware security key, enrolment and loss (real key)

Setup: one spare FIDO2 key, the same test tenant, one test user with an authenticator app also registered as a second method.

| Check | Prediction | Why I think so |
|---|---|---|
| E02a. Enrolling the key and signing in with it works first time | Yes | Ordinary use. |
| E02b. With the key removed from the picture and the authenticator app still registered, the user can still sign in without the key | Yes | A second method exists. |
| E02c. With the key as the only method and the key "lost", the user cannot sign in alone and needs an admin | Yes | Nothing else to fall back on. |
| E02d. After an admin deletes the key's registration, the key no longer signs in, but a session that was already open keeps working for a while | Yes, a session stays open until its token expires (I guess up to about an hour) | Matches the Z18 source note on token lifetimes. |
| E02e. Entering the wrong PIN repeatedly blocks the key, and only a full reset brings it back, which erases the passkeys on it | Yes | My understanding of how FIDO2 keys protect against guessing. Not verified against the key's manual. |

Record: the key make and model, the number of wrong PIN tries before it blocked, how long the old session lasted.

## E03: help desk call, role played (friend plays the desk)

Setup: a made-up company, 10 made-up staff with employee numbers, a one-page script for the "desk" that says: call back to the number on file before any reset, and tell the user by email after any reset. The friend has not seen my predictions. You play four callers, each in a separate call, in a random order the friend does not know.

| Caller | Check | Prediction | Why I think so |
|---|---|---|---|
| 1. Name and phone number only | The desk refuses the reset | Yes | The script says to call back. |
| 2. Name, employee number and date of birth (as if leaked) | The desk refuses the reset | No, the desk does the reset | The script's callback is easy to forget once the caller sounds sure. One person is a small sample. |
| 3. Name only, with pressure ("I'm boarding a flight, I need this now") | The desk refuses the reset | No, the desk gives in or half gives in | Pressure beats a checklist more often than people admit. |
| 4. Claims to be the person's manager | The desk refuses the reset | No | Authority works better than urgency. |
| Any reset that happened | The desk sends the after-reset email without being reminded | No, forgotten in at least one case | The after-reset step comes last and nobody checks it. |

Record: for each call, what the desk said, which script step was skipped, and how long the call took.

Limits, to say on the page: a friend at a desk is one person on one day. It tests whether the script survives pressure. It does not show how a real desk behaves.

## What this does to the lab

If all three are run, the lab has 105 cases, 105 run. The count of wrong guesses may change. Pages and register need one more update. The three rows say "tested by hand", not "modelled".
