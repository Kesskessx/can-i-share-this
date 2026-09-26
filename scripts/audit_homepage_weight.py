#!/usr/bin/env python3
"""Fail the build if homepage asset extraction regresses."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INDEX = DIST / "index.html"

def main() -> None:
    if not INDEX.is_file():
        raise SystemExit("Homepage audit failed: dist/index.html missing")

    doc = INDEX.read_text(encoding="utf-8")
    failures: list[str] = []

    if len(doc) > 320_000:
        failures.append(f"homepage HTML too large: {len(doc)} bytes")

    styles = re.findall(r"<style\b[^>]*>[\s\S]*?</style>", doc, re.I)
    if len(styles) != 1:
        failures.append(f"expected exactly one critical inline style, found {len(styles)}")

    match = re.search(
        r'<link\s+rel=["\']stylesheet["\']\s+href=["\'](/assets/home-overrides-[a-f0-9]{12}\.css)["\'][^>]*data-home-overrides=["\']true["\'][^>]*>',
        doc,
        re.I,
    )
    if not match:
        failures.append("hashed homepage override stylesheet link missing")
    else:
        asset = DIST / match.group(1).lstrip("/")
        if not asset.is_file():
            failures.append(f"referenced stylesheet missing: {asset}")
        else:
            css = asset.read_text(encoding="utf-8")
            if len(css) < 100_000:
                failures.append(f"externalized stylesheet unexpectedly small: {len(css)} bytes")
            for required in (
                "cist-link-first-home-v1-style",
                "cist-mobile-layout-fix-v1-style",
                "cist-mega-scanner-v2-style",
            ):
                if required not in css:
                    failures.append(f"externalized stylesheet missing marker: {required}")

    for required in (
        'id="scan-form"',
        'id="url"',
        'id="analyze"',
        '<link rel="canonical" href="https://canisharethis.com/">',
        '<meta name="robots" content="index,follow">',
        '/_vercel/insights/script.js',
    ):
        if required not in doc:
            failures.append(f"homepage lost required marker: {required}")

    executable_inline = [
        m for m in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>[\s\S]*?)</script>", doc, re.I)
        if "application/ld+json" not in m.group("attrs").lower()
        and "src=" not in m.group("attrs").lower()
        and m.group("body").strip()
    ]
    if len(executable_inline) < 40:
        failures.append(f"homepage executable scripts changed unexpectedly: {len(executable_inline)}")

    if failures:
        raise SystemExit("Homepage performance audit failed:\n- " + "\n- ".join(failures))

    print(f"Homepage performance audit passed: {len(doc)} HTML bytes, 1 critical inline style")


if __name__ == "__main__":
    main()
