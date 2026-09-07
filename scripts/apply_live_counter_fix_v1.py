#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

if not HOME.is_file():
    raise RuntimeError('Homepage not found')

s = HOME.read_text(encoding='utf-8')

# The old counters were bound to the legacy result event. Mega Scanner now emits
# cist:mega-result for every /api/analyze response, including screenshots.
legacy_count = "document.addEventListener('cist:result-updated',countOnce);"
if legacy_count not in s:
    raise RuntimeError('Legacy homepage counter listener not found')
s = s.replace(legacy_count, "document.addEventListener('cist:result-updated',function(){});", 1)

# Keep the existing rails as read-only renderers/pollers. A single controller below
# records totals, duration and signal metrics so one scan cannot be double-counted.
old_daily = "form.addEventListener('submit',function(){startedAt=Date.now();metricsSent=false},true);"
if old_daily not in s:
    raise RuntimeError('Legacy daily metric submit hook not found')
s = s.replace(old_daily, "form.addEventListener('submit',function(){metricsSent=true},true);", 1)

old_signal = "form.addEventListener('submit',function(){signalSent=false},true);"
if old_signal not in s:
    raise RuntimeError('Legacy signal metric submit hook not found')
s = s.replace(old_signal, "form.addEventListener('submit',function(){signalSent=true},true);", 1)

s = re.sub(r'\s*<script id="cist-live-counter-fix-v1-script">.*?</script>', '', s, count=1, flags=re.S)

SCRIPT = r'''
<script id="cist-live-counter-fix-v1-script">
(function(){
  var form=document.getElementById('scan-form');
  var file=document.getElementById('image-file');
  var startedAt=0,lastRecordedAt=0,recording=false;
  var typeLabels={link:'URL',qr:'QR code',email:'Email',file:'File',shortlink:'Short link',crypto:'Crypto',message:'Message',social:'Social profile',other:'Other'};

  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim().toLowerCase()}
  function start(){startedAt=(window.performance&&performance.now)?performance.now():Date.now()}
  if(form)form.addEventListener('submit',start,true);
  if(file)file.addEventListener('change',function(){if(file.files&&file.files.length)start()},true);

  function arrays(d){
    var el=d&&d.detectedElements||{},a=d&&d.analysis||{};
    return {
      social:(el.socialProfiles||[]).length||!!a.social_profile,
      qr:(el.qr||[]).length||(a.qr_values||[]).length,
      crypto:(el.crypto||[]).length,
      email:(el.emails||[]).length||(a.emails||[]).length,
      file:(el.files||[]).length,
      url:(el.urls||[]).length||(el.domains||[]).length||(a.urls||[]).length
    }
  }
  function resultType(d){
    var t=clean(d&&d.detectedType||d&&d.inputType);
    if(t==='social-profile')return'social';
    if(t==='url')return'link';
    if(t==='email')return'email';
    if(t==='crypto')return'crypto';
    if(t==='message'||t==='message-url'||t==='message-email')return'message';
    if(t==='image'){
      var x=arrays(d);
      if(x.social)return'social';
      if(x.qr)return'qr';
      if(x.crypto)return'crypto';
      if(x.email)return'email';
      if(x.file)return'file';
      if(x.url)return'link';
      return'message';
    }
    return ['link','qr','email','file','shortlink','crypto','message','social','other'].indexOf(t)>=0?t:'other';
  }
  function resultRisk(d){
    var r=clean(d&&d.megaScanner&&d.megaScanner.finalRisk||d&&d.explanation&&d.explanation.verdict||d&&d.analysis&&d.analysis.risk||d&&d.safety&&d.safety.status);
    return ['low','caution','high'].indexOf(r)>=0?r:'unknown';
  }
  function signalFlags(d){
    var codes=[],parts=[];
    var sig=d&&d.safety&&Array.isArray(d.safety.signals)?d.safety.signals:[];
    sig.forEach(function(x){codes.push(clean(x&&x.code));parts.push(clean((x&&x.title||'')+' '+(x&&x.detail||'')))});
    var as=d&&d.analysis&&Array.isArray(d.analysis.suspicious_signals)?d.analysis.suspicious_signals:[];
    as.forEach(function(x){parts.push(clean((x&&x.type||'')+' '+(x&&x.detail||'')))});
    var cs=Array.isArray(d&&d.correlations)?d.correlations:[];
    cs.forEach(function(x){parts.push(clean((x&&x.title||'')+' '+(x&&x.detail||'')))});
    var text=parts.join(' '),has=function(c){return codes.indexOf(c)>=0},starts=function(p){return codes.some(function(c){return c.indexOf(p)===0})};
    var redirects=Array.isArray(d&&d.redirects)?d.redirects.length:0;
    var files=d&&d.detectedElements&&Array.isArray(d.detectedElements.files)?d.detectedElements.files:[];
    var riskyFile=files.some(function(x){return /\.(exe|msi|msix|scr|bat|cmd|ps1|vbs|jar|apk|dmg|pkg|iso|hta|appinstaller)(?:$|\s)/i.test(String(x||''))});
    return {
      redirected:redirects>0||has('domain-change')||/suspicious redirect|redirect chain/.test(text),
      phishing:has('phishing-language')||starts('brand-')||/\bphishing\b|credential theft|fake login/.test(text),
      lookalike:!!(d&&d.brandMismatch&&d.brandMismatch.detected)||has('punycode')||/lookalike|look-alike|homoglyph|brand.?domain mismatch/.test(text),
      riskyDownload:riskyFile||has('executable-download')||has('binary-content')||has('forced-download')||has('archive-download')||/risky download|malicious file/.test(text)
    };
  }
  function request(payload){
    var opts={cache:'no-store'};
    if(payload){opts.method='POST';opts.headers={'content-type':'application/json'};opts.body=JSON.stringify(payload)}
    return fetch('/api/counter',opts).then(function(r){if(!r.ok)throw new Error('counter');return r.json()});
  }
  function topType(by){var best='',count=0;Object.keys(by||{}).forEach(function(k){var n=Number(by[k]||0);if(n>count){count=n;best=k}});return count>0?(typeLabels[best]||best):'—'}
  function formatTime(ms){ms=Number(ms);if(!Number.isFinite(ms)||ms<=0)return'—';if(ms<1000)return Math.round(ms)+' ms';return (ms/1000).toFixed(ms<10000?1:0)+' s'}
  function paint(data){
    if(!data)return;var d=data.daily||{},by=d.byType||{},ss=d.signals||{};
    var set=function(id,v){var el=document.getElementById(id);if(el)el.textContent=v};
    set('cist-daily-scans',Number(d.total||0).toLocaleString());
    set('cist-daily-warnings',Number(d.warnings||0).toLocaleString());
    set('cist-daily-average',formatTime(d.averageMs));
    set('cist-daily-type',topType(by));
    set('cist-signal-total',Number(d.signalTotal||0).toLocaleString());
    set('cist-signal-redirect',Number(ss.redirect||0).toLocaleString());
    set('cist-signal-phishing',Number(ss.phishing||0).toLocaleString());
    set('cist-signal-lookalike',Number(ss.lookalike||0).toLocaleString());
    set('cist-signal-download',Number(ss.risky_download||0).toLocaleString());
    set('cist-total-checks',Number(data.total||0).toLocaleString());
    var dl=document.getElementById('cist-daily-live');if(dl)dl.textContent=data.persistent===false?'Session':'Live';
    var sl=document.getElementById('cist-signal-live');if(sl)sl.textContent=data.persistent===false?'Session':'Today';
  }
  async function record(d){
    if(!d||d.error||d.counterSkip)return;
    recording=true;
    var type=resultType(d),risk=resultRisk(d),f=signalFlags(d);
    var end=(window.performance&&performance.now)?performance.now():Date.now();
    var duration=Number(d.scanDurationMs)>0?Number(d.scanDurationMs):(startedAt?Math.max(1,end-startedAt):null);
    try{
      var first=await request({type:type});paint(first);
      var second=await request({metricsOnly:true,warning:risk==='high'||risk==='caution',durationMs:duration,redirected:f.redirected,phishing:f.phishing,lookalike:f.lookalike,riskyDownload:f.riskyDownload});paint(second);
    }catch(e){}finally{startedAt=0;recording=false}
  }
  var recordQueue=Promise.resolve();
  document.addEventListener('cist:mega-result',function(e){var data=e.detail||{};recordQueue=recordQueue.then(function(){return record(data)}).catch(function(){})});
  // Legacy runScan uses a variable endpoint, so the build's literal fetch
  // replacement does not route these requests through the Mega result event.
  // Observe successful primary responses only; enrichment requests do not count.
  var previousCounterFetch=window.fetch.bind(window);
  window.fetch=async function(resource,options){
    var target=typeof resource==='string'?resource:resource&&resource.url;
    var path='';try{var parsed=new URL(target,location.href);if(parsed.origin===location.origin)path=parsed.pathname}catch(_){}
    var legacyTypes={'/api/check':'link','/api/email-check':'email','/api/crypto-check':'crypto','/api/image-check':'image'};
    var response=await previousCounterFetch.apply(window,arguments);
    if(legacyTypes[path]&&response.ok){
      response.clone().json().then(function(data){
        if(!data||data.error)return;
        record(Object.assign({},data,{detectedType:data.detectedType||legacyTypes[path]}));
      }).catch(function(){});
    }
    return response;
  };
  request().then(paint).catch(function(){});
})();
</script>
'''

if '</body>' not in s:
    raise RuntimeError('Invalid homepage HTML')
s = s.replace('</body>', SCRIPT + '\n</body>', 1)

for token in ['cist-live-counter-fix-v1-script', "document.addEventListener('cist:mega-result'", "cist-signal-phishing", "metricsOnly:true"]:
    if token not in s:
        raise RuntimeError('Live counter fix guard failed: ' + token)

HOME.write_text(s, encoding='utf-8')
print('Fixed live counters for all Mega Scanner result types')
