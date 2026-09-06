#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'
html = HOME.read_text(encoding='utf-8')

if 'id="analyze-loading-halo-style"' in html:
    raise SystemExit('analyze loading halo already applied')

css = r'''
<style id="analyze-loading-halo-style">
@keyframes cistAnalyzeHaloPulse {
  0%,100% {
    box-shadow:
      0 0 0 0 rgba(120,143,247,.18),
      0 0 18px rgba(120,143,247,.24),
      0 8px 24px rgba(120,143,247,.18);
  }
  50% {
    box-shadow:
      0 0 0 7px rgba(120,143,247,.08),
      0 0 34px rgba(120,143,247,.48),
      0 10px 30px rgba(120,143,247,.28);
  }
}

#scan-form button[type="submit"]:disabled {
  opacity:.96!important;
  cursor:progress!important;
  filter:none!important;
  animation:cistAnalyzeHaloPulse 1.35s ease-in-out infinite!important;
  will-change:box-shadow;
}

@media(prefers-reduced-motion:reduce){
  #scan-form button[type="submit"]:disabled {
    animation:none!important;
    box-shadow:
      0 0 0 3px rgba(120,143,247,.14),
      0 0 24px rgba(120,143,247,.34),
      0 8px 24px rgba(120,143,247,.18)!important;
  }
}
</style>
'''

if '</head>' not in html:
    raise SystemExit('missing </head>')

html = html.replace('</head>', css + '\n</head>', 1)
HOME.write_text(html, encoding='utf-8')
print('Applied blue loading halo to Analyze button')
