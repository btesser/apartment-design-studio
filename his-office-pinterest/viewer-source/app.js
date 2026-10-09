import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { acceleratedRaycast, computeBoundsTree } from './vendor/three-mesh-bvh.module.js';
THREE.Mesh.prototype.raycast=acceleratedRaycast;
THREE.BufferGeometry.prototype.computeBoundsTree=computeBoundsTree;

const $=id=>document.getElementById(id);
const catalog=window.OFFICE_EMBED?.config || await fetch('./assets/config.json').then(response=>{if(!response.ok)throw new Error('Room configuration is missing.');return response.json();});
let variant=catalog.variants[0],config=variant.config;
const viewport=$('viewport'),app=$('app');
const scene=new THREE.Scene();scene.background=new THREE.Color('#d8dde3');
const camera=new THREE.PerspectiveCamera(48,innerWidth/innerHeight,.04,65);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));renderer.setSize(innerWidth,innerHeight);
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1;renderer.localClippingEnabled=true;
viewport.appendChild(renderer.domElement);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;orbit.dampingFactor=.10;orbit.minDistance=.4;orbit.maxDistance=16;orbit.maxPolarAngle=Math.PI*.495;
let dirty=true;orbit.addEventListener('change',()=>dirty=true);
scene.add(new THREE.HemisphereLight(0xf4f7ff,0x8b929b,1.65));
const sunlight=new THREE.DirectionalLight(0xf4f7ff,2.2);sunlight.position.set(-4,10,4);scene.add(sunlight);
const fill=new THREE.DirectionalLight(0xe2ecff,.8);fill.position.set(-10,7,-4);scene.add(fill);
let shell=new THREE.Group(),furniture=new THREE.Group(),doors=new THREE.Group();
const variantCache=new Map();let variantRequest=0;
const decodedChunkCache=new Map();
let deskLift=null,deskHeight=config.desk?.operatingHeight||.74;
function embeddedAssetBuffer(reference){
  if(typeof reference==='string')return Uint8Array.from(atob(reference),character=>character.charCodeAt(0)).buffer;
  const parts=reference.map(hash=>{if(!decodedChunkCache.has(hash))decodedChunkCache.set(hash,Uint8Array.from(atob(window.OFFICE_EMBED.assetChunks[hash]),character=>character.charCodeAt(0)));return decodedChunkCache.get(hash);});
  const bytes=new Uint8Array(parts.reduce((total,part)=>total+part.length,0));let offset=0;
  for(const part of parts){bytes.set(part,offset);offset+=part.length;}return bytes.buffer;
}
function liftFactor(node){
  if(Number.isFinite(node.userData.viewer_desk_height_factor))return node.userData.viewer_desk_height_factor;
  return{desktop:1,middle:.5,fixed:0,'desktop-equipment-proxy':1}[node.userData.supplier_lift_group]??null;
}
function prepareDeskLift(state){
  const specification=state.variant.config.deskLift;if(!specification)return null;
  const records=[],errors=[];state.furniture.updateMatrixWorld(true);
  state.furniture.traverse(node=>{
    const factor=liftFactor(node);if(factor===null)return;
    for(let ancestor=node.parent;ancestor&&ancestor!==state.furniture;ancestor=ancestor.parent){const parentFactor=liftFactor(ancestor);if(parentFactor!==null){if(parentFactor!==factor)errors.push('Nested inconsistent height factors: '+node.name);return;}}
    const ids=[];for(let ancestor=node;ancestor;ancestor=ancestor.parent)for(const key of ['id','canonical_layout_id'])if(ancestor.userData[key])ids.push(ancestor.userData[key]);
    records.push({node,factor,ids,sourceComponent:node.userData.source_component_name,sourcePosition:node.position.clone(),sourceScale:node.scale.clone(),sourceQuaternion:node.quaternion.clone(),sourceWorld:node.getWorldPosition(new THREE.Vector3())});
  });
  for(const part of specification.parts){const record=records.find(r=>r.sourceComponent===part.source_name);if(!record||record.factor!==part.height_factor)errors.push('Supplier component missing or incorrect: '+part.source_name);}
  for(const id of specification.requiredCarryRoots||[])if(!records.some(record=>record.factor===1&&record.ids.includes(id)))errors.push('Desktop carry item is untagged: '+id);
  if(!records.some(record=>record.node.userData.supplier_lift_group==='desktop-equipment-proxy'))errors.push('Desk equipment root is untagged.');
  return{specification,records,errors,enabled:!errors.length};
}
function setDeskHeight(value){
  if(!deskLift?.enabled)return false;
  if(!Number.isFinite(Number(value)))return false;
  const [minimum,maximum]=deskLift.specification.heightRange_m,seated=deskLift.specification.seatedHeight_m;
  deskHeight=THREE.MathUtils.clamp(Number(value),minimum,maximum);if(!Number.isFinite(deskHeight)){deskHeight=seated;return false;}
  const delta=deskHeight-seated;
  for(const record of deskLift.records){
    if(Math.abs(delta)<1e-10||record.factor===0)record.node.position.copy(record.sourcePosition);
    else{record.node.parent?.updateWorldMatrix(true,false);const world=record.sourceWorld.clone();world.y+=delta*record.factor;record.node.position.copy(record.node.parent?record.node.parent.worldToLocal(world):world);}
    record.node.updateMatrix();
  }
  furniture.updateMatrixWorld(true);$('desk-height').value=String(deskHeight);$('desk-height-value').textContent=(deskHeight*100).toFixed(1)+' cm';dirty=true;return true;
}
function resetDeskHeight(){if(deskLift?.enabled)setDeskHeight(deskLift.specification.seatedHeight_m);}
const grid=new THREE.GridHelper(12,12,0x789496,0xbfc9b9);grid.position.set(-6,config.room.floor+.015,1);grid.material.transparent=true;grid.material.opacity=.4;grid.visible=false;scene.add(grid);
let shellPlanes=[],furniturePlanes=[],shellMaterials=new Set(),furnitureMaterials=new Set(),doorMeshes=[],closetSuggestionMeshes=[],wallArtMeshes=[];
const raycaster=new THREE.Raycaster();raycaster.firstHitOnly=true;
const clock=new THREE.Clock(),forward=new THREE.Vector3();
let mode='orbit',selectedView='room-a',yaw=0,pitch=0,cutaway=Number($('cutaway').value),ready=false,pointer=null,toastTimer;
const keys=new Set();let assetState={};

function notify(message){$('toast').textContent=message;$('toast').style.opacity=1;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').style.opacity=0,3500);}
function updateProjection(){
  const pose=config.views.find(view=>view.id===selectedView),horizontal=pose?.horizontal_FOV_deg;
  camera.fov=mode==='walk'?(horizontal?THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(horizontal)/2)/camera.aspect)):68):48;
  if(innerWidth>780&&mode==='orbit')camera.setViewOffset(innerWidth,innerHeight,-145,0,innerWidth,innerHeight);else camera.clearViewOffset();camera.updateProjectionMatrix();dirty=true;
}
function updateClip(){
  shellPlanes.length=0;furniturePlanes.length=0;
  const floor=config.room.floor,ceiling=config.room.ceiling;
  shellPlanes.push(new THREE.Plane(new THREE.Vector3(0,1,0),-(floor-.10)),new THREE.Plane(new THREE.Vector3(0,-1,0),mode==='orbit'?floor+cutaway:ceiling+.025));
  furniturePlanes.push(new THREE.Plane(new THREE.Vector3(0,1,0),-(floor-.10)),new THREE.Plane(new THREE.Vector3(0,-1,0),ceiling+.025));
  for(const material of [...shellMaterials,...furnitureMaterials])material.needsUpdate=true;
  dirty=true;
}
function isDoorLeaf(object){
  for(let current=object;current;current=current.parent){
    const role=String(current.userData.role||current.userData.category||current.userData.element_type||'').toLowerCase();
    if(/door[_ -]?leaf/.test(role))return true;
    if(/door[_ -]?leaf/.test(current.name.toLowerCase()))return true;
  }
  return false;
}
function isClosetSuggestion(object){
  for(let current=object;current;current=current.parent){
    if(current.userData.hide_in_closed_door_views===true)return true;
    const tags=[current.name,current.userData.id,current.userData.product_id].filter(Boolean).join(' ');
    if(/grejig|closet[_ -]?shoe[_ -]?rack/i.test(tags))return true;
  }
  return false;
}
function wallArtFootprint(object,roomConfig=config){
  for(let current=object;current;current=current.parent){
    const id=current.userData.canonical_layout_id||current.userData.id;
    const art=(roomConfig.footprints||[]).find(item=>['art','wall_art'].includes(item.kind)&&(item.id===id||current.name===item.id||current.name.startsWith(item.id+'::')));
    if(art)return art;
  }
  return null;
}
function updateArtViewingState(){
  for(const {mesh,item,minY} of wallArtMeshes){
    // A removed near wall must not leave the opaque back of its art in the way.
    const behind=item.facing&&(camera.position.x-item.center[0])*item.facing[0]+(camera.position.z-item.center[1])*item.facing[1]<0;
    mesh.visible=!(mode==='orbit'&&config.room.floor+cutaway<minY&&behind);
  }
}
async function loadAsset(key,state){
  const filename=state.variant.config.assets[key],group=state[key],materialSet=key==='furniture'?state.furnitureMaterials:state.shellMaterials,planes=key==='furniture'?state.furniturePlanes:state.shellPlanes;
  if(!filename){state.assetState[key]='absent';group.visible=false;return;}
  const loader=new GLTFLoader();
  const embedded=window.OFFICE_EMBED?.assets[state.variant.id]?.[key];
  const gltf=embedded?await loader.parseAsync(embeddedAssetBuffer(embedded),''):await loader.loadAsync('./assets/'+filename);
  gltf.scene.updateMatrixWorld(true);
  gltf.scene.traverse(object=>{
    if(!object.isMesh)return;
    if(!object.geometry.boundsTree)object.geometry.computeBoundsTree();
    for(const material of [object.material].flat()){material.side=THREE.DoubleSide;material.clippingPlanes=planes;materialSet.add(material);}
    if(key==='doors'||(key==='shell'&&isDoorLeaf(object)))state.doorMeshes.push(object);
    if(key==='furniture'&&isClosetSuggestion(object)){state.closetSuggestionMeshes.push(object);object.visible=$('hide-doors').checked;}
    if(key==='furniture'){const item=wallArtFootprint(object,state.variant.config);if(item)state.wallArtMeshes.push({mesh:object,item,minY:new THREE.Box3().setFromObject(object).min.y});}
  });
  group.add(gltf.scene);state.assetState[key]='loaded';
}
async function prepareVariant(next){
  if(variantCache.has(next.id))return variantCache.get(next.id);
  const promise=(async()=>{
    const state={variant:next,shell:new THREE.Group(),furniture:new THREE.Group(),doors:new THREE.Group(),shellMaterials:new Set(),furnitureMaterials:new Set(),shellPlanes:[],furniturePlanes:[],doorMeshes:[],closetSuggestionMeshes:[],wallArtMeshes:[],assetState:{}};
    state.shell.name=next.id+'-room-shell';state.furniture.name=next.id+'-furnishings';state.doors.name=next.id+'-recorded-door-leaves';
    await Promise.all(['shell','doors','furniture'].map(key=>loadAsset(key,state)));state.deskLift=prepareDeskLift(state);return state;
  })();variantCache.set(next.id,promise);return promise;
}
function updateProductInspection(){
  const item=(config.products||[]).find(item=>item.id===$('inspect-product').value);
  if(!item){$('product-facts').textContent='Choose a product to check its size and orientation.';return;}
  const d=item.dimensions_m||[],format=value=>new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(value*100),label=d.length===3?`${format(d[0])} × ${format(d[1])} × ${format(d[2])} cm (W × D × H)`:'';
  $('product-facts').textContent=[label,item.orientation,item.note].filter(Boolean).join(' · ');
}
function updateVariantUI(){
  $('model-status').textContent=catalog.status==='final'?'TWO DIRECTIONS · ONE REAL ROOM':'WORKING MODEL · FURNITURE UPDATE PENDING';
  $('variant').value=variant.id;$('variant-description').textContent=variant.description;
  $('desk-title').textContent=`Standing desk: ${Math.round(config.desk.width*100)} × ${Math.round(config.desk.depth*100)} cm.`;
  $('desk-note').textContent=config.desk.confidence+'; seated height in this model is '+Math.round(config.desk.operatingHeight*100)+' cm.';
  $('model-note').textContent=config.notes;
  $('inspect-product').replaceChildren(...(config.products||[]).map(item=>new Option(item.name,item.id)));updateProductInspection();
  $('model-source').href=new URL(variant.model_source,new URL(window.OFFICE_EMBED?'./':'../',location.href)).href;$('model-source').textContent='Download '+variant.label+' Blender model';
  $('model-hash').textContent='SHA-256: '+variant.model_sha256;
  $('desk-height-panel').hidden=!deskLift?.enabled;
  if(deskLift?.enabled){const[min,max]=deskLift.specification.heightRange_m;$('desk-height').min=String(min);$('desk-height').max=String(max);resetDeskHeight();}
}
async function switchVariant(id){
  const next=catalog.variants.find(item=>item.id===id);if(!next)throw new Error('Unknown room alternative.');
  const request=++variantRequest;ready=false;keys.clear();$('loading').style.display='flex';$('loading-detail').textContent='Opening '+next.label+'…';
  try{
    const state=await prepareVariant(next);if(request!==variantRequest)return;
    resetDeskHeight();scene.remove(shell,furniture,doors);variant=next;config=next.config;
    ({shell,furniture,doors,shellMaterials,furnitureMaterials,shellPlanes,furniturePlanes,doorMeshes,closetSuggestionMeshes,wallArtMeshes,assetState}=state);
    deskLift=state.deskLift;deskHeight=config.desk.operatingHeight;
    scene.add(shell,furniture,doors);setFurniture($('furniture').checked);setDoorsHidden($('hide-doors').checked);updateVariantUI();updateClip();updateProjection();
    if(selectedView==='overview')overview();else goToView(selectedView);
    await renderer.compileAsync(scene,camera);if(request!==variantRequest)return;
    $('loading').style.display='none';$('hide-doors').disabled=!doorMeshes.length;ready=true;dirty=true;
  }catch(error){if(request===variantRequest){$('loading-detail').textContent='Could not open this model: '+error.message;console.error(error);}throw error;}
}
function setDoorsHidden(hidden){doorMeshes.forEach(mesh=>mesh.visible=!hidden);closetSuggestionMeshes.forEach(mesh=>mesh.visible=hidden);$('hide-doors').checked=hidden;$('door-note').textContent=hidden?'Door leaves are hidden for an inferred open viewing state. Closet racks are a provisional fit idea.':'Doors match the recorded closed state. Provisional closet racks are hidden.';dirty=true;}
function setFurniture(visible){furniture.visible=visible;$('furniture').checked=visible;dirty=true;}
function setWalkRotation(){camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));dirty=true;}
function lookAt(target){const direction=new THREE.Vector3().fromArray(target).sub(camera.position).normalize();yaw=Math.atan2(-direction.x,-direction.z);pitch=Math.asin(THREE.MathUtils.clamp(direction.y,-1,1));pitch=THREE.MathUtils.clamp(pitch,-Math.PI*.46,Math.PI*.46);setWalkRotation();}
function setMode(next,place=true){
  if(next===mode)return;mode=next;keys.clear();orbit.enabled=next==='orbit';
  app.classList.toggle('walking',next==='walk');$('orbit').classList.toggle('active',next==='orbit');$('walk').classList.toggle('active',next==='walk');
  if(next==='walk'){
    $('panel').classList.remove('open');$('controls-toggle').setAttribute('aria-expanded','false');viewport.focus({preventScroll:true});
    if(place){const view=config.views.find(view=>view.id===selectedView)||config.views[0];camera.position.fromArray(view.eye);lookAt(view.target);}
    $('nav-hint').textContent='Click the room to look · W A S D to walk · Esc releases the mouse';
  }else{
    if(document.pointerLockElement)document.exitPointerLock();
    const target=camera.position.clone().add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(2));target.y=config.room.floor+.65;orbit.target.copy(target);orbit.update();
    $('nav-hint').textContent='Drag to rotate · scroll to zoom · right-drag to pan';
  }
  updateProjection();updateClip();
}
function goToView(id){
  if(id==='overview'){overview();return;}
  const view=config.views.find(view=>view.id===id);if(!view)return;
  resetDeskHeight();
  selectedView=id;$('view').value=id;setMode('walk',false);camera.position.fromArray(view.eye);lookAt(view.target);
  updateProjection();$('view-title').textContent=view.label;$('view-description').textContent=view.description||'The selected design inside the measured office shell.';
  $('panel').classList.remove('open');$('controls-toggle').setAttribute('aria-expanded','false');viewport.focus({preventScroll:true});dirty=true;
}
function overview(){
  if(mode!=='orbit')setMode('orbit',false);selectedView='overview';$('view').value='overview';
  const [xmin,xmax,zmin,zmax]=config.room.bounds,center=[(xmin+xmax)/2,config.room.floor+.6,(zmin+zmax)/2];
  orbit.target.fromArray(center);camera.position.set(center[0]+4.2,center[1]+4.9,center[2]+5.4);orbit.update();
  $('view-title').textContent='Whole room';$('view-description').textContent='Compare '+variant.label+' in the measured office shell.';dirty=true;
}
function insidePolygon(x,z,polygon){let result=false;for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){const[xi,zi]=polygon[i],[xj,zj]=polygon[j];if(((zi>z)!==(zj>z))&&x<(xj-xi)*(z-zi)/(zj-zi)+xi)result=!result;}return result;}
function inside(x,z){return insidePolygon(x,z,config.room.polygon);}
function circleOverlapsPolygon(x,z,radius,polygon){
  if(insidePolygon(x,z,polygon))return true;
  for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){
    const[ax,az]=polygon[j],[bx,bz]=polygon[i],dx=bx-ax,dz=bz-az;
    const t=THREE.MathUtils.clamp(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz||1),0,1);
    if(Math.hypot(x-ax-t*dx,z-az-t*dz)<radius)return true;
  }
  return false;
}
function canMoveTo(position){
  const bodyRadius=.16;
  const bodyPoints=[[0,0],[bodyRadius,0],[-bodyRadius,0],[0,bodyRadius],[0,-bodyRadius]];
  if(!bodyPoints.every(([dx,dz])=>inside(position.x+dx,position.z+dz)))return false;
  if(furniture.visible&&(config.footprints||[]).some(item=>item.walkBlocker===true&&!(item.hiddenWhenDoorsClosed&&!$('hide-doors').checked)&&item.polygon&&circleOverlapsPolygon(position.x,position.z,bodyRadius,item.polygon)))return false;
  const direction=position.clone().sub(camera.position);direction.y=0;const distance=direction.length();if(distance<1e-7)return true;direction.normalize();
  const colliders=[shell,doors,...(furniture.visible?[furniture]:[])];
  for(const height of [-1.15,-.82,-.4,0]){
    raycaster.set(new THREE.Vector3(camera.position.x,camera.position.y+height,camera.position.z),direction);raycaster.near=.005;raycaster.far=distance+bodyRadius;
    const hits=raycaster.intersectObjects(colliders,true).filter(hit=>hit.object.isMesh&&hit.object.visible&&hit.point.y>config.room.floor+.15&&hit.point.y<config.room.ceiling-.05);
    if(hits.length)return false;
  }
  return true;
}
function move(dt){
  if(mode!=='walk')return;let dx=0,dz=0;
  if(keys.has('KeyW')||keys.has('ArrowUp')||keys.has('forward'))dz--;
  if(keys.has('KeyS')||keys.has('ArrowDown')||keys.has('back'))dz++;
  if(keys.has('KeyA')||keys.has('ArrowLeft')||keys.has('left'))dx--;
  if(keys.has('KeyD')||keys.has('ArrowRight')||keys.has('right'))dx++;
  if(!dx&&!dz)return;
  const speed=dt*(keys.has('ShiftLeft')||keys.has('ShiftRight')?1.8:1.0)/Math.hypot(dx,dz);
  const vx=(Math.cos(yaw)*dx+Math.sin(yaw)*dz)*speed,vz=(-Math.sin(yaw)*dx+Math.cos(yaw)*dz)*speed;
  const next=camera.position.clone();next.x+=vx;if(canMoveTo(next))camera.position.x=next.x;
  next.copy(camera.position);next.z+=vz;if(canMoveTo(next))camera.position.z=next.z;
  camera.position.y=config.room.floor+config.room.eyeHeight;dirty=true;
}
const map=$('map'),ctx=map.getContext('2d');
function drawMap(){
  const[xmin,xmax,zmin,zmax]=config.room.bounds,w=map.width,h=map.height,margin=16,scale=Math.min((w-2*margin)/(xmax-xmin),(h-2*margin)/(zmax-zmin));
  const ox=(w-(xmax-xmin)*scale)/2,oz=(h-(zmax-zmin)*scale)/2,p=(x,z)=>[ox+(x-xmin)*scale,oz+(z-zmin)*scale];
  ctx.clearRect(0,0,w,h);ctx.fillStyle='#f1f5fa';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#dce4ef';ctx.lineWidth=1;
  for(let x=Math.ceil(xmin);x<xmax;x++){const[a,b]=p(x,zmin),[c,d]=p(x,zmax);ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke();}
  for(let z=Math.ceil(zmin);z<zmax;z++){const[a,b]=p(xmin,z),[c,d]=p(xmax,z);ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke();}
  ctx.beginPath();config.room.polygon.forEach(([x,z],i)=>{const[a,b]=p(x,z);i?ctx.lineTo(a,b):ctx.moveTo(a,b)});ctx.closePath();ctx.fillStyle='#e5ecf5';ctx.fill();ctx.strokeStyle='#8fa4c0';ctx.lineWidth=3;ctx.stroke();
  if(furniture.visible)[...(config.footprints||[])].sort((a,b)=>(a.kind==='rug'?-1:0)-(b.kind==='rug'?-1:0)).forEach(item=>{
    if(!item.polygon||item.hiddenWhenDoorsClosed&&!$('hide-doors').checked)return;
    ctx.beginPath();item.polygon.forEach(([x,z],i)=>{const[a,b]=p(x,z);i?ctx.lineTo(a,b):ctx.moveTo(a,b)});ctx.closePath();
    if(item.kind==='provisional_branch_reach'){ctx.strokeStyle='#b88443';ctx.lineWidth=1.5;ctx.setLineDash([4,3]);ctx.stroke();ctx.setLineDash([]);}
    else{ctx.fillStyle=item.kind==='rug'?'#c6d3e5':item.provisional?'#d8c9a7':'#9eb1c9';ctx.fill();}
    if(item.center&&item.facing){const[a,b]=p(...item.center),[c,d]=p(item.center[0]+item.facing[0]*.3,item.center[1]+item.facing[1]*.3);ctx.beginPath();ctx.strokeStyle='#47688f';ctx.lineWidth=2;ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke();}
  });
  const[cx,cz]=p(camera.position.x,camera.position.z);camera.getWorldDirection(forward);ctx.save();ctx.translate(cx,cz);ctx.rotate(Math.atan2(forward.z,forward.x));ctx.fillStyle='#426a9b';ctx.beginPath();ctx.moveTo(12,0);ctx.lineTo(-7,-6);ctx.lineTo(-3,0);ctx.lineTo(-7,6);ctx.closePath();ctx.fill();ctx.restore();
}

catalog.variants.forEach(item=>$('variant').appendChild(new Option(item.label,item.id)));
config.views.forEach(view=>$('view').appendChild(new Option(view.label,view.id)));
$('dimensions').textContent=`Approximately ${config.room.width.toFixed(1)} × ${config.room.depth.toFixed(1)} m · ${config.room.area.toFixed(1)} m² · irregular outline. Ceiling ${(config.room.ceiling-config.room.floor).toFixed(2)} m.`;
$('variant').addEventListener('change',event=>switchVariant(event.target.value).catch(()=>{}));
$('inspect-product').addEventListener('change',updateProductInspection);
$('desk-height').addEventListener('input',event=>setDeskHeight(event.target.value));$('reset-desk-height').addEventListener('click',resetDeskHeight);
$('view').addEventListener('change',event=>goToView(event.target.value));$('overview').addEventListener('click',overview);$('orbit').addEventListener('click',()=>setMode('orbit'));$('walk').addEventListener('click',()=>setMode('walk'));
$('furniture').addEventListener('change',event=>setFurniture(event.target.checked));$('hide-doors').addEventListener('change',event=>setDoorsHidden(event.target.checked));$('grid').addEventListener('change',event=>{grid.visible=event.target.checked;dirty=true;});
$('cutaway').addEventListener('input',event=>{cutaway=Number(event.target.value);$('cutaway-value').value=cutaway.toFixed(1)+' m';updateClip();});
$('controls-toggle').addEventListener('click',()=>{$('controls-toggle').setAttribute('aria-expanded',String($('panel').classList.toggle('open')));});
$('save-view').addEventListener('click',()=>{updateArtViewingState();renderer.render(scene,camera);const link=document.createElement('a');link.href=renderer.domElement.toDataURL('image/png');const heightSuffix=deskLift?.enabled&&Math.abs(deskHeight-deskLift.specification.seatedHeight_m)>.0001?'-'+Math.round(deskHeight*1000)+'mm':'';link.download=`his-office-${variant.id}-${selectedView}-${mode}${heightSuffix}.png`;link.click();notify('Image saved from the current 3D geometry.');});
$('enter-walk').addEventListener('click',()=>renderer.domElement.requestPointerLock?.());
document.addEventListener('pointerlockchange',()=>{app.classList.toggle('locked',!!document.pointerLockElement);keys.clear();});
document.addEventListener('mousemove',event=>{if(mode!=='walk'||!document.pointerLockElement)return;yaw-=event.movementX*.002;pitch=THREE.MathUtils.clamp(pitch-event.movementY*.002,-Math.PI*.46,Math.PI*.46);setWalkRotation();});
renderer.domElement.addEventListener('click',()=>{if(mode==='walk'&&!matchMedia('(pointer:coarse)').matches)renderer.domElement.requestPointerLock?.();});
renderer.domElement.addEventListener('pointerdown',event=>{if(mode!=='walk'||document.pointerLockElement)return;pointer=[event.clientX,event.clientY];renderer.domElement.setPointerCapture(event.pointerId);});
renderer.domElement.addEventListener('pointermove',event=>{if(mode!=='walk'||!pointer||document.pointerLockElement)return;const dx=event.clientX-pointer[0],dy=event.clientY-pointer[1];yaw-=dx*.003;pitch=THREE.MathUtils.clamp(pitch-dy*.003,-Math.PI*.46,Math.PI*.46);pointer=[event.clientX,event.clientY];setWalkRotation();});
['pointerup','pointercancel'].forEach(type=>renderer.domElement.addEventListener(type,()=>pointer=null));
const motionKeys=['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'];
document.addEventListener('keydown',event=>{if(mode!=='walk'||(!document.pointerLockElement&&event.target.closest('select,input')))return;if(motionKeys.includes(event.code)){keys.add(event.code);event.preventDefault();}});
document.addEventListener('keyup',event=>keys.delete(event.code));window.addEventListener('blur',()=>keys.clear());
document.querySelectorAll('[data-move]').forEach(button=>{button.addEventListener('pointerdown',event=>{event.preventDefault();keys.add(button.dataset.move);button.setPointerCapture(event.pointerId);});['pointerup','pointercancel','lostpointercapture'].forEach(type=>button.addEventListener(type,()=>keys.delete(button.dataset.move)));});
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;renderer.setSize(innerWidth,innerHeight);updateProjection();});

try{
  await switchVariant(variant.id);
}catch(error){$('loading-detail').textContent=`Could not open this model: ${error.message}`;console.error(error);}
window.officeViewer={ready:()=>ready,get config(){return config;},catalog,scene,camera,renderer,goToView,overview,setMode,setDoorsHidden,setFurniture,switchVariant,setDeskHeight,resetDeskHeight,deskLiftProof:()=>({enabled:!!deskLift?.enabled,errors:deskLift?.errors||[],height_m:deskHeight,seatedHeight_m:deskLift?.specification.seatedHeight_m,heightRange_m:deskLift?.specification.heightRange_m,requiredCarryRoots:deskLift?.specification.requiredCarryRoots||[],components:(deskLift?.records||[]).map(record=>({name:record.node.name,sourceComponent:record.sourceComponent,factor:record.factor,ids:record.ids,worldDelta_m:record.node.getWorldPosition(new THREE.Vector3()).sub(record.sourceWorld).toArray(),scaleUnchanged:record.node.scale.equals(record.sourceScale),rotationUnchanged:record.node.quaternion.equals(record.sourceQuaternion),sourcePositionResetExact:record.node.position.equals(record.sourcePosition)}))}),advanceWalk:move,pressedKeys:()=>[...keys],canMoveTo:point=>canMoveTo(new THREE.Vector3().fromArray(point)),lampAperture:()=>{
  scene.updateMatrixWorld(true);const objects=[];
  furniture.traverse(mesh=>{if(!mesh.isMesh)return;for(let node=mesh;node;node=node.parent)if(node.userData.canonical_layout_id==='honeywell-lamp'||node.userData.id==='honeywell-lamp'||node.name==='kept-honeywell-02e-pro'){objects.push(mesh);break;}});
  const cases=[];for(const x of [-.03,0,.03])for(const y of [-.1,0,.1])cases.push([x,y,null]);
  cases.push([-.070,.08,'Narrow_parallel_LED_light_bar'],[.080,.08,'Narrow_parallel_LED_light_bar'],[-.135018,0,'Rectangular_panel_long_rim'],[.135018,0,'Rectangular_panel_long_rim']);
  const rays=cases.map(([x,y,name])=>{const origin=[-7.67+x,3.8,.24-y],ray=new THREE.Raycaster(new THREE.Vector3().fromArray(origin),new THREE.Vector3(0,-1,0),0,.5),hit=ray.intersectObjects(objects,false)[0];return{originGltfM:origin,expected:name||'Open aperture',actual:hit?hit.object.name:null,pass:name===null?!hit:Boolean(hit&&hit.object.name.startsWith(name))};});
  return{variant:variant.id,lampMeshCount:objects.length,rays,allRaysPass:rays.every(ray=>ray.pass)};
},state:()=>({variant:variant.id,modelSHA256:variant.model_sha256,mode,selectedView,position:camera.position.toArray(),assets:{...assetState},furniture:furniture.visible,doorsHidden:$('hide-doors').checked,doorMeshCount:doorMeshes.length,closetSuggestionMeshCount:closetSuggestionMeshes.length,closetSuggestionVisible:closetSuggestionMeshes.some(mesh=>mesh.visible),bounds:new THREE.Box3().setFromObject(shell).min.toArray().concat(new THREE.Box3().setFromObject(shell).max.toArray())})};
function animate(){requestAnimationFrame(animate);const dt=Math.min(clock.getDelta(),.25);if(mode==='orbit')orbit.update();const count=Math.max(1,Math.ceil(dt/.035));for(let i=0;i<count;i++)move(dt/count);if(dirty){updateArtViewingState();renderer.render(scene,camera);drawMap();dirty=false;}$('status-text').textContent=mode==='walk'?`Eye height ${config.room.eyeHeight.toFixed(2)} m · ${variant.label}`:variant.label+' · original metre scale';}
animate();
