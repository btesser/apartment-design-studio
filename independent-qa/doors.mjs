import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:800,height:650}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});
const doors=await page.evaluate(()=>{
 const v=window.apartmentViewer;const routes=[
 {id:'his-office-to-living',room:'his-office',eye:[-3.45,3.155,2.20],look:[-2,3.155,2.20],steps:32,wallX:-3.08},
 {id:'living-to-her-office',room:'living',eye:[3.20,3.115,.40],look:[4.8,3.115,.40],steps:36,wallX:3.62},
 {id:'living-to-bathroom',room:'living',eye:[-1.48,3.115,-.93],look:[.2,3.115,-.93],steps:32,wallX:-1.24},
 {id:'music-to-bedroom',room:'music-gym',eye:[-4.15,.135,1.75],look:[-2.9,.135,1.75],steps:32,wallX:-3.8}];
 return routes.map(route=>{const r=v.config.rooms.find(r=>r.id===route.room);r.eye=route.eye;r.look=route.look;v.goToRoom(r.id,true);const before=v.state().position;const c=document.querySelector('#viewport canvas');c.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyW',bubbles:true}));for(let i=0;i<route.steps;i++)v.advanceWalk(.025);c.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyW',bubbles:true}));const after=v.state().position;return {id:route.id,before,after,wallX:route.wallX,crossed:before[0]<route.wallX&&after[0]>route.wallX};});
});await fs.writeFile('/workspace/independent-qa/door-approaches.json',JSON.stringify({errors,doors},null,2));console.log(JSON.stringify({errors,doors},null,2));await browser.close();
