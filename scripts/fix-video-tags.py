#!/usr/bin/env python3
"""Give every <video> on the site a size, a name and a VideoObject entry.

- width and height from the file, so the player keeps its space while the page loads
- aria-label from the caption next to it, when the video has none
- a VideoObject in a separate ld+json block (id="ld-video") for videos the page does not describe yet

Sizes and lengths are kept in data/videos.json; ffprobe refreshes them when it is installed.
Run after any page builder that writes a video:  python3 scripts/fix-video-tags.py   (--check in CI)
"""
import html, json, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://roshantrivedi.co.in"
DATA = ROOT / "data" / "videos.json"
SKIP = ("agent-skills/", "_site/", "node_modules/")
check = "--check" in sys.argv
meta = json.loads(DATA.read_text()) if DATA.exists() else {}


def probe(src):
    f = ROOT / src.lstrip("/")
    if src in meta or not f.exists() or not shutil.which("ffprobe"):
        return meta.get(src)
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(f)], capture_output=True, text=True).stdout
    j = json.loads(out)
    date = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", src.lstrip("/")],
                          cwd=ROOT, capture_output=True, text=True).stdout.split()
    meta[src] = {"width": j["streams"][0]["width"], "height": j["streams"][0]["height"],
                 "seconds": round(float(j["format"]["duration"])), "uploaded": date[-1] if date else None}
    return meta[src]


def iso(sec):
    m, s = divmod(int(sec), 60)
    return "PT" + (f"{m}M" if m else "") + (f"{s}S" if s or not m else "")


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


problems, changed = [], []
for p in sorted(ROOT.rglob("index.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(SKIP):
        continue
    t = p.read_text(encoding="utf-8")
    if "<video" not in t:
        continue
    url = "/" + rel[: -len("index.html")]
    new, ld = t, []
    # what the page's other structured data already describes (ld-video is rebuilt each run)
    described = " ".join(b for b in re.findall(r'<script type="application/ld\+json"(?! id="ld-video")[^>]*>(.*?)</script>', t, re.S)
                         if '"VideoObject"' in b)
    for m in re.finditer(r"<video\b[^>]*>.*?</video>(?:\s*<figcaption[^>]*>(.*?)</figcaption>)?", t, re.S):
        tag = re.match(r"<video\b[^>]*>", m.group(0)).group(0)
        src = (re.search(r'<source src="([^"]+)"', m.group(0)) or re.search(r'\bsrc="([^"]+)"', tag))
        if not src:
            continue
        src = src.group(1).split("?")[0]
        info = probe(src)
        cap = plain(m.group(1) or "")
        cap = re.sub(r"\s*Download.*$", "", cap).rstrip(" .,:") or plain(re.search(r'poster="([^"]+)"', tag).group(1) if 'poster="' in tag else src)
        fixed = tag
        if info and "width=" not in tag:
            fixed = fixed.replace("<video", f'<video width="{info["width"]}" height="{info["height"]}"', 1)
        if "aria-label=" not in tag:
            fixed = fixed.replace("<video", f'<video aria-label="{html.escape(cap, quote=True)}"', 1)
        if fixed != tag:
            if check:
                problems.append(f"{rel}: {src} needs " + ", ".join(k for k in ("width", "aria-label") if k + "=" not in tag))
            new = new.replace(tag, fixed, 1)
        if info and (SITE + src) not in described:
            label = re.search(r'aria-label="([^"]+)"', fixed).group(1)
            poster = re.search(r'poster="([^"]+)"', tag)
            ld.append({"@type": "VideoObject", "name": html.unescape(label)[:110], "description": html.unescape(label),
                       "thumbnailUrl": SITE + poster.group(1) if poster else None, "uploadDate": info.get("uploaded"),
                       "duration": iso(info["seconds"]), "contentUrl": SITE + src, "embedUrl": SITE + url,
                       "isAccessibleForFree": True, "author": {"@type": "Person", "name": "Roshan Trivedi", "url": SITE + "/about/"}})
            described += SITE + src
    if ld:
        block = '<script type="application/ld+json" id="ld-video">' + json.dumps(
            {"@context": "https://schema.org", "@graph": [{k: v for k, v in d.items() if v is not None} for d in ld]},
            ensure_ascii=False) + "</script>"
        if 'id="ld-video"' in new:
            new = re.sub(r'<script type="application/ld\+json" id="ld-video">.*?</script>', lambda _: block, new, flags=re.S)
        else:
            new = new.replace("</head>", "  " + block + "\n  </head>", 1)
        if check and new != t:
            problems.append(f"{rel}: no VideoObject for " + ", ".join(d["contentUrl"] for d in ld))
    if new != t and not check:
        p.write_text(new, encoding="utf-8")
        changed.append(rel)

if not check:
    DATA.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print("updated:", *changed, sep="\n  ") if changed else print("all videos already have a size, a name and a VideoObject")
else:
    print(*problems, sep="\n") if problems else print("videos ok")
    sys.exit(1 if problems else 0)
