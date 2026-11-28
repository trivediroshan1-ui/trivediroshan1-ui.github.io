# Findings: privileged access lab, round 4 (real software)

STATUS: DRAFT for Roshan Trivedi's review. Made-up data only (Kaveri Finance).

## The short version

I locked five guesses (sha256 `0a7cac42…`, pull request #194), then measured them on real open-source software in GitHub Actions: Keycloak 26.8.1, OpenBao 2.6.4 with PostgreSQL 16, OpenSSH 9.2 with sudo 1.9.13p3 on Debian bookworm, and Kubernetes 1.35 in kind. The clean run is [46133108171](https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/actions/runs/46133108171). Its full log is public.

4 of 5 rows matched. Both joint checks matched. No cell had a harness error. The one miss was in Keycloak, and the software was safer than I guessed.

Before the clean run, the harness stopped twice on its own setup checks. Both were mistakes in my test setup, not results. They are written up in `round4/HARNESS-CHANGES.md`. The guesses were never changed.

## Results

| Case | What it tests | Guess | Measured | Controls noticed |
|---|---|---|---|---|
| PA-R4-01 | A token outlives the removed role (Keycloak) | 300, 0, 60, 0, 60 | 300, 0, 60, 0, **0** | online check only |
| PA-R4-02 | A sub-agent reuses the parent's token (token exchange) | 3, 0, 3, 0, 0 | same | token exchange only |
| PA-R4-03 | A copied database password after the task (OpenBao) | 30, 0, 30, 0, 3 | same | per-task credential, revoke at end |
| PA-R4-04 | An open SSH session after removal from the admin group | 5, 0, 0, 0, 0 | same | none alone |
| PA-R4-05 | Three routes to cluster-admin (Kubernetes) | 3, 0, 1, 2, 0 | same | no standing binding, no admin service account with Pod Security |

Columns are: no controls, all controls, then each control switched off on its own (a, b, c). Joint checks: case 01 with the online check and the logout both off gave 60, and case 04 with the group re-read and the session end both off gave 5. Both were guessed.

## The miss: PA-R4-01 with the logout switched off

I guessed 60. Measured: 0.

My guess said Keycloak's online check (token introspection) would keep calling the token active, with the roles it was issued with, until it expired. So I bet that the online check only helps if the session is also logged out.

That bet was wrong. With the logout off and the 60-second token not yet expired, the test API refused the token at the very first check, right after the role was removed. The API accepts a token only when introspection says it is active and lists the admin role. The session was still open and the token was still in date, so it was the role that was missing: Keycloak built its answer from the user's current roles, not the roles written into the token.

That last step is inferred from the code and the log. The log records the API's decision, not Keycloak's full answer. A later run could record the full answer to confirm it.

Why it matters: an API that checks tokens online sees a role removal straight away. An API that only checks the signature keeps trusting the token until it expires, which is 5 minutes by default and 1 minute with the short life switched on. That's why only the online check showed up as noticed in this case. It covers for both of the other controls.

## What the five cases show

1. **Check online, or wait for expiry.** In Keycloak, removing a role takes effect at once for an API that asks Keycloak, and only at expiry for one that doesn't (case 01).
2. **Give every sub-agent its own token.** Passing the parent's token on gave all 3 sub-agents admin. With token exchange on, the audience check and the scope check each blocked them alone, so neither was noticed on its own (case 02).
3. **Per-task credentials beat stored passwords, and revoke-at-end beats a short lease.** The stored password worked for all 30 minutes. A per-task credential with no revoke still worked for 3 minutes after the task, until its 5-minute lease ran out. With the revoke on, it failed at once (case 03).
4. **An open session keeps old groups unless something re-reads them.** On this sudo version, a session that is already open keeps admin after the user leaves the group. Either the group re-read or ending the session closes it; only both off gives all 5 commands. The alert never blocked anything (case 04).
5. **Standing admin and admin service accounts are the routes in.** Removing the people's binding closed impersonation. Removing the admin service account and enforcing Pod Security closed the other two, including the privileged pod. The audit rule changed nothing (case 05).

Same lesson as rounds 1 and 3: alerts and logs don't block, and layered controls often only show their effect when two are off together.

## What this round can't tell you

- How commercial PAM products behave. Only the software and versions above were measured.
- Anything about other versions or settings.
- Anything about timing finer than the check interval: every 15 seconds in case 01, every minute in case 03.
