#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'dist' / 'index.html'
html = INDEX.read_text(encoding='utf-8')

if 'id="unified-scanner-style"' in html:
    raise SystemExit('unified scanner UI already present')

# Final-copy pass: this runs after all earlier scanner transformations.
html = html.replace('>Check link<', '>Analyze<', 1)
html = html.replace('Paste &amp; check', 'Paste', 1)
html = html.replace('Paste & check', 'Paste', 1)
html = html.replace('>Upload image<', '>Photo<', 1)
html = html.replace('>Use camera<', '>Camera<', 1)
html = html.replace('Screenshots and photos are analyzed temporarily and are not stored by Can I Share This?.', 'Automatic detection · Images are analyzed temporarily and not stored by Can I Share This?.', 1)

css = r'''
<style id="unified-scanner-style">
#scan-form{position:relative}
#image-safety-tools{max-width:720px;margin:8px auto 0;gap:8px}
#image-safety-tools .image-tool{min-height:46px;border-radius:14px;background:var(--card);font-size:13px}
#image-safety-tools .image-note{margin-top:2px;text-align:center;line-height:1.45}
.unified-scanner-label{max-width:720px;margin:9px auto 0;color:var(--muted);font-size:11px;font-weight:750;text-align:center;letter-spacing:.01em}
@media(max-width:600px){
  #image-safety-tools{margin-top:7px}
  #image-safety-tools .image-tool{min-width:0;flex:1;padding:10px 8px}
  .unified-scanner-label{font-size:10.5px;margin-top:7px}
}
</style>
'''
if '</head>' not in html:
    raise SystemExit('missing </head>')
html = html.replace('</head>', css + '\n</head>', 1)

# Add one compact explanation only; avoid adding another feature block.
needle = '<div id="image-safety-tools"'
pos = html.find(needle)
if pos >= 0:
    html = html[:pos] + '<div class="unified-scanner-label">One scanner · Type detection is automatic</div>\n' + html[pos:]

INDEX.write_text(html, encoding='utf-8')
print('Unified the homepage scanner UI')
