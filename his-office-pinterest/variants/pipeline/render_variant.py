import argparse,bpy,json,sys,hashlib,time
from pathlib import Path
P=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=['b-charcoal-slat','c-ink-studio'],required=True);parser.add_argument('--preview',action='store_true');parser.add_argument('--views',nargs='+',default=['room-a','room-b','room-c']);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=P/args.variant/'model';scene_file=ROOT/'his-office-design.blend';scenehash=hashlib.sha256(scene_file.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(scene_file));s=bpy.context.scene
s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=95
out=ROOT/('previews'if args.preview else'renders');out.mkdir(exist_ok=True)
if args.preview:s.render.resolution_x=1000;s.render.resolution_y=694;s.cycles.samples=16;s.cycles.adaptive_threshold=.05;s.cycles.adaptive_min_samples=8
proof=ROOT/('preview-provenance.json'if args.preview else'render-provenance.json');records=json.loads(proof.read_text())if proof.exists()else{}
for id in args.views:
 s.camera=bpy.data.objects['CAM '+id];s.render.filepath=str(out/(id+'.jpg'));start=time.time();bpy.ops.render.render(write_still=True);path=Path(s.render.filepath)
 records[id]={'filename':str(path.relative_to(ROOT)),'scene_sha256':scenehash,'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixels':[s.render.resolution_x,s.render.resolution_y],'maximum_samples':s.cycles.samples,'minimum_samples':s.cycles.adaptive_min_samples,'adaptive_threshold':s.cycles.adaptive_threshold,'exposure':s.view_settings.exposure,'engine':'CyclesCPU','denoising':False,'elapsed_seconds':time.time()-start,'camera':'CAM '+id}
 proof.write_text(json.dumps(records,indent=2));print('VIEW_READY',args.variant,id,flush=True)
if hashlib.sha256(scene_file.read_bytes()).hexdigest()!=scenehash:raise RuntimeError('Frozen scene changed while rendering')
