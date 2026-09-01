#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

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
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}button,input{font:inherit}a{color:inherit}
    header{height:66px;display:flex;align-items:center;border-bottom:1px solid var(--line)}.top{width:min(940px,calc(100% - 36px));margin:auto;display:flex;align-items:center;justify-content:space-between}.brand{font-weight:850;text-decoration:none;letter-spacing:-.025em}.mini-link{font-size:13px;color:var(--muted);text-decoration:none}
    main{width:min(760px,calc(100% - 32px));margin:0 auto;padding:clamp(54px,9vw,105px) 0 70px}.hero{text-align:center}.eyebrow{font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}.hero h1{font-size:clamp(38px,8vw,68px);line-height:.98;letter-spacing:-.055em;margin:0;text-wrap:balance}.sub{max-width:590px;margin:18px auto 28px;color:var(--muted);font-size:clamp(16px,2.4vw,19px);line-height:1.55}
    .scan-form{display:flex;gap:10px;padding:9px;background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}.scan-form:focus-within{outline:3px solid color-mix(in srgb,var(--text) 12%,transparent)}.scan-form input{min-width:0;flex:1;height:52px;border:0;outline:0;background:transparent;color:var(--text);padding:0 13px;font-size:16px}.scan-form input::placeholder{color:var(--muted)}.primary{height:52px;border:0;border-radius:12px;background:var(--button);color:var(--buttonText);padding:0 22px;font-weight:800;cursor:pointer}.primary:disabled{opacity:.55;cursor:wait}.privacy{margin:12px 0 0;color:var(--muted);font-size:12px}
    #result{margin-top:24px;text-align:left}.hidden{display:none!important}.result-card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:clamp(20px,4vw,30px);box-shadow:var(--shadow)}.result-top{display:flex;gap:14px;align-items:flex-start}.status-icon{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:var(--soft);font-size:21px;font-weight:900;flex:0 0 auto}.result-main{min-width:0;flex:1}.result-main h2{margin:0;font-size:clamp(23px,4vw,31px);line-height:1.12;letter-spacing:-.035em}.result-summary{margin:7px 0 0;color:var(--muted)}.status-low .status-icon,.status-low h2{color:var(--green)}.status-caution .status-icon,.status-caution h2{color:var(--amber)}.status-high .status-icon,.status-high h2{color:var(--red)}
    .meta{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.pill{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:6px 10px;font-size:12px;color:var(--muted)}.signals{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:9px}.signals li{position:relative;padding:12px 14px 12px 38px;background:var(--soft);border-radius:12px;font-size:14px}.signals li:before{content:"•";position:absolute;left:16px;font-weight:900}.caveat{font-size:12px;color:var(--muted);margin:14px 0 0}
    .actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:18px}.secondary{border:1px solid var(--line);background:transparent;color:var(--text);border-radius:11px;padding:10px 13px;font-weight:750;cursor:pointer}.deep-note{margin:12px 0 0;font-size:12px;color:var(--muted)}.consent{margin-top:12px;padding:14px;border:1px solid var(--line);background:var(--soft);border-radius:12px}.consent p{margin:0 0 10px;font-size:13px}.consent-actions{display:flex;gap:8px}.small-primary{border:0;background:var(--button);color:var(--buttonText);border-radius:9px;padding:8px 12px;font-weight:800;cursor:pointer}.small-secondary{border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:9px;padding:8px 12px;font-weight:750;cursor:pointer}
    .reputation{margin-top:14px;border-radius:12px;padding:13px 14px;background:var(--soft);font-size:14px}.reputation strong{display:block;margin-bottom:3px}.reputation.bad strong{color:var(--red)}.reputation.good strong{color:var(--green)}
    details.technical{margin-top:16px;border-top:1px solid var(--line);padding-top:14px}details.technical summary{cursor:pointer;font-size:13px;font-weight:750;color:var(--muted)}.technical-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:12px}.tech{padding:10px 12px;background:var(--soft);border-radius:10px}.tech span{display:block;font-size:11px;color:var(--muted);margin-bottom:2px}.tech strong{font-size:13px;word-break:break-word}.provider-list{list-style:none;padding:0;margin:12px 0 0;display:grid;gap:8px}.provider-list li{padding:10px 12px;background:var(--soft);border-radius:10px;font-size:12px}
    footer{width:min(760px,calc(100% - 32px));margin:0 auto 35px;color:var(--muted);font-size:12px;text-align:center}.footer-main{padding-top:24px;border-top:1px solid var(--line)}footer details{margin:10px auto;max-width:520px}footer summary{cursor:pointer}footer nav{display:flex;justify-content:center;gap:8px 14px;flex-wrap:wrap;margin-top:10px}footer nav a{text-underline-offset:3px}
    @media(max-width:600px){header{height:58px}.top{width:calc(100% - 28px)}.mini-link{display:none}main{width:calc(100% - 24px);padding-top:46px}.hero h1{font-size:44px}.sub{margin-top:14px;margin-bottom:22px}.scan-form{display:block;padding:8px}.scan-form input{width:100%;height:50px}.primary{width:100%;height:48px}.result-card{border-radius:16px}.result-top{gap:11px}.status-icon{width:38px;height:38px}.technical-grid{grid-template-columns:1fr}.actions>*{flex:1}.consent-actions>*{flex:1}}
  </style>
</head>
<body>
<header><div class="top"><a class="brand" href="/">↗ Can I Share This?</a><a class="mini-link" href="/safe-link-checker">How it works</a></div></header>
<main id="top">
  <section class="hero" aria-labelledby="page-title">
    <p class="eyebrow">Link safety checker</p>
    <h1 id="page-title">Is this link safe?</h1>
    <p class="sub">Paste a suspicious link. We’ll check for common scam, phishing, redirect and risky-download warning signs before you open it.</p>
    <form id="scan-form" class="scan-form">
      <input id="url" type="text" inputmode="url" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Paste a link here…" aria-label="Link to analyze" required>
      <button id="analyze" class="primary" type="submit">Analyze</button>
    </form>
    <p class="privacy">No account required. The first scan does not send your URL to third-party reputation databases.</p>
  </section>

  <section id="result" class="hidden" aria-live="polite">
    <div id="result-card" class="result-card">
      <div class="result-top">
        <div id="status-icon" class="status-icon">…</div>
        <div class="result-main">
          <h2 id="verdict">Analyzing…</h2>
          <p id="summary" class="result-summary">Checking the URL and destination.</p>
        </div>
      </div>
      <div id="meta" class="meta hidden"></div>
      <ul id="signals" class="signals hidden"></ul>
      <p id="caveat" class="caveat hidden">This is a risk assessment, not a guarantee that a website is malware-free.</p>
      <div id="actions" class="actions hidden">
        <button id="deep" class="secondary" type="button">Check reputation too</button>
        <button id="again" class="secondary" type="button">Check another link</button>
      </div>
      <p id="deep-note" class="deep-note hidden">Optional: the reputation check can share this public URL with external threat databases.</p>
      <div id="consent" class="consent hidden">
        <p>Continue only for a public link. Private or signed URLs may contain sensitive access tokens.</p>
        <div class="consent-actions"><button id="deep-confirm" class="small-primary" type="button">Continue</button><button id="deep-cancel" class="small-secondary" type="button">Cancel</button></div>
      </div>
      <div id="reputation" class="reputation hidden"></div>
      <details id="technical" class="technical hidden">
        <summary>Technical details</summary>
        <div id="technical-grid" class="technical-grid"></div>
        <ul id="provider-list" class="provider-list"></ul>
      </details>
    </div>
  </section>
</main>
<footer>
  <div class="footer-main">Can I Share This? checks warning signs before you click. It cannot guarantee that a link is safe.</div>
  <details><summary>Specialized link checks</summary><nav><a href="/safe-link-checker">Safe link</a><a href="/scam-link-checker">Scam link</a><a href="/phishing-link-checker">Phishing</a><a href="/google-drive-link-checker">Google Drive</a><a href="/dropbox-link-checker">Dropbox</a><a href="/drive-vs-dropbox-share-link-checker">Drive vs Dropbox</a></nav></details>
</footer>
<script id="minimal-homepage-script">
(function(){
  var form=document.getElementById('scan-form'), input=document.getElementById('url'), analyze=document.getElementById('analyze');
  var result=document.getElementById('result'), card=document.getElementById('result-card'), icon=document.getElementById('status-icon'), verdict=document.getElementById('verdict'), summary=document.getElementById('summary');
  var meta=document.getElementById('meta'), signals=document.getElementById('signals'), caveat=document.getElementById('caveat'), actions=document.getElementById('actions'), deep=document.getElementById('deep'), again=document.getElementById('again'), deepNote=document.getElementById('deep-note'), consent=document.getElementById('consent'), deepConfirm=document.getElementById('deep-confirm'), deepCancel=document.getElementById('deep-cancel'), reputation=document.getElementById('reputation'), technical=document.getElementById('technical'), technicalGrid=document.getElementById('technical-grid'), providerList=document.getElementById('provider-list');
  var currentUrl='';
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function normalize(v){v=String(v||'').trim();if(v&&!/^https?:\/\//i.test(v))v='https://'+v;return v}
  function busy(on){analyze.disabled=on;analyze.textContent=on?'Analyzing…':'Analyze'}
  function resetExtras(){meta.classList.add('hidden');signals.classList.add('hidden');caveat.classList.add('hidden');actions.classList.add('hidden');deepNote.classList.add('hidden');consent.classList.add('hidden');reputation.classList.add('hidden');reputation.className='reputation hidden';technical.classList.add('hidden');technical.open=false;technicalGrid.innerHTML='';providerList.innerHTML=''}
  function loading(){resetExtras();result.classList.remove('hidden');card.className='result-card';icon.textContent='…';verdict.textContent='Analyzing…';summary.textContent='Checking the URL and destination.'}
  function renderQuick(data){
    var s=data&&data.safety?data.safety:{};var status=['low','caution','high'].indexOf(s.status)>=0?s.status:'unknown';
    card.className='result-card status-'+status;
    icon.textContent=status==='low'?'✓':status==='caution'?'!':status==='high'?'×':'?';
    verdict.textContent=status==='low'?'No obvious danger found':status==='caution'?'Be careful with this link':status==='high'?'High-risk signals found':'We could not fully check this link';
    summary.textContent=status==='low'?'No obvious scam or malicious URL pattern was detected.':status==='caution'?'Some characteristics deserve a closer look before you continue.':status==='high'?'Do not open, sign in, pay, or download anything until you verify the link.':(data.error||'The destination could not be assessed completely.');
    var score=Number.isFinite(s.riskScore)?s.riskScore:0;var host=data.finalHost||'';meta.innerHTML=(host?'<span class="pill">'+esc(host)+'</span>':'')+'<span class="pill">Risk '+esc(score)+'/100</span>';meta.classList.remove('hidden');
    var list=Array.isArray(s.signals)?s.signals.slice(0,3):[];
    if(!list.length) list=[{title:'No obvious suspicious URL pattern detected.'}];
    signals.innerHTML=list.map(function(x){return '<li>'+esc(x.title||x.detail||'Warning sign detected')+'</li>'}).join('');signals.classList.remove('hidden');caveat.classList.remove('hidden');actions.classList.remove('hidden');deepNote.classList.remove('hidden');
    technicalGrid.innerHTML='<div class="tech"><span>Final domain</span><strong>'+esc(host||'Unknown')+'</strong></div><div class="tech"><span>HTTP status</span><strong>'+esc(data.status||'Unknown')+'</strong></div><div class="tech"><span>Redirects</span><strong>'+esc(Array.isArray(data.redirects)?data.redirects.length:0)+'</strong></div><div class="tech"><span>Login gate</span><strong>'+esc(data.loginRequired?'Detected':'Not detected')+'</strong></div>';
    technical.classList.remove('hidden');
  }
  async function quickScan(url){loading();busy(true);try{var r=await fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:url})});var data=await r.json();renderQuick(data)}catch(e){card.className='result-card status-unknown';icon.textContent='?';verdict.textContent='Check failed';summary.textContent='Please try again in a moment.';actions.classList.remove('hidden')}finally{busy(false)}}
  function renderDeep(data){consent.classList.add('hidden');reputation.classList.remove('hidden');var status=data&&data.status||'unknown';if(data&&data.privacyBlocked){reputation.className='reputation';reputation.innerHTML='<strong>Protected: deep check skipped</strong>This link appears to contain a private token or signature, so it was not sent to external databases.'}else if(status==='known-dangerous'){reputation.className='reputation bad';reputation.innerHTML='<strong>Known threat reported</strong>At least one external reputation source flags this URL. Do not continue.'}else if(status==='no-known-threat'){reputation.className='reputation good';reputation.innerHTML='<strong>No known threat found</strong>The available reputation sources did not report this URL. This is not a guarantee of safety.'}else{reputation.className='reputation';reputation.innerHTML='<strong>Reputation check unavailable</strong>The external databases could not provide a reliable answer right now.'}
    var providers=Array.isArray(data&&data.providers)?data.providers:[];providerList.innerHTML=providers.map(function(p){return '<li><strong>'+esc(p.provider||'Provider')+'</strong><br>'+esc(p.detail||p.status||'No detail')+'</li>'}).join('');technical.open=false
  }
  form.addEventListener('submit',function(e){e.preventDefault();var url=normalize(input.value);if(!url)return;currentUrl=url;input.value=url;quickScan(url)});
  deep.addEventListener('click',function(){consent.classList.remove('hidden');deepNote.classList.add('hidden')});
  deepCancel.addEventListener('click',function(){consent.classList.add('hidden');deepNote.classList.remove('hidden')});
  deepConfirm.addEventListener('click',async function(){if(!currentUrl)return;deepConfirm.disabled=true;deepConfirm.textContent='Checking…';try{var r=await fetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:currentUrl,consent:true})});renderDeep(await r.json())}catch(e){renderDeep({status:'unknown',providers:[]})}finally{deepConfirm.disabled=false;deepConfirm.textContent='Continue'}});
  again.addEventListener('click',function(){result.classList.add('hidden');resetExtras();input.value='';currentUrl='';input.focus()});
})();
</script>
</body>
</html>
'''

(DIST / "index.html").write_text(HTML, encoding="utf-8")
print("Generated minimal 3-second homepage")
