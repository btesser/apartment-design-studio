import sys,math,json,os
sys.path.insert(0,'/workspace/apartment-furniture')
source=open('/workspace/apartment-furniture/build_furniture.py').read().split('layout=json.load')[0]
exec(compile(source,'furniture_helpers','exec'),globals())
ROOT='/workspace/design-fidelity';COL.name='Entry design — provisional placement'
mat('Entry glass',(.58,.67,.68),.16,.12)
glass=MAT['Entry glass'];glass.diffuse_color=(.58,.67,.68,.42);bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.58,.67,.68,.42)
if hasattr(glass,'surface_render_method'):glass.surface_render_method='DITHERED'
mat('Entry rug red',(.37,.075,.047),1);mat('Entry rug sage',(.30,.32,.24),1);mat('Entry rug charcoal',(.035,.034,.028),1);mat('Entry rug pale',(.65,.64,.55),1)
items=[{'id':'entry-gold-console','kind':'console','position':[1.365,.80,1.575],'rotation_deg':-90,'dimensions':[.5588,.2032,.7493],'shopping_row':4,'source':'Wayfair W009247541; gold console22W×8D×29.5H inches','dimension_confidence':'Selected product dimensions verified; modeled shape approximate','placement_confidence':'Provisional: source plan does not assign entry furnishing positions'}, {'id':'entry-faceted-mirror','kind':'mirror','position':[1.255,.80,2.485],'rotation_deg':-90,'dimensions':[.4064,.035,.6096],'shopping_row':5,'source':'Shopping list24H×16W inches; source board faceted beveled mirror','dimension_confidence':'Width/height sourced; thickness approximate','placement_confidence':'Provisional above console'}, {'id':'entry-rattan-shoe-cabinet','kind':'cabinet','position':[3.48,.95,1.575],'rotation_deg':90,'dimensions':[.679958,.399796,.834898],'shopping_row':11,'source':'Wayfair W100191469; natural wood26.77W×15.74D×32.87H inches','dimension_confidence':'Selected product dimensions verified; modeled shape approximate','placement_confidence':'Provisional: solid side wall placement'}, {'id':'entry-patchwork-rug','kind':'rug','position':[2.55,1.0,1.578],'rotation_deg':0,'dimensions':[.6096,.9144,.009],'shopping_row':12,'source':'Shopping list Ruggable Patchwork Boho red2×3ft flatwoven','dimension_confidence':'Selected source size exact; pattern conceptual','placement_confidence':'Provisional clear entry floor'}]
# Ground all entry objects to the measured living/entry plane Z1.535.
for it in items:
 it['position'][2]=round(it['position'][2]-.04,6)
for it in items:
 PARENT=bpy.data.objects.new(it['id'],None);COL.objects.link(PARENT);PARENT['provisional_placement']=True;PARENT['source']=it['source'];PARENT['shopping_row']=it['shopping_row'];w,d,h=it['dimensions'];kind=it['kind']
 if kind=='console':
  for x in [-w/2+.008,w/2-.008]:
   for y in [-d/2+.008,d/2-.008]:cube('slender brass upright',(x,y,h/2),(.015,.015,h),'Gold brushed metal',.003)
  for y in [-d/2+.008,d/2-.008]:cube('brass top rail',(0,y,h-.008),(w,.015,.015),'Gold brushed metal',.003)
  for x in [-w/2+.008,w/2-.008]:cube('brass side rail',(x,0,h-.008),(.015,d,.015),'Gold brushed metal',.003)
  cube('glass top',(0,0,h-.012),(w-.018,d-.018,.008),'Entry glass',.002)
  for x,z in [(-w*.23,h*.59),(w*.23,h*.29)]:
   cube('asymmetric glass shelf',(x,0,z),(w*.50-.01,d-.018,.008),'Entry glass',.001)
   for y in [-d/2+.008,d/2-.008]:cube('brass shelf rail',(x,y,z-.007),(w*.5,.014,.014),'Gold brushed metal',.003)
 elif kind=='mirror':
  pts=[(-w*.30,0),(w*.30,0),(w/2,h*.16),(w/2,h*.84),(w*.30,h),(-w*.30,h),(-w/2,h*.84),(-w/2,h*.16)]
  me=bpy.data.meshes.new('Faceted glass mirror');me.from_pydata([(x,.008,z) for x,z in pts],[],[tuple(range(8))]);me.update();o=bpy.data.objects.new('faceted mirror panel',me);bpy.context.collection.objects.link(o);own(o,'faceted mirror panel','Mirror approximation')
  for i,(x,z) in enumerate(pts):
   xx,zz=pts[(i+1)%8];rod('beveled glass perimeter',(x,.006,z),(xx,.006,zz),.006,'Mirror approximation')
 elif kind=='cabinet':
  leg=.11;cube('natural oak carcass',(0,0,(h+leg)/2),(w,d,h-leg),'Natural oak',.015)
  for x in [-w*.37,w*.37]:
   for y in [-d*.32,d*.32]:cyl('tapered cabinet leg',(x,y,leg/2),.023,leg,'Natural oak')
  for c in [-w*.248,w*.248]:
   cube('oak door',(c,d/2+.006,(h+leg)/2),(w*.486,.018,h-leg-.019),'Natural oak',.01)
   ww=w*.34;hh=(h-leg)*.77;zc=(h+leg)/2;r=ww/2;straight=hh-2*r
   # Vertical capsule cane insert: curved ends and close slatted weave.
   verts=[]
   for i in range(24):
    a=math.pi*i/23;verts.append((c+r*math.cos(a),d/2+.019,zc+straight/2+r*math.sin(a)))
   for i in range(24):
    a=math.pi+math.pi*i/23;verts.append((c+r*math.cos(a),d/2+.019,zc-straight/2+r*math.sin(a)))
   me=bpy.data.meshes.new('cane door capsule');me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.update();o=bpy.data.objects.new('woven cane oval',me);bpy.context.collection.objects.link(o);own(o,'woven cane oval','Cane rattan')
   for i in range(21):
    xx=-r+.007+i*(2*r-.014)/20;ext=math.sqrt(max(0,r*r-xx*xx));rod('cane vertical strand',(c+xx,d/2+.021,zc-straight/2-ext+.007),(c+xx,d/2+.021,zc+straight/2+ext-.007),.0016,'Oat linen')
   for i in range(21):
    zz=-hh/2+.013+i*(hh-.026)/20;off=max(0,abs(zz)-straight/2);rr=math.sqrt(max(0,r*r-off*off));rod('cane horizontal strand',(c-rr+.004,d/2+.023,zc+zz),(c+rr-.004,d/2+.023,zc+zz),.0012,'Natural oak')
  for x in [-.021,.021]:cube('oak door handle',(x,d/2+.043,h*.62),(.018,.035,.102),'Natural oak',.004)
 elif kind=='rug':
  cube('flatwoven rug',(0,0,.0045),(w,d,.009),'Entry rug pale')
  for x,y,ww,dd,ma in [(-.18,.26,.15,.20,'Entry rug charcoal'),(.15,.29,.22,.26,'Entry rug red'),(-.16,-.23,.22,.23,'Entry rug red'),(.14,-.29,.23,.16,'Entry rug charcoal'),(-.19,.03,.13,.12,'Entry rug sage'),(.18,-.02,.18,.13,'Entry rug sage')]:
   cube('patchwork motif',(x,y,.010),(ww,dd,.002),ma)
  for x in [-w/2+.012,w/2-.012]:cube('rug stitched edge',(x,0,.010),(.008,d,.002),'Entry rug charcoal')
 PARENT.location=it['position'];PARENT.rotation_euler.z=math.radians(it['rotation_deg'])
 x,y,z=it['position'];a=math.radians(it['rotation_deg'])
 it['footprint_blender_xy']=[[round(x+math.cos(a)*u-math.sin(a)*v,6),round(y+math.sin(a)*u+math.cos(a)*v,6)] for u,v in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
 it['viewer_position']=[x,z,-y];it['facing_blender_xy']=[round(-math.sin(a),6),round(math.cos(a),6)]
bpy.context.view_layer.update()
checks={'console_min_x_m':min(p[0] for p in items[0]['footprint_blender_xy']),'cabinet_max_x_m':max(p[0] for p in items[2]['footprint_blender_xy']),'cabinet_to_stair_void_y_clearance_m':round(1.83-max(p[1] for p in items[2]['footprint_blender_xy']),6),'console_to_cabinet_walk_width_m':round(min(p[0] for p in items[2]['footprint_blender_xy'])-max(p[0] for p in items[0]['footprint_blender_xy']),6),'doorway_y_m':1.84,'doorway_x_interval_m':[1.7,2.78]}
assert checks['console_min_x_m']>1.25
assert checks['cabinet_max_x_m']<3.68
assert checks['cabinet_to_stair_void_y_clearance_m']>.5
assert checks['console_to_cabinet_walk_width_m']>1.8
manifest={'coordinate_frame':'Meters; original Blender Z-up. GLB Y-up maps(x,y,z)→(x,z,-y), no rescale.','status':'Provisional design staging. Source plan omits exact entry furniture locations.','floor_grounding':{'measured_entry_floor_z_m':1.535,'source':'plate-geometry.json living architecture_floor','uniform_z_correction_m':-.04,'rug_surface_offset_m':.003},'items':items,'clearance_checks':checks,'limitations':['Actual entry doorway and stair-opening shell must remain visible; no wall geometry modified.','Entry paint and wallpaper are alternatives, not final selections. No wallpaper or painted wall is inserted.','Dimensions from selected product titles/specs; shapes and rug motif are simplified concept approximations.'],'paint_options_reference':['Benjamin Moore Conch Shell052','Benjamin Moore Hidden SapphireCSP-690']}
json.dump(manifest,open(ROOT+'/entry-manifest.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/entry-design.blend')
bpy.ops.export_scene.gltf(filepath=ROOT+'/entry-design.glb',export_format='GLB',export_extras=True,export_apply=True)
print('ENTRY_MODEL_READY',len(COL.objects),checks)
