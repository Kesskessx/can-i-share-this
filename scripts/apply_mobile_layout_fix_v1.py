#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-mobile-layout-fix-v1-style">
@media(max-width:700px){
  html,body{max-width:100%;overflow-x:hidden}
  body{min-width:0}
  .site-header .top,.header-mobile-inner{width:calc(100% - 20px)!important}
  main{width:calc(100% - 20px)!important;max-width:720px!important;padding:28px 0 48px!important}
  .hero{padding:18px 0 12px!important}
  .hero h1{font-size:clamp(34px,10.4vw,44px)!important;line-height:1.02!important;letter-spacing:-.04em!important;max-width:360px!important}
  .hero .sub{font-size:15px!important;line-height:1.4!important;margin:12px auto 18px!important;max-width:340px!important}

  #scan-form{width:100%!important;max-width:none!important;display:block!important;padding:6px!important;border-radius:16px!important}
  #scan-form .input-wrap{width:100%!important;min-width:0!important;height:50px!important;display:flex!important}
  #scan-form input,#scan-form textarea{min-width:0!important;width:100%!important;font-size:16px!important;line-height:1.25!important;padding:0 8px!important}
  #scan-form .paste,#scan-form button#paste{flex:0 0 auto!important;min-width:66px!important;max-width:82px!important;padding:0 10px!important;white-space:nowrap!important}
  #scan-form button[type="submit"]{display:block!important;width:100%!important;margin-top:6px!important;min-height:48px!important;height:48px!important}

  #image-safety-tools.image-tools{width:100%!important;max-width:none!important;margin-top:9px!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
  #image-safety-tools .image-tool{width:100%!important;min-width:0!important;min-height:46px!important;padding:8px!important;font-size:12px!important}
  #image-safety-tools .image-note{grid-column:1/-1!important;width:100%!important;margin:0!important;padding:0 4px!important;font-size:10.5px!important}

  .cist-input-types-v2{width:100%!important;display:flex!important;justify-content:center!important;align-items:center!important;flex-wrap:wrap!important;gap:5px 9px!important;margin:8px auto 0!important;line-height:1.25!important}
  .cist-input-types-v2 span{display:inline-flex!important;white-space:nowrap!important}
  .cist-input-types-v2 span:not(:last-child)::after{content:none!important}
  .cist-detected-type{width:100%!important;margin:7px auto 0!important;font-size:10.5px!important;line-height:1.35!important}

  #result{width:100%!important;margin-top:18px!important}
  #result-card{width:100%!important;min-width:0!important;padding:16px!important;border-radius:16px!important;overflow:hidden!important}
  .result-top{gap:10px!important;min-width:0!important}
  .result-main{min-width:0!important;flex:1 1 auto!important}
  .status-icon{width:36px!important;height:36px!important;font-size:18px!important}
  .result-main h2{font-size:24px!important;line-height:1.1!important;overflow-wrap:anywhere!important}
  .result-summary{font-size:13px!important;line-height:1.45!important;overflow-wrap:anywhere!important}

  .cist-result-v2-grid{grid-template-columns:1fr!important;gap:8px!important;margin-top:9px!important}
  .cist-result-v2-card,.cist-result-v2-card.cist-result-v2-wide{grid-column:auto!important;min-width:0!important;width:100%!important;padding:11px 12px!important;border-radius:12px!important}
  .cist-result-v2-value{font-size:13px!important;line-height:1.35!important}
  .cist-result-v2-note,.cist-result-v2-signals li{font-size:11.5px!important;line-height:1.4!important}
  .cist-result-v2-found{grid-template-columns:1fr!important;gap:6px!important}
  .cist-result-v2-found-item{width:100%!important;min-width:0!important;padding:8px 9px!important}
  .cist-result-v2-found-item strong{font-size:11.5px!important;overflow-wrap:anywhere!important}

  .actions,.consent-actions{display:grid!important;grid-template-columns:1fr!important;gap:8px!important}
  .actions>*,.consent-actions>*{width:100%!important;min-width:0!important}
  details.technical,#technical{width:100%!important;min-width:0!important}
  .tech-grid{grid-template-columns:1fr!important}
  .tech,.providers li{min-width:0!important;overflow-wrap:anywhere!important}

  .site-footer,footer{width:calc(100% - 20px)!important;max-width:720px!important}
}

@media(max-width:380px){
  .site-header .top,.header-mobile-inner{width:calc(100% - 16px)!important}
  main{width:calc(100% - 16px)!important}
  .hero h1{font-size:34px!important;max-width:320px!important}
  #result-card{padding:14px!important}
  #image-safety-tools.image-tools{grid-template-columns:1fr!important}
  #image-safety-tools .image-note{grid-column:auto!important}
  .header-brand{max-width:calc(100% - 68px)!important;font-size:13px!important}
  .header-mobile-toggle{min-width:54px!important;padding:7px 9px!important}
  .header-mobile-group{grid-template-columns:1fr!important;gap:4px!important}
  .header-mobile-label{margin:0!important}
  .header-mobile-links{gap:5px 11px!important}
  .site-footer,footer{width:calc(100% - 16px)!important}
}
</style>
'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')
    source = re.sub(
        r'\s*<style id="cist-mobile-layout-fix-v1-style">.*?</style>',
        '',
        source,
        count=1,
        flags=re.S,
    )

    if '</head>' not in source:
        raise RuntimeError('Homepage </head> not found')

    source = source.replace('</head>', STYLE + '\n</head>', 1)

    required = [
        'id="cist-mobile-layout-fix-v1-style"',
        '@media(max-width:700px)',
        'overflow-x:hidden',
        '#scan-form',
        'font-size:16px!important',
        '.cist-result-v2-grid',
        '.cist-result-v2-found',
        '.actions,.consent-actions',
        '@media(max-width:380px)',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Mobile layout guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied final mobile homepage and result layout fix V1')


if __name__ == '__main__':
    main()
