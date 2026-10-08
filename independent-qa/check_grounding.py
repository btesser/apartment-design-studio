import pathlib,json,contextlib,io,runpy
with contextlib.redirect_stdout(io.StringIO()):api=runpy.run_path('/workspace/independent-qa/audit_artifacts.py')
root=pathlib.Path('/workspace');bounds=api['world_bounds'](root/'apartment-model/integrated-apartment.glb')
floor_upper=bounds['architecture_floor — living'][0][1];floor_lower=bounds['architecture_floor — basement-open'][0][1]
rows=[]
for item,floor in [('entry-gold-console',floor_upper),('entry-rattan-shoe-cabinet',floor_upper),('bedroom-king-bed',floor_lower),('bedroom-nightstand-1',floor_lower),('bedroom-nightstand-2',floor_lower),('bedroom-large-dresser',floor_lower)]:
 parts=[b for name,b in bounds.items() if name.startswith(item+'::')]
 if not parts:raise ValueError('Missing support mesh: '+item)
 bottom=min(b[0][1] for b in parts);gap=bottom-floor;rows.append({'item':item,'model_floor_y_m':floor,'actual_lowest_mesh_y_m':bottom,'gap_m':gap,'grounded':abs(gap)<.0002})
report={'coordinates':'GLTF Y-up; actual exported mesh extrema compared to clean architecture planes','items':rows,'all_grounded':all(r['grounded'] for r in rows)}
json.dump(report,open(root/'independent-qa/vertical-grounding.json','w'),indent=2);print(json.dumps(report,indent=2))
