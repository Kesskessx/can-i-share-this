#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "dist" / "index.html"

STYLE = r"""
<style id="cist-x-viral-loop-style">
#cist-mega-share{background:#11151d!important;color:var(--text)!important;border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 58%,var(--line))!important}
#cist-mega-share:before{content:"𝕏";margin-right:6px;font-weight:950}
#cist-mega-share[disabled]{opacity:.62;cursor:wait!important}
</style>
"""

SCRIPT = r"""
<script id="cist-x-viral-loop-script">
(function(){
  function api(action,body,keepalive){
    return fetch('/api/event?action='+encodeURIComponent(action),{
      method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body||{}),keepalive:!!keepalive
    });
  }
  function track(event,resultId,parentResultId){
    try{api('viral-event',{event:event,resultId:resultId||null,parentResultId:parentResultId||null},true).catch(function(){})}catch(_){}
  }
  function intent(url,summary){
    var verdict=String(summary&&summary.verdict||'unknown');
    var lead=verdict==='high'?'Would you open this?':verdict==='caution'?'Would you trust this?':'I checked this before opening it.';
    var headline=String(summary&&summary.headline||'Can I Share This? scan result');
    return 'https://twitter.com/intent/tweet?text='+encodeURIComponent(lead+' '+headline)+'&url='+encodeURIComponent(url);
  }
  async function createShare(summary,parentResultId){
    var response=await api('share-result',{summary:summary,parentResultId:parentResultId||null},false);
    var data=await response.json().catch(function(){return {}});
    if(!response.ok||!data.url)throw new Error(data.error||'Could not create shared result');
    return data;
  }
  function labelButton(){var button=document.getElementById('cist-mega-share');if(button&&!button.disabled&&button.textContent!=='Share on X')button.textContent='Share on X'}
  document.addEventListener('cist:mega-result',function(){setTimeout(labelButton,0)});
  new MutationObserver(labelButton).observe(document.body,{childList:true,subtree:true});
  labelButton();
  document.addEventListener('click',async function(event){
    var button=event.target&&event.target.closest?event.target.closest('#cist-mega-share'):null;if(!button)return;
    event.preventDefault();event.stopPropagation();if(event.stopImmediatePropagation)event.stopImmediatePropagation();
    var result=window.cistMegaLastResult;if(!result||!result.shareSummary||button.disabled)return;
    var popup=window.open('about:blank','_blank');if(popup)try{popup.opener=null}catch(_){}
    button.disabled=true;button.textContent='Preparing X post…';
    try{var shared=await createShare(result.shareSummary,null);track('share_x',shared.id,null);var target=intent(shared.url,result.shareSummary);if(popup)popup.location.replace(target);else window.open(target,'_blank','noopener,noreferrer');button.textContent='Shared on X'}
    catch(error){if(popup)popup.close();button.textContent='Share on X'}
    finally{setTimeout(function(){button.disabled=false;button.textContent='Share on X'},1400)}
  },true);
})();
</script>
"""

def apply():
    html = HOME.read_text(encoding="utf-8")
    html = html.replace('<meta name="twitter:card" content="summary">', '<meta name="twitter:card" content="summary_large_image">')
    html = html.replace(STYLE, "").replace(SCRIPT, "")
    if "</head>" not in html or "</body>" not in html:
        raise RuntimeError("Homepage structure not found")
    html = html.replace("</head>", STYLE + "\n</head>", 1)
    html = html.replace("</body>", SCRIPT + "\n</body>", 1)
    HOME.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    apply()
