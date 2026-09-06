#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-desktop-daily-rail-visibility-fix">
/* One complete desktop layout for the stats rail. This avoids partially styled
   states when browser zoom changes the CSS viewport width. */
@media(min-width:1100px){
  #cist-daily-rail.cist-daily-rail{
    display:block!important;
    position:absolute!important;
    left:auto!important;
    right:16px!important;
    top:144px!important;
    width:clamp(150px,calc((100vw - 800px)/2 - 12px),240px)!important;
    z-index:2!important;
    box-sizing:border-box!important;
    font-family:inherit!important;
  }
  #cist-daily-rail .cist-daily-card{
    overflow:hidden!important;
    width:100%!important;
    box-sizing:border-box!important;
    border:1px solid color-mix(in srgb,var(--line) 92%,transparent)!important;
    border-radius:18px!important;
    background:linear-gradient(180deg,color-mix(in srgb,var(--card) 88%,transparent),color-mix(in srgb,var(--bg) 72%,var(--card)))!important;
    box-shadow:0 16px 42px rgba(0,0,0,.14)!important;
  }
  #cist-daily-rail .cist-daily-head{
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:8px!important;
    padding:13px 14px!important;
    border-bottom:1px solid var(--line)!important;
  }
  #cist-daily-rail .cist-daily-title{
    font-size:10px!important;
    font-weight:900!important;
    letter-spacing:.09em!important;
    text-transform:uppercase!important;
    color:var(--muted)!important;
  }
  #cist-daily-rail .cist-daily-live{
    display:inline-flex!important;
    align-items:center!important;
    gap:6px!important;
    font-size:9px!important;
    font-weight:800!important;
    color:var(--muted)!important;
    white-space:nowrap!important;
  }
  #cist-daily-rail .cist-daily-live:before{
    content:''!important;
    width:6px!important;
    height:6px!important;
    flex:0 0 auto!important;
    border-radius:999px!important;
    background:var(--green)!important;
    box-shadow:0 0 0 4px color-mix(in srgb,var(--green) 10%,transparent)!important;
  }
  #cist-daily-rail .cist-daily-primary{
    padding:17px 14px 15px!important;
  }
  #cist-daily-rail .cist-daily-number{
    display:block!important;
    color:var(--text)!important;
    font-size:clamp(30px,3vw,38px)!important;
    font-weight:920!important;
    letter-spacing:-.045em!important;
    line-height:1!important;
    font-variant-numeric:tabular-nums!important;
  }
  #cist-daily-rail .cist-daily-primary-label{
    display:block!important;
    margin-top:5px!important;
    color:var(--muted)!important;
    font-size:10px!important;
    font-weight:750!important;
  }
  #cist-daily-rail .cist-daily-list{
    display:grid!important;
    border-top:1px solid var(--line)!important;
  }
  #cist-daily-rail .cist-daily-row{
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:8px!important;
    min-width:0!important;
    padding:11px 14px!important;
    border-bottom:1px solid color-mix(in srgb,var(--line) 78%,transparent)!important;
  }
  #cist-daily-rail .cist-daily-row:last-child{border-bottom:0!important}
  #cist-daily-rail .cist-daily-row span{
    min-width:0!important;
    color:var(--muted)!important;
    font-size:9px!important;
    line-height:1.3!important;
  }
  #cist-daily-rail .cist-daily-row strong{
    max-width:96px!important;
    min-width:0!important;
    color:var(--text)!important;
    font-size:11px!important;
    font-weight:900!important;
    text-align:right!important;
    line-height:1.25!important;
    overflow-wrap:anywhere!important;
    font-variant-numeric:tabular-nums!important;
  }
  #cist-daily-rail .cist-daily-row.cist-daily-warning strong{color:var(--amber)!important}
  #cist-daily-rail .cist-daily-foot{
    padding:10px 12px!important;
    border-top:1px solid var(--line)!important;
    color:var(--muted)!important;
    font-size:8px!important;
    line-height:1.4!important;
    text-align:center!important;
  }
}

/* Compact the rail instead of letting it lose its styling at higher zoom. */
@media(min-width:1100px) and (max-width:1249px){
  #cist-daily-rail.cist-daily-rail{right:10px!important;border-radius:15px!important}
  #cist-daily-rail .cist-daily-head{padding:11px 10px!important}
  #cist-daily-rail .cist-daily-primary{padding:14px 10px 12px!important}
  #cist-daily-rail .cist-daily-row{display:block!important;padding:9px 10px!important}
  #cist-daily-rail .cist-daily-row strong{display:block!important;max-width:none!important;margin-top:3px!important;text-align:left!important}
  #cist-daily-rail .cist-daily-foot{padding:9px!important;font-size:7.5px!important}
}

@media(min-width:1450px){
  #cist-daily-rail.cist-daily-rail{right:24px!important}
}

@media(max-width:1099px){
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
    import re
    source = re.sub(r'\s*<style id="cist-desktop-daily-rail-visibility-fix">.*?</style>', '', source, count=1, flags=re.S)
    source = source.replace('</head>', STYLE + '\n</head>', 1)
    required = ['min-width:1100px', 'cist-daily-card', 'cist-daily-row', 'max-width:1249px']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Daily stats zoom-safe guard failed: missing {token}')
    HOME.write_text(source, encoding='utf-8')
    print('Applied complete zoom-safe desktop stats rail styling')


if __name__ == '__main__':
    main()
