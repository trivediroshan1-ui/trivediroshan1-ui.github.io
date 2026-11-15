#!/usr/bin/env python3
"""Build the two print QR codes as SVG (for print and the web) and PNG.

Each code holds only a URL on this domain, so the page behind it can change
without reprinting, and no phone number or email is inside the code.
Error correction level M, a four-module quiet zone, black on white.

Run from the repository root:  python3 scripts/build-qr.py
Then check:                     python3 scripts/build-qr.py --check
"""
import os, sys
from reportlab.graphics.barcode import qrencoder as q

CODES = {
    "qr-site": "https://roshantrivedi.co.in/",
    "qr-contact": "https://roshantrivedi.co.in/contact/",
}
OUT = "assets/qr"
QUIET = 4


def matrix(url):
    c = q.QRCode(None, q.QRErrorCorrectLevel.M)
    c.addData(url)
    c.make()
    n = c.getModuleCount()
    return [[bool(c.isDark(r, col)) for col in range(n)] for r in range(n)]


def svg(m, label):
    n = len(m) + 2 * QUIET
    path = []
    for r, row in enumerate(m):
        for col, dark in enumerate(row):
            if dark:
                path.append(f"M{col + QUIET},{r + QUIET}h1v1h-1z")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{label}">'
        f'<rect width="{n}" height="{n}" fill="#fff"/>'
        f'<path fill="#000" d="{"".join(path)}"/></svg>\n'
    )


def png(m, path, px=1200):
    from PIL import Image
    n = len(m) + 2 * QUIET
    scale = max(1, px // n)
    img = Image.new("1", (n, n), 1)
    for r, row in enumerate(m):
        for col, dark in enumerate(row):
            if dark:
                img.putpixel((col + QUIET, r + QUIET), 0)
    img.resize((n * scale, n * scale), Image.NEAREST).save(path, optimize=True)


def check():
    import cv2
    ok = True
    for name, url in CODES.items():
        img = cv2.imread(f"{OUT}/{name}.png")
        # Read it back the way a phone would: at a few sizes, not only full size.
        reads = {cv2.QRCodeDetector().detectAndDecode(
            cv2.resize(img, (s, s), interpolation=cv2.INTER_AREA))[0] for s in (240, 480, 720)}
        got = url if reads == {url} else ",".join(sorted(reads))
        status = "ok" if got == url else f"MISMATCH (read {got!r})"
        ok &= got == url
        print(f"{name}.png -> {url}: {status}")
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    os.makedirs(OUT, exist_ok=True)
    for name, url in CODES.items():
        m = matrix(url)
        with open(f"{OUT}/{name}.svg", "w") as f:
            f.write(svg(m, f"QR code for {url}"))
        png(m, f"{OUT}/{name}.png")
        print(f"{name}: {url} ({len(m)}x{len(m)} modules)")
