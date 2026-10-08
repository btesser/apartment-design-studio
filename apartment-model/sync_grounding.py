import bpy,json
from pathlib import Path
ROOT=Path('/workspace/apartment-model');bpy.ops.wm.open_mainfile(filepath=str(ROOT/'integrated.blend'))
s=bpy.context.scene;changes=[]
for o in bpy.data.objects:
 if o.type!='EMPTY':continue
 if o.get('room')=='bedroom-flex':o.location.z+=.03;changes.append({'item':o.name,'delta_z_m':.03,'new_z_m':o.location.z})
 elif o.name in ['entry-gold-console','entry-faceted-mirror','entry-rattan-shoe-cabinet','entry-patchwork-rug']:o.location.z-=.04;changes.append({'item':o.name,'delta_z_m':-.04,'new_z_m':o.location.z})
cols=[c for c in bpy.data.collections if c.name.startswith(('03 ','05 ','Amy proposed furniture','08 Optional','Entry design'))]
bpy.ops.object.select_all(action='DESELECT')
for c in cols:
 for o in c.all_objects:
  if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'integrated-apartment.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_apply=True,export_image_format='JPEG',export_jpeg_quality=92,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'integrated.blend'))
json.dump({'reason':'Exact visual alignment with modeled architectural floor: entry Z1.535m, lower zone Z−1.385m; source raw floor modes remain separate','changes':changes,'canonical_furniture_stamp':'2026-10-07 23:15:56UTC','canonical_entry_stamp':'2026-10-07 23:15:33UTC'},open(ROOT/'grounding-corrections.json','w'),indent=2)
print('GROUNDING_SYNC_COMPLETE',len(changes))
