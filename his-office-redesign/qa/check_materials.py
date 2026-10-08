"""Read-only texture availability and linkage check, not a render comparison."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT=Path('/workspace/his-office-redesign')
source=ROOT/'model/his-office-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
used={m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m}
records=[]
for m in used:
    if not m.use_nodes:continue
    for n in m.node_tree.nodes:
        if n.type!='TEX_IMAGE':continue
        im=n.image
        links=[{'to_node':l.to_node.name,'to_socket':l.to_socket.name,'from_socket':l.from_socket.name} for l in m.node_tree.links if l.from_node==n]
        r={'material':m.name,'node':n.name,'image':im.name if im else None,'pixels':list(im.size) if im else None,
           'has_data':bool(im and im.has_data),'packed_bytes':len(im.packed_file.data) if im and im.packed_file else 0,
           'file_exists':bool(im and Path(bpy.path.abspath(im.filepath)).is_file()),'links':links}
        r['image_available']=bool(im and im.has_data and min(im.size)>0 and (r['packed_bytes']>0 or r['file_exists']))
        records.append(r)
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'method':'Read-only Blender image-node references in materials used by scene meshes; verifies pixel buffers and a packed or existing backing file, records shader links.',
     'all_used_image_nodes_available':all(r['image_available'] for r in records),'used_image_node_count':len(records),'records':records,
     'limits':['Availability/linkage is not a proof of GLB/Cycles identical shading. Final visual renders reviewed separately.']}
p=ROOT/'qa/material-availability.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'all_available':out['all_used_image_nodes_available'],'image_nodes':len(records),'missing':[r for r in records if not r['image_available']]}))
