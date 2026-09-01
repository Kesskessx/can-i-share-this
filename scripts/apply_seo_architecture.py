#!/usr/bin/env python3
"""Post-process the built static site for production SEO architecture.

This script is intentionally idempotent: every build can run it safely.
It strengthens internal linking, differentiates legacy quick-check routes from
SEO hubs, and adds lightweight structured data to legacy/static pages.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOST = "https://canisharethis.com"

PRIORITY_LINKS = [
    ("/google-drive-link-checker", "Google Drive Link Checker", "Test recipient access and Drive sharing barriers."),
    ("/dropbox-link-checker", "Dropbox Link Checker", "Check Dropbox sharing, login and expiration risks."),
    ("/drive-vs-dropbox-share-link-checker", "Google Drive vs Dropbox", "Compare the sharing risks of both platforms."),
]

CLUSTERS = {
    "/google-drive-link-checker": [
        ("/check-google-drive-link", "Run the quick Google Drive link check"),
        ("/google-drive-permission-checker", "Check Google Drive permissions"),
        ("/google-drive-link-not-working", "Diagnose a Drive link that does not work"),
        ("/google-drive-folder-sharing-checker", "Test a shared Drive folder"),
        ("/google-drive-share-link-test", "Test the final Drive share URL"),
        ("/drive-vs-dropbox-share-link-checker", "Compare Drive and Dropbox sharing"),
    ],
    "/google-drive-permission-checker": [
        ("/google-drive-link-checker", "Google Drive Link Checker hub"),
        ("/google-drive-link-not-working", "Why a Drive link does not work"),
        ("/google-drive-folder-sharing-checker", "Check Drive folder sharing"),
        ("/google-drive-share-link-test", "Test the final Drive share URL"),
    ],
    "/google-drive-link-not-working": [
        ("/google-drive-link-checker", "Google Drive Link Checker hub"),
        ("/google-drive-permission-checker", "Check Google Drive permissions"),
        ("/google-drive-share-link-test", "Test the final Drive share URL"),
    ],
    "/google-drive-folder-sharing-checker": [
        ("/google-drive-link-checker", "Google Drive Link Checker hub"),
        ("/google-drive-permission-checker", "Check Google Drive permissions"),
        ("/google-drive-share-link-test", "Test the final Drive share URL"),
    ],
    "/google-drive-share-link-test": [
        ("/google-drive-link-checker", "Google Drive Link Checker hub"),
        ("/google-drive-permission-checker", "Check Google Drive permissions"),
        ("/google-drive-link-not-working", "Diagnose a Drive link that does not work"),
    ],
    "/dropbox-link-checker": [
        ("/check-dropbox-link", "Run the quick Dropbox link check"),
        ("/dropbox-permission-checker", "Check Dropbox permissions"),
        ("/dropbox-shared-link-not-working", "Diagnose a Dropbox link that does not work"),
        ("/dropbox-link-expiration-checker", "Check Dropbox link expiration"),
        ("/drive-vs-dropbox-share-link-checker", "Compare Drive and Dropbox sharing"),
    ],
    "/dropbox-permission-checker": [
        ("/dropbox-link-checker", "Dropbox Link Checker hub"),
        ("/dropbox-shared-link-not-working", "Why a Dropbox link does not work"),
        ("/dropbox-link-expiration-checker", "Check Dropbox link expiration"),
    ],
    "/dropbox-shared-link-not-working": [
        ("/dropbox-link-checker", "Dropbox Link Checker hub"),
        ("/dropbox-permission-checker", "Check Dropbox permissions"),
        ("/dropbox-link-expiration-checker", "Check Dropbox link expiration"),
    ],
    "/dropbox-link-expiration-checker": [
        ("/dropbox-link-checker", "Dropbox Link Checker hub"),
        ("/dropbox-permission-checker", "Check Dropbox permissions"),
        ("/dropbox-shared-link-not-working", "Diagnose a Dropbox link that does not work"),
    ],
    "/drive-vs-dropbox-share-link-checker": [
        ("/google-drive-link-checker", "Google Drive Link Checker"),
        ("/dropbox-link-checker", "Dropbox Link Checker"),
        ("/google-drive-permission-checker", "Google Drive Permission Checker"),
        ("/dropbox-permission-checker", "Dropbox Permission Checker"),
    ],
}

LEGACY_TOOLS = {
    "/check-google-drive-link": {
        "title": "Quick Google Drive Link Test — Check Access Now | Can I Share This?",
        "description": "Paste a Google Drive URL for a fast recipient-access check. For detailed permission guidance, use the full Google Drive Link Checker guide.",
        "h1": "Run a Quick Google Drive Link Test",
        "hub": "/google-drive-link-checker",
        "hub_label": "Read the full Google Drive Link Checker guide",
        "copy": "Use this page when you already have a Drive URL and want to run the checker immediately. For troubleshooting permissions, sign-in walls, Workspace restrictions and recipient access, the detailed Google Drive Link Checker guide explains what each result means and what to change before sharing.",
    },
    "/check-dropbox-link": {
        "title": "Quick Dropbox Link Test — Check Access Now | Can I Share This?",
        "description": "Paste a Dropbox shared URL for a fast recipient-access check. For detailed sharing and expiration guidance, use the full Dropbox Link Checker guide.",
        "h1": "Run a Quick Dropbox Link Test",
        "hub": "/dropbox-link-checker",
        "hub_label": "Read the full Dropbox Link Checker guide",
        "copy": "Use this page when you already have a Dropbox URL and want a quick access verdict. For deeper help with login barriers, permissions, disabled links and expiration risk, the detailed Dropbox Link Checker guide explains the recipient-facing signals to review before sending.",
    },
}

SECONDARY_PAGES = {
    "/check-notion-link": (
        "Before sending a Notion page, test the exact public or shared URL rather than relying on your signed-in workspace view. A recipient may see a login prompt or a restricted page even when the link opens normally for you.",
        [("/recipient-access-checker", "Learn how recipient-access checking works"), ("/privacy-link-checker", "Review privacy signals before sharing")],
    ),
    "/check-onedrive-link": (
        "OneDrive and SharePoint links can behave differently for owners, organization members and external recipients. Test the final URL after changing sharing permissions so the result reflects the link you will actually send.",
        [("/recipient-access-checker", "Learn how recipient-access checking works"), ("/privacy-link-checker", "Review privacy signals before sharing")],
    ),
    "/remove-tracking-from-url": (
        "Tracking parameters can expose campaign, referral or analytics data that is unnecessary for the recipient. Clean the URL first, then test the cleaned link to make sure removing parameters did not break the destination.",
        [("/privacy-link-checker", "Check link privacy signals"), ("/recipient-access-checker", "Test recipient access after cleaning the URL")],
    ),
    "/check-if-link-expires": (
        "Some shared links can expire because of platform settings, temporary tokens or account policies. An expiration check is a risk signal rather than a guarantee, so important links should be re-tested close to the time they are sent.",
        [("/dropbox-link-expiration-checker", "Check Dropbox link expiration"), ("/recipient-access-checker", "Test whether a recipient can open the link now")],
    ),
}


def route_file(route: str) -> Path | None:
    rel = route.strip("/")
    candidates = [
        DIST / "index.html" if route == "/" else DIST / f"{rel}.html",
        DIST / rel / "index.html",
        DIST / rel,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def insert_before_main_end(source: str, block: str) -> str:
    if block in source:
        return source
    if "</main>" in source:
        return source.replace("</main>", block + "\n</main>", 1)
    return source.replace("</body>", block + "\n</body>", 1)


def replace_title(source: str, title: str) -> str:
    escaped = html.escape(title)
    if re.search(r"<title>.*?</title>", source, flags=re.I | re.S):
        return re.sub(r"<title>.*?</title>", f"<title>{escaped}</title>", source, count=1, flags=re.I | re.S)
    return source.replace("</head>", f"  <title>{escaped}</title>\n</head>", 1)


def upsert_meta_description(source: str, description: str) -> str:
    escaped = html.escape(description, quote=True)
    pattern = r'<meta\s+name=["\']description["\'][^>]*>'
    replacement = f'<meta name="description" content="{escaped}">'
    if re.search(pattern, source, flags=re.I):
        return re.sub(pattern, replacement, source, count=1, flags=re.I)
    return source.replace("</head>", f"  {replacement}\n</head>", 1)


def replace_first_h1(source: str, h1: str) -> str:
    replacement = f"<h1>{html.escape(h1)}</h1>"
    return re.sub(r"<h1(?:\s[^>]*)?>.*?</h1>", replacement, source, count=1, flags=re.I | re.S)


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def ensure_schema(source: str, route: str, title: str, description: str) -> str:
    canonical = HOST + (route if route != "/" else "/")
    if '"@type":"WebPage"' in source or '"@type": "WebPage"' in source:
        return source
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Can I Share This?", "url": HOST + "/"},
    }
    tag = f'<script type="application/ld+json">{json_ld(schema)}</script>'
    return source.replace("</head>", f"  {tag}\n</head>", 1)


def patch_homepage() -> None:
    path = route_file("/")
    if not path:
        raise RuntimeError("Homepage dist/index.html not found")
    source = path.read_text(encoding="utf-8", errors="replace")

    marker = 'id="seo-popular-checks"'
    if marker not in source:
        cards = "".join(
            f'<li><a href="{href}"><strong>{html.escape(label)}</strong></a><br><span>{html.escape(desc)}</span></li>'
            for href, label, desc in PRIORITY_LINKS
        )
        block = (
            '<section id="seo-popular-checks" aria-labelledby="seo-popular-checks-title">'
            '<h2 id="seo-popular-checks-title">Popular link checks</h2>'
            '<p>Start with the platform-specific guide for the link you are about to share.</p>'
            f'<ul>{cards}</ul></section>'
        )
        source = insert_before_main_end(source, block)

    source = replace_title(source, "Can I Share This? — Check Link Access, Privacy & Expiration")
    source = upsert_meta_description(
        source,
        "Check whether a shared link will open for the recipient, expose unnecessary tracking or privacy signals, or carry expiration risk before you send it.",
    )

    if '"@type":"WebSite"' not in source and '"@type": "WebSite"' not in source:
        website = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Can I Share This?",
            "url": HOST + "/",
            "description": "Recipient-access, privacy and expiration checks for shared links.",
        }
        tag = f'<script type="application/ld+json">{json_ld(website)}</script>'
        source = source.replace("</head>", f"  {tag}\n</head>", 1)

    write(path, source)


def related_block(links: list[tuple[str, str]]) -> str:
    existing = [(href, label) for href, label in links if route_file(href)]
    items = "".join(f'<li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>' for href, label in existing)
    return (
        '<section class="seo-related" aria-labelledby="seo-related-title">'
        '<h2 id="seo-related-title">Related checks</h2>'
        f'<ul>{items}</ul></section>'
    )


def patch_priority_clusters() -> None:
    for route, links in CLUSTERS.items():
        path = route_file(route)
        if not path:
            raise RuntimeError(f"Priority route missing: {route}")
        source = path.read_text(encoding="utf-8", errors="replace")
        source = re.sub(
            r'\s*<h2>Related checks</h2>\s*(?:<ul>.*?</ul>)?',
            "\n",
            source,
            count=1,
            flags=re.I | re.S,
        )
        source = re.sub(
            r'\s*<section class="seo-related".*?</section>',
            "\n",
            source,
            flags=re.I | re.S,
        )
        block = related_block(links)
        anchor = '<section class="cta">'
        if anchor in source:
            source = source.replace(anchor, block + "\n" + anchor, 1)
        else:
            source = insert_before_main_end(source, block)
        write(path, source)


def patch_legacy_tools() -> None:
    for route, config in LEGACY_TOOLS.items():
        path = route_file(route)
        if not path:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        source = replace_title(source, config["title"])
        source = upsert_meta_description(source, config["description"])
        source = replace_first_h1(source, config["h1"])
        marker = f'id="seo-legacy-context-{route.strip("/")}"'
        if marker not in source:
            block = (
                f'<section {marker}>'
                '<h2>Need the detailed sharing guide?</h2>'
                f'<p>{html.escape(config["copy"])}</p>'
                f'<p><a href="{config["hub"]}">{html.escape(config["hub_label"])}</a></p>'
                '</section>'
            )
            source = insert_before_main_end(source, block)
        source = ensure_schema(source, route, config["title"], config["description"])
        write(path, source)


def patch_secondary_pages() -> None:
    for route, (copy, links) in SECONDARY_PAGES.items():
        path = route_file(route)
        if not path:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        marker = f'id="seo-context-{route.strip("/")}"'
        if marker not in source:
            items = "".join(
                f'<li><a href="{href}">{html.escape(label)}</a></li>'
                for href, label in links
                if route_file(href)
            )
            block = (
                f'<section {marker}>'
                '<h2>Before you share</h2>'
                f'<p>{html.escape(copy)}</p>'
                + (f'<ul>{items}</ul>' if items else '')
                + '</section>'
            )
            source = insert_before_main_end(source, block)
        title_match = re.search(r"<title>(.*?)</title>", source, flags=re.I | re.S)
        desc_match = re.search(r'<meta\s+name=["\']description["\'][^>]*content=["\']([^"\']*)', source, flags=re.I)
        title = html.unescape(title_match.group(1).strip()) if title_match else "Can I Share This?"
        description = html.unescape(desc_match.group(1).strip()) if desc_match else copy
        source = ensure_schema(source, route, title, description)
        write(path, source)


def validate() -> None:
    home_path = route_file("/")
    if not home_path:
        raise RuntimeError("Homepage not found during validation")
    home = home_path.read_text(encoding="utf-8", errors="replace")
    for href, _, _ in PRIORITY_LINKS:
        if f'href="{href}"' not in home:
            raise RuntimeError(f"Homepage is missing priority link {href}")

    for route, links in CLUSTERS.items():
        route_path = route_file(route)
        if not route_path:
            raise RuntimeError(f"Priority route missing during validation: {route}")
        source = route_path.read_text(encoding="utf-8", errors="replace")
        if source.count('class="seo-related"') != 1:
            raise RuntimeError(f"Expected exactly one related-links block on {route}")
        for href, _ in links:
            if route_file(href) and f'href="{href}"' not in source:
                raise RuntimeError(f"{route} is missing internal link to {href}")

    for route, config in LEGACY_TOOLS.items():
        path = route_file(route)
        if not path:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        if config["title"] not in source or f'href="{config["hub"]}"' not in source:
            raise RuntimeError(f"Legacy route differentiation failed for {route}")


def main() -> None:
    patch_homepage()
    patch_priority_clusters()
    patch_legacy_tools()
    patch_secondary_pages()
    validate()
    print("Applied production SEO architecture and internal-linking improvements")


if __name__ == "__main__":
    main()
