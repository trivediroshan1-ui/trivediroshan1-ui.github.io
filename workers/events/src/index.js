// Event counter for roshantrivedi.co.in, as a Cloudflare Worker.
//
// Accepts POST /e with a small JSON body from assets/events.js and writes one
// data point to Workers Analytics Engine: event name, one short parameter and
// the page path. It stores no IP address, no user agent, no cookie and no ID.
// Anything unexpected is dropped quietly with a 204, so the page never waits.

const EVENTS = new Set(["download", "lab_use", "subscribe", "video_play", "read_75", "search_none"]);
const SAFE = /^[A-Za-z0-9._\/+-]{0,80}$/;
const ORIGIN = "https://roshantrivedi.co.in";

export default {
  async fetch(request, env) {
    const ok = new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
    if (request.method !== "POST") return ok;

    // Same-site only: browsers attach our Origin to a beacon from our pages.
    // A request with no Origin (a script, curl) is not counted.
    if (request.headers.get("Origin") !== ORIGIN) return ok;

    const len = Number(request.headers.get("Content-Length") || 0);
    if (len > 512) return ok;

    let body;
    try { body = JSON.parse(await request.text()); } catch { return ok; }
    if (!body || typeof body !== "object") return ok;

    const e = String(body.e || "");
    const p = String(body.p || "");
    const path = String(body.path || "");
    if (!EVENTS.has(e) || !SAFE.test(p) || !path.startsWith("/") || !SAFE.test(path)) return ok;

    env.EVENTS.writeDataPoint({ blobs: [e, p, path], doubles: [1], indexes: [e] });
    return ok;
  },
};
