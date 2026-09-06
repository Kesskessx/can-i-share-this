#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-brand-depth-polish-v1-style">
/* Final visual depth layer: intentionally subtle, decorative only. */
.hero{
  position:relative!important;
  isolation:isolate!important;
}
.hero::before{
  content:'';
  position:absolute;
  z-index:-2;
  pointer-events:none;
  left:50%;
  top:38px;
  width:min(1120px,92vw);
  height:430px;
  transform:translateX(-50%);
  background:
    radial-gradient(ellipse 48% 38% at 50% 44%,rgba(120,143,247,.105) 0%,rgba(120,143,247,.045) 42%,transparent 74%),
    radial-gradient(ellipse 34% 30% at 61% 38%,rgba(151,107,255,.055) 0%,transparent 72%);
  filter:blur(18px);
  opacity:.95;
}
.hero::after{
  content:'';
  position:absolute;
  z-index:-1;
  pointer-events:none;
  left:50%;
  top:118px;
  width:min(900px,82vw);
  height:255px;
  transform:translateX(-50%);
  background:radial-gradient(ellipse at center,rgba(120,143,247,.035),transparent 70%);
}

/* Keep the scanner as the visual focal point, but give it a more finished edge. */
#scan-form{
  box-shadow:
    0 0 0 1px rgba(120,143,247,.14),
    0 0 30px rgba(120,143,247,.16),
    0 18px 48px rgba(0,0,0,.22)!important;
}
#scan-form::before{
  content:'';
  position:absolute;
  pointer-events:none;
  inset:0;
  border-radius:inherit;
  padding:1px;
  background:linear-gradient(105deg,rgba(164,178,255,.22),rgba(120,143,247,.04) 45%,rgba(151,107,255,.13));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
  -webkit-mask-composite:xor;
  mask-composite:exclude;
  opacity:.75;
}
#scan-form{position:relative!important;isolation:isolate!important}

/* Brand-colored separators instead of flat grey lines. */
.site-header{position:relative!important}
.site-header::after{
  content:'';
  position:absolute;
  left:0;
  right:0;
  bottom:-1px;
  height:1px;
  pointer-events:none;
  background:linear-gradient(90deg,transparent 0%,rgba(120,143,247,.18) 22%,rgba(151,107,255,.12) 50%,rgba(120,143,247,.18) 78%,transparent 100%);
}

.site-footer{
  position:relative!important;
  isolation:isolate!important;
}
.site-footer::before{
  content:'';
  position:absolute;
  left:0;
  right:0;
  top:-1px;
  height:1px;
  pointer-events:none;
  background:linear-gradient(90deg,transparent 0%,rgba(120,143,247,.18) 24%,rgba(151,107,255,.13) 50%,rgba(120,143,247,.18) 76%,transparent 100%);
}
.site-footer::after{
  content:'';
  position:absolute;
  z-index:-1;
  pointer-events:none;
  left:50%;
  top:-125px;
  width:min(1080px,92vw);
  height:150px;
  transform:translateX(-50%);
  background:linear-gradient(180deg,transparent 0%,rgba(120,143,247,.018) 48%,rgba(120,143,247,.04) 100%);
  filter:blur(10px);
}

/* Tiny brand edge on the two desktop information cards. */
@media(min-width:1100px){
  #cist-scam-signals-rail .cist-signal-card,
  #cist-daily-rail .cist-daily-card{
    box-shadow:0 12px 32px rgba(0,0,0,.12),0 0 0 1px rgba(120,143,247,.025)!important;
  }
  #cist-scam-signals-rail .cist-signal-head,
  #cist-daily-rail .cist-daily-head{
    background:linear-gradient(90deg,rgba(120,143,247,.025),transparent 68%)!important;
  }
}

@media(max-width:700px){
  .hero::before{
    top:18px;
    width:100vw;
    height:340px;
    opacity:.58;
    filter:blur(24px);
  }
  .hero::after{display:none}
  #scan-form{
    box-shadow:0 0 0 1px rgba(120,143,247,.12),0 0 20px rgba(120,143,247,.12),0 12px 34px rgba(0,0,0,.20)!important;
  }
  .site-footer::after{opacity:.5}
}

@media(prefers-reduced-motion:reduce){
  .hero::before,.hero::after,.site-footer::after{filter:none}
}
</style>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    source = re.sub(r'\s*<style id="cist-brand-depth-polish-v1-style">.*?</style>', '', source, count=1, flags=re.S)
    if '</head>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source = source.replace('</head>', STYLE + '\n</head>', 1)
    required = [
        'cist-brand-depth-polish-v1-style',
        'radial-gradient',
        '#scan-form::before',
        '.site-header::after',
        '.site-footer::after',
        'prefers-reduced-motion'
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Brand depth polish guard failed: missing {token}')
    HOME.write_text(source, encoding='utf-8')
    print('Applied subtle brand depth, accent separators and footer transition')


if __name__ == '__main__':
    main()
