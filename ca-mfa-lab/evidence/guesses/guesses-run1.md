# Draft guesses: Run 1 (MFA methods, SSO protocols, recovery), written before any code

STATUS: DRAFT until hashed and committed on the Mac. Made-up data only (Kaveri Finance). 41 cases.
Each case runs three ways: no control, with the control, then the control switched off alone.
These are models of the rule as I understand it. They show whether a rule as written lets a case through, not how any vendor product behaves.
Format: ID | no control | with control | control off | limit I expect.

## MFA methods
M01 | SMS code relayed live: attacker gets in | SMS kept as a factor: still gets in (relay works) | n/a | Only a phishing-resistant factor stops it
M02 | TOTP relayed inside 30s: gets in | TOTP: still gets in | n/a | Same limit as M01
M03 | Push, no number match: tired user approves, attacker in | Number matching: blocked | Off: in again | A user who reads the number to the attacker still loses
M04 | Number match: attacker cannot supply number: blocked | blocked | off: in | Vishing a user into reading the number is not modelled
M05 | Passkey on look-alike domain: refused (origin differs) | refused | origin check off: accepted | Only if the real site is not itself compromised
M06 | Synced passkey, one device lost: user still signs in from another | in | n/a | Synced to a compromised cloud account is not modelled
M07 | Backup code reused: accepted twice | one-time use: second refused | off: accepted twice | Codes stolen before first use still work once
M08 | SMS recovery allowed: attacker picks SMS and gets in | SMS removed from recovery: blocked | off: in | Another weak recovery path can replace it
M09 | SIM swap: attacker gets SMS codes | no SMS factor: blocked | off: in | Swap detection is not modelled
M10 | TOTP seed in shared sheet: attacker generates valid codes | seed in vault only: blocked | off: in | Seed stolen at enrolment time still works
M11 | Wide TOTP window: a code from 3 steps ago accepted | 1 step window: refused | off: accepted | Clock skew will refuse some real users, which I expect to record
M12 | 6-digit code, no rate limit: guessed within the run | rate limit: blocked | off: guessed | Slow guessing across many accounts passes a per-account limit
M13 | Attacker locks real user out | lockout on: real user locked out (lockout is the attack) | off: user stays in | Lockout and rate limit pull in opposite directions
M14 | Weaker factor offered at prompt: user picks it, attacker uses it | only strong factors allowed: blocked | off: weak accepted | None
Z01 | QR lure to look-alike page: credentials and code captured | user trained: partly | phishing-resistant factor: blocked | Training alone will fail some users
Z02 | Attacker registers own method after password theft: persists | registration needs existing MFA: blocked | off: persists | Registration right after a password reset is the gap

## SSO protocols
S01 | Assertion replayed: accepted twice | one-time id check: second refused | off: accepted | Replay inside the same second across two servers not modelled
S02 | Wrong audience accepted | audience check: refused | off: accepted | None
S03 | Signature wrapping: forged assertion accepted | strict signature-to-element check: refused | off: accepted | Parser library flaws not modelled
S04 | Expired assertion accepted | time check: refused | off: accepted | Skew allowance leaves a small window; I expect to record it
S05 | Wrong nonce accepted | nonce check: refused | off: accepted | None
S06 | Prefix-matched redirect URI: attacker URI accepted | exact match: refused | off: accepted | None
S07 | Code intercepted, no PKCE: exchanged by attacker | PKCE: refused | off: exchanged | None
S08 | No state: login CSRF works | state check: refused | off: works | None
S09 | API accepts token for another audience | audience check: refused | off: accepted | None
S10 | Refresh token stolen: works repeatedly | rotation with reuse detection: stolen use detected on second use | off: works | The first use by the thief succeeds before detection
S11 | Session outlives logout: still valid | session ends with token: refused | off: valid | Cached tokens at other apps remain until expiry
S12 | Single logout misses one app: that app stays signed in | logout list complete: none left | off: one stays | An app that never registered for logout cannot be reached
S13 | Local login beside SSO: bypasses SSO rules | local login disabled: closed | off: open | Break-glass local login is a deliberate exception
S14 | Old signing key still trusted by one app: forged token accepted | remove old key: refused | off: accepted | Overlap period during rotation is a real window
Z03 | Golden SAML: forged assertion for any user accepted; IdP log shows no sign-in | key in HSM, assertions logged at app: forging blocked or seen | off: accepted unseen | Stolen key before HSM use still works
Z04 | Silver SAML: forged for one app accepted | app pins its trusted key: refused | off: accepted | Same limit as Z03
Z05 | ID token with alg none or bad signature accepted | signature and alg allow-list: refused | off: accepted | None
Z06 | Mix-up: code sent to wrong IdP accepted | issuer check: refused | off: accepted | Apps with one IdP are not exposed
Z07 | Unverified email at IdP: attacker signs in as victim | app requires verified email and stable subject id: refused | off: signed in | Apps that match on email alone stay exposed

## Recovery and help desk
R01 | Name and phone number: MFA reset granted | strong identity proof: refused | off: granted | A well-informed attacker may still pass weak proof
R02 | Method changed, no notice: owner never learns | notice sent: owner learns | off: silent | Notice to an email the attacker also controls does not help
R03 | Admin reset with no delay: instant | 24 hour delay with notice: owner can object | off: instant | Delay only helps if someone reads the notice
R04 | Recovery email owned by attacker: account taken | recovery email must be verified and old: refused | off: taken | Compromised legitimate mailbox is not modelled
R05 | New device enrolled right after password reset: accepted | hold new enrolment 24 hours: held | off: accepted | None
R06 | Temporary access pass long lived: reused by attacker | short life, one use: refused | off: reused | One short window still exists

## Predictions on the whole run
- Cases where I expect the control to fully stop the case: about 28 of 41.
- Cases I expect to show a limit even with the control: about 10 (M01, M02, M13, S04, S10, S14, Z01, R01, R03, R06).
- Cases where I expect the control-off check to behave differently from what I wrote above: about 3. I cannot say which.
- Likely wrong in the usual way: counts (how many attempts, how many minutes) and where two controls interact (M12 with M13).
