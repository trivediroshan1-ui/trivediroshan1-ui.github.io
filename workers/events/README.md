# Event counter (AN-01)

This is a small Cloudflare Worker that counts six named actions on the site. The page side is `assets/events.js`, which stays **off** until the Worker is live.

## What it counts

| Event | Parameter | When it is sent |
|---|---|---|
| `download` | File path | A link to a PDF, CSV, JSON, ZIP, vCard, TXT or QR file is clicked |
| `lab_use` | Lab slug | The first button pressed inside a lab page |
| `subscribe` | Page path | The newsletter form is submitted |
| `video_play` | Video file name | A video starts, once per video |
| `read_75` | Page path | A reader reaches 75% of an article or case study |
| `search_none` | Length bucket: `1-3`, `4-8` or `9+` | A site search finds nothing. Only the length is sent, never the words |

**What it never collects:**
- an IP address;
- a user agent;
- a cookie, or anything stored in the browser;
- a user ID;
- search words.

**Do Not Track:** the script sends nothing if the browser has Do Not Track or Global Privacy Control turned on.

**Retention:** Workers Analytics Engine keeps data for a limited period set by Cloudflare. Check the current limit in Cloudflare's documentation before relying on it [verify].

## Turning it on (owner only)

This deploys code to your Cloudflare account, so only you can do it.

1. **Check the free plan.** In the Cloudflare dashboard, confirm that Workers Analytics Engine is available on your plan [verify: plan limits change].
2. **Deploy the Worker.** From this folder, run `npx wrangler login` and then `npx wrangler deploy`. This creates the `rt-events` Worker on the route `roshantrivedi.co.in/e` only.
3. **Test the route.** Run `curl -i -X POST https://roshantrivedi.co.in/e -d '{}'`. You should get `HTTP/2 204`.
4. **Switch the page side on.** In `assets/events.js`, set `ON = true`, bump the `events.js?v=` stamp, and open a PR.
5. **Confirm the privacy page.** The "Event counts" section on `/privacy/` already describes this. Check it still matches before you merge.

**To turn it off:** set `ON = false`, or delete the route in Cloudflare. The site works the same either way.

## Reading the counts

Use the Analytics Engine SQL API with an API token that can only read Account Analytics. Example query for the top 10 downloads in the last 30 days:

```sql
SELECT blob2 AS file, SUM(_sample_interval) AS count
FROM rt_events
WHERE blob1 = 'download' AND timestamp > NOW() - INTERVAL '30' DAY
GROUP BY file ORDER BY count DESC LIMIT 10
```

**Keep the token out of the repository.** Store it in your password manager.
