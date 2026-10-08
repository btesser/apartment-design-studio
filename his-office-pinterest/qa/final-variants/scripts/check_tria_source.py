"""Independent supplier-CAD shape/pose check; never saves Blender artifacts."""
import bpy
import hashlib
import json
import sys
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:]
ROOT=Path(args[0]);QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
SOURCE=ROOT/'model/his-office-design.blend'
CAD=Path('/workspace/his-office-pinterest/products/standing-desk-candidates/branch-tria-official-48x27-woodgrain-white.glb')
MAPPING=ROOT/'model/tria-component-map.json'
mapping=json.loads(MAPPING.read_text());layout=json.loads((ROOT/'model/layout.json').read_text())
spec=next(i for i in layout['items'] if i['id']=='standing-main-desk')
file_hash=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert file_hash(CAD)==mapping['supplier_source_sha256']


def capture(objects):
    deps=bpy.context.evaluated_depsgraph_get();out={}
    for o in objects:
        if o.type!='MESH':continue
        ev=o.evaluated_get(deps);m=ev.to_mesh()
        out[o.name]={'points':[list(ev.matrix_world@v.co) for v in m.vertices],
                     'faces':[list(p.vertices) for p in m.polygons]}
        ev.to_mesh_clear()
    return out


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
current=capture([bpy.data.objects[p['name']] for p in mapping['parts']])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(CAD))
supplier=capture(bpy.context.scene.objects)
checks=[]
for p in mapping['parts']:
    a=current[p['name']];b=supplier.get(p['source_name'])
    shift=Vector(spec['position_blender_m'])+Vector((0,-mapping['depth_center_native_y_m'],
                                                  -mapping['source_floor_m']+(mapping['seated_top_m']-mapping['source_top_m'])*p['height_factor']))
    same_count=bool(b and len(a['points'])==len(b['points']))
    same_faces=bool(b and a['faces']==b['faces'])
    max_error=max((Vector(x)-(Vector(y)+shift)).length for x,y in zip(a['points'],b['points'])) if same_count else None
    checks.append({'mesh':p['name'],'supplier_mesh':p['source_name'],'lift_group':p['lift'],
                   'supplier_vertices':len(b['points']) if b else None,'actual_vertices':len(a['points']),
                   'face_indices_identical':same_faces,'max_world_point_deviation_m':max_error,
                   'pass':same_count and same_faces and max_error<2e-6})
out={'source_file':str(SOURCE),'source_sha256':file_hash(SOURCE),'supplier_file':str(CAD),'supplier_sha256':file_hash(CAD),
     'layout_sha256':file_hash(ROOT/'model/layout.json'),
     'method':'Independent Blender importer reads original supplier GLB after caching current evaluated meshes. Vertex order/topology and expected world-space translation (axis conversion from importer, desktop depth centering, seated upper/middle adjustment) compared directly; no artifact saved.',
     'checks':checks,'all_supplier_components_unscaled_and_correctly_positioned':all(c['pass'] for c in checks),
     'supplier_top_width_depth_m':[1.2000001668930054,.685000091791153],
     'published_top_width_depth_m':[1.19888,.6858],
     'catalog_CAD_rounding_disclosed':True,
     'limits':['Two-micrometre comparison tolerance is export/import numerical precision, not site or vendor manufacturing accuracy.',
               'CAD geometry is supplier Woodgrain/White example; BlackOak/Charcoal finish is a selected material substitution. Product dimensions rounded differently by catalogue and CAD are disclosed.']}
(QA/'tria-supplier-parity.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'parts':len(checks),'all_pass':out['all_supplier_components_unscaled_and_correctly_positioned'],
                  'max_deviation_m':max(c['max_world_point_deviation_m'] or 0 for c in checks),'failures':[c for c in checks if not c['pass']]}))
