#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise RuntimeError(f'Email input integration failed: {label} anchor not found')
    return source.replace(old, new, 1)


def main() -> None:
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')

    source = HOME.read_text(encoding='utf-8')

    source = replace_once(
        source,
        'inputmode="url" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Paste a link here…" aria-label="Link to analyze"',
        'inputmode="text" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Paste a link or email address…" aria-label="Link or email address to analyze"',
        'universal input copy'
    )
    source = replace_once(source, '🔒 Links aren’t stored', '🔒 Inputs aren’t stored', 'privacy wording')

    state_anchor = "  var currentUrl='',lastStatus='unknown',lastVerdict='';"
    state_block = "  var currentUrl='',currentInputType='url',lastStatus='unknown',lastVerdict='';"
    source = replace_once(source, state_anchor, state_block, 'input type state')

    normalize_anchor = "  function normalize(v){v=String(v||'').trim();if(v&&!/^https?:\\/\\//i.test(v))v='https://'+v;return v}"
    normalize_block = "  function emailValue(v){return String(v||'').trim().replace(/^mailto:/i,'')}\n  function looksLikeEmail(v){v=emailValue(v);return /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v)}\n  function normalize(v){v=String(v||'').trim();if(v&&!/^https?:\\/\\//i.test(v))v='https://'+v;return v}"
    source = replace_once(source, normalize_anchor, normalize_block, 'input detector')

    loading_anchor = "  function loading(){clearExtra();destination.classList.add('hidden');destinationNote.className='destination-note hidden';destinationNote.textContent='';riskMeter.classList.add('hidden');riskFill.style.width='0%';riskMeter.setAttribute('aria-valuenow','0');result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}"
    loading_block = "  function loading(){clearExtra();destination.classList.add('hidden');destinationNote.className='destination-note hidden';destinationNote.textContent='';riskMeter.classList.add('hidden');riskFill.style.width='0%';riskMeter.setAttribute('aria-valuenow','0');result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent=currentInputType==='email'?'Checking the email address and domain.':'Checking the URL and destination.'}"
    source = replace_once(source, loading_anchor, loading_block, 'type-aware loading text')

    guidance_anchor = "  function guidance(status){if(status==='high')return 'Do not open this link. Delete the message and visit the company or service through its official website instead.';if(status==='caution')return 'Verify the sender and the final domain before continuing. Avoid signing in, paying, or downloading anything until you are sure.';if(status==='low')return 'If you expected this link, you can continue cautiously. Be extra careful if the message asks for a password, payment, or download.';return 'Do not trust the link yet. Verify the sender or use the official website directly.'}"
    guidance_block = "  function guidance(status){if(currentInputType==='email'){if(status==='high')return 'Do not trust this sender yet. Verify the organization through its official website or another channel before replying, paying, or sharing personal information.';if(status==='caution')return 'Verify the sender independently before replying, opening attachments, paying, or sharing sensitive information.';if(status==='low')return 'No obvious address-level warning signs were found. This does not prove that the person using the mailbox is trustworthy.';return 'The address could not be fully checked. Verify the sender through another channel.'}if(status==='high')return 'Do not open this link. Delete the message and visit the company or service through its official website instead.';if(status==='caution')return 'Verify the sender and the final domain before continuing. Avoid signing in, paying, or downloading anything until you are sure.';if(status==='low')return 'If you expected this link, you can continue cautiously. Be extra careful if the message asks for a password, payment, or download.';return 'Do not trust the link yet. Verify the sender or use the official website directly.'}"
    source = replace_once(source, guidance_anchor, guidance_block, 'email guidance')

    verdict_anchor = "    lastVerdict=status==='low'?'NO KNOWN DANGER FOUND':status==='caution'?'BE CAREFUL':status==='high'?'DANGEROUS LINK SIGNALS':'CHECK INCOMPLETE';verdict.textContent=lastVerdict;\n    summary.textContent=status==='low'?'No obvious scam or malicious URL pattern was detected.':status==='caution'?'Suspicious characteristics were detected.':status==='high'?'High-risk warning signs were detected. Do not open it.':(data.error||'We could not fully assess this destination.');"
    verdict_block = "    if(currentInputType==='email'){lastVerdict=status==='low'?'NO OBVIOUS SUSPICIOUS SIGNALS':status==='caution'?'SUSPICIOUS EMAIL SIGNALS':status==='high'?'HIGH-RISK EMAIL SIGNALS':'CHECK INCOMPLETE';summary.textContent=status==='low'?'No obvious suspicious email address or domain signals were detected.':status==='caution'?'Suspicious email address or domain characteristics were detected.':status==='high'?'High-risk email address warning signs were detected. Verify the sender independently.':(data.error||'We could not fully assess this email address.')}else{lastVerdict=status==='low'?'NO KNOWN DANGER FOUND':status==='caution'?'BE CAREFUL':status==='high'?'DANGEROUS LINK SIGNALS':'CHECK INCOMPLETE';summary.textContent=status==='low'?'No obvious scam or malicious URL pattern was detected.':status==='caution'?'Suspicious characteristics were detected.':status==='high'?'High-risk warning signs were detected. Do not open it.':(data.error||'We could not fully assess this destination.')}verdict.textContent=lastVerdict;"
    source = replace_once(source, verdict_anchor, verdict_block, 'type-aware verdict')

    actions_anchor = "    adviceText.textContent=guidance(status);advice.classList.remove('hidden');actions.classList.remove('hidden');technical.classList.remove('hidden');"
    actions_block = "    adviceText.textContent=guidance(status);advice.classList.remove('hidden');actions.classList.remove('hidden');technical.classList.remove('hidden');if(currentInputType==='email'){deep.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden')}else{deep.classList.remove('hidden')}"
    source = replace_once(source, actions_anchor, actions_block, 'email action controls')

    score_anchor = "    var host=data.finalHost||'';var redirects=Array.isArray(data.redirects)?data.redirects:[];var originalHost='';try{originalHost=new URL(currentUrl).hostname.toLowerCase()}catch(e){}if(host){var finalHost=String(host).toLowerCase();destinationHost.textContent=host;destination.classList.remove('hidden');if(originalHost&&finalHost!==originalHost){destinationNote.textContent=(status==='caution'||status==='high'?'⚠ Destination changed: ':'Redirected: ')+originalHost+' → '+host;destinationNote.className='destination-note'+((status==='caution'||status==='high')?' warn':'')}else if(redirects.length){destinationNote.textContent='Followed '+redirects.length+' redirect'+(redirects.length===1?'':'s')+' to this destination.';destinationNote.className='destination-note'}else{destinationNote.className='destination-note hidden'}}else{destination.classList.add('hidden')}var rawScore=s.riskScore;var hasScore=Number.isFinite(rawScore)&&status!=='unknown';var score=hasScore?Math.max(0,Math.min(100,Math.round(rawScore))):0;if(hasScore){riskValue.textContent=score+'/100';riskFill.style.width=score+'%';riskMeter.setAttribute('aria-valuenow',String(score));riskMeter.classList.remove('hidden')}else{riskMeter.classList.add('hidden')}techGrid.innerHTML='<div class=\"tech\"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class=\"tech\"><span>Risk score</span><strong>'+(hasScore?esc(score)+'/100':'Unavailable')+'</strong></div><div class=\"tech\"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class=\"tech\"><span>Redirects</span><strong>'+esc(redirects.length)+'</strong></div>';"
    score_block = "    var rawScore=s.riskScore;var hasScore=Number.isFinite(rawScore)&&status!=='unknown';var score=hasScore?Math.max(0,Math.min(100,Math.round(rawScore))):0;if(hasScore){riskValue.textContent=score+'/100';riskFill.style.width=score+'%';riskMeter.setAttribute('aria-valuenow',String(score));riskMeter.classList.remove('hidden')}else{riskMeter.classList.add('hidden')}if(currentInputType==='email'){var info=data&&data.email?data.email:{};var emailDomain=data.emailDomain||info.domain||'';var destinationLabel=destination.querySelector('.destination-label');if(destinationLabel)destinationLabel.textContent='Email domain';if(emailDomain){destinationHost.textContent=emailDomain;destination.classList.remove('hidden');destinationNote.className='destination-note hidden'}else{destination.classList.add('hidden')}techGrid.innerHTML='<div class=\"tech\"><span>Email domain</span><strong>'+esc(emailDomain||'Unknown')+'</strong></div><div class=\"tech\"><span>MX records</span><strong>'+(info.hasMx?'Found':'Not found')+'</strong></div><div class=\"tech\"><span>SPF</span><strong>'+(info.hasSpf?'Found':'Not found')+'</strong></div><div class=\"tech\"><span>DMARC</span><strong>'+(info.hasDmarc?'Found':'Not found')+'</strong></div>'}else{var destinationLabel=destination.querySelector('.destination-label');if(destinationLabel)destinationLabel.textContent='Final destination';var host=data.finalHost||'';var redirects=Array.isArray(data.redirects)?data.redirects:[];var originalHost='';try{originalHost=new URL(currentUrl).hostname.toLowerCase()}catch(e){}if(host){var finalHost=String(host).toLowerCase();destinationHost.textContent=host;destination.classList.remove('hidden');if(originalHost&&finalHost!==originalHost){destinationNote.textContent=(status==='caution'||status==='high'?'⚠ Destination changed: ':'Redirected: ')+originalHost+' → '+host;destinationNote.className='destination-note'+((status==='caution'||status==='high')?' warn':'')}else if(redirects.length){destinationNote.textContent='Followed '+redirects.length+' redirect'+(redirects.length===1?'':'s')+' to this destination.';destinationNote.className='destination-note'}else{destinationNote.className='destination-note hidden'}}else{destination.classList.add('hidden')}techGrid.innerHTML='<div class=\"tech\"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class=\"tech\"><span>Risk score</span><strong>'+(hasScore?esc(score)+'/100':'Unavailable')+'</strong></div><div class=\"tech\"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class=\"tech\"><span>Redirects</span><strong>'+esc(redirects.length)+'</strong></div>'}"
    source = replace_once(source, score_anchor, score_block, 'email technical renderer')

    run_anchor = "  async function runScan(url){currentUrl=normalize(url);if(!currentUrl)return;input.value=currentUrl;loading();busy(true);track('analyze');try{var r=await fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl})});var d=await r.json();renderQuick(d);trackScanSummary(d)}catch(e){renderQuick({error:'The safety check could not complete.',safety:{status:'unknown',riskScore:0,signals:[]}})}finally{busy(false)}}"
    run_block = "  function notifyResultUpdated(){document.dispatchEvent(new CustomEvent('cist:result-updated'))}\n  async function fetchJson(endpoint,payload,timeoutMs){var controller=typeof AbortController==='function'?new AbortController():null;var timer=setTimeout(function(){if(controller)controller.abort()},timeoutMs);try{var options={method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)};if(controller)options.signal=controller.signal;var r=await fetch(endpoint,options);var d=await r.json();if(!r.ok)throw new Error(d&&d.error?d.error:'Request failed.');return d}finally{clearTimeout(timer)}}\n  async function runScan(value){var raw=String(value||'').trim();if(!raw)return;currentInputType=looksLikeEmail(raw)?'email':'url';currentUrl=currentInputType==='email'?emailValue(raw):normalize(raw);if(!currentUrl)return;input.value=currentUrl;loading();busy(true);track('analyze');try{var endpoint=currentInputType==='email'?'/api/email-check':'/api/check';var payload=currentInputType==='email'?{input:currentUrl}:{url:currentUrl};var d=await fetchJson(endpoint,payload,currentInputType==='email'?6500:9000);renderQuick(d);renderScannerUx(d);notifyResultUpdated();if(currentInputType==='url')trackScanSummary(d)}catch(e){var timedOut=e&&e.name==='AbortError';var failed={inputType:currentInputType,error:timedOut?(currentInputType==='email'?'The email check took too long. Try again.':'The link took too long to respond. Try again or verify the destination manually.'):(currentInputType==='email'?'The email address check could not complete.':'The safety check could not complete.'),safety:{status:'unknown',riskScore:0,signals:[]}};renderQuick(failed);renderScannerUx(failed);notifyResultUpdated()}finally{busy(false)}}"
    source = replace_once(source, run_anchor, run_block, 'endpoint routing')

    deep_anchor = "var r=await fetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl,consent:true})});var d=await r.json();"
    deep_block = "var d=await fetchJson('/api/deep-check',{url:currentUrl,consent:true},8000);"
    source = replace_once(source, deep_anchor, deep_block, 'deep check timeout')

    again_anchor = "  again.addEventListener('click',function(){result.classList.add('hidden');input.value='';currentUrl='';input.focus()});"
    again_block = "  again.addEventListener('click',function(){result.classList.add('hidden');input.value='';currentUrl='';currentInputType='url';deep.classList.remove('hidden');input.focus()});"
    source = replace_once(source, again_anchor, again_block, 'reset input type')

    deep_anchor = "  deep.addEventListener('click',function(){consent.classList.remove('hidden')});deepCancel.addEventListener('click',function(){consent.classList.add('hidden')});"
    deep_block = "  deep.addEventListener('click',function(){if(currentInputType==='email')return;consent.classList.remove('hidden')});deepCancel.addEventListener('click',function(){consent.classList.add('hidden')});"
    source = replace_once(source, deep_anchor, deep_block, 'email deep-scan guard')

    share_anchor = "  share.addEventListener('click',async function(){var text='Can I Share This? result: '+lastVerdict+'. '+(lastStatus==='high'?'Do not open this link.':lastStatus==='caution'?'Use caution before opening this link.':'No obvious danger was found, but no scanner can guarantee safety.')+' Check suspicious links at https://canisharethis.com/';try{if(navigator.share)await navigator.share({title:'Can I Share This? link safety result',text:text});else{await navigator.clipboard.writeText(text);share.textContent='Copied';setTimeout(function(){share.textContent='Share result'},1500)}}catch(e){}});"
    share_block = "  share.addEventListener('click',async function(){var emailMode=currentInputType==='email';var note=emailMode?(lastStatus==='high'?'Verify this sender independently before replying or sharing information.':lastStatus==='caution'?'Use caution and verify the sender independently.':'No obvious address-level warning signs were found, but this does not prove the sender is trustworthy.'):(lastStatus==='high'?'Do not open this link.':lastStatus==='caution'?'Use caution before opening this link.':'No obvious danger was found, but no scanner can guarantee safety.');var text='Can I Share This? result: '+lastVerdict+'. '+note+' Check suspicious '+(emailMode?'email addresses':'links')+' at https://canisharethis.com/';try{if(navigator.share)await navigator.share({title:'Can I Share This? safety result',text:text});else{await navigator.clipboard.writeText(text);share.textContent='Copied';setTimeout(function(){share.textContent='Share result'},1500)}}catch(e){}});"
    source = replace_once(source, share_anchor, share_block, 'type-aware share copy')

    required = [
        "'/api/email-check'",
        "currentInputType==='email'",
        'Paste a link or email address…',
        'Email domain',
        'MX records',
        'SPF',
        'DMARC',
        'AbortController',
        "fetchJson('/api/deep-check'",
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Email integration guard failed: missing {token}')

    # Privacy guard: email values are sent only to the dedicated checker, never to telemetry.
    run_section = source[source.index('async function runScan'):source.index("form.addEventListener", source.index('async function runScan'))]
    if "trackScanSummary(d)" not in run_section or "if(currentInputType==='url')trackScanSummary(d)" not in run_section:
        raise RuntimeError('Email integration privacy guard failed: aggregate telemetry is not URL-scoped')

    HOME.write_text(source, encoding='utf-8')
    print('Integrated email address checks into the existing homepage input')


if __name__ == '__main__':
    main()
