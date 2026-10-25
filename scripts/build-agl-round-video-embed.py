#!/usr/bin/env python3
"""Puts the round videos (assets/share/agl-round-N.mp4) into the lab page, under each round's animated journey.
Safe to re-run. Run after the round page builders: python3 scripts/build-agl-round-video-embed.py"""
import os, re, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "ai-governance-lab/index.html")
h = open(P, encoding="utf-8").read()
SEC = {10: ("credentials", "Credentials, sessions and identity edge cases"), 11: ("delegation", "Agents handing work to agents, keys and mergers"),
       12: ("approvals", "Who approved it, what exactly, and when"), 13: ("meaning", "Finding documents by meaning")}
for n, (sid, name) in SEC.items():
    mp4 = f"assets/share/agl-round-{n}.mp4"
    if not os.path.exists(os.path.join(ROOT, mp4)): continue
    mb = os.path.getsize(os.path.join(ROOT, mp4)) / 1e6
    block = (f'<!-- rv{n}:start -->\n        <figure class="rvid" style="margin:18px 0;max-width:420px">'
             f'<video controls playsinline preload="none" poster="/assets/share/agl-round-{n}-poster.jpg" style="width:100%;height:auto;border-radius:12px;background:#05061a">'
             f'<source src="/{mp4}" type="video/mp4"></video>'
             f'<figcaption class="body-text" style="font-size:.9em">Round {n} as a short video, no sound: {name}. <a href="/{mp4}">Download the MP4</a> ({mb:.1f} MB).</figcaption></figure>\n        <!-- rv{n}:end -->')
    h = re.sub(rf"<!-- rv{n}:start -->.*?<!-- rv{n}:end -->\n?\s*", "", h, flags=re.S)
    i = h.index(f'<section id="{sid}"'); j = h.index("</section>", i); seg = h[i:j]
    k = seg.index('<ol class="lc-steps">'); k = seg.index("</ol>", k); k = seg.index("</div>", k) + len("</div>")
    seg = seg[:k] + "\n        " + block + seg[k:]
    h = h[:i] + seg + h[j:]
open(P, "w", encoding="utf-8").write(h)
print("ok", sum(h.count(f"<!-- rv{n}:start -->") for n in SEC), "videos embedded")
