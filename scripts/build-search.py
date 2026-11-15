#!/usr/bin/env python3
"""The full-text search page, /search/ (STR-02). It searches assets/chatbot-index.json, the same
passages the chat uses, in the browser: nothing typed leaves the page. Run after build-chat-index.py
if the shell changes:  python3 scripts/build-search.py
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from page_shell import shell, write, ROOT

stamp = re.search(r"chatbot-index\.json\?v=([0-9a-z]+)", (ROOT / "assets/chatbot-widget.js").read_text()).group(1)
body = f'''      <section class="sec cat" aria-labelledby="sr-h">
        <div class="wrap">
          <p class="ey">Search</p>
          <h1 id="sr-h">Search every page</h1>
          <p class="lede">Searches the full text of the site: labs, case studies, books' web pages and articles. It runs in your browser, so what you type is not sent anywhere.</p>
          <form class="sr-box" role="search" action="/search/" method="get" data-search>
            <label class="sr-only" for="sr-q">Search the site</label>
            <input type="search" id="sr-q" name="q" autocomplete="off" placeholder="For example: help desk reset, token audience, break-glass">
          </form>
          <p id="sr-n" class="cat-n" role="status" aria-live="polite"></p>
          <ol class="sr-res" id="sr-res"></ol>
          <noscript><p>Search needs JavaScript. Without it, try <a href="/topics/">topics</a>, <a href="/labs/cases/">every lab case</a> or <a href="/library/">the library</a>.</p></noscript>
          <p class="cat-note">Looking for a lab case? <a href="/labs/cases/">Every case in one list</a> has filters by lab and topic.</p>
        </div>
      </section>'''
page = shell("/search/", "Search", "Search the full text of every page on roshantrivedi.co.in: labs, case studies, books and articles.",
             body, [("Home", "/"), ("Search", "/search/")],
             head_extra='    <link rel="stylesheet" href="/assets/catalogue.css?v=20261115a">\n'
                        f'    <script defer src="/assets/search.js?v=20261115a" data-index="/assets/chatbot-index.json?v={stamp}"></script>')
write("/search/", page)
