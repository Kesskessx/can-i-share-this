#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

TITLE = 'Is This Link Safe? Scam, Phishing & Malware URL Checker'
DESCRIPTION = ('Check suspicious links for scams, phishing, malware, malicious downloads and dangerous redirects '
               'before you open them. Free, privacy-first URL safety checker.')
VISIBLE_SUB = ('Paste a suspicious link. Check for scams, phishing, malware, malicious downloads and dangerous '
               'redirects before you open it.')


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
        '<meta property="og:description" content="Free link checker for scam, phishing, malware, malicious-download and redirect warning signs.">',
        'Open Graph description',
    )
    source = replace_once(
        source,
        '"description":"Simple link safety checks for suspicious URLs."',
        '"description":"Free privacy-first URL safety checker for suspicious links, scams, phishing, malware, malicious downloads and dangerous redirects."',
        'structured-data description',
    )
    source = replace_once(
        source,
        '<p class="eyebrow">Link safety checker</p>',
        '<p class="eyebrow">Scam · Phishing · Malware Link Checker</p>',
        'visible eyebrow',
    )
    source = replace_once(
        source,
        '<p class="sub">Paste a suspicious link. We’ll check the warning signs before you open it.</p>',
        f'<p class="sub">{VISIBLE_SUB}</p>',
        'visible description',
    )

    # Guard against accidental keyword-stuffing regressions: keep one concise title and description only.
    if source.count(f'<title>{TITLE}</title>') != 1:
        raise RuntimeError('Expected exactly one optimized title')
    if source.count(f'<meta name="description" content="{DESCRIPTION}">') != 1:
        raise RuntimeError('Expected exactly one optimized meta description')
    if '<meta name="keywords"' in source.lower():
        raise RuntimeError('Do not add meta keywords; they are not used for Google ranking')

    HOME.write_text(source, encoding='utf-8')
    print('Applied homepage Google search title/snippet SEO')


if __name__ == '__main__':
    main()
