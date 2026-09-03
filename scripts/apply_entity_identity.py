#!/usr/bin/env python3
"""Keep Can I Share This? identity signals consistent across generated pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

APP_NAME = '<meta name="application-name" content="Can I Share This?">'
OG_SITE_NAME = '<meta property="og:site_name" content="Can I Share This?">'
STYLE = (
    '<style id="cist-entity-style">'
    '.entity-faq{margin-top:10px}.entity-faq summary{cursor:pointer;font-weight:750}'
    '.entity-faq p{max-width:620px;margin:8px auto 0;color:var(--muted,#6d7480);font-size:12px}'
    '</style>'
)
FAQ = (
    '<details id="cist-entity-faq" class="entity-faq">'
    '<summary>Is Can I Share This? related to ShareThis?</summary>'
    '<p>No. Can I Share This? is an independent safety-checking service available at '
    'canisharethis.com and is not affiliated with ShareThis.</p>'
    '</details>'
)


def ensure_meta(source: str, pattern: str, tag: str) -> str:
    if re.search(pattern, source, flags=re.I):
        return re.sub(pattern, tag, source, count=1, flags=re.I)
    if not re.search(r'</head>', source, flags=re.I):
        raise RuntimeError('Generated page has no closing head tag')
    return re.sub(r'</head>', tag + '\n</head>', source, count=1, flags=re.I)


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist directory not found')

    pages = sorted(DIST.glob('*.html'))
    if not pages:
        raise RuntimeError('No generated HTML pages found')

    changed = 0
    for page in pages:
        source = page.read_text(encoding='utf-8', errors='strict')
        original = source

        source = ensure_meta(
            source,
            r'<meta\b[^>]*\bname=["\']application-name["\'][^>]*>',
            APP_NAME,
        )
        source = ensure_meta(
            source,
            r'<meta\b[^>]*\bproperty=["\']og:site_name["\'][^>]*>',
            OG_SITE_NAME,
        )

        if page.name == 'index.html':
            if 'id="cist-entity-style"' not in source:
                source = re.sub(r'</head>', STYLE + '\n</head>', source, count=1, flags=re.I)
            if 'id="cist-entity-faq"' not in source:
                if re.search(r'</footer>', source, flags=re.I):
                    source = re.sub(r'</footer>', FAQ + '</footer>', source, count=1, flags=re.I)
                elif re.search(r'<footer\b', source, flags=re.I):
                    source = re.sub(r'<footer\b', FAQ + '<footer', source, count=1, flags=re.I)
                else:
                    raise RuntimeError('Homepage has no footer for entity clarification')

        if source != original:
            page.write_text(source, encoding='utf-8')
            changed += 1

    home = (DIST / 'index.html').read_text(encoding='utf-8')
    required = [
        'Check anything before you trust it',
        'id="cist-entity-graph"',
        'id="cist-entity-faq"',
        'content="Can I Share This?"',
        'not affiliated with ShareThis',
    ]
    for value in required:
        if value not in home:
            raise RuntimeError(f'Missing homepage entity signal: {value}')

    print(f'Applied consistent brand/entity metadata to {changed} pages')


if __name__ == '__main__':
    main()
