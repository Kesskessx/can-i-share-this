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

const SPOTS=window.BMV_CONFIG.spots;

let renderer;
for(const options of [{antialias:false,powerPreference:'default'},{antialias:false,powerPreference:'low-power'}]){
 try{renderer=new THREE.WebGLRenderer({canvas,alpha:true,...options});break;}catch(error){console.warn('3D initialization attempt failed',error);}
}
if(!renderer)throw new Error('WebGL unavailable');
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
const scene=new THREE.Scene();scene.background=new THREE.Color('#f7f6f1');
const camera=new THREE.PerspectiveCamera(29,1,.01,100);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.enablePan=false;controls.autoRotate=false;controls.minPolarAngle=Math.PI*.18;controls.maxPolarAngle=Math.PI*.82;
const hemi=new THREE.HemisphereLight(0xffffff,0xb8b0a2,3.1);scene.add(hemi);
const key=new THREE.DirectionalLight(0xffffff,3.2);key.position.set(5,7,5);scene.add(key);
const fill=new THREE.DirectionalLight(0xffffff,1.3);fill.position.set(-5,3,-4);scene.add(fill);
const floor=new THREE.Mesh(new THREE.CircleGeometry(4.3,72),new THREE.MeshStandardMaterial({color:0xebe7dc,roughness:1,metalness:0}));floor.rotation.x=-Math.PI/2;floor.position.y=-.02;scene.add(floor);

let model=null,modelBox=null,currentView='left',selectedId=null,tween=null,longAxis='x',wideAxis='z',garageGroup=null;
const viewGroups={left:null,right:null,rear:null},viewSpotMeshes={left:[],right:[],rear:[]};
const modelRaycaster=new THREE.Raycaster(),clickRaycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
function money(v){return `€${v.toLocaleString('en-US')}`}
function axisVector(axis,value=1){const v=new THREE.Vector3();v[axis]=value;return v}
function viewConfig(view){if(view==='rear')return{rayAxis:longAxis,hAxis:wideAxis,out:axisVector(longAxis,-1),flipU:longAxis==='z'};if(view==='left')return{rayAxis:wideAxis,hAxis:longAxis,out:axisVector(wideAxis,1),flipU:true};return{rayAxis:wideAxis,hAxis:longAxis,out:axisVector(wideAxis,-1),flipU:false}}
function resize(){const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight),r=renderer.getPixelRatio();if(canvas.width!==Math.round(w*r)||canvas.height!==Math.round(h*r))renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
function fitDistance(view){if(!modelBox)return 6;resize();const size=modelBox.getSize(new THREE.Vector3()),width=view==='rear'?size[wideAxis]:size[longAxis],fov=THREE.MathUtils.degToRad(camera.fov),byHeight=(size.y*.5)/Math.tan(fov*.5),byWidth=(width*.5)/(Math.tan(fov*.5)*Math.max(camera.aspect,.42));return Math.max(byHeight,byWidth)*(view==='rear'?1.24:1.18)}
function cameraPose(view){const center=modelBox.getCenter(new THREE.Vector3()),size=modelBox.getSize(new THREE.Vector3()),d=fitDistance(view),pos=center.clone(),target=center.clone();target.y+=size.y*.015;if(view==='left')pos[wideAxis]+=d;if(view==='right')pos[wideAxis]-=d;if(view==='rear')pos[longAxis]-=d;pos.y+=size.y*.015;return{pos,target}}
function animateCamera(pos,target,duration=380){tween={startPos:camera.position.clone(),startTarget:controls.target.clone(),pos,target,started:performance.now(),duration}}
function updateTween(){if(!tween)return;const t=Math.min(1,(performance.now()-tween.started)/tween.duration),e=1-Math.pow(1-t,3);camera.position.lerpVectors(tween.startPos,tween.pos,e);controls.target.lerpVectors(tween.startTarget,tween.target,e);if(t>=1)tween=null}

function makeGarageSignTexture(){const c=document.createElement('canvas');c.width=1024;c.height=256;const ctx=c.getContext('2d');ctx.fillStyle='#111315';ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle='#dcff29';ctx.font='900 92px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('BRAND MYVAN',512,105);ctx.fillStyle='#fff';ctx.font='700 28px Arial';ctx.fillText('GARAGE · SPONSOR BUILD',512,184);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.needsUpdate=true;return t}
function buildGarage(){
  if(!modelBox||garageGroup)return;const size=modelBox.getSize(new THREE.Vector3()),roomLong=Math.max(size[longAxis]*2.9,14),roomWide=Math.max(size[wideAxis]*5,12.5),roomHeight=Math.max(size.y*2.75,5.4),worldX=longAxis==='x'?roomLong:roomWide,worldZ=longAxis==='z'?roomLong:roomWide,backCoord=wideAxis==='z'?-worldZ/2:-worldX/2,insideBack=backCoord+.10;
  garageGroup=new THREE.Group();garageGroup.name='garage-environment';scene.add(garageGroup);
  const concrete=new THREE.MeshStandardMaterial({color:0x3e4247,roughness:.94,metalness:.02}),wallMat=new THREE.MeshStandardMaterial({color:0x8c9094,roughness:.9,metalness:.01}),darkMat=new THREE.MeshStandardMaterial({color:0x202327,roughness:.8,metalness:.08}),doorMat=new THREE.MeshStandardMaterial({color:0x70757a,roughness:.72,metalness:.18});
  const floorGarage=new THREE.Mesh(new THREE.PlaneGeometry(worldX,worldZ),concrete);floorGarage.rotation.x=-Math.PI/2;floorGarage.position.y=-.035;garageGroup.add(floorGarage);
  const backWall=wideAxis==='z'?new THREE.Mesh(new THREE.BoxGeometry(worldX,roomHeight,.16),wallMat):new THREE.Mesh(new THREE.BoxGeometry(.16,roomHeight,worldZ),wallMat);backWall.position.y=roomHeight/2-.02;backWall.position[wideAxis]=backCoord;garageGroup.add(backWall);
  const sideGeom=longAxis==='x'?new THREE.BoxGeometry(.16,roomHeight,worldZ):new THREE.BoxGeometry(worldX,roomHeight,.16);const sideWall=new THREE.Mesh(sideGeom,wallMat);sideWall.position.y=roomHeight/2-.02;sideWall.position[longAxis]=-roomLong/2;garageGroup.add(sideWall);
  const lowerStripe=wideAxis==='z'?new THREE.Mesh(new THREE.BoxGeometry(worldX*.96,.42,.05),darkMat):new THREE.Mesh(new THREE.BoxGeometry(.05,.42,worldZ*.96),darkMat);lowerStripe.position.y=.45;lowerStripe.position[wideAxis]=insideBack+.02;garageGroup.add(lowerStripe);
  const doorW=Math.min(roomLong*.56,Math.max(size[longAxis]*1.45,5.2)),doorH=Math.min(roomHeight*.64,Math.max(size.y*1.55,3.6)),panelCount=6,panelH=doorH/panelCount;
  for(let i=0;i<panelCount;i++){const panel=wideAxis==='z'?new THREE.Mesh(new THREE.BoxGeometry(doorW,panelH-.025,.07),doorMat):new THREE.Mesh(new THREE.BoxGeometry(.07,panelH-.025,doorW),doorMat);panel.position.y=.12+panelH*(i+.5);panel.position[wideAxis]=insideBack+.04;garageGroup.add(panel)}
  const signMesh=new THREE.Mesh(new THREE.PlaneGeometry(Math.min(4.2,roomLong*.42),1),new THREE.MeshBasicMaterial({map:makeGarageSignTexture(),toneMapped:false}));signMesh.position.y=Math.min(roomHeight-.8,doorH+1.05);signMesh.position[wideAxis]=insideBack+.09;if(wideAxis==='x')signMesh.rotation.y=Math.PI/2;garageGroup.add(signMesh);
  const beamMat=new THREE.MeshStandardMaterial({color:0x2b2e32,roughness:.7,metalness:.35}),lightMat=new THREE.MeshBasicMaterial({color:0xf7fbff,toneMapped:false}),barLength=Math.min(roomLong*.48,5.8);
  for(const w of [-roomWide*.18,roomWide*.18]){const beam=longAxis==='x'?new THREE.Mesh(new THREE.BoxGeometry(barLength,.10,.20),beamMat):new THREE.Mesh(new THREE.BoxGeometry(.20,.10,barLength),beamMat);beam.position.y=roomHeight-.52;beam.position[wideAxis]=w;garageGroup.add(beam);const glow=longAxis==='x'?new THREE.Mesh(new THREE.BoxGeometry(barLength*.92,.035,.12),lightMat):new THREE.Mesh(new THREE.BoxGeometry(.12,.035,barLength*.92),lightMat);glow.position.y=roomHeight-.58;glow.position[wideAxis]=w;garageGroup.add(glow);const lamp=new THREE.PointLight(0xeef6ff,22,roomWide*1.45,2);lamp.position.y=roomHeight-.72;lamp.position[wideAxis]=w;garageGroup.add(lamp)}
  const lineMat=new THREE.MeshBasicMaterial({color:0xc9bd70,toneMapped:false});for(const sign of[-1,1]){const line=longAxis==='x'?new THREE.Mesh(new THREE.BoxGeometry(roomLong*.45,.012,.035),lineMat):new THREE.Mesh(new THREE.BoxGeometry(.035,.012,roomLong*.45),lineMat);line.position.y=.006;line.position[wideAxis]=sign*Math.max(size[wideAxis]*.72,.9);garageGroup.add(line)}
  const shadow=new THREE.Mesh(new THREE.CircleGeometry(1,72),new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.23,depthWrite:false}));shadow.rotation.x=-Math.PI/2;shadow.position.y=.008;shadow.scale.set(Math.max(size.x*.58,1.4),Math.max(size.z*.72,.8),1);garageGroup.add(shadow);garageGroup.visible=false;
}
function setEnvironmentMode(garage){if(garageGroup)garageGroup.visible=garage;floor.visible=!garage;scene.background.set(garage?0x1b1e22:0xf7f6f1);hemi.intensity=garage?1.45:3.1;key.intensity=garage?3.8:3.2;fill.intensity=garage?1.8:1.3;renderer.toneMappingExposure=garage?1.08:1.15}
function setGroupVisibility(view){for(const k of['left','right','rear'])if(viewGroups[k])viewGroups[k].visible=view==='free'||k===view}
function setFixedView(view,instant=false,keepSelection=false){if(!modelBox)return;currentView=view;setEnvironmentMode(false);controls.enableRotate=false;controls.enableZoom=false;controls.enablePan=false;controls.autoRotate=false;freeMessage.style.display='none';zoneLayer.style.display='none';setGroupVisibility(view);const pose=cameraPose(view);if(instant){camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update()}else animateCamera(pose.pos,pose.target);viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view===view));const count=SPOTS.filter(s=>s.view===view).length;viewLabel.textContent=`${view.toUpperCase()} · ${count} AVAILABLE SPOTS`;viewLabel.style.display='block';if(viewerTip){viewerTip.textContent='Tap a spot to see price';viewerTip.style.display='block'}stopRotation();if(!keepSelection)closePanel()}
function setFreeView(keepSelection=false){currentView='free';setEnvironmentMode(true);zoneLayer.style.display='none';setGroupVisibility('free');viewLabel.style.display='none';freeMessage.style.display='block';if(viewerTip)viewerTip.style.display='none';controls.enableRotate=true;controls.enableZoom=true;controls.enablePan=false;const c=modelBox.getCenter(new THREE.Vector3()),size=modelBox.getSize(new THREE.Vector3()),d=fitDistance('left')*.90,p=c.clone();p[wideAxis]+=d*.66;p[longAxis]+=d*.66;p.y+=size.y*.20;controls.minDistance=d*.50;controls.maxDistance=d*1.10;animateCamera(p,c,460);viewButtons.forEach(b=>b.classList.toggle('active',b.dataset.view==='free'));if(!keepSelection)closePanel()}

function sampleSurface(view,u,v,{strict=true}={}){if(!model||!modelBox)return null;const cfg=viewConfig(view),size=modelBox.getSize(new THREE.Vector3()),origin=modelBox.getCenter(new THREE.Vector3());origin[cfg.hAxis]=modelBox.min[cfg.hAxis]+u*size[cfg.hAxis];origin.y=modelBox.min.y+v*size.y;const margin=Math.max(.35,size[cfg.rayAxis]*.12);origin[cfg.rayAxis]=cfg.out[cfg.rayAxis]>0?modelBox.max[cfg.rayAxis]+margin:modelBox.min[cfg.rayAxis]-margin;const dir=cfg.out.clone().multiplyScalar(-1);modelRaycaster.set(origin,dir);modelRaycaster.far=size[cfg.rayAxis]*1.6;const hits=modelRaycaster.intersectObject(model,true);for(const hit of hits){if(!hit.face)continue;const n=hit.face.normal.clone().applyMatrix3(new THREE.Matrix3().getNormalMatrix(hit.object.matrixWorld)).normalize(),facing=n.dot(cfg.out);// Only the first visible surface can receive a sticker; never project through glass or trim.
if(strict&&(facing<.62||hit.object.material?.name!=='Textures_Body_1'))return null;return{point:hit.point.clone(),normal:n,distance:hit.distance,object:hit.object}}return null}
// Contours are inset from the stamped cargo recesses visible in this GLB.
// Coordinates stay in panel space so the artwork itself is never skewed.
function panelOutline(spot){
  if(spot.edge==='cargo-front')return [[0,0],[.87,0],[.95,.06],[1,.20],[1,.93],[.94,1],[0,1]];
  if(spot.edge==='cargo-rear')return [[0,0],[1,0],[1,1],[.14,1],[0,.88]];
  return [[0,0],[1,0],[1,1],[0,1]];
}
// Clip the ORIGINAL body triangles, retaining their positions and smooth normals.
// A sampled grid can bridge grooves or sink inside curved panels between samples.
function createSurfacePatch(view,{u0,u1,v0,v1,material,outline=[[0,0],[1,0],[1,1],[0,1]],offset=.0005}){
  const cfg=viewConfig(view),size=modelBox.getSize(new THREE.Vector3());
  const horizontalMin=modelBox.min[cfg.hAxis]+u0*size[cfg.hAxis];
  const horizontalMax=modelBox.min[cfg.hAxis]+u1*size[cfg.hAxis];
  const bottom=modelBox.min.y+v0*size.y,top=modelBox.min.y+v1*size.y;
  const surfaceDepths=[];
  for(let y=0;y<=4;y++)for(let x=0;x<=4;x++){
    const sample=sampleSurface(view,u0+(u1-u0)*x/4,v0+(v1-v0)*y/4);
    if(sample)surfaceDepths.push(sample.point[cfg.rayAxis]);
  }
  if(!surfaceDepths.length)throw new Error(`No printable body surface for ${view}`);
  const planes=[
    [cfg.hAxis,horizontalMin,1],[cfg.hAxis,horizontalMax,-1],
    ['y',bottom,1],['y',top,-1],
    [cfg.rayAxis,Math.min(...surfaceDepths)-.008,1],
    [cfg.rayAxis,Math.max(...surfaceDepths)+.008,-1]
  ];
  function clipPolygon(vertices,signedDistance){
    const result=[];
    for(let i=0;i<vertices.length;i++){
      const a=vertices[i],b=vertices[(i+1)%vertices.length];
      const da=signedDistance(a.p),db=signedDistance(b.p);
      if(da>=0)result.push(a);
      if((da>=0)!==(db>=0)){
        const t=da/(da-db);
        result.push({p:a.p.clone().lerp(b.p,t),n:a.n.clone().lerp(b.n,t).normalize()});
      }
    }
    return result;
  }
  const positions=[],normals=[],uvs=[];
  const emit=vertex=>{
    const p=vertex.p.clone().addScaledVector(vertex.n,offset);
    positions.push(p.x,p.y,p.z);normals.push(vertex.n.x,vertex.n.y,vertex.n.z);
    const u=(vertex.p[cfg.hAxis]-horizontalMin)/(horizontalMax-horizontalMin);
    uvs.push(cfg.flipU?1-u:u,(vertex.p.y-bottom)/(top-bottom));
  };
  model.traverse(object=>{
    if(!object.isMesh||object.material?.name!=='Textures_Body_1')return;
    const geometry=object.geometry,position=geometry.attributes.position,normal=geometry.attributes.normal,index=geometry.index;
    const normalMatrix=new THREE.Matrix3().getNormalMatrix(object.matrixWorld);
    for(let i=0,count=index?index.count:position.count;i<count;i+=3){
      let polygon=[];
      for(let j=0;j<3;j++){
        const k=index?index.getX(i+j):i+j;
        polygon.push({p:new THREE.Vector3().fromBufferAttribute(position,k).applyMatrix4(object.matrixWorld),n:new THREE.Vector3().fromBufferAttribute(normal,k).applyMatrix3(normalMatrix).normalize()});
      }
      const faceNormal=new THREE.Vector3().subVectors(polygon[1].p,polygon[0].p).cross(new THREE.Vector3().subVectors(polygon[2].p,polygon[0].p)).normalize();
      if(faceNormal.dot(cfg.out)<.25)continue;
      for(const [axis,limit,sign] of planes){polygon=clipPolygon(polygon,p=>(p[axis]-limit)*sign);if(polygon.length<3)break;}
      for(let edge=0;edge<outline.length&&polygon.length>=3;edge++){
        const a=outline[edge],b=outline[(edge+1)%outline.length];
        polygon=clipPolygon(polygon,p=>{
          const u=(p[cfg.hAxis]-horizontalMin)/(horizontalMax-horizontalMin),v=(p.y-bottom)/(top-bottom);
          return (b[0]-a[0])*(v-a[1])-(b[1]-a[1])*(u-a[0]);
        });
      }
      if(polygon.length<3)continue;
      for(let j=1;j<polygon.length-1;j++){
        emit(polygon[0]);emit(polygon[j]);emit(polygon[j+1]);
      }
    }
  });
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
  geometry.computeBoundingSphere();
  return new THREE.Mesh(geometry,material);
}
function makeSpotTexture(spot,selected=false){
  // Match the texture to the physical patch so labels keep their proportions.
  const size=modelBox.getSize(new THREE.Vector3()),cfg=viewConfig(spot.view);
  const aspect=(spot.uw*size[cfg.hAxis])/(spot.vh*size.y);
  const c=document.createElement('canvas');c.width=1024;c.height=Math.round(1024/aspect);
  const ctx=c.getContext('2d'),w=c.width,h=c.height,pad=Math.min(w,h)*.055;
  const contour=panelOutline(spot).map(([u,v])=>[pad+(cfg.flipU?1-u:u)*(w-2*pad),pad+(1-v)*(h-2*pad)]);
  // Round only the print corners; the silhouette remains parallel to the recess.
  ctx.beginPath();
  for(let i=0;i<contour.length;i++){
    const prev=contour[(i+contour.length-1)%contour.length],point=contour[i],next=contour[(i+1)%contour.length];
    const r=pad*.45,d1=Math.hypot(prev[0]-point[0],prev[1]-point[1]),d2=Math.hypot(next[0]-point[0],next[1]-point[1]);
    const before=[point[0]+(prev[0]-point[0])*r/d1,point[1]+(prev[1]-point[1])*r/d1];
    const after=[point[0]+(next[0]-point[0])*r/d2,point[1]+(next[1]-point[1])*r/d2];
    if(i===0)ctx.moveTo(...before);else ctx.lineTo(...before);
    ctx.quadraticCurveTo(point[0],point[1],after[0],after[1]);
  }
  ctx.closePath();
  ctx.fillStyle=selected?'#dcff29':'#f8f8f5';ctx.fill();
  ctx.strokeStyle=selected?'#111111':'#6f7476';ctx.lineWidth=Math.min(w,h)*.012;ctx.stroke();
  ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#111111';
  const fontSize=Math.min(h*.29,w*.21);
  ctx.font=`900 ${fontSize}px Arial`;ctx.fillText(spot.id,w/2,h*.34);
  ctx.font=`700 ${fontSize*.86}px Arial`;ctx.fillText(money(spot.price),w/2,h*.70);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());t.needsUpdate=true;return t;
}
function buildSpotMesh(spot){
  // Satin vinyl: it receives the same light as the paint instead of glowing flat.
  const material=new THREE.MeshStandardMaterial({map:makeSpotTexture(spot,false),roughness:.62,metalness:0,transparent:true,alphaTest:.08,depthWrite:false,side:THREE.FrontSide,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
  material.userData.normalMap=material.map;material.userData.selectedMap=makeSpotTexture(spot,true);
  const mesh=createSurfacePatch(spot.view,{u0:spot.u-spot.uw/2,u1:spot.u+spot.uw/2,v0:spot.v-spot.vh/2,v1:spot.v+spot.vh/2,material,outline:panelOutline(spot)});
  mesh.name=`spot-${spot.id}`;mesh.userData.spot=spot;mesh.renderOrder=30;return mesh;
}
function buildViewGroups(){for(const view of['left','right','rear']){const group=new THREE.Group();group.name=`${view}-sponsor-spots`;scene.add(group);viewGroups[view]=group;viewSpotMeshes[view]=[];for(const spot of SPOTS.filter(s=>s.view===view)){const mesh=buildSpotMesh(spot);viewSpotMeshes[view].push(mesh);group.add(mesh)}group.visible=false}}
function resetSpotTextures(){for(const view of['left','right','rear'])for(const m of viewSpotMeshes[view])if(m.material?.userData?.normalMap){m.material.map=m.userData.logoTexture||m.material.userData.normalMap;m.material.needsUpdate=true}}
function stopRotation(){controls.autoRotate=false;window.dispatchEvent(new CustomEvent('bmv:rotation',{detail:false}));}
function selectSpot(spot){if(window.BMV_CONFIRMED?.has(spot.id))return;
  stopRotation();selectedId=spot.id;resetSpotTextures();
  const mesh=viewSpotMeshes[spot.view].find(m=>m.userData.spot?.id===spot.id);
  if(mesh&&!mesh.userData.logoTexture){mesh.material.map=mesh.material.userData.selectedMap;mesh.material.needsUpdate=true;}
  window.dispatchEvent(new CustomEvent('bmv:spot',{detail:spot.id}));
  if(viewerTip)viewerTip.style.display='none';
}
function closePanel(){selectedId=null;resetSpotTextures();window.dispatchEvent(new CustomEvent('bmv:closed'));if(viewerTip&&currentView!=='free')viewerTip.style.display='block'}
window.addEventListener('bmv:select',e=>{
  const spot=SPOTS.find(s=>s.id===e.detail);if(!spot||!modelBox)return;
  setFixedView(spot.view,false,true);selectSpot(spot);
});
window.addEventListener('bmv:deselect',()=>{selectedId=null;resetSpotTextures();stopRotation();});
window.addEventListener('bmv:pause',stopRotation);
window.addEventListener('bmv:face',e=>{const spot=SPOTS.find(s=>s.id===e.detail);if(spot&&modelBox)setFixedView(spot.view,false,true);});
window.addEventListener('bmv:inspect',e=>{
  if(!modelBox)return;if(controls.autoRotate){stopRotation();return;}
  const spot=SPOTS.find(s=>s.id===e.detail);if(!spot)return;
  if(currentView!=='free'){
    setFreeView(true);const cfg=viewConfig(spot.view),center=modelBox.getCenter(new THREE.Vector3()),d=fitDistance(spot.view);
    const position=center.clone().addScaledVector(cfg.out,d*.96);position[cfg.hAxis]+=d*.18;position.y+=modelBox.getSize(new THREE.Vector3()).y*.10;
    animateCamera(position,center,400);
  }
  controls.autoRotate=true;controls.autoRotateSpeed=.6;window.dispatchEvent(new CustomEvent('bmv:rotation',{detail:true}));
});
window.addEventListener('bmv:artwork',e=>{
  const {id,canvas:art,hasLogo}=e.detail,spot=SPOTS.find(s=>s.id===id);if(!spot)return;
  const mesh=viewSpotMeshes[spot.view].find(m=>m.userData.spot.id===id);if(!mesh)return;
  if(hasLogo){if(!mesh.userData.logoTexture)mesh.userData.logoTexture=new THREE.CanvasTexture(art);
    const texture=mesh.userData.logoTexture;texture.image=art;texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());texture.needsUpdate=true;mesh.material.map=texture;
  }else{mesh.userData.logoTexture?.dispose();delete mesh.userData.logoTexture;mesh.material.map=selectedId===id?mesh.material.userData.selectedMap:mesh.material.userData.normalMap;}
  mesh.material.needsUpdate=true;
});
controls.addEventListener('start',stopRotation);
function setPointer(e){const r=canvas.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1}
function interactiveMeshes(){return currentView==='free'?Object.values(viewSpotMeshes).flat():viewSpotMeshes[currentView]||[]}
function pickSpot(e){
  if(tween)return null;
  setPointer(e);clickRaycaster.setFromCamera(pointer,camera);
  const hit=clickRaycaster.intersectObjects(interactiveMeshes(),false)[0];
  if(!hit)return null;
  const bodyHit=clickRaycaster.intersectObject(model,true)[0];
  // The far-side stickers must never be clickable through the van.
  if(bodyHit&&bodyHit.distance+.002<hit.distance)return null;
  return hit.object.userData.spot;
}
let pointerStart=null,pointerDragged=false;
canvas.addEventListener('pointerdown',e=>{pointerStart={x:e.clientX,y:e.clientY};pointerDragged=false});
canvas.addEventListener('pointercancel',()=>{pointerStart=null;pointerDragged=true});
canvas.addEventListener('pointermove',e=>{
  if(pointerStart&&e.buttons&&Math.hypot(e.clientX-pointerStart.x,e.clientY-pointerStart.y)>5)pointerDragged=true;
  canvas.style.cursor=pickSpot(e)?'pointer':currentView==='free'?'grab':'';
});
canvas.addEventListener('click',e=>{
  if(pointerDragged){pointerStart=null;return;}
  const spot=pickSpot(e);if(spot)selectSpot(spot);pointerStart=null;
});
viewButtons.forEach(btn=>btn.addEventListener('click',()=>btn.dataset.view==='free'?setFreeView():setFixedView(btn.dataset.view)));resetBtn?.addEventListener('click',()=>currentView==='free'?setFreeView():setFixedView(currentView));window.addEventListener('resize',()=>{if(modelBox&&currentView!=='free')setFixedView(currentView,true,true)});
const frameClock=new THREE.Clock();renderer.setAnimationLoop(()=>{const delta=Math.min(frameClock.getDelta(),.1);resize();updateTween();controls.update(delta);renderer.render(scene,camera)});
async function boot(){try{const gltf=await new GLTFLoader().loadAsync('./van-realistic.glb');model=gltf.scene;const rawBox=new THREE.Box3().setFromObject(model),rawSize=rawBox.getSize(new THREE.Vector3()),rawCenter=rawBox.getCenter(new THREE.Vector3()),scale=4.75/Math.max(rawSize.x,rawSize.y,rawSize.z),origin=new THREE.Vector3(rawCenter.x,rawBox.min.y,rawCenter.z);model.scale.setScalar(scale);model.position.copy(origin).multiplyScalar(-scale);scene.add(model);scene.updateMatrixWorld(true);modelBox=new THREE.Box3().setFromObject(model);const size=modelBox.getSize(new THREE.Vector3());longAxis=size.x>=size.z?'x':'z';wideAxis=longAxis==='x'?'z':'x';buildGarage();buildViewGroups();setEnvironmentMode(false);setFixedView('left',true,true);window.dispatchEvent(new CustomEvent('bmv:ready'));}catch(err){console.error(err);viewLabel.textContent='3D MODEL UNAVAILABLE';zoneLayer.style.display='none';throw err}}
await boot();