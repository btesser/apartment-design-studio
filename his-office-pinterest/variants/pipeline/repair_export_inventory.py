"""Export complete product descendants from frozen native scenes; never save BLEND."""
import bpy, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene_tools as guard

base=Path('/workspace/his-office-pinterest/variants')
for variant in ['b-charcoal-slat','c-ink-studio']:
    root=base/variant/'model'
    native=root/'his-office-design.blend'
    before=guard.file_hash(native)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    furniture={o for o in bpy.data.objects if o.type in ['MESH','EMPTY'] and o.get('role')=='furniture'}
    for obj in list(furniture):
        furniture.update(guard.descendants(obj))
    for obj in list(furniture):
        parent=obj.parent
        while parent:
            furniture.add(parent)
            parent=parent.parent
    chair=[o for o in furniture if o.type=='MESH' and o.name.startswith('aeron-primary ::')]
    if len(chair)!=40:
        raise RuntimeError(f'Expected40 Aeron meshes, found {len(chair)}')
    for obj in chair:
        obj['role']='furniture'
    structure={o for n in guard.STRUCTURE_COLLECTIONS for o in bpy.data.collections[n].all_objects}
    structure.update(bpy.data.collections['08 Chosen workwall finish'].all_objects)
    exports=[]
    for name,objects in [('his-office-furniture.glb',furniture),('his-office-design.glb',structure|furniture)]:
        path=root/name
        guard.export_selected(path,objects)
        exports.append({'filename':name,'sha256':guard.file_hash(path),'bytes':path.stat().st_size})
    if guard.file_hash(native)!=before:
        raise RuntimeError('Frozen native scene changed during export-only repair')
    report={'method':'Export-only furniture assembly descendant inclusion; native scene not saved or mutated on disk.',
            'native_sha256_before':before,'native_sha256_after':guard.file_hash(native),
            'native_frozen_unchanged':True,'aeron_mesh_count_exported':len(chair),
            'furniture_mesh_count':sum(o.type=='MESH' for o in furniture),'exports':exports}
    (root/'export-inventory-repair.json').write_text(json.dumps(report,indent=2))
    manifest_path=root/'model-manifest.json'
    manifest=json.loads(manifest_path.read_text())
    replacement={i['filename']:i for i in exports}
    manifest['exports']=[replacement.get(i['filename'],i) for i in manifest['exports']]
    manifest['export_inventory_repair']=report
    manifest_path.write_text(json.dumps(manifest,indent=2))
    print('EXPORT_INVENTORY_REPAIRED',variant,json.dumps(exports),flush=True)
