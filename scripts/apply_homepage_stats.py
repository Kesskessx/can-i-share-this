#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-homepage-stats-style">
.cist-stats{max-width:760px;margin:22px auto 0;padding:18px 16px;border:1px solid var(--border,#2a2f38);border-radius:16px;background:var(--panel,#15181e)}
.cist-stats-title{margin:0 0 12px;text-align:center;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted,#aab0bb)}
.cist-stats-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.cist-stat{padding:12px 10px;text-align:center;border-radius:12px;background:rgba(255,255,255,.025)}
.cist-stat-value{display:block;font-size:25px;line-height:1;font-weight:850;color:var(--text,#f6f7f9)}
.cist-stat-label{display:block;margin-top:7px;font-size:11px;line-height:1.25;color:var(--muted,#aab0bb)}
.cist-stats-note{margin:11px 0 0;text-align:center;font-size:10px;line-height:1.45;color:var(--muted,#8f96a3)}
@media(max-width:650px){.cist-stats{margin-top:16px;padding:14px 12px}.cist-stats-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.cist-stat-value{font-size:22px}}
</style>
'''

BLOCK = r'''
<section class="cist-stats" id="cist-stats" aria-label="Can I Share This statistics">
  <p class="cist-stats-title">By the numbers</p>
  <div class="cist-stats-grid">
    <div class="cist-stat"><strong class="cist-stat-value">8</strong><span class="cist-stat-label">Input types supported</span></div>
    <div class="cist-stat"><strong class="cist-stat-value">5</strong><span class="cist-stat-label">Security checks available</span></div>
    <div class="cist-stat"><strong class="cist-stat-value">1</strong><span class="cist-stat-label">Universal scanner</span></div>
    <div class="cist-stat"><strong class="cist-stat-value">0</strong><span class="cist-stat-label">Accounts required</span></div>
  </div>
  <p class="cist-stats-note">Only verifiable product statistics are shown here. Usage totals are not displayed until persistent aggregate counting is enabled.</p>
</section>
'''

def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    if 'id="cist-homepage-stats-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)
    if 'id="cist-stats"' not in source:
        anchor = '<footer'
        if anchor in source:
            source = source.replace(anchor, BLOCK + '\n' + anchor, 1)
        else:
            source = source.replace('</body>', BLOCK + '\n</body>', 1)
    required = ['id="cist-stats"', 'Input types supported', 'Security checks available', 'Universal scanner', 'Accounts required']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Homepage stats guard failed: missing {token}')
    HOME.write_text(source, encoding='utf-8')
    print('Applied trustworthy homepage statistics block')

if __name__ == '__main__':
    main()
