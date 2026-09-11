import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const canvas=document.getElementById('vanCanvas');
const zoneLayer=document.getElementById('zoneLayer');
const viewLabel=document.getElementById('viewLabel');
const viewerTip=document.getElementById('viewerTip');
const freeMessage=document.getElementById('freeMessage');
const resetBtn=document.getElementById('resetVan');
const viewButtons=[...document.querySelectorAll('[data-view]')];
const panel=document.getElementById('spotPanel');
const panelTier=document.getElementById('spotPanelTier');
const panelName=document.getElementById('spotPanelName');
const panelPrice=document.getElementById('spotPanelPrice');
const panelCopy=document.getElementById('spotPanelCopy');
const panelClaim=document.getElementById('spotPanelClaim');
const panelClose=document.getElementById('spotPanelClose');

const SPOTS=[
  {id:'S1',view:'left',tier:'Signature',price:1500,u:.47,v:.54,uw:.28,vh:.22,copy:'Main left cargo-panel placement.'},
  {id:'L1',view:'left',tier:'Large',price:750,u:.80,v:.53,uw:.18,vh:.18,copy:'Front-door body placement below the glass line.'},
  {id:'L2',view:'left',tier:'Large',price:750,u:.20,v:.53,uw:.18,vh:.20,copy:'Rear cargo-panel placement above the wheel area.'},
  {id:'M1',view:'left',tier:'Medium',price:400,u:.55,v:.70,uw:.12,vh:.085,copy:'Upper cargo-panel placement.'},
  {id:'M2',view:'left',tier:'Medium',price:400,u:.42,v:.70,uw:.12,vh:.085,copy:'Upper cargo-panel placement.'},
  {id:'SM1',view:'left',tier:'Small',price:200,u:.52,v:.315,uw:.12,vh:.070,copy:'Compact lower cargo-panel placement.'},
  {id:'SM2',view:'left',tier:'Small',price:200,u:.39,v:.315,uw:.12,vh:.070,copy:'Compact lower cargo-panel placement.'},

  {id:'S2',view:'right',tier:'Signature',price:1500,u:.50,v:.54,uw:.28,vh:.22,copy:'Main right cargo-panel placement.'},
  {id:'L3',view:'right',tier:'Large',price:750,u:.20,v:.53,uw:.18,vh:.20,copy:'Rear cargo-panel placement above the wheel area.'},
  {id:'L4',view:'right',tier:'Large',price:750,u:.80,v:.53,uw:.18,vh:.18,copy:'Front-door body placement below the glass line.'},
  {id:'M3',view:'right',tier:'Medium',price:400,u:.42,v:.70,uw:.12,vh:.085,copy:'Upper cargo-panel placement.'},
  {id:'M4',view:'right',tier:'Medium',price:400,u:.55,v:.70,uw:.12,vh:.085,copy:'Upper cargo-panel placement.'},
  {id:'SM3',view:'right',tier:'Small',price:200,u:.45,v:.315,uw:.12,vh:.070,copy:'Compact lower cargo-panel placement.'},
  {id:'SM4',view:'right',tier:'Small',price:200,u:.58,v:.315,uw:.12,vh:.070,copy:'Compact lower cargo-panel placement.'},

  {id:'M5',view:'rear',tier:'Medium',price:400,u:.395,v:.785,uw:.105,vh:.095,copy:'Upper-left rear-door sticker.'},
  {id:'M6',view:'rear',tier:'Medium',price:400,u:.605,v:.785,uw:.105,vh:.095,copy:'Upper-right rear-door sticker.'},
  {id:'SM5',view:'rear',tier:'Small',price:200,u:.315,v:.665,uw:.070,vh:.065,copy:'Lower-left rear-door sticker.'},
  {id:'SM6',view:'rear',tier:'Small',price:200,u:.435,v:.665,uw:.070,vh:.065,copy:'Lower-left-center rear-door sticker.'},
  {id:'SM7',view:'rear',tier:'Small',price:200,u:.565,v:.665,uw:.070,vh:.065,copy:'Lower-right-center rear-door sticker.'},
  {id:'SM8',view:'rear',tier:'Small',price:200,u:.685,v:.665,uw:.070,vh:.065,copy:'Lower-right rear-door sticker.'}
];

const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.15;

const scene=new THREE.Scene();
scene.background=new THREE.Color('#f7f6f1');
const camera=new THREE.PerspectiveCamera(29,1,.01,100);
const controls=new OrbitControls(camera,canvas);
controls.enableDamping=true;
controls.enablePan=false;
controls.autoRotate=false;
controls.minPolarAngle=Math.PI*.18;
controls.maxPolarAngle=Math.PI*.82;

const hemi=new THREE.HemisphereLight(0xffffff,0xb8b0a2,3.1);scene.add(hemi);
const key=new THREE.DirectionalLight(0xffffff,3.2);key.position.set(5,7,5);scene.add(key);
const fill=new THREE.DirectionalLight(0xffffff,1.3);fill.position.set(-5,3,-4);scene.add(fill);
const floor=new THREE.Mesh(new THREE.CircleGeometry(4.3,72),new THREE.MeshStandardMaterial({color:0xebe7dc,roughness:1,metalness:0}));
floor.rotation.x=-Math.PI/2;floor.position.y=-.02;scene.add(floor);

let model=null,modelBox=null,currentView='left',selectedId=null,tween=null;
let longAxis='x',wideAxis='z',garageGroup=null;
const garageLights=[];
const viewGroups={left:null,right:null,rear:null};
const viewSpotMeshes={left:[],right:[],rear:[]};
const modelRaycaster=new THREE.Raycaster();
const clickRaycaster=new THREE.Raycaster();
const pointer=new THREE.Vector2();

function money(v){return `€${v.toLocaleString('en-US')}`}
function axisVector(axis,value=1){const v=new THREE.Vector3();v[axis]=value;return v}
function viewConfig(view){
  if(view==='rear')return {rayAxis:longAxis,hAxis:wideAxis,out:axisVector(longAxis,-1),flipU:false};
  if(view==='left')return {rayAxis:wideAxis,hAxis:longAxis,out:axisVector(wideAxis,1),flipU:true};
  return {rayAxis:wideAxis,hAxis:longAxis,out:axisVector(wideAxis,-1),flipU:false};
}

function resize(){
  const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),r=renderer.getPixelRatio();
  if(canvas.width!==Math.round(w*r)||canvas.height!==Math.round(h*r))renderer.setSize(w,h,false);
  camera.aspect=w/h;camera.updateProjectionMatrix();
}
function fitDistance(view){
  if(!modelBox)return 6;resize();
  const size=modelBox.getSize(new THREE.Vector3());
  const width=view==='rear'?size[wideAxis]:size[longAxis];
  const fov=THREE.MathUtils.degToRad(camera.fov);
  const byHeight=(size.y*.5)/Math.tan(fov*.5);
  const byWidth=(width*.5)/(Math.tan(fov*.5)*Math.max(camera.aspect,.42));
  return Math.max(byHeight,byWidth)*(view==='rear'?1.24:1.18);
}
function cameraPose(view){
  const center=modelBox.getCenter(new THREE.Vector3()),size=modelBox.getSize(new THREE.Vector3()),d=fitDistance(view);
  const pos=center.clone(),target=center.clone();target.y+=size.y*.015;
  if(view==='left')pos[wideAxis]+=d;
  if(view==='right')pos[wideAxis]-=d;
  if(view==='rear')pos[longAxis]-=d;
  pos.y+=size.y*.015;
  return {pos,target};
}
function animateCamera(pos,target,duration=380){
  tween={startPos:camera.position.clone(),startTarget:controls.target.clone(),pos,target,started:performance.now(),duration};
}
function updateTween(){
  if(!tween)return;const t=Math.min(1,(performance.now()-tween.started)/tween.duration),e=1-Math.pow(1-t,3);
  camera.position.lerpVectors(tween.startPos,tween.pos,e);controls.target.lerpVectors(tween.startTarget,tween.target,e);if(t>=1)tween=null;
}

function makeGarageSignTexture(){
  const c=document.createElement('canvas');c.width=1024;c.height=256;const ctx=c.getContext('2d');
  ctx.fillStyle='#111315';ctx.fillRect(0,0,c.width,c.height);
  ctx.fillStyle='#dcff29';ctx.font='900 92px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('BRAND MYVAN',512,105);
  ctx.fillStyle='#ffffff';ctx.font='700 28px Arial';ctx.fillText('GARAGE · SPONSOR BUILD',512,184);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;return t;
}

function buildGarage(){
  if(!modelBox||garageGroup)return;
  const size=modelBox.getSize(new THREE.Vector3());
  const roomLong=Math.max(size[longAxis]*2.45,11);
  const roomWide=Math.max(size[wideAxis]*3.8,8.2);
  const roomHeight=Math.max(size.y*2.75,5.4);
  const worldX=longAxis==='x'?roomLong:roomWide;
  const worldZ=longAxis==='z'?roomLong:roomWide;
  const backCoord=wideAxis==='z'?-worldZ/2:-worldX/2;
  const insideBack=backCoord+.10;

  garageGroup=new THREE.Group();garageGroup.name='garage-environment';scene.add(garageGroup);
  const concrete=new THREE.MeshStandardMaterial({color:0x3e4247,roughness:.94,metalness:.02});
  const wallMat=new THREE.MeshStandardMaterial({color:0x8c9094,roughness:.9,metalness:.01});
  const darkMat=new THREE.MeshStandardMaterial({color:0x202327,roughness:.8,metalness:.08});
  const doorMat=new THREE.MeshStandardMaterial({color:0x70757a,roughness:.72,metalness:.18});
  const floorGarage=new THREE.Mesh(new THREE.PlaneGeometry(worldX,worldZ),concrete);floorGarage.rotation.x=-Math.PI/2;floorGarage.position.y=-.035;garageGroup.add(floorGarage);

  const backWall=wideAxis==='z'
    ?new THREE.Mesh(new THREE.BoxGeometry(worldX,roomHeight,.16),wallMat)
    :new THREE.Mesh(new THREE.BoxGeometry(.16,roomHeight,worldZ),wallMat);
  backWall.position.y=roomHeight/2-.02;backWall.position[wideAxis]=backCoord;garageGroup.add(backWall);

  const sideGeom=longAxis==='x'?new THREE.BoxGeometry(.16,roomHeight,worldZ):new THREE.BoxGeometry(worldX,roomHeight,.16);
  for(const sign of [-1,1]){
    const wall=new THREE.Mesh(sideGeom,wallMat);wall.position.y=roomHeight/2-.02;
    wall.position[longAxis]=sign*(roomLong/2);garageGroup.add(wall);
  }

  const lowerStripe=wideAxis==='z'
    ?new THREE.Mesh(new THREE.BoxGeometry(worldX*.96,.42,.05),darkMat)
    :new THREE.Mesh(new THREE.BoxGeometry(.05,.42,worldZ*.96),darkMat);
  lowerStripe.position.y=.45;lowerStripe.position[wideAxis]=insideBack+.02;garageGroup.add(lowerStripe);

  const doorW=Math.min(roomLong*.56,Math.max(size[longAxis]*1.45,5.2));
  const doorH=Math.min(roomHeight*.64,Math.max(size.y*1.55,3.6));
  const panelCount=6,panelH=doorH/panelCount;
  for(let i=0;i<panelCount;i++){
    const panel=wideAxis==='z'
      ?new THREE.Mesh(new THREE.BoxGeometry(doorW,panelH-.025,.07),doorMat)
      :new THREE.Mesh(new THREE.BoxGeometry(.07,panelH-.025,doorW),doorMat);
    panel.position.y=.12+panelH*(i+.5);panel.position[wideAxis]=insideBack+.04;garageGroup.add(panel);
  }

  const signMat=new THREE.MeshBasicMaterial({map:makeGarageSignTexture(),toneMapped:false});
  const signMesh=new THREE.Mesh(new THREE.PlaneGeometry(Math.min(4.2,roomLong*.42),1.0),signMat);
  signMesh.position.y=Math.min(roomHeight-.8,doorH+1.05);signMesh.position[wideAxis]=insideBack+.09;
  if(wideAxis==='x')signMesh.rotation.y=Math.PI/2;
  garageGroup.add(signMesh);

  const beamMat=new THREE.MeshStandardMaterial({color:0x2b2e32,roughness:.7,metalness:.35});
  const lightMat=new THREE.MeshBasicMaterial({color:0xf7fbff,toneMapped:false});
  const barLength=Math.min(roomLong*.48,5.8);
  for(const w of [-roomWide*.18,roomWide*.18]){
    const beam=longAxis==='x'?new THREE.Mesh(new THREE.BoxGeometry(barLength,.10,.20),beamMat):new THREE.Mesh(new THREE.BoxGeometry(.20,.10,barLength),beamMat);
    beam.position.y=roomHeight-.52;beam.position[wideAxis]=w;garageGroup.add(beam);
    const glow=longAxis==='x'?new THREE.Mesh(new THREE.BoxGeometry(barLength*.92,.035,.12),lightMat):new THREE.Mesh(new THREE.BoxGeometry(.12,.035,barLength*.92),lightMat);
    glow.position.y=roomHeight-.58;glow.position[wideAxis]=w;garageGroup.add(glow);
    const lamp=new THREE.PointLight(0xeef6ff,22,roomWide*1.45,2);lamp.position.y=roomHeight-.72;lamp.position[wideAxis]=w;garageGroup.add(lamp);garageLights.push(lamp);
  }

  const lineMat=new THREE.MeshBasicMaterial({color:0xc9bd70,toneMapped:false});
  for(const sign of [-1,1]){
    const line=longAxis==='x'?new THREE.Mesh(new THREE.BoxGeometry(roomLong*.45,.012,.035),lineMat):new THREE.Mesh(new THREE.BoxGeometry(.035,.012,roomLong*.45),lineMat);
    line.position.y=.006;line.position[wideAxis]=sign*Math.max(size[wideAxis]*.72,.9);garageGroup.add(line);
  }

  const shadowMat=new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.23,depthWrite:false});
  const shadow=new THREE.Mesh(new THREE.CircleGeometry(1,72),shadowMat);shadow.rotation.x=-Math.PI/2;shadow.position.y=.008;shadow.scale.set(Math.max(size.x*.58,1.4),Math.max(size.z*.72,.8),1);garageGroup.add(shadow);
  garageGroup.visible=false;
}

function setEnvironmentMode(garage){
  if(garageGroup)garageGroup.visible=garage;
  floor.visible=!garage;
  scene.background.set(garage?0x1b1e22:0xf7f6f1);
  hemi.intensity=garage?1.45:3.1;
  key.intensity=garage?3.8:3.2;
  fill.intensity=garage?1.8:1.3;
  renderer.toneMappingExposure=garage?1.08:1.15;
}

function setGroupVisibility(view){
  for(const k of ['left','right','rear'])if(viewGroups[k])viewGroups[k].visible=(k===view);
}
function setFixedView(view,instant=false){
  if(!modelBox)return;currentView=view;
  setEnvironmentMode(false);
  controls.enableRotate=false;controls.enableZoom=false;controls.enablePan=false;controls.autoRotate=false;
  freeMessage.style.display='none';zoneLayer.style.display='none';setGroupVisibility(view);
  const pose=cameraPose(view);if(instant){camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update()}else animateCamera(pose.pos,pose.target);
  viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  const count=SPOTS.filter(s=>s.view===view).length;
  viewLabel.textContent=`${view.toUpperCase()} · ${count} AVAILABLE SPOTS`;
  viewLabel.style.display='block';if(viewerTip){viewerTip.textContent='Tap a spot to see price';viewerTip.style.display='block'};
  closePanel();
}
function setFreeView(){
  currentView='free';setEnvironmentMode(true);zoneLayer.style.display='none';setGroupVisibility('none');viewLabel.style.display='none';
  freeMessage.style.display='block';if(viewerTip)viewerTip.style.display='none';
  controls.enableRotate=true;controls.enableZoom=true;controls.enablePan=false;
  const c=modelBox.getCenter(new THREE.Vector3()),size=modelBox.getSize(new THREE.Vector3()),d=fitDistance('left')*1.18,p=c.clone();
  p[wideAxis]+=d*.82;p[longAxis]+=d*.82;p.y+=size.y*.24;
  controls.minDistance=d*.48;controls.maxDistance=d*1.65;
  animateCamera(p,c,460);viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view==='free'));closePanel();
}

function sampleSurface(view,u,v,{strict=true}={}){
  if(!model||!modelBox)return null;
  const cfg=viewConfig(view),size=modelBox.getSize(new THREE.Vector3()),origin=modelBox.getCenter(new THREE.Vector3());
  origin[cfg.hAxis]=modelBox.min[cfg.hAxis]+u*size[cfg.hAxis];origin.y=modelBox.min.y+v*size.y;
  const margin=Math.max(.35,size[cfg.rayAxis]*.12);
  origin[cfg.rayAxis]=(cfg.out[cfg.rayAxis]>0?modelBox.max[cfg.rayAxis]+margin:modelBox.min[cfg.rayAxis]-margin);
  const dir=cfg.out.clone().multiplyScalar(-1);modelRaycaster.set(origin,dir);modelRaycaster.far=size[cfg.rayAxis]*1.6;
  const hits=modelRaycaster.intersectObject(model,true);
  for(const hit of hits){
    if(!hit.face)continue;
    const n=hit.face.normal.clone().applyMatrix3(new THREE.Matrix3().getNormalMatrix(hit.object.matrixWorld)).normalize();
    const facing=n.dot(cfg.out);if(strict&&facing<.62)continue;
    return {point:hit.point.clone(),normal:n,distance:hit.distance,object:hit.object};
  }
  return null;
}

function createSurfacePatch(view,{u0,u1,v0,v1,nx=18,ny=12,material,autoMask=true,offset=.006,erode=1}){
  const cfg=viewConfig(view),samples=[];
  for(let y=0;y<=ny;y++){
    samples[y]=[];
    for(let x=0;x<=nx;x++){
      const u=u0+(u1-u0)*(x/nx),v=v0+(v1-v0)*(y/ny);samples[y][x]=sampleSurface(view,u,v,{strict:autoMask});
    }
  }
  if(autoMask){
    const distances=[];for(const row of samples)for(const s of row)if(s)distances.push(s.distance);distances.sort((a,b)=>a-b);
    const median=distances.length?distances[Math.floor(distances.length/2)]:0;
    const size=modelBox.getSize(new THREE.Vector3()),depthTol=Math.max(.022,size[cfg.rayAxis]*.022);
    for(let y=0;y<=ny;y++)for(let x=0;x<=nx;x++)if(samples[y][x]&&Math.abs(samples[y][x].distance-median)>depthTol)samples[y][x]=null;
    for(let pass=0;pass<erode;pass++){
      const ok=samples.map(r=>r.map(Boolean));
      for(let y=1;y<ny;y++)for(let x=1;x<nx;x++){
        if(!ok[y][x]){samples[y][x]=null;continue}
        let keep=true;for(let yy=-1;yy<=1;yy++)for(let xx=-1;xx<=1;xx++)if(!ok[y+yy]?.[x+xx])keep=false;
        if(!keep)samples[y][x]=null;
      }
    }
  }
  const verts=[],uvs=[],grid=[];
  for(let y=0;y<=ny;y++){
    grid[y]=[];
    for(let x=0;x<=nx;x++){
      const s=samples[y][x];if(!s){grid[y][x]=-1;continue}
      const p=s.point.clone().addScaledVector(s.normal,offset);grid[y][x]=verts.length/3;verts.push(p.x,p.y,p.z);
      const ux=cfg.flipU?1-x/nx:x/nx;uvs.push(ux,y/ny);
    }
  }
  const tangent=axisVector(cfg.hAxis,1),up=new THREE.Vector3(0,1,0),basis=tangent.clone().cross(up),front=basis.dot(cfg.out)>0,idx=[];
  for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
    const a=grid[y][x],b=grid[y][x+1],c=grid[y+1][x],d=grid[y+1][x+1];
    if(a>=0&&b>=0&&c>=0)idx.push(...(front?[a,b,c]:[a,c,b]));
    if(b>=0&&d>=0&&c>=0)idx.push(...(front?[b,d,c]:[b,c,d]));
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));g.setIndex(idx);g.computeVertexNormals();
  const mesh=new THREE.Mesh(g,material);mesh.renderOrder=20;return mesh;
}

function makeSpotTexture(spot,selected=false){
  const c=document.createElement('canvas');c.width=1024;c.height=640;const ctx=c.getContext('2d');
  ctx.clearRect(0,0,c.width,c.height);
  ctx.fillStyle=selected?'rgba(220,255,41,.74)':'rgba(229,58,63,.13)';ctx.fillRect(16,16,992,608);
  ctx.strokeStyle=selected?'#111111':'#e53a3f';ctx.lineWidth=18;ctx.strokeRect(18,18,988,604);
  ctx.fillStyle='#111';ctx.beginPath();ctx.roundRect(54,54,190,112,56);ctx.fill();
  ctx.fillStyle='#fff';ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='900 58px Arial';ctx.fillText(spot.id,149,110);
  ctx.fillStyle='#111';ctx.font='900 58px Arial';ctx.textAlign='right';ctx.fillText(money(spot.price),950,555);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;return t;
}

function buildSpotMesh(spot){
  const material=new THREE.MeshBasicMaterial({map:makeSpotTexture(spot,false),transparent:true,opacity:.98,depthWrite:false,side:THREE.DoubleSide});
  material.userData.normalMap=material.map;material.userData.selectedMap=makeSpotTexture(spot,true);
  const mesh=createSurfacePatch(spot.view,{u0:spot.u-spot.uw/2,u1:spot.u+spot.uw/2,v0:spot.v-spot.vh/2,v1:spot.v+spot.vh/2,nx:spot.tier==='Small'?14:20,ny:spot.tier==='Small'?10:14,material,autoMask:true,offset:.010,erode:1});
  mesh.name=`spot-${spot.id}`;mesh.userData.spot=spot;mesh.renderOrder=30;return mesh;
}

function buildViewGroups(){
  for(const view of ['left','right','rear']){
    const group=new THREE.Group();group.name=`${view}-sponsor-spots`;scene.add(group);viewGroups[view]=group;viewSpotMeshes[view]=[];
    if(view==='rear'){
      const redMat=new THREE.MeshBasicMaterial({color:0xf1282d,transparent:true,opacity:.22,depthWrite:false,side:THREE.DoubleSide});
      const field=createSurfacePatch('rear',{u0:.22,u1:.78,v0:.61,v1:.90,nx:92,ny:54,material:redMat,autoMask:true,offset:.004,erode:2});
      field.name='rear-printable-area';field.renderOrder=15;group.add(field);
    }
    for(const spot of SPOTS.filter(s=>s.view===view)){
      const mesh=buildSpotMesh(spot);viewSpotMeshes[view].push(mesh);group.add(mesh);
    }
    group.visible=false;
  }
}

function resetSpotTextures(){
  for(const view of ['left','right','rear'])for(const m of viewSpotMeshes[view]){if(m.material?.userData?.normalMap){m.material.map=m.material.userData.normalMap;m.material.needsUpdate=true}}
}
function selectSpot(spot){
  selectedId=spot.id;resetSpotTextures();
  const mesh=viewSpotMeshes[spot.view].find(m=>m.userData.spot?.id===spot.id);if(mesh?.material?.userData?.selectedMap){mesh.material.map=mesh.material.userData.selectedMap;mesh.material.needsUpdate=true}
  panelTier.textContent=`${spot.tier} · ${spot.view.toUpperCase()} · ${spot.id}`;panelName.textContent=`Spot ${spot.id}`;panelPrice.textContent=money(spot.price);
  panelCopy.textContent=`${spot.copy} The position follows the actual GLB body surface for the 12-month campaign.`;
  panelClaim.textContent=`Reserve ${spot.id} — ${money(spot.price)}`;panelClaim.href=`https://x.com/THEFOFOSHOW?brandmyvan=${encodeURIComponent(spot.id)}`;panel.hidden=false;
  if(viewerTip)viewerTip.style.display='none';
}
function closePanel(){selectedId=null;panel.hidden=true;resetSpotTextures();if(viewerTip&&currentView!=='free')viewerTip.style.display='block'}

function setPointer(e){const r=canvas.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1}
function interactiveMeshes(){return currentView==='free'?[]:(viewSpotMeshes[currentView]||[])}
canvas.addEventListener('pointermove',e=>{
  const meshes=interactiveMeshes();if(!meshes.length){canvas.style.cursor='';return}setPointer(e);clickRaycaster.setFromCamera(pointer,camera);canvas.style.cursor=clickRaycaster.intersectObjects(meshes,false).length?'pointer':'';
});
canvas.addEventListener('click',e=>{
  const meshes=interactiveMeshes();if(!meshes.length)return;setPointer(e);clickRaycaster.setFromCamera(pointer,camera);const hits=clickRaycaster.intersectObjects(meshes,false);if(hits.length)selectSpot(hits[0].object.userData.spot);
});

panelClose?.addEventListener('click',closePanel);
viewButtons.forEach(btn=>btn.addEventListener('click',()=>btn.dataset.view==='free'?setFreeView():setFixedView(btn.dataset.view)));
resetBtn?.addEventListener('click',()=>currentView==='free'?setFreeView():setFixedView(currentView));
window.addEventListener('resize',()=>{if(modelBox&&currentView!=='free')setFixedView(currentView,true)});

renderer.setAnimationLoop(()=>{resize();updateTween();controls.update();renderer.render(scene,camera)});

async function boot(){
  try{
    const gltf=await new GLTFLoader().loadAsync('./van-realistic.glb');model=gltf.scene;
    const rawBox=new THREE.Box3().setFromObject(model),rawSize=rawBox.getSize(new THREE.Vector3()),rawCenter=rawBox.getCenter(new THREE.Vector3());
    const scale=4.75/Math.max(rawSize.x,rawSize.y,rawSize.z),origin=new THREE.Vector3(rawCenter.x,rawBox.min.y,rawCenter.z);
    model.scale.setScalar(scale);model.position.copy(origin).multiplyScalar(-scale);scene.add(model);scene.updateMatrixWorld(true);
    modelBox=new THREE.Box3().setFromObject(model);const size=modelBox.getSize(new THREE.Vector3());longAxis=size.x>=size.z?'x':'z';wideAxis=longAxis==='x'?'z':'x';
    buildGarage();buildViewGroups();setEnvironmentMode(false);setFixedView('left',true);
  }catch(err){console.error(err);viewLabel.textContent='3D MODEL UNAVAILABLE';zoneLayer.style.display='none'}
}
boot();