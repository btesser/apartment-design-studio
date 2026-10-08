import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';

const root='/workspace/his-office-redesign';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const result={source:'http://127.0.0.1:8770',errors:[],views:[],fireplaceRays:[],screenshots:[]};
try {
  const page=await browser.newPage({viewport:{width:1360,height:900}});
  page.on('pageerror',e=>result.errors.push(e.message));
  await page.goto(result.source);
  await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:120000});
  result.initial=await page.evaluate(()=>window.officeViewer.state());
  result.fireplaceRays=await page.evaluate(async()=>{
    const THREE=await import('./vendor/three.module.js');
    const scene=window.officeViewer.scene;scene.updateMatrixWorld(true);
    const cases=[];
    for(const x of [-5.535,-5.315,-5.095])for(const z of [1.75,2.1,2.32])cases.push([x,z,'Observed_recessed_white_arched_fireplace_infill',2.835]);
    cases.push([-5.315,2.43,'Observed_recessed_white_arched_fireplace_infill',2.835]);
    for(const [x,z] of [[-5.69,2.02],[-4.94,2.02],[-5.315,2.53]])cases.push([x,z,'Observed_brick_chimney_projection',2.722]);
    return cases.map(([x,height,expected,z])=>{
      const caster=new THREE.Raycaster(new THREE.Vector3(x,height,2.0),new THREE.Vector3(0,0,1),0,2);
      const hit=caster.intersectObjects(scene.children,true).find(h=>h.object.visible);
      const pass=Boolean(hit&&hit.object.name===expected&&Math.abs(hit.point.z-z)<.0001);
      return {originGltfM:[x,height,2.0],expectedObject:expected,expectedSurfaceZ:z,actual:hit?{name:hit.object.name,point:hit.point.toArray()}:null,pass};
    });
  });
  // GLTF names sanitize spaces; record the first actual returned names before asserting.
  const ids=await page.evaluate(()=>window.officeViewer.config.views.map(v=>v.id));
  for(const id of ids){
    await page.evaluate(id=>window.officeViewer.goToView(id),id);
    const initial=await page.evaluate(()=>{const v=window.officeViewer;return {...v.state(),clear:v.canMoveTo(v.camera.position.toArray())};});
    assert.equal(initial.clear,true);
    await page.screenshot({path:`${root}/qa/viewer-${id}.png`,timeout:60000});
    result.screenshots.push(`viewer-${id}.png`);
    await page.focus('#viewport');
    await page.keyboard.down('KeyW');
    let acknowledged=[];
    try {
      acknowledged=await page.evaluate(()=>window.officeViewer.pressedKeys());
      await page.waitForFunction(p=>{const n=window.officeViewer.state().position;return Math.hypot(n[0]-p[0],n[2]-p[2])>.025;},initial.position,{timeout:10000,polling:100});
    } finally {await page.keyboard.up('KeyW');}
    const after=await page.evaluate(()=>window.officeViewer.state().position);
    const distance=Math.hypot(after[0]-initial.position[0],after[2]-initial.position[2]);
    result.views.push({id,initial,actualPressedKeys:acknowledged,afterWPosition:after,actualWDistanceM:distance,actualKeyboardPass:acknowledged.includes('KeyW')&&distance>.025});
    assert.ok(result.views.at(-1).actualKeyboardPass);
  }
  result.allFourTeleportsAndActualKeyboardPass=result.views.length===4&&result.views.every(v=>v.actualKeyboardPass&&v.initial.clear);
  result.fireplaceRayPass=result.fireplaceRays.every(r=>r.pass);
  result.noPageErrors=result.errors.length===0;
  const proofPath=`${root}/viewer-source/tests/final-asset-proof.json`;
  result.viewerAssetProof={file:proofPath,sha256:crypto.createHash('sha256').update(await fs.readFile(proofPath)).digest('hex')};
  result.limit='Browser keyboard/clear-start and topology smoke check, not metric real installation or walkable-person clearance certification.';
  await fs.writeFile(`${root}/qa/viewer-independent-checks.json`,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({proof:`${root}/qa/viewer-independent-checks.json`,teleportsAndKeyboard:result.allFourTeleportsAndActualKeyboardPass,fireplace:result.fireplaceRayPass,errors:result.errors,rayNames:result.fireplaceRays.map(r=>r.actual?.name),distances:result.views.map(v=>[v.id,v.actualWDistanceM])}));
} finally {await browser.close();}
