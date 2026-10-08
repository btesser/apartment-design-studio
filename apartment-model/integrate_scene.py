import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/workspace/apartment-model');OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene-base.blend'))
s=bpy.context.scene
arch=bpy.data.collections.get('03 Clean Measured Shell — inferred finishes');fix=bpy.data.collections.get('05 Observed Fixed Fixture Proxies')
raw=bpy.data.collections.get('01 Retained Scan — original scale');rep=bpy.data.collections.get('02 Conservative Architecture Repairs');unc=bpy.data.collections.get('06 Unrecorded Utility Interiors — Listing Inference')
for c in [raw,rep,unc]:c.hide_viewport=True;c.hide_render=True
for c in [arch,fix]:c.hide_viewport=False;c.hide_render=False
# Add recorded-floor-derived connecting floor strips rather than leaving holes between schematic room polygons.
for pp in json.load(open(ROOT/'connected-floor-infill.json')):
 v=[];f=[]
 for tri in pp['triangles']:
  i=len(v);v.extend([(x,y,pp['z']) for x,y in tri]);f.append((i,i+1,i+2))
 me=bpy.data.meshes.new(pp['name']);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(pp['name'],me);arch.objects.link(o)
 o.data.materials.append(bpy.data.materials.get('Reconstructed upper wood' if pp['level']=='upper' else 'Reconstructed lower tile'));uv=me.uv_layers.new(name='MetricProjection')
 for p in me.polygons:
  for li in p.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.55,q.y*.55)
 o['confidence']='Floor extent observed in original mesh; flattened continuation inferred'
# Correct anisotropic brick tile scale on both clean shell and repair backs.
for c in [arch,rep]:
 for o in c.objects:
  if o.type!='MESH' or not any(m.name.startswith('Reconstructed exposed brick') for m in o.data.materials):continue
  uv=o.data.uv_layers.active
  if not uv:continue
  for p in o.data.polygons:
   n=o.matrix_world.to_3x3()@p.normal
   for li in p.loop_indices:
    q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.714,q.z*1.667)
# Preserve photographed closed fireplaces, not newly invented functional openings.
white=bpy.data.materials.get('Fixture porcelain')
def box(name,pos,dim,m,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);return o
for name,x,w in [('HIS',-5.31,.62),('HER',5.61,.82)]:
 o=box(name+' existing fireplace closed panel',(x,-2.735,1.575+.39),(w,.06,.78),white,fix);o['confidence']='Center/opening width measured from raw scan wall orthographic; closed white panel form approximate'
 box(name+' fireplace trim top',(x,-2.68,1.575+.83),(w+.10,.10,.075),white,fix)
 for xx in [x-w/2-.025,x+w/2+.025]:box(name+' fireplace trim side',(xx,-2.68,1.575+.41),(.055,.10,.86),white,fix)
# Append native source furniture material/mesh exactly, keeping proposed dresser optional.
with bpy.data.libraries.load('/workspace/apartment-furniture/furniture.blend',link=False) as (src,dst):
 dst.collections=[n for n in src.collections if n.startswith('Amy proposed furniture')]
for c in dst.collections:
 if c:s.collection.children.link(c)
furn=dst.collections[0]
optional=bpy.data.collections.new('08 Optional Large Dresser — clearance conflict');s.collection.children.link(optional)
for o in list(furn.objects):
 if o.name=='bedroom-large-dresser' or o.name.startswith('bedroom-large-dresser::'):
  furn.objects.unlink(o);optional.objects.link(o)
optional.hide_render=True;optional.hide_viewport=True
# Presentation-only sky backdrops are placed beyond the preserved glazing; no geometry normalizing.
present=bpy.data.collections.new('09 Presentation Window Backgrounds');s.collection.children.link(present)
sky=bpy.data.materials.new('Presentation daylight');sky.use_nodes=True;ns=sky.node_tree.nodes;ns.clear();e=ns.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.63,.76,.88,1);e.inputs['Strength'].default_value=.80;o=ns.new('ShaderNodeOutputMaterial');sky.node_tree.links.new(e.outputs[0],o.inputs['Surface'])
for x,ya,yb in [(-8.24,-1.05,.10),(8.14,-2.48,-1.44),(8.14,-.57,.39),(-8.24,1.18,2.17)]:box('Sky outside window',(x,(ya+yb)/2,3.30),(.012,yb-ya,1.9),sky,present)
# Wider source-room cameras are matched across views; geometry is identical in every image.
lightcol=bpy.data.collections.get('04 Preview Lights and Cameras')
def cam(name,eye,target,lens=23):
 o=bpy.data.objects.get('CAM '+name)
 if o is None:
  bpy.ops.object.camera_add(location=eye);o=bpy.context.object;o.name='CAM '+name
  for cc in list(o.users_collection):cc.objects.unlink(o)
  lightcol.objects.link(o)
 o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='PERSP';o.data.lens=lens;o.data.clip_start=.025;o.data.clip_end=100
 return o
poses={
 'living-a':((2.88,-.35,3.05),(-.60,-1.65,2.60),21),
 'living-b':((-2.68,-.31,3.05),(1.50,-1.38,2.60),21),
 'his-office-a':((-3.48,-2.10,3.08),(-6.10,-.28,2.65),21),
 'his-office-b':((-7.33,-2.11,3.08),(-4.87,-.32,2.64),21),
 'her-office-a':((4.44,-2.30,3.10),(6.22,-.17,2.67),21),
 'her-office-b':((7.35,-.38,3.10),(5.22,-1.54,2.70),21),
 'entry-a':((3.34,1.46,3.06),(1.50,.55,2.65),21),
 'entry-b':((1.59,.42,3.06),(3.38,1.30,2.65),21),
 'bedroom-flex-a':((-.05,.25,.15),(-1.55,-1.25,-.15),21),
 'bedroom-flex-b':((-3.40,.29,.15),(-1.48,-1.48,-.20),21),
 'basement-open-a':((.58,-2.13,.18),(3.9,-.25,-.25),21),
 'basement-open-b':((6.95,-1.30,.18),(2.00,-.52,-.25),21),
 'music-gym-a':((-4.26,-2.06,.12),(-6.25,-.25,-.35),21),
 'music-gym-b':((-7.04,-2.12,.12),(-4.55,-.25,-.35),21),
 'kitchen-a':((-2.03,1.85,3.09),(-6.85,1.56,2.65),21),
 'kitchen-b':((-7.36,2.06,3.09),(-2.17,1.70,2.65),21),
 'bathroom-a':((-1.09,.85,3.08),(.54,2.07,2.55),18),
 'bathroom-b':((.94,2.44,3.08),(-.46,.84,2.55),18),
 'stairs-a':((5.86,1.47,.35),(2.25,2.3,1.17),21)}
for name,(eye,target,lens) in poses.items():cam(name,eye,target,lens)
# Reusable renderer metadata; every image has original-world pose and physical lens.
meta={name:{'room':name.rsplit('-',1)[0],'eye_blender_m':eye,'target_blender_m':target,'eye_gltf_m':[eye[0],eye[2],-eye[1]],'target_gltf_m':[target[0],target[2],-target[1]],'lens_mm':lens,'sensor_width_mm':36,'resolution':[1440,1000],'source_scene':'integrated.blend','renderer':'EEVEE raster renderer; no generative image edits'} for name,(eye,target,lens) in poses.items()}
json.dump(meta,open(ROOT/'render-cameras.json','w'),indent=2)
# Raster rendering provides deterministic clean contours with modest samples in this CPU environment.
s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
if hasattr(s,'eevee'):s.eevee.taa_render_samples=16
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.camera=bpy.data.objects['CAM living-a']
# Export measured shell, observed fixtures, and furniture as clean native coordinates. Retained scan untouched in separate collection.
def export(path,cols):
 bpy.ops.object.select_all(action='DESELECT')
 for c in cols:
  for o in c.all_objects:
   if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/path),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_image_format='JPEG',export_jpeg_quality=92,export_cameras=False,export_lights=False)
export('architectural-shell.glb',[arch]);export('observed-fixtures.glb',[fix]);rep.hide_viewport=False;export('repair-shell.glb',[rep]);rep.hide_viewport=True
export('integrated-apartment.glb',[arch,fix,furn])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'integrated.blend'))
# Early checks: exact same scene as final batch, preview resolution temporarily reduced.
s.render.resolution_x=1000;s.render.resolution_y=700;s.eevee.taa_render_samples=8
for name in ['living-a','her-office-a','bedroom-flex-b']:
 s.camera=bpy.data.objects['CAM '+name];s.render.filepath=str(OUT/('preview-'+name+'.jpg'));bpy.ops.render.render(write_still=True)
print('INTEGRATED_READY')
