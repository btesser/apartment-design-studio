import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';

const target=process.argv[2] || 'http://127.0.0.1:8765';
const inline=process.argv.includes('--standalone');
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const report={target:inline?'Embedded standalone, network blocked':target,errors:[],requests:[],checks:[],rooms:[]};
try {
  const page=await browser.newPage({viewport:{width:1200,height:850}});
  page.on('pageerror',error=>report.errors.push(error.message));
  if(inline){await page.route('http{,s}://**/*',route=>{report.requests.push(route.request().url());return route.abort();});await page.setContent(await fs.readFile(new URL('../../apartment-walkthrough.html',import.meta.url),'utf8'),{timeout:60000});}
  else await page.goto(target);
  await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});
  const state=await page.evaluate(()=>window.apartmentViewer.state());
  report.assetHashes=await page.evaluate(()=>window.APARTMENT_EMBED?.assetHashes||null);
  for(const layer of ['scan','architecture','repairs','furniture','fixtures','dresser','utilities','entry'])assert.equal(state.assets[layer],'loaded');
  assert.equal(state.layers.architecture,true);assert.equal(state.layers.scan,false);assert.equal(state.layers.furniture,true);
  assert.ok(Math.abs(state.scanBounds[0][0]+8.445853233337402)<1e-5);assert.ok(Math.abs(state.scanBounds[1][1]-4.744903564453125)<1e-5);
  assert.equal(state.layers.dresser,true);assert.equal(state.layers.entry,true);assert.equal(state.layers.utilities,false);
  report.checks.push('All eight layers loaded; scan native bounds preserved; proposal dresser included; unrecorded utility layer hidden.');
  await page.click('#walk-mode');
  const before=await page.evaluate(()=>window.apartmentViewer.state().position);
  await page.keyboard.down('KeyW');await page.waitForTimeout(700);await page.keyboard.up('KeyW');
  const after=await page.evaluate(()=>window.apartmentViewer.state().position);
  assert.ok(Math.hypot(before[0]-after[0],before[2]-after[2])>.01,'Walk keys must move from the default clear viewpoint.');
  report.checks.push('W key moves the eye-level camera from the default viewpoint.');
  const roomIds=await page.evaluate(()=>window.apartmentViewer.config.rooms.map(r=>r.id));
  for(const id of roomIds){await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);const s=await page.evaluate(()=>window.apartmentViewer.state());assert.equal(s.activeRoom,id);assert.equal(s.mode,'walk');report.rooms.push(s);}
  report.checks.push(`${roomIds.length} room teleports selected their floor and walk camera.`);
  await page.evaluate(()=>window.apartmentViewer.setFloor('all'));
  assert.equal(await page.evaluate(()=>window.apartmentViewer.state().mode),'orbit');
  // Trigger native checkbox click handlers in one turn. Software WebGL can
  // block compositor frames while the original scan textures are uploaded.
  const transitions=await page.evaluate(()=>{
    const scan=document.getElementById('scan'),highlight=document.getElementById('highlight'),architecture=document.getElementById('architecture');
    if(!scan.checked)scan.click();const architectureOff=!window.apartmentViewer.state().layers.architecture;
    if(!highlight.checked)highlight.click();const repairsOn=window.apartmentViewer.state().layers.repairs;
    if(!architecture.checked)architecture.click();const scanOff=!window.apartmentViewer.state().layers.scan;
    return {architectureOff,repairsOn,scanOff};
  });
  assert.deepEqual(transitions,{architectureOff:true,repairsOn:true,scanOff:true});
  report.checks.push('Both-floor overview and independent evidence/design layer toggles work.');
  if(inline)assert.equal(report.requests.length,0,'Standalone should not make network requests.');
  assert.deepEqual(report.errors,[]);
  report.checks.push('No browser errors'+(inline?' and no external requests.':'.'));
  await fs.writeFile(new URL(inline?'standalone-results.json':'browser-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({checks:report.checks,errors:report.errors},null,2));
}finally{await browser.close();}
