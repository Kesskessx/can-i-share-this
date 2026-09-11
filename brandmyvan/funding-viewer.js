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

  // Real 3D rear decals. u/v are normalized across the GLB rear body.
  {id:'M5',view:'rear',tier:'Medium',price:400,u:.405,v:.735,uw:.105,vh:.105,copy:'Upper-left rear-door sticker.'},
  {id:'M6',view:'rear',tier:'Medium',price:400,u:.595,v:.735,uw:.105,vh:.105,copy:'Upper-right rear-door sticker.'},
  {id:'SM5',view:'rear',tier:'Small',price:200,u:.34,v:.605,uw:.078,vh:.075,copy:'Left rear-door sticker.'},
  {id:'SM6',view:'rear',tier:'Small',price:200,u:.50,v:.605,uw:.078,vh:.075,copy:'Center rear-door sticker.'},
  {id:'SM7',view:'rear',tier:'Small',price:200,u:.66,v:.605,uw:.078,vh:.075,copy:'Right rear-door sticker.'},
  {id:'SM8',view:'rear',tier:'Small',price:200,u:.50,v:.505,uw:.078,vh:.075,copy:'Lower-center rear-door sticker.'}
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
controls.minPolarAngle = Math.PI * .18;
controls.maxPolarAngle = Math.PI * .82;

scene.add(new THREE.HemisphereLight(0xffffff,0xb8b0a2,3.2));
const key = new THREE.DirectionalLight(0xffffff,3.3); key.position.set(5,7,5); scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff,1.4); fill.position.set(-5,3,-4); scene.add(fill);
const floor = new THREE.Mesh(new THREE.CircleGeometry(4.2,72),new THREE.MeshStandardMaterial({color:0xebe7dc,roughness:1,metalness:0}));
floor.rotation.x=-Math.PI/2; floor.position.y=-.02; scene.add(floor);

let model = null;
let modelBox = null;
let longAxis = 'x';
let wideAxis = 'z';
let currentView = 'left';
let selectedId = null;
let tween = null;
let rearSurfaceGroup = null;
let rearStickerMeshes = [];
let rearReady = false;
const modelRaycaster = new THREE.Raycaster();
const clickRaycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function money(v){return `€${v.toLocaleString('en-US')}`}

function resize(){
  const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),r=renderer.getPixelRatio();
  if(canvas.width!==Math.round(w*r)||canvas.height!==Math.round(h*r)) renderer.setSize(w,h,false);
  camera.aspect=w/h; camera.updateProjectionMatrix();
}

function fitDistance(view){
  if(!modelBox) return 6;
  resize();
  const size=modelBox.getSize(new THREE.Vector3());
  const height=size.y;
  const width=view==='rear'?size[wideAxis]:size[longAxis];
  const fov=THREE.MathUtils.degToRad(camera.fov);
  const byHeight=(height*.5)/Math.tan(fov*.5);
  const byWidth=(width*.5)/(Math.tan(fov*.5)*Math.max(camera.aspect,.4));
  return Math.max(byHeight,byWidth)*(view==='rear'?1.32:1.24);
}

function cameraPose(view){
  const center=modelBox.getCenter(new THREE.Vector3());
  const size=modelBox.getSize(new THREE.Vector3());
  const distance=fitDistance(view);
  const pos=center.clone();
  const target=center.clone();
  target.y += size.y*.02;
  if(view==='left') pos[wideAxis]+=distance;
  if(view==='right') pos[wideAxis]-=distance;
  if(view==='rear') pos[longAxis]-=distance;
  pos.y += size.y*.03;
  return {pos,target};
}

function animateCamera(pos,target,duration=420){
  const startPos=camera.position.clone();
  const startTarget=controls.target.clone();
  const started=performance.now();
  tween={startPos,startTarget,pos,target,started,duration};
}

function updateTween(){
  if(!tween) return;
  const raw=(performance.now()-tween.started)/tween.duration;
  const t=Math.min(1,raw);
  const eased=1-Math.pow(1-t,3);
  camera.position.lerpVectors(tween.startPos,tween.pos,eased);
  controls.target.lerpVectors(tween.startTarget,tween.target,eased);
  if(t>=1) tween=null;
}

function setFixedView(view,instant=false){
  if(!modelBox) return;
  currentView=view;
  controls.autoRotate=false;
  controls.enableRotate=false;
  controls.enableZoom=false;
  controls.enablePan=false;
  freeMessage.style.display='none';
  zoneLayer.style.display=view==='rear'?'none':'block';
  if(rearSurfaceGroup) rearSurfaceGroup.visible=view==='rear';
  const pose=cameraPose(view);
  if(instant){camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update();}
  else animateCamera(pose.pos,pose.target);
  renderZones(view);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  const count=SPOTS.filter(s=>s.view===view).length;
  viewLabel.textContent=view==='rear' ? `REAR GLB SURFACE · ${count} STICKER SPOTS` : `${view.toUpperCase()} SIDE · ${count} AVAILABLE ZONES`;
  viewLabel.style.display='block';
  closePanel();
}

function setFreeView(){
  currentView='free';
  zoneLayer.innerHTML='';
  zoneLayer.style.display='none';
  if(rearSurfaceGroup) rearSurfaceGroup.visible=false;
  viewLabel.style.display='none';
  freeMessage.style.display='block';
  controls.enableRotate=true;
  controls.enableZoom=true;
  controls.enablePan=false;
  const center=modelBox.getCenter(new THREE.Vector3());
  const d=fitDistance('left')*1.05;
  const p=center.clone(); p[wideAxis]+=d*.72; p[longAxis]+=d*.72; p.y+=modelBox.getSize(new THREE.Vector3()).y*.18;
  animateCamera(p,center,450);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view==='free'));
  closePanel();
}

function renderZones(view){
  zoneLayer.innerHTML='';
  if(view==='rear') return;
  SPOTS.filter(s=>s.view===view).forEach(spot=>{
    const el=document.createElement('button');
    el.type='button';
    el.className=`zone ${spot.tier.toLowerCase()}`;
    el.style.left=`${spot.x}%`;
    el.style.top=`${spot.y}%`;
    el.style.width=`${spot.w}%`;
    el.style.height=`${spot.h}%`;
    el.setAttribute('aria-label',`${spot.tier} zone ${spot.id}, ${money(spot.price)}`);
    el.innerHTML=`<span class="zone-badge"><b>${spot.id}</b></span><span class="zone-price">${money(spot.price)}</span>`;
    el.addEventListener('click',()=>selectSpot(spot,el));
    zoneLayer.appendChild(el);
  });
}

function selectSpot(spot,el=null){
  selectedId=spot.id;
  [...zoneLayer.querySelectorAll('.zone')].forEach(z=>z.classList.remove('selected'));
  if(el) el.classList.add('selected');
  rearStickerMeshes.forEach(m=>{
    if(m.material) m.material.color.set(m.userData.spot?.id===spot.id?0xdcff29:0xffffff);
  });
  panelTier.textContent=`${spot.tier} · ${spot.view.toUpperCase()} · ${spot.id}`;
  panelName.textContent=spot.view==='rear'?`Rear sticker ${spot.id}`:`Sponsor zone ${spot.id}`;
  panelPrice.textContent=money(spot.price);
  panelCopy.textContent=spot.view==='rear'
    ? `${spot.copy} This sticker is projected onto the real GLB surface, so it follows the rear-door curvature.`
    : `${spot.copy} This exact rectangle becomes the physical location for your logo for 12 months.`;
  panelClaim.textContent=`Reserve ${spot.id} — ${money(spot.price)}`;
  panelClaim.href=`https://x.com/THEFOFOSHOW?brandmyvan=${encodeURIComponent(spot.id)}`;
  panel.hidden=false;
}

function closePanel(){
  selectedId=null;
  panel.hidden=true;
  [...zoneLayer.querySelectorAll('.zone')].forEach(z=>z.classList.remove('selected'));
  rearStickerMeshes.forEach(m=>{if(m.material)m.material.color.set(0xffffff)});
}

panelClose?.addEventListener('click',closePanel);
viewButtons.forEach(btn=>btn.addEventListener('click',()=>btn.dataset.view==='free'?setFreeView():setFixedView(btn.dataset.view)));
resetBtn?.addEventListener('click',()=>currentView==='free'?setFreeView():setFixedView(currentView));
window.addEventListener('resize',()=>{if(modelBox&&currentView!=='free')setFixedView(currentView,true)});

function rearRayHit(u,v){
  if(!model||!modelBox) return null;
  const size=modelBox.getSize(new THREE.Vector3());
  const origin=modelBox.getCenter(new THREE.Vector3());
  origin[wideAxis]=modelBox.min[wideAxis]+u*size[wideAxis];
  origin.y=modelBox.min.y+v*size.y;
  origin[longAxis]=modelBox.min[longAxis]-Math.max(.35,size[longAxis]*.10);
  const dir=new THREE.Vector3(); dir[longAxis]=1;
  modelRaycaster.set(origin,dir);
  modelRaycaster.far=size[longAxis]*1.35;
  const hits=modelRaycaster.intersectObject(model,true);
  if(!hits.length) return null;
  const p=hits[0].point.clone();
  p[longAxis]-=.004;
  return p;
}

function pointInPolygon(u,v,poly){
  let inside=false;
  for(let i=0,j=poly.length-1;i<poly.length;j=i++){
    const xi=poly[i][0], yi=poly[i][1];
    const xj=poly[j][0], yj=poly[j][1];
    const intersect=((yi>v)!==(yj>v))&&(u<(xj-xi)*(v-yi)/((yj-yi)||1e-9)+xi);
    if(intersect) inside=!inside;
  }
  return inside;
}

function createProjectedPatch({u0,u1,v0,v1,segmentsX=18,segmentsY=12,polygon=null,material}){
  const verts=[],uvs=[],indices=[],grid=[];
  for(let y=0;y<=segmentsY;y++){
    grid[y]=[];
    const tv=y/segmentsY;
    const v=v0+(v1-v0)*tv;
    for(let x=0;x<=segmentsX;x++){
      const tu=x/segmentsX;
      const u=u0+(u1-u0)*tu;
      const allowed=!polygon||pointInPolygon(u,v,polygon);
      const hit=allowed?rearRayHit(u,v):null;
      if(hit){
        const idx=verts.length/3;
        verts.push(hit.x,hit.y,hit.z);
        uvs.push(tu,tv);
        grid[y][x]=idx;
      } else grid[y][x]=-1;
    }
  }
  for(let y=0;y<segmentsY;y++){
    for(let x=0;x<segmentsX;x++){
      const a=grid[y][x],b=grid[y][x+1],c=grid[y+1][x],d=grid[y+1][x+1];
      if(a>=0&&b>=0&&c>=0) indices.push(a,b,c);
      if(b>=0&&d>=0&&c>=0) indices.push(b,d,c);
    }
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  const mesh=new THREE.Mesh(geometry,material);
  mesh.renderOrder=20;
  return mesh;
}

function makeStickerTexture(spot){
  const c=document.createElement('canvas');
  c.width=512; c.height=512;
  const ctx=c.getContext('2d');
  ctx.fillStyle='rgba(255,255,255,.96)'; ctx.fillRect(18,18,476,476);
  ctx.strokeStyle='#111'; ctx.lineWidth=18; ctx.strokeRect(18,18,476,476);
  ctx.fillStyle='#111'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.font='900 128px Arial'; ctx.fillText(spot.id,256,218);
  ctx.font='900 58px Arial'; ctx.fillText(money(spot.price),256,335);
  const texture=new THREE.CanvasTexture(c);
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.flipY=false;
  return texture;
}

function buildRearSurface(){
  if(!model||!modelBox||rearReady) return;
  rearSurfaceGroup=new THREE.Group();
  rearSurfaceGroup.name='rear-sponsor-surface';
  scene.add(rearSurfaceGroup);

  const rearPolygon=[
    [.29,.885],[.42,.902],[.58,.902],[.71,.885],
    [.745,.825],[.755,.665],[.72,.605],[.62,.565],
    [.50,.548],[.38,.565],[.28,.605],[.245,.665],[.255,.825]
  ];

  const redMaterial=new THREE.MeshBasicMaterial({
    color:0xff2026,transparent:true,opacity:.30,depthWrite:false,
    side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-4
  });
  const rearField=createProjectedPatch({u0:.22,u1:.78,v0:.54,v1:.91,segmentsX:42,segmentsY:28,polygon:rearPolygon,material:redMaterial});
  rearField.name='rear-allowed-sticker-field';
  rearSurfaceGroup.add(rearField);

  rearStickerMeshes=[];
  SPOTS.filter(s=>s.view==='rear').forEach(spot=>{
    const material=new THREE.MeshBasicMaterial({
      map:makeStickerTexture(spot),color:0xffffff,transparent:true,opacity:.98,depthWrite:false,
      side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-8
    });
    const decal=createProjectedPatch({
      u0:spot.u-spot.uw/2,u1:spot.u+spot.uw/2,
      v0:spot.v-spot.vh/2,v1:spot.v+spot.vh/2,
      segmentsX:12,segmentsY:10,material
    });
    decal.name=`rear-sticker-${spot.id}`;
    decal.userData.spot=spot;
    decal.renderOrder=30;
    rearStickerMeshes.push(decal);
    rearSurfaceGroup.add(decal);
  });
  rearSurfaceGroup.visible=currentView==='rear';
  rearReady=true;
}

function setPointer(event){
  const rect=canvas.getBoundingClientRect();
  pointer.x=((event.clientX-rect.left)/rect.width)*2-1;
  pointer.y=-((event.clientY-rect.top)/rect.height)*2+1;
}

canvas.addEventListener('pointermove',event=>{
  if(currentView!=='rear'||!rearStickerMeshes.length){canvas.style.cursor='';return;}
  setPointer(event);
  clickRaycaster.setFromCamera(pointer,camera);
  const hits=clickRaycaster.intersectObjects(rearStickerMeshes,false);
  canvas.style.cursor=hits.length?'pointer':'';
});

canvas.addEventListener('click',event=>{
  if(currentView!=='rear'||!rearStickerMeshes.length) return;
  setPointer(event);
  clickRaycaster.setFromCamera(pointer,camera);
  const hits=clickRaycaster.intersectObjects(rearStickerMeshes,false);
  if(hits.length) selectSpot(hits[0].object.userData.spot);
});

renderer.setAnimationLoop(()=>{
  resize();
  updateTween();
  controls.update();
  renderer.render(scene,camera);
});

async function boot(){
  try{
    const gltf=await new GLTFLoader().loadAsync('./van-realistic.glb');
    model=gltf.scene;
    const rawBox=new THREE.Box3().setFromObject(model);
    const rawSize=rawBox.getSize(new THREE.Vector3());
    const rawCenter=rawBox.getCenter(new THREE.Vector3());
    const scale=4.75/Math.max(rawSize.x,rawSize.y,rawSize.z);
    const origin=new THREE.Vector3(rawCenter.x,rawBox.min.y,rawCenter.z);
    model.scale.setScalar(scale);
    model.position.copy(origin).multiplyScalar(-scale);
    scene.add(model);
    scene.updateMatrixWorld(true);
    modelBox=new THREE.Box3().setFromObject(model);
    const size=modelBox.getSize(new THREE.Vector3());
    longAxis=size.x>=size.z?'x':'z';
    wideAxis=longAxis==='x'?'z':'x';
    buildRearSurface();
    setFixedView('left',true);
  }catch(err){
    console.error(err);
    viewLabel.textContent='3D MODEL UNAVAILABLE';
    zoneLayer.style.display='none';
  }
}

boot();
