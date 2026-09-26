#!/usr/bin/env python3
from pathlib import Path
import re

HOME = Path(__file__).resolve().parents[1] / 'dist' / 'index.html'
if not HOME.is_file():
    raise RuntimeError('Homepage not found')
s = HOME.read_text(encoding='utf-8')

# Position the homepage around one job: understand a suspicious link before opening it.
s = re.sub(r'<title>.*?</title>', '<title>Can I Share This? — Check Where a Link Goes Before You Open It</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Paste a suspicious or shortened link to reveal its final destination, redirects and trust signals. Can I Share This? explains why the link may or may not deserve your trust.">', s, count=1)
s = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Can you trust this link? — Can I Share This?">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="See where a link really goes, what changed on the way, and why it may or may not deserve your trust.">', s, count=1)
s = re.sub(r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="Can you trust this link? — Can I Share This?">', s, count=1)
s = re.sub(r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="Reveal the destination, redirects and trust signals before you open a suspicious link.">', s, count=1)

hero = '''<p class="eyebrow">Link trust checker</p>
      <h1 id="page-title">Can you trust <span class="cist-title-end">this link?</span></h1>
      <p class="sub">Paste a suspicious or shortened link. See where it really goes, what changed on the way, and why it may—or may not—deserve your trust.</p>'''
s, n = re.subn(r'<p class="eyebrow">.*?</p>\s*<h1 id="page-title">.*?</h1>\s*<p class="sub">.*?</p>', hero, s, count=1, flags=re.S)
if n != 1:
    raise RuntimeError('Hero copy not found')
s = re.sub(r'placeholder="Paste a link,[^"]*"', 'placeholder="Paste a suspicious link…"', s, count=1)
s = re.sub(r'(<button[^>]+id="analyze"[^>]*>).*?(</button>)', r'\1Check link\2', s, count=1, flags=re.S)

STYLE = r'''
<style id="cist-link-first-home-v1-style">
#cist-daily-rail,#cist-scam-signals-rail,#cist-mega-badges,#cist-check-selector,#cist-other-checks-toggle,.cist-detected-type,#input-kind,#cist-unified-home-scanner #choose-image,#cist-unified-home-scanner #paste,#cist-unified-home-scanner #image-file,#cist-unified-home-scanner #camera-file{display:none!important}
.hero{padding-top:clamp(62px,8vw,104px)!important}.hero .eyebrow{margin-bottom:12px!important;color:var(--cist-accent,#788ff7)!important;letter-spacing:.12em!important}.hero h1{max-width:760px!important;margin-left:auto!important;margin-right:auto!important;font-size:clamp(46px,7.2vw,82px)!important;line-height:.96!important;letter-spacing:-.055em!important}.hero .sub{max-width:670px!important;margin:20px auto 0!important;font-size:clamp(15px,2vw,18px)!important;line-height:1.55!important;color:var(--muted)!important}
#cist-unified-home-scanner{width:min(760px,calc(100% - 28px))!important;margin-top:28px!important;padding:9px!important;border-radius:18px!important}#cist-unified-home-scanner #scan-form{grid-template-columns:minmax(0,1fr) auto!important;gap:8px!important}#cist-unified-home-scanner .input-wrap{grid-column:auto!important;height:56px!important;border-bottom:0!important;border-radius:13px!important}#cist-unified-home-scanner #url{height:56px!important;font-size:15px!important;padding:0 12px!important}#cist-unified-home-scanner #analyze{display:inline-flex!important;align-items:center!important;justify-content:center!important;min-width:126px!important;height:48px!important;padding:0 18px!important;font-size:13px!important}#cist-unified-home-note{margin-top:8px!important;font-size:10px!important}
#cist-return-hook{width:min(760px,calc(100% - 28px));margin:12px auto 0;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:10.5px;line-height:1.35;text-align:center}#cist-return-hook .live-dot{width:6px;height:6px;border-radius:999px;background:#61c99a;box-shadow:0 0 0 4px color-mix(in srgb,#61c99a 14%,transparent)}#cist-return-hook strong{color:var(--text);font-weight:850}#cist-return-hook .sep{opacity:.45}
body.cist-link-result-active #cist-mega-v2-panel .cist-mega-v2-head{display:none!important}body.cist-link-result-active #cist-mega-v2-panel .cist-mega-v2-body>*{display:none!important}body.cist-link-result-active #cist-mega-v2-panel .cist-mega-v2-body>#cist-link-first-result{display:block!important}
#cist-link-first-result .lf-verdict{padding:26px 26px 22px;border-bottom:1px solid var(--line)}#cist-link-first-result .lf-kicker{font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}#cist-link-first-result .lf-label{margin:7px 0 0;font-size:clamp(36px,7vw,58px);line-height:.98;letter-spacing:-.05em;font-weight:950}#cist-link-first-result[data-risk=high] .lf-label{color:#ff7770}#cist-link-first-result[data-risk=caution] .lf-label{color:#f0b85b}#cist-link-first-result[data-risk=low] .lf-label{color:#61c99a}#cist-link-first-result .lf-headline{max-width:650px;margin:12px 0 0;color:var(--muted);font-size:14px;line-height:1.5}
#cist-link-first-result .lf-grid{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:12px;padding:20px 26px 8px}#cist-link-first-result .lf-card{border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--soft) 55%,transparent);padding:15px}#cist-link-first-result .lf-card h3{margin:0 0 8px;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}#cist-link-first-result .lf-destination{font-size:18px;font-weight:900;letter-spacing:-.02em;overflow-wrap:anywhere}#cist-link-first-result .lf-route{margin-top:5px;color:var(--muted);font-size:10px}#cist-link-first-result .lf-reasons{display:grid;gap:9px;margin:0;padding:0;list-style:none}#cist-link-first-result .lf-reasons li{display:grid;grid-template-columns:7px 1fr;gap:9px;align-items:start}#cist-link-first-result .lf-reasons i{width:7px;height:7px;margin-top:6px;border-radius:999px;background:var(--cist-accent,#788ff7)}#cist-link-first-result[data-risk=high] .lf-reasons i{background:#ff7770}#cist-link-first-result[data-risk=caution] .lf-reasons i{background:#f0b85b}#cist-link-first-result[data-risk=low] .lf-reasons i{background:#61c99a}#cist-link-first-result .lf-reasons strong{display:block;font-size:12px;line-height:1.35}#cist-link-first-result .lf-reasons span{display:block;margin-top:2px;color:var(--muted);font-size:10.5px;line-height:1.45}

#cist-link-detail-v2{margin:14px 26px 0;border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--card) 94%,var(--soft));overflow:hidden}
#cist-link-detail-v2>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 15px;cursor:pointer}
#cist-link-detail-v2>summary::-webkit-details-marker{display:none}
#cist-link-detail-v2 .lf-detail-head strong{display:block;color:var(--text);font-size:12px;font-weight:900}
#cist-link-detail-v2 .lf-detail-head small{display:block;margin-top:2px;color:var(--muted);font-size:9.5px;line-height:1.4}
#cist-link-detail-v2 .lf-detail-toggle{color:var(--cist-accent,#788ff7);font-size:10px;font-weight:900;white-space:nowrap}
#cist-link-detail-v2[open]>summary{border-bottom:1px solid var(--line)}
#cist-link-detail-v2 .lf-detail-body{padding:0 15px 15px}
#cist-link-detail-v2 .lf-detail-section{padding-top:14px}
#cist-link-detail-v2 .lf-detail-section+.lf-detail-section{margin-top:14px;border-top:1px solid var(--line)}
#cist-link-detail-v2 .lf-detail-kicker{margin:0 0 7px;color:var(--muted);font-size:8.5px;font-weight:950;letter-spacing:.08em;text-transform:uppercase}
#cist-link-detail-v2 .lf-detail-section h4{margin:0 0 8px;color:var(--text);font-size:12px;font-weight:900}
#cist-link-detail-v2 .lf-detail-list{display:grid;gap:8px;margin:0;padding:0;list-style:none}
#cist-link-detail-v2 .lf-detail-list li{display:grid;grid-template-columns:8px minmax(0,1fr);gap:9px;align-items:start;color:var(--text);font-size:10.5px;line-height:1.4}
#cist-link-detail-v2 .lf-detail-list i{width:8px;height:8px;margin-top:4px;border-radius:50%;background:var(--muted)}
#cist-link-detail-v2 .lf-detail-list li.pass i{background:#61c99a}
#cist-link-detail-v2 .lf-detail-list li.attention i{background:#f0b85b}
#cist-link-detail-v2 .lf-detail-list strong{display:block;font-size:10.5px}
#cist-link-detail-v2 .lf-detail-list span{display:block;margin-top:1px;color:var(--muted);font-size:9.5px}
#cist-link-detail-v2 .lf-detail-chain{display:grid;gap:0}
#cist-link-detail-v2 .lf-chain-row{display:grid;grid-template-columns:18px minmax(0,1fr);gap:8px;padding-bottom:10px}
#cist-link-detail-v2 .lf-chain-row:last-child{padding-bottom:0}
#cist-link-detail-v2 .lf-chain-dot{position:relative;display:flex;justify-content:center}
#cist-link-detail-v2 .lf-chain-dot:after{content:"";position:absolute;top:11px;bottom:-2px;width:1px;background:var(--line)}
#cist-link-detail-v2 .lf-chain-row:last-child .lf-chain-dot:after{display:none}
#cist-link-detail-v2 .lf-chain-dot:before{content:"";position:relative;z-index:1;width:8px;height:8px;margin-top:2px;border-radius:50%;background:var(--cist-accent,#788ff7);box-shadow:0 0 0 2px var(--card)}
#cist-link-detail-v2 .lf-chain-copy small{display:block;color:var(--muted);font-size:8px;font-weight:850;text-transform:uppercase}
#cist-link-detail-v2 .lf-chain-copy code{display:block;margin-top:2px;color:var(--text);font:700 10px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:normal;overflow-wrap:anywhere}
#cist-link-detail-v2 .lf-detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
#cist-link-detail-v2 .lf-detail-cell{padding:9px 10px;border:1px solid var(--line);border-radius:10px;background:color-mix(in srgb,var(--soft) 45%,transparent)}
#cist-link-detail-v2 .lf-detail-cell small{display:block;color:var(--muted);font-size:8px;font-weight:900;text-transform:uppercase;letter-spacing:.05em}
#cist-link-detail-v2 .lf-detail-cell strong{display:block;margin-top:2px;color:var(--text);font-size:10.5px;line-height:1.35;overflow-wrap:anywhere}
#cist-link-detail-v2 .lf-detail-limit{padding:11px 12px;border-left:3px solid var(--cist-accent,#788ff7);border-radius:0 10px 10px 0;background:color-mix(in srgb,var(--cist-accent,#788ff7) 6%,transparent);color:var(--muted);font-size:9.5px;line-height:1.5}
#cist-link-detail-v2 .lf-detail-limit strong{color:var(--text)}
#cist-link-detail-v2 .lf-advanced{margin-top:10px;border:1px solid var(--line);border-radius:10px;overflow:hidden}
#cist-link-detail-v2 .lf-advanced>summary{list-style:none;display:flex;justify-content:space-between;gap:10px;padding:10px 11px;cursor:pointer;color:var(--text);font-size:9.5px;font-weight:900}
#cist-link-detail-v2 .lf-advanced>summary::-webkit-details-marker{display:none}
#cist-link-detail-v2 .lf-advanced-body{padding:0 11px 11px}
#cist-link-detail-v2 .lf-advanced-row{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid var(--line);font-size:9px}
#cist-link-detail-v2 .lf-advanced-row:first-child{border-top:0}
#cist-link-detail-v2 .lf-advanced-row span:first-child{color:var(--text);font-weight:800}
#cist-link-detail-v2 .lf-advanced-row span:last-child{color:var(--muted);text-align:right;overflow-wrap:anywhere}

#cist-link-first-result .lf-action{margin:12px 26px 0;padding:14px 15px;border-left:3px solid var(--cist-accent,#788ff7);border-radius:10px;background:color-mix(in srgb,var(--cist-accent,#788ff7) 7%,transparent);font-size:12px;font-weight:800;line-height:1.5}#cist-link-first-result .lf-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:18px 26px 24px}#cist-link-first-result .lf-actions #cist-mega-share{display:inline-flex!important;align-items:center!important;justify-content:center!important;min-height:42px!important;padding:0 16px!important;border-radius:10px!important;background:var(--cist-accent,#788ff7)!important;color:#fff!important;border:0!important;font-weight:900!important}#cist-link-first-result .lf-reset{appearance:none;border:1px solid var(--line);border-radius:10px;background:transparent;color:var(--text);min-height:42px;padding:0 14px;font:inherit;font-size:11px;font-weight:800;cursor:pointer}#cist-link-first-result .lf-disclaimer{width:100%;margin:4px 0 0;color:var(--muted);font-size:9.5px;line-height:1.45}
@media(max-width:700px){.hero{padding-top:48px!important}.hero h1{font-size:clamp(42px,13vw,62px)!important}#cist-unified-home-scanner{width:calc(100% - 24px)!important;margin-top:22px!important}#cist-unified-home-scanner #scan-form{grid-template-columns:1fr!important}#cist-unified-home-scanner .input-wrap{grid-column:1!important;height:52px!important}#cist-unified-home-scanner #url{height:52px!important}#cist-unified-home-scanner #analyze{width:100%!important;height:48px!important}#cist-link-first-result .lf-verdict{padding:21px 18px 18px}#cist-link-first-result .lf-grid{grid-template-columns:1fr;padding:16px 18px 6px}#cist-link-first-result .lf-action{margin:10px 18px 0}#cist-link-detail-v2{margin:12px 18px 0}#cist-link-detail-v2 .lf-detail-grid{grid-template-columns:1fr}#cist-link-first-result .lf-actions{padding:16px 18px 20px}#cist-link-first-result .lf-actions #cist-mega-share,#cist-link-first-result .lf-reset{flex:1}}
</style>
'''

SCRIPT = r'''
<script id="cist-link-first-home-v1-script">
(function(){
var input=document.getElementById('url'),analyze=document.getElementById('analyze'),note=document.getElementById('cist-unified-home-note');
if(input){input.placeholder='Paste a suspicious link…';input.setAttribute('aria-label','Paste a suspicious or shortened link');input.setAttribute('inputmode','url');input.setAttribute('autocomplete','off')}if(analyze)analyze.textContent='Check link';if(note)note.innerHTML='<span>Private by design</span><span class="cist-dot">·</span><span>No account</span><span class="cist-dot">·</span><span>Fresh check every time</span>';
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}function clean(v,m){return String(v==null?'':v).replace(/\s+/g,' ').trim().slice(0,m||220)}
function find(root,names,depth){var seen=new Set();function walk(v,d){if(!v||typeof v!=='object'||d>(depth||5)||seen.has(v))return null;seen.add(v);for(var i=0;i<names.length;i++){var k=names[i];if(Object.prototype.hasOwnProperty.call(v,k)&&v[k]!=null&&v[k]!=='')return v[k]}var ks=Object.keys(v).slice(0,80);for(var j=0;j<ks.length;j++){var x=v[ks[j]],hit=x&&typeof x==='object'?walk(x,d+1):null;if(hit!=null)return hit}return null}return walk(root,0)}
function risk(d){var v=(d.megaScanner&&d.megaScanner.finalRisk)||(d.shareSummary&&d.shareSummary.verdict)||(d.explanation&&d.explanation.verdict)||find(d,['finalRisk','verdict','riskLevel'],4)||'unknown';v=String(v).toLowerCase();if(/high|danger|malicious|unsafe/.test(v))return'high';if(/caution|medium|verify|suspicious|warn/.test(v))return'caution';if(/low|safe|clear|normal|no major/.test(v))return'low';return'unknown'}
function label(r){return r==='high'?'HIGH RISK':r==='caution'?'VERIFY FIRST':r==='low'?'NO MAJOR WARNING':'INCOMPLETE'}
function dest(d){var raw=find(d,['finalUrl','finalURL','resolvedUrl','destinationUrl'],5),host=find(d,['finalHost','resolvedHost','destinationHost'],5);if(raw){try{host=new URL(String(raw)).hostname||host}catch(_){}}if(!host&&d.detectedElements&&Array.isArray(d.detectedElements.domains))host=d.detectedElements.domains[0];return clean(host||'Destination could not be fully resolved',140)}
function hops(d){var r=find(d,['redirects','redirectChain'],5);return Array.isArray(r)?r.length:0}
function reasons(d,r){var a=(d.shareSummary&&d.shareSummary.reasons)||(d.explanation&&d.explanation.reasons)||find(d,['signals'],4)||[];if(!Array.isArray(a))a=[];a=a.slice(0,3).map(function(x){return{title:clean(x&&x.title||'Signal reviewed',70),detail:clean(x&&x.detail||'',145)}});if(!a.length)a=[{title:r==='low'?'No obvious suspicious pattern found':'Fresh verification recommended',detail:r==='low'?'The automated checks did not find a major warning in this snapshot.':'The scan did not have enough evidence for a stronger conclusion.'}];return a}
function headline(d,r){return clean((d.shareSummary&&d.shareSummary.headline)||(d.explanation&&d.explanation.headline)||(r==='high'?'This link contains signals that deserve caution before you open it.':r==='caution'?'Some signals need verification before you trust this destination.':r==='low'?'No major warning was found, but the final destination still matters.':'The scan could not establish a complete verdict.'),180)}
function action(d,r){return clean((d.shareSummary&&d.shareSummary.action)||(d.explanation&&d.explanation.action)||(r==='high'?'Do not enter passwords, payment details or download files until you verify the final domain independently.':r==='caution'?'Confirm that the final domain is the one you expected before signing in, paying or downloading anything.':'Check that the final domain matches what you expected before entering sensitive information.'),220)}

function safeUrl(v){try{var u=new URL(String(v||''));return u.origin+u.pathname+(u.search?'?…':'')}catch(_){return clean(v,260)}}
function finalUrl(d){return clean(find(d,['finalUrl','finalURL','resolvedUrl','destinationUrl'],5)||'',500)}
function redirectData(d){var x=find(d,['redirects','redirectChain'],5);return Array.isArray(x)?x:[]}
function redirectUrl(x){if(typeof x==='string')return x;if(!x||typeof x!=='object')return'';return x.url||x.location||x.to||x.target||x.finalUrl||''}
function redirectStatus(x){if(!x||typeof x!=='object')return'';return x.status||x.statusCode||x.code||''}
function detailCell(label,value){return '<div class="lf-detail-cell"><small>'+esc(label)+'</small><strong>'+esc(value==null||value===''?'Not reported':value)+'</strong></div>'}
function detailV2(d,r,rs){
  var f=finalUrl(d),host=dest(d),reds=redirectData(d),status=find(d,['status','statusCode','httpStatus'],5),contentType=find(d,['contentType','mimeType'],5),responseMs=find(d,['responseMs','responseTimeMs','latencyMs'],5),login=find(d,['loginRequired','loginWall','accessWall'],5),identity=clean(d.identityConsistency&&d.identityConsistency.level||find(d,['identityLevel'],4)||'unknown',40).toLowerCase(),checks=find(d,['checksPerformed'],5),protocol='';
  try{protocol=new URL(f||input.value).protocol}catch(_){}
  var ev=[];
  rs.forEach(function(x){ev.push('<li class="'+(r==='high'||r==='caution'?'attention':'pass')+'"><i></i><div><strong>'+esc(x.title)+'</strong>'+(x.detail?'<span>'+esc(x.detail)+'</span>':'')+'</div></li>')});
  if(protocol==='https:')ev.push('<li class="pass"><i></i><div><strong>HTTPS destination</strong><span>The final observed URL uses HTTPS.</span></div></li>');
  if(reds.length)ev.push('<li class="attention"><i></i><div><strong>'+reds.length+' redirect'+(reds.length===1?'':'s')+' followed</strong><span>Redirects change where the submitted URL ultimately goes.</span></div></li>');
  if(identity!=='high')ev.push('<li><i></i><div><strong>Identity not independently established</strong><span>No warning is not proof of who controls the destination.</span></div></li>');
  var chain=[],submitted=clean(input.value,500);
  if(/^https?:\/\//i.test(submitted))chain.push({label:'Submitted URL',url:safeUrl(submitted)});
  reds.forEach(function(x,i){var u=redirectUrl(x);if(u)chain.push({label:'Redirect '+(i+1)+(redirectStatus(x)?' · '+redirectStatus(x):''),url:safeUrl(u)})});
  if(f){var sf=safeUrl(f);if(!chain.length||chain[chain.length-1].url!==sf)chain.push({label:'Final destination'+(status?' · '+status:''),url:sf})}
  if(!chain.length)chain.push({label:'Final destination',url:host});
  var chainHtml=chain.map(function(x){return'<div class="lf-chain-row"><div class="lf-chain-dot"></div><div class="lf-chain-copy"><small>'+esc(x.label)+'</small><code>'+esc(x.url)+'</code></div></div>'}).join('');
  var https=protocol==='https:'?'Yes':protocol==='http:'?'No':'Could not determine',loginText=login===true?'Detected':login===false?'Not detected':'Could not determine';
  var checkText=Array.isArray(checks)&&checks.length?checks.join(' · '):'Local URL and destination checks';
  return '<details id="cist-link-detail-v2"><summary><span class="lf-detail-head"><strong>Detailed analysis</strong><small>Evidence, redirects, response data and scan limits</small></span><span class="lf-detail-toggle">View details ↓</span></summary><div class="lf-detail-body">'+
    '<section class="lf-detail-section"><p class="lf-detail-kicker">Evidence</p><h4>What the scan observed</h4><ul class="lf-detail-list">'+ev.join('')+'</ul></section>'+
    '<section class="lf-detail-section"><p class="lf-detail-kicker">Destination</p><h4>Redirect chain</h4><div class="lf-detail-chain">'+chainHtml+'</div></section>'+
    '<section class="lf-detail-section"><p class="lf-detail-kicker">Response</p><h4>Domain & response</h4><div class="lf-detail-grid">'+detailCell('Final host',host)+detailCell('HTTP response',status)+detailCell('HTTPS',https)+detailCell('Redirects',reds.length)+detailCell('Content type',contentType)+detailCell('Response time',responseMs?responseMs+' ms':'Not reported')+detailCell('Login / access wall',loginText)+detailCell('Identity',identity==='high'?'Supporting evidence found':'Not independently verified')+'</div></section>'+
    '<section class="lf-detail-section"><p class="lf-detail-kicker">Limits</p><h4>What this result does not mean</h4><div class="lf-detail-limit"><strong>This is not a guarantee of safety.</strong> A legitimate site can be compromised, a new malicious page may have no known warning yet, and content can change after this scan.</div><details class="lf-advanced"><summary><span>Advanced technical details</span><span>Open ↓</span></summary><div class="lf-advanced-body"><div class="lf-advanced-row"><span>Checks performed</span><span>'+esc(checkText)+'</span></div><div class="lf-advanced-row"><span>Final destination</span><span>'+esc(f||host)+'</span></div><div class="lf-advanced-row"><span>Identity verification</span><span>'+(identity==='high'?'Supporting relationship evidence found':'Not independently established')+'</span></div></div></details></section>'+
  '</div></details>';
}

function pulse(){if(document.getElementById('cist-return-hook'))return;var anchor=document.getElementById('cist-unified-home-scanner')||document.getElementById('scan-form');if(!anchor)return;var p=document.createElement('div');p.id='cist-return-hook';p.innerHTML='<span class="live-dot"></span><strong>Today\'s signal pulse</strong><span class="sep">·</span><span><b id="cist-return-scans">—</b> checks</span><span class="sep">·</span><span><b id="cist-return-warnings">—</b> warning signals</span>';anchor.insertAdjacentElement('afterend',p);var a=document.getElementById('cist-daily-scans'),b=document.getElementById('cist-daily-warnings')||document.getElementById('cist-signal-total');function sync(){var x=document.getElementById('cist-return-scans'),y=document.getElementById('cist-return-warnings');if(x&&a&&clean(a.textContent,20))x.textContent=clean(a.textContent,20);if(y&&b&&clean(b.textContent,20))y.textContent=clean(b.textContent,20)}sync();[a,b].filter(Boolean).forEach(function(n){new MutationObserver(sync).observe(n,{childList:true,subtree:true,characterData:true})})}
function render(d){if(!d||typeof d!=='object')return;var panel=document.getElementById('cist-mega-v2-panel');if(!panel)return;var body=panel.querySelector('.cist-mega-v2-body')||panel,old=document.getElementById('cist-link-first-result'),detailWasOpen=!!(old&&old.querySelector('#cist-link-detail-v2[open]'));if(old)old.remove();var r=risk(d),rs=reasons(d,r),h=hops(d),card=document.createElement('section');card.id='cist-link-first-result';card.dataset.risk=r;card.innerHTML='<div class="lf-verdict"><div class="lf-kicker">Link trust verdict</div><div class="lf-label">'+label(r)+'</div><p class="lf-headline">'+esc(headline(d,r))+'</p></div><div class="lf-grid"><div class="lf-card"><h3>Where it goes</h3><div class="lf-destination">'+esc(dest(d))+'</div><div class="lf-route">'+(h?esc(h+' redirect'+(h===1?'':'s')+' before the final destination'):'Direct destination or no redirect observed')+'</div></div><div class="lf-card"><h3>Why this verdict</h3><ul class="lf-reasons">'+rs.map(function(x){return'<li><i></i><div><strong>'+esc(x.title)+'</strong>'+(x.detail?'<span>'+esc(x.detail)+'</span>':'')+'</div></li>'}).join('')+'</ul></div></div><div class="lf-action">'+esc(action(d,r))+'</div>'+detailV2(d,r,rs)+'<div class="lf-actions"></div>';body.insertBefore(card,body.firstChild);var nativeDetail=card.querySelector('#cist-link-detail-v2');if(nativeDetail&&detailWasOpen)nativeDetail.open=true;if(nativeDetail)nativeDetail.addEventListener('toggle',function(){var t=nativeDetail.querySelector('.lf-detail-toggle');if(t)t.textContent=nativeDetail.open?'Hide details ↑':'View details ↓'});var actions=card.querySelector('.lf-actions'),share=document.getElementById('cist-mega-share');if(share){share.hidden=false;share.textContent='Share result on X';actions.appendChild(share)}var reset=document.getElementById('cist-unified-reset');if(reset){reset.classList.add('lf-reset');reset.textContent='Check another';actions.appendChild(reset)}var dis=document.createElement('p');dis.className='lf-disclaimer';dis.textContent='Automated checks reduce uncertainty; they cannot prove a link is safe. Verify the final domain before entering passwords or payment details.';actions.appendChild(dis);document.body.classList.add('cist-link-result-active')}
pulse();document.addEventListener('cist:mega-result',function(e){render(e&&e.detail?e.detail:null)});document.addEventListener('click',function(e){var t=e.target&&e.target.closest&&e.target.closest('#cist-unified-reset');if(!t)return;document.body.classList.remove('cist-link-result-active');var old=document.getElementById('cist-link-first-result');if(old)old.remove();if(input){input.value='';input.focus()}});
})();
</script>
'''

s = re.sub(r'\s*<style id="cist-link-first-home-v1-style">.*?</style>', '', s, count=1, flags=re.S)
s = re.sub(r'\s*<script id="cist-link-first-home-v1-script">.*?</script>', '', s, count=1, flags=re.S)
s = s.replace('</head>', STYLE + '\n</head>', 1).replace('</body>', SCRIPT + '\n</body>', 1)
for token in ['Can you trust', 'Paste a suspicious link', 'cist-link-first-home-v1-style', 'cist-link-first-result', 'cist-link-detail-v2', 'Detailed analysis', 'Redirect chain', 'Domain & response', 'Advanced technical details', 'detailV2(d,r,rs)', 'signal pulse']:
    if token not in s:
        raise RuntimeError('Link-first homepage guard failed: ' + token)
HOME.write_text(s, encoding='utf-8')
print('Applied link-first homepage: one field, one button, one verdict, one share loop, one return hook')
