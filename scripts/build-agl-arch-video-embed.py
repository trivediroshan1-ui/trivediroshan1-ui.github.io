#!/usr/bin/env python3
"""Puts the architecture video on the lab page, just before the gateway section. Safe to run twice."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "ai-governance-lab/index.html")
html = open(P).read()
block = """<!-- archvid:start -->
      <section id="architecture-video">
        <h2>The whole architecture, in motion</h2>
        <p class="body-text">One picture of the lab, then each part on its own: the gateway, going round the gateway, noticing it, answering it, an identity starting in HR, an assistant that answers from documents, and agents handing work on. Every step has a caption. No sound.</p>
        <figure class="rvid" style="margin:18px 0;max-width:420px"><video controls playsinline preload="none" poster="/assets/share/agl-master-architecture.png" style="width:100%;height:auto;border-radius:12px;background:#05061a"><source src="/assets/share/agl-architecture.mp4" type="video/mp4"></video><figcaption class="body-text" style="font-size:.9em">2 minutes. <a href="/assets/share/agl-architecture.mp4">Download the full MP4</a> (7.0 MB), <a href="/assets/share/agl-architecture-60s.mp4">the 1-minute cut</a> (2.7 MB), or <a href="/assets/share/agl-master-architecture.png">the master picture</a>.</figcaption></figure>
      </section>
      <!-- archvid:end -->
"""
if "<!-- archvid:start -->" in html:
    html = re.sub(r"<!-- archvid:start -->.*?<!-- archvid:end -->\n", block, html, flags=re.S)
else:
    html = html.replace('      <section id="architecture">', "      " + block + '      <section id="architecture">', 1)
open(P, "w").write(html)
print("ok")
