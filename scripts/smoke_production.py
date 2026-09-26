#!/usr/bin/env python3
"""Production smoke checks for the public site.

Designed for GitHub Actions after a successful Vercel deployment. Uses only
the Python standard library and performs read-only/non-mutating requests.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("SMOKE_BASE_URL", "https://canisharethis.com").rstrip("/")
TIMEOUT = float(os.getenv("SMOKE_TIMEOUT_SECONDS", "12"))

PAGES = {
    "/": [
        'id="scan-form"',
        '<link rel="canonical" href="https://canisharethis.com/">',
        '<meta name="robots" content="index,follow">',
    ],
    "/google-drive-link-not-working": [
        '<link rel="canonical" href="https://canisharethis.com/google-drive-link-not-working">',
        '<meta name="robots" content="index,follow">',
    ],
    "/google-drive-link-checker": [
        '<link rel="canonical" href="https://canisharethis.com/google-drive-link-checker">',
        '<meta name="robots" content="index,follow">',
    ],
    "/is-my-google-drive-link-public": [
        '<link rel="canonical" href="https://canisharethis.com/is-my-google-drive-link-public">',
        '<meta name="robots" content="index,follow">',
    ],
    "/download-link-checker": [
        '<link rel="canonical" href="https://canisharethis.com/download-link-checker">',
        '<meta name="robots" content="index,follow">',
    ],
}


def fetch(path: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(
        BASE + path,
        headers={
            "User-Agent": "CanIShareThis-Smoke/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read()
    except urllib.error.HTTPError as error:
        return error.code, {k.lower(): v for k, v in error.headers.items()}, error.read()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []

    for path, markers in PAGES.items():
        status, headers, body = fetch(path)
        text = body.decode("utf-8", "replace")
        require(status == 200, f"{path}: expected 200, got {status}", failures)
        require("text/html" in headers.get("content-type", ""), f"{path}: unexpected content-type", failures)
        for marker in markers:
            require(marker in text, f"{path}: missing marker {marker}", failures)

    status, headers, body = fetch("/api/analyze")
    analyze_text = body.decode("utf-8", "replace")
    require(status == 405, f"/api/analyze GET: expected 405, got {status}", failures)
    require("application/json" in headers.get("content-type", ""), "/api/analyze: expected JSON", failures)
    try:
        analyze_json = json.loads(analyze_text)
        require(analyze_json.get("error") == "Method not allowed", "/api/analyze: wrong 405 payload", failures)
    except json.JSONDecodeError:
        failures.append("/api/analyze: invalid JSON response")

    status, headers, body = fetch("/api/counter")
    require(status == 200, f"/api/counter: expected 200, got {status}", failures)
    require("application/json" in headers.get("content-type", ""), "/api/counter: expected JSON", failures)
    try:
        counter = json.loads(body.decode("utf-8", "replace"))
        require(isinstance(counter.get("total"), (int, float)), "/api/counter: total missing", failures)
        require(isinstance(counter.get("byType"), dict), "/api/counter: byType missing", failures)
    except json.JSONDecodeError:
        failures.append("/api/counter: invalid JSON response")

    status, headers, body = fetch("/robots.txt")
    robots = body.decode("utf-8", "replace")
    require(status == 200, f"/robots.txt: expected 200, got {status}", failures)
    require("text/plain" in headers.get("content-type", ""), "/robots.txt: unexpected content-type", failures)
    require("Sitemap: https://canisharethis.com/sitemap.xml" in robots, "/robots.txt: sitemap directive missing", failures)

    status, headers, body = fetch("/sitemap.xml")
    sitemap = body.decode("utf-8", "replace")
    require(status == 200, f"/sitemap.xml: expected 200, got {status}", failures)
    require("xml" in headers.get("content-type", ""), "/sitemap.xml: unexpected content-type", failures)
    for path in PAGES:
        url = "https://canisharethis.com/" if path == "/" else f"https://canisharethis.com{path}"
        require(url in sitemap, f"/sitemap.xml: missing {url}", failures)
    require("<lastmod>" in sitemap, "/sitemap.xml: no lastmod values found", failures)

    if failures:
        print("Production smoke checks FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Production smoke checks passed against {BASE}: {len(PAGES)} pages + APIs + robots + sitemap")


if __name__ == "__main__":
    main()
