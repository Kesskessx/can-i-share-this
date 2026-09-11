import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const canvas = document.getElementById('vanCanvas');
const status = document.getElementById('viewerStatus');
const rotateBtn = document.getElementById('rotateVan');
const resetBtn = document.getElementById('resetVan');
const overlay = document.getElementById('spotOverlay');
const panel = document.getElementById('spotPanel');
const panelTier = document.getElementById('spotPanelTier');
const panelName = document.getElementById('spotPanelName');
const panelPrice = document.getElementById('spotPanelPrice');
const panelCopy = document.getElementById('spotPanelCopy');
const panelClaim = document.getElementById('spotPanelClaim');
const panelClose = document.getElementById('spotPanelClose');

const SPOTS = [
  { id:'S1', tier:'Signature', price:1500, kind:'side', side: 1, u:-0.12, y:.58, copy:'Prime side placement. One of only two founding sponsor positions.' },
  { id:'S2', tier:'Signature', price:1500, kind:'side', side:-1, u:-0.12, y:.58, copy:'Prime side placement. One of only two founding sponsor positions.' },

  { id:'L1', tier:'Large', price:750, kind:'side', side: 1, u:.42, y:.56, copy:'Large side placement with strong visibility on the road and while parked.' },
  { id:'L2', tier:'Large', price:750, kind:'side', side:-1, u:.42, y:.56, copy:'Large side placement with strong visibility on the road and while parked.' },
  { id:'L3', tier:'Large', price:750, kind:'side', side: 1, u:-.52, y:.54, copy:'Large side placement with strong visibility on the road and while parked.' },
  { id:'L4', tier:'Large', price:750, kind:'side', side:-1, u:-.52, y:.54, copy:'Large side placement with strong visibility on the road and while parked.' },

  { id:'M1', tier:'Medium', price:400, kind:'side', side: 1, u:.68, y:.49, copy:'Mid-size sponsor position for a clear physical brand presence.' },
  { id:'M2', tier:'Medium', price:400, kind:'side', side:-1, u:.68, y:.49, copy:'Mid-size sponsor position for a clear physical brand presence.' },
  { id:'M3', tier:'Medium', price:400, kind:'side', side: 1, u:-.72, y:.46, copy:'Mid-size sponsor position for a clear physical brand presence.' },
  { id:'M4', tier:'Medium', price:400, kind:'side', side:-1, u:-.72, y:.46, copy:'Mid-size sponsor position for a clear physical brand presence.' },
  { id:'M5', tier:'Medium', price:400, kind:'end', end: 1, v:-.22, y:.50, copy:'Medium end-panel position, visible when traffic approaches the van.' },
  { id:'M6', tier:'Medium', price:400, kind:'end', end:-1, v:.22, y:.50, copy:'Medium end-panel position, visible when traffic approaches the van.' },

  { id:'SM1', tier:'Small', price:200, kind:'side', side: 1, u:.18, y:.76, copy:'Compact 12-month sponsor placement.' },
  { id:'SM2', tier:'Small', price:200, kind:'side', side:-1, u:.18, y:.76, copy:'Compact 12-month sponsor placement.' },
  { id:'SM3', tier:'Small', price:200, kind:'side', side: 1, u:-.34, y:.77, copy:'Compact 12-month sponsor placement.' },
  { id:'SM4', tier:'Small', price:200, kind:'side', side:-1, u:-.34, y:.77, copy:'Compact 12-month sponsor placement.' },
  { id:'SM5', tier:'Small', price:200, kind:'end', end: 1, v:.22, y:.72, copy:'Compact end-panel sponsor placement.' },
  { id:'SM6', tier:'Small', price:200, kind:'end', end: 1, v:-.22, y:.72, copy:'Compact end-panel sponsor placement.' },
  { id:'SM7', tier:'Small', price:200, kind:'end', end:-1, v:.22, y:.72, copy:'Compact end-panel sponsor placement.' },
  { id:'SM8', tier:'Small', price:200, kind:'end', end:-1, v:-.22, y:.72, copy:'Compact end-panel sponsor placement.' }
];

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#f5f3ed');

const camera = new THREE.PerspectiveCamera(34, 1, 0.01, 100);
camera.position.set(4.7, 2.35, 5.8);

const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 0.95, 0);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 3.2;
controls.maxDistance = 9;
controls.maxPolarAngle = Math.PI / 2 - 0.02;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.55;

scene.add(new THREE.HemisphereLight(0xffffff, 0xb7b0a4, 3.1));
const key = new THREE.DirectionalLight(0xffffff, 3.2);
key.position.set(4, 7, 5);
scene.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 1.5);
fill.position.set(-5, 3, -4);
scene.add(fill);

const floor = new THREE.Mesh(
  new THREE.CircleGeometry(3.3, 64),
  new THREE.MeshStandardMaterial({ color: 0xe8e4d9, roughness: 1, metalness: 0 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.02;
scene.add(floor);

let hotspotState = [];
let selectedId = null;

function money(value) {
  return `€${value.toLocaleString('en-US')}`;
}

function resetView() {
  camera.position.set(4.7, 2.35, 5.8);
  controls.target.set(0, 0.95, 0);
  controls.update();
}

rotateBtn.addEventListener('click', () => {
  controls.autoRotate = !controls.autoRotate;
  rotateBtn.textContent = controls.autoRotate ? 'Pause rotation' : 'Auto rotate';
});

resetBtn.addEventListener('click', resetView);
controls.addEventListener('start', () => {
  if (controls.autoRotate) {
    controls.autoRotate = false;
    rotateBtn.textContent = 'Auto rotate';
  }
});

panelClose?.addEventListener('click', () => {
  panel.hidden = true;
  selectedId = null;
  hotspotState.forEach(item => item.el.classList.remove('selected'));
});

function selectSpot(spot, el) {
  selectedId = spot.id;
  controls.autoRotate = false;
  rotateBtn.textContent = 'Auto rotate';
  hotspotState.forEach(item => item.el.classList.toggle('selected', item.spot.id === spot.id));
  panelTier.textContent = `${spot.tier} · Spot ${spot.id}`;
  panelName.textContent = `${spot.tier} sponsor spot`;
  panelPrice.textContent = money(spot.price);
  panelCopy.textContent = spot.copy;
  panelClaim.textContent = `Claim spot ${spot.id}`;
  panelClaim.href = `https://x.com/THEFOFOSHOW?brandmyvan=${encodeURIComponent(spot.id)}`;
  panel.hidden = false;
}

function buildHotspots(modelBox) {
  overlay.innerHTML = '';
  hotspotState = [];

  const size = modelBox.getSize(new THREE.Vector3());
  const center = modelBox.getCenter(new THREE.Vector3());
  const longAxis = size.x >= size.z ? 'x' : 'z';
  const wideAxis = longAxis === 'x' ? 'z' : 'x';
  const longSize = size[longAxis];
  const wideSize = size[wideAxis];
  const height = size.y;

  SPOTS.forEach(spot => {
    const pos = center.clone();
    const normal = new THREE.Vector3();

    if (spot.kind === 'side') {
      pos[longAxis] = center[longAxis] + spot.u * longSize * .48;
      pos[wideAxis] = center[wideAxis] + spot.side * (wideSize * .51);
      pos.y = modelBox.min.y + spot.y * height;
      normal[wideAxis] = spot.side;
    } else {
      pos[longAxis] = center[longAxis] + spot.end * (longSize * .505);
      pos[wideAxis] = center[wideAxis] + spot.v * wideSize;
      pos.y = modelBox.min.y + spot.y * height;
      normal[longAxis] = spot.end;
    }

    const el = document.createElement('button');
    el.type = 'button';
    el.className = `van-spot van-spot-${spot.tier.toLowerCase()}`;
    el.innerHTML = `<span>${spot.id}</span><strong>${money(spot.price)}</strong>`;
    el.setAttribute('aria-label', `${spot.tier} spot ${spot.id}, ${money(spot.price)}`);
    el.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      selectSpot(spot, el);
    });
    overlay.appendChild(el);
    hotspotState.push({ spot, el, pos, normal });
  });
}

function updateHotspots() {
  if (!hotspotState.length) return;
  const rect = canvas.getBoundingClientRect();
  const cameraDirection = new THREE.Vector3();

  hotspotState.forEach(item => {
    const toCamera = cameraDirection.copy(camera.position).sub(item.pos).normalize();
    const facingCamera = item.normal.dot(toCamera) > .08;
    const p = item.pos.clone().project(camera);
    const onScreen = p.z > -1 && p.z < 1 && p.x > -1.08 && p.x < 1.08 && p.y > -1.08 && p.y < 1.08;
    const visible = facingCamera && onScreen;

    item.el.style.opacity = visible ? '1' : '0';
    item.el.style.pointerEvents = visible ? 'auto' : 'none';
    item.el.style.transform = `translate(-50%,-50%) translate(${(p.x * .5 + .5) * rect.width}px,${(-p.y * .5 + .5) * rect.height}px)`;
    item.el.style.zIndex = item.spot.id === selectedId ? '12' : '8';
  });
}

function resize() {
  const width = Math.max(1, canvas.clientWidth);
  const height = Math.max(1, canvas.clientHeight);
  const ratio = renderer.getPixelRatio();
  if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
    renderer.setSize(width, height, false);
  }
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

renderer.setAnimationLoop(() => {
  resize();
  controls.update();
  updateHotspots();
  renderer.render(scene, camera);
});

async function boot() {
  try {
    status.textContent = 'Loading the van…';
    const gltf = await new GLTFLoader().loadAsync('./van-realistic.glb', event => {
      if (event.total) status.textContent = `Loading ${Math.round((event.loaded / event.total) * 100)}%`;
    });

    const model = gltf.scene;
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const scale = 4.15 / Math.max(size.x, size.y, size.z);
    const origin = new THREE.Vector3(center.x, box.min.y, center.z);

    model.scale.setScalar(scale);
    model.position.copy(origin).multiplyScalar(-scale);
    scene.add(model);
    scene.updateMatrixWorld(true);

    const worldBox = new THREE.Box3().setFromObject(model);
    buildHotspots(worldBox);
    status.textContent = '20 clickable sponsor spots';
  } catch (error) {
    console.error(error);
    status.textContent = '3D model unavailable';
  }
}

boot();
