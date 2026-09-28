# AI-powered chatbot backend — setup

This is a small Cloudflare Worker that lets your site's chatbot give natural,
conversational answers using Claude, instead of just keyword matching. It
holds your Anthropic API key safely on the server side — the key is never
visible in your website's code or to visitors.

**Cost:** Cloudflare Workers free tier covers 100,000 requests/day — plenty
for a personal site. Anthropic API usage is pay-per-use; this uses Claude
Haiku (their cheapest, fastest model) with short answers, so realistic cost
for a personal-site chatbot is well under $1/month unless you get very heavy
traffic.

## What you need

1. A free Cloudflare account: https://dash.cloudflare.com/sign-up
2. An Anthropic API key: https://console.anthropic.com/ → **Settings → API Keys → Create Key**
   (you'll need to add a payment method there for pay-per-use billing)
3. Node.js installed on your computer (to run the deploy command)

## Steps

### 1. Install Wrangler (Cloudflare's CLI) and log in

```bash
npm install -g wrangler
wrangler login
```

This opens a browser window to connect Wrangler to your Cloudflare account.

### 2. Deploy the Worker

From this `worker/` folder:

```bash
wrangler deploy
```

This publishes the Worker and prints a URL like:
`https://roshantrivedi-chatbot.<your-subdomain>.workers.dev`

**Copy that URL** — you'll need it in step 4.

### 3. Add your Anthropic API key as a secret

```bash
wrangler secret put ANTHROPIC_API_KEY
```

Paste your API key (from console.anthropic.com) when prompted. This stores
it encrypted on Cloudflare's side — it's never written to any file, never
committed to git, and never sent to the browser.

### 4. Point the site's chatbot at your Worker

Open `assets/chatbot-widget.js` in the site repo and find this line near the
top:

```js
var AI_ENDPOINT = ""; // e.g. "https://roshantrivedi-chatbot.yoursubdomain.workers.dev"
```

Paste in the URL from step 2, commit, and push. Once that's live, the
chatbot will call your Worker for natural AI answers, and will automatically
fall back to the existing free keyword-search bot if the Worker is ever
unreachable — so the site never breaks even if the Worker or your Anthropic
account has an issue.

## Updating what the bot knows

The Worker's knowledge is a snapshot of `assets/chatbot-data.js` baked into
`worker.js` as a constant (`SYSTEM_PROMPT`). When you add or edit content in
`chatbot-data.js`, regenerate the Worker's knowledge section and redeploy
with `wrangler deploy` — ask Claude to do this for you, or run:

```bash
node -e "
global.window = {};
require('../assets/chatbot-data.js');
console.log(window.SITE_QA.map(e => '### ' + e.title + ' (' + e.url + ')\n' + e.answer).join('\n\n'));
"
```

and paste the output into the `KNOWLEDGE:` section of `worker.js`, then
`wrangler deploy` again.

## Enforcing the site's security headers

`_headers` at the repo root lists HSTS, CSP and a few other security headers
— but GitHub Pages (which serves `roshantrivedi.co.in` directly; the site
isn't currently proxied through Cloudflare) has no concept of a `_headers`
file and silently ignores it. None of those headers reach a visitor's
browser today. To make them real, put Cloudflare in front of GitHub Pages
and add a Transform Rule:

### 1. Add the zone to Cloudflare, if it isn't already

In the Cloudflare dashboard, **Add a site** → `roshantrivedi.co.in` → free
plan. Cloudflare scans the domain's existing DNS records (it should find the
GitHub Pages `A`/`CNAME` records already in place) and then gives you two
nameservers to use instead, something like `xxx.ns.cloudflare.com` and
`yyy.ns.cloudflare.com` — copy those.

If the domain is registered through **GoDaddy**: sign in at godaddy.com →
**My Products** → find `roshantrivedi.co.in` → **DNS** (or the **⋮** menu
next to it) → **Nameservers** → **Change** → **Enter my own nameservers
(Advanced)** → replace whatever's there with the two Cloudflare gave you →
**Save**. GoDaddy will warn that this hands DNS management to someone else —
that's expected, it's the whole point. Propagation is usually under a few
hours, sometimes up to 24. Cloudflare emails you once it detects the switch
and the zone goes active; until then the site keeps working exactly as it
does now, so there's no downtime risk in making the change.

Skip this step entirely if the zone is already in Cloudflare.

### 2. Proxy the DNS records (turn the cloud orange)

**DNS** → find the records for `roshantrivedi.co.in` (apex) and `www` → click
each record's cloud icon so it's **Proxied** (orange), not **DNS only**
(grey). Traffic now flows through Cloudflare before it reaches GitHub Pages,
which is what makes a Transform Rule possible — this step alone changes
nothing else about how the site behaves.

### 3. Add a Modify Response Header Transform Rule

**Rules** → **Transform Rules** → **Modify Response Header** → **Create
rule**. Name it something like "Security headers". Under **When incoming
requests match…** choose **All incoming requests** (or scope it to
`roshantrivedi.co.in/*` if you'd rather be explicit). Add one **Set static**
header entry per line below, copying the value exactly from `_headers` at
the repo root so the two never drift:

| Header name | Value |
|---|---|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=(), interest-cohort=()` |
| `Cross-Origin-Opener-Policy` | `same-origin` |
| `Content-Security-Policy` | *(the full `Content-Security-Policy` line from `_headers` — long, so copy/paste it rather than retyping)* |

Save and deploy the rule. It's live immediately — check with your browser's
Network tab (or `curl -I https://roshantrivedi.co.in/`) that the response now
carries these headers.

### Keeping it in sync

`_headers`'s CSP `script-src` allows the site's own scripts by exact SHA-256
hash, one per inline `<script>` block (see the comment at the top of
`_headers`). If you ever edit the text of an inline script in `index.html` or
`case-studies/non-human-identity-at-scale/index.html`, its hash changes —
regenerate it and update both `_headers` and the Transform Rule's CSP value,
or the browser will silently block that script. Ask Claude to do this
whenever an inline script changes; it's a five-second check.

## Security notes

- The Worker only accepts requests from your site's own domains (checked via
  the `Origin` header) — it can't be used as a free API proxy by other sites.
- It only answers from the knowledge embedded in the prompt and is
  instructed to ignore any attempt to override its instructions via a
  visitor's message.
- Messages are capped in length and only a short recent history is kept per
  request, to bound cost per query.
