#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'dist'/'index.html'
if not HOME.is_file(): raise RuntimeError('Homepage not found')
s=HOME.read_text(encoding='utf-8')

STYLE=r'''
<style id="cist-universal-evidence-ui-v1-style">
#cist-evidence-coverage{display:none}
#cist-evidence-coverage.cist-show{display:block}
.cist-coverage-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px}
.cist-coverage-score{font-size:11px;font-weight:900;color:var(--text)}
.cist-coverage-bar{height:6px;border-radius:999px;background:var(--line);overflow:hidden;margin:7px 0 10px}.cist-coverage-bar>span{display:block;height:100%;border-radius:inherit;background:var(--cist-accent,#788ff7);width:0}
.cist-coverage-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.cist-coverage-item{padding:7px 8px;border:1px solid var(--line);border-radius:10px;font-size:10px;color:var(--muted)}.cist-coverage-item.done{color:var(--text)}
.cist-evidence-source-row{margin-top:9px;color:var(--muted);font-size:9.5px;line-height:1.45}.cist-evidence-source-row strong{color:var(--text)}
#cist-reputation-box{display:none}#cist-reputation-box.cist-show{display:block}.cist-reputation-row{display:flex;align-items:center;justify-content:space-between;gap:10px}.cist-reputation-state{font-size:10.5px;color:var(--muted);line-height:1.45}.cist-reputation-btn{appearance:none;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);padding:8px 10px;font:inherit;font-size:10px;font-weight:850;cursor:pointer;white-space:nowrap}.cist-reputation-btn:disabled{opacity:.55;cursor:default}
.cist-evidence-group{margin-top:9px}.cist-evidence-group h4{margin:0 0 6px;font-size:9px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}.cist-evidence-group ul{margin:0;padding-left:17px}.cist-evidence-group li{margin:4px 0;font-size:10.5px;line-height:1.4}
@media(max-width:600px){.cist-coverage-grid{grid-template-columns:1fr}.cist-reputation-row{align-items:flex-start;flex-direction:column}.cist-reputation-btn{width:100%}}
</style>
'''

SCRIPT=r'''
<script id="cist-universal-evidence-ui-v1-script">
(function(){
  var file=document.getElementById('image-file'),choose=document.getElementById('choose-image'),panel=document.getElementById('cist-mega-v2-panel');
  if(!file||!choose)return;
  file.setAttribute('accept','image/jpeg,image/png,image/webp,.pdf,.txt,.csv,.eml,.doc,.docx,.docm,.xls,.xlsx,.xlsm,.ppt,.pptx,.pptm,.zip,.rar,.7z,.exe,.msi,.apk,application/pdf,text/plain,message/rfc822,application/zip');
  choose.textContent='＋ Screenshot / File';
  choose.setAttribute('aria-label','Add a screenshot or file to analyze');

  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function fileData(f){return new Promise(function(resolve,reject){var r=new FileReader();r.onload=function(){var raw=String(r.result||''),i=raw.indexOf(',');resolve(i>=0?raw.slice(i+1):raw)};r.onerror=reject;r.readAsDataURL(f)})}
  async function analyzeNonImage(f){
    if(!f)return;var note=document.getElementById('cist-unified-home-note'),analyze=document.getElementById('analyze');
    if(f.size>3*1024*1024){if(note)note.innerHTML='<strong>File too large</strong><span class="cist-dot">·</span><span>Maximum 3 MB for static file analysis</span>';file.value='';return}
    try{
      if(note)note.innerHTML='<strong>Analyzing file…</strong><span class="cist-dot">·</span><span>Hash · real type · embedded links · active content</span>';
      if(analyze)analyze.disabled=true;
      var data=await fileData(f);
      var r=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({file:{name:f.name||'uploaded-file',mime:f.type||'application/octet-stream',data:data}})});
      var out=await r.json().catch(function(){return{}});if(!r.ok)throw new Error(out.error||'File analysis failed');
    }catch(e){if(note)note.innerHTML='<strong>File check unavailable</strong><span class="cist-dot">·</span><span>'+esc(e&&e.message||'The file could not be analyzed')+'</span>'}
    finally{if(analyze)analyze.disabled=false;file.value=''}
  }
  file.addEventListener('change',function(e){var f=file.files&&file.files[0];if(!f||/^image\/(jpeg|png|webp)$/i.test(f.type||''))return;e.stopImmediatePropagation();e.preventDefault();analyzeNonImage(f)},true);

  function ensureSections(){
    panel=document.getElementById('cist-mega-v2-panel');if(!panel)return null;var body=panel.querySelector('.cist-mega-v2-body');if(!body)return null;
    var coverage=document.getElementById('cist-evidence-coverage');if(!coverage){coverage=document.createElement('div');coverage.id='cist-evidence-coverage';coverage.className='cist-mega-v2-section';coverage.innerHTML='<div class="cist-coverage-head"><div class="cist-mega-v2-label" style="margin:0">Evidence coverage</div><div id="cist-coverage-score" class="cist-coverage-score">—</div></div><div class="cist-coverage-bar"><span id="cist-coverage-fill"></span></div><div id="cist-coverage-grid" class="cist-coverage-grid"></div><div id="cist-evidence-confirmed" class="cist-evidence-group"></div><div id="cist-evidence-warnings" class="cist-evidence-group"></div><div id="cist-evidence-sources" class="cist-evidence-source-row"></div>';var first=body.firstElementChild;body.insertBefore(coverage,first&&first.nextSibling?first.nextSibling:first)}
    var rep=document.getElementById('cist-reputation-box');if(!rep){rep=document.createElement('div');rep.id='cist-reputation-box';rep.className='cist-mega-v2-section';rep.innerHTML='<div class="cist-mega-v2-label">Independent reputation</div><div class="cist-reputation-row"><div id="cist-reputation-state" class="cist-reputation-state">Not checked.</div><button id="cist-reputation-btn" class="cist-reputation-btn" type="button">Check external reputation</button></div>';coverage.insertAdjacentElement('afterend',rep)}
    return{coverage:coverage,reputation:rep};
  }
  function renderGroup(id,title,items){var el=document.getElementById(id);if(!el)return;if(!items||!items.length){el.innerHTML='';return}el.innerHTML='<h4>'+esc(title)+'</h4><ul>'+items.slice(0,5).map(function(x){return '<li><strong>'+esc(x.title||'Evidence')+'</strong>'+(x.detail?' — '+esc(x.detail):'')+'</li>'}).join('')+'</ul>'}
  function renderCoverage(d){
    var sec=ensureSections();if(!sec||!d||!d.megaScanner)return;var m=d.megaScanner,c=m.coverage||{},rows=Array.isArray(c.rows)?c.rows:[];
    var score=document.getElementById('cist-coverage-score'),fill=document.getElementById('cist-coverage-fill'),grid=document.getElementById('cist-coverage-grid');if(score)score.textContent=(c.completed||0)+' / '+(c.total||0)+' checks';if(fill)fill.style.width=Math.round((c.ratio||0)*100)+'%';if(grid)grid.innerHTML=rows.map(function(x){var done=x.status==='completed';return '<div class="cist-coverage-item '+(done?'done':'')+'">'+(done?'✓ ':'— ')+esc(x.label||x.id)+'</div>'}).join('');
    renderGroup('cist-evidence-confirmed','Independent confirmations',m.independentConfirmations||[]);renderGroup('cist-evidence-warnings','Warning signals',m.warningSignals||[]);
    var src=document.getElementById('cist-evidence-sources');if(src)src.innerHTML='<strong>Sources:</strong> '+esc((m.sources||[]).join(' · ')||'Specialized scanners');sec.coverage.classList.add('cist-show');
    var reps=Array.isArray(d.reputationChecks)?d.reputationChecks:[],checked=reps.filter(function(x){return x&&x.checked}),danger=reps.find(function(x){return x&&x.status==='known-dangerous'}),state=document.getElementById('cist-reputation-state'),btn=document.getElementById('cist-reputation-btn');
    sec.reputation.classList.toggle('cist-show',Boolean((d.detectedElements&&d.detectedElements.urls||[]).length));
    if(danger){state.textContent='Known threat reported by '+(danger.provider||'an external source')+'.';if(btn)btn.style.display='none'}else if(checked.length){state.textContent='Checked: '+checked.map(function(x){return x.provider||'provider'}).join(' · ')+'. No known threat is not a safety guarantee.';if(btn)btn.style.display='none'}else{state.textContent='Not checked. External providers receive the detected URL only after your consent.';if(btn){btn.style.display='';btn.disabled=false;btn.textContent='Check external reputation'}}
    window.cistUniversalLastResult=d;
  }
  async function runReputation(){var d=window.cistUniversalLastResult,btn=document.getElementById('cist-reputation-btn'),state=document.getElementById('cist-reputation-state');var urls=d&&d.detectedElements&&d.detectedElements.urls||[];if(!urls.length)return;if(btn){btn.disabled=true;btn.textContent='Checking…'}if(state)state.textContent='Checking Google Web Risk / PhishTank where configured…';var results=[];for(var i=0;i<Math.min(3,urls.length);i++){try{var r=await fetch('/api/deep-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:urls[i],consent:true})});var x=await r.json();results.push(x)}catch(e){results.push({status:'unknown'})}}var known=results.find(function(x){return x&&x.status==='known-dangerous'}),providers=[];results.forEach(function(x){(x&&x.providers||[]).forEach(function(p){if(p&&p.checked)providers.push(p.provider)})});if(state)state.textContent=known?'Known threat reported by an external reputation source.':providers.length?'No known threat returned by '+Array.from(new Set(providers)).join(' · ')+'. This is not a safety guarantee.':'External reputation could not complete.';if(btn)btn.style.display='none'}
  document.addEventListener('click',function(e){if(e.target&&e.target.id==='cist-reputation-btn')runReputation()});
  document.addEventListener('cist:mega-result',function(e){renderCoverage(e.detail||{})});
})();
</script>
'''

s=re.sub(r'\s*<style id="cist-universal-evidence-ui-v1-style">.*?</style>','',s,count=1,flags=re.S)
s=re.sub(r'\s*<script id="cist-universal-evidence-ui-v1-script">.*?</script>','',s,count=1,flags=re.S)
if '</head>' not in s or '</body>' not in s: raise RuntimeError('Invalid homepage HTML')
s=s.replace('</head>',STYLE+'\n</head>',1).replace('</body>',SCRIPT+'\n</body>',1)
for token in ['Screenshot / File','Evidence coverage','Check external reputation','message/rfc822']:
    if token not in s: raise RuntimeError('Universal evidence UI guard failed: '+token)
HOME.write_text(s,encoding='utf-8')
print('Applied Universal Evidence Engine UI')
