#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'dist' / 'index.html'
html = INDEX.read_text(encoding='utf-8')

MARKER = 'id="universal-scanner-design"'
if MARKER in html:
    raise SystemExit('universal scanner design already present')

css = r'''
<style id="universal-scanner-design">
/* Universal scanner: keep every input mode visually part of one product. */
#scan-form{position:relative}
.cist-capabilities{display:flex;justify-content:center;align-items:center;gap:7px;flex-wrap:wrap;margin:0 auto 12px;color:var(--muted);font-size:12px;font-weight:750;letter-spacing:.01em}
.cist-capabilities span{display:inline-flex;align-items:center;gap:7px}
.cist-capabilities span:not(:last-child)::after{content:'·';opacity:.55;margin-left:1px}
.cist-input-hint{margin:8px auto 0;color:var(--muted);font-size:11px;text-align:center}
#image-safety-tools.image-tools{max-width:720px;margin:9px auto 0;display:grid;grid-template-columns:1fr 1fr;gap:8px;align-items:stretch}
#image-safety-tools .image-tool{min-height:44px;border-radius:12px;padding:10px 12px;font-size:13px;background:var(--card);border:1px solid var(--line);box-shadow:none;transition:transform .12s ease,border-color .12s ease,background .12s ease}
#image-safety-tools .image-tool:hover{transform:translateY(-1px)}
#image-safety-tools .image-note{grid-column:1/-1;margin:2px 0 0;text-align:center;font-size:11px;line-height:1.45;color:var(--muted)}
#image-analysis.image-analysis{max-width:720px;margin-top:14px;padding:17px;border-radius:17px}
#image-analysis .image-analysis-head{align-items:flex-start}
#image-analysis .image-analysis-icon{width:38px;height:38px;font-size:18px}
#image-analysis h3{font-size:18px;line-height:1.2}
#image-analysis p{font-size:13px;line-height:1.55}
#image-analysis .image-findings{margin-top:11px}
#image-analysis .image-finding{padding:6px 9px;font-size:11px;border:1px solid color-mix(in srgb,var(--line) 78%,transparent)}
#image-analysis .image-detected{line-height:1.55}
@media(max-width:600px){
  .cist-capabilities{margin-bottom:9px;font-size:11px;gap:5px}
  #image-safety-tools.image-tools{gap:7px;margin-top:8px}
  #image-safety-tools .image-tool{min-width:0;min-height:42px;padding:9px 8px}
  #image-analysis.image-analysis{margin-top:12px;padding:15px;border-radius:15px}
  #image-analysis h3{font-size:17px}
  h1{margin-bottom:12px!important;line-height:1.02!important}
  h1 + p{margin-top:0!important;margin-bottom:18px!important;line-height:1.45!important}
}
</style>
'''

js = r'''
<script id="universal-scanner-design-script">
(function(){
  function init(){
    var form=document.getElementById('scan-form');
    if(!form)return;

    if(!document.querySelector('.cist-capabilities')){
      var caps=document.createElement('div');
      caps.className='cist-capabilities';
      caps.setAttribute('aria-label','Supported inputs');
      ['Link','Email','QR','Image','Crypto'].forEach(function(label){var s=document.createElement('span');s.textContent=label;caps.appendChild(s)});
      form.parentNode.insertBefore(caps,form);
    }

    var submit=form.querySelector('button[type="submit"],input[type="submit"]');
    if(submit){
      if(submit.tagName==='INPUT')submit.value='Analyze';
      else submit.textContent='Analyze';
      submit.setAttribute('aria-label','Analyze');
    }

    var input=document.getElementById('url')||form.querySelector('input[type="text"],input[type="url"],input[type="email"]');
    if(input){
      input.placeholder='Paste anything suspicious…';
      input.setAttribute('aria-label','Paste a link, email, crypto address or other suspicious content');
    }

    var imageTools=document.getElementById('image-safety-tools');
    if(imageTools){
      var upload=document.getElementById('choose-image'),camera=document.getElementById('take-photo');
      if(upload)upload.textContent='Photo';
      if(camera)camera.textContent='Camera';
      var note=imageTools.querySelector('.image-note');
      if(note)note.textContent='Private by design · No account required · Images are not stored by Can I Share This?';
    }

    var paste=document.getElementById('paste')||document.querySelector('[id*="paste"],button[data-action="paste"]');
    if(paste && /paste/i.test(paste.textContent||''))paste.textContent='Paste';
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
</script>
'''

if '</head>' not in html or '</body>' not in html:
    raise SystemExit('invalid homepage HTML')
html = html.replace('</head>', css + '\n</head>', 1)
html = html.replace('</body>', js + '\n</body>', 1)
INDEX.write_text(html, encoding='utf-8')
print('Applied universal scanner design polish')
