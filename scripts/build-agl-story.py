#!/usr/bin/env python3
"""Builds ai-governance-lab/story/index.html from the diagrams page shell."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = (root/"ai-governance-lab/diagrams/index.html").read_text()
head, rest = src.split('<main id="main">', 1)
tail = rest.split('</main>', 1)[1]
T = "Why I built the AI governance lab"
D = "From years of mapping controls for auditors to testing AI controls on a private laptop: the story behind the AI governance lab, in plain words."
head = re.sub(r'<meta name="description" content=".*?" />', f'<meta name="description" content="{D}" />', head)
head = head.replace("AI governance lab: architecture diagrams", T).replace('/ai-governance-lab/diagrams/', '/ai-governance-lab/story/')
head = re.sub(r'<meta property="og:description" content=".*?" />', f'<meta property="og:description" content="{D}" />', head)
head = re.sub(r'<title>.*?</title>', '<title>Why I built the lab &middot; AI governance lab</title>', head)
head = head.replace('agl.css?v=20261024f">', 'agl.css?v=20261024f">\n    <link rel="stylesheet" href="/assets/story.css?v=20261024c">')
body = '''<main id="main">
      <header class="hero mcp-hero">
        <p class="eyebrow">AI governance lab</p>
        <h1>Why I built this lab</h1>
        <p class="dek">I spent years mapping access controls for auditors. When AI agents arrived with the same promises, I wanted to see whether the controls really hold, so I tested them.</p>
        <div class="mcp-ribbon" aria-hidden="true"></div>
      </header>
      <div class="agl story">
      <section aria-labelledby="watch">
        <h2 id="watch">Watch the story <span class="sv-new">New</span></h2>
        <p>The same story as a 78-second animated workflow. It has no sound, so you can watch it anywhere. Tap a chapter to jump.</p>
        <div class="sv">
          <div>
            <div class="sv-frame"><video id="sv-video" controls playsinline preload="metadata" poster="/assets/share/agl-story-poster.jpg" aria-label="My story as a 78-second animated workflow"><source src="/assets/share/agl-story.mp4" type="video/mp4">Your browser cannot play this video. The same story is written out below.</video></div>
            <div class="sv-bar" aria-hidden="true"><i id="sv-bar"></i></div>
          </div>
          <div>
            <p class="sv-cap" id="sv-cap" aria-live="polite"></p>
            <ol class="sv-ch"><li><button type="button" data-t="0" data-d="I wanted to know if AI governance controls really hold, so I tested them on my own laptop."><b>0:00</b><span>Why I built it</span></button></li><li><button type="button" data-t="5" data-d="For years I mapped vendor controls to IAM policy, then to what external auditors check: NIST, PCI, HIPAA, ISO 27001."><b>0:05</b><span>Mapping controls</span></button></li><li><button type="button" data-t="14" data-d="Hooks, agents that map policies, AI that automates identity, a Centre of Excellence setting each agent's access."><b>0:14</b><span>The AI promises</span></button></li><li><button type="button" data-t="23" data-d="Which use cases, which policy, which certifier, and what stops an agent that decides on its own?"><b>0:23</b><span>What I never heard</span></button></li><li><button type="button" data-t="32" data-d="A bank bot, a corporate assistant, a one-time Allow and a shared token: none of them needs an attacker."><b>0:32</b><span>Read access is not small</span></button></li><li><button type="button" data-t="41" data-d="NIST, ISO and vendor papers first. Then a made-up lender, Kaveri Finance, and 59 cases."><b>0:41</b><span>Read first, then build</span></button></li><li><button type="button" data-t="49" data-d="One request through the gateway: register, paperwork, guardrail scan, data and region rules, model, response screen. Each request ends in one decision line in the tamper-evident log. Personal data sent to a use not approved for it is blocked."><b>0:49</b><span>The architecture, animated</span></button></li><li><button type="button" data-t="64" data-d="The register, approvals, expiry and the log held. A plain text filter broke, and only 4 of 10 new items were caught."><b>1:04</b><span>What I found</span></button></li><li><button type="button" data-t="72" data-d="The data, every use case, diagrams, a browser lab and a 69-page book. Tell me where my tests are weak."><b>1:12</b><span>Free and public</span></button></li></ol>
          </div>
        </div>
        <details class="sv-tr"><summary>Read the video as text</summary>
          <ol>
            <li>I mapped vendor controls to IAM policy for years, and external auditors checked that policy against NIST, PCI, HIPAA and ISO 27001. One question stayed: do the controls really follow the policy?</li>
            <li>Then the AI era: hooks, agents that map policies, AI that automates identity, a Centre of Excellence that sets each agent&rsquo;s access.</li>
            <li>What I never heard: which use cases, which policy, which certifier, and what stops an agent that decides on its own.</li>
            <li>&ldquo;Read access&rdquo; is not small: a bank bot, a corporate assistant, a one-time Allow, a shared token.</li>
            <li>So I read NIST, ISO and vendor papers, then built a test: a made-up lender, Kaveri Finance, and 59 cases.</li>
            <li>One request through the gateway. A public question is allowed and logged. A request with an Aadhaar number for a use not approved for personal data is blocked and logged. Each request ends in one decision line, chained to the one before.</li>
            <li>What I found: 59 cases; filters caught 20, 42 and 45 of 53 variants; 4 of 10 unseen items; the assistant followed policy in 9 of 9 requests.</li>
            <li>Everything is free at roshantrivedi.co.in/ai-governance-lab.</li>
          </ol>
        </details>
      </section>

      <section>
        <p class="kick">My story, in my words</p>
        <p class="lead">I used to do control mapping for PAM tools against IAM policies, created internally and verified by external auditors against standards like NIST, PCI, HIPAA and ISO 27001, depending on the project: finance, healthcare or an information security firm.</p>
        <p>One question was always at the back of my mind.</p>
        <blockquote class="st-quote">Are we serious about these controls we map from the vendor, and do they really adhere to the organisation&rsquo;s policy? It still fascinates me.</blockquote>
        <p>Then the AI era started. I kept hearing that AI hooks will help, that agents will map policies, that AI identification will automate identity, and that a Centre of Excellence for AI governance will sit at the top and decide what level of permission each agent should get. Later I heard that AI agents will use PAM or identity APIs to stay within governance and meet compliance.</p>
        <p>But I never heard what the use cases are, what policies we are trying to manage, how the governance factor is aligned, or who the certifier is. And what if an AI agent goes vague and makes its own decisions?</p>
        <p>That is when my mind started building towards this AI governance test on my private laptop. Before that, I read white papers from NIST, ISO and the IGA and PAM vendors on how they manage, discover and automate the identity life cycle, accounts linked to an identity, non-human identities and agents, so that I had the knowledge before I built anything.</p>
      </section>

      <section aria-labelledby="path">
        <h2 id="path">From mapping sheets to a test bench</h2>
        <ol class="st-path">
          <li><h3>Mapping controls</h3><p>Vendor controls matched to policy, then to audit standards, for finance, healthcare and security firms.</p></li>
          <li><h3>The AI promise</h3><p>Agents will map policies, AI will discover and automate identities, a central team will set each agent&rsquo;s access.</p></li>
          <li class="gap"><h3>The gap</h3><p>No clear use cases, no named policy per agent, no certifier, no answer for an agent that decides on its own.</p></li>
          <li class="now"><h3>The lab</h3><p>A private test on made-up data. Expected results written first, then 59 cases run.</p></li>
        </ol>
      </section>

      <section>
        <h2>The questions nobody answered</h2>
        <ul class="st-q">
          <li>Which use cases are we talking about?</li>
          <li>Which policy is each agent bound to?</li>
          <li>How does the governance part line up with an actual control?</li>
          <li>Who is the certifier for an agent&rsquo;s decision?</li>
          <li>If an agent goes off script and decides on its own, what stops it, and what proves it?</li>
        </ul>
      </section>

      <section>
        <h2>Why &ldquo;read access&rdquo; is not a small thing</h2>
        <p>These are everyday situations. None of them needs an attacker.</p>
        <div class="st-grid">
          <div class="st-card"><span class="tag">Bank</span><h3>The support bot</h3><p>A bot with &ldquo;read access&rdquo; can see PAN, Aadhaar and transactions. If it repeats them in a chat, or sends them to an outside model, nobody was hacked. It did what it was allowed to do.</p></div>
          <div class="st-card"><span class="tag">Corporate</span><h3>The helpful assistant</h3><p>An assistant that reads mail and shared drives can surface salary or legal files to someone who was never meant to see them.</p></div>
          <div class="st-card"><span class="tag">Tools and apps</span><h3>The one-time Allow</h3><p>A plugin is approved once and then reads the whole workspace, every day, with the same rights as the person who clicked.</p></div>
          <div class="st-card"><span class="tag">Bots and agents</span><h3>The shared token</h3><p>A bot on a shared or long-lived token looks exactly like a real employee in the log. After a mistake, nobody can tell who did what.</p></div>
        </div>
      </section>

      <section>
        <h2>So I built the test</h2>
        <p>The company is made up: Kaveri Finance, a small lender. The Aadhaar, PAN and card numbers are invented. Aadhaar numbers pass the real Verhoeff check and card numbers pass the Luhn check. PAN has no public checksum, so the PANs only follow the real format. That way the tests behave like real data. I wrote the expected result of every case and saved it in git before running anything.</p>
        <div class="st-stats">
          <div class="st-stat"><b>59</b><span>cases across gateway, filter, agent identity and audit log</span></div>
          <div class="st-stat bad"><b>20 / 42 / 45</b><span>of 53 attack variants caught by filter v1, v2, v3</span></div>
          <div class="st-stat bad"><b>4 of 10</b><span>unseen items caught by all three filters</span></div>
          <div class="st-stat ok"><b>9 of 9</b><span>requests where a real assistant followed one written policy</span></div>
        </div>
        <div class="st-held">
          <div class="h"><strong>What held</strong>Access register, approvals, expiry, kill switches, short-lived agent tokens and the tamper-evident log.</div>
          <div class="b"><strong>What broke</strong>A plain text filter. Hinglish, numbers in Hindi words, split messages and quoted attacks got through.</div>
        </div>
        <p class="st-note" style="margin-top:12px">This is a small test, on one laptop, with made-up data. The 100% filter score on 200 samples is not a result I trust, because I tuned the filter on those samples.</p>
      </section>

      <section>
        <h2>What I take back to my old audit questions</h2>
        <p>A control that looks right in a mapping sheet still has to be tested against the attack it is meant to stop. For AI agents, that means a named policy, its own short-lived identity, a human approval where it matters, and a log that shows who approved, not only that it ran.</p>
        <div class="st-cta">
          <a class="p" href="/ai-governance-lab/">Open the lab</a>
          <a href="/ai-governance-lab/cases/">Every use case, one by one</a>
          <a href="/assets/ai-governance-lab-book.pdf">Free book (PDF)</a>
        </div>
        <p class="st-note" style="margin-top:14px">If you work in IAM, PAM, risk or audit and see a weak test, please tell me. I would rather learn it from you than from an incident.</p>
      </section>
      </div>
    </main>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"VideoObject","name":"Why I built an AI governance lab: my story as an animated workflow","description":"A 78-second silent animated workflow: from mapping controls for auditors to testing AI governance controls on made-up Indian data, including one request through the gateway.","thumbnailUrl":"https://roshantrivedi.co.in/assets/share/agl-story-poster.jpg","contentUrl":"https://roshantrivedi.co.in/assets/share/agl-story.mp4","uploadDate":"2026-10-24","duration":"PT1M18S","author":{"@type":"Person","name":"Roshan Trivedi"}}</script>
    <script defer src="/assets/story-video.js?v=20261024a"></script>'''
out = head + body + tail
out = out.replace("diagrams/", "diagrams/")
(root/"ai-governance-lab/story/index.html").write_text(out)
print(len(out))
