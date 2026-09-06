#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-universal-home-result-v2-style">
.cist-detected-type{max-width:760px;margin:8px auto 0;text-align:center;color:var(--muted);font-size:11px;font-weight:780;min-height:16px}
.cist-detected-type strong{color:var(--text);font-weight:850}
#cist-result-v2{display:none;margin-top:14px;text-align:left}
body.cist-result-v2-active #cist-result-v2{display:block}
body.cist-result-v2-active #universal-summary,
body.cist-result-v2-active #risk-breakdown,
body.cist-result-v2-active #recommended-action,
body.cist-result-v2-active #why-verdict,
body.cist-result-v2-active #advice,
body.cist-result-v2-active #reputation{display:none!important}
.cist-result-v2-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}
.cist-result-v2-card{padding:13px 14px;border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--soft) 62%,transparent)}
.cist-result-v2-card.cist-result-v2-wide{grid-column:1/-1}
.cist-result-v2-label{display:block;margin:0 0 6px;color:var(--muted);font-size:10px;font-weight:900;letter-spacing:.075em;text-transform:uppercase}
.cist-result-v2-value{display:block;color:var(--text);font-size:14px;font-weight:850;line-height:1.35;overflow-wrap:anywhere}
.cist-result-v2-note{display:block;margin-top:4px;color:var(--muted);font-size:11px;line-height:1.45;overflow-wrap:anywhere}
.cist-result-v2-signals{display:grid;gap:7px;margin:0;padding:0;list-style:none}
.cist-result-v2-signals li{position:relative;padding-left:16px;color:var(--text);font-size:12px;line-height:1.45}
.cist-result-v2-signals li:before{content:'•';position:absolute;left:2px;color:var(--muted)}
.cist-result-v2-found{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:2px}
.cist-result-v2-found-item{padding:9px 10px;border:1px solid color-mix(in srgb,var(--line) 82%,transparent);border-radius:11px;background:color-mix(in srgb,var(--card) 78%,transparent);min-width:0}
.cist-result-v2-found-item small{display:block;color:var(--muted);font-size:9px;font-weight:850;text-transform:uppercase;letter-spacing:.05em}
.cist-result-v2-found-item strong{display:block;margin-top:3px;color:var(--text);font-size:11px;line-height:1.35;overflow-wrap:anywhere}
.cist-confidence-high{color:var(--green)!important}.cist-confidence-medium{color:var(--amber)!important}.cist-confidence-low{color:var(--red)!important}
body.cist-result-v2-active #technical{margin-top:12px!important}
body.cist-result-v2-active #technical summary{font-size:11px!important}
@media(max-width:700px){
 .cist-result-v2-grid{grid-template-columns:1fr}
 .cist-result-v2-card.cist-result-v2-wide{grid-column:auto}
 .cist-result-v2-found{grid-template-columns:1fr}
 .cist-result-v2-card{padding:12px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-universal-home-result-v2-script">
(function(){
  var input=document.getElementById('url');
  var form=document.getElementById('scan-form');
  var result=document.getElementById('result');
  var card=document.getElementById('result-card');
  var summary=document.getElementById('summary');
  var technical=document.getElementById('technical');
  if(!input||!form||!result||!card)return;

  input.setAttribute('placeholder','Paste a link, email, message, social profile or crypto address');
  input.setAttribute('aria-label','Paste something suspicious to analyze');

  var detected=document.createElement('div');
  detected.className='cist-detected-type';
  detected.setAttribute('aria-live','polite');
  form.insertAdjacentElement('afterend',detected);

  var panel=document.createElement('section');
  panel.id='cist-result-v2';
  panel.setAttribute('aria-label','Scan result details');
  panel.innerHTML=''+
    '<div class="cist-result-v2-grid">'+
      '<div class="cist-result-v2-card"><span class="cist-result-v2-label">Confidence</span><strong id="cist-confidence" class="cist-result-v2-value">—</strong><small id="cist-confidence-note" class="cist-result-v2-note"></small></div>'+
      '<div class="cist-result-v2-card"><span class="cist-result-v2-label">What to do</span><strong id="cist-action" class="cist-result-v2-value">—</strong><small id="cist-action-note" class="cist-result-v2-note"></small></div>'+
      '<div class="cist-result-v2-card cist-result-v2-wide"><span class="cist-result-v2-label">Why</span><ul id="cist-why" class="cist-result-v2-signals"></ul></div>'+
      '<div class="cist-result-v2-card cist-result-v2-wide"><span class="cist-result-v2-label">What we found</span><div id="cist-found" class="cist-result-v2-found"></div></div>'+
    '</div>';
  if(summary&&summary.parentNode)summary.insertAdjacentElement('afterend',panel);else card.appendChild(panel);

  function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
  function value(){return clean(input.value)}
  function hostFrom(v){try{return new URL(v).hostname.replace(/^www\./,'')}catch(e){return''}}
  function isSocialUrl(v){
    try{var u=new URL(v),h=u.hostname.toLowerCase(),p=u.pathname.split('/').filter(Boolean);if(!p.length)return false;
      if(/(^|\.)instagram\.com$/.test(h))return !['p','reel','reels','stories','explore','accounts','direct'].includes((p[0]||'').toLowerCase());
      if(/(^|\.)tiktok\.com$/.test(h))return p.some(function(x){return x.charAt(0)==='@'});
      if(/(^|\.)(x\.com|twitter\.com)$/.test(h))return !['home','explore','search','messages','settings','i','intent'].includes((p[0]||'').toLowerCase());
      if(/(^|\.)facebook\.com$/.test(h)||h==='m.facebook.com')return !['watch','groups','marketplace','gaming','events','reel','reels','share'].includes((p[0]||'').toLowerCase());
      if(h==='t.me'||h==='telegram.me'||h==='www.telegram.me')return !['joinchat','share','proxy','socks'].includes((p[0]||'').toLowerCase());
    }catch(e){}return false;
  }
  function detect(v){
    v=clean(v);if(!v)return'';
    if(/^@[A-Za-z0-9._-]{2,64}$/.test(v)||(/^https?:\/\//i.test(v)&&isSocialUrl(v)))return'Social profile';
    if(/^https?:\/\//i.test(v))return'URL';
    if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))return'Email';
    if(/^0x[a-fA-F0-9]{40}$/.test(v)||/^bc1[ac-hj-np-z02-9]{11,87}$/i.test(v)||/^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(v)||/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(v))return'Crypto address';
    return'Message';
  }
  function updateDetected(){var t=detect(value());detected.innerHTML=t?'Detected automatically: <strong>'+t+'</strong>':'Automatic type detection';}

  function status(){if(card.classList.contains('status-high'))return'high';if(card.classList.contains('status-caution'))return'caution';if(card.classList.contains('status-low'))return'low';return'unknown'}
  function signals(){
    var out=[];var list=document.querySelectorAll('#signals li');
    for(var i=0;i<list.length&&out.length<3;i++){var t=clean(list[i].textContent);if(t&&out.indexOf(t)<0)out.push(t)}
    if(!out.length&&summary){var s=clean(summary.textContent);if(s)out.push(s)}
    if(!out.length)out.push('The available checks did not provide enough detail for a stronger explanation.');
    return out;
  }
  function finalHost(){
    var d=window.cistUniversalResultData||{};
    return clean(d.finalHost)||hostFrom(clean(d.finalUrl))||hostFrom(value());
  }
  function threatChecked(){return card.classList.contains('reputation-checked-safe')||document.querySelector('.reputation-checked-safe')!==null}
  function confidence(s,sigs){
    if(s==='unknown')return{v:'Low',c:'cist-confidence-low',n:'The scan could not complete enough checks to support a strong conclusion.'};
    if(s==='high')return sigs.length>=2?{v:'High',c:'cist-confidence-high',n:'Multiple warning signals support this verdict.'}:{v:'Medium',c:'cist-confidence-medium',n:'A strong warning was found, but supporting evidence is limited.'};
    if(s==='caution')return{v:'Medium',c:'cist-confidence-medium',n:'Some signals need verification before you trust this input.'};
    if(threatChecked())return{v:'High',c:'cist-confidence-high',n:'The available local checks and known threat-list checks completed.'};
    return{v:'Medium',c:'cist-confidence-medium',n:'No major warning was found, but not every risk can be verified.'};
  }
  function action(s){
    var av=document.getElementById('universal-advice-value'),an=document.getElementById('universal-advice-note');
    var v=clean(av&&av.textContent),n=clean(an&&an.textContent);
    if(s==='high')return{v:'Do not open or act on it.',n:'Verify the sender or destination independently before doing anything else.'};
    if(s==='caution')return{v:v||'Verify it before continuing.',n:n||'Confirm the sender, website or request through another trusted channel.'};
    if(s==='low')return{v:v||'Continue only if you expected it.',n:n||'Stay cautious if it asks for a password, payment or download.'};
    return{v:'Do not rely on this result yet.',n:'The scan is incomplete or uncertain.'};
  }
  function verdictCopy(s){
    var verdict=document.getElementById('verdict');if(!verdict)return;
    verdict.textContent=s==='high'?'High risk':s==='caution'?'Suspicious':s==='low'?'Looks safe':'Incomplete';
  }
  function foundItems(s,type){
    var items=[['Input type',type||'Unknown'],['Risk level',s==='high'?'High risk':s==='caution'?'Needs verification':s==='low'?'No major warning':'Incomplete']];
    var host=finalHost();if(host)items.push(['Destination',host]);
    else if(type==='Message'){var m=value().match(/https?:\/\/[^\s<>"']+/i);if(m)items.push(['Embedded link',hostFrom(m[0])||m[0]]);else items.push(['Content','Text message']);}
    else if(type==='Email'){var parts=value().split('@');if(parts[1])items.push(['Domain',parts[1].toLowerCase()]);}
    else if(type==='Crypto address')items.push(['Address','Format analyzed']);
    else if(type==='Social profile')items.push(['Profile','Identity signals analyzed']);
    return items.slice(0,3);
  }
  function render(){
    if(result.classList.contains('hidden')){document.body.classList.remove('cist-result-v2-active');return}
    var s=status(),type=detect(value()),sigs=signals(),conf=confidence(s,sigs),act=action(s);
    verdictCopy(s);
    var ce=document.getElementById('cist-confidence'),cn=document.getElementById('cist-confidence-note');
    if(ce){ce.textContent=conf.v;ce.className='cist-result-v2-value '+conf.c}if(cn)cn.textContent=conf.n;
    var ae=document.getElementById('cist-action'),an=document.getElementById('cist-action-note');if(ae)ae.textContent=act.v;if(an)an.textContent=act.n;
    var why=document.getElementById('cist-why');if(why){why.innerHTML='';sigs.forEach(function(x){var li=document.createElement('li');li.textContent=x;why.appendChild(li)})}
    var found=document.getElementById('cist-found');if(found){found.innerHTML='';foundItems(s,type).forEach(function(it){var box=document.createElement('div');box.className='cist-result-v2-found-item';var sm=document.createElement('small');sm.textContent=it[0];var st=document.createElement('strong');st.textContent=it[1];box.appendChild(sm);box.appendChild(st);found.appendChild(box)})}
    document.body.classList.add('cist-result-v2-active');
    if(technical){technical.classList.remove('hidden');technical.open=false}
  }

  input.addEventListener('input',function(){updateDetected();document.body.classList.remove('cist-result-v2-active')});
  form.addEventListener('submit',function(){document.body.classList.remove('cist-result-v2-active');setTimeout(render,0)},true);
  document.addEventListener('cist:result-updated',function(){setTimeout(render,0)});
  new MutationObserver(function(){setTimeout(render,0)}).observe(card,{attributes:true,attributeFilter:['class']});
  updateDetected();render();
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')

    source = re.sub(r'\s*<style id="cist-universal-home-result-v2-style">.*?</style>', '', source, count=1, flags=re.S)
    source = re.sub(r'\s*<script id="cist-universal-home-result-v2-script">.*?</script>', '', source, count=1, flags=re.S)

    # Make the universal promise part of the static HTML, not only client-side copy.
    h1_pattern = r'(<h1\b[^>]*>).*?(</h1>)'
    source, n = re.subn(h1_pattern, r'\1Check it before you trust it.\2', source, count=1, flags=re.S|re.I)
    if n != 1:
        raise RuntimeError('Homepage H1 not found')

    source = source.replace('</head>', STYLE + '\n</head>', 1)
    source = source.replace('</body>', SCRIPT + '\n</body>', 1)

    required = [
        'Check it before you trust it.',
        'Paste a link, email, message, social profile or crypto address',
        'Detected automatically:',
        'id="cist-result-v2"',
        'Confidence',
        'What to do',
        'What we found',
        "'High risk'",
        "'Suspicious'",
        "'Looks safe'",
        'Technical details'
    ]
    for token in required:
        if token not in source:
            raise RuntimeError(f'Universal home/result V2 guard failed: missing {token}')

    HOME.write_text(source, encoding='utf-8')
    print('Applied universal homepage promise and structured scan result V2')


if __name__ == '__main__':
    main()
