#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

TITLE = 'Can I Share This? — Link, QR, Email & Scam Safety Checker'
DESCRIPTION = ('Check suspicious links, QR codes, email addresses, short links and downloads before opening or sharing '
               'them. Detect phishing, scams, tracking and other risk signals.')
VISIBLE_SUB = ('Can I Share This? is an independent online safety checker for suspicious links, QR codes, email '
               'addresses, downloads and shortened URLs.')

ENTITY_GRAPH = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": "https://canisharethis.com/#organization",
            "name": "Can I Share This?",
            "alternateName": "CanIShareThis",
            "url": "https://canisharethis.com/",
            "description": (
                "Independent online safety checker for suspicious links, QR codes, email addresses, shortened URLs "
                "and downloads. Can I Share This? is not affiliated with ShareThis."
            ),
            "sameAs": ["https://x.com/CanIshareLink"],
        },
        {
            "@type": "WebSite",
            "@id": "https://canisharethis.com/#website",
            "url": "https://canisharethis.com/",
            "name": "Can I Share This?",
            "publisher": {"@id": "https://canisharethis.com/#organization"},
            "description": (
                "Independent online safety checker for suspicious links, QR codes, email addresses, shortened URLs "
                "and downloads."
            ),
        },
        {
            "@type": "SoftwareApplication",
            "@id": "https://canisharethis.com/#app",
            "name": "Can I Share This?",
            "url": "https://canisharethis.com/",
            "applicationCategory": "SecurityApplication",
            "operatingSystem": "Web",
            "isAccessibleForFree": True,
            "publisher": {"@id": "https://canisharethis.com/#organization"},
            "description": (
                "Online safety checker for suspicious links, QR codes, email addresses, short links and downloads, "
                "with phishing, scam, tracking and risk-signal analysis."
            ),
        },
        {
            "@type": "FAQPage",
            "@id": "https://canisharethis.com/#identity-faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "Is Can I Share This? related to ShareThis?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": (
                            "No. Can I Share This? is an independent safety-checking service available at "
                            "canisharethis.com and is not affiliated with ShareThis."
                        ),
                    },
                }
            ],
        },
    ],
}


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Homepage SEO patch failed: {label} source text not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    source = replace_once(
        source,
        '<title>Is This Link Safe? — Can I Share This?</title>',
        f'<title>{TITLE}</title>',
        'title',
    )
    source = replace_once(
        source,
        '<meta name="description" content="Paste a suspicious link and get a simple scam, phishing, redirect and risky-download check before you open it.">',
        f'<meta name="description" content="{DESCRIPTION}">',
        'meta description',
    )
    source = replace_once(
        source,
        '<meta property="og:title" content="Is This Link Safe? — Can I Share This?">',
        f'<meta property="og:title" content="{TITLE}">',
        'Open Graph title',
    )
    source = replace_once(
        source,
        '<meta property="og:description" content="Paste a suspicious link. Analyze it before you open it.">',
        '<meta property="og:description" content="Independent safety checker for links, QR codes, email addresses, short links and downloads.">',
        'Open Graph description',
    )

    old_schema = (
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"WebSite","name":"Can I Share This?",'
        '"url":"https://canisharethis.com/","description":"Simple link safety checks for suspicious URLs."}'
        '</script>'
    )
    new_schema = (
        '<script id="cist-entity-graph" type="application/ld+json">'
        + json.dumps(ENTITY_GRAPH, ensure_ascii=False, separators=(',', ':'))
        + '</script>'
    )
    source = replace_once(source, old_schema, new_schema, 'entity structured data')

    source = replace_once(
        source,
        '<p class="eyebrow">Link safety checker</p>',
        '<p class="eyebrow">Links · QR · Email · Scam Safety</p>',
        'visible eyebrow',
    )
    source = replace_once(
        source,
        '<h1 id="page-title">Is this link safe?</h1>',
        '<h1 id="page-title">Check anything before you trust it</h1>',
        'H1',
    )
    source = replace_once(
        source,
        '<p class="sub">Paste a suspicious link. We’ll check the warning signs before you open it.</p>',
        f'<p class="sub">{VISIBLE_SUB}</p>',
        'visible description',
    )

    if source.count(f'<title>{TITLE}</title>') != 1:
        raise RuntimeError('Expected exactly one optimized title')
    if source.count(f'<meta name="description" content="{DESCRIPTION}">') != 1:
        raise RuntimeError('Expected exactly one optimized meta description')
    if source.count('id="cist-entity-graph"') != 1:
        raise RuntimeError('Expected exactly one entity graph')
    if '<meta name="keywords"' in source.lower():
        raise RuntimeError('Do not add meta keywords; they are not used for Google ranking')

    HOME.write_text(source, encoding='utf-8')
    print('Applied homepage entity, GEO and Google search SEO')


if __name__ == '__main__':
    main()
