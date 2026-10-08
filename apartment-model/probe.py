import bpy,json,numpy as np
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
summary=[]
for o in bpy.data.objects:
 if o.type!='MESH': continue
 vs=np.array([o.matrix_world@v.co for v in o.data.vertices]); tri=np.array([p.vertices[:] for p in o.data.polygons])
 print(o.name,len(vs),len(tri),'bound',np.round(vs.min(axis=0),3),np.round(vs.max(axis=0),3),'median',np.round(np.median(vs,axis=0),3))
 summary.append({'name':o.name,'nvertices':len(vs),'nfaces':len(tri),'bounds':[vs.min(axis=0).tolist(),vs.max(axis=0).tolist()]})
 np.savez_compressed('/workspace/apartment-model/'+o.name+'.npz',vertices=vs,faces=tri)
json.dump(summary,open('/workspace/apartment-model/scan-object-summary.json','w'),indent=2)
