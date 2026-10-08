import json,math,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
out=Path('/workspace/his-office-redesign/geometry');out.mkdir(exist_ok=True,parents=True)
poly=[[-7.98,-2.79],[-3.08,-2.79],[-3.08,-1.35],[-3.78,-1.35],[-3.78,.31],[-7.98,.31]]
area=abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
F=[]
def feature(id,label,bounds,status,confidence,notes,**kw):
 f=dict(id=id,label=label,bounds_blender_xyz_m=bounds,evidence_status=status,confidence=confidence,notes=notes);f.update(kw);F.append(f)
feature('closet-door','Existing hanging closet door',[-3.90,-3.72,-.88,-.16,1.60,3.65],'observed scan frame and partly missing leaf','high placement; medium depth/leaf details','Nominal closet face X=-3.78 is generalized. Raw face/trim locally ranges X≈-3.90..-3.72. Actual leaf approxY[-.83,-.21],Z[1.61,3.64]. White plain panel, metal knob at -Y/right edge in face-on view; hinge at +Y edge is inferred from knob, not directly seen.',nominal_plane_x=-3.78,opening_yz=[-.83,-.21,1.61,3.64],observed_state='closed, scan leaf has large holes',hinge={'y':-.21,'status':'inferred from knob side'},swing='Toward room plausible, not directly observed. Reserve approach regardless.')
feature('upper-cupboard','Existing overhead cupboard',[-3.90,-3.84,-.83,-.21,3.70,4.56],'observed scan','high placement; medium trim details','White plain panel above closet; small metal latch at -Y edge. Plane sits about8–10cm forward of nominal wall face; do not omit it.',opening_yz=[-.83,-.21,3.70,4.56])
feature('living-entry','Door to living room',[-3.18,-2.97,-2.73,-1.65,1.60,3.65],'observed scan frame and partly missing leaf','high frame placement; medium plane/depth; low swing','White plain panel, silver lever at +Y side; substantial human occlusion. Frame width1.08m, actual clear opening likely~1.00m. Previously used0.80m was incomplete. Observed door appears closed. Separate open leaf in a viewer is an inferred viewing state.',nominal_plane_x=-3.08,frame_yz=[-2.73,-1.65,1.60,3.65],clear_width_approx_m=1.0,observed_state='closed, partly occluded',hinge={'y':-2.73,'status':'inferred from visible handle opposite side'})
feature('rear-exterior-door','Rear exterior door',[-8.15,-7.91,-2.55,-1.64,1.61,3.64],'observed scan plus listing door','high placement; medium depth/swing','White six-panel door with brass knob and deadbolt at +Y/right edge in rear face-on view. Frame width~.91m, clear leaf~.80m. Knob side implies hinge at -Y edge; swing not directly observed. Do not replace with solid black rectangle.',nominal_plane_x=-7.98,frame_yz=[-2.55,-1.64,1.61,3.64],clear_width_approx_m=.80,observed_state='closed',hinge={'y':-2.55,'status':'inferred from knob side'})
feature('rear-window','Single rear sash window',[-8.24,-7.93,-1.01,-.11,2.46,4.37],'observed calibrated raw ortho and scan vertices','high Y/Z position; medium recess depth','Outer vertical/header trim~.82m wide×1.84m high; clear glass~.72m wide. Sill board wider Y[-1.01,-.11]. White double-hung sash, upper roller blind, exterior bars. Sill~.95m above scan floor. Prior integrated proxy Y[-.98,.03],Z[2.38,4.23] was too wide and too low.',nominal_wall_x=-7.98,outer_trim_yz=[-.96,-.14,2.53,4.37],clear_glass_y=[-.92,-.20],sill_y=[-1.01,-.11],sill_and_apron_z=[2.46,2.56],sill_height_above_floor_m=.955,measured_tolerance_m=.04)
feature('rear-radiator','Existing small rear radiator',[-7.96,-7.43,-2.79,-2.47,1.61,2.30],'observed scan in two orthos plus local geometry','high location; medium envelope±.05–.08m','Dark cast-iron vertical fins in rear brick corner beside exterior door, not beneath window. Actual surface front modeY≈-2.60; envelope includes irregular fins/projection. Radiator function not tested.',nominal_envelope_m=[.53,.32,.69])
feature('rear-pipe','Existing vertical white pipe',[-8.00,-7.72,.14,.31,1.60,4.60],'observed scan','medium: warped mesh and ceiling merge','Vertical white pipe in rear white-wall corner; protrudes into room near X≈-7.91. Keep this feature instead of flattening corner.',approx_center_xy=[-7.91,.24],diameter_approx_m=.10)
feature('closed-fireplace','Existing infilled fireplace/chimney',[-6.10,-4.48,-2.85,-2.71,1.59,4.60],'observed textured brick, white infill and prior calibrated anchor','high center; medium broad envelope','Opening center X=-5.31; opening X[-5.65,-4.98]~.67m. White closed arched infill is recessed at median Y=-2.835. Full-height brick chimney face at median Y=-2.722, about .115m forward of adjacent brick Y=-2.837. Broad span~1.62m; edges taper/warp. Raw arch has brick voussoirs, without a big rectangular white mantel/trim. Closed appearance does not establish operability.',opening_center_x=-5.31,opening_bounds_approx=[-5.65,-4.98,-2.85,-2.82,1.62,2.48],chimney_face_y=-2.722,adjacent_brick_face_y=-2.837,infill_face_y=-2.835,old_proxy_trim_status='Old forward white trim Y=-2.63 is not observed and must not be treated as measured.',hearth_keepout_xy=[-6.10,-4.48,-2.94,-2.48],hearth_keepout_status='conservative architectural footprint including uncertain low lip, not an exact measured raised hearth polygon')
feature('front-shelf-nook','Existing built-in shelf nook near entry',[-3.95,-3.08,-2.90,-2.55,1.60,4.15],'observed raw angle4 and horizontal triangle peaks','medium topology; low individual shelf detail','White boards/brackets sit in brick-side front recess. Approx shelf surface modesZ2.33,2.61,2.80,3.05,3.24,3.60; holes/occlusion prevent reliable count. Do not turn scan fragments into arbitrary tall cabinet. Visible shelf fronts project to roughlyY-2.58.',approx_shelf_surface_z=[2.33,2.61,2.80,3.05,3.24,3.60])
feature('entry-controls','Thermostat and small control near entry',[-3.18,-2.97,-1.56,-1.35,2.7,3.29],'observed raw closet/entry ortho','medium placement','Two small wall controls plus switch near +Y jamb of living door; preserve as approximate visual details if modeled.')
room={
 'id':'his-office','authority':'Original Polycam measured geometry. No Amy furniture placements are used in this redesign.',
 'sources':{'original_glb':'/workspace/apartment/8_21_2026.glb','original_blender':'/workspace/apartment/scan.blend','raw_triangles':'/workspace/geometry-audit/upstairs_surface.npz','listing':'/workspace/source-evidence/listing-floorplan.jpg','prior_integrated_model':'/workspace/apartment-model/integrated.blend'},
 'coordinate_system':{'unit':'metres','blender_axes':'X toward street/front, -X rear/backyard; +Y white wall/kitchen side, -Y exposed brick; +Z up','to_gltf':'[X,Y,Z]_Blender -> [X,Z,-Y]_glTF','north':'Listing north arrow corresponds -X after registration; not surveyed.'},
 'outline_blender_xy_m':poly,'outline_gltf_xz_m':[[x,-y]for x,y in poly],
 'outline_confidence':'Generalized floor/inside-wall outline, typical5–12cm uncertainty. Mesh walls are warped/slightly off-axis. Do not stretch to listing.',
 'area_m2':round(area,3),'overall_bounds_blender_xyz_m':[-7.98,-3.08,-2.79,.31,1.575,4.595],
 'overall_dimensions_xy_m':[4.90,3.10],'main_rectangle_dimensions_xy_m':[4.20,3.10],
 'closet_carveout_bounds_xy_m':[-3.78,-3.08,-1.35,.31],
 'closet_note':'Hanging closet interior not recorded. Existing door and overhead cupboard observed. .70×1.66m carveout describes generalized external architectural mass, not validated closet interior capacity.',
 'floor':{'nominal_z_m':1.575,'plane':'z=.008859*x-.004139*y+1.617083','fit_rms_m':.008,'observed_support_area_m2':10.453},
 'ceiling':{'nominal_z_m':4.595,'plane':'z=.004656*x-.014263*y+4.602549','fit_rms_m':.0075,'observed_support_area_m2':10.669,'nominal_room_height_m':3.020,'note':'Local height varies several cm; planes summarize scan, not surveyed leveling.'},
 'listing_dimensions_m':{'x':4.7244,'y':2.9972,'printed_label':'rear bedroom9ft10in×15ft6in','comparison':'scan overall about3.7% longerX and3.4% widerY; listing says approximate.'},
 'features':F,
 'scope':'Feature positions/architecture only. Furniture zones are feasibility guidance, not final layout authority or measured installation clearance.'}
json.dump(room,open(out/'room-measurements.json','w'),indent=2)
json.dump({'coordinate_system':room['coordinate_system'],'features':F},open(out/'fixed-features.json','w'),indent=2)
zones=[
 dict(id='closet-approach',bounds_xy_m=[-4.80,-3.87,-.98,-.06],type='preserve access',basis='Planning rectangle in front of observed .62m closet door and forward trim at X~-3.87. Includes .93m depth; hinge/swing not directly verified.'),
 dict(id='living-entry-approach',bounds_xy_m=[-4.08,-3.08,-2.79,-1.55],type='preserve access',basis='Planning rectangle1.00m inward depth from observed1.08m frame. Allows approach without furniture pinching door.'),
 dict(id='rear-door-approach',bounds_xy_m=[-7.98,-6.98,-2.66,-1.52],type='preserve access',basis='Planning rectangle1m inward from exterior door; door swing not observed.'),
 dict(id='rear-radiator-envelope',bounds_xy_m=[-7.96,-7.43,-2.79,-2.47],type='observed fixed object',basis='Measured approximate radiator footprint, not hypothetical regulatory buffer.'),
 dict(id='fireplace-projection',bounds_xy_m=[-6.10,-4.48,-2.94,-2.48],type='preserve architecture',basis='Conservative projected chimney/hearth bounds; operability unknown.'),
 dict(id='window-access',bounds_xy_m=[-7.98,-7.32,-1.08,-.05],type='operating access preference',basis='Optional reachable strip for sash/blind. Cat tree may overlap this strip if reachable around; not a door path.'),
 dict(id='rear-pipe',bounds_xy_m=[-8,-7.72,.14,.31],type='observed fixed object',basis='Measured approximate protrusion; keep desk end away.'),
 dict(id='white-wall-worktop-run',bounds_xy_m=[-7.70,-4.85,-.452,.31],type='feasible work/storage zone',basis='2.85m run clear of pipe and forward closet trim. Existing UPLIFT 1.0668×.762m plus 1.40m secondary worktop total 2.4668m, leaving .3832m for separation/end margins. Chair use extends into room.'),
 dict(id='rear-brick-clothes-storage',bounds_xy_m=[-7.25,-6.35,-2.79,-2.27],type='feasible folded-clothes zone',basis='Can fit~.80m width×.47m depth drawers. Clear of observed radiator and broad chimney; user says hanging clothes remain in existing closet.'),
 dict(id='visitor-chair-adjusted',bounds_xy_m=[-4.92,-4.14,-2.29,-1.51],type='feasible compact visitor-chair zone',basis='Example .78×.78 footprint centered(-4.53,-1.90), forward of hearth and .06m left of entry approach. Requires final actual product/collision check.'),
 dict(id='cat-tree-near-window',bounds_xy_m=[-7.93,-6.97,-1.43,-.47],type='provisional retained-tree zone',basis='Conservative .96×.96 example centered(-7.45,-.95). Actual product branching envelope must be checked; do not infer physical footprint from category/photo.'),
]
layout_notes=[
 'Main desk now confirmed by order screenshot:42×30in=1.0668×.762m, UPLIFTV2C, Pheasantwood barkline front/square back. Zone fit uses exact known footprint; frame/monitor arrangement separate.',
 'Feasible primary center X=-6.95 gives X[-7.4834,-6.4166], against white wall Y=.31 -> Y[-.452,.31]. Rear window/cat tree remain near its left end; rear pipe envelope ends X=-7.72.',
 'Secondary width 1.40m centered X=-5.20 gives X[-5.90,-4.50] and overlaps the updated closet approach by .30m if its depth enters Y<-.06. Feasible center X=-5.55 gives X[-6.25,-4.85], .05m before the planning buffer. With primary center X=-6.95, desk-to-desk gap is .1666m.',
 'Proposed dresser center(-6.80,-2.50), .80×.47m fits rearbrick zone; its rear edge-2.735m clears generalizedbrickwall-2.79m by.055m. Practical againstwallcenterY=-2.555 givesrear-2.79.',
 'Original visitor chair center(-4.20,-2.05), .78×.78m would overlap entryapproach0.27m along X; shiftto(-4.53,-1.90) or choose narrower chair.',
 'Catcenter(-7.45,-1.10) with1mYbranching envelope reaches-1.60 and intersectsreardoorapproachY≤-1.52; centerY-.95 leaves~.07m under .96m footprint assumption. ActualretainedMUTTROS productdimensionsrequired forfinalfit.',
 'Chair use zones for both desks will occupyYroughly[-1.45,-.45]. This leavescentral circulation behindchairs towardbrickside but mustbe checkedwithactual chairarm/swivel envelope. Theseare planningenvelopes, notasserted measuredclearances.'
]
json.dump({'coordinate_system':'Blender Z-up metres; rectangles[xmin,xmax,ymin,ymax]','zones':zones,'feasibility_notes':layout_notes,'status':'Room-only feasibility; root owns final furniture layout.'},open(out/'access-and-feasible-zones.json','w'),indent=2)
# annotated source images, retain original renders unchanged
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
anns={
 'rear-door-window':[((212,483,598,1411),'Exterior door','.91m frame | Z1.61–3.64m','#ffd166'),((932,145,1303,995),'Window','.82m outer trim | Z2.53–4.37m','#4cc9f0'),((75,1094,195,1413),'Radiator','At brick corner, beside door','#ef476f'),((1435,28,1506,1430),'Pipe','Rear white-wall corner','#a8e6a1')],
 'closet-entry':[((323,478,616,1410),'Closet door','.62m leaf | Z1.61–3.64m','#4cc9f0'),((323,56,616,459),'Upper cupboard','.62×.86m | Z3.70–4.56m','#a8e6a1'),((991,471,1490,1426),'Living entry','1.08m frame; clear≈1.00m','#ffd166')],
 'brick-wall':[((482,0,964,878),'Infilled fireplace','CenterX=-5.31; broad spanX[-6.10,-4.48]','#ffd166'),((67,249,331,873),'Shelf nook','Observed shelves; count/details uncertain','#4cc9f0'),((1346,675,1504,874),'Radiator','X[-7.96,-7.43]','#ef476f')]
}
for stem,aa in anns.items():
 im=Image.open(out/f'raw-{stem}.png').convert('RGB'); canvas=Image.new('RGB',(im.width,im.height+200),(25,28,34));canvas.paste(im,(0,0));d=ImageDraw.Draw(canvas)
 for i,(box,name,text,color) in enumerate(aa):
  d.rectangle(box,outline=color,width=5);x,y=box[0]+8,max(5,box[1]+8);d.rectangle((x-4,y-2,x+len(name)*18+10,y+35),fill=(20,23,28));d.text((x,y),name,font=font,fill=color)
  d.text((18,im.height+12+i*42),f'{name}: {text}',font=small,fill=color)
 d.text((18,im.height+177),'Calibrated raw Polycam orthographic view. Approximate dimensions; scan holes retained.',font=small,fill='white')
 canvas.save(out/f'reference-{stem}-annotated.png')
# Floor plan, geometry only
for showzones,name in [(False,'room-only-dimensioned-plan.png'),(True,'access-and-work-zones-plan.png')]:
 fig,ax=plt.subplots(figsize=(17,10));ax.set_aspect('equal');ax.add_patch(Polygon(poly,facecolor='#faf7ee',edgecolor='#202e40',linewidth=4))
 ax.add_patch(Rectangle((-3.78,-1.35),.70,1.66,facecolor='#eee0c5',edgecolor='#947e57',hatch='//',alpha=.8))
 ax.text(-3.43,-.53,'Existing hanging\ncloset interior\nnot recorded',ha='center',va='center',fontsize=8)
 if showzones:
  for z in zones:
   x1,x2,y1,y2=z['bounds_xy_m'];kind=z['type'];color='#cc6655'if kind.startswith('preserve') else '#7592ad'if 'access' in kind else '#77b39a'if 'zone' in kind else '#a68cb5'
   ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,facecolor=color,edgecolor=color,alpha=.20,linewidth=1.5))
  for id,label in [('white-wall-worktop-run','Two work surfaces\n2.85m available run'),('rear-brick-clothes-storage','Folded clothes\n~.8×.47m'),('visitor-chair-adjusted','Compact visitor\nchair option'),('cat-tree-near-window','Cat tree option\nverify full envelope')]:
   z=next(q for q in zones if q['id']==id);x1,x2,y1,y2=z['bounds_xy_m'];ax.text((x1+x2)/2,(y1+y2)/2,label,ha='center',va='center',fontsize=9,color='#16382d')
  ax.text(-4.24,-.51,'Closet\napproach',ha='center',fontsize=9,color='#aa4434');ax.text(-3.55,-2.2,'Entry\napproach',ha='center',fontsize=9,color='#aa4434');ax.text(-7.43,-2.04,'Exterior door\napproach',ha='center',fontsize=9,color='#aa4434')
 # doorway openings white knockout then colored symbol
 for x,yr,label,col in [(-7.98,[-2.55,-1.64],'Rear exterior\n6-panel door','#ad733e'),(-3.08,[-2.73,-1.65],'Living door\nframe 1.08m','#ad733e'),(-3.78,[-.83,-.21],'Closet\nleaf.62m','#3792ac')]:
  ax.plot([x,x],yr,color='white',lw=8,zorder=3);ax.plot([x,x],yr,color=col,lw=3,zorder=4)
  if x==-3.78:
   ax.annotate('Closet leaf .62m', (x,np.mean(yr)), (-2.84,.53), arrowprops=dict(arrowstyle='-',color=col),ha='center',fontsize=9,color=col)
  else:
   off=-.18 if x<-7 else .15
   ax.text(x+off,np.mean(yr),label,ha='right'if off<0 else'left',va='center',fontsize=9,color=col)
 ax.plot([-7.98,-7.98],[-.96,-.14],color='#55aac1',lw=8,zorder=4);ax.text(-8.08,-.50,'Single sash window\ntrim~.82×1.84m\nsill~.95m above floor',ha='right',va='center',fontsize=10,color='#27778a')
 ax.add_patch(Rectangle((-7.96,-2.79),.53,.32,facecolor='#4a4b50'));ax.annotate('Observed radiator\n.53×.32m approx',(-7.69,-2.63),(-8.45,-3.15),arrowprops=dict(arrowstyle='-'),ha='center',fontsize=10)
 ax.add_patch(Rectangle((-6.1,-2.85),1.62,.14,facecolor='#9b6951',alpha=.7));ax.plot([-5.65,-4.98],[-2.835,-2.835],color='white',lw=4);ax.text(-5.31,-3.15,'Brick chimney / recessed infill\ncenter X=-5.31; broad span~1.62m',ha='center',va='top',fontsize=10)
 ax.add_patch(Rectangle((-3.95,-2.9),.87,.35,facecolor='#b7babc',alpha=.5));ax.text(-3.49,-3.13,'Built-in shelf nook\npartly scanned',ha='center',va='top',fontsize=9)
 ax.add_patch(Rectangle((-8,.14),.28,.17,facecolor='#aeb6b6'));ax.text(-8.08,.48,'Existing pipe',ha='right',fontsize=9)
 ax.annotate('',(-3.08,.82),(-7.98,.82),arrowprops=dict(arrowstyle='<->',lw=1.3));ax.text(-5.53,.92,'4.90m overall along X',ha='center',fontsize=12)
 ax.annotate('',(-3.78,.59),(-7.98,.59),arrowprops=dict(arrowstyle='<->',lw=1.0));ax.text(-5.88,.40,'4.20m main white-wall run',ha='center',fontsize=10)
 ax.annotate('',(-2.15,.31),(-2.15,-2.79),arrowprops=dict(arrowstyle='<->',lw=1.3));ax.text(-2.02,-1.24,'3.10m',rotation=90,ha='left',va='center',fontsize=12)
 ax.text(-5.80,.14,'WHITE WALL / +Y',ha='center',fontsize=10,color='#666');ax.text(-6.8,-2.93,'BRICK / -Y',ha='center',fontsize=9,color='#905740')
 ax.text(-7.6,-3.80,'← Rear / backyard (-X)',fontsize=10,ha='left');ax.text(-3.4,-3.80,'Front / living (+X) →',fontsize=10,ha='right')
 ax.set_title('HIS OFFICE — grounded room architecture'+('\nAccess buffers and feasible zones (planning assumptions)'if showzones else'\nRoom architecture and observed fixed features'),loc='left',fontsize=18,pad=20)
 ax.text(-8.85,-4.22,'Scan overall 4.90×3.10m; ~14.03m². Ceiling≈3.02m above floor. Listing≈4.72×3.00m.\nWalls/generalized bounds≈±5–12cm; calibrated openings≈±3–6cm. Closet interior unrecorded. Door swings inferred.\nBlender Z-up metres. Plans show nominal footprints; verify installation measurements before purchase.',fontsize=10,ha='left',va='top')
 ax.set_xlim(-8.90,-1.80);ax.set_ylim(-4.75,1.30);ax.axis('off');fig.tight_layout();fig.savefig(out/name,dpi=180,bbox_inches='tight',pad_inches=.25);plt.close(fig)
# source pack note
readme='''His Office room-only geometry/reference pack\n\nAuthority: original Polycam recording, original scan.blend, calibrated orthographic renders and observed mesh surfaces. Amy furnishing placement is excluded. Preserve original metre scale. Generalized floor plan is not a survey.\n\nOverall envelope4.90m along X×3.10m alongY; main rectangle4.20×3.10m with brick-side front entry extension. Usable generalized floor area14.028m², closet interior excluded. FloorZ≈1.575, ceilingZ≈4.595, height≈3.02m. Listing rear bedroom4.724×2.997m agrees within3–4%; neither is surveyed.\n\nAxis mapping: +X front/living, -X rear/backyard; +Y white wall, -Y brick/fireplace; +Z up. glTF=[X,Z,-Y].\n\nEvery observed access/fixture is in fixed-features.json. Most consequential corrections: actual closet door and overhead cupboard, wider~1.08m living frame, white6panel rear door, smaller and higher rear sash window than the old integrated proxy, radiator beside rear door at brick corner, white pipe and front built-in shelf nook. Closed fireplace infill observed; operability unknown.\n\nAll door approach rectangles and furniture zones in access-and-feasible-zones.json are planning choices. Door closed states observed; hinge/swing inferred from knob sides because hardware is incomplete. No new furnishing authority is implied. Final layout must check products against architecture and these access rectangles.\n\nRaw image references preserve scan holes. The calibrated ortho cameras are recorded in raw-camera-poses.json. Pixel calibration for rear/front views: horizontal and vertical .0021875m/px; rear Y=-2.99+.0021875u, front Y=.51-.0021875u, bothZ=4.690625-.0021875v. Brick/white views .003375m/px; Z=4.56875-.003375v.\n\nModel-source-pointers.json inventories the old integrated model. It provides source object pointers only: ignore all Amy/entry proposed furniture and optional dresser collections, and apply corrections only in the new room model. The raw scan upper source meshes are Mesh_11..21.\n'''
open(out/'README.txt','w').write(readme+'\nFeasibility notes:\n'+'\n'.join('- '+s for s in layout_notes)+'\n')
print('Wrote pack',out,'area',area)
