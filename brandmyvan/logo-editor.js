const $=id=>document.getElementById(id);
const {spots,model,version}=window.BMV_CONFIG,{fit,clamp}=window.BMV_LAYOUT;
const drafts=new Map();let selected=null,lastLogo=null,uploadSequence=0,submitting=false,uploading=false,previewDrag=null;
const emit=(name,detail)=>window.dispatchEvent(new CustomEvent(name,{detail}));
const money=n=>`${n.toLocaleString('fr-FR')} €`,viewNames={left:'Gauche',right:'Droite',rear:'Arrière'};
for(const spot of spots){const option=document.createElement('option');option.value=spot.id;option.textContent=`${spot.id} · ${viewNames[spot.view]} · ${money(spot.price)}`;$('spotChoice').append(option);}
function draftFor(id){if(!drafts.has(id))drafts.set(id,{logo:lastLogo,scale:.85,x:.5,y:.5,requestId:null,receipt:null});return drafts.get(id);}
function dimensions(spot){const aspect=spot.uw*(spot.view==='rear'?model.width:model.length)/(spot.vh*model.height);return {width:1024,height:Math.round(1024/aspect)};}
function status(message='',error=false){$('logoStatus').textContent=message;$('logoStatus').dataset.error=String(error);}
function drawArtwork(spot,draft){
 const {width,height}=dimensions(spot);const canvas=draft.canvas||document.createElement('canvas');
 if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;}
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,width,height);
 if(draft.logo){const box=fit(width,height,draft.logo.image.width,draft.logo.image.height,draft.scale,draft.x,draft.y);ctx.drawImage(draft.logo.image,box.x,box.y,box.width,box.height);}
 draft.canvas=canvas;return canvas;
}
function refresh(){
 if(!selected)return;const d=draftFor(selected.id),art=drawArtwork(selected,d);const preview=$('logoPreview');preview.width=art.width;preview.height=art.height;
 preview.getContext('2d').drawImage(art,0,0);$('logoAdjustments').hidden=!d.logo;$('logoFileName').textContent=d.logo?d.logo.name:'PNG, JPG ou WebP · 8 Mo maximum. Un PNG transparent donne le meilleur résultat.';
 $('logoScale').value=Math.round(d.scale*100);$('logoScaleValue').textContent=`${Math.round(d.scale*100)}%`;$('logoX').value=Math.round(d.x*100);$('logoY').value=Math.round(d.y*100);
 $('spotPanelClaim').disabled=!d.logo||submitting||uploading||window.BMV_CONFIRMED?.has(selected.id); $('spotPanelClaim').textContent=d.logo?`Demander ${selected.id} — ${money(selected.price)}`:'Importez un logo pour continuer';
 $('requestReceipt').hidden=!d.receipt;if(d.receipt)$('requestReceipt').textContent=`Demande reçue. Référence ${d.receipt}. Votre logo et son placement ont été enregistrés. L’emplacement reste en attente de validation et aucun paiement n’a été effectué.`;
 $('spotPanelClaim').hidden=!!d.receipt||!$('logoRequestForm').hidden;
 emit('bmv:artwork',{id:selected.id,canvas:art,hasLogo:!!d.logo});
}
function openSpot(id){
 if(submitting)return;if(window.BMV_CONFIRMED?.has(id)){status('Cet emplacement est déjà confirmé. Choisissez-en un autre.',true);return;}const spot=spots.find(s=>s.id===id);if(!spot)return;
 if(selected?.id!==id){uploadSequence++;uploading=false;$('logoFile').value='';status();$('logoRequestForm').hidden=true;}
 selected=spot;const d=draftFor(id);$('spotPanel').hidden=false;document.querySelector('.hero-layout').classList.add('is-editing');$('spotChoice').value=id;
 $('spotPanelTier').textContent=`${spot.tier} · ${viewNames[spot.view]}`;$('spotPanelName').textContent=`Emplacement ${id}`;$('spotPanelPrice').textContent=money(spot.price);$('spotPanelCopy').textContent=`${spot.copy} Durée : 12 mois.`;
 $('logoRequestForm').hidden=true;refresh();
}
function closeEditor(){if(submitting)return;selected=null;uploadSequence++;uploading=false;$('spotPanel').hidden=true;document.querySelector('.hero-layout').classList.remove('is-editing');$('spotChoice').value='';emit('bmv:pause');}
$('spotChoice').addEventListener('change',e=>{if(e.target.value){openSpot(e.target.value);emit('bmv:select',e.target.value);}});
window.addEventListener('bmv:spot',e=>openSpot(e.detail));
window.addEventListener('bmv:closed',closeEditor);
window.addEventListener('bmv:ready',()=>{for(const [id,d] of drafts)if(d.logo)emit('bmv:artwork',{id,canvas:d.canvas,hasLogo:true});if(selected)emit('bmv:select',selected.id);});
window.addEventListener('bmv:rotation',e=>{$('inspectLogo').textContent=e.detail?'Arrêter la rotation':'Faire tourner le van';});
$('spotPanelClose').addEventListener('click',()=>{closeEditor();emit('bmv:deselect');});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&selected&&!submitting){closeEditor();emit('bmv:deselect');}});
function editChanged(){const d=draftFor(selected.id);d.requestId=null;d.receipt=null;status();emit('bmv:pause');refresh();}
for(const [id,key] of [['logoScale','scale'],['logoX','x'],['logoY','y']])$(id).addEventListener('input',e=>{if(!selected||submitting)return;draftFor(selected.id)[key]=Number(e.target.value)/100;editChanged();});
$('logoCenter').addEventListener('click',()=>{if(!selected)return;const d=draftFor(selected.id);d.x=d.y=.5;editChanged();});
$('logoRemove').addEventListener('click',()=>{if(!selected)return;const d=draftFor(selected.id);d.logo=null;lastLogo=null;uploadSequence++;uploading=false;$('logoFile').value='';$('logoRequestForm').hidden=true;editChanged();});
$('inspectLogo').addEventListener('click',()=>{if(selected)emit('bmv:inspect',selected.id);});
$('editLogo').addEventListener('click',()=>{if(selected)emit('bmv:face',selected.id);});
$('logoPreview').addEventListener('pointerdown',e=>{
 if(!selected||submitting)return;const d=draftFor(selected.id);if(!d.logo)return;emit('bmv:pause');
 previewDrag={pointerId:e.pointerId,startX:e.clientX,startY:e.clientY,x:d.x,y:d.y};e.currentTarget.setPointerCapture(e.pointerId);
});
$('logoPreview').addEventListener('pointermove',e=>{
 if(!previewDrag||e.pointerId!==previewDrag.pointerId||!selected||submitting)return;
 const d=draftFor(selected.id),canvas=$('logoPreview'),rect=canvas.getBoundingClientRect(),box=fit(canvas.width,canvas.height,d.logo.image.width,d.logo.image.height,d.scale,d.x,d.y);
 // Canvas is displayed at its natural ratio, so screen and artwork coordinates agree.
 d.x=clamp(previewDrag.x+(e.clientX-previewDrag.startX)*canvas.width/rect.width/Math.max(1,box.slackX),0,1);
 d.y=clamp(previewDrag.y+(e.clientY-previewDrag.startY)*canvas.height/rect.height/Math.max(1,box.slackY),0,1);editChanged();
});
for(const event of ['pointerup','pointercancel','lostpointercapture'])$('logoPreview').addEventListener(event,()=>{previewDrag=null;});
async function readLogo(file){
 if(!['image/png','image/jpeg','image/webp'].includes(file.type))throw Error('Utilisez une image PNG, JPG ou WebP.');
 if(file.size>8*1024*1024)throw Error('Choisissez un logo inférieur à 8 Mo.');
 let bitmap;try{bitmap=await createImageBitmap(file);}catch{throw Error('Cette image ne peut pas être ouverte. Essayez un autre fichier PNG, JPG ou WebP.');}
 try{
  if(bitmap.width*bitmap.height>25000000)throw Error('Choisissez une image inférieure à 25 mégapixels.');
  const factor=Math.min(1,1024/Math.max(bitmap.width,bitmap.height)),temp=document.createElement('canvas');temp.width=Math.max(1,Math.round(bitmap.width*factor));temp.height=Math.max(1,Math.round(bitmap.height*factor));
  const ctx=temp.getContext('2d',{willReadFrequently:true});ctx.drawImage(bitmap,0,0,temp.width,temp.height);
  const pixels=ctx.getImageData(0,0,temp.width,temp.height).data;let left=temp.width,top=temp.height,right=-1,bottom=-1;
  for(let y=0;y<temp.height;y++)for(let x=0;x<temp.width;x++)if(pixels[(y*temp.width+x)*4+3]>8){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);}
  if(right<left)throw Error('Cette image est entièrement transparente. Choisissez un logo visible.');
  const image=document.createElement('canvas');image.width=right-left+1;image.height=bottom-top+1;image.getContext('2d').drawImage(temp,left,top,image.width,image.height,0,0,image.width,image.height);
  const png=image.toDataURL('image/png');if(png.length>1900000)throw Error('Ce logo est trop détaillé. Utilisez une image plus petite.');
  return {image,png,name:file.name.slice(0,120)};
 }finally{bitmap.close();}
}
$('logoFile').addEventListener('change',async e=>{
 const file=e.target.files?.[0];if(!file||!selected||submitting)return;const id=selected.id,sequence=++uploadSequence;
 uploading=true;emit('bmv:pause');status('Préparation de votre logo…');$('spotPanelClaim').disabled=true;
 try{const logo=await readLogo(file);if(sequence!==uploadSequence||selected?.id!==id)return;lastLogo=logo;Object.assign(draftFor(id),{logo,scale:.85,x:.5,y:.5,requestId:null,receipt:null});$('logoRequestForm').hidden=true;status('Logo prêt. Faites-le glisser dans l’aperçu ou ajustez sa taille.');refresh();}
 catch(error){if(sequence===uploadSequence){status(error.message,true);}}
 finally{if(sequence===uploadSequence){uploading=false;refresh();}}
});
$('spotPanelClaim').addEventListener('click',()=>{if(!selected||uploading||submitting||!draftFor(selected.id).logo)return;emit('bmv:pause');$('logoRequestForm').hidden=false;$('spotPanelClaim').hidden=true;$('requestCompany').focus({preventScroll:true});});
function lockForm(locked){submitting=locked;for(const input of $('spotPanel').querySelectorAll('input,button'))input.disabled=locked;$('spotChoice').disabled=locked;document.querySelector('.view-tabs').inert=locked;$('vanCanvas').style.pointerEvents=locked?'none':'';if($('resetVan'))$('resetVan').disabled=locked;}
$('logoRequestForm').addEventListener('submit',async e=>{
 e.preventDefault();if(!selected||submitting||uploading||!e.currentTarget.reportValidity())return;
 const spot=selected,d=draftFor(spot.id);if(window.BMV_CONFIRMED?.has(spot.id)){status('Cet emplacement est déjà confirmé. Choisissez-en un autre.',true);return;}if(!d.logo)return;
 const artwork=drawArtwork(spot,d).toDataURL('image/png');if(artwork.length>1900000){status('Utilisez un logo plus simple ou plus petit.',true);return;}
 d.requestId=d.requestId||crypto.randomUUID();const payload={id:d.requestId,spotId:spot.id,version,company:$('requestCompany').value.trim(),email:$('requestEmail').value.trim(),website_check:e.currentTarget.elements.website_check.value,logoName:d.logo.name,logo:d.logo.png,artwork,adjustment:{scale:d.scale,x:d.x,y:d.y}};
 // Reuse the same id only when retrying the exact same submission.
 const signature=JSON.stringify({...payload,id:''});if(d.submission&&d.submission!==signature){d.requestId=crypto.randomUUID();payload.id=d.requestId;}d.submission=signature;
 lockForm(true);emit('bmv:pause');status('Envoi de votre logo et de son placement…');$('sendLogoRequest').textContent='Envoi…';
 try{
  const response=await fetch('/api/counter?operation=brandmyvan-request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(25000)});
  const data=await response.json().catch(()=>({}));if(!response.ok||!data.id)throw Error(data.error||'La demande ne peut pas être enregistrée. Réessayez.');
  d.receipt=data.id;$('logoRequestForm').hidden=true;status();
 }catch(error){status(error.name==='TimeoutError'?'La connexion a expiré. Réessayez : la même demande sera vérifiée sans être dupliquée.':error.message,true);}
 finally{lockForm(false);$('sendLogoRequest').textContent='Envoyer ma demande';refresh();}
});

window.addEventListener('bmv:availability',()=>{if(selected&&window.BMV_CONFIRMED?.has(selected.id)){status('Cet emplacement vient d’être confirmé. Choisissez-en un autre pour envoyer votre demande.',true);refresh();}});
