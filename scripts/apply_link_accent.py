#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-link-accent-style">
:root{--link-accent:#5366d7}
@media(prefers-color-scheme:dark){:root{--link-accent:#8EA2FF}}
.header-dropdown a,
.header-mobile-links a,
.footer-resource-links a,
.under-form a{color:var(--link-accent)!important}
.header-dropdown a:hover,
.header-mobile-links a:hover,
.footer-resource-links a:hover,
.under-form a:hover{color:var(--link-accent)!important;text-decoration:underline;text-underline-offset:3px}
.under-form a{text-decoration:none}
.footer-resource-links a{opacity:.88}
.footer-resource-links a:hover{opacity:1}
.header-dropdown a:focus-visible,
.header-mobile-links a:focus-visible,
.footer-resource-links a:focus-visible,
.under-form a:focus-visible{outline:2px solid var(--link-accent);outline-offset:3px;border-radius:4px}
</style>
'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')
    source = re.sub(
        r'\s*<style id="cist-link-accent-style">.*?</style>',
        '',
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace('</head>', STYLE + '\n</head>', 1)

    required = [
        '--link-accent:#8EA2FF',
        '.header-dropdown a',
        '.header-mobile-links a',
        '.footer-resource-links a',
        '.under-form a',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Link accent guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied blue-violet navigation link accent')


if __name__ == '__main__':
    main()
