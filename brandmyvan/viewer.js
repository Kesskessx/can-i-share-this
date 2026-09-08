import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const stage=document.querySelector('#van');
const status=document.querySelector('#status');
const spots=[
 {name:'Driver door',price:420,point:[24,24,22],normal:[1,0,0],size:[18,11]},
 {name:'Passenger door',price:420,point:[-24,24,22],normal:[-1,0,0],size:[18,11]},
 {name:'Left panel',price:650,point:[23.8,37,-29],normal:[1,0,0],size:[34,18]},
 {name:'Right panel',price:650,point:[-23.8,37,-29],normal:[-1,0,0],size:[34,18]},
 {name:'Rear left',price:350,point:[12,34,-72.25],normal:[0,0,-1],size:[14,13]},
 {name:'Rear right',price:350,point:[-12,34,-72.25],normal:[0,0,-1],size:[14,13]},
 {name:'Hood',price:800,point:[0,25.8,53],normal:[0,.62,.78],size:[25,13]},
 {name:'Roof',price:900,point:[0,60.72,-18],normal:[0,1,0],size:[28,16]},
];

let focusSpot=()=>{},sceneRef=null,scaleRef=1,originRef=null,cameraRef=null,rendererRef=null;
const zoneMeshes=new Map();
const zoneGroups=new Map();
let selectedIndex=0;

function selectSpot(i,focus=true){
  selectedIndex=i;
  spots.forEach((s,j)=>{
    s.card?.classList.toggle('active',i===j);
    s.card?.setAttribute('aria-pressed',String(i===j));
    const g=zoneGroups.get(j+1);
    if(g?.userData?.border?.material) g.userData.border.material.color.set(i===j?0x111111:0x353535);
  });
  document.querySelector('#selname').textContent=`${String(i+1).padStart(2,'0')} — ${spots[i].name}`;
  document.querySelector('#selprice').textContent=`From €${spots[i].price}`;
  if(focus)focusSpot(spots[i]);
}

spots.forEach((s,i)=>{
  s.card=document.createElement('button');s.card.type='button';s.card.className='card';
  s.card.innerHTML=`<span class="num">${String(i+1).padStart(2,'0')}</span><b>${s.name}</b><strong>€${s.price}</strong>`;
  s.card.addEventListener('click',()=>selectSpot(i));document.querySelector('#grid').append(s.card);
  // Legacy HTML pins stay hidden: the 3D rectangles are now the visual/click target.
  s.pin=document.createElement('button');s.pin.type='button';s.pin.className='pin';s.pin.hidden=true;
  document.querySelector('#hotspots')?.append(s.pin);
});
selectSpot(0,false);

function placeholderTexture(spot,index){
  const ratio=Math.max(.5,Math.min(4,spot.size[0]/spot.size[1]));
  const w=768,h=Math.round(w/ratio);
  const c=document.createElement('canvas');c.width=w;c.height=h;
  const x=c.getContext('2d');
  x.clearRect(0,0,w,h);
  x.fillStyle='rgba(220,255,41,.42)';x.fillRect(2,2,w-4,h-4);
  x.strokeStyle='#111';x.lineWidth=Math.max(5,w/150);x.strokeRect(4,4,w-8,h-8);
  x.fillStyle='#111';x.textAlign='center';x.textBaseline='middle';
  x.font=`900 ${Math.round(h*.25)}px Arial`;
  x.fillText(`SPOT ${String(index).padStart(2,'0')}`,w/2,h*.42);
  x.font=`900 ${Math.round(h*.16)}px Arial`;
  x.fillText(`FROM €${spot.price}`,w/2,h*.69);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;return t;
}

async function logoTexture(url,spot){
  const response=await fetch(url,{mode:'cors',cache:'no-store'});
  if(!response.ok)throw new Error(`Logo HTTP ${response.status}`);
  const blob=await response.blob();
  const bmp=await createImageBitmap(blob);
  const ratio=Math.max(.5,Math.min(4,spot.size[0]/spot.size[1]));
  const w=1024,h=Math.round(w/ratio);
  const c=document.createElement('canvas');c.width=w;c.height=h;
  const x=c.getContext('2d');
  x.fillStyle='#fff';x.fillRect(0,0,w,h);
  const pad=Math.round(Math.min(w,h)*.055);
  const availW=w-pad*2,availH=h-pad*2;
  const k=Math.min(availW/bmp.width,availH/bmp.height);
  const dw=bmp.width*k,dh=bmp.height*k;
  x.drawImage(bmp,(w-dw)/2,(h-dh)/2,dw,dh);
  bmp.close?.();
  // permanent thin boundary so visitors always understand the purchased area
  x.strokeStyle='#111';x.lineWidth=Math.max(5,w/180);x.strokeRect(3,3,w-6,h-6);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;t.needsUpdate=true;return t;
}

function createZone(id){
  if(!sceneRef||!originRef)return;
  const spot=spots[id-1];
  const n=new THREE.Vector3(...spot.normal).normalize();
  const pos=new THREE.Vector3(...spot.point).sub(originRef).multiplyScalar(scaleRef);
  // only a hair above the body to prevent z-fighting, not a floating billboard
  pos.addScaledVector(n,.055*scaleRef);

  const group=new THREE.Group();group.position.copy(pos);
  group.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),n);
  group.userData.spotId=id;

  const geometry=new THREE.PlaneGeometry(spot.size[0]*scaleRef,spot.size[1]*scaleRef);
  const mat=new THREE.MeshBasicMaterial({map:placeholderTexture(spot,id),transparent:true,depthWrite:false,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2});
  const mesh=new THREE.Mesh(geometry,mat);mesh.renderOrder=15;mesh.userData.spotId=id;
  group.add(mesh);

  const edges=new THREE.EdgesGeometry(geometry);
  const lineMat=new THREE.LineBasicMaterial({color:0x353535,transparent:true,opacity:.95,depthTest:true});
  const border=new THREE.LineSegments(edges,lineMat);border.position.z=.001;border.renderOrder=16;group.add(border);
  group.userData.border=border;

  sceneRef.add(group);zoneGroups.set(id,group);zoneMeshes.set(id,mesh);
}

async function setZoneLogo(id,logoUrl,company='Sponsor'){
  const mesh=zoneMeshes.get(Number(id));const spot=spots[Number(id)-1];
  if(!mesh||!spot)return;
  if(mesh.userData.logoUrl===logoUrl)return;
  const old=mesh.material.map;
  try{
    const tex=logoUrl?await logoTexture(logoUrl,spot):placeholderTexture(spot,Number(id));
    mesh.material.map=tex;mesh.material.transparent=true;mesh.material.needsUpdate=true;
    mesh.userData.logoUrl=logoUrl||'';mesh.userData.company=company;
    if(old&&old!==tex)old.dispose?.();
  }catch(e){console.warn('Sponsor zone texture failed',id,e)}
}

function syncSponsorZones(state){
  const byId=new Map((state?.spots||[]).map(s=>[Number(s.id),s]));
  for(let id=1;id<=8;id++){
    const s=byId.get(id);
    setZoneLogo(id,s?.winner_logo_url||'',s?.winner_company||'Sponsor');
  }
}
window.addEventListener('brandmyvan:auction',e=>syncSponsorZones(e.detail));

try{
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});rendererRef=renderer;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));renderer.setClearColor(0xfaf9f5,1);renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;stage.append(renderer.domElement);
  const scene=new THREE.Scene();sceneRef=scene;
  const camera=new THREE.PerspectiveCamera(36,1,.01,100);cameraRef=camera;camera.position.set(4,2.6,5);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,.9,0);controls.enableDamping=true;controls.enablePan=false;
  controls.minDistance=3.5;controls.maxDistance=10;controls.maxPolarAngle=Math.PI/2-.025;controls.autoRotateSpeed=.7;
  scene.add(new THREE.HemisphereLight(0xffffff,0xb5b0a3,3));
  for(const [position,intensity] of [[[3,6,5],3],[[-4,3,-3],1.5]]){const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...position);scene.add(light);}

  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=128;shadowCanvas.height=128;
  const ctx=shadowCanvas.getContext('2d'),g=ctx.createRadialGradient(64,64,10,64,64,64);g.addColorStop(0,'rgba(0,0,0,.24)');g.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=g;ctx.fillRect(0,0,128,128);
  const shadow=new THREE.Mesh(new THREE.PlaneGeometry(2.8,5.4),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));shadow.rotation.x=-Math.PI/2;shadow.position.y=-.01;scene.add(shadow);

  let desiredPosition=null;
  const resize=()=>{const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();};new ResizeObserver(resize).observe(stage);resize();
  const stopAuto=()=>{controls.autoRotate=false;document.querySelector('#rotate')?.setAttribute('aria-pressed','false');};
  controls.addEventListener('start',()=>{desiredPosition=null;stopAuto();});
  document.querySelector('#rotate')?.addEventListener('click',()=>{desiredPosition=null;controls.autoRotate=!controls.autoRotate;document.querySelector('#rotate').setAttribute('aria-pressed',String(controls.autoRotate));});
  document.querySelector('#reset')?.addEventListener('click',()=>{stopAuto();desiredPosition=new THREE.Vector3(4,2.6,5);});
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();status.textContent='3D VIEW INTERRUPTED — RELOAD THE PAGE';});

  const gltf=await new GLTFLoader().loadAsync('https://raw.githubusercontent.com/Kesskessx/can-i-share-this/brandmyvan-real-glb/brandmyvan/van-realistic.glb',event=>{if(event.total)status.textContent=`LOADING THE VAN · ${Math.round(event.loaded/event.total*100)}%`;});
  const box=new THREE.Box3().setFromObject(gltf.scene),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
  const scale=4/Math.max(size.x,size.y,size.z),origin=new THREE.Vector3(center.x,box.min.y,center.z);scaleRef=scale;originRef=origin;
  gltf.scene.scale.setScalar(scale);gltf.scene.position.copy(origin).multiplyScalar(-scale);scene.add(gltf.scene);
  spots.forEach(s=>{s.world=new THREE.Vector3(...s.point).sub(origin).multiplyScalar(scale);s.direction=new THREE.Vector3(...s.normal).normalize();});
  for(let id=1;id<=8;id++)createZone(id);
  if(window.__BMV_AUCTION_STATE)syncSponsorZones(window.__BMV_AUCTION_STATE);

  focusSpot=s=>{stopAuto();const dir=s.direction.clone();if(dir.y>.5)dir.set(.45,1,s.name==='Hood'?1:-.15);else dir.y=.30;desiredPosition=controls.target.clone().add(dir.normalize().multiplyScalar(5.4));};
  stage.dataset.modelLoaded='true';status.textContent='REAL 3D VAN · CHOOSE A PREDEFINED SPONSOR ZONE';

  // Tap/click the actual 3D zone instead of a floating marker.
  const raycaster=new THREE.Raycaster(),mouse=new THREE.Vector2();let downX=0,downY=0;
  renderer.domElement.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;});
  renderer.domElement.addEventListener('pointerup',e=>{
    if(Math.hypot(e.clientX-downX,e.clientY-downY)>8)return;
    const rect=renderer.domElement.getBoundingClientRect();mouse.x=((e.clientX-rect.left)/rect.width)*2-1;mouse.y=-((e.clientY-rect.top)/rect.height)*2+1;
    raycaster.setFromCamera(mouse,camera);
    const hits=raycaster.intersectObjects([...zoneMeshes.values()],false);
    if(hits.length){const id=Number(hits[0].object.userData.spotId);if(id)selectSpot(id-1,false);}
  });

  renderer.setAnimationLoop(()=>{if(desiredPosition){camera.position.lerp(desiredPosition,.085);if(camera.position.distanceTo(desiredPosition)<.01)desiredPosition=null;}controls.update();renderer.render(scene,camera);});
}catch(error){
  console.error('Van viewer failed:',error);status.replaceChildren(document.createTextNode('THE 3D VAN COULD NOT LOAD. '));
  const retry=document.createElement('a');retry.href='';retry.className='status-link';retry.textContent='RETRY';status.append(retry);stage.dataset.modelLoaded='false';
}
