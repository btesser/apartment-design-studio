import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {build} from 'esbuild';
const root=dirname(fileURLToPath(import.meta.url));
const config=JSON.parse(await readFile(resolve(root,'assets/config.json'),'utf8'));
const assets={},assetHashes={},assetChunks={};
for(const variant of config.variants){
  assets[variant.id]={};assetHashes[variant.id]={};
  for(const[key,name]of Object.entries(variant.config.assets)){
    const data=await readFile(resolve(root,'assets',name));
    if(data.readUInt32LE(0)!==0x46546c67||data.readUInt32LE(4)!==2||data.readUInt32LE(8)!==data.length)throw new Error('Invalid canonical GLB: '+name);
    const binaryStart=20+data.readUInt32LE(12);
    // Preserve every canonical GLB byte. Shared BIN chunks are embedded once;
    // their alternative-specific JSON/header bytes are kept independently.
    const parts=[data.subarray(0,binaryStart),data.subarray(binaryStart)];
    assets[variant.id][key]=parts.map(part=>{const hash=createHash('sha256').update(part).digest('hex');assetChunks[hash]??=part.toString('base64');return hash;});
    assetHashes[variant.id][key]=createHash('sha256').update(data).digest('hex');
  }
}
const source=await readFile(resolve(root,'app.js'),'utf8');
const imports=source.match(/^(?:import[^;]+;\s*)+/)[0],body=source.slice(imports.length);
const wrapped=`${imports}\n(async()=>{${body}\n})().catch(error=>{document.getElementById('loading-detail').textContent='Could not open this model: '+error.message;console.error(error);});`;
const result=await build({stdin:{contents:wrapped,resolveDir:root,sourcefile:'app.js',loader:'js'},bundle:true,format:'iife',minify:true,target:['chrome100','safari16','firefox110'],write:false,legalComments:'inline'});
const code=result.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
const css=await readFile(resolve(root,'style.css'),'utf8');
let html=await readFile(resolve(root,'index.html'),'utf8');
html=html.replace('<link rel="stylesheet" href="style.css">',()=>`<style>${css}</style>`).replace(/\s*<script type="importmap">[\s\S]*?<\/script>/,'');
const embed=JSON.stringify({config,assets,assetHashes,assetChunks}).replace(/</g,'\\u003c');
html=html.replace('<script type="module" src="app.js"></script>',()=>`<script>window.OFFICE_EMBED=${embed};</script><script>${code}</script>`);
const output=process.argv[2]||resolve(root,'..','his-office-viewer.html');
await writeFile(output,html);console.log(`Standalone B/C office viewer: ${output} (${(Buffer.byteLength(html)/1048576).toFixed(2)} MiB)`);
