#!/usr/bin/env python3
"""Final SEO quality pass for v51.

Runs after all page generators. It keeps structured data consistent, removes
repeated related-link blocks on priority pages, improves high-opportunity
titles/meta, enriches the contact page, and builds a focused internal-link
network without creating new indexable routes.
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "seo" / "SEO_ROUTE_MANIFEST.json"
HOST = "https://canisharethis.com"
def resolved_date_modified() -> str:
    override = os.getenv("CIST_CONTENT_DATE", "").strip()
    if re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", override):
        return override
    try:
        value = subprocess.check_output(
            ["git", "show", "-s", "--format=%cs", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", value):
            return value
    except (OSError, subprocess.SubprocessError):
        pass
    return "2026-09-26"


DATE_MODIFIED = resolved_date_modified()

PREFERRED_HUBS = {
    "universal-safety": "/supported-checks",
    "trust-methodology": "/methodology",
    "scam-prevention": "/scam-prevention",
    "link-safety": "/safe-link-checker",
    "google-drive": "/google-drive-link-checker",
    "dropbox": "/dropbox-link-checker",
    "email-safety": "/email-safety-checker",
}

TITLE_OVERRIDES = {
    "/safe-link-checker": "Safe Link Checker — Check a URL Before You Open It",
    "/phishing-link-checker": "Phishing Link Checker — Check a Suspicious URL",
    "/malware-link-checker": "Malware Link Checker — Check a Suspicious URL",
    "/download-link-checker": "Download Link Checker — Check a File URL Before Opening",
    "/google-drive-link-checker": "Google Drive Link Checker — Test Access Before Sharing",
    "/is-my-google-drive-link-public": "Is My Google Drive Link Public? Check Sharing Access",
    "/dropbox-link-checker": "Dropbox Link Checker — Test Access Before Sharing",
    "/dropbox-shared-link-not-working": "Dropbox Shared Link Not Working? 6 Fixes to Try",
    "/how-to-check-if-a-link-is-safe": "How to Check If a Link Is Safe Before Clicking It",
}

DESCRIPTION_OVERRIDES = {
    "/is-my-google-drive-link-public": (
        "Check whether a Google Drive link is accessible to anyone with the link or restricted "
        "to specific accounts. Verify recipient access before sharing."
    ),
    "/how-link-scanning-works": (
        "See how CanIShareThis evaluates URL structure, redirects, domain context, "
        "reputation, privacy signals and link types—and where scanning has limits."
    ),
    "/scam-warning-signs": (
        "Learn common scam warning signs across email, text, social media, marketplaces, "
        "crypto, payments and impersonation attempts, with official safety references."
    ),
}

PRIORITY_LINKS = {
    "/": [
        ("/safe-link-checker", "Safe link checker"),
        ("/phishing-link-checker", "Phishing link checker"),
        ("/malware-link-checker", "Malware link checker"),
        ("/download-link-checker", "Download link checker"),
        ("/google-drive-link-checker", "Google Drive link checker"),
        ("/google-drive-link-not-working", "Fix a Google Drive link"),
        ("/dropbox-link-checker", "Dropbox link checker"),
        ("/dropbox-shared-link-not-working", "Fix a Dropbox shared link"),
        ("/how-to-check-if-a-link-is-safe", "How to check if a link is safe"),
    ],
    "/safe-link-checker": [
        ("/phishing-link-checker", "Phishing link checker"),
        ("/malware-link-checker", "Malware link checker"),
        ("/download-link-checker", "Download link checker"),
        ("/how-to-check-if-a-link-is-safe", "Manual link safety guide"),
        ("/google-drive-link-checker", "Google Drive link checker"),
    ],
    "/phishing-link-checker": [
        ("/safe-link-checker", "Safe link checker"),
        ("/malware-link-checker", "Malware link checker"),
        ("/scam-warning-signs", "Common scam warning signs"),
        ("/what-to-do-after-clicking-a-phishing-link", "What to do after clicking"),
        ("/how-to-check-if-a-link-is-safe", "Check a link before clicking"),
    ],
    "/malware-link-checker": [
        ("/safe-link-checker", "Safe link checker"),
        ("/download-link-checker", "Download link checker"),
        ("/phishing-link-checker", "Phishing link checker"),
        ("/how-to-check-if-a-link-is-safe", "Manual link safety guide"),
    ],
    "/download-link-checker": [
        ("/malware-link-checker", "Malware link checker"),
        ("/safe-link-checker", "Safe link checker"),
        ("/phishing-link-checker", "Phishing link checker"),
        ("/how-to-check-if-a-link-is-safe", "Check a link before clicking"),
    ],
    "/google-drive-link-checker": [
        ("/google-drive-link-not-working", "Fix a Drive link that is not working"),
        ("/is-my-google-drive-link-public", "Check whether the Drive link is public"),
        ("/google-drive-permission-checker", "Check Drive permissions"),
        ("/check-google-drive-link-without-signing-in", "Test without signing in"),
    ],
    "/google-drive-link-not-working": [
        ("/google-drive-link-checker", "Google Drive link checker"),
        ("/is-my-google-drive-link-public", "Check whether the Drive link is public"),
        ("/google-drive-permission-checker", "Check Drive permissions"),
        ("/check-google-drive-link-without-signing-in", "Test without signing in"),
    ],
    "/is-my-google-drive-link-public": [
        ("/google-drive-link-checker", "Google Drive link checker"),
        ("/google-drive-link-not-working", "Fix a Drive link that is not working"),
        ("/google-drive-permission-checker", "Check Drive permissions"),
        ("/google-drive-anyone-with-the-link-vs-restricted", "Anyone with the link vs Restricted"),
    ],
    "/dropbox-link-checker": [
        ("/dropbox-shared-link-not-working", "Fix a Dropbox shared link"),
        ("/dropbox-permission-checker", "Check Dropbox permissions"),
        ("/check-dropbox-link-without-account", "Test without a Dropbox account"),
        ("/safe-link-checker", "General safe link checker"),
    ],
    "/dropbox-shared-link-not-working": [
        ("/dropbox-link-checker", "Dropbox link checker"),
        ("/dropbox-permission-checker", "Check Dropbox permissions"),
        ("/check-dropbox-link-without-account", "Test without a Dropbox account"),
        ("/safe-link-checker", "General safe link checker"),
    ],
    "/how-to-check-if-a-link-is-safe": [
        ("/safe-link-checker", "Safe link checker"),
        ("/phishing-link-checker", "Phishing link checker"),
        ("/malware-link-checker", "Malware link checker"),
        ("/download-link-checker", "Download link checker"),
        ("/scam-warning-signs", "Common scam warning signs"),
    ],
}

CTA_COPY = {
    "/google-drive-link-checker": (
        "Paste the exact Google Drive URL into the scanner before you send it.",
        "Check a Google Drive link",
    ),
    "/google-drive-link-not-working": (
        "Paste the exact Google Drive URL into the scanner to check the destination and recipient-facing access signals.",
        "Check the Drive link",
    ),
    "/is-my-google-drive-link-public": (
        "Paste the exact Google Drive URL into the scanner, then verify whether a recipient can open it without a specific invitation.",
        "Check the Drive link",
    ),
    "/dropbox-link-checker": (
        "Paste the exact Dropbox share URL into the scanner before you send it.",
        "Check a Dropbox link",
    ),
    "/dropbox-shared-link-not-working": (
        "Paste the exact Dropbox URL into the scanner to check the destination and recipient-facing access signals.",
        "Check the Dropbox link",
    ),
    "/download-link-checker": (
        "Paste the download URL before opening the file to review redirects, the destination domain and link context.",
        "Check the download link",
    ),
    "/phishing-link-checker": (
        "Paste the suspicious URL into the scanner before you sign in, pay, download or reply.",
        "Check the suspicious link",
    ),
    "/malware-link-checker": (
        "Paste the URL into the scanner before downloading or opening unexpected content.",
        "Check the link",
    ),
    "/safe-link-checker": (
        "Paste the URL into the scanner for a destination and risk-signal check before opening it.",
        "Check the link",
    ),
    "/how-to-check-if-a-link-is-safe": (
        "Use the scanner as a second check after reviewing the domain, sender and context manually.",
        "Scan the link",
    ),
}

OFFICIAL_SOURCES = {
    "/google-drive-link-checker": [
        ("https://support.google.com/drive/answer/2494822?hl=en", "Google Drive Help — sharing and access"),
    ],
    "/google-drive-link-not-working": [
        ("https://support.google.com/drive/answer/2494822?hl=en", "Google Drive Help — sharing and access"),
    ],
    "/is-my-google-drive-link-public": [
        ("https://support.google.com/drive/answer/2494822?hl=en", "Google Drive Help — sharing and access"),
    ],
    "/dropbox-link-checker": [
        ("https://help.dropbox.com/share/set-link-permissions", "Dropbox Help — shared link permissions"),
    ],
    "/dropbox-shared-link-not-working": [
        ("https://help.dropbox.com/share/shared-link-stopped-working", "Dropbox Help — troubleshoot shared links"),
        ("https://help.dropbox.com/share/set-link-permissions", "Dropbox Help — shared link permissions"),
    ],
}

STYLE = r"""
<style id="seo-quality-v51-style">
.seo-priority-network{max-width:900px;margin:24px auto 0;padding:0 2px}
.seo-priority-card{padding:clamp(18px,3vw,26px);border:1px solid var(--line,#dfe3ea);border-radius:18px;background:var(--card,#fff)}
.seo-priority-card h2{margin:0 0 8px;font-size:clamp(21px,3vw,27px);line-height:1.2;letter-spacing:-.02em}
.seo-priority-card p{margin:0 0 14px;max-width:72ch}
.seo-priority-links{display:flex;flex-wrap:wrap;gap:9px}
.seo-priority-links a{display:inline-flex;padding:9px 11px;border:1px solid var(--line,#dfe3ea);border-radius:999px;color:inherit;text-decoration:none;font-size:13px;font-weight:750}
.seo-priority-links a:hover{text-decoration:underline;text-underline-offset:3px}
.seo-priority-cta{margin-top:16px;padding-top:15px;border-top:1px solid var(--line,#dfe3ea)}
.seo-priority-cta a{display:inline-flex;margin-top:2px;padding:10px 13px;border-radius:11px;background:var(--accent,#6578e8);color:var(--accent-text,#fff);text-decoration:none;font-weight:800}
.seo-priority-sources{margin-top:15px;color:var(--muted,#69707d);font-size:13px}
.seo-priority-sources a{text-underline-offset:3px}
@media(max-width:680px){.seo-priority-network{margin-top:18px}.seo-priority-links{display:grid}.seo-priority-links a{border-radius:12px}}
</style>
"""

SCRIPT_RE = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.I | re.S)


def route_file(route: str) -> Path | None:
    if route == "/":
        candidates = [DIST / "index.html"]
    else:
        rel = route.strip("/")
        candidates = [DIST / f"{rel}.html", DIST / rel / "index.html", DIST / rel]
    return next((p for p in candidates if p.is_file()), None)


def set_title(doc: str, title: str) -> str:
    esc_text = html.escape(title)
    esc_attr = html.escape(title, quote=True)
    doc = re.sub(r"<title>.*?</title>", f"<title>{esc_text}</title>", doc, count=1, flags=re.I | re.S)
    for key, value in (("property", "og:title"), ("name", "twitter:title")):
        pattern = rf'(<meta\s+{key}=["\']{re.escape(value)}["\']\s+content=["\'])[^"\']*(["\'])'
        doc = re.sub(pattern, lambda m: m.group(1) + esc_attr + m.group(2), doc, count=1, flags=re.I)
    return doc


def set_description(doc: str, description: str) -> str:
    esc_attr = html.escape(description, quote=True)
    for key, value in (
        ("name", "description"),
        ("property", "og:description"),
        ("name", "twitter:description"),
    ):
        pattern = rf'(<meta\s+{key}=["\']{re.escape(value)}["\']\s+content=["\'])[^"\']*(["\'])'
        doc = re.sub(pattern, lambda m: m.group(1) + esc_attr + m.group(2), doc, count=1, flags=re.I)
    return doc


def extract_title(doc: str) -> str:
    m = re.search(r"<title>(.*?)</title>", doc, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""


def extract_description(doc: str) -> str:
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', doc, re.I)
    return html.unescape(m.group(1)).strip() if m else ""


def remove_old_related_blocks(doc: str) -> str:
    patterns = [
        r"<!--\s*cist-registry-links:start\s*-->.*?<!--\s*cist-registry-links:end\s*-->",
        r'<section\b[^>]*class=["\'][^"\']*\bseo-related\b[^"\']*["\'][^>]*>.*?</section>',
        r'<nav\b[^>]*class=["\'][^"\']*\brelated-section\b[^"\']*["\'][^>]*>.*?</nav>',
        r'<section\b[^>]*class=["\'][^"\']*\bcard\b[^"\']*["\'][^>]*>\s*<h2>\s*Related safety guides\s*</h2>.*?</section>',
        r'<section\b[^>]*class=["\'][^"\']*\bcard\b[^"\']*["\'][^>]*>\s*<h2>\s*Related checks\s*</h2>.*?</section>',
    ]
    for pattern in patterns:
        doc = re.sub(pattern, "", doc, flags=re.I | re.S)
    doc = re.sub(r"<!--\s*SEO_PRIORITY_NETWORK_START\s*-->.*?<!--\s*SEO_PRIORITY_NETWORK_END\s*-->", "", doc, flags=re.I | re.S)
    return doc


def add_style(doc: str) -> str:
    if 'id="seo-quality-v51-style"' in doc:
        return doc
    return re.sub(r"</head>", STYLE + "\n</head>", doc, count=1, flags=re.I)


def priority_block(route: str) -> str:
    links = "".join(
        f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for href, label in PRIORITY_LINKS[route]
    )
    cta = ""
    if route in CTA_COPY:
        text, label = CTA_COPY[route]
        cta = (
            '<div class="seo-priority-cta">'
            f"<p>{html.escape(text)}</p>"
            f'<a href="/">{html.escape(label)}</a>'
            "</div>"
        )
    sources = ""
    if route in OFFICIAL_SOURCES:
        source_links = " · ".join(
            f'<a href="{html.escape(url, quote=True)}" rel="noopener noreferrer">{html.escape(label)}</a>'
            for url, label in OFFICIAL_SOURCES[route]
        )
        sources = f'<div class="seo-priority-sources">Official references: {source_links}</div>'
    heading = "Popular safety checks" if route == "/" else "Related checks"
    return (
        "\n<!-- SEO_PRIORITY_NETWORK_START -->\n"
        '<section class="seo-priority-network" aria-label="Related safety checks">'
        '<div class="seo-priority-card">'
        f"<h2>{heading}</h2>"
        '<p>Use the most relevant checker or guide for the exact link, platform or risk you are reviewing.</p>'
        f'<div class="seo-priority-links">{links}</div>'
        f"{cta}{sources}"
        "</div></section>\n"
        "<!-- SEO_PRIORITY_NETWORK_END -->\n"
    )


def inject_priority_network(doc: str, route: str) -> str:
    doc = remove_old_related_blocks(doc)
    doc = add_style(doc)
    block = priority_block(route)
    if re.search(r"</main>", doc, re.I):
        return re.sub(r"</main>", block + "</main>", doc, count=1, flags=re.I)
    return re.sub(r"</body>", block + "</body>", doc, count=1, flags=re.I)


def enrich_contact(doc: str) -> str:
    marker = "<!-- SEO_CONTACT_ENRICHMENT -->"
    if marker in doc:
        return doc
    extra = f"""
{marker}
<section class="card">
  <h2>What to include in your message</h2>
  <p>Describe the organization, product, publication, or integration you represent and the specific reason you are contacting CanIShareThis. For product or API discussions, include the use case, expected audience, and any technical requirements that would help us evaluate fit.</p>
  <p>For press or research inquiries, include the topic, deadline, and the claims or product behavior you want clarified. For security-related questions, do not email passwords, private access tokens, recovery codes, payment details, or sensitive personal data.</p>
  <p>CanIShareThis focuses on link, sharing, scam, and recipient-access safety. The site does not provide guarantees that a URL, sender, file, company, or transaction is safe, so business discussions should not be treated as a substitute for independent security review.</p>
</section>
"""
    return re.sub(r"</main>", extra + "</main>", doc, count=1, flags=re.I)


def json_has_type(payload, wanted: str) -> bool:
    if isinstance(payload, dict):
        t = payload.get("@type")
        if t == wanted or (isinstance(t, list) and wanted in t):
            return True
    return False


def prune_breadcrumb(payload):
    if isinstance(payload, dict):
        if json_has_type(payload, "BreadcrumbList"):
            return None
        if "@graph" in payload and isinstance(payload["@graph"], list):
            graph = [x for x in (prune_breadcrumb(x) for x in payload["@graph"]) if x is not None]
            payload = dict(payload)
            payload["@graph"] = graph
        return payload
    if isinstance(payload, list):
        return [x for x in (prune_breadcrumb(x) for x in payload) if x is not None]
    return payload


def sync_webpage_schema(payload, title: str, description: str):
    if isinstance(payload, dict):
        out = dict(payload)
        if json_has_type(out, "WebPage"):
            if title:
                out["name"] = title
            if description:
                out["description"] = description
            out["dateModified"] = DATE_MODIFIED
        if "@graph" in out and isinstance(out["@graph"], list):
            out["@graph"] = [sync_webpage_schema(x, title, description) for x in out["@graph"]]
        return out
    if isinstance(payload, list):
        return [sync_webpage_schema(x, title, description) for x in payload]
    return payload


def clean_jsonld(doc: str, route: str, route_meta: dict, by_path: dict) -> str:
    title = extract_title(doc)
    description = extract_description(doc)
    should_sync = route in set(PRIORITY_LINKS) | set(DESCRIPTION_OVERRIDES)

    def repl(match: re.Match) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        if "application/ld+json" not in attrs.lower():
            return match.group(0)
        try:
            payload = json.loads(body.strip())
        except Exception:
            return match.group(0)
        payload = prune_breadcrumb(payload)
        if payload is None or payload == []:
            return ""
        if should_sync:
            payload = sync_webpage_schema(payload, title, description)
        return f"<script{attrs}>{json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}</script>"

    doc = SCRIPT_RE.sub(repl, doc)

    if route == "/" or not route_meta.get("index"):
        return doc

    items = [{"@type": "ListItem", "position": 1, "name": "Can I Share This?", "item": HOST + "/"}]
    hub_path = PREFERRED_HUBS.get(route_meta.get("cluster"))
    if hub_path and hub_path != route and hub_path in by_path:
        hub = by_path[hub_path]
        hub_label = hub.get("breadcrumbLabel") or hub.get("primaryKeyword") or hub_path.strip("/").replace("-", " ")
        items.append({"@type": "ListItem", "position": 2, "name": hub_label, "item": HOST + hub_path})
    current_label = route_meta.get("breadcrumbLabel") or route_meta.get("primaryKeyword") or route.strip("/").replace("-", " ")
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": current_label, "item": HOST + route})
    payload = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
    script = '<script id="cist-breadcrumb-schema" type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return re.sub(r"</head>", script + "\n</head>", doc, count=1, flags=re.I)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    routes = [r for r in manifest.get("routes", []) if r.get("status") == "active"]
    by_path = {r["path"]: r for r in routes}

    touched = set()

    for route, title in TITLE_OVERRIDES.items():
        path = route_file(route)
        if not path:
            raise RuntimeError(f"Missing priority page: {route}")
        doc = path.read_text(encoding="utf-8")
        path.write_text(set_title(doc, title), encoding="utf-8")
        touched.add(route)

    for route, description in DESCRIPTION_OVERRIDES.items():
        path = route_file(route)
        if not path:
            raise RuntimeError(f"Missing metadata page: {route}")
        doc = path.read_text(encoding="utf-8")
        path.write_text(set_description(doc, description), encoding="utf-8")
        touched.add(route)

    for route in PRIORITY_LINKS:
        path = route_file(route)
        if not path:
            raise RuntimeError(f"Missing internal-link priority page: {route}")
        doc = path.read_text(encoding="utf-8")
        path.write_text(inject_priority_network(doc, route), encoding="utf-8")
        touched.add(route)

    contact = route_file("/contact")
    if not contact:
        raise RuntimeError("Missing /contact page")
    contact.write_text(enrich_contact(contact.read_text(encoding="utf-8")), encoding="utf-8")
    touched.add("/contact")

    schema_changes = 0
    for route_meta in routes:
        route = route_meta["path"]
        path = route_file(route)
        if not path:
            continue
        before = path.read_text(encoding="utf-8")
        after = clean_jsonld(before, route, route_meta, by_path)
        if after != before:
            path.write_text(after, encoding="utf-8")
            schema_changes += 1

    print(
        "SEO quality pass complete: "
        f"{len(touched)} priority/contact routes updated, "
        f"{schema_changes} pages normalized for structured data."
    )


if __name__ == "__main__":
    main()
