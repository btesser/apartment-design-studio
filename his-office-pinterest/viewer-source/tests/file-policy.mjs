import fs from 'node:fs/promises';
import {chromium} from 'playwright';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const result={scope:'Direct file navigation policy only. No furniture or layout validation.',url:new URL('../../his-office-viewer.html',import.meta.url).href,networkRequests:[],errors:[]};
try{
  const page=await browser.newPage({viewport:{width:1100,height:800}});
  page.on('pageerror',e=>result.errors.push(e.message));await page.route('http{,s}://**/*',route=>{result.networkRequests.push(route.request().url());return route.abort();});
  try{await page.goto(result.url,{timeout:60000});await page.waitForFunction(()=>window.officeViewer?.ready(),{timeout:180000});result.navigation='passed';result.viewerReady=true;}
  catch(e){result.navigation='blocked or failed';result.observedError=e.message;result.viewerReady=false;}
  await fs.writeFile(new URL('file-policy-result.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
