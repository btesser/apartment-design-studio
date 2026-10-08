"""Blender read-only wall-wrap audit. No scene or material writes."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

OUT=Path('/workspace/his-office-pinterest/variants/pipeline')
SOURCE=Path('/workspace/his-office-redesign/model/his-office-design.blend')
EXPECTED='607e11d67b8fc8813da0872b5f18278733c6a40cd9e1988c3b1cb743971ada0a'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert source_hash==EXPECTED
work=['his-office wall4 segment']
window=['his-office wall5 corrected solid 0','his-office wall5 corrected solid 2',
        'his-office wall5 corrected solid 4','his-office wall5 corrected bottom 1',
        'his-office wall5 corrected bottom 3','his-office wall5 corrected head 1',
        'his-office wall5 corrected head 3']
names=work+window
records=[]
for name in names:
    o=bpy.data.objects.get(name)
    assert o is not None and o.type=='MESH',name
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    mats=[m.name for m in o.data.materials if m]
    assert mats==['Reconstructed warm plaster'],(name,mats)
    records.append({'name':name,'type':o.type,'collection_names':[c.name for c in o.users_collection],
        'role':'workwall' if name in work else 'windowwall plaster around existing openings',
        'world_bounds_xyz_m':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
        'material_names':mats,'mesh_datablock':o.data.name,'mesh_datablock_users':o.data.users,
        'other_objects_sharing_mesh':[q.name for q in bpy.data.objects if q!=o and q.type=='MESH' and q.data==o.data]})
shared={}
for matname in set(m for r in records for m in r['material_names']):
    users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material and s.material.name==matname for s in o.material_slots)]
    shared[matname]={'all_object_users':sorted(users),'paint_whitelist_users':sorted(n for n in users if n in names),
                     'must_remain_unchanged_users':sorted(n for n in users if n not in names),
                     'trim_sharing':False,'required_action':'Assign a new variant-private paint material to exact whitelisted wall objects; never mutate this original shared material.'}
protected=[]
for cname in ['01 Measured room shell','02 Existing fixed feature proxies','02b Existing door leaves — closed observed state']:
    c=bpy.data.collections.get(cname)
    for o in c.all_objects:
        if o.name not in names:
            protected.append({'name':o.name,'collection':cname,
                              'materials':[s.material.name for s in o.material_slots if s.material]})
report={'schema_version':1,'read_only_audit':True,'scene_mutations':False,
    'source':str(SOURCE),'source_sha256':source_hash,
    'execution_status':'Builder execution held pending root GO',
    'paint_targets':{'B':{'paint':'Peppercorn SW7674','screen_sRGB':[88,88,88]},
                     'C':{'paint':'Naval SW6244','screen_sRGB':[47,61,76]}},
    'exact_workwall_object_names':work,'exact_windowwall_object_names':window,
    'exact_combined_whitelist':names,'object_records':records,'source_material_sharing':shared,
    'preserve_objects':sorted(protected,key=lambda r:r['name']),
    'preserve_material_names':sorted(set(m for r in protected for m in r['materials'])),
    'implementation_rules':[
        'Use exact object-name whitelist, not collection-wide or substring paint.',
        'Create fresh B/C private paint materials; do not recolor Reconstructed warm plaster in place.',
        'If a whitelisted mesh is shared with an excluded object, copy its mesh datablock before changing material slots.',
        'Preserve all source vertex coordinates, transforms, openings and wall thickness.',
        'Preserve Fixture porcelain white trim, pipe and leaves; Window glass; all brick, wood floor and ceiling materials.',
        'Dark wrap is source workwall plus all corrected windowwall plaster pieces, including plaster over/under opening boundaries; no new wall or opening geometry.',
        'Do not pack or reload any already packed source images.'],
    'source_sha256_after_audit':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
report['source_unchanged']=report['source_sha256_after_audit']==source_hash
(OUT/'wall-wrap-whitelist.json').write_text(json.dumps(report,indent=2)+'\n')
summary='READ-ONLY WALL WRAP WHITELIST\nSource SHA256 '+source_hash+'\n\nPAINT EXACTLY:\n'+'\n'.join(names)
summary+='\n\nAssign fresh variant-private Peppercorn/Naval materials. Reconstructed warm plaster has17 users:8 whitelist and9 excluded white architectural wall pieces. Do not recolor it globally. Trim/door/pipe use Fixture porcelain, separate from wall plaster; preserve. Preserve glass,brick,floor,ceiling,all fixed features/doors. No geometry changes. Already packed images must not be repacked.\n'
summary+='Mesh sharing: '+str({r['name']:r['other_objects_sharing_mesh'] for r in records})+'\nSource unchanged: '+str(report['source_unchanged'])+'\n'
(OUT/'wall-wrap-whitelist.txt').write_text(summary)
print('WALL_WRAP_AUDIT_OK',len(records),'targets; source unchanged',report['source_unchanged'])
