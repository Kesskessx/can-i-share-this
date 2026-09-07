import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const stage = document.querySelector('#van');
const status = document.querySelector('#status');
const spots = [
  {name:'Driver door', price:420, point:[24,24,22], normal:[1,0,0]},
  {name:'Passenger door', price:420, point:[-24,24,22], normal:[-1,0,0]},
  {name:'Left panel', price:650, point:[23.5,38,-28], normal:[1,0,0]},
  {name:'Right panel', price:650, point:[-23.5,38,-28], normal:[-1,0,0]},
  {name:'Rear left', price:350, point:[12,34,-72.5], normal:[0,0,-1]},
  {name:'Rear right', price:350, point:[-12,34,-72.5], normal:[0,0,-1]},
  {name:'Hood', price:800, point:[0,26,53], normal:[0,1,0]},
  {name:'Roof', price:900, point:[0,61,-23], normal:[0,1,0]},
];
let focusSpot = () => {};
function selectSpot(i, focus=true) {
  spots.forEach((s,j) => {
    s.card.classList.toggle('active',i===j); s.pin.classList.toggle('active',i===j);
    s.card.setAttribute('aria-pressed',String(i===j)); s.pin.setAttribute('aria-pressed',String(i===j));
  });
  document.querySelector('#selname').textContent = `${String(i+1).padStart(2,'0')} — ${spots[i].name}`;
  document.querySelector('#selprice').textContent = `From €${spots[i].price}`;
  if(focus) focusSpot(spots[i]);
}
spots.forEach((s,i) => {
  s.card = document.createElement('button'); s.card.type='button'; s.card.className='card';
  s.card.innerHTML=`<span class="num">${String(i+1).padStart(2,'0')}</span><b>${s.name}</b><strong>€${s.price}</strong>`;
  s.card.addEventListener('click',()=>selectSpot(i)); document.querySelector('#grid').append(s.card);
  s.pin=document.createElement('button');s.pin.type='button';s.pin.className='pin';s.pin.textContent=i+1;s.pin.hidden=true;
  s.pin.setAttribute('aria-label',`${s.name}, from €${s.price}`);
  s.pin.addEventListener('click',()=>selectSpot(i));document.querySelector('#hotspots').append(s.pin);
});
selectSpot(0,false);
try {
  const renderer = new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.setClearColor(0xfaf9f5,1); renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
  stage.append(renderer.domElement);
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(36,1,0.01,100);
  camera.position.set(4,2.6,5);
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.target.set(0,0.9,0);controls.enableDamping=true;controls.enablePan=false;
  controls.minDistance=3.5;controls.maxDistance=10;controls.maxPolarAngle=Math.PI/2-0.025;
  controls.autoRotateSpeed=0.7;
  scene.add(new THREE.HemisphereLight(0xffffff,0xb5b0a3,3.0));
  for(const [position,intensity] of [[[3,6,5],3], [[-4,3,-3],1.5]]) {
    const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...position);scene.add(light);
  }
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=128;shadowCanvas.height=128;
  const ctx=shadowCanvas.getContext('2d');const gradient=ctx.createRadialGradient(64,64,10,64,64,64);
  gradient.addColorStop(0,'rgba(0,0,0,.24)');gradient.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,128,128);
  const shadow=new THREE.Mesh(new THREE.PlaneGeometry(2.8,5.4),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));
  shadow.rotation.x=-Math.PI/2;shadow.position.y=-0.01;scene.add(shadow);
  let ready=false,desiredPosition=null;
  const resize=()=>{const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();};
  new ResizeObserver(resize).observe(stage);resize();
  const stopAuto=()=>{controls.autoRotate=false;document.querySelector('#rotate').setAttribute('aria-pressed','false');};
  controls.addEventListener('start',()=>{desiredPosition=null;stopAuto();});
  document.querySelector('#rotate').addEventListener('click',()=>{desiredPosition=null;controls.autoRotate=!controls.autoRotate;document.querySelector('#rotate').setAttribute('aria-pressed',String(controls.autoRotate));});
  document.querySelector('#reset').addEventListener('click',()=>{stopAuto();desiredPosition=new THREE.Vector3(4,2.6,5);});
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();status.textContent='3D VIEW INTERRUPTED — RELOAD THE PAGE';});
  const gltf=await new GLTFLoader().loadAsync('./van-realistic.glb',event=>{
    if(event.total)status.textContent=`LOADING THE VAN · ${Math.round(event.loaded/event.total*100)}%`;
  });
  const box=new THREE.Box3().setFromObject(gltf.scene);const size=box.getSize(new THREE.Vector3());const center=box.getCenter(new THREE.Vector3());
  const scale=4/Math.max(size.x,size.y,size.z);
  const origin=new THREE.Vector3(center.x,box.min.y,center.z);
  gltf.scene.scale.setScalar(scale);gltf.scene.position.copy(origin).multiplyScalar(-scale);scene.add(gltf.scene);
  spots.forEach(s=>{s.world=new THREE.Vector3(...s.point).sub(origin).multiplyScalar(scale);s.direction=new THREE.Vector3(...s.normal);});
  focusSpot=s=>{stopAuto();const dir=s.direction.clone();if(dir.y>0.5)dir.set(0.5,1,s.name==='Hood'?1:-0.3);else dir.y=.36;desiredPosition=controls.target.clone().add(dir.normalize().multiplyScalar(6));};
  ready=true;stage.dataset.modelLoaded='true';status.textContent='DRAG TO ROTATE · SCROLL OR PINCH TO ZOOM';
  const projected=new THREE.Vector3(),towardCamera=new THREE.Vector3();
  renderer.setAnimationLoop(()=>{
    if(desiredPosition){camera.position.lerp(desiredPosition,.085);if(camera.position.distanceTo(desiredPosition)<.01)desiredPosition=null;}
    controls.update();renderer.render(scene,camera);
    if(ready)spots.forEach(s=>{
      projected.copy(s.world).project(camera);towardCamera.copy(camera.position).sub(s.world);
      s.pin.hidden=s.direction.dot(towardCamera)<.2 || projected.z>1 || Math.abs(projected.x)>1 || Math.abs(projected.y)>1;
      if(!s.pin.hidden){s.pin.style.left=`${(projected.x*.5+.5)*stage.clientWidth}px`;s.pin.style.top=`${(-projected.y*.5+.5)*stage.clientHeight}px`;}
    });
  });
} catch(error) {
  console.error('Van viewer failed:',error);
  status.replaceChildren(document.createTextNode('THE 3D VAN COULD NOT LOAD. '));
  const retry=document.createElement('a');retry.href='';retry.className='status-link';retry.textContent='RETRY';status.append(retry);
  stage.dataset.modelLoaded='false';
}
