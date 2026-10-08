import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:800,height:600}});await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>window.apartmentViewer?.ready(),{timeout:120000});
const report=await page.evaluate(()=>{
 const v=window.apartmentViewer;
 function step(key,n){const c=document.querySelector('#viewport canvas');c.dispatchEvent(new KeyboardEvent('keydown',{code:key,bubbles:true}));for(let i=0;i<n;i++)v.advanceWalk(.025);c.dispatchEvent(new KeyboardEvent('keyup',{code:key,bubbles:true}));return v.state();}
 const b=v.config.rooms.find(r=>r.id==='basement-open');b.eye=[5.38,.195,-2.31];b.look=[2,.195,-2.31];v.goToRoom(b.id,true);const start=v.state(),ascent=step('KeyW',132),egress=step('KeyA',24);
 const u=v.config.rooms.find(r=>r.id==='entry');u.eye=[1.92,3.155,-2.31];u.look=[5.5,3.155,-2.31];v.goToRoom(u.id,true);const descent=step('KeyW',132);return {start,ascent,egress,descent};
});await fs.writeFile('/workspace/independent-qa/stair-roundtrip.json',JSON.stringify(report,null,2));console.log(JSON.stringify(Object.fromEntries(Object.entries(report).map(([k,v])=>[k,{position:v.position,floor:v.activeFloor}])),null,2));await browser.close();
