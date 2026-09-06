#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-desktop-daily-rail-style">
.cist-daily-rail{display:none}
@media(min-width:1320px){
  .cist-daily-rail{display:block;position:absolute;top:144px;left:calc(50% + 430px);width:clamp(210px,15vw,250px);z-index:2}
  .cist-daily-card{overflow:hidden;border:1px solid color-mix(in srgb,var(--line) 92%,transparent);border-radius:18px;background:linear-gradient(180deg,color-mix(in srgb,var(--card) 88%,transparent),color-mix(in srgb,var(--bg) 72%,var(--card)));box-shadow:0 16px 42px rgba(0,0,0,.14)}
  .cist-daily-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:14px 15px;border-bottom:1px solid var(--line)}
  .cist-daily-title{font-size:10px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
  .cist-daily-live{display:inline-flex;align-items:center;gap:6px;font-size:9px;font-weight:800;color:var(--muted)}
  .cist-daily-live:before{content:'';width:6px;height:6px;border-radius:999px;background:var(--green);box-shadow:0 0 0 4px color-mix(in srgb,var(--green) 10%,transparent)}
  .cist-daily-primary{padding:17px 15px 15px}
  .cist-daily-number{display:block;color:var(--text);font-size:38px;font-weight:920;letter-spacing:-.045em;line-height:1;font-variant-numeric:tabular-nums}
  .cist-daily-primary-label{display:block;margin-top:5px;color:var(--muted);font-size:11px;font-weight:750}
  .cist-daily-list{display:grid;border-top:1px solid var(--line)}
  .cist-daily-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 15px;border-bottom:1px solid color-mix(in srgb,var(--line) 78%,transparent)}
  .cist-daily-row:last-child{border-bottom:0}
  .cist-daily-row span{color:var(--muted);font-size:10px;line-height:1.3}
  .cist-daily-row strong{max-width:112px;color:var(--text);font-size:12px;font-weight:900;text-align:right;line-height:1.25;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
  .cist-daily-row.cist-daily-warning strong{color:var(--amber)}
  .cist-daily-foot{padding:11px 14px;border-top:1px solid var(--line);color:var(--muted);font-size:8.5px;line-height:1.45;text-align:center}
}
@media(min-width:1700px){.cist-daily-rail{left:calc(50% + 455px)}}
</style>
'''

BLOCK = r'''
<aside id="cist-daily-rail" class="cist-daily-rail" aria-label="Today's anonymous scanner statistics">
  <div class="cist-daily-card">
    <div class="cist-daily-head"><span class="cist-daily-title">Today</span><span id="cist-daily-live" class="cist-daily-live">Live</span></div>
    <div class="cist-daily-primary"><strong id="cist-daily-scans" class="cist-daily-number">—</strong><span class="cist-daily-primary-label">Scans today</span></div>
    <div class="cist-daily-list">
      <div class="cist-daily-row cist-daily-warning"><span>Warnings detected</span><strong id="cist-daily-warnings">—</strong></div>
      <div class="cist-daily-row"><span>Average scan time</span><strong id="cist-daily-average">—</strong></div>
      <div class="cist-daily-row"><span>Most checked type</span><strong id="cist-daily-type">—</strong></div>
    </div>
    <div class="cist-daily-foot">Anonymous aggregate statistics only · no scanned content stored here</div>
  </div>
</aside>
'''

SCRIPT = r'''
<script id="cist-desktop-daily-rail-script">
(function(){
  var rail=document.getElementById('cist-daily-rail'),form=document.getElementById('scan-form'),card=document.getElementById('result-card');
  var scans=document.getElementById('cist-daily-scans'),warnings=document.getElementById('cist-daily-warnings'),average=document.getElementById('cist-daily-average'),typeEl=document.getElementById('cist-daily-type'),live=document.getElementById('cist-daily-live');
  if(!rail||!form||!card||!scans)return;
  var startedAt=0,metricsSent=true,refreshTimer=0;
  var typeLabels={link:'URL',qr:'QR code',email:'Email',file:'File',shortlink:'Short link',crypto:'Crypto',message:'Message',social:'Social profile',other:'Other'};

  function status(){if(card.classList.contains('status-high'))return'high';if(card.classList.contains('status-caution'))return'caution';if(card.classList.contains('status-low'))return'low';return'unknown'}
  function formatTime(ms){ms=Number(ms);if(!Number.isFinite(ms)||ms<=0)return'—';if(ms<1000)return Math.round(ms)+' ms';return (ms/1000).toFixed(ms<10000?1:0)+' s'}
  function topType(by){var best='',count=-1;Object.keys(by||{}).forEach(function(k){var n=Number(by[k]||0);if(n>count){count=n;best=k}});return count>0?(typeLabels[best]||best):'—'}
  function render(data){
    var d=data&&data.daily||{};scans.textContent=Number(d.total||0).toLocaleString();warnings.textContent=Number(d.warnings||0).toLocaleString();average.textContent=formatTime(d.averageMs);typeEl.textContent=topType(d.byType||{});live.textContent=data&&data.persistent===false?'Session':'Live';
  }
  function request(options){var controller=new AbortController(),timer=setTimeout(function(){controller.abort()},1800),opts=options||{};opts.signal=controller.signal;return fetch('/api/counter',opts).then(function(r){clearTimeout(timer);if(!r.ok)throw new Error('stats');return r.json()}).catch(function(e){clearTimeout(timer);throw e})}
  function refresh(delay){clearTimeout(refreshTimer);refreshTimer=setTimeout(function(){request({cache:'no-store'}).then(render).catch(function(){live.textContent='Unavailable'})},delay||0)}
  function finishMetrics(){
    if(metricsSent||!startedAt||!document.body.classList.contains('cist-compact-result-active'))return;
    metricsSent=true;var duration=Math.max(1,Date.now()-startedAt),s=status();
    request({method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({metricsOnly:true,warning:s==='high'||s==='caution',durationMs:duration})}).then(function(data){render(data);refresh(250)}).catch(function(){refresh(300)});
  }
  form.addEventListener('submit',function(){startedAt=Date.now();metricsSent=false},true);
  document.addEventListener('cist:result-updated',function(){setTimeout(finishMetrics,40)});
  new MutationObserver(function(){finishMetrics()}).observe(document.body,{attributes:true,attributeFilter:['class']});
  refresh(0);
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=re.sub(r'\s*<style id="cist-desktop-daily-rail-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<aside id="cist-daily-rail".*?</aside>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-desktop-daily-rail-script">.*?</script>','',source,count=1,flags=re.S)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source=source.replace('</head>',STYLE+'\n</head>',1)
    source=source.replace('<main',BLOCK+'\n<main',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['Scans today','Warnings detected','Average scan time','Most checked type','metricsOnly:true','min-width:1320px','Anonymous aggregate statistics only']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Desktop daily rail guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied desktop-only anonymous daily statistics rail')

if __name__=='__main__':
    main()
