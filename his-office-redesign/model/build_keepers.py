import bpy,math,json,sys,random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'/workspace/his-office-redesign/model')
from primitives import material,link_object,product_root,box,cylinder,ellipsoid,rod,bounds_world
P=Path('/workspace/his-office-redesign/model'); K=Path('/workspace/his-office-redesign/products/keepers')
bpy.ops.wm.read_factory_settings(use_empty=True)
COL=bpy.data.collections.new('His Office — kept products and two Branch task chairs');bpy.context.scene.collection.children.link(COL)
WHITE=material('Honeywell warm white enamel',(.84,.86,.85),.42,.12)
STEEL=material('UPLIFT industrial tinted clear steel',(.25,.255,.245),.42,.72)
NICKEL=material('UPLIFT brushed nickel grommet covers',(.59,.61,.60),.33,.83)
WOOD=material('Pheasantwood official appearance reference',(.39,.235,.085),.44)
DARKWOOD=material('Pheasantwood barkline edge',(.19,.105,.034),.65)
TREEWOOD=material('MUTTROS natural pear wood',(.35,.17,.065),.69)
KNOT=material('MUTTROS natural branch knots',(.20,.105,.051),.78)
FLEECE=material('MUTTROS brown cloud fleece',(.16,.075,.032),.99)
INTERIOR=material('MUTTROS brown condo interior',(.10,.060,.034),.99)
SISAL=material('MUTTROS natural sisal',(.40,.29,.17),.97)
RATTAN=material('MUTTROS handwoven wicker',(.38,.24,.11),.84)
RATTAN2=material('MUTTROS darker wicker strands',(.25,.145,.061),.9)
BLACK=material('Black product trim',(.015,.018,.020),.46)
LED=material('Honeywell4000K luminous diffuser',(.96,.96,.85),.35)
p=LED.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.895,.72,1);p.inputs['Emission Strength'].default_value=2.0
img=bpy.data.images.load(str(K/'uplift-live-edge-pheasantwood-front.jpg'));img.pack()
tex=WOOD.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;grain=WOOD.node_tree.nodes.new('ShaderNodeMix');grain.data_type='RGBA';grain.blend_type='MULTIPLY';grain.inputs[0].default_value=1;grain.inputs[7].default_value=(.62,.52,.42,1);WOOD.node_tree.links.new(tex.outputs['Color'],grain.inputs[6]);WOOD.node_tree.links.new(grain.outputs[2],WOOD.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
ROOTS=[];SPECS=[]
def root(id,name,pos,dims,url,notes,rot=0):
 s={'id':id,'product_name':name,'position_blender_m':pos,'external_dimensions_m':dims,'rotation_z_deg':rot,'product_url':url,'dimension_confidence':notes,'dimension_source':'Keeper research / exact selected products'}
 r=product_root(s,COL);ROOTS.append(r);SPECS.append(s);return r

def mesh(name,verts,faces,mat,parent):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(parent.name+'::'+name,data);COL.objects.link(o);o.parent=parent;data.materials.append(mat);return o

def curve_strands(name,strands,radius,mat,parent,res=2):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=radius;d.bevel_resolution=res
 for points in strands:
  sp=d.splines.new('POLY');sp.points.add(len(points)-1)
  for a,v in zip(sp.points,points):a.co=(*v,1)
 o=bpy.data.objects.new(parent.name+'::'+name,d);COL.objects.link(o);o.parent=parent;d.materials.append(mat);return o

def desk():
 r=root('kept-uplift-desk','Owned UPLIFT V2 Pheasantwood42×30in',[-6.95,-.131,1.575],[1.0668,.762,.74],'https://www.upliftdesk.com/desktop-lookbook/','Exact user-order top42×30in,1.75in thickness; frame and grommet spacing approximated from official photos')
 w,d,h=1.0668,.762,.74;th=.04445
 outline=[(-w/2,d/2),(w/2,d/2)]
 for i in range(23,-1,-1):
  x=-w/2+w*i/23;y=-d/2+(.010*(.5+.5*math.sin(i*1.73)) if i not in [0,23] else 0);outline.append((x,y))
 n=len(outline);vs=[(x,y,z) for z in [h-th,h] for x,y in outline];fs=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[((i+1)%n,i,i+n,(i+1)%n+n) for i in range(n)]
 o=mesh('solid wood barkline top',vs,fs,WOOD,r);uv=o.data.uv_layers.new(name='Official grain appearance')
 for face in o.data.polygons:
  for li in face.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(.12+.76*(v.x/w+.5),.15+.35*(v.y/d+.5))
 b=o.modifiers.new('Soft finished edge','BEVEL');b.width=.0015;b.segments=2
 for x in [-.452,.452]:
  box('C-frame steel foot',(x,0,.024),(.070,.70104,.034),STEEL,COL,r,.009)
  for y in [-.315,.315]:box('Foot glide',(x,y,.0055),(.058,.04,.011),BLACK,COL,r,.004)
  box('V2 lower slim stage',(x,.128,.18),(.046,.056,.31),STEEL,COL,r,.004)
  box('V2 middle stage',(x,.128,.397),(.058,.073,.26),STEEL,COL,r,.004)
  box('V2 upper stage',(x,.128,.581),(.073,.091,.225),STEEL,COL,r,.004)
  box('Underside side bracket',(x,0,h-th-.008),(.088,.68,.016),STEEL,COL,r,.003)
  rod('V2 triangular stability brace',(x,.13,.584),(x,.01,.678),.019,STEEL,COL,r)
 box('Hidden upper crossbar',(0,.133,.656),(.91,.065,.065),STEEL,COL,r,.006)
 for x in [-.35,.35]:
  cylinder('Two brushed nickel grommet covers',(x,.270,h+.001),.042,.003,NICKEL,COL,r)
 box('Height keypad',(w*.30,-d/2+.005,h-.029),(.10,.028,.024),BLACK,COL,r,.004)
 r['front_vector_blender']=[0,-1,0];r['back_vector_blender']=[0,1,0]

def lamp():
 r=root('kept-honeywell-02e-pro','Owned Honeywell02E Pro10400lm white',[-7.67,-.24,1.575],[.288036,.610108,1.9685],'https://www.amazon.com/dp/B0C3BVYTXP','Exact overall dimensions. U-base separate dimensions approximate; do not substitute6000lm02E.')
 # Open U points along +Y, main light panel long axis Y.
 box('U-base closed crossbar',(0,-.196,.012),(.247,.07,.024),WHITE,COL,r,.01)
 for x in [-.084,.084]:box('U-base open prong',(x,.018,.012),(.079,.438,.024),WHITE,COL,r,.009)
 box('Slim rectangular upright',(0,-.155,.990),(.039,.050,1.932),WHITE,COL,r,.005)
 o=cylinder('Rotary dimming knob',(.026,-.155,1.06),.015,.011,NICKEL,COL,r,32);o.rotation_euler.y=math.pi/2
 z=1.9535;w=.288036;d=.610108
 for x in [-w/2+.009,w/2-.009]:box('Rectangular panel long rim',(x,0,z),(.018,d,.030),WHITE,COL,r,.002)
 for y in [-d/2+.009,d/2-.009]:box('Rectangular panel end rim',(0,y,z),(w-.032,.018,.030),WHITE,COL,r,.002)
 # Exact product photo has an empty central aperture. Two narrow diffusers
 # run inside its rectangular perimeter; a broad slab would seal the opening.
 for x in [-.075,.075]:
  box('Narrow parallel LED light bar',(x,0,1.946),(.038,d-.041,.011),LED,COL,r,.002)
 r['panel_long_axis_blender']=[0,1,0];r['head_form_status']='Source-photo open rectangular perimeter with two narrow parallel LED bars and empty center; outer envelope unchanged';r['base_dimensions_status']='U-base shape from exact photos; .247×.438m proxy size is unverified, inside exact overall envelope'

def basket(r,name,center,diam,h=.115):
 cx,cy,z0=center;rad=diam/2-.003
 def point(t,a):
  rr=.046+(rad-.046)*math.sin(t*math.pi/2);zz=z0+h*(t**1.15)+.004*(t**4)*math.cos(6*a)
  return (cx+rr*math.cos(a),cy+rr*math.sin(a),zz)
 rings=[]
 for j in range(12):
  t=(j+.25)/12;rings.append([point(t,2*math.pi*i/80) for i in range(81)])
 rings.append([point(1,2*math.pi*i/96) for i in range(97)])
 warps=[]
 for j in range(58):
  a=2*math.pi*j/58;warps.append([point(i/16,a+.010*math.sin(i*math.pi)) for i in range(17)])
 curve_strands(name+' woven horizontal courses',rings,.0028,RATTAN,r,1)
 curve_strands(name+' crossing wicker strands',warps,.0026,RATTAN2,r,1)
 # Fleece insert stays at the base of each open basket, leaving visible woven sides.
 ellipsoid(name+' brown fleece cushion',(cx,cy,z0+.027),(rad*.54,rad*.54,.025),FLEECE,COL,r)

def tree():
 r=root('kept-muttros-cat-tree','Owned MUTTROS59in brown3wicker-basket tree',[-7.59,-1.00,1.575],[.59944,.5588,1.4986],'https://www.amazon.com/dp/B0HHRC6XBC','Exact base/height/components; natural branch positions and overall envelope are provisional, not vendor CAD')
 box('Triple thickness brown fleece base',(0,0,.01905),(.59944,.5588,.0381),FLEECE,COL,r,.017)
 # Hollow round condo with a real arched +X opening, not a black painted rectangle.
 R=.19939;Rin=.182;bottom=.0381;hh=.3048;N=96;M=18;vs=[];fs=[]
 for rr in [R,Rin]:
  for iz in range(M+1):
   for ia in range(N):
    a=2*math.pi*ia/N;vs.append((rr*math.cos(a),-.11+rr*math.sin(a),bottom+hh*iz/M))
 for layer in [0,1]:
  off=layer*(M+1)*N
  for iz in range(M):
   zmid=hh*(iz+.5)/M
   for ia in range(N):
    a=2*math.pi*(ia+.5)/N;y=R*math.sin(a)
    opening=(math.cos(a)>0 and abs(y)<.105 and zmid<.145+math.sqrt(max(0,.104**2-y**2)))
    if not opening:
     a0=off+iz*N+ia;a1=off+iz*N+(ia+1)%N;b0=a0+N;b1=a1+N
     fs.append((a0,a1,b1,b0) if layer==0 else (a0,b0,b1,a1))
 o=mesh('arched hollow condo wall',vs,fs,FLEECE,r);o.data.materials.append(INTERIOR)
 for f in o.data.polygons:
  if all(o.data.vertices[i].co.x**2+(o.data.vertices[i].co.y+.11)**2<R**2*.95 for i in f.vertices):f.material_index=1
 cylinder('Condo top plush cushion',(0,-.11,bottom+hh),R,.025,FLEECE,COL,r)
 cylinder('Condo dark floor',(0,-.11,bottom+.012),Rin,.015,INTERIOR,COL,r)
 # Natural pear-wood branches connect supports to the correct basket heights.
 main=[(-.11,-.15,.07),(-.10,-.15,.35),(-.12,-.13,.73),(-.10,-.10,1.01),(-.095,-.085,1.36)]
 side=[(.105,.19,.045),(.11,.18,.31),(.10,.165,.60),(.09,.12,.86)]
 upper=[(-.11,-.11,.94),(-.12,-.21,1.015),(-.105,-.30,1.078)]
 lower=[(.108,.18,.18),(.115,.26,.32),(.11,.34,.43)]
 for j,points in enumerate([main,side,upper,lower]):
  for i in range(len(points)-1):rod('Natural wood branch%d-%d'%(j,i),points[i],points[i+1],.043 if j<2 else .031,TREEWOOD,COL,r,24)
  for v in points[1:-1]:ellipsoid('Organic branch junction',v,(.047,.042,.049),TREEWOOD,COL,r)
 # Woven baskets extend along Y beside the rear window; X remains narrow.
 basket(r,'Top wicker basket',(-.095,-.085,1.370),.44958,.1216)
 basket(r,'High side wicker basket',(-.105,-.345,1.078),.381,.104)
 basket(r,'Low side wicker basket',(.105,.345,.432),.381,.104)
 # Fleece sling hammock between the two trunks.
 cx,cy,z0=0,.04,.70;nv=64;nr=12;verts=[];faces=[]
 for j in range(nr+1):
  t=j/nr
  for i in range(nv):
   a=2*math.pi*i/nv;verts.append((cx+.198*t*math.cos(a),cy+.198*t*math.sin(a),z0+.128*t*t))
 for j in range(nr):
  for i in range(nv):faces.append((j*nv+i,j*nv+(i+1)%nv,(j+1)*nv+(i+1)%nv,(j+1)*nv+i))
 o=mesh('Brown fleece suspended bowl hammock',verts,faces,FLEECE,r);m=o.modifiers.new('Soft cloth thickness','SOLIDIFY');m.thickness=.009
 curve_strands('Thick fleece hammock rim',[[(cx+.198*math.cos(2*math.pi*i/80),cy+.198*math.sin(2*math.pi*i/80),.828) for i in range(81)]],.016,FLEECE,r)
 for a,b,z0,z1 in [(-.10,-.15,.38,.53),(-.11,-.13,.77,.93),(.11,.18,.05,.24)]:
  turns=max(6,int((z1-z0)/.008));helix=[(a+.046*math.cos(2*math.pi*turns*i/(turns*9)),b+.046*math.sin(2*math.pi*turns*i/(turns*9)),z0+(z1-z0)*i/(turns*9)) for i in range(turns*9+1)];curve_strands('Sisal rope winding',[helix],.0036,SISAL,r,1)
 for p0 in [(-.095,-.085,1.37),(-.105,-.345,1.078),(.105,.345,.432)]:
  xx,yy,zz=p0;curve_strands('Hanging pom-pom cord',[[(xx+.10,yy,zz),(xx+.10,yy,zz-.16)]],.0015,SISAL,r,1);ellipsoid('Brown play ball',(xx+.10,yy,zz-.18),(.025,.025,.025),FLEECE,COL,r)
 r['condo_opening_vector_blender']=[1,0,0];r['basket_span_axis_blender']=[0,1,0];r['upper_envelope_status']='Provisional .7X×1.1Y allocation, not a verified manufacturer envelope'

def chairs():
 bpy.ops.import_scene.gltf(filepath=str(P/'branch-pro-official-shore-reference.glb'))
 imported=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in COL.objects[:]]
 # glTF's generic Image_0… names and empty paths can collide with empty image
 # datablocks in the shell when this collection is appended. Preserve source
 # encoded bytes under unique paths/names, then pack: no pixel postprocessing.
 texture_dir=P/'branch-textures';texture_dir.mkdir(exist_ok=True)
 branch_images={n.image for o in imported for ma in o.data.materials for n in ma.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
 for im in branch_images:
  loaded_size=tuple(im.size) # Access forces Blender's lazy packed image load.
  if min(loaded_size)<1 or not im.has_data or not im.packed_file:raise RuntimeError('Missing official Branch source texture: '+im.name)
  data=bytes(im.packed_file.data);suffix='.png' if data.startswith(b'\x89PNG') else '.jpg'
  unique_name='Branch Ergonomic Pro official Shore source — '+im.name
  filepath=texture_dir/('branch-pro-'+im.name.lower()+suffix)
  filepath.write_bytes(data);im.name=unique_name;im.filepath=str(filepath)
  # Already packed images retain their bytes. Repacking FILE images with an
  # empty path can clear their packed data in this Blender version.
  if not im.packed_file:im.pack()
 # Original preview model faces -Y. Its body height is inside official adjustable range.
 pts=[o.matrix_world@v.co for o in imported for v in o.data.vertices];minz=min(v.z for v in pts)
 base=[v for v in pts if v.z<minz+.20];radius=max(math.hypot(v.x,v.y) for v in base);xy=.35052/radius
 for m in {ma for o in imported for ma in o.data.materials}:
  m.name='Branch selected Black — '+m.name;m.diffuse_color=(.035,.037,.039,1)
  bs=m.node_tree.nodes.get('Principled BSDF');old=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else None
  if old:
   mult=m.node_tree.nodes.new('ShaderNodeMix');mult.data_type='RGBA';mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[7].default_value=(.055,.057,.060,1);m.node_tree.links.new(old,mult.inputs[6]);m.node_tree.links.new(mult.outputs[2],bs.inputs['Base Color'])
  else:bs.inputs['Base Color'].default_value=(.03,.032,.035,1)
  bs.inputs['Roughness'].default_value=.69
 prototypes=[]
 for o in imported:
  # Bake source world matrix before applying the nominal base-diameter normalization.
  data=o.data.copy()
  for v in data.vertices:
   v.co=o.matrix_world@v.co;v.co.x*=xy;v.co.y*=xy;v.co.z-=minz
  prototypes.append((o.name,data,list(o.data.materials)))
 for o in imported:bpy.data.objects.remove(o,do_unlink=True)
 for idx,x in enumerate([-6.82,-5.40],1):
  r=root('branch-pro-task-chair-%d'%idx,'Selected Branch Ergonomic Chair Pro Black', [x,[-.85,-.80][idx-1],1.575],[.70104,.70104,.9810278],'https://www.branchfurniture.com/products/ergonomic-chair-pro?variant=40553208840227','Official vendor preview mesh (Shore) recoloured black; plan resized uniformly to nominal27.6in base diameter; configured preview height.981m within official.9652–1.04648m range',180)
  for name,data,mats in prototypes:
   o=bpy.data.objects.new(r.name+'::'+name,data);COL.objects.link(o);o.parent=r
  r['seated_gaze_vector_blender']=[0,1,0];r['official_geometry_source']='https://www.branchfurniture.com/cdn/shop/3d/models/o/081fd233399ddfee/FBX_Ergonomic_Chair_Pro_Shore.glb?v=0';r['source_mesh_colour']='Shore; selected Black represented by dark material factor';r['plan_scale_to_nominal_base']=xy;r['source_textures']='Vendor embedded texture bytes saved under unique product paths/names and packed to prevent empty-image collision on library append'

desk();lamp();tree();chairs()
# Convert strands and evaluate all modifiers once so blend/GLB/bounds share exact meshes.
bpy.ops.object.select_all(action='DESELECT')
for o in list(COL.objects):
 if o.type=='CURVE':
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
for o in list(COL.objects):
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
  for f in o.data.polygons:f.use_smooth=('solid wood barkline top' not in o.name)
bpy.context.view_layer.update()
manifest={'coordinate_frame':'Unscaled native Polycam Blender meters, Z up. GLB exportY-up maps(x,y,z) to(x,z,-y).','collection':COL.name,'proxy_notes':'Dimensioned form proxies. Not a claim of exact vendor CAD; source geometry/material adjustments documented by product.','products':[]}
for r,s in zip(ROOTS,SPECS):
 objects=[o for o in COL.objects if o.type=='MESH' and o.parent==r];bb=bounds_world(objects);s['world_bounds_blender_m']=bb;s['mesh_component_count']=len(objects);s['actual_world_bbox_dimensions_m']=[bb[1][i]-bb[0][i] for i in range(3)];s['notes']={k:(v if isinstance(v,(str,int,float,bool)) else list(v)) for k,v in r.items()};s['component_bounds']={o.name:bounds_world([o]) for o in objects};manifest['products'].append(s)
manifest['expected_quantity']={'desk':1,'lamp':1,'cat_tree':1,'task_chairs':2};manifest['actual_meshes']=sum(o.type=='MESH' for o in COL.objects);manifest['mesh_vertices']=sum(len(o.data.vertices) for o in COL.objects if o.type=='MESH')
(P/'keepers-and-taskchairs-bounds.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'keepers-and-taskchairs.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in COL.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'keepers-and-taskchairs.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
print('KEEPERS DONE',json.dumps([{k:p[k] for k in ['id','world_bounds_blender_m','actual_world_bbox_dimensions_m']} for p in manifest['products']]))
