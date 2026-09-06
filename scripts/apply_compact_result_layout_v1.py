#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-compact-result-v1-style">
body.cist-compact-result-active #cist-result-v2,
body.cist-compact-result-active #universal-summary,
body.cist-compact-result-active .universal-summary,
body.cist-compact-result-active #cist-destination,
body.cist-compact-result-active #url-domain-age,
body.cist-compact-result-active #signals,
body.cist-compact-result-active #risk-breakdown,
body.cist-compact-result-active #recommended-action,
body.cist-compact-result-active #why-verdict,
body.cist-compact-result-active #advice,
body.cist-compact-result-active #reputation{display:none!important}

body.cist-compact-result-active #result-card{padding:22px!important}
body.cist-compact-result-active .result-top{align-items:center!important}
body.cist-compact-result-active .result-main{min-width:0;flex:1}
body.cist-compact-result-active .result-main h2{display:inline;vertical-align:middle}
.cist-compact-confidence{display:inline-flex;align-items:center;margin-left:9px;padding:5px 8px;border:1px solid var(--line);border-radius:999px;background:var(--soft);color:var(--muted);font-size:9px;font-weight:900;letter-spacing:.055em;text-transform:uppercase;vertical-align:middle;white-space:nowrap}
.status-low .cist-compact-confidence{color:var(--green);background:color-mix(in srgb,var(--green) 8%,var(--soft));border-color:color-mix(in srgb,var(--green) 24%,var(--line))}
.status-caution .cist-compact-confidence{color:var(--amber);background:color-mix(in srgb,var(--amber) 8%,var(--soft));border-color:color-mix(in srgb,var(--amber) 25%,var(--line))}
.status-high .cist-compact-confidence{color:var(--red);background:color-mix(in srgb,var(--red) 8%,var(--soft));border-color:color-mix(in srgb,var(--red) 25%,var(--line))}

#cist-compact-result{margin-top:17px;text-align:left}
.cist-compact-action{padding:14px 15px;border:1px solid var(--line);border-radius:14px;background:color-mix(in srgb,var(--soft) 56%,transparent)}
.cist-compact-label{display:block;color:var(--muted);font-size:9px;font-weight:900;letter-spacing:.075em;text-transform:uppercase}
.cist-compact-action strong{display:block;margin-top:5px;color:var(--text);font-size:14px;line-height:1.35}
.cist-compact-action p{margin:3px 0 0;color:var(--muted);font-size:11px;line-height:1.45}
.cist-key-title{margin:16px 0 8px;color:var(--text);font-size:11px;font-weight:900;letter-spacing:.01em}
.cist-key-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.cist-key-item{display:flex;align-items:center;gap:10px;min-width:0;padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--card) 88%,var(--soft))}
.cist-key-icon{display:grid;place-items:center;width:28px;height:28px;flex:0 0 auto;border-radius:9px;background:var(--soft);font-size:14px}
.cist-key-copy{min-width:0}.cist-key-copy small{display:block;color:var(--muted);font-size:8px;font-weight:850;letter-spacing:.055em;text-transform:uppercase}.cist-key-copy strong{display:block;margin-top:2px;color:var(--text);font-size:11px;line-height:1.3;overflow-wrap:anywhere}
.cist-compact-why{margin-top:10px;padding:10px 12px;border-left:2px solid color-mix(in srgb,var(--cist-accent,#788ff7) 52%,var(--line));color:var(--muted);font-size:10px;line-height:1.45}
.cist-compact-why strong{color:var(--text)}
body.cist-compact-result-active #actions{display:flex!important;margin-top:14px!important;gap:8px!important}
body.cist-compact-result-active #actions #deep{display:none!important}
body.cist-compact-result-active #again{order:1;background:var(--cist-accent,#788ff7)!important;color:#fff!important;border-color:transparent!important}
body.cist-compact-result-active #share{order:2}
body.cist-compact-result-active #technical{margin-top:13px!important;padding-top:12px!important}
body.cist-compact-result-active #technical summary{font-size:11px!important}
body.cist-compact-result-active #technical>p,
body.cist-compact-result-active #technical .technical-intro{font-size:10px!important;line-height:1.4!important}

@media(max-width:700px){
 body.cist-compact-result-active #result-card{padding:16px!important}
 body.cist-compact-result-active .result-top{align-items:flex-start!important}
 .cist-compact-confidence{display:flex!important;width:max-content;margin:6px 0 0 0}
 .cist-key-grid{grid-template-columns:1fr}
 .cist-compact-action{padding:13px}
 .cist-key-item{padding:10px 11px}
 body.cist-compact-result-active #actions{display:grid!important;grid-template-columns:1fr 1fr!important}
 body.cist-compact-result-active #actions button{width:100%!important;min-height:44px}
}
</style>
'''

SCRIPT = r'''
<script id="cist-compact-result-v1-script">
(function(){
  var result=document.getElementById('result'),card=document.getElementById('result-card'),form=document.getElementById('scan-form'),input=document.getElementById('url');
  var verdict=document.getElementById('verdict'),summary=document.getElementById('summary');
  if(!result||!card||!form||!input||!verdict)return;

  function clean(v){return String(v||'').replace(/\s+/g,' ').trim()}
  function status(){if(card.classList.contains('status-high'))return'high';if(card.classList.contains('status-caution'))return'caution';if(card.classList.contains('status-low'))return'low';return'unknown'}
  function text(id){var el=document.getElementById(id);return clean(el&&el.textContent)}
  function found(label){
    var items=document.querySelectorAll('#cist-found .cist-result-v2-found-item');
    for(var i=0;i<items.length;i++){
      var l=clean(items[i].querySelector('small')&&items[i].querySelector('small').textContent).toLowerCase();
      if(l===String(label).toLowerCase())return clean(items[i].querySelector('strong')&&items[i].querySelector('strong').textContent);
    }
    return'';
  }
  function tech(label){
    var items=document.querySelectorAll('#tech-grid .tech');
    for(var i=0;i<items.length;i++){
      var l=clean(items[i].querySelector('span')&&items[i].querySelector('span').textContent).toLowerCase();
      if(l.indexOf(String(label).toLowerCase())>=0)return clean(items[i].querySelector('strong')&&items[i].querySelector('strong').textContent);
    }
    return'';
  }
  function isUrl(){return found('Input type').toLowerCase()==='url'||/^https?:\/\//i.test(clean(input.value))}
  function finalHost(){var d=window.cistUniversalResultData||{};return clean(d.finalHost)||found('Destination')||tech('where this link goes')||tech('final host')||''}
  function redirectCount(){var d=window.cistUniversalResultData||{};if(Array.isArray(d.redirects))return d.redirects.length;var t=tech('redirects');var n=parseInt(t,10);return Number.isFinite(n)?n:null}
  function confidence(){var c=text('cist-confidence');return c&&c!=='—'?c:''}
  function action(){var a=text('cist-action');return a&&a!=='—'?a:''}
  function actionNote(){return text('cist-action-note')}
  function why(){var w=document.querySelector('#cist-why li');return clean(w&&w.textContent)||clean(document.querySelector('#signals li')&&document.querySelector('#signals li').textContent)||clean(summary&&summary.textContent)}
  function domainAge(){var a=text('url-domain-age-value');return a&&a!=='Checking registration age…'?a:tech('domain age')}
  function threatLabel(){var s=status();if(s==='high')return'Warning found';if(s==='caution')return'Needs review';if(s==='low')return'No known match';return'Incomplete'}
  function icon(label){var l=String(label).toLowerCase();if(l.indexOf('age')>=0)return'🕒';if(l.indexOf('destination')>=0||l.indexOf('domain')>=0)return'🌐';if(l.indexOf('redirect')>=0)return'↪️';if(l.indexOf('threat')>=0||l.indexOf('reputation')>=0)return'🛡️';if(l.indexOf('email')>=0)return'✉️';if(l.indexOf('profile')>=0)return'👤';if(l.indexOf('content')>=0||l.indexOf('message')>=0)return'💬';if(l.indexOf('address')>=0)return'₿';return'✓'}
  function addItem(grid,label,value){if(!value)return;var item=document.createElement('div');item.className='cist-key-item';var ic=document.createElement('span');ic.className='cist-key-icon';ic.setAttribute('aria-hidden','true');ic.textContent=icon(label);var copy=document.createElement('div');copy.className='cist-key-copy';var sm=document.createElement('small');sm.textContent=label;var st=document.createElement('strong');st.textContent=value;copy.appendChild(sm);copy.appendChild(st);item.appendChild(ic);item.appendChild(copy);grid.appendChild(item)}

  function ensure(){
    var panel=document.getElementById('cist-compact-result');if(panel)return panel;
    panel=document.createElement('section');panel.id='cist-compact-result';panel.setAttribute('aria-label','Essential scan result');
    var top=card.querySelector('.result-top');if(top)top.insertAdjacentElement('afterend',panel);else card.insertBefore(panel,card.firstChild);
    return panel;
  }
  function ensureBadge(){
    var main=card.querySelector('.result-main');if(!main)return null;var b=document.getElementById('cist-compact-confidence');if(!b){b=document.createElement('span');b.id='cist-compact-confidence';b.className='cist-compact-confidence';verdict.insertAdjacentElement('afterend',b)}return b;
  }
  function render(){
    if(result.classList.contains('hidden')||/analyz|check(ing)?…?/i.test(clean(verdict.textContent))){document.body.classList.remove('cist-compact-result-active');return}
    var panel=ensure(),badge=ensureBadge(),conf=confidence(),act=action(),note=actionNote(),reason=why(),urlMode=isUrl();
    if(badge){badge.textContent=conf?conf+' confidence':'Result';badge.style.display='inline-flex'}
    panel.innerHTML='';
    var actionBox=document.createElement('div');actionBox.className='cist-compact-action';var lab=document.createElement('span');lab.className='cist-compact-label';lab.textContent='What you should do';var strong=document.createElement('strong');strong.textContent=act||(status()==='high'?'Do not open or act on it.':status()==='caution'?'Verify it before continuing.':'Continue only if you expected it.');actionBox.appendChild(lab);actionBox.appendChild(strong);if(note){var p=document.createElement('p');p.textContent=note;actionBox.appendChild(p)}panel.appendChild(actionBox);
    var title=document.createElement('div');title.className='cist-key-title';title.textContent='Key checks';panel.appendChild(title);var grid=document.createElement('div');grid.className='cist-key-grid';panel.appendChild(grid);
    if(urlMode){
      var host=finalHost();var redirects=redirectCount(),age=domainAge();addItem(grid,'Destination',host||'Could not verify');addItem(grid,'Redirects',redirects===null?'Could not verify':redirects===0?'None':String(redirects));addItem(grid,'Threat databases',threatLabel());if(age)addItem(grid,'Domain age',age);
    }else{
      var items=document.querySelectorAll('#cist-found .cist-result-v2-found-item');var added=0;for(var i=0;i<items.length&&added<3;i++){var l=clean(items[i].querySelector('small')&&items[i].querySelector('small').textContent),v=clean(items[i].querySelector('strong')&&items[i].querySelector('strong').textContent);if(!l||!v||l.toLowerCase()==='risk level')continue;addItem(grid,l,v);added++}addItem(grid,'Risk signals',status()==='high'?'High risk':status()==='caution'?'Needs review':status()==='low'?'No major warning':'Incomplete');
    }
    if(reason){var whyBox=document.createElement('div');whyBox.className='cist-compact-why';var lead=document.createElement('strong');lead.textContent='Why this verdict: ';whyBox.appendChild(lead);whyBox.appendChild(document.createTextNode(reason));panel.appendChild(whyBox)}
    document.body.classList.add('cist-compact-result-active');
    var technical=document.getElementById('technical');if(technical){technical.classList.remove('hidden');technical.open=false;var sum=technical.querySelector('summary');if(sum&&sum.textContent!=='Technical details (advanced)')sum.textContent='Technical details (advanced)'}
  }
  function reset(){document.body.classList.remove('cist-compact-result-active');var b=document.getElementById('cist-compact-confidence');if(b)b.style.display='none'}
  input.addEventListener('input',reset);form.addEventListener('submit',reset,true);document.addEventListener('cist:result-updated',function(){setTimeout(render,30)});
  new MutationObserver(function(mutations){
    var meaningful=false;
    for(var i=0;i<mutations.length;i++){
      var t=mutations[i].target&&mutations[i].target.nodeType===3?mutations[i].target.parentElement:mutations[i].target;
      if(!t)continue;
      if(t.closest&&t.closest('#cist-compact-result'))continue;
      if(t.id==='cist-compact-confidence'||(t.closest&&t.closest('#actions'))||(t.closest&&t.closest('#technical')))continue;
      meaningful=true;break;
    }
    if(meaningful)setTimeout(render,30);
  }).observe(card,{attributes:true,subtree:true,childList:true,characterData:true});
  render();
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    source=re.sub(r'\s*<style id="cist-compact-result-v1-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-compact-result-v1-script">.*?</script>','',source,count=1,flags=re.S)
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage HTML')
    source=source.replace('</head>',STYLE+'\n</head>',1).replace('</body>',SCRIPT+'\n</body>',1)
    required=['Essential scan result','What you should do','Key checks','Threat databases','Technical details (advanced)','cist-compact-result-active']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Compact result guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied compact non-redundant scan result layout')

if __name__=='__main__':
    main()
