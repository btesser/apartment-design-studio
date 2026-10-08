import {chromium} from '/workspace/apartment-walkthrough/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
const page=await browser.newPage({viewport:{width:1440,height:1000}});
await page.goto('http://127.0.0.1:8773');await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:180000});
await page.evaluate(()=>window.officeViewer.switchVariant('c-ink-studio'));await page.waitForFunction(()=>window.officeViewer.ready()&&window.officeViewer.state().variant==='c-ink-studio',{timeout:180000});
const proof=await page.evaluate(async()=>{
 const THREE=await import('./vendor/three.module.js');const v=window.officeViewer;v.goToView('room-a');v.setDeskHeight(1.24206);v.scene.updateMatrixWorld(true);v.camera.updateMatrixWorld(true);
 const ray=new THREE.Raycaster();const result=[];
 for(const [x,y] of [[720,500],[700,510],[740,525],[715,380]]){ray.setFromCamera(new THREE.Vector2(x/1440*2-1,1-y/1000*2),v.camera);const hits=ray.intersectObject(v.scene,true).filter(h=>{for(let p=h.object;p;p=p.parent)if(!p.visible)return false;return true;});result.push({pixel:[x,y],hits:hits.slice(0,3).map(h=>({name:h.object.name,point:h.point.toArray(),distance:h.distance}))});}
 const equipment=[];v.scene.traverse(o=>{if(o.isMesh&&/monitor|display|keyboard/i.test(o.name)){const b=new THREE.Box3().setFromObject(o);equipment.push({name:o.name,min:b.min.toArray(),max:b.max.toArray()});}});
 return {result,equipment,height:v.deskLiftProof().height_m};
});await fs.writeFile('/workspace/his-office-pinterest/qa/final-variants/viewer-standing-visual-diagnostic.json',JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify(proof));
}finally{await browser.close();}
