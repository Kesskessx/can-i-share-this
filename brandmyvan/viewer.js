import * as THREE from 'three';
import { OrbitControls } from 'https://cdn.jsdelivr.net/gh/Kesskessx/can-i-share-this@brandmyvan-real-glb/brandmyvan/vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/gh/Kesskessx/can-i-share-this@brandmyvan-real-glb/brandmyvan/vendor/examples/jsm/loaders/GLTFLoader.js';

const stage=document.querySelector('#van');
const status=document.querySelector('#status');
const grid=document.querySelector('#grid');

const spots=[
 {id:1,name:'Driver door',price:420,point:[24,24,22],normal:[1,0,0],size:[18,11],tier:'PREMIUM'},
 {id:2,name:'Passenger door',price:420,point:[-24,24,22],normal:[-1,0,0],size:[18,11],tier:'PREMIUM'},
 {id:3,name:'Left premium panel',price:650,point:[23.5,38,-28],normal:[1,0,0],size:[30,16],tier:'PREMIUM'},
 {id:4,name:'Right premium panel',price:650,point:[-23.5,38,-28],normal:[-1,0,0],size:[30,16],tier:'PREMIUM'},
 {id:5,name:'Rear left premium',price:350,point:[12,34,-72.5],normal:[0,0,-1],size:[13,12],tier:'PREMIUM'},
 {id:6,name:'Rear right premium',price:350,point:[-12,34,-72.5],normal:[0,0,-1],size:[13,12],tier:'PREMIUM'},
 {id:7,name:'Hood premium',price:800,point:[0,26,53],normal:[0,.62,.78],size:[23,12],tier:'PREMIUM'},
 {id:8,name:'Roof premium',price:900,point:[0,60.8,-23],normal:[0,1,0],size:[26,13],tier:'PREMIUM'},
];

const sideZ=[8,-8,-48,-62];
for(let r=0;r<2;r++) for(let c=0;c<4;c++){
  const id=9+r*4+c;
  spots.push({id,name:`Left grid ${String.fromCharCode(65+r)}${c+1}`,price:50,point:[24.05,r?47:26,sideZ[c]],normal:[1,0,0],size:[11,7.2],tier:'SMALL'});
}
for(let r=0;r<2;r++) for(let c=0;c<4;c++){
  const id=17+r*4+c;
  spots.push({id,name:`Right grid ${String.fromCharCode(65+r)}${c+1}`,price:50,point:[-24.05,r?47:26,sideZ[c]],normal:[-1,0,0],size:[11,7.2],tier:'SMALL'});
}
[
 {id:25,name:'Rear grid A1',point:[8,47,-72.4]},
 {id:26,name:'Rear grid A2',point:[-8,47,-72.4]},
 {id:27,name:'Rear grid B1',point:[8,22,-72.4]},
 {id:28,name:'Rear grid B2',point:[-8,22,-72.4]},
].forEach(s=>spots.push({...s,price:50,normal:[0,0,-1],size:[8.5,6.5],tier:'SMALL'}));
[
 {id:29,name:'Roof grid A1',point:[9,60.85,7]},
 {id:30,name:'Roof grid A2',point:[-9,60.85,7]},
 {id:31,name:'Roof grid B1',point:[9,60.85,-48]},
 {id:32,name:'Roof grid B2',point:[-9,60.85,-48]},
].forEach(s=>spots.push({...s,price:75,normal:[0,1,0],size:[10,7],tier:'SMALL'}));

let sceneRef=null, scaleRef=1, originRef=null, focusSpot=()=>{}, selectedIndex=0;
const zoneMeshes=new Map(), zoneState=new Map();

function euro(n){return `€${Math.round(Number(n)||0)}`}

function cardFor(s){
  const el=document.createElement('button');
  el.type='button';el.className='card';el.dataset.spotId=s.id;
  el.innerHTML=`<span class="num">${String(s.id).padStart(2,'0')} · ${s.tier}</span><b>${s.name}</b><strong>${euro(s.price)}</strong>`;
  el.addEventListener('click',()=>selectSpot(s.id-1));
  grid?.append(el);s.card=el;
}
spots.forEach(cardFor);

function selectSpot(i,focus=true){
  selectedIndex=i;
  spots.forEach((s,j)=>s.card?.classList.toggle('active',i===j));
  const s=spots[i];
  document.querySelector('#selname').textContent=`${String(s.id).padStart(2,'0')} — ${s.name}`;
  document.querySelector('#selprice').textContent=`From ${euro(s.price)}`;
  zoneMeshes.forEach((m,id)=>{m.material.opacity=id===s.id?1:(zoneState.get(id)?.logoUrl?1:.78)});
  if(focus)focusSpot(s);
}
selectSpot(0,false);

function canvasBase(s){
  const c=document.createElement('canvas');c.width=512;c.height=320;
  const x=c.getContext('2d');
  x.fillStyle=s.tier==='PREMIUM'?'rgba(220,255,41,.82)':'rgba(220,255,41,.62)';
  x.fillRect(4,4,504,312);
  x.strokeStyle='#111';x.lineWidth=12;x.strokeRect(7,7,498,306);
  x.fillStyle='#111';x.textAlign='center';
  x.font='900 68px Arial';x.fillText(String(s.id).padStart(2,'0'),256,135);
  x.font='900 34px Arial';x.fillText(s.tier,256,188);
  x.font='700 32px Arial';x.fillText(`FROM ${euro(s.price)}`,256,245);
  return c;
}
function texFromCanvas(c){
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;return t;
}
function emptyTexture(s){return texFromCanvas(canvasBase(s))}
function loadImage(url){
  return new Promise((resolve,reject)=>{
    const img=new Image();img.crossOrigin='anonymous';img.onload=()=>resolve(img);img.onerror=reject;img.src=url;
  });
}
async function logoTexture(s,url){
  const c=document.createElement('canvas');c.width=512;c.height=320;
  const x=c.getContext('2d');
  x.fillStyle='#fff';x.fillRect(4,4,504,312);
  x.strokeStyle='#111';x.lineWidth=12;x.strokeRect(7,7,498,306);
  const img=await loadImage(url);
  const pad=24, W=512-pad*2,H=320-pad*2;
  const k=Math.min(W/img.width,H/img.height);
  const w=img.width*k,h=img.height*k;
  x.drawImage(img,(512-w)/2,(320-h)/2,w,h);
  return texFromCanvas(c);
}
function orient(mesh,s){
  const n=new THREE.Vector3(...s.normal).normalize();
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),n);
}
function worldPos(s,offset=.08){
  const n=new THREE.Vector3(...s.normal).normalize();
  return new THREE.Vector3(...s.point).sub(originRef).multiplyScalar(scaleRef).addScaledVector(n,offset*scaleRef);
}
function makeZone(s){
  const g=new THREE.PlaneGeometry(s.size[0]*scaleRef,s.size[1]*scaleRef);
  const m=new THREE.MeshBasicMaterial({
    map:emptyTexture(s),transparent:true,opacity:.78,depthWrite:false,
    polygonOffset:true,polygonOffsetFactor:-5,side:THREE.DoubleSide
  });
  const mesh=new THREE.Mesh(g,m);
  mesh.position.copy(worldPos(s));
  orient(mesh,s);mesh.renderOrder=30;mesh.userData={spotId:s.id,spotIndex:s.id-1};
  sceneRef.add(mesh);zoneMeshes.set(s.id,mesh);
}
async function applyLogo(s,url){
  const mesh=zoneMeshes.get(s.id);if(!mesh||!url)return;
  const prev=zoneState.get(s.id);
  if(prev?.logoUrl===url)return;
  try{
    const t=await logoTexture(s,url);
    if(mesh.material.map)mesh.material.map.dispose();
    mesh.material.map=t;mesh.material.opacity=1;mesh.material.needsUpdate=true;
    zoneState.set(s.id,{logoUrl:url});
  }catch(e){console.warn('logo texture failed',s.id,e)}
}
function clearLogo(s){
  const mesh=zoneMeshes.get(s.id);if(!mesh)return;
  if(mesh.material.map)mesh.material.map.dispose();
  mesh.material.map=emptyTexture(s);mesh.material.opacity=s.id===spots[selectedIndex].id?1:.78;
  mesh.material.needsUpdate=true;zoneState.delete(s.id);
}
function syncAuction(state){
  const byId=new Map((state?.spots||[]).map(x=>[Number(x.id),x]));
  for(const s of spots){
    const live=byId.get(s.id);
    if(live?.start_price!=null)s.price=Number(live.start_price);
    if(live?.winner_logo_url)applyLogo(s,live.winner_logo_url);
    else if(zoneState.has(s.id))clearLogo(s);
  }
}
window.addEventListener('brandmyvan:auction',e=>syncAuction(e.detail));
if(window.__BMV_AUCTION_STATE)syncAuction(window.__BMV_AUCTION_STATE);

try{
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.setClearColor(0xfaf9f5,1);
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.28;
  stage.append(renderer.domElement);

  const scene=new THREE.Scene();sceneRef=scene;
  const camera=new THREE.PerspectiveCamera(36,1,.01,100);camera.position.set(4,2.6,5);
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.target.set(0,.9,0);controls.enableDamping=true;controls.enablePan=false;
  controls.minDistance=3.5;controls.maxDistance=10;controls.maxPolarAngle=Math.PI/2-.02;controls.autoRotateSpeed=.65;
  scene.add(new THREE.HemisphereLight(0xffffff,0xb5b0a3,3));
  for(const [p,intensity] of [[[3,6,5],3],[[-4,3,-3],1.5]]){const l=new THREE.DirectionalLight(0xffffff,intensity);l.position.set(...p);scene.add(l)}

  let desiredPosition=null;
  const resize=()=>{const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()};
  new ResizeObserver(resize).observe(stage);resize();
  const stopAuto=()=>{controls.autoRotate=false;document.querySelector('#rotate')?.setAttribute('aria-pressed','false')};
  controls.addEventListener('start',()=>{desiredPosition=null;stopAuto()});
  document.querySelector('#rotate')?.addEventListener('click',()=>{desiredPosition=null;controls.autoRotate=!controls.autoRotate;document.querySelector('#rotate').setAttribute('aria-pressed',String(controls.autoRotate))});
  document.querySelector('#reset')?.addEventListener('click',()=>{stopAuto();desiredPosition=new THREE.Vector3(4,2.6,5)});

  const gltf=await new GLTFLoader().loadAsync(
    'https://cdn.jsdelivr.net/gh/Kesskessx/can-i-share-this@brandmyvan-real-glb/brandmyvan/van-realistic.glb',
    e=>{if(e.total)status.textContent=`LOADING THE VAN · ${Math.round(e.loaded/e.total*100)}%`}
  );
  const box=new THREE.Box3().setFromObject(gltf.scene),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
  const scale=4/Math.max(size.x,size.y,size.z),origin=new THREE.Vector3(center.x,box.min.y,center.z);
  scaleRef=scale;originRef=origin;
  gltf.scene.scale.setScalar(scale);gltf.scene.position.copy(origin).multiplyScalar(-scale);scene.add(gltf.scene);

  spots.forEach(s=>makeZone(s));
  if(window.__BMV_AUCTION_STATE)syncAuction(window.__BMV_AUCTION_STATE);

  focusSpot=s=>{
    stopAuto();
    const dir=new THREE.Vector3(...s.normal).normalize();
    if(dir.y>.5)dir.set(.5,1,s.id===7?1:-.2);else dir.y=.34;
    desiredPosition=controls.target.clone().add(dir.normalize().multiplyScalar(6));
  };

  status.textContent='REAL 3D VAN · 32 LIVE SPONSOR SLOTS · TAP A ZONE';

  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
  let downX=0,downY=0;
  renderer.domElement.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY});
  renderer.domElement.addEventListener('pointerup',e=>{
    if(Math.hypot(e.clientX-downX,e.clientY-downY)>7)return;
    const r=renderer.domElement.getBoundingClientRect();
    pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1;
    raycaster.setFromCamera(pointer,camera);
    const hit=raycaster.intersectObjects([...zoneMeshes.values()],false)[0];
    if(hit)selectSpot(hit.object.userData.spotIndex);
  });

  renderer.setAnimationLoop(()=>{
    if(desiredPosition){camera.position.lerp(desiredPosition,.085);if(camera.position.distanceTo(desiredPosition)<.01)desiredPosition=null}
    controls.update();renderer.render(scene,camera);
  });
}catch(error){
  console.error(error);
  status.textContent='THE 3D VAN COULD NOT LOAD · RETRY';
}
