#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-mega-scanner-v4-style">
#cist-mega-confidence{display:none!important}
#image-analysis.cist-v4-secondary-hidden{display:none!important}
.cist-v4-summary-copy{margin:5px 0 0;color:var(--muted);font-size:11px;line-height:1.45;max-width:560px}
.cist-v4-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;padding:0}
.cist-v4-metric{min-width:0;padding:10px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--soft) 52%,transparent)}
.cist-v4-metric-label{display:block;color:var(--muted);font-size:8px;font-weight:900;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px}
.cist-v4-metric-value{display:block;font-size:11px;font-weight:900;line-height:1.2;overflow-wrap:anywhere}
.cist-v4-metric[data-tone="good"] .cist-v4-metric-value{color:#64c99d}
.cist-v4-metric[data-tone="warn"] .cist-v4-metric-value{color:var(--amber)}
.cist-v4-metric[data-tone="bad"] .cist-v4-metric-value{color:var(--red)}
.cist-v4-context{display:none;padding:11px 12px;border:1px solid color-mix(in srgb,var(--amber) 25%,var(--line));border-radius:13px;background:color-mix(in srgb,var(--amber) 4%,var(--card));font-size:11px;line-height:1.45;color:var(--muted)}
.cist-v4-context strong{display:block;color:var(--text);margin-bottom:2px}
.cist-v4-chain{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.cist-v4-chain-node{padding:7px 9px;border:1px solid var(--line);border-radius:10px;background:var(--card);font-size:10px;font-weight:850;overflow-wrap:anywhere}
.cist-v4-chain-rel{font-size:9px;color:#64c99d;font-weight:850;text-align:center;line-height:1.2}
.cist-v4-checked{display:grid;gap:7px;margin-top:6px}
.cist-v4-check-row{position:relative;padding-left:18px;color:var(--text);font-size:10.5px;font-weight:800;line-height:1.35}
.cist-v4-check-row:before{content:'✓';position:absolute;left:0;color:#64c99d;font-weight:950}
.cist-v4-detected{margin-top:9px;color:var(--muted);font-size:10px;line-height:1.4}
.cist-v4-detected strong{color:var(--text)}
#cist-v3-coverage{display:none!important}
#cist-v3-context{display:none!important}
#cist-v3-coverage-wrap .cist-mega-v2-label{margin-bottom:5px}
.cist-v4-why-hidden{display:none!important}
@media(max-width:600px){
 .cist-v4-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
 .cist-v4-metric{padding:9px}
 .cist-v4-metric-value{font-size:10.5px}
 .cist-v4-chain{gap:5px}.cist-v4-chain-node{font-size:9.5px;padding:6px 8px}.cist-v4-chain-rel{font-size:8.5px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-mega-scanner-v4-script">
(function(){
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function cap(v){v=clean(v);return v?v.charAt(0).toUpperCase()+v.slice(1):''}
  function norm(v){return clean(v).toLowerCase().replace(/[^a-z0-9]+/g,' ').replace(/\s+/g,' ').trim()}
  function uniq(a){var out=[],seen={};(a||[]).forEach(function(x){var k=norm(x);if(k&&!seen[k]){seen[k]=1;out.push(x)}});return out}
  function tone(metric,value){value=clean(value).toLowerCase();if(metric==='risk'){if(value==='low')return'good';if(value==='caution')return'warn';if(value==='high')return'bad'}if(metric==='identity'){if(value==='high')return'good';if(value==='medium')return'warn';if(value==='low')return'bad'}if(metric==='maturity'){if(value==='limited'||value==='new')return'warn';if(value==='established')return'good'}if(metric==='confidence'){if(value==='high')return'good';if(value==='low')return'warn'}return'neutral'}
  function decision(risk,identity){risk=clean(risk).toLowerCase();identity=clean(identity).toLowerCase();if(risk==='high')return'High risk';if(risk==='caution')return'Verify first';if(risk==='low'&&identity==='high')return'Likely official';if(risk==='low')return'No major warning';return'Not enough evidence'}
  function ensureSummary(){
    var panel=document.getElementById('cist-mega-v2-panel'),body=panel&&panel.querySelector('.cist-mega-v2-body'),head=panel&&panel.querySelector('.cist-mega-v2-head');if(!body||!head)return null;
    var copy=document.getElementById('cist-v4-summary-copy');if(!copy){copy=document.createElement('p');copy.id='cist-v4-summary-copy';copy.className='cist-v4-summary-copy';var h=head.querySelector('h3');if(h)h.insertAdjacentElement('afterend',copy)}
    var metrics=document.getElementById('cist-v4-metrics');if(!metrics){metrics=document.createElement('div');metrics.id='cist-v4-metrics';metrics.className='cist-v4-metrics';body.insertBefore(metrics,body.firstChild)}
    var context=document.getElementById('cist-v4-context');if(!context){context=document.createElement('div');context.id='cist-v4-context';context.className='cist-v4-context';var pos=document.getElementById('cist-v3-positive');if(pos)pos.insertAdjacentElement('afterend',context);else body.insertBefore(context,body.children[1]||null)}
    var coverage=document.getElementById('cist-v3-coverage-wrap');if(coverage){var label=coverage.querySelector('.cist-mega-v2-label');if(label)label.textContent='Checked';var checked=document.getElementById('cist-v4-checked');if(!checked){checked=document.createElement('div');checked.id='cist-v4-checked';checked.className='cist-v4-checked';coverage.appendChild(checked)}var detected=document.getElementById('cist-v4-detected');if(!detected){detected=document.createElement('div');detected.id='cist-v4-detected';detected.className='cist-v4-detected';coverage.appendChild(detected)}}
    return {panel:panel,body:body,head:head,copy:copy,metrics:metrics,context:context,coverage:coverage};
  }
  function renderMetrics(d,ui){
    var ex=d.explanation||{},risk=clean((d.megaScanner&&d.megaScanner.finalRisk)||ex.verdict||'unknown').toLowerCase(),identity=clean(d.identityConsistency&&d.identityConsistency.level||'unknown').toLowerCase(),maturity=clean(d.accountContext&&d.accountContext.maturity||'unknown').toLowerCase(),conf=clean(ex.confidence&&ex.confidence.level||'unknown').toLowerCase(),score=typeof(ex.confidence&&ex.confidence.score)==='number'?Math.round(ex.confidence.score*100):null;
    var head=document.getElementById('cist-mega-headline');if(head)head.textContent=decision(risk,identity);if(ui.copy)ui.copy.textContent=clean(ex.headline)||'The result combines the evidence and independent checks that completed.';
    var values=[['Risk',risk,'risk'],['Identity',identity,'identity'],['Account maturity',maturity,'maturity'],['Confidence',conf+(score!==null?' · '+score+'%':''),'confidence']];
    ui.metrics.innerHTML=values.map(function(x){var raw=x[1].split(' · ')[0];return '<div class="cist-v4-metric" data-tone="'+esc(tone(x[2],raw))+'"><span class="cist-v4-metric-label">'+esc(x[0])+'</span><span class="cist-v4-metric-value">'+esc(cap(x[1]))+'</span></div>'}).join('');
  }
  function sameReason(r,positives){var a=norm((r&&r.title||'')+' '+(r&&r.detail||''));return positives.some(function(p){var b=norm((p&&p.title||'')+' '+(p&&p.detail||''));return a&&b&&(a===b||a.indexOf(b)>=0||b.indexOf(a)>=0)})}
  function simplifyWhy(d){
    var why=document.getElementById('cist-mega-reasons'),section=why&&why.closest('.cist-mega-v2-section');if(!why||!section)return;var positives=Array.isArray(d.positiveEvidence)?d.positiveEvidence:[],reasons=Array.isArray(d.explanation&&d.explanation.reasons)?d.explanation.reasons:[];var distinct=reasons.filter(function(r){if(clean(r&&r.severity).toLowerCase()==='positive')return false;if(sameReason(r,positives))return false;return true});
    var maturity=clean(d.accountContext&&d.accountContext.maturity).toLowerCase();distinct=distinct.filter(function(r){return !(maturity==='limited'&&/new or limited account history|limited account history/i.test((r&&r.title||'')+' '+(r&&r.detail||'')))});
    if(!distinct.length){section.classList.add('cist-v4-why-hidden');return}section.classList.remove('cist-v4-why-hidden');why.innerHTML=distinct.slice(0,3).map(function(r){return '<li><strong>'+esc(r.title||'Signal')+'</strong><span>'+esc(r.detail||'')+'</span></li>'}).join('');
  }
  function renderContext(d,ui){var ac=d.accountContext||{},m=clean(ac.maturity).toLowerCase();if(m==='limited'||m==='new'){ui.context.style.display='block';ui.context.innerHTML='<strong>Context: this account has limited public history</strong>'+esc(ac.note||'A new or low-activity account is useful context, but it is not evidence of impersonation by itself.')}else{ui.context.style.display='none';ui.context.innerHTML=''}}
  function renderChain(d){
    var chain=document.getElementById('cist-mega-chain');if(!chain)return;var rel=(Array.isArray(d.relationshipChecks)?d.relationshipChecks:[]).find(function(x){return x&&x.positive&&x.status==='confirmed'});if(!rel)return;var brands=d.detectedElements&&Array.isArray(d.detectedElements.claimedBrands)?d.detectedElements.claimedBrands:[];var brand=clean(brands[0])||'Claimed identity',domain=clean(rel.websiteDomain),platform=clean(rel.socialPlatform).toUpperCase()||'Social',handle=clean(rel.socialHandle);chain.className='cist-v4-chain';chain.innerHTML='<span class="cist-v4-chain-node">'+esc(brand)+'</span><span class="cist-mega-arrow">→</span><span class="cist-v4-chain-node">'+esc(domain)+'</span><span class="cist-v4-chain-rel">↔ confirmed</span><span class="cist-v4-chain-node">@'+esc(handle)+' on '+esc(platform)+'</span>';
  }
  function cleanedElements(d){var el=d.detectedElements||{},domains=(el.domains||[]).map(function(x){return clean(x).toLowerCase()});var files=(el.files||[]).filter(function(f){var x=clean(f).toLowerCase();return domains.indexOf(x)<0});return {urls:el.urls||[],domains:el.domains||[],emails:el.emails||[],phones:el.phones||[],crypto:el.crypto||[],qr:el.qr||[],files:files,socialProfiles:el.socialProfiles||[],claimedBrands:el.claimedBrands||[]}}
  function checkedLabel(t){t=clean(t).toLowerCase();return {'url':'Website','social-profile':'Social profile','message':'Visible message','email':'Email','crypto':'Crypto address'}[t]||cap(t.replace(/-/g,' '))}
  function renderCoverage(d,ui){if(!ui.coverage)return;var checks=Array.isArray(d.crossChecks)?d.crossChecks:[],labels=[];checks.forEach(function(x){var l=checkedLabel(x&&x.type);if(l&&labels.indexOf(l)<0)labels.push(l)});if(d.orchestration&&d.orchestration.relationshipChecksRun)labels.push('Website ↔ profile relationship');labels=uniq(labels);var checked=document.getElementById('cist-v4-checked');if(checked)checked.innerHTML=labels.map(function(x){return '<div class="cist-v4-check-row">'+esc(x)+'</div>'}).join('');var el=cleanedElements(d),det=[];if(el.urls.length||el.domains.length)det.push('website');if(el.socialProfiles.length)det.push('social profile');if(el.emails.length)det.push('email');if(el.phones.length)det.push('phone number');if(el.qr.length)det.push('QR code');if(el.crypto.length)det.push('crypto address');if(el.claimedBrands.length)det.push('brand claim');if(el.files.length)det.push('visible file name');var target=document.getElementById('cist-v4-detected');if(target)target.innerHTML=det.length?'<strong>Detected:</strong> '+esc(uniq(det).join(' · ')):'';ui.coverage.style.display=labels.length?'block':'none'}
  function hideRawImageCard(d){if(!(d.detectedType==='image'||d.orchestration))return;var raw=document.getElementById('image-analysis');if(raw)raw.classList.add('cist-v4-secondary-hidden');var upload=document.getElementById('choose-image');if(upload)upload.textContent='Upload screenshot'}
  function render(d){var ui=ensureSummary();if(!ui||!d||!d.megaScanner)return;renderMetrics(d,ui);simplifyWhy(d);renderContext(d,ui);renderChain(d);renderCoverage(d,ui);hideRawImageCard(d);var kicker=ui.head.querySelector('.cist-mega-v2-kicker');if(kicker)kicker.textContent='Universal safety result'}
  document.addEventListener('cist:mega-result',function(e){try{render(e.detail)}catch(err){}});
})();
</script>
'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s = HOME.read_text(encoding='utf-8')
s = re.sub(r'\s*<style id="cist-mega-scanner-v4-style">.*?</style>', '', s, count=1, flags=re.S)
s = re.sub(r'\s*<script id="cist-mega-scanner-v4-script">.*?</script>', '', s, count=1, flags=re.S)
if 'cist-mega-scanner-v3-script' not in s:
    raise RuntimeError('Mega Scanner V3 UI must be applied before V4')
s = s.replace('</head>', STYLE + '\n</head>', 1).replace('</body>', SCRIPT + '\n</body>', 1)
for token in ['Universal safety result','Account maturity','Website ↔ profile relationship','cist-v4-secondary-hidden']:
    if token not in s:
        raise RuntimeError('V4 UI guard failed: ' + token)
HOME.write_text(s, encoding='utf-8')
print('Applied Mega Scanner V4 concise decision-first result UI')
