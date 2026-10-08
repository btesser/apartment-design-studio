import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { acceleratedRaycast, computeBoundsTree } from './vendor/three-mesh-bvh.module.js';
THREE.Mesh.prototype.raycast = acceleratedRaycast;
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;

const $ = (id) => document.getElementById(id);
const app = $('app'), viewport = $('viewport');
const config = window.APARTMENT_EMBED?.config || await fetch('./assets/config.json').then(r => { if (!r.ok) throw new Error('Model configuration is missing.'); return r.json(); });
const scene = new THREE.Scene();
scene.background = new THREE.Color('#e8eae2');
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, .045, 180);
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.setSize(innerWidth, innerHeight);
function updateViewOffset() { if(innerWidth>780&&mode!=='walk')camera.setViewOffset(innerWidth,innerHeight,-145,0,innerWidth,innerHeight);else camera.clearViewOffset(); }
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
renderer.localClippingEnabled = true;
viewport.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
let needsRender=true;
controls.addEventListener('change',()=>needsRender=true);
controls.enableDamping = true;
controls.dampingFactor = .10;
controls.minDistance = .45;
controls.maxDistance = 38;
controls.maxPolarAngle = Math.PI * .495;
scene.add(new THREE.HemisphereLight(0xffffff, 0xaba997, 2.0));
const keyLight = new THREE.DirectionalLight(0xfffbec, 2.4); keyLight.position.set(4, 14, 7); scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0xe3edff, .8); fillLight.position.set(-8, 6, -6); scene.add(fillLight);
const grids = new THREE.Group(); scene.add(grids); grids.visible = false;
const layerKeys=['scan','architecture','repairs','furniture','fixtures','dresser','utilities','entry'];
const layers = Object.fromEntries(layerKeys.map(key => { const g = new THREE.Group(); g.name = key; g.visible=$(key).checked;scene.add(g); return [key,g]; }));
const assetStatus = {}, raycaster = new THREE.Raycaster(), temp = new THREE.Vector3(), forward = new THREE.Vector3();
const clock = new THREE.Clock();
let activeFloor = config.floorOrder?.[0] || 'upper', activeRoom = '', mode = 'orbit';
let yaw = 0, pitch = 0, pointerStart = null, toastTimeout;
let cutawayHeight = Number($('cutaway').value);
let stairTransit = false;
let modelBounds = new THREE.Box3(), movement = new Set(), lookDragging = false, settled = false;
const eyeHeight = () => config.floors[activeFloor === 'all' ? 'upper' : activeFloor].eyeHeight || 1.58;
const floorInfo = () => config.floors[activeFloor === 'all' ? 'upper' : activeFloor];
const currentClipPlanes = [];
const materials = new Set();

function toast(text) { $('toast').textContent = text; $('toast').style.opacity = 1; clearTimeout(toastTimeout); toastTimeout = setTimeout(() => $('toast').style.opacity = 0, 4000); }
function prepareMaterial(material, key) {
  if (materials.has(material)) return;
  materials.add(material);
  material.side = THREE.DoubleSide;
  material.clippingPlanes = currentClipPlanes;
  material.clipIntersection = false;
  material.userData.originalColor = material.color?.clone();
  material.userData.originalEmissive = material.emissive?.clone();
  material.userData.originalEmissiveIntensity = material.emissiveIntensity;
  material.userData.layer = key;
  if (key === 'scan' && material.map) {
    // Polycam textures carry recorded illumination; use a little self-lighting without changing the mesh.
    if (material.emissive) { material.emissiveMap = material.map; material.emissive.set(0xffffff); material.emissiveIntensity = .15; }
    material.roughness = .92;
  }
}
async function loadLayer(key) {
  const path = config.assets?.[key];
  if (!path) { assetStatus[key] = 'absent'; return; }
  try {
    const embedded = window.APARTMENT_EMBED?.assets?.[key];
    if (window.APARTMENT_EMBED && !embedded) throw new Error('Layer is not included in this build.');
    if (!embedded) { const response = await fetch(`./assets/${path}`, {method:'HEAD'}); if (!response.ok) throw new Error(`HTTP ${response.status}`); }
    const loader = new GLTFLoader();
    const gltf = embedded ? await loader.parseAsync(Uint8Array.from(atob(embedded),character=>character.charCodeAt(0)).buffer,'') : await loader.loadAsync(`./assets/${path}`, event => {
      if (key === 'scan' && event.total) $('load-detail').textContent = `Loading the original scan · ${Math.round(event.loaded / event.total * 100)}%`;
    });
    gltf.scene.updateMatrixWorld(true);
    gltf.scene.traverse(object => {
      if (!object.isMesh) return;
      object.frustumCulled = true;
      if(object.geometry.attributes.position && !object.geometry.boundsTree)object.geometry.computeBoundsTree();
      for (const material of [object.material].flat()) prepareMaterial(material, key);
      object.userData.layer = key;
    });
    layers[key].add(gltf.scene);
    assetStatus[key] = 'loaded';
    if (key === 'scan') modelBounds.setFromObject(gltf.scene);
  } catch (error) {
    assetStatus[key] = key === 'scan' ? 'error' : 'absent';
    console[key === 'scan' ? 'error' : 'info'](`${key} layer: ${error.message}`);
    $(`${key}`).checked = false;
    $(`${key}`).disabled = true;
    layers[key].visible = false;
    if (key === 'scan') throw error;
  }
}
function updateClipping() {
  needsRender=true;
  currentClipPlanes.length = 0;
  if (activeFloor !== 'all' && !(mode==='walk'&&stairTransit)) {
    const f = floorInfo();
    currentClipPlanes.push(new THREE.Plane(new THREE.Vector3(0, 1, 0), -(f.height - .14)));
    const top = mode === 'orbit' ? f.height + cutawayHeight : (f.maxCeiling || f.ceiling) + .025;
    currentClipPlanes.push(new THREE.Plane(new THREE.Vector3(0, -1, 0), top));
  }
  for (const material of materials) material.needsUpdate = true;
  grids.children.forEach(grid => grid.visible = activeFloor === 'all' || grid.userData.floor === activeFloor);
}
function createGrids() {
  for (const [id,floor] of Object.entries(config.floors)) {
    const grid = new THREE.GridHelper(22,22,0x718770,0xb9c4af);
    grid.position.set(0,floor.height+.025,0);
    grid.material.transparent=true; grid.material.opacity=.36; grid.userData.floor=id;
    grids.add(grid);
  }
}
function resetOverview() {
  activeRoom = ''; $('room').value = '';
  if (mode === 'walk') setMode('orbit');
  const floor = floorInfo(), [x0,x1,z0,z1] = floor.bounds;
  const x=(x0+x1)/2,z=(z0+z1)/2;
  const height=activeFloor==='all' ? .9 : floor.height+.5;
  controls.target.set(x,height,z);
  camera.position.set(x+8.0,height+10.3,z-12.9);
  controls.update(); updateAreaInfo();
}
function populateRooms() {
  const rooms = config.rooms.filter(room => activeFloor === 'all' || room.floor === activeFloor);
  $('room').replaceChildren(new Option('Floor overview', ''));
  rooms.forEach(room => $('room').appendChild(new Option(room.label,room.id)));
}
function setFloor(id, reset=true) {
  if (id !== 'all' && !config.floors[id]) return;
  if (id === 'all' && mode === 'walk') setMode('orbit');
  activeFloor=id; $('floor').value=id;
  populateRooms(); updateClipping();
  if(reset){
    if(mode==='walk') {activeRoom='';const f=floorInfo();camera.position.fromArray(f.walkStart);orientWalk(new THREE.Vector3().fromArray(f.walkLook));}
    else resetOverview();
  }
  updateAreaInfo();
  if(reset&&mode==='walk')viewport.focus({preventScroll:true});
}
function updateAreaInfo() {
  const room=config.rooms.find(r=>r.id===activeRoom);
  $('area-name').textContent=room?.label || (activeFloor === 'all' ? 'Whole apartment' : floorInfo().label);
  $('area-description').textContent=room?.description || 'Measured room outlines with Amy’s furniture layout. The recorded scan is available for comparison.';
  if(room?.id==='bedroom-flex')$('area-description').textContent+=' Bed-to-dresser clearance is approximately 0.47 m; compare with the dresser toggle below.';
  $('clearance-warning').hidden=room?.id!=='bedroom-flex'||!$('dresser').checked;
  $('room-dimensions').textContent=room?.dimensionsLabel || (room?.width && room?.depth ? `${room.width.toFixed(2)} × ${room.depth.toFixed(2)} m · scan envelope` : '');
  $('map-label').textContent=activeFloor==='all'?'UPSTAIRS PLAN · BOTH FLOORS SHOWN':floorInfo().label.toUpperCase();
}
function orientWalk(target) {
  const direction = new THREE.Vector3().subVectors(target,camera.position).normalize();
  yaw=Math.atan2(-direction.x,-direction.z); pitch=Math.asin(THREE.MathUtils.clamp(direction.y,-1,1));
  pitch=THREE.MathUtils.clamp(pitch,-Math.PI*.46,Math.PI*.46);
  updateWalkRotation();
}
function updateWalkRotation() { camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));needsRender=true; }
function goToRoom(id, walk=mode==='walk') {
  const room=config.rooms.find(r=>r.id===id); if(!room)return;
  if(room.floor!==activeFloor)setFloor(room.floor,false);
  activeRoom=id; $('room').value=id;
  const f=config.floors[room.floor];
  const center=room.center || [0,f.height,0];
  const eye=room.eye || [center[0],f.height+eyeHeight(),center[2]];
  const look=room.look || [center[0],f.height+1.2,center[2]-1.5];
  if(walk) {
    setMode('walk',false); camera.position.fromArray(eye); orientWalk(new THREE.Vector3().fromArray(look));
  } else {
    const orbit=room.orbit || [center[0]+2.8,f.height+4.0,center[2]-3.6];
    camera.position.fromArray(orbit); controls.target.set(center[0],f.height+.6,center[2]); controls.update();
  }
  updateClipping();updateAreaInfo();
  if(walk){$('panel').classList.remove('open');$('panel-toggle').setAttribute('aria-expanded','false');viewport.focus({preventScroll:true});}
}
function setMode(next, position=true) {
  if(next===mode)return;
  mode=next;stairTransit=false;movement.clear();
  camera.fov=next==='walk'?68:50;camera.updateProjectionMatrix();
  if(next==='walk'&&activeFloor==='all')setFloor('upper',false);
  app.classList.toggle('walking',next==='walk');
  if(next==='walk'){$('panel').classList.remove('open');$('panel-toggle').setAttribute('aria-expanded','false');viewport.focus({preventScroll:true});}
  $('orbit-mode').classList.toggle('active',next==='orbit');$('walk-mode').classList.toggle('active',next==='walk');
  controls.enabled=next==='orbit';
  if(next==='walk') {
    if(position) {
      const room=config.rooms.find(r=>r.id===activeRoom);
      const f=floorInfo();
      const eye=room?.eye || f.walkStart || [(f.bounds[0]+f.bounds[1])/2,f.height+eyeHeight(),(f.bounds[2]+f.bounds[3])/2];
      camera.position.fromArray(eye);
      orientWalk(new THREE.Vector3().fromArray(room?.look || f.walkLook || [eye[0],eye[1],eye[2]-2]));
    }
    $('navigation-hint').textContent='Click the view to look · W A S D to walk · Esc releases mouse';
  } else {
    if(document.pointerLockElement)document.exitPointerLock();
    const target=camera.position.clone().add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(3));
    target.y=floorInfo().height+.6;controls.target.copy(target);controls.update();
    $('navigation-hint').textContent='Drag to orbit · scroll to zoom · right-drag to pan';
  }
  updateClipping();
  updateViewOffset();
}
function setLayer(key,visible) {
  needsRender=true;
  layers[key].visible=visible;$(key).checked=visible;
  if(visible&&key==='scan'){layers.architecture.visible=false;$('architecture').checked=false;layers.fixtures.visible=false;$('fixtures').checked=false;}
  if(visible&&key==='architecture'){layers.scan.visible=false;$('scan').checked=false;layers.repairs.visible=false;$('repairs').checked=false;if(assetStatus.fixtures==='loaded'){layers.fixtures.visible=true;$('fixtures').checked=true;}}
  if(key==='dresser'){$('dresser-note').textContent=visible?'Bedroom foot clearance is approximately 0.47 m with Amy’s dresser.':'Dresser omitted for clearance comparison. Amy’s proposal includes it.';updateAreaInfo();}
}
function setHighlight(enabled) {
  needsRender=true;
  for(const material of materials) {
    if(material.userData.layer!=='repairs')continue;
    if(material.color)material.color.copy(enabled?new THREE.Color('#de915b'):material.userData.originalColor);
    if(material.emissive)material.emissive.copy(enabled?new THREE.Color('#753812'):material.userData.originalEmissive);
    material.emissiveIntensity=enabled?.12:material.userData.originalEmissiveIntensity;
  }
}
function insidePolygon(x,z,polygon) {
  let inside=false;
  for(let i=0,j=polygon.length-1;i<polygon.length;j=i++) {
    const [xi,zi]=polygon[i],[xj,zj]=polygon[j];
    if(((zi>z)!==(zj>z))&&(x<(xj-xi)*(z-zi)/(zj-zi)+xi))inside=!inside;
  }
  return inside;
}
function stairProgress(x,z) {
  const s=config.stair;if(!s)return null;
  if(z<s.zBounds[0]||z>s.zBounds[1]||x<Math.min(s.upperX,s.lowerX)-.12||x>Math.max(s.upperX,s.lowerX)+.12)return null;
  return THREE.MathUtils.clamp((s.lowerX-x)/(s.lowerX-s.upperX),0,1);
}
function groundHeight(position) {
  const progress=stairProgress(position.x,position.z);
  if(progress!==null)return config.stair.lowerY+progress*(config.stair.upperY-config.stair.lowerY);
  const room=config.rooms.find(r=>r.floor===activeFloor&&r.floorHeight!=null&&r.polygon&&insidePolygon(position.x,position.z,r.polygon));
  return (layers.scan.visible ? room?.rawFloorHeight : room?.floorHeight) ?? room?.floorHeight ?? floorInfo().height;
}
function canMove(position) {
  const f=floorInfo(), [x0,x1,z0,z1]=f.bounds;
  if(position.x<x0+.12 || position.x>x1-.12 || position.z<z0+.12 || position.z>z1-.12)return false;
  if(stairProgress(position.x,position.z)===null&&f.walkablePolygons?.length&&!f.walkablePolygons.some(p=>insidePolygon(position.x,position.z,p)))return false;
  for(const shape of config.collisions||[]) {
    if(shape.floor!==activeFloor)continue;
    if(shape.polygon && insidePolygon(position.x,position.z,shape.polygon))return false;
    if(shape.bounds) {
      const [a,b,c,d]=shape.bounds,r=.18;
      if(position.x>a-r&&position.x<b+r&&position.z>c-r&&position.z<d+r)return false;
    }
  }
  // A low pair of forward rays catches solid retained walls and furniture proxies.
  const direction=temp.subVectors(position,camera.position);direction.y=0;
  const length=direction.length();if(length<1e-7)return true;direction.normalize();
  const collisionLayers=[layers.architecture,...(layers.scan.visible?[layers.scan]:[]),...(layers.repairs.visible?[layers.repairs]:[]),...(layers.furniture.visible?[layers.furniture]:[]),...(layers.fixtures.visible?[layers.fixtures]:[]),...(layers.dresser.visible?[layers.dresser]:[]),...(layers.entry.visible?[layers.entry]:[])];
  raycaster.firstHitOnly=true;
  for(const offset of [-.65,0]) {
    raycaster.set(new THREE.Vector3(camera.position.x,camera.position.y+offset,camera.position.z),direction);
    raycaster.far=length+.17;raycaster.near=.005;
    const hits=raycaster.intersectObjects(collisionLayers,true).filter(hit=>hit.object.isMesh&&hit.object.visible&&hit.point.y>=f.height+.15&&hit.point.y<=(f.maxCeiling||f.ceiling)-.08);
    if(hits.length)return false;
  }
  return true;
}
function move(dt) {
  if(mode!=='walk')return;
  let dx=0,dz=0;
  if(movement.has('KeyW')||movement.has('ArrowUp')||movement.has('forward'))dz-=1;
  if(movement.has('KeyS')||movement.has('ArrowDown')||movement.has('back'))dz+=1;
  if(movement.has('KeyA')||movement.has('ArrowLeft')||movement.has('left'))dx-=1;
  if(movement.has('KeyD')||movement.has('ArrowRight')||movement.has('right'))dx+=1;
  if(!dx&&!dz)return;
  const speed=(movement.has('ShiftLeft')||movement.has('ShiftRight')?2.1:1.05)*dt/Math.hypot(dx,dz);
  const vx=(Math.cos(yaw)*dx+Math.sin(yaw)*dz)*speed;
  const vz=(-Math.sin(yaw)*dx+Math.cos(yaw)*dz)*speed;
  const proposed=camera.position.clone();proposed.x+=vx;
  if(canMove(proposed))camera.position.x=proposed.x;
  proposed.copy(camera.position);proposed.z+=vz;
  if(canMove(proposed))camera.position.z=proposed.z;
  camera.position.y=groundHeight(camera.position)+eyeHeight();
  needsRender=true;
  const progress=stairProgress(camera.position.x,camera.position.z),wasTransit=stairTransit;
  stairTransit=progress!==null;
  if(stairTransit) {
    if(progress>.97&&activeFloor!=='upper'){setFloor('upper',false);activeRoom='';$('room').value='';updateAreaInfo();}
    if(progress<.03&&activeFloor!=='basement'){setFloor('basement',false);activeRoom='';$('room').value='';updateAreaInfo();}
  }
  if(stairTransit!==wasTransit)updateClipping();
}
const map=$('map'), ctx=map.getContext('2d');let mapTransform;
function drawMap() {
  const f=floorInfo(),[x0,x1,z0,z1]=f.bounds;
  const w=map.width,h=map.height,margin=12;
  const scale=Math.min((w-margin*2)/(x1-x0),(h-margin*2)/(z1-z0));
  const offX=(w-(x1-x0)*scale)/2,offZ=(h-(z1-z0)*scale)/2;
  mapTransform={scale,offX,offZ,x0,z0};
  const p=(x,z)=>[offX+(x-x0)*scale,offZ+(z-z0)*scale];
  ctx.clearRect(0,0,w,h);ctx.fillStyle='#f7f9f4';ctx.fillRect(0,0,w,h);
  ctx.strokeStyle='#e0e6d8';ctx.lineWidth=1;
  for(let x=Math.ceil(x0);x<x1;x++){const [a,b]=p(x,z0),[c,d]=p(x,z1);ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke();}
  for(let z=Math.ceil(z0);z<z1;z++){const [a,b]=p(x0,z),[c,d]=p(x1,z);ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke();}
  const polygonArea=room=>Math.abs((room.polygon||[]).reduce((sum,p,i,list)=>{const next=list[(i+1)%list.length];return sum+p[0]*next[1]-next[0]*p[1]},0));
  const visibleRooms=config.rooms.filter(r=>r.floor===(activeFloor==='all'?'upper':activeFloor)).sort((a,b)=>polygonArea(b)-polygonArea(a));
  visibleRooms.forEach(room=> {
    let polygon=room.polygon;
    if(!polygon&&room.bounds){const[a,b,c,d]=room.bounds;polygon=[[a,c],[b,c],[b,d],[a,d]];}
    if(!polygon)return;
    ctx.beginPath();polygon.forEach(([x,z],i)=>{const[a,b]=p(x,z);i?ctx.lineTo(a,b):ctx.moveTo(a,b)});ctx.closePath();
    ctx.fillStyle=room.id===activeRoom?'#dce8d4':'#e9eee2';ctx.fill();ctx.strokeStyle='#9cad8d';ctx.lineWidth=2;ctx.stroke();
  });
  // Optional polygons show actual furniture footprints and their facing direction.
  (config.furnitureFootprints||[]).filter(item=>item.floor===(activeFloor==='all'?'upper':activeFloor)).forEach(item=>{
    if(!$(item.layer||'furniture').checked)return;
    if(item.id==='bedroom-large-dresser'&&!$('dresser').checked)return;
    const poly=item.polygon;if(!poly)return;ctx.beginPath();poly.forEach(([x,z],i)=>{const[a,b]=p(x,z);i?ctx.lineTo(a,b):ctx.moveTo(a,b)});ctx.closePath();ctx.fillStyle='#b9c7ad';ctx.fill();
    if(item.front&&item.center){const[a,b]=p(item.center[0],item.center[1]),[c,d]=p(item.front[0],item.front[1]);ctx.strokeStyle='#657d5a';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke();}
  });
  visibleRooms.forEach(room=>{
    const center=room.center;if(!center)return;const[a,b]=p(center[0],center[2]);
    ctx.font='14px sans-serif';ctx.textAlign='center';ctx.lineWidth=3;ctx.strokeStyle='#edf2e7';ctx.strokeText(room.shortLabel||room.label,a,b+4);ctx.fillStyle='#5f7357';ctx.fillText(room.shortLabel||room.label,a,b+4);
  });
  const[cx,cz]=p(camera.position.x,camera.position.z);
  camera.getWorldDirection(forward);let angle=Math.atan2(forward.z,forward.x);
  ctx.save();ctx.translate(cx,cz);ctx.rotate(angle);ctx.fillStyle='#c77d58';ctx.beginPath();ctx.moveTo(13,0);ctx.lineTo(-7,-6);ctx.lineTo(-4,0);ctx.lineTo(-7,6);ctx.closePath();ctx.fill();ctx.restore();
  ctx.fillStyle='#bb744d';ctx.beginPath();ctx.arc(cx,cz,3,0,Math.PI*2);ctx.fill();
}

$('floor').addEventListener('change',event=>setFloor(event.target.value));
$('room').addEventListener('change',event=>event.target.value?goToRoom(event.target.value):resetOverview());
$('orbit-mode').addEventListener('click',()=>setMode('orbit'));
$('walk-mode').addEventListener('click',()=>setMode('walk'));
$('enter-walk').addEventListener('click',()=>renderer.domElement.requestPointerLock?.());
$('reset').addEventListener('click',resetOverview);
layerKeys.forEach(key=>$(key).addEventListener('change',event=>setLayer(key,event.target.checked)));
$('highlight').addEventListener('change',event=>{setHighlight(event.target.checked);if(event.target.checked&&assetStatus.repairs==='loaded'){setLayer('scan',true);setLayer('repairs',true);}});
$('grid').addEventListener('change',event=>{grids.visible=event.target.checked;needsRender=true;});
$('cutaway').addEventListener('input',event=>{cutawayHeight=Number(event.target.value);$('cutaway-value').value=`${cutawayHeight.toFixed(1)} m`;updateClipping();});
$('panel-toggle').addEventListener('click',()=>{const expanded=$('panel').classList.toggle('open');$('panel-toggle').setAttribute('aria-expanded',String(expanded));});
$('capture').addEventListener('click',()=>{renderer.render(scene,camera);const a=document.createElement('a');a.download=`apartment-${activeRoom||activeFloor}-${mode}.png`;a.href=renderer.domElement.toDataURL('image/png');a.click();toast('View saved at the model’s current geometry.');});
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);updateViewOffset();needsRender=true;});
document.addEventListener('pointerlockchange',()=>{app.classList.toggle('locked',!!document.pointerLockElement);movement.clear();});
document.addEventListener('mousemove',event=>{if(mode!=='walk'||!document.pointerLockElement)return;yaw-=event.movementX*.002;pitch-=event.movementY*.002;pitch=THREE.MathUtils.clamp(pitch,-Math.PI*.46,Math.PI*.46);updateWalkRotation();});
renderer.domElement.addEventListener('click',()=>{if(mode==='walk'&&!pointerStart&&!matchMedia('(pointer:coarse)').matches)renderer.domElement.requestPointerLock?.();});
renderer.domElement.addEventListener('pointerdown',event=>{if(mode!=='walk'||document.pointerLockElement)return;pointerStart=[event.clientX,event.clientY];lookDragging=false;renderer.domElement.setPointerCapture(event.pointerId);});
renderer.domElement.addEventListener('pointermove',event=>{if(mode!=='walk'||!pointerStart||document.pointerLockElement)return;const dx=event.clientX-pointerStart[0],dy=event.clientY-pointerStart[1];if(Math.abs(dx)+Math.abs(dy)>1)lookDragging=true;yaw-=dx*.003;pitch-=dy*.003;pitch=THREE.MathUtils.clamp(pitch,-Math.PI*.46,Math.PI*.46);updateWalkRotation();pointerStart=[event.clientX,event.clientY];});
renderer.domElement.addEventListener('pointerup',()=>{pointerStart=null;});
const movementKeys=['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowLeft','ArrowDown','ArrowRight','ShiftLeft','ShiftRight'];
document.addEventListener('keydown',event=>{if(mode!=='walk'||(!document.pointerLockElement&&event.target.closest('select,input')))return;if(movementKeys.includes(event.code)){movement.add(event.code);event.preventDefault();}});
document.addEventListener('keyup',event=>movement.delete(event.code));
window.addEventListener('blur',()=>movement.clear());
document.querySelectorAll('[data-move]').forEach(button=>{button.addEventListener('pointerdown',event=>{event.preventDefault();movement.add(button.dataset.move);button.setPointerCapture(event.pointerId);});['pointerup','pointercancel','lostpointercapture'].forEach(type=>button.addEventListener(type,()=>movement.delete(button.dataset.move)));});
map.addEventListener('click',event=>{if(!mapTransform)return;if(activeFloor==='all')setFloor('upper',false);const rect=map.getBoundingClientRect();const x=(event.clientX-rect.left)/rect.width*map.width,z=(event.clientY-rect.top)/rect.height*map.height;const t=mapTransform;const worldX=(x-t.offX)/t.scale+t.x0,worldZ=(z-t.offZ)/t.scale+t.z0;const room=config.rooms.find(r=>r.floor===activeFloor&&r.polygon&&insidePolygon(worldX,worldZ,r.polygon));if(room){goToRoom(room.id);return;}if(mode!=='walk'){toast('Choose a room to move to its verified viewpoint.');return;}const next=new THREE.Vector3(worldX,floorInfo().height+eyeHeight(),worldZ);if(canMove(next)){camera.position.copy(next);activeRoom='';$('room').value='';updateAreaInfo();}});

try {
  await Promise.all(layerKeys.map(loadLayer));
  if(assetStatus.architecture!=='loaded')setLayer('scan',true);
  createGrids();populateRooms();updateClipping();resetOverview();updateViewOffset();
  $('load-detail').textContent='Preparing the walk-through…';
  const visibility=Object.fromEntries(layerKeys.map(key=>[key,layers[key].visible]));
  layerKeys.forEach(key=>layers[key].visible=assetStatus[key]==='loaded');
  await renderer.compileAsync(scene,camera);
  layerKeys.forEach(key=>layers[key].visible=visibility[key]);
  const details=[assetStatus.scan==='loaded'?'Original scan loaded':'',assetStatus.architecture==='loaded'?'measured shell loaded':'',assetStatus.repairs==='loaded'?'gap repairs loaded':'',assetStatus.furniture==='loaded'?'furniture layout loaded':''].filter(Boolean);
  $('model-status').textContent=details.join(' · ')+'.';
  $('loading').style.display='none';settled=true;
} catch(error) {
  $('load-detail').textContent=`Could not open the scan: ${error.message}. Run python3 serve.py from the extracted folder.`;
}
window.apartmentViewer={
  ready:()=>settled,config,scene,camera,renderer,controls,
  setFloor,setMode,goToRoom,setLayer,resetOverview,
  canMoveTo:(position)=>canMove(new THREE.Vector3().fromArray(position)),
  advanceWalk:move,
  pressedKeys:()=>[...movement],
  state:()=>({activeFloor,activeRoom,mode,assets:{...assetStatus},position:camera.position.toArray(),scanBounds:[modelBounds.min.toArray(),modelBounds.max.toArray()],layers:Object.fromEntries(Object.entries(layers).map(([key,value])=>[key,value.visible]))})
};
function animate(){requestAnimationFrame(animate);const dt=Math.min(clock.getDelta(),.25);if(mode==='orbit')controls.update();const steps=Math.max(1,Math.ceil(dt/.035));for(let i=0;i<steps;i++)move(dt/steps);if(needsRender){renderer.render(scene,camera);drawMap();needsRender=false;}if(mode==='walk')$('position-text').textContent=`Eye height ${eyeHeight().toFixed(2)} m · ${floorInfo().label}`;else $('position-text').textContent='Scan scale · metres';}
animate();
