import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/workspace/apartment-model')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'repaired-apartment.blend'))
s=bpy.context.scene
fix=bpy.data.collections.new('05 Observed Fixed Fixture Proxies');s.collection.children.link(fix)
unc=bpy.data.collections.new('06 Unrecorded Utility Interiors — Listing Inference');s.collection.children.link(unc)
def mat(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.6;return m
white=mat('Fixture porcelain',(.82,.83,.81));dark=mat('Existing dark countertop proxy',(.08,.075,.068));oak=mat('Existing kitchen cabinet proxy',(.44,.37,.25));steel=mat('Existing appliance proxy',(.22,.24,.25));blue=mat('Unrecorded listing-only architecture',(.50,.63,.68));pale=mat('Pale glass',(.40,.61,.66));trim=mat('Window/door trim',(.85,.83,.78));water=mat('Inset basin',(.42,.48,.46));glass=mat('Window glass',(.45,.62,.68));glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.45;glass.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.14
records=[]
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
def box(name,pos,dim,m=white,c=fix,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);move(o,c)
 if bevel:
  mod=o.modifiers.new('Rounded proxy edge','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 o['confidence']='fixture location observed; exact product shape approximated' if c==fix else 'unrecorded interior inferred only from listing topology'
 return o
def cyl(name,pos,dim,m=white,c=fix):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=pos);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);move(o,c);return o
def countertop(name,pos,dim):
 box(name+' cabinet',pos,dim,oak,bevel=.025);x,y,z=pos;w,d,h=dim;box(name+' countertop',(x,y,z+h/2+.025),(w+.03,d+.03,.05),dark,bevel=.01)
 # Front-panel cues are shape proxies; not dimensions of unseen cabinetry.
 for i in range(max(1,int(w/.5))):
  xx=x-w/2+(i+.5)*w/max(1,int(w/.5));box(name+' panel',(xx,y+d/2+.008,z),(w/max(1,int(w/.5))-.028,.013,h-.045),oak,bevel=.015)
# Upper kitchen measured cabinet run + end sink; size proxies only.
fu=1.565
countertop('Upper kitchen lower run',(-5.60,.74,fu+.43),(3.4,.66,.86))
countertop('Upper kitchen end sink',(-7.60,1.70,fu+.43),(.67,1.15,.86))
box('Upper kitchen refrigerator',(-2.65,.74,fu+.93),(1.02,.68,1.86),steel,bevel=.045)
box('Upper refrigerator door seam',(-2.65,1.088,fu+.58),(1.015,.012,.015),dark)
box('Upper cooking range',(-5.48,.76,fu+.45),(.65,.68,.90),steel,bevel=.025)
box('Upper cooking surface',(-5.48,.76,fu+.925),(.66,.69,.04),dark)
for x in [-5.65,-5.32]:
 for y in [.59,.91]:cyl('Upper burner',(x,y,fu+.96),(.14,.14,.018),dark)
box('Upper sink inset',(-7.60,1.70,fu+.89),(.44,.60,.04),steel,bevel=.035)
for x in [-6.85,-6.2,-5.0,-4.35]:box('Upper cabinet box',(x,.56,fu+1.72),(.60,.42,.63),oak,bevel=.015)
# Lower kitchen: front-end cabinet/kitchenette locations preserved from scan, generalized envelopes.
fl=-1.385
countertop('Lower kitchen front run',(7.47,-.09,fl+.43),(.66,2.22,.86))
countertop('Lower kitchen return',(6.78,-1.77,fl+.43),(1.74,.61,.86))
box('Lower refrigerator',(7.34,1.75,fl+.91),(.78,.76,1.82),steel,bevel=.045)
box('Lower range',(7.43,-.94,fl+.45),(.68,.63,.90),steel,bevel=.025)
box('Lower sink inset',(6.67,-1.77,fl+.91),(.57,.40,.035),steel,bevel=.025)
for y in [-.2,.50,1.1]:box('Lower upper cabinet',(7.59,y,fl+1.69),(.40,.61,.59),oak,bevel=.018)
# Upper bath fixture positions from scan and plan; no proposal applied here.
f=1.575
box('Upper tub outer',(-.46,2.32,f+.28),(1.48,.79,.56),white,bevel=.05)
box('Upper tub inset',(-.46,2.32,f+.566),(1.18,.52,.026),water,bevel=.06)
box('Upper bathroom vanity',(.34,.68,f+.43),(1.04,.48,.86),oak,bevel=.025)
box('Upper bathroom countertop',(.34,.68,f+.89),(1.08,.51,.045),dark,bevel=.018)
cyl('Upper bathroom basin',(.32,.68,f+.90),(.48,.32,.045),white)
box('Upper bathroom mirror',(.34,.408,f+1.59),(.65,.024,.76),steel,bevel=.018)
box('Upper toilet cistern',(.80,2.52,f+.64),(.37,.20,.42),white,bevel=.06)
cyl('Upper toilet bowl',(.80,2.22,f+.39),(.42,.60,.26),white)
box('Upper toilet pedestal',(.80,2.30,f+.18),(.25,.32,.36),white,bevel=.07)
# Transparent glazing & trim preserve the actual window holes; proxies are not new openings.
for x,yr in [(-7.98,(-.98,.03)),(7.88,(-2.41,-1.51)),(7.88,(-.50,.32)),(-7.98,(1.23,2.12))]:
 y=sum(yr)/2;h=1.85;bottom=2.38;top=bottom+h;width=yr[1]-yr[0]
 box('Window glazing',(x,y,(bottom+top)/2),(.012,width,h),glass)
 for yy in [yr[0],yr[1]]:box('Window vertical trim',(x,yy,(bottom+top)/2),(.08,.045,h+.09),trim)
 for z in [bottom,(bottom+top)/2,top]:box('Window horizontal trim',(x,y,z),(.08,width+.09,.045),trim)
# Listing-only lower bath/laundry/boiler rooms: spatial topology estimated, colored and separable.
inferred=[{'id':'bathroom-lower-unrecorded','bounds':[-3.80,-2.15,.61,2.40],'note':'listing-only inferred; geometry/dimensions unverified'},{'id':'laundry-unrecorded','bounds':[-2.15,-.65,.61,2.40],'note':'listing-only inferred; geometry/dimensions unverified'},{'id':'boiler-utility-unrecorded','bounds':[-6.65,-3.80,.52,1.95],'note':'listing-only inferred; geometry/dimensions unverified'}]
for rr in inferred:
 xa,xb,ya,yb=rr['bounds'];z=-1.415;top=1.245
 box(rr['id']+' floor',((xa+xb)/2,(ya+yb)/2,z-.03),(xb-xa,yb-ya,.06),blue,unc)
 # Outside boundary only; entrance opening locations deliberately left to evidence layer.
 box(rr['id']+' exterior north',((xa+xb)/2,yb,(z+top)/2),(xb-xa,.08,top-z),blue,unc)
 box(rr['id']+' right divider',(xb,(ya+yb)/2,(z+top)/2),(.06,yb-ya,top-z),blue,unc)
# Fixtures are generic, separated from observed proxies and explicitly listing-only.
box('INFERRED lower shower pan',(-2.55,1.96,-1.36),(.78,.78,.11),white,unc,bevel=.04)
box('INFERRED lower shower partition',(-2.20,1.96,-.39),(.025,.78,1.84),pale,unc)
cyl('INFERRED lower toilet',(-3.35,1.65,-1.02),(.42,.60,.32),white,unc)
box('INFERRED lower basin',(-3.35,2.18,-.63),(.53,.37,.12),white,unc,bevel=.03)
box('INFERRED laundry appliance',(-1.70,1.90,-.99),(.62,.67,.83),white,unc,bevel=.03)
box('INFERRED stacked laundry top',(-1.70,1.90,-.16),(.62,.67,.83),white,unc,bevel=.03)
# Add the 2-view room camera counterparts used for deterministic screenshots.
cameras={'kitchen-b':((-7.50,2.0,3.03),(-2.35,1.60,2.65)),'bathroom-a':((-1.07,.69,3.03),(.55,2.1,2.52)),'bathroom-b':((.92,2.53,3.03),(-.46,.69,2.50))}
lightcol=bpy.data.collections.get('04 Preview Lights and Cameras')
for name,(eye,target) in cameras.items():
 bpy.ops.object.camera_add(location=eye);o=bpy.context.object;o.name='CAM '+name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=21;o.data.clip_start=.04;move(o,lightcol)
# Explicit default: unseen utility layer can be revealed, never mixed with measured shell.
unc.hide_render=True;unc.hide_viewport=True
for col,name in [(fix,'observed-fixtures.glb'),(unc,'inferred-utility-shell.glb')]:
 col.hide_viewport=False;bpy.ops.object.select_all(action='DESELECT')
 for o in col.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/name),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_image_format='JPEG')
unc.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene-base.blend'))
json.dump({'observed_fixtures':'positions from scan; object envelopes/render forms approximate; fixture rendering does not imply measured SKU','inferred_utility_rooms':inferred,'visibility':'Observed fixture proxies are default clean-shell render. Unrecorded utility interiors are an independently toggleable listing-inference layer, excluded from design photos unless named.'},open(ROOT/'fixture-confidence.json','w'),indent=2)
print('FIXTURES_COMPLETE')
