#!/usr/bin/env python3
"""Put the home page's CSS inline, so the first paint does not wait for four
separate stylesheet requests (the biggest mobile PageSpeed item). The source
files stay as they are: edit them, then run this from the repo root.

    python3 scripts/inline-home-css.py

It rewrites the block between the inline-css markers in index.html.
"""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ["fonts.css", "home.css", "upgrade.css", "chatbot-widget.css"]
css = ""
for f in FILES:
    t = (ROOT / "assets" / f).read_text()
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    css += re.sub(r"\s+", " ", t).strip() + "\n"
page = ROOT / "index.html"
h = page.read_text()
block = "<!-- inline-css:start -->\n<style>\n" + css + "</style>\n<!-- inline-css:end -->"
if "<!-- inline-css:start -->" in h:
    h = re.sub(r"<!-- inline-css:start -->.*?<!-- inline-css:end -->", lambda m: block, h, flags=re.S)
else:
    h = re.sub(r'    <link rel="stylesheet" href="/assets/fonts.css">\n    <link rel="stylesheet" href="/assets/home.css">\n    <link rel="stylesheet" href="/assets/upgrade.css[^"]*">\n', lambda m: block + "\n", h, count=1)
    h = h.replace('    <link rel="stylesheet" href="/assets/chatbot-widget.css" />\n', "")
page.write_text(h)
print("inlined", len(css), "bytes")
