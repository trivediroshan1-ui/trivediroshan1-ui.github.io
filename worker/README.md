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

## Security notes

- The Worker only accepts requests from your site's own domains (checked via
  the `Origin` header) — it can't be used as a free API proxy by other sites.
- It only answers from the knowledge embedded in the prompt and is
  instructed to ignore any attempt to override its instructions via a
  visitor's message.
- Messages are capped in length and only a short recent history is kept per
  request, to bound cost per query.
