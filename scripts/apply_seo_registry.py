#!/usr/bin/env python3
"""Apply the canonical route registry to the generated static site.

The registry owns active routes, canonicals, redirects, sitemap membership and
the compact internal-link graph. Content generators remain responsible for the
body copy of each page.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REGISTRY_PATH = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"

LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.I)
META_TAG_RE = re.compile(r"<meta\b[^>]*>", re.I)
HREF_RE = re.compile(r"(?P<prefix>\bhref\s*=\s*['\"])(?P<value>[^'\"]+)(?P<suffix>['\"])", re.I)


def attr(tag: str, name: str) -> str | None:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    return html.unescape(match.group(2).strip()) if match else None


def route_file(path: str) -> Path:
    return DIST / ("index.html" if path == "/" else f"{path.lstrip('/')}.html")


def normalized_route(value: str, host: str) -> tuple[str, str, str] | None:
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
    if path.endswith(".html"):
        path = path[:-5] or "/"
    path = "/" if path == "/" else "/" + path.strip("/")
    return path, parsed.query, parsed.fragment


def replace_special_tag(source: str, tag_re: re.Pattern[str], predicate, replacement: str) -> str:
    found = False

    def replace(match: re.Match[str]) -> str:
        nonlocal found
        tag = match.group(0)
        if not predicate(tag):
            return tag
        if found:
            return ""
        found = True
        return replacement

    source = tag_re.sub(replace, source)
    if not found:
        if "</head>" not in source.lower():
            raise RuntimeError("Generated page has no closing head tag")
        source = re.sub(r"</head>", replacement + "\n</head>", source, count=1, flags=re.I)
    return source


def rewrite_redirect_links(source: str, host: str, redirects: dict[str, str]) -> tuple[str, int]:
    changed = 0

    def replace_href(match: re.Match[str]) -> str:
        nonlocal changed
        value = match.group("value")
        parsed = normalized_route(value, host)
        if parsed is None:
            return match.group(0)
        path, query, fragment = parsed
        if path not in redirects:
            return match.group(0)
        destination = redirects[path]
        suffix = ("?" + query if query else "") + ("#" + fragment if fragment else "")
        changed += 1
        return match.group("prefix") + destination + suffix + match.group("suffix")

    source = HREF_RE.sub(replace_href, source)
    for old, new in redirects.items():
        absolute_old = host + old
        absolute_new = host + new
        occurrences = source.count(absolute_old)
        if occurrences:
            source = source.replace(absolute_old, absolute_new)
            changed += occurrences
    return source, changed


def related_routes(route: dict, active: list[dict]) -> list[dict]:
    same_cluster = [candidate for candidate in active if candidate["cluster"] == route["cluster"] and candidate["path"] != route["path"]]
    role_order = {"hub": 0, "product": 0, "tool": 1, "comparison": 2, "reference": 3, "guide": 4, "policy": 5}
    same_cluster.sort(key=lambda candidate: (role_order.get(candidate["role"], 9), candidate["path"]))

    selected: list[dict] = []
    for candidate in same_cluster:
        if candidate not in selected:
            selected.append(candidate)
        if len(selected) == 4:
            break

    by_path = {candidate["path"]: candidate for candidate in active}
    for fallback in ("/methodology", "/"):
        candidate = by_path.get(fallback)
        if candidate and candidate["path"] != route["path"] and candidate not in selected:
            selected.append(candidate)
        if len(selected) == 5:
            break
    return selected


def install_related_block(source: str, route: dict, active: list[dict]) -> str:
    start = "<!-- cist-registry-links:start -->"
    end = "<!-- cist-registry-links:end -->"
    source = re.sub(re.escape(start) + r".*?" + re.escape(end), "", source, flags=re.S)
    if route["path"] == "/":
        return source

    links = related_routes(route, active)
    anchors = "".join(
        f'<a href="{html.escape(item["path"], quote=True)}">{html.escape(item["primaryKeyword"])}</a>'
        for item in links
    )
    block = (
        f"{start}<nav class=\"seo-registry-links\" aria-label=\"Related checks and guides\">"
        f"<strong>Related checks and guides</strong><div>{anchors}</div></nav>{end}"
    )
    anchor = re.search(r"</main>", source, re.I)
    if anchor:
        return source[:anchor.start()] + block + "\n" + source[anchor.start():]
    anchor = re.search(r"<footer\b", source, re.I)
    if anchor:
        return source[:anchor.start()] + block + "\n" + source[anchor.start():]
    raise RuntimeError(f"Cannot place internal links on {route['path']}")


def install_related_style(source: str) -> str:
    marker = 'id="cist-registry-links-style"'
    if marker in source:
        return source
    style = (
        '<style id="cist-registry-links-style">'
        '.seo-registry-links{margin:26px 0 0;padding:18px 0 0;border-top:1px solid var(--line,#d9dde5)}'
        '.seo-registry-links strong{display:block;margin-bottom:10px;font-size:14px}'
        '.seo-registry-links div{display:flex;flex-wrap:wrap;gap:8px}'
        '.seo-registry-links a{display:inline-flex;padding:7px 10px;border:1px solid var(--line,#d9dde5);border-radius:999px;color:inherit;font-size:12px;text-decoration:none}'
        '.seo-registry-links a:hover{text-decoration:underline}'
        '</style>'
    )
    if "</head>" not in source.lower():
        raise RuntimeError("Generated page has no closing head tag")
    return re.sub(r"</head>", style + "\n</head>", source, count=1, flags=re.I)


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError("dist directory not found")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    host = registry["canonicalHost"].rstrip("/")
    active = [route for route in registry["routes"] if route["status"] == "active"]
    active_paths = {route["path"] for route in active}
    redirects = {item["from"]: item["to"] for item in registry["redirects"]}

    if len(active_paths) != len(active):
        raise RuntimeError("Duplicate active path in SEO registry")
    if active_paths & redirects.keys():
        raise RuntimeError("A route cannot be both active and redirected")
    if any(destination not in active_paths for destination in redirects.values()):
        raise RuntimeError("Every redirect must target an active route")
    for route in active:
        if route["canonical"] not in active_paths:
            raise RuntimeError(f"Canonical target is not active: {route['path']} -> {route['canonical']}")
        if not route_file(route["path"]).is_file():
            raise RuntimeError(f"Registered active route was not generated: {route['path']}")

    removed = 0
    for alias in redirects:
        target = route_file(alias)
        if target.is_file():
            target.unlink()
            removed += 1

    rewritten = 0
    for route in active:
        target = route_file(route["path"])
        source = target.read_text(encoding="utf-8", errors="strict")
        source, link_changes = rewrite_redirect_links(source, host, redirects)
        rewritten += link_changes
        canonical = host + route["canonical"]
        source = replace_special_tag(
            source,
            LINK_TAG_RE,
            lambda tag: "canonical" in (attr(tag, "rel") or "").lower().split(),
            f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">',
        )
        robots_value = "index,follow" if route["index"] else "noindex,follow"
        source = replace_special_tag(
            source,
            META_TAG_RE,
            lambda tag: (attr(tag, "name") or "").lower() == "robots",
            f'<meta name="robots" content="{robots_value}">',
        )
        source = install_related_block(source, route, active)
        source = install_related_style(source)
        target.write_text(source, encoding="utf-8")

    indexable = [route for route in active if route["index"] and route["canonical"] == route["path"]]
    indexable.sort(key=lambda route: (route["path"] != "/", route["path"]))
    entries = "\n".join(
        f"  <url><loc>{html.escape(host + route['path'])}</loc></url>" for route in indexable
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries + '\n</urlset>\n'
    )
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {host}/sitemap.xml\n", encoding="utf-8"
    )
    print(
        f"Applied SEO registry: {len(active)} active routes, {len(redirects)} permanent redirects, "
        f"{rewritten} legacy links rewritten, {removed} duplicate outputs removed."
    )


if __name__ == "__main__":
    main()
