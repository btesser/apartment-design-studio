"""Independent read-only evaluated room/keeper parity against the frozen source."""
import bpy
import hashlib
import json
from pathlib import Path

import sys
variant_args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
ROOT=Path(variant_args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
QA.mkdir(parents=True,exist_ok=True)
BASE=ROOT
OLD = Path('/workspace/his-office-redesign/model/his-office-design.blend')
NEW = BASE/'model/his-office-design.blend'
OLD_HASH = '607e11d67b8fc8813da0872b5f18278733c6a40cd9e1988c3b1cb743971ada0a'
FIXED = {'architecture', 'fixed_fixture', 'door_leaf'}
ROOTS = {'kept-honeywell-02e-pro', 'kept-muttros-cat-tree'}


def file_hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def keeper_owner(obj):
    while obj:
        if obj.name in ROOTS:
            return obj.name
        obj = obj.parent
    return None


def material_signature(m):
    if not m:
        return None
    data = {'nodes': [], 'links': []}
    if m.use_nodes:
        for n in m.node_tree.nodes:
            item = {'name': n.name, 'type': n.type, 'inputs': []}
            for socket in n.inputs:
                if not hasattr(socket, 'default_value'):
                    continue
                v = socket.default_value
                if isinstance(v, (float, int, str, bool)):
                    item['inputs'].append([socket.identifier, v])
                elif hasattr(v, '__len__'):
                    item['inputs'].append([socket.identifier, list(v)])
            if n.type == 'TEX_IMAGE' and n.image:
                im = n.image
                item['image'] = {'size': list(im.size), 'colorspace': im.colorspace_settings.name,
                                 'packed_sha256': hashlib.sha256(im.packed_file.data).hexdigest()
                                 if im.packed_file else None}
            data['nodes'].append(item)
        data['links'] = sorted([l.from_node.name, l.from_socket.identifier,
                                l.to_node.name, l.to_socket.identifier]
                               for l in m.node_tree.links)
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def snapshot(p):
    bpy.ops.wm.open_mainfile(filepath=str(p))
    deps = bpy.context.evaluated_depsgraph_get()
    records = {}
    for obj in bpy.context.scene.objects:
        owner = keeper_owner(obj)
        if obj.type != 'MESH' or not (obj.get('role') in FIXED or owner):
            continue
        ev = obj.evaluated_get(deps)
        mesh = ev.to_mesh()
        pts = [[round(v, 7) for v in ev.matrix_world@vert.co] for vert in mesh.vertices]
        # Evaluated component geometry includes modifiers; world positions also
        # detect any moved/scaled room or protected product in this revision.
        geom = {'world_vertices_m': pts, 'faces': [list(f.vertices) for f in mesh.polygons],
                'uv_layers': [{'name': uv.name, 'uv': [[round(v, 7) for v in data.uv] for data in uv.data]} for uv in mesh.uv_layers]}
        records[obj.name] = {
            'role': obj.get('role'), 'keeper': owner,
            'evaluated_world_geometry_sha256': hashlib.sha256(json.dumps(geom).encode()).hexdigest(),
            'vertices': len(pts), 'faces': len(mesh.polygons),
            'bounds_m': [[min(v[k] for v in pts) for k in range(3)],
                         [max(v[k] for v in pts) for k in range(3)]],
            'material_signatures': [material_signature(m) for m in obj.data.materials]
        }
        ev.to_mesh_clear()
    return records


assert file_hash(OLD) == OLD_HASH, 'Prior frozen source changed'
old = snapshot(OLD)
new = snapshot(NEW)
checks = []
for name, before in old.items():
    after = new.get(name)
    checks.append({'mesh': name, 'keeper': before['keeper'], 'role': before['role'],
                   'exists': after is not None,
                   'geometry_identical_at_1e_7_m': bool(after and before['evaluated_world_geometry_sha256'] == after['evaluated_world_geometry_sha256']),
                   'materials_identical': bool(after and before['material_signatures'] == after['material_signatures']),
                   'keeper_materials_identical': before['material_signatures'] == after['material_signatures']
                   if after and before['keeper'] else None,
                   'prior_geometry_sha256': before['evaluated_world_geometry_sha256'],
                   'current_geometry_sha256': after['evaluated_world_geometry_sha256'] if after else None})
out = {'source': str(OLD), 'source_sha256': OLD_HASH, 'current': str(NEW),
       'current_sha256': file_hash(NEW),
       'method': 'Independent evaluated world vertices (rounded to 0.1 micrometre) and face-index topology, including applied modifiers; keeper shader inputs, links and packed-image bytes compared separately. No scene saved.',
       'scope': 'Unchanged measured architecture/fixed fixtures/closed observed leaves and the two retained owned lamp/cat products. Prior calibrated dimensions, fireplace/lamp topology and product-envelope proofs remain applicable only when parity passes.',
       'checks': checks,
       'unexpected_new_protected_meshes': sorted(n for n in set(new)-set(old) if not (ROOT.name=='b-charcoal-slat' and n.startswith('WoodUpp panel'))),
       'all_original_geometry_unchanged': all(c['geometry_identical_at_1e_7_m'] for c in checks),
       'authorized_panel_additions': sorted(n for n in set(new)-set(old) if ROOT.name=='b-charcoal-slat' and n.startswith('WoodUpp panel')),
       'all_geometry_unchanged': all(c['geometry_identical_at_1e_7_m'] for c in checks) and all(ROOT.name=='b-charcoal-slat' and n.startswith('WoodUpp panel') for n in set(new)-set(old)),
       'all_keeper_materials_unchanged': all(c['keeper_materials_identical'] for c in checks if c['keeper']),
       'all_fixed_materials_unchanged': all(c['materials_identical'] for c in checks if not c['keeper']),
       'fixed_material_changes': [c['mesh'] for c in checks if not c['keeper'] and not c['materials_identical']],
       'intentional_workwall_material_change_only': all(c['mesh']=='his-office wall4 segment' for c in checks if not c['keeper'] and not c['materials_identical']),
       'limits': ['Numerical equality establishes revision parity, not scan or product-proxy accuracy. Actual cat reach, lamp base detail and inferred door swings retain prior field-check limitations.']}
(QA/'protected-source-parity.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['current_sha256','all_geometry_unchanged','all_keeper_materials_unchanged','unexpected_new_protected_meshes']}))
