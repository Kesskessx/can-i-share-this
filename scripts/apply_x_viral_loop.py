#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-x-viral-loop-style">
#cist-mega-share{background:#11151d!important;color:var(--text)!important;border-color:color-mix(in srgb,var(--cist-accent,#788ff7) 58%,var(--line))!important}
#cist-mega-share:before{content:"𝕏";margin-right:6px;font-weight:950}
#cist-mega-share[disabled]{opacity:.62;cursor:wait!important}
</style>
'''

SCRIPT = r'''
<script id="cist-x-viral-loop-script">
(function(){
  function api(action,body,keepalive){return fetch('/api/event?action='+encodeURIComponent(action),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body||{}),keepalive:!!keepalive})}
  function track(event,resultId,parentResultId){try{api('viral-event',{event:event,resultId:resultId||null,parentResultId:parentResultId||null},true).catch(function(){})}catch(_){}}
  function intent(url,summary){var verdict=String(summary&&summary.verdict||'unknown'),lead=verdict==='high'?'Would you open this?':verdict==='caution'?'Would you trust this?':'I checked this before opening it.',headline=String(summary&&summary.headline||'Can I Share This? scan result').replace(/\s+/g,' ').trim().slice(0,155);return'https://x.com/intent/tweet?text='+encodeURIComponent(lead+' '+headline)+'&url='+encodeURIComponent(url)}
  async function createShare(summary){var response=await api('share-result',{summary:summary},false),data=await response.json().catch(function(){return{}});if(!response.ok||!data.url)throw new Error(data.error||'Could not create shared result');return data}
  function setLabel(){var b=document.getElementById('cist-mega-share');if(b&&!b.disabled)b.textContent='Share on X'}
  document.addEventListener('cist:mega-result',function(){setTimeout(setLabel,0)});setTimeout(setLabel,0);
  document.addEventListener('click',async function(e){var b=e.target&&e.target.closest?e.target.closest('#cist-mega-share'):null;if(!b)return;e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();var d=window.cistMegaLastResult;if(!d||!d.shareSummary||b.disabled)return;var popup=window.open('about:blank','_blank');if(popup)try{popup.opener=null}catch(_){}b.disabled=true;b.textContent='Preparing X post…';try{var shared=await createShare(d.shareSummary);track('share_x',shared.id,null);var target=intent(shared.url,d.shareSummary);if(popup)popup.location.replace(target);else window.open(target,'_blank','noopener,noreferrer');b.textContent='Shared on X'}catch(err){if(popup)popup.close();b.textContent='Share unavailable'}finally{setTimeout(function(){b.disabled=false;b.textContent='Share on X'},1400)}},true);
})();
</script>
'''

if not HOME.exists():
    raise SystemExit('dist/index.html not found')

html = HOME.read_text(encoding='utf-8')
html = re.sub(r'(<meta\s+name=["\']twitter:card["\']\s+content=["\'])summary(["\'])', r'\1summary_large_image\2', html, flags=re.I)
if 'id="cist-x-viral-loop-style"' not in html:
    html = html.replace('</head>', STYLE + '\n</head>', 1)
if 'id="cist-x-viral-loop-script"' not in html:
    html = html.replace('</body>', SCRIPT + '\n</body>', 1)
HOME.write_text(html, encoding='utf-8')
