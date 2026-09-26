#!/usr/bin/env python3
"""Add trustworthy <lastmod> values to sitemap entries.

A date is emitted only when the corresponding built HTML already contains an
explicit schema.org dateModified value. Routes without an explicit date keep
only their <loc>, avoiding synthetic "updated today" dates.
"""

from __future__ import annotations

import datetime as dt
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITEMAP = DIST / "sitemap.xml"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
DATE_RE = re.compile(r'["\']dateModified["\']\s*:\s*["\'](\d{4}-\d{2}-\d{2})["\']', re.I)


def route_file(path: str) -> Path | None:
    clean = path.strip("/")
    candidates = [DIST / "index.html"] if not clean else [
        DIST / f"{clean}.html",
        DIST / clean / "index.html",
        DIST / clean,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def explicit_modified_date(path: Path) -> str | None:
    doc = path.read_text(encoding="utf-8")
    dates = sorted(set(DATE_RE.findall(doc)))
    if not dates:
        return None

    today = dt.date.today()
    parsed: list[tuple[dt.date, str]] = []
    for value in dates:
        try:
            day = dt.date.fromisoformat(value)
        except ValueError as exc:
            raise RuntimeError(f"{path}: invalid dateModified {value!r}") from exc
        if day > today:
            raise RuntimeError(f"{path}: future dateModified {value!r}")
        parsed.append((day, value))

    return max(parsed)[1]


def main() -> None:
    if not SITEMAP.is_file():
        raise RuntimeError("dist/sitemap.xml is missing")

    ET.register_namespace("", NS)
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    if root.tag != f"{{{NS}}}urlset":
        raise RuntimeError(f"Unexpected sitemap root: {root.tag}")

    urls = root.findall(f"{{{NS}}}url")
    if not urls:
        raise RuntimeError("Sitemap contains no URLs")

    added = 0
    unresolved = 0
    for item in urls:
        loc = item.find(f"{{{NS}}}loc")
        if loc is None or not (loc.text or "").strip():
            raise RuntimeError("Sitemap URL missing <loc>")

        parsed = urlparse((loc.text or "").strip())
        if parsed.scheme != "https" or parsed.netloc != "canisharethis.com":
            raise RuntimeError(f"Unexpected sitemap host: {loc.text}")

        page = route_file(parsed.path)
        if page is None:
            unresolved += 1
            continue

        modified = explicit_modified_date(page)
        existing = item.find(f"{{{NS}}}lastmod")
        if modified:
            if existing is None:
                existing = ET.SubElement(item, f"{{{NS}}}lastmod")
            existing.text = modified
            added += 1
        elif existing is not None:
            item.remove(existing)

    if added == 0:
        raise RuntimeError("No trustworthy sitemap lastmod values were found")

    ET.indent(tree, space="  ")
    tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)
    print(f"Sitemap lastmod updated: {added}/{len(urls)} URLs; unresolved routes: {unresolved}")


if __name__ == "__main__":
    main()
