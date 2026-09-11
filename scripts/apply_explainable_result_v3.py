#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-explainable-result-v3-style">
#cist-explain-v3{display:none;margin:12px 0 4px;padding:14px;border:1px solid var(--line);border-radius:16px;background:color-mix(in srgb,var(--card) 92%,transparent)}
#cist-explain-v3.cist-show{display:block}
.cist-explain-v3-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:11px}
.cist-explain-v3-title{margin:0;font-size:14px;font-weight:950;letter-spacing:-.015em;color:var(--text)}
.cist-explain-v3-sub{margin:3px 0 0;color:var(--muted);font-size:10.5px;line-height:1.4}
.cist-explain-v3-badge{flex:0 0 auto;padding:6px 9px;border:1px solid var(--line);border-radius:999px;font-size:9px;font-weight:950;text-transform:uppercase;letter-spacing:.06em}
.cist-explain-v3-badge[data-risk="high"]{color:var(--red);border-color:color-mix(in srgb,var(--red) 45%,var(--line));background:color-mix(in srgb,var(--red) 8%,var(--card))}
.cist-explain-v3-badge[data-risk="caution"]{color:var(--amber);border-color:color-mix(in srgb,var(--amber) 45%,var(--line));background:color-mix(in srgb,var(--amber) 8%,var(--card))}
.cist-explain-v3-badge[data-risk="low"]{color:#64c99d;border-color:color-mix(in srgb,#64c99d 40%,var(--line));background:color-mix(in srgb,#64c99d 7%,var(--card))}
.cist-explain-v3-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:9px}
.cist-explain-v3-box{min-width:0;padding:11px 12px;border:1px solid color-mix(in srgb,var(--line) 88%,transparent);border-radius:12px;background:color-mix(in srgb,var(--soft) 48%,transparent)}
.cist-explain-v3-box-wide{grid-column:1/-1}
.cist-explain-v3-label{display:block;margin-bottom:7px;color:var(--muted);font-size:8.5px;font-weight:950;text-transform:uppercase;letter-spacing:.075em}
.cist-explain-v3-reasons{display:grid;gap:7px;margin:0;padding:0;list-style:none}
.cist-explain-v3-reason{display:grid;grid-template-columns:18px minmax(0,1fr);gap:7px;align-items:start}
.cist-explain-v3-icon{display:flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:6px;background:color-mix(in srgb,var(--amber) 9%,var(--card));color:var(--amber);font-size:10px;font-weight:950}
.cist-explain-v3-reason strong{display:block;color:var(--text);font-size:11px;line-height:1.35}
.cist-explain-v3-reason span{display:block;margin-top:1px;color:var(--muted);font-size:10px;line-height:1.4;overflow-wrap:anywhere}
.cist-explain-v3-action strong,.cist-explain-v3-domain strong{display:block;color:var(--text);font-size:12px;line-height:1.35;overflow-wrap:anywhere}
.cist-explain-v3-action span,.cist-explain-v3-domain span{display:block;margin-top:3px;color:var(--muted);font-size:10px;line-height:1.4;overflow-wrap:anywhere}
.cist-explain-v3-domain-code{display:inline-flex!important;margin-top:7px!important;padding:6px 8px;border:1px solid var(--line);border-radius:9px;background:var(--card);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--text)!important;font-size:10px!important;font-weight:850}
.cist-explain-v3-note{margin:9px 1px 0;color:var(--muted);font-size:9px;line-height:1.4}
@media(max-width:640px){.cist-explain-v3-grid{grid-template-columns:1fr}.cist-explain-v3-box-wide{grid-column:auto}.cist-explain-v3-head{align-items:center}#cist-explain-v3{padding:12px}.cist-explain-v3-title{font-size:13px}}
</style>
'''

SCRIPT = r'''
<script id="cist-explainable-result-v3-script">
(function(){
  var OFFICIAL={
    google:'google.com',microsoft:'microsoft.com',apple:'apple.com',paypal:'paypal.com',amazon:'amazon.com',netflix:'netflix.com',dropbox:'dropbox.com',notion:'notion.so',meta:'meta.com',facebook:'facebook.com',instagram:'instagram.com',whatsapp:'whatsapp.com',tiktok:'tiktok.com',x:'x.com',telegram:'telegram.org',discord:'discord.com',linkedin:'linkedin.com',youtube:'youtube.com',binance:'binance.com',coinbase:'coinbase.com',kraken:'kraken.com',revolut:'revolut.com',wise:'wise.com',stripe:'stripe.com',dhl:'dhl.com',fedex:'fedex.com',ups:'ups.com',usps:'usps.com',chronopost:'chronopost.fr','la poste':'laposte.fr',github:'github.com',cloudflare:'cloudflare.com',adobe:'adobe.com',steam:'steampowered.com',spotify:'spotify.com',airbnb:'airbnb.com',booking:'booking.com'
  };
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function cap(v){v=clean(v);return v?v.charAt(0).toUpperCase()+v.slice(1):''}
  function riskOf(d){return clean((d.megaScanner&&d.megaScanner.finalRisk)||(d.explanation&&d.explanation.verdict)||d.risk||'unknown').toLowerCase()}
  function ensure(){
    var panel=document.getElementById('cist-mega-v2-panel'),body=panel&&panel.querySelector('.cist-mega-v2-body');if(!body)return null;
    var box=document.getElementById('cist-explain-v3');
    if(!box){box=document.createElement('section');box.id='cist-explain-v3';box.setAttribute('aria-label','Why this safety result');var metrics=document.getElementById('cist-v4-metrics');if(metrics)metrics.insertAdjacentElement('afterend',box);else body.insertBefore(box,body.firstChild)}
    return box;
  }
  function relationshipReasons(d){
    var out=[],rels=Array.isArray(d.relationshipChecks)?d.relationshipChecks:[];
    rels.forEach(function(r){if(out.length>=3||!r||r.positive)return;var sev=clean(r.severity).toLowerCase();if(r.status==='conflict'||sev==='high'||sev==='medium')out.push({title:r.type==='claimed-brand-domain'?'Brand and domain do not match':r.type==='email-authentication'?'Email authentication failed':r.type==='email-from-replyto'?'Sender and reply address differ':'Identity relationship not confirmed',detail:clean(r.detail),kind:'warning'})});
    return out;
  }
  function explanationReasons(d){var out=[],items=Array.isArray(d.explanation&&d.explanation.reasons)?d.explanation.reasons:[];items.forEach(function(r){if(out.length>=3&&!out.length)return;var title=clean(r&&r.title),detail=clean(r&&r.detail);if(title||detail)out.push({title:title||'Safety signal',detail:detail,kind:clean(r&&r.severity).toLowerCase()==='positive'?'ok':'warning'})});return out}
  function signalReasons(d){var src=[];if(Array.isArray(d.signals))src=d.signals;else if(Array.isArray(d.analysis&&d.analysis.signals))src=d.analysis.signals;return src.slice(0,3).map(function(s){return{title:clean(s.title||s.id||'Safety signal').replace(/_/g,' '),detail:clean(s.detail||s.evidence||''),kind:'warning'}})}
  function reasons(d,risk){var all=relationshipReasons(d).concat(explanationReasons(d)).concat(signalReasons(d)),out=[],seen={};all.forEach(function(x){var k=(x.title+' '+x.detail).toLowerCase();if(!k||seen[k]||out.length>=3)return;seen[k]=1;out.push(x)});if(!out.length){out.push(risk==='low'?{title:'No major warning detected',detail:'The checks that completed did not find a strong scam signal.',kind:'ok'}:{title:'Limited evidence',detail:'The available checks did not provide enough evidence for a stronger explanation.',kind:'warning'})}return out}
  function brandConflict(d){var rels=Array.isArray(d.relationshipChecks)?d.relationshipChecks:[];for(var i=0;i<rels.length;i++){var r=rels[i];if(r&&r.type==='claimed-brand-domain'&&r.status==='conflict'){var brand=clean(r.brand).toLowerCase();return{brand:brand,seen:clean(r.websiteDomain),official:OFFICIAL[brand]||''}}}return null}
  function action(risk){if(risk==='high')return{title:'Do not open, pay, sign in or reply.',detail:'Contact the company or sender using a website, app or phone number you already trust.'};if(risk==='caution')return{title:'Verify independently before continuing.',detail:'Do not use the contact details or links contained in the suspicious content itself.'};if(risk==='low')return{title:'Continue only if you expected this.',detail:'A low-risk result is not proof of legitimacy. Be cautious with passwords, payments and downloads.'};return{title:'Do not rely on this result yet.',detail:'Try again with the full message, URL, sender information, screenshot or file.'}}
  function riskLabel(r){return r==='high'?'High risk':r==='caution'?'Verify first':r==='low'?'No major warning':'Incomplete'}
  function render(d){
    if(!d||d.error)return;var box=ensure();if(!box)return;var risk=riskOf(d),why=reasons(d,risk),conflict=brandConflict(d),act=action(risk),confidence=clean(d.explanation&&d.explanation.confidence&&d.explanation.confidence.level||d.confidence||'');
    var whyHtml=why.map(function(x){return '<li class="cist-explain-v3-reason"><span class="cist-explain-v3-icon">'+(x.kind==='ok'?'✓':'!')+'</span><div><strong>'+esc(x.title)+'</strong>'+(x.detail?'<span>'+esc(x.detail)+'</span>':'')+'</div></li>'}).join('');
    var domainHtml=conflict?'<div class="cist-explain-v3-box cist-explain-v3-domain"><span class="cist-explain-v3-label">Official domain expected</span><strong>'+esc(cap(conflict.brand))+' appears to be claimed</strong><span>Detected: '+esc(conflict.seen||'unknown domain')+'</span>'+(conflict.official?'<span class="cist-explain-v3-domain-code">'+esc(conflict.official)+'</span>':'<span>Use the company\'s official website from a trusted source.</span>')+'</div>':'';
    box.innerHTML='<div class="cist-explain-v3-head"><div><h4 class="cist-explain-v3-title">Why this result</h4><p class="cist-explain-v3-sub">The verdict is based on the strongest evidence found'+(confidence?' · Confidence '+esc(confidence):'')+'.</p></div><span class="cist-explain-v3-badge" data-risk="'+esc(risk)+'">'+esc(riskLabel(risk))+'</span></div><div class="cist-explain-v3-grid"><div class="cist-explain-v3-box '+(domainHtml?'':'cist-explain-v3-box-wide')+'"><span class="cist-explain-v3-label">Evidence</span><ul class="cist-explain-v3-reasons">'+whyHtml+'</ul></div>'+domainHtml+'<div class="cist-explain-v3-box cist-explain-v3-box-wide cist-explain-v3-action"><span class="cist-explain-v3-label">What to do now</span><strong>'+esc(act.title)+'</strong><span>'+esc(act.detail)+'</span></div></div><p class="cist-explain-v3-note">Automated checks reduce uncertainty but cannot prove that content is legitimate or malicious.</p>';
    box.classList.add('cist-show');
  }
  document.addEventListener('cist:mega-result',function(e){try{render(e.detail)}catch(err){}});
  var reset=document.getElementById('cist-unified-reset');if(reset)reset.addEventListener('click',function(){var box=document.getElementById('cist-explain-v3');if(box)box.classList.remove('cist-show')});
})();
</script>
'''

if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s = HOME.read_text(encoding='utf-8')
s = re.sub(r'\s*<style id="cist-explainable-result-v3-style">.*?</style>', '', s, count=1, flags=re.S)
s = re.sub(r'\s*<script id="cist-explainable-result-v3-script">.*?</script>', '', s, count=1, flags=re.S)
if 'cist-mega-v2-panel' not in s or 'cist:mega-result' not in s:
    raise RuntimeError('Explainable result requires the unified Mega Scanner UI')
s = s.replace('</head>', STYLE + '\n</head>', 1)
s = s.replace('</body>', SCRIPT + '\n</body>', 1)
for token in ['Why this result','Official domain expected','What to do now','Automated checks reduce uncertainty']:
    if token not in s:
        raise RuntimeError('Explainable result V3 guard failed: ' + token)
HOME.write_text(s, encoding='utf-8')
print('Applied explainable result V3')
