"""Read-only inventory of the frozen source. Writes JSON only, never a .blend."""
import bpy
import hashlib
import json
from pathlib import Path

OUT = Path('/workspace/his-office-pinterest/model')
SOURCE = Path('/workspace/his-office-redesign/model/his-office-design.blend')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
roots = ['kept-uplift-desk', 'kept-honeywell-02e-pro', 'kept-muttros-cat-tree']
info = {
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'collections': [{'name': c.name, 'direct': len(c.objects), 'all': len(c.all_objects), 'hide_render': c.hide_render, 'hide_viewport': c.hide_viewport} for c in bpy.data.collections],
    'roots': {}
}
for name in roots:
    root = bpy.data.objects.get(name)
    objects = [root, *root.children_recursive] if root else []
    info['roots'][name] = {'found': bool(root), 'properties': dict(root.items()) if root else {}, 'children': [{'name': o.name, 'type': o.type, 'materials': [slot.material.name if slot.material else None for slot in o.material_slots]} for o in objects]}
(OUT / 'guard-source-inventory.json').write_text(json.dumps(info, indent=2, default=str))
print(json.dumps({'sha256': info['source_sha256'], 'collections': info['collections'], 'roots': {name: {'found': r['found'], 'parts': len(r['children']), 'materials': sorted({m for o in r['children'] for m in o['materials'] if m})} for name, r in info['roots'].items()}}, indent=2))
