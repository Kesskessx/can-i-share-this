#!/usr/bin/env python3
"""Fail closed on common SEO preview mistakes before any production merge."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.description: str | None = None
        self.canonical: str | None = None
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k.lower(): (v or "") for k, v in attrs_list}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "").strip()
        elif tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonical = attrs.get("href", "").strip()
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"].strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "h1":
            self.in_h1 = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1(self) -> str:
        return " ".join("".join(self.h1_parts).split())


def route_file(route: str) -> Path | None:
    clean = unquote(route.split("?", 1)[0].split("#", 1)[0])
    if clean == "/":
        candidates = [DIST / "index.html"]
    else:
        rel = clean.lstrip("/").rstrip("/")
        candidates = [
            DIST / rel,
            DIST / f"{rel}.html",
            DIST / rel / "index.html",
        ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser


def validate_manifest() -> list[dict]:
    if not MANIFEST.is_file():
        fail("Missing seo/SEO_ROUTE_MANIFEST.json")
        return []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"SEO route manifest is invalid JSON: {exc}")
        return []

    routes = data.get("routes")
    if not isinstance(routes, list):
        fail("Manifest routes must be a list")
        return []
    if len(routes) != 10:
        fail(f"Expected exactly 10 priority SEO routes, found {len(routes)}")

    for key in ("path", "title", "description", "h1"):
        vals = [r.get(key) for r in routes if isinstance(r, dict)]
        if len(vals) != len(set(vals)):
            fail(f"Manifest contains duplicate {key} values")

    for route in routes:
        if not isinstance(route, dict):
            fail("Manifest contains a non-object route")
            continue
        path = route.get("path", "")
        if not isinstance(path, str) or not path.startswith("/") or path == "/":
            fail(f"Invalid SEO route path: {path!r}")
        if route.get("index") is not True:
            fail(f"Priority route is not marked indexable: {path}")
        for field in ("title", "description", "h1", "cluster", "role"):
            if not str(route.get(field, "")).strip():
                fail(f"Missing {field} for {path}")

    if data.get("status") != "prepared-not-deployed":
        warn("Manifest status is no longer 'prepared-not-deployed'; verify deployment gate manually")
    return routes


def validate_build(routes: list[dict]) -> None:
    if not DIST.is_dir():
        fail("dist/ does not exist; run bash build.sh first")
        return
    if not (DIST / "index.html").is_file():
        fail("dist/index.html is missing")

    html_files = list(DIST.rglob("*.html"))
    if not html_files:
        fail("Build produced no HTML files")
        return

    parsed: dict[Path, PageParser] = {}
    for html in html_files:
        page = parse_page(html)
        parsed[html] = page
        if not page.title:
            fail(f"Missing <title>: {html.relative_to(DIST)}")
        if not page.description:
            fail(f"Missing meta description: {html.relative_to(DIST)}")
        if not page.h1:
            warn(f"No H1 detected: {html.relative_to(DIST)}")

    for route in routes:
        route_path = route["path"]
        html = route_file(route_path)
        if html is None:
            fail(f"Priority route has no static HTML output: {route_path}")
            continue
        page = parsed.get(html) or parse_page(html)
        if page.title != route["title"]:
            fail(f"Title mismatch for {route_path}: {page.title!r}")
        if page.description != route["description"]:
            fail(f"Meta description mismatch for {route_path}")
        if page.h1 != route["h1"]:
            fail(f"H1 mismatch for {route_path}: {page.h1!r}")
        if not page.canonical:
            fail(f"Missing canonical for {route_path}")
        else:
            parsed_canonical = urlparse(page.canonical)
            canonical_path = parsed_canonical.path.rstrip("/") or "/"
            if canonical_path != route_path.rstrip("/"):
                fail(f"Canonical path mismatch for {route_path}: {page.canonical}")
            if parsed_canonical.hostname and parsed_canonical.hostname.endswith("vercel.app"):
                fail(f"Preview Vercel hostname used as canonical for {route_path}")

    # Validate crawl-control files when present; fail if absent because this is an SEO preview.
    robots = DIST / "robots.txt"
    sitemap = DIST / "sitemap.xml"
    if not robots.is_file():
        fail("dist/robots.txt is missing")
    if not sitemap.is_file():
        fail("dist/sitemap.xml is missing")
    else:
        sitemap_text = sitemap.read_text(encoding="utf-8", errors="replace")
        for route in routes:
            if route["path"] not in sitemap_text:
                fail(f"Priority route missing from sitemap: {route['path']}")
        if ".vercel.app" in sitemap_text:
            fail("sitemap.xml contains a Vercel preview hostname")

    # Catch common broken local links in generated HTML.
    for html, page in parsed.items():
        for href in page.links:
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            parsed_href = urlparse(href)
            if parsed_href.scheme or parsed_href.netloc:
                continue
            local_path = parsed_href.path
            if not local_path or local_path.startswith("/api/"):
                continue
            if local_path.startswith("/"):
                target = route_file(local_path)
            else:
                # Resolve simple relative links against the static file directory.
                candidate = (html.parent / unquote(local_path)).resolve()
                try:
                    candidate.relative_to(DIST.resolve())
                except ValueError:
                    fail(f"Link escapes dist/: {html.relative_to(DIST)} -> {href}")
                    continue
                target = candidate if candidate.is_file() else None
                if target is None and candidate.suffix == "":
                    for c in (Path(str(candidate) + ".html"), candidate / "index.html"):
                        if c.is_file():
                            target = c
                            break
            if target is None:
                fail(f"Broken local link: {html.relative_to(DIST)} -> {href}")


def main() -> int:
    routes = validate_manifest()
    validate_build(routes)

    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")

    if errors:
        print(f"Validation failed with {len(errors)} error(s) and {len(warnings)} warning(s).")
        return 1
    print(f"Validation passed: 10 priority routes, {len(list(DIST.rglob('*.html')))} HTML files, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
