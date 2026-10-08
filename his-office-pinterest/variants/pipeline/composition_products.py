"""Source-CAD ledges/FADO and disclosed small composition proxies; native metres."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from primitives import box,cylinder,rod,material,product_root

def add_composition(collection,layout,products,variant,source_products):
 floor=layout['room_floor_z_m'];isB=variant.startswith('b');mount=.238 if isB else .260
 items=[];supports=[];source=Path(source_products)/'composition-pieces'
 def tagged(o,root=None):
  o['role']='furniture';o['walk_blocker']=False
  if root:o['moves_with']=root
  return o
 def root(id,pid,pos,dim,kind='accessory',**extra):
  p=products[pid];spec={'id':id,'kind':kind,'product_id':pid,'position_blender_m':pos,'external_dimensions_m':dim,'rotation_z_deg':0,'walk_blocker':False,**extra}
  items.append(spec);r=product_root({**spec,'product_name':p['name'],'product_url':p['source_url'],'dimension_source':'Published product/supplier CAD; reference proxies disclosed'},collection);r['id']=id;r['role']='furniture';r['selected_product_id']=pid;r['walk_blocker']=False
  for k,v in extra.items():r[k]=v
  return r
 def import_cad(path):
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));added=set(bpy.data.objects)-before;bpy.context.view_layer.update()
  meshes=[o for o in added if o.type=='MESH']
  for o in meshes:
   o.data=o.data.copy();o.data.transform(o.matrix_world);o.parent=None;o.matrix_world=Matrix.Identity(4)
   for c in list(o.users_collection):c.objects.unlink(o)
   collection.objects.link(o)
  for o in added:
   if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
  return meshes
 black=material('Chosen MOSSLANDA black paperfoil finish',(.011,.012,.014),.6)
 # Original tray shape: backlip70mm, frontlip30mm, support floor measured by mesh rays.
 for id,cx,top in [('project-display-ledge',-5.55,1.25),('primary-display-ledge',-6.915,2.10)]:
  r=root(id,'mosslanda-black-display-ledge',[cx,mount-.06000016-.001,floor+top-.070000015],[1.1499348879,.1200003214,.0700000152],kind='wall_ledge',wall_mounted=True,top_height_above_floor_m=top)
  meshes=import_cad(source/'mosslanda-official.glb')
  for o in meshes:
   o.name=id+'::original supplier black ledge';o.parent=r;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);o.data.materials.clear();o.data.materials.append(black);tagged(o);o['source_geometry_unscaled']=True
  hit,point,normal,index=meshes[0].ray_cast(Vector((0,0,.2)),Vector((0,0,-1)))
  if not hit:raise RuntimeError('Cannot identify actual MOSSLANDA support floor')
  trayZ=point.z;r['tray_support_local_z_m']=trayZ;r['tray_support_world_z_m']=r.location.z+trayZ;r['back_lip_top_world_z_m']=r.location.z+.070000015;r['front_lip_top_world_z_m']=r.location.z+.03000001
  supports.append({'id':id,'tray_support_world_z_m':r.location.z+trayZ,'back_lip_top_world_z_m':r.location.z+.070000015,'front_lip_top_world_z_m':r.location.z+.03000001})
  # Few generic small books on the usable tray; decor only, no claimed purchases.
  bookroot=bpy.data.objects.new(id+'::illustrative pocket journals',None);collection.objects.link(bookroot);bookroot.parent=r;bookroot['assumption']='Illustrative face-out14cm-high pocket journals with89mm covers and10mm thickness; no purchase/product identity';bookroot['role']='furniture';bookroot['walk_blocker']=False
  for k,(x,w,h,color) in enumerate([(-.36,.089,.140,(.055,.060,.064)),(-.25,.089,.135,(.22,.24,.245)),(-.14,.089,.145,(.46,.47,.45))]):
   m=material('Illustrative calm book '+str(k),color,.8);o=box(id+'::illustrative pocket journal'+str(k),(x,.025,trayZ+h/2),(w,.010,h),m,collection,bookroot,bevel=.001);tagged(o)
 # Supplier FADO body preserved1:1; source cord is NOT treated as globe diameter.
 dresserZ=floor+.7493;r=root('dresser-fado','fado-kajplats-opal-table-lamp',[-6.80,-2.51,dresserZ],[.23988155,.23988153,.23648912],kind='table_lamp',support_product_id='clothes-dresser',catalog_body_dimensions_m=[.254,.254,.2286],source_body_geometry_preserved=True)
 imported=import_cad(source/'fado-official.glb');body_center=.11644313856959343;body_parts=[]
 for original in imported:
  bm=bmesh.new();bm.from_mesh(original.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.verts.ensure_lookup_table();seen=set()
  for v in bm.verts:
   if v in seen:continue
   queue=[v];seen.add(v);component=[]
   while queue:
    a=queue.pop();component.append(a)
    for e in a.link_edges:
     q=e.other_vert(a)
     if q not in seen:seen.add(q);queue.append(q)
   if len(component)not in [7426,2097,896]:continue
   selected=set(component);verts=list(component);idx={v:i for i,v in enumerate(verts)};faces=[f for f in bm.faces if all(v in selected for v in f.verts)]
   mesh=bpy.data.meshes.new('Original FADO source body component');mesh.from_pydata([(v.co.x-body_center,v.co.y,v.co.z)for v in verts],[],[[idx[v]for v in f.verts]for f in faces]);mesh.update()
   o=bpy.data.objects.new('dresser-fado::original body component'+str(len(body_parts)),mesh);collection.objects.link(o);o.parent=r;tagged(o);o['source_geometry_unscaled']=True
   if len(component)==7426:
    m=material('FADO opal glass neutral white glow',(.76,.79,.82),.32);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.05;p.inputs['Emission Color'].default_value=(.76,.82,.90,1);p.inputs['Emission Strength'].default_value=.55
   else:m=material('FADO original white polymer base/feet',(.72,.75,.78),.5)
   mesh.materials.append(m)
   for f in mesh.polygons:f.use_smooth=True
   body_parts.append(o)
  bm.free();bpy.data.objects.remove(original,do_unlink=True)
 if len(body_parts)!=4:raise RuntimeError('FADO supplier body separation differs from verified connected component counts')
 r['source_cord_handling']='Original cord/switch excluded from body dimension fit. Separate illustrative cord route down dresser rear; outlet reach/location unverified.'
 cord=material('Illustrative FADO cord',(.018,.019,.020),.8)
 path=[(-6.80,-2.60,dresserZ+.008),(-6.80,-2.758,dresserZ+.008),(-6.80,-2.758,floor+.06)]
 for k in range(2):o=rod('dresser-fado::illustrative rear cord'+str(k),path[k],path[k+1],.0014,cord,collection);o['role']='furniture';o['walk_blocker']=False;o['assumption']='Cable routing illustration; real outlet unrecorded'
 supports.append({'id':'dresser-fado','support_world_z_m':dresserZ,'source_body_diameter_m':.23988155,'source_body_height_m':.23648912,'catalog_body_diameter_height_m':[.254,.2286],'source_cord_in_total_bounds':True,'whole_source_scaled':False})
 # Small source-selected parlor palm: bounded tabletop foliage, never a floor plant.
 r=root('dresser-parlor-palm','sill-small-parlor-westcott-black',[-6.40,-2.51,dresserZ],[.28,.28,.2794],kind='tabletop_plant',support_product_id='clothes-dresser',published_outer_pot_diameter_m=.127,proxy_crown_width_m=.28,proxy_total_height_m=.2794,shape_confidence='Representative small plant/pot silhouette; pot height and live crown size unpublished. Source6-11in refers nursery pot-bottom to foliage-top, not guaranteed outer-pot assembly.')
 pot=material('Westcott chosen black ceramic proxy',(.008,.010,.012),.36);soil=material('Parlor soil proxy',(.018,.012,.008),.95);leaf=material('Small parlor palm representative foliage',(.026,.075,.035),.61)
 tagged(cylinder('dresser-parlor-palm::black saucer',(0,0,.004),.0635,.008,pot,collection,r,vertices=64))
 bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=.052,radius2=.060,depth=.096,location=(0,0,.056));o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.name='dresser-parlor-palm::black Westcott pot proxy';o.parent=r;o.data.materials.append(pot);tagged(o)
 tagged(cylinder('dresser-parlor-palm::soil',(0,0,.103),.0535,.004,soil,collection,r,vertices=48))
 for j in range(7):
  angle=j*2*math.pi/7;reach=.105 if j%2 else .12;top=.2794 if j==0 else .245+.009*(j%3)
  a=Vector((0,0,.106));b=Vector((math.cos(angle)*reach,math.sin(angle)*reach,top))
  tagged(rod('dresser-parlor-palm::thin palm rachis'+str(j),a,b,.00075,leaf,collection,r,vertices=8))
  for k in range(2,9):
   t=k/10;c=a.lerp(b,t);side=Vector((-math.sin(angle),math.cos(angle),-.18));length=.028*(1-t)+.009
   for sign in [-1,1]:
    tip=c+side*sign*length;tip.z-=.004;mid=(c+tip)/2;per=Vector((math.cos(angle)*.0025,math.sin(angle)*.0025,0));mesh=bpy.data.meshes.new('Small palm leaflet mesh');mesh.from_pydata([c,mid+per,tip,mid-per],[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('dresser-parlor-palm::representative leaflet',mesh);collection.objects.link(o);o.parent=r;mesh.materials.append(leaf);tagged(o)
 supports.append({'id':'dresser-parlor-palm','support_world_z_m':dresserZ,'outer_pot_diameter_m':.127,'proxy_crown_envelope_m':[.28,.28,.2794],'shape_dimensions_unpublished':True})
 # Generic small tray; illustrative only, useful front part of dresser retained.
 trayroot=bpy.data.objects.new('dresser::illustrative small tray',None);collection.objects.link(trayroot);trayroot.location=(-6.60,-2.40,dresserZ);trayroot['role']='furniture';trayroot['walk_blocker']=False;trayroot['assumption']='Illustrative14x12cm tray; no retailer product/purchase included'
 tm=material('Illustrative tray matte dark gray',(.035,.038,.041),.74)
 tagged(box('dresser::illustrative tray base',(0,0,.004),(.14,.12,.008),tm,collection,trayroot,bevel=.005))
 for x in [-.068,.068]:tagged(box('dresser::illustrative tray rim',(x,0,.010),(.004,.12,.012),tm,collection,trayroot,bevel=.001))
 for y in [-.058,.058]:tagged(box('dresser::illustrative tray rim',(0,y,.010),(.132,.004,.012),tm,collection,trayroot,bevel=.001))
 # Mat is an independent moving accessory on main desk only; monitor/keyboard rest on its top.
 r=root('primary-felt-mat','grovemade-dark-grey-medium-plus',[-6.915,-.131,floor+.740+.0035/2],[.9652,.40005,.0035],kind='desk_mat',support_product_id='standing-main-desk',moves_with='standing-main-desk',supplier_lift_group='desktop',canonical_owner='standing-main-desk',viewer_desk_height_factor=1)
 felt=material('Grovemade chosen dark gray Merino felt proxy',(.055,.059,.062),.94);p=felt.node_tree.nodes.get('Principled BSDF');n=felt.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=170;b=felt.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.1;b.inputs['Distance'].default_value=.0002;felt.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);felt.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 tagged(box('primary-felt-mat::MediumPlus darkgray wool felt',(0,0,0),(.9652,.40005,.0035),felt,collection,r,bevel=.001),'standing-main-desk')
 supports.append({'id':'primary-felt-mat','support_world_z_m':floor+.740,'top_world_z_m':floor+.7435,'moves_with':'standing-main-desk','monitor_keyboard_support':'Both resting on mat; keyboard rear-adjusted50mm after rootequipment−75mm shift.'})
 layout['items'].extend(items);layout['composition_supports']=supports
 return supports
