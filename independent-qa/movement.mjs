import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:800,height:650}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});
const rooms=[];
for(const id of await page.evaluate(()=>window.apartmentViewer.config.rooms.map(r=>r.id))){
 const checks=[];
 for(const key of ['KeyW','KeyA','KeyD']){
  await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);await page.click('#walk-mode');
  const before=await page.evaluate(()=>window.apartmentViewer.state().position);
  await page.keyboard.down(key);await page.waitForTimeout(1500);await page.keyboard.up(key);
  const after=await page.evaluate(()=>window.apartmentViewer.state().position);
  checks.push({key,before,after,distance:Math.hypot(before[0]-after[0],before[2]-after[2])});
 }
 rooms.push({id,checks});console.log(id,checks.map(c=>c.key+':'+c.distance.toFixed(3)).join(' '));
}
await page.evaluate(()=>{const v=window.apartmentViewer,r=v.config.rooms.find(r=>r.id==='basement-open');r.eye=[5.38,.195,-2.31];r.look=[2.0,.195,-2.31];v.goToRoom(r.id,true);});await page.click('#walk-mode');
const stairsBefore=await page.evaluate(()=>window.apartmentViewer.state());
await page.keyboard.down('KeyW');await page.waitForTimeout(11000);await page.keyboard.up('KeyW');
const stairsAfter=await page.evaluate(()=>window.apartmentViewer.state());
await fs.writeFile('/workspace/independent-qa/movement-results.json',JSON.stringify({errors,rooms,stairsBefore,stairsAfter},null,2));
console.log('STAIRS',JSON.stringify({before:stairsBefore.position,after:stairsAfter.position,floor:stairsAfter.activeFloor,errors}));await browser.close();
