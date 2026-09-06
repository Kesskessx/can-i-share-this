#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-mega-scanner-v3-style">
.cist-v3-positive{border-color:color-mix(in srgb,#4fbf8f 32%,var(--line))!important;background:color-mix(in srgb,#4fbf8f 5%,var(--card))!important}
.cist-v3-positive-list{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.cist-v3-positive-list li{position:relative;padding-left:20px;font-size:11.5px;line-height:1.45;color:var(--text)}
.cist-v3-positive-list li:before{content:'✓';position:absolute;left:0;top:0;color:#4fbf8f;font-weight:950}
.cist-v3-positive-list strong{display:block;margin-bottom:1px;font-size:11.5px}.cist-v3-positive-list span{color:var(--muted)}
.cist-v3-identity-row{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-top:8px}
.cist-v3-pill{padding:5px 7px;border:1px solid var(--line);border-radius:999px;font-size:9px;font-weight:850;color:var(--muted);background:var(--card)}
.cist-v3-pill[data-level="high"]{border-color:color-mix(in srgb,#4fbf8f 35%,var(--line));color:color-mix(in srgb,#4fbf8f 78%,var(--text))}
.cist-v3-pill[data-level="low"]{border-color:color-mix(in srgb,var(--red) 34%,var(--line));color:var(--red)}
.cist-v3-coverage{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}.cist-v3-check{padding:5px 7px;border:1px solid var(--line);border-radius:9px;background:var(--card);font-size:9px;font-weight:800;color:var(--muted)}
.cist-v3-context{margin-top:8px;color:var(--muted);font-size:10.5px;line-height:1.45}.cist-v3-context strong{color:var(--text)}
</style>
'''

SCRIPT = r'''
<script id="cist-mega-scanner-v3-script">
(function(){
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function cap(v){v=clean(v);return v?v.charAt(0).toUpperCase()+v.slice(1):''}
  function ensure(){
    var body=document.querySelector('#cist-mega-v2-panel .cist-mega-v2-body');if(!body)return null;
    var pos=document.getElementById('cist-v3-positive');
    if(!pos){pos=document.createElement('div');pos.id='cist-v3-positive';pos.className='cist-mega-v2-section cist-v3-positive';pos.style.display='none';pos.innerHTML='<div class="cist-mega-v2-label">Positive evidence</div><ul id="cist-v3-positive-list" class="cist-v3-positive-list"></ul><div id="cist-v3-identity-row" class="cist-v3-identity-row"></div>';var why=body.querySelector('.cist-mega-v2-section');body.insertBefore(pos,why||body.firstChild)}
    var coverage=document.getElementById('cist-v3-coverage-wrap');
    if(!coverage){coverage=document.createElement('div');coverage.id='cist-v3-coverage-wrap';coverage.className='cist-mega-v2-section';coverage.style.display='none';coverage.innerHTML='<div class="cist-mega-v2-label">Cross-check coverage</div><div id="cist-v3-coverage" class="cist-v3-coverage"></div><div id="cist-v3-context" class="cist-v3-context"></div>';var share=body.querySelector('.cist-mega-share-row');body.insertBefore(coverage,share||null)}
    return {pos:pos,coverage:coverage};
  }
  function dedupeChain(){
    var chain=document.getElementById('cist-mega-chain');if(!chain)return;var seen={},children=Array.from(chain.children);children.forEach(function(n){if(!n.classList.contains('cist-mega-node'))return;var k=clean(n.textContent).toLowerCase();if(!k)return;if(seen[k]){var prev=n.previousElementSibling,next=n.nextElementSibling;n.remove();if(prev&&prev.classList.contains('cist-mega-arrow'))prev.remove();else if(next&&next.classList.contains('cist-mega-arrow'))next.remove()}else seen[k]=1});
  }
  function render(d){
    var ui=ensure();if(!ui||!d)return;
    var positives=Array.isArray(d.positiveEvidence)?d.positiveEvidence:[],list=document.getElementById('cist-v3-positive-list'),identity=d.identityConsistency||{},row=document.getElementById('cist-v3-identity-row');
    if(positives.length){ui.pos.style.display='block';list.innerHTML=positives.slice(0,3).map(function(x){return '<li><strong>'+esc(x.title||'Positive evidence')+'</strong><span>'+esc(x.detail||'')+'</span></li>'}).join('')}else ui.pos.style.display='none';
    if(row){var html='';if(identity.level&&identity.level!=='unknown')html+='<span class="cist-v3-pill" data-level="'+esc(identity.level)+'">Identity consistency: '+esc(cap(identity.level))+'</span>';var ac=d.accountContext||{};if(ac.maturity&&ac.maturity!=='unknown')html+='<span class="cist-v3-pill">Account maturity: '+esc(cap(ac.maturity))+' · context only</span>';row.innerHTML=html}
    var orch=d.orchestration||{},checks=Array.isArray(d.crossChecks)?d.crossChecks:[],cov=document.getElementById('cist-v3-coverage'),ctx=document.getElementById('cist-v3-context');
    var types=[];checks.forEach(function(x){var t=clean(x&&x.type);if(t&&types.indexOf(t)<0)types.push(t)});if(orch.relationshipChecksRun)types.push('website ↔ profile');
    if(types.length){ui.coverage.style.display='block';cov.innerHTML=types.slice(0,9).map(function(t){return '<span class="cist-v3-check">'+esc(t.replace(/-/g,' '))+'</span>'}).join('');var el=d.detectedElements||{},parts=[];Object.keys(el).forEach(function(k){if(Array.isArray(el[k])&&el[k].length)parts.push(el[k].length+' '+k)});ctx.innerHTML=parts.length?'<strong>Detected:</strong> '+esc(parts.join(' · ')):''}else ui.coverage.style.display='none';
    dedupeChain();
  }
  document.addEventListener('cist:mega-result',function(e){try{render(e.detail)}catch(err){}});
})();
</script>
'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s = HOME.read_text(encoding='utf-8')
s = re.sub(r'\s*<style id="cist-mega-scanner-v3-style">.*?</style>', '', s, count=1, flags=re.S)
s = re.sub(r'\s*<script id="cist-mega-scanner-v3-script">.*?</script>', '', s, count=1, flags=re.S)
if 'cist-mega-scanner-v2-script' not in s:
    raise RuntimeError('Mega Scanner V2 UI must be applied before V3')
s = s.replace('</head>', STYLE + '\n</head>', 1).replace('</body>', SCRIPT + '\n</body>', 1)
for token in ['Positive evidence','Cross-check coverage','Identity consistency','cist:mega-result']:
    if token not in s:
        raise RuntimeError('V3 UI guard failed: ' + token)
HOME.write_text(s, encoding='utf-8')
print('Applied Mega Scanner V3 positive evidence and cross-check coverage UI')
