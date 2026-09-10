#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'dist' / 'index.html'
html = INDEX.read_text(encoding='utf-8')

if 'id="cist-local-ocr-script"' in html:
    raise SystemExit('local OCR already present')

script = r'''<script id="cist-local-ocr-script">
(function(){
  var OCR_SRC='https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js';
  var loading=null;
  function loadOCR(){
    if(window.Tesseract)return Promise.resolve(window.Tesseract);
    if(loading)return loading;
    loading=new Promise(function(resolve,reject){
      var s=document.createElement('script');s.src=OCR_SRC;s.async=true;s.crossOrigin='anonymous';
      s.onload=function(){window.Tesseract?resolve(window.Tesseract):reject(new Error('OCR failed to initialize.'))};
      s.onerror=function(){reject(new Error('OCR library could not be loaded.'))};
      document.head.appendChild(s);
    });
    return loading;
  }
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function box(){return document.getElementById('image-analysis')}
  function setBusy(on){
    ['choose-image','take-photo'].forEach(function(id){var b=document.getElementById(id);if(b){b.disabled=on;b.textContent=on?'Analyzing…':(id==='choose-image'?'Upload image':'Use camera')}})
  }
  function renderStatus(title,msg){var b=box();if(!b)return;b.className='image-analysis';b.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">…</div><div><h3>'+esc(title)+'</h3><p>'+esc(msg)+'</p></div></div>';b.classList.remove('hidden')}
  function renderError(msg){var b=box();if(!b)return;b.className='image-analysis caution';b.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">!</div><div><h3>Image check incomplete</h3><p>'+esc(msg)+'</p></div></div>';b.classList.remove('hidden')}
  async function decodeQr(f){
    if(!('BarcodeDetector' in window)||!window.createImageBitmap)return '';
    try{var d=new BarcodeDetector({formats:['qr_code']});var bm=await createImageBitmap(f);var c=await d.detect(bm);if(bm.close)bm.close();return c&&c[0]&&c[0].rawValue?String(c[0].rawValue).trim():''}catch(_){return ''}
  }
  async function recognize(f){
    var T=await loadOCR();
    var r=await T.recognize(f,'eng',{logger:function(m){if(m&&m.status==='recognizing text'&&typeof m.progress==='number')renderStatus('Reading visible text…',Math.round(m.progress*100)+'% complete. Analysis stays in your browser until extracted text is submitted.')}});
    return r&&r.data&&r.data.text?String(r.data.text).trim():'';
  }
  async function handle(f,input){
    if(!f)return;
    if(!/^image\/(jpeg|png|webp)$/i.test(f.type||'')){renderError('Use a JPEG, PNG or WebP image.');return}
    if(f.size>4*1024*1024){renderError('The image is too large. Maximum size: 4 MB.');return}
    setBusy(true);renderStatus('Analyzing image locally…','Reading QR codes and visible text without Gemini.');
    try{
      var pair=await Promise.all([decodeQr(f),recognize(f).catch(function(){return ''})]);
      var qr=pair[0],text=pair[1];
      if(!text&&!qr){renderError('No readable text or QR code was detected. The image was not assigned a safety verdict.');return}
      var r=await fetch('/api/image-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({visibleText:text,qrValues:qr?[qr]:[],inputSource:'local-ocr'})});
      var data=await r.json().catch(function(){return {}});
      if(!r.ok||!data.analysis)throw new Error(data.error||'Local image analysis failed.');
      var a=data.analysis,b=box();if(!b)return;
      var risk=['low','caution','high'].indexOf(a.risk)>=0?a.risk:'unknown';var icon=risk==='low'?'✓':risk==='high'?'×':risk==='caution'?'!':'?';
      var title=risk==='high'?'High-risk signs found':risk==='caution'?'Suspicious signs found':risk==='low'?'No obvious scam signs found':'Image analysis incomplete';
      var found=[];(a.urls||[]).slice(0,2).forEach(function(v){found.push('URL: '+v)});(a.emails||[]).slice(0,2).forEach(function(v){found.push('Email: '+v)});(a.qr_values||[]).slice(0,1).forEach(function(v){found.push('QR: '+v)});
      b.className='image-analysis '+risk;b.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">'+icon+'</div><div><h3>'+esc(title)+'</h3><p>'+esc(a.summary||'Local rule-based analysis completed.')+'</p></div></div>'+(found.length?'<div class="image-detected"><strong>Detected:</strong> '+found.map(esc).join('<br>')+'</div>':'')+(a.recommended_action?'<div class="image-detected"><strong>Recommended action:</strong> '+esc(a.recommended_action)+'</div>':'');b.classList.remove('hidden');
      var target=(a.urls&&a.urls[0])||(a.qr_values||[]).find(function(v){return /^https?:\/\//i.test(v)})||(a.emails&&a.emails[0])||'';
      var main=document.getElementById('url'),form=document.getElementById('scan-form');if(target&&main&&form){main.value=target;main.dispatchEvent(new Event('input',{bubbles:true}));setTimeout(function(){if(form.requestSubmit)form.requestSubmit()},80)}
    }catch(e){renderError(e&&e.message?e.message:'Local image analysis failed.')}finally{setBusy(false);if(input)input.value=''}
  }
  document.addEventListener('change',function(e){var t=e.target;if(!t||!(t.id==='image-file'||t.id==='camera-file'))return;e.stopImmediatePropagation();handle(t.files&&t.files[0],t)},true);
})();
</script>'''

html = html.replace('</body>', script + '\n</body>', 1)
INDEX.write_text(html, encoding='utf-8')
print('Added Gemini-free local OCR and QR image scanner')
