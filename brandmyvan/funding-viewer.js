import * as THREE from 'three';
import { OrbitControls } from './vendor/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from './vendor/examples/jsm/loaders/GLTFLoader.js';

const canvas = document.getElementById('vanCanvas');
const status = document.getElementById('viewerStatus');
const rotateBtn = document.getElementById('rotateVan');
const resetBtn = document.getElementById('resetVan');

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#f3f1ea');

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
    status.textContent = 'Drag to rotate';
  } catch (error) {
    console.error(error);
    status.textContent = '3D model unavailable';
  }
}

boot();
