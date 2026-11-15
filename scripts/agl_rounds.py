#!/usr/bin/env python3
"""AI governance lab: rounds 5 to 13 live on their own pages (/ai-governance-lab/round-N/).
The overview keeps one table with a row per round. Each row carries the old section id, so old links like
/ai-governance-lab/#bypass still land on the right row.

Used two ways:
  python3 scripts/agl_rounds.py split      one-time move of the round sections out of the overview
  from agl_rounds import write_round       the build-agl-rN-page.py scripts call this instead of editing the overview
Safe to re-run."""
import html, os, re, sys

SHORT_TITLES = {5: 'gaps in my own audit', 6: 'agents that instruct an API', 7: 'from HR to the directory', 8: 'agents that bypass the gateway', 9: 'a document assistant', 10: 'credentials and sessions', 11: 'agent-to-agent handoffs', 12: 'who approved what, and when', 13: 'finding documents by meaning'}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_nav

OVERVIEW = os.path.join(ROOT, "ai-governance-lab", "index.html")
TEMPLATE = os.path.join(ROOT, "ai-governance-lab", "what-i-got-wrong", "index.html")
BASE = "https://roshantrivedi.co.in"
REVIEWED = "14 November 2026"
def E(x, quote=False):
    return html.escape(x, quote=quote)

# n: (old section id, title shown on the page, cases added, one line for the overview table)
ROUNDS = {
    5: ("round5", "Gaps I found in my own audit", 14,
        "Gaps I found in my own audit, starting with the claim that an AI only needs read access on your domain."),
    6: ("api-pattern", "Zoom in: agents that send instructions to an API", 18,
        "An agent that only sends a request, while a gateway outside it decides and acts."),
    7: ("hr-lifecycle", "From HR to the directory: how an identity should start", 12,
        "How an identity should start, from HR to the directory, one step at a time."),
    8: ("bypass", "When an agent goes around the gateway", 12,
        "What happens when an agent finds a way round the gateway, and how the response plays out."),
    9: ("rag", "An assistant that answers from documents", 12,
        "Where the permission is checked in an assistant that answers from documents, and what still leaks."),
    10: ("credentials", "Credentials, sessions and identity edge cases", 12,
         "A copied token, a leaver with a live session, a rehire, a contractor, an emergency account and an erasure request."),
    11: ("delegation", "Agents handing work to agents, keys and mergers", 12,
         "One agent handing work to another, what a compromised executor can sign, rotated keys and merged companies."),
    12: ("approvals", "Who approved, what exactly, and when", 7,
         "Who approved, what exactly, and whether it was still true when it ran."),
    13: ("meaning", "Finding documents by meaning", 6,
         "Whether round nine's permission controls still hold when a document is found by meaning instead of words."),
}
HELD_BROKE = {5: ('All 14 cases came out as I guessed.', 'Nothing differed from my guesses on the first run.'),
    6: ('All 18 cases came out as I guessed.', 'A wrong but allowed request, such as the wrong person with the same name, passes every check (case T15). That is a limit, not a fix.'),
    7: ('All 12 cases came out as I guessed.', 'In the first control-off check, 13 of 14 were noticed: my MFA test could not tell a missing MFA step from a missing signed policy.'),
    8: ('All 12 cases came out as I guessed.', 'Nothing differed on the first run. Real products and real networks will behave differently.'),
    9: ('11 of 12 as I guessed on the first run, then 12 of 12 after a fix.', 'Case Q8 was a fault in my own code: my Aadhaar masking only caught numbers written with spaces.'),
    10: ('All 12 cases came out as I guessed the first time.', 'Nothing differed, which shows the rules do what I intended, not that I thought of every case.'),
    11: ('11 of 12 as I guessed on the first run, then 12 of 12 after a fix.', 'Case D11 was a fault in my own test: one number written three ways counted as a hit for all three.'),
    12: ('All 7 cases came out as I guessed.', 'Nothing differed on the first run.'),
    13: ('All 6 cases came out as I guessed.', 'A broken install made every case fail, and my checker counted that error as noticing. Round 13 now uses a stricter rule.')}

WORD = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen"}

def path(n):
    return f"/ai-governance-lab/round-{n}/"

def file_for(n):
    return os.path.join(ROOT, "ai-governance-lab", f"round-{n}", "index.html")

def table():
    rows = ""
    for n, (sid, title, cases, line) in ROUNDS.items():
        held, broke = HELD_BROKE[n]
        rows += (f'<tr id="{sid}"><td style="white-space:normal"><a href="{path(n)}">Round {n}</a><br><small>{cases} new cases</small></td>'
                 f'<td style="white-space:normal"><b>Asks:</b> {E(line)}<br><b>Held:</b> {E(held)}<br><b>Broke:</b> {E(broke)}</td></tr>\n              ')
    return f'''<!-- rounds:start -->
      <section id="rounds">
        <h2>Rounds 5 to 13, one page each</h2>
        <p class="body-text">After the first four rounds I kept testing the gaps I found in my own lab. Each round has its own page with the full write-up, the cases and the guesses file. Under each round number is how many cases it added. "Held" and "Broke" describe the first run against the guesses I wrote down before running it.</p>
        <div class="tbl-wrap">
          <table class="tbl" style="table-layout:fixed;width:100%;min-width:0">
            <colgroup><col style="width:26%"><col></colgroup>
            <thead><tr><th>Round</th><th>The question, what held, what broke</th></tr></thead>
            <tbody>
              {rows.rstrip()}
            </tbody>
          </table>
        </div>
      </section>
<!-- rounds:end -->

      '''

def lab_foot(n):
    prev = ("/ai-governance-lab/#rounds", "All rounds") if n == 5 else (path(n - 1), f"Round {n - 1}")
    nxt = ("/ai-governance-lab/cases/", "Every use case") if n == 13 else (path(n + 1), f"Round {n + 1}")
    return (f'<nav class="lab-foot" aria-label="More in this lab"><a class="lf-prev" href="{prev[0]}"><small>Previous</small><b>{prev[1]}</b></a>'
            f'<a class="lf-next" href="{nxt[0]}"><small>Next</small><b>{nxt[1]}</b></a>'
            f'<span class="lf-extra"><a href="/assets/ai-governance-lab-book.pdf">Get the book</a><a href="/topics/">Browse by topic</a></span></nav>')

def render_page(n, block):
    sid, title, cases, line = ROUNDS[n]
    t = open(TEMPLATE, encoding="utf-8").read()
    i, j = t.index('<main id="main">'), t.index("</main>")
    head, after = t[:i], t[j + len("</main>"):]
    url = f"{BASE}{path(n)}"
    ttl = f"AI governance lab, round {n}: {title}"
    # Search results cut titles after about 60 characters, so the <title> uses a short form.
    short = f"Round {n}: {SHORT_TITLES.get(n, title)} · AI governance lab"
    head = re.sub(r"<title>[^<]*</title>", lambda m: f"<title>{E(short)}</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*" />', lambda m: f'<meta name="description" content="{E(line, quote=True)}" />', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*" />', lambda m: f'<meta property="og:title" content="{E(ttl, quote=True)}" />', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*" />', lambda m: f'<meta property="og:description" content="{E(line, quote=True)}" />', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', head)
    if "agl-lifecycle.css" not in head:
        head = head.replace("</head>", '    <link rel="stylesheet" href="/assets/agl-lifecycle.css?v=20261111a">\n  </head>', 1)
    after = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + (
        '{"@context":"https://schema.org","@type":"TechArticle","headline":%s,"dateModified":"2026-11-14",'
        '"author":{"@type":"Person","name":"Roshan Trivedi","url":"https://roshantrivedi.co.in/"},"url":"%s",'
        '"isPartOf":{"@type":"WebPage","url":"%s/ai-governance-lab/"},"license":"https://creativecommons.org/licenses/by/4.0/"}'
        % (__import__("json").dumps(ttl), url, BASE)) + "</script>", after, count=1, flags=re.S)
    if "agl-lifecycle.js" not in after:
        after = after.replace('<script defer src="/assets/chatbot-widget.js', '<script defer src="/assets/agl-lifecycle.js?v=20261025a"></script>\n  <script defer src="/assets/chatbot-widget.js', 1)
    hero = (f'<header class="hero mcp-hero">\n        <p class="eyebrow">AI governance lab</p>\n        <h1>Round {n} of the AI governance lab</h1>\n'
            f'        <p class="dek">{E(line)}</p><p class="lastrev">Last reviewed {REVIEWED}</p>\n'
            f'        <div class="mcp-ribbon" aria-hidden="true"></div>\n      </header>\n'
            f'      <p class="body-text"><a href="/ai-governance-lab/#rounds">All rounds</a> &middot; <a href="/ai-governance-lab/">Lab overview</a> &middot; <a href="/ai-governance-lab/cases/">Case explorer</a></p>\n')
    nav = lab_nav.render("agl", path(n))
    return head + '<main id="main">\n      ' + nav + "\n      " + hero + "\n      " + block.strip() + "\n    " + lab_foot(n) + "\n</main>" + after

def _fw_markers(h):
    return h

def refresh_overview(h):
    """Put the rounds table in the overview, once, in place of any earlier table."""
    h = re.sub(r"<!-- rounds:start -->.*?<!-- rounds:end -->\n\n      ", "", h, flags=re.S)
    anchor = "<!-- fw:start -->"
    assert anchor in h, "overview has no frameworks marker"
    return h.replace(anchor, table() + anchor, 1)

def write_round(n, block):
    """Called by build-agl-rN-page.py with the round's block (start and end markers included)."""
    if n == 5 and os.path.exists(file_for(5)) and "--force" not in sys.argv:
        pass
    elif n == 5:  # round five's block also carries the standards table, which stays on the overview
        k = block.index('<section id="frameworks">')
        fw, block = block[k:].replace("<!-- r5:end -->", "").rstrip(), block[:k] + "<!-- r5:end -->"
        h = open(OVERVIEW, encoding="utf-8").read()
        h = re.sub(r"<!-- fw:start -->.*?<!-- fw:end -->", lambda m: "<!-- fw:start -->\n      " + fw + "\n<!-- fw:end -->", h, flags=re.S)
        open(OVERVIEW, "w", encoding="utf-8").write(h)
    p = file_for(n)
    if os.path.exists(p) and "--force" not in sys.argv:
        print(f"round {n}: ai-governance-lab/round-{n}/index.html exists and has had edits since this script was written "
              "(video blocks, wording). Not overwritten. Pass --force to rebuild it from this script.")
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(render_page(n, block))
    print(f"round {n}: wrote ai-governance-lab/round-{n}/index.html")

def split():
    h = open(OVERVIEW, encoding="utf-8").read()
    if "<!-- rounds:start -->" in h:
        print("already split"); return
    for n in ROUNDS:
        m = re.search(rf"<!-- r{n}:start -->.*?<!-- r{n}:end -->", h, re.S)
        assert m, n
        block = m.group(0)
        if n == 5:
            k = block.index('<section id="frameworks">')
            fw = block[k:].replace("<!-- r5:end -->", "").rstrip()
            block = block[:k] + "<!-- r5:end -->"
            h = h.replace(m.group(0), "<!-- fw:start -->\n      " + fw + "\n<!-- fw:end -->", 1)
        else:
            h = h.replace(m.group(0), "", 1)
        p = file_for(n)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(render_page(n, block))
    h = refresh_overview(h)
    h = re.sub(r"\n(\s*\n){2,}", "\n\n", h)
    open(OVERVIEW, "w", encoding="utf-8").write(h)
    print("split", len(ROUNDS), "rounds")

if __name__ == "__main__":
    if sys.argv[1:] == ["split"]:
        split()
    else:
        print(__doc__)
