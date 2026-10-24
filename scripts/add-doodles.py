#!/usr/bin/env python3
"""Adds one small hand-drawn doodle to the top of each case study (inside the short-version box).
Safe to re-run: it replaces an existing doodle."""
import re, pathlib
D = {
 "break-glass-access": '<path d="M14 30 L64 24 L68 66 L18 72 Z"/><path d="M38 28 L33 44 L45 50 L40 70"/><path d="M62 10 L80 30"/><path d="M80 30 L88 22 L92 28 L84 36 Z"/>',
 "access-recertification": '<path d="M16 14 L68 12 L70 82 L14 84 Z"/><path d="M26 32 l6 7 l11 -13"/><path d="M26 54 l6 7 l11 -13"/><path d="M50 34 h12 M50 56 h12"/><path d="M74 62 l8 8 l12 -22"/>',
 "agentic-ai-identity-governance": '<rect x="20" y="30" width="56" height="42" rx="12"/><path d="M48 30 V16"/><circle cx="48" cy="12" r="4"/><circle cx="36" cy="49" r="4"/><circle cx="60" cy="49" r="4"/><path d="M36 62 q12 6 24 0"/><path d="M12 52 h8 M76 52 h8"/>',
 "ai-agent-credential-sharing": '<circle cx="28" cy="40" r="14"/><circle cx="28" cy="40" r="4"/><path d="M42 40 H86 M70 40 v12 M80 40 v9"/><path d="M14 72 q14 8 28 0 M54 72 q14 8 28 0"/>',
 "ai-coworker": '<rect x="18" y="26" width="48" height="38" rx="10"/><circle cx="32" cy="44" r="3.5"/><circle cx="52" cy="44" r="3.5"/><path d="M32 54 q10 5 20 0"/><path d="M42 26 V14"/><path d="M70 50 h12 v22 h-14"/><path d="M76 40 q3 -5 0 -8"/>',
 "ai-processing-tax": '<circle cx="46" cy="46" r="30"/><circle cx="46" cy="46" r="22"/><path d="M46 32 v28 M38 40 q8 -8 16 0 M38 52 q8 8 16 0"/><path d="M82 20 l6 -6 M84 34 h8"/>',
 "audit-mapping": '<path d="M14 14 L58 12 L60 70 L12 72 Z"/><path d="M22 28 h28 M22 40 h24 M22 52 h20"/><circle cx="66" cy="58" r="14"/><path d="M76 68 l14 14"/>',
 "ciem-at-scale": '<path d="M24 62 q-14 -2 -12 -16 q2 -12 16 -10 q4 -16 22 -14 q16 2 18 18 q16 0 14 16 q-2 8 -12 6 z"/><path d="M32 48 q16 -14 32 0 q-16 14 -32 0 z"/><circle cx="48" cy="48" r="4"/>',
 "credential-platform": '<rect x="14" y="14" width="68" height="68" rx="8"/><circle cx="48" cy="48" r="18"/><path d="M48 34 v28 M34 48 h28"/><circle cx="48" cy="48" r="4"/><path d="M22 82 v6 M74 82 v6"/>',
 "credential-tiering-model": '<path d="M10 80 H34 V58 H56 V36 H78 V14 H90"/><path d="M10 80 V90 H90"/><circle cx="22" cy="48" r="5"/><circle cx="44" cy="26" r="5"/><path d="M22 53 v5 M44 31 v5"/>',
 "jit-jea-elevation": '<path d="M26 12 H66 M26 84 H66"/><path d="M30 12 q0 30 18 36 q-18 6 -18 36 M62 12 q0 30 -18 36 q18 6 18 36"/><path d="M40 72 q8 -8 16 0"/><path d="M76 20 l8 -6 M78 32 h10"/>',
 "migration-planning": '<rect x="8" y="30" width="30" height="34" rx="5"/><rect x="62" y="30" width="30" height="34" rx="5"/><path d="M42 44 H58 M52 38 l8 6 l-8 6"/><path d="M42 58 H58" stroke-dasharray="3 4"/><path d="M15 76 h16 M69 76 h16"/>',
 "non-human-identity-at-scale": '<circle cx="48" cy="48" r="14"/><path d="M48 14 v10 M48 72 v10 M14 48 h10 M72 48 h10 M24 24 l7 7 M65 65 l7 7 M72 24 l-7 7 M31 65 l-7 7"/><path d="M42 48 h12"/>',
 "pam-modernization": '<path d="M20 78 L52 46"/><circle cx="60" cy="38" r="12"/><path d="M52 30 l8 8"/><path d="M66 82 V58 M56 68 l10 -12 l10 12"/><path d="M12 18 q6 -8 12 0"/>',
 "passwordless-authentication": '<path d="M30 80 q-12 -20 0 -44 q18 -22 40 -2"/><path d="M40 78 q-8 -16 2 -32 q10 -12 22 -4"/><path d="M52 74 q-3 -14 4 -22"/><path d="M62 30 q12 6 14 22"/><path d="M70 16 l4 -6 M80 24 l6 -4"/>',
 "platform-evaluation": '<path d="M48 14 V80 M30 80 H66"/><path d="M16 30 H80"/><path d="M16 30 l-8 22 h24 z M80 30 l-8 22 h24 z"/>',
 "privileged-access-program": '<path d="M8 82 Q30 40 48 56 Q66 72 92 30"/><path d="M8 82 H92"/><path d="M64 60 V22"/><path d="M64 22 L84 30 L64 38"/>',
 "secrets-consolidation": '<path d="M14 16 H82 L56 46 V68 L40 78 V46 Z"/><path d="M26 6 v6 M48 4 v8 M70 6 v6"/><path d="M40 84 h16"/>',
 "shadow-ai-discovery-gap": '<path d="M22 80 V40 q0 -24 26 -24 q26 0 26 24 V80 l-9 -8 l-9 8 l-8 -8 l-9 8 l-9 -8 z"/><circle cx="38" cy="42" r="4"/><circle cx="58" cy="42" r="4"/><path d="M42 56 q6 5 12 0"/><circle cx="78" cy="22" r="8"/><path d="M84 28 l8 8"/>',
 "vendor-privileged-access": '<rect x="22" y="22" width="44" height="58" rx="6"/><path d="M36 22 v-8 h16 v8"/><circle cx="44" cy="44" r="7"/><path d="M32 66 q12 -14 24 0"/><path d="M72 36 h14 M72 48 h10"/>',
}
CSS_MARK = "doodle"
for slug, body in D.items():
    p = pathlib.Path("case-studies")/slug/"index.html"
    s = p.read_text()
    s = re.sub(r'\s*<svg class="doodle".*?</svg>', '', s, flags=re.S)
    svg = ('<svg class="doodle" viewBox="0 0 96 96" width="88" height="88" aria-hidden="true" focusable="false" fill="none" '
           'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'+body+'</svg>')
    new, n = re.subn(r'(<div class="tldr">)', r'\1\n        '+svg, s, count=1)
    assert n == 1, slug
    p.write_text(new)
print("done", len(D))
