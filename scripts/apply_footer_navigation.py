#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-footer-navigation-style">
.site-footer{width:min(860px,calc(100% - 28px));margin:0 auto 32px;color:var(--muted);font-size:12px}
.footer-shell{border-top:1px solid var(--line);padding-top:26px}
.footer-brand{margin-bottom:22px}
.footer-brand strong{display:block;color:var(--text);font-size:15px;letter-spacing:-.015em}
.footer-brand p{max-width:520px;margin:5px 0 0;line-height:1.55}
.footer-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:34px;margin:0;text-align:left}
.footer-group{min-width:0}
.footer-label{margin:0 0 10px;color:var(--text);font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}
.footer-links{display:grid;gap:7px}
.footer-links a,.footer-secondary a,.footer-social a{color:var(--muted);text-decoration:none}
.footer-links a{font-size:13px;line-height:1.35}
.footer-links a:hover,.footer-secondary a:hover,.footer-social a:hover{color:var(--text);text-decoration:underline;text-underline-offset:3px}
.footer-secondary{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:20px;padding-top:16px;border-top:1px solid var(--line);font-size:12px}
.footer-secondary i{font-style:normal;opacity:.45}
.footer-bottom{display:flex;align-items:center;justify-content:space-between;gap:12px 20px;flex-wrap:wrap;margin-top:16px}
.footer-trust{display:flex;gap:5px 13px;flex-wrap:wrap}
.footer-trust span:first-child{color:var(--text);font-weight:700}
.footer-social a{display:inline-flex;align-items:center;gap:5px;font-weight:650}
@media(max-width:600px){
  .site-footer{width:min(720px,calc(100% - 28px));margin-bottom:18px;font-size:11px}
  .footer-shell{padding-top:17px}
  .footer-brand{display:none}
  .footer-grid{grid-template-columns:1fr;gap:12px}
  .footer-label{margin-bottom:5px;font-size:9px}
  .footer-links{display:flex;gap:4px 12px;flex-wrap:wrap}
  .footer-links a{font-size:11.5px;line-height:1.35}
  .footer-secondary{gap:4px 8px;margin-top:13px;padding-top:11px;font-size:10.5px}
  .footer-bottom{display:block;margin-top:10px;text-align:center}
  .footer-trust{display:block;line-height:1.45;font-size:10.5px}
  .footer-trust span{display:block}
  .footer-trust span+span{margin-top:2px}
  .footer-social{margin-top:5px;font-size:10.5px}
}
</style>
'''

FOOTER = r'''<footer class="site-footer">
  <div class="footer-shell">
    <div class="footer-brand">
      <strong>Can I Share This?</strong>
      <p>Check suspicious links and email addresses before you trust them.</p>
    </div>

    <nav class="footer-grid" aria-label="Safety tools and prevention">
      <section class="footer-group" aria-labelledby="footer-check">
        <h2 class="footer-label" id="footer-check">Check</h2>
        <div class="footer-links">
          <a href="/">Link checker</a>
          <a href="/email-safety-checker">Email checker</a>
          <a href="/qr-code-link-checker">QR code checker</a>
        </div>
      </section>

      <section class="footer-group" aria-labelledby="footer-prevention">
        <h2 class="footer-label" id="footer-prevention">Prevention</h2>
        <div class="footer-links">
          <a href="/scam-prevention">Scam Prevention</a>
          <a href="/scam-warning-signs">Scam warnings</a>
          <a href="/phishing-link-checker">Phishing</a>
        </div>
      </section>

      <section class="footer-group" aria-labelledby="footer-about">
        <h2 class="footer-label" id="footer-about">About</h2>
        <div class="footer-links">
          <a href="/how-link-scanning-works">How it works</a>
          <a href="/methodology">Methodology</a>
        </div>
      </section>
    </nav>

    <nav class="footer-secondary" aria-label="Specialized link checks">
      <a href="/safe-link-checker">Safe link</a><i aria-hidden="true">·</i>
      <a href="/google-drive-link-checker">Google Drive</a><i aria-hidden="true">·</i>
      <a href="/dropbox-link-checker">Dropbox</a>
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

    if 'id="cist-footer-navigation-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, count = re.subn(r'<footer(?:\s[^>]*)?>.*?</footer>', FOOTER, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'Expected exactly one homepage footer, replaced {count}')

    source = re.sub(r'\s*<script id="cist-footer-navigation-script">.*?</script>', '', source, count=1, flags=re.S)

    required = [
        'class="site-footer"',
        'class="footer-grid"',
        'Link checker',
        'Email checker',
        'QR code checker',
        'Scam Prevention',
        'Scam warnings',
        'Phishing',
        'How it works',
        'Methodology',
        'Safe link',
        'Google Drive',
        'Dropbox',
        'Privacy-first · No signup',
        '@CanIShareLink',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Footer guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied compact mobile homepage footer navigation')


if __name__ == '__main__':
    main()
