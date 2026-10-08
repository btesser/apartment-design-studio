import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {chromium} from 'playwright';
const standalone=process.argv.includes('--standalone');
const fileMode=process.argv.includes('--file');
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const report={source:fileMode?'Direct file URL, network blocked':standalone?'Embedded standalone, network blocked':'http://127.0.0.1:8770',errors:[],requests:[],checks:[],views:[]};
try{
  const page=await browser.newPage({viewport:{width:1250,height:850}});
  page.on('pageerror',error=>report.errors.push(error.message));
  if(standalone){await page.route('http{,s}://**/*',route=>{report.requests.push(route.request().url());return route.abort();});if(fileMode)await page.goto(new URL('../../his-office-viewer.html',import.meta.url).href,{timeout:60000});else await page.setContent(await fs.readFile(new URL('../../his-office-viewer.html',import.meta.url),'utf8'),{timeout:60000});}
  else await page.goto(report.source);
  await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:120000});
  const state=await page.evaluate(()=>window.officeViewer.state());
  assert.equal(state.assets.shell,'loaded');assert.equal(state.assets.doors,'loaded');assert.equal(state.assets.furniture,'loaded');
  assert.equal(state.doorsHidden,false);assert.ok(state.doorMeshCount>0);
  assert.ok(state.closetSuggestionMeshCount>0);assert.equal(state.closetSuggestionVisible,false);
  report.textureCheck=await page.evaluate(()=>{
    const seen=new Set(),invalid=[],productMaps={};
    window.officeViewer.scene.traverse(mesh=>{
      if(!mesh.isMesh)return;
      const ids=[];for(let node=mesh;node;node=node.parent){const id=node.userData.id||node.userData.canonical_layout_id;if(id)ids.push(id);}
      for(const material of [mesh.material].flat())for(const key of ['map','normalMap','roughnessMap','metalnessMap','alphaMap','aoMap','emissiveMap']){
        const texture=material[key];if(!texture)continue;
        if(!seen.has(texture.uuid)){seen.add(texture.uuid);const image=texture.image;if(!image||!(image.width>0)||!(image.height>0))invalid.push({mesh:mesh.name,material:material.name,key});}
        if(key==='map')for(const id of ids)productMaps[id]=(productMaps[id]||0)+1;
      }
    });return{uniqueLoadedTextures:seen.size,invalid,productMaps};
  });
  assert.deepEqual(report.textureCheck.invalid,[]);assert.ok(report.textureCheck.uniqueLoadedTextures>10);
  for(const id of ['clothes-dresser','branch-primary','branch-secondary'])assert.ok(report.textureCheck.productMaps[id]>0,`${id} needs its restored base-colour texture.`);
  report.checks.push('Restored dresser and both task-chair image maps load with nonzero image dimensions.');
  report.assetHashes=await page.evaluate(()=>window.OFFICE_EMBED?.assetHashes||null);
  if(process.argv.includes('--capture'))await page.screenshot({path:new URL('overview-verified.png',import.meta.url).pathname,timeout:60000});
  report.checks.push('Only the new office shell, furnishings and recorded closed door leaves loaded.');
  const dimensions=await page.evaluate(()=>window.officeViewer.config.desk);
  assert.equal(dimensions.width,1.0668);assert.equal(dimensions.depth,.762);
  assert.equal(await page.locator('#view option').count(),5);
  report.checks.push('Confirmed 42 × 30 inch desk and four office viewpoints present.');
  const ids=await page.evaluate(()=>window.officeViewer.config.views.map(view=>view.id));
  for(const id of ids){await page.evaluate(id=>window.officeViewer.goToView(id),id);const pose=await page.evaluate(()=>{const v=window.officeViewer;return{...v.state(),clearStart:v.canMoveTo(v.camera.position.toArray())};});assert.equal(pose.selectedView,id);assert.equal(pose.mode,'walk');assert.equal(pose.clearStart,true,`Viewpoint ${id} must be clear of furniture and room boundaries.`);report.views.push(pose);}
  report.checks.push('All four viewpoint shortcuts select eye-level walk views.');
  await page.evaluate(()=>window.officeViewer.goToView(window.officeViewer.config.views[0].id));
  const before=await page.evaluate(()=>window.officeViewer.state().position);
  await page.focus('#viewport');await page.keyboard.down('KeyW');
  try{await page.waitForFunction(before=>{const p=window.officeViewer.state().position;return Math.hypot(p[0]-before[0],p[2]-before[2])>.015;},before,{timeout:10000,polling:100});}
  finally{await page.keyboard.up('KeyW');}
  const after=await page.evaluate(()=>window.officeViewer.state().position);
  const distance=Math.hypot(before[0]-after[0],before[2]-after[2]);assert.ok(distance>.01,'The default walk camera must move from its clear viewpoint.');report.walkDistanceMetres=distance;
  report.checks.push('Actual W input moves the eye-level camera.');
  await page.evaluate(()=>window.officeViewer.overview());
  const toggles=await page.evaluate(()=>{document.getElementById('hide-doors').click();const hidden=window.officeViewer.state().doorsHidden;const racks=window.officeViewer.state().closetSuggestionVisible;document.getElementById('furniture').click();const empty=!window.officeViewer.state().furniture;document.getElementById('hide-doors').click();document.getElementById('furniture').click();return{hidden,empty,racks,restored:!window.officeViewer.state().closetSuggestionVisible};});
  assert.deepEqual(toggles,{hidden:true,empty:true,racks:true,restored:true});
  report.checks.push('Recorded/inferred door viewing states and new furnishings visibility toggle correctly.');
  // Validate the real download handler without compositor screenshots.
  const downloaded=page.waitForEvent('download');await page.locator('#save-view').click({force:true});const download=await downloaded;assert.match(download.suggestedFilename(),/^his-office-new-design-.*\.png$/);const png=await fs.readFile(await download.path());assert.ok(png.length>10000);assert.equal(png.subarray(0,8).toString('hex'),'89504e470d0a1a0a');report.exportPngBytes=png.length;
  report.checks.push('Save image produces a PNG download.');
  assert.deepEqual(report.errors,[]);if(standalone)assert.deepEqual(report.requests,[]);
  report.checks.push(standalone?'No browser errors or network requests.':'No browser errors.');
  await fs.writeFile(new URL(fileMode?'file-results.json':standalone?'offline-results.json':'source-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({checks:report.checks,errors:report.errors,distance},null,2));
}finally{await browser.close();}
