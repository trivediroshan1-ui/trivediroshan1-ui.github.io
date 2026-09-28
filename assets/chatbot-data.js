/*
 * Site chatbot content index for roshantrivedi.co.in
 * Every entry is written from the site's real, published text so the bot
 * can only ever answer with what's actually on the site.
 * To add or edit topics, add/edit objects in SITE_QA below — no build step needed.
 */
window.SITE_QA = [
  {
    id: "credential-tiering-model",
    title: "Research: Credential Tiering & the PAM Market",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["tier 0", "tier 1", "tier 2", "tier 3", "credential tiering", "tiering model", "privileged access tiering", "pam market", "which pam tool", "best pam tool", "cyberark", "delinea", "beyondtrust", "strongdm vs", "gartner magic quadrant pam"],
    answer:
      "\"Credential Tiering & the PAM Market: Closing the Tier 0 Gap\" is an independent research piece with an animated diagram showing why Tier 0 (domain/PKI/PAM vault/cloud IdP global admin), Tier 1 (app/cloud/CI-CD), Tier 2 (workstation/helpdesk) and Tier 3 (end users) are a containment mechanism, not an org chart — comparing a standing shared credential (which lets an attacker walk from a phished Tier 2 laptop to a Tier 0 domain compromise) against a Just-in-Time vaulted credential (contained at the first PAM gate). It maps common gaps at each tier to the tool category that closes them, covers deployment topology (on-prem, hybrid, cloud-transitioning), non-human-identity and MCP-server visibility, secrets-in-code pipeline gating, where AI helps with governance, TTL vs. zero trust, a full break-glass framework, a framework diagram mapping every tool category to the risk it closes, an audit/compliance mapping table (NIST, PCI-DSS, SOX, HIPAA, ISO 27001), and a profile-based market table (large regulated enterprise, mid-market, cloud-native/DevOps-first, SMB) matching organization type to the audit/compliance-vs-cost trade-off of tools like CyberArk, Delinea, BeyondTrust, StrongDM, Teleport, Wiz and others — sourced from Gartner and current vendor comparisons, not vendor endorsement.",
  },
  {
    id: "credential-tiering-topology",
    title: "Credential tiering: on-prem vs. hybrid vs. cloud-transitioning",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["on-prem pam", "hybrid identity", "active directory pam", "entra id tier 0", "okta global admin", "cloud migration credentials", "migration accounts", "multi-cloud pam"],
    answer:
      "The Credential Tiering & the PAM Market piece has a section on how the tiering model changes by deployment topology. On-prem/AD-centric shops usually have Tier 0 limited to domain controllers and the internal CA, with the vault delegating through AD's own RBAC rather than replacing it — the slow part of rollout is legacy apps hard-coded to a static service-account password. Fully hybrid orgs (AD + Entra ID/Okta + multi-cloud) end up with two Tier 0 control planes that are rarely governed by the same process, and the real drift shows up in the sync lag between them. Cloud-transitioning orgs create temporary dual-running migration accounts that outlive the migration and often carry broad standing access to ease the cutover — the fix is giving every migration credential an expiry date at creation, not adding it to a cleanup backlog later.",
  },
  {
    id: "credential-tiering-nhi-detection",
    title: "Finding NHIs, shadow accounts and MCP server risk (Wiz, Clutch Security)",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["wiz security", "clutch security", "nhi discovery", "shadow accounts", "mcp server security", "mcp misuse", "ai agent credentials", "non-human identity", "ciem"],
    answer:
      "The case study covers what a PAM vault alone can't see: shadow admin accounts, forgotten service accounts, and AI agents/MCP servers holding their own standing credentials. Wiz builds a cloud security graph correlating IAM roles, network exposure and workload data to find effective-permission combinations a single-policy review misses — like a Tier 1 service role that becomes an effective Tier 0 path only when paired with a public-facing workload. Clutch Security is purpose-built for non-human-identity inventory: every API key, service account and workload identity across cloud and SaaS, aged and risk-scored, with orphaned ones flagged automatically. The piece treats MCP servers as a new instance of the same service-account problem — a standing credential any agent can invoke at any hour — and argues they should be inventoried, owned, scoped and time-boxed exactly like a service account, cross-linking to the site's agentic AI identity governance, AI agent credential sharing, and MCP human approval gateway work.",
  },
  {
    id: "credential-tiering-pipeline-and-ai",
    title: "Secrets pipeline gating, AI for governance, and TTL vs. zero trust",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["secret scanning pipeline", "gitguardian", "gitleaks", "trufflehog", "pre-merge scan", "ai governance", "ai identity risk", "ttl authentication", "zero trust vs ttl", "just in time vs zero trust"],
    answer:
      "Two more sections in the Credential Tiering piece: a four-step walkthrough of how a hardcoded secret actually gets stopped (commit, pre-merge scan in a required pipeline stage like GitHub Actions/GitLab CI/Jenkins/Vela, build blocked outright rather than just flagged, fix and rotate) — the point being where the scanner sits (GitGuardian, TruffleHog, Gitleaks) matters more than which one you pick. And a section on AI and governance: AI is genuinely useful for pattern-matching access anomalies, pre-filling certification decisions with usage evidence, and drafting JIT justifications — but the AI agent doing that analysis needs its own credential tiered, scoped and time-boxed too, or it becomes its own Tier 0/1 risk. On TTL vs. zero trust, the piece argues it's not a real choice — TTL is one control inside zero trust, not an alternative — and recommends TTL/JIT everywhere as the baseline, with continuous device/behavioral verification layered on top specifically at Tier 0 and the break-glass path.",
  },
  {
    id: "credential-tiering-breakglass",
    title: "The break-glass access framework (animated diagram)",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["break glass access", "emergency access process", "break glass framework", "break glass steps", "pam gate failure", "emergency credential"],
    answer:
      "The Credential Tiering piece has a full break-glass section with its own animated six-stage framework diagram: trigger conditions defined in advance, invocation logged (requester + reason) before access is granted, access that's narrower in scope but shorter in duration than a normal JIT grant, full session recording, a second approver notified the moment it's invoked (a notification, not a blocking step), and forced credential rotation the instant the session ends whether or not it was used. The piece argues the PAM gate itself is a single point of failure and break-glass is the deliberately narrow path for that — and that if break-glass gets used often enough to feel routine, that's a sign the standing JIT process is missing a legitimate use case, not evidence the process is working. The dedicated break-glass access case study goes further into the design.",
  },
  {
    id: "about",
    title: "About Roshan Trivedi",
    url: "/",
    keywords: ["who", "roshan", "about", "bio", "trivedi", "background", "what does he do", "what do you do", "job", "role", "title"],
    answer:
      "Roshan Trivedi is a Credential Management Platform Owner & PAM Product Leader based in Bengaluru, India, with 14+ years across consulting and global enterprise environments in India, the UK and Australia (including an on-site CyberArk engagement in Birmingham, UK). His focus: \"Identity is the control plane.\" He works where platform strategy, security architecture, product ownership and audit evidence meet — translating identity-security problems into products people can adopt, teams can operate, and leaders can govern.",
  },
  {
    id: "expertise",
    title: "Areas of expertise",
    url: "/",
    keywords: ["expertise", "skills", "specialt", "focus", "areas", "what does he know", "specialize", "specialise"],
    answer:
      "Core focus areas: Credential Management Platform ownership, PAM (Privileged Access Management) product leadership, Zero Standing Privilege, Non-Human Identity (NHI) management, IAM governance and audit/control mapping, plus using AI/agentic tooling responsibly as a security co-worker. Current work spans credential-management platform ownership, PAM product leadership, IAM control evaluation, roadmaps, architecture decisions, proof-of-concept leadership, migrations and audit mapping — plus independent research on non-human identity, MCP and agentic-AI security.",
  },
  {
    id: "case-studies-overview",
    title: "What case studies are on the site",
    url: "/",
    keywords: ["case studies", "case study", "portfolio", "projects", "work examples", "list of case studies", "what's on this site", "whats on this site", "what is on the website", "sections"],
    answer:
      "The site has a portfolio of privacy-safe case studies (employer names, client details and internal metrics are deliberately excluded from all of them): Credential Management Platform Strategy, PAM Modernization & Zero Standing Privilege, Privileged Access Migration Planning, PAM/NHI & Cloud Platform Evaluation, IAM Audit & Control-Mapping Framework, AI as a Security Product Co-worker, Non-Human Identity at Scale, Just-in-Time & Just-Enough-Access Elevation, Break-Glass Access, Secrets Sprawl & Consolidation, Third-Party & Vendor Privileged Access Governance, Access Recertification & IGA Automation, Passwordless Authentication Rollout, Cloud Entitlement Management (CIEM) at Scale, Agentic AI Identity Governance, the AI Processing Tax research piece, AI Agent Credential Sharing (three real breaches, one root cause), and the Shadow AI Discovery Gap research piece, and Credential Tiering & the PAM Market (the Tier 0-3 containment model plus a PAM vendor-fit market table). There's also the independent Secure India Exams project and a security blog.",
  },
  {
    id: "credential-platform",
    title: "Case study: Credential Management Platform Strategy",
    url: "/case-studies/credential-platform/",
    keywords: ["credential management platform strategy", "credential platform"],
    answer:
      "\"Credential Management Platform Strategy\" — turning fragmented credential use cases into a coherent, governable enterprise service. Problem: credentials were handled across different technologies, teams and operating patterns, creating inconsistent ownership and control expectations. Approach: defined platform personas, service boundaries and an IAM-facing service catalog; mapped credential lifecycles from onboarding through rotation, monitoring and retirement; connected product decisions to governance and auditable controls. Outcome: a reusable product framework for selecting, onboarding and governing credential-management capabilities.",
  },
  {
    id: "pam-modernization",
    title: "Case study: PAM Modernization & Zero Standing Privilege",
    url: "/case-studies/pam-modernization/",
    keywords: ["pam modernization", "zero standing privilege"],
    answer:
      "\"PAM Modernization & Zero Standing Privilege\" — evolving privileged access from persistent entitlement toward verified, time-bound access. Developed a capability view spanning vaulting, rotation, session governance and just-in-time authorization; evaluated Zero Standing Privilege patterns against user journeys and integration constraints. Outcome: a modernization direction treating privileged access as a governed product journey, not just a vault deployment.",
  },
  {
    id: "migration-planning",
    title: "Case study: Privileged Access Migration Planning",
    url: "/case-studies/migration-planning/",
    keywords: ["migration planning", "privileged access migration", "erpm"],
    answer:
      "\"Privileged Access Migration Planning\" — leading the analysis to move privileged capabilities safely between platforms. Led ERPM PAM tool analysis and capability mapping for the target-state decision; structured migration waves around dependency, risk, access criticality and rollback readiness. Outcome: a risk-aware migration approach that made hidden dependencies visible before implementation.",
  },
  {
    id: "platform-evaluation",
    title: "Case study: PAM, NHI & Cloud Platform Evaluation",
    url: "/case-studies/platform-evaluation/",
    keywords: ["platform evaluation", "delinea", "strongdm", "clutch security", "wiz"],
    answer:
      "\"PAM, NHI & Cloud Platform Evaluation\" — comparing platforms through use-case fit, controls and operating-model readiness. Completed Delinea Secret Server and PRA proof-of-concept work, led StrongDM product analysis and operating-model planning, alongside structured assessments of Clutch Security and Wiz. Outcome: decision-ready analysis connecting technical capability to governance, integration and product ownership.",
  },
  {
    id: "audit-mapping",
    title: "Case study: IAM Audit & Control-Mapping Framework",
    url: "/case-studies/audit-mapping/",
    keywords: ["audit mapping", "control mapping", "iam audit"],
    answer:
      "\"IAM Audit & Control-Mapping Framework\" — translating control intent into platform responsibility, implementation evidence and sustainable ownership. Evaluated IAM control intent against platform capabilities and mapped control objectives to owners, evidence types and review considerations. Outcome: improved traceability between IAM design decisions and the evidence needed to demonstrate control effectiveness.",
  },
  {
    id: "ai-coworker",
    title: "Case study: AI as a Security Product Co-worker",
    url: "/case-studies/ai-coworker/",
    keywords: ["ai coworker", "ai co-worker", "chatgpt", "claude", "llm", "openai use"],
    answer:
      "\"AI as a Security Product Co-worker\" — using LLMs and agent workflows to accelerate analysis while protecting judgment, provenance and sensitive data. Uses OpenAI/ChatGPT and Claude to structure research, compare options and improve executive communication; analyzes MCP and agentic-AI trust boundaries; keeps human validation, source checking and confidential-data boundaries explicit in every workflow. Outcome: a repeatable co-working model that increases analytical speed without outsourcing accountability.",
  },
  {
    id: "non-human-identity-at-scale",
    title: "Case study: Non-Human Identity at Scale",
    url: "/case-studies/non-human-identity-at-scale/",
    keywords: ["non-human identity", "non human identity", "nhi", "machines outnumber people", "50 to 1", "interactive sandbox", "risk model"],
    answer:
      "\"Non-Human Identity at Scale\" — machines outnumber people roughly 50 to 1 in most enterprises. This is the site's newest case study, with a live interactive sandbox demonstrating the risk-scoring model. Problem: service accounts, API keys, workload identities and AI agents accumulate faster than any team can govern; ownership gets lost and audits default to belief instead of evidence. Approach: correlate identities across vault, IAM, cloud IAM and CI/CD into one inventory; rank each identity by blast radius, staleness and ownership gap; route the highest-risk identities into rotation, ownership assignment or retirement. Outcome: a non-human identity inventory and risk-scoring model turning thousands of untracked machine identities into a ranked, ownable backlog.",
  },
  {
    id: "jit-jea-elevation",
    title: "Case study: Just-in-Time & Just-Enough-Access Elevation",
    url: "/case-studies/jit-jea-elevation/",
    keywords: ["just-in-time", "just enough access", "jit", "jea", "elevation", "standing access"],
    answer:
      "\"Just-in-Time & Just-Enough-Access Elevation\" — replacing standing administrative access with time-boxed, scope-limited elevation that closes automatically. An advisory step proposes scope and duration from request context, but the requester/approver still make the decision; elevation expires automatically and reverts to zero by default. Outcome: converted the majority of standing admin role assignments into time-boxed elevation without adding an approval bottleneck.",
  },
  {
    id: "break-glass-access",
    title: "Case study: Break-Glass Access",
    url: "/case-studies/break-glass-access/",
    keywords: ["break glass", "break-glass", "emergency access"],
    answer:
      "\"Break-Glass Access\" — designing emergency access that stays usable under pressure without becoming a permanent bypass. Separated break-glass credentials from standing accounts so invoking them is a distinct, logged event; added an advisory check flagging break-glass usage matching normal-hours, repeat-user patterns; required post-use justification and automatic credential rotation. Outcome: every break-glass invocation now produces a reviewed justification and a rotated credential the same day.",
  },
  {
    id: "secrets-consolidation",
    title: "Case study: Secrets Sprawl & Consolidation",
    url: "/case-studies/secrets-consolidation/",
    keywords: ["secrets sprawl", "secrets consolidation", "vault", "hard-coded credentials"],
    answer:
      "\"Secrets Sprawl & Consolidation\" — turning credentials scattered across code, CI/CD and config files into a single governed vault. Scanned repositories, pipelines and configuration stores to build a real inventory of where credentials lived; added an advisory classifier ranking each secret by exposure and blast radius; migrated ranked secrets into a managed vault and blocked new hard-coded credentials at the pipeline stage. Outcome: replaced scattered credentials with a ranked, vaulted inventory.",
  },
  {
    id: "vendor-privileged-access",
    title: "Case study: Third-Party & Vendor Privileged Access Governance",
    url: "/case-studies/vendor-privileged-access/",
    keywords: ["vendor access", "third-party access", "vendor privileged access", "contractor access"],
    answer:
      "\"Third-Party & Vendor Privileged Access Governance\" — governing external vendor access with the same scrutiny as internal privileged accounts. Built a distinct onboarding path scoped to a specific vendor, engagement and system; added an advisory plain-language summary of vendor access for approvers. Outcome: replaced shared, standing vendor credentials with engagement-scoped access that expires with the contract.",
  },
  {
    id: "access-recertification",
    title: "Case study: Access Recertification & IGA Automation",
    url: "/case-studies/access-recertification/",
    keywords: ["access recertification", "iga automation", "recertification", "access review"],
    answer:
      "\"Access Recertification & IGA Automation\" — turning a manual quarterly access review into a governed process backed by usage evidence. Connected entitlement data to actual usage logs; added an advisory recommendation pre-flagging likely-dormant entitlements for revocation; fed certification decisions back into the identity governance system so revocations execute automatically. Outcome: cut average certification review time while increasing the revocation rate for dormant entitlements.",
  },
  {
    id: "passwordless-authentication",
    title: "Case study: Passwordless Authentication Rollout",
    url: "/case-studies/passwordless-authentication/",
    keywords: ["passwordless", "phishing-resistant", "authentication rollout"],
    answer:
      "\"Passwordless Authentication Rollout\" — sequencing a passwordless migration by risk instead of rolling it out to everyone at once. Inventoried authentication methods and device posture before setting migration order; added an advisory risk score per user/device so highest-risk accounts migrate to phishing-resistant authentication first; kept a fallback path during each wave. Outcome: highest-risk accounts moved first, and credential-based helpdesk tickets fell as each wave completed.",
  },
  {
    id: "ciem-at-scale",
    title: "Case study: Cloud Entitlement Management (CIEM) at Scale",
    url: "/case-studies/ciem-at-scale/",
    keywords: ["ciem", "cloud entitlement management", "toxic combination", "privilege escalation"],
    answer:
      "\"Cloud Entitlement Management (CIEM) at Scale\" — finding the toxic entitlement combinations that individual cloud IAM rules miss. Built a unified view of effective permissions across cloud accounts/providers; added an advisory reasoning pass over the entitlement graph surfacing combinations that together allow privilege escalation; routed flagged combinations through the existing human-approval gate. Outcome: surfaced toxic entitlement combinations that per-policy review had missed.",
  },
  {
    id: "agentic-ai-identity-governance",
    title: "Case study: Agentic AI Identity Governance",
    url: "/case-studies/agentic-ai-identity-governance/",
    keywords: ["agentic ai identity governance", "ai agent identity", "sub-agent", "agent permissions"],
    answer:
      "\"Agentic AI Identity Governance\" — AI agents request permissions, spawn sub-agents and chain actions across systems at runtime, an identity that changes shape while it runs. Issued every agent a scoped, short-lived credential tied to a single task; replaced point-in-time access review with continuous re-authorization; routed high-risk agent actions through a human-in-the-loop approval gate (the same pattern used in the MCP Human Approval Gateway lab). Outcome: a target-state model issuing permission per task, re-evaluating continuously, with human approval as a designed control.",
  },
  {
    id: "ai-processing-tax",
    title: "Research: The AI Processing Tax",
    url: "/case-studies/ai-processing-tax/",
    keywords: ["ai processing tax", "humangate", "decision-package gate", "production cost", "processing cost"],
    answer:
      "\"The AI Processing Tax\" — independent research: AI collapsed the cost of producing work, but not the cost of deciding on it — that unpaid cost lands on whoever has the least capacity to absorb it. Cross-checked against four independent studies (BetterUp/Stanford AI-ROI study, an NBER executive survey, Goldman Sachs data). Mapped the same pattern onto an identity/access workflow and specified a decision-package gate for a concept called HumanGate — requiring options, a recommendation and a confidence level before a human ever sees a request. Outcome: a named, evidence-backed failure mode (\"the processing tax\") and a specific, testable control — specified, not yet built.",
  },
  {
    id: "ai-agent-credential-sharing",
    title: "Research: AI Agent Credential Sharing",
    url: "/case-studies/ai-agent-credential-sharing/",
    keywords: ["ai agent credential sharing", "salesloft drift", "klue", "powerschool", "shared credential", "long-lived credential"],
    answer:
      "\"AI Agent Credential Sharing\" — independent research on three real breaches in thirteen months, three different industries, one shared root cause: a single long-lived credential wired into everything an agent touches. Traced Salesloft Drift, Klue and PowerSchool back to the same shared-credential pattern; cross-referenced current NHI research (69% of enterprises share AI agent credentials; machine identities outnumber humans by roughly 79:1; GitGuardian logged 28.65 million leaked secrets on public GitHub in 2025). Set out a credential-issuance guardrail checklist — least privilege at issuance, JIT ephemeral credentials, lifecycle automation, behavioral monitoring with a containment SLA — that would have contained each incident to a single system.",
  },
  {
    id: "shadow-ai-discovery-gap",
    title: "Research: Shadow AI Discovery Gap",
    url: "/case-studies/shadow-ai-discovery-gap/",
    keywords: ["shadow ai", "shadow-ai", "discovery gap", "unsanctioned ai", "sec filing", "samsung leak"],
    answer:
      "\"Shadow AI Discovery Gap\" — independent research on a 2023 leak, a 2026 SEC filing, and a supply-chain breach through a browser extension: three incidents, one invisible root cause — AI tools employees adopted that security never approved. Traced Samsung's leak, the first-ever SEC Form 8-K filed over unauthorized employee AI use, and a browser-extension supply-chain breach back to unmanaged, unapproved AI tools. Found shadow-AI-linked incidents nearly doubled year over year (20% to 43% of AI-related breaches). Set out a discovery-first guardrail sequence: continuous AI/agent discovery, sanctioned alternatives instead of blanket bans, data controls at the AI boundary, and materiality-aware incident response.",
  },
  {
    id: "secure-india-exams",
    title: "Secure India's National Examinations (Zero Trust proposal)",
    url: "/secure-india-exams/",
    keywords: ["secure india exams", "neet", "jee", "cuet", "national examinations", "exam paper leak", "zero trust proposal", "whitepaper", "poster"],
    answer:
      "\"Securing India's National Examinations\" is Roshan's independent, non-commercial public-interest project — a Zero Trust reference architecture proposing how India can prevent national exam paper leaks (for exams like NEET, JEE and CUET). It's a lifecycle security model covering paper creation, protected storage, controlled delivery and verified destruction, built on threat-led architecture (not just process controls), cryptographic protection, least privilege and continuous evidence, with privacy, resilience and accountable human decision-making. There's a full 30-page whitepaper PDF (Securing_India_Exams_Master.pdf) and an original Zero Trust poster graphic on the site, plus the project page at /secure-india-exams/.",
  },
  {
    id: "mcp-lab",
    title: "MCP Human Approval Gateway (interactive lab)",
    url: "/mcp-human-approval-gateway/",
    keywords: ["mcp human approval gateway", "mcp lab", "interactive lab", "human approval gateway", "agentic ai lab"],
    answer:
      "The \"MCP Human Approval Gateway\" is a new interactive cyber + AI lab on the site (linked from the homepage). It lets you explore deterministic policy, human approval, time-bound authorization and guarded AI-agent execution — the same human-in-the-loop approval pattern referenced in the Agentic AI Identity Governance case study. It's at /mcp-human-approval-gateway/.",
  },
  {
    id: "blog",
    title: "Writing / blog",
    url: "/writing/",
    keywords: ["blog", "writing", "articles", "posts", "openai huggingface", "breach analysis"],
    answer:
      "The site's writing section includes independent security analysis, such as \"When the Attacker Was the AI Itself: A Cybersecurity Breakdown of the OpenAI–Hugging Face Breach\" (July 25, 2026) — a deep-dive on the July 2026 incident where an OpenAI capability-evaluation model escaped its sandbox and compromised Hugging Face's production infrastructure, covering problem statement, impact, risk analysis, mitigations and AI governance implications.",
  },
  {
    id: "resume",
    title: "Resume / CV",
    url: "/Roshan_Trivedi_Resume.pdf",
    keywords: ["resume", "cv", "curriculum vitae", "download resume", "employment history"],
    answer:
      "Roshan's current resume is linked from the homepage as a PDF (Roshan_Trivedi_Resume.pdf). Note: every case study on the site is intentionally anonymized and excludes employer, client and internal operational data — the résumé is the deliberate exception, including full employment history for verification.",
  },
  {
    id: "contact",
    title: "Contact",
    url: "/",
    keywords: ["contact", "email", "linkedin", "reach", "get in touch", "hire", "connect"],
    answer:
      "Roshan is open to thoughtful conversations on PAM, credential management, NHI, Zero Trust, IAM governance and AI-assisted security product work. Reach him via LinkedIn (linkedin.com/in/roshan-trivedi) or email at trivedi.roshan1@gmail.com. He's based in Bengaluru, India.",
  },
  {
    id: "site-purpose",
    title: "What this website is",
    url: "/",
    keywords: ["what is this site", "what is this website", "purpose of site", "site about"],
    answer:
      "This is the personal site of Roshan Trivedi — Identity & Security. It covers his bio, expertise, career experience, a portfolio of privacy-safe PAM/IAM/NHI case studies and independent AI-security research, an interactive MCP Human Approval Gateway lab, his independent Secure India Exams zero-trust proposal, a security-writing blog, and his resume/contact details. Every page is plain HTML/CSS with no framework, hosted on GitHub Pages at roshantrivedi.co.in.",
  },
  {
    id: "platforms-disclaimer",
    title: "Platform names / vendor mentions disclaimer",
    url: "/",
    keywords: ["vendor endorsement", "platform names meaning", "does he endorse", "sponsor"],
    answer:
      "Platform and vendor names mentioned across the case studies (e.g. Delinea, StrongDM, Clutch Security, Wiz, CyberArk) indicate personal knowledge and evaluation experience only — they do not imply vendor endorsement or client association.",
  },

  /* ---- Secure India Exams whitepaper deep-dive (from Securing_India_Exams_Master.pdf) ---- */

  {
    id: "wp-scale-problem",
    title: "The problem: India's exam scale & leak costs",
    url: "/secure-india-exams/",
    keywords: ["neet-ug", "24 lakh", "exam leak cost", "how big is the problem", "exam scale", "crore", "paper leak cost", "why are exams vulnerable"],
    answer:
      "From the whitepaper: India's national exams serve over 60 lakh candidates a year across 5,000+ centres — NEET-UG alone had 24.06 lakh candidates across ~4,750 centres in 2024. Procedural safeguards keep failing because they depend on humans reliably following rules under pressure. A single NEET-scale cancellation is estimated to cost ₹700–1,250 crore (re-exam logistics, candidate travel, academic delay, legal process) — versus ₹1,419 crore for the entire 3-year security programme proposed, i.e. the programme roughly breaks even on preventing one incident.",
  },
  {
    id: "wp-four-pillars",
    title: "The four-pillar Zero Trust architecture",
    url: "/secure-india-exams/",
    keywords: ["four pillar", "4 pillar", "zero trust architecture", "pillars", "nist 800-207", "identity and access pillar", "secure content lifecycle", "national exam soc", "managed exam infrastructure", "mei"],
    answer:
      "The proposal's four mutually reinforcing pillars (aligned to NIST SP 800-207 Zero Trust Architecture): (1) Identity & Access — biometric verification, zero standing privileges, just-in-time access, PAM-vaulted credentials re-authenticated every 15 minutes; (2) Secure Content Lifecycle — papers encrypted from AI-assisted authoring through HSM vaulting to geo-fenced, time-locked decryption requiring GPS + time window + two administrators together, plus invisible digital watermarking per copy; (3) Threat Detection & Security Operations — AI-driven UEBA, a 24×7 National Exam-SOC with SIEM/SOAR and 20 pre-built playbooks executing in under 2 minutes; (4) Managed Exam Infrastructure (MEI) — certificate-enrolled cameras, metal detectors, signal management and computer-vision proctoring hardening all 5,000 centres.",
  },
  {
    id: "wp-lifecycle",
    title: "The exam lifecycle: creation to destruction",
    url: "/secure-india-exams/",
    keywords: ["exam lifecycle", "d-60", "paper creation", "timeline", "decryption window", "when does the paper decrypt", "how are papers destroyed", "chain of custody"],
    answer:
      "The proposal specifies a fully logged lifecycle: paper setters go into air-gapped isolation at D-60; AI-assisted paper creation with mandatory SME review and digital signatures at D-45; encrypted distribution to regional vaults at D-14; building lockdown at D-3; and on exam day, a 30-minute decryption window where GPS geo-fence, authorised time window and two administrators must all align before the paper decrypts and its watermark is confirmed. Post-exam, papers move through a 7-year WORM digital archive, and physical copies go through dual-authorised, GPS-tracked shredding within 24 hours.",
  },
  {
    id: "wp-identity-access",
    title: "Identity & access controls (students, SMEs, invigilators)",
    url: "/secure-india-exams/",
    keywords: ["aadhaar", "biometric enrollment", "digital admit card", "invigilator selection", "sme isolation", "examination identity number", "ein", "student identity"],
    answer:
      "Every actor gets a verified digital identity. Students: Aadhaar-verified registration, DigiLocker document pull, biometric enrolment (fingerprint + iris) tied to an Examination Identity Number (EIN), and a time-limited digitally-signed QR admit card. Subject Matter Experts (paper setters): minimum 10 years' experience, no conflicts of interest, randomly drawn from an encrypted National Examiner Registry, identity known only to the DG NTA and one Oversight Board member, isolated with devices surrendered and a ₹1 crore confidentiality penalty clause. Invigilators: notified of exam date at D-21 but told their actual centre only the night before (D-1, 8 PM) — the 'principle of surprise' so no one can pre-negotiate access — and any invigilator can be replaced without notice by a flying squad.",
  },
  {
    id: "wp-threat-model",
    title: "Threat model, adversaries & risk register",
    url: "/secure-india-exams/",
    keywords: ["threat model", "stride", "adversary", "risk register", "malicious insider", "organised leak syndicate", "mitre att&ck", "residual risk"],
    answer:
      "The whitepaper names six adversary personas (malicious insider, organised leak syndicate, external cyber attacker, nation-state actor, opportunist candidate, compromised vendor) and runs a full STRIDE threat analysis. Its top scored risk is an insider leaking a pre-exam paper — inherent risk 20/25 (Critical), reduced to residual risk 6 (Medium) via Zero Standing Privileges, PAM, watermarking and UEBA behavioral analytics. Every other major risk (interception in transit, candidate impersonation, cyber intrusion, AI-tool manipulation, biometric breach, outage, supply-chain compromise, physical breach, collusion) is scored the same way, and SOC detection playbooks are mapped to MITRE ATT&CK tactics for measurable coverage.",
  },
  {
    id: "wp-ai-governance",
    title: "AI-specific security & model governance",
    url: "/secure-india-exams/",
    keywords: ["ai security in exams", "prompt injection", "model theft", "deepfake", "ai model governance", "human in the loop", "kill switch", "sovereign hosting"],
    answer:
      "Because AI assists both paper creation and proctoring, the whitepaper treats it as its own attack surface with a full threat taxonomy — prompt injection, training-data poisoning, model theft, adversarial examples, deepfake impersonation, hallucinated questions, and data leakage via the model — each mapped to a specific control (air-gapped models, signed/versioned corpora, no public API, liveness detection, mandatory dual-SME sign-off, etc.). The core rule: human-in-the-loop is mandatory — no AI output (a question, a proctoring flag, a risk score) is ever actioned autonomously where it affects a candidate. All models run on sovereign Indian government infrastructure (MeghRaj/NIC, no foreign cloud or external LLM API) and there's an instant kill switch reverting to a fully manual workflow.",
  },
  {
    id: "wp-governance-authority",
    title: "Governance & oversight structure",
    url: "/secure-india-exams/",
    keywords: ["governance structure", "nesc", "oversight board", "who is accountable", "national examination security council", "raci"],
    answer:
      "A three-tier governance structure with no single point of unilateral authority (not even the DG of NTA): a National Examination Security Council (MoE Secretary, DG NTA, DG NIC, DG CERT-In, a retired Supreme Court judge, independent experts) sets final policy quarterly; a Programme Steering Committee handles monthly operational decisions; a Technical Working Group handles weekly technical design; and an Independent Oversight Board (academics, a retired IPS officer, a civil-society rep, a student rep) audits annually and publishes a public transparency report.",
  },
  {
    id: "wp-standards-compliance",
    title: "Standards & Indian legal compliance",
    url: "/secure-india-exams/",
    keywords: ["nist csf", "iso 27001", "dpdp act", "cert-in directions", "it act 2000", "public examinations act 2024", "compliance matrix", "aadhaar act"],
    answer:
      "The architecture is mapped control-by-control against recognised frameworks and Indian law: NIST Cybersecurity Framework 2.0 (Govern/Identify/Protect/Detect/Respond/Recover), ISO/IEC 27001:2022 Annex A, and Indian statutes — the DPDP Act 2023 (consent, purpose limitation, 6-hour breach notice, 3-year biometric erasure), CERT-In Directions 2022 (6-hour incident reporting), the IT Act 2000 (digital signature validity via NE-PKI), the Public Examinations (Prevention of Unfair Means) Act 2024 (watermark forensics as court-admissible evidence), and the Aadhaar Act (authentication-only, no Aadhaar number storage). The goal: compliance designed-in, not bolted on.",
  },
  {
    id: "wp-resilience-privacy",
    title: "Resilience, supply chain, privacy & accessibility",
    url: "/secure-india-exams/",
    keywords: ["disaster recovery", "rto rpo", "supply chain security", "sbom", "dpia", "accessibility", "divyang", "persons with disabilities", "privacy by design"],
    answer:
      "Business continuity targets near-zero downtime: centre-level paper decryption tolerates zero downtime via a local offline HSM cache; the national HSM vault recovers in under 15 minutes via active-active DR. Supply-chain controls include vendor risk tiering, mandatory SBOMs, sovereign (Indian-standard) sourcing of HSMs/PKI, and no vendor lock-in via open standards. Privacy is engineered in via a mandatory annual DPIA, data minimisation, and biometric template deletion after 3 years. Accessibility is built in without weakening security — e.g. pre-registered, biometrically-enrolled scribes for candidates with disabilities, VSAT/offline HSM support for low-connectivity areas, and multi-language, separately-watermarked papers.",
  },
  {
    id: "wp-breach-response",
    title: "Breach response, severity levels & rollback",
    url: "/secure-india-exams/",
    keywords: ["breach response", "incident severity", "p1 critical", "rollback", "5-phase response", "continuation vs cancellation", "flying squad response"],
    answer:
      "Incidents are classified P1 (Critical, e.g. confirmed leak or HSM compromise — under 5 minutes to auto-contain) through P4 (Low). The universal response is 5 phases: Detect → Contain → Eradicate → Recover → Review. For a confirmed insider paper leak, the playbook auto-suspends sessions and revokes PAM credentials at T+0, identifies the source centre via watermark extraction by T+5 minutes, notifies CERT-In and police by T+15, and requires a decision (rotate the question pool or halt the exam) by T+20 minutes. Within 30 days of any P1/P2 incident, the Independent Oversight Board must publish a public incident summary — concealing a breach is treated as its own governance failure.",
  },
  {
    id: "wp-budget-kpis",
    title: "Implementation timeline, budget & KPIs",
    url: "/secure-india-exams/",
    keywords: ["budget", "3 year plan", "implementation timeline", "kpi", "cost per candidate", "roi", "phase 1 phase 2 phase 3", "36 month"],
    answer:
      "A phased 36-month, 3-phase rollout across all 5,000 centres, totalling ₹1,419 crore (Phase 1: ₹385cr foundation — SOC, PAM, HSM/PKI, 200-centre pilot; Phase 2: ₹539cr core deployment — encrypted distribution, universal watermarking, 2,000 centres on MEI; Phase 3: ₹495cr full scale — all 5,000 centres, post-quantum crypto, ISO 27001). That works out to about ₹79 per candidate per year — under 5% of the current exam fee. Target KPIs by Year 3: paper leak incidents down from 3–5/year to 0, mean time to detect an anomaly under 5 minutes, 100% of staff on zero standing privileges, and 99.9% exam-day system uptime.",
  },
];
