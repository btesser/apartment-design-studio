import bpy
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
m=bpy.data.materials.get('Material_0')
for n in m.node_tree.nodes:print(n.name,n.type)
for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'=>',l.to_node.name,l.to_socket.name)
