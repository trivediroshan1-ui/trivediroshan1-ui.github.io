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
    keywords: ["tier 0", "tier 1", "tier 2", "tier 3", "credential tiering", "tiering model", "privileged access tiering", "pam market", "which pam tool", "best pam tool", "cyberark", "delinea", "beyondtrust", "strongdm vs", "mint test", "blast radius"],
    answer:
      "\"Credential Tiering & the PAM Market: Closing the Tier 0 Gap\" is independent research. A tier is a claim about which credentials can mint access to which other credentials, so a credential belongs in the highest tier of anything it can change, wherever it is stored. Each tier gets a fixed set of controls (storage, rotation, access path, monitoring, approval and session recording) that get stronger toward Tier 0. The page covers six credential classes, a classify-place-control-review workflow with a pipeline deploy key example, how PAM products map to what each tier needs, a profile view of which categories to shortlist by organization shape (large regulated enterprise, mid-market, cloud-native, small first deployment), a phased build, guardrails, audit questions and common mistakes. It says plainly that the examples are not a ranking and that no vendor is the answer for every tier.",
  },
  {
    id: "credential-tiering-workflow",
    title: "Credential tiering: the workflow and the deploy-key example",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["classify credential", "place credential in tier", "credential classes", "deploy key", "pipeline key", "owner for every credential", "six controls", "old path"],
    answer:
      "The tiering page runs one loop for every credential: name an owner, classify it by what it can change, place it with the mint test (the highest tier it could reach, directly or by creating something else), apply the tier's controls and close the old path, then review on usage and whenever something changes. Its worked example is a pipeline deploy key that looks like Tier 1 until the mint test shows its role can create roles and attach policies, which makes it Tier 0 until the permissions are cut.",
  },
  {
    id: "credential-tiering-market",
    title: "Credential tiering: where the PAM market fits",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["pam vendors", "pam shortlist", "wiz security", "clutch security", "teleport", "manageengine", "hashicorp vault", "gitguardian", "nhi market", "pam capabilities"],
    answer:
      "The tiering page says PAM products are sold as capabilities such as vaulting, session management and just-in-time access, not as tiers, so you write down what each tier needs first and then look at tools. It lists tool categories per tier (PAM vault with session recording for Tier 0, secrets management, cloud entitlement management and scanning for Tier 1, endpoint privilege management for Tier 2, NHI governance and identity governance across tiers) and a profile view by organization shape. The examples are not a league table. It also notes two market signals: GitGuardian's count of new hardcoded secrets in public commits, and consolidation of NHI products into larger platforms.",
  },
  {
    id: "credential-tiering-guardrails",
    title: "Credential tiering: phases, guardrails and what goes wrong",
    url: "/case-studies/credential-tiering-model/",
    keywords: ["tiering phases", "tiering guardrails", "tier 0 too small", "tiering mistakes", "ai agent tier", "temporary credentials expiry", "tiering lessons"],
    answer:
      "The tiering page builds in phases, Tier 0 first: agree the definitions, inventory and classify, close Tier 0 with a gate, hardware-key sign-in, two approvers and recording, then work down. Common failures it lists: Tier 0 drawn too small, a vault that stops at Tier 0, classification done once, the gate being a single point of failure (hence a tested break-glass path), tiers turning into org charts, a product mistaken for a tier, temporary credentials that never expire, and AI agents with standing access. Habits it recommends include asking what a credential can mint before where it lives, finishing Tier 0 first, keeping to four tiers and testing the boundary by trying to cross it.",
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
      "The site has 20 privacy-safe case studies (employer names, client details and internal metrics are left out of all of them): Credential Management Platform Strategy, PAM Modernization & Zero Standing Privilege, How I Run a Privileged Access Program, Privileged Access Migration Planning, PAM/NHI & Cloud Platform Evaluation, IAM Audit & Control-Mapping Framework, AI as a Security Product Co-worker, Non-Human Identity at Scale, Just-in-Time & Just-Enough-Access Elevation, Break-Glass Emergency Access, Secrets Sprawl & Consolidation, Third-Party & Vendor Privileged Access Governance, Access Recertification & IGA Automation, Passwordless Authentication Rollout, Cloud Entitlement Management (CIEM) at Scale, Agentic AI Identity Governance, the AI Processing Tax research piece, One Key, Every Agent (AI agent credential sharing), the Shadow AI Discovery Gap research piece, and Credential Tiering & the PAM Market (the Tier 0-3 model and where PAM tools fit). There's also the independent Secure India Exams project and a security blog.",
  },
  {
    id: "credential-platform",
    title: "Case study: Credential Management Platform Strategy",
    url: "/case-studies/credential-platform/",
    keywords: ["credential management platform strategy", "credential platform"],
    answer:
      "\"Credential Management Platform Strategy\" covers how to turn scattered passwords, keys and tokens into one service. Credentials end up in vaults, config files, chat, wikis and pipeline variables, and the usual problem is that nobody owns the whole picture. The platform has three parts: a short service catalog, one named owner for every credential, and a lifecycle that runs the same way for all of them. Where a short-lived identity will do, use it before vaulting a long-lived secret.",
  },
  {
    id: "pam-modernization",
    title: "Case study: PAM Modernization & Zero Standing Privilege",
    url: "/case-studies/pam-modernization/",
    keywords: ["pam modernization", "zero standing privilege"],
    answer:
      "\"PAM Modernization & Zero Standing Privilege\" is about moving privileged access from permanent admin rights to short, approved, recorded sessions, and proving to an auditor that it works. Most PAM programs stop once passwords are in a vault, and the remaining risk is access that never expires. Modernizing means four things together: vault the secret, rotate it, put a recorded session in front of it, and grant access only for the length of the task, with evidence at every step.",
  },
  {
    id: "privileged-access-program",
    title: "Case study: How I Run a Privileged Access Program",
    url: "/case-studies/privileged-access-program/",
    keywords: ["privileged access program", "pam program", "how i run", "pam roadmap", "pam rollout", "pam architecture", "pam poc", "proof of concept", "pam training", "go-live", "hypercare"],
    answer:
      "\"How I Run a Privileged Access Program\" is the order I follow from the first conversation to the last training session. It starts with the organization's pain, not a tool: talk to stakeholders, assess any existing tool, run a proof of concept with more than one product against the real problems, then decide and engage professional services. Design and planning cover the architecture, inventory sign-off, wave plan and requirements, and policies such as break-glass and naming are approved before they are built. Delivery goes Dev, pre-prod, production with go/no-go criteria, a rollback plan and a security review of the platform, then training, go-live and hypercare. It also covers privilege beyond people (service accounts, IoT, OT, AI agents) and lists the documents I leave behind.",
  },
  {
    id: "migration-planning",
    title: "Case study: Privileged Access Migration Planning",
    url: "/case-studies/migration-planning/",
    keywords: ["migration planning", "privileged access migration", "pam migration"],
    answer:
      "\"Privileged Access Migration Planning\" is how I plan a move from one privileged access tool to another so nothing the old tool quietly did gets lost. I start by analysing what the current tool does, what it fails to do and what is inside it, then run discovery and get the plan signed off before anything moves. Waves follow dependency, risk, access criticality and rollback readiness, every secret is rotated at cutover, and the plan covers archiving logs and recordings and switching the old tool off.",
  },
  {
    id: "platform-evaluation",
    title: "Case study: PAM, NHI & Cloud Platform Evaluation",
    url: "/case-studies/platform-evaluation/",
    keywords: ["platform evaluation", "delinea", "strongdm", "clutch security", "wiz"],
    answer:
      "\"PAM, NHI & Cloud Platform Evaluation\" is a method for comparing platforms. Feature lists do not settle a decision, so I write scenarios, weights and pass marks first, run every candidate through the same scripts, and score before anyone argues. The result is a decision record linking what a tool can do to integration, operations, audit and ownership. The work covered Delinea Secret Server and Privileged Remote Access proofs of concept, StrongDM product analysis and operating-model planning, and assessments of Clutch Security and Wiz. The page is about method and does not rank those products.",
  },
  {
    id: "audit-mapping",
    title: "Case study: IAM Audit & Control-Mapping Framework",
    url: "/case-studies/audit-mapping/",
    keywords: ["audit mapping", "control mapping", "iam audit"],
    answer:
      "\"IAM Audit & Control-Mapping Framework\" is about connecting what an IAM control is meant to do with the proof that it did, who holds that proof and how often someone looks at it. The tool is a control register with one row per control: a plain objective, one owner, the system setting that enforces it, the evidence it produces and how fresh that evidence must be. Evidence is collected by a scheduled job into a store the audited people cannot edit, and every gap gets an owner and an expiry date.",
  },
  {
    id: "ai-coworker",
    title: "Case study: AI as a Security Product Co-worker",
    url: "/case-studies/ai-coworker/",
    keywords: ["ai coworker", "ai co-worker", "chatgpt", "claude", "llm", "openai use"],
    answer:
      "\"AI as a Security Product Co-worker\" covers how to bring an AI assistant into a working team. Treat it like a new team member: a job, a named owner, its own identity, access limited to that job, and a written agreement about what it does alone and what needs a yes. Every connection to a company tool, including MCP, is an access decision, so a broker and a policy sit in front of it, a person checks anything that writes, sends or leaves the company, and everything is logged. The author uses OpenAI, ChatGPT and Claude to structure research, compare options and tighten writing.",
  },
  {
    id: "non-human-identity-at-scale",
    title: "Case study: Non-Human Identity at Scale",
    url: "/case-studies/non-human-identity-at-scale/",
    keywords: ["non-human identity", "non human identity", "nhi", "service account inventory", "machine identity", "risk scoring"],
    answer:
      "\"Non-Human Identity at Scale\" covers finding the service accounts, keys, tokens and agents nobody wrote down, giving each one an owner, ranking them by risk and replacing the long-lived ones with credentials that expire. Start with one inventory with a named owner against every entry and a flag on every entry with none. A simple score turns it into a queue, ranked on how long since the secret changed, how much it can do and whether anyone owns it, with exposure and last use next. The best fix removes the secret, using a role, federation or short-lived token before rotating a static key.",
  },
  {
    id: "jit-jea-elevation",
    title: "Case study: Just-in-Time & Just-Enough-Access Elevation",
    url: "/case-studies/jit-jea-elevation/",
    keywords: ["just-in-time", "just enough access", "jit", "jea", "elevation", "standing access"],
    answer:
      "\"Just-in-Time & Just-Enough-Access Elevation\" replaces standing admin role membership with time-boxed, scope-limited elevation that closes automatically. Each request opens a window and the window closes on its own, sized from what people actually did with the role. An advisory step can propose scope and duration, but the requester and the approver still decide.",
  },
  {
    id: "break-glass-access",
    title: "Case study: Break-Glass Access",
    url: "/case-studies/break-glass-access/",
    keywords: ["break glass", "break-glass", "emergency access"],
    answer:
      "\"Break-Glass Emergency Access\" is about designing emergency access that stays usable under pressure without becoming a permanent bypass. It has to work when the PAM platform, identity provider and MFA service may all be down. Five habits keep it from turning into a side door: credentials kept apart from standing accounts, every use a logged event, an alert on any sign-in or checkout, a written justification, and rotation the same day. An advisory check flags use that looks routine, a person decides, and the account is tested on a calendar.",
  },
  {
    id: "secrets-consolidation",
    title: "Case study: Secrets Sprawl & Consolidation",
    url: "/case-studies/secrets-consolidation/",
    keywords: ["secrets sprawl", "secrets consolidation", "vault", "hard-coded credentials"],
    answer:
      "\"Secrets Sprawl & Consolidation\" is about finding credentials scattered across repositories, pipelines and config files and moving them into one governed service that applications read at runtime. Anything a scan finds is treated as compromised: rotate first, clean history second, then move it into a governed store. Migrate one application at a time, fetch at runtime, use short-lived or federated credentials where possible, then block new secrets at commit and pipeline and retire the old stores. An advisory classifier can propose a ranking and a person confirms it.",
  },
  {
    id: "vendor-privileged-access",
    title: "Case study: Third-Party & Vendor Privileged Access Governance",
    url: "/case-studies/vendor-privileged-access/",
    keywords: ["vendor access", "third-party access", "vendor privileged access", "contractor access"],
    answer:
      "\"Third-Party & Vendor Privileged Access Governance\" treats a vendor engineer like any other privileged user, plus rules about sponsorship and end dates. Each vendor person gets their own named account, a named internal sponsor, MFA and an end date, and reaches the target through a broker that records the session with no network path of their own. Expiry does the offboarding: if nothing renews the access it ends, and the sponsor has to say yes again to keep it. An advisory plain-language summary helps approvers, and the real scope stays next to it.",
  },
  {
    id: "access-recertification",
    title: "Case study: Access Recertification & IGA Automation",
    url: "/case-studies/access-recertification/",
    keywords: ["access recertification", "iga automation", "recertification", "access review"],
    answer:
      "\"Access Recertification & IGA Automation\" turns a manual quarterly review into a governed process backed by usage evidence. A review that asks managers to approve long lists from memory produces a signature, not a control. Each line shows who owns the account, whether it was used and an advisory keep or revoke suggestion the reviewer can overrule. The decision then executes from the identity governance system and is checked, because a certification is only finished when the access is gone and you can show it.",
  },
  {
    id: "passwordless-authentication",
    title: "Case study: Passwordless Authentication Rollout",
    url: "/case-studies/passwordless-authentication/",
    keywords: ["passwordless", "phishing-resistant", "authentication rollout"],
    answer:
      "\"Passwordless Authentication Rollout\" moves a workforce to phishing-resistant sign-in in risk order: privileged users first, then people who reach high-risk apps, then everyone else. A single company-wide date puts the heaviest support load on the worst day. Recovery decides whether the program works, since a lost key fixed by text message or password reset gives attackers an easier route. A fallback stays during each wave and retires only when adoption and help-desk data say it is stable. An advisory per-user risk score proposes the order and a named person approves it. Legacy apps and break-glass accounts get named plans.",
  },
  {
    id: "ciem-at-scale",
    title: "Case study: Cloud Entitlement Management (CIEM) at Scale",
    url: "/case-studies/ciem-at-scale/",
    keywords: ["ciem", "cloud entitlement management", "toxic combination", "privilege escalation"],
    answer:
      "\"Cloud Entitlement Management (CIEM) at Scale\" is about finding toxic entitlement combinations that individual cloud IAM rules miss. Cloud identities hold far more access than they use, and each cloud already records the usage data to measure that gap. What an identity can really do is the union of everything attached to it plus whatever it reaches through trust links. Every cut goes to an owner for approval with a rollback, backed by policy as code and organization-level guardrails. An advisory pass over the entitlement graph proposes combinations and must cite the policy statements behind each finding.",
  },
  {
    id: "agentic-ai-identity-governance",
    title: "Case study: Agentic AI Identity Governance",
    url: "/case-studies/agentic-ai-identity-governance/",
    keywords: ["agentic ai identity governance", "ai agent identity", "sub-agent", "agent permissions"],
    answer:
      "\"Agentic AI Identity Governance\" is a governance model for an identity that changes shape in the middle of a task, since agents pick up scopes, call APIs and launch sub-agents as they run. Each agent gets its own identity, a named human owner and no standing access, with one short-lived credential per task scoped to one tool, a decision on every action, and a person for actions that are expensive to undo. Sub-agents get less, never more. The record shows who the agent acted for, and there is a kill switch that gets practised.",
  },
  {
    id: "ai-processing-tax",
    title: "Research: The AI Processing Tax",
    url: "/case-studies/ai-processing-tax/",
    keywords: ["ai processing tax", "humangate", "decision-package gate", "production cost", "processing cost"],
    answer:
      "\"The AI Processing Tax\" is independent research. AI made producing work nearly free but did not make deciding on it free, and that cost moves to whoever opens the file next, often the people with the least slack. The page checks the idea against four independent sources and is clear that none measures it directly. The control it specifies is a decision-package gate where an AI agent hands a request to a human: it sends back any handoff that has not done its own thinking first, and checks completeness, never correctness, so the human keeps the judgment. It is a design, not a built system.",
  },
  {
    id: "ai-agent-credential-sharing",
    title: "Research: AI Agent Credential Sharing (One Key, Every Agent)",
    url: "/case-studies/ai-agent-credential-sharing/",
    keywords: ["ai agent credential sharing", "one key every agent", "salesloft drift", "shared credential", "long-lived credential", "agent credentials"],
    answer:
      "\"One Key, Every Agent\" looks at what goes wrong when AI agents run on a person's token or a team's shared key: the logs name the wrong party, access is wider than the task, secrets leak into prompts, config and logs, tokens live too long, and one leak reaches every system. It uses the 2025 Salesloft Drift token compromise as the clearest public example of the same shape. The alternative is that each agent has its own identity and a broker issues a short-lived credential for one task and one target on behalf of a named user, so the model never sees the secret and every record shows both the agent and the person.",
  },
  {
    id: "shadow-ai-discovery-gap",
    title: "Research: Shadow AI Discovery Gap",
    url: "/case-studies/shadow-ai-discovery-gap/",
    keywords: ["shadow ai", "shadow-ai", "discovery gap", "unsanctioned ai", "unapproved ai", "samsung"],
    answer:
      "\"You can't govern the AI tools you don't know exist\" is about the gap between the AI a company approves and the AI its people use. Discovery comes before policy and draws on proxy and network logs, browser and endpoint data, SaaS and OAuth grants, expense records and the data stores. Each finding is classified by the data it touches and gets one of four outcomes: allow, allow with controls, replace or block. A block alone moves use out of sight, so the approved route has to be quicker than the one people found, and the gap is measured by how much use moves onto it.",
  },
  {
    id: "secure-india-exams",
    title: "Secure India's National Examinations (Zero Trust proposal)",
    url: "/secure-india-exams/",
    keywords: ["secure india exams", "neet", "jee", "cuet", "national examinations", "exam paper leak", "zero trust proposal", "whitepaper", "poster"],
    answer:
      "\"Securing India's National Examinations\" is Roshan's independent, non-commercial public-interest project — a Zero Trust reference architecture proposing how India can prevent national exam paper leaks (for exams like NEET, JEE and CUET). It's a lifecycle security model covering paper creation, protected storage, controlled delivery and verified destruction, built on threat-led architecture (not just process controls), cryptographic protection, least privilege and continuous evidence, with privacy, resilience and accountable human decision-making. There's a full 30-page whitepaper PDF (Securing_India_Exams_Master.pdf), plus the project page at /secure-india-exams/.",
  },
  {
    id: "mcp-lab",
    title: "MCP Human Approval Gateway (interactive lab)",
    url: "/mcp-human-approval-gateway/",
    keywords: ["mcp human approval gateway", "mcp lab", "mcp", "interactive lab", "human approval gateway", "agentic ai lab", "approval gateway", "ai agent approval"],
    answer:
      "The MCP lab is a hands-on demo you can run in the browser at /mcp-human-approval-gateway/. An AI agent asks to use a tool, a deterministic policy engine decides, higher-risk requests wait for a role-qualified human to approve or deny, and an approval is time-bound, single-use and tied to the exact request. Every step goes into a hash-chained audit log, and an animated architecture view shows the path each scenario takes. Nine scenarios cover auto-approval, review queues, prompt-injected context, scope creep, unregistered tools, replay and audit tampering. All data is synthetic, the AI analyst is advisory only, and the source, threat model and tests are on GitHub: github.com/trivediroshan1-ui/mcp-human-approval-gateway.",
  },
  {
    id: "blog",
    title: "Writing / blog",
    url: "/writing/",
    keywords: ["blog", "writing", "articles", "posts", "openai huggingface", "breach analysis", "written", "wrote", "pam series", "latest posts"],
    answer:
      "The writing section has four posts. Three are a PAM series: \"PAM Framework and Design: What Sits Around the Vault\" (4 Oct 2026), \"A PAM Project Plan for Tier 1, 2 and 3 Organisations\" (11 Oct 2026) and \"PAM as an Identity: What Changes When the Vault Can Talk to Your Governance System\" (18 Oct 2026). The fourth is independent security analysis, \"When the Attacker Was the AI Itself: A Cybersecurity Breakdown of the OpenAI–Hugging Face Breach\" (25 July 2026). Everything is at /writing/, and there is an RSS feed.",
  },
  {
    id: "post-pam-framework",
    title: "Blog: PAM Framework and Design",
    url: "/writing/pam-framework-and-design/",
    keywords: ["pam framework", "pam design", "pam architecture", "sso mfa pam", "help desk pam", "least privilege authorization authentication pam"],
    answer:
      "\"PAM Framework and Design: What Sits Around the Vault\" is a ten-layer reference framework: scope and discovery, account tiering, authentication (SSO and MFA), authorization and least privilege, vaulting and session control, service and application secrets, help desk and operations, monitoring and audit evidence, governance and resilience. It includes an animated architecture and request workflow, tables for where MFA applies and what the help desk may and may not do, and common design mistakes.",
  },
  {
    id: "post-pam-project-plan",
    title: "Blog: PAM project plan by organisation tier",
    url: "/writing/pam-project-plan-by-organisation-tier/",
    keywords: ["pam project plan", "pam roadmap", "pam 90 days", "pam 365 days", "pam sizing", "pam readiness", "pam tier 1 2 3"],
    answer:
      "\"A PAM Project Plan for Tier 1, 2 and 3 Organisations\" shows how to size a PAM programme from readiness gates (RFC, POC, tool chosen, contract signed, professional-services hours bought, team named) and capacity inputs (privileged users, assets, service accounts, use cases). It works through a sizing formula and gives illustrative 90-day, 180-day and 270 to 365-day plans. The unit costs in it are labelled planning assumptions, not industry benchmarks.",
  },
  {
    id: "post-pam-identity",
    title: "Blog: PAM as an identity",
    url: "/writing/pam-as-an-identity/",
    keywords: ["pam as an identity", "pam iga", "iga integration", "privileged identity governance", "pam identity governance", "mover leaver privileged"],
    answer:
      "\"PAM as an Identity\" treats a privileged account as an identity with an owner and a lifecycle. It compares PAM with no IGA, with an IGA planned and with a mature IGA, shows what stays in PAM (secrets, sessions, checkout, break-glass) and what moves to IGA (who is entitled, request, certification, separation of duties), walks through mover and leaver flows, and lists what should not be linked, such as letting an IGA outage block break-glass access.",
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
      "This is the personal site of Roshan Trivedi — Identity & Security. It covers his bio, expertise, career experience, a portfolio of privacy-safe PAM/IAM/NHI case studies and independent AI-security research, an interactive MCP Human Approval Gateway lab, his independent Secure India Exams zero-trust proposal, a security-writing blog with a PAM series, and his resume/contact details. Most pages are plain HTML/CSS with no framework, hosted on GitHub Pages at roshantrivedi.co.in.",
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
