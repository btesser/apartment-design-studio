import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path('/workspace/apartment-model')
geo=json.load(open('/workspace/geometry-audit/geometry.json'))
plates=json.load(open(ROOT/'plate-geometry.json'))
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
scene=bpy.context.scene
# Exporter requires file-backed texture images for packed original photographs.
for mm in bpy.data.materials:
 if not mm.use_nodes:continue
 tx=next((nn for nn in mm.node_tree.nodes if nn.type=='TEX_IMAGE'),None)
 if not tx or not tx.image:continue
 im=tx.image
 if im.packed_file:
  fn=ROOT/(im.name+'.jpg');fn.write_bytes(im.packed_file.data);im.filepath=str(fn);im.file_format='JPEG'
 # Recreate canonical PBR graph in the copy; keep the actual original image/UV data.
 ns=mm.node_tree.nodes;ns.clear();out=ns.new('ShaderNodeOutputMaterial');ps=ns.new('ShaderNodeBsdfPrincipled');tt=ns.new('ShaderNodeTexImage');tt.image=im;ps.inputs['Roughness'].default_value=.82;mm.node_tree.links.new(tt.outputs['Color'],ps.inputs['Base Color']);mm.node_tree.links.new(ps.outputs['BSDF'],out.inputs['Surface'])
for o in list(bpy.data.objects):
 if not o.name.startswith('Mesh_'):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.name!='Collection' and len(c.objects)==0:bpy.data.collections.remove(c)
raw=bpy.data.collections.get('Collection');raw.name='01 Retained Scan — original scale'
for oo in list(bpy.data.objects):
 if oo.type=='MESH' and oo.name.startswith('Mesh_'):
  for cc in list(oo.users_collection):cc.objects.unlink(oo)
  raw.objects.link(oo)
repair=bpy.data.collections.new('02 Conservative Architecture Repairs');scene.collection.children.link(repair)
arch=bpy.data.collections.new('03 Clean Measured Shell — inferred finishes');scene.collection.children.link(arch)
lights=bpy.data.collections.new('04 Preview Lights and Cameras');scene.collection.children.link(lights)
# Remove only texture-black faces in the confidently observed captured-person volume.
removed=[]
for o in list(raw.objects):
 if o.type!='MESH' or int(o.name.split('_')[1])<11:continue
 file=ROOT/f'dark_{o.name}.npz'
 if not file.exists():continue
 p=np.load(file);v=p['loc'];ids=p['faceids'];m=(v[:,0]>-3)&(v[:,0]<1)&(v[:,1]>-2.6)&(v[:,1]<-1.2)&(v[:,2]>1.65)&(v[:,2]<3.65)
 indexes=set(int(i) for i in ids[m])
 if indexes:
  bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in indexes],context='FACES');bm.to_mesh(o.data);bm.free();removed.append({'object':o.name,'removed_black_human_faces':len(indexes)})
# GLTF-compatible image materials: reconstructed surfaces visibly remain separate.
def material(name,color,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.78
 if texture:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/texture));tx.extension='REPEAT';m.node_tree.links.new(tx.outputs['Color'],p.inputs['Base Color'])
 return m
white=material('Reconstructed warm plaster',(.78,.76,.72));ceilmat=material('Reconstructed ceiling',(.86,.84,.79));wood=material('Reconstructed upper wood',(.52,.37,.20),'wood-upper.png');tile=material('Reconstructed lower tile',(.28,.29,.28),'tile-lower.png');brick=material('Reconstructed exposed brick',(.4,.17,.08),'brick-upper.png');stairmat=material('Reconstructed wood stairs',(.43,.24,.10),'wood-upper.png');metal=material('Column paint',(.77,.76,.73))
def move_to(o,col):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
def uv_world(o):
 for old in list(o.data.uv_layers):o.data.uv_layers.remove(old)
 uv=o.data.uv_layers.new(name='MetricProjection');uv.active_render=True
 for p in o.data.polygons:
  n=p.normal
  axes=(0,1) if abs(n.z)>.6 else ((0,2) if abs(n.y)>.6 else (1,2))
  for li in p.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   scale=1.83 if any(mm.name.startswith('Reconstructed exposed brick') for mm in o.data.materials) else .55
   uv.data[li].uv=(v[axes[0]]*scale,v[axes[1]]*scale)
def box(name,center,size,mat,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);move_to(o,col);uv_world(o);return o
log=[]
def plate(p,col,z=None,kind=None):
 zz=p['z'] if z is None else z;verts=[];faces=[]
 for tri in p['triangles']:
  base=len(verts);verts.extend([(x,y,zz) for x,y in tri]);faces.append((base,base+1,base+2))
 mesh=bpy.data.meshes.new(p['name']+' plane mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new((kind or p['type'])+' — '+p['name'],mesh);col.objects.link(o)
 is_ceiling='ceiling' in p['type'];mat=ceilmat if is_ceiling else (wood if p['level'] in ('upper','upstairs') else tile);o.data.materials.append(mat);uv_world(o)
 # Render and export both sides for scan backing patches; ceiling normals can face room.
 if is_ceiling:
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 o['evidence']='observed architectural extent with planar missing-surface continuation';o['confidence']='medium: local plane and extent estimated from scan';return o
for p in plates:
 if p['type'] in ['floor_underlay','ceiling_underlay']:plate(p,repair)
 else:plate(p,arch)
# Room wall backs: holes and openings are handled by interval splitting, not mesh hole fill.
rooms={r['id']:dict(r) for r in geo['rooms']}
rooms['bathroom-upper']['openings']=[{'type':'bathroom-door','x':-1.24,'y_range':[.52,1.35]}]
rooms['upper-kitchen']['openings']=[{'type':'window','x':-7.98,'y_range':[1.23,2.12]}]
wallrecords=[]
def wall(name,p0,p1,floor,ceiling,openings,mat,col,offset=0,thickness=.12):
 x0,y0=p0;x1,y1=p1;dx=x1-x0;dy=y1-y0;length=math.hypot(dx,dy)
 if length<.02:return
 # Generic endpoints allow measured non-axis-aligned perimeter edges.
 intervals=[0,length]
 for op in openings:intervals.extend([max(0,min(length,op[0])),max(0,min(length,op[1]))])
 intervals=sorted(set(intervals));ang=math.atan2(dy,dx)
 for a,b in zip(intervals,intervals[1:]):
  if b-a<.01:continue
  mid=(a+b)/2;cut=next((q for q in openings if q[0]-1e-6<=mid<=q[1]+1e-6),None)
  bands=[(floor,ceiling)] if cut is None else [(floor,max(floor,cut[2])),(min(ceiling,cut[3]),ceiling)]
  for lo,hi in bands:
   if hi-lo<.01:continue
   cx=x0+dx/length*mid-dy/length*offset;cy=y0+dy/length*mid+dx/length*offset
   o=box(name+' segment',(cx,cy,(lo+hi)/2),(b-a,thickness,hi-lo),mat,col);o.rotation_euler.z=ang
   o['confidence']='medium; measured wall with approximate opening trim';o['opening_preserved']=bool(cut)
 if col==arch:wallrecords.append({'name':name,'a':p0,'b':p1,'floor':floor,'ceiling':ceiling,'openings':openings})
def opening_for_edge(r,p0,p1):
 x0,y0=p0;x1,y1=p1;dx=x1-x0;dy=y1-y0;l=math.hypot(dx,dy);ops=[]
 for op in r.get('openings',[]):
  if 'x' in op and abs(dx)<.14 and abs(x0-op['x'])<.14:
   rr=op['y_range'];start=(rr[0]-y0)/(dy/l);end=(rr[1]-y0)/(dy/l)
  elif 'wall_y' in op and abs(dy)<.14 and abs(y0-op['wall_y'])<.14:
   rr=op['x_range'];start=(rr[0]-x0)/(dx/l);end=(rr[1]-x0)/(dx/l)
  else:continue
  a,b=sorted([start,end]);f=r['floor_z_m'];win=op['type']=='window'
  ops.append((a,b,f+.80 if win else f-.02,f+2.65 if win else f+2.2))
 return ops
def roomwalls(r,edges=None):
 poly=r['outline'];signed=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)));outsign=-1 if signed>0 else 1
 for i,p0 in enumerate(poly):
  if edges is not None and i not in edges:continue
  p1=poly[(i+1)%len(poly)];ops=opening_for_edge(r,p0,p1);mat=brick if r['level']=='upper' and p0[1]<-2.65 and p1[1]<-2.65 else white
  for col,offset,t in [(arch,0,.10),(repair,outsign*.08,.08)]:wall(r['id']+f' wall{i}',p0,p1,r['floor_z_m']-.04,r['ceiling_z_m']+.04,ops,mat,col,offset,t)
for id in ['his-office','her-office','bathroom-upper','music-gym']:roomwalls(rooms[id])
# Kitchen retains the open connection to dining/living; the north exterior shape is observed.
roomwalls(rooms['upper-kitchen'],[4,5,6,7,8,9])
# Living wall sides already modeled by adjacent rooms. Only its independent brick and entry walls.
r=rooms['living'];roomwalls(r,[0])
# Entry partition includes wide verified doorway rather than closing access to the stair landing.
for col,offset in [(arch,0),(repair,.07)]:
 wall('Upper entry / stair partition',(1.28,1.84),(3.73,1.84),r['floor_z_m'],r['ceiling_z_m'],[(.42,1.50,r['floor_z_m']-.02,r['floor_z_m']+2.30)],white,col,offset)
 wall('Upper entry side',(3.73,.20),(3.73,1.84),r['floor_z_m'],r['ceiling_z_m'],[],white,col,offset)
# Main lower perimeter. Do not guess doors into unscanned utility zones, or seal the stair well.
r=rooms['basement-open'];roomwalls(r,[0,1,2,3,5,9,11])
for col,offset in [(arch,0),(repair,-.08)]:
 wall('Lower front wall with high windows and entrance',(7.85,-1.31),(7.85,2.55),r['floor_z_m'],r['ceiling_z_m'],[(.12,1.05,.65,1.15),(1.58,2.40,.65,1.15),(2.90,3.86,r['floor_z_m']-.02,r['floor_z_m']+2.18)],white,col,offset)
# Twelve scan-matched stair planes; final two steps and top landing are inferred continuation.
for col,recess in [(arch,0),(repair,.035)]:
 for i in range(1,15):
  run=.24286;right=5.245-(i-1)*run;left=right-run;top=-1.385+i*(2.96/14)-recess
  box(f'Stair tread {i:02d}'+(' repair' if col==repair else ''),((left+right)/2,2.31,(top-1.48)/2),(run,.90,top+1.48),stairmat,col)
 # Observed basement posts and beam/soffit align independently from floor labels.
 for j,(x,y) in enumerate(r['columns_xy']):box(f'Structural post {j+1}',(x,y,(-1.385+.955)/2),(.18,.18,2.34),metal,col)
 box('Main lower soffit continuation',(.10,.85,1.10),(15.10,.48,.29),white,col)
# Separate scene cameras and lights; source model dimensions never normalized.
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100
scene.world.color=(.12,.12,.12);scene.view_settings.view_transform='AgX'
cameras={
 'living-view-a':((2.85,-.8,3.0),(-1.0,-1.7,2.65)),
 'living-view-b':((-2.65,-.55,3.0),(2.2,-1.5,2.6)),
 'his-office':((-3.45,-2.25,3.02),(-6.30,-.05,2.6)),
 'her-office':((4.45,-2.12,3.06),(6.05,.30,2.6)),
 'kitchen':((-2.0,1.65,3.02),(-6.0,1.6,2.6)),
 'basement-open-a':((-.1,-1.7,.1),(4.3,.10,-.25)),
 'basement-open-b':((7.25,-1.65,.1),(.0,.00,-.3)),
 'bedroom-flex':((-.90,-1.75,.1),(-2.9,-.05,-.3)),
 'music-gym':((-4.3,-1.7,.1),(-6.4,-.30,-.3)),
 'stairs':((5.8,1.2,.22),(2.4,2.28,1.1)),
 'his-office-b':((-7.25,-2.0,3.02),(-4.4,-.05,2.60)),
 'her-office-b':((7.2,-2.10,3.06),(4.8,.15,2.60)),
 'bedroom-flex-b':((-3.45,.25,.08),(-1.6,-1.65,-.35)),
 'music-gym-b':((-7.00,-2.10,.1),(-4.35,-.30,-.3)),
 'entry-a':((3.35,1.50,3.00),(1.65,.40,2.6)),
 'entry-b':((1.48,.45,3.0),(3.3,1.4,2.65))}
for name,(pos,target) in cameras.items():
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name='CAM '+name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=21;o.data.clip_start=.04;o.data.clip_end=80;move_to(o,lights)
for rr in geo['rooms']:
 if rr['id']=='bedroom-flex':continue
 p=rr['outline'];x=sum(v[0] for v in p)/len(p);y=sum(v[1] for v in p)/len(p)
 bpy.ops.object.light_add(type='AREA',location=(x,y,rr['ceiling_z_m']-.18));o=bpy.context.object;o.name='LIGHT '+rr['id'];o.data.energy=160 if rr['level']=='upper' else 130;o.data.shape='DISK';o.data.size=2.3;move_to(o,lights)
# Daylight through preserved office windows, supplements the scan's photographed light.
for x,y,z in [(-7.9,-.5,3.1),(7.8,-1.9,3.1),(7.8,-.1,3.1)]:
 bpy.ops.object.light_add(type='AREA',location=(x,y,z));o=bpy.context.object;o.name='LIGHT window';o.data.energy=200;o.data.size=1.2;o.rotation_euler=(Vector((0,y,z))-o.location).to_track_quat('-Z','Y').to_euler();move_to(o,lights)
for im in bpy.data.images:
 if im.source=='FILE' or im.packed_file: 
  try:im.pack()
  except:pass
# Exports per collection keep source scan/repairs/furniture independently toggleable.
def export(path,cols):
 bpy.ops.object.select_all(action='DESELECT')
 for col in cols:
  for o in col.objects:
   if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/path),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_image_format='JPEG',export_jpeg_quality=88,export_extras=True)
export('cleaned-scan.glb',[raw]);export('repair-shell.glb',[repair]);export('architectural-shell.glb',[arch]);export('repaired-apartment.glb',[raw,repair])
arch.hide_render=True;arch.hide_viewport=True
scene.camera=bpy.data.objects.get('CAM living-view-a')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'repaired-apartment.blend'))
json.dump({'human_artifact_removals':removed,'wall_records':wallrecords,'camera_presets_blender':{k:{'eye':v[0],'target':v[1],'lens_mm':21} for k,v in cameras.items()},'originals_untouched':['/workspace/apartment/8_21_2026.glb','/workspace/apartment/scan.blend']},open(ROOT/'repair-log.json','w'),indent=2)
print('COMPLETE_MODEL',str(ROOT/'repaired-apartment.blend'))
