import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment-furniture/furniture.blend')
p=bpy.data.objects['her-loveseat'];result=[]
for o in bpy.data.objects:
 if o.parent!=p or o.type!='MESH':continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];xyz=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
 result.append({'name':o.name,'bounds':xyz})
json.dump(result,open('/workspace/apartment-furniture/loveseat-component-bounds.json','w'),indent=2)
