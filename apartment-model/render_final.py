import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/workspace/apartment-model');OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'integrated.blend'))
s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
room_names=['living','his-office','her-office','entry','bedroom-flex','basement-open','music-gym','kitchen','bathroom']
names=[r+'-'+a for r in room_names for a in ['a','b']]+['stairs-a']
subset=names[int(args[0]):int(args[1])] if len(args)>1 else names
for name in subset:
 if (OUT/(name+'.jpg')).exists():
  print('RENDER_CACHED_UNCHANGED',name,flush=True);continue
 s.camera=bpy.data.objects['CAM '+name];s.render.filepath=str(OUT/(name+'.jpg'));bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)
if args and len(args)>2 and args[2]=='plans':
 presentation=bpy.data.collections.get('09 Presentation Window Backgrounds')
 if presentation:presentation.hide_render=True
 plancol=bpy.data.collections.new('Temporary roofless plan cuts');s.collection.children.link(plancol)
 bpy.ops.object.camera_add(location=(0,0,16));cam=bpy.context.object;cam.name='CAM plan';cam.data.type='ORTHO';cam.data.ortho_scale=18;cam.rotation_euler=(0,0,0);s.camera=cam;s.render.resolution_x=1800;s.render.resolution_y=700
 orig={o.name:o.hide_render for o in bpy.data.objects}
 allowed={o.name for c in bpy.data.collections if c.name.startswith(('03 ','05 ','Amy proposed furniture','08 Optional','Entry design')) for o in c.all_objects}
 for level,minz,maxz in [('upper',1.30,4.70),('lower',-1.70,1.30)]:
  for o in list(bpy.data.objects):
   if o.type!='MESH' or o.name not in allowed:continue
   if orig[o.name]:continue
   b=[o.matrix_world@Vector(v) for v in o.bound_box];lo=min(p.z for p in b);hi=max(p.z for p in b)
   ceiling='ceiling' in o.name.lower();wall=(('wall' in o.name.lower() or 'partition' in o.name.lower() or 'entry side' in o.name.lower()) and hi-lo>1.3)
   if lo>maxz or hi<minz or ceiling or 'soffit' in o.name.lower() or o.name.startswith('Sky outside window') or 'chandelier' in o.name.lower():o.hide_render=True
   elif wall:
    # Roofless plans keep short wall slices; original source untouched via temporary edit copy.
    dup=o.copy();dup.data=o.data.copy();plancol.objects.link(dup);dup.name='Plan cut '+o.name
    import bmesh
    bm=bmesh.new();bm.from_mesh(dup.data)
    plane_z=(1.95 if level=='upper' else -.94)
    localpoint=dup.matrix_world.inverted()@Vector((0,0,plane_z));normal=dup.matrix_world.inverted().to_3x3()@Vector((0,0,1));geom=list(bm.verts)+list(bm.edges)+list(bm.faces);bmesh.ops.bisect_plane(bm,geom=geom,plane_co=localpoint,plane_no=normal,clear_outer=True,clear_inner=False);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(dup.data);bm.free();o.hide_render=True
  s.render.filepath=str(OUT/(level+'-plan.jpg'));bpy.ops.render.render(write_still=True);print('PLAN_DONE',level,flush=True)
  for o in list(bpy.data.objects):
   if o.name.startswith('Plan cut '):bpy.data.objects.remove(o,do_unlink=True)
   elif o.name in orig:o.hide_render=orig[o.name]
print('FINAL_RENDER_BATCH_COMPLETE',flush=True)
