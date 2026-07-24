# roshantrivedi.co.in

Personal site of **Roshan Trivedi** — Identity & Security. Cybersecurity professional specialising in Identity & Access Management (IAM), Privileged Access Management (PAM), and Zero Trust architecture. Hosted on GitHub Pages at the custom domain [roshantrivedi.co.in](https://roshantrivedi.co.in).

## What's here

| Path | What it is |
|---|---|
| `index.html` | The homepage — about, expertise, experience, featured work, poster, writing, contact. Single self-contained HTML file (no build step). |
| `secure-india-exams/` | A published research project — a Zero Trust reference architecture proposing how India can prevent national exam paper leaks (NEET, JEE, CUET). |
| `Roshan_Trivedi_Resume.pdf` | Current resume, linked from the homepage. |
| `Securing_India_Exams_Master.pdf` | Full 30-page whitepaper for the exam-security proposal. |
| `poster-zero-trust.png` | Original Zero Trust poster graphic, displayed in the Poster section. |
| `og-home.png`, `og-image.png` | Social-share preview images (Open Graph / Twitter cards). |
| `CNAME` | Custom domain config for GitHub Pages (`roshantrivedi.co.in`). |
| `robots.txt`, `sitemap.xml`, `.well-known/security.txt` | Standard SEO / security metadata files. |

There's no build system, framework, or dependency — every page is plain HTML/CSS. That's intentional: it keeps the site editable directly in the GitHub web UI, with no local dev environment required.

## How to update this site yourself

You don't need git installed or any tooling — everything below can be done from github.com in a browser, and GitHub Pages redeploys automatically (usually within 1–2 minutes) every time you commit to `main`.

**Edit existing text (e.g. About copy, a bio line, a link):**
1. Open the file (e.g. [`index.html`](index.html)) in this repo.
2. Click the pencil icon (top-right of the file view) to edit.
3. Make your change and click **Commit changes** at the bottom.

**Add or replace a file (e.g. a new resume PDF, a new image):**
1. Go to **Add file → Upload files** (or visit `/upload/main` on this repo).
2. Drag in your file. If it has the *same name* as an existing file (e.g. `Roshan_Trivedi_Resume.pdf`), it will replace it on commit.
3. Add a short commit message and click **Commit changes**.

**Remove something:**
1. Open the file, click the **⋯** (or the trash icon on the file page) and choose **Delete file**.
2. Commit the deletion.

**Add a new section to the homepage:**
Open `index.html`, find a `<section>` block that looks similar to what you want, copy its structure, and edit the text inside. Sections are numbered (`01`, `02`, …) in the `sec-num` span — update the numbering if you insert one in the middle.

**Check it went live:**
Watch the green checkmark under **Deployments → github-pages** on the repo's main page, then refresh [roshantrivedi.co.in](https://roshantrivedi.co.in) (hard-refresh / add `?v=2` to the URL if your browser cached the old version).

**Prefer not to touch code at all?** You can always describe the change you want in plain English to Claude and have it make the edit and commit for you the same way this update was made.

## Contact

- LinkedIn: [linkedin.com/in/roshan-trivedi](https://www.linkedin.com/in/roshan-trivedi)
- Email: trivedi.roshan1@gmail.com
