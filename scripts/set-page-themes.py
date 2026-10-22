#!/usr/bin/env python3
"""Gives every page its own background theme.

Each page gets  <html data-bg="name" data-m="motif">  and assets/themes.css is rewritten from the table below.
A theme is three hues (the glow colours), a motif (the pattern drawn behind the page) and how that pattern moves.
The look is pure CSS plus the SVG tiles in assets/bg/, so it works under the site's script policy and
stops moving for anyone who asks their device for reduced motion.

Safe to re-run:  python3 scripts/set-page-themes.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# name: (hue 1, hue 2, hue 3, motif, scale, dx, dy, seconds for one tile of drift)
THEMES = {
    # site pages
    "home":      (262, 190, 35,  "nodes",    1.15,  1,  0, 160),
    "work":      (250, 170, 320, "grid",     1.0,   0,  1, 150),
    "about":     (28,  330, 255, "dots",     1.0,   1,  1, 170),
    "now":       (165, 205, 55,  "waves",    1.2,  -1,  0, 130),
    "ai":        (278, 195, 330, "topo",     1.0,   0, -1, 150),
    "resume":    (215, 255, 185, "diag",     1.4,   1, -1, 200),
    "labs":      (188, 265, 150, "cubes",    1.0,  -1,  1, 170),
    "book":      (36,  335, 265, "ledger",   1.1,   0,  1, 220),
    "writing":   (22,  285, 195, "ledger",   1.0,   0, -1, 200),
    "series":    (160, 215, 270, "chevrons", 0.9,   1,  0, 120),
    "designsys": (282, 190, 150, "grid",     1.3,   1,  1, 180),
    "tiercheck": (160, 258, 42,  "rings",    0.9,   1, -1, 160),
    "exams":     (28,  145, 228, "ledger",   1.2,   1,  0, 190),
    "notfound":  (350, 265, 200, "topo",     1.2,  -1,  0, 140),
    # MCP lab
    "mcp":       (190, 268, 152, "circuit",  1.0,   1,  0, 150),
    "mcpdepth":  (205, 275, 25,  "grid",     0.9,  -1,  0, 170),
    "mcpresult": (152, 190, 42,  "rings",    1.0,   0,  1, 160),
    "mcpcases":  (270, 190, 335, "chevrons", 1.1,   1,  1, 130),
    "mcpportal": (192, 150, 272, "hex",      1.2,   0, -1, 180),
    # essays
    "post-breach":    (6,   320, 275, "rings",    1.0, -1, 0, 170),
    "post-framework": (205, 165, 255, "hex",      1.0,  0, 1, 180),
    "post-identity":  (288, 205, 160, "nodes",    1.0,  1, 0, 150),
    "post-plan":      (150, 215, 48,  "grid",     1.0,  0, 1, 160),
    "post":           (22,  285, 195, "ledger",   1.0,  0, -1, 200),
    # case studies
    "cs-credential-platform":          (160, 205, 262, "circuit",  1.1,  1,  0, 150),
    "cs-pam-modernization":            (150, 265, 40,  "keys",     1.1,  0,  1, 170),
    "cs-privileged-access-program":    (172, 255, 38,  "grid",     1.0, -1,  1, 160),
    "cs-migration-planning":           (262, 175, 330, "chevrons", 1.2,  1,  1, 130),
    "cs-platform-evaluation":          (270, 35,  190, "diag",     1.1,  1,  0, 180),
    "cs-audit-mapping":                (38,  260, 175, "ledger",   1.0,  0,  1, 210),
    "cs-ai-coworker":                  (190, 275, 330, "nodes",    0.9,  0, -1, 150),
    "cs-non-human-identity-at-scale":  (195, 150, 270, "topo",     1.0,  1,  0, 160),
    "cs-credential-tiering-model":     (158, 258, 45,  "cubes",    1.1,  0,  1, 170),
    "cs-jit-jea-elevation":            (150, 200, 45,  "waves",    1.0,  1,  0, 120),
    "cs-break-glass-access":           (8,   25,  255, "rings",    1.1, -1,  0, 150),
    "cs-secrets-consolidation":        (265, 160, 40,  "dots",     1.0,  1, -1, 170),
    "cs-vendor-privileged-access":     (168, 265, 215, "keys",     1.3, -1,  0, 190),
    "cs-access-recertification":       (38,  150, 265, "waves",    1.4,  0,  1, 140),
    "cs-passwordless-authentication":  (272, 195, 320, "topo",     1.3, -1,  1, 150),
    "cs-ciem-at-scale":                (255, 190, 150, "cubes",    1.3,  1, -1, 180),
    "cs-agentic-ai-identity-governance": (192, 285, 335, "nodes",  1.2, -1, -1, 160),
    "cs-ai-processing-tax":            (200, 28,  285, "diag",     0.9,  0,  1, 200),
    "cs-ai-agent-credential-sharing":  (185, 260, 160, "circuit",  0.9,  0, -1, 160),
    "cs-shadow-ai-discovery-gap":      (200, 275, 350, "rings",    1.3,  1,  1, 170),
}
# Brand alignment (October 2026). Every page now shares the site's violet + cyan glow pair, so the site reads as one
# brand. Each page keeps its own character through its motif, its drift and its third (accent) glow. Pages whose
# first glow used to be warm (orange, red) keep that warmth as the accent instead.
def _brand(h1, h2, h3):
    warm = h1 < 60 or h1 > 330
    return (255 + h1 % 25, 185 + h2 % 15, h1 if warm else h3)
THEMES = {k: _brand(*v[:3]) + tuple(v[3:]) for k, v in THEMES.items()}

MOTIF_SIZE = {"hex": (249.415, 288), "cubes": (249.415, 288)}
MOTIFS = ["grid", "dots", "waves", "topo", "circuit", "hex", "cubes", "rings", "nodes", "keys", "diag", "chevrons", "ledger"]

# page file -> theme name. Veil strength: how much of the middle is calmed so text stays easy to read.
PAGES = {
    "index.html": "home", "case-studies/index.html": "work", "about/index.html": "about", "now/index.html": "now",
    "ai/index.html": "ai", "resume/index.html": "resume", "labs/index.html": "labs", "book/index.html": "book",
    "writing/index.html": "writing", "writing/pam-series/index.html": "series", "design-system/index.html": "designsys",
    "tools/tier-check/index.html": "tiercheck", "secure-india-exams/index.html": "exams", "404.html": "notfound",
    "mcp-lab-case-study/index.html": "mcp", "mcp-lab-in-depth/index.html": "mcpdepth", "mcp-lab-results/index.html": "mcpresult",
    "mcp-lab-use-cases/index.html": "mcpcases", "mcp-lab-portal/index.html": "mcpportal",
}
for d in sorted((ROOT / "case-studies").iterdir()):
    if d.is_dir() and (d / "index.html").exists():
        PAGES[f"case-studies/{d.name}/index.html"] = f"cs-{d.name}"
        assert f"cs-{d.name}" in THEMES, f"no theme for {d.name}"
HOME_LIKE = {"home"}   # pages whose cards carry the content: lighter veil
INDEX_LIKE = {"work", "labs", "writing", "series", "book", "mcpportal"}

def theme_css():
    out = ["""/* Page themes. GENERATED by scripts/set-page-themes.py: edit the table there, not this file.
   Every page has <html data-bg="..." data-m="...">. Three glows drift slowly behind a tiled pattern.
   Only CSS and SVG tiles: no script, so it works under the site's script policy. */
:root {
  --m-grid: url(/assets/bg/grid.svg); --m-dots: url(/assets/bg/dots.svg); --m-waves: url(/assets/bg/waves.svg); --m-topo: url(/assets/bg/topo.svg);
  --m-circuit: url(/assets/bg/circuit.svg); --m-hex: url(/assets/bg/hex.svg); --m-cubes: url(/assets/bg/cubes.svg); --m-rings: url(/assets/bg/rings.svg);
  --m-nodes: url(/assets/bg/nodes.svg); --m-keys: url(/assets/bg/keys.svg); --m-diag: url(/assets/bg/diag.svg); --m-chevrons: url(/assets/bg/chevrons.svg);
  --m-ledger: url(/assets/bg/ledger.svg);
}
html[data-bg] {
  --h1: 250; --h2: 190; --h3: 320;
  --tb-w: 360px; --tb-h: 360px; --tb-s: 1; --tb-dx: 1; --tb-dy: 0; --tb-dur: 160s; --tb-mesh: 60s;
  --tw: calc(var(--tb-w) * var(--tb-s)); --th: calc(var(--tb-h) * var(--tb-s));
  --tb-base: hsl(var(--h1) 48% 5%);
  --tb-a: hsl(var(--h1) 85% 52% / .30); --tb-b: hsl(var(--h2) 85% 50% / .21); --tb-c: hsl(var(--h3) 80% 52% / .19);
  --tb-ink: hsl(var(--h2) 90% 78%); --tb-mo: .15; --tb-veil: .55;
  background-color: var(--tb-base);
}
html[data-bg][data-theme="light"] {
  --tb-base: hsl(var(--h1) 42% 97%);
  --tb-a: hsl(var(--h1) 85% 62% / .20); --tb-b: hsl(var(--h2) 85% 58% / .15); --tb-c: hsl(var(--h3) 80% 62% / .14);
  --tb-ink: hsl(var(--h1) 55% 30%); --tb-mo: .11;
}
html[data-bg]:has(body.read) { --tb-veil: .82; }
html[data-bg="home"] { --tb-veil: .0; }
"""]
    for m in MOTIFS:
        w, h = MOTIF_SIZE.get(m, (360, 360))
        out.append(f'html[data-m="{m}"] {{ --tb-motif: var(--m-{m}); --tb-w: {w:g}px; --tb-h: {h:g}px; }}')
    out.append("")
    for name, (h1, h2, h3, m, s, dx, dy, dur) in THEMES.items():
        extra = ""
        if name in INDEX_LIKE: extra = " --tb-veil: .3;"
        out.append(f'html[data-bg="{name}"] {{ --h1: {h1}; --h2: {h2}; --h3: {h3}; --tb-s: {s:g}; --tb-dx: {dx}; --tb-dy: {dy}; --tb-dur: {dur}s;{extra} }}')
    out.append("/* Pages made of many cards and small chips get quieter glows in the light theme, so the chip text keeps its contrast */")
    for name in sorted(INDEX_LIKE | HOME_LIKE):
        out.append(f'html[data-bg="{name}"][data-theme="light"] {{ --tb-a: hsl(var(--h1) 85% 62% / .12); --tb-b: hsl(var(--h2) 85% 58% / .09); --tb-c: hsl(var(--h3) 80% 62% / .08); --tb-mo: .08; }}')
    out.append("""
/* The pages paint their own background colour in a few places; the theme sits behind everything */
html[data-bg] body { background-color: transparent !important; }
/* The exam paper is a light, print-style document with dark text and its own white page: keep its page white in both themes. */
html[data-bg="exams"] body { background-color: #fff !important; }
html[data-bg] body::before { display: none; }
html[data-bg]::before {
  content: ""; position: fixed; inset: -18%; z-index: -4; pointer-events: none;
  background:
    radial-gradient(52% 46% at 14% 18%, var(--tb-a), transparent 72%),
    radial-gradient(46% 42% at 88% 8%, var(--tb-b), transparent 72%),
    radial-gradient(54% 50% at 72% 96%, var(--tb-c), transparent 74%),
    radial-gradient(40% 40% at 6% 88%, var(--tb-b), transparent 70%);
  animation: tb-drift var(--tb-mesh) ease-in-out infinite alternate; will-change: transform;
}
html[data-bg]::after {
  content: ""; position: fixed; inset: calc(var(--th) * -1) calc(var(--tw) * -1); z-index: -3; pointer-events: none;
  background: var(--tb-ink); opacity: var(--tb-mo);
  -webkit-mask: var(--tb-motif) 0 0 / var(--tw) var(--th) repeat; mask: var(--tb-motif) 0 0 / var(--tw) var(--th) repeat;
  animation: tb-slide var(--tb-dur) linear infinite; will-change: transform;
}
/* a soft veil over the reading column keeps text calm */
html[data-bg] body::after {
  content: ""; position: fixed; inset: 0; z-index: -2; pointer-events: none; opacity: 1; background-size: auto;
  background: radial-gradient(ellipse 40% 100% at 50% 40%, color-mix(in srgb, var(--tb-base) calc(var(--tb-veil) * 100%), transparent) 0%, transparent 100%);
}
@keyframes tb-drift { from { transform: translate3d(-2%, -1%, 0) rotate(-1deg) scale(1); } to { transform: translate3d(2%, 2%, 0) rotate(1.5deg) scale(1.08); } }
@keyframes tb-slide { to { transform: translate3d(calc(var(--tw) * var(--tb-dx)), calc(var(--th) * var(--tb-dy)), 0); } }
@media (prefers-reduced-motion: reduce) { html[data-bg]::before, html[data-bg]::after { animation: none; } }
@media print { html[data-bg]::before, html[data-bg]::after, html[data-bg] body::after { display: none; } }

/* Moving between pages: a short fade and lift in browsers that support it (Chrome, Edge, Safari 18.2+; others just navigate) */
@view-transition { navigation: auto; }
@media (prefers-reduced-motion: reduce) { @view-transition { navigation: none; } }
.hg-sitenav, header.top { view-transition-name: sitenav; }
::view-transition-old(root) { animation: vt-out .26s ease both; }
::view-transition-new(root) { animation: vt-in .4s cubic-bezier(.2, .7, .2, 1) both; }
@keyframes vt-out { to { opacity: 0; transform: translateY(-6px); } }
@keyframes vt-in { from { opacity: 0; transform: translateY(12px); } }
""")
    (ROOT / "assets" / "themes.css").write_text("\n".join(out))

VER = "20261022m"
LINK = f'<link rel="stylesheet" href="/assets/themes.css?v={VER}">\n    <link rel="stylesheet" href="/assets/site-2026.css?v={VER}">'

def apply(path, name):
    p = ROOT / path
    h = p.read_text()
    m_ = THEMES[name][3]
    h2 = re.sub(r'<html lang="en"[^>]*>', f'<html lang="en" data-bg="{name}" data-m="{m_}">', h, count=1)
    h2 = re.sub(r'\s*<link rel="stylesheet" href="/assets/(themes|site-2026)\.css[^>]*>', "", h2)
    # last stylesheet in <head>, so it wins; inline <style> on the home page comes earlier in the file
    h2 = h2.replace("</head>", f"    {LINK}\n  </head>", 1)
    if h2 != h:
        p.write_text(h2)
        return 1
    return 0

if __name__ == "__main__":
    theme_css()
    n = sum(apply(path, name) for path, name in PAGES.items())
    # the post layout reads its theme from each post's front matter ("bg:"), default "post"
    lay = ROOT / "_layouts" / "post.html"
    h = lay.read_text()
    h = re.sub(r'<html lang="en"[^>]*>', '<html lang="en" data-bg="{{ page.bg | default: \'post\' }}" data-m="{{ page.motif | default: \'ledger\' }}">', h, count=1)
    h = re.sub(r'\s*<link rel="stylesheet" href="/assets/(themes|site-2026)\.css[^>]*>', "", h)
    h = h.replace("</head>", f"    {LINK}\n  </head>", 1)
    lay.write_text(h)
    POSTS = {"2026-07-25-openai-huggingface-breach-cybersecurity-analysis.md": ("post-breach", "rings"),
             "2026-10-10-pam-framework-and-design.md": ("post-framework", "hex"),
             "2026-10-10-pam-as-an-identity.md": ("post-identity", "nodes"),
             "2026-10-10-pam-project-plan-by-organization-tier.md": ("post-plan", "grid")}
    for fn, (bg, mo) in POSTS.items():
        f = ROOT / "_posts" / fn
        t = f.read_text()
        t = re.sub(r"^bg: .*\n|^motif: .*\n", "", t, flags=re.M)
        t = t.replace("\nlayout: post\n", f"\nlayout: post\nbg: {bg}\nmotif: {mo}\n", 1)
        f.write_text(t)
    print("themes:", len(THEMES), "| pages updated:", n)
