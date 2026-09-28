/*
 * Site chatbot content index for roshantrivedi.co.in
 * Every entry is written from the site's real, published text so the bot
 * can only ever answer with what's actually on the site.
 * To add or edit topics, add/edit objects in SITE_QA below — no build step needed.
 */
window.SITE_QA = [
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
      "The site has a portfolio of privacy-safe case studies (employer names, client details and internal metrics are deliberately excluded from all of them): Credential Management Platform Strategy, PAM Modernization & Zero Standing Privilege, Privileged Access Migration Planning, PAM/NHI & Cloud Platform Evaluation, IAM Audit & Control-Mapping Framework, AI as a Security Product Co-worker, Non-Human Identity at Scale, Just-in-Time & Just-Enough-Access Elevation, Break-Glass Access, Secrets Sprawl & Consolidation, Third-Party & Vendor Privileged Access Governance, Access Recertification & IGA Automation, Passwordless Authentication Rollout, Cloud Entitlement Management (CIEM) at Scale, Agentic AI Identity Governance, the AI Processing Tax research piece, AI Agent Credential Sharing (three real breaches, one root cause), and the Shadow AI Discovery Gap research piece. There's also the independent Secure India Exams project and a security blog.",
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
];
