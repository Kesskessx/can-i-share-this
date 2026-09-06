#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-homepage-title-wrap-fix">
.hero h1{
  max-width:980px!important;
  text-wrap:balance;
}
.hero h1 .cist-title-end{
  white-space:nowrap;
}
@media(max-width:700px){
  .hero h1{max-width:360px!important}
}
</style>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    # Keep the final phrase together so "it." can never become an orphan line.
    source, count = re.subn(
        r'(<h1\b[^>]*>)\s*Check it before you trust it\.\s*(</h1>)',
        r'\1Check it before you <span class="cist-title-end">trust it.</span>\2',
        source,
        count=1,
        flags=re.I | re.S,
    )
    if count != 1:
        raise RuntimeError(f'Homepage title wrap fix failed: H1 replaced {count} times')

    if 'id="cist-homepage-title-wrap-fix"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    required = [
        'class="cist-title-end">trust it.</span>',
        'id="cist-homepage-title-wrap-fix"',
        'white-space:nowrap',
        'max-width:980px',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Homepage title wrap guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied balanced homepage title with non-breaking final phrase')


if __name__ == '__main__':
    main()
