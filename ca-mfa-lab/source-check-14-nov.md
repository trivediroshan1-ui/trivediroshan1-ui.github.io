# Source check, 14 November 2026

Last reviewed 14 November 2026. This is the record behind the "Source read" column on the register.

57 distinct rows had a source I had not read or had marked "verify": 21 marked verify and 36 added from search. I opened each source and compared it with the row and with my model. "Confirmed" means the source supports the row as worded. It does not mean the model proves anything about a real product. Vendor documentation changes, so every Microsoft row is true on 14 November only.

Result: 30 confirmed, 10 confirmed with a qualifier, 16 partly confirmed, 1 open.

## What the check changed

- Six rows were worded more strongly than their sources allow, so I reworded them: S08, S10, X09, Z09, Z19, Y08. No guess and no result changed. The old wording is in catalogue v1.2.
- One model claims more than the documentation. Z18 (continuous access evaluation) blocks a stolen token 10 minutes after revoke. Microsoft says the check covers Exchange, Teams and SharePoint Online with capable clients, can lag by up to 15 minutes, and has location exceptions. The result holds only with a capable client and no lag.
- Four chain tests (Z21, Z22, Y15, Y16) and the second half of Y04 are my own constructions. Each part has a source. The combination does not.
- Most of what I read is Microsoft Entra documentation, so those rows describe Entra, not every identity provider. The models are not vendor products.
- Dates that go stale are left off the page: the SMTP password retirement (Z20), whether the nested app path is still open (Y06), and Duo's default (Y10).

## Row by row

| ID | Case (v1.3 wording) | Verdict | What the source says |
|---|---|---|---|
| A02 | Admin role activation without fresh MFA | Confirmed | Microsoft PIM: users might not be prompted for MFA if they signed in with strong credentials or did MFA earlier in the session. Fresh authentication needs an authentication context plus an authentication strength. |
| A05 | Guest or partner user not covered by internal rules | Confirmed | Microsoft: MFA and device claims from other tenants are not trusted by default. When trust is on, the home tenant's claim is accepted, and SMS counts as a home-tenant method. |
| C02 | Token replay plus long session plus no device check | Partly confirmed | Chain. Its main part, token replay, is supported (X08). The combination is my construction. |
| M06 | Passkey synced across devices: loss of one device | Open | NIST SP 800-63B-4 covers syncable authenticators and says they cannot be used at AAL3. The part about losing one device sits in Appendix B, which I did not reach. |
| M07 | Backup codes reused after first use | Confirmed | NIST SP 800-63B-4: a look-up secret is used only once. |
| P01 | Two policies conflict: block and grant both match | Confirmed | Microsoft: block always wins. |
| P08 | Legacy sign-in protocol skips MFA | Confirmed, with a qualifier | New Microsoft policies apply to legacy clients by default, and a policy that needs MFA blocks them. The gap exists when a policy is scoped to modern clients only, or legacy accounts are excluded. |
| P10 | Rule order or precedence misunderstood | Confirmed | Microsoft: policies are evaluated in no particular order. The row is about someone who assumes an order. |
| R06 | Temporary access pass lifetime too long | Confirmed | Microsoft Temporary Access Pass: 1 hour by default, 8 hours maximum by default policy, 30 days at most, one-time use off by default. The 15 minute window in the model is my assumption. |
| S06 | OIDC redirect URI matched by prefix, not exact | Confirmed | RFC 9700 requires exact string matching of redirect URIs, except the port on a localhost redirect for native apps. |
| S08 | OAuth state parameter missing, and no PKCE or nonce either: login CSRF | Confirmed, with a qualifier | State is one of three accepted CSRF protections. PKCE or the OIDC nonce do the same job (RFC 9700, 4.7.1). Row reworded. |
| S09 | Token audience not checked by the API | Confirmed | RFC 9068 section 4: the resource server must reject a token whose audience does not include itself. RFC 9700 says the same. |
| S10 | Refresh token not rotated or bound (public client) | Confirmed, with a qualifier | RFC 9700 requires rotation or sender constraint for public clients. Confidential clients are already bound to their client. Row reworded to say public client. |
| Z01 | QR code lure (quishing) sends the user to a look-alike sign-in page | Partly confirmed | Microsoft's Q1 2026 email threat report covers QR code phishing trends, and a vendor describes QR codes sending people to look-alike Microsoft sign-in pages. Excerpts only. |
| Z02 | Attacker registers their own MFA method after stealing the password | Confirmed | Microsoft's 9 Sep 2026 post lists removing attacker-registered authentication methods as part of recovery. Excerpt only. |
| Z03 | Golden SAML: forged assertion signed with a stolen IdP signing key; no IdP sign-in event | Confirmed | Microsoft Entra blog: stealing a federation server's private key to forge signed tokens is the essence of Golden SAML. The 'no sign-in event' part was not in the excerpt. |
| Z04 | Silver SAML: forged assertion for one app using a key the app trusts | Confirmed | Semperis: whoever holds the private key of an externally generated SAML signing certificate can forge a response for that app. |
| Z05 | ID token signature or algorithm not verified by the app (library flaw) | Confirmed | RFC 8725 lists weak or missing signature validation as a threat and says to check the algorithm against an allow list. Excerpts. |
| Z06 | OIDC mix-up: app with two IdPs sends the code to the wrong one | Partly confirmed | RFC 9700, as quoted by a blog: a client that talks to two or more authorization servers must prevent mix-up attacks. I did not read the RFC text itself. |
| Z07 | Unverified email at the IdP lets an attacker sign in as the victim at the app | Confirmed | The Entra email claim was mutable and unverified (nOAuth, 2023). Microsoft already advised against using it as an identifier and added a verified-email claim. |
| Z08 | OAuth device code phishing: victim enters an attacker code at the real IdP; attacker gets tokens | Confirmed | Microsoft Threat Intelligence (Storm-2372, Feb 2025, and an April 2026 follow-up): device code phishing. Microsoft recommends blocking the device code flow. |
| Z09 | ROPC (password sent straight to the token endpoint) cannot perform MFA | Confirmed, with a qualifier | Microsoft: ROPC is incompatible with MFA. It cannot do MFA, so it works on a password alone only where no policy forces MFA. Row reworded. |
| Z10 | OAuth consent phishing: malicious app granted access with no password stolen | Partly confirmed | Consent phishing is real and mapped to MITRE ATT&CK T1528. I read two vendor write-ups, not Microsoft's own guide. |
| Z11 | A policy blocks one named client (e.g. a CLI) but the same flow arrives via another client | Partly confirmed | A vendor blog (Huntress) describes MFA scoped to some apps while Azure CLI traffic got through. Not Microsoft documentation. |
| Z12 | Policy has too many AND conditions (e.g. sign-in risk and user risk) and rarely fires | Confirmed | Compass Security (April 2026): too many conditions leave gaps. Sign-in risk plus user risk rarely fire together because user risk is often raised later. |
| Z13 | No default deny: a sign-in no policy matches is allowed | Confirmed | Compass Security: Conditional Access has no simple default deny. Access is allowed unless a policy applies. |
| Z14 | Built-in bypass: compliant-device rule still allows security-info registration or device join | Confirmed | Compass Security: a built-in bypass exists for policies that require only a compliant device. Example: the Intune Company Portal client (2023). |
| Z15 | Policy drift: console edits diverge from the approved baseline (policy as code) | Partly confirmed | A blog mentions Conditional Access as code and drift detection. Secondary source, thin. |
| Z16 | Device platform condition relies on a user agent string the attacker can change | Confirmed | Microsoft: user agent strings can be modified, so device platform is not verified. Use it with compliance or in a block rule. |
| Z17 | AiTM session replay refused because policy needs a compliant device | Partly confirmed | A Microsoft staff answer on Microsoft Q&A says compliant-device controls apply before a token is issued, so an attacker's proxy cannot present such a device. Not documentation. |
| Z18 | Continuous access evaluation: stolen token used from a new location after revoke | Confirmed, with a qualifier | Microsoft continuous access evaluation covers Exchange, Teams and SharePoint Online with capable clients, can lag by up to 15 minutes, and has location exceptions. My model blocks the token 10 minutes after revoke, so it assumes a capable client and no lag. |
| Z19 | Refresh token valid for 90 days of inactivity with no maximum age, so it may outlive a password reset | Confirmed, with a qualifier | Microsoft: refresh tokens expire after 90 days of inactivity and have no maximum age. Whether a password reset revokes them is not stated on that page. Row reworded. |
| Z20 | Printers and scanners justify a broad legacy-auth exception | Partly confirmed | Printers and scanners that use SMTP with a password are the named group, and Microsoft is retiring that path. The dates have moved before, so none are on the page. |
| Z21 | Device code phishing plus no flow block plus long refresh token | Partly confirmed | Chain. The device code lure and the advice to block the flow are supported. The 1 hour refresh token in the model is my assumption. Microsoft's default is a 90 day inactive window. |
| Z22 | Stolen password plus open security-info registration plus no device rule | Partly confirmed | Chain. Each part has support (Z02, Z14). The combination is my construction. |
| X01 | Managed device required: unmanaged laptop with valid MFA | Confirmed | True by design: an unmanaged device fails a managed-device rule whatever MFA it holds. |
| X02 | Device compliance claim is stale | Confirmed, with a qualifier | Intune treats a silent device as noncompliant after 30 days by default (1 to 120). That a device in its grace period is not blocked comes from a vendor blog citing Microsoft. I did not open Microsoft's page. |
| X05 | Risk-based step-up: low risk score on a real attack | Confirmed | Several Microsoft ID Protection detections are calculated offline, so they cannot trigger a step-up at the moment of sign-in. |
| X06 | Risk-based block: high false positive on a travelling user | Confirmed | Microsoft tells admins to add VPN ranges to named locations to reduce false positives. |
| X08 | Token stolen after MFA is replayed from another device | Confirmed, with a qualifier | Microsoft token protection page (updated 20 Aug 2026): generally available for native apps. Browser support is a preview limited to Azure Resource Manager, and not supported in iOS or iPadOS browsers. Browser sessions outside that preview are not covered. |
| X09 | Silent token renewal keeps a session alive past the intended re-sign-in interval | Partly confirmed | Microsoft says refresh and session token lifetimes are not configurable and sign-in frequency is the control, so the old wording was not supported. The reworded row is. Model unchanged. |
| Y01 | Privileged app says step-up is required but its server never checks that the token shows fresh MFA | Confirmed | RFC 9470: the resource server decides whether authentication is strong or recent enough. max_age can be enforced, acr_values is only a request, so the server must check the acr claim it gets back. |
| Y02 | Scheduled job or API integration runs with no active user session, so the step-up challenge never fires | Confirmed | Microsoft: service principals cannot perform MFA. Conditional Access for them can block by location or risk, not step up. |
| Y03 | Federated domain backdoor: an admin adds the attacker's own federated domain, which forges tokens and claims MFA was done | Confirmed | Datadog Security Labs showed that an identity with Domain.ReadWrite.All can add a federated domain and forge tokens, with an MFA claim, for any synced hybrid user. Third-party research. |
| Y04 | Tenant accepts the federated IdP's MFA claim, and the on-premises IdP skips MFA for internal addresses | Confirmed, with a qualifier | Microsoft documents that Entra accepts MFA done by the federated IdP when set to acceptIfMfaDoneByFederatedIdp. That the on-premises IdP skips MFA for internal addresses is my assumption. |
| Y05 | Native app signs in without the broker, so device identity is missing and a device rule cannot be checked | Confirmed | Microsoft: device registration, approved client app and app protection controls all need the broker app. A rule that requires one fails the sign-in, so the bad outcome only arises where no such rule exists. |
| Y06 | Token obtained through a nested app path that the conditional access policy does not evaluate (verify) | Partly confirmed | NetSPI, Dirk-jan Mollema and Secureworks document the technique. Excerpts only, and I do not know whether Microsoft has since closed the path. |
| Y07 | Token used from inside the compliant device itself, through a malicious browser extension | Confirmed | Vendor write-ups (Push Security, Adaptive Security, Varonis): extensions with cookie access can copy session tokens, and replay from the victim's own browser looks familiar. |
| Y08 | Pass-the-passkey: malware on the endpoint gets a valid passkey assertion with little or no user action (verify) | Partly confirmed | Unit 42 research and a Black Swan advisory (8 Sep 2026) exist. The advisory's own first example shows a prompt, so 'no user action' was too strong. Row reworded. |
| Y09 | Attacker with a stolen session registers their own passkey and keeps access after sessions are revoked | Confirmed | Microsoft's 9 Sep 2026 post lists removing attacker-registered authentication methods as part of recovery. Excerpt only. |
| Y10 | MFA provider unreachable: the sign-in system fails open and accepts the password alone | Confirmed, with a qualifier | Duo's Windows Logon is fail-closed by default from version 4.3.0 and was fail-open before. The row describes a deployment set to fail open. |
| Y11 | MCP proxy confused deputy: a malicious client registers itself and skips consent because of an old consent cookie | Confirmed | MCP Security Best Practices covers the confused deputy problem and consent cookie rules. |
| Y12 | MCP server accepts a token issued for another service and passes it on to a downstream API | Confirmed | MCP: servers must not accept any tokens that were not explicitly issued for the MCP server. |
| Y13 | Agent includes its own token in data sent to a tool; the token is long lived and broad | Confirmed | OWASP MCP Top 10 and LLM01 (excerpts): tokens can leak through prompt injection, compromised context or debug traces. Keep the application's own tokens in code, away from the model. |
| Y14 | Agent runs an irreversible action because injected text told it to; the token allows it and nobody asks a person | Partly confirmed | OWASP agentic Top 10 summary: injected instructions can make an agent use a token it holds. The 'nobody asks a person' part was not in the excerpts. |
| Y15 | Malicious extension steals a session plus a new passkey is registered plus no revoke of recent methods | Partly confirmed | Chain. The extension (Y07) and the attacker-registered method (Y09) are each supported. The combination is my construction. |
| Y16 | Malicious MCP client plus broad agent token plus long token life | Partly confirmed | Chain. Each step has OWASP support. The combination is my construction. |

Nothing is unread. M06 is the one row still open: the NIST text on syncable authenticators is read, but Appendix B is not.

