#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-explainable-result-v3-style">
#cist-explain-v3{display:none;margin:12px 0 4px;padding:14px;border:1px solid var(--line);border-radius:16px;background:color-mix(in srgb,var(--card) 92%,transparent)}
#cist-explain-v3.cist-show{display:block}
.cist-explain-v3-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}
.cist-explain-v3-title{margin:0;font-size:15px;font-weight:950;letter-spacing:-.015em;color:var(--text)}
.cist-explain-v3-sub{margin:3px 0 0;color:var(--muted);font-size:10.5px;line-height:1.4}
.cist-explain-v3-badge{flex:0 0 auto;padding:6px 9px;border:1px solid var(--line);border-radius:999px;font-size:9px;font-weight:950;text-transform:uppercase;letter-spacing:.06em}
.cist-explain-v3-badge[data-risk="high"]{color:var(--red);border-color:color-mix(in srgb,var(--red) 45%,var(--line));background:color-mix(in srgb,var(--red) 8%,var(--card))}
.cist-explain-v3-badge[data-risk="caution"]{color:var(--amber);border-color:color-mix(in srgb,var(--amber) 45%,var(--line));background:color-mix(in srgb,var(--amber) 8%,var(--card))}
.cist-explain-v3-badge[data-risk="low"]{color:#64c99d;border-color:color-mix(in srgb,#64c99d 40%,var(--line));background:color-mix(in srgb,#64c99d 7%,var(--card))}
.cist-explain-v3-summary{padding:11px 12px;border:1px solid color-mix(in srgb,var(--line) 88%,transparent);border-radius:12px;background:color-mix(in srgb,var(--soft) 48%,transparent)}
.cist-explain-v3-summary strong{display:block;color:var(--text);font-size:12px;line-height:1.4}
.cist-explain-v3-summary span{display:block;margin-top:3px;color:var(--muted);font-size:10.5px;line-height:1.45}
.cist-explain-v3-domain{margin-top:9px;padding:10px 11px;border:1px solid color-mix(in srgb,var(--amber) 28%,var(--line));border-radius:11px;background:color-mix(in srgb,var(--amber) 5%,var(--card))}
.cist-explain-v3-domain b{display:block;color:var(--text);font-size:10.5px}.cist-explain-v3-domain span{display:block;margin-top:2px;color:var(--muted);font-size:10px;line-height:1.4}.cist-explain-v3-domain code{display:inline-block;margin-top:5px;padding:4px 6px;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--text);font-size:10px;font-weight:850}
.cist-explain-v3-action{margin-top:9px;padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.cist-explain-v3-action small{display:block;margin-bottom:4px;color:var(--muted);font-size:8.5px;font-weight:950;text-transform:uppercase;letter-spacing:.07em}.cist-explain-v3-action strong{display:block;color:var(--text);font-size:12px;line-height:1.4}.cist-explain-v3-action span{display:block;margin-top:3px;color:var(--muted);font-size:10px;line-height:1.4}
body.cist-clean-result-v3 #cist-v4-metrics,
body.cist-clean-result-v3 #cist-v3-positive,
body.cist-clean-result-v3 #cist-v5-no-warning,
body.cist-clean-result-v3 #cist-v4-context,
body.cist-clean-result-v3 #cist-v3-coverage-wrap,
body.cist-clean-result-v3 #cist-mega-reasons,
body.cist-clean-result-v3 #cist-mega-chain,
body.cist-clean-result-v3 .cist-v4-summary-copy,
body.cist-clean-result-v3 .cist-mega-v2-section:has(#cist-mega-reputation),
body.cist-clean-result-v3 .cist-mega-v2-section:has(#cist-v4-advanced),
body.cist-clean-result-v3 .cist-mega-v2-section:has(#cist-v4-coverage){display:none!important}
body.cist-clean-result-v3 #technical{display:block!important;margin-top:10px!important}
body.cist-clean-result-v3 #technical summary{cursor:pointer;font-size:10.5px!important;font-weight:850!important;color:var(--muted)!important}
@media(max-width:640px){#cist-explain-v3{padding:12px}.cist-explain-v3-title{font-size:14px}.cist-explain-v3-head{align-items:flex-start}}
</style>
'''

SCRIPT = r'''
<script id="cist-explainable-result-v3-script">
(function(){
  var OFFICIAL={google:'google.com',microsoft:'microsoft.com',apple:'apple.com',paypal:'paypal.com',amazon:'amazon.com',netflix:'netflix.com',dropbox:'dropbox.com',notion:'notion.so',meta:'meta.com',facebook:'facebook.com',instagram:'instagram.com',whatsapp:'whatsapp.com',tiktok:'tiktok.com',x:'x.com',telegram:'telegram.org',discord:'discord.com',linkedin:'linkedin.com',youtube:'youtube.com',binance:'binance.com',coinbase:'coinbase.com',kraken:'kraken.com',revolut:'revolut.com',wise:'wise.com',stripe:'stripe.com',dhl:'dhl.com',fedex:'fedex.com',ups:'ups.com',usps:'usps.com',chronopost:'chronopost.fr','la poste':'laposte.fr',github:'github.com',cloudflare:'cloudflare.com',adobe:'adobe.com',steam:'steampowered.com',spotify:'spotify.com',airbnb:'airbnb.com',booking:'booking.com'};
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v){return String(v==null?'':v).replace(/\s+/g,' ').trim()}
  function cap(v){v=clean(v);return v?v.charAt(0).toUpperCase()+v.slice(1):''}
  function riskOf(d){return clean((d.megaScanner&&d.megaScanner.finalRisk)||(d.explanation&&d.explanation.verdict)||d.risk||'unknown').toLowerCase()}
  function ensure(){var panel=document.getElementById('cist-mega-v2-panel'),body=panel&&panel.querySelector('.cist-mega-v2-body');if(!body)return null;var box=document.getElementById('cist-explain-v3');if(!box){box=document.createElement('section');box.id='cist-explain-v3';box.setAttribute('aria-label','Safety result summary');body.insertBefore(box,body.firstChild)}return box}
  function brandConflict(d){var rels=Array.isArray(d.relationshipChecks)?d.relationshipChecks:[];for(var i=0;i<rels.length;i++){var r=rels[i];if(r&&r.type==='claimed-brand-domain'&&r.status==='conflict'){var brand=clean(r.brand).toLowerCase();return{brand:brand,seen:clean(r.websiteDomain),official:OFFICIAL[brand]||''}}}return null}
  function identityLevel(d){return clean(d.identityConsistency&&d.identityConsistency.level||'unknown').toLowerCase()}
  function confidenceLabel(d){var c=clean(d.explanation&&d.explanation.confidence&&d.explanation.confidence.level||'').toLowerCase();if(c==='high')return'High evidence coverage';if(c==='medium')return'Medium evidence coverage';if(c==='low')return'Low evidence coverage';return''}
  function host(d){var el=d.detectedElements||{};if(Array.isArray(el.domains)&&el.domains[0])return clean(el.domains[0]);try{var u=(el.urls&&el.urls[0])||'';return u?new URL(u).hostname.replace(/^www\./,''):''}catch(_){return''}}
  function explanation(d,risk){var id=identityLevel(d),h=host(d);if(risk==='high')return{title:'Strong scam or impersonation signals were detected.',detail:h?'The destination '+h+' triggered one or more high-risk checks.':'One or more high-risk checks were triggered.'};if(risk==='caution')return{title:'Some signals need independent verification.',detail:'The content is not clearly malicious, but there is enough uncertainty to verify it before acting.'};if(risk==='low'&&id==='unknown')return{title:'No strong scam signals were found.',detail:(h?'The checks on '+h+' did not find a major warning. ':'')+'The identity could not be independently verified.'};if(risk==='low')return{title:'No strong scam signals were found.',detail:h?'The checks on '+h+' did not find a major warning.':'The completed checks did not find a major warning.'};return{title:'The scan is incomplete.',detail:'There is not enough evidence to support a reliable conclusion.'}}
  function action(risk){if(risk==='high')return{title:'Do not open, pay, sign in or reply.',detail:'Verify the company or sender through a website, app or phone number you already trust.'};if(risk==='caution')return{title:'Verify independently before continuing.',detail:'Do not rely on links or contact details contained in the suspicious content itself.'};if(risk==='low')return{title:'Continue only if you expected this.',detail:'Be cautious if it asks for a password, payment, download or sensitive information.'};return{title:'Do not rely on this result yet.',detail:'Try again with the full message, URL, sender information, screenshot or file.'}}
  function label(r){return r==='high'?'High risk':r==='caution'?'Verify first':r==='low'?'No major warning':'Incomplete'}
  function render(d){if(!d||d.error)return;var box=ensure();if(!box)return;var risk=riskOf(d),exp=explanation(d,risk),act=action(risk),conf=confidenceLabel(d),bc=brandConflict(d);var domain=bc?'<div class="cist-explain-v3-domain"><b>Official domain expected</b><span>Detected: '+esc(bc.seen||'unknown domain')+'</span>'+(bc.official?'<code>'+esc(bc.official)+'</code>':'<span>Use the official company website from a trusted source.</span>')+'</div>':'';box.innerHTML='<div class="cist-explain-v3-head"><div><h4 class="cist-explain-v3-title">'+esc(label(risk))+'</h4><p class="cist-explain-v3-sub">'+esc(conf||'Evidence-based automated check')+'</p></div><span class="cist-explain-v3-badge" data-risk="'+esc(risk)+'">'+esc(label(risk))+'</span></div><div class="cist-explain-v3-summary"><strong>'+esc(exp.title)+'</strong><span>'+esc(exp.detail)+'</span>'+domain+'</div><div class="cist-explain-v3-action"><small>What to do</small><strong>'+esc(act.title)+'</strong><span>'+esc(act.detail)+'</span></div>';box.classList.add('cist-show');document.body.classList.add('cist-clean-result-v3');var tech=document.getElementById('technical');if(tech){tech.classList.remove('hidden');tech.open=false}}
  document.addEventListener('cist:mega-result',function(e){try{render(e.detail)}catch(err){}});
  var reset=document.getElementById('cist-unified-reset');if(reset)reset.addEventListener('click',function(){var box=document.getElementById('cist-explain-v3');if(box)box.classList.remove('cist-show');document.body.classList.remove('cist-clean-result-v3')});
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
for token in ['Safety result summary','Official domain expected','What to do','High evidence coverage','cist-clean-result-v3']:
    if token not in s:
        raise RuntimeError('Clean explainable result guard failed: ' + token)
HOME.write_text(s, encoding='utf-8')
print('Applied compact explainable result V3')
