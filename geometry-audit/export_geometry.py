import bpy, numpy as np, json
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
meta=[]
for obj in bpy.context.scene.objects:
 if obj.type != 'MESH' or not obj.name.startswith('Mesh_'):continue
 mat=np.array(obj.matrix_world);mesh=obj.data
 vv=np.array([list(v.co) for v in mesh.vertices]);vv=(vv@mat[:3,:3].T)+mat[:3,3]
 mesh.calc_loop_triangles();ff=np.array([list(p.vertices) for p in mesh.loop_triangles])
 np.savez_compressed('/workspace/geometry-audit/'+obj.name+'.npz',v=vv,f=ff)
 meta.append(dict(name=obj.name,nv=len(vv),nf=len(ff),min=vv.min(0).tolist(),max=vv.max(0).tolist(),matrix=mat.tolist()))
json.dump(meta,open('/workspace/geometry-audit/mesh_summary.json','w'),indent=2)
print(json.dumps(meta,indent=2))
