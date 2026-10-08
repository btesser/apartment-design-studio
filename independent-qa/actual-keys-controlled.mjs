import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});const page=await browser.newPage({viewport:{width:800,height:650}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});const rooms=[];
for(const id of await page.evaluate(()=>window.apartmentViewer.config.rooms.map(r=>r.id))){
 await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);
 const before=await page.evaluate(()=>window.apartmentViewer.state().position);
 await page.keyboard.down('KeyW');
 const pressed=await page.evaluate(()=>window.apartmentViewer.pressedKeys());
 await page.evaluate(()=>{for(let i=0;i<20;i++)window.apartmentViewer.advanceWalk(.025);});
 await page.keyboard.up('KeyW');
 const after=await page.evaluate(()=>window.apartmentViewer.state().position);const cleared=await page.evaluate(()=>window.apartmentViewer.pressedKeys());
 rooms.push({id,before,after,keydown_received:pressed.includes('KeyW'),keyup_received:!cleared.includes('KeyW'),distance:Math.hypot(before[0]-after[0],before[2]-after[2])});console.log(id,JSON.stringify(rooms.at(-1)));
}
await fs.writeFile('/workspace/independent-qa/actual-keys-controlled-results.json',JSON.stringify({method:'Real Playwright keyboard.down/up events plus 20 controlled 25ms collision-controller steps. Wall-clock render speed is deliberately separate.',errors,rooms},null,2));await browser.close();
