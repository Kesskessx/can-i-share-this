#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-homepage-brand-accent">
.hero-safe{color:var(--cist-accent,#6578e8)}
@media(prefers-color-scheme:dark){.hero-safe{color:var(--cist-accent,#8ea2ff)}}
</style>
'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')
    old = '<h1 id="page-title">Check anything before you trust it</h1>'
    new = '<h1 id="page-title">Check anything before you <span class="hero-safe">trust it</span></h1>'

    if old not in source:
        if new in source and 'id="cist-homepage-brand-accent"' in source:
            print('Homepage brand accent already applied')
            return
        raise RuntimeError('Homepage H1 source text not found')

    source = source.replace(old, new, 1)
    source = source.replace('</head>', STYLE + '\n</head>', 1)

    if source.count('class="hero-safe"') != 1:
        raise RuntimeError('Expected exactly one accent in homepage H1')
    if '<p class="eyebrow">Links · QR · Email · Scam Safety</p>' not in source:
        raise RuntimeError('Homepage universal-safety eyebrow must remain unchanged')
    if 'Can I Share This? is an independent online safety checker for suspicious links, QR codes, email addresses, downloads and shortened URLs.' not in source:
        raise RuntimeError('Homepage entity description must remain unchanged')

    HOME.write_text(source, encoding='utf-8')
    print('Applied homepage trust-word accent')


if __name__ == '__main__':
    main()
