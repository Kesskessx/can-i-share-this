#!/usr/bin/env python3
"""Fail the build when generated SEO routes drift from the central registry."""

from __future__ import annotations

import html
import itertools
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REGISTRY_PATH = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"
VERCEL_PATH = ROOT / "vercel.json"

LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.I)
META_TAG_RE = re.compile(r"<meta\b[^>]*>", re.I)
ANCHOR_RE = re.compile(r"<a\b[^>]*\bhref\s*=\s*(['\"])(.*?)\1", re.I | re.S)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
STRIP_BLOCK_RE = re.compile(r"<(script|style|svg|nav|header|footer|form|aside)\b.*?</\1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>", re.S)

STOPWORDS = {
    "a", "an", "and", "are", "before", "can", "do", "does", "for", "how", "i", "if",
    "in", "is", "it", "my", "of", "or", "the", "this", "to", "will", "with", "without", "you", "your",
}


def attr(tag: str, name: str) -> str | None:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    return html.unescape(match.group(2).strip()) if match else None


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", value))).strip()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", clean_text(value).lower()).strip()


def route_file(path: str) -> Path:
    return DIST / ("index.html" if path == "/" else f"{path.lstrip('/')}.html")


def file_route(path: Path) -> str:
    return "/" if path.name == "index.html" else "/" + path.relative_to(DIST).with_suffix("").as_posix()


def normalized_route(value: str, host: str) -> str | None:
    value = html.unescape(value.strip())
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        allowed_hosts = {urlsplit(host).netloc.lower(), "www." + urlsplit(host).netloc.lower()}
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in allowed_hosts:
            return None
    elif not value.startswith("/"):
        return None
    path = parsed.path or "/"
    if path.startswith("/api/") or path == "/api":
        return None
    if path.endswith(".html"):
        path = path[:-5] or "/"
    return "/" if path == "/" else "/" + path.strip("/")


def special_tags(source: str, tag_re: re.Pattern[str], predicate) -> list[str]:
    return [match.group(0) for match in tag_re.finditer(source) if predicate(match.group(0))]


def visible_words(source: str) -> list[str]:
    source = STRIP_BLOCK_RE.sub(" ", source)
    return re.findall(r"[a-z0-9]+", clean_text(source).lower())


def shingles(words: list[str], size: int = 5) -> set[tuple[str, ...]]:
    return {tuple(words[index:index + size]) for index in range(max(0, len(words) - size + 1))}


def keyword_terms(value: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", value.lower()) if word not in STOPWORDS}


def jaccard(left: set, right: set) -> float:
    return len(left & right) / len(left | right) if left and right else 0.0


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    host = registry.get("canonicalHost", "").rstrip("/")
    policy = registry.get("policy", {})
    active = [route for route in registry.get("routes", []) if route.get("status") == "active"]
    redirects = registry.get("redirects", [])
    active_by_path = {route["path"]: route for route in active}
    redirect_by_path = {item["from"]: item for item in redirects}

    if host != "https://canisharethis.com":
        errors.append(f"canonicalHost must be the production HTTPS origin, got {host!r}")
    if len(active_by_path) != len(active):
        errors.append("Duplicate active path in registry")
    if len(redirect_by_path) != len(redirects):
        errors.append("Duplicate redirect source in registry")

    required_route_fields = {"path", "status", "index", "canonical", "cluster", "role", "intent", "primaryKeyword"}
    for route in active:
        missing = required_route_fields - set(route)
        if missing:
            errors.append(f"{route.get('path', '<unknown>')}: missing registry fields {sorted(missing)}")
        path = route.get("path", "")
        if path != "/" and not re.fullmatch(r"/[a-z0-9-]+", path):
            errors.append(f"Invalid clean route path: {path}")
        if route.get("canonical") not in active_by_path:
            errors.append(f"{path}: canonical target is not active: {route.get('canonical')}")

    for item in redirects:
        source = item.get("from")
        destination = item.get("to")
        if source in active_by_path:
            errors.append(f"Redirect source is also active: {source}")
        if destination not in active_by_path:
            errors.append(f"Redirect target is not active: {source} -> {destination}")
        if destination in redirect_by_path:
            errors.append(f"Redirect chain is forbidden: {source} -> {destination}")
        if item.get("statusCode") not in {301, 308}:
            errors.append(f"Redirect must be permanent: {source}")

    generated = {file_route(path): path for path in DIST.rglob("*.html")}
    for path in sorted(set(active_by_path) - set(generated)):
        errors.append(f"Registered active route is missing its HTML output: {path}")
    for path in sorted(set(generated) - set(active_by_path)):
        if path in redirect_by_path:
            errors.append(f"Redirect source still has an indexable HTML output: {path}")
        else:
            errors.append(f"Generated HTML route is absent from registry: {path}")

    metadata: dict[str, dict[str, str]] = {}
    inbound: dict[str, set[str]] = {path: set() for path in active_by_path}
    content_shingles: dict[str, set[tuple[str, ...]]] = {}

    for path, route in active_by_path.items():
        target = route_file(path)
        if not target.is_file():
            continue
        source = target.read_text(encoding="utf-8", errors="strict")
        if re.search(r"https?://[^\s'\"<>]*vercel\.app", source, re.I):
            errors.append(f"Preview Vercel hostname leaked into production page: {path}")

        titles = [clean_text(value) for value in TITLE_RE.findall(source)]
        h1s = [clean_text(value) for value in H1_RE.findall(source)]
        descriptions = special_tags(source, META_TAG_RE, lambda tag: (attr(tag, "name") or "").lower() == "description")
        canonicals = special_tags(source, LINK_TAG_RE, lambda tag: "canonical" in (attr(tag, "rel") or "").lower().split())
        robots = special_tags(source, META_TAG_RE, lambda tag: (attr(tag, "name") or "").lower() == "robots")

        if len(titles) != 1 or not titles[0]:
            errors.append(f"{path}: expected exactly one non-empty title")
        if len(h1s) != 1 or not h1s[0]:
            errors.append(f"{path}: expected exactly one non-empty H1")
        if len(descriptions) != 1 or not (attr(descriptions[0], "content") if descriptions else ""):
            errors.append(f"{path}: expected exactly one non-empty meta description")
        if len(canonicals) != 1:
            errors.append(f"{path}: expected exactly one canonical link")
        if len(robots) != 1:
            errors.append(f"{path}: expected exactly one robots meta tag")

        title = titles[0] if titles else ""
        h1 = h1s[0] if h1s else ""
        description = attr(descriptions[0], "content") if len(descriptions) == 1 else ""
        canonical = attr(canonicals[0], "href") if len(canonicals) == 1 else ""
        robots_value = (attr(robots[0], "content") or "").lower() if len(robots) == 1 else ""
        expected_canonical = host + route["canonical"]

        if canonical != expected_canonical:
            errors.append(f"{path}: canonical {canonical!r} does not match {expected_canonical!r}")
        if route["index"] and ("index" not in robots_value.split(",") or "noindex" in robots_value):
            errors.append(f"{path}: indexable registry route has incompatible robots value {robots_value!r}")
        if title and not 30 <= len(title) <= 70:
            warnings.append(f"{path}: title length is {len(title)} characters")
        if description and not 100 <= len(description) <= 165:
            warnings.append(f"{path}: meta description length is {len(description)} characters")

        metadata[path] = {"title": title, "h1": h1, "description": description or "", "canonical": canonical or ""}
        words = visible_words(source)
        if len(words) < 120:
            warnings.append(f"{path}: only {len(words)} visible words after navigation is removed")
        content_shingles[path] = shingles(words)

        for _, href in ANCHOR_RE.findall(source):
            destination = normalized_route(href, host)
            if destination is None:
                continue
            if destination in redirect_by_path:
                errors.append(f"{path}: internal link still points through redirect {destination}")
            elif destination not in active_by_path:
                errors.append(f"{path}: internal link points to an unknown route {destination}")
            elif destination != path:
                inbound[destination].add(path)

    for field in ("title", "h1", "description", "canonical"):
        values: dict[str, list[str]] = defaultdict(list)
        for path, values_by_field in metadata.items():
            value = normalized(values_by_field[field])
            if value:
                values[value].append(path)
        for paths in values.values():
            if len(paths) > 1:
                errors.append(f"Duplicate {field}: {', '.join(sorted(paths))}")

    intents: dict[str, list[str]] = defaultdict(list)
    keywords: dict[str, list[str]] = defaultdict(list)
    for route in active:
        intents[normalized(route["intent"])].append(route["path"])
        keywords[normalized(route["primaryKeyword"])].append(route["path"])
    for label, groups in (("intent", intents), ("primary keyword", keywords)):
        for paths in groups.values():
            if len(paths) > 1:
                errors.append(f"Duplicate {label}: {', '.join(sorted(paths))}")

    intent_threshold = float(policy.get("intentSimilarityReviewThreshold", 0.88))
    for left, right in itertools.combinations(active, 2):
        score = jaccard(keyword_terms(left["primaryKeyword"]), keyword_terms(right["primaryKeyword"]))
        if score >= intent_threshold:
            errors.append(
                f"Potential duplicate search intent ({score:.2f}): {left['path']} and {right['path']}"
            )

    content_threshold = float(policy.get("contentSimilarityFailThreshold", 0.82))
    for left, right in itertools.combinations(sorted(content_shingles), 2):
        score = jaccard(content_shingles[left], content_shingles[right])
        if score >= content_threshold:
            errors.append(f"Near-duplicate page content ({score:.2f}): {left} and {right}")

    for path, sources in sorted(inbound.items()):
        if path != "/" and not sources:
            errors.append(f"Orphan page has no internal inbound link: {path}")

    sitemap_path = DIST / "sitemap.xml"
    try:
        tree = ET.parse(sitemap_path)
        sitemap_urls = [node.text.strip() for node in tree.findall("{*}url/{*}loc") if node.text]
    except (ET.ParseError, OSError) as exc:
        errors.append(f"Invalid sitemap.xml: {exc}")
        sitemap_urls = []
    expected_urls = {
        host + route["path"] for route in active if route["index"] and route["canonical"] == route["path"]
    }
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append("sitemap.xml contains duplicate URLs")
    missing_urls = expected_urls - set(sitemap_urls)
    extra_urls = set(sitemap_urls) - expected_urls
    if missing_urls:
        errors.append("Indexable routes missing from sitemap: " + ", ".join(sorted(missing_urls)))
    if extra_urls:
        errors.append("Non-canonical or unknown routes in sitemap: " + ", ".join(sorted(extra_urls)))

    robots_text = (DIST / "robots.txt").read_text(encoding="utf-8", errors="replace") if (DIST / "robots.txt").is_file() else ""
    if "Disallow: /" in robots_text or f"Sitemap: {host}/sitemap.xml" not in robots_text:
        errors.append("robots.txt blocks crawling or does not advertise the canonical sitemap")

    vercel = json.loads(VERCEL_PATH.read_text(encoding="utf-8"))
    if vercel.get("cleanUrls") != policy.get("cleanUrls") or vercel.get("trailingSlash") != policy.get("trailingSlash"):
        errors.append("vercel.json clean URL policy differs from the SEO registry")
    expected_redirects = {
        (item["from"], item["to"], item["statusCode"] in {301, 308}) for item in redirects
    }
    actual_redirects = {
        (item.get("source"), item.get("destination"), bool(item.get("permanent")))
        for item in vercel.get("redirects", [])
    }
    if actual_redirects != expected_redirects:
        errors.append("vercel.json permanent redirects differ from the SEO registry")

    if warnings:
        print(f"SEO registry audit warnings: {len(warnings)}")
        for warning in warnings:
            print("WARNING", warning)
    if errors:
        print(f"SEO registry audit FAILED: {len(errors)} error(s)")
        for error in errors:
            print("ERROR", error)
        sys.exit(1)

    print(
        f"SEO registry audit passed: {len(active)} canonical pages, {len(redirects)} permanent redirects, "
        f"{len(sitemap_urls)} sitemap URLs, 0 orphan pages and 0 duplicate metadata fields."
    )


if __name__ == "__main__":
    main()
