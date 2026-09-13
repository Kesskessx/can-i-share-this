export function startFallback(){
 const $=id=>document.getElementById(id),{spots,model}=window.BMV_CONFIG;
 const emit=(name,detail)=>window.dispatchEvent(new CustomEvent(name,{detail}));
 const stage=$('vanStage'),viewer=$('vanCanvas').parentElement;
 $('vanCanvas').hidden=true;stage.classList.add('fallback-active');
 const wrap=document.createElement('div');wrap.className='van-flat-wrap';
 const plane=document.createElement('div');plane.className='van-flat-plane';
 const photo=document.createElement('img');photo.alt='Van side preview';photo.draggable=false;
 plane.append(photo);wrap.append(plane);viewer.append(wrap);
 const note=document.createElement('p');note.className='van-flat-note';note.textContent='2D preview · 3D is not supported in this browser. Your logo editor remains available.';viewer.append(note);
 let current='left',selected=null;const artwork=new Map(),buttons=new Map();
 for(const spot of spots){
  const button=document.createElement('button');button.type='button';button.className='van-flat-spot';button.setAttribute('aria-label',spot.id+' · '+spot.tier+' · €'+spot.price);
  const drawing=document.createElement('canvas');drawing.hidden=true;const label=document.createElement('span');label.textContent=spot.id;button.append(drawing,label);
  button.addEventListener('click',()=>{if($('spotChoice').disabled)return;selected=spot.id;show(spot.view);emit('bmv:spot',spot.id);});
  buttons.set(spot.id,{button,drawing,label});plane.append(button);
 }
 function show(view){
  current=view;photo.src='./fallback-'+view+'.png';photo.alt='Van '+view+' view';
  const width=view==='rear'?model.width:model.length;
  plane.style.aspectRatio=String(width/model.height);
  plane.style.width=view==='rear'?'min(60%, 320px)':'100%';
  for(const s of spots){const {button}=buttons.get(s.id);button.hidden=s.view!==view;
   const flip=view!=='right',x=flip?1-s.u:s.u;
   Object.assign(button.style,{left:(x-s.uw/2)*100+'%',top:(1-s.v-s.vh/2)*100+'%',width:s.uw*100+'%',height:s.vh*100+'%'});
   button.classList.toggle('selected',s.id===selected);button.setAttribute('aria-pressed',String(s.id===selected));
  }
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  $('viewLabel').textContent=view.toUpperCase()+' · 2D PREVIEW';$('viewerTip').textContent='Tap a spot or use the list';
 }
 document.querySelectorAll('[data-view]').forEach(b=>{
  if(b.dataset.view==='free'){b.disabled=true;b.textContent='3D unavailable';b.title='Open in a browser with WebGL support to rotate the van';}
  else b.addEventListener('click',()=>{selected=null;show(b.dataset.view);emit('bmv:closed');});
 });
 $('resetVan').addEventListener('click',()=>{selected=null;show(current);emit('bmv:closed');});
 for(const id of ['inspectLogo','editLogo'])$(id).hidden=true;
 window.addEventListener('bmv:select',e=>{const s=spots.find(s=>s.id===e.detail);if(s){selected=s.id;show(s.view);}});
 window.addEventListener('bmv:deselect',()=>{selected=null;show(current);});
 window.addEventListener('bmv:artwork',e=>{
  const {id,canvas,hasLogo}=e.detail,entry=buttons.get(id);if(!entry)return;
  entry.drawing.hidden=!hasLogo;entry.label.hidden=hasLogo;entry.button.classList.toggle('has-logo',hasLogo);
  if(hasLogo){entry.drawing.width=canvas.width;entry.drawing.height=canvas.height;entry.drawing.getContext('2d').drawImage(canvas,0,0);}
 });
 show('left');emit('bmv:ready');
}
