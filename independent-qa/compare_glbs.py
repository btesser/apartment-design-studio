import json,struct,pathlib,numpy as np,contextlib,io,runpy
with contextlib.redirect_stdout(io.StringIO()):
    api=runpy.run_path('/workspace/independent-qa/audit_artifacts.py')
root=pathlib.Path('/workspace');target=root/'apartment-model/integrated-apartment.glb'
def read(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n])
def names(j):return {n['name'] for n in j.get('nodes',[]) if 'mesh'in n and 'name'in n}
def vertices(j):return sum(j['accessors'][p['attributes']['POSITION']]['count'] for m in j['meshes'] for p in m['primitives'])
i=read(target);have=names(i);tb=api['world_bounds'](target)
report={'target':str(target),'target_vertex_count':vertices(i),'target_mesh_count':len(i['meshes']),'layers':{}}
for f in ['architectural-shell.glb','observed-fixtures.glb','proposal-furniture.glb','proposed-dresser.glb','entry-design.glb']:
 p=root/'apartment-walkthrough/assets'/f;j=read(p);need=names(j);missing=sorted(need-have);sb=api['world_bounds'](p);deltas=[]
 for name,bounds in sb.items():
  if name not in tb:continue
  delta=float(np.max(np.abs(np.array(bounds)-np.array(tb[name]))))
  if delta>2e-5:deltas.append({'mesh':name,'max_world_bound_delta_m':round(delta,6)})
 report['layers'][f]={'mesh_nodes_expected':len(need),'mesh_nodes_missing':len(missing),'missing_names':missing,'source_vertex_count':vertices(j),'world_bound_mismatches':deltas}
json.dump(report,open(root/'independent-qa/integrated-inventory.json','w'),indent=2)
for f,r in report['layers'].items():print(f,'missing',r['mesh_nodes_missing'],'/',r['mesh_nodes_expected'],'changed_bounds',len(r['world_bound_mismatches']),r['world_bound_mismatches'][:3])
