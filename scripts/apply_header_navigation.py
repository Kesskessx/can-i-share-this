#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-header-navigation-style">
.site-header{height:auto;min-height:64px;position:relative;z-index:40;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:saturate(140%) blur(12px);-webkit-backdrop-filter:saturate(140%) blur(12px)}
.site-header .top{min-height:64px;gap:18px}
.header-brand{white-space:nowrap}
.header-desktop-nav{display:flex;align-items:center;gap:3px;margin-left:auto}
.header-menu{position:relative}
.header-menu>summary{list-style:none;cursor:pointer;color:var(--muted);font-size:13px;font-weight:700;padding:8px 10px;border-radius:9px;user-select:none}
.header-menu>summary::-webkit-details-marker{display:none}
.header-menu>summary:hover,.header-menu[open]>summary{color:var(--text);background:var(--soft)}
.header-dropdown{position:absolute;top:calc(100% + 8px);right:0;min-width:190px;padding:7px;background:var(--card);border:1px solid var(--line);border-radius:13px;box-shadow:var(--shadow)}
.header-dropdown a{display:block;padding:9px 10px;border-radius:8px;color:var(--text);font-size:13px;text-decoration:none;white-space:nowrap}
.header-dropdown a:hover{background:var(--soft)}
.header-mobile-toggle{display:none;margin-left:auto;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--text);padding:7px 10px;font:inherit;font-size:13px;font-weight:800;cursor:pointer}
.header-mobile-panel{display:none;border-top:1px solid var(--line);background:var(--bg)}
.header-mobile-inner{width:min(920px,calc(100% - 28px));margin:auto;padding:13px 0 15px}
.header-mobile-group{display:flex;align-items:baseline;gap:12px}
.header-mobile-group+.header-mobile-group{margin-top:8px}
.header-mobile-label{flex:0 0 76px;margin:0;color:var(--muted);font-size:9px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}
.header-mobile-links{display:flex;align-items:center;gap:4px 12px;flex-wrap:wrap}
.header-mobile-links a{color:var(--text);font-size:12px;line-height:1.45;text-decoration:none}
.header-mobile-links a:hover{text-decoration:underline;text-underline-offset:3px}
.header-mobile-panel[hidden]{display:none!important}
@media(max-width:600px){
  .site-header{min-height:58px}
  .site-header .top{width:min(920px,calc(100% - 28px));min-height:58px}
  .header-desktop-nav{display:none}
  .header-mobile-toggle{display:inline-flex;align-items:center;justify-content:center}
  .header-mobile-panel{display:block;position:static;width:100%;box-shadow:none}
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

    <button class="header-mobile-toggle" id="mobile-menu-button" type="button" aria-expanded="false" aria-controls="mobile-menu-panel">Menu</button>
  </div>

  <nav class="header-mobile-panel" id="mobile-menu-panel" aria-label="Mobile navigation" hidden>
    <div class="header-mobile-inner">
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
  </nav>
</header>'''

SCRIPT = r'''
<script id="cist-header-navigation-script">
(function(){
  var button=document.getElementById('mobile-menu-button');
  var panel=document.getElementById('mobile-menu-panel');
  if(!button||!panel)return;
  function setOpen(open){
    panel.hidden=!open;
    button.setAttribute('aria-expanded',open?'true':'false');
    button.textContent=open?'Close':'Menu';
  }
  button.addEventListener('click',function(){setOpen(panel.hidden)});
  panel.addEventListener('click',function(event){if(event.target&&event.target.closest('a'))setOpen(false)});
  document.addEventListener('keydown',function(event){if(event.key==='Escape'&&!panel.hidden){setOpen(false);button.focus()}});
  var mq=window.matchMedia('(min-width:601px)');
  function closeForDesktop(event){if(event.matches)setOpen(false)}
  if(mq.addEventListener)mq.addEventListener('change',closeForDesktop);else if(mq.addListener)mq.addListener(closeForDesktop);
})();
</script>
'''


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    source = re.sub(
        r'\s*<style id="cist-header-navigation-style">.*?</style>',
        '',
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r'\s*<script id="cist-header-navigation-script">.*?</script>',
        '',
        source,
        count=1,
        flags=re.S,
    )
    source = source.replace('</head>', STYLE + '\n</head>', 1)

    source, count = re.subn(r'<header(?:\s[^>]*)?>.*?</header>', HEADER, source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'Expected exactly one homepage header, replaced {count}')

    source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'class="site-header"',
        'class="header-desktop-nav"',
        'id="mobile-menu-button"',
        'id="mobile-menu-panel"',
        'aria-expanded="false"',
        '<summary>Check</summary>',
        '<summary>Prevention</summary>',
        '<summary>About</summary>',
        '/email-safety-checker',
        '/qr-code-link-checker',
        '/scam-prevention',
        '/scam-warning-signs',
        '/phishing-link-checker',
        '/how-link-scanning-works',
        '/methodology',
        'cist-header-navigation-script',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Header guard failed: missing {token}')

    if 'header-mobile-panel{position:absolute' in source:
        raise RuntimeError('Mobile navigation must stay in document flow')

    HOME.write_text(source, encoding='utf-8')
    print('Applied responsive header with in-flow mobile navigation')


if __name__ == '__main__':
    main()
