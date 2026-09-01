#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
manifest = json.loads((ROOT / "seo" / "SEO_ROUTE_MANIFEST.json").read_text(encoding="utf-8"))

for route in manifest["routes"]:
    page = DIST / f"{route['path'].lstrip('/').rstrip('/')}.html"
    if not page.is_file():
        raise SystemExit(f"Missing generated page: {route['path']}")
    html = page.read_text(encoding="utf-8")
    old = '<meta name="robots" content="noindex,follow">'
    if old not in html:
        raise SystemExit(f"Expected preview robots tag missing: {route['path']}")
    page.write_text(html.replace(old, '<meta name="robots" content="index,follow">', 1), encoding="utf-8")

print(f"Enabled indexing for {len(manifest['routes'])} priority SEO pages")
