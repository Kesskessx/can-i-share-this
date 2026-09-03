#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"
HOST = "https://canisharethis.com"
SCRIPT_RE = re.compile(r'\s*<script id="cist-breadcrumb-schema" type="application/ld\+json">.*?</script>', re.S | re.I)

PREFERRED_HUBS = {
    "universal-safety": "/supported-checks",
    "trust-methodology": "/methodology",
    "scam-prevention": "/scam-prevention",
    "link-safety": "/safe-link-checker",
    "google-drive": "/google-drive-link-checker",
    "dropbox": "/dropbox-link-checker",
    "email-safety": "/email-safety-checker"
}


def label(route: dict) -> str:
    return route.get("breadcrumbLabel") or route.get("primaryKeyword") or route["path"].strip("/").replace("-", " ").title()


def route_file(path: str) -> Path:
    return DIST / ("index.html" if path == "/" else f'{path.lstrip("/")}.html')


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    active = [r for r in manifest["routes"] if r.get("status") == "active" and r.get("index")]
    by_path = {r["path"]: r for r in active}
    changed = 0

    for route in active:
        if route["path"] == "/":
            continue
        target = route_file(route["path"])
        if not target.is_file():
            raise RuntimeError(f'Missing generated page for breadcrumb schema: {route["path"]}')

        items = [
            {"@type":"ListItem","position":1,"name":"Can I Share This?","item":HOST + "/"}
        ]
        hub_path = PREFERRED_HUBS.get(route.get("cluster"))
        if hub_path and hub_path != route["path"] and hub_path in by_path:
            items.append({"@type":"ListItem","position":2,"name":label(by_path[hub_path]),"item":HOST + hub_path})
        items.append({"@type":"ListItem","position":len(items)+1,"name":label(route),"item":HOST + route["path"]})

        payload = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items}
        script = '<script id="cist-breadcrumb-schema" type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + '</script>'

        source = target.read_text(encoding="utf-8")
        source = SCRIPT_RE.sub("", source)
        if not re.search(r'</head>', source, flags=re.I):
            raise RuntimeError(f'No closing head tag on {route["path"]}')
        source = re.sub(r'</head>', script + '\n</head>', source, count=1, flags=re.I)
        target.write_text(source, encoding="utf-8")
        changed += 1

    print(f'Applied BreadcrumbList schema to {changed} indexed pages')


if __name__ == "__main__":
    main()
