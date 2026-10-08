import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {chromium} from 'playwright';
const standalone=process.argv.includes('--standalone'),fileMode=process.argv.includes('--file');
const sourceUrl=process.env.VIEWER_URL||'http://127.0.0.1:8773';
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const report={source:fileMode?'Direct file URL, network blocked':standalone?'Embedded standalone, network blocked':sourceUrl,errors:[],requests:[],checks:[],variants:[]};
try{
  const page=await browser.newPage({viewport:{width:1250,height:850}});
  const selectControl=async(id,value)=>{
    if(!await page.locator('#'+id).isVisible())await page.locator('#controls-toggle').click();
    await page.selectOption('#'+id,value);
  };
  page.on('pageerror',error=>report.errors.push(error.message));
  if(standalone){
    await page.route('http{,s}://**/*',route=>{report.requests.push(route.request().url());return route.abort();});
    if(fileMode)await page.goto(new URL('../../his-office-viewer.html',import.meta.url).href,{timeout:60000});
    else await page.setContent(await fs.readFile(new URL('../../his-office-viewer.html',import.meta.url),'utf8'),{timeout:120000});
  }else await page.goto(sourceUrl);
  await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:180000});
  const variantIds=await page.evaluate(()=>window.officeViewer.catalog.variants.map(v=>v.id));
  assert.deepEqual(variantIds,['b-charcoal-slat','c-ink-studio']);assert.equal(await page.locator('#variant option').count(),2);
  for(const variantId of variantIds){
    await selectControl('variant',variantId);await page.waitForFunction(id=>window.officeViewer.ready()&&window.officeViewer.state().variant===id,variantId,{timeout:180000});
    const state=await page.evaluate(()=>window.officeViewer.state());
    assert.equal(state.assets.shell,'loaded');assert.equal(state.assets.doors,'loaded');assert.equal(state.assets.furniture,'loaded');assert.equal(state.doorsHidden,false);assert.ok(state.doorMeshCount>0);assert.ok(state.closetSuggestionMeshCount>0);assert.equal(state.closetSuggestionVisible,false);
    const detail=await page.evaluate(()=>({config:window.officeViewer.config,source:document.getElementById('model-source').getAttribute('href'),hash:document.getElementById('model-hash').textContent}));
    assert.equal(detail.config.desk.width,1.2);assert.equal(detail.config.desk.depth,.685);
    assert.equal(detail.config.products.filter(p=>p.kind==='task_chair').length,1);
    assert.ok(detail.source.includes(variantId));assert.ok(detail.hash.includes(state.modelSHA256));assert.match(state.modelSHA256,/^[a-f0-9]{64}$/);
    if(!standalone){const link=new URL(detail.source,sourceUrl).href;const response=await page.request.head(link);assert.equal(response.status(),200,'Editable model link resolves to the accompanying Blender file.');}
    assert.equal(await page.locator('#inspect-product option').count(),detail.config.products.length);
    const primary=detail.config.products.find(p=>p.kind==='task_chair');assert.deepEqual(primary.front_blender_vector,[0,1,0]);
    const visitor=detail.config.products.find(p=>p.id==='visitor-chair');assert.deepEqual(visitor.front_blender_vector,[0,1,0]);
    const textures=await page.evaluate(()=>{
      const seen=new Set(),invalid=[],productMaps={};
      window.officeViewer.scene.traverse(mesh=>{
        if(!mesh.isMesh)return;const ids=[];for(let node=mesh;node;node=node.parent){const id=node.userData.id||node.userData.canonical_layout_id;if(id)ids.push(id);}
        for(const material of [mesh.material].flat())for(const key of ['map','normalMap','roughnessMap','metalnessMap','alphaMap','aoMap','emissiveMap']){
          const texture=material[key];if(!texture)continue;
          if(!seen.has(texture.uuid)){seen.add(texture.uuid);const image=texture.image;if(!image||!(image.width>0)||!(image.height>0))invalid.push({mesh:mesh.name,material:material.name,key});}
          if(key==='map')for(const id of ids)productMaps[id]=(productMaps[id]||0)+1;
        }
      });return{uniqueLoadedTextures:seen.size,invalid,productMaps};
    });
    assert.deepEqual(textures.invalid,[]);assert.ok(textures.uniqueLoadedTextures>0);
    const poses=[];
    for(const id of detail.config.views.map(v=>v.id)){
      await selectControl('view',id);
      const pose=await page.evaluate(()=>{const v=window.officeViewer;return{...v.state(),clearStart:v.canMoveTo(v.camera.position.toArray()),fov:v.camera.fov};});
      assert.equal(pose.selectedView,id);assert.equal(pose.mode,'walk');assert.equal(pose.clearStart,true,`${variantId}/${id} starts clear of footprints.`);
      const canonical=detail.config.views.find(v=>v.id===id);assert.deepEqual(pose.position,canonical.eye);
      const expected=2*Math.atan(Math.tan(canonical.horizontal_FOV_deg*Math.PI/360)/(1250/850))*180/Math.PI;assert.ok(Math.abs(pose.fov-expected)<1e-6);poses.push(pose);
    }
    await page.evaluate(()=>window.officeViewer.goToView(window.officeViewer.config.views[0].id));
    const before=await page.evaluate(()=>window.officeViewer.state().position);await page.focus('#viewport');await page.keyboard.down('KeyW');
    try{await page.waitForFunction(before=>{const p=window.officeViewer.state().position;return Math.hypot(p[0]-before[0],p[2]-before[2])>.015;},before,{timeout:10000,polling:100});}finally{await page.keyboard.up('KeyW');}
    const after=await page.evaluate(()=>window.officeViewer.state().position);const walkDistance=Math.hypot(before[0]-after[0],before[2]-after[2]);assert.ok(walkDistance>.01);
    await page.evaluate(()=>window.officeViewer.overview());
    const toggles=await page.evaluate(()=>{document.getElementById('hide-doors').click();const hidden=window.officeViewer.state().doorsHidden,racks=window.officeViewer.state().closetSuggestionVisible;document.getElementById('furniture').click();const empty=!window.officeViewer.state().furniture;document.getElementById('hide-doors').click();document.getElementById('furniture').click();return{hidden,empty,racks,restored:!window.officeViewer.state().closetSuggestionVisible};});
    assert.deepEqual(toggles,{hidden:true,empty:true,racks:true,restored:true});
    if(process.argv.includes('--capture'))await page.screenshot({path:new URL(variantId+'-overview.png',import.meta.url).pathname,timeout:60000});
    const lamp=await page.evaluate(()=>window.officeViewer.lampAperture());assert.ok(lamp.lampMeshCount>0);assert.equal(lamp.allRaysPass,true,variantId+' open lamp head aperture and LED/rim controls');
    report.variants.push({id:variantId,state,poses,textures,walkDistance,toggles,lamp,sourceLink:detail.source});
  }
  // Switch back to the cached alternative without resetting camera or navigation mode.
  await selectControl('view','room-b');const beforeSwitch=await page.evaluate(()=>window.officeViewer.state());
  await selectControl('variant',variantIds[0]);await page.waitForFunction(()=>window.officeViewer.ready()&&window.officeViewer.state().variant==='b-charcoal-slat',{timeout:120000});
  const afterSwitch=await page.evaluate(()=>window.officeViewer.state());assert.equal(afterSwitch.selectedView,beforeSwitch.selectedView);assert.equal(afterSwitch.mode,'walk');assert.deepEqual(afterSwitch.position,beforeSwitch.position);
  report.checks.push('Both alternatives load independently, switch in both directions, and preserve the selected camera.');
  await page.evaluate(()=>window.officeViewer.overview());
  const downloaded=page.waitForEvent('download');await page.locator('#save-view').click({force:true});const download=await downloaded;assert.match(download.suggestedFilename(),/^his-office-b-charcoal-slat-.*\.png$/);const png=await fs.readFile(await download.path());assert.ok(png.length>10000);assert.equal(png.subarray(0,8).toString('hex'),'89504e470d0a1a0a');report.exportPngBytes=png.length;
  report.checks.push('Save image exports the selected alternative as a valid PNG.');
  report.assetHashes=await page.evaluate(()=>window.OFFICE_EMBED?.assetHashes||null);
  if(standalone){
    const runtimeHashes=await page.evaluate(async()=>{
      const result={};for(const [id,assets]of Object.entries(window.OFFICE_EMBED.assets)){result[id]={};for(const[key,reference]of Object.entries(assets)){
        const bytesLength=Array.isArray(reference)?reference.reduce((total,hash)=>total+atob(window.OFFICE_EMBED.assetChunks[hash]).length,0):atob(reference).length;
        // Opaque about:blank can lack SubtleCrypto. Original embedded bytes are exported
        // to the test driver instead; the node-side comparison below is authoritative.
        result[id][key]=bytesLength;
      }}return result;
    });report.runtimeEmbeddedBytes=runtimeHashes;
    const html=await fs.readFile(new URL('../../his-office-viewer.html',import.meta.url),'utf8');
    const embed=JSON.parse(html.match(/window\.OFFICE_EMBED=([\s\S]*?);<\/script>/)[1]);
    for(const[id,assets]of Object.entries(embed.assets))for(const[key,reference]of Object.entries(assets)){
      const bytes=Array.isArray(reference)?Buffer.concat(reference.map(hash=>{const part=Buffer.from(embed.assetChunks[hash],'base64');assert.equal(crypto.createHash('sha256').update(part).digest('hex'),hash);return part;})):Buffer.from(reference,'base64');assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),report.assetHashes[id][key]);assert.equal(bytes.length,report.runtimeEmbeddedBytes[id][key]);
    }
    assert.deepEqual(report.requests,[]);report.checks.push('Every embedded GLB decodes to its sealed SHA-256, with no network requests.');
  }
  assert.deepEqual(report.errors,[]);
  report.checks.push('All camera poses/lenses, textures, native dimensions, orientations, controls, and keyboard walking pass for both alternatives.');
  await fs.writeFile(new URL(fileMode?'file-results.json':standalone?'offline-results.json':'source-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({checks:report.checks,errors:report.errors},null,2));
}catch(error){report.failure=error.stack;await fs.writeFile(new URL(fileMode?'file-failure.json':standalone?'offline-failure.json':'source-failure.json',import.meta.url),JSON.stringify(report,null,2)+'\n');throw error;}finally{await browser.close();}
