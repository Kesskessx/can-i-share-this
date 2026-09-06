#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-desktop-sidebars-polish-v1-style">
@media(min-width:1100px){
  #cist-scam-signals-rail.cist-scam-signals-rail,
  #cist-daily-rail.cist-daily-rail{
    top:258px!important;
    width:clamp(145px,calc((100vw - 820px)/2 - 24px),210px)!important;
    box-sizing:border-box!important;
  }
  #cist-scam-signals-rail.cist-scam-signals-rail{
    left:max(12px,calc(50% - 618px))!important;
    right:auto!important;
  }
  #cist-daily-rail.cist-daily-rail{
    right:max(12px,calc(50% - 618px))!important;
    left:auto!important;
  }

  #cist-scam-signals-rail .cist-signal-card,
  #cist-daily-rail .cist-daily-card{
    display:flex!important;
    flex-direction:column!important;
    height:252px!important;
    min-height:252px!important;
    overflow:hidden!important;
    border-radius:16px!important;
    border:1px solid color-mix(in srgb,var(--line,#2a3140) 90%,transparent)!important;
    background:linear-gradient(180deg,color-mix(in srgb,var(--card,#151b26) 94%,transparent),color-mix(in srgb,var(--bg,#0b0f17) 82%,var(--card,#151b26)))!important;
    box-shadow:0 12px 32px rgba(0,0,0,.12)!important;
  }

  #cist-scam-signals-rail .cist-signal-head,
  #cist-daily-rail .cist-daily-head{
    flex:0 0 38px!important;
    min-height:38px!important;
    padding:0 12px!important;
    gap:7px!important;
    border-bottom:1px solid color-mix(in srgb,var(--line,#2a3140) 82%,transparent)!important;
  }
  #cist-scam-signals-rail .cist-signal-title,
  #cist-daily-rail .cist-daily-title{
    font-size:9px!important;
    letter-spacing:.08em!important;
  }
  #cist-scam-signals-rail .cist-signal-live,
  #cist-daily-rail .cist-daily-live{
    font-size:8px!important;
    gap:5px!important;
  }
  #cist-scam-signals-rail .cist-signal-live:before,
  #cist-daily-rail .cist-daily-live:before{
    width:5px!important;
    height:5px!important;
    box-shadow:0 0 0 3px color-mix(in srgb,currentColor 9%,transparent)!important;
  }

  #cist-scam-signals-rail .cist-signal-primary,
  #cist-daily-rail .cist-daily-primary{
    flex:0 0 66px!important;
    min-height:66px!important;
    padding:11px 12px 9px!important;
    box-sizing:border-box!important;
  }
  #cist-scam-signals-rail .cist-signal-number,
  #cist-daily-rail .cist-daily-number{
    font-size:31px!important;
    line-height:.95!important;
    letter-spacing:-.045em!important;
  }
  #cist-scam-signals-rail .cist-signal-primary-label,
  #cist-daily-rail .cist-daily-primary-label{
    margin-top:4px!important;
    font-size:9px!important;
    line-height:1.2!important;
  }
  #cist-scam-signals-rail .cist-signal-activity{
    margin-top:3px!important;
    font-size:7.8px!important;
    line-height:1.2!important;
    opacity:.82!important;
  }
  #cist-scam-signals-rail .cist-signal-zero-note{display:none!important}

  #cist-scam-signals-rail .cist-signal-list,
  #cist-daily-rail .cist-daily-list{
    display:flex!important;
    flex:1 1 auto!important;
    min-height:0!important;
    flex-direction:column!important;
    border-top:1px solid color-mix(in srgb,var(--line,#2a3140) 82%,transparent)!important;
  }
  #cist-scam-signals-rail .cist-signal-row,
  #cist-daily-rail .cist-daily-row{
    display:flex!important;
    flex:1 1 0!important;
    min-height:0!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:8px!important;
    padding:6px 12px!important;
    box-sizing:border-box!important;
    border-bottom:1px solid color-mix(in srgb,var(--line,#2a3140) 66%,transparent)!important;
  }
  #cist-scam-signals-rail .cist-signal-row:last-child,
  #cist-daily-rail .cist-daily-row:last-child{border-bottom:0!important}
  #cist-scam-signals-rail .cist-signal-row span,
  #cist-daily-rail .cist-daily-row span{
    font-size:8px!important;
    line-height:1.18!important;
  }
  #cist-scam-signals-rail .cist-signal-row strong,
  #cist-daily-rail .cist-daily-row strong{
    display:inline!important;
    max-width:78px!important;
    margin:0!important;
    font-size:10px!important;
    line-height:1.15!important;
    text-align:right!important;
  }
  #cist-scam-signals-rail .cist-signal-foot,
  #cist-daily-rail .cist-daily-foot{display:none!important}

  body.cist-compact-result-active #cist-destination{display:none!important}
}

@media(min-width:1100px) and (max-width:1249px){
  #cist-scam-signals-rail.cist-scam-signals-rail,
  #cist-daily-rail.cist-daily-rail{width:145px!important}
  #cist-scam-signals-rail .cist-signal-row,
  #cist-daily-rail .cist-daily-row{display:flex!important;padding:5px 9px!important}
  #cist-scam-signals-rail .cist-signal-row strong,
  #cist-daily-rail .cist-daily-row strong{display:inline!important;text-align:right!important;margin:0!important}
  #cist-scam-signals-rail .cist-signal-head,
  #cist-daily-rail .cist-daily-head{padding:0 9px!important}
  #cist-scam-signals-rail .cist-signal-primary,
  #cist-daily-rail .cist-daily-primary{padding-left:9px!important;padding-right:9px!important}
}
</style>
'''

SCRIPT = r'''
<script id="cist-desktop-sidebars-polish-v1-script">
(function(){
  var card=document.getElementById('result-card');
  var scam=document.getElementById('cist-scam-signals-rail');

  function compactScamCopy(){
    if(!scam)return;
    var live=document.getElementById('cist-signal-live');
    var label=scam.querySelector('.cist-signal-primary-label');
    var activity=document.getElementById('cist-signal-activity');
    if(live&&live.textContent!=='Live')live.textContent='Live';
    if(label&&label.textContent!=='Signals today')label.textContent='Signals today';
    if(activity){
      var t=String(activity.textContent||'').replace(/\s+/g,' ').trim();
      t=t.replace(/\s+analyzed today$/i,' analyzed');
      if(activity.textContent!==t)activity.textContent=t;
    }
  }

  function ownText(el){
    var out='';
    for(var i=0;i<el.childNodes.length;i++)if(el.childNodes[i].nodeType===3)out+=' '+el.childNodes[i].nodeValue;
    return out.replace(/\s+/g,' ').trim().toLowerCase();
  }
  function hideBorderedAncestor(el){
    if(!el||!card)return;
    var p=el.closest&&el.closest('#cist-destination');
    if(p){p.style.setProperty('display','none','important');return}
    p=el.parentElement;
    var fallback=null,depth=0;
    while(p&&p!==card&&depth<6){
      if(!fallback&&p.matches&&p.matches('section,article'))fallback=p;
      try{
        var s=getComputedStyle(p),w=parseFloat(s.borderTopWidth)||0;
        if(w>0&&s.borderTopStyle!=='none'){
          p.style.setProperty('display','none','important');
          return;
        }
      }catch(e){}
      p=p.parentElement;depth++;
    }
    if(fallback)fallback.style.setProperty('display','none','important');
  }
  function removeDuplicateDestination(){
    if(!card||!document.body.classList.contains('cist-compact-result-active'))return;
    var known=document.getElementById('cist-destination');
    if(known)known.style.setProperty('display','none','important');
    var nodes=card.querySelectorAll('small,span,strong,h2,h3,h4,h5,h6');
    for(var i=0;i<nodes.length;i++){
      var t=ownText(nodes[i]);
      if(t==='where this link goes'||t==='where does this link really go?'||t==='where does this link go?')hideBorderedAncestor(nodes[i]);
    }
  }
  function polish(){compactScamCopy();removeDuplicateDestination()}

  polish();
  document.addEventListener('cist:result-updated',function(){setTimeout(polish,80)});
  if(card)new MutationObserver(function(){setTimeout(polish,30)}).observe(card,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['class']});
  if(scam)new MutationObserver(function(){setTimeout(compactScamCopy,20)}).observe(scam,{childList:true,subtree:true,characterData:true});
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source=HOME.read_text(encoding='utf-8')
    if 'id="cist-daily-rail"' not in source or 'id="cist-scam-signals-rail"' not in source:
        raise RuntimeError('Desktop sidebars not found')
    source=re.sub(r'\s*<style id="cist-desktop-sidebars-polish-v1-style">.*?</style>','',source,count=1,flags=re.S)
    source=re.sub(r'\s*<script id="cist-desktop-sidebars-polish-v1-script">.*?</script>','',source,count=1,flags=re.S)
    source=source.replace('</head>',STYLE+'\n</head>',1)
    source=source.replace('</body>',SCRIPT+'\n</body>',1)
    required=['height:252px!important','Signals today','where this link goes','cist-destination','max(12px,calc(50% - 618px))']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Desktop sidebars polish guard failed: missing {token}')
    HOME.write_text(source,encoding='utf-8')
    print('Applied compact symmetric desktop sidebars and removed duplicate destination UI')

if __name__=='__main__':
    main()
