#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE_ORIGIN = "https://canisharethis.com"

HREF_RE = re.compile(r'''href\s*=\s*["']([^"']+)["']''', re.I)
LOC_RE = re.compile(r"<loc>\s*(https://canisharethis\.com[^<]*)\s*</loc>", re.I)


def normalize_route(raw: str) -> str | None:
    raw = raw.strip()
    if not raw or raw.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
        return None
    if raw.startswith(('http://', 'https://')):
        try:
            parsed = urlsplit(raw)
        except ValueError:
            return None
        if parsed.netloc.lower() not in {'canisharethis.com', 'www.canisharethis.com'}:
            return None
        path = parsed.path or '/'
    elif raw.startswith('/'):
        path = urlsplit(raw).path or '/'
    else:
        return None
    if path.startswith('/api/') or path in {'/api'}:
        return None
    if path != '/':
        path = '/' + path.strip('/')
    return path


def route_exists(route: str) -> bool:
    if route == '/':
        return (DIST / 'index.html').is_file()
    rel = route.lstrip('/')
    candidates = [
        DIST / rel,
        DIST / f'{rel}.html',
        DIST / rel / 'index.html',
    ]
    return any(p.is_file() for p in candidates)


def main() -> None:
    if not DIST.is_dir():
        raise SystemExit('dist directory not found')

    broken: dict[str, set[str]] = {}
    checked = 0

    for page in sorted(DIST.rglob('*.html')):
        text = page.read_text(encoding='utf-8', errors='replace')
        for href in HREF_RE.findall(text):
            route = normalize_route(href)
            if route is None:
                continue
            checked += 1
            if not route_exists(route):
                broken.setdefault(route, set()).add(page.relative_to(DIST).as_posix())

    sitemap = DIST / 'sitemap.xml'
    if sitemap.is_file():
        text = sitemap.read_text(encoding='utf-8', errors='replace')
        for loc in LOC_RE.findall(text):
            route = normalize_route(loc)
            if route is None:
                continue
            checked += 1
            if not route_exists(route):
                broken.setdefault(route, set()).add('sitemap.xml')

    if broken:
        print(f'Internal route audit FAILED: {len(broken)} missing route(s); {checked} references checked.')
        for route in sorted(broken):
            refs = ', '.join(sorted(broken[route]))
            print(f'BROKEN_INTERNAL_ROUTE {route} <- {refs}')
        sys.exit(1)

    print(f'Internal route audit passed: 0 missing routes; {checked} references checked.')


if __name__ == '__main__':
    main()
