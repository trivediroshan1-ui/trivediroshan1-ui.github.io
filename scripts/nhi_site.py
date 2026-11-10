"""Shared page shell and small helpers for the NHI lab pages."""
import html, re, os, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape
CSS_V = '20261102d'
BASE = 'https://roshantrivedi.co.in'

SUBNAV = [
    ('/nhi-lab/', 'Overview', 'overview'),
    ('/nhi-lab/framework/', 'Framework', 'framework'),
    ('/nhi-lab/market/', 'Market', 'market'),
    ('/nhi-lab/method/', 'What we did', 'method'),
    ('/nhi-lab/audit/', 'Audit data', 'audit'),
    ('/nhi-lab/round-18/', 'Round 18', 'round18'),
    ('/nhi-lab/stage-2/', 'Stage 2', 'stage2'),
    ('/nhi-lab/roadmap/', 'Roadmap', 'roadmap'),
    ('/nhi-lab/explainer/', 'Explainer', 'explainer'),
    ('/nhi-lab/nhi-lab-book.pdf', 'Book (PDF)', 'book'),
    ('/book/', 'All books', 'books'),
]

def subnav(active):
    items = ''.join(
        f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{E(t)}</a>' for h, t, k in SUBNAV)
    return f'<nav class="nsub" aria-label="Non-human identity lab sections">{items}</nav>'

_idx = open(os.path.join(ROOT, 'ai-governance-lab', 'index.html'), encoding='utf-8').read()
_HEAD = _idx.split('<body')[0]
_NAV = re.search(r'<nav class="hg-sitenav".*?</nav>', _idx, re.S).group(0)
_FOOT = re.search(r'<footer class="hg-foot">.*?</footer>', _idx, re.S).group(0)

def shell(path, title, desc, og_title, body, js=None, ld=None, published='2026-11-02'):
    """path like 'nhi-lab/framework/'. Returns the whole HTML document."""
    url = f'{BASE}/{path}'
    head = _HEAD
    head = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{E(desc, True)}" />', head)
    head = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{url}" />', head)
    head = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{E(og_title, True)}" />', head)
    head = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{E(desc, True)}" />', head)
    head = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{url}" />', head)
    head = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*(")', r'\g<1>https://roshantrivedi.co.in/assets/share/og-nhi-lab.png\g<2>', head)
    head = re.sub(r'<title>.*?</title>', f'<title>{E(title)} &middot; Roshan Trivedi</title>', head, flags=re.S)
    head = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    extra = (f'  <link rel="stylesheet" href="/assets/blinks.css?v={CSS_V}">\n'
             f'  <link rel="stylesheet" href="/assets/nhi-lab.css?v={CSS_V}">\n'
             f'  <link rel="stylesheet" href="/assets/nhi-site.css?v={CSS_V}">\n')
    if ld:
        extra += f'  <script type="application/ld+json">{ld}</script>\n'
    head = head.replace('</head>', extra + '</head>')
    tail = f'  <script src="/assets/{js}?v={CSS_V}" defer></script>\n' if js else ''
    tail += '  <script defer src="/assets/chatbot-widget.js?v=20261105a"></script>\n'
    return (head + '  <body style="--c:#7df2d0">\n    <a class="skip" href="#main">Skip to content</a>\n    ' + _NAV +
            '\n' + body + '\n    ' + _FOOT + '\n' + tail + '  </body>\n</html>\n')

def hero(eyebrow, h1, dek, meta=()):
    m = ''.join(f'<li>{x}</li>' for x in meta)
    return (f'<header class="nhero"><p class="eyebrow">{E(eyebrow)}</p><h1>{E(h1)}</h1><p class="dek">{dek}</p>'
            + (f'<ul class="nmeta">{m}</ul>' if m else '') + '</header>')

def wrap(s, n):
    return textwrap.wrap(s, n) or ['']

def tsp(lines, x, y, dy=16, cls=''):
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<tspan x="{x}" y="{y + i * dy}"{c}>{E(l)}</tspan>' for i, l in enumerate(lines))

def box(x, y, w, h, title, sub='', cls='', num=None, tw=None):
    """A labelled box with an optional step number badge. Text is centred."""
    cx = x + w / 2
    tw = tw or max(10, int(w / 8.2))
    tl = wrap(title, tw)[:2]
    sl = wrap(sub, int(w / 6.6))[:3] if sub else []
    ty = y + 24 if not sl and len(tl) == 1 else y + 22
    total = len(tl) * 17 + len(sl) * 15
    ty = y + (h - total) / 2 + 13
    out = f'<rect class="bx {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
    out += f'<text class="tt" text-anchor="middle">{tsp(tl, cx, ty, 17)}</text>'
    if sl:
        out += f'<text class="ts" text-anchor="middle">{tsp(sl, cx, ty + len(tl) * 17 + 1, 15)}</text>'
    if num is not None:
        out += f'<circle class="nc" cx="{x + 4}" cy="{y + 4}" r="11"/><text class="nm" x="{x + 4}" y="{y + 8}" text-anchor="middle">{num}</text>'
    return out

def arrow(d, cls='', label=None, lx=0, ly=0, anchor='middle', mid='ah'):
    out = f'<path class="ar {cls}" d="{d}" marker-end="url(#{mid})"/>'
    if label:
        out += f'<text class="al" x="{lx}" y="{ly}" text-anchor="{anchor}">{E(label)}</text>'
    return out

def defs(mid='ah', color='var(--mut)'):
    return (f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{color}"/></marker></defs>')

def figure(svg, caption, legend=None):
    leg = ''
    if legend:
        leg = '<ul class="dgleg" aria-label="Legend">' + ''.join(f'<li><i class="{c}"></i>{E(t)}</li>' for c, t in legend) + '</ul>'
    return f'<figure class="dgfig"><div class="dgwrap">{svg}</div>{leg}<figcaption>{caption}</figcaption></figure>'

def table(head, rows, caption=None, cls='ntable'):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head)
    body = ''.join('<tr>' + ''.join(c for c in r) + '</tr>' for r in rows)
    cap = f'<caption>{caption}</caption>' if caption else ''
    return f'<div class="twrap" tabindex="0" role="region" aria-label="{E(caption or "table", True)}"><table class="{cls}">{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

def td(x, cls=''):
    return f'<td class="{cls}">{x}</td>' if cls else f'<td>{x}</td>'

def th_row(x):
    return f'<th scope="row">{x}</th>'

def case_link(cid):
    return f'<a href="/nhi-lab/#{cid.lower()}">{cid}</a>'

def case_links(ids):
    return ', '.join(case_link(i) for i in ids)

def badge(kind, text=None):
    names = {'primary': 'Primary source', 'secondary': 'Secondary source', 'vendor': 'Vendor claim', 'opinion': 'Opinion',
             'high': 'High confidence', 'med': 'Medium confidence', 'low': 'Low confidence', 'hi': 'High impact', 'irr': 'Irreversible'}
    return f'<span class="nb {kind}">{text or names[kind]}</span>'

def ld_article(name, desc, path, kind='TechArticle', date='2026-11-02'):
    import json
    return json.dumps({
        '@context': 'https://schema.org', '@type': kind, 'headline': name, 'description': desc,
        'url': f'{BASE}/{path}', 'datePublished': date, 'dateModified': date,
        'author': {'@type': 'Person', 'name': 'Roshan Trivedi', 'url': f'{BASE}/'},
        'license': 'https://creativecommons.org/licenses/by/4.0/', 'isAccessibleForFree': True,
    }, separators=(',', ':'))

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)
    print('wrote', path, len(text))
