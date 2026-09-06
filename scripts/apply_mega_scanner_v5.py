#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-mega-scanner-v5-style">
.cist-v5-no-warning{border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 24%,var(--line))!important;background:color-mix(in srgb,var(--cist-accent,#788ff7) 3%,var(--card))!important}
.cist-v5-no-warning-list{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.cist-v5-no-warning-list li{position:relative;padding-left:19px;font-size:11px;line-height:1.45;color:var(--text)}
.cist-v5-no-warning-list li:before{content:'✓';position:absolute;left:0;top:0;color:var(--muted);font-weight:950}
.cist-v5-no-warning-list strong{display:block;margin-bottom:1px}.cist-v5-no-warning-list span{color:var(--muted)}
.cist-v5-chain-hidden{display:none!important}
#cist-v3-positive .cist-mega-v2-label{color:#64c99d}
</style>
'''

SCRIPT = r'''
<script id="cist-mega-scanner-v5-script">
(function(){
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function cap(v){v=clean(v);return v?v.charAt(0).toUpperCase()+v.slice(1):''}
  function decision(risk,identity,confidence){
    risk=clean(risk).toLowerCase();identity=clean(identity).toLowerCase();confidence=clean(confidence).toLowerCase();
    if(risk==='high')return'High risk';
    if(risk==='caution')return'Verify first';
    if(risk==='low'&&identity==='high'&&confidence==='high')return'Likely official';
    if(risk==='low'&&(identity==='medium'||identity==='low'))return'Verify first';
    if(risk==='low'&&identity==='unknown')return'No major warning — identity not confirmed';
    if(risk==='low')return'No major warning';
    return'Not enough evidence';
  }
  function ensureNoWarning(){
    var body=document.querySelector('#cist-mega-v2-panel .cist-mega-v2-body');if(!body)return null;
    var section=document.getElementById('cist-v5-no-warning');
    if(!section){
      section=document.createElement('div');section.id='cist-v5-no-warning';section.className='cist-mega-v2-section cist-v5-no-warning';section.style.display='none';
      section.innerHTML='<div class="cist-mega-v2-label">No warning found</div><ul id="cist-v5-no-warning-list" class="cist-v5-no-warning-list"></ul>';
      var positive=document.getElementById('cist-v3-positive');
      if(positive)positive.insertAdjacentElement('afterend',section);else body.insertBefore(section,body.children[1]||null);
    }
    return section;
  }
  function renderEvidenceKinds(d){
    var positive=document.getElementById('cist-v3-positive');
    if(positive){var label=positive.querySelector('.cist-mega-v2-label');if(label)label.textContent='Confirmed evidence';var items=Array.isArray(d.positiveEvidence)?d.positiveEvidence:[];positive.style.display=items.length?'block':'none'}
    var section=ensureNoWarning();if(!section)return;
    var noWarnings=Array.isArray(d.noWarningEvidence)?d.noWarningEvidence:[],list=document.getElementById('cist-v5-no-warning-list');
    if(noWarnings.length){section.style.display='block';list.innerHTML=noWarnings.slice(0,3).map(function(x){return '<li><strong>'+esc(x.title||'No warning found')+'</strong><span>'+esc(x.detail||'')+'</span></li>'}).join('')}else{section.style.display='none';if(list)list.innerHTML=''}
  }
  function renderDecision(d){
    var ex=d.explanation||{},risk=clean((d.megaScanner&&d.megaScanner.finalRisk)||ex.verdict||'unknown').toLowerCase(),identity=clean(d.identityConsistency&&d.identityConsistency.level||'unknown').toLowerCase(),confidence=clean(ex.confidence&&ex.confidence.level||'unknown').toLowerCase();
    var head=document.getElementById('cist-mega-headline');if(head)head.textContent=decision(risk,identity,confidence);
    var copy=document.getElementById('cist-v4-summary-copy');if(!copy)return;
    if(risk==='low'&&identity==='medium')copy.textContent='No major safety warning was found, but the detected profile and website relationship was not independently confirmed.';
    else if(risk==='low'&&identity==='unknown')copy.textContent='No major safety warning was found, but there is not enough independent evidence to establish the identity.';
    else if(risk==='low'&&identity==='high')copy.textContent=clean(ex.headline)||'Independent relationship evidence supports this identity.';
    else copy.textContent=clean(ex.headline)||'The result combines the evidence and checks that completed.';
  }
  function renderVerifiedChain(d){
    var chain=document.getElementById('cist-mega-chain'),section=chain&&chain.closest('.cist-mega-v2-section');if(!chain||!section)return;
    var verified=Array.isArray(d.verifiedRelationships)?d.verifiedRelationships:[];
    if(!verified.length){
      var fallback=(Array.isArray(d.relationshipChecks)?d.relationshipChecks:[]).filter(function(x){return x&&x.positive&&x.status==='confirmed'}).map(function(x){return {websiteDomain:x.websiteDomain,platform:x.socialPlatform,handle:x.socialHandle,status:'confirmed'}});
      verified=fallback;
    }
    if(!verified.length){chain.innerHTML='';section.classList.add('cist-v5-chain-hidden');return}
    section.classList.remove('cist-v5-chain-hidden');var label=section.querySelector('.cist-mega-v2-label');if(label)label.textContent='Verified relationship';
    var rel=verified[0],domain=clean(rel.websiteDomain),platform=clean(rel.platform).toUpperCase(),handle=clean(rel.handle);
    chain.className='cist-v4-chain';
    chain.innerHTML='<span class="cist-v4-chain-node">'+esc(domain)+'</span><span class="cist-v4-chain-rel">↔ confirmed</span><span class="cist-v4-chain-node">'+esc(platform)+' @'+esc(handle)+'</span>';
  }
  function removeFalseDetectedFile(d){
    var target=document.getElementById('cist-v4-detected');if(!target)return;var el=d.detectedElements||{};
    if(!(Array.isArray(el.files)&&el.files.length)){
      var html=target.innerHTML;html=html.replace(/\s*·\s*visible file name/gi,'').replace(/visible file name\s*·\s*/gi,'').replace(/visible file name/gi,'');target.innerHTML=html;
    }
  }
  function render(d){if(!d||!d.megaScanner)return;renderEvidenceKinds(d);renderDecision(d);renderVerifiedChain(d);removeFalseDetectedFile(d)}
  document.addEventListener('cist:mega-result',function(e){try{render(e.detail)}catch(err){}});
})();
</script>
'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s = HOME.read_text(encoding='utf-8')
s = re.sub(r'\s*<style id="cist-mega-scanner-v5-style">.*?</style>', '', s, count=1, flags=re.S)
s = re.sub(r'\s*<script id="cist-mega-scanner-v5-script">.*?</script>', '', s, count=1, flags=re.S)
if 'cist-mega-scanner-v4-script' not in s:
    raise RuntimeError('Mega Scanner V4 UI must be applied before V5')
s = s.replace('</head>', STYLE + '\n</head>', 1).replace('</body>', SCRIPT + '\n</body>', 1)
for token in ['Confirmed evidence','No warning found','Verified relationship','identity not confirmed']:
    if token not in s:
        raise RuntimeError('V5 UI guard failed: ' + token)
HOME.write_text(s, encoding='utf-8')
print('Applied Mega Scanner V5 verified-evidence result logic')
