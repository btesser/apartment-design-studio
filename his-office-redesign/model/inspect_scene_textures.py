import bpy,json
from pathlib import Path
ROOT=Path('/workspace/his-office-redesign/model')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'his-office-design.blend'))
used={m for o in bpy.data.objects if o.type=='MESH' for m in o.data.materials if m}
r=[]
for m in used:
    if not m.use_nodes:continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE':
            im=n.image
            r.append({'material':m.name,'node':n.name,'image':im.name if im else None,'size':list(im.size) if im else None,
                      'filepath':im.filepath if im else None,'packed_bytes':len(im.packed_file.data) if im and im.packed_file else None,
                      'links':[(l.from_node.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links if l.from_node==n]})
(ROOT/'texture-diagnostic.json').write_text(json.dumps(r,indent=2))
for x in r:print(json.dumps(x))
