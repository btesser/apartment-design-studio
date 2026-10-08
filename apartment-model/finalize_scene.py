import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/workspace/apartment-model')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'integrated.blend'))
s=bpy.context.scene;lights=bpy.data.collections.get('04 Preview Lights and Cameras')
# Apply the final source-audited furniture coordinates exactly.
for name,x in [('his-slim-console',-6.70),('her-fireplace-blush-art',5.61)]:
 o=bpy.data.objects.get(name)
 if o:o.location.x=x
dresser=bpy.data.collections.get('08 Optional Large Dresser — clearance conflict')
if dresser:dresser.hide_render=False;dresser.hide_viewport=False
love=bpy.data.objects.get('her-loveseat')
if love:love.location.y=-1.80
# Provisional entry staging is separately named, with source-based sizes and its own confidence metadata.
with bpy.data.libraries.load('/workspace/design-fidelity/entry-design.blend',link=False) as (src,dst):dst.collections=[n for n in src.collections if n.startswith('Entry design')]
for c in dst.collections:
 if c:s.collection.children.link(c)
entry=dst.collections[0]
# Low-energy ceiling fills represent existing room lighting, improve visibility without moving geometry.
geo=json.load(open('/workspace/geometry-audit/geometry.json'))
for r in geo['rooms']:
 if r['id']=='bedroom-flex':continue
 p=r['outline'];x=sum(q[0] for q in p)/len(p);y=sum(q[1] for q in p)/len(p);z=r['floor_z_m']+1.05
 bpy.ops.object.light_add(type='AREA',location=(x,y,z));o=bpy.context.object;o.name='FILL '+r['id'];o.rotation_euler=(math.pi,0,0);o.data.energy=90;o.data.size=3.0;o.data.use_shadow=False
 for old in list(o.users_collection):old.objects.unlink(o)
 lights.objects.link(o)
# Bedroom is a curtained zone; its own ceiling light remains essential when the divider is closed.
bpy.ops.object.light_add(type='AREA',location=(-1.65,-1.15,1.10));o=bpy.context.object;o.name='LIGHT bedroom-flex';o.data.energy=230;o.data.size=1.8
for old in list(o.users_collection):old.objects.unlink(o)
lights.objects.link(o)
bpy.ops.object.light_add(type='AREA',location=(-1.65,-1.10,-.2));o=bpy.context.object;o.name='FILL bedroom-flex';o.rotation_euler=(math.pi,0,0);o.data.energy=75;o.data.size=2.0;o.data.use_shadow=False
for old in list(o.users_collection):old.objects.unlink(o)
lights.objects.link(o)
# Camera positions remain on accessible floor at the bed's feet, below the observed local ceiling.
poses={'bedroom-flex-a':((-.45,.10,.10),(-1.43,-1.6,-.5)),'bedroom-flex-b':((-3.45,-.10,.10),(-1.43,-1.6,-.5))}
meta=json.load(open(ROOT/'render-cameras.json'))
for name,(eye,target) in poses.items():
 o=bpy.data.objects['CAM '+name];o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();meta[name].update({'eye_blender_m':eye,'target_blender_m':target,'eye_gltf_m':[eye[0],eye[2],-eye[1]],'target_gltf_m':[target[0],target[2],-target[1]]})
# Texture-free raw-source shelf heaths remain separate confidence geometry once available.
hearth=ROOT/'hearth-geometry.json'
if hearth.exists():
 h=json.load(open(hearth));verts=h['vertices'];faces=h['faces'];me=bpy.data.meshes.new('Source-sampled Her hearth');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Observed Her low hearth lip',me);bpy.data.collections['05 Observed Fixed Fixture Proxies'].objects.link(o);o.data.materials.append(bpy.data.materials.get('Fixture porcelain'));o['confidence']='scan-supported shallow hull infill: actual raised patch observed0.087m², filled hull0.430m²; missingsupport inferred'
json.dump(meta,open(ROOT/'render-cameras.json','w'),indent=2)
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;
if hasattr(s.eevee,'use_shadow_jitter'):s.eevee.use_shadow_jitter=False
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95
s.camera=bpy.data.objects['CAM living-a']
# Final clean export inventory keeps original scan and inferred utility rooms independently hidden.
cols=[bpy.data.collections['03 Clean Measured Shell — inferred finishes'],bpy.data.collections['05 Observed Fixed Fixture Proxies'],bpy.data.collections.get('Amy proposed furniture — registered placement'),dresser,entry]
bpy.ops.object.select_all(action='DESELECT')
for c in cols:
 if c:
  for o in c.all_objects:
   if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'integrated-apartment.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_image_format='JPEG',export_jpeg_quality=92,export_cameras=False,export_lights=False,export_apply=True)
# Updated fireplaces and hearth should also be available to the modular viewer.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.collections['05 Observed Fixed Fixture Proxies'].objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'observed-fixtures.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_image_format='JPEG',export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'integrated.blend'))
json.dump({'mesh_counts':{c.name:sum(o.type=='MESH' for o in c.all_objects) for c in cols if c},'item_parent_names':[o.name for c in cols if c for o in c.all_objects if o.type=='EMPTY'],'clearance_warning':['bedroom-large-dresser leaves approximately 0.47 m foot aisle; drawer-use conflict remains unresolved; separate collection toggles dresser off'],'utility_layer':'06 Unrecorded Utility Interiors — Listing Inference','default_layers':[c.name for c in cols if c]},open(ROOT/'integrated-inventory.json','w'),indent=2)
print('FINAL_SCENE_READY')
