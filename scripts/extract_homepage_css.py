#!/usr/bin/env python3
"""Externalize non-critical homepage CSS after all homepage transforms.

The first inline <style> block is kept as critical CSS. Every later inline
<style> block is concatenated in its original order into one content-hashed
stylesheet. JavaScript is intentionally untouched because the homepage has
many parser-order-dependent enhancement scripts.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INDEX = DIST / "index.html"
ASSETS = DIST / "assets"
STYLE_RE = re.compile(r"<style(?P<attrs>[^>]*)>(?P<body>[\s\S]*?)</style>", re.I)


def label(attrs: str, index: int) -> str:
    match = re.search(r"\bid=[\"']([^\"']+)", attrs, re.I)
    return match.group(1) if match else f"inline-style-{index}"


def main() -> None:
    if not INDEX.is_file():
        raise RuntimeError("dist/index.html is missing")

    source = INDEX.read_text(encoding="utf-8")
    matches = list(STYLE_RE.finditer(source))
    if len(matches) < 10:
        raise RuntimeError(f"Expected many homepage style blocks, found {len(matches)}")

    # Keep the first/base stylesheet inline so the initial shell can paint
    # without waiting for an extra request.
    extracted = matches[1:]
    parts: list[str] = []
    for index, match in enumerate(extracted, start=1):
        attrs = match.group("attrs")
        body = match.group("body").strip()
        parts.append(f"/* {label(attrs, index)} */\n{body}\n")

    css = "\n".join(parts).strip() + "\n"
    if len(css) < 100_000:
        raise RuntimeError(f"Extracted CSS unexpectedly small: {len(css)} bytes")

    digest = hashlib.sha256(css.encode("utf-8")).hexdigest()[:12]
    ASSETS.mkdir(parents=True, exist_ok=True)
    for old in ASSETS.glob("home-overrides-*.css"):
        old.unlink()
    asset = ASSETS / f"home-overrides-{digest}.css"
    asset.write_text(css, encoding="utf-8")

    href = f"/assets/{asset.name}"
    link = f'<link rel="stylesheet" href="{href}" data-home-overrides="true">'

    pieces: list[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        pieces.append(source[cursor:match.start()])
        if index == 0:
            pieces.append(match.group(0))
        elif index == 1:
            pieces.append(link)
        cursor = match.end()
    pieces.append(source[cursor:])
    output = "".join(pieces)

    if link not in output:
        raise RuntimeError("Homepage stylesheet link was not inserted")
    if len(STYLE_RE.findall(output)) != 1:
        raise RuntimeError("Expected exactly one critical inline style after extraction")
    if len(output) >= len(source) - 100_000:
        raise RuntimeError("Homepage HTML did not shrink by the expected amount")

    INDEX.write_text(output, encoding="utf-8")
    print(
        f"Homepage CSS externalized: {len(source)} -> {len(output)} HTML bytes; "
        f"{len(css)} CSS bytes in {asset.name}"
    )


if __name__ == "__main__":
    main()
