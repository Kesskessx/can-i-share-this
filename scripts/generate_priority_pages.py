#!/usr/bin/env python3
"""Generate the 10 prepared SEO pages as a reversible overlay on the static preview."""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST_PATH = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"
CONTENT_PATH = ROOT / "seo" / "SEO_PAGES_2026.md"
CANONICAL_HOST = os.environ.get("CANONICAL_HOST", "https://canisharethis.com").rstrip("/")


def inline(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"`(.+?)`", r"<code>\1</code>", value)
    return value


def extract_page_section(source: str, route: str) -> str:
    pattern = re.compile(
        rf"^#\s+\d+\.\s+{re.escape(route)}\s*$\n(?P<body>.*?)(?=^---\s*$|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"No content section found for {route}")
    body = match.group("body")
    marker = "## Above-the-fold answer"
    if marker not in body:
        raise RuntimeError(f"Missing above-the-fold section for {route}")
    return body.split(marker, 1)[1].strip()


def route_exists(route: str, priority_routes: set[str]) -> bool:
    if route in priority_routes or route == "/":
        return True
    rel = route.lstrip("/").rstrip("/")
    return any(
        p.is_file()
        for p in (DIST / rel, DIST / f"{rel}.html", DIST / rel / "index.html")
    )


def render_body(markdown: str, priority_routes: set[str]) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    in_internal_links = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(line.strip() for line in paragraph).strip()
            if text:
                out.append(f"<p>{inline(text)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            out.append("<ul>" + "".join(list_items) + "</ul>")
            list_items = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if stripped == "## Main copy":
            flush_paragraph(); flush_list()
            continue
        if stripped == "## FAQ":
            flush_paragraph(); flush_list()
            out.append("<h2>Frequently asked questions</h2>")
            in_internal_links = False
            continue
        if stripped == "## Internal links":
            flush_paragraph(); flush_list()
            out.append("<h2>Related checks</h2>")
            in_internal_links = True
            continue
        if stripped.startswith("## "):
            flush_paragraph(); flush_list()
            out.append(f"<h2>{inline(stripped[3:])}</h2>")
            in_internal_links = False
            continue
        if stripped.startswith("### "):
            flush_paragraph(); flush_list()
            out.append(f"<h2>{inline(stripped[4:])}</h2>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            item = stripped[2:].strip()
            if in_internal_links:
                m = re.match(r"`(/[^`]+)`\s*(?:—|-)\s*(.+)", item)
                if m:
                    target, label = m.groups()
                    if route_exists(target, priority_routes):
                        list_items.append(
                            f'<li><a href="{html.escape(target)}">{inline(label)}</a></li>'
                        )
                    continue
            list_items.append(f"<li>{inline(item)}</li>")
            continue

        numbered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            flush_paragraph()
            list_items.append(f"<li>{inline(numbered.group(1))}</li>")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(out)


def page_html(route: dict, body_html: str) -> str:
    path = route["path"]
    canonical = CANONICAL_HOST + path
    title = route["title"]
    description = route["description"]
    h1 = route["h1"]

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": CANONICAL_HOST + "/"},
            {"@type": "ListItem", "position": 2, "name": h1, "item": canonical},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": CANONICAL_HOST + "/"},
    }

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta name="robots" content="noindex,follow">
  <link rel="canonical" href="{html.escape(canonical, quote=True)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:url" content="{html.escape(canonical, quote=True)}">
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">{html.escape(json.dumps(breadcrumb, ensure_ascii=False))}</script>
  <script type="application/ld+json">{html.escape(json.dumps(webpage, ensure_ascii=False))}</script>
  <style>
    :root{{color-scheme:light dark;--bg:#f7f7f5;--card:#fff;--text:#171717;--muted:#626262;--line:#deded8;--accent:#111;--accentText:#fff}}
    @media(prefers-color-scheme:dark){{:root{{--bg:#101010;--card:#171717;--text:#f1f1f1;--muted:#aaa;--line:#303030;--accent:#f5f5f5;--accentText:#111}}}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    a{{color:inherit}}header{{border-bottom:1px solid var(--line);background:var(--card)}}.nav{{max-width:980px;margin:auto;padding:18px 24px;display:flex;justify-content:space-between;align-items:center;gap:20px}}
    .brand{{font-weight:800;text-decoration:none}}.button{{display:inline-block;background:var(--accent);color:var(--accentText);padding:10px 15px;border-radius:9px;text-decoration:none;font-weight:700}}
    main{{max-width:820px;margin:0 auto;padding:54px 24px 72px}}.crumbs{{font-size:14px;color:var(--muted);margin-bottom:24px}}h1{{font-size:clamp(34px,6vw,56px);line-height:1.04;letter-spacing:-.035em;margin:0 0 24px}}
    h2{{font-size:26px;line-height:1.2;margin:42px 0 14px}}p{{margin:0 0 18px}}main>p:first-of-type{{font-size:20px;color:var(--muted)}}ul{{padding-left:24px;margin:0 0 22px}}li{{margin:7px 0}}code{{font-size:.9em;background:var(--line);padding:2px 5px;border-radius:4px}}
    .cta{{margin:48px 0 0;padding:24px;border:1px solid var(--line);background:var(--card);border-radius:14px}}.cta h2{{margin-top:0}}footer{{border-top:1px solid var(--line);padding:25px;text-align:center;color:var(--muted);font-size:14px}}
  </style>
</head>
<body>
<header><div class="nav"><a class="brand" href="/">Can I Share This?</a><a class="button" href="/">Check a link</a></div></header>
<main>
  <div class="crumbs"><a href="/">Home</a> / {html.escape(route['cluster'])}</div>
  <h1>{html.escape(h1)}</h1>
  {body_html}
  <section class="cta"><h2>Check the link before you send it</h2><p>Paste the final share URL into Can I Share This? and review the recipient-access verdict before sending.</p><a class="button" href="/">Check a link</a></section>
</main>
<footer>Can I Share This? · Recipient-access checks before sharing</footer>
</body>
</html>'''


def write_route(route: dict, source: str, priority_routes: set[str]) -> None:
    section = extract_page_section(source, route["path"])
    body = render_body(section, priority_routes)
    target = DIST / f"{route['path'].lstrip('/').rstrip('/')}.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page_html(route, body), encoding="utf-8")


def update_sitemap(routes: list[dict]) -> None:
    sitemap = DIST / "sitemap.xml"
    urls: set[str] = set()
    if sitemap.is_file():
        old = sitemap.read_text(encoding="utf-8", errors="replace")
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", old, flags=re.I | re.S):
            parsed = urlparse(html.unescape(loc.strip()))
            if parsed.path:
                urls.add(CANONICAL_HOST + (parsed.path.rstrip("/") or "/"))
    urls.add(CANONICAL_HOST + "/")
    for route in routes:
        urls.add(CANONICAL_HOST + route["path"])

    body = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    sitemap.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{body}\n'</urlset>\n',
        encoding="utf-8",
    )


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    routes = manifest["routes"]
    source = CONTENT_PATH.read_text(encoding="utf-8")
    priority_routes = {route["path"] for route in routes}
    for route in routes:
        write_route(route, source, priority_routes)
    update_sitemap(routes)
    print(f"Generated {len(routes)} priority SEO pages on top of the static preview")


if __name__ == "__main__":
    main()
