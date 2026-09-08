import * as THREE from 'three';
import { OrbitControls } from 'https://cdn.jsdelivr.net/gh/Kesskessx/can-i-share-this@brandmyvan-real-glb/brandmyvan/vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/gh/Kesskessx/can-i-share-this@brandmyvan-real-glb/brandmyvan/vendor/examples/jsm/loaders/GLTFLoader.js';
import { DecalGeometry } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/geometries/DecalGeometry.js';

const stage=document.querySelector('#van');
const status=document.querySelector('#status');
const grid=document.querySelector('#grid');

const spots=[
 {id:1,name:'Driver door',price:420,point:[24,25,22],normal:[1,0,0],size:[17,10],tier:'MEDIUM',panel:'Front door'},
 {id:2,name:'Passenger door',price:420,point:[-24,25,22],normal:[-1,0,0],size:[17,10],tier:'MEDIUM',panel:'Front door'},
 {id:3,name:'Left premium panel',price:650,point:[23.7,37,-30],normal:[1,0,0],size:[29,15],tier:'PREMIUM',panel:'Side panel'},
 {id:4,name:'Right premium panel',price:650,point:[-23.7,37,-30],normal:[-1,0,0],size:[29,15],tier:'PREMIUM',panel:'Side panel'},
 {id:5,name:'Rear left premium',price:350,point:[12,35,-72],normal:[0,0,-1],size:[12,11],tier:'MEDIUM',panel:'Rear door'},
 {id:6,name:'Rear right premium',price:350,point:[-12,35,-72],normal:[0,0,-1],size:[12,11],tier:'MEDIUM',panel:'Rear door'},
 {id:7,name:'Hood premium',price:800,point:[0,25.5,54],normal:[0,.58,.82],size:[22,11],tier:'PREMIUM',panel:'Hood'},
 {id:8,name:'Roof premium',price:900,point:[0,60.5,-24],normal:[0,1,0],size:[25,12],tier:'PREMIUM',panel:'Roof'},
];

const sideZ=[6,-7,-51,-63];
for(let r=0;r<2;r++) for(let c=0;c<4;c++){
  const id=9+r*4+c;
  spots.push({id,name:`Left sticker ${String.fromCharCode(65+r)}${c+1}`,price:50,point:[24.1,r?48:26.5,sideZ[c]],normal:[1,0,0],size:[9.5,6.4],tier:'SMALL',panel:'Left side'});
}
for(let r=0;r<2;r++) for(let c=0;c<4;c++){
  const id=17+r*4+c;
  spots.push({id,name:`Right sticker ${String.fromCharCode(65+r)}${c+1}`,price:50,point:[-24.1,r?48:26.5,sideZ[c]],normal:[-1,0,0],size:[9.5,6.4],tier:'SMALL',panel:'Right side'});
}
[
 {id:25,name:'Rear sticker A1',point:[8.2,48,-72.2]},
 {id:26,name:'Rear sticker A2',point:[-8.2,48,-72.2]},
 {id:27,name:'Rear sticker B1',point:[8.2,22.5,-72.2]},
 {id:28,name:'Rear sticker B2',point:[-8.2,22.5,-72.2]},
].forEach(s=>spots.push({...s,price:50,normal:[0,0,-1],size:[7.8,5.8],tier:'SMALL',panel:'Rear'}));
[
 {id:29,name:'Roof sticker A1',point:[8.5,60.6,6]},
 {id:30,name:'Roof sticker A2',point:[-8.5,60.6,6]},
 {id:31,name:'Roof sticker B1',point:[8.5,60.6,-50]},
 {id:32,name:'Roof sticker B2',point:[-8.5,60.6,-50]},
].forEach(s=>spots.push({...s,price:75,normal:[0,1,0],size:[9.2,6.2],tier:'SMALL',panel:'Roof'}));

let sceneRef=null, scaleRef=1, originRef=null, focusSpot=()=>{}, selectedIndex=0;
let modelRoot=null;
const decalMeshes=new Map(), decalState=new Map(), bodyMeshes=[];
const projectorRay=new THREE.Raycaster();

function euro(n){return `€${Math.round(Number(n)||0)}`}
function cardFor(s){
  const el=document.createElement('button');el.type='button';el.className='card';el.dataset.spotId=s.id;
  el.innerHTML=`<span class="num">${String(s.id).padStart(2,'0')} · ${s.tier}</span><b>${s.name}</b><strong>${euro(s.price)}</strong><small>${s.panel}</small>`;
  el.addEventListener('click',()=>selectSpot(s.id-1));grid?.append(el);s.card=el;
}
spots.forEach(cardFor);

function selectSpot(i,focus=true){
  selectedIndex=Math.max(0,Math.min(spots.length-1,i));
  spots.forEach((s,j)=>s.card?.classList.toggle('active',selectedIndex===j));
  const s=spots[selectedIndex];
  document.querySelector('#selname').textContent=`${String(s.id).padStart(2,'0')} — ${s.name}`;
  document.querySelector('#selprice').textContent=`From ${euro(s.price)}`;
  decalMeshes.forEach((m,id)=>{m.material.opacity=id===s.id?1:(decalState.get(id)?.logoUrl?1:.72)});
  if(focus)focusSpot(s);
}
selectSpot(0,false);

function baseCanvas(s){
  const c=document.createElement('canvas');c.width=640;c.height=400;const x=c.getContext('2d');
  const premium=s.tier==='PREMIUM',medium=s.tier==='MEDIUM';x.clearRect(0,0,c.width,c.height);
  x.fillStyle=premium?'rgba(220,255,41,.58)':medium?'rgba(220,255,41,.42)':'rgba(220,255,41,.30)';x.fillRect(8,8,624,384);
  x.strokeStyle='rgba(17,17,17,.84)';x.lineWidth=premium?14:10;x.strokeRect(12,12,616,376);
  x.fillStyle='#111';x.textAlign='center';x.font=premium?'900 86px Arial':medium?'900 76px Arial':'900 66px Arial';x.fillText(String(s.id).padStart(2,'0'),320,170);
  x.font='900 34px Arial';x.fillText(s.tier,320,222);x.font='700 31px Arial';x.fillText(`FROM ${euro(s.price)}`,320,285);return c;
}
function canvasTexture(c){const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;t.needsUpdate=true;return t}
function emptyTexture(s){return canvasTexture(baseCanvas(s))}
function loadImage(url){return new Promise((resolve,reject)=>{const i=new Image();i.crossOrigin='anonymous';i.onload=()=>resolve(i);i.onerror=reject;i.src=url})}
async function logoTexture(s,url){
  const c=document.createElement('canvas');c.width=640;c.height=400;const x=c.getContext('2d');x.clearRect(0,0,640,400);x.fillStyle='rgba(255,255,255,.98)';x.fillRect(8,8,624,384);
  x.strokeStyle='#111';x.lineWidth=s.tier==='PREMIUM'?12:8;x.strokeRect(12,12,616,376);
  const img=await loadImage(url),pad=s.tier==='PREMIUM'?24:18,W=640-pad*2,H=400-pad*2,k=Math.min(W/img.width,H/img.height),w=img.width*k,h=img.height*k;
  x.drawImage(img,(640-w)/2,(400-h)/2,w,h);return canvasTexture(c);
}
function desiredWorldPoint(s){return new THREE.Vector3(...s.point).sub(originRef).multiplyScalar(scaleRef)}
function desiredNormal(s){return new THREE.Vector3(...s.normal).normalize()}
function projectToBody(s){
  const n=desiredNormal(s),seed=desiredWorldPoint(s),start=seed.clone().addScaledVector(n,Math.max(.18,8*scaleRef));
  projectorRay.set(start,n.clone().multiplyScalar(-1));projectorRay.near=0;projectorRay.far=Math.max(.75,35*scaleRef);
  const hits=projectorRay.intersectObjects(bodyMeshes,false);if(!hits.length)return null;
  hits.sort((a,b)=>a.point.distanceToSquared(seed)-b.point.distanceToSquared(seed));return hits[0];
}
function orientationFor(n){const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),n.clone().normalize());return new THREE.Euler().setFromQuaternion(q)}
function disposeDecal(id){const m=decalMeshes.get(id);if(!m)return;sceneRef?.remove(m);m.geometry?.dispose();m.material?.map?.dispose();m.material?.dispose();decalMeshes.delete(id)}
function makeDecal(s,texture,logoUrl=''){
  const hit=projectToBody(s);if(!hit){console.warn('No body hit for decal',s.id);return null}
  const n=desiredNormal(s),pos=hit.point.clone().addScaledVector(n,.0025),size=new THREE.Vector3(s.size[0]*scaleRef,s.size[1]*scaleRef,Math.max(.08,5.5*scaleRef));
  let geometry;try{geometry=new DecalGeometry(hit.object,pos,orientationFor(n),size)}catch(e){console.warn('Decal geometry failed',s.id,e);return null}
  if(!geometry.attributes.position?.count)return null;
  const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,opacity:logoUrl?1:.72,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-12,polygonOffsetUnits:-12,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(geometry,material);mesh.renderOrder=40;mesh.userData={spotId:s.id,spotIndex:s.id-1,target:hit.object.name||''};sceneRef.add(mesh);decalMeshes.set(s.id,mesh);decalState.set(s.id,{logoUrl});return mesh;
}
function createEmptyDecal(s){disposeDecal(s.id);return makeDecal(s,emptyTexture(s),'')}
async function applyLogo(s,url){if(!sceneRef||!url)return;const prev=decalState.get(s.id);if(prev?.logoUrl===url)return;try{const t=await logoTexture(s,url);disposeDecal(s.id);makeDecal(s,t,url)}catch(e){console.warn('logo decal failed',s.id,e)}}
function clearLogo(s){createEmptyDecal(s)}
function syncAuction(state){const byId=new Map((state?.spots||[]).map(x=>[Number(x.id),x]));for(const s of spots){const live=byId.get(s.id);if(live?.start_price!=null)s.price=Number(live.start_price);if(live?.winner_logo_url)applyLogo(s,live.winner_logo_url);else if(decalState.get(s.id)?.logoUrl)clearLogo(s)}}
window.addEventListener('brandmyvan:auction',e=>syncAuction(e.detail));if(window.__BMV_AUCTION_STATE)syncAuction(window.__BMV_AUCTION_STATE);

try{
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));renderer.setClearColor(0xfaf9f5,1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.26;stage.append(renderer.domElement);
  const scene=new THREE.Scene();sceneRef=scene;const camera=new THREE.PerspectiveCamera(36,1,.01,100);camera.position.set(4,2.6,5);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,.9,0);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=3.5;controls.maxDistance=10;controls.maxPolarAngle=Math.PI/2-.02;controls.autoRotateSpeed=.55;
  scene.add(new THREE.HemisphereLight(0xffffff,0xb5b0a3,3));for(const [p,intensity] of [[[3,6,5],3],[[-4,3,-3],1.5]]){const l=new THREE.DirectionalLight(0xffffff,intensity);l.position.set(...p);scene.add(l)}
  let desiredPosition=null;const resize=()=>{const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()};new ResizeObserver(resize).observe(stage);resize();
  const stopAuto=()=>{controls.autoRotate=false;document.querySelector('#rotate')?.setAttribute('aria-pressed','false')};controls.addEventListener('start',()=>{desiredPosition=null;stopAuto()});
  document.querySelector('#rotate')?.addEventListener('click',()=>{desiredPosition=null;controls.autoRotate=!controls.autoRotate;document.querySelector('#rotate').setAttribute('aria-pressed',String(controls.autoRotate))});document.querySelector('#reset')?.addEventListener('click',()=>{stopAuto();desiredPosition=new THREE.Vector3(4,2.6,5)});
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();status.textContent='3D VIEW INTERRUPTED · RELOAD'});

  const gltf=await new GLTFLoader().loadAsync('https://cdn.jsdelivr.net/gh/Kesskessx/can-i-share-this@brandmyvan-real-glb/brandmyvan/van-realistic.glb',e=>{if(e.total)status.textContent=`LOADING THE VAN · ${Math.round(e.loaded/e.total*100)}%`});
  modelRoot=gltf.scene;const box=new THREE.Box3().setFromObject(modelRoot),sizeBox=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const scale=4/Math.max(sizeBox.x,sizeBox.y,sizeBox.z),origin=new THREE.Vector3(center.x,box.min.y,center.z);scaleRef=scale;originRef=origin;modelRoot.scale.setScalar(scale);modelRoot.position.copy(origin).multiplyScalar(-scale);scene.add(modelRoot);scene.updateMatrixWorld(true);
  modelRoot.traverse(o=>{if(!o.isMesh)return;const mats=Array.isArray(o.material)?o.material:[o.material],names=mats.map(m=>(m?.name||'').toLowerCase()).join(' ');if(/glass|window|wheel|tire|tyre/.test(names))return;bodyMeshes.push(o)});
  if(bodyMeshes.length<2)modelRoot.traverse(o=>{if(o.isMesh&&!bodyMeshes.includes(o))bodyMeshes.push(o)});
  for(const s of spots)createEmptyDecal(s);if(window.__BMV_AUCTION_STATE)syncAuction(window.__BMV_AUCTION_STATE);
  focusSpot=s=>{stopAuto();const dir=desiredNormal(s);if(dir.y>.5)dir.set(.45,1,s.id===7?.9:-.2);else dir.y=.34;desiredPosition=controls.target.clone().add(dir.normalize().multiplyScalar(6))};
  status.textContent='REAL 3D VAN · SURFACE-FITTED SPONSOR DECALS';
  const clickRay=new THREE.Raycaster(),pointer=new THREE.Vector2();let downX=0,downY=0;
  renderer.domElement.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY});renderer.domElement.addEventListener('pointerup',e=>{if(Math.hypot(e.clientX-downX,e.clientY-downY)>7)return;const r=renderer.domElement.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1;clickRay.setFromCamera(pointer,camera);const hit=clickRay.intersectObjects([...decalMeshes.values()],false)[0];if(hit)selectSpot(hit.object.userData.spotIndex)});
  renderer.setAnimationLoop(()=>{if(desiredPosition){camera.position.lerp(desiredPosition,.085);if(camera.position.distanceTo(desiredPosition)<.01)desiredPosition=null}controls.update();renderer.render(scene,camera)});
}catch(error){console.error(error);status.textContent='THE 3D VAN COULD NOT LOAD · RETRY'}
