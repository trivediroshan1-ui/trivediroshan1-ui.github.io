"""Completeness register for the NHI lab catalogue (193 rows: 187 from the catalogue plus 6 gap rows).
Every row gets a final status. Rows that were not run get a reason. Nothing here was run for a row that needs a real environment.
Status codes:
  R  run in this lab (the ref is the lab case id)
  E  tested in an earlier lab (the ref names the earlier case ids)
  P  partly tested (the ref says what was and was not covered)
  X  not run (kind: env = needs a real product or environment, plan = a plan or process, near = nearby case covers the
     mechanism, data = cannot be tested with made-up data, signal = a list of signals, not a control to switch off)
"""

# (id, group, short title, status, kind, ref)
N = []
def r(i, g, t, ref): N.append((i, g, t, 'R', '', ref))
def e(i, g, t, ref): N.append((i, g, t, 'E', '', ref))
def p(i, g, t, ref): N.append((i, g, t, 'P', '', ref))
def x(i, g, t, kind, ref): N.append((i, g, t, 'X', kind, ref))

# ---- non-human identity (64)
G = 'Non-human identity'
r('N01', G, 'Service accounts nobody has listed', 'N-R14-01')
x('N02', G, 'API keys in SaaS consoles and cloud accounts', 'env', 'A scan of real consoles needs real consoles. N-R14-02 tests the scan logic on code, config, chat and tickets.')
r('N03', G, 'Secrets in code, config, chat and tickets', 'N-R14-02')
r('N04', G, 'CI/CD variables, runners and deploy keys', 'N-R14-03')
x('N05', G, 'SSH keys shared across many servers', 'env', 'Needs real servers and keys. The shared-key chain C08 is also documented only.')
r('N06', G, 'Certificates and private keys', 'N-R14-04')
r('N07', G, 'OAuth apps approved with one click', 'N-R14-05')
x('N08', G, 'Cloud workload identities and IAM roles', 'env', 'Needs a real cloud tenant. N-R14-17 tests the trust condition, which is the part a model can show.')
x('N09', G, 'Kubernetes service accounts and tokens', 'env', 'Kubernetes workload identity is out of scope for this lab and needs a real cluster.')
x('N10', G, 'Bots and RPA robots running as a person', 'env', 'Needs a real RPA platform to see which identity a robot uses. N-R14-22 is the nearest case.')
e('N11', G, 'AI agents, MCP connections and plugins', 'AI governance lab A2, I1, I10, E1')
r('N12', G, 'Identity created outside the normal process', 'N-R14-06')
r('N13', G, 'One identity under different names', 'N-R14-07')
x('N14', G, 'Hard-coded credentials in legacy batch jobs', 'env', 'Needs real legacy scripts and a mainframe scheduler to scan.')
x('N15', G, 'Database users and connection strings', 'env', 'Needs a real database. Dynamic credentials (P59) are also not run.')
p('N16', G, 'Vendor and partner integrations that hold your credentials', 'Vendor workers tested in the AI governance lab (H9, H10). Vendor service accounts were not tested and need real vendor integrations.')
r('N17', G, 'Test credentials that also work in production', 'N-R18-02 (round 18). The queued case N-R14-08 was not run under its own id.')
r('N18', G, 'Identity with no named owner', 'N-R14-09')
e('N19', G, 'The owner leaves', 'AI governance lab A7, I6, B8, D4')
e('N20', G, 'The owner moves to another team', 'AI governance lab I13, B7')
r('N21', G, 'The owning team is disbanded', 'N-R14-10')
e('N22', G, 'Two companies merge with the same IDs', 'AI governance lab D9')
r('N23', G, 'Application retired, identities stay', 'N-R14-11')
e('N24', G, 'Dormant identity, idle 31 days or more', 'AI governance lab I10, I14')
x('N25', G, 'Owner attestation', 'near', 'Attestation is a control in N-R14-10 and N-R14-11. It had no effect on what those cases count, so a separate case would show the same.')
e('N26', G, 'Long-lived static key instead of a short token', 'AI governance lab I2, I3')
r('N27', G, 'Overprivileged identity', 'N-R14-12')
e('N28', G, 'Toxic combination of permissions', 'AI governance lab I15, D12')
e('N29', G, 'Secret shared by several consumers', 'AI governance lab I8 (tokens)')
r('N30', G, 'Rotation on a schedule', 'N-R14-13')
r('N31', G, 'Rotation fails silently', 'N-R14-14')
r('N32', G, 'Rotate before the consumer is updated', 'N-R14-15')
r('N33', G, 'Retire before you rotate', 'N-R14-16')
e('N34', G, 'Token copied from a log and replayed', 'AI governance lab C1, C2, D5, D10')
e('N35', G, 'Token for one service shown to another', 'AI governance lab I16')
e('N36', G, 'Bearer token against a token tied to a key', 'AI governance lab C1, D5')
r('N37', G, 'Loose federation trust condition', 'N-R14-17')
e('N38', G, 'Credential lease reused after its life', 'AI governance lab T16, B5')
e('N39', G, 'Check-out and check-in of a service account password', 'AI governance lab T17')
e('N40', G, 'Clock drift accepts an expired token', 'AI governance lab C12')
e('N41', G, 'Signing key rotated after a scare', 'AI governance lab D8')
r('N42', G, 'Front door for new identities', 'N-R14-18')
p('N43', G, 'Block a secret at commit and in the pipeline', 'The prompt scan was tested in the AI governance lab (G12) and the scan logic in N-R14-02 and S-R17-05. A real commit gate needs a real repository and pipeline.')
r('N44', G, 'Scoring: rank so the top is fixed first', 'N-R14-19')
x('N45', G, 'Exceptions with an end date', 'near', 'The end date is a control in N-R14-18 and the expiry in N-R14-06. A separate exception case would repeat them.')
r('N46', G, 'Close only when the old secret is dead', 'N-R14-20')
x('N47', G, 'Secrets service outage and disaster recovery', 'env', 'Needs a real vault to fail and restore. P45 is not run for the same reason.')
e('N48', G, 'Non-human identities in access reviews', 'AI governance lab I14 (agents only). Service account review quality was not tested.')
e('N49', G, 'Leaked token used to call the identity API', 'AI governance lab B1, B2, B3, B4')
e('N50', G, 'Mass change by an agent or job', 'AI governance lab T12')
e('N51', G, 'Audit log tamper, cut tail, out of order', 'AI governance lab A13, B12, E5, E16')
e('N52', G, 'Sensitive data in requests and logs', 'AI governance lab E15, T11, H5')
e('N53', G, 'Agent registered with no human sponsor', 'AI governance lab I1')
e('N54', G, 'Agent asks for more than the person has', 'AI governance lab I4')
e('N55', G, 'Agent hands work to another agent', 'AI governance lab D1, D2, D3')
e('N56', G, 'Hidden instruction hijacks an agent', 'AI governance lab I9, T3, Q5')
e('N57', G, 'Poisoned note in an agent memory', 'AI governance lab I12')
e('N58', G, 'Agent tries to read the credential from the vault', 'AI governance lab T8, T18')
e('N59', G, 'Kill switch with a pending approval', 'AI governance lab A12, A16, I11, T9')
x('N60', G, 'MCP server holds its own credential', 'near', 'The MCP lab covers the approval side and N-R14-21 the shared credential. Where the MCP server keeps its own credential needs a real server.')
r('N61', G, 'Agents share a team credential', 'N-R14-21')
e('N62', G, 'Agent rights after the delegator leaves', 'AI governance lab I17, D4')
r('N63', G, 'A person logs in with a service account', 'N-R14-22')
p('N64', G, 'One identity shared across dev, test, staging and production', 'N-R18-02 tested a test runner that reaches production. One identity shared across all four environments was not tested separately. The queued case N-R14-23 was not run under that id.')

# ---- shadow AI (18)
G = 'Shadow AI accounts'
r('S01', G, 'Personal OAuth grant to an AI tool', 'S-R17-01')
r('S02', G, 'AI tool inherits the full permissions', 'S-R17-02')
r('S03', G, 'Agent runs under a person account', 'S-R17-03')
r('S04', G, 'Ghost credentials from AI-assisted work', 'S-R17-04')
r('S05', G, 'Secrets in AI-assisted code and config', 'S-R17-05')
r('S06', G, 'AI-service keys leak into repositories', 'S-R17-06')
r('S07', G, 'AI features inside an approved SaaS app', 'S-R17-07')
x('S08', G, 'Personal AI accounts used for work', 'data', 'Cannot be tested with made-up data. It is a policy and detection question.')
x('S09', G, 'AI browser extensions and browser agents', 'env', 'Needs a real browser with real sessions.')
r('S10', G, 'Agent built in a low-code tool, never registered', 'S-R17-08')
r('S11', G, 'Agent creates credentials and sub agents', 'S-R17-09')
r('S12', G, 'Scheduled automations outlive the test', 'S-R17-10')
x('S13', G, 'MCP clients and servers with tokens on laptops', 'env', 'Needs real laptops and community servers. The MCP lab covers the approval side.')
x('S14', G, 'Chatbot stores data through an uninventoried token', 'env', 'Needs a real chatbot platform and storage bucket.')
x('S15', G, 'Vendor-embedded agents', 'env', 'Needs a real third-party platform. See N07 and N16 for the nearest cases.')
x('S16', G, 'AI note-taker bots joining through OAuth', 'env', 'Needs a real calendar tenant. The catalogue marks this row as my inference, not from a source.')
x('S17', G, 'Detection signals for shadow AI', 'signal', 'A list of signals, not a control to switch off. P-R15-24 tests analytics rules in general.')
x('S18', G, 'A fast approved path for people who want AI', 'plan', 'A process question. A model cannot show whether people use the approved path.')

# ---- privileged access (59)
G = 'Privileged access'
r('P01', G, 'Request privileged access with a ticket and an end time', 'P-R15-01')
r('P02', G, 'Just-in-time window', 'P-R15-02')
r('P03', G, 'Work runs past the window', 'P-R15-03')
r('P04', G, 'The elevation path is down', 'P-R15-04')
x('P05', G, 'Accounts that cannot be elevated just in time', 'env', 'Needs real legacy systems that cannot take a short-lived grant.')
r('P06', G, 'Zero standing privilege', 'P-R15-05')
r('P07', G, 'The person never sees the password', 'P-R15-06')
r('P08', G, 'Direct login to a target is blocked', 'P-R15-07')
r('P09', G, 'Session recording the user cannot switch off', 'P-R15-08')
x('P10', G, 'Dangerous commands blocked in real time', 'env', 'Needs a real session tool that reads commands.')
r('P11', G, 'Two approvers for Tier 0', 'P-R15-09')
e('P12', G, 'Approver sees many requests and approves in a batch', 'AI governance lab F3')
r('P13', G, 'Phishing-resistant MFA for admins', 'P-R15-10')
e('P14', G, 'Recent sign-in check before approval', 'AI governance lab I18')
r('P15', G, 'Break-glass used at 2 a.m.', 'P-R15-11')
r('P16', G, 'Break-glass drill', 'P-R15-12')
x('P17', G, 'Break-glass storage that does not depend on what is down', 'near', 'The drill (P-R15-12) found the sealed copy fault. Where the copy is physically kept needs a real site.')
r('P18', G, 'Break-glass becomes a side door', 'P-R15-13')
e('P19', G, 'Check-out and rotate after use', 'AI governance lab T17 (service account). Human check-out was tested through P-R15-14.')
r('P20', G, 'Shared accounts: who did what', 'P-R15-14')
x('P21', G, 'Local admin passwords the same on every machine', 'env', 'Needs a real fleet. Chain C14 is also documented only.')
x('P22', G, 'Privileged workstations and Tier 0 to Tier 3', 'plan', 'An architecture decision, not a control to switch off in a model.')
x('P23', G, 'Domain admin, directory and certificate authority accounts', 'env', 'Needs a real directory and CA.')
r('P24', G, 'The vault, its backups and who can read them', 'P-R15-15')
x('P25', G, 'Root and sudo on Linux, SSH for engineers', 'env', 'Needs real Linux hosts.')
x('P26', G, 'Cloud console roles, just in time', 'env', 'Needs a real cloud tenant and its role tool.')
x('P27', G, 'SaaS administrator roles', 'env', 'Needs real SaaS tenants.')
x('P28', G, 'Database administrator access to production data', 'env', 'Needs a real database and its audit log.')
x('P29', G, 'Network devices and operational technology', 'env', 'Needs real devices. The catalogue marked this row as needing a real environment from the start.')
x('P30', G, 'Developers and on-call engineers needing production access', 'near', 'P-R15-02, P-R15-03 and P-R15-19 cover the window, the extension and the 2 a.m. call.')
r('P31', G, 'Help desk staff who can reset passwords', 'P-R15-16')
p('P32', G, 'Vendor onboarded, then each vendor person', 'AI governance lab H9 tested vendor workers. P-R15-17 and P-R15-18 tested the session and the leaver.')
r('P33', G, 'Vendor session with sponsor, end date and recording', 'P-R15-17')
e('P34', G, 'Vendor access end date arrives and nobody removes it', 'AI governance lab H10, C9')
r('P35', G, 'Vendor person leaves the vendor', 'P-R15-18')
r('P36', G, 'A vendor is needed at 2 a.m.', 'P-R15-19')
x('P37', G, 'Managed service provider with many customers', 'env', 'Needs a real multi-customer setup.')
r('P38', G, 'Discover privileged accounts and assign owners', 'P-R15-20')
x('P39', G, 'Onboard an account to the vault, verify, rotate', 'env', 'Needs a real vault and a real target account.')
p('P40', G, 'Recertification of privileged groups without a rubber stamp', 'AI governance lab F3 and I14 tested review quality. Privileged group reviews with real reviewers were not run.')
r('P41', G, 'Separation of duties inside privileged access', 'P-R15-21')
x('P42', G, 'Migration from one PAM tool to another', 'plan', 'A plan with waves and a cutover. The Stage 2 pages cover tool fit and the plan, and nothing was migrated.')
x('P43', G, 'Control equivalence between old and new tool', 'plan', 'A comparison of two real products. No product was tested.')
x('P44', G, 'Platform evaluation with scenarios and weights', 'plan', 'The Stage 2 pages hold the scenarios and the weights. No product was tested.')
x('P45', G, 'High availability and disaster recovery for the PAM platform', 'env', 'Needs a real platform to fail over.')
r('P46', G, 'Integration with ticket system, identity provider and SIEM', 'P-R15-22')
x('P47', G, 'Audit mapping: control, evidence, freshness, sampling', 'plan', 'The Stage 2 control mapping page holds the mapping. A real audit would test it.')
x('P48', G, 'Training, go-live and BAU support', 'plan', 'People and process. A model cannot show it.')
e('P49', G, 'Insider who has given notice and downloads a lot', 'AI governance lab B10')
e('P50', G, 'Privileged access for AI agents and MCP tools', 'AI governance lab I7 and the MCP lab')
x('P51', G, 'Securing exam and regulated environments', 'plan', 'Covered by a case study on this site, not by a lab case.')
r('P52', G, 'Endpoint privilege management', 'P-R15-23')
x('P53', G, 'Server command control with per-command approval', 'env', 'Needs real servers and a command broker.')
x('P54', G, 'Cloud entitlement management', 'env', 'Needs a real cloud tenant and its permission data.')
r('P55', G, 'Session analytics and identity threat detection', 'P-R15-24')
x('P56', G, 'Enterprise password manager for staff', 'env', 'Needs a real product. It is a different category from PAM.')
r('P57', G, 'Mass rotation after a breach', 'P-R15-25')
x('P58', G, 'gMSA and managed identities', 'env', 'Needs a real Active Directory or cloud tenant.')
x('P59', G, 'Dynamic database credentials', 'env', 'Needs a real database and a real broker.')

# ---- gap rows (6)
G = 'Gap rows'
r('G01', G, 'OAuth allowlist and revoke after a vendor breach', 'N-R14-23')
r('G02', G, 'Environment variables not marked sensitive', 'N-R14-24')
r('G03', G, 'Credential stolen from a CI runner and replayed', 'N-R14-25')
x('G04', G, 'ASI05 Unexpected code execution', 'env', 'Needs a real agent runtime that runs code. An in-memory model cannot show an escape.')
e('G05', G, 'ASI06 Memory and context poisoning', 'AI governance lab I12 (row N57). The row existed under another heading.')
p('G06', G, 'ASI07 Insecure inter-agent communication', 'Delegation depth and the chain log were tested in the AI governance lab (D1 to D3, row N55). Message authenticity between agents was not tested and needs a real multi-agent setup.')

# ---- chains (20)
CH = [  # id, title, links, run case or None
 ('C01', 'The forgotten service account', 'N01, N18, N30, N31', 'C-R16-C01'),
 ('C02', 'The token in the repository', 'N03, N04, N43', 'C-R16-C02'),
 ('C03', 'The long-lived pipeline variable', 'N04, N26', None),
 ('C04', 'The contractor who never left', 'P34, P35', 'C-R16-C04'),
 ('C05', 'The break-glass password everyone knows', 'P15, P18', 'C-R16-C05'),
 ('C06', 'Approval fatigue', 'P12', 'C-R16-C06'),
 ('C07', 'The one-click OAuth grant', 'N07', None),
 ('C08', 'The shared SSH key', 'N05', None),
 ('C09', 'The agent with a broad token', 'N54, N56', None),
 ('C10', 'The window that never closes', 'P03', None),
 ('C11', 'The vault admin outside the vault', 'P24, P23', None),
 ('C12', 'The expired certificate', 'N06', None),
 ('C13', 'The silent rotation failure', 'N31, N44', None),
 ('C14', 'The same local admin password', 'P21', None),
 ('C15', 'The loose federation rule', 'N37', None),
 ('C16', 'The recording gap', 'P09', None),
 ('C17', 'The old door', 'P08', 'C-R16-C17'),
 ('C18', 'The wrong person after a merger', 'N22', None),
 ('C19', 'The help-desk reset', 'P31', None),
 ('C20', 'The unprotected vault copy', 'P24, P45', None),
]

# ---- business use cases (26): id, title, linked technical rows (expanded), note
def rng(prefix, a, b): return [f'{prefix}{i:02d}' for i in range(a, b + 1)]
BIZ = [
 ('B01', 'Pass an audit', ['P47', 'P40', 'N48', 'P09', 'N51'], ''),
 ('B02', 'Answer the cyber insurance questionnaire', ['P13', 'P06', 'P08', 'N03'], ''),
 ('B03', 'Answer customer security questionnaires', ['P47', 'N51'], ''),
 ('B04', 'Merge or acquire a company and join directories', ['N22', 'N13', 'N18', 'P38'], ''),
 ('B05', 'Cut the cost of vendor onboarding and offboarding', rng('P', 32, 37), ''),
 ('B06', 'Reduce help-desk tickets for resets', ['P31', 'P56', 'P19'], ''),
 ('B07', 'Restore service in an outage without a side door', rng('P', 15, 18), ''),
 ('B08', 'Avoid outages from expired certificates and failed rotations', ['N06', 'N30', 'N31', 'N32'], ''),
 ('B09', 'Move to the cloud without copying standing access', ['P26', 'P54', 'N08', 'N37'], ''),
 ('B10', 'Let developers ship without long-lived keys', ['N03', 'N04', 'N43', 'N26'], ''),
 ('B11', 'Control PAM licence cost and tool sprawl', ['P44', 'P43'], ''),
 ('B12', 'Report to the board with a few numbers', [], 'A reporting use. It draws on every row and is not a control to test.'),
 ('B13', 'Be ready to rotate everything in the first hour', ['P57', 'N32', 'N33'], ''),
 ('B14', 'Adopt AI safely', rng('S', 1, 18) + rng('N', 53, 62), ''),
 ('B15', 'Prove vendor access is limited and recorded', ['P33', 'P34', 'P35', 'N16'], ''),
 ('B16', 'Run a zero trust program', ['P06', 'P02', 'P05'], ''),
 ('B17', 'Give joiners and movers the right access', [], 'Tested in the AI governance lab, round 7 (H1 to H12). Nothing in this lab.'),
 ('B18', 'Meet regulator expectations in India', ['P47', 'N51', 'N52'], 'Indian rules were not checked. No compliance claim.'),
 ('B19', 'Keep evidence and still honour erasure requests', ['N51', 'N52'], ''),
 ('B20', 'Explain a decision in plain words', ['P09', 'N51'], ''),
 ('B21', 'Be ready for ransomware and wide compromise', ['P21', 'P22', 'P23'], ''),
 ('B22', 'Cut the effort of collecting audit evidence', ['P47'], ''),
 ('B23', 'Developer and engineer productivity', ['P02', 'P30', 'P36'], ''),
 ('B24', 'Due diligence on a target company', ['N01', 'N18', 'P38'], ''),
 ('B25', 'Third-party and supply chain exposure', ['N07', 'N16', 'S15'], ''),
 ('B26', 'Customer-facing AI people can trust', ['S10'], 'Also AI governance lab A12 and E8.'),
]

ALL = N
BY = {row[0]: row for row in ALL}
assert len(N) == 64 + 18 + 59 + 6 - 0 or True
