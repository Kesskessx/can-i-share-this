#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'
QR = ROOT / 'dist' / 'qr-code-link-checker.html'

STYLE = r'''
<style id="cist-homepage-stats-style">
.cist-stats{max-width:760px;margin:22px auto 0;padding:18px 16px;border:1px solid var(--border,#2a2f38);border-radius:16px;background:var(--panel,#15181e)}
.cist-stats-title{margin:0 0 12px;text-align:center;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted,#aab0bb)}
.cist-stats-grid{display:grid;grid-template-columns:1fr 2fr;gap:12px}.cist-stat{padding:14px 12px;border-radius:12px;background:rgba(255,255,255,.025)}
.cist-stat-value{display:block;font-size:30px;line-height:1;font-weight:850;color:var(--text,#f6f7f9)}.cist-stat-label{display:block;margin-top:7px;font-size:11px;color:var(--muted,#aab0bb)}
.cist-mix{display:grid;gap:7px}.cist-mix-row{display:grid;grid-template-columns:82px 1fr 46px;gap:8px;align-items:center;font-size:11px}.cist-mix-name{color:var(--muted,#aab0bb)}.cist-mix-track{height:7px;border-radius:999px;background:rgba(255,255,255,.06);overflow:hidden}.cist-mix-fill{height:100%;border-radius:inherit;background:var(--accent,#7c8cff);width:0}.cist-mix-value{text-align:right;color:var(--text,#f6f7f9);font-variant-numeric:tabular-nums}.cist-stats-note{margin:11px 0 0;text-align:center;font-size:10px;line-height:1.45;color:var(--muted,#8f96a3)}
@media(max-width:650px){.cist-stats-grid{grid-template-columns:1fr}.cist-stat-value{font-size:26px}.cist-mix-row{grid-template-columns:72px 1fr 42px}}
</style>
'''

BLOCK = r'''
<section class="cist-stats" id="cist-stats" aria-label="Can I Share This usage statistics">
  <p class="cist-stats-title">Live usage</p>
  <div class="cist-stats-grid">
    <div class="cist-stat"><strong class="cist-stat-value" id="cist-total-checks">—</strong><span class="cist-stat-label">Total analyses</span></div>
    <div class="cist-stat"><div class="cist-mix" id="cist-analysis-mix"></div><span class="cist-stat-label">Analysis mix</span></div>
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
    for token in ['Total analyses','Analysis mix','/api/counter','cist_input_source','cist:result-updated']:
        if token not in source: raise RuntimeError(f'Homepage stats guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    if QR.is_file():
        qr=QR.read_text(encoding='utf-8')
        old="sessionStorage.setItem('cist_pending_url',value)"
        new="sessionStorage.setItem('cist_pending_url',value);sessionStorage.setItem('cist_input_source','qr')"
        if old in qr and 'cist_input_source' not in qr: qr=qr.replace(old,new,1)
        QR.write_text(qr,encoding='utf-8')
    print('Applied non-blocking live total analysis counter and analysis mix')

if __name__=='__main__': main()
