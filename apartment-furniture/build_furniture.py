import bpy, bmesh, math, json, random, os, sys
from mathutils import Matrix
from mathutils import Vector
ROOT='/workspace/apartment-furniture'; random.seed(81)
bpy.ops.wm.read_factory_settings(use_empty=True)
COL=bpy.data.collections.new('Amy proposed furniture — registered placement');bpy.context.scene.collection.children.link(COL)
MAT={}
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;MAT[name]=m;return m
mat('Camel fabric',(.50,.405,.285),.85);mat('Cream sheer',(.86,.845,.77),.85);mat('Charcoal leather',(.085,.095,.103),.38);mat('Warm ivory boucle',(.78,.74,.65),.85);mat('Ivory velvet',(.85,.82,.72),.7);mat('Blush pink velvet',(.59,.23,.3),.7);mat('Burnt orange chenille',(.36,.095,.032),.8);mat('Gold brushed metal',(.55,.37,.13),.27,.7);mat('Black steel',(.014,.018,.022),.45,.65);mat('White fluted cabinet',(.82,.81,.75),.5);mat('Walnut',(.205,.095,.038),.5);mat('Natural oak',(.51,.345,.185),.6);mat('Cane rattan',(.59,.435,.235),.86);mat('Teal painted wood',(.073,.255,.29),.6);mat('Linen sepia ebony',(.105,.098,.072),.85);mat('Fresh moss linen',(.17,.23,.098),.92);mat('Oat linen',(.68,.635,.53),.95);mat('Black marble',(.015,.019,.019),.26);mat('Tabletop ivory',(.86,.84,.76),.38);mat('Rug pink',(.61,.375,.375),1);mat('Rug tan',(.43,.31,.195),1);mat('Rug terracotta',(.44,.14,.08),1);mat('Rug ivory',(.76,.73,.66),1);mat('Rug ink',(.022,.031,.025),1);mat('Rug green',(.23,.25,.18),1);mat('Glass screen',(.009,.02,.032),.18);mat('Mirror approximation',(.63,.71,.72),.06,.9);mat('Off white shade',(.85,.81,.69),.9)
PARENT=None

def own(o,name,material):
 o.name=PARENT.name+'::'+name;o.parent=PARENT
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o)
 if material:o.data.materials.append(MAT[material])
 return o

def cube(name,xyz,whd,material,bevel=0):
 vs=[(x*whd[0]/2,y*whd[1]/2,z*whd[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);o=bpy.data.objects.new(name,mesh);COL.objects.link(o);o.location=xyz;own(o,name,material)
 if bevel:
  mod=o.modifiers.new('Soft furniture edges','BEVEL');mod.width=min(bevel,min(whd)*.45);mod.segments=3
  mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def cyl(name,xyz,r,h,material,verts=48):
 vs=[(r*math.cos(2*math.pi*i/verts),r*math.sin(2*math.pi*i/verts),z) for z in [-h/2,h/2] for i in range(verts)];fs=[tuple(reversed(range(verts))),tuple(range(verts,2*verts))]+[(i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);o=bpy.data.objects.new(name,mesh);COL.objects.link(o);o.location=xyz;own(o,name,material);m=o.modifiers.new('Rim softness','BEVEL');m.width=min(.014,h*.2);m.segments=2
 for p in o.data.polygons:p.use_smooth=True
 return o

def sphere(name,xyz,scale,material):
 mesh=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=20,v_segments=10,radius=1);bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);COL.objects.link(o);o.location=xyz;own(o,name,material);o.scale=scale
 for p in o.data.polygons:p.use_smooth=True
 return o

def rod(name,a,b,r,material):
 mid=(Vector(a)+Vector(b))/2;o=cyl(name,mid,r,(Vector(b)-Vector(a)).length,material,16);o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler();return o

def cone(name,xyz,r1,r2,h,material):
 n=48;vs=[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z) for r,z in [(r1,-h/2),(r2,h/2)] for i in range(n)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);o=bpy.data.objects.new(name,mesh);COL.objects.link(o);o.location=xyz;return own(o,name,material)

def sofa(it):
 w,d,h=it['dimensions'];velvet=it.get('material','Warm ivory boucle');legs=it.get('legs','Walnut');n=it.get('cushions',2)
 for x in [-w*.4,w*.4]:
  for y in [-d*.33,d*.33]:cyl('foot',(x,y,.095),.035,.19,legs)
 cube('seat base',(0,0,.3),(w,d*.92,.24),velvet,.065)
 for i in range(n):
  x=(i-(n-1)/2)*(w-.22)/n
  cube('seat cushion '+str(i),(x,d*.10,.47),((w-.24)/n-.012,d*.71,.19),velvet,.07)
  o=cube('back cushion '+str(i),(x,-d*.31,.71),((w-.22)/n-.013,.23,.48),velvet,.08);o.rotation_euler.x=math.radians(-9)
 for x in [-w/2+.06,w/2-.06]:cube('arm',(x,0,.59),(.135,d,.56),velvet,.06)
 if it.get('fluted'):
  for i in range(13):
   x=(i-6)*(w-.22)/13
   sphere('shell back lobe',(x,-d*.29,.68),((w-.22)/26,.14,.28+(.04*math.cos(i/12*math.pi))),velvet)
 if it.get('pillows',True):
  for i,x in enumerate([-w*.28,w*.28]):
   o=cube('accent pillow '+str(i),(x,-d*.08,.76),(.41,.14,.4),it.get('pillow_material','Oat linen'),.067);o.rotation_euler.x=-.24;o.rotation_euler.y=(-.12 if i==0 else .12)

def chair(it):
 w,d,h=it['dimensions'];m=it.get('material','Warm ivory boucle');swivel=it.get('swivel',False);office=it.get('office',False)
 if swivel or office:
  cyl('pedestal',(0,0,.2),.025,.35,'Gold brushed metal' if m=='Blush pink velvet' else 'Black steel')
  if office:
   for i in range(5):
    a=2*math.pi*i/5;rod('caster arm',(0,0,.12),(math.cos(a)*w*.43,math.sin(a)*w*.43,.09),.016,'Gold brushed metal' if m=='Blush pink velvet' else 'Black steel');sphere('caster',(math.cos(a)*w*.44,math.sin(a)*w*.44,.055),(.041,.041,.041),'Black steel')
  else:cyl('swivel base',(0,0,.075),w*.4,.10,'Black steel')
 else:
  for x in [-w*.35,w*.35]:
   for y in [-d*.33,d*.33]:rod('leg',(x,y,.05),(x*.9,y*.9,.45),.018,'Black steel')
 cube('seat',(0,.015,.46),(w*.9,d*.88,.14),m,.075)
 if not swivel:cube('back',(0,-d*.37,(h+.48)/2),(w*.94,.12,h-.45),m,.09)
 else:
  vs=[];fs=[];n=42
  for i in range(n+1):
   a=math.radians(30+300*i/n);z=.62+(h-.62)*max(0,-math.cos(a))
   for rr,zz in [(0,.43),(0,z),(1,.43),(1,z)]:
    rx=w/2-(.085 if rr else 0);ry=d/2-(.085 if rr else 0);vs.append((rx*math.sin(a),ry*math.cos(a),zz))
  for i in range(n):
   b=4*i;fs.extend([(b,b+4,b+5,b+1),(b+2,b+3,b+7,b+6),(b+1,b+5,b+7,b+3),(b,b+2,b+6,b+4)])
  mesh=bpy.data.meshes.new('curved tub-chair back');mesh.from_pydata(vs,[],fs);o=bpy.data.objects.new('curved tub-chair back',mesh);COL.objects.link(o);own(o,'continuous curved orange back',m)
  for pp in mesh.polygons:pp.use_smooth=True
 if it.get('arms',True) and not swivel:
  for x in [-w*.44,w*.44]:cube('arm',(x,-.02,.64),(.115,d*.74,.27),m,.054)
 if office and m!='Blush pink velvet':
  cube('mesh lumbar',(0,-d*.28,.74),(w*.72,.035,.25),'Black steel',.02)

def cabinet(it):
 w,d,h=it['dimensions'];m=it.get('material','White fluted cabinet');leg=.11
 cube('body',(0,0,(h+leg)/2),(w,d,h-leg),m,.025)
 for x in [-w*.4,w*.4]:
  for y in [-d*.33,d*.33]:cyl('leg',(x,y,leg/2),.018,leg,it.get('leg_material','Black steel'))
 rows=it.get('rows',2);cols=it.get('cols',2)
 for i in range(rows):
  z=leg+(h-leg)*(i+.5)/rows
  for j in range(cols):
   x=(j-(cols-1)/2)*w/cols;cube('drawer front',(x,d/2+.003,z),(w/cols-.01,.013,(h-leg)/rows-.012),m,.003);cube('drawer pull',(x,d/2+.019,z+.035),(.10,.016,.011),'Gold brushed metal',.004)
 if it.get('fluted',True):
  for i in range(int(w/.023)):
   x=-w/2+.012+i*.023;cube('flute',(x,d/2+.013,(h+leg)/2),(.009,.009,h-leg-.02),m,.004)

def desk(it):
 w,d,h=it['dimensions'];m=it.get('material','Walnut');cube('top',(0,0,h-.025),(w,d,.05),m,.018)
 if it.get('vanity'):
  for x in [-w*.35,w*.35]:
   cube('drawer bank',(x,-.04,h*.45),(w*.24,d*.85,h*.75),m,.012)
   for z in [.22,.4,.58]:cube('gold drawer pull',(x,d*.435,z),(.17,.015,.012),'Gold brushed metal',.006)
  cube('apron',(0,-.17,h-.11),(w*.47,.2,.13),m,.007)
  mw,mh=.813,.559
  cube('mirror frame',(0,-d*.38,h+.34),(mw,.035,mh),'Gold brushed metal',.015);cube('mirror glass',(0,-d*.38+.023,h+.34),(mw-.03,.011,mh-.03),'Mirror approximation',.006)
 else:
  for x in [-w*.39,w*.39]:
   cube('standing desk column',(x,0,h/2),(.065,.09,h-.05),'Black steel',.007);cube('standing desk foot',(x,0,.035),(.065,d*.85,.045),'Black steel',.014)
  cube('monitor',(0,-d*.33,h+.3),(.72,.038,.40),'Black steel',.008);cube('screen',(0,-d*.33+.025,h+.3),(.69,.009,.367),'Glass screen',.002);cyl('monitor stand',(0,-d*.33,h+.07),.015,.14,'Black steel');cube('keyboard',(0,d*.15,h+.015),(.42,.13,.017),'Black steel',.003)

def table(it):
 w,d,h=it['dimensions'];m=it.get('material','Natural oak')
 if it.get('round'):
  cyl('table top',(0,0,h-.024),w/2,.048,m)
  if it.get('pedestal',True):
   cyl('table pedestal',(0,0,h*.45),w*.1,h*.9,it.get('base_material',m));cone('flared base',(0,0,.075),w*.34,w*.10,.14,it.get('base_material',m))
  else:
   for i in range(3):
    a=i*2*math.pi/3;rod('table leg',(w*.33*math.cos(a),w*.33*math.sin(a),.025),(w*.25*math.cos(a+.8),w*.25*math.sin(a+.8),h-.04),.023,it.get('base_material','Gold brushed metal'))
 elif it.get('oval'):
  sphere('oval top',(0,0,h-.026),(w/2,d/2,.038),m)
  for x in [-w*.25,w*.25]:cone('sculptural pedestal',(x,0,(h-.05)/2),d*.21,d*.25,h-.05,m)
 else:
  cube('dining top',(0,0,h-.032),(w,d,.064),m,.016)
  for x in [-w*.41,w*.41]:
   for y in [-d*.36,d*.36]:cube('table leg',(x,y,(h-.065)/2),(.085,.085,h-.065),m,.01)

def bed(it):
 w,d,h=it['dimensions'];m='Walnut';cube('frame',(0,0,.285),(w,d,.21),m,.019);cube('king mattress 76 by 80 inches',(0,.005,.485),(1.9304,2.032,.21),'Oat linen',.061)
 for x in [-w*.46,w*.46]:
  for y in [-d*.43,d*.43]:cyl('bed leg',(x,y,.15),.042,.3,m)
 cube('moss duvet',(0,.35,.615),(w-.015,d*.68,.052),'Fresh moss linen',.037)
 for x in [-.48,.48]:
  cube('oat pillow',(x,-d*.30,.66),(.81,.41,.16),'Oat linen',.07)
  cube('moss pillow',(x,-d*.18,.70),(.68,.18,.31),'Fresh moss linen',.06)
 cube('blue lumbar',(0,-d*.10,.75),(.88,.13,.24),'Teal painted wood',.055)
 # Elliptical cane headboard with timber border, flat lower edge, arched upper profile.
 verts=[]
 for side in [0,1]:
  y=-d/2+side*.055
  verts.extend([(-w/2,y,.55),(w/2,y,.55)])
  for i in range(25):
   a=i*math.pi/24;verts.append((w/2*math.cos(a),y,.71+.36*math.sin(a)))
 faces=[];N=27
 faces.append(tuple(range(N)));faces.append(tuple(range(N,2*N)))
 for i in range(N):faces.append((i,(i+1)%N,(i+1)%N+N,i+N))
 mesh=bpy.data.meshes.new('arched timber and cane mesh');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new('arched cane headboard',mesh);COL.objects.link(o);o.parent=PARENT;o.data.materials.append(MAT['Cane rattan'])
 for i in range(25):
  a=i*math.pi/24;b=(i+1)*math.pi/24
  rod('arched walnut rail',(w/2*math.cos(a),-d/2+.065,.71+.36*math.sin(a)),(w/2*math.cos(b),-d/2+.065,.71+.36*math.sin(b)),.026,m)
 for x in [-w/2,w/2]:rod('headboard post',(x,-d/2,.24),(x,-d/2,.71),.028,m)
 for i in range(53):
  x=-w/2+.02+i*(w-.04)/52;t=.71+.36*math.sqrt(max(0,1-(x/(w/2))**2));rod('cane vertical weave',(x,-d/2+.061,.56),(x,-d/2+.061,t-.035),.0025,'Natural oak')
 for z in [.6+i*.035 for i in range(14)]:
  x=w/2*math.sqrt(max(0,1-((z-.71)/.36)**2));rod('cane horizontal weave',(-x,-d/2+.063,z),(x,-d/2+.063,z),.0025,'Natural oak')

def rug(it):
 w,d,h=it['dimensions'];m=it.get('material','Rug ivory')
 if it.get('round'):cyl('round rug',(0,0,.005),w/2,.01,m,64)
 else:
  cube('woven rug',(0,0,.005),(w,d,.01),m)
  pattern=it.get('pattern')
  if pattern=='living':
   for t,ma in [(.12,'Rug ink'),(.18,'Rug terracotta'),(.40,'Rug tan'),(.47,'Rug ink')]:
    for x in [-w/2+t,w/2-t]:cube('graphic border',(x,0,.012),(.035,d-2*t,.008),ma)
    for y in [-d/2+t,d/2-t]:cube('graphic border',(0,y,.012),(w-2*t,.035,.008),ma)
   cube('pink centre',(0,0,.013),(w-.96,d-.96,.006),'Rug pink')
  elif pattern=='nazco':
   for x in [-w*.33,0,w*.33]:
    coords=[]
    for i in range(37):
     y=-d/2+.06+i*(d-.12)/36;coords.append((x+.1*math.sin(i/36*6*math.pi),y,.012))
    for a,b in zip(coords,coords[1:]):rod('organic black line',a,b,.018,'Rug ink')
  elif pattern=='office':
   for i in range(80):
    x=random.uniform(-w*.44,w*.44);y=random.uniform(-d*.44,d*.44);cube('abstract fleck',(x,y,.013),(random.uniform(.05,.23),random.uniform(.02,.17),.005),random.choice(['Rug ink','Rug tan']))
  elif pattern=='bedroom':
   for x in [-w/2+.08,w/2-.08]:cube('rug border',(x,0,.012),(.075,d,.005),'Rug tan')
   for y in [-d/2+.08,d/2-.08]:cube('rug border',(0,y,.012),(w,.075,.005),'Rug tan')
   for i in range(22):
    a=i*2*math.pi/22;sphere('muted floral motif',(w*.29*math.cos(a),d*.33*math.sin(a),.012),(.055,.075,.005),'Rug pink')

def shelf(it):
 w,d,h=it['dimensions'];m='Walnut';cube('back',(0,-d/2+.008,h/2),(w,.015,h),m)
 for x in [-w/2+.007,w/2-.007]:cube('side',(x,0,h/2),(.014,d,h),m)
 for i in range(6):cube('shelf',(0,0,.012+(h-.025)*i/5),(w,d,.016),m)

def lamp(it):
 w,d,h=it['dimensions'];m=it.get('material','Black steel');cyl('base',(0,0,.025),w*.3,.05,m);cyl('stem',(0,0,h*.43),.013,h*.82,m)
 cone('linen shade',(0,0,h*.87),w/2,w*.4,h*.26,it.get('shade','Off white shade'))

def curtain(it):
 w,d,h=it['dimensions'];rod('white divider rail',(-w/2,0,h),(w/2,0,h),.016,'White fluted cabinet')
 verts=[];faces=[];n=140
 # Curtain drawn partially back at circulation end rather than walling off bedroom access.
 for i in range(n+1):
  x=-w/2+i*w/n;y=.034*math.cos(2*math.pi*i/7)
  verts.extend([(x,y,.035),(x,y,h-.035)])
 for i in range(n):faces.append((2*i,2*i+1,2*i+3,2*i+2))
 mesh=bpy.data.meshes.new('continuous pleated drapery');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new(PARENT.name+'::sepia blackout divider',mesh);COL.objects.link(o);o.parent=PARENT;mesh.materials.append(MAT['Linen sepia ebony']);mod=o.modifiers.new('Fabric thickness','SOLIDIFY');mod.thickness=.002

def console(it):
 w,d,h=it['dimensions'];m=it.get('material','Walnut');cube('top',(0,0,h-.02),(w,d,.04),m,.01);cube('lower shelf',(0,0,.36),(w,d,.025),m,.01)
 for x in [-w*.47,w*.47]:
  for y in [-d*.38,d*.38]:cube('steel frame',(x,y,h/2),(.021,.021,h),'Black steel',.003)

def tv(it):
 w,d,h=it['dimensions'];cube('TV frame',(0,0,h/2),(w,d,h),'Black steel',.009);cube('dark TV panel',(0,d/2+.004,h/2),(w-.04,.009,h-.04),'Glass screen',.002)

def window_curtain(it):
 w,d,h=it['dimensions'];rod('curtain rod',(-w/2,0,h),(w/2,0,h),.011,'Gold brushed metal')
 for side in [-1,1]:
  vs=[];fs=[];n=32;panel=.27
  for i in range(n+1):
   x=side*(w/2-panel+i*panel/n);y=.021*math.cos(i/32*10*math.pi)
   vs.extend([(x,y,.02),(x,y,h-.02)])
  for i in range(n):fs.append((2*i,2*i+1,2*i+3,2*i+2))
  mesh=bpy.data.meshes.new('soft cream sheer folds');mesh.from_pydata(vs,[],fs);o=bpy.data.objects.new('cream sheer panel',mesh);COL.objects.link(o);own(o,'cream sheer panel','Cream sheer');mod=o.modifiers.new('Fabric thickness','SOLIDIFY');mod.thickness=.001

BUILD={'window_curtain':window_curtain,'sofa':sofa,'chair':chair,'cabinet':cabinet,'desk':desk,'table':table,'bed':bed,'rug':rug,'shelf':shelf,'lamp':lamp,'curtain':curtain,'console':console,'tv':tv}
sys.path.insert(0,ROOT)
from decor_helpers import make_builders
BUILD.update(make_builders(globals()))
layout=json.load(open(ROOT+'/placements.json'))
for it in layout['items']:
 PARENT=bpy.data.objects.new(it['id'],None);COL.objects.link(PARENT);PARENT.empty_display_type='PLAIN_AXES';PARENT['room']=it['room'];PARENT['source']=it.get('source','Amy Wu design board and plan');PARENT['dimension_confidence']=it.get('dimension_confidence','assumed concept')
 BUILD[it['kind']](it)
 if it['kind'] in ['bed','sofa']:
  bpy.context.view_layer.update();children=[o for o in COL.objects if o.parent==PARENT and o.type=='MESH'];pts=[o.matrix_world@Vector(c) for o in children for c in o.bound_box];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];dim=it['dimensions'];sf=[dim[k]/(hi[k]-lo[k]) for k in range(3)];S=Matrix.Diagonal((*sf,1));T=Matrix.Translation((-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]))
  for o in children:o.data.transform(S@T@o.matrix_world);o.matrix_basis=Matrix.Identity(4)
 PARENT.location=it['position'];PARENT.rotation_euler.z=math.radians(it['rotation_deg'])
 # Manifest world footprint independent of shape detail.
 x,y,z=it['position'];w,d,h=it['dimensions'];a=math.radians(it['rotation_deg'])
 it['footprint_blender_xy']=[[round(x+math.cos(a)*u-math.sin(a)*v,6),round(y+math.sin(a)*u+math.cos(a)*v,6)] for u,v in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
 it['front_blender_xy']=[round(-math.sin(a),6),round(math.cos(a),6)];it['facing_blender_xy']=it['front_blender_xy'];it['front_meaning']='seat gaze' if it['kind']=='chair' else ('user side of work surface; seated gaze is opposite' if it['kind']=='desk' else 'front of furniture');
 if it['kind']=='desk':it['seated_gaze_blender_xy']=[round(math.sin(a),6),round(-math.cos(a),6)]
 it['viewer_position']=[x,z,-y]
 it['viewer_facing']=[-math.sin(a),0,-math.cos(a)]
layout['coordinate_frame']='Meters; source Blender X/Y/Z unscaled with Z-up. GLB exporter maps (x,y,z) to (x,z,-y), Y-up.'
layout['source_plan_registration']='Every Amy floor plan fragment: image u-right -> scan +Y; image v-down -> scan +X, established by room doors, exterior windows and fireplace.'
layout['limitations']=['Furniture is dimensioned concept geometry approximating the selected products, not vendor CAD. Axis dimension confidence is explicit for each item.','Existing sofa and desk external dimensions remain unmeasured. All positions are wall-relative registered interpretations of Amy\'s diagram.','Curtain proposal is opened at the side for access. Divider railing/drape purchase lengths and ceiling height need field verification.']
json.dump(layout,open(ROOT+'/furniture-manifest.json','w'),indent=2)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;
if not s.world:s.world=bpy.data.worlds.new('Furniture preview world')
s.world.color=(.25,.25,.25);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/furniture.blend')
# Dresser is separately exported so the walkthrough can reveal the genuine clearance conflict.
bpy.ops.object.select_all(action='DESELECT')
for o in COL.objects:
 if o.name=='bedroom-large-dresser' or o.name.startswith('bedroom-large-dresser::'):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT+'/proposed-dresser.glb',export_format='GLB',use_selection=True,export_extras=True,export_apply=True)
bpy.ops.object.select_all(action='DESELECT')
for o in COL.objects:
 if not(o.name=='bedroom-large-dresser' or o.name.startswith('bedroom-large-dresser::')):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT+'/furniture.glb',export_format='GLB',use_selection=True,export_extras=True,export_apply=True)
print('FURNITURE_EXPORT_COMPLETE',len(layout['items']),len(COL.objects))
