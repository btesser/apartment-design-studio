import bpy
bpy.ops.wm.open_mainfile(filepath='/workspace/his-office-redesign/model/his-office-design.blend')
s=bpy.context.scene
print('VIEW',s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure)
print('DENOISERS',[(e.identifier,e.name)for e in s.cycles.bl_rna.properties['denoiser'].enum_items])
print('WORLD',[(n.name,n.type,[(i.name,str(i.default_value))for i in n.inputs if hasattr(i,'default_value')])for n in s.world.node_tree.nodes])
print('LIGHTS',[(o.name,o.data.energy,list(o.data.color),o.data.size)for o in bpy.data.objects if o.type=='LIGHT'])
