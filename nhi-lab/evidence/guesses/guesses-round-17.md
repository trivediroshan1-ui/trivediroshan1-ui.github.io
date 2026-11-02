# Draft guesses, round 17 (shadow AI accounts), must cases

Written before any code. Made-up data only. You change them, then I hash and commit. These are my expectations, so they can be wrong.

## S-R17-01 Personal OAuth grant to an AI tool
Scenario: an employee grants an AI tool read access to mail and files with a personal approval. The employee then leaves.
- Control off (no grant inventory, no expiry): I expect the grant keeps working after the employee is disabled.
- Control on (grant list, owner check, 30-day expiry in the lab, revoke on leaving): I expect it is found and revoked on the next scan, and a new grant without an owner is refused.
- Control-off check: switch off the leaver revoke step. The scan should flag the orphan grant. If nothing flags it, the scan is not working.

## S-R17-03 Agent runs under a person's account
Scenario: an automation uses a person's login, so the log shows that person.
- Control off: log shows the person and cannot tell human from agent.
- Control on (agent has its own identity and a tag in every log line): I expect actions are attributed to the agent and the person's own session history is clean.
- Control-off check: remove the tag. A report that separates human from agent actions should then fail.

## S-R17-04 Ghost credential
Scenario: an AI-assisted workflow creates a key with no owner for a project that then ends.
- Control off: the key stays valid indefinitely.
- Control on (owner and end date required at creation, weekly sweep): I expect creation without an owner is refused, and a key past its end date is disabled by the sweep.
- Control-off check: disable the sweep. A key past its end date should remain active, proving the sweep did the work.

## S-R17-05 Secrets in AI-assisted code and config
Scenario: generated code and an MCP configuration file contain fake secrets.
- Control off: the fake secrets reach the repository.
- Control on (secret pattern scan before commit and in CI): I expect most patterns are blocked. I expect one miss: a secret split across two lines or encoded. I will record the miss, not hide it.
- Control-off check: disable the scan and confirm all fake secrets pass.
