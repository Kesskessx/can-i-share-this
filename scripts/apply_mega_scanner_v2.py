#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-mega-scanner-v2-style">
#cist-mega-or{display:none!important}
#cist-mega-screenshot-kicker{width:min(720px,calc(100% - 28px));margin:12px auto 7px;text-align:center;color:var(--text);font-size:12px;font-weight:900;letter-spacing:-.01em}
#image-safety-tools.cist-screenshot-first{width:min(720px,calc(100% - 28px));margin:0 auto!important;padding:9px!important;border:1px solid color-mix(in srgb,var(--cist-accent,#788ff7) 34%,var(--line))!important;background:color-mix(in srgb,var(--cist-accent,#788ff7) 5%,var(--card))!important;box-shadow:0 10px 28px rgba(0,0,0,.08)!important}
#image-safety-tools.cist-screenshot-first #choose-image{min-height:52px!important;border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 48%,var(--line))!important;background:color-mix(in srgb,var(--cist-accent,#788ff7) 10%,var(--soft))!important;font-size:13px!important}
#image-safety-tools.cist-screenshot-first.cist-drag-over{border-style:solid!important;background:color-mix(in srgb,var(--cist-accent,#788ff7) 12%,var(--card))!important}
#cist-mega-paste-separator{width:min(720px,calc(100% - 28px));margin:10px auto 7px;display:flex;align-items:center;gap:10px;color:var(--muted);font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}
#cist-mega-paste-separator:before,#cist-mega-paste-separator:after{content:'';height:1px;flex:1;background:var(--line)}
#cist-mega-v2-panel{display:none;max-width:760px;margin:14px auto 0;text-align:left}
#cist-mega-v2-panel.cist-show{display:block}
.cist-mega-v2-shell{border:1px solid var(--line);border-radius:17px;background:var(--card);box-shadow:var(--shadow);overflow:hidden}
.cist-mega-v2-head{padding:15px 16px;border-bottom:1px solid var(--line);display:flex;align-items:flex-start;justify-content:space-between;gap:14px}
.cist-mega-v2-kicker{display:block;color:var(--muted);font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}
.cist-mega-v2-head h3{margin:4px 0 0;font-size:16px;line-height:1.3;letter-spacing:-.02em}
.cist-mega-v2-confidence{flex:0 0 auto;padding:6px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:9px;font-weight:850;white-space:nowrap}
.cist-mega-v2-body{padding:14px 16px;display:grid;gap:13px}
.cist-mega-v2-section{padding:12px;border:1px solid color-mix(in srgb,var(--line) 84%,transparent);border-radius:13px;background:color-mix(in srgb,var(--soft) 58%,transparent)}
.cist-mega-v2-label{margin:0 0 8px;color:var(--muted);font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:.075em}
.cist-mega-reasons,.cist-mega-limits{display:grid;gap:7px;margin:0;padding:0;list-style:none}
.cist-mega-reasons li,.cist-mega-limits li{font-size:11.5px;line-height:1.45;color:var(--text)}
.cist-mega-reasons strong{display:block;font-size:11.5px;margin-bottom:1px}
.cist-mega-reasons span,.cist-mega-limits li{color:var(--muted)}
.cist-mega-evidence-chain{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.cist-mega-node{max-width:220px;padding:6px 8px;border:1px solid var(--line);border-radius:10px;background:var(--card);font-size:10px;font-weight:800;overflow-wrap:anywhere}
.cist-mega-arrow{color:var(--muted);font-size:10px}
.cist-mega-brand-alert{padding:9px 10px;border-radius:11px;border:1px solid color-mix(in srgb,var(--red) 34%,var(--line));background:color-mix(in srgb,var(--red) 5%,var(--card));font-size:11px;line-height:1.45}
.cist-mega-action{font-size:12px;line-height:1.5;font-weight:800}
.cist-mega-share-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.cist-mega-share{appearance:none;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);padding:8px 10px;font:inherit;font-size:10.5px;font-weight:850;cursor:pointer}
.cist-mega-share:hover{border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 45%,var(--line))}
.cist-mega-share-note{color:var(--muted);font-size:9.5px;line-height:1.4}
#cist-shared-result{display:none;max-width:760px;margin:14px auto 0;text-align:left}
#cist-shared-result.cist-show{display:block}
.cist-shared-shell{border:1px solid var(--line);border-radius:17px;background:var(--card);padding:16px;box-shadow:var(--shadow)}
.cist-shared-shell h3{margin:4px 0 6px;font-size:17px}.cist-shared-shell p{margin:0;color:var(--muted);font-size:11.5px;line-height:1.5}
.cist-shared-risk{display:inline-flex;margin-top:10px;padding:5px 8px;border:1px solid var(--line);border-radius:999px;font-size:10px;font-weight:900;text-transform:uppercase}
.cist-shared-reasons{margin:12px 0 0;padding-left:18px}.cist-shared-reasons li{margin:6px 0;font-size:11.5px;line-height:1.45}
.cist-shared-action{margin-top:12px!important;color:var(--text)!important;font-weight:800}
.cist-shared-fresh{margin-top:12px}
@media(max-width:600px){
 #cist-mega-screenshot-kicker,#image-safety-tools.cist-screenshot-first,#cist-mega-paste-separator{width:calc(100% - 24px)}
 #image-safety-tools.cist-screenshot-first #choose-image{min-height:50px!important}
 .cist-mega-v2-head,.cist-mega-v2-body,.cist-shared-shell{padding-left:12px;padding-right:12px}
 .cist-mega-v2-head{gap:8px}.cist-mega-v2-head h3{font-size:15px}.cist-mega-v2-confidence{font-size:8.5px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-mega-scanner-v2-script">
(function(){
  var form=document.getElementById('scan-form'),input=document.getElementById('url'),tools=document.getElementById('image-safety-tools'),fileInput=document.getElementById('image-file'),result=document.getElementById('result'),imageAnalysis=document.getElementById('image-analysis');
  if(!form||!input||!tools)return;
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function cap(v){v=clean(v);return v?v.charAt(0).toUpperCase()+v.slice(1):''}
  tools.classList.add('cist-screenshot-first');
  var upload=document.getElementById('choose-image');if(upload){upload.textContent='Upload or paste a screenshot';upload.setAttribute('aria-label','Upload or paste a screenshot to analyze')}
  var kicker=document.getElementById('cist-mega-screenshot-kicker');if(kicker)kicker.remove();
  kicker=document.createElement('div');kicker.id='cist-mega-screenshot-kicker';kicker.textContent='Fastest check: send the screenshot exactly as you received it.';
  form.parentNode.insertBefore(kicker,form);form.parentNode.insertBefore(tools,form);
  var sep=document.getElementById('cist-mega-paste-separator');if(sep)sep.remove();sep=document.createElement('div');sep.id='cist-mega-paste-separator';sep.textContent='or paste something suspicious';form.parentNode.insertBefore(sep,form);
  input.placeholder='Paste a link, message, email, profile or crypto address';
  var badges=document.getElementById('cist-mega-badges');if(badges)form.insertAdjacentElement('afterend',badges);
  function transferImage(files){if(!fileInput||!files||!files.length)return false;var f=Array.from(files).find(function(x){return /^image\/(jpeg|png|webp)$/i.test(x.type||'')});if(!f)return false;try{var dt=new DataTransfer();dt.items.add(f);fileInput.files=dt.files;fileInput.dispatchEvent(new Event('change',{bubbles:true}));return true}catch(e){return false}}
  ['dragenter','dragover'].forEach(function(name){tools.addEventListener(name,function(e){e.preventDefault();tools.classList.add('cist-drag-over')})});
  ['dragleave','drop'].forEach(function(name){tools.addEventListener(name,function(e){e.preventDefault();tools.classList.remove('cist-drag-over');if(name==='drop')transferImage(e.dataTransfer&&e.dataTransfer.files)})});
  document.addEventListener('paste',function(e){var tag=(e.target&&e.target.tagName||'').toLowerCase();if(tag==='input'||tag==='textarea'||(e.target&&e.target.isContentEditable))return;var items=e.clipboardData&&e.clipboardData.files;if(items&&items.length)transferImage(items)});
  var panel=document.getElementById('cist-mega-v2-panel');if(panel)panel.remove();panel=document.createElement('section');panel.id='cist-mega-v2-panel';panel.setAttribute('aria-live','polite');
  panel.innerHTML='<div class="cist-mega-v2-shell"><div class="cist-mega-v2-head"><div><span class="cist-mega-v2-kicker">Mega Scanner evidence</span><h3 id="cist-mega-headline">What the evidence says</h3></div><span id="cist-mega-confidence" class="cist-mega-v2-confidence">Confidence —</span></div><div class="cist-mega-v2-body"><div id="cist-mega-brand-wrap"></div><div class="cist-mega-v2-section"><div class="cist-mega-v2-label">Why</div><ul id="cist-mega-reasons" class="cist-mega-reasons"></ul></div><div class="cist-mega-v2-section"><div class="cist-mega-v2-label">Evidence chain</div><div id="cist-mega-chain" class="cist-mega-evidence-chain"></div></div><div class="cist-mega-v2-section"><div class="cist-mega-v2-label">What to do</div><div id="cist-mega-action" class="cist-mega-action"></div></div><div class="cist-mega-v2-section"><div class="cist-mega-v2-label">Could not verify</div><ul id="cist-mega-limits" class="cist-mega-limits"></ul></div><div class="cist-mega-share-row"><button id="cist-mega-share" class="cist-mega-share" type="button">Share result</button><span class="cist-mega-share-note">The shared link excludes the original message, full email addresses, phone numbers and crypto addresses.</span></div></div></div>';
  var anchor=imageAnalysis||result||form;anchor.insertAdjacentElement('afterend',panel);
  function safeNode(n){if(!n)return'';var type=clean(n.type),value=clean(n.value);if(type==='phone')return'Phone number';if(type==='crypto')return'Crypto address';if(type==='email'&&!/^Email on /i.test(value))return'Email detected';if(type==='social')return value||'Social profile';return value||cap(type)}
  function renderChain(graph){var chain=document.getElementById('cist-mega-chain');if(!chain)return;var nodes=(graph&&graph.nodes)||[],edges=(graph&&graph.edges)||[],map={};nodes.forEach(function(n){map[n.id]=n});var selected=[];var relations=['claims_identity','contains','resolves_to','uses_domain','links_to','redirects_to','cross_checked'];edges.forEach(function(e){if(selected.length>=4)return;if(relations.indexOf(e.relation)<0)return;var a=map[e.from],b=map[e.to];if(!a||!b||a.type==='input'&&b.type==='check')return;selected.push([a,b,e.relation])});if(!selected.length){nodes.filter(function(n){return n.type!=='input'&&n.type!=='check'}).slice(0,4).forEach(function(n){selected.push([null,n,''])})}var html='',used={};selected.forEach(function(pair){var a=pair[0],b=pair[1],rel=pair[2];if(a&&a.type!=='input'&&!used[a.id]){html+='<span class="cist-mega-node">'+esc(safeNode(a))+'</span><span class="cist-mega-arrow">→</span>';used[a.id]=1}if(b&&!used[b.id]){html+='<span class="cist-mega-node">'+esc(safeNode(b))+'</span>';used[b.id]=1;if(rel&&rel!=='contains')html+='<span class="cist-mega-arrow" title="'+esc(rel.replace(/_/g,' '))+'">·</span>'}});chain.innerHTML=html||'<span class="cist-mega-node">Evidence extracted automatically</span>'}
  function renderMega(d){if(!d||!d.explanation||!d.megaScanner)return;window.cistMegaLastResult=d;var ex=d.explanation||{},head=document.getElementById('cist-mega-headline'),conf=document.getElementById('cist-mega-confidence'),reasons=document.getElementById('cist-mega-reasons'),action=document.getElementById('cist-mega-action'),limits=document.getElementById('cist-mega-limits'),brand=document.getElementById('cist-mega-brand-wrap');if(head)head.textContent=ex.headline||'What the evidence says';if(conf){var x=ex.confidence||{};conf.textContent='Confidence '+cap(x.level||'unknown')+(typeof x.score==='number'?' · '+Math.round(x.score*100)+'%':'')};if(reasons){var rs=Array.isArray(ex.reasons)?ex.reasons.slice(0,4):[];reasons.innerHTML=rs.map(function(r){return '<li><strong>'+esc(r.title||'Signal')+'</strong><span>'+esc(r.detail||'')+'</span></li>'}).join('')||'<li><span>No additional correlated warning was found.</span></li>'}if(action)action.textContent=ex.action||'';if(limits){var ls=Array.isArray(ex.couldNotVerify)?ex.couldNotVerify:[];limits.innerHTML=ls.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')}if(brand){var items=d.brandMismatch&&Array.isArray(d.brandMismatch.items)?d.brandMismatch.items:[];brand.innerHTML=items.length?'<div class="cist-mega-brand-alert"><strong>Identity mismatch:</strong> '+esc(items[0].detail||'The claimed brand does not match the observed domain.')+'</div>':''}renderChain(d.evidenceGraph);panel.classList.add('cist-show')}
  var baseFetch=window.fetch.bind(window);window.fetch=async function(){var args=arguments,scanStarted=performance.now(),res=await baseFetch.apply(window,args);try{var target=typeof args[0]==='string'?args[0]:(args[0]&&args[0].url)||'';if(String(target).indexOf('/api/analyze')>=0){res.clone().json().then(function(d){if(!res.ok||!d||d.error)return;d.scanDurationMs=Math.max(1,performance.now()-scanStarted);try{d.counterSkip=JSON.parse(args[1]&&args[1].body||'{}').externalConsent===true}catch(_){}try{renderMega(d)}finally{document.dispatchEvent(new CustomEvent('cist:mega-result',{detail:d}))}}).catch(function(){})}}catch(e){}return res};
  input.addEventListener('input',function(){panel.classList.remove('cist-show')});
  function bytesToBase64Url(bytes){var s='';for(var i=0;i<bytes.length;i++)s+=String.fromCharCode(bytes[i]);return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
  function base64UrlToBytes(s){s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';var raw=atob(s),out=new Uint8Array(raw.length);for(var i=0;i<raw.length;i++)out[i]=raw.charCodeAt(i);return out}
  function encodeShare(obj){return bytesToBase64Url(new TextEncoder().encode(JSON.stringify(obj)))}
  function decodeShare(token){return JSON.parse(new TextDecoder().decode(base64UrlToBytes(token)))}
  function makeShareUrl(summary){var payload={...summary,sharedAt:new Date().toISOString()};return location.origin+'/#r='+encodeShare(payload)}
  var share=document.getElementById('cist-mega-share');if(share)share.addEventListener('click',async function(){var d=window.cistMegaLastResult;if(!d||!d.shareSummary)return;var url=makeShareUrl(d.shareSummary),text=(d.shareSummary.headline||'Can I Share This? scan result')+' '+url;try{if(navigator.share){await navigator.share({title:'Can I Share This? scan result',text:d.shareSummary.headline||'Shared safety scan',url:url});share.textContent='Shared'}else if(navigator.clipboard){await navigator.clipboard.writeText(url);share.textContent='Link copied'}else{throw new Error('clipboard unavailable')}}catch(e){try{if(navigator.clipboard){await navigator.clipboard.writeText(text);share.textContent='Link copied'}}catch(_){share.textContent='Copy unavailable'}}setTimeout(function(){share.textContent='Share result'},1800)});
  var shared=document.getElementById('cist-shared-result');if(shared)shared.remove();shared=document.createElement('section');shared.id='cist-shared-result';kicker.insertAdjacentElement('beforebegin',shared);
  function renderShared(payload){if(!payload||payload.schema!==1)return;var reasons=Array.isArray(payload.reasons)?payload.reasons.slice(0,3):[];shared.innerHTML='<div class="cist-shared-shell"><span class="cist-mega-v2-kicker">Shared scan summary</span><h3>'+esc(payload.headline||'Shared Can I Share This? result')+'</h3><p>This is a privacy-filtered summary from another scan. It is not a live verification and the fragment can be modified, so run a fresh scan before relying on it.</p><span class="cist-shared-risk">'+esc(payload.verdict||'unknown')+' · '+esc(payload.confidence||'unknown')+' confidence</span><ul class="cist-shared-reasons">'+reasons.map(function(r){return '<li><strong>'+esc(r.title||'Signal')+':</strong> '+esc(r.detail||'')+'</li>'}).join('')+'</ul><p class="cist-shared-action">'+esc(payload.action||'Verify independently before acting.')+'</p><button id="cist-shared-fresh" class="cist-mega-share cist-shared-fresh" type="button">Run a fresh scan</button></div>';shared.classList.add('cist-show');var fresh=document.getElementById('cist-shared-fresh');if(fresh)fresh.addEventListener('click',function(){history.replaceState(null,'',location.pathname+location.search);shared.classList.remove('cist-show');input.focus()})}
  try{var m=location.hash.match(/^#r=([A-Za-z0-9_-]+)$/);if(m)renderShared(decodeShare(m[1]))}catch(e){history.replaceState(null,'',location.pathname+location.search)}
})();
</script>
'''

def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    source = re.sub(r'\s*<style id="cist-mega-scanner-v2-style">.*?</style>', '', source, count=1, flags=re.S)
    source = re.sub(r'\s*<script id="cist-mega-scanner-v2-script">.*?</script>', '', source, count=1, flags=re.S)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source = source.replace('</head>', STYLE + '\n</head>', 1)
    source = source.replace('</body>', SCRIPT + '\n</body>', 1)
    required = ['cist-mega-scanner-v2-style','Upload or paste a screenshot','Evidence chain','Share result','Shared scan summary','/api/analyze']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Mega Scanner V2 guard failed: missing {token}')
    HOME.write_text(source, encoding='utf-8')
    print('Applied Mega Scanner V2 evidence, screenshot-first and shareable-result UI')

if __name__ == '__main__':
    main()
