#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

if not HOME.is_file():
    raise RuntimeError('Homepage not found')

s = HOME.read_text(encoding='utf-8')

# Homepage positioning: link-first, explanation-first.
s = re.sub(r'<title>.*?</title>', '<title>Can I Share This? — Check Where a Link Goes Before You Open It</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Paste a suspicious or shortened link to reveal its final destination, redirects and trust signals. Can I Share This? explains why the link may or may not deserve your trust.">', s, count=1)
s = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Can you trust this link? — Can I Share This?">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="See where a link really goes, what changed on the way, and why it may or may not deserve your trust.">', s, count=1)
s = re.sub(r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="Can you trust this link? — Can I Share This?">', s, count=1)
s = re.sub(r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="Reveal the destination, redirects and trust signals before you open a suspicious link.">', s, count=1)

hero_pattern = re.compile(r'<p class="eyebrow">.*?</p>\s*<h1 id="page-title">.*?</h1>\s*<p class="sub">.*?</p>', re.S)
hero = '''<p class="eyebrow">Link trust checker</p>
      <h1 id="page-title">Can you trust <span class="cist-title-end">this link?</span></h1>
      <p class="sub">Paste a suspicious or shortened link. See where it really goes, what changed on the way, and why it may—or may not—deserve your trust.</p>'''
s, hero_count = hero_pattern.subn(hero, s, count=1)
if hero_count != 1:
    raise RuntimeError('Hero copy not found')

s = re.sub(r'placeholder="Paste a link,[^"]*"', 'placeholder="Paste a suspicious link…"', s, count=1)
s = re.sub(r'(<button[^>]+id="analyze"[^>]*>).*?(</button>)', r'\1Check link\2', s, count=1, flags=re.S)

STYLE = r'''
<style id="cist-link-first-home-v1-style">
/* One field. One button. One verdict. */
#cist-daily-rail,
#cist-scam-signals-rail,
#cist-mega-badges,
#cist-check-selector,
#cist-other-checks-toggle,
.cist-detected-type,
#input-kind,
#cist-unified-home-scanner #choose-image,
#cist-unified-home-scanner #paste,
#cist-unified-home-scanner #image-file,
#cist-unified-home-scanner #camera-file{display:none!important}

.hero{padding-top:clamp(62px,8vw,104px)!important}
.hero .eyebrow{margin-bottom:12px!important;color:var(--cist-accent,#788ff7)!important;letter-spacing:.12em!important}
.hero h1{max-width:760px!important;margin-left:auto!important;margin-right:auto!important;font-size:clamp(46px,7.2vw,82px)!important;line-height:.96!important;letter-spacing:-.055em!important}
.hero .sub{max-width:670px!important;margin:20px auto 0!important;font-size:clamp(15px,2vw,18px)!important;line-height:1.55!important;color:var(--muted)!important}

#cist-unified-home-scanner{
  width:min(760px,calc(100% - 28px))!important;
  margin-top:28px!important;
  padding:9px!important;
  border-radius:18px!important;
}
#cist-unified-home-scanner #scan-form{
  grid-template-columns:minmax(0,1fr) auto!important;
  gap:8px!important;
}
#cist-unified-home-scanner .input-wrap{
  grid-column:auto!important;
  height:56px!important;
  border-bottom:0!important;
  border-radius:13px!important;
}
#cist-unified-home-scanner #url{height:56px!important;font-size:15px!important;padding:0 12px!important}
#cist-unified-home-scanner #analyze{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  min-width:126px!important;
  height:48px!important;
  padding:0 18px!important;
  font-size:13px!important;
}
#cist-unified-home-note{margin-top:8px!important;font-size:10px!important}

#cist-return-hook{
  width:min(760px,calc(100% - 28px));
  margin:12px auto 0;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  flex-wrap:wrap;
  color:var(--muted);
  font-size:10.5px;
  line-height:1.35;
  text-align:center;
}
#cist-return-hook .live-dot{width:6px;height:6px;border-radius:999px;background:#61c99a;box-shadow:0 0 0 4px color-mix(in srgb,#61c99a 14%,transparent)}
#cist-return-hook strong{color:var(--text);font-weight:850}
#cist-return-hook .sep{opacity:.45}

body.cist-link-result-active #cist-mega-v2-panel .cist-mega-v2-head{display:none!important}
body.cist-link-result-active #cist-mega-v2-panel .cist-mega-v2-body > *{display:none!important}
body.cist-link-result-active #cist-mega-v2-panel .cist-mega-v2-body > #cist-link-first-result{display:block!important}
#cist-link-first-result{padding:0!important}
#cist-link-first-result .lf-verdict{
  padding:26px 26px 22px;
  border-bottom:1px solid var(--line);
}
#cist-link-first-result .lf-kicker{font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
#cist-link-first-result .lf-label{margin:7px 0 0;font-size:clamp(36px,7vw,58px);line-height:.98;letter-spacing:-.05em;font-weight:950}
#cist-link-first-result[data-risk="high"] .lf-label{color:#ff7770}
#cist-link-first-result[data-risk="caution"] .lf-label{color:#f0b85b}
#cist-link-first-result[data-risk="low"] .lf-label{color:#61c99a}
#cist-link-first-result .lf-headline{max-width:650px;margin:12px 0 0;color:var(--muted);font-size:14px;line-height:1.5}
#cist-link-first-result .lf-grid{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:12px;padding:20px 26px 8px}
#cist-link-first-result .lf-card{border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--soft) 55%,transparent);padding:15px}
#cist-link-first-result .lf-card h3{margin:0 0 8px;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
#cist-link-first-result .lf-destination{font-size:18px;font-weight:900;letter-spacing:-.02em;overflow-wrap:anywhere}
#cist-link-first-result .lf-route{margin-top:5px;color:var(--muted);font-size:10px}
#cist-link-first-result .lf-reasons{display:grid;gap:9px;margin:0;padding:0;list-style:none}
#cist-link-first-result .lf-reasons li{display:grid;grid-template-columns:7px 1fr;gap:9px;align-items:start}
#cist-link-first-result .lf-reasons i{width:7px;height:7px;margin-top:6px;border-radius:999px;background:var(--cist-accent,#788ff7)}
#cist-link-first-result[data-risk="high"] .lf-reasons i{background:#ff7770}
#cist-link-first-result[data-risk="caution"] .lf-reasons i{background:#f0b85b}
#cist-link-first-result[data-risk="low"] .lf-reasons i{background:#61c99a}
#cist-link-first-result .lf-reasons strong{display:block;font-size:12px;line-height:1.35}
#cist-link-first-result .lf-reasons span{display:block;margin-top:2px;color:var(--muted);font-size:10.5px;line-height:1.45}
#cist-link-first-result .lf-action{margin:12px 26px 0;padding:14px 15px;border-left:3px solid var(--cist-accent,#788ff7);border-radius:10px;background:color-mix(in srgb,var(--cist-accent,#788ff7) 7%,transparent);font-size:12px;font-weight:800;line-height:1.5}
#cist-link-first-result .lf-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:18px 26px 24px}
#cist-link-first-result .lf-actions #cist-mega-share{display:inline-flex!important;align-items:center!important;justify-content:center!important;min-height:42px!important;padding:0 16px!important;border-radius:10px!important;background:var(--cist-accent,#788ff7)!important;color:#fff!important;border:0!important;font-weight:900!important}
#cist-link-first-result .lf-reset{appearance:none;border:1px solid var(--line);border-radius:10px;background:transparent;color:var(--text);min-height:42px;padding:0 14px;font:inherit;font-size:11px;font-weight:800;cursor:pointer}
#cist-link-first-result .lf-disclaimer{width:100%;margin:4px 0 0;color:var(--muted);font-size:9.5px;line-height:1.45}

@media(max-width:700px){
  .hero{padding-top:48px!important}
  .hero h1{font-size:clamp(42px,13vw,62px)!important}
  #cist-unified-home-scanner{width:calc(100% - 24px)!important;margin-top:22px!important}
  #cist-unified-home-scanner #scan-form{grid-template-columns:1fr!important}
  #cist-unified-home-scanner .input-wrap{grid-column:1!important;height:52px!important}
  #cist-unified-home-scanner #url{height:52px!important}
  #cist-unified-home-scanner #analyze{width:100%!important;height:48px!important}
  #cist-link-first-result .lf-verdict{padding:21px 18px 18px}
  #cist-link-first-result .lf-grid{grid-template-columns:1fr;padding:16px 18px 6px}
  #cist-link-first-result .lf-action{margin:10px 18px 0}
  #cist-link-first-result .lf-actions{padding:16px 18px 20px}
  #cist-link-first-result .lf-actions #cist-mega-share,#cist-link-first-result .lf-reset{flex:1}
}
</style>
'''

SCRIPT = r'''
<script id="cist-link-first-home-v1-script">
(function(){
  var input=document.getElementById('url');
  var analyze=document.getElementById('analyze');
  var note=document.getElementById('cist-unified-home-note');
  if(input){
    input.placeholder='Paste a suspicious link…';
    input.setAttribute('aria-label','Paste a suspicious or shortened link');
    input.setAttribute('inputmode','url');
    input.setAttribute('autocomplete','off');
  }
  if(analyze)analyze.textContent='Check link';
  if(note)note.innerHTML='<span>Private by design</span><span class="cist-dot">·</span><span>No account</span><span class="cist-dot">·</span><span>Fresh check every time</span>';

  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(v,max){return String(v==null?'':v).replace(/\s+/g,' ').trim().slice(0,max||220)}
  function firstKey(root,names,maxDepth){
    var seen=new Set();
    function walk(v,depth){
      if(v==null||depth>(maxDepth||5)||typeof v!=='object'||seen.has(v))return null;
      seen.add(v);
      for(var i=0;i<names.length;i++){var n=names[i];if(Object.prototype.hasOwnProperty.call(v,n)&&v[n]!=null&&v[n]!=='')return v[n]}
      var keys=Object.keys(v).slice(0,80);
      for(var j=0;j<keys.length;j++){
        var x=v[keys[j]];
        if(x&&typeof x==='object'){var hit=walk(x,depth+1);if(hit!=null)return hit}
      }
      return null;
    }
    return walk(root,0);
  }
  function riskOf(d){
    var v=(d&&d.megaScanner&&d.megaScanner.finalRisk)||(d&&d.shareSummary&&d.shareSummary.verdict)||(d&&d.explanation&&d.explanation.verdict)||firstKey(d,['finalRisk','verdict','riskLevel','status'],4)||'unknown';
    v=String(v).toLowerCase();
    if(/high|danger|malicious|unsafe/.test(v))return'high';
    if(/caution|medium|verify|suspicious|warn/.test(v))return'caution';
    if(/low|safe|clear|normal|no major/.test(v))return'low';
    return'unknown';
  }
  function labelFor(r){return r==='high'?'HIGH RISK':r==='caution'?'VERIFY FIRST':r==='low'?'NO MAJOR WARNING':'INCOMPLETE'}
  function destinationOf(d){
    var raw=firstKey(d,['finalUrl','finalURL','resolvedUrl','destinationUrl'],5);
    var host=firstKey(d,['finalHost','resolvedHost','destinationHost'],5);
    if(raw){try{host=new URL(String(raw)).hostname||host}catch(_){}}
    if(!host&&d&&d.detectedElements&&Array.isArray(d.detectedElements.domains)&&d.detectedElements.domains.length)host=d.detectedElements.domains[0];
    return clean(host||'Destination could not be fully resolved',140);
  }
  function redirectsOf(d){
    var r=firstKey(d,['redirects','redirectChain'],5);
    return Array.isArray(r)?r.length:0;
  }
  function reasonsOf(d,risk){
    var candidates=(d&&d.shareSummary&&d.shareSummary.reasons)||(d&&d.explanation&&d.explanation.reasons)||firstKey(d,['signals'],4)||[];
    if(!Array.isArray(candidates))candidates=[];
    var out=candidates.slice(0,3).map(function(x){return{title:clean((x&&x.title)||'Signal reviewed',70),detail:clean((x&&x.detail)||'',145)}}).filter(function(x){return x.title});
    if(!out.length){
      if(risk==='low')out.push({title:'No obvious suspicious pattern found',detail:'The automated checks did not find a major warning in this snapshot.'});
      else out.push({title:'Fresh verification recommended',detail:'The scan did not have enough evidence for a stronger conclusion.'});
    }
    return out;
  }
  function headlineOf(d,risk){
    var h=(d&&d.shareSummary&&d.shareSummary.headline)||(d&&d.explanation&&d.explanation.headline)||firstKey(d,['summary'],3);
    if(h)return clean(h,180);
    if(risk==='high')return'This link contains signals that deserve caution before you open it.';
    if(risk==='caution')return'Some signals need verification before you trust this destination.';
    if(risk==='low')return'No major warning was found, but the final destination still matters.';
    return'The scan could not establish a complete verdict.';
  }
  function actionOf(d,risk){
    var a=(d&&d.shareSummary&&d.shareSummary.action)||(d&&d.explanation&&d.explanation.action);
    if(a)return clean(a,220);
    if(risk==='high')return'Do not enter passwords, payment details or download files until you verify the final domain independently.';
    if(risk==='caution')return'Confirm that the final domain is the one you expected before signing in, paying or downloading anything.';
    return'Check that the final domain matches what you expected before entering sensitive information.';
  }

  function ensurePulse(){
    if(document.getElementById('cist-return-hook'))return;
    var anchor=document.getElementById('cist-unified-home-scanner')||document.getElementById('scan-form');
    if(!anchor)return;
    var pulse=document.createElement('div');
    pulse.id='cist-return-hook';
    pulse.innerHTML='<span class="live-dot" aria-hidden="true"></span><strong>Today\'s signal pulse</strong><span class="sep">·</span><span><b id="cist-return-scans">—</b> checks</span><span class="sep">·</span><span><b id="cist-return-warnings">—</b> warning signals</span>';
    anchor.insertAdjacentElement('afterend',pulse);
    var srcScans=document.getElementById('cist-daily-scans');
    var srcWarnings=document.getElementById('cist-daily-warnings')||document.getElementById('cist-signal-total');
    function sync(){
      var a=document.getElementById('cist-return-scans'),b=document.getElementById('cist-return-warnings');
      if(a&&srcScans&&clean(srcScans.textContent,20))a.textContent=clean(srcScans.textContent,20);
      if(b&&srcWarnings&&clean(srcWarnings.textContent,20))b.textContent=clean(srcWarnings.textContent,20);
    }
    sync();
    [srcScans,srcWarnings].filter(Boolean).forEach(function(n){new MutationObserver(sync).observe(n,{childList:true,subtree:true,characterData:true})});
  }

  function renderSimple(d){
    if(!d||typeof d!=='object')return;
    var panel=document.getElementById('cist-mega-v2-panel');
    if(!panel)return;
    var body=panel.querySelector('.cist-mega-v2-body')||panel;
    var old=document.getElementById('cist-link-first-result');
    if(old)old.remove();
    var risk=riskOf(d),label=labelFor(risk),dest=destinationOf(d),redirects=redirectsOf(d),reasons=reasonsOf(d,risk),headline=headlineOf(d,risk),action=actionOf(d,risk);
    var card=document.createElement('section');
    card.id='cist-link-first-result';
    card.setAttribute('data-risk',risk);
    card.setAttribute('aria-label','Link trust verdict');
    card.innerHTML='<div class="lf-verdict"><div class="lf-kicker">Link trust verdict</div><div class="lf-label">'+esc(label)+'</div><p class="lf-headline">'+esc(headline)+'</p></div>'+
      '<div class="lf-grid"><div class="lf-card"><h3>Where it goes</h3><div class="lf-destination">'+esc(dest)+'</div><div class="lf-route">'+(redirects?esc(String(redirects)+' redirect'+(redirects===1?'':'s')+' before the final destination'):'Direct destination or no redirect observed')+'</div></div>'+
      '<div class="lf-card"><h3>Why this verdict</h3><ul class="lf-reasons">'+reasons.map(function(x){return'<li><i></i><div><strong>'+esc(x.title)+'</strong>'+(x.detail?'<span>'+esc(x.detail)+'</span>':'')+'</div></li>'}).join('')+'</ul></div></div>'+
      '<div class="lf-action">'+esc(action)+'</div><div class="lf-actions"></div>';
    body.insertBefore(card,body.firstChild);
    var actions=card.querySelector('.lf-actions');
    var share=document.getElementById('cist-mega-share');
    if(share){share.hidden=false;share.textContent='Share result on X';actions.appendChild(share)}
    var reset=document.getElementById('cist-unified-reset');
    if(reset){reset.classList.add('lf-reset');reset.textContent='Check another';actions.appendChild(reset)}
    var disclaimer=document.createElement('p');
    disclaimer.className='lf-disclaimer';
    disclaimer.textContent='Automated checks reduce uncertainty; they cannot prove a link is safe. Verify the final domain before entering passwords or payment details.';
    actions.appendChild(disclaimer);
    document.body.classList.add('cist-link-result-active');
  }

  ensurePulse();
  document.addEventListener('cist:mega-result',function(e){renderSimple(e&&e.detail?e.detail:null)});
  document.addEventListener('click',function(e){
    var t=e.target&&e.target.closest&&e.target.closest('#cist-unified-reset');
    if(!t)return;
    document.body.classList.remove('cist-link-result-active');
    var old=document.getElementById('cist-link-first-result');if(old)old.remove();
    if(input){input.value='';input.focus()}
  });
})();
</script>
'''

s = re.sub(r'\s*<style id="cist-link-first-home-v1-style">.*?</style>', '', s, count=1, flags=re.S)
s = re.sub(r'\s*<script id="cist-link-first-home-v1-script">.*?</script>', '', s, count=1, flags=re.S)
s = s.replace('</head>', STYLE + '\n</head>', 1)
s = s.replace('</body>', SCRIPT + '\n</body>', 1)

for token in ['Can you trust', 'Paste a suspicious link', 'cist-link-first-home-v1-style', 'cist-link-first-result', "Today's signal pulse"]:
    if token not in s:
        raise RuntimeError('Link-first homepage guard failed: ' + token)

HOME.write_text(s, encoding='utf-8')
print('Applied link-first homepage: one field, one button, one verdict, one share loop, one return hook')
