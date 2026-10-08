import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});const page=await browser.newPage({viewport:{width:800,height:650}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});const rooms=[];
for(const id of await page.evaluate(()=>window.apartmentViewer.config.rooms.map(r=>r.id))){
 await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);await page.waitForTimeout(400);
 const before=await page.evaluate(()=>window.apartmentViewer.state().position);await page.keyboard.down('KeyW');await page.waitForTimeout(900);await page.keyboard.up('KeyW');const after=await page.evaluate(()=>window.apartmentViewer.state().position);
 rooms.push({id,before,after,distance:Math.hypot(before[0]-after[0],before[2]-after[2])});console.log(id,rooms.at(-1).distance.toFixed(3));
}
await fs.writeFile('/workspace/independent-qa/real-keyboard-results.json',JSON.stringify({errors,rooms},null,2));console.log('errors',JSON.stringify(errors));await browser.close();
