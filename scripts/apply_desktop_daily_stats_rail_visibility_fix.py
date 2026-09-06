#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-desktop-daily-rail-visibility-fix">
@media(min-width:1180px){
  #cist-daily-rail.cist-daily-rail{
    display:block!important;
    left:auto!important;
    right:16px!important;
    width:clamp(178px,calc((100vw - 800px)/2 - 20px),240px)!important;
    top:144px!important;
  }
}
@media(min-width:1450px){
  #cist-daily-rail.cist-daily-rail{right:24px!important}
}
@media(max-width:1179px){
  #cist-daily-rail.cist-daily-rail{display:none!important}
}
</style>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    if 'id="cist-desktop-daily-rail"' not in source and 'id="cist-daily-rail"' not in source:
        raise RuntimeError('Daily stats rail not found')
    if 'id="cist-desktop-daily-rail-visibility-fix"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)
    HOME.write_text(source, encoding='utf-8')
    print('Applied robust desktop stats rail visibility for zoomed desktop viewports')


if __name__ == '__main__':
    main()
