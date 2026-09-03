#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-scanner-ux-v2-style">
:root{--cist-accent:#6578e8;--cist-accent-soft:rgba(101,120,232,.10);--cist-accent-line:rgba(101,120,232,.24)}
@media(prefers-color-scheme:dark){:root{--cist-accent:#8ea2ff;--cist-accent-soft:rgba(142,162,255,.11);--cist-accent-line:rgba(142,162,255,.25)}}
.input-kind{flex:0 0 auto;margin-right:7px;padding:3px 7px;border:1px solid var(--cist-accent-line);border-radius:999px;background:var(--cist-accent-soft);color:var(--cist-accent);font-size:10px;font-weight:850;line-height:1.35;letter-spacing:.03em}
.scan-progress{width:min(620px,100%);margin:10px auto 0;padding:9px 11px;border:1px solid var(--line);border-radius:11px;background:color-mix(in srgb,var(--soft) 72%,transparent);text-align:left}
.scan-progress-copy{display:flex;align-items:baseline;justify-content:space-between;gap:8px 14px;flex-wrap:wrap;font-size:11px}.scan-progress-copy strong{font-size:11px;color:var(--text)}.scan-progress-copy span{color:var(--muted)}
.scan-progress-bar{display:block;height:3px;margin-top:7px;overflow:hidden;border-radius:999px;background:var(--line)}.scan-progress-bar i{display:block;width:34%;height:100%;border-radius:inherit;background:var(--cist-accent);animation:cistScanTravel 1.15s ease-in-out infinite}
@keyframes cistScanTravel{0%{transform:translateX(-110%)}50%{transform:translateX(100%)}100%{transform:translateX(300%)}}
#signals{display:none!important}
.why-verdict{margin-top:14px;padding:14px 15px;border:1px solid var(--line);border-radius:13px;background:var(--soft);text-align:left}.why-verdict h3{margin:0 0 7px;font-size:13px;letter-spacing:-.01em}.why-list{list-style:none;padding:0;margin:0;display:grid;gap:6px}.why-list li{position:relative;padding-left:14px;color:var(--muted);font-size:13px;line-height:1.42}.why-list li:before{content:"";position:absolute;left:0;top:.58em;width:5px;height:5px;border-radius:50%;background:var(--cist-accent)}
.contextual-prevention{margin-top:12px;padding:12px 14px;border:1px solid var(--cist-accent-line);border-radius:12px;background:var(--cist-accent-soft);text-align:left}.contextual-prevention strong{display:block;margin-bottom:3px;font-size:12px}.contextual-prevention p{margin:0;color:var(--muted);font-size:12px;line-height:1.45}.contextual-prevention a{display:inline-block;margin-top:6px;color:var(--cist-accent);font-size:12px;font-weight:800;text-decoration:none}.contextual-prevention a:hover{text-decoration:underline;text-underline-offset:3px}
.under-form a,.header-mobile-links a,.footer-resource-links a{color:var(--cist-accent)}
.header-dropdown a:hover{color:var(--cist-accent)}
@media(max-width:600px){.input-kind{margin-right:5px;padding:2px 6px;font-size:9px}.scan-progress{margin-top:8px;padding:8px 10px}.scan-progress-copy{display:block}.scan-progress-copy span{display:block;margin-top:2px;font-size:10px}.why-verdict{padding:12px 13px}.contextual-prevention{padding:11px 12px}}
@media(prefers-reduced-motion:reduce){.scan-progress-bar i{animation:none;width:100%;opacity:.7}}
</style>
'''

WHY_BLOCK = r'''      <section id="why-verdict" class="why-verdict hidden" aria-labelledby="why-verdict-title">
        <h3 id="why-verdict-title">Why this verdict?</h3>
        <ul id="why-list" class="why-list"></ul>
      </section>
'''

PREVENTION_BLOCK = r'''      <aside id="contextual-prevention" class="contextual-prevention hidden" aria-live="polite">
        <strong id="prevention-title">Safety guidance</strong>
        <p id="prevention-copy"></p>
        <a id="prevention-link" href="/scam-prevention">Open prevention guide</a>
      </aside>
'''

PROGRESS_BLOCK = r'''    <div id="scan-progress" class="scan-progress hidden" role="status" aria-live="polite">
      <div class="scan-progress-copy"><strong id="scan-progress-title">Checking link signals…</strong><span id="scan-progress-items">Domain · Redirects · Phishing signals · Downloads</span></div>
      <span class="scan-progress-bar" aria-hidden="true"><i></i></span>
    </div>
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Scanner UX v2 failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    if 'id="cist-scanner-ux-v2-style"' not in source:
        source = source.replace('</head>', STYLE + '\n</head>', 1)

    input_pattern = re.compile(r'(<div class="input-wrap"><input id="url"[^>]*>)(<button id="paste" class="paste" type="button">Paste</button></div>)')
    source, count = input_pattern.subn(r'\1<span id="input-kind" class="input-kind hidden" aria-live="polite"></span>\2', source, count=1)
    if count != 1:
        raise RuntimeError(f'Scanner UX v2 failed: universal input anchor replaced {count} times')

    source = replace_once(source, '</form>\n    <div class="check-strip"', '</form>\n' + PROGRESS_BLOCK + '    <div class="check-strip"', 'scan progress placement')

    source = replace_once(source, '      <ul id="signals" class="signals hidden"></ul>', WHY_BLOCK + '      <ul id="signals" class="signals hidden"></ul>', 'why verdict placement')
    source = replace_once(source, '      <div id="actions" class="actions hidden">', PREVENTION_BLOCK + '      <div id="actions" class="actions hidden">', 'prevention placement')

    state_anchor = "  var currentUrl='',currentInputType='url',lastStatus='unknown',lastVerdict='';"
    state_block = state_anchor + "\n  var inputKind=document.getElementById('input-kind'),scanProgress=document.getElementById('scan-progress'),scanProgressTitle=document.getElementById('scan-progress-title'),scanProgressItems=document.getElementById('scan-progress-items');\n  var whyVerdict=document.getElementById('why-verdict'),whyList=document.getElementById('why-list'),contextualPrevention=document.getElementById('contextual-prevention'),preventionTitle=document.getElementById('prevention-title'),preventionCopy=document.getElementById('prevention-copy'),preventionLink=document.getElementById('prevention-link');"
    source = replace_once(source, state_anchor, state_block, 'scanner UX references')

    normalize_anchor = "  function normalize(v){v=String(v||'').trim();if(v&&!/^https?:\\/\\//i.test(v))v='https://'+v;return v}"
    helpers = r'''
  function updateInputKind(){var v=String(input.value||'').trim();if(!v){inputKind.classList.add('hidden');inputKind.textContent='';return}if(looksLikeEmail(v)){inputKind.textContent='Email';inputKind.classList.remove('hidden');return}if(/^https?:\/\//i.test(v)||/^www\./i.test(v)||/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}(?:[\/:?#]|$)/i.test(v)){inputKind.textContent='Link';inputKind.classList.remove('hidden');return}inputKind.classList.add('hidden');inputKind.textContent=''}
  function setScanProgress(on){if(!scanProgress)return;if(!on){scanProgress.classList.add('hidden');return}if(currentInputType==='email'){scanProgressTitle.textContent='Checking email signals…';scanProgressItems.textContent='Address · Mail setup · Impersonation · Domain age'}else{scanProgressTitle.textContent='Checking link signals…';scanProgressItems.textContent='Domain · Redirects · Phishing signals · Downloads'}scanProgress.classList.remove('hidden')}
  function preventionFor(data,status){if(status!=='caution'&&status!=='high')return null;var s=data&&data.safety?data.safety:{};var sig=Array.isArray(s.signals)?s.signals:[];var codes=sig.map(function(x){return String(x&&x.code||'')});var has=function(code){return codes.indexOf(code)>=0};var starts=function(prefix){return codes.some(function(code){return code.indexOf(prefix)===0})};if(currentInputType==='email'){return{title:'Suspicious sender?',copy:'Verify the sender through an official website or a separate trusted channel before replying, paying or sharing information.',href:'/scam-warning-signs',label:'Review scam warning signs'}}if(has('executable-download')||has('binary-content')||has('forced-download')||has('archive-download')){return{title:'Unexpected file or download?',copy:'Do not run an unexpected file. Check the source independently before downloading or opening anything.',href:'/can-a-link-give-you-a-virus',label:'Read the malware-link safety guide'}}if(has('phishing-language')||starts('brand-')||has('password-over-http')||has('punycode')){return{title:'Phishing signs detected',copy:'Do not sign in from the message. Open the service through its official app or type the known website address yourself.',href:'/how-to-tell-if-a-link-is-phishing',label:'See how to verify a phishing link'}}if(has('domain-change')||has('many-redirects')||has('shortener')){return{title:'Redirect warning',copy:'The visible link may not be the final destination. Verify the final domain before entering information or downloading files.',href:'/redirect-risk-explained',label:'Understand redirect risk'}}return{title:'Think this may be a scam?',copy:'Verify the sender independently and avoid payments, passwords or personal information until the request is confirmed.',href:'/scam-prevention',label:'Open the scam prevention guide'}}
  function renderScannerUx(data){var s=data&&data.safety?data.safety:{};var status=['low','caution','high'].indexOf(s.status)>=0?s.status:'unknown';var list=Array.isArray(s.signals)?s.signals.slice(0,3):[];var reasons=[];if(list.length){reasons=list.map(function(x){return String(x&&x.title||x&&x.detail||'Warning sign detected')})}else if(status==='low'){reasons=[currentInputType==='email'?'No high-risk address or domain warning signs were found in the checks completed.':'No high-risk URL, redirect or download warning signs were found in the checks completed.']}else if(status==='unknown'){reasons=['The check did not return enough information for a confident assessment.']}if(reasons.length){whyList.innerHTML=reasons.map(function(x){return '<li>'+esc(x)+'</li>'}).join('');whyVerdict.classList.remove('hidden')}else{whyVerdict.classList.add('hidden');whyList.innerHTML=''}var p=preventionFor(data,status);if(p){preventionTitle.textContent=p.title;preventionCopy.textContent=p.copy;preventionLink.href=p.href;preventionLink.textContent=p.label;contextualPrevention.classList.remove('hidden')}else{contextualPrevention.classList.add('hidden')}}
'''
    source = replace_once(source, normalize_anchor, normalize_anchor + helpers, 'scanner UX helpers')

    busy_anchor = "  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze';form.classList.toggle('is-scanning',!!on)}"
    busy_block = "  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze';form.classList.toggle('is-scanning',!!on);setScanProgress(!!on)}"
    source = replace_once(source, busy_anchor, busy_block, 'scan progress state')

    clear_anchor = "  function clearExtra(){signals.classList.add('hidden');advice.classList.add('hidden');actions.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden');technical.classList.add('hidden');technical.open=false;signals.innerHTML='';techGrid.innerHTML='';providers.innerHTML=''}"
    clear_block = "  function clearExtra(){signals.classList.add('hidden');advice.classList.add('hidden');actions.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden');technical.classList.add('hidden');whyVerdict.classList.add('hidden');contextualPrevention.classList.add('hidden');technical.open=false;signals.innerHTML='';whyList.innerHTML='';techGrid.innerHTML='';providers.innerHTML=''}"
    source = replace_once(source, clear_anchor, clear_block, 'scanner UX reset')

    verdict_anchor = "    if(currentInputType==='email'){lastVerdict=status==='low'?'NO OBVIOUS SUSPICIOUS SIGNALS':status==='caution'?'SUSPICIOUS EMAIL SIGNALS':status==='high'?'HIGH-RISK EMAIL SIGNALS':'CHECK INCOMPLETE';summary.textContent=status==='low'?'No obvious suspicious email address or domain signals were detected.':status==='caution'?'Suspicious email address or domain characteristics were detected.':status==='high'?'High-risk email address warning signs were detected. Verify the sender independently.':(data.error||'We could not fully assess this email address.')}else{lastVerdict=status==='low'?'NO KNOWN DANGER FOUND':status==='caution'?'BE CAREFUL':status==='high'?'DANGEROUS LINK SIGNALS':'CHECK INCOMPLETE';summary.textContent=status==='low'?'No obvious scam or malicious URL pattern was detected.':status==='caution'?'Suspicious characteristics were detected.':status==='high'?'High-risk warning signs were detected. Do not open it.':(data.error||'We could not fully assess this destination.')}verdict.textContent=lastVerdict;"
    verdict_block = "    if(currentInputType==='email'){lastVerdict=status==='low'?'Looks low risk':status==='caution'?'Use caution':status==='high'?'High-risk email':'Check incomplete';summary.textContent=status==='low'?'No obvious high-risk address or domain signals were detected.':status==='caution'?'Some address or domain warning signs need verification.':status==='high'?'Strong email warning signs were detected. Verify the sender independently.':(data.error||'We could not fully assess this email address.')}else{lastVerdict=status==='low'?'Looks low risk':status==='caution'?'Use caution':status==='high'?'High-risk link':'Check incomplete';summary.textContent=status==='low'?'No obvious high-risk link signals were detected.':status==='caution'?'Some link warning signs need verification before you continue.':status==='high'?'Strong warning signs were detected. Do not open this link.':(data.error||'We could not fully assess this destination.')}verdict.textContent=lastVerdict;"
    source = replace_once(source, verdict_anchor, verdict_block, 'clearer verdict copy')

    if 'renderScannerUx(d)' not in source or 'renderScannerUx(failed)' not in source:
        raise RuntimeError('Scanner UX v2 failed: result renderer hooks not found')

    paste_anchor = "  input.addEventListener('paste',function(){track('paste')});"
    paste_block = "  input.addEventListener('input',updateInputKind);\n  input.addEventListener('paste',function(){track('paste');setTimeout(updateInputKind,0)});"
    source = replace_once(source, paste_anchor, paste_block, 'input type detection listener')

    clipboard_anchor = "if(text){input.value=text;track('paste');input.focus()}"
    clipboard_block = "if(text){input.value=text;updateInputKind();track('paste');input.focus()}"
    source = replace_once(source, clipboard_anchor, clipboard_block, 'clipboard type detection')

    again_anchor = "  again.addEventListener('click',function(){result.classList.add('hidden');input.value='';currentUrl='';currentInputType='url';deep.classList.remove('hidden');input.focus()});"
    again_block = "  again.addEventListener('click',function(){result.classList.add('hidden');input.value='';currentUrl='';currentInputType='url';deep.classList.remove('hidden');updateInputKind();input.focus()});"
    source = replace_once(source, again_anchor, again_block, 'reset type badge')

    required = [
        'id="input-kind"',
        'id="scan-progress"',
        'id="why-verdict"',
        'Why this verdict?',
        'id="contextual-prevention"',
        'renderScannerUx(d)',
        'Checking link signals…',
        'Checking email signals…',
        "'Looks low risk'",
        "'High-risk link'",
        "'High-risk email'",
        '/scam-warning-signs',
        '/can-a-link-give-you-a-virus',
        '/how-to-tell-if-a-link-is-phishing',
        '/redirect-risk-explained',
        '/scam-prevention',
        '#8ea2ff',
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Scanner UX v2 guard failed: missing {token}')

    if 'completed ·' in source.lower():
        raise RuntimeError('Scanner UX must not imply real-time completion stages without backend progress events')

    HOME.write_text(source, encoding='utf-8')
    print('Applied input detection, clearer verdicts, explanation, contextual prevention and scan animation')


if __name__ == '__main__':
    main()
