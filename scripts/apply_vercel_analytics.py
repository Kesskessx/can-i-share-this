#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SCRIPT = '<script defer src="/_vercel/insights/script.js"></script>'


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist directory not found')

    changed = 0
    for page in DIST.rglob('*.html'):
        source = page.read_text(encoding='utf-8')
        if '/_vercel/insights/script.js' in source:
            continue
        if '</body>' not in source:
            continue
        source = source.replace('</body>', f'{SCRIPT}\n</body>', 1)
        page.write_text(source, encoding='utf-8')
        changed += 1

    print(f'Applied Vercel Web Analytics to {changed} HTML pages')


if __name__ == '__main__':
    main()
