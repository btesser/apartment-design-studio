import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const out='/workspace/his-office-pinterest/qa/final-variants';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const report={source:'http://127.0.0.1:8773',errors:[],variants:[]};
try {
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.goto(report.source);await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:180000});
 for(const id of ['b-charcoal-slat','c-ink-studio']) {
  if(!await page.locator('#variant').isVisible())await page.locator('#controls-toggle').click();
  await page.selectOption('#variant',id);await page.waitForFunction(id=>window.officeViewer.ready()&&window.officeViewer.state().variant===id,id,{timeout:180000});
  await page.evaluate(()=>window.officeViewer.goToView('room-a'));
  const state=await page.evaluate(()=>window.officeViewer.state());
  const presence=await page.evaluate(()=>{
   const counts={};window.officeViewer.scene.traverse(o=>{if(!o.isMesh||!o.geometry?.attributes.position?.count)return;
    const ids=new Set();let visible=true;for(let p=o;p;p=p.parent){if(!p.visible)visible=false;const id=p.userData.canonical_layout_id||p.userData.id;if(id)ids.add(id);}
    for(const id of ids){counts[id]??={meshes:0,visible:0};counts[id].meshes++;if(visible)counts[id].visible++;}
   });return counts;
  });
  assert.equal(presence['aeron-primary'].meshes,40);assert.equal(presence['aeron-primary'].visible,40);
  for(const item of await page.evaluate(()=>window.officeViewer.config.products.filter(x=>x.kind!=='wall_finish')))assert.ok(presence[item.id]?.meshes>0,item.id);
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:`${out}/${id}/viewer-room-a.png`,timeout:60000});
  const before=state.position;await page.focus('#viewport');await page.keyboard.down('KeyW');
  try{await page.waitForFunction(p=>{const q=window.officeViewer.state().position;return Math.hypot(q[0]-p[0],q[2]-p[2])>.02},before,{timeout:20000});}finally{await page.keyboard.up('KeyW');}
  const after=await page.evaluate(()=>window.officeViewer.state().position);const distance=Math.hypot(after[0]-before[0],after[2]-before[2]);assert.ok(distance>.02);
  await page.evaluate(()=>window.officeViewer.goToView('room-a'));
  const maximum=await page.evaluate(()=>{const s=document.querySelector('#desk-height');s.value=s.max;s.dispatchEvent(new Event('input',{bubbles:true}));return window.officeViewer.deskLiftProof();});
  assert.equal(maximum.height_m,1.24206);
  for(const x of maximum.components)assert.ok(Math.abs(x.worldDelta_m[1]-(maximum.height_m-.74)*x.factor)<1e-7);
  assert.ok(maximum.components.some(x=>x.ids.includes('primary-felt-mat')&&x.factor===1));
  assert.ok(maximum.components.some(x=>/generic.*equipment.*assumption/.test(x.name)&&x.factor===1));
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:`${out}/${id}/viewer-standing-max.png`,timeout:60000});
  await page.evaluate(()=>window.officeViewer.resetDeskHeight());const reset=await page.evaluate(()=>window.officeViewer.deskLiftProof());assert.ok(reset.components.every(x=>x.sourcePositionResetExact));
  report.variants.push({id,state,ownedChairAndProductGeometry:presence,actualKeyboardDistance_m:distance,standingMaximum:maximum,resetExact:true});
 }
 assert.deepEqual(report.errors,[]);report.status='PASS: independent visible geometry, actual keyboard movement, upper assembly/mat/equipment travel and exact reset';
 await fs.writeFile(`${out}/independent-viewer-QA.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,variants:report.variants.map(x=>({id:x.id,keyboardDistance:x.actualKeyboardDistance_m,chairMeshes:x.ownedChairAndProductGeometry['aeron-primary']}))}));
} finally {await browser.close();}
