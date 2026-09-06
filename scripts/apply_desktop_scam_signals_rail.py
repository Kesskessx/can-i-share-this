#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-desktop-scam-signals-style">
.cist-scam-signals-rail{display:none}
@media(min-width:1100px){
  #cist-scam-signals-rail{
    display:block!important;
    position:absolute!important;
    left:16px!important;
    right:auto!important;
    top:144px!important;
    width:clamp(150px,calc((100vw - 800px)/2 - 12px),240px)!important;
    z-index:3!important;
    box-sizing:border-box!important;
    font-family:inherit!important;
    visibility:visible!important;
    opacity:1!important;
    color:var(--text,#f3f6ff)!important;
    isolation:isolate!important;
  }
  #cist-scam-signals-rail,
  #cist-scam-signals-rail *{
    visibility:visible!important;
    opacity:1!important;
    text-indent:0!important;
    filter:none!important;
    clip:auto!important;
    clip-path:none!important;
  }
  #cist-scam-signals-rail .cist-signal-card{
    display:block!important;
    overflow:hidden!important;
    width:100%!important;
    box-sizing:border-box!important;
    border:1px solid color-mix(in srgb,var(--line,#2a3140) 92%,transparent)!important;
    border-radius:18px!important;
    background:linear-gradient(180deg,color-mix(in srgb,var(--card,#151b26) 88%,transparent),color-mix(in srgb,var(--bg,#0b0f17) 72%,var(--card,#151b26)))!important;
    box-shadow:0 16px 42px rgba(0,0,0,.14)!important;
  }
  #cist-scam-signals-rail .cist-signal-head{
    display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;
    padding:13px 14px!important;border-bottom:1px solid var(--line,#2a3140)!important;
  }
  #cist-scam-signals-rail .cist-signal-title{
    display:inline!important;color:var(--muted,#9ba6ba)!important;font-size:10px!important;font-weight:900!important;line-height:1.2!important;letter-spacing:.09em!important;text-transform:uppercase!important;
  }
  #cist-scam-signals-rail .cist-signal-live{
    display:inline-flex!important;align-items:center!important;gap:6px!important;color:var(--muted,#9ba6ba)!important;font-size:9px!important;font-weight:800!important;line-height:1.2!important;white-space:nowrap!important;
  }
  #cist-scam-signals-rail .cist-signal-live:before{
    content:''!important;width:6px!important;height:6px!important;flex:0 0 auto!important;border-radius:999px!important;
    background:var(--amber,#f0b85b)!important;box-shadow:0 0 0 4px color-mix(in srgb,var(--amber,#f0b85b) 10%,transparent)!important;
  }
  #cist-scam-signals-rail .cist-signal-primary{display:block!important;padding:17px 14px 15px!important}
  #cist-scam-signals-rail .cist-signal-number{
    display:block!important;color:var(--text,#f3f6ff)!important;font-size:clamp(30px,3vw,38px)!important;font-weight:920!important;
    letter-spacing:-.045em!important;line-height:1!important;font-variant-numeric:tabular-nums!important;
  }
  #cist-scam-signals-rail .cist-signal-primary-label{
    display:block!important;margin-top:5px!important;color:var(--muted,#9ba6ba)!important;font-size:10px!important;font-weight:750!important;line-height:1.35!important;
  }
  #cist-scam-signals-rail .cist-signal-list{display:grid!important;border-top:1px solid var(--line,#2a3140)!important}
  #cist-scam-signals-rail .cist-signal-row{
    display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;min-width:0!important;
    padding:11px 14px!important;border-bottom:1px solid color-mix(in srgb,var(--line,#2a3140) 78%,transparent)!important;
  }
  #cist-scam-signals-rail .cist-signal-row:last-child{border-bottom:0!important}
  #cist-scam-signals-rail .cist-signal-row span{display:inline!important;min-width:0!important;color:var(--muted,#9ba6ba)!important;font-size:9px!important;line-height:1.3!important}
  #cist-scam-signals-rail .cist-signal-row strong{
    display:inline!important;color:var(--text,#f3f6ff)!important;font-size:11px!important;font-weight:900!important;line-height:1.25!important;text-align:right!important;font-variant-numeric:tabular-nums!important;
  }
  #cist-scam-signals-rail .cist-signal-row.cist-signal-hot strong{color:var(--amber,#f0b85b)!important}
  #cist-scam-signals-rail .cist-signal-foot{
    display:block!important;padding:10px 12px!important;border-top:1px solid var(--line,#2a3140)!important;color:var(--muted,#9ba6ba)!important;font-size:8px!important;line-height:1.4!important;text-align:center!important;
  }
}
@media(min-width:1100px) and (max-width:1249px){
  #cist-scam-signals-rail{left:10px!important}
  #cist-scam-signals-rail .cist-signal-head{padding:11px 10px!important}
  #cist-scam-signals-rail .cist-signal-primary{padding:14px 10px 12px!important}
  #cist-scam-signals-rail .cist-signal-row{display:block!important;padding:9px 10px!important}
  #cist-scam-signals-rail .cist-signal-row strong{display:block!important;margin-top:3px!important;text-align:left!important}
  #cist-scam-signals-rail .cist-signal-foot{padding:9px!important;font-size:7.5px!important}
}
@media(min-width:1450px){#cist-scam-signals-rail{left:24px!important}}
@media(max-width:1099px){#cist-scam-signals-rail{display:none!important}}
</style>
'''

BLOCK = r'''
<aside id="cist-scam-signals-rail" class="cist-scam-signals-rail" aria-label="Anonymous scam signals detected today">
  <div class="cist-signal-card">
    <div class="cist-signal-head"><span class="cist-signal-title">Scam signals</span><span id="cist-signal-live" class="cist-signal-live">Today</span></div>
    <div class="cist-signal-primary"><strong id="cist-signal-total" class="cist-signal-number">0</strong><span class="cist-signal-primary-label">Signals detected today</span></div>
    <div class="cist-signal-list">
      <div class="cist-signal-row"><span>Suspicious redirects</span><strong id="cist-signal-redirect">0</strong></div>
      <div class="cist-signal-row cist-signal-hot"><span>Phishing indicators</span><strong id="cist-signal-phishing">0</strong></div>
      <div class="cist-signal-row"><span>Lookalike domains</span><strong id="cist-signal-lookalike">0</strong></div>
      <div class="cist-signal-row"><span>Risky downloads</span><strong id="cist-signal-download">0</strong></div>
    </div>
    <div class="cist-signal-foot">Anonymous aggregate counts · no scanned content shown</div>
  </div>
</aside>
'''

SCRIPT = r'''
<script id="cist-desktop-scam-signals-script">
(function(){
  var rail=document.getElementById('cist-scam-signals-rail'),form=document.getElementById('scan-form');
  var total=document.getElementById('cist-signal-total'),redirect=document.getElementById('cist-signal-redirect'),phishing=document.getElementById('cist-signal-phishing'),lookalike=document.getElementById('cist-signal-lookalike'),download=document.getElementById('cist-signal-download'),live=document.getElementById('cist-signal-live');
  if(!rail||!form||!total)return;
  var signalSent=true,pollTimer=0,refreshTimer=0,requestRunning=false;

  function ensureCopy(){
    var defaults={
      'cist-signal-live':'Today','cist-signal-total':'0','cist-signal-redirect':'0','cist-signal-phishing':'0','cist-signal-lookalike':'0','cist-signal-download':'0'
    };
    Object.keys(defaults).forEach(function(id){var el=document.getElementById(id);if(el&&!String(el.textContent||'').trim())el.textContent=defaults[id]});
    var title=rail.querySelector('.cist-signal-title'),label=rail.querySelector('.cist-signal-primary-label'),foot=rail.querySelector('.cist-signal-foot');
    if(title&&!String(title.textContent||'').trim())title.textContent='Scam signals';
    if(label&&!String(label.textContent||'').trim())label.textContent='Signals detected today';
    if(foot&&!String(foot.textContent||'').trim())foot.textContent='Anonymous aggregate counts · no scanned content shown';
  }
  function clean(v){return String(v||'').replace(/\s+/g,' ').trim().toLowerCase()}
  function signalFlags(){
    var d=window.cistUniversalResultData||{},s=d.safety||{},sig=Array.isArray(s.signals)?s.signals:[];
    var codes=sig.map(function(x){return clean(x&&x.code)}).filter(Boolean);
    var has=function(code){return codes.indexOf(code)>=0};
    var starts=function(prefix){return codes.some(function(code){return code.indexOf(prefix)===0})};
    var pageSignals=clean((document.getElementById('signals')||{}).textContent)+' '+clean((document.getElementById('cist-why')||{}).textContent);
    var tech='';document.querySelectorAll('#tech-grid .tech').forEach(function(el){tech+=' '+clean(el.textContent)});
    var redirects=Array.isArray(d.redirects)?d.redirects.length:0;
    if(!redirects){var m=tech.match(/redirects?\s*(\d+)/);if(m)redirects=Number(m[1]||0)}
    return {
      redirected:redirects>0||has('domain-change'),
      phishing:has('phishing-language')||starts('brand-')||pageSignals.indexOf('phishing')>=0,
      lookalike:starts('brand-')||has('punycode')||pageSignals.indexOf('lookalike')>=0||pageSignals.indexOf('look-alike')>=0,
      riskyDownload:has('executable-download')||has('binary-content')||has('forced-download')||has('archive-download')||pageSignals.indexOf('risky download')>=0
    }
  }
  function render(data){
    ensureCopy();
    var d=data&&data.daily||{},s=d.signals||{};
    total.textContent=Number(d.signalTotal||0).toLocaleString();
    redirect.textContent=Number(s.redirect||0).toLocaleString();
    phishing.textContent=Number(s.phishing||0).toLocaleString();
    lookalike.textContent=Number(s.lookalike||0).toLocaleString();
    download.textContent=Number(s.risky_download||0).toLocaleString();
    live.textContent=data&&data.persistent===false?'Session':'Today';
  }
  function request(options){
    var controller=new AbortController(),timer=setTimeout(function(){controller.abort()},1800),opts=options||{};opts.signal=controller.signal;
    return fetch('/api/counter',opts).then(function(r){clearTimeout(timer);if(!r.ok)throw new Error('signals');return r.json()}).catch(function(e){clearTimeout(timer);throw e});
  }
  function refresh(delay){
    clearTimeout(refreshTimer);refreshTimer=setTimeout(function(){
      if(document.hidden||requestRunning)return;requestRunning=true;
      request({cache:'no-store'}).then(render).catch(function(){ensureCopy();live.textContent='Reconnecting…'}).finally(function(){requestRunning=false});
    },delay||0)
  }
  function finishSignals(){
    if(signalSent||!document.body.classList.contains('cist-compact-result-active'))return;
    signalSent=true;var f=signalFlags();
    request({method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({metricsOnly:true,redirected:f.redirected,phishing:f.phishing,lookalike:f.lookalike,riskyDownload:f.riskyDownload})}).then(function(data){render(data);refresh(250)}).catch(function(){refresh(300)});
  }
  form.addEventListener('submit',function(){signalSent=false},true);
  document.addEventListener('cist:result-updated',function(){setTimeout(finishSignals,70)});
  new MutationObserver(function(){finishSignals()}).observe(document.body,{attributes:true,attributeFilter:['class']});
  document.addEventListener('visibilitychange',function(){if(!document.hidden)refresh(0)});
  window.addEventListener('focus',function(){refresh(0)});
  window.addEventListener('online',function(){refresh(0)});
  ensureCopy();
  pollTimer=setInterval(function(){if(!document.hidden)refresh(0)},15000);
  refresh(0);
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=re.sub(r'\s*<style id="cist-desktop-scam-signals-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<aside id="cist-scam-signals-rail".*?</aside>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-desktop-scam-signals-script">.*?</script>','',source,count=1,flags=re.S)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source=source.replace('</head>',STYLE+'\n</head>',1)
    source=source.replace('<main',BLOCK+'\n<main',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['Scam signals','Signals detected today','Suspicious redirects','Phishing indicators','Lookalike domains','Risky downloads','ensureCopy','visibility:visible!important','opacity:1!important','metricsOnly:true','min-width:1100px','15000']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Scam signals rail guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied visible desktop-only live scam signals rail')

if __name__=='__main__':
    main()
