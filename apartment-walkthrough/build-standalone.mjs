import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
import { createHash } from 'node:crypto';

const root=dirname(fileURLToPath(import.meta.url));
const config=JSON.parse(await readFile(resolve(root,'assets/config.json'),'utf8'));
const assets={},assetHashes={};
for(const[key,path]of Object.entries(config.assets)) {
  if(!path)continue;
  try {const data=await readFile(resolve(root,'assets',path));assets[key]=data.toString('base64');assetHashes[key]=createHash('sha256').update(data).digest('hex');}
  catch(error){if(key==='scan')throw error;console.log(`Optional ${key} layer is absent.`);}
}
const source=await readFile(resolve(root,'app.js'),'utf8');
const imports=source.match(/^(?:import[^;]+;\s*)+/)[0];
const body=source.slice(imports.length);
const wrapped=`${imports}\n(async()=>{\n${body}\n})().catch(error=>{document.getElementById('load-detail').textContent='Could not open the model: '+error.message;console.error(error);});`;
const result=await build({stdin:{contents:wrapped,resolveDir:root,sourcefile:'app.js',loader:'js'},bundle:true,format:'iife',target:['chrome100','safari16','firefox110'],minify:true,write:false,legalComments:'inline'});
const code=result.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
const css=await readFile(resolve(root,'style.css'),'utf8');
let html=await readFile(resolve(root,'index.html'),'utf8');
html=html.replace(/<link rel="stylesheet" href="style.css">/,()=>`<style>${css}</style>`).replace(/\s*<script type="importmap">[\s\S]*?<\/script>/,'');
const embed=JSON.stringify({config,assets,assetHashes}).replace(/</g,'\\u003c');
html=html.replace('<script type="module" src="app.js"></script>',()=>`<script>window.APARTMENT_EMBED=${embed};</script>\n<script>${code}</script>`);
const output=process.argv[2] || resolve(root,'..','apartment-walkthrough.html');
await writeFile(output,html);
console.log(`Standalone viewer: ${output} (${(Buffer.byteLength(html)/1048576).toFixed(1)} MiB)`);
