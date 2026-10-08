import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment-model/integrated.blend')
out={'collections':[], 'objects':[]}
for c in bpy.data.collections:
 out['collections'].append({'name':c.name,'n_objects':len(c.objects),'children':[x.name for x in c.children]})
for o in bpy.data.objects:
 if o.type=='MESH':
  bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in bb) for i in range(3)];hi=[max(p[i] for p in bb) for i in range(3)]
  if hi[0]<-8.5 or lo[0]>-2.8 or hi[1]<-3.2 or lo[1]>.7 or hi[2]<1.3 or lo[2]>4.9:continue
  out['objects'].append({'name':o.name,'collections':[c.name for c in o.users_collection],'min':lo,'max':hi,'props':{k:o[k] for k in o.keys() if isinstance(o[k],(str,int,float,bool))}})
json.dump(out,open('/workspace/his-office-redesign/geometry/model-source-pointers.json','w'),indent=2)
print(json.dumps({'collections':out['collections'],'objects':[{k:v for k,v in o.items() if k!='props'} for o in out['objects']]},indent=2))
