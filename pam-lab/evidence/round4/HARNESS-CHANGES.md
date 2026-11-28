# Round 4 harness changes

Every change to the measurement code after the guesses were locked (#194) is listed here. The guesses file is never changed.

## Fix 1, 28 Nov 2026, after the first run (run 46130355693)

The first run stopped on two setup errors. Both were caught by the setup checks and recorded as errors, not numbers.

- **PA-R4-01, every setting with the online check on:** Keycloak's introspection answer did not include the user's realm roles, so the test API refused a valid admin token before anything was removed. Fix: turn on "add to token introspection" for the realm roles mapper. If the setup check still fails, the error now includes Keycloak's introspection answer.
- **PA-R4-04, every setting with the group re-read on:** the harness put `group_source=dynamic` in the sudoers rules, where sudo rejects it. `group_source` is a `/etc/sudo.conf` setting. Fix: write `Set group_source dynamic` to `/etc/sudo.conf`.

Neither fix changes what is measured or the counting rule. The results come from a fresh full run after this fix.
