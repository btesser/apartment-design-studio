import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});
console.log('Initial',JSON.stringify(await page.evaluate(()=>window.apartmentViewer.state())));
const ids=await page.evaluate(()=>window.apartmentViewer.config.rooms.map(r=>r.id));
const rooms=[];
for(const id of ids){
 await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);await page.waitForTimeout(200);
 await page.screenshot({path:`/workspace/independent-qa/room-${id}.png`});
 const before=await page.evaluate(()=>window.apartmentViewer.state().position);
 await page.locator('#walk-mode').click();await page.keyboard.down('KeyD');await page.waitForTimeout(250);await page.keyboard.up('KeyD');
 const after=await page.evaluate(()=>window.apartmentViewer.state().position);
 rooms.push({id,before,after,distance:Math.hypot(before[0]-after[0],before[2]-after[2])});
}
await fs.writeFile('/workspace/independent-qa/browser-tour.json',JSON.stringify({errors,rooms},null,2));
console.log(JSON.stringify({errors,rooms},null,2));await browser.close();
