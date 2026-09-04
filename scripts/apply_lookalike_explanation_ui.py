#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''<style id="cist-lookalike-explanation-style">
.cist-risk-explain{margin:14px 0 0;padding:14px 15px;border:1px solid rgba(255,255,255,.09);border-radius:14px;background:rgba(255,255,255,.025);display:none}.cist-risk-explain.show{display:block}.cist-risk-explain.high{border-color:rgba(255,92,92,.35);background:rgba(255,92,92,.055)}.cist-risk-explain.caution{border-color:rgba(255,190,80,.30);background:rgba(255,190,80,.045)}.cist-risk-explain-title{font-size:13px;font-weight:850;color:var(--text);margin:0 0 8px}.cist-risk-explain-list{display:grid;gap:7px}.cist-risk-explain-item{font-size:12px;line-height:1.45;color:var(--muted)}.cist-risk-explain-item strong{color:var(--text)}.cist-risk-explain-action{margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.07);font-size:12px;line-height:1.45;color:var(--text)}
</style>'''

SCRIPT = r'''<script id="cist-lookalike-explanation-script">
(function(){
  var input=document.getElementById('url'),card=document.getElementById('result-card'),summary=document.getElementById('summary');
  if(!input||!card)return;
  var box=document.createElement('div');box.className='cist-risk-explain';box.setAttribute('aria-live','polite');
  box.innerHTML='<div class="cist-risk-explain-title">Why this may be risky</div><div class="cist-risk-explain-list"></div><div class="cist-risk-explain-action"></div>';
  var anchor=summary||card.firstElementChild; if(anchor&&anchor.parentNode===card)anchor.insertAdjacentElement('afterend',box);else card.appendChild(box);
  var list=box.querySelector('.cist-risk-explain-list'),action=box.querySelector('.cist-risk-explain-action');
  var last='',seq=0;
  function esc(v){return String(v||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function normalize(v){v=String(v||'').trim();if(!/^https?:\/\//i.test(v)&&/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}/i.test(v))v='https://'+v;return v}
  function isLink(v){try{var u=new URL(normalize(v));return /^https?:$/.test(u.protocol)}catch(e){return false}}
  function existingReasons(){var out=[];var nodes=document.querySelectorAll('#signals li');for(var i=0;i<nodes.length&&out.length<3;i++){var t=String(nodes[i].textContent||'').replace(/\s+/g,' ').trim();if(t)out.push({title:'Detected signal',detail:t})}return out}
  function render(findings){
    var reasons=findings.slice();existingReasons().forEach(function(x){if(reasons.length<3&&!reasons.some(function(r){return String(r.detail||'').indexOf(x.detail)>=0}))reasons.push(x)});
    if(!reasons.length){box.className='cist-risk-explain';box.style.display='none';return}
    var high=findings.some(function(x){return x.severity==='high'});box.style.display='';box.className='cist-risk-explain show '+(high?'high':'caution');
    list.innerHTML=reasons.slice(0,3).map(function(r){return '<div class="cist-risk-explain-item"><strong>'+esc(r.title||'Warning')+':</strong> '+esc(r.detail||'')+'</div>'}).join('');
    action.textContent=high?'Do not sign in or enter payment details. Open the official service directly from its app or typed address.':'Verify the final domain and sender before entering passwords, payment details, or downloading a file.';
  }
  async function run(){
    var raw=String(input.value||'').trim();if(!isLink(raw))return;var url=normalize(raw);if(last===url)return;last=url;var mine=++seq;
    try{var r=await fetch('/api/lookalike-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({url:url})});var d=await r.json();if(mine!==seq)return;render(Array.isArray(d.findings)?d.findings:[])}catch(e){if(mine===seq)render([])}
  }
  function reset(){last='';seq++;box.className='cist-risk-explain';box.style.display='none';list.innerHTML='';action.textContent=''}
  input.addEventListener('input',reset);document.addEventListener('cist:result-updated',function(){setTimeout(run,0)});var form=document.getElementById('scan-form');if(form)form.addEventListener('submit',function(){last=''},true);
})();</script>'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
source = HOME.read_text(encoding='utf-8')
if 'id="cist-lookalike-explanation-style"' in source or 'id="cist-lookalike-explanation-script"' in source:
    raise RuntimeError('Lookalike explanation UI already applied')
source = source.replace('</head>', STYLE + '\n</head>', 1).replace('</body>', SCRIPT + '\n</body>', 1)
HOME.write_text(source, encoding='utf-8')
print('Added brand lookalike detection explanation UI')
