#!/usr/bin/env python3
"""Fail the Vercel build if the highest-value GSC pages regress."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"

EXPECTED = {
    "/google-drive-link-not-working": "Google Drive Link Not Working? Fix Access & Permission Problems",
    "/google-drive-link-checker": "Google Drive Link Checker — Test Access Before Sharing",
    "/is-my-google-drive-link-public": "Is My Google Drive Link Public? Check Sharing Access",
    "/download-link-checker": "Download Link Checker — Check a File URL Before Opening",
}

REQUIRED_LINKS = {
    "/google-drive-link-checker": {
        "/google-drive-link-not-working",
        "/is-my-google-drive-link-public",
        "/google-drive-permission-checker",
        "/check-google-drive-link-without-signing-in",
    },
    "/google-drive-link-not-working": {
        "/google-drive-link-checker",
        "/is-my-google-drive-link-public",
        "/google-drive-permission-checker",
        "/check-google-drive-link-without-signing-in",
    },
    "/is-my-google-drive-link-public": {
        "/google-drive-link-checker",
        "/google-drive-link-not-working",
        "/google-drive-permission-checker",
        "/google-drive-anyone-with-the-link-vs-restricted",
    },
}


def route_file(route: str) -> Path:
    rel = route.strip("/")
    candidates = [DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError(f"Missing priority route: {route}")


def extract(pattern: str, doc: str) -> str:
    match = re.search(pattern, doc, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip()) if match else ""


def main() -> None:
    failures: list[str] = []

    for route, expected_title in EXPECTED.items():
        path = route_file(route)
        doc = path.read_text(encoding="utf-8")

        title = extract(r"<title>(.*?)</title>", doc)
        if title != expected_title:
            failures.append(f"{route}: title mismatch: {title!r}")

        h1_count = len(re.findall(r"<h1\b", doc, re.I))
        if h1_count != 1:
            failures.append(f"{route}: expected one H1, found {h1_count}")

        canonical = extract(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', doc)
        expected_canonical = HOST + route
        if canonical != expected_canonical:
            failures.append(f"{route}: canonical mismatch: {canonical!r}")

        robots = extract(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', doc)
        normalized_robots = robots.lower().replace(" ", "")
        if "index" not in normalized_robots or "follow" not in normalized_robots or "noindex" in normalized_robots:
            failures.append(f"{route}: robots is not index,follow: {robots!r}")

        description = extract(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', doc)
        if len(description) < 70:
            failures.append(f"{route}: meta description unexpectedly short")

        for href in REQUIRED_LINKS.get(route, set()):
            if f'href="{href}"' not in doc and f"href='{href}'" not in doc:
                failures.append(f"{route}: missing internal link to {href}")

    public_doc = route_file("/is-my-google-drive-link-public").read_text(encoding="utf-8")
    if "GSC_2026_09_24_START" not in public_doc:
        failures.append("/is-my-google-drive-link-public: GSC answer block missing")

    drive_doc = route_file("/google-drive-link-not-working").read_text(encoding="utf-8")
    if "GSC_2026_09_24_START" not in drive_doc:
        failures.append("/google-drive-link-not-working: GSC troubleshooting block missing")

    if failures:
        raise SystemExit("GSC priority audit failed:\n- " + "\n- ".join(failures))

    print(f"GSC priority audit passed for {len(EXPECTED)} routes")


if __name__ == "__main__":
    main()
