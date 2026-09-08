import * as THREE from 'three';
import { OrbitControls } from '../vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from '../vendor/examples/jsm/loaders/GLTFLoader.js';
import { DecalGeometry } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/geometries/DecalGeometry.js';

const API='https://zzicsafjzmvbfrgaizot.supabase.co/functions/v1/brandmyvan-auction';
const SPOTS=[
  {id:1,name:'Driver door',point:[24,25,22],normal:[1,0,0],size:[17,10],aspect:17/10},
  {id:3,name:'Left cargo',point:[23.7,37,-30],normal:[1,0,0],size:[29,15],aspect:29/15},
  {id:5,name:'Rear left',point:[12,35,-72],normal:[0,0,-1],size:[12,11],aspect:12/11},
];
const $=id=>document.getElementById(id);
const canvas=$('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.2;

const scene=new THREE.Scene();
scene.background=new THREE.Color('#f4f1e8');
const camera=new THREE.PerspectiveCamera(36,1,.01,100);
camera.position.set(4,2.6,5);
const controls=new OrbitControls(camera,canvas);
controls.target.set(0,.9,0);
controls.enableDamping=true;
controls.enablePan=false;
controls.minDistance=3.5;
controls.maxDistance=10;
controls.maxPolarAngle=Math.PI/2-.02;
controls.autoRotateSpeed=.55;

scene.add(new THREE.HemisphereLight(0xffffff,0xb5b0a3,3));
for(const [p,intensity] of [[[3,6,5],3],[[-4,3,-3],1.5]]){
  const light=new THREE.DirectionalLight(0xffffff,intensity);
  light.position.set(...p);
  scene.add(light);
}

const loader=new GLTFLoader();
const raycaster=new THREE.Raycaster();
const decals=new Map();
const bodyMeshes=[];
let selected=1;
let guidesVisible=true;
let fileUrl=null;
let scaleRef=1;
let originRef=new THREE.Vector3();

function resize(){
  const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),pr=renderer.getPixelRatio();
  if(canvas.width!==Math.round(w*pr)||canvas.height!==Math.round(h*pr))renderer.setSize(w,h,false);
  camera.aspect=w/h;
  camera.updateProjectionMatrix();
}
function animate(){
  requestAnimationFrame(animate);
  resize();
  controls.update();
  renderer.render(scene,camera);
}
animate();

function guideTexture(spot){
  const W=1024,H=Math.max(360,Math.round(W/spot.aspect));
  const c=document.createElement('canvas');c.width=W;c.height=H;
  const x=c.getContext('2d');
  x.fillStyle='rgba(220,255,41,.34)';x.fillRect(8,8,W-16,H-16);
  x.strokeStyle='#111';x.lineWidth=12;x.setLineDash([30,20]);x.strokeRect(18,18,W-36,H-36);x.setLineDash([]);
  x.fillStyle='#111';x.textAlign='center';x.textBaseline='middle';
  x.font='900 96px Arial';x.fillText(String(spot.id).padStart(2,'0'),W/2,H*.44);
  x.font='900 34px Arial';x.fillText('SPONSOR AREA',W/2,H*.66);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;return t;
}
function imageTexture(src,spot){
  return new Promise((resolve,reject)=>{
    const im=new Image();im.crossOrigin='anonymous';
    im.onload=()=>{
      const W=1024,H=Math.max(360,Math.round(W/spot.aspect)),c=document.createElement('canvas');
      c.width=W;c.height=H;
      const x=c.getContext('2d'),pad=Math.round(Math.min(W,H)*.06);
      x.fillStyle='rgba(255,255,255,.98)';x.fillRect(0,0,W,H);
      const k=Math.min((W-pad*2)/im.width,(H-pad*2)/im.height),dw=im.width*k,dh=im.height*k;
      x.drawImage(im,(W-dw)/2,(H-dh)/2,dw,dh);
      const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;resolve(t);
    };
    im.onerror=()=>reject(Error('Logo image failed'));
    im.src=src;
  });
}
function decalMaterial(map,isGuide=true){
  return new THREE.MeshBasicMaterial({
    map,transparent:true,opacity:isGuide?.78:1,depthWrite:false,
    polygonOffset:true,polygonOffsetFactor:-12,polygonOffsetUnits:-12,side:THREE.DoubleSide
  });
}
function worldPoint(spot){
  return new THREE.Vector3(...spot.point).sub(originRef).multiplyScalar(scaleRef);
}
function surfaceHit(spot){
  const n=new THREE.Vector3(...spot.normal).normalize();
  const seed=worldPoint(spot);
  const start=seed.clone().addScaledVector(n,Math.max(.18,8*scaleRef));
  raycaster.set(start,n.clone().multiplyScalar(-1));
  raycaster.near=0;
  raycaster.far=Math.max(.75,35*scaleRef);
  const hits=raycaster.intersectObjects(bodyMeshes,false);
  if(!hits.length)return null;
  hits.sort((a,b)=>a.point.distanceToSquared(seed)-b.point.distanceToSquared(seed));
  return hits[0];
}
function orientationFor(normal){
  const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),normal.clone().normalize());
  return new THREE.Euler().setFromQuaternion(q);
}
function buildDecal(spot){
  const hit=surfaceHit(spot);
  if(!hit)return null;
  const n=new THREE.Vector3(...spot.normal).normalize();
  const pos=hit.point.clone().addScaledVector(n,.0025);
  const size=new THREE.Vector3(spot.size[0]*scaleRef,spot.size[1]*scaleRef,Math.max(.08,5.5*scaleRef));
  const geometry=new DecalGeometry(hit.object,pos,orientationFor(n),size);
  if(!geometry.attributes.position?.count)return null;
  const mesh=new THREE.Mesh(geometry,decalMaterial(guideTexture(spot),true));
  mesh.renderOrder=40;
  mesh.userData={spotId:spot.id,isGuide:true,target:hit.object.name||''};
  scene.add(mesh);
  decals.set(spot.id,mesh);
  return mesh;
}
async function applyLogo(id,src){
  const spot=SPOTS.find(s=>s.id===id),mesh=decals.get(id);
  if(!spot||!mesh)return;
  const tex=await imageTexture(src,spot);
  mesh.material.map?.dispose?.();
  mesh.material.dispose?.();
  mesh.material=decalMaterial(tex,false);
  mesh.userData.isGuide=false;
  mesh.visible=true;
}
function restore(id){
  const spot=SPOTS.find(s=>s.id===id),mesh=decals.get(id);
  if(!spot||!mesh)return;
  mesh.material.map?.dispose?.();
  mesh.material.dispose?.();
  mesh.material=decalMaterial(guideTexture(spot),true);
  mesh.userData.isGuide=true;
  mesh.visible=guidesVisible;
}
async function live(){
  try{
    const r=await fetch(API,{cache:'no-store'});
    if(!r.ok)throw Error('HTTP '+r.status);
    const d=await r.json(),names=[];
    for(const spot of SPOTS){
      const s=(d.spots||[]).find(x=>Number(x.id)===spot.id);
      if(s?.winner_logo_url){
        await applyLogo(spot.id,s.winner_logo_url);
        names.push(`${String(spot.id).padStart(2,'0')} ${s.winner_company||'sponsor'}`);
      }
    }
    $('liveStatus').textContent='Live auction connected';
    $('liveText').textContent=names.length?'Applied: '+names.join(' · '):'No winner logo on 01/03/05';
  }catch(e){
    $('liveStatus').textContent='Live auction unavailable';
    $('liveText').textContent=e.message;
  }
}
async function boot(){
  try{
    $('status').textContent='LOADING REAL GLB…';
    const van=await loader.loadAsync('../van-realistic.glb',e=>{
      if(e.total)$('status').textContent=`LOADING REAL GLB · ${Math.round(e.loaded/e.total*100)}%`;
    });
    const model=van.scene;
    const box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
    scaleRef=4/Math.max(size.x,size.y,size.z);
    originRef=new THREE.Vector3(center.x,box.min.y,center.z);
    model.scale.setScalar(scaleRef);
    model.position.copy(originRef).multiplyScalar(-scaleRef);
    scene.add(model);
    scene.updateMatrixWorld(true);

    model.traverse(o=>{
      if(!o.isMesh)return;
      const mats=Array.isArray(o.material)?o.material:[o.material];
      const names=mats.map(m=>(m?.name||'').toLowerCase()).join(' ');
      if(/glass|window|wheel|tire|tyre/.test(names))return;
      bodyMeshes.push(o);
    });
    if(bodyMeshes.length<2)model.traverse(o=>{if(o.isMesh&&!bodyMeshes.includes(o))bodyMeshes.push(o)});

    for(const spot of SPOTS)buildDecal(spot);
    controls.target.set(0,.9,0);
    camera.position.set(4,2.6,5);
    controls.update();
    controls.saveState();

    const ok=SPOTS.filter(s=>decals.has(s.id)).length;
    $('status').textContent=ok===SPOTS.length?'READY · REAL GLB + SURFACE DECALS':`PARTIAL · ${ok}/${SPOTS.length} DECALS`;
    $('diag').textContent=`GLB: direct static file\nBase64 payload: NONE\nbody meshes: ${bodyMeshes.length}\ndecals: ${ok}/${SPOTS.length}\n01: ${decals.has(1)?'OK':'MISS'}\n03: ${decals.has(3)?'OK':'MISS'}\n05: ${decals.has(5)?'OK':'MISS'}\nruntime raycast: YES\nDecalGeometry: YES`;
    await live();
  }catch(e){
    console.error(e);
    $('status').textContent='LOAD ERROR · '+(e.message||e);
    $('diag').textContent=String(e.stack||e);
  }
}

document.querySelectorAll('.zone').forEach(b=>b.onclick=()=>{
  selected=Number(b.dataset.id);
  document.querySelectorAll('.zone').forEach(x=>x.classList.toggle('active',x===b));
});
$('file').onchange=e=>{
  if(fileUrl)URL.revokeObjectURL(fileUrl);
  const f=e.target.files?.[0];
  fileUrl=f?URL.createObjectURL(f):null;
};
$('apply').onclick=()=>fileUrl?applyLogo(selected,fileUrl):alert('Choose an image first.');
$('restore').onclick=()=>restore(selected);
$('guides').onclick=()=>{
  guidesVisible=!guidesVisible;
  for(const mesh of decals.values())if(mesh.userData.isGuide)mesh.visible=guidesVisible;
  $('guides').textContent=guidesVisible?'HIDE FREE GUIDES':'SHOW FREE GUIDES';
};
$('rotate').onclick=()=>{
  controls.autoRotate=!controls.autoRotate;
  $('rotate').textContent=controls.autoRotate?'STOP ROTATE':'AUTO ROTATE';
};
$('reset').onclick=()=>{
  controls.autoRotate=false;
  $('rotate').textContent='AUTO ROTATE';
  controls.reset();
};
boot();
