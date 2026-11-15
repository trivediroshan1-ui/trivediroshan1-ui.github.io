#!/usr/bin/env python3
"""CA and MFA lab: builds /ca-mfa-lab/what-i-got-wrong/ and /ca-mfa-lab/method/, puts the animated chain in the overview hero
and shortens the overview's #wrong section into a summary with a link. Safe to re-run.
Run from the repo root:  python3 scripts/ca/build_method_pages.py
Facts come from ca-mfa-lab/evidence (locked, never edited) and from the overview text that was already published."""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lab_nav

BASE = "https://roshantrivedi.co.in"
GH = "https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/blob/main/ca-mfa-lab"
REVIEWED = "14 November 2026"
STAMP = "20261114j"
COLS = ["#a78bfa", "#4de2ff", "#60a5fa", "#f59e0b", "#34d399", "#f472b6", "#f87171"]
E = lambda s: html.escape(s, quote=False)

# ---------------------------------------------------------------- the animated chain (overview hero)
def chain_svg():
    rings, nums = "", ""
    for i, c in enumerate(COLS):
        cx = 40 + 44 * i
        rings += f'<circle class="ring l" style="stroke:{c};animation-delay:{i * 0.825:g}s" cx="{cx}" cy="40" r="18"/>'
        nums += f'<text class="num" x="{cx}" y="45">{i + 1}</text>'
    steps = ""
    for j, (name, c, x) in enumerate([("Guess", "#9aa3b8", 40), ("Lock", "#f59e0b", 148), ("Run", "#4de2ff", 256)]):
        steps += (f'<g class="l" style="animation-delay:{5.4 + j:g}s"><rect class="box" style="stroke:{c}" x="{x}" y="104" width="84" height="38" rx="6"/>'
                  f'<text class="lab" x="{x + 42}" y="128">{name}</text></g>')
    arrows = ('<path class="arw" d="M128 123h14m-5-4 5 4-5 4"/><path class="arw" d="M236 123h14m-5-4 5 4-5 4"/>')
    return (
        '<!-- chain:start -->\n'
        '<figure class="ca-chain" aria-label="Animated picture of the seven links of the sign-in chain">'
        '<svg viewBox="16 0 330 160" role="img"><title>The seven links of the sign-in chain</title>'
        '<desc>A dot travels along seven numbered rings, one for each link in the sign-in chain. Then three steps light up in order: guess, lock, run. '
        'The loop repeats every nine seconds and can be paused.</desc>'
        '<line class="trk" x1="58" y1="40" x2="322" y2="40"/>' + rings + nums +
        '<circle class="dot" cx="40" cy="10" r="4"/>'
        '<text class="cap" x="40" y="84">Seven links, and how I tested them</text>' + steps + arrows +
        '</svg></figure>\n<!-- chain:end -->'
    )

# ---------------------------------------------------------------- page shell, taken from the overview
def shell():
    s = open("ca-mfa-lab/index.html", encoding="utf-8").read()
    i = s.index('<main id="main" class="nhi">')
    k = s.index("</main>")
    head, tail = s[:i], s[k + len("</main>"):]
    head = re.sub(r'<link rel="stylesheet" href="/assets/ca-chain\.css[^"]*">\s*', "", head)
    tail = re.sub(r'<script defer src="/assets/ca-chain\.js[^"]*"></script>\s*', "", tail)
    return head, tail

def page(path, title, desc, hero_h1, dek, meta_items, body, prev, nxt):
    head, tail = shell()
    url = BASE + path
    head = re.sub(r"<title>[^<]*</title>", lambda m: f"<title>{E(title)} &middot; Roshan Trivedi</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*" />', lambda m: f'<meta name="description" content="{html.escape(desc)}" />', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*" />', lambda m: f'<meta property="og:title" content="{html.escape(title)}" />', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*" />', lambda m: f'<meta property="og:description" content="{html.escape(desc)}" />', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url,
        "datePublished": "2026-11-14", "dateModified": "2026-11-14",
        "author": {"@type": "Person", "name": "Roshan Trivedi", "url": BASE + "/"},
        "isPartOf": {"@type": "WebPage", "url": BASE + "/ca-mfa-lab/"},
        "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True}) + "</script>", head, count=1, flags=re.S)
    meta = "".join(f"<li>{m}</li>" for m in meta_items)
    foot = ('<nav class="lab-foot" aria-label="More in this lab">'
            f'<a class="lf-prev" href="{prev[0]}"><small>Previous</small><b>{prev[1]}</b></a>'
            f'<a class="lf-next" href="{nxt[0]}"><small>Next</small><b>{nxt[1]}</b></a>'
            '<span class="lf-extra"><a href="/ca-mfa-lab/ca-mfa-lab-book.pdf">Get the book</a><a href="/topics/">Browse by topic</a></span></nav>')
    main = (f'<main id="main" class="nhi">\n  {lab_nav.render("ca", path)}\n'
            f'  <header class="nhero"><p class="eyebrow">Lab</p><h1>{hero_h1}</h1><p class="dek">{dek}</p>'
            f'<ul class="nmeta"><li>Last reviewed {REVIEWED}</li>{meta}<li>Made-up data only</li></ul></header>\n'
            f'{body}\n  {foot}\n</main>')
    return head + main + tail

def link(href, text):
    return f'<a href="{href}">{text}</a>'

def card(title, lines):
    ps = "".join(f"<p><b>{k}</b> {v}</p>" for k, v in lines)
    return f'<div class="ncard"><h3>{title}</h3>{ps}</div>'

# ---------------------------------------------------------------- what I got wrong
def wrong_page():
    g2 = f"{GH}/evidence/guesses/guesses-run2.md"
    r2 = f"{GH}/evidence/RESULTS-run2.md"
    cards = [
        card("A notice is not a block (C01, C03)", [
            ("The case:", "C01 has three controls: remove SMS recovery (A), strong help desk proof (B) and a notice when a sign-in method changes (C). The bad outcome I defined was &ldquo;account taken and unnoticed&rdquo;. C03 has the same shape with SSO, an exclusion review and an alert on exclusion use."),
            ("I guessed:", "switch off SMS removal alone, or help desk proof alone, and the bad outcome happens. In C03, switch off the exclusion review alone and it happens."),
            ("What ran:", "neither one let it in. The notice was still on, so every takeover was noticed."),
            ("What it taught me:", "a notice is a detective control. It tells you about an attack and does not stop it. If the bad outcome is only &ldquo;account taken&rdquo;, both cases go back to <i>in</i>. I should have said what I was counting before I guessed."),
        ]),
        card("Trusting a partner&rsquo;s MFA (A05)", [
            ("The case:", "A guest signs in. Control A trusts the home tenant&rsquo;s MFA claim for guests. Control B asks for MFA in our own tenant. The bad outcome is a guest getting in without real MFA."),
            ("I guessed:", "with both controls on, the bad outcome does not happen."),
            ("What ran:", "with both on, it still happened."),
            ("What it taught me:", "if you accept the home tenant&rsquo;s claim and that tenant&rsquo;s MFA is weak, the weak MFA satisfies your requirement and your own guest rule adds nothing. The result rests on my assumption that the home claim is weak. I wrote that assumption in the code, so you can change it and see the result change."),
        ]),
        card("The control that decides the question (Z21)", [
            ("The case:", "Three controls: block the device code flow (A), a one-hour refresh token (B) and a compliant device at use (C). The question: does the attacker still have access at 24 hours?"),
            ("I guessed:", "refresh token lifetime does not matter, and switching off A and C together lets the attacker in."),
            ("What ran:", "each single switch matched my guess, but A and C off together still gave <i>out</i>."),
            ("What it taught me:", "blocking the flow and requiring a compliant device matter for the first hour. The one-hour refresh token is what decides the 24 hour question. Ask which control answers the question you are asking."),
        ]),
        card("Scope of a control (X07)", [
            ("The case:", "Trusted locations are limited to the managed office network (A), and there is a device compliance rule (B). The bad outcome is an attacker on guest wifi skipping MFA."),
            ("I guessed:", "with the device rule off, the attacker gets in."),
            ("What ran:", "the attacker did not get in."),
            ("What it taught me:", "guest wifi is not a trusted location, so MFA is required, and an attacker who has only the password is stopped without the device rule. I had not thought through what the location control already covered."),
        ]),
        card("A convention is not enforcement (A03)", [
            ("The case:", "Separate admin accounts (A) against blocking the admin group from non-admin apps (B). The bad outcome is an admin session on a risky app."),
            ("I guessed:", "separate accounts alone stop it, and the group block alone does not."),
            ("What ran:", "the other way round. With only separate accounts, nothing stops the admin account reaching the risky app. With only the group block, the daily account is blocked."),
            ("What it taught me:", "separate accounts are a habit. Blocking the group is enforcement. The result also depends on whether you count a convention as a control."),
        ]),
    ]
    mine = [
        ("P11 (Run 2)", "my first model said approval stops an unauthorised change in the console. An unauthorised change skips approval by definition, so only the log can show it. That one was my mistake, not a surprise. First pass was 38 of 45 matched; after I fixed the model it was 39 of 45."),
        ("S06 (Run 3)", "bad test data."),
        ("Z01 (Run 3)", "a missing limit flag."),
    ]
    mine_html = "".join(f"<li><b>{k}:</b> {v}</li>" for k, v in mine)
    body = f'''  <section class="nsec" id="six" aria-labelledby="six-h">
    <h2 id="six-h">The 6 guesses I got wrong</h2>
    <p class="lede">I wrote every guess before any code existed and locked it in a commit. Six were wrong, all of them in Run 2. Each card below says what I guessed, what the script showed and what it taught me. Five cards cover six cases, because C01 and C03 were wrong for the same reason. All data is made up.</p>
    <p class="lede">How to read a guess: <i>in</i> means the bad outcome happens, <i>out</i> means it does not. I guess one word for all controls on, for all off, and for each control switched off by itself.</p>
    <div class="ngrid">
      {"".join(cards)}
    </div>
  </section>
  <section class="nsec" id="code" aria-labelledby="code-h">
    <h2 id="code-h">3 mistakes in my own test code</h2>
    <p class="lede">These were errors in the code I wrote after locking the guesses, not wrong guesses. I fixed the code and left the guesses alone.</p>
    <ul>{mine_html}</ul>
  </section>
  <section class="nsec" id="numbers" aria-labelledby="num-h">
    <h2 id="num-h">The numbers</h2>
    <p class="lede">Run 1 matched all 41 guesses. Run 2 had 45 cases and 39 matched every guess; the 6 that did not are the ones above. Runs 1 and 2 together: 86 cases run, 80 matched. The later runs added cases and did not add wrong guesses, so the lab total stays at 6.</p>
    <p class="lede">Still models I wrote, not a real tenant. Several results rest on assumptions I chose and wrote in the code. {link("/ca-mfa-lab/method/#limits", "What the method does not show")}.</p>
  </section>
  <section class="nsec" id="check" aria-labelledby="chk-h">
    <h2 id="chk-h">Check it yourself</h2>
    <p class="lede">The Run 2 guesses are in commit <a href="https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/7d31554">7d31554</a>, before the Run 2 code. {link(g2, "Run 2 guesses")} &middot; {link(r2, "Run 2 results")} &middot; {link(GH + "/evidence/run2.py", "Run 2 code")} &middot; {link("/ca-mfa-lab/register/", "Full register")} &middot; {link("/ca-mfa-lab/method/", "How the method works")}</p>
  </section>'''
    return page("/ca-mfa-lab/what-i-got-wrong/", "What I got wrong in the CA and MFA lab",
                "The 6 guesses I got wrong in my conditional access and MFA lab, what the script showed, and 3 mistakes in my own test code. Made-up data only.",
                "What I got wrong in the CA and MFA lab",
                "6 of my guesses were wrong, and I made 3 mistakes in my own test code. Here is each one, with what I guessed, what ran and what it taught me.",
                [link("/ca-mfa-lab/", "Lab overview"), link("/ca-mfa-lab/method/", "How the method works")],
                body, ("/ca-mfa-lab/", "Overview"), ("/ca-mfa-lab/method/", "How the method works"))

# ---------------------------------------------------------------- how the method works
def method_page():
    steps = [
        ("Write the case.", "A made-up company, the bad outcome, and the controls that could stop it.", "If I do not say what I am counting first, I can talk myself into any result afterwards."),
        ("Write my guess for each switch.", "One word each: <i>in</i> if the bad outcome happens, <i>out</i> if it does not. All controls on, all off, and each control off by itself.", "A guess with no switch to flip cannot be wrong, so it cannot teach me anything."),
        ("Hash the guesses file and commit it.", "After that I do not edit it.", "A commit shows the order. The guesses came first."),
        ("Only then write the code.", "A small model of the rule logic on made-up data. Assumptions I chose are written in comments.", "Writing the code second means the code cannot shape the guess."),
        ("Run it.", "Each case prints one line ending in OK, or MISMATCH where my guess was wrong.", "A mismatch is the useful result. It shows where my picture of the controls was off."),
        ("Fix my code, never my guess.", "If the code was wrong, I fix the code and say so. If the guess was wrong, both stay on the page.", "Changing a guess after the fact would turn the record into a story I like."),
    ]
    sh = "".join(f'<li><b>{a}</b> {b} <i>Why: {c}</i></li>' for a, b, c in steps)
    commits = ("The guesses were committed to this site&rsquo;s repository before any code existed. Commit <a href=\"https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/5875323\">5875323</a> holds the Run 1 guesses. Commit <a href=\"https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/7d31554\">7d31554</a> holds the Run 2 guesses. "
               "Commit <a href=\"https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/56b9622\">56b9622</a> holds the Run 1 and Run 2 code and results. Commit <a href=\"https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/f8d6676\">f8d6676</a> holds the Run 3 guesses, and commit <a href=\"https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/179b763\">179b763</a> holds the Run 3 code and results. "
               "Commit <a href=\"https://github.com/trivediroshan1-ui/trivediroshan1-ui.github.io/commit/64c3573\">64c3573</a> holds the predictions for the three tests I will run by hand. These commits sit on the pull request branches, because pull requests here are squash-merged into one commit each, so you will not find them by browsing the main branch. GitHub keeps them, and each link opens the commit with its date and files.")
    body = f'''  <section class="nsec" id="order" aria-labelledby="o-h">
    <h2 id="o-h">The order is the method</h2>
    <ol>{sh}</ol>
  </section>
  <section class="nsec" id="read" aria-labelledby="r-h">
    <h2 id="r-h">How to read one case</h2>
    <p class="lede">Each case has up to three controls, A, B and C, and a bad outcome. The script tries every case with all controls on, with all off, and with each control off on its own. If switching off one control lets the bad outcome in, that control is doing the work. If no single switch does, either control alone is enough. Some cases also have a pair check, where two controls go off together.</p>
    <p class="lede">The {link("/ca-mfa-lab/what-i-got-wrong/", "wrong guesses")} are the cases where my one-word answers and the script disagreed.</p>
  </section>
  <section class="nsec" id="check" aria-labelledby="c-h">
    <h2 id="c-h">Check it yourself</h2>
    <p class="lede">{commits}</p>
    <p class="lede">On 14 November 2026 I reran all five scripts on my own Mac. Every results file came out byte for byte identical to the one published here. You can also {link("/ca-mfa-lab/virtual-lab/run/", "run it in your browser")}.</p>
    <p>{link(GH + "/evidence/guesses/guesses-run1.md", "Run 1 guesses")} &middot; {link(GH + "/evidence/guesses/guesses-run2.md", "Run 2 guesses")} &middot; {link(GH + "/evidence/guesses/guesses-run3.md", "Run 3 guesses")} &middot; {link(GH + "/evidence/guesses/guesses-run4.md", "Run 4 predictions")} &middot; {link(GH + "/source-check-14-nov.md", "Source check")} &middot; {link("/ca-mfa-lab/register/", "Full register")}</p>
  </section>
  <section class="nsec" id="limits" aria-labelledby="l-h">
    <h2 id="l-h">What the method does not show</h2>
    <p class="lede">These are small models of rule logic. They do not show how any vendor product behaves. Three cases need a real tenant, a hardware key and a person on the phone; the {link("/ca-mfa-lab/run-4/", "Run 4 page")} has the details. Several results depend on assumptions I chose and wrote in the code, such as a weak home tenant claim, a reviewer who keeps at most 5 exclusions, a change log read within 7 days and 40 percent of users falling for a code lure. Change one and a result can change.</p>
    <p class="lede">Writing the guess first keeps me honest about my own thinking. It does not make the model right.</p>
    <p class="lede">The same method runs the {link("/nhi-lab/method/", "non-human identity lab")}.</p>
  </section>'''
    return page("/ca-mfa-lab/method/", "How the method works in the CA and MFA lab",
                "Write the guess, lock it in a commit, then write the code and run it. How the conditional access and MFA lab keeps its guesses honest, and how to check it.",
                "How the method works",
                "I write what I expect before any code exists, lock it in a commit, then run the cases. Where I was wrong, the wrong guess stays.",
                [link("/ca-mfa-lab/", "Lab overview"), link("/ca-mfa-lab/what-i-got-wrong/", "What I got wrong")],
                body, ("/ca-mfa-lab/what-i-got-wrong/", "What I got wrong"), ("/ca-mfa-lab/framework/", "Framework"))

# ---------------------------------------------------------------- overview patches
def patch_overview():
    p = "ca-mfa-lab/index.html"
    s = open(p, encoding="utf-8").read()
    # hero animation, right after the dek
    s = re.sub(r"<!-- chain:start -->.*?<!-- chain:end -->\n?", "", s, flags=re.S)
    s = s.replace("</p><ul class=\"nmeta\">", "</p>" + chain_svg() + "<ul class=\"nmeta\">", 1)
    s = re.sub(r'<link rel="stylesheet" href="/assets/ca-chain\.css[^"]*">\s*', "", s)
    s = s.replace("</head>", f'  <link rel="stylesheet" href="/assets/ca-chain.css?v={STAMP}">\n  </head>', 1)
    s = re.sub(r'<script defer src="/assets/ca-chain\.js[^"]*"></script>\s*', "", s)
    s = s.replace('<script defer src="/assets/chatbot-widget.js', f'<script defer src="/assets/ca-chain.js?v={STAMP}"></script>\n  <script defer src="/assets/chatbot-widget.js', 1)
    # short #wrong section that keeps the anchor
    m = re.search(r'<section class="nsec" id="wrong"[^>]*>.*?</section>', s, re.S)
    new = ('<section class="nsec" id="wrong" aria-labelledby="w-h">\n    <h2 id="w-h">The 6 guesses I got wrong</h2>\n'
           '    <p class="lede">I wrote every guess before any code existed. Six were wrong, all in Run 2. The pattern: I treated a notice as if it were a block (C01, C03), trusted a partner&rsquo;s MFA (A05), '
           'missed which control decides the 24 hour question (Z21), forgot what a location rule already covers (X07) and counted a habit as enforcement (A03).</p>\n'
           '    <p><a class="btn btn-primary" href="/ca-mfa-lab/what-i-got-wrong/">What I got wrong, case by case</a> '
           '<a class="btn" href="/ca-mfa-lab/method/">How the method works</a></p>\n  </section>')
    assert m, "no #wrong section"
    s = s[:m.start()] + new + s[m.end():]
    s = s.replace('The method is the same as the <a href="/nhi-lab/method/">non-human identity lab</a>.',
                  'How it works is on the <a href="/ca-mfa-lab/method/">method page</a>; the <a href="/nhi-lab/method/">non-human identity lab</a> uses the same method.')
    open(p, "w", encoding="utf-8").write(s)

if __name__ == "__main__":
    for path, fn in (("ca-mfa-lab/what-i-got-wrong/index.html", wrong_page), ("ca-mfa-lab/method/index.html", method_page)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(fn())
        print("wrote", path)
    patch_overview()
    print("overview patched")
