import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const canvas = document.getElementById('vanCanvas');
const stage = document.getElementById('vanStage');
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
  {id:'S1',view:'left',tier:'Signature',price:1500,x:35,y:36,w:28,h:25,copy:'Main left-side sponsor zone. The largest and most visible placement on this side.'},
  {id:'L1',view:'left',tier:'Large',price:750,x:13,y:38,w:19,h:22,copy:'Large left-side placement with strong visibility while driving or parked.'},
  {id:'L2',view:'left',tier:'Large',price:750,x:66,y:38,w:19,h:22,copy:'Large left-side placement with strong visibility while driving or parked.'},
  {id:'M1',view:'left',tier:'Medium',price:400,x:35,y:23,w:13,h:10,copy:'Medium left-side sponsor zone.'},
  {id:'M2',view:'left',tier:'Medium',price:400,x:50,y:23,w:13,h:10,copy:'Medium left-side sponsor zone.'},
  {id:'SM1',view:'left',tier:'Small',price:200,x:27,y:65,w:15,h:9,copy:'Compact left-side sponsor zone.'},
  {id:'SM2',view:'left',tier:'Small',price:200,x:44,y:65,w:15,h:9,copy:'Compact left-side sponsor zone.'},

  {id:'S2',view:'right',tier:'Signature',price:1500,x:37,y:36,w:28,h:25,copy:'Main right-side sponsor zone. The largest and most visible placement on this side.'},
  {id:'L3',view:'right',tier:'Large',price:750,x:15,y:38,w:19,h:22,copy:'Large right-side placement with strong visibility while driving or parked.'},
  {id:'L4',view:'right',tier:'Large',price:750,x:68,y:38,w:19,h:22,copy:'Large right-side placement with strong visibility while driving or parked.'},
  {id:'M3',view:'right',tier:'Medium',price:400,x:37,y:23,w:13,h:10,copy:'Medium right-side sponsor zone.'},
  {id:'M4',view:'right',tier:'Medium',price:400,x:52,y:23,w:13,h:10,copy:'Medium right-side sponsor zone.'},
  {id:'SM3',view:'right',tier:'Small',price:200,x:29,y:65,w:15,h:9,copy:'Compact right-side sponsor zone.'},
  {id:'SM4',view:'right',tier:'Small',price:200,x:46,y:65,w:15,h:9,copy:'Compact right-side sponsor zone.'},

  {id:'M5',view:'rear',tier:'Medium',price:400,x:36,y:34,w:13,h:18,copy:'Medium rear sponsor zone.'},
  {id:'M6',view:'rear',tier:'Medium',price:400,x:51,y:34,w:13,h:18,copy:'Medium rear sponsor zone.'},
  {id:'SM5',view:'rear',tier:'Small',price:400,x:36,y:54,w:13,h:11,copy:'Compact rear sponsor zone.'},
  {id:'SM6',view:'rear',tier:'Small',price:200,x:51,y:54,w:13,h:11,copy:'Compact rear sponsor zone.'},
  {id:'SM7',view:'rear',tier:'Small',price:200,x:36,y:67,w:13,h:9,copy:'Compact rear sponsor zone.'},
  {id:'SM8',view:'rear',tier:'Small',price:200,x:51,y:67,w:13,h:9,copy:'Compact rear sponsor zone.'}
];

// Keep the funding math exact: the first rear small spot belongs to the €200 tier.
SPOTS.find(s => s.id === 'SM5').price = 200;

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
const key = new THREE.DirectionalLight(0xffffff,3.3);key.position.set(5,7,5);scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff,1.4);fill.position.set(-5,3,-4);scene.add(fill);
const floor = new THREE.Mesh(new THREE.CircleGeometry(4.2,72),new THREE.MeshStandardMaterial({color:0xebe7dc,roughness:1,metalness:0}));
floor.rotation.x=-Math.PI/2;floor.position.y=-.02;scene.add(floor);

let model = null;
let modelBox = null;
let longAxis = 'x';
let wideAxis = 'z';
let currentView = 'left';
let selectedId = null;
let tween = null;

function money(v){return `€${v.toLocaleString('en-US')}`}

function resize(){
  const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),r=renderer.getPixelRatio();
  if(canvas.width!==Math.round(w*r)||canvas.height!==Math.round(h*r)) renderer.setSize(w,h,false);
  camera.aspect=w/h;camera.updateProjectionMatrix();
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
  return Math.max(byHeight,byWidth)*1.18;
}

function cameraPose(view){
  const center=modelBox.getCenter(new THREE.Vector3());
  const size=modelBox.getSize(new THREE.Vector3());
  const distance=fitDistance(view);
  const pos=center.clone();
  const target=center.clone();
  target.y += size.y*.03;

  if(view==='left') pos[wideAxis]+=distance;
  if(view==='right') pos[wideAxis]-=distance;
  if(view==='rear') pos[longAxis]+=distance;
  pos.y += size.y*.04;

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
  zoneLayer.style.display='block';
  const pose=cameraPose(view);
  if(instant){camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update();}
  else animateCamera(pose.pos,pose.target);
  renderZones(view);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  const count=SPOTS.filter(s=>s.view===view).length;
  viewLabel.textContent=`${view.toUpperCase()} ${view==='rear'?'VIEW':'SIDE'} · ${count} AVAILABLE ZONES`;
  viewLabel.style.display='block';
  closePanel();
}

function setFreeView(){
  currentView='free';
  zoneLayer.innerHTML='';
  zoneLayer.style.display='none';
  viewLabel.style.display='none';
  freeMessage.style.display='block';
  controls.enableRotate=true;
  controls.enableZoom=true;
  controls.enablePan=false;
  const center=modelBox.getCenter(new THREE.Vector3());
  const d=fitDistance('left')*1.05;
  const p=center.clone();p[wideAxis]+=d*.72;p[longAxis]+=d*.72;p.y+=modelBox.getSize(new THREE.Vector3()).y*.18;
  animateCamera(p,center,450);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view==='free'));
  closePanel();
}

function renderZones(view){
  zoneLayer.innerHTML='';
  SPOTS.filter(s=>s.view===view).forEach(spot=>{
    const el=document.createElement('button');
    el.type='button';
    el.className=`zone ${spot.tier.toLowerCase()}`;
    el.style.left=`${spot.x}%`;el.style.top=`${spot.y}%`;el.style.width=`${spot.w}%`;el.style.height=`${spot.h}%`;
    el.setAttribute('aria-label',`${spot.tier} zone ${spot.id}, ${money(spot.price)}`);
    el.innerHTML=`<span class="zone-badge"><b>${spot.id}</b><span>${money(spot.price)}</span></span><span class="zone-price">${money(spot.price)}</span>`;
    el.addEventListener('click',()=>selectSpot(spot,el));
    zoneLayer.appendChild(el);
  });
}

function selectSpot(spot,el){
  selectedId=spot.id;
  [...zoneLayer.querySelectorAll('.zone')].forEach(z=>z.classList.remove('selected'));
  el.classList.add('selected');
  panelTier.textContent=`${spot.tier} · ${spot.view.toUpperCase()} · ${spot.id}`;
  panelName.textContent=`Sponsor zone ${spot.id}`;
  panelPrice.textContent=money(spot.price);
  panelCopy.textContent=`${spot.copy} This exact rectangle becomes the physical location for your logo for 12 months.`;
  panelClaim.textContent=`Reserve ${spot.id} — ${money(spot.price)}`;
  panelClaim.href=`https://x.com/THEFOFOSHOW?brandmyvan=${encodeURIComponent(spot.id)}`;
  panel.hidden=false;
}

function closePanel(){
  selectedId=null;
  panel.hidden=true;
  [...zoneLayer.querySelectorAll('.zone')].forEach(z=>z.classList.remove('selected'));
}

panelClose?.addEventListener('click',closePanel);
viewButtons.forEach(btn=>btn.addEventListener('click',()=>btn.dataset.view==='free'?setFreeView():setFixedView(btn.dataset.view)));
resetBtn?.addEventListener('click',()=>currentView==='free'?setFreeView():setFixedView(currentView));
window.addEventListener('resize',()=>{if(modelBox&&currentView!=='free')setFixedView(currentView,true)});

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
    setFixedView('left',true);
  }catch(err){
    console.error(err);
    viewLabel.textContent='3D MODEL UNAVAILABLE';
    zoneLayer.style.display='none';
  }
}

boot();
