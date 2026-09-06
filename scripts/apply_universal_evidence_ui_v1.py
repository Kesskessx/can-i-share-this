#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/'dist'/'index.html'
if not HOME.is_file(): raise RuntimeError('Homepage not found')
s=HOME.read_text(encoding='utf-8')

STYLE=r'''
<style id="cist-universal-evidence-v1-style">
#cist-unified-home-scanner #choose-image{min-width:112px!important}
.cist-v4-coverage-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
.cist-v4-metric{padding:9px;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.cist-v4-metric span{display:block;color:var(--muted);font-size:8px;font-weight:850;text-transform:uppercase;letter-spacing:.06em}
.cist-v4-metric strong{display:block;margin-top:3px;font-size:11px;color:var(--text)}
.cist-v4-sources{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px}.cist-v4-source{padding:4px 7px;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:8.5px;font-weight:800}
.cist-v4-rep-summary{display:grid;gap:7px}.cist-v4-rep-row{display:flex;justify-content:space-between;gap:10px;padding:7px 0;border-bottom:1px solid color-mix(in srgb,var(--line) 70%,transparent);font-size:10.5px}.cist-v4-rep-row:last-child{border-bottom:0}.cist-v4-rep-status{font-weight:850;text-align:right}
#cist-v4-reputation-button{margin-top:9px;appearance:none;border:1px solid color-mix(in srgb,var(--cist-accent,#788ff7) 45%,var(--line));background:color-mix(in srgb,var(--cist-accent,#788ff7) 8%,var(--card));color:var(--text);border-radius:10px;padding:8px 10px;font:inherit;font-size:10px;font-weight:850;cursor:pointer}
#cist-v4-reputation-button:disabled{opacity:.55;cursor:default}
.cist-v4-privacy-note{margin-top:7px;color:var(--muted);font-size:8.8px;line-height:1.45}
.cist-v4-advanced details{border-top:1px solid var(--line);padding-top:8px;margin-top:8px}.cist-v4-advanced details:first-child{border-top:0;padding-top:0;margin-top:0}.cist-v4-advanced summary{cursor:pointer;font-size:10.5px;font-weight:850;color:var(--text)}
.cist-v4-detail-list{display:grid;gap:5px;margin-top:8px;font-size:9.5px;color:var(--muted)}.cist-v4-detail-list b{color:var(--text)}
.cist-v4-file-loading{display:flex;gap:10px;align-items:center}.cist-v4-file-loading strong{font-size:12px}.cist-v4-file-loading span{font-size:10px;color:var(--muted)}
@media(max-width:600px){.cist-v4-coverage-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.cist-v4-metric{padding:8px}.cist-v4-rep-row{align-items:flex-start}}
</style>
'''

SCRIPT=r'''
<script id="cist-universal-evidence-v1-script">
(function(){
  var choose=document.getElementById('choose-image'),imageFile=document.getElementById('image-file'),host=document.getElementById('cist-unified-home-scanner'),note=document.getElementById('cist-unified-home-note'),panel=document.getElementById('cist-mega-v2-panel'),imageBox=document.getElementById('image-analysis');
  if(!choose||!imageFile||!host)return;
  var MAX=3*1024*1024,lastPayload=null,uploading=false;
  var allowed=/\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|eml|txt|csv|rtf|exe|msi|msix|scr|bat|cmd|ps1|vbs|js|jar|apk|dmg|pkg|iso|img|hta|appinstaller|html?)$/i;
  var universal=document.createElement('input');universal.type='file';universal.id='cist-universal-file';universal.hidden=true;universal.accept='image/jpeg,image/png,image/webp,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.eml,.txt,.csv,.rtf,.exe,.msi,.msix,.scr,.bat,.cmd,.ps1,.vbs,.js,.jar,.apk,.dmg,.pkg,.iso,.img,.hta,.appinstaller,.html,.htm';host.appendChild(universal);
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function setLabel(){if(!uploading)choose.textContent='＋ Upload';choose.setAttribute('aria-label','Upload a screenshot, document, email or file to analyze')}
  setLabel();
  var badges=document.getElementById('cist-mega-badges');if(badges&&!Array.from(badges.children).some(function(x){return clean(x.textContent).toLowerCase()==='files'})){var b=document.createElement('span');b.textContent='Files';badges.appendChild(b)}
  function transferImage(f){try{var dt=new DataTransfer();dt.items.add(f);imageFile.files=dt.files;imageFile.dispatchEvent(new Event('change',{bubbles:true}));return true}catch(e){return false}}
  function readDataUrl(f){return new Promise(function(resolve,reject){var r=new FileReader();r.onload=function(){resolve(String(r.result||''))};r.onerror=function(){reject(new Error('The file could not be read.'))};r.readAsDataURL(f)})}
  function loadingFile(f){if(!imageBox)return;imageBox.className='image-analysis';imageBox.innerHTML='<div class="cist-v4-file-loading"><div class="image-analysis-icon">…</div><div><strong>Analyzing file…</strong><br><span>'+esc(f.name)+' · static analysis only · file is never executed</span></div></div>';imageBox.classList.remove('hidden')}
  function errorFile(msg){if(!imageBox)return;imageBox.className='image-analysis caution';imageBox.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">!</div><div><h3>File check unavailable</h3><p>'+esc(msg)+'</p></div></div>';imageBox.classList.remove('hidden')}
  async function analyzeFile(f){
    if(!f)return;if(/^image\/(jpeg|png|webp)$/i.test(f.type||'')){transferImage(f);return}
    if(f.size>MAX){errorFile('The file is too large. Maximum size for static file analysis is 3 MB.');return}
    if(!allowed.test(f.name||'')&&!/^(message\/rfc822|application\/pdf|application\/zip|text\/)/i.test(f.type||'')){errorFile('This file type is not supported yet.');return}
    uploading=true;choose.disabled=true;choose.textContent='Analyzing…';loadingFile(f);if(note)note.innerHTML='<strong>Static file analysis…</strong><span class="cist-dot">·</span><span>Hash · real type · structure · embedded links</span>';
    try{var data=await readDataUrl(f);var r=await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({file:{name:f.name||'upload.bin',mimeType:f.type||'application/octet-stream',data:data}})});var out=await r.json().catch(function(){return{}});if(!r.ok||out.error)throw new Error(out.error||('File analysis failed (HTTP '+r.status+').'));if(imageBox)imageBox.classList.add('hidden')}
    catch(e){errorFile(e&&e.message?e.message:'The file could not be analyzed.')}
    finally{uploading=false;choose.disabled=false;universal.value='';setLabel();if(note)note.innerHTML='<span>Private by design</span><span class="cist-dot">·</span><span>No account required</span><span class="cist-dot">·</span><span>Automatic type detection</span>'}
  }
  choose.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();universal.click()},true);
  universal.addEventListener('change',function(){analyzeFile(universal.files&&universal.files[0])});
  host.addEventListener('drop',function(e){var fs=e.dataTransfer&&e.dataTransfer.files;if(!fs||!fs.length)return;var f=fs[0];if(!/^image\//i.test(f.type||'')){e.preventDefault();e.stopImmediatePropagation();analyzeFile(f)}},true);
  document.addEventListener('cist:mega-result',function(){setTimeout(setLabel,0)});

  // Capture the latest /api/analyze request so the exact same evidence can be re-run after explicit external-consent.
  var previousFetch=window.fetch.bind(window);window.fetch=async function(){var args=arguments,target=typeof args[0]==='string'?args[0]:(args[0]&&args[0].url)||'';if(String(target).indexOf('/api/analyze')>=0){try{var opts=args[1]||{},body=opts.body&&JSON.parse(opts.body);if(body&&typeof body==='object')lastPayload=body}catch(_){}}return previousFetch.apply(window,args)};

  function ensureSection(id,label,afterId){
    var x=document.getElementById(id);if(x)return x;var body=panel&&panel.querySelector('.cist-mega-v2-body');if(!body)return null;x=document.createElement('div');x.id=id;x.className='cist-mega-v2-section';x.innerHTML='<div class="cist-mega-v2-label">'+label+'</div><div class="cist-v4-section-body"></div>';var after=document.getElementById(afterId);if(after&&after.parentNode===body)after.insertAdjacentElement('afterend',x);else body.insertBefore(x,body.firstChild);return x
  }
  function renderCoverage(d){var c=d.coverageMatrix;if(!c)return;var sec=ensureSection('cist-v4-coverage','Evidence coverage','cist-v3-positive');if(!sec)return;var body=sec.querySelector('.cist-v4-section-body'),ratio=Math.round(Number(c.ratio||0)*100);body.innerHTML='<div class="cist-v4-coverage-grid"><div class="cist-v4-metric"><span>Completed</span><strong>'+esc(c.completed)+' / '+esc(c.relevant)+'</strong></div><div class="cist-v4-metric"><span>Coverage</span><strong>'+ratio+'%</strong></div><div class="cist-v4-metric"><span>Independent</span><strong>'+esc(c.independentEvidenceCount||0)+'</strong></div><div class="cist-v4-metric"><span>Unresolved</span><strong>'+esc((c.pendingChecks||[]).length)+'</strong></div></div>'+(c.sources&&c.sources.length?'<div class="cist-v4-sources">'+c.sources.slice(0,10).map(function(x){return'<span class="cist-v4-source">'+esc(x)+'</span>'}).join('')+'</div>':'');var conf=document.getElementById('cist-mega-confidence');if(conf&&d.explanation&&d.explanation.confidence)conf.textContent='Confidence '+clean(d.explanation.confidence.level).replace(/^./,function(x){return x.toUpperCase()})+' · '+c.completed+'/'+c.relevant+' checks'}
  function repRows(d){var rep=d.externalReputation||{},rows=[];(rep.urlChecks||[]).forEach(function(x){var label=x.urlHost||'URL',status=x.dangerous?'Known threat':x.checked?'No known threat':x.privacyBlocked?'Privacy blocked':clean(x.status||'Unavailable');rows.push([label,status])});(rep.cryptoChecks||[]).forEach(function(x){rows.push(['Crypto activity',x.checked?'Public activity read':clean(x.status||'Unavailable')])});return rows}
  function renderReputation(d){var rep=d.externalReputation||{},sec=ensureSection('cist-v4-reputation','Independent reputation','cist-v4-coverage');if(!sec)return;var body=sec.querySelector('.cist-v4-section-body');if(!Number(rep.eligible||0)){sec.style.display='none';return}sec.style.display='block';if(!rep.consent){body.innerHTML='<div class="cist-v4-rep-summary"><div class="cist-v4-rep-row"><span>External reputation</span><span class="cist-v4-rep-status">Not checked</span></div></div><button id="cist-v4-reputation-button" type="button">Check external reputation</button><div class="cist-v4-privacy-note">This requires consent because detected URLs or public wallet addresses may be sent to external reputation/blockchain services. Sensitive URL parameters are blocked from external sharing.</div>';var btn=document.getElementById('cist-v4-reputation-button');if(btn)btn.onclick=async function(){if(!lastPayload)return;btn.disabled=true;btn.textContent='Checking…';try{var payload=JSON.parse(JSON.stringify(lastPayload));payload.externalConsent=true;await fetch('/api/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)})}catch(_){btn.disabled=false;btn.textContent='Try external reputation again'}};return}var rows=repRows(d);body.innerHTML='<div class="cist-v4-rep-summary">'+(rows.length?rows.map(function(x){return'<div class="cist-v4-rep-row"><span>'+esc(x[0])+'</span><span class="cist-v4-rep-status">'+esc(x[1])+'</span></div>'}).join(''):'<div class="cist-v4-rep-row"><span>External sources</span><span class="cist-v4-rep-status">Unavailable</span></div>')+'</div><div class="cist-v4-privacy-note">“No known threat” means no match was returned by the available source. It is not a guarantee of safety.</div>'}
  function renderAdvanced(d){var domains=d.domainIntelligence||[],pages=d.webpageChecks||[];if(!domains.length&&!pages.length&&!d.file&&!d.emailMessage)return;var sec=ensureSection('cist-v4-advanced','Technical evidence','cist-v4-reputation');if(!sec)return;sec.classList.add('cist-v4-advanced');var html='';domains.slice(0,4).forEach(function(x){var dns=x.dns||{},rdap=x.rdap||{},tls=x.tls||{};html+='<details><summary>'+esc(x.domain)+'</summary><div class="cist-v4-detail-list"><div><b>Domain age:</b> '+esc(rdap.ageDays==null?'unknown':rdap.ageDays+' days')+'</div><div><b>Mail/DNS:</b> MX '+(dns.hasMx?'yes':'no')+' · SPF '+(dns.hasSpf?'yes':'no')+' · DMARC '+(dns.hasDmarc?(dns.dmarcPolicy||'yes'):'no')+' · DNSSEC '+(dns.hasDnssec?'yes':'no')+'</div><div><b>TLS:</b> '+esc(tls.checked?(tls.authorized?'certificate validated':'certificate not validated'):'not available')+'</div>'+(dns.nameServers&&dns.nameServers.length?'<div><b>Name servers:</b> '+esc(dns.nameServers.slice(0,3).join(', '))+'</div>':'')+'</div></details>'});pages.slice(0,3).forEach(function(x){if(!x.checked)return;var p=x.page||{};html+='<details><summary>Webpage structure · '+esc((new URL(x.finalUrl||'https://example.invalid')).hostname)+'</summary><div class="cist-v4-detail-list"><div><b>Password field:</b> '+(p.hasPasswordField?'yes':'no')+' · <b>Payment field:</b> '+(p.hasPaymentField?'yes':'no')+'</div><div><b>External iframes:</b> '+esc((p.externalIframeHosts||[]).length)+'</div><div><b>Findings:</b> '+esc((x.findings||[]).length)+'</div></div></details>'});if(d.file){html+='<details><summary>Uploaded file</summary><div class="cist-v4-detail-list"><div><b>Real type:</b> '+esc(d.file.actualMime||'unknown')+'</div><div><b>SHA-256:</b> '+esc((d.file.sha256||'').slice(0,16))+'…</div><div><b>Size:</b> '+esc(d.file.size||0)+' bytes</div></div></details>'}if(d.emailMessage){var a=d.emailMessage.authentication||{};html+='<details><summary>Email authentication</summary><div class="cist-v4-detail-list"><div><b>SPF:</b> '+esc(a.spf||'unknown')+' · <b>DKIM:</b> '+esc(a.dkim||'unknown')+' · <b>DMARC:</b> '+esc(a.dmarc||'unknown')+'</div><div><b>Received hops:</b> '+esc(d.emailMessage.receivedHops||0)+'</div></div></details>'}sec.querySelector('.cist-v4-section-body').innerHTML=html}
  document.addEventListener('cist:mega-result',function(e){var d=e.detail||{};try{renderCoverage(d);renderReputation(d);renderAdvanced(d);if(imageBox&&d.detectedType==='file')imageBox.classList.add('hidden')}catch(_){}});
})();
</script>
'''

s=re.sub(r'\s*<style id="cist-universal-evidence-v1-style">.*?</style>','',s,count=1,flags=re.S)
s=re.sub(r'\s*<script id="cist-universal-evidence-v1-script">.*?</script>','',s,count=1,flags=re.S)
if 'cist-unified-home-scanner-v1-script' not in s or 'cist-mega-scanner-v5-script' not in s: raise RuntimeError('Required scanner UI is missing')
s=s.replace('</head>',STYLE+'\n</head>',1).replace('</body>',SCRIPT+'\n</body>',1)
for token in ['Evidence coverage','Check external reputation','cist-universal-file','Static file analysis']:
    if token not in s: raise RuntimeError('Universal evidence UI guard failed: '+token)
HOME.write_text(s,encoding='utf-8')
print('Applied universal evidence upload, coverage and reputation UI')
