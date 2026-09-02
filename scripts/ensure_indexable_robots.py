#!/usr/bin/env python3
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = "canisharethis.com"
ROBOTS_META_RE = re.compile(r'<meta\s+[^>]*name=["\']robots["\'][^>]*>', re.I)


def target_for(url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.netloc.lower() not in {ORIGIN, f"www.{ORIGIN}"}:
        return None
    route = parsed.path or "/"
    if route == "/":
        return DIST / "index.html"
    rel = route.strip("/")
    candidates = [DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel]
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() == ".html":
            return candidate
    return None


def main() -> None:
    sitemap = DIST / "sitemap.xml"
    if not sitemap.is_file():
        raise RuntimeError("sitemap.xml not found")

    root = ET.fromstring(sitemap.read_text(encoding="utf-8"))
    changed: list[str] = []
    checked = 0

    for elem in root.iter():
        if not elem.tag.lower().endswith("loc") or not elem.text:
            continue
        target = target_for(elem.text.strip())
        if target is None:
            continue
        checked += 1
        source = target.read_text(encoding="utf-8", errors="replace")
        if ROBOTS_META_RE.search(source):
            continue
        if "</head>" not in source:
            raise RuntimeError(f"Cannot add robots meta: </head> missing in {target.relative_to(DIST)}")
        source = source.replace('</head>', '<meta name="robots" content="index,follow">\n</head>', 1)
        target.write_text(source, encoding="utf-8")
        changed.append(target.relative_to(DIST).as_posix())

    print(f"Ensured indexable robots meta on {checked} sitemap HTML pages; added to {len(changed)} page(s).")
    if changed:
        print("Robots meta added: " + ", ".join(changed))


if __name__ == "__main__":
    main()
