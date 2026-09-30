# roshantrivedi.co.in

Personal site of **Roshan Trivedi** — Identity & Security. Cybersecurity professional specialising in Identity & Access Management (IAM), Privileged Access Management (PAM), and Zero Trust architecture. Hosted on GitHub Pages at the custom domain [roshantrivedi.co.in](https://roshantrivedi.co.in).

## What's here

| Path | What it is |
|---|---|
| `index.html`, `assets/home.css`, `assets/home.js` | The homepage: plain, hand-editable HTML and CSS (no build step, no JavaScript needed to read it). Sections are in order: hero, stats, perspective, expertise, case studies, platforms, research, career, contact. The dismissible announcement banner, the Cloudflare beacon and the chatbot widget sit at the bottom of `index.html`. |
| `case-studies/*/`, `secure-india-exams/` | All 19 case studies are standalone, hand-editable HTML/CSS. 5 have extra hand-built diagrams/sections (`credential-tiering-model`, `shadow-ai-discovery-gap`, `non-human-identity-at-scale`, `ai-agent-credential-sharing`, `ai-processing-tax`); the other 14 use a shared, simpler template (hero, challenge, approach, outcome, tags). |
| `_posts/`, `_layouts/post.html`, `writing/index.html` | Jekyll blog posts, built by GitHub Pages automatically (no `.nojekyll` file) and served under `/writing/:title/`. `/writing/` lists every post automatically. Plain HTML/CSS, genuinely hand-editable. |
| `assets/site.css`, `assets/polish.css` | `site.css` holds the shared styles for the 14 standard case-study pages (colours are variables at the top; each page sets its theme colour with `<body style="--c:#hex">`). The five hand-built case studies and the exam study keep their own `<style>` blocks. `polish.css` is small and additive and loads on every case-study, index and writing page: reading-progress line, previous/next cards, print view. |
| `assets/fonts.css` | Self-hosted DM Sans, Manrope and JetBrains Mono (all SIL OFL) for every standalone page. Don't link Google Fonts: the site's CSP only allows fonts from this domain, so they'd be blocked. |
| `404.html` | Custom not-found page; GitHub Pages serves it for any missing URL. |
| `favicon.svg`, `favicon.ico`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `site.webmanifest` | Site icons (RT monogram), linked from every page. |
| `Roshan_Trivedi_Resume.pdf` | Current resume, linked from the homepage. |
| `Securing_India_Exams_Master.pdf` | Full 30-page whitepaper for the exam-security proposal. |
| `og-image.png` | Social-share preview image (Open Graph / Twitter cards). |
| `CNAME` | Custom domain config for GitHub Pages (`roshantrivedi.co.in`). |
| `robots.txt`, `sitemap.xml`, `.well-known/security.txt` | Standard SEO / security metadata files. |
| `_headers` | The source of truth for the site's security headers (CSP, HSTS, etc.). GitHub Pages ignores this file; the headers are actually served by a Cloudflare Transform Rule that copies these values. If you change one, update the rule too; see `worker/README.md`. |

**The homepage used to be a compiled React app, and is now plain HTML.** Until September 2026 `index.html` loaded a minified React/Vite bundle whose source code was never committed anywhere, which made the homepage impossible to edit cleanly. It was rebuilt as ordinary HTML and CSS that looks and reads the same, and the old bundle was removed. If you ever need it back, it is in git history (commit `cf86fab` and earlier: `assets/main-DkBXTN6c.js` and `assets/main-Dilp92U4.css`).

Things that changed in the rebuild, so nothing surprises you:

- The homepage now lists all 19 case studies (the React version listed 18 and left out Credential Tiering). Each row links to its own page; the old in-page "Preview" panels were dropped because every case study has a full page.
- The nav gained a **Writing** link. On phones the menu is a plain HTML `<details>` element, so it works without JavaScript.
- Scroll-reveal animations are gone; the hero has a small load-in animation that switches off for people who prefer reduced motion.
- Case-study titles and categories on the homepage match the pages themselves. The one-line summaries are the homepage's original wording.
- Fonts come from `assets/fonts.css` like every other page.

**Editing the homepage:** open `index.html` and change the text directly. The markup is in section order, and every style is in `assets/home.css` (colours are variables at the top). `assets/home.js` is optional: it only closes the phone menu after you tap a link, and the page works without it. To add a case study to the list, copy an existing `<article class="cs-row">` block and update the number, category, title, link and summary.

## How to update this site yourself

You don't need git installed or any tooling for the genuinely hand-editable files above — everything below can be done from github.com in a browser, and GitHub Pages redeploys automatically (usually within 1–2 minutes) every time you commit to `main`.

**Edit existing text in a hand-editable file (a blog post, a case study's hand-written section, the chatbot's knowledge):**
1. Open the file in this repo.
2. Click the pencil icon (top-right of the file view) to edit.
3. Make your change and click **Commit changes** at the bottom.

**Add or replace a file (e.g. a new resume PDF, a new image):**
1. Go to **Add file → Upload files** (or visit `/upload/main` on this repo).
2. Drag in your file. If it has the *same name* as an existing file (e.g. `Roshan_Trivedi_Resume.pdf`), it will replace it on commit.
3. Add a short commit message and click **Commit changes**.

**Remove something:**
1. Open the file, click the **⋯** (or the trash icon on the file page) and choose **Delete file**.
2. Commit the deletion.

**Add a new blog post:**
Add a new file under `_posts/` named `YYYY-MM-DD-a-short-slug.md`, following the frontmatter shape of the existing post there. It'll be live at `/writing/a-short-slug/` and appear on `/writing/` automatically. Add a `description:` line to the frontmatter (it's used for the listing, search results and share previews), and add the URL to `sitemap.xml`.

**Change the homepage's layout or nav:** edit `index.html` and `assets/home.css` like any other page.

**Add a new case study:** copy `case-studies/access-recertification/index.html` as a starting template (it uses `/assets/site.css`, so you only write content), fill in the content, set `--c` on `<body>` to the theme colour, and add the new URL to `sitemap.xml`. Then add it to the homepage list and to the previous/next order: each case study has a `<nav class="pager">` near the bottom, and the neighbours of the new page need their links updated by hand.

**Check it went live:**
Watch the green checkmark under **Deployments → github-pages** on the repo's main page, then refresh [roshantrivedi.co.in](https://roshantrivedi.co.in) (hard-refresh / add `?v=2` to the URL if your browser cached the old version).

**Prefer not to touch code at all?** You can always describe the change you want in plain English to Claude and have it make the edit and commit for you the same way this update was made.

## Contact

- LinkedIn: [linkedin.com/in/roshan-trivedi](https://www.linkedin.com/in/roshan-trivedi)
- Email: trivedi.roshan1@gmail.com

## Newer pages and assets

- `/about/`, `/resume/`, `/now/`, `/ai/` are hand-written pages using `assets/site.css`. `/resume/` mirrors the public PDF minus the phone number; update it when the PDF changes.
- `/tools/tier-check/` is a client-side self-check driven by `assets/tier-check.js` (nothing is sent anywhere).
- `/case-studies/` filter chips use `assets/filter.js` and each card's `data-group`.
- `feed.xml` is the RSS feed (Jekyll builds it from `_posts`).
- Share images `assets/og-case-*.png` were generated from the case-study titles and group colours (1200x630).
