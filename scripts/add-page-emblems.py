#!/usr/bin/env python3
"""A hand-drawn emblem beside the title of the hub pages that otherwise open with text only.

Same hand as the case study doodles (scripts/add-doodles.py): round caps, slightly loose lines.
Each emblem is decorative (aria-hidden) and draws itself in once when the page loads; with
reduced motion it simply appears. Styles live in assets/sitebar.css (search for page-emblem).

    python3 scripts/add-page-emblems.py           # write the emblems
    python3 scripts/add-page-emblems.py --check   # fail if a page is out of date (CI)
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ink: the main lines. a2: the accent lines, drawn in the second colour.
E = {
    "start": ('<path d="M58 108 V18"/><path d="M42 108 H76"/>'
              '<path d="M58 28 H92 L101 37 L92 46 H58"/><path d="M58 56 H26 L17 65 L26 74 H58"/>',
              '<path d="M80 98 h4 M90 91 h4 M100 84 h4"/>'),
    "method": ('<path d="M30 57 Q30 52 35 52 H85 Q90 52 90 57 V97 Q90 102 85 102 H35 Q30 102 30 97 Z"/>'
               '<path d="M42 52 V38 Q42 19 60 19 Q78 19 78 38 V52"/>',
               '<path d="M53 64 L49 92 M68 64 L64 92 M45 72 H73 M42 84 H70"/>'),
    "topics": ('<path d="M12 40 H50 L64 54 L50 68 H12 Z"/><circle cx="21" cy="54" r="3"/>'
               '<path d="M44 74 L80 67 L96 79 L85 95 L48 99 Z"/><circle cx="56" cy="86" r="3"/>',
               '<path d="M58 14 L92 18 L103 32 L89 43 L57 37 Z"/><circle cx="67" cy="26" r="3"/>'),
    "glossary": ('<path d="M60 30 Q40 19 13 25 V95 Q40 88 60 98"/><path d="M60 30 Q80 19 107 25 V95 Q80 88 60 98"/>'
                 '<path d="M60 30 V98"/>',
                 '<path d="M22 76 L31 50 L40 76 M26 67 H37"/><path d="M71 50 H96 M71 61 H94 M71 72 H89"/>'),
    "library": ('<path d="M8 98 H112 M8 56 H112"/><rect x="16" y="62" width="14" height="36" rx="2"/>'
                '<rect x="33" y="68" width="10" height="30" rx="2"/><rect x="66" y="66" width="11" height="32" rx="2"/>'
                '<rect x="68" y="22" width="12" height="34" rx="2"/><path d="M22 56 L30 26 L40 29 L32 56"/>',
                '<rect x="47" y="60" width="15" height="38" rx="2"/><rect x="84" y="30" width="16" height="26" rx="2"/>'),
    "privacy": ('<path d="M60 11 Q80 20 99 20 Q101 61 87 83 Q77 99 60 109 Q43 99 33 83 Q19 61 21 20 Q40 20 60 11 Z"/>',
                '<path d="M40 57 Q60 74 80 57"/><path d="M46 66 L42 75 M60 70 V80 M74 66 L78 75"/>'),
    "speaking": ('<rect x="46" y="12" width="28" height="50" rx="14"/><path d="M35 50 Q35 79 60 79 Q85 79 85 50"/>'
                 '<path d="M60 79 V101 M43 105 H77"/>',
                 '<path d="M96 30 Q104 41 96 52 M105 23 Q118 41 105 59"/>'),
    "contact": ('<rect x="12" y="34" width="84" height="58" rx="7"/><path d="M15 38 L54 68 L93 38"/>',
                '<path d="M106 12 V28 M98 20 H114"/><circle cx="104" cy="44" r="3"/>'),
    "now": ('<circle cx="60" cy="60" r="45"/><path d="M60 19 V28 M60 92 V101 M19 60 H28 M92 60 H101"/>'
            '<circle cx="60" cy="60" r="4"/>',
            '<path d="M60 60 L80 33 M60 60 L42 84"/>'),
    "search": ('<path d="M12 28 H70 M12 42 H58 M12 56 H48"/><circle cx="72" cy="68" r="24"/><path d="M90 86 L107 103"/>',
               '<path d="M60 58 Q64 50 72 50"/>'),
    "ca-mfa-lab/what-i-got-wrong": ('<rect x="12" y="20" width="46" height="46" rx="9"/><path d="M22 43 L33 54 L50 31"/>'
                                    '<rect x="62" y="54" width="46" height="46" rx="9"/>',
                                    '<path d="M74 66 L96 88 M96 66 L74 88"/>'),
    "ai-governance-lab/what-i-got-wrong": ('<rect x="12" y="20" width="46" height="46" rx="9"/><path d="M22 43 L33 54 L50 31"/>'
                                          '<rect x="62" y="54" width="46" height="46" rx="9"/>',
                                          '<path d="M74 66 L96 88 M96 66 L74 88"/>'),
    "nhi-lab/roadmap": ('<rect x="8" y="14" width="30" height="92" rx="6"/><rect x="45" y="14" width="30" height="92" rx="6"/>'
                        '<rect x="82" y="14" width="30" height="92" rx="6"/><path d="M14 28 H32 M14 40 H32 M51 28 H69"/>',
                        '<rect x="13" y="50" width="20" height="14" rx="3"/><rect x="50" y="40" width="20" height="14" rx="3"/>'
                        '<path d="M88 30 H106"/>'),
    "ai-governance-lab/implement": ('<path d="M16 106 V42 L60 16 L104 42 V106"/><path d="M8 106 H112"/>'
                                    '<rect x="26" y="52" width="14" height="14" rx="2"/><rect x="80" y="52" width="14" height="14" rx="2"/>',
                                    '<path d="M47 106 V72 H73 V106 M56 72 V106 M64 72 V106"/>'),
}

MARK = re.compile(r"\s*<!-- emblem:start -->.*?<!-- emblem:end -->", re.S)


def svg(ink, a2):
    lenify = lambda s: re.sub(r"<(path|rect|circle)\b", r'<\1 pathLength="1"', s)
    return ('<!-- emblem:start --><svg class="page-emblem" viewBox="0 0 120 120" aria-hidden="true" focusable="false" '
            'fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
            '<circle class="pe-glow" cx="60" cy="60" r="56" stroke="none"/>'
            f'<g class="pe-ink">{lenify(ink)}</g><g class="pe-a2">{lenify(a2)}</g></svg><!-- emblem:end -->')


def place(h, emblem):
    h = MARK.sub("", h)
    main = h.index("<main")
    # Hub pages: first thing inside the hero header. Library and search: just before their eyebrow.
    m = re.compile(r'(<header class="[^"]*\b(?:hero|nhero)\b[^"]*">)').search(h, main)
    if m:
        return h[:m.end()] + "\n        " + emblem + h[m.end():]
    m = re.compile(r'(\s*)(<p class="ey">)').search(h, main)
    if m:
        return h[:m.start(2)] + emblem + m.group(1) + h[m.start(2):]
    sys.exit("no place for the emblem")


check, stale = "--check" in sys.argv, []
for slug, (ink, a2) in E.items():
    p = ROOT / slug / "index.html"
    h = p.read_text(encoding="utf-8")
    new = place(h, svg(ink, a2))
    if new != h:
        stale.append(slug)
        if not check:
            p.write_text(new, encoding="utf-8")
if check and stale:
    sys.exit("page emblems out of date, run python3 scripts/add-page-emblems.py: " + ", ".join(stale))
print("page emblems up to date" if check else f"page emblems written on {len(stale)} pages")
