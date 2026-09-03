#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-footer-navigation-style">
.site-footer{width:min(860px,calc(100% - 28px));margin:0 auto 26px;color:var(--muted);font-size:12px}
.footer-shell{border-top:1px solid var(--line);padding-top:18px}
.footer-resources{display:flex;align-items:center;justify-content:center;gap:8px 14px;flex-wrap:wrap;text-align:center}
.footer-label{margin:0;color:var(--text);font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}
.footer-resource-links{display:flex;align-items:center;justify-content:center;gap:5px 9px;flex-wrap:wrap}
.footer-resource-links a,.footer-social a{color:var(--muted);text-decoration:none}
.footer-resource-links i{font-style:normal;opacity:.4}
.footer-resource-links a:hover,.footer-social a:hover{color:var(--text);text-decoration:underline;text-underline-offset:3px}
.footer-bottom{display:flex;align-items:center;justify-content:center;gap:7px 14px;flex-wrap:wrap;margin-top:12px;text-align:center}
.footer-trust{display:flex;align-items:center;justify-content:center;gap:5px 10px;flex-wrap:wrap}
.footer-trust span:first-child{color:var(--text);font-weight:700}
.footer-social a{display:inline-flex;align-items:center;gap:5px;font-weight:650}
@media(max-width:600px){
  .site-footer{width:min(720px,calc(100% - 28px));margin-bottom:16px;font-size:10.5px}
  .footer-shell{padding-top:14px}
  .footer-resources{display:block}
  .footer-label{margin-bottom:5px;font-size:9px}
  .footer-resource-links{gap:3px 7px;line-height:1.45}
  .footer-bottom{display:block;margin-top:9px}
  .footer-trust{display:block;line-height:1.45}
  .footer-trust span{display:block}
  .footer-trust span+span{margin-top:2px}
  .footer-social{margin-top:4px}
}
</style>
'''

FOOTER = r'''<footer class="site-footer">
  <div class="footer-shell">
    <nav class="footer-resources" aria-label="Safety resources">
      <h2 class="footer-label">Safety resources</h2>
      <div class="footer-resource-links">
        <a href="/scam-checker">Scam Checker</a><i aria-hidden="true">·</i>
        <a href="/supported-checks">Supported Checks</a><i aria-hidden="true">·</i>
        <a href="/scan-examples">Examples</a><i aria-hidden="true">·</i>
        <a href="/methodology">Methodology</a><i aria-hidden="true">·</i>
        <a href="/security">Security</a><i aria-hidden="true">·</i>
        <a href="/about">About</a>
      </div>
    </nav>

    <div class="footer-bottom">
      <div class="footer-trust">
        <span>Privacy-first · No signup</span>
        <span>No scanner can guarantee that a link or sender is safe.</span>
      </div>
      <div class="footer-social"><a href="https://x.com/CanIShareLink" target="_blank" rel="noopener noreferrer" aria-label="Can I Share This on X"><span aria-hidden="true">𝕏</span><span>@CanIShareLink</span></a></div>
    </div>
  </div>
</footer>'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    source = re.sub(
        r'\s*<style id="cist-footer-navigation-style">.*?</style>',
        '',
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, count = re.subn(r'<footer(?:\s[^>]*)?>.*?</footer>', FOOTER, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'Expected exactly one homepage footer, replaced {count}')

    source = re.sub(r'\s*<script id="cist-footer-navigation-script">.*?</script>', '', source, count=1, flags=re.S)

    required = [
        'class="site-footer"',
        'class="footer-resources"',
        'Safety resources',
        'Scam Checker',
        'Supported Checks',
        'Examples',
        'Methodology',
        'Security',
        'About',
        'Privacy-first · No signup',
        'No scanner can guarantee that a link or sender is safe.',
        '@CanIShareLink',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Footer guard failed: missing {token}')

    if 'class="footer-grid"' in source or 'class="footer-brand"' in source:
        raise RuntimeError('Footer must remain secondary and compact')

    HOME.write_text(source, encoding='utf-8')
    print('Applied compact secondary homepage footer')


if __name__ == '__main__':
    main()
