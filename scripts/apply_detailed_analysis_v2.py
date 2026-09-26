#!/usr/bin/env python3
"""Add a progressive Detailed Analysis V2 below the compact result.

The summary result stays decision-first. This layer exposes observed evidence,
redirects, response/domain data and advanced technical fields without turning
missing checks into positive safety claims.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "dist" / "index.html"

STYLE = r'''
<style id="cist-detailed-analysis-v2-style">
/* V2 replaces the old always-open technical block. */
#technical{display:none!important}
body.cist-visible-tech-result #technical{display:none!important}

#cist-detail-v2{display:none;margin:14px 0 4px;border:1px solid var(--line);border-radius:16px;background:color-mix(in srgb,var(--card) 95%,transparent);overflow:hidden}
#cist-detail-v2.cist-ready{display:block}
#cist-detail-v2>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:14px;padding:15px 16px;cursor:pointer;user-select:none}
#cist-detail-v2>summary::-webkit-details-marker{display:none}
.cist-detail-v2-summary-copy{min-width:0}
.cist-detail-v2-summary-copy strong{display:block;color:var(--text);font-size:13px;font-weight:900;line-height:1.25}
.cist-detail-v2-summary-copy small{display:block;margin-top:3px;color:var(--muted);font-size:9.5px;line-height:1.4}
.cist-detail-v2-toggle{flex:0 0 auto;color:var(--cist-accent,#788ff7);font-size:10px;font-weight:900;white-space:nowrap}
#cist-detail-v2[open]>summary{border-bottom:1px solid var(--line)}
.cist-detail-v2-body{padding:0 16px 16px}
.cist-detail-v2-section{padding:16px 0 0}
.cist-detail-v2-section+.cist-detail-v2-section{margin-top:16px;border-top:1px solid var(--line)}
.cist-detail-v2-kicker{margin:0 0 9px;color:var(--muted);font-size:9px;font-weight:950;letter-spacing:.08em;text-transform:uppercase}
.cist-detail-v2-title{margin:0 0 4px;color:var(--text);font-size:14px;font-weight:950;line-height:1.25}
.cist-detail-v2-desc{margin:0 0 12px;color:var(--muted);font-size:10px;line-height:1.5}

.cist-detail-v2-evidence{display:grid;gap:9px}
.cist-detail-v2-evidence-group{padding:12px;border:1px solid var(--line);border-radius:13px;background:color-mix(in srgb,var(--soft) 36%,transparent)}
.cist-detail-v2-evidence-head{display:flex;align-items:center;gap:7px;margin:0 0 7px;color:var(--text);font-size:10px;font-weight:900}
.cist-detail-v2-dot{width:8px;height:8px;border-radius:50%;background:var(--muted)}
.cist-detail-v2-evidence-group[data-tone="pass"] .cist-detail-v2-dot{background:var(--green,#64c99d)}
.cist-detail-v2-evidence-group[data-tone="attention"] .cist-detail-v2-dot{background:var(--amber,#e7b45b)}
.cist-detail-v2-evidence-group[data-tone="unknown"] .cist-detail-v2-dot{background:var(--muted)}
.cist-detail-v2-list{display:grid;gap:7px;margin:0;padding:0;list-style:none}
.cist-detail-v2-list li{display:grid;grid-template-columns:16px minmax(0,1fr);gap:7px;align-items:start;color:var(--text);font-size:10.5px;line-height:1.4}
.cist-detail-v2-list .mark{font-weight:950;text-align:center}
.cist-detail-v2-list li[data-tone="pass"] .mark{color:var(--green,#64c99d)}
.cist-detail-v2-list li[data-tone="attention"] .mark{color:var(--amber,#e7b45b)}
.cist-detail-v2-list li[data-tone="unknown"] .mark{color:var(--muted)}
.cist-detail-v2-list b{font-weight:850}
.cist-detail-v2-list span.detail{display:block;margin-top:1px;color:var(--muted);font-size:9.5px}

.cist-detail-v2-chain{display:grid;gap:0;margin-top:9px}
.cist-detail-v2-chain-row{position:relative;display:grid;grid-template-columns:20px minmax(0,1fr);gap:9px;padding:0 0 12px}
.cist-detail-v2-chain-row:last-child{padding-bottom:0}
.cist-detail-v2-chain-rail{position:relative;display:flex;justify-content:center}
.cist-detail-v2-chain-rail:after{content:"";position:absolute;top:13px;bottom:-2px;width:1px;background:var(--line)}
.cist-detail-v2-chain-row:last-child .cist-detail-v2-chain-rail:after{display:none}
.cist-detail-v2-chain-node{position:relative;z-index:1;width:9px;height:9px;margin-top:3px;border:2px solid var(--card);border-radius:50%;background:var(--cist-accent,#788ff7);box-shadow:0 0 0 1px var(--line)}
.cist-detail-v2-chain-copy{min-width:0}
.cist-detail-v2-chain-copy small{display:block;color:var(--muted);font-size:8.5px;font-weight:850;text-transform:uppercase;letter-spacing:.05em}
.cist-detail-v2-chain-copy code{display:block;margin-top:2px;color:var(--text);font:700 10.5px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere;white-space:normal}
.cist-detail-v2-chain-copy span{display:block;margin-top:2px;color:var(--muted);font-size:9px}

.cist-detail-v2-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.cist-detail-v2-cell{min-width:0;padding:10px 11px;border:1px solid var(--line);border-radius:11px;background:color-mix(in srgb,var(--soft) 36%,transparent)}
.cist-detail-v2-cell small{display:block;color:var(--muted);font-size:8px;font-weight:900;letter-spacing:.055em;text-transform:uppercase}
.cist-detail-v2-cell strong{display:block;margin-top:3px;color:var(--text);font-size:10.5px;line-height:1.35;overflow-wrap:anywhere}

.cist-detail-v2-limit{padding:12px 13px;border-left:3px solid color-mix(in srgb,var(--cist-accent,#788ff7) 72%,var(--line));border-radius:0 11px 11px 0;background:color-mix(in srgb,var(--cist-accent,#788ff7) 6%,var(--soft));color:var(--muted);font-size:9.5px;line-height:1.5}
.cist-detail-v2-limit strong{color:var(--text)}

#cist-detail-v2-advanced{margin-top:12px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--soft) 30%,transparent);overflow:hidden}
#cist-detail-v2-advanced>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 12px;cursor:pointer;color:var(--text);font-size:10px;font-weight:900}
#cist-detail-v2-advanced>summary::-webkit-details-marker{display:none}
.cist-detail-v2-advanced-body{padding:0 12px 12px}
.cist-detail-v2-provider{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid var(--line);font-size:9.5px}
.cist-detail-v2-provider:first-child{border-top:0}
.cist-detail-v2-provider span:first-child{color:var(--text);font-weight:800}
.cist-detail-v2-provider span:last-child{color:var(--muted);text-align:right}
.cist-detail-v2-provider .good{color:var(--green,#64c99d)!important}
.cist-detail-v2-provider .bad{color:var(--red,#ef6a70)!important}
.cist-detail-v2-provider .warn{color:var(--amber,#e7b45b)!important}

@media(max-width:640px){
 #cist-detail-v2>summary{align-items:flex-start;padding:14px}
 .cist-detail-v2-body{padding:0 14px 14px}
 .cist-detail-v2-grid{grid-template-columns:1fr}
 .cist-detail-v2-toggle{padding-top:1px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-detailed-analysis-v2-script">
(function(){
  var input=document.getElementById('url');
  var result=document.getElementById('result');
  var card=document.getElementById('result-card');
  if(!input||!result||!card)return;

  var lastMega=null,lastScan=null,lastDeep=null,lastDomainAge=null;

  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function route(resource){try{return new URL(typeof resource==='string'?resource:(resource&&resource.url)||'',location.href).pathname}catch(e){return''}}
  function scanData(){return lastScan||window.cistUniversalResultData||lastMega||{}}
  function isUrlData(d){return d&&typeof d==='object'&&(d.detectedType==='url'||d.finalUrl||d.finalHost||Array.isArray(d.redirects))}
  function isUrlResult(){var d=scanData();return isUrlData(d)||/^https?:\/\//i.test(clean(input.value))}
  function unique(items){
    var seen={},out=[];
    (items||[]).forEach(function(x){if(!x)return;var key=clean((x.title||'')+'|'+(x.detail||'')).toLowerCase();if(!key||seen[key])return;seen[key]=1;out.push(x)});
    return out;
  }
  function safeUrl(v){
    try{var u=new URL(String(v||''));return u.origin+u.pathname+(u.search?'?…':'')}
    catch(e){return clean(v)}
  }
  function finalUrl(){var d=scanData();return clean(d.finalUrl)||(/^https?:\/\//i.test(clean(input.value))?clean(input.value):'')}
  function finalHost(){var d=scanData();if(clean(d.finalHost))return clean(d.finalHost);try{return new URL(finalUrl()).hostname}catch(e){return''}}
  function safetySignals(){
    var d=scanData(),a=d&&d.safety&&Array.isArray(d.safety.signals)?d.safety.signals:[],b=lastMega&&lastMega.explanation&&Array.isArray(lastMega.explanation.reasons)?lastMega.explanation.reasons:[];
    return unique(a.concat(b).map(function(x){return{title:clean(x.title)||'Observed signal',detail:clean(x.detail),severity:clean(x.severity).toLowerCase(),code:clean(x.code).toLowerCase()}}))
  }
  function hasSignal(pattern){
    return safetySignals().some(function(x){return pattern.test((x.code+' '+x.title+' '+x.detail).toLowerCase())})
  }
  function risk(){
    var d=lastMega||{},v=clean((d.megaScanner&&d.megaScanner.finalRisk)||(d.explanation&&d.explanation.verdict)||'').toLowerCase();
    if(v)return v;
    if(card.classList.contains('status-high'))return'high';
    if(card.classList.contains('status-caution'))return'caution';
    if(card.classList.contains('status-low'))return'low';
    return'unknown';
  }
  function identityLevel(){return clean(lastMega&&lastMega.identityConsistency&&lastMega.identityConsistency.level||'unknown').toLowerCase()}
  function providerState(p){
    if(!p)return{label:'Not checked',cls:''};
    if(p.dangerous||p.status==='known-threat'||p.status==='known-phishing')return{label:'Threat match',cls:'bad'};
    if(p.checked)return{label:'Checked · no match',cls:'good'};
    if(p.status==='unavailable'||p.status==='misconfigured')return{label:'Unavailable',cls:'warn'};
    return{label:'Not checked',cls:''};
  }
  function provider(name){
    var list=lastDeep&&Array.isArray(lastDeep.providers)?lastDeep.providers:[];
    for(var i=0;i<list.length;i++)if(list[i]&&list[i].provider===name)return list[i];
    return null;
  }
  function domainAge(){
    if(lastDomainAge&&Number.isFinite(lastDomainAge.ageDays)){
      var d=lastDomainAge.ageDays;
      if(d<60)return d+' days';
      if(d<730)return'About '+Math.max(2,Math.round(d/30))+' months';
      return'About '+Math.max(2,Math.round(d/365))+' years';
    }
    var el=document.getElementById('url-domain-age-value'),t=clean(el&&el.textContent);
    return t&&t!=='Checking registration age…'?t:'Not available';
  }
  function ensure(){
    var box=document.getElementById('cist-detail-v2');
    if(box)return box;
    var panel=document.getElementById('cist-mega-v2-panel'),body=panel&&panel.querySelector('.cist-mega-v2-body');
    if(!body)return null;
    box=document.createElement('details');
    box.id='cist-detail-v2';
    box.innerHTML=''+
      '<summary><span class="cist-detail-v2-summary-copy"><strong>Detailed analysis</strong><small>Evidence, redirects, response data and scan limits</small></span><span class="cist-detail-v2-toggle">View details ↓</span></summary>'+
      '<div class="cist-detail-v2-body">'+
        '<section class="cist-detail-v2-section" id="cist-detail-v2-evidence-section"><p class="cist-detail-v2-kicker">Evidence</p><h4 class="cist-detail-v2-title">What the scan observed</h4><p class="cist-detail-v2-desc">Observed signals are separated from checks that did not run or could not be established.</p><div id="cist-detail-v2-evidence" class="cist-detail-v2-evidence"></div></section>'+
        '<section class="cist-detail-v2-section" id="cist-detail-v2-chain-section"><p class="cist-detail-v2-kicker">Destination</p><h4 class="cist-detail-v2-title">Redirect chain</h4><p class="cist-detail-v2-desc">The route followed from the submitted URL to the final response.</p><div id="cist-detail-v2-chain" class="cist-detail-v2-chain"></div></section>'+
        '<section class="cist-detail-v2-section" id="cist-detail-v2-response-section"><p class="cist-detail-v2-kicker">Response</p><h4 class="cist-detail-v2-title">Domain & response</h4><div id="cist-detail-v2-grid" class="cist-detail-v2-grid"></div></section>'+
        '<section class="cist-detail-v2-section"><p class="cist-detail-v2-kicker">Limits</p><h4 class="cist-detail-v2-title">What this result does not mean</h4><div class="cist-detail-v2-limit"><strong>This is not a guarantee of safety.</strong> A legitimate site can be compromised, a new malicious page may have no known warning yet, and content can change after this scan. Identity and private account permissions are only reported when they can actually be established.</div>'+
        '<details id="cist-detail-v2-advanced"><summary><span>Advanced technical details</span><span>Open ↓</span></summary><div id="cist-detail-v2-advanced-body" class="cist-detail-v2-advanced-body"></div></details></section>'+
      '</div>';
    var explain=document.getElementById('cist-explain-v3');
    if(explain&&explain.parentNode===body)explain.insertAdjacentElement('afterend',box);else body.appendChild(box);
    box.addEventListener('toggle',function(){var t=box.querySelector('.cist-detail-v2-toggle');if(t)t.textContent=box.open?'Hide details ↑':'View details ↓'});
    var adv=box.querySelector('#cist-detail-v2-advanced');
    if(adv)adv.addEventListener('toggle',function(){var s=adv.querySelector('summary span:last-child');if(s)s.textContent=adv.open?'Close ↑':'Open ↓'});
    return box;
  }
  function itemHtml(x,tone){
    var mark=tone==='pass'?'✓':tone==='attention'?'!':'?';
    return '<li data-tone="'+tone+'"><span class="mark">'+mark+'</span><span><b>'+esc(x.title)+'</b>'+(x.detail?'<span class="detail">'+esc(x.detail)+'</span>':'')+'</span></li>';
  }
  function groupHtml(title,tone,items){
    if(!items.length)return'';
    return '<div class="cist-detail-v2-evidence-group" data-tone="'+tone+'"><div class="cist-detail-v2-evidence-head"><span class="cist-detail-v2-dot"></span><span>'+esc(title)+'</span></div><ul class="cist-detail-v2-list">'+items.slice(0,6).map(function(x){return itemHtml(x,tone)}).join('')+'</ul></div>';
  }
  function evidence(){
    var pass=[],attention=[],unknown=[],d=scanData(),sig=safetySignals(),urlResult=isUrlResult();

    if(lastMega){
      var positives=Array.isArray(lastMega.positiveEvidence)?lastMega.positiveEvidence:[],noWarnings=Array.isArray(lastMega.noWarningEvidence)?lastMega.noWarningEvidence:[];
      positives.concat(noWarnings).forEach(function(x){pass.push({title:clean(x.title)||'Observed evidence',detail:clean(x.detail)})});
    }

    sig.forEach(function(x){
      var target=(x.severity==='high'||x.severity==='medium'||x.severity==='warning'||x.severity==='caution')?attention:(x.severity==='low'?attention:unknown);
      target.push({title:x.title,detail:x.detail});
    });

    if(urlResult&&d&&d.status){
      var f=finalUrl();
      try{
        var protocol=new URL(f).protocol;
        if(protocol==='https:')pass.push({title:'HTTPS destination',detail:'The final observed URL uses HTTPS.'});
        else if(protocol==='http:')attention.push({title:'Unencrypted HTTP destination',detail:'The final observed URL does not use HTTPS.'});
      }catch(e){}

      var redirects=Array.isArray(d.redirects)?d.redirects:[];
      if(redirects.length)attention.push({title:redirects.length+' redirect'+(redirects.length===1?'':'s')+' followed',detail:'Redirects are not automatically malicious, but they change where the submitted URL ultimately goes.'});
      else pass.push({title:'No redirect observed',detail:'The submitted URL did not report an HTTP redirect before the final response.'});

      if(d.loginRequired===true)attention.push({title:'Login or access wall detected',detail:'The returned page showed a sign-in, permission or access-related signal.'});
      else if(d.loginRequired===false)pass.push({title:'No visible login wall detected',detail:'The public response did not expose an obvious sign-in or access-wall signal.'});

      if(!hasSignal(/brand-.*|lookalike/))pass.push({title:'No obvious brand-lookalike signal',detail:'The URL checks did not flag a recognized brand name on an unrelated hostname.'});
      if(!hasSignal(/executable-download/))pass.push({title:'No executable-download signal',detail:'The URL checks did not flag a direct executable-download pattern.'});
    }

    var id=identityLevel();
    if(id==='unknown'||id==='medium')unknown.push({title:'Destination identity not independently verified',detail:'Absence of a warning is not proof of who controls the site or account.'});

    if(!lastDeep)unknown.push({title:'External threat providers not run',detail:'Additional provider checks require the separate consent-based safety check.'});

    pass=unique(pass);attention=unique(attention);unknown=unique(unknown);
    return {pass:pass,attention:attention,unknown:unknown};
  }
  function renderEvidence(){
    var root=document.getElementById('cist-detail-v2-evidence');if(!root)return;
    var e=evidence();
    root.innerHTML=groupHtml('Observed without a major warning','pass',e.pass)+groupHtml('Needs attention or context','attention',e.attention)+groupHtml('Not established / not checked','unknown',e.unknown);
    if(!root.innerHTML)root.innerHTML=groupHtml('Not established / not checked','unknown',[{title:'Not enough evidence for detailed analysis',detail:'The available scan result did not expose additional structured evidence.'}]);
  }
  function renderChain(){
    var sec=document.getElementById('cist-detail-v2-chain-section'),root=document.getElementById('cist-detail-v2-chain');
    if(!sec||!root)return;
    var d=scanData(),redirects=d&&Array.isArray(d.redirects)?d.redirects:[];
    if(!isUrlResult()){sec.style.display='none';return}
    sec.style.display='';
    var rows=[],submitted=clean(input.value),final=finalUrl();
    if(/^https?:\/\//i.test(submitted))rows.push({label:'Submitted URL',url:safeUrl(submitted),meta:'Start'});
    redirects.forEach(function(r,i){rows.push({label:'Redirect '+(i+1),url:safeUrl(r&&r.url),meta:(r&&r.status?String(r.status)+' · ':'')+'HTTP redirect'})});
    if(final){
      var last=rows.length?rows[rows.length-1].url:'';
      if(!last||last!==safeUrl(final))rows.push({label:'Final destination',url:safeUrl(final),meta:(d.status?String(d.status)+' · ':'')+'Final response'});
      else if(rows.length)rows[rows.length-1].label='Final destination';
    }
    if(!rows.length)rows.push({label:'Destination',url:finalHost()||'Could not determine',meta:'No route data available'});
    root.innerHTML=rows.map(function(x){return '<div class="cist-detail-v2-chain-row"><div class="cist-detail-v2-chain-rail"><span class="cist-detail-v2-chain-node"></span></div><div class="cist-detail-v2-chain-copy"><small>'+esc(x.label)+'</small><code>'+esc(x.url)+'</code><span>'+esc(x.meta)+'</span></div></div>'}).join('');
  }
  function cell(label,value){
    if(value===undefined||value===null||value==='')return'';
    return '<div class="cist-detail-v2-cell"><small>'+esc(label)+'</small><strong>'+esc(value)+'</strong></div>';
  }
  function renderResponse(){
    var sec=document.getElementById('cist-detail-v2-response-section'),root=document.getElementById('cist-detail-v2-grid');
    if(!sec||!root)return;
    var d=scanData();
    if(!isUrlResult()){sec.style.display='none';return}
    sec.style.display='';
    var f=finalUrl(),https='Could not determine';
    try{https=new URL(f).protocol==='https:'?'Yes':'No'}catch(e){}
    var redirects=Array.isArray(d.redirects)?d.redirects.length:null;
    root.innerHTML=''+
      cell('Final host',finalHost()||'Could not determine')+
      cell('HTTP response',d.status||'Not reported')+
      cell('HTTPS',https)+
      cell('Redirects',redirects===null?'Not reported':String(redirects))+
      cell('Content type',clean(d.contentType)||'Not reported')+
      cell('Response time',Number.isFinite(d.responseMs)?d.responseMs+' ms':'Not reported')+
      cell('Login / access wall',d.loginRequired===true?'Detected':d.loginRequired===false?'Not detected':'Could not determine')+
      cell('Domain age',domainAge());
  }
  function advancedRow(label,state){
    return '<div class="cist-detail-v2-provider"><span>'+esc(label)+'</span><span class="'+esc(state.cls||'')+'">'+esc(state.label)+'</span></div>';
  }
  function renderAdvanced(){
    var root=document.getElementById('cist-detail-v2-advanced-body');if(!root)return;
    var d=scanData(),html='';
    html+=advancedRow('Google Web Risk',providerState(provider('Google Web Risk')));
    html+=advancedRow('PhishTank',providerState(provider('PhishTank')));
    if(Array.isArray(d.addresses)&&d.addresses.length){
      var ips=d.addresses.slice(0,3).map(function(x){return clean(x&&x.address)}).filter(Boolean).join(', ');
      if(ips)html+=advancedRow('Resolved IP'+(d.addresses.length>1?'s':''),{label:ips,cls:''});
    }
    var checks=d.safety&&Array.isArray(d.safety.checksPerformed)?d.safety.checksPerformed:[];
    if(checks.length)html+=advancedRow('Local checks performed',{label:checks.join(' · '),cls:''});
    html+=advancedRow('Identity verification',{label:(identityLevel()==='high'?'Supporting relationship evidence found':'Not independently established'),cls:identityLevel()==='high'?'good':''});
    root.innerHTML=html;
  }
  function render(){
    var box=ensure();if(!box||result.classList.contains('hidden'))return;
    renderEvidence();renderChain();renderResponse();renderAdvanced();
    box.classList.add('cist-ready');
    var old=document.getElementById('technical');if(old){old.open=false;old.removeAttribute('open');old.classList.add('hidden')}
    document.body.classList.remove('cist-visible-tech-result');
  }
  function reset(){
    lastMega=null;lastScan=null;lastDeep=null;lastDomainAge=null;
    var box=document.getElementById('cist-detail-v2');if(box){box.classList.remove('cist-ready');box.open=false}
    document.body.classList.remove('cist-visible-tech-result');
  }

  var originalFetch=window.fetch;
  if(typeof originalFetch==='function')window.fetch=function(resource,options){
    var path=route(resource);
    return originalFetch.apply(this,arguments).then(function(response){
      if(path==='/api/check'||path==='/api/analyze'||path==='/api/deep-check'||path==='/api/domain-age'){
        response.clone().json().then(function(data){
          if((path==='/api/check'||path==='/api/analyze')&&isUrlData(data))lastScan=data;
          else if(path==='/api/deep-check')lastDeep=data;
          else if(path==='/api/domain-age')lastDomainAge=data;
          setTimeout(render,0);
        }).catch(function(){});
      }
      return response;
    });
  };

  document.addEventListener('cist:mega-result',function(e){if(e.detail&&!e.detail.error){lastMega=e.detail;if(isUrlData(e.detail)&&!lastScan)lastScan=e.detail;setTimeout(render,0)}});
  document.addEventListener('cist:result-updated',function(){setTimeout(render,20)});

  var resetBtn=document.getElementById('cist-unified-reset'),again=document.getElementById('again');
  if(resetBtn)resetBtn.addEventListener('click',reset);
  if(again)again.addEventListener('click',reset);
  input.addEventListener('input',function(){if(!result.classList.contains('hidden'))reset()});

  new MutationObserver(function(){if(!result.classList.contains('hidden'))setTimeout(render,30)}).observe(card,{attributes:true,attributeFilter:['class']});
})();
</script>
'''

def main() -> None:
    if not HOME.is_file():
        raise RuntimeError("Homepage not found")
    source = HOME.read_text(encoding="utf-8")

    for marker in (
        "cist-detailed-analysis-v2-style",
        "cist-visible-technical-evidence-v1-style",
    ):
        source = re.sub(
            rf'\s*<style id="{re.escape(marker)}">.*?</style>',
            "",
            source,
            count=1,
            flags=re.S,
        )
    for marker in (
        "cist-detailed-analysis-v2-script",
        "cist-visible-technical-evidence-v1-script",
    ):
        source = re.sub(
            rf'\s*<script id="{re.escape(marker)}">.*?</script>',
            "",
            source,
            count=1,
            flags=re.S,
        )

    required_before = ("id=\"technical\"", "cist-mega-v2-panel", "cist:mega-result")
    for token in required_before:
        if token not in source:
            raise RuntimeError(f"Detailed Analysis V2 prerequisite missing: {token}")

    source = source.replace("</head>", STYLE + "\n</head>", 1)
    source = source.replace("</body>", SCRIPT + "\n</body>", 1)

    required_after = (
        "Detailed analysis",
        "What the scan observed",
        "Redirect chain",
        "Domain & response",
        "What this result does not mean",
        "Advanced technical details",
        "External threat providers not run",
        "This is not a guarantee of safety.",
        "cist-detailed-analysis-v2-script",
    )
    for token in required_after:
        if token not in source:
            raise RuntimeError(f"Detailed Analysis V2 guard failed: missing {token}")

    HOME.write_text(source, encoding="utf-8")
    print("Applied progressive Detailed Analysis V2")


if __name__ == "__main__":
    main()
