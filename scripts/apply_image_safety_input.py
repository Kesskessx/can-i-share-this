#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'dist' / 'index.html'
html = INDEX.read_text(encoding='utf-8')

MARKER = 'id="image-safety-tools"'
if MARKER in html:
    raise SystemExit('image safety UI already present')

css = r'''
<style id="image-safety-style">
.image-tools{margin:12px auto 0;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap}.image-tool{appearance:none;border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:11px;padding:9px 13px;font:inherit;font-size:13px;font-weight:800;cursor:pointer}.image-tool:disabled{opacity:.55;cursor:default}.image-note{width:100%;font-size:11px;color:var(--muted);margin-top:1px}.image-analysis{max-width:720px;margin:16px auto 0;text-align:left;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;box-shadow:var(--shadow)}.image-analysis-head{display:flex;gap:11px;align-items:flex-start}.image-analysis-icon{width:34px;height:34px;display:grid;place-items:center;border-radius:50%;background:var(--soft);flex:0 0 auto;font-weight:900}.image-analysis h3{margin:0;font-size:17px;letter-spacing:-.02em}.image-analysis p{margin:5px 0 0;color:var(--muted);font-size:13px}.image-analysis.high .image-analysis-icon,.image-analysis.high h3{color:var(--red)}.image-analysis.caution .image-analysis-icon,.image-analysis.caution h3{color:var(--amber)}.image-analysis.low .image-analysis-icon,.image-analysis.low h3{color:var(--green)}.image-findings{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}.image-finding{background:var(--soft);border-radius:999px;padding:6px 9px;font-size:11px;font-weight:750}.image-detected{margin-top:12px;padding-top:12px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);word-break:break-word}.image-preview{margin-top:11px;display:flex;align-items:center;gap:10px}.image-preview img{width:48px;height:48px;object-fit:cover;border-radius:9px;border:1px solid var(--line)}.image-preview span{font-size:12px;color:var(--muted)}
@media(max-width:600px){.image-tools{gap:7px}.image-tool{flex:1;min-width:120px;padding:10px 9px}.image-analysis{border-radius:14px}}
</style>
'''

ui = r'''
<div id="image-safety-tools" class="image-tools" aria-label="Analyze a screenshot or photo">
  <button id="choose-image" class="image-tool" type="button">Upload image</button>
  <button id="take-photo" class="image-tool" type="button">Use camera</button>
  <input id="image-file" type="file" accept="image/jpeg,image/png,image/webp" hidden>
  <input id="camera-file" type="file" accept="image/jpeg,image/png,image/webp" capture="environment" hidden>
  <div class="image-note">Screenshots and photos are analyzed temporarily and are not stored by Can I Share This?.</div>
</div>
<div id="image-analysis" class="image-analysis hidden" aria-live="polite"></div>
'''

js = r'''
<script id="image-safety-script">
(function(){
  var choose=document.getElementById('choose-image'),camera=document.getElementById('take-photo'),file=document.getElementById('image-file'),cameraFile=document.getElementById('camera-file'),box=document.getElementById('image-analysis');
  var mainInput=document.getElementById('url'),form=document.getElementById('scan-form');
  if(!choose||!camera||!file||!cameraFile||!box)return;
  var MAX=4*1024*1024,MAX_DIMENSION=1800,TARGET_BYTES=1500*1024;
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function setBusy(on){choose.disabled=on;camera.disabled=on;choose.textContent=on?'Analyzing…':'Upload image';camera.textContent=on?'Please wait…':'Use camera'}
  function renderLoading(name,url){box.className='image-analysis';box.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">…</div><div><h3>Analyzing image…</h3><p>Reading visible text, profile identity, links, QR codes, email addresses and brand clues.</p></div></div><div class="image-preview"><img src="'+esc(url)+'" alt="Selected image preview"><span>'+esc(name)+'</span></div>';box.classList.remove('hidden')}
  function renderError(msg){box.className='image-analysis caution';box.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">!</div><div><h3>Image check unavailable</h3><p>'+esc(msg||'The image could not be analyzed.')+'</p></div></div>';box.classList.remove('hidden')}
  function firstTarget(a){var qr=(a.qr_values||[]).find(function(v){return /^https?:\/\//i.test(v)});return (a.urls&&a.urls[0])||qr||(a.emails&&a.emails[0])||''}
  function runTarget(target){if(target&&mainInput&&form){try{sessionStorage.setItem('cist_input_source','image')}catch(e){}mainInput.value=target;mainInput.dispatchEvent(new Event('input',{bubbles:true}));setTimeout(function(){if(typeof form.requestSubmit==='function')form.requestSubmit();else form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))},180)}}
  async function decodeQr(f){if(!('BarcodeDetector' in window)||!window.createImageBitmap)return '';try{var detector=new BarcodeDetector({formats:['qr_code']});var bitmap=await createImageBitmap(f);var codes=await detector.detect(bitmap);if(bitmap.close)bitmap.close();return codes&&codes[0]&&codes[0].rawValue?String(codes[0].rawValue).trim():''}catch(e){return ''}}
  function render(a,localQr){
    if(localQr){a.qr_values=Array.isArray(a.qr_values)?a.qr_values:[];if(a.qr_values.indexOf(localQr)<0)a.qr_values.unshift(localQr);if(/^https?:\/\//i.test(localQr)){a.urls=Array.isArray(a.urls)?a.urls:[];if(a.urls.indexOf(localQr)<0)a.urls.unshift(localQr)}}
    var risk=['low','caution','high'].indexOf(a.risk)>=0?a.risk:'unknown',social=a.social_profile&&((a.social_profile.username||'')||(a.social_profile.platform||''));var icon=risk==='low'?'✓':risk==='high'?'×':risk==='caution'?'!':'?';var title=social?(risk==='high'?'High impersonation risk':risk==='caution'?'Profile needs verification':risk==='low'?'No obvious impersonation signs':'Profile check incomplete'):(risk==='high'?'Likely scam or high-risk signs':risk==='caution'?'Suspicious signs found':risk==='low'?'No obvious scam signs found':'Image analysis incomplete');var chips=[];
    if(social&&a.social_profile.platform)chips.push('Platform: '+a.social_profile.platform);if(social&&a.social_profile.username)chips.push('@'+a.social_profile.username);(a.claimed_brands||[]).slice(0,2).forEach(function(x){chips.push('Brand: '+x)});if((a.urls||[]).length)chips.push((a.urls||[]).length+' URL'+((a.urls||[]).length>1?'s':''));if((a.emails||[]).length)chips.push((a.emails||[]).length+' email');if((a.qr_values||[]).length)chips.push((a.qr_values||[]).length+' QR value');(a.suspicious_signals||[]).slice(0,3).forEach(function(s){chips.push(s.type||'warning')});var target=firstTarget(a);
    box.className='image-analysis '+risk;box.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">'+icon+'</div><div><h3>'+esc(title)+'</h3><p>'+esc(a.summary||'The image was analyzed for visible scam indicators.')+'</p></div></div>'+(chips.length?'<div class="image-findings">'+chips.map(function(x){return '<span class="image-finding">'+esc(x)+'</span>'}).join('')+'</div>':'')+(a.recommended_action?'<div class="image-detected"><strong>Recommended action:</strong> '+esc(a.recommended_action)+'</div>':'')+(target?'<div class="image-detected"><strong>Detected:</strong> '+esc(target)+'<br>Running it through the existing safety scanner…</div>':'');box.classList.remove('hidden');runTarget(target)
  }
  function canvasToDataURL(canvas,quality){return canvas.toDataURL('image/jpeg',quality)}
  async function prepareImage(f){
    var bitmap=await createImageBitmap(f),w=bitmap.width,h=bitmap.height,scale=Math.min(1,MAX_DIMENSION/Math.max(w,h)),cw=Math.max(1,Math.round(w*scale)),ch=Math.max(1,Math.round(h*scale));
    var canvas=document.createElement('canvas');canvas.width=cw;canvas.height=ch;var ctx=canvas.getContext('2d',{alpha:false});ctx.drawImage(bitmap,0,0,cw,ch);if(bitmap.close)bitmap.close();
    var q=.86,data=canvasToDataURL(canvas,q);while(data.length*.75>TARGET_BYTES&&q>.5){q-=.08;data=canvasToDataURL(canvas,q)}return data;
  }
  async function analyzeImage(f){
    if(!f)return;if(!/^image\/(jpeg|png|webp)$/i.test(f.type||'')){renderError('Use a JPEG, PNG or WebP image.');return}if(f.size>MAX){renderError('The image is too large. Maximum size: 4 MB.');return}
    var preview=URL.createObjectURL(f);renderLoading(f.name||'Camera photo',preview);setBusy(true);
    try{
      var qrPromise=decodeQr(f),dataUrl;
      try{dataUrl=await prepareImage(f)}catch(_){dataUrl=await new Promise(function(resolve,reject){var rr=new FileReader();rr.onload=function(){resolve(rr.result)};rr.onerror=reject;rr.readAsDataURL(f)})}
      var r=await fetch('/api/image-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({image:dataUrl})});
      var data=await r.json().catch(function(){return {}}),localQr=await qrPromise;
      if(!r.ok||!data.analysis){if(localQr&&/^https?:\/\//i.test(localQr)){box.className='image-analysis caution';box.innerHTML='<div class="image-analysis-head"><div class="image-analysis-icon">QR</div><div><h3>QR code detected</h3><p>The QR destination was decoded locally. Running the destination through the safety scanner…</p></div></div><div class="image-detected"><strong>Detected:</strong> '+esc(localQr)+'</div>';box.classList.remove('hidden');runTarget(localQr);return}if(r.status===413)throw new Error('The image upload was too large. Please try a smaller image.');throw new Error(data.error||('Image analysis failed (HTTP '+r.status+').'))}
      render(data.analysis,localQr)
    }catch(e){renderError(e&&e.message?e.message:'The image could not be analyzed.')}finally{setBusy(false);URL.revokeObjectURL(preview);file.value='';cameraFile.value=''}
  }
  choose.addEventListener('click',function(){file.click()});camera.addEventListener('click',function(){cameraFile.click()});file.addEventListener('change',function(){analyzeImage(file.files&&file.files[0])});cameraFile.addEventListener('change',function(){analyzeImage(cameraFile.files&&cameraFile.files[0])});
})();
</script>
'''

if '</head>' not in html: raise SystemExit('missing </head>')
html = html.replace('</head>', css + '\n</head>', 1)
needle='</form>';pos=html.find(needle)
if pos<0: raise SystemExit('scan form closing tag not found')
pos+=len(needle);html=html[:pos]+'\n'+ui+html[pos:]
if '</body>' not in html: raise SystemExit('missing </body>')
html=html.replace('</body>',js+'\n</body>',1)
INDEX.write_text(html,encoding='utf-8')
print('Added image analysis with client-side compression and local QR decoding')
