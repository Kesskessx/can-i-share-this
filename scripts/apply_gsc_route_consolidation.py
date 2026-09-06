#!/usr/bin/env python3
"""Consolidate overlapping SEO routes before the canonical registry is applied."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"

CONSOLIDATIONS = {
    "/how-to-check-a-link-without-clicking-it": "/how-to-check-if-a-link-is-safe",
}


def main() -> None:
    registry = json.loads(MANIFEST.read_text(encoding="utf-8"))
    routes = list(registry.get("routes", []))
    redirects = list(registry.get("redirects", []))

    active_paths = {route.get("path") for route in routes if route.get("status") == "active"}

    for source, destination in CONSOLIDATIONS.items():
        if destination not in active_paths:
            raise RuntimeError(f"SEO consolidation target is not active: {destination}")

        routes = [route for route in routes if route.get("path") != source]
        redirects = [item for item in redirects if item.get("from") != source]
        redirects.append({
            "from": source,
            "to": destination,
            "statusCode": 308,
            "reason": "Consolidate overlapping manual link-safety intent after GSC review",
        })
        print(f"SEO route consolidated {source} -> {destination}")

    registry["routes"] = routes
    registry["redirects"] = redirects
    MANIFEST.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
