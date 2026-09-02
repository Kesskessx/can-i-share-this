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
.scan-form{transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease}
.scan-form.is-scanning{border-color:var(--green);animation:cistScanPulse 1.15s ease-in-out infinite}
@keyframes cistScanPulse{0%,100%{box-shadow:var(--shadow),0 0 0 0 var(--cist-scan-glow)}50%{box-shadow:var(--shadow),0 0 0 5px var(--cist-scan-glow)}}
.risk-meter{margin:18px 0 0;padding:13px 14px;border:1px solid var(--line);border-radius:13px;background:var(--soft)}
.risk-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px;font-size:13px}
.risk-head span{color:var(--muted);font-weight:750}.risk-head strong{font-size:13px}
.risk-track{height:7px;overflow:hidden;border-radius:999px;background:var(--line)}
.risk-fill{display:block;width:0;height:100%;border-radius:inherit;background:var(--muted);transition:width .4s ease,background-color .2s ease}
.status-low .risk-fill{background:var(--green)}.status-caution .risk-fill{background:var(--amber)}.status-high .risk-fill{background:var(--red)}
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

    meter_anchor = '<div class="result-top"><div id="status-icon" class="status-icon">…</div><div class="result-main"><h2 id="verdict">Analyzing…</h2><p id="summary" class="result-summary">Checking the URL and destination.</p></div></div>\n      <ul id="signals" class="signals hidden"></ul>'
    meter_block = '<div class="result-top"><div id="status-icon" class="status-icon">…</div><div class="result-main"><h2 id="verdict">Analyzing…</h2><p id="summary" class="result-summary">Checking the URL and destination.</p></div></div>\n      <div id="risk-meter" class="risk-meter hidden" role="progressbar" aria-label="Risk score" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="risk-head"><span>Risk score</span><strong id="risk-value">0/100</strong></div><div class="risk-track"><span id="risk-fill" class="risk-fill"></span></div></div>\n      <ul id="signals" class="signals hidden"></ul>'
    source = replace_once(source, meter_anchor, meter_block, 'risk meter')

    state_anchor = "  var currentUrl='',lastStatus='unknown',lastVerdict='';"
    state_block = "  var currentUrl='',lastStatus='unknown',lastVerdict='';\n  var riskMeter=document.getElementById('risk-meter'),riskValue=document.getElementById('risk-value'),riskFill=document.getElementById('risk-fill');"
    source = replace_once(source, state_anchor, state_block, 'risk meter JS references')

    busy_anchor = "  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze'}"
    busy_block = "  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze';form.classList.toggle('is-scanning',!!on)}"
    source = replace_once(source, busy_anchor, busy_block, 'scan animation state')

    loading_anchor = "  function loading(){clearExtra();result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}"
    loading_block = "  function loading(){clearExtra();riskMeter.classList.add('hidden');riskFill.style.width='0%';riskMeter.setAttribute('aria-valuenow','0');result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}"
    source = replace_once(source, loading_anchor, loading_block, 'loading risk reset')

    score_anchor = "    var host=data.finalHost||'';var score=Number.isFinite(s.riskScore)?s.riskScore:0;techGrid.innerHTML='<div class=\"tech\"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class=\"tech\"><span>Risk score</span><strong>'+esc(score)+'/100</strong></div><div class=\"tech\"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class=\"tech\"><span>Redirects</span><strong>'+esc(Array.isArray(data.redirects)?data.redirects.length:0)+'</strong></div>';"
    score_block = "    var host=data.finalHost||'';var rawScore=s.riskScore;var hasScore=Number.isFinite(rawScore)&&status!=='unknown';var score=hasScore?Math.max(0,Math.min(100,Math.round(rawScore))):0;if(hasScore){riskValue.textContent=score+'/100';riskFill.style.width=score+'%';riskMeter.setAttribute('aria-valuenow',String(score));riskMeter.classList.remove('hidden')}else{riskMeter.classList.add('hidden')}techGrid.innerHTML='<div class=\"tech\"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class=\"tech\"><span>Risk score</span><strong>'+(hasScore?esc(score)+'/100':'Unavailable')+'</strong></div><div class=\"tech\"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class=\"tech\"><span>Redirects</span><strong>'+esc(Array.isArray(data.redirects)?data.redirects.length:0)+'</strong></div>';"
    source = replace_once(source, score_anchor, score_block, 'risk score renderer')

    HOME.write_text(source, encoding='utf-8')


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    add_favicon_to_pages()
    polish_homepage()
    print('Applied homepage design polish and premium favicon')


if __name__ == '__main__':
    main()
