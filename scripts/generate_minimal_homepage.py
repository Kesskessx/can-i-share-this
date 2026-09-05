#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Is This Link Safe? — Can I Share This?</title>
  <meta name="description" content="Paste a suspicious link and get a simple scam, phishing, redirect and risky-download check before you open it.">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://canisharethis.com/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Is This Link Safe? — Can I Share This?">
  <meta property="og:description" content="Paste a suspicious link. Analyze it before you open it.">
  <meta property="og:url" content="https://canisharethis.com/">
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"Can I Share This?","url":"https://canisharethis.com/","description":"Simple link safety checks for suspicious URLs."}</script>
  <style>
    :root{color-scheme:light dark;--bg:#f7f8fa;--card:#fff;--text:#17191d;--muted:#6d7480;--line:#e2e5e9;--button:#17191d;--buttonText:#fff;--soft:#f1f3f5;--green:#137333;--amber:#9a5b00;--red:#b3261e;--shadow:0 18px 50px rgba(17,24,39,.08)}
    @media(prefers-color-scheme:dark){:root{--bg:#0d0f12;--card:#15181d;--text:#f4f5f7;--muted:#a6acb7;--line:#2a2f37;--button:#f4f5f7;--buttonText:#111318;--soft:#1c2026;--green:#75d18b;--amber:#ffc266;--red:#ff8f87;--shadow:0 18px 50px rgba(0,0,0,.28)}}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}button,input{font:inherit}a{color:inherit}.hidden{display:none!important}
    header{height:64px;border-bottom:1px solid var(--line);display:flex;align-items:center}.top{width:min(920px,calc(100% - 32px));margin:auto;display:flex;justify-content:space-between;align-items:center}.brand{text-decoration:none;font-weight:850;letter-spacing:-.025em}.qr-top{font-size:13px;color:var(--muted);text-decoration:none}
    main{width:min(720px,calc(100% - 28px));margin:auto;padding:clamp(40px,4vw,48px) 0 64px}.hero{text-align:center}.eyebrow{margin:0 0 12px;font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}h1{font-size:clamp(40px,8vw,66px);line-height:.98;letter-spacing:-.055em;margin:0}.sub{max-width:570px;margin:17px auto 26px;color:var(--muted);font-size:clamp(16px,2.2vw,19px)}
    .scan-form{display:flex;gap:8px;padding:8px;background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}.input-wrap{display:flex;align-items:center;flex:1;min-width:0}.input-wrap input{min-width:0;flex:1;height:52px;border:0;outline:0;background:transparent;color:var(--text);padding:0 12px}.paste{height:38px;border:0;background:var(--soft);color:var(--text);border-radius:10px;padding:0 11px;font-weight:750;cursor:pointer}.primary{height:52px;border:0;border-radius:12px;background:var(--button);color:var(--buttonText);padding:0 22px;font-weight:850;cursor:pointer}.primary:disabled{opacity:.55}.under-form{display:flex;justify-content:center;gap:8px 14px;flex-wrap:wrap;margin-top:12px;font-size:12px;color:var(--muted)}.under-form a{text-underline-offset:3px}
    #result{margin-top:24px}.result-card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:clamp(20px,4vw,28px);box-shadow:var(--shadow)}.result-top{display:flex;gap:13px;align-items:flex-start}.status-icon{width:42px;height:42px;display:grid;place-items:center;border-radius:50%;background:var(--soft);font-size:21px;font-weight:900;flex:0 0 auto}.result-main h2{margin:0;font-size:clamp(24px,4vw,31px);line-height:1.12;letter-spacing:-.035em}.result-summary{margin:7px 0 0;color:var(--muted)}.status-low .status-icon,.status-low h2{color:var(--green)}.status-caution .status-icon,.status-caution h2{color:var(--amber)}.status-high .status-icon,.status-high h2{color:var(--red)}
    .signals{list-style:none;padding:0;margin:17px 0 0;display:grid;gap:8px}.signals li{padding:11px 13px;border-radius:11px;background:var(--soft);font-size:14px}.advice{margin-top:18px;padding:15px;border:1px solid var(--line);border-radius:13px}.advice strong{display:block;margin-bottom:4px}.advice p{margin:0;color:var(--muted);font-size:14px}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:17px}.secondary{border:1px solid var(--line);background:transparent;color:var(--text);border-radius:10px;padding:9px 12px;font-weight:750;cursor:pointer}.consent,.reputation{margin-top:13px;padding:13px 14px;border-radius:12px;background:var(--soft);font-size:13px}.consent p{margin:0 0 10px}.consent-actions{display:flex;gap:8px}.small-primary,.small-secondary{border-radius:9px;padding:8px 11px;font-weight:800;cursor:pointer}.small-primary{border:0;background:var(--button);color:var(--buttonText)}.small-secondary{border:1px solid var(--line);background:var(--card);color:var(--text)}.reputation.bad{color:var(--red)}.reputation.good{color:var(--green)}
    details.technical{margin-top:15px;border-top:1px solid var(--line);padding-top:13px}details.technical summary{cursor:pointer;color:var(--muted);font-size:13px;font-weight:750}.tech-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:11px}.tech{padding:10px 11px;background:var(--soft);border-radius:10px}.tech span{display:block;color:var(--muted);font-size:11px}.tech strong{font-size:13px;word-break:break-word}.providers{list-style:none;padding:0;margin:8px 0 0;display:grid;gap:7px}.providers li{padding:9px 11px;background:var(--soft);border-radius:9px;font-size:12px}
    footer{width:min(720px,calc(100% - 28px));margin:0 auto 32px;text-align:center;color:var(--muted);font-size:12px}.footer-line{border-top:1px solid var(--line);padding-top:22px}footer details{margin-top:9px}footer nav{display:flex;justify-content:center;gap:8px 13px;flex-wrap:wrap;margin-top:9px}
    @media(max-width:600px){header{height:58px}.qr-top{display:none}main{padding-top:44px}.scan-form{display:block}.input-wrap{height:50px}.primary{width:100%;height:48px}.result-card{border-radius:16px}.tech-grid{grid-template-columns:1fr}.actions>*{flex:1}.consent-actions>*{flex:1}}
  </style>
</head>
<body>
<header><div class="top"><a class="brand" href="/">↗ Can I Share This?</a><a class="qr-top" href="/qr-code-link-checker">Scan QR</a></div></header>
<main>
  <section class="hero" aria-labelledby="page-title">
    <p class="eyebrow">Link safety checker</p>
    <h1 id="page-title">Is this link safe?</h1>
    <p class="sub">Paste a suspicious link. We’ll check the warning signs before you open it.</p>
    <form id="scan-form" class="scan-form">
      <div class="input-wrap"><input id="url" type="text" inputmode="url" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Paste a link here…" aria-label="Link to analyze" required><button id="paste" class="paste" type="button">Paste</button></div>
      <button id="analyze" class="primary" type="submit">Analyze</button>
    </form>
    <div class="under-form"><span>🔒 Links aren’t stored</span><a href="/qr-code-link-checker">Scan a QR code instead</a></div>
  </section>

  <section id="result" class="hidden" aria-live="polite">
    <div id="result-card" class="result-card">
      <div class="result-top"><div id="status-icon" class="status-icon">…</div><div class="result-main"><h2 id="verdict">Analyzing…</h2><p id="summary" class="result-summary">Checking the URL and destination.</p></div></div>
      <ul id="signals" class="signals hidden"></ul>
      <div id="advice" class="advice hidden"><strong>What should I do?</strong><p id="advice-text"></p></div>
      <div id="actions" class="actions hidden"><button id="deep" class="secondary" type="button">Check reputation</button><button id="share" class="secondary" type="button">Share result</button><button id="again" class="secondary" type="button">Check another</button></div>
      <div id="consent" class="consent hidden"><p>Reputation checks share this public URL with external threat databases. Private or signed links may contain access tokens.</p><div class="consent-actions"><button id="deep-confirm" class="small-primary" type="button">Continue</button><button id="deep-cancel" class="small-secondary" type="button">Cancel</button></div></div>
      <div id="reputation" class="reputation hidden"></div>
      <details id="technical" class="technical hidden"><summary>Technical details</summary><div id="tech-grid" class="tech-grid"></div><ul id="providers" class="providers"></ul></details>
    </div>
  </section>
</main>
<footer><div class="footer-line">Can I Share This? checks warning signs before you click. No scanner can guarantee a link is safe.</div><details><summary>Specialized checks</summary><nav><a href="/safe-link-checker">Safe link</a><a href="/scam-link-checker">Scam</a><a href="/phishing-link-checker">Phishing</a><a href="/qr-code-link-checker">QR code</a><a href="/google-drive-link-checker">Google Drive</a><a href="/dropbox-link-checker">Dropbox</a></nav></details></footer>
<script>
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),paste=document.getElementById('paste'),analyze=document.getElementById('analyze');
  var result=document.getElementById('result'),card=document.getElementById('result-card'),icon=document.getElementById('status-icon'),verdict=document.getElementById('verdict'),summary=document.getElementById('summary'),signals=document.getElementById('signals'),advice=document.getElementById('advice'),adviceText=document.getElementById('advice-text'),actions=document.getElementById('actions'),deep=document.getElementById('deep'),share=document.getElementById('share'),again=document.getElementById('again'),consent=document.getElementById('consent'),deepConfirm=document.getElementById('deep-confirm'),deepCancel=document.getElementById('deep-cancel'),reputation=document.getElementById('reputation'),technical=document.getElementById('technical'),techGrid=document.getElementById('tech-grid'),providers=document.getElementById('providers');
  var currentUrl='',lastStatus='unknown',lastVerdict='';
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function normalize(v){v=String(v||'').trim();if(v&&!/^https?:\/\//i.test(v))v='https://'+v;return v}
  function track(event){try{var b=new Blob([JSON.stringify({event:event})],{type:'application/json'});navigator.sendBeacon('/api/event',b)}catch(e){}}
  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze'}
  function clearExtra(){signals.classList.add('hidden');advice.classList.add('hidden');actions.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden');technical.classList.add('hidden');technical.open=false;signals.innerHTML='';techGrid.innerHTML='';providers.innerHTML=''}
  function loading(){clearExtra();result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}
  function guidance(status){if(status==='high')return 'Do not open this link. Delete the message and visit the company or service through its official website instead.';if(status==='caution')return 'Verify the sender and the final domain before continuing. Avoid signing in, paying, or downloading anything until you are sure.';if(status==='low')return 'If you expected this link, you can continue cautiously. Be extra careful if the message asks for a password, payment, or download.';return 'Do not trust the link yet. Verify the sender or use the official website directly.'}
  function renderQuick(data){
    var s=data&&data.safety?data.safety:{};var status=['low','caution','high'].indexOf(s.status)>=0?s.status:'unknown';lastStatus=status;
    card.className='result-card status-'+status;icon.textContent=status==='low'?'✓':status==='caution'?'!':status==='high'?'×':'?';
    lastVerdict=status==='low'?'NO KNOWN DANGER FOUND':status==='caution'?'BE CAREFUL':status==='high'?'DANGEROUS LINK SIGNALS':'CHECK INCOMPLETE';verdict.textContent=lastVerdict;
    summary.textContent=status==='low'?'No obvious scam or malicious URL pattern was detected.':status==='caution'?'Suspicious characteristics were detected.':status==='high'?'High-risk warning signs were detected. Do not open it.':(data.error||'We could not fully assess this destination.');
    var list=Array.isArray(s.signals)?s.signals.slice(0,3):[];if(status!=='low'&&list.length){signals.innerHTML=list.map(function(x){return '<li>'+esc(x.title||x.detail||'Warning sign detected')+'</li>'}).join('');signals.classList.remove('hidden')}
    adviceText.textContent=guidance(status);advice.classList.remove('hidden');actions.classList.remove('hidden');technical.classList.remove('hidden');
    var host=data.finalHost||'';var score=Number.isFinite(s.riskScore)?s.riskScore:0;techGrid.innerHTML='<div class="tech"><span>Final host</span><strong>'+esc(host||'Unknown')+'</strong></div><div class="tech"><span>Risk score</span><strong>'+esc(score)+'/100</strong></div><div class="tech"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class="tech"><span>Redirects</span><strong>'+esc(Array.isArray(data.redirects)?data.redirects.length:0)+'</strong></div>';
  }
  async function runScan(url){currentUrl=normalize(url);if(!currentUrl)return;input.value=currentUrl;loading();busy(true);track('analyze');try{var r=await fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl})});renderQuick(await r.json())}catch(e){renderQuick({error:'The safety check could not complete.',safety:{status:'unknown',riskScore:0,signals:[]}})}finally{busy(false)}}
  form.addEventListener('submit',function(e){e.preventDefault();runScan(input.value)});
  input.addEventListener('paste',function(){track('paste')});
  paste.addEventListener('click',async function(){try{var text=await navigator.clipboard.readText();if(text){input.value=text;track('paste');input.focus()}}catch(e){input.focus()}});
  again.addEventListener('click',function(){result.classList.add('hidden');input.value='';currentUrl='';input.focus()});
  deep.addEventListener('click',function(){consent.classList.remove('hidden')});deepCancel.addEventListener('click',function(){consent.classList.add('hidden')});
  deepConfirm.addEventListener('click',async function(){consent.classList.add('hidden');reputation.className='reputation';reputation.textContent='Checking reputation…';track('deep_scan');try{var r=await fetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl,consent:true})});var d=await r.json();providers.innerHTML=(d.providers||[]).map(function(p){return '<li><strong>'+esc(p.provider)+'</strong> — '+esc(p.detail||p.status||'')+'</li>'}).join('');if(d.status==='known-dangerous'){reputation.className='reputation bad';reputation.textContent='Known threat reported. Do not open this link.';lastStatus='high';lastVerdict='DANGEROUS LINK'}else if(d.status==='no-known-threat'){reputation.className='reputation good';reputation.textContent='No known threat was found by the available reputation sources.'}else if(d.status==='privacy-blocked'){reputation.className='reputation';reputation.textContent='Deep scan was blocked because this URL appears to contain sensitive access data.'}else{reputation.className='reputation';reputation.textContent='External reputation could not be confirmed right now.'}}catch(e){reputation.className='reputation';reputation.textContent='External reputation could not be checked right now.'}});
  share.addEventListener('click',async function(){var text='Can I Share This? result: '+lastVerdict+'. '+(lastStatus==='high'?'Do not open this link.':lastStatus==='caution'?'Use caution before opening this link.':'No obvious danger was found, but no scanner can guarantee safety.')+' Check suspicious links at https://canisharethis.com/';try{if(navigator.share)await navigator.share({title:'Can I Share This? link safety result',text:text});else{await navigator.clipboard.writeText(text);share.textContent='Copied';setTimeout(function(){share.textContent='Share result'},1500)}}catch(e){}});
  track('homepage_view');
  try{var pending=sessionStorage.getItem('cist_pending_url');if(pending){sessionStorage.removeItem('cist_pending_url');input.value=pending;runScan(pending)}}catch(e){}
})();
</script>
</body>
</html>'''


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / 'index.html').write_text(HTML, encoding='utf-8')
    print('Generated minimal V7.5 homepage')

if __name__ == '__main__':
    main()
