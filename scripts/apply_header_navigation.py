#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-header-navigation-style">
.site-header{position:relative;z-index:40;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:saturate(140%) blur(12px);-webkit-backdrop-filter:saturate(140%) blur(12px)}
.site-header .top{gap:18px}
.header-brand{white-space:nowrap}
.header-desktop-nav{display:flex;align-items:center;gap:3px;margin-left:auto}
.header-menu{position:relative}
.header-menu>summary{list-style:none;cursor:pointer;color:var(--muted);font-size:13px;font-weight:700;padding:8px 10px;border-radius:9px;user-select:none}
.header-menu>summary::-webkit-details-marker{display:none}
.header-menu>summary:hover,.header-menu[open]>summary{color:var(--text);background:var(--soft)}
.header-dropdown{position:absolute;top:calc(100% + 8px);right:0;min-width:190px;padding:7px;background:var(--card);border:1px solid var(--line);border-radius:13px;box-shadow:var(--shadow)}
.header-dropdown a{display:block;padding:9px 10px;border-radius:8px;color:var(--text);font-size:13px;text-decoration:none;white-space:nowrap}
.header-dropdown a:hover{background:var(--soft)}
.header-mobile-menu{display:none;position:relative;margin-left:auto}
.header-mobile-menu>summary{list-style:none;cursor:pointer;color:var(--text);font-size:13px;font-weight:800;padding:7px 10px;border:1px solid var(--line);border-radius:9px;background:var(--card);user-select:none}
.header-mobile-menu>summary::-webkit-details-marker{display:none}
.header-mobile-panel{position:absolute;top:calc(100% + 10px);right:0;width:min(318px,calc(100vw - 28px));padding:13px;background:var(--card);border:1px solid var(--line);border-radius:15px;box-shadow:var(--shadow)}
.header-mobile-group+.header-mobile-group{margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.header-mobile-label{margin:0 0 6px;color:var(--muted);font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}
.header-mobile-links{display:grid;grid-template-columns:1fr 1fr;gap:2px 6px}
.header-mobile-links a{padding:8px;border-radius:8px;color:var(--text);font-size:13px;text-decoration:none}
.header-mobile-links a:hover{background:var(--soft)}
@media(max-width:600px){
  .site-header .top{width:min(920px,calc(100% - 28px))}
  .header-desktop-nav{display:none}
  .header-mobile-menu{display:block}
}
</style>
'''

HEADER = r'''<header class="site-header">
  <div class="top">
    <a class="brand header-brand" href="/">↗ Can I Share This?</a>

    <nav class="header-desktop-nav" aria-label="Primary navigation">
      <details class="header-menu">
        <summary>Check</summary>
        <div class="header-dropdown">
          <a href="/">Link checker</a>
          <a href="/email-safety-checker">Email checker</a>
          <a href="/qr-code-link-checker">QR code checker</a>
        </div>
      </details>
      <details class="header-menu">
        <summary>Prevention</summary>
        <div class="header-dropdown">
          <a href="/scam-prevention">Scam Prevention</a>
          <a href="/scam-warning-signs">Scam warnings</a>
          <a href="/phishing-link-checker">Phishing</a>
        </div>
      </details>
      <details class="header-menu">
        <summary>About</summary>
        <div class="header-dropdown">
          <a href="/how-link-scanning-works">How it works</a>
          <a href="/methodology">Methodology</a>
        </div>
      </details>
    </nav>

    <details class="header-mobile-menu">
      <summary>Menu</summary>
      <div class="header-mobile-panel">
        <section class="header-mobile-group" aria-labelledby="mobile-check-label">
          <h2 class="header-mobile-label" id="mobile-check-label">Check</h2>
          <div class="header-mobile-links">
            <a href="/">Link checker</a>
            <a href="/email-safety-checker">Email checker</a>
            <a href="/qr-code-link-checker">QR checker</a>
          </div>
        </section>
        <section class="header-mobile-group" aria-labelledby="mobile-prevention-label">
          <h2 class="header-mobile-label" id="mobile-prevention-label">Prevention</h2>
          <div class="header-mobile-links">
            <a href="/scam-prevention">Scam Prevention</a>
            <a href="/scam-warning-signs">Scam warnings</a>
            <a href="/phishing-link-checker">Phishing</a>
          </div>
        </section>
        <section class="header-mobile-group" aria-labelledby="mobile-about-label">
          <h2 class="header-mobile-label" id="mobile-about-label">About</h2>
          <div class="header-mobile-links">
            <a href="/how-link-scanning-works">How it works</a>
            <a href="/methodology">Methodology</a>
          </div>
        </section>
      </div>
    </details>
  </div>
</header>'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    # Replace a prior injected style if this script is ever run more than once.
    source = re.sub(
        r'\s*<style id="cist-header-navigation-style">.*?</style>',
        '',
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, count = re.subn(r'<header(?:\s[^>]*)?>.*?</header>', HEADER, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'Expected exactly one homepage header, replaced {count}')

    required = [
        'class="site-header"',
        'class="header-desktop-nav"',
        'class="header-mobile-menu"',
        '<summary>Check</summary>',
        '<summary>Prevention</summary>',
        '<summary>About</summary>',
        '<summary>Menu</summary>',
        '/email-safety-checker',
        '/qr-code-link-checker',
        '/scam-prevention',
        '/scam-warning-signs',
        '/phishing-link-checker',
        '/how-link-scanning-works',
        '/methodology',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Header guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied compact responsive homepage header navigation')


if __name__ == '__main__':
    main()
