#!/usr/bin/env python3
"""Draw one small story illustration per case-study card (three icons, the key step ringed)
and put it in the card's <div class="art">. Icons are simple shapes on a 24 x 24 grid.
Safe to re-run: python3 scripts/case-art.py"""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

I = {  # stroke icons, 24x24
 "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M14 9l2 2"/>',
 "stack": '<rect x="4" y="3" width="16" height="5" rx="1.5"/><rect x="4" y="10" width="16" height="5" rx="1.5"/><rect x="4" y="17" width="16" height="4" rx="1.5"/><path d="M7 5.5h1M7 12.5h1"/>',
 "shieldok": '<path d="M12 3l8 3v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
 "shield": '<path d="M12 3l8 3v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/>',
 "vault": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="12" cy="12" r="4"/><path d="M12 8v1.5M12 14.5V16M8 12h1.5M14.5 12H16M6 20v1.5M18 20v1.5"/>',
 "hourglass": '<path d="M6 3h12M6 21h12M7 3c0 5 10 5 10 9s-10 4-10 9M17 3c0 5-10 5-10 9s10 4 10 9"/>',
 "people": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2c2.8.3 5 2.6 5 5.8"/>',
 "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>',
 "list": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8.5 8l1.5 1.5L12.5 7M8.5 13l1.5 1.5 2.5-2.5M14.5 8.5H16M14.5 13.5H16M8.5 18h7"/>',
 "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
 "docok": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 14l2 2 4-4"/>',
 "arrows": '<path d="M3 8h14l-3-3M17 8l-3 3M21 16H7l3-3M7 16l3 3"/>',
 "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
 "scale": '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 7h6zM19 7l-3 7h6z"/>',
 "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
 "chain": '<path d="M10 14a4 4 0 0 1 0-5.7l2.5-2.5a4 4 0 0 1 5.7 5.7L17 12.7"/><path d="M14 10a4 4 0 0 1 0 5.7l-2.5 2.5a4 4 0 0 1-5.7-5.7L7 11.3"/>',
 "robot": '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 4v4M9.5 13h.01M14.5 13h.01M9.5 16h5M3 12v3M21 12v3"/><circle cx="12" cy="3.5" r="1"/>',
 "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
 "rotate": '<path d="M20 12a8 8 0 1 1-2.3-5.7M20 4v4h-4"/>',
 "layers": '<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5M3 16.5L12 21l9-4.5"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
 "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 21h4"/>',
 "glass": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M12 3l-2 6 4 3-3 5 1 4M10 9l-6 1M14 12l6-2"/>',
 "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3M12 15v2"/>',
 "locks": '<rect x="2" y="9" width="8" height="7" rx="1.5"/><path d="M4 9V7a2 2 0 0 1 4 0v2"/><rect x="14" y="5" width="8" height="7" rx="1.5"/><path d="M16 5V3.5a2 2 0 0 1 4 0V5"/><rect x="9" y="15" width="7" height="6" rx="1.5"/><path d="M11 15v-1.5a1.5 1.5 0 0 1 3 0V15"/>',
 "funnel": '<path d="M3 4h18l-7 8v6l-4 2v-8z"/>',
 "building": '<rect x="4" y="3" width="11" height="18" rx="1"/><path d="M15 9h5v12h-5M7 7h2M11 7h1M7 11h2M11 11h1M7 15h2M11 15h1M8 21v-3h3v3"/>',
 "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "server": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01M11 7.5h6M11 16.5h6"/>',
 "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M8 15l2 2 4-4"/>',
 "pwd": '<rect x="2" y="7" width="20" height="10" rx="2"/><path d="M6 12h.01M10 12h.01M14 12h.01M18 12h.01M3 20L21 4"/>',
 "finger": '<path d="M8 20c-1-2-1.5-4-1.5-7a5.5 5.5 0 0 1 11 0c0 1.2-.2 2.4-.5 3.5"/><path d="M12 13c0 3-.5 5.5-1.5 8M9.5 9.5A3 3 0 0 1 15 12c0 2.5-.3 4.5-1 6.5M17 19.5c.4-.8.7-1.7.9-2.5"/>',
 "phone": '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M10.5 18.5h3"/>',
 "cloud": '<path d="M7 18a5 5 0 0 1-.6-10A6 6 0 0 1 18 8.5 4.5 4.5 0 0 1 17.5 18z"/>',
 "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>',
 "scissors": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M8.5 7.5L20 18M8.5 16.5L20 6"/>',
 "tool": '<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3l7.5-7.5a4 4 0 0 0-2-5.5"/>',
 "idcard": '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2.5"/><path d="M13 10h5M13 14h4M4.5 17c.6-1.6 1.9-2.5 3.5-2.5s2.9.9 3.5 2.5"/>',
 "gauge": '<path d="M3 17a9 9 0 1 1 18 0"/><path d="M12 17l5-6M7 13l1 .5M12 9v1M17 13l-1 .5"/>',
 "coin": '<ellipse cx="12" cy="7" rx="8" ry="3"/><path d="M4 7v5c0 1.7 3.6 3 8 3s8-1.3 8-3V7M4 12v5c0 1.7 3.6 3 8 3s8-1.3 8-3v-5"/>',
 "radar": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><path d="M12 12l6-6"/><circle cx="16" cy="15" r="1"/>',
 "truck": '<path d="M2 6h12v10H2zM14 10h4l3 3v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
 "pyramid": '<path d="M12 3l9 18H3z"/><path d="M8 11h8M5.5 16h13"/>',
 "warn": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
}

SCENES = {  # href: (left, middle, right) ; a list means a small stack of icons in that slot
 "/case-studies/credential-platform/": (["key", "key", "key"], "stack", "shieldok"),
 "/case-studies/pam-modernization/": ("vault", "hourglass", "key"),
 "/case-studies/privileged-access-program/": ("people", "list", "shieldok"),
 "/case-studies/migration-planning/": ("vault", "truck", "vault"),
 "/case-studies/platform-evaluation/": ("grid", "scale", "check"),
 "/case-studies/audit-mapping/": ("shield", "chain", "docok"),
 "/case-studies/ai-coworker/": ("person", "robot", "list"),
 "/case-studies/non-human-identity-at-scale/": (["gear", "server", "gear"], "key", "rotate"),
 "/case-studies/credential-tiering-model/": ("key", "pyramid", "shield"),
 "/case-studies/jit-jea-elevation/": ("person", "clock", "key"),
 "/case-studies/break-glass-access/": ("bell", "glass", "key"),
 "/case-studies/secrets-consolidation/": ("locks", "funnel", "vault"),
 "/case-studies/vendor-privileged-access/": ("building", "eye", "server"),
 "/case-studies/access-recertification/": ("people", "list", "calendar"),
 "/case-studies/passwordless-authentication/": ("pwd", "finger", "phone"),
 "/case-studies/ciem-at-scale/": ("cloud", "search", "scissors"),
 "/mcp-lab-case-study/": ("robot", "person", "tool"),
 "/case-studies/agentic-ai-identity-governance/": ("robot", "idcard", "doc"),
 "/case-studies/ai-processing-tax/": ("robot", "gauge", "coin"),
 "/case-studies/ai-agent-credential-sharing/": ("key", "warn", ["robot", "robot", "robot"]),
 "/case-studies/shadow-ai-discovery-gap/": ("radar", "eye", ["robot", "robot"]),
}

def icon(name, cx, cy, size, extra=""):
    s = size / 24
    return (f'<g transform="translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.3f})" fill="none" stroke="currentColor" '
            f'stroke-width="{1.6 / s * (size / 34):.2f}" stroke-linecap="round" stroke-linejoin="round"{extra}>{I[name]}</g>')

def slot(item, cx, cy, size):
    if isinstance(item, list):
        n = len(item); small = size * 0.62; gap = small * 0.95
        y0 = cy - gap * (n - 1) / 2
        return "".join(icon(name, cx + (8 if i % 2 else -8), y0 + i * gap, small, ' opacity=".85"') for i, name in enumerate(item))
    return icon(item, cx, cy, size)

def scene(parts):
    xs = (62, 160, 258); cy = 56
    out = ['<svg viewBox="0 0 320 112" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">',
           '<g stroke="currentColor" fill="none" stroke-width="1.2" opacity=".55" stroke-dasharray="3 4">'
           '<path d="M92 56H124"/><path d="M196 56H228"/></g>',
           '<g fill="currentColor" opacity=".7"><path d="M124 52l6 4-6 4z"/><path d="M228 52l6 4-6 4z"/></g>',
           f'<circle class="ring" cx="160" cy="{cy}" r="34" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 5" opacity=".7"/>',
           f'<circle cx="160" cy="{cy}" r="25" fill="currentColor" opacity=".1"/>']
    for i, (x, item) in enumerate(zip(xs, parts)):
        out.append(f'<g opacity="{1 if i == 1 else .78}">' + slot(item, x, cy, 34 if i == 1 else 30) + "</g>")
    out.append("</svg>")
    return "".join(out)

p = ROOT / "case-studies" / "index.html"
h = p.read_text()
n = 0
for href, parts in SCENES.items():
    pat = re.compile(r'(<a class="card"[^>]*href="' + re.escape(href) + r'"[^>]*>\s*<div class="art"[^>]*>)(.*?)(</div>)', re.S)
    h, k = pat.subn(lambda m: m.group(1) + scene(parts) + m.group(3), h, count=1)
    n += k
p.write_text(h)
print("illustrations set:", n, "of", len(SCENES))
