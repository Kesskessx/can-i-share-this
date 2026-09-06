#!/usr/bin/env python3
"""Keep final priority-page meta descriptions aligned with the SEO manifest.

Late content passes may enrich page copy, but the manifest remains the source of
truth for the canonical meta description validated by CI.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"


def route_file(route: str) -> Path | None:
    if route == "/":
        candidates = [DIST / "index.html"]
    else:
        rel = route.strip("/")
        candidates = [DIST / rel, DIST / f"{rel}.html", DIST / rel / "index.html"]
    return next((p for p in candidates if p.is_file()), None)


def replace_meta(doc: str, key: str, value: str) -> str:
    escaped = html.escape(value, quote=True)
    if key == "description":
        patterns = [
            r'(<meta\s+name=["\']description["\'][^>]*content=["\'])[^"\']*(["\'])',
            r'(<meta\s+content=["\'])[^"\']*(["\'][^>]*name=["\']description["\'])',
        ]
    else:
        patterns = [
            r'(<meta\s+property=["\']og:description["\'][^>]*content=["\'])[^"\']*(["\'])',
            r'(<meta\s+content=["\'])[^"\']*(["\'][^>]*property=["\']og:description["\'])',
        ]
    for pattern in patterns:
        updated, count = re.subn(pattern, lambda m: m.group(1) + escaped + m.group(2), doc, count=1, flags=re.I)
        if count:
            return updated
    return doc


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = 0
    for route in data.get("routes", []):
        if route.get("generator") != "priority":
            continue
        description = str(route.get("description") or "").strip()
        path = route_file(str(route.get("path") or ""))
        if not description or path is None:
            continue
        doc = path.read_text(encoding="utf-8")
        updated = replace_meta(replace_meta(doc, "description", description), "og:description", description)
        if updated != doc:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Synchronized priority meta descriptions on {changed} page(s)")


if __name__ == "__main__":
    main()
