#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-footer-navigation-style">
.site-footer{width:min(860px,calc(100% - 28px));margin:0 auto 32px;text-align:left;color:var(--muted);font-size:12px}
.footer-brand{border-top:1px solid var(--line);padding:24px 0 18px;text-align:center}
.footer-brand strong{display:block;color:var(--text);font-size:15px;letter-spacing:-.015em}
.footer-brand p{max-width:520px;margin:5px auto 0;line-height:1.55}
.footer-grid{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:0!important;text-align:left}
.footer-group{margin:0!important;padding:15px 16px;border:1px solid var(--line);border-radius:14px;background:var(--card)}
.footer-group summary{list-style:none;cursor:default;color:var(--text);font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
.footer-group summary::-webkit-details-marker{display:none}
.footer-links{display:grid;gap:7px;margin-top:11px}
.footer-links a{color:var(--muted);text-decoration:none;font-size:13px;line-height:1.35}
.footer-links a:hover{color:var(--text);text-decoration:underline;text-underline-offset:3px}
.footer-bottom{display:flex;justify-content:center;gap:6px 16px;flex-wrap:wrap;margin-top:18px;padding-top:17px;border-top:1px solid var(--line);text-align:center}
.footer-bottom p{margin:0}
.site-footer .x-follow{margin-top:11px}
@media(max-width:600px){
  .site-footer{width:min(720px,calc(100% - 28px))}
  .footer-brand{padding-top:21px}
  .footer-grid{grid-template-columns:1fr;gap:8px}
  .footer-group{padding:0;border-radius:12px;overflow:hidden}
  .footer-group summary{cursor:pointer;padding:13px 14px}
  .footer-group summary:after{content:'+';float:right;color:var(--muted);font-size:15px;line-height:1}
  .footer-group[open] summary:after{content:'−'}
  .footer-links{margin:0;padding:0 14px 14px;gap:9px}
  .footer-links a{font-size:13px}
  .footer-bottom{display:block;margin-top:15px;padding-top:15px}
  .footer-bottom p+p{margin-top:4px}
}
@media(prefers-reduced-motion:reduce){.footer-links a{scroll-behavior:auto}}
</style>
'''

FOOTER = r'''<footer class="site-footer">
  <div class="footer-brand">
    <strong>Can I Share This?</strong>
    <p>Check suspicious links and email addresses before you trust them.</p>
  </div>
  <nav class="footer-grid" aria-label="Safety tools and prevention">
    <details class="footer-group" open>
      <summary>Check</summary>
      <div class="footer-links">
        <a href="/">Link checker</a>
        <a href="/email-safety-checker">Email checker</a>
        <a href="/qr-code-link-checker">QR code checker</a>
      </div>
    </details>
    <details class="footer-group" open>
      <summary>Prevention</summary>
      <div class="footer-links">
        <a href="/scam-prevention">Scam Prevention</a>
        <a href="/phishing-link-checker">Phishing</a>
        <a href="/fake-package-delivery-scam">Fake package scams</a>
        <a href="/scam-warning-signs">Scam warning signs</a>
      </div>
    </details>
    <details class="footer-group" open>
      <summary>About</summary>
      <div class="footer-links">
        <a href="/how-link-scanning-works">How it works</a>
        <a href="/methodology">Methodology</a>
      </div>
    </details>
  </nav>
  <div class="footer-bottom">
    <p>No scanner can guarantee that a link or sender is safe.</p>
    <p>Privacy-first · No signup</p>
  </div>
  <div class="x-follow"><a href="https://x.com/CanIShareLink" target="_blank" rel="noopener noreferrer" aria-label="Can I Share This on X"><span class="x-follow-logo" aria-hidden="true">𝕏</span><span>@CanIShareLink</span></a></div>
</footer>'''

SCRIPT = r'''
<script id="cist-footer-navigation-script">
(function(){
  var groups=Array.prototype.slice.call(document.querySelectorAll('.footer-group'));
  if(!groups.length||!window.matchMedia)return;
  var mq=window.matchMedia('(min-width:601px)');
  function sync(){groups.forEach(function(group){if(mq.matches)group.setAttribute('open','');else group.removeAttribute('open')})}
  sync();
  if(mq.addEventListener)mq.addEventListener('change',sync);else if(mq.addListener)mq.addListener(sync);
})();
</script>
'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-footer-navigation-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, count = re.subn(r'<footer(?:\s[^>]*)?>.*?</footer>', FOOTER, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'Expected exactly one homepage footer, replaced {count}')

    if 'id="cist-footer-navigation-script"' not in source:
        source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'class="site-footer"',
        'Link checker',
        'Email checker',
        'Scam Prevention',
        'Fake package scams',
        'Scam warning signs',
        'How it works',
        'Methodology',
        'Privacy-first · No signup',
        '@CanIShareLink',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Footer guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied compact safety, prevention and methodology footer navigation')


if __name__ == '__main__':
    main()
