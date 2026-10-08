import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1200,height:850}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});
const rooms=[];
for(const id of await page.evaluate(()=>window.apartmentViewer.config.rooms.map(r=>r.id))){
 await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);await page.waitForTimeout(300);
 await page.screenshot({path:`/workspace/independent-qa/final-${id}.png`});
 const tests=[];
 for(const key of ['KeyW','KeyA','KeyD']){
  await page.evaluate(id=>window.apartmentViewer.goToRoom(id,true),id);
  await page.evaluate(key=>document.querySelector('#viewport canvas').dispatchEvent(new KeyboardEvent('keydown',{code:key,bubbles:true})),key);
  const before=await page.evaluate(()=>window.apartmentViewer.state().position);
  await page.evaluate(()=>{for(let i=0;i<20;i++)window.apartmentViewer.advanceWalk(.025);});
  await page.evaluate(key=>document.querySelector('#viewport canvas').dispatchEvent(new KeyboardEvent('keyup',{code:key,bubbles:true})),key);
  const after=await page.evaluate(()=>window.apartmentViewer.state().position);
  tests.push({key,before,after,distance:Math.hypot(before[0]-after[0],before[2]-after[2])});
 }
 rooms.push({id,tests});console.log(id,tests.map(t=>t.key+':'+t.distance.toFixed(3)).join(' '));
}
await page.evaluate(()=>{const v=window.apartmentViewer,r=v.config.rooms.find(r=>r.id==='basement-open');r.eye=[5.38,.195,-2.31];r.look=[2.0,.195,-2.31];v.goToRoom(r.id,true);});
const stairsBefore=await page.evaluate(()=>window.apartmentViewer.state());
await page.evaluate(()=>{document.querySelector('#viewport canvas').dispatchEvent(new KeyboardEvent('keydown',{code:'KeyW',bubbles:true}));for(let i=0;i<132;i++)window.apartmentViewer.advanceWalk(.025);document.querySelector('#viewport canvas').dispatchEvent(new KeyboardEvent('keyup',{code:'KeyW',bubbles:true}));});
const stairsAfter=await page.evaluate(()=>window.apartmentViewer.state());
await fs.writeFile('/workspace/independent-qa/final-browser-results.json',JSON.stringify({errors,rooms,stairsBefore,stairsAfter},null,2));
console.log('STAIRS',JSON.stringify({before:stairsBefore.position,after:stairsAfter.position,floor:stairsAfter.activeFloor,errors}));await browser.close();
