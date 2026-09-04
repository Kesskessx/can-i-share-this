#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'
QR = ROOT / 'dist' / 'qr-code-link-checker.html'

STYLE = r'''
<style id="cist-homepage-stats-style">
.cist-stats{max-width:760px;margin:28px auto 0;padding:0;border:1px solid var(--border,#2a2f38);border-radius:20px;background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.012));overflow:hidden;box-shadow:0 14px 40px rgba(0,0,0,.12)}
.cist-stats-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 18px;border-bottom:1px solid var(--border,#2a2f38)}
.cist-stats-title{margin:0;font-size:11px;font-weight:850;letter-spacing:.1em;text-transform:uppercase;color:var(--muted,#aab0bb)}
.cist-live-badge{display:inline-flex;align-items:center;gap:6px;font-size:10px;font-weight:750;color:var(--muted,#aab0bb)}
.cist-live-badge:before{content:"";width:7px;height:7px;border-radius:999px;background:#37c976;box-shadow:0 0 0 4px rgba(55,201,118,.1)}
.cist-stats-grid{display:grid;grid-template-columns:minmax(180px,.85fr) minmax(0,2fr)}
.cist-total-card{padding:24px 20px;border-right:1px solid var(--border,#2a2f38);display:flex;flex-direction:column;justify-content:center;min-height:180px}
.cist-stat-kicker{font-size:11px;font-weight:700;color:var(--muted,#aab0bb);margin-bottom:8px}
.cist-stat-value{display:block;font-size:clamp(38px,5vw,52px);line-height:.95;letter-spacing:-.045em;font-weight:900;color:var(--text,#f6f7f9);font-variant-numeric:tabular-nums}
.cist-stat-label{display:block;margin-top:9px;font-size:12px;line-height:1.35;color:var(--muted,#aab0bb)}
.cist-mix-card{padding:20px 20px 18px}.cist-mix-heading{display:flex;align-items:end;justify-content:space-between;gap:10px;margin-bottom:14px}.cist-mix-title{font-size:13px;font-weight:820;color:var(--text,#f6f7f9)}.cist-mix-sub{font-size:10px;color:var(--muted,#aab0bb)}
.cist-mix{display:grid;gap:10px}.cist-mix-row{display:grid;grid-template-columns:88px 1fr 44px;gap:10px;align-items:center;font-size:11px}.cist-mix-name{color:var(--muted,#aab0bb);white-space:nowrap}.cist-mix-track{height:9px;border-radius:999px;background:rgba(127,127,127,.13);overflow:hidden}.cist-mix-fill{height:100%;border-radius:inherit;background:linear-gradient(90deg,var(--accent,#7c8cff),#a8b2ff);width:0;min-width:2px;transition:width .35s ease}.cist-mix-value{text-align:right;color:var(--text,#f6f7f9);font-weight:750;font-variant-numeric:tabular-nums}
.cist-stats-note{margin:0;padding:10px 18px;border-top:1px solid var(--border,#2a2f38);text-align:center;font-size:9.5px;line-height:1.45;color:var(--muted,#8f96a3);background:rgba(255,255,255,.015)}
@media(max-width:650px){.cist-stats{margin-top:20px;border-radius:17px}.cist-stats-head{padding:12px 14px}.cist-stats-grid{grid-template-columns:1fr}.cist-total-card{min-height:0;padding:20px 16px;border-right:0;border-bottom:1px solid var(--border,#2a2f38);text-align:center}.cist-stat-value{font-size:42px}.cist-mix-card{padding:16px 14px}.cist-mix-heading{margin-bottom:12px}.cist-mix-row{grid-template-columns:76px 1fr 40px;gap:8px}.cist-stats-note{padding:9px 12px}}
</style>
'''

BLOCK = r'''
<section class="cist-stats" id="cist-stats" aria-label="Can I Share This usage statistics">
  <div class="cist-stats-head">
    <p class="cist-stats-title">Can I Share This? activity</p>
    <span class="cist-live-badge">Live usage</span>
  </div>
  <div class="cist-stats-grid">
    <div class="cist-total-card">
      <span class="cist-stat-kicker">Since tracking started</span>
      <strong class="cist-stat-value" id="cist-total-checks">—</strong>
      <span class="cist-stat-label">Total analyses performed</span>
    </div>
    <div class="cist-mix-card">
      <div class="cist-mix-heading"><span class="cist-mix-title">What people check</span><span class="cist-mix-sub">Share of analyses</span></div>
      <div class="cist-mix" id="cist-analysis-mix"></div>
    </div>
  </div>
  <p class="cist-stats-note" id="cist-stats-note">Anonymous aggregate counters only. No scanned content is shown here.</p>
</section>
'''

SCRIPT = r'''
<script id="cist-homepage-stats-script">
(function(){
  var total=document.getElementById('cist-total-checks'),mix=document.getElementById('cist-analysis-mix'),note=document.getElementById('cist-stats-note'),input=document.getElementById('url'),form=document.getElementById('scan-form');
  if(!total||!mix)return;
  var labels={link:'Links',qr:'QR',email:'Email',file:'Files',shortlink:'Short links',crypto:'Crypto',message:'Messages',other:'Other'};
  var order=['link','qr','email','file','shortlink','crypto','message','other'];
  var counted=false;
  function detectType(){
    try{if(sessionStorage.getItem('cist_input_source')==='qr'){sessionStorage.removeItem('cist_input_source');return 'qr'}}catch(e){}
    var v=String(input&&input.value||'').trim();if(/^mailto:/i.test(v)||/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v))return 'email';
    if(/^(0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{20,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[1-9A-HJ-NP-Za-km-z]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})$/.test(v))return 'crypto';
    try{var u=new URL(/^https?:\/\//i.test(v)?v:'https://'+v);var h=u.hostname.toLowerCase(),p=u.pathname.toLowerCase();if(/(^|\.)(bit\.ly|t\.co|tinyurl\.com|is\.gd|ow\.ly|buff\.ly|rebrand\.ly|cutt\.ly|rb\.gy)$/.test(h))return 'shortlink';if(/\.(exe|msi|apk|dmg|pkg|zip|rar|7z|pdf|docx?|xlsx?|pptx?|iso|img)$/i.test(p))return 'file'}catch(e){}
    return 'link';
  }
  function render(data){var t=Number(data&&data.total||0),by=data&&data.byType||{};total.textContent=t.toLocaleString();mix.innerHTML='';order.forEach(function(k){var n=Number(by[k]||0);if(!n&&t>0)return;var pct=t?Math.round(n*100/t):0;var row=document.createElement('div');row.className='cist-mix-row';row.innerHTML='<span class="cist-mix-name">'+labels[k]+'</span><span class="cist-mix-track"><span class="cist-mix-fill" style="width:'+pct+'%"></span></span><span class="cist-mix-value">'+pct+'%</span>';mix.appendChild(row)});if(!mix.children.length)mix.textContent='No analyses yet';if(data&&data.persistent===false)note.textContent='Live counters are active, but persistent storage is not configured yet.'}
  function request(url,options){var controller=new AbortController(),timer=setTimeout(function(){controller.abort()},1500),opts=options||{};opts.signal=controller.signal;return fetch(url,opts).then(function(r){clearTimeout(timer);if(!r.ok)throw new Error('counter');return r.json()}).catch(function(e){clearTimeout(timer);throw e})}
  function refresh(){request('/api/counter',{cache:'no-store'}).then(render).catch(function(){total.textContent='—';note.textContent='Usage statistics are temporarily unavailable.'})}
  function countOnce(){if(counted)return;counted=true;request('/api/counter',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({type:detectType()})}).then(render).catch(function(){})}
  if(form)form.addEventListener('submit',function(){counted=false},true);
  document.addEventListener('cist:result-updated',countOnce);
  refresh();
})();
</script>
'''

def main():
    if not HOME.is_file(): raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    import re
    source=re.sub(r'\s*<style id="cist-homepage-stats-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<section class="cist-stats" id="cist-stats".*?</section>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-homepage-stats-script">.*?</script>','',source,count=1,flags=re.S)
    source=source.replace('</head>',STYLE+'\n</head>',1)
    anchor='<footer'
    source=source.replace(anchor,BLOCK+'\n'+anchor,1) if anchor in source else source.replace('</body>',BLOCK+'\n</body>',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)
    for token in ['Total analyses performed','What people check','/api/counter','cist_input_source','cist:result-updated']:
        if token not in source: raise RuntimeError(f'Homepage stats guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    if QR.is_file():
        qr=QR.read_text(encoding='utf-8')
        old="sessionStorage.setItem('cist_pending_url',value)"
        new="sessionStorage.setItem('cist_pending_url',value);sessionStorage.setItem('cist_input_source','qr')"
        if old in qr and 'cist_input_source' not in qr: qr=qr.replace(old,new,1)
        QR.write_text(qr,encoding='utf-8')
    print('Applied polished non-blocking live usage counters')

if __name__=='__main__': main()
