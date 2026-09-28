#!/usr/bin/env python3
"""Final answer-engine optimization for link-safety discovery.

The homepage already owns the "is this link safe" intent in the SEO registry.
This pass strengthens that canonical instead of creating a competing route.
It also makes the product definition, methodology and crawler access explicit
without changing scanner behavior, public URLs or API contracts.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
HOME = DIST / "index.html"
SAFE = DIST / "safe-link-checker.html"
METHOD = DIST / "methodology.html"

TITLE = "Is This Link Safe? Free URL Safety Checker — Can I Share This?"
DESCRIPTION = (
    "Check if a link is safe before opening it. Can I Share This? analyzes the final destination, "
    "redirects, suspicious URL patterns and available reputation signals."
)
ENTITY_SENTENCE = (
    "Can I Share This? is a free link safety checker that analyzes URLs before you open or share them."
)
MARKER_START = "<!-- CIST_AEO_2026_09_28_START -->"
MARKER_END = "<!-- CIST_AEO_2026_09_28_END -->"


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Missing generated file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8")


def upsert_meta(source: str, key: str, value: str, *, prop: bool = False) -> str:
    attr = "property" if prop else "name"
    escaped = html.escape(value, quote=True)
    pattern = rf'(<meta\s+{attr}=["\']{re.escape(key)}["\']\s+content=["\'])[^"\']*(["\'])'
    if re.search(pattern, source, re.I):
        return re.sub(pattern, lambda m: m.group(1) + escaped + m.group(2), source, count=1, flags=re.I)
    if "</head>" not in source:
        raise RuntimeError(f"Cannot add metadata {key}: closing head missing")
    return source.replace("</head>", f'<meta {attr}="{html.escape(key, quote=True)}" content="{escaped}">\n</head>', 1)


def set_title(source: str, title: str) -> str:
    escaped = html.escape(title)
    source, count = re.subn(r"<title>.*?</title>", f"<title>{escaped}</title>", source, count=1, flags=re.I | re.S)
    if count != 1:
        raise RuntimeError("Homepage title not found")
    source = upsert_meta(source, "og:title", title, prop=True)
    source = upsert_meta(source, "twitter:title", title)
    return source


def set_description(source: str, description: str) -> str:
    source = upsert_meta(source, "description", description)
    source = upsert_meta(source, "og:description", description, prop=True)
    source = upsert_meta(source, "twitter:description", description)
    return source


def strip_marker_block(source: str) -> str:
    return re.sub(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        "",
        source,
        flags=re.S,
    )


def add_jsonld(source: str, script_id: str, payload: dict) -> str:
    source = re.sub(
        rf'\s*<script\s+id=["\']{re.escape(script_id)}["\'][^>]*>.*?</script>',
        "",
        source,
        flags=re.I | re.S,
    )
    tag = (
        f'<script id="{script_id}" type="application/ld+json">'
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        + "</script>"
    )
    if "</head>" not in source:
        raise RuntimeError(f"Cannot insert {script_id}: closing head missing")
    return source.replace("</head>", tag + "\n</head>", 1)


def patch_homepage() -> None:
    source = read(HOME)
    source = strip_marker_block(source)
    source = set_title(source, TITLE)
    source = set_description(source, DESCRIPTION)

    source, count = re.subn(
        r'(<h1\s+id=["\']page-title["\'][^>]*>).*?(</h1>)',
        r'\1Is this link safe?\2',
        source,
        count=1,
        flags=re.I | re.S,
    )
    if count != 1:
        raise RuntimeError("Homepage page-title H1 not found")

    source, count = re.subn(
        r'<p\s+class=["\']sub["\'][^>]*>.*?</p>',
        (
            '<p class="sub" id="checker-intro">'
            + html.escape(ENTITY_SENTENCE)
            + " Paste a suspicious URL to inspect its final destination, redirects and available scam, phishing and reputation signals."
            + "</p>"
        ),
        source,
        count=1,
        flags=re.I | re.S,
    )
    if count != 1:
        raise RuntimeError("Homepage hero description not found")

    source = re.sub(
        r'(<form\s+id=["\']scan-form["\'][^>]*)(>)',
        lambda m: m.group(1) + ' aria-describedby="checker-intro"' + m.group(2)
        if "aria-describedby=" not in m.group(1)
        else m.group(0),
        source,
        count=1,
        flags=re.I,
    )
    source = re.sub(
        r'(<input\s+id=["\']url["\'])(?![^>]*\bname=)',
        r'\1 name="url"',
        source,
        count=1,
        flags=re.I,
    )

    answer_block = f"""
{MARKER_START}
<section id="cist-answer-engine" class="seo-priority-network" aria-labelledby="cist-answer-engine-title">
  <div class="seo-priority-card">
    <h2 id="cist-answer-engine-title">What does this link checker check?</h2>
    <p><strong>{html.escape(ENTITY_SENTENCE)}</strong> It checks the destination domain, redirect chain, suspicious URL structure, lookalike-domain patterns, risky download indicators and the reputation signals available to the scanner.</p>
    <p><strong>Can it guarantee a link is safe?</strong> No. A low-risk result means the checks performed did not find obvious warning signs. New phishing pages, changed content and unknown malware can still evade scanners.</p>
    <p><strong>What should I do with a suspicious link?</strong> Check it before signing in, paying or downloading. If the result is caution or high risk, use the organization's official app or type its known website address yourself.</p>
    <div class="seo-priority-links">
      <a href="/safe-link-checker">Safe Link Checker</a>
      <a href="/methodology">How the check works</a>
      <a href="/supported-checks">Supported checks</a>
      <a href="/phishing-link-checker">Phishing Link Checker</a>
    </div>
  </div>
</section>
{MARKER_END}
"""
    anchor = "<!-- SEO_PRIORITY_NETWORK_START -->"
    if anchor not in source:
        raise RuntimeError("Homepage priority-network anchor missing")
    source = source.replace(anchor, answer_block + "\n" + anchor, 1)

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": "https://canisharethis.com/#link-safety-page",
                "url": "https://canisharethis.com/",
                "name": TITLE,
                "description": DESCRIPTION,
                "about": {"@type": "Thing", "name": "URL safety checking"},
                "isPartOf": {"@id": "https://canisharethis.com/#website"},
            },
            {
                "@type": "SoftwareApplication",
                "@id": "https://canisharethis.com/#link-safety-app",
                "name": "Can I Share This?",
                "url": "https://canisharethis.com/",
                "applicationCategory": "SecurityApplication",
                "operatingSystem": "Web",
                "isAccessibleForFree": True,
                "description": ENTITY_SENTENCE,
            },
            {
                "@type": "FAQPage",
                "@id": "https://canisharethis.com/#link-safety-faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What does Can I Share This? check?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "Can I Share This? checks destination and redirect behavior, suspicious URL structure, "
                                "lookalike-domain patterns, risky download indicators and available reputation signals."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Can a link checker guarantee a link is safe?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "No. A low-risk result means the performed checks did not find obvious warning signs; "
                                "new phishing pages, changed content and unknown malware can still evade scanners."
                            ),
                        },
                    },
                ],
            },
        ],
    }
    source = add_jsonld(source, "cist-aeo-link-safety-schema", schema)

    if source.count("<h1") != 1:
        raise RuntimeError("Homepage must keep exactly one H1")
    if source.count('id="cist-answer-engine"') != 1:
        raise RuntimeError("Homepage answer-engine block missing or duplicated")
    if ENTITY_SENTENCE not in html.unescape(source):
        raise RuntimeError("Homepage entity definition missing")

    write(HOME, source)


def patch_safe_link_checker() -> None:
    source = read(SAFE)
    source = re.sub(r'\s*<!-- CIST_SAFE_AEO_START -->.*?<!-- CIST_SAFE_AEO_END -->', "", source, flags=re.S)
    source = re.sub(r'\s+id=["\']cist-safe-answer["\']', "", source, flags=re.I)

    intro = (
        f'<p id="cist-safe-answer"><strong>{html.escape(ENTITY_SENTENCE)}</strong> '
        'Use this page when you want to check whether an unfamiliar URL shows phishing, scam, redirect, '
        'lookalike-domain or risky-download warning signs before opening it.</p>'
    )
    marker = '<section class="lead">'
    if marker not in source:
        raise RuntimeError("Safe Link Checker lead section missing")
    source = source.replace(marker, marker + intro, 1)

    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": "https://canisharethis.com/safe-link-checker#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Can a link be dangerous even if it uses HTTPS?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. HTTPS encrypts the connection, but phishing sites can also use HTTPS.",
                },
            },
            {
                "@type": "Question",
                "name": "Does a low-risk result mean the link has no virus?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "No. A low-risk result only means the checks performed did not find obvious warning signs.",
                },
            },
            {
                "@type": "Question",
                "name": "Should I open a shortened link?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "A short link is not automatically malicious, but it hides the destination and should be checked before sensitive actions.",
                },
            },
        ],
    }
    source = add_jsonld(source, "cist-safe-link-faq-schema", faq)

    if source.count('id="cist-safe-answer"') != 1:
        raise RuntimeError("Safe Link Checker answer block missing or duplicated")
    write(SAFE, source)


def patch_methodology() -> None:
    source = read(METHOD)
    marker = '<section class="card"><h2>What the quick scan checks</h2>'
    if marker not in source:
        raise RuntimeError("Methodology quick-scan section missing")
    entity = (
        '<section class="card" id="product-definition">'
        '<h2>What Can I Share This? is</h2>'
        f'<p><strong>{html.escape(ENTITY_SENTENCE)}</strong> '
        'The service is designed to explain observable link-safety signals before a user opens, shares, signs in, pays or downloads.</p>'
        '<p>Results are evidence summaries, not certifications. The methodology separates what the scanner observed from what it could not verify.</p>'
        '</section>'
    )
    source = re.sub(
        r'<section class="card" id="product-definition">.*?</section>',
        "",
        source,
        flags=re.S,
    )
    source = source.replace(marker, entity + marker, 1)

    source = re.sub(
        r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
        lambda m: _methodology_schema(m),
        source,
        count=2,
        flags=re.I | re.S,
    )
    if source.count('id="product-definition"') != 1:
        raise RuntimeError("Methodology product definition missing or duplicated")
    write(METHOD, source)


def _methodology_schema(match: re.Match) -> str:
    try:
        payload = json.loads(match.group(2))
    except Exception:
        return match.group(0)
    if isinstance(payload, dict) and payload.get("@type") == "WebPage":
        payload["dateModified"] = "2026-09-28"
        payload["about"] = {
            "@type": "Thing",
            "name": "URL safety assessment and link checker methodology",
        }
        payload["mainEntity"] = {
            "@type": "SoftwareApplication",
            "name": "Can I Share This?",
            "url": "https://canisharethis.com/",
            "applicationCategory": "SecurityApplication",
            "isAccessibleForFree": True,
            "description": ENTITY_SENTENCE,
        }
    return match.group(1) + json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + match.group(3)


def patch_robots() -> None:
    path = DIST / "robots.txt"
    current = read(path)
    sitemap = re.search(r"^Sitemap:\s*(\S+)", current, flags=re.I | re.M)
    sitemap_url = sitemap.group(1) if sitemap else "https://canisharethis.com/sitemap.xml"
    desired = (
        "User-agent: OAI-SearchBot\n"
        "Allow: /\n\n"
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {sitemap_url}\n"
    )
    write(path, desired)


def validate() -> None:
    home = read(HOME)
    safe = read(SAFE)
    method = read(METHOD)
    robots = read(DIST / "robots.txt")

    checks = [
        ("homepage title", f"<title>{html.escape(TITLE)}</title>" in home),
        ("homepage canonical", '<link rel="canonical" href="https://canisharethis.com/">' in home),
        ("homepage indexable", '<meta name="robots" content="index,follow">' in home),
        ("homepage H1", ">Is this link safe?</h1>" in home),
        ("homepage scanner", 'id="scan-form"' in home and 'id="url"' in home and 'id="analyze"' in home),
        ("homepage entity schema", 'id="cist-aeo-link-safety-schema"' in home),
        ("safe checker canonical", '<link rel="canonical" href="https://canisharethis.com/safe-link-checker">' in safe),
        ("safe checker definition", ENTITY_SENTENCE in html.unescape(safe)),
        ("methodology definition", ENTITY_SENTENCE in html.unescape(method)),
        ("OAI SearchBot access", "User-agent: OAI-SearchBot\nAllow: /" in robots),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        raise RuntimeError("AEO validation failed: " + ", ".join(failed))


def main() -> None:
    patch_homepage()
    patch_safe_link_checker()
    patch_methodology()
    patch_robots()
    validate()
    print("Applied ChatGPT/search answer-engine optimization without creating a competing route")


if __name__ == "__main__":
    main()
