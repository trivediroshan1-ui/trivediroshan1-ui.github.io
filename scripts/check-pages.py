#!/usr/bin/env python3
"""Page checks in a real browser (ENG-04): layout, readability, tap targets, contrast, layout shift,
script errors and basic HTML. Fails only on issues that are not in the baseline, so old issues do
not block a pull request but new ones do.

    python3 scripts/check-pages.py                    # every page in sitemap.xml
    python3 scripts/check-pages.py /about/ /labs/     # only these
    python3 scripts/check-pages.py --changed origin/main   # pages whose files changed since that ref
    python3 scripts/check-pages.py --update-baseline  # accept today's issues as the baseline

Serves the repository with Python's own web server, so it checks the static pages. Blog posts are
built by Jekyll and are not checked here. Needs Playwright with Chromium.

What counts as an issue (each a short, stable signature, so the baseline can match it):
  overflow@W      the page scrolls sideways at width W (320, 390 or 1280 px)
  small-text      visible text under 12 px (not in SVG diagrams)
                  (every check runs at all three widths, so phone-only problems are caught)
  tap-target      a control smaller than 24 x 24 px (WCAG 2.2 AA 2.5.8), links inside sentences excepted
  light contrast  the same contrast check with the light theme switched on (390 px)
  contrast        text below 4.5:1 (3:1 for large text) on a plain background; text over images or
                  gradients is skipped, because it cannot be measured this way
  cls             layout shift over 0.1 in the first two seconds. Reported, never failing: it depends on
                  the machine's speed and font loading, so it differs between a laptop and CI.
  js-error        an uncaught script error
  dup-id, img-alt, no-name, no-label   basic HTML: repeated id, image with no alt, button or link
                  with no name, form field with no label
"""
import json, pathlib, re, subprocess, sys, time
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "data" / "page-check-baseline.json"
PORT = 8790
WIDTHS = (320, 390, 1280)

PROBE = r"""() => {
  const out = [], seen = new Set();
  const add = (k, el) => {
    const d = el ? (el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (el.classList && el.classList.length ? "." + [...el.classList].slice(0, 2).join(".") : "")
      + ":" + (el.textContent || el.getAttribute("aria-label") || el.getAttribute("src") || "").trim().replace(/\s+/g, " ").slice(0, 40)) : "";
    const s = k + (d ? " " + d : "");
    if (!seen.has(s)) { seen.add(s); out.push(s); }
  };
  const vis = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none" && +cs.opacity !== 0 && !el.closest("[hidden],[aria-hidden=true],.sr-only,.visually-hidden"); };
  const ownText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const lum = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
  // The page itself: its own colour, or the theme colour when the page is a gradient or picture.
  const solid = c => c && c[3] >= 1 ? c.slice(0, 3) : null;
  const meta = document.querySelector('meta[name=theme-color]');
  const hex = meta && meta.content.match(/^#([0-9a-f]{6})$/i);
  const light = document.documentElement.getAttribute("data-theme") === "light";
  const pageBg = solid(parse(getComputedStyle(document.body).backgroundColor)) || solid(parse(getComputedStyle(document.documentElement).backgroundColor))
    || (light ? [255, 255, 255] : hex ? [0, 2, 4].map(i => parseInt(hex[1].substr(i, 2), 16)) : [255, 255, 255]);
  const bgOf = el => { const layers = [];
    let b = pageBg;
    for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e), top = e === document.body || e === document.documentElement;
      if (!top && cs.backgroundImage && cs.backgroundImage !== "none") return null;
      const c = parse(cs.backgroundColor); if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; } }
    for (let i = layers.length - 1; i >= 0; i--) { const c = layers[i]; b = [0, 1, 2].map(k => c[k] * c[3] + b[k] * (1 - c[3])); }
    return b; };
  // text checks
  document.querySelectorAll("body *").forEach(el => {
    if (el.closest("svg,script,style,noscript,template,video,audio") || !ownText(el) || !vis(el)) return;
    const cs = getComputedStyle(el), fs = parseFloat(cs.fontSize);
    if (fs < 12) add("small-text", el);
    const fg = parse(cs.color), bg = bgOf(el);
    if (fg && bg && !el.closest("[data-contrast-skip]")) {
      const f = [0, 1, 2].map(k => fg[k] * fg[3] + bg[k] * (1 - fg[3]));
      const L1 = lum(f), L2 = lum(bg), ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
      const large = fs >= 24 || (fs >= 18.66 && +cs.fontWeight >= 700);
      if (ratio < (large ? 3 : 4.5)) add("contrast", el);
    }
  });
  // tap targets
  document.querySelectorAll("a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button]").forEach(el => {
    if (!vis(el) || el.closest("svg")) return;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (r.width >= 24 && r.height >= 24) return;
    if (el.tagName === "A" && cs.display === "inline") {
      const p = el.parentElement; if (p && (p.textContent || "").trim().length > (el.textContent || "").trim().length + 2) return; }
    add("tap-target", el);
  });
  // basic HTML
  const ids = {}; document.querySelectorAll("[id]").forEach(e => { ids[e.id] = (ids[e.id] || 0) + 1; });
  Object.entries(ids).forEach(([k, v]) => { if (v > 1) out.push("dup-id #" + k); });
  document.querySelectorAll("img:not([alt])").forEach(e => add("img-alt", e));
  const named = e => (e.textContent || "").trim() || e.getAttribute("aria-label") || e.getAttribute("aria-labelledby") || e.getAttribute("title") || e.querySelector("img[alt]:not([alt='']),svg title,[aria-label]");
  document.querySelectorAll("a[href],button").forEach(e => { if (!named(e) && !e.closest("[aria-hidden=true]")) add("no-name", e); });
  document.querySelectorAll("input:not([type=hidden]):not([type=submit]):not([type=button]),select,textarea").forEach(e => {
    if (e.labels && e.labels.length) return; if (e.getAttribute("aria-label") || e.getAttribute("aria-labelledby") || e.getAttribute("title")) return; add("no-label", e); });
  return out;
}"""


def pages_from_sitemap():
    sm = (ROOT / "sitemap.xml").read_text()
    out = []
    for u in re.findall(r"<loc>https://roshantrivedi\.co\.in([^<]*)</loc>", sm):
        if u.endswith("/") and (ROOT / u.strip("/") / "index.html").exists() or u == "/":
            out.append(u)
    return out


def changed_pages(ref):
    files = subprocess.run(["git", "diff", "--name-only", f"{ref}...HEAD", "--"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    if any(f.startswith("assets/") and f.endswith((".css", ".js")) for f in files):
        return pages_from_sitemap()  # a shared style or script can change any page
    out = []
    for f in files:
        if f.endswith("index.html") and (ROOT / f).exists():
            out.append("/" + f[: -len("index.html")])
    return sorted(set(out))


def check(pages):
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    found = {}
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for w in WIDTHS:
                ctx = b.new_context(viewport={"width": w, "height": 900}, reduced_motion="reduce")
                ctx.route(re.compile(r"^https?://(?!localhost)"), lambda r: r.abort())  # no outside requests
                pg = ctx.new_page()
                errs = []
                pg.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:80]))
                pg.add_init_script("window.__cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}")
                for u in pages:
                    errs.clear()
                    s = found.setdefault(u, set())
                    try:
                        pg.goto(f"http://localhost:{PORT}{u}", wait_until="load", timeout=30000)
                    except Exception as e:
                        s.add("load-failed"); continue
                    pg.wait_for_timeout(2000 if w == 1280 else 600)
                    if pg.evaluate("document.documentElement.scrollWidth - innerWidth") > 1:
                        s.add(f"overflow@{w}")
                    if w == 1280 and pg.evaluate("window.__cls") > 0.1:
                        s.add("cls")
                    s.update(pg.evaluate(PROBE))  # every check at every width: phone-only problems count too
                    s.update("js-error " + e for e in errs)
                ctx.close()
            # Light theme, phone width: contrast only, since layout does not change with the theme.
            ctx = b.new_context(viewport={"width": 390, "height": 900}, reduced_motion="reduce", color_scheme="light")
            ctx.route(re.compile(r"^https?://(?!localhost)"), lambda r: r.abort())
            ctx.add_init_script("try{localStorage.setItem('theme','light')}catch(e){}")
            pg = ctx.new_page()
            for u in pages:
                try:
                    pg.goto(f"http://localhost:{PORT}{u}", wait_until="load", timeout=30000)
                except Exception:
                    continue
                pg.wait_for_timeout(400)
                if pg.evaluate("document.documentElement.getAttribute('data-theme')") != "light":
                    continue  # the page has no light theme
                found.setdefault(u, set()).update("light " + i for i in pg.evaluate(PROBE) if i.startswith("contrast"))
            ctx.close()
            b.close()
    finally:
        srv.terminate()
    return {u: sorted(v) for u, v in found.items()}


def main(argv):
    update = "--update-baseline" in argv
    args = [a for a in argv if a != "--update-baseline"]
    if args and args[0] == "--changed":
        pages = changed_pages(args[1] if len(args) > 1 else "origin/main")
    else:
        pages = args or pages_from_sitemap()
    if not pages:
        print("No pages to check."); return 0
    print(f"Checking {len(pages)} page(s) at {', '.join(map(str, WIDTHS))} px")
    found = check(pages)
    base = json.loads(BASE.read_text()) if BASE.exists() else {}
    if update:
        found = {u: [i for i in v if i != "cls"] for u, v in found.items()}
        base.update(found)
        BASE.write_text(json.dumps(base, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
        print("Baseline updated:", sum(len(v) for v in found.values()), "known issues on", len(found), "pages")
        return 0
    shifts = sorted(u for u, v in found.items() if "cls" in v)
    found = {u: [i for i in v if i != "cls"] for u, v in found.items()}
    base = {u: [i for i in v if i != "cls"] for u, v in base.items()}
    if shifts:
        print(f"Layout shift over 0.1 on {len(shifts)} page(s), reported only: {', '.join(shifts[:10])}" + (" ..." if len(shifts) > 10 else ""))
    new = {u: [i for i in v if i not in set(base.get(u, []))] for u, v in found.items()}
    new = {u: v for u, v in new.items() if v}
    fixed = sum(len(set(base.get(u, [])) - set(v)) for u, v in found.items())
    if fixed:
        print(f"{fixed} baseline issue(s) are gone. Run with --update-baseline to record that.")
    if not new:
        print("No new issues."); return 0
    for u, v in new.items():
        print(f"\n{u}")
        for i in v:
            print("  NEW", i)
    print(f"\n{sum(len(v) for v in new.values())} new issue(s). Fix them, or if one is intended, run with --update-baseline.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
