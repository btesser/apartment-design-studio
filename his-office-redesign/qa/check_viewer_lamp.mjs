import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
const root='/workspace/his-office-redesign';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
  const page=await browser.newPage({viewport:{width:1100,height:760}});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8770');
  await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:120000});
  if(!process.argv.includes('--no-capture'))await page.screenshot({path:`${root}/qa/viewer-final-overview.png`,timeout:60000});
  const result=await page.evaluate(async()=>{
    const THREE=await import('./vendor/three.module.js');
    const originalMeshRaycast=(await import('./vendor/three.core.js?qa-native=1')).Mesh.prototype.raycast;
    const v=window.officeViewer;
    v.scene.updateMatrixWorld(true);const objects=[];
    v.scene.traverse(o=>{if(!o.isMesh)return;for(let p=o;p;p=p.parent)if(p.userData.canonical_layout_id==='honeywell-lamp'||p.name==='kept-honeywell-02e-pro'){objects.push(o);break;}});
    const cases=[];for(const x of [-.03,0,.03])for(const y of [-.1,0,.1])cases.push([x,y,null]);
    cases.push([-.070,.08,'Narrow_parallel_LED_light_bar'],[.080,.08,'Narrow_parallel_LED_light_bar'],[-.135018,0,'Rectangular_panel_long_rim'],[.135018,0,'Rectangular_panel_long_rim']);
    const rays=cases.map(([x,y,name])=>{
      const origin=[-7.67+x,3.8,.24-y];const ray=new THREE.Raycaster(new THREE.Vector3().fromArray(origin),new THREE.Vector3(0,-1,0),0,.5);
      const h=ray.intersectObjects(objects,false)[0];const pass=name===null?!h:Boolean(h&&h.object.name.startsWith(name));
      return{originGltfM:origin,expected:name||'Open aperture',actual:h?{name:h.object.name,point:h.point.toArray()}:null,pass};
    });
    const edgeOrigin=[-7.745,3.8,.24];const edgeRay=new THREE.Raycaster(new THREE.Vector3().fromArray(edgeOrigin),new THREE.Vector3(0,-1,0),0,.5);
    const accelerated=edgeRay.intersectObjects(objects,false);const baseline=[];
    for(const o of objects)originalMeshRaycast.call(o,edgeRay,baseline);
    baseline.sort((a,b)=>a.distance-b.distance);
    const centerDiagnostic={originGltfM:edgeOrigin,acceleratedHits:accelerated.map(h=>h.object.name),baselineHits:baseline.map(h=>h.object.name),note:'Exact-center diagnostic is separate from off-diagonal LED positive controls to detect numerical triangle-edge/BVH differences.'};
    const barBounds=objects.filter(o=>o.name.startsWith('Narrow_parallel_LED_light_bar')).map(o=>{
      const b=new THREE.Box3().setFromObject(o);return{name:o.name,min:b.min.toArray(),max:b.max.toArray(),materialSide:[o.material].flat().map(m=>m.side),vertexCount:o.geometry.attributes.position.count,indexCount:o.geometry.index.count,matrix:o.matrixWorld.toArray()};
    });
    return{lampMeshCount:objects.length,rays,allRaysPass:rays.every(r=>r.pass),centerDiagnostic,barBounds,state:v.state()};
  });
  const proof=`${root}/viewer-source/tests/final-asset-proof.json`;
  result.assetProof={file:proof,sha256:crypto.createHash('sha256').update(await fs.readFile(proof)).digest('hex')};
  result.currentOverviewScreenshot='viewer-final-overview.png';
  result.errors=errors;result.scope='Current exported runtime lamp aperture after local product-form correction. Earlier four-camera/keyboard proof remains valid for unchanged camera/config/placement; asset hashes for current lamp are recorded here.';
  await fs.writeFile(`${root}/qa/viewer-lamp-aperture-check.json`,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({pass:result.allRaysPass,lampMeshCount:result.lampMeshCount,errors,failures:result.rays.filter(r=>!r.pass)}));
}finally{await browser.close();}
