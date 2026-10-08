"""Read-only texture availability and linkage check, not a render comparison."""
import bpy
import hashlib
import json
from pathlib import Path

import sys
variant_args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
ROOT=Path(variant_args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
QA.mkdir(parents=True,exist_ok=True)

source=ROOT/'model/his-office-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
used={m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m}
records=[];shaders=[]
for m in used:
    if not m.use_nodes:continue
    bsdf=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bsdf:
        def socket(name):
            s=bsdf.inputs.get(name)
            if s is None:return None
            value=s.default_value
            return {'value':list(value) if hasattr(value,'__len__') else value,'linked':s.is_linked}
        shaders.append({'name':m.name,'base_color':socket('Base Color'),'roughness':socket('Roughness'),
                        'metallic':socket('Metallic'),'emission_color':socket('Emission Color'),'emission_strength':socket('Emission Strength'),
                        'procedural_nodes':[n.type for n in m.node_tree.nodes if n.type in ['TEX_NOISE','TEX_WAVE','BUMP','TEX_VORONOI']]})
    for n in m.node_tree.nodes:
        if n.type!='TEX_IMAGE':continue
        im=n.image
        links=[{'to_node':l.to_node.name,'to_socket':l.to_socket.name,'from_socket':l.from_socket.name} for l in m.node_tree.links if l.from_node==n]
        r={'material':m.name,'node':n.name,'image':im.name if im else None,'pixels':list(im.size) if im else None,
           'has_data':bool(im and im.has_data),'packed_bytes':len(im.packed_file.data) if im and im.packed_file else 0,
           'file_exists':bool(im and Path(bpy.path.abspath(im.filepath)).is_file()),'links':links,
           'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest() if im and im.packed_file else None}
        r['image_available']=bool(im and im.has_data and min(im.size)>0 and (r['packed_bytes']>0 or r['file_exists']))
        records.append(r)
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'method':'Read-only Blender image-node references in materials used by scene meshes; verifies pixel buffers and a packed or existing backing file, records shader links.',
     'all_used_image_nodes_available':all(r['image_available'] for r in records),'used_image_node_count':len(records),'records':records,
     'principled_material_constants':shaders,
     'native_mesh_material_names':{o.name:[o.data.materials[i].name for i in sorted({p.material_index for p in o.data.polygons}) if i<len(o.data.materials) and o.data.materials[i]] for o in bpy.context.scene.objects if o.type=='MESH'},
     'limits':['Availability/linkage is not a proof of GLB/Cycles identical shading. Final visual renders reviewed separately.']}
p=QA/'material-availability.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'all_available':out['all_used_image_nodes_available'],'image_nodes':len(records),'missing':[r for r in records if not r['image_available']]}))
