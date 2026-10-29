#!/usr/bin/env python3
"""Fail if a tracked file looks like it holds a real secret.

A small, dependency-free check for the common key shapes. It is a safety net,
not a full scanner. Known fake or documented example values are allowed below.
"""
import re, subprocess, sys

PATTERNS = {
    "AWS access key id": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b",
    "Private key block": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "Google API key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
    "Stripe live key": r"\b[sr]k_live_[0-9A-Za-z]{20,}\b",
}
ALLOWED = {"AKIAIOSFODNN7EXAMPLE"}  # AWS's documented example key
# Deliberately fake inputs for the "try the filters" demo on the lab page.
ALLOWED_FILES = {"assets/agl-try-filters.js"}
SKIP_EXT = (".png", ".webp", ".jpg", ".jpeg", ".gif", ".pdf", ".woff2", ".ico", ".mp4")

files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
bad = 0
for f in filter(None, files):
    if f in ALLOWED_FILES or f.lower().endswith(SKIP_EXT):
        continue
    try:
        text = open(f, encoding="utf-8", errors="ignore").read()
    except OSError:
        continue
    for name, pat in PATTERNS.items():
        for m in re.finditer(pat, text):
            if m.group(0) in ALLOWED:
                continue
            line = text.count("\n", 0, m.start()) + 1
            print(f"{f}:{line}: looks like a {name}")
            bad += 1
print(f"{bad} possible secrets")
sys.exit(1 if bad else 0)
