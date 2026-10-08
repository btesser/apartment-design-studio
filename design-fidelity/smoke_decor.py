import sys
sys.path.insert(0,'/workspace/apartment-furniture')
source=open('/workspace/apartment-furniture/build_furniture.py').read().split("layout=json.load")[0]
exec(compile(source,'furniture_prefix','exec'),globals())
from decor_helpers import make_builders
builders=make_builders(globals())
for i,(kind,builder) in enumerate(builders.items()):
 PARENT=bpy.data.objects.new(kind,None);COL.objects.link(PARENT)
 it={'id':kind,'dimensions':[.7,.7,1.0] if kind=='chandelier' else [.8,.06,1.0] if kind=='art' else [.25,.25,1.1]}
 builder(it);PARENT.location.x=i*.9
bpy.context.view_layer.update()
print('DECOR_SMOKE',list(builders),len(COL.objects))
for ob in COL.objects:
 if ob.type=='MESH':
  assert all(math.isfinite(v) for v in ob.location),ob.name
bpy.ops.wm.save_as_mainfile(filepath='/workspace/design-fidelity/decor-smoke.blend')
