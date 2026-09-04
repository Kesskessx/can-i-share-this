#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'dist'/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="cist-final-mobile-design"' in s: raise SystemExit('already applied')
css=r'''<style id="cist-final-mobile-design">
/* Small visual corrections after the universal scanner redesign. */
.what-check,.what-we-check,.check-grid,.checks-grid{align-items:stretch}
@media(max-width:600px){
  .hero{padding-bottom:18px!important}
  #scan-form{margin-bottom:0!important}
  #image-safety-tools.image-tools{margin-top:12px!important;gap:10px!important}
  #image-safety-tools .image-tool{min-height:54px!important;border-radius:16px!important;font-size:14px!important;font-weight:750!important}
  .image-note{margin-top:6px!important;line-height:1.35!important}
  .what-check,.what-we-check,.check-grid,.checks-grid{gap:10px!important}
  .site-footer{padding-top:22px!important}
  .footer-resource-links{row-gap:8px!important}
}
</style>'''
js=r'''<script id="cist-final-mobile-design-script">(function(){
function norm(v){return String(v||'').replace(/\s+/g,' ').trim()}
function hideControl(el){if(!el)return;var x=el.closest('a,button')||el;x.style.display='none'}
/* Remove the obsolete standalone QR CTA and duplicate trust pills. */
document.querySelectorAll('a,button,span,div').forEach(function(el){var t=norm(el.textContent);if(t==='Scan a QR code'||t==='Nothing you paste is saved'||t==='No account needed')hideControl(el)});
/* Restore the fourth What we check card and repurpose it for the new message/email engine. */
document.querySelectorAll('body *').forEach(function(el){var t=norm(el.textContent);if(t.indexOf('Copycat sites')===0&&t.indexOf('Look-alike website names')>0&&t.length<180){el.style.display='';var title=el.querySelector('strong,b,h3,h4');if(title)title.textContent='Suspicious messages';var candidates=el.querySelectorAll('span,p,small,div');for(var i=0;i<candidates.length;i++){var q=norm(candidates[i].textContent);if(q==='Look-alike website names')candidates[i].textContent='Scam emails and messages'}var icon=el.querySelector('[aria-hidden="true"],.icon,.check-icon');if(icon)icon.textContent='✉'}}});
/* Ensure four cards stay balanced: if the legacy fourth card is still hidden by inline style, reveal it. */
var heading=[].slice.call(document.querySelectorAll('h2,h3,h4')).find(function(x){return norm(x.textContent)==='What we check'});if(heading){var section=heading.parentElement;var cards=section?section.querySelectorAll('article,.card,.check-card,li'):[];if(cards.length>=4)cards[3].style.display=''}
})();</script>'''
if '</head>' not in s or '</body>' not in s: raise SystemExit('invalid homepage')
s=s.replace('</head>',css+'\n</head>',1).replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Applied final mobile design cleanup')
