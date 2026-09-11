import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const canvas = document.getElementById('vanCanvas');
const zoneLayer = document.getElementById('zoneLayer');
const viewLabel = document.getElementById('viewLabel');
const freeMessage = document.getElementById('freeMessage');
const resetBtn = document.getElementById('resetVan');
const viewButtons = [...document.querySelectorAll('[data-view]')];
const panel = document.getElementById('spotPanel');
const panelTier = document.getElementById('spotPanelTier');
const panelName = document.getElementById('spotPanelName');
const panelPrice = document.getElementById('spotPanelPrice');
const panelCopy = document.getElementById('spotPanelCopy');
const panelClaim = document.getElementById('spotPanelClaim');
const panelClose = document.getElementById('spotPanelClose');

const SPOTS = [
  {id:'S1',view:'left',tier:'Signature',price:1500,x:40,y:43,w:27,h:24,copy:'Main left cargo-panel placement. Large, flat and highly visible.'},
  {id:'L1',view:'left',tier:'Large',price:750,x:21,y:56,w:17,h:16,copy:'Front-door body placement below the glass line.'},
  {id:'L2',view:'left',tier:'Large',price:750,x:70,y:47,w:20,h:21,copy:'Large rear cargo-panel placement above the wheel area.'},
  {id:'M1',view:'left',tier:'Medium',price:400,x:40,y:32,w:11,h:9,copy:'Upper-left cargo-panel placement.'},
  {id:'M2',view:'left',tier:'Medium',price:400,x:53,y:32,w:11,h:9,copy:'Upper-right cargo-panel placement.'},
  {id:'SM1',view:'left',tier:'Small',price:200,x:43,y:68,w:11,h:7,copy:'Compact lower-left cargo-panel placement.'},
  {id:'SM2',view:'left',tier:'Small',price:200,x:56,y:68,w:11,h:7,copy:'Compact lower-right cargo-panel placement.'},

  {id:'S2',view:'right',tier:'Signature',price:1500,x:37,y:43,w:27,h:24,copy:'Main right cargo-panel placement. Large, flat and highly visible.'},
  {id:'L3',view:'right',tier:'Large',price:750,x:15,y:47,w:20,h:21,copy:'Large rear cargo-panel placement above the wheel area.'},
  {id:'L4',view:'right',tier:'Large',price:750,x:67,y:56,w:17,h:16,copy:'Front-door body placement below the glass line.'},
  {id:'M3',view:'right',tier:'Medium',price:400,x:37,y:32,w:11,h:9,copy:'Upper-left cargo-panel placement.'},
  {id:'M4',view:'right',tier:'Medium',price:400,x:50,y:32,w:11,h:9,copy:'Upper-right cargo-panel placement.'},
  {id:'SM3',view:'right',tier:'Small',price:200,x:40,y:68,w:11,h:7,copy:'Compact lower-left cargo-panel placement.'},
  {id:'SM4',view:'right',tier:'Small',price:200,x:53,y:68,w:11,h:7,copy:'Compact lower-right cargo-panel placement.'},

  {id:'M5',view:'rear',tier:'Medium',price:400,u:.395,v:.785,uw:.105,vh:.095,copy:'Upper-left rear-door sticker.'},
  {id:'M6',view:'rear',tier:'Medium',price:400,u:.605,v:.785,uw:.105,vh:.095,copy:'Upper-right rear-door sticker.'},
  {id:'SM5',view:'rear',tier:'Small',price:200,u:.315,v:.665,uw:.070,vh:.065,copy:'Lower-left rear-door sticker.'},
  {id:'SM6',view:'rear',tier:'Small',price:200,u:.435,v:.665,uw:.070,vh:.065,copy:'Lower-left-center rear-door sticker.'},
  {id:'SM7',view:'rear',tier:'Small',price:200,u:.565,v:.665,uw:.070,vh:.065,copy:'Lower-right-center rear-door sticker.'},
  {id:'SM8',view:'rear',tier:'Small',price:200,u:.685,v:.665,uw:.070,vh:.065,copy:'Lower-right rear-door sticker.'}
];

const renderer = new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1,2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#f7f6f1');
const camera = new THREE.PerspectiveCamera(30,1,0.01,100);
const controls = new OrbitControls(camera,canvas);
controls.enableDamping = true;
controls.enablePan = false;
controls.autoRotate = false;
controls.minPolarAngle = Math.PI*.18;
controls.maxPolarAngle = Math.PI*.82;

scene.add(new THREE.HemisphereLight(0xffffff,0xb8b0a2,3.2));
const key = new THREE.DirectionalLight(0xffffff,3.3); key.position.set(5,7,5); scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff,1.4); fill.position.set(-5,3,-4); scene.add(fill);
const floor = new THREE.Mesh(new THREE.CircleGeometry(4.2,72),new THREE.MeshStandardMaterial({color:0xebe7dc,roughness:1,metalness:0}));
floor.rotation.x=-Math.PI/2; floor.position.y=-.02; scene.add(floor);

let model=null, modelBox=null, currentView='left', selectedId=null, tween=null;
let longAxis='x', wideAxis='z', rearSurfaceGroup=null, rearStickerMeshes=[];
let rearOut = new THREE.Vector3(-1,0,0);
const modelRaycaster = new THREE.Raycaster();
const clickRaycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function money(v){return `€${v.toLocaleString('en-US')}`}
function axisVector(axis,value=1){const v=new THREE.Vector3();v[axis]=value;return v}

function resize(){
  const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),r=renderer.getPixelRatio();
  if(canvas.width!==Math.round(w*r)||canvas.height!==Math.round(h*r)) renderer.setSize(w,h,false);
  camera.aspect=w/h; camera.updateProjectionMatrix();
}

function fitDistance(view){
  if(!modelBox) return 6;
  resize();
  const size=modelBox.getSize(new THREE.Vector3());
  const width=view==='rear'?size[wideAxis]:size[longAxis];
  const fov=THREE.MathUtils.degToRad(camera.fov);
  const byHeight=(size.y*.5)/Math.tan(fov*.5);
  const byWidth=(width*.5)/(Math.tan(fov*.5)*Math.max(camera.aspect,.4));
  return Math.max(byHeight,byWidth)*(view==='rear'?1.28:1.24);
}

function cameraPose(view){
  const center=modelBox.getCenter(new THREE.Vector3());
  const size=modelBox.getSize(new THREE.Vector3());
  const d=fitDistance(view);
  const pos=center.clone(), target=center.clone();
  target.y+=size.y*.02;
  if(view==='left') pos[wideAxis]+=d;
  if(view==='right') pos[wideAxis]-=d;
  if(view==='rear') pos[longAxis]-=d;
  pos.y+=size.y*.03;
  return {pos,target};
}

function animateCamera(pos,target,duration=420){
  tween={startPos:camera.position.clone(),startTarget:controls.target.clone(),pos,target,started:performance.now(),duration};
}
function updateTween(){
  if(!tween)return;
  const t=Math.min(1,(performance.now()-tween.started)/tween.duration),e=1-Math.pow(1-t,3);
  camera.position.lerpVectors(tween.startPos,tween.pos,e);
  controls.target.lerpVectors(tween.startTarget,tween.target,e);
  if(t>=1)tween=null;
}

function setFixedView(view,instant=false){
  if(!modelBox)return;
  currentView=view;
  controls.enableRotate=false;controls.enableZoom=false;controls.enablePan=false;controls.autoRotate=false;
  freeMessage.style.display='none';
  zoneLayer.style.display=view==='rear'?'none':'block';
  if(rearSurfaceGroup) rearSurfaceGroup.visible=view==='rear';
  const pose=cameraPose(view);
  if(instant){camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update()}else animateCamera(pose.pos,pose.target);
  renderZones(view);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  const count=SPOTS.filter(s=>s.view===view).length;
  viewLabel.textContent=view==='rear'?`REAR DOOR SURFACE · ${count} GLB STICKER SPOTS`:`${view.toUpperCase()} SIDE · ${count} AVAILABLE ZONES`;
  viewLabel.style.display='block';
  closePanel();
}

function setFreeView(){
  currentView='free';zoneLayer.innerHTML='';zoneLayer.style.display='none';
  if(rearSurfaceGroup)rearSurfaceGroup.visible=false;
  viewLabel.style.display='none';freeMessage.style.display='block';
  controls.enableRotate=true;controls.enableZoom=true;controls.enablePan=false;
  const c=modelBox.getCenter(new THREE.Vector3()),d=fitDistance('left')*1.05,p=c.clone();
  p[wideAxis]+=d*.72;p[longAxis]+=d*.72;p.y+=modelBox.getSize(new THREE.Vector3()).y*.18;
  animateCamera(p,c,450);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view==='free'));
  closePanel();
}

function renderZones(view){
  zoneLayer.innerHTML='';
  if(view==='rear')return;
  SPOTS.filter(s=>s.view===view).forEach(spot=>{
    const el=document.createElement('button');el.type='button';el.className=`zone ${spot.tier.toLowerCase()}`;
    el.style.left=`${spot.x}%`;el.style.top=`${spot.y}%`;el.style.width=`${spot.w}%`;el.style.height=`${spot.h}%`;
    el.innerHTML=`<span class="zone-badge"><b>${spot.id}</b></span><span class="zone-price">${money(spot.price)}</span>`;
    el.addEventListener('click',()=>selectSpot(spot,el));zoneLayer.appendChild(el);
  });
}

function selectSpot(spot,el=null){
  selectedId=spot.id;
  [...zoneLayer.querySelectorAll('.zone')].forEach(z=>z.classList.remove('selected'));if(el)el.classList.add('selected');
  rearStickerMeshes.forEach(m=>m.material.color.set(m.userData.spot?.id===spot.id?0xdcff29:0xffffff));
  panelTier.textContent=`${spot.tier} · ${spot.view.toUpperCase()} · ${spot.id}`;
  panelName.textContent=spot.view==='rear'?`Rear sticker ${spot.id}`:`Sponsor zone ${spot.id}`;
  panelPrice.textContent=money(spot.price);
  panelCopy.textContent=spot.view==='rear'?`${spot.copy} The decal is generated from the GLB triangles and follows the local rear-door curvature.`:`${spot.copy} This exact rectangle becomes the physical location for your logo for 12 months.`;
  panelClaim.textContent=`Reserve ${spot.id} — ${money(spot.price)}`;
  panelClaim.href=`https://x.com/THEFOFOSHOW?brandmyvan=${encodeURIComponent(spot.id)}`;panel.hidden=false;
}
function closePanel(){
  selectedId=null;panel.hidden=true;[...zoneLayer.querySelectorAll('.zone')].forEach(z=>z.classList.remove('selected'));
  rearStickerMeshes.forEach(m=>m.material.color.set(0xffffff));
}

panelClose?.addEventListener('click',closePanel);
viewButtons.forEach(btn=>btn.addEventListener('click',()=>btn.dataset.view==='free'?setFreeView():setFixedView(btn.dataset.view)));
resetBtn?.addEventListener('click',()=>currentView==='free'?setFreeView():setFixedView(currentView));
window.addEventListener('resize',()=>{if(modelBox&&currentView!=='free')setFixedView(currentView,true)});

function rearSample(u,v,{strict=true}={}){
  if(!model||!modelBox)return null;
  const size=modelBox.getSize(new THREE.Vector3());
  const origin=modelBox.getCenter(new THREE.Vector3());
  origin[wideAxis]=modelBox.min[wideAxis]+u*size[wideAxis];
  origin.y=modelBox.min.y+v*size.y;
  origin[longAxis]=modelBox.min[longAxis]-Math.max(.45,size[longAxis]*.12);
  const dir=axisVector(longAxis,1);
  modelRaycaster.set(origin,dir);modelRaycaster.far=size[longAxis]*1.45;
  const hits=modelRaycaster.intersectObject(model,true);
  if(!hits.length)return null;
  for(const hit of hits){
    if(!hit.face)continue;
    const n=hit.face.normal.clone().applyMatrix3(new THREE.Matrix3().getNormalMatrix(hit.object.matrixWorld)).normalize();
    const facing=n.dot(rearOut);
    if(strict&&facing<.62)continue;
    const p=hit.point.clone().addScaledVector(n,.006);
    return {point:p,normal:n,object:hit.object,distance:hit.distance};
  }
  return null;
}

function createSurfacePatch({u0,u1,v0,v1,nx,ny,material,autoMask=false,offset=.006}){
  const samples=[];
  for(let y=0;y<=ny;y++){
    samples[y]=[];
    for(let x=0;x<=nx;x++){
      const u=u0+(u1-u0)*(x/nx),v=v0+(v1-v0)*(y/ny);
      samples[y][x]=rearSample(u,v,{strict:autoMask});
    }
  }
  if(autoMask){
    const original=samples.map(r=>r.map(Boolean));
    for(let y=1;y<ny;y++)for(let x=1;x<nx;x++){
      if(!original[y][x]){samples[y][x]=null;continue}
      let keep=true;
      for(let yy=-1;yy<=1;yy++)for(let xx=-1;xx<=1;xx++)if(!original[y+yy]?.[x+xx])keep=false;
      if(!keep)samples[y][x]=null;
    }
  }
  const verts=[],uvs=[],grid=[];
  for(let y=0;y<=ny;y++){
    grid[y]=[];
    for(let x=0;x<=nx;x++){
      const s=samples[y][x];
      if(!s){grid[y][x]=-1;continue}
      const p=s.point.clone().addScaledVector(s.normal,offset);
      grid[y][x]=verts.length/3;verts.push(p.x,p.y,p.z);uvs.push(x/nx,y/ny);
    }
  }
  const tangent=axisVector(wideAxis,1),up=new THREE.Vector3(0,1,0),basis=tangent.clone().cross(up);
  const front=basis.dot(rearOut)>0;
  const idx=[];
  for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
    const a=grid[y][x],b=grid[y][x+1],c=grid[y+1][x],d=grid[y+1][x+1];
    if(a>=0&&b>=0&&c>=0) idx.push(...(front?[a,b,c]:[a,c,b]));
    if(b>=0&&d>=0&&c>=0) idx.push(...(front?[b,d,c]:[b,c,d]));
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));g.setIndex(idx);g.computeVertexNormals();
  const mesh=new THREE.Mesh(g,material);mesh.renderOrder=20;return mesh;
}

function makeStickerTexture(spot){
  const c=document.createElement('canvas');c.width=512;c.height=512;const ctx=c.getContext('2d');
  ctx.fillStyle='rgba(255,255,255,.98)';ctx.fillRect(18,18,476,476);ctx.strokeStyle='#111';ctx.lineWidth=18;ctx.strokeRect(18,18,476,476);
  ctx.fillStyle='#111';ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='900 126px Arial';ctx.fillText(spot.id,256,215);ctx.font='900 56px Arial';ctx.fillText(money(spot.price),256,334);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;return t;
}

function buildRearSurface(){
  if(!model||!modelBox)return;
  if(rearSurfaceGroup){scene.remove(rearSurfaceGroup);rearSurfaceGroup.traverse(o=>{o.geometry?.dispose();o.material?.dispose?.()})}
  rearSurfaceGroup=new THREE.Group();rearSurfaceGroup.name='rear-sponsor-surface';scene.add(rearSurfaceGroup);

  const redMat=new THREE.MeshBasicMaterial({color:0xf1282d,transparent:true,opacity:.27,depthWrite:false,side:THREE.DoubleSide});
  const field=createSurfacePatch({u0:.22,u1:.78,v0:.61,v1:.90,nx:92,ny:54,material:redMat,autoMask:true,offset:.004});
  field.name='rear-precise-body-mask';rearSurfaceGroup.add(field);

  rearStickerMeshes=[];
  for(const spot of SPOTS.filter(s=>s.view==='rear')){
    const mat=new THREE.MeshBasicMaterial({map:makeStickerTexture(spot),color:0xffffff,transparent:true,opacity:.99,depthWrite:false,side:THREE.DoubleSide});
    const decal=createSurfacePatch({u0:spot.u-spot.uw/2,u1:spot.u+spot.uw/2,v0:spot.v-spot.vh/2,v1:spot.v+spot.vh/2,nx:18,ny:14,material:mat,autoMask:true,offset:.011});
    decal.name=`rear-sticker-${spot.id}`;decal.userData.spot=spot;decal.renderOrder=30;rearStickerMeshes.push(decal);rearSurfaceGroup.add(decal);
  }
  rearSurfaceGroup.visible=currentView==='rear';
}

function setPointer(e){const r=canvas.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1}
canvas.addEventListener('pointermove',e=>{if(currentView!=='rear'){canvas.style.cursor='';return}setPointer(e);clickRaycaster.setFromCamera(pointer,camera);canvas.style.cursor=clickRaycaster.intersectObjects(rearStickerMeshes,false).length?'pointer':''});
canvas.addEventListener('click',e=>{if(currentView!=='rear')return;setPointer(e);clickRaycaster.setFromCamera(pointer,camera);const h=clickRaycaster.intersectObjects(rearStickerMeshes,false);if(h.length)selectSpot(h[0].object.userData.spot)});

renderer.setAnimationLoop(()=>{resize();updateTween();controls.update();renderer.render(scene,camera)});

async function boot(){
  try{
    const gltf=await new GLTFLoader().loadAsync('./van-realistic.glb');model=gltf.scene;
    const rawBox=new THREE.Box3().setFromObject(model),rawSize=rawBox.getSize(new THREE.Vector3()),rawCenter=rawBox.getCenter(new THREE.Vector3());
    const scale=4.75/Math.max(rawSize.x,rawSize.y,rawSize.z),origin=new THREE.Vector3(rawCenter.x,rawBox.min.y,rawCenter.z);
    model.scale.setScalar(scale);model.position.copy(origin).multiplyScalar(-scale);scene.add(model);scene.updateMatrixWorld(true);
    modelBox=new THREE.Box3().setFromObject(model);const size=modelBox.getSize(new THREE.Vector3());longAxis=size.x>=size.z?'x':'z';wideAxis=longAxis==='x'?'z':'x';rearOut=axisVector(longAxis,-1);
    buildRearSurface();setFixedView('left',true);
  }catch(err){console.error(err);viewLabel.textContent='3D MODEL UNAVAILABLE';zoneLayer.style.display='none'}
}
boot();