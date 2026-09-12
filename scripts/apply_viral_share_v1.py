#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

SCRIPT = r'''
<script id="cist-viral-share-v1">
(function(){
  function postEvent(event,resultId,parentResultId){
    try{fetch('/api/viral-event',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({event:event,resultId:resultId||null,parentResultId:parentResultId||null}),keepalive:true}).catch(function(){})}catch(_){}
  }
  function xIntent(summary,url){
    var headline=String(summary&&summary.headline||'Can I Share This? scan result').replace(/\s+/g,' ').trim().slice(0,150);
    return 'https://x.com/intent/tweet?text='+encodeURIComponent('Would you open this? '+headline+' '+url);
  }
  function install(){
    var old=document.getElementById('cist-mega-share');
    if(!old||old.dataset.cistViralShare==='1')return;
    var btn=old.cloneNode(true);
    btn.dataset.cistViralShare='1';
    btn.textContent='Share on X';
    old.replaceWith(btn);
    btn.addEventListener('click',async function(){
      var d=window.cistMegaLastResult;
      if(!d||!d.shareSummary)return;
      var popup=window.open('about:blank','_blank');
      btn.disabled=true;btn.textContent='Creating share link…';
      try{
        var response=await fetch('/api/share',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({summary:d.shareSummary})});
        if(!response.ok)throw new Error('share');
        var data=await response.json();
        postEvent('share_x',data.id,null);
        var target=xIntent(d.shareSummary,data.url);
        if(popup)popup.location=target;else location.href=target;
      }catch(e){
        if(popup)popup.close();
        btn.textContent='Share unavailable';
        setTimeout(function(){btn.textContent='Share on X'},1600);
      }finally{btn.disabled=false}
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else setTimeout(install,0);
  document.addEventListener('cist:mega-result',function(){setTimeout(install,0)});
})();
</script>
'''

if not HOME.exists():
    raise SystemExit('dist/index.html not found')

html = HOME.read_text(encoding='utf-8')
html = re.sub(r'(<meta\s+name=["\']twitter:card["\']\s+content=["\'])summary(["\'])', r'\1summary_large_image\2', html, flags=re.I)
if 'id="cist-viral-share-v1"' not in html:
    html = html.replace('</body>', SCRIPT + '\n</body>')
HOME.write_text(html, encoding='utf-8')
