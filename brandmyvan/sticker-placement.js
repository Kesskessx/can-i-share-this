import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';
import { DecalGeometry } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/geometries/DecalGeometry.js';

const RESERVE_API='https://zzicsafjzmvbfrgaizot.supabase.co/functions/v1/brandmyvan-sticker-reserve';
const ANON_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6aWNzYWZqem12YmZyZ2Fpem90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg0ODE3NTgsImV4cCI6MjEwNDA1Nzc1OH0.zRvaGUhJU1CPrld90GuIZ27naY40OyzhrgxvDlvtRz0';
const STICKER_CM=10;
const STICKER_WORLD=0.068;
const MIN_GAP=STICKER_WORLD*1.35;

const $=id=>document.getElementById(id);
const canvas=$('vanCanvas');
const status=$('viewerStatus');
const placementTitle=$('placementTitle');
const placementInfo=$('placementInfo');
const reserveBtn=$('reserveBtn');
const reserveMsg=$('reserveMsg');
const logoPreview=$('logoPreview');

let logoUrl='';
let logoName='';
let shape='circle';
let previewMesh=null;
let currentPlacement=null;
let confirmedMeshes=[];
const occupiedPoints=[];
const bodyMeshes=[];

function setMessage(text,type=''){
  reserveMsg.textContent=text;
  reserveMsg.className='msg'+(type?` ${type}`:'');
}
function round3(v){return v.toArray().map(n=>Number(n.toFixed(6)))}
function stopAuto(){controls.autoRotate=false;$('rotate').classList.remove('active');$('rotate').textContent='AUTO ROTATE'}
function placementReady(){
  const ready=!!currentPlacement;
  reserveBtn.disabled=!ready;
  reserveBtn.textContent=ready?'RESERVE THIS PLACEMENT — €49':'SELECT A POSITION FIRST';
}

function placeholderCanvas(){
  const c=document.createElement('canvas');c.width=512;c.height=512;const x=c.getContext('2d');
  x.fillStyle='#111';x.fillRect(0,0,512,512);x.fillStyle='#dcff29';x.textAlign='center';x.textBaseline='middle';x.font='900 56px Arial';x.fillText('YOUR',256,214);x.fillText('LOGO',256,286);return c;
}
logoPreview.src=placeholderCanvas().toDataURL('image/png');

function loadImage(src){return new Promise((resolve,reject)=>{const im=new Image();im.crossOrigin='anonymous';im.onload=()=>resolve(im);im.onerror=()=>reject(new Error('Logo image could not load'));im.src=src})}
async function stickerTexture(src,kind='circle'){
  const c=document.createElement('canvas');c.width=768;c.height=768;const x=c.getContext('2d');x.clearRect(0,0,768,768);
  const im=src?await loadImage(src):placeholderCanvas();
  x.save();
  if(kind==='circle'){x.beginPath();x.arc(384,384,352,0,Math.PI*2);x.clip()}else{const r=54;x.beginPath();x.roundRect(30,30,708,708,r);x.clip()}
  x.fillStyle='#fff';x.fillRect(0,0,768,768);
  const pad=86,k=Math.min((768-pad*2)/im.width,(768-pad*2)/im.height),w=im.width*k,h=im.height*k;
  x.drawImage(im,(768-w)/2,(768-h)/2,w,h);x.restore();
  x.strokeStyle='#fff';x.lineWidth=28;
  if(kind==='circle'){x.beginPath();x.arc(384,384,354,0,Math.PI*2);x.stroke()}else{x.beginPath();x.roundRect(30,30,708,708,54);x.stroke()}
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;t.needsUpdate=true;return t;
}
function orientationFor(normal){
  const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),normal.clone().normalize());
  return new THREE.Euler().setFromQuaternion(q);
}
function decalMaterial(map,opacity=1){return new THREE.MeshBasicMaterial({map,transparent:true,opacity,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-10,polygonOffsetUnits:-10,side:THREE.DoubleSide})}
function disposeMesh(mesh){if(!mesh)return;scene.remove(mesh);mesh.geometry?.dispose?.();mesh.material?.map?.dispose?.();mesh.material?.dispose?.()}
function meshLabel(mesh){const mats=Array.isArray(mesh.material)?mesh.material:[mesh.material];return `${mesh.name||''} ${mats.map(m=>m?.name||'').join(' ')}`.toLowerCase()}
function isRestrictedMesh(mesh){
  return /glass|window|windshield|wheel|tire|tyre|rim|lamp|light|headlight|taillight|mirror|interior|seat|steering|dashboard|wiper|badge|emblem|logo|handle|plate|license|grill|grille/.test(meshLabel(mesh));
}
function isPlacementAllowed(hit,normal){
  if(!hit?.object || isRestrictedMesh(hit.object))return {ok:false,reason:'That part is not printable.'};
  if(hit.point.y<0.34)return {ok:false,reason:'Too low on the van. Choose a body panel.'};
  if(normal.y<-0.38)return {ok:false,reason:'The underside is not an allowed sticker area.'};
  for(const p of occupiedPoints)if(p.distanceTo(hit.point)<MIN_GAP)return {ok:false,reason:'Too close to another confirmed sticker.'};
  return {ok:true};
}
async function makeStickerOn(object,point,normal,textureSrc,kind,opacity=1){
  const pos=point.clone().addScaledVector(normal,.0028);
  const size=new THREE.Vector3(STICKER_WORLD,STICKER_WORLD,Math.max(.055,STICKER_WORLD*.9));
  const geometry=new DecalGeometry(object,pos,orientationFor(normal),size);
  if(!geometry.attributes.position?.count)throw new Error('This surface is too complex for a clean sticker.');
  const texture=await stickerTexture(textureSrc,kind);
  const mesh=new THREE.Mesh(geometry,decalMaterial(texture,opacity));mesh.renderOrder=50;scene.add(mesh);return mesh;
}
async function rebuildPreview(){
  if(!currentPlacement)return;
  disposeMesh(previewMesh);previewMesh=null;
  try{
    previewMesh=await makeStickerOn(currentPlacement.object,currentPlacement.point,currentPlacement.normal,logoUrl,shape,1);
    previewMesh.userData.preview=true;
  }catch(e){
    currentPlacement=null;placementReady();placementTitle.textContent='Choose another point';placementInfo.textContent=e.message||'Sticker projection failed.';setMessage('Choose another bodywork point.','err');
  }
}
async function placeFromHit(hit){
  if(!logoUrl){placementTitle.textContent='Upload your logo first';placementInfo.textContent='The 3D position tool activates after a logo is selected.';setMessage('Upload a logo before choosing the position.','err');return}
  const normal=hit.face?.normal?.clone();if(!normal)return;
  normal.transformDirection(hit.object.matrixWorld).normalize();
  const allowed=isPlacementAllowed(hit,normal);
  if(!allowed.ok){placementTitle.textContent='Position blocked';placementInfo.textContent=allowed.reason;setMessage(allowed.reason,'err');return}
  currentPlacement={object:hit.object,point:hit.point.clone(),normal:normal.clone()};
  await rebuildPreview();
  if(!currentPlacement)return;
  placementTitle.textContent='10 cm sticker positioned';
  placementInfo.textContent='Rotate the van to inspect it. Click somewhere else to move it.';
  placementReady();setMessage('Valid placement selected. The exact 3D coordinates will be saved with the reservation.','ok');
}
function removePreview(){disposeMesh(previewMesh);previewMesh=null;currentPlacement=null;placementReady();placementTitle.textContent='Upload a logo, then click the van';placementInfo.textContent='No position selected yet.';setMessage('Reservation status: waiting for a valid 3D placement.');}

const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.24;
const scene=new THREE.Scene();scene.background=new THREE.Color('#efede5');
const camera=new THREE.PerspectiveCamera(36,1,.01,100);camera.position.set(4,2.5,5);
const controls=new OrbitControls(camera,canvas);controls.target.set(0,.9,0);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=3.2;controls.maxDistance=9.5;controls.maxPolarAngle=Math.PI/2-.015;controls.autoRotateSpeed=.55;
scene.add(new THREE.HemisphereLight(0xffffff,0xb7b1a5,3));
for(const [p,i] of [[[3,6,5],3.2],[[-4,3,-3],1.5]]){const l=new THREE.DirectionalLight(0xffffff,i);l.position.set(...p);scene.add(l)}
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();

function resize(){const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),pr=renderer.getPixelRatio();if(canvas.width!==Math.round(w*pr)||canvas.height!==Math.round(h*pr))renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
renderer.setAnimationLoop(()=>{resize();controls.update();renderer.render(scene,camera)});
controls.addEventListener('start',stopAuto);

let downX=0,downY=0;
canvas.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY});
canvas.addEventListener('pointerup',async e=>{
  if(Math.hypot(e.clientX-downX,e.clientY-downY)>7)return;
  const r=canvas.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1;ray.setFromCamera(pointer,camera);
  const hit=ray.intersectObjects(bodyMeshes,false)[0];if(hit)await placeFromHit(hit);else{placementTitle.textContent='Click directly on the metal body';placementInfo.textContent='No printable surface was detected at that point.'}
});

$('reset').addEventListener('click',()=>{stopAuto();camera.position.set(4,2.5,5);controls.target.set(0,.9,0);controls.update()});
$('rotate').addEventListener('click',()=>{controls.autoRotate=!controls.autoRotate;$('rotate').classList.toggle('active',controls.autoRotate);$('rotate').textContent=controls.autoRotate?'STOP ROTATE':'AUTO ROTATE'});
$('undo').addEventListener('click',removePreview);
$('circle').addEventListener('click',async()=>{shape='circle';$('circle').classList.add('active');$('square').classList.remove('active');await rebuildPreview()});
$('square').addEventListener('click',async()=>{shape='square';$('square').classList.add('active');$('circle').classList.remove('active');await rebuildPreview()});

$('logoFile').addEventListener('change',async e=>{
  const f=e.target.files?.[0];if(!f)return;
  if(!/^image\/(png|jpeg|webp)$/.test(f.type)){setMessage('Use PNG, JPG or WebP.','err');e.target.value='';return}
  if(f.size>2*1024*1024){setMessage('Keep the logo under 2 MB.','err');e.target.value='';return}
  if(logoUrl)URL.revokeObjectURL(logoUrl);logoUrl=URL.createObjectURL(f);logoName=f.name;logoPreview.src=logoUrl;
  placementTitle.textContent='Logo ready — click the van';placementInfo.textContent='Rotate to the side you want, then click an allowed metal surface.';setMessage('Logo loaded. Choose the exact position on the 3D van.','ok');
  if(currentPlacement)await rebuildPreview();
});

async function loadConfirmed(){
  try{
    const r=await fetch(RESERVE_API,{headers:{Authorization:`Bearer ${ANON_KEY}`,apikey:ANON_KEY},cache:'no-store'});if(!r.ok)return;
    const data=await r.json();
    for(const s of data.stickers||[]){
      if(!s?.logo_url||!Array.isArray(s?.placement?.point)||!Array.isArray(s?.placement?.normal))continue;
      const point=new THREE.Vector3(...s.placement.point),normal=new THREE.Vector3(...s.placement.normal).normalize();
      ray.set(point.clone().addScaledVector(normal,.15),normal.clone().multiplyScalar(-1));ray.near=0;ray.far=.45;
      const hit=ray.intersectObjects(bodyMeshes,false)[0];if(!hit)continue;
      try{const mesh=await makeStickerOn(hit.object,point,normal,s.logo_url,s.sticker_shape||'circle',1);confirmedMeshes.push(mesh);occupiedPoints.push(point.clone())}catch{}
    }
  }catch(e){console.warn('Confirmed sticker load unavailable',e)}
}

$('reserveForm').addEventListener('submit',async e=>{
  e.preventDefault();if(!currentPlacement)return;
  const company=$('company').value.trim(),email=$('email').value.trim(),website=$('website').value.trim(),websiteTrap=$('websiteTrap').value;
  reserveBtn.disabled=true;reserveBtn.textContent='SAVING POSITION…';setMessage('Saving your exact 3D placement…');
  const payload={company,email,website,websiteTrap,logoName,sizeCm:STICKER_CM,shape,placement:{point:round3(currentPlacement.point),normal:round3(currentPlacement.normal),objectName:String(currentPlacement.object.name||'').slice(0,180)}};
  try{
    const r=await fetch(RESERVE_API,{method:'POST',headers:{Authorization:`Bearer ${ANON_KEY}`,apikey:ANON_KEY,'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error(data.error||'Reservation failed');
    setMessage(`Placement reserved. Reference ${String(data.id).slice(0,8).toUpperCase()} · payment status: pending. Payment can now be connected without changing your chosen 3D position.`,'ok');
    reserveBtn.textContent='PLACEMENT RESERVED';placementTitle.textContent='Position reserved';placementInfo.textContent=`Reference ${String(data.id).slice(0,8).toUpperCase()} · €${data.price_eur}`;
  }catch(err){setMessage(err.message||'Reservation failed.','err');reserveBtn.disabled=false;reserveBtn.textContent='RESERVE THIS PLACEMENT — €49'}
});

async function boot(){
  try{
    status.textContent='LOADING THE REAL VAN…';
    const gltf=await new GLTFLoader().loadAsync('./van-realistic.glb',e=>{if(e.total)status.textContent=`LOADING THE REAL VAN · ${Math.round(e.loaded/e.total*100)}%`});
    const model=gltf.scene;const box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3()),scale=4/Math.max(size.x,size.y,size.z),origin=new THREE.Vector3(center.x,box.min.y,center.z);
    model.scale.setScalar(scale);model.position.copy(origin).multiplyScalar(-scale);scene.add(model);scene.updateMatrixWorld(true);
    model.traverse(o=>{if(!o.isMesh||isRestrictedMesh(o))return;bodyMeshes.push(o)});
    if(!bodyMeshes.length)model.traverse(o=>{if(o.isMesh)bodyMeshes.push(o)});
    status.textContent='READY · UPLOAD LOGO · CLICK THE BODY';
    await loadConfirmed();
  }catch(e){console.error(e);status.textContent='THE REAL VAN COULD NOT LOAD';placementTitle.textContent='3D load error';placementInfo.textContent=e.message||String(e)}
}
boot();
