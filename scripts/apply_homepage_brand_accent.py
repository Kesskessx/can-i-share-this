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
    old = '<h1 id="page-title">Is this link safe?</h1>'
    new = '<h1 id="page-title">Is this link <span class="hero-safe">safe?</span></h1>'

    if old not in source:
        if new in source and 'id="cist-homepage-brand-accent"' in source:
            print('Homepage brand accent already applied')
            return
        raise RuntimeError('Homepage H1 source text not found')

    source = source.replace(old, new, 1)
    source = source.replace('</head>', STYLE + '\n</head>', 1)

    if source.count('class="hero-safe"') != 1:
        raise RuntimeError('Expected exactly one safe accent in homepage H1')
    if '<p class="eyebrow">Scam · Phishing · Malware Link Checker</p>' not in source:
        raise RuntimeError('Homepage eyebrow must remain unchanged')
    if 'Paste a suspicious link. Check for scams, phishing, malware, malicious downloads and dangerous redirects before you open it.' not in source:
        raise RuntimeError('Homepage description must remain unchanged')

    HOME.write_text(source, encoding='utf-8')
    print('Applied homepage safe word accent')


if __name__ == '__main__':
    main()
