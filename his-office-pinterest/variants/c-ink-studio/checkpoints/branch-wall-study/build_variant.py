"""Two authorized alternatives: unchanged native room, shared actual-product furniture."""
import bpy,json,sys,math,hashlib,argparse
from pathlib import Path
from mathutils import Vector,Matrix
PIPE=Path(__file__).resolve().parent
sys.path.insert(0,str(PIPE))
import scene_tools as guard
from scene_tools import resolve_root,descendants,delete_tree,canonical_id,bounds
from primitives import box,rod,material,product_root
parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=['b-charcoal-slat','c-ink-studio'],required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);VARIANT=args.variant
ROOT=PIPE.parent/VARIANT/'model';PRODUCTS=PIPE.parent.parent/'products';FLOOR=1.575
catalog=json.loads((PRODUCTS/'selected-products.json').read_text());products={p['id']:p for p in catalog['items']}
if catalog['version']!='selected-shared-cool-furniture-two-directions-B-C-2026-10-08':raise RuntimeError('Final shared product spec not promoted')
guard.ROOT=ROOT;guard.KEEPER_IDS.discard('uplift-main-desk')
guard.read_source();before=guard.protected_signatures()
scene=bpy.context.scene
for id in ['branch-secondary','blue-bold-art','blue-geometric-art','uplift-main-desk','visitor-chair']:delete_tree(resolve_root(id))
delete_tree(bpy.data.objects['secondary-workspace::generic equipment assumption'])
new=bpy.data.collections.new('07 Shared B-C chosen new products');scene.collection.children.link(new)
finish=bpy.data.collections.new('08 Chosen workwall finish');scene.collection.children.link(finish)
layout=json.loads((PIPE.parent.parent/'model/layout.json').read_text());layout['design']='B Charcoal + Slat Bay' if VARIANT[0]=='b' else 'C Ink Studio';layout['layout_version']='shared-B-C-root-approved-2026-10-08'
for item in layout['items']:
 if item['id']=='uplift-main-desk':
  item.update(id='standing-main-desk',product_id='branch-tria-black-oak-charcoal',position_blender_m=[-6.915,-.131,FLOOR],external_dimensions_m=[1.2,.685,.74],top_thickness_m=.0254,dimension_confidence='Official supplier CAD1:1; desktop1200x685mm vs published1198.88x685.8mm rounding disclosed; top operating height740mm assumed',published_height_range_m=[.6477,1.24206],dimension_scope='DesktopW/D and seated top surface; keypad/cable door projections recorded in component bounds')
 if item['id']=='secondary-workspace':item['position_blender_m'][1]=-.070;item['panel_clearance_fit_shift_y_m']=-.020
 if item['id']=='visitor-chair':item.update(product_id='ekenaset-axvall-gray-blue',external_dimensions_m=[.650875,.739775,.7493],selected_color='Walnut effect/Axvall dark gray-blue boucle',dimension_confidence='Selected actual506.243.26 US retailer external measurements; new dimensioned proxy, detailed profile approximate')
 if item['id']=='clothes-dresser':item.update(product_id='storklinta-dark-brown',selected_color='Dark-brown/oak effect605.592.93')
 if item['id']=='rug':item.update(product_id='rift',selected_color='Rift Charcoal',texture_file=str(PRODUCTS/'proposal-complements/photos/rift-6x9.jpg'))
 if item['id']=='abstract-scenery-art':
  item.update(id='richmond-art',product_id='dan-hobday-richmond',position_blender_m=[-5.55,.22557 if VARIANT[0]=='b' else .24757,3.20],texture_file=str(PRODUCTS/'proposal-complements/art/dan-hobday-richmond-70x100-official.jpg'),dimension_confidence='Exact selected native landscape100x70cm paper; thin frame outside profile inferred from verified face/depth')
items={p['id']:p for p in layout['items']}
layout['product_catalog_authority']=str(PRODUCTS/'selected-products.json')
layout['generic_functional_assumptions']=['One generic monitor/keyboard on primary standing desk only; actual user hardware unknown.','Clear140x60cm project bench with left ALEX five drawers/right two ADILS; no fixed second monitor/task chair.','Closet contents unrecorded: three GREJIG racks conditional on actual internal dimensions.','Wall finishes are proposed; unchanged ceiling/door/window/brick/floor geometry.']
layout['notes']=['Source room geometry and Honeywell/cat forms/materials unchanged.','Main Tria CAD unscaled; only moving assembly translated to seated740mm top.','Bench moved20mm toward room in both variants to clearB22mm wall panel by8mm.','No separate baseboard geometry exists in source model; B panels floor aligned, mounting/baseboard detail requires site check.','Unrecorded closet rack floor support excluded from GLB; recorded closet leaf closed.']

def tag(o):o['role']='furniture';return o

def root_for(id):
 s=items[id];p=products[s['product_id']];spec={**s,'product_name':p.get('name',p.get('title','')),'product_url':p['source_url'],'dimension_source':'Chosen shared product spec and official supplier/retailer dimensions'}
 r=product_root(spec,new);r['id']=id;r['role']='furniture';r['selected_product_id']=s['product_id'];return r

def assign(o,m):
 if o.data.users>1:o.data=o.data.copy()
 o.data.materials.clear();o.data.materials.append(m)

def photograph(name,path,rough=.8):
 m=material(name,(.3,.3,.3),rough);p=m.node_tree.nodes.get('Principled BSDF');t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);return m

def textile(name,color):
 m=material(name,color,.93);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Sheen Weight'].default_value=.14
 tc=m.node_tree.nodes.new('ShaderNodeTexCoord');n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=220;n.inputs['Roughness'].default_value=.72
 m.node_tree.links.new(tc.outputs['Generated'],n.inputs['Vector']);b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.13;b.inputs['Distance'].default_value=.0003
 m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal']);return m

def detailed_wood(name,color,rough=.55):
 m=material(name,color,rough);p=m.node_tree.nodes.get('Principled BSDF');tc=m.node_tree.nodes.new('ShaderNodeTexCoord');scale=m.node_tree.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1,85,7)
 n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=6;n.inputs['Detail'].default_value=2
 m.node_tree.links.new(tc.outputs['Generated'],scale.inputs[0]);m.node_tree.links.new(scale.outputs[0],n.inputs['Vector']);b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.08;b.inputs['Distance'].default_value=.00025
 m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal']);return m
# Clear independent project bench, exact support/top contact and black chosen component finishes.
bench=resolve_root('secondary-workspace');bench.location.y=-.070
black=material('Shared black ADILS powder coat',(.012,.013,.015),.48)
blackbrown=detailed_wood('Shared black-brown LAGKAPTEN and ALEX finish proxy',(.035,.026,.019),.57)
for o in descendants(bench):
 if o.type!='MESH':continue
 if 'black-brown tabletop' in o.name:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;o.location.z=.7+.034925/2;o.dimensions.z=.034925;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False);assign(o,blackbrown)
 elif 'official alex-drawers' in o.name:assign(o,blackbrown);o['selected_sku']='604.735.48'
 elif 'ADILS' in o.name:assign(o,black);o.name=o.name.replace('white ADILS','black ADILS')
bench['modeled_assembled_height_m']=.734925;bench['catalog_nominal_height_m']=.73
# Supplier Tria: source coordinates are transformed/recentered, never geometrically scaled.
r=root_for('standing-main-desk');asset=Path(products['branch-tria-black-oak-charcoal']['geometry']['asset']['path'])
if guard.file_hash(asset)!='1122e1e218a4d351b58138637b8d18ada1ec66d2345e7cb2f035dc93e123dbdc':raise RuntimeError('Supplier CAD hash mismatch')
old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(asset));added=set(bpy.data.objects)-old;bpy.context.view_layer.update()
source_nodes=json.loads((PRODUCTS/'standing-desk-candidates/branch-tria-gltf.json').read_text())['nodes'];extras={n['name']:n.get('extras',{})for n in source_nodes if 'name'in n}
meshes=[o for o in added if o.type=='MESH'];desktop=next(o for o in meshes if o.name=='desktop')
topworld=[desktop.matrix_world@Vector(v)for v in desktop.bound_box];source_top=max(p.z for p in topworld);depth_center=(min(p.y for p in topworld)+max(p.y for p in topworld))/2
source_floor=min((o.matrix_world@Vector(v)).z for o in meshes for v in o.bound_box)
frame=material('Shared Tria selected Charcoal frame proxy',(.045,.047,.050),.43,.22);oak=detailed_wood('Shared Tria selected Black Oak top proxy',(.028,.030,.032),.54);dark=material('Shared Tria dark cable electrical felt',(.012,.013,.015),.78)
partlog=[]
for o in meshes:
 name=o.name
 key=name if name in extras else max([k for k in extras if name.startswith(k+'_')],key=len,default='')
 spec=extras.get(key,{})
 lift=spec.get('lift');role=spec.get('role')
 # Split material primitives inherit the supplier object/parent extras.
 parent=o.parent
 while lift is None and parent:
  lift=parent.get('lift');parent=parent.parent
 if lift not in ['desktop','middle','fixed']:raise RuntimeError('Missing official lift tag '+name)
 mat=oak if role=='desktop' else dark if role in ['felt','electrical','glide'] else frame
 world=o.matrix_world.copy();o.data=o.data.copy();o.data.transform(world);o.matrix_world=Matrix.Identity(4)
 dz=(.74-source_top)*(1 if lift=='desktop' else .5 if lift=='middle' else 0)-source_floor
 o.data.transform(Matrix.Translation((0,-depth_center,dz)))
 for c in list(o.users_collection):c.objects.unlink(o)
 new.objects.link(o);o.parent=r;o.matrix_parent_inverse=Matrix.Identity(4);o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
 o.name='standing-main-desk::'+name;o['role']='furniture';o['supplier_lift_group']=lift;o['supplier_component_role']=role or '';o['source_component_name']=name;o['source_unscaled']=True
 assign(o,mat);partlog.append({'name':o.name,'source_name':name,'lift':lift,'role':role,'height_factor':1 if lift=='desktop' else .5 if lift=='middle' else 0})
for o in added:
 if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
r['official_geometry_source']=str(asset);r['CAD_shape_preserved_at_scale1']=True;r['supplier_top_height_m']=source_top;r['seated_top_height_m']=.74;r['published_height_range_m']=[.6477,1.24206];r['CAD_source_color']='Woodgrain/White; rematerialized to selected BlackOak/Charcoal from official photograph';r['source_depth_centering_translation_m']=-depth_center
# Generic functional equipment remains only on primary desktop at the same74cm top surface.
equipment=bpy.data.objects['uplift-main-desk::generic equipment assumption'];equipment.name='standing-main-desk::generic equipment assumption';equipment.location.x+=.035;equipment['canonical_owner']='standing-main-desk';equipment['supplier_lift_group']='desktop-equipment-proxy'
# Fresh Axvall refresh proxy with its actual dimensions/rounded upholstered silhouettes.
v=root_for('visitor-chair');fabric=textile('Shared EKENASET Axvall dark gray-blue boucle proxy',(.047,.090,.128));wood=detailed_wood('Shared EKENASET walnut-effect wood proxy',(.085,.068,.053),.53)
tag(box('visitor-chair::rounded boucle seat',(0,.017,.43),(.548,.515,.125),fabric,new,v,bevel=.035))
b=tag(box('visitor-chair::rounded sloping boucle back',(0,-.220,.545),(.548,.105,.395),fabric,new,v,bevel=.033));b.rotation_euler.x=math.radians(14)
for x in [-.30,.30]:
 tag(box('visitor-chair::rounded walnut arm',(x,.005,.575),(.044,.625,.035),wood,new,v,bevel=.017))
 tag(rod('visitor-chair::front walnut leg',(x,.325,.024),(x*.945,.190,.565),.024,wood,new,v,vertices=24))
 tag(rod('visitor-chair::rear walnut leg',(x,-.318,.024),(x*.945,-.175,.565),.024,wood,new,v,vertices=24))
 tag(rod('visitor-chair::side seat rail',(x,-.19,.355),(x,.245,.355),.021,wood,new,v,vertices=24))
tag(box('visitor-chair::front walnut seat stretcher',(0,.236,.355),(.598,.040,.045),wood,new,v,bevel=.003))
tag(box('visitor-chair::rear walnut seat stretcher',(0,-.206,.355),(.598,.040,.045),wood,new,v,bevel=.003))
bpy.context.view_layer.update()
# New proxy construction is fitted to the selected variant's external envelope, not old SKU recoloring.
pp=[o.matrix_world@Vector(c) for o in descendants(v)if o.type=='MESH'for c in o.bound_box];lo=[min(p[i]for p in pp)for i in range(3)];hi=[max(p[i]for p in pp)for i in range(3)]
actual=[hi[i]-lo[i]for i in range(3)];target=items['visitor-chair']['external_dimensions_m'];fac=[target[i]/actual[i]for i in range(3)];center=[(lo[i]+hi[i])/2-v.location[i]for i in range(2)]
for o in descendants(v):
 if o.type!='MESH':continue
 transform=Matrix.Diagonal(Vector((*fac,1)))@Matrix.Translation((-center[0],-center[1],-(lo[2]-FLOOR)))@o.matrix_basis
 o.data=o.data.copy();o.data.transform(transform);o.matrix_basis=Matrix.Identity(4)
v['new_AXVALL_refresh_proxy']=True;v['detailed_shape_confidence']='Nominal external dimensions exact; individual upholstered/timber profiles inferred from official selected photograph, not vendorCAD.'
# Existing clothes dresser CAD geometry with the selected darkbrown finish proxy.
dresser=resolve_root('clothes-dresser');dressermat=detailed_wood('Shared selected STORKLINTA dark-brown oak effect proxy',(.073,.049,.035),.6)
for o in descendants(dresser):
 if o.type=='MESH':assign(o,dressermat)
# Actual selected6x9 rugbody and full native100x70 Richmond artwork, no crop/rotation of motif.
rugroot=resolve_root('rug');rug=next(o for o in descendants(rugroot)if 'flatwoven textile'in o.name);assign(rug,photograph('Actual selected Rift Charcoal6x9 flatwoven source',PRODUCTS/'proposal-complements/photos/rift-6x9.jpg',.89));rug.name='rug::actual Rift Charcoal6x9 flatwoven textile'
for li,uv in enumerate([(.119375,.0495),(.119375,.953833333),(.883541667,.953833333),(.883541667,.0495)]):rug.data.uv_layers.active.data[li].uv=uv
art=root_for('richmond-art');blackframe=material('Shared selected black landscape wood frame',(.011,.010,.009),.48);ow,oh,f,d=1.0254,.7254,.0127,.02286
for name,pos,dim in [('top',(0,0,oh/2-f/2),(ow,d,f)),('bottom',(0,0,-oh/2+f/2),(ow,d,f)),('left',(-ow/2+f/2,0,0),(f,d,.7)),('right',(ow/2-f/2,0,0),(f,d,.7))]:tag(box('richmond-art::black wood frame '+name,pos,dim,blackframe,new,art,bevel=.0008))
mesh=bpy.data.meshes.new('Richmond native100x70 full source paper');mesh.from_pydata([(-.5,-.0107,-.35),(.5,-.0107,-.35),(.5,-.0107,.35),(-.5,-.0107,.35)],[],[(0,1,2,3)]);mesh.update();paper=bpy.data.objects.new('richmond-art::full actual native landscape print',mesh);new.objects.link(paper);paper.parent=art;tag(paper)
u=mesh.uv_layers.new(name='Exact full source paper UV')
for li,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):u.data[li].uv=uv
mesh.materials.append(photograph('Actual selected DanHobday Richmond100x70 native landscape',PRODUCTS/'proposal-complements/art/dan-hobday-richmond-70x100-official.jpg',.85))
# Intentional workwall paint only; all source architecture coordinates/brick/door/window finishes stay.
def linear(x):
 t=x/255;return t/12.92 if t<=.04045 else ((t+.055)/1.055)**2.4
rgb=[88,88,88] if VARIANT[0]=='b' else [47,61,76];paint=material('Chosen PeppercornSW7674 matte workwall'if VARIANT[0]=='b'else'Chosen NavalSW6244 matte workwall',tuple(linear(c)for c in rgb),.9)
assign(bpy.data.objects['his-office wall4 segment'],paint)
wallbounds=bounds([bpy.data.objects['his-office wall4 segment']]);wallface=wallbounds[0][1]
if abs(wallface-.26)>.0001:raise RuntimeError('Measured source workwall face changed')
if VARIANT[0]=='b':
 felt=material('WoodUpp chosen black PET felt proxy',(.007,.008,.010),.93);slat=detailed_wood('WoodUpp chosen BlackAsh veneer proxy',(.018,.020,.023),.62)
 for j in range(3):
  r=bpy.data.objects.new('woodupp-panel-'+str(j+1),None);finish.objects.link(r);r.location=(-6.15+j*.6,wallface,FLOOR);r['role']='architecture_finish';r['selected_sku']='1013';r['external_dimensions_m']=[.6,.022,2.4];r['installation_proxy']='Direct-mounted22mm total:9mm felt+13mm veneer/MDF slats; fine profiles inferred; verify substrate/baseboard onsite.'
  o=box('WoodUpp panel'+str(j+1)+' black felt',(0,-.0045,1.2),(.6,.009,2.4),felt,finish,r);o['role']='architecture'
  for k in range(15):
   x=-.3+.0065+.027/2+k*.040;o=box('WoodUpp panel'+str(j+1)+' vertical BlackAsh slat'+str(k+1),(x,-.0155,1.2),(.027,.013,2.4),slat,finish,r,bevel=.0005);o['role']='architecture'
 layout['workwall_finish']={'paint':'PeppercornSW7674','screen_sRGB':rgb,'panel_count':3,'panel_W_D_H_m':[.6,.022,2.4],'bay_W_H_m':[1.8,2.4],'panel_bottom_z_m':FLOOR,'panel_top_z_m':FLOOR+2.4,'ceiling_upper_band_m':.620,'baseboard':'No separate workwall baseboard geometry recorded in source; onsite mounting detail unmeasured','slat_profile_proxy_m':[.027,.013],'felt_thickness_proxy_m':.009,'slat_pitch_proxy_m':.040}
else:layout['workwall_finish']={'paint':'NavalSW6244','screen_sRGB':rgb,'panels':False}
# Same neutral/cool overhead/daylight in both; no invented ceiling luminaires.
for o in bpy.data.objects:
 if o.type=='LIGHT':o.data.color=(.91,.96,1.0) if 'ceiling'in o.name else(.87,.93,1.0)
scene.view_settings.exposure=-.5;scene.cycles.samples=32;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.035;scene.cycles.adaptive_min_samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['CAM room-a'];scene['design_revision']=layout['design'];scene['source_geometry_authority']=str(guard.SOURCE)
# Canonical identity/nominal dimensions for every chosen product; keep source fitted geometry metadata.
for s in layout['items']:
 rr=resolve_root(s['id']);p=products.get(s.get('product_id'),{});rr['pinterest_layout_id']=s['id'];rr['selected_product_id']=s.get('product_id','');rr['canonical_position_blender_m']=s['position_blender_m']
 if p:rr['product_name']=p.get('name',rr.get('product_name',''));rr['product_url']=p.get('source_url',rr.get('product_url',''))
bpy.data.collections['His Office — kept products and two Branch task chairs'].name='His Office — exact Honeywell-cat and one Branch chair'
bpy.context.view_layer.update();guard.assert_protected(before);images=guard.active_image_checks()
structure={o for n in guard.STRUCTURE_COLLECTIONS for o in bpy.data.collections[n].all_objects}|set(finish.all_objects);doors=set(bpy.data.collections['02b Existing door leaves — closed observed state'].all_objects)
furniture={o for o in bpy.data.objects if o.type in ['MESH','EMPTY'] and o.get('role')=='furniture'}
for o in list(furniture):
 p=o.parent
 while p:furniture.add(p);p=p.parent
for filename,objects in [('his-office-shell.glb',structure-doors),('his-office-door-leaves.glb',doors),('his-office-furniture.glb',furniture),('his-office-design.glb',structure|furniture)]:guard.export_selected(ROOT/filename,objects)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'his-office-design.blend'));guard.assert_protected(before)
(ROOT/'layout.json').write_text(json.dumps(layout,indent=2));(ROOT/'tria-component-map.json').write_text(json.dumps({'supplier_source_sha256':guard.file_hash(asset),'source_top_m':source_top,'source_floor_m':source_floor,'depth_center_native_y_m':depth_center,'seated_top_m':.74,'height_range_m':[.6477,1.24206],'parts':partlog},indent=2))
poses=[]
for name in ['room-a','room-b','room-c']:
 cam=bpy.data.objects['CAM '+name];f=cam.matrix_world.to_quaternion()@Vector((0,0,-1));t=cam.location+f
 poses.append({'id':name,'filename':'renders/'+name+'.jpg','eye_blender_m':list(cam.location),'look_direction_blender':list(f),'eye_gltf_m':[cam.location.x,cam.location.z,-cam.location.y],'target_gltf_m':[t.x,t.z,-t.y],'eye':[cam.location.x,cam.location.z,-cam.location.y],'target':[t.x,t.z,-t.y],'lens_mm':cam.data.lens,'sensor_width_mm':cam.data.sensor_width,'horizontal_FOV_deg':math.degrees(2*math.atan(cam.data.sensor_width/(2*cam.data.lens))),'pixels':[1440,1000],'unit':'metres; BlenderZ-up; GLTF[X,Z,-Y]'})
(ROOT/'camera-poses.json').write_text(json.dumps(poses,indent=2))
manifest={'variant':VARIANT,'protected_geometry_pass':True,'unchanged_source_sha256':guard.file_hash(guard.SOURCE),'allowed_material_exception':'his-office wall4 segment only; paint screenRGB converted correctly to linear shader values','owned_products_protected':['honeywell-lamp','muttros-cat-tree'],'shared_product_count':len(layout['items']),'mesh_count':sum(o.type=='MESH'for o in bpy.data.objects),'active_images':images,'exports':[]}
for p in sorted(ROOT.iterdir()):
 if p.suffix in ['.blend','.glb','.json'] and p.name!='model-manifest.json':manifest['exports'].append({'filename':p.name,'sha256':guard.file_hash(p),'bytes':p.stat().st_size})
(ROOT/'model-manifest.json').write_text(json.dumps(manifest,indent=2));print('AUTHORIZED_VARIANT_READY',VARIANT,flush=True)
