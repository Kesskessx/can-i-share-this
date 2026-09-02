#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Can I Share This?">
  <rect width="64" height="64" fill="#000000"/>
  <path d="M31 10H23C13 10 7 18 7 32s6 22 16 22h8" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round"/>
  <text x="16.2" y="33.8" fill="#ffffff" font-family="Arial,Helvetica,sans-serif" font-size="4.8" font-weight="700" letter-spacing="0.18">I SHARE THIS</text>
  <text x="35" y="51" fill="#6578e8" font-family="Arial,Helvetica,sans-serif" font-size="48" font-weight="900">?</text>
</svg>\n'''


def main() -> None:
    if not DIST.is_dir():
        raise RuntimeError('dist directory not found')
    (DIST / 'favicon.svg').write_text(FAVICON, encoding='utf-8')
    print('Applied C? brand favicon')


if __name__ == '__main__':
    main()
