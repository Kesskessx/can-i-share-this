#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
HOME = DIST / 'index.html'

STYLE = r'''
<style id="cist-design-polish">
:root{--cist-scan-glow:rgba(19,115,51,.16);--cist-hero-glow:rgba(19,115,51,.075)}
@media(prefers-color-scheme:dark){:root{--cist-scan-glow:rgba(117,209,139,.18);--cist-hero-glow:rgba(117,209,139,.07)}}
body{background:radial-gradient(ellipse 560px 310px at 50% 132px,var(--cist-hero-glow),transparent 72%),var(--bg)}
.brand-wrap{display:flex;align-items:baseline;gap:10px;min-width:0}.brand-tagline{color:var(--muted);font-size:11px;font-weight:650;white-space:nowrap}
.scan-form{transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease}
.scan-form.is-scanning{border-color:var(--green);animation:cistScanPulse 1.15s ease-in-out infinite}
@keyframes cistScanPulse{0%,100%{box-shadow:var(--shadow),0 0 0 0 var(--cist-scan-glow)}50%{box-shadow:var(--shadow),0 0 0 5px var(--cist-scan-glow)}}
.check-strip{display:flex;justify-content:center;align-items:center;gap:6px 9px;flex-wrap:wrap;margin-top:11px;color:var(--muted);font-size:12px}.check-strip .check-label{font-weight:800;color:var(--text)}.check-strip i{font-style:normal;opacity:.55}
.destination-box{margin:17px 0 0;padding:14px 15px;border:1px solid var(--line);border-radius:13px;background:var(--soft);text-align:left}.destination-label{color:var(--muted);font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}.destination-host{display:block;margin-top:3px;font-size:16px;line-height:1.3;word-break:break-word}.destination-note{margin-top:5px;color:var(--muted);font-size:12px;word-break:break-word}.destination-note.warn{color:var(--amber);font-weight:750}
.risk-meter{margin:12px 0 0;padding:13px 14px;border:1px solid var(--line);border-radius:13px;background:var(--soft)}
.risk-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px;font-size:13px}
.risk-head span{color:var(--muted);font-weight:750}.risk-head strong{font-size:13px}
.risk-track{height:7px;overflow:hidden;border-radius:999px;background:var(--line)}
.risk-fill{display:block;width:0;height:100%;border-radius:inherit;background:var(--muted);transition:width .4s ease,background-color .2s ease}
.status-low .risk-fill{background:var(--green)}.status-caution .risk-fill{background:var(--amber)}.status-high .risk-fill{background:var(--red)}
@media(max-width:600px){header{height:66px}.top{align-items:center}.brand-wrap{display:block}.brand-tagline{display:block;margin-top:1px;font-size:10px}.check-strip{gap:5px 7px}.check-strip i{display:none}.destination-box{padding:12px 13px}}
@media(prefers-reduced-motion:reduce){.scan-form{transition:none}.scan-form.is-scanning{animation:none;box-shadow:var(--shadow),0 0 0 3px var(--cist-scan-glow)}.risk-fill{transition:none}}
</style>
'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="16" fill="#111827"/>
  <path d="M32 11 49 18v12c0 11.2-6.8 19.3-17 23-10.2-3.7-17-11.8-17-23V18l17-7Z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>
  <path d="m23.5 31.5 6 6 11.5-13" fill="none" stroke="#5ee2a0" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>\n'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Design polish failed: {label} anchor not found')
    return source.replace(old, new, 1)


def add_favicon_to_pages() -> None:
    (DIST / 'favicon.svg').write_text(FAVICON, encoding='utf-8')
    favicon_tag = '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
    theme_tag = '<meta name="theme-color" content="#111827">'
    for page in DIST.rglob('*.html'):
        source = page.read_text(encoding='utf-8')
        if favicon_tag not in source:
            source = source.replace('</head>', f'{favicon_tag}\n{theme_tag}\n</head>', 1)
            page.write_text(source, encoding='utf-8')


def polish_homepage() -> None:
    source = HOME.read_text(encoding='utf-8')
    if 'id="cist-design-polish"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    header_anchor = '<header><div class="top"><a class="brand" href="/">↗ Can I Share This?</a><a class="qr-top" href="/qr-code-link-checker">Scan QR</a></div></header>'
    header_block = '<header><div class="top"><div class="brand-wrap"><a class="brand" href="/">↗ Can I Share This?</a><span class="brand-tagline">Free Link Safety Checker</span></div><a class="qr-top" href="/qr-code-link-checker">Scan QR</a></div></header>'
    source = replace_once(source, header_anchor, header_block, 'brand descriptor')

    under_anchor = '<div class="under-form"><span>🔒 Links aren’t stored</span><a href="/qr-code-link-checker">Scan a QR code instead</a></div>'
    under_block = '<div class="check-strip" aria-label="What we check"><span class="check-label">What we check:</span><span>Phishing patterns</span><i>·</i><span>Malware signals</span><i>·</i><span>Redirects</span><i>·</i><span>Lookalike domains</span></div>\n    <div class="under-form"><span>🔒 Links aren’t stored</span><span>No signup</span><a href="/qr-code-link-checker">Scan a QR code</a></div>'
    source = replace_once(source, under_anchor, under_block, 'trust and check strip')

    footer_anchor = '<footer><div class="footer-line">Can I Share This? checks warning signs before you click. No scanner can guarantee a link is safe.</div><details><summary>Specialized checks</summary><nav><a href="/safe-link-checker">Safe link</a><a href="/scam-link-checker">Scam</a><a href="/phishing-link-checker">Phishing</a><a href="/qr-code-link-checker">QR code</a><a href="/google-drive-link-checker">Google Drive</a><a href="/dropbox-link-checker">Dropbox</a></nav></details>'
    footer_block = '<footer><div class="footer-line">Can I Share This? checks warning signs before you click. No scanner can guarantee a link is safe.</div><details><summary>More link checks</summary><nav><a href="/methodology">How it works</a><a href="/safe-link-checker">Safe link</a><a href="/scam-link-checker">Scam</a><a href="/phishing-link-checker">Phishing</a><a href="/qr-code-link-checker">QR code</a><a href="/google-drive-link-checker">Google Drive</a><a href="/dropbox-link-checker">Dropbox</a></nav></details>'
    source = replace_once(source, footer_anchor, footer_block, 'footer navigation')

    meter_anchor = '<div class="result-top"><div id="status-icon" class="status-icon">…</div><div class="result-main"><h2 id="verdict">Analyzing…</h2><p id="summary" class="result-summary">Checking the URL and destination.</p></div></div>\n      <ul id="signals" class="signals hidden"></ul>'
    meter_block = '<div class="result-top"><div id="status-icon" class="status-icon">…</div><div class="result-main"><h2 id="verdict">Analyzing…</h2><p id="summary" class="result-summary">Checking the URL and destination.</p></div></div>\n      <div id="destination" class="destination-box hidden"><div class="destination-label">Final destination</div><strong id="destination-host" class="destination-host">Unknown</strong><div id="destination-note" class="destination-note hidden"></div></div>\n      <div id="risk-meter" class="risk-meter hidden" role="progressbar" aria-label="Risk score" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="risk-head"><span>Risk score</span><strong id="risk-value">0/100</strong></div><div class="risk-track"><span id="risk-fill" class="risk-fill"></span></div></div>\n      <ul id="signals" class="signals hidden"></ul>'
    source = replace_once(source, meter_anchor, meter_block, 'destination and risk meter')

    state_anchor = "  var currentUrl='',lastStatus='unknown',lastVerdict='';"
    state_block = "  var currentUrl='',lastStatus='unknown',lastVerdict='';\n  var destination=document.getElementById('destination'),destinationHost=document.getElementById('destination-host'),destinationNote=document.getElementById('destination-note');\n  var riskMeter=document.getElementById('risk-meter'),riskValue=document.getElementById('risk-value'),riskFill=document.getElementById('risk-fill');"
    source = replace_once(source, state_anchor, state_block, 'result JS references')

    busy_anchor = "  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze'}"
    busy_block = "  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze';form.classList.toggle('is-scanning',!!on)}"
    source = replace_once(source, busy_anchor, busy_block, 'scan animation state')

    loading_anchor = "  function loading(){clearExtra();result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}"
    loading_block = "  function loading(){clearExtra();destination.classList.add('hidden');destinationNote.className='destination-note hidden';destinationNote.textContent='';riskMeter.classList.add('hidden');riskFill.style.width='0%';riskMeter.setAttribute('aria-valuenow','0');result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}"
    source = replace_once(source, loading_anchor, loading_block, 'loading result reset')

    score_anchor = "    var host=data.finalHost||'';var score=Number.isFinite(s.riskScore)?s.riskScore:0;techGrid.innerHTML='<div class=\"tech\"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class=\"tech\"><span>Risk score</span><strong>'+esc(score)+'/100</strong></div><div class=\"tech\"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class=\"tech\"><span>Redirects</span><strong>'+esc(Array.isArray(data.redirects)?data.redirects.length:0)+'</strong></div>';"
    score_block = "    var host=data.finalHost||'';var redirects=Array.isArray(data.redirects)?data.redirects:[];var originalHost='';try{originalHost=new URL(currentUrl).hostname.toLowerCase()}catch(e){}if(host){var finalHost=String(host).toLowerCase();destinationHost.textContent=host;destination.classList.remove('hidden');if(originalHost&&finalHost!==originalHost){destinationNote.textContent=(status==='caution'||status==='high'?'⚠ Destination changed: ':'Redirected: ')+originalHost+' → '+host;destinationNote.className='destination-note'+((status==='caution'||status==='high')?' warn':'')}else if(redirects.length){destinationNote.textContent='Followed '+redirects.length+' redirect'+(redirects.length===1?'':'s')+' to this destination.';destinationNote.className='destination-note'}else{destinationNote.className='destination-note hidden'}}else{destination.classList.add('hidden')}var rawScore=s.riskScore;var hasScore=Number.isFinite(rawScore)&&status!=='unknown';var score=hasScore?Math.max(0,Math.min(100,Math.round(rawScore))):0;if(hasScore){riskValue.textContent=score+'/100';riskFill.style.width=score+'%';riskMeter.setAttribute('aria-valuenow',String(score));riskMeter.classList.remove('hidden')}else{riskMeter.classList.add('hidden')}techGrid.innerHTML='<div class=\"tech\"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class=\"tech\"><span>Risk score</span><strong>'+(hasScore?esc(score)+'/100':'Unavailable')+'</strong></div><div class=\"tech\"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class=\"tech\"><span>Redirects</span><strong>'+esc(redirects.length)+'</strong></div>';"
    source = replace_once(source, score_anchor, score_block, 'destination and risk score renderer')

    HOME.write_text(source, encoding='utf-8')


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    add_favicon_to_pages()
    polish_homepage()
    print('Applied homepage design polish, trust cues and clearer destination results')


if __name__ == '__main__':
    main()
