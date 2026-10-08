import json,math,hashlib,datetime
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle,FancyBboxPatch
P=Path('/workspace/his-office-pinterest');G=P/'layout';oldG=Path('/workspace/his-office-redesign/geometry');src=P/'model/layout.json';raw=src.read_bytes();layout=json.loads(raw);room=json.load(open(oldG/'room-measurements.json'));access=json.load(open(oldG/'access-and-feasible-zones.json'));items={x['id']:x for x in layout['items']};poly=room['outline_blender_xy_m'];lamp_base_foot_gap=(items['uplift-main-desk']['position_blender_m'][0]-.452-.035)-(items['honeywell-lamp']['position_blender_m'][0]+.084+.079/2);drawer_front=items['clothes-dresser']['position_blender_m'][1]+items['clothes-dresser']['external_dimensions_m'][1]/2+items['clothes-dresser']['drawer_pullout_m'];primary_base_back=items['branch-primary']['position_blender_m'][1]-items['branch-primary']['rolling_base_diameter_m']/2;drawer_default_gap=primary_base_back-drawer_front;drawer_pulledback_gap=drawer_default_gap-.45
fig=plt.figure(figsize=(16.5,11.7),facecolor='white');ax=fig.add_axes([.04,.21,.735,.70]);ax.set_aspect('equal');ax.set_xlim(-8.60,-2.23);ax.set_ylim(-3.65,1.05);ax.axis('off')
fig.text(.045,.95,'HIS OFFICE',fontsize=23,fontweight='bold',color='#1a2837')
fig.text(.045,.92,'Warm architectural studio · measured room geometry + selected product footprints',fontsize=14,color='#4f5b69')
# measured architecture
ax.add_patch(Polygon(poly,facecolor='#f9f5ed',edgecolor='#233448',lw=3.3,zorder=1))
ax.add_patch(Rectangle((-3.78,-1.35),.70,1.66,fc='#e8dfcc',ec='#a39274',hatch='//',alpha=.70,zorder=1))
# door access is a planning layer, not furniture or a measured door swing
for z in access['zones']:
 if z['id'] not in ['closet-approach','living-entry-approach','rear-door-approach']:continue
 x1,x2,y1,y2=z['bounds_xy_m'];ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,fill=False,ec='#cb8f7f',lw=1.05,ls=(0,(3,3)),zorder=2))
# rug at floor height; footprint dimensions are exact to selected nominal size
rug=items['rug'];x,y=rug['position_blender_m'][:2];w,d=rug['external_dimensions_m'][:2]
ax.add_patch(Rectangle((x-w/2,y-d/2),w,d,fc='#ecece5',ec='#82909a',lw=1.1,hatch='//',alpha=.55,zorder=2.2))
ax.text(x+.17,y-.81,'8',fontsize=11,color='#4c5968',ha='center',va='center',bbox=dict(boxstyle='circle',fc='white',ec='#a5afb9',pad=.2),zorder=9)
# fixed fixtures
ax.add_patch(Rectangle((-7.96,-2.79),.53,.32,fc='#484b4f',ec='#343b44',lw=.8,zorder=4))
for i in range(9):xx=-7.94+i*.058;ax.plot([xx,xx],[-2.77,-2.49],color='#7f8387',lw=1,zorder=4.1)
ax.add_patch(Rectangle((-8,.14),.28,.17,fc='#bcc4c3',ec='#879594',lw=.7,zorder=4))
ax.add_patch(Rectangle((-6.10,-2.85),1.62,.14,fc='#aa765b',ec='#825741',lw=.8,zorder=4))
ax.plot([-5.65,-4.98],[-2.835,-2.835],color='white',lw=4,zorder=4.2)
ax.add_patch(Rectangle((-3.95,-2.90),.87,.35,fc='#d7dcdb',ec='#9fa8a8',lw=.7,zorder=4))
# closed door/window apertures and separately observed actual closet forward face
for x,yr,col in [(-7.98,[-2.55,-1.64],'#ae794d'),(-3.08,[-2.73,-1.65],'#ae794d'),(-3.78,[-.83,-.21],'#398ba6')]:
 ax.plot([x,x],yr,color='white',lw=8,zorder=5);ax.plot([x,x],yr,color=col,lw=2,zorder=5.2)
ax.plot([-3.87,-3.87],[-.83,-.21],color='#398ba6',lw=2,zorder=5.3)
ax.plot([-7.98,-7.98],[-.96,-.14],color='#51a7bc',lw=7,zorder=5)
ax.plot([-7.93,-7.93],[-.96,-.14],color='#a6d2dc',lw=1,zorder=5.2)
# layout helpers
def dims_world(it):
 if 'world_axis_dimensions_m' in it:return it['world_axis_dimensions_m'][:2]
 w,d=it['external_dimensions_m'][:2];ang=math.radians(it.get('rotation_z_deg',0));return [abs(w*math.cos(ang))+abs(d*math.sin(ang)),abs(w*math.sin(ang))+abs(d*math.cos(ang))]
def rect_item(id,fc,ec,label=None,fs=10,z=5):
 it=items[id];x,y=it['position_blender_m'][:2];w,d=dims_world(it);patch=FancyBboxPatch((x-w/2,y-d/2),w,d,boxstyle='round,pad=0,rounding_size=.012',fc=fc,ec=ec,lw=1.15,zorder=z);ax.add_patch(patch)
 if label:ax.text(x,y,label,ha='center',va='center',fontsize=fs,color='#1f2d3b'if fc!='#3f4241'else'white',zorder=z+1)
 return x,y,w,d
# desks: arrow marks front of desktop; chair arrows indicate seated direction
x,y,w,d=rect_item('uplift-main-desk','#bf966e','#805c3e','1  UPLIFT\n42×30in',10)
xs=np.linspace(x-w/2,x+w/2,24);ys=y-d/2+.006*(1+np.sin(np.arange(24)*1.73));ax.plot(xs,ys,color='#70462c',lw=1.2,zorder=6)
ax.annotate('',(x,y-d/2-.09),(x,y-d/2+.06),arrowprops=dict(arrowstyle='-|>',color='#68452e',lw=1),zorder=8)
x,y,w,d=rect_item('secondary-workspace','#3f4241','#252a2d','2  Project bench\n140×60cm',10)
# ALEX left pedestal footprint, underneath desktop
ax.add_patch(Rectangle((x-w/2+.035,y-d/2+.02),.36,d-.04,fill=False,ec='#c7c8c5',lw=.75,zorder=6));ax.text(x-w/2+.215,y-.02,'ALEX',fontsize=7,color='#e7e9e6',ha='center',va='center',rotation=90,zorder=7)
ax.annotate('',(x+.2,y-d/2-.09),(x+.2,y-d/2+.06),arrowprops=dict(arrowstyle='-|>',color='#323b3e',lw=1),zorder=8)
# Task chair body + true rolling base circle; optional .45m rearward motion dashed
for id in ['branch-primary']:
 it=items[id];x,y=it['position_blender_m'][:2];rad=it['rolling_base_diameter_m']/2
 ax.add_patch(Circle((x,y),rad,fc='#323943',ec='#1e2833',lw=1,zorder=5.5));ax.add_patch(FancyBboxPatch((x-.20,y-.17),.40,.34,boxstyle='round,pad=0,rounding_size=.07',fc='#626b74',ec='#222f3b',lw=.8,zorder=6))
 ax.plot([x-.21,x+.21],[y-.20,y-.20],color='#141f2b',lw=4,zorder=6)
 ax.text(x,y-.02,'3',color='white',ha='center',va='center',fontsize=10,zorder=7)
 ax.annotate('',(x,y+.47),(x,y+.28),arrowprops=dict(arrowstyle='-|>',color='#2d657b',lw=1.5),zorder=7)
 ax.add_patch(Circle((x,y-.45),rad,fill=False,ec='#8b939b',lw=.9,ls=(0,(5,3)),zorder=3.5))
 ax.annotate('',(x+rad+.045,y-.45),(x+rad+.045,y),arrowprops=dict(arrowstyle='<->',lw=.7,color='#7d868f'),zorder=3.5)
# dresser, full drawer pull-out dashed
x,y,w,d=rect_item('clothes-dresser','#d1ba8a','#8d7755','4\n70×48cm',9)
front=y+d/2;pull=items['clothes-dresser']['drawer_pullout_m'];ax.add_patch(Rectangle((x-w/2,front),w,pull,fill=False,ec='#9b906f',lw=.8,ls=(0,(2,3)),zorder=3.5))
ax.annotate('',(x,front+.14),(x,front-.04),arrowprops=dict(arrowstyle='-|>',color='#765e3f',lw=1),zorder=7)
# visitor chair accurately narrower than earlier feasibility example
it=items['visitor-chair'];x,y=it['position_blender_m'][:2];w,d=dims_world(it)
ax.add_patch(FancyBboxPatch((x-w/2,y-d/2),w,d,boxstyle='round,pad=0,rounding_size=.07',fc='#b8a998',ec='#7e7064',lw=1.1,zorder=5));ax.plot([x-w/2+.055,x+w/2-.055],[y-d/2+.07,y-d/2+.07],color='#77695b',lw=7,zorder=6)
ax.text(x,y,'5',ha='center',va='center',color='white',fontsize=11,zorder=7);ax.annotate('',(x,y+d/2+.17),(x,y+d/2-.02),arrowprops=dict(arrowstyle='-|>',lw=1.2,color='#6c645a'),zorder=7)
# retained cat base is solid; upper basket circles dashed at their model-relative offsets
it=items['muttros-cat-tree'];x,y=it['position_blender_m'][:2];w,d=dims_world(it)
ax.add_patch(FancyBboxPatch((x-w/2,y-d/2),w,d,boxstyle='round,pad=0,rounding_size=.035',fc='#876347',ec='#614632',lw=1.2,zorder=5));ax.add_patch(Circle((x,y-.11),.19939,fc='#a27b59',ec='#654b34',lw=.8,zorder=5.3));ax.text(x,y-.06,'6',ha='center',va='center',color='white',fontsize=10,zorder=8)
for dx,dy,diam in [(-.095,-.085,.44958),(-.105,-.345,.381),(.105,.345,.381)]:
 ax.add_patch(Circle((x+dx,y+dy),diam/2,fill=False,ec='#a07745',lw=1.25,ls=(0,(4,3)),zorder=7))
ax.annotate('',(x+.41,y-.11),(x+.27,y-.11),arrowprops=dict(arrowstyle='-|>',lw=.9,color='#6d482d'),zorder=8)
# lamp U-base plus separate overhead light panel: shape dimensions are model approximations
it=items['honeywell-lamp'];x,y=it['position_blender_m'][:2]
for cx,cy,ww,dd in [(0,-.196,.247,.07),(-.084,.018,.079,.438),(.084,.018,.079,.438)]:
 ax.add_patch(Rectangle((x+cx-ww/2,y+cy-dd/2),ww,dd,fc='#fdfdf8',ec='#789088',lw=.8,zorder=7))
w,d=it['external_dimensions_m'][:2];ax.add_patch(Rectangle((x-w/2,y-d/2),w,d,fill=False,ec='#75a398',lw=1,ls=(0,(4,3)),zorder=8));ax.text(x-.02,y+.055,'7',color='#507469',ha='center',va='center',fontsize=10,zorder=9)
# stacked shoes: one dashed footprint denotes all three levels inside unrecorded closet
x,y,w,d=rect_item('grejig-1','#eeeae0','#8d927b',None,z=5)
ax.add_patch(Rectangle((x-w/2,y-d/2),w,d,fill=False,ec='#687861',lw=1,ls=(0,(3,2)),zorder=8));ax.text(x,y,'9\n×3',ha='center',va='center',fontsize=9,color='#54644d',zorder=9)
# art wall locations, not floor obstacles
for id in ['abstract-scenery-art']:
 it=items[id];x,y=it['position_blender_m'][:2];w=it['external_dimensions_m'][0];ax.plot([x-w/2,x+w/2],[y,y],color='#74705f',lw=3,zorder=7);ax.text(x,y+.08 if y>0 else y-.15,'10',color='#74705f',ha='center',fontsize=8,zorder=8)
# dimensions and external architectural callouts
ax.annotate('',(-3.08,.83),(-7.98,.83),arrowprops=dict(arrowstyle='<->',lw=1.2,color='#283a4c'));ax.text(-5.53,.91,'4.90m overall',ha='center',fontsize=11,color='#283a4c')
ax.annotate('',(-3.78,.54),(-7.98,.54),arrowprops=dict(arrowstyle='<->',lw=.9,color='#697684'));ax.text(-5.88,.60,'4.20m main wall',ha='center',fontsize=9,color='#697684')
ax.annotate('',(-2.43,.31),(-2.43,-2.79),arrowprops=dict(arrowstyle='<->',lw=1.1,color='#283a4c'));ax.text(-2.33,-1.24,'3.10m',rotation=90,ha='left',va='center',fontsize=11,color='#283a4c')
ax.text(-8.09,-.55,'Window\n~.82×1.84m\nsill~.95m',ha='right',va='center',fontsize=9,color='#348598')
ax.text(-8.09,-2.04,'Rear\nexterior door',ha='right',va='center',fontsize=9,color='#9a643d')
ax.text(-3.00,-2.02,'Living\ndoor',ha='left',va='center',fontsize=9,color='#9a643d')
ax.annotate('Closet door\n+ upper cupboard',(-3.87,-.21),(-3.33,.43),arrowprops=dict(arrowstyle='-',lw=.8,color='#368aa4'),fontsize=8.5,color='#368aa4',ha='center')
ax.text(-3.44,-1.08,'Interior\nunrecorded',ha='center',va='center',fontsize=8,color='#83775e')
ax.annotate('Radiator',(-7.69,-2.67),(-8.02,-3.07),arrowprops=dict(arrowstyle='-',lw=.8,color='#59626c'),fontsize=9,color='#59626c',ha='center')
ax.text(-5.31,-3.07,'Brick arch / recessed white infill',ha='center',fontsize=9,color='#9c6f54')
ax.text(-3.5,-3.10,'Existing\nshelf nook',ha='center',va='top',fontsize=8,color='#7d8c8a')
ax.text(-6.95,.36,'WHITE WALL / +Y',ha='center',fontsize=8,color='#7c8c8e')
ax.text(-6.85,-2.97,'BRICK / -Y',ha='center',fontsize=8,color='#9c6f54')
ax.text(-7.78,-3.52,'← Rear / backyard (-X)',ha='left',fontsize=9,color='#5b6773');ax.text(-3.30,-3.52,'Front / living (+X) →',ha='right',fontsize=9,color='#5b6773')
# Right-hand product legend and honest uncertainty
leg=fig.add_axes([.80,.24,.185,.63]);leg.axis('off')
leg.text(0,1.02,'PRODUCT KEY',fontsize=12,fontweight='bold',color='#273b4f')
rows=[('1','Owned UPLIFT desk','42×30in · 106.7×76.2cm'),('2','Clear project work surface','140×60cm · black ALEX on left'),('3','Branch Pro chair ×1','Rolling base Ø70.1cm'),('4','STORKLINTA drawers','69.85×47.94cm · three drawers'),('5','EKENÄSET visitor chair','Kilanda beige · 64.14×78.11cm'),('6','Owned MUTTROS cat tree','Base 59.94×55.88cm · H149.86cm'),('7','Owned Honeywell 02E Pro','U-base approximate; head overhead'),('8','Ruggable Impasto Taupe','6×9ft · 274.32×182.88cm'),('9','GREJIG shoe racks ×3','58×27cm, rotated inside closet'),('10','Abstract Scenery art','100×70cm paper; frame assumed')]
for i,(num,title,detail) in enumerate(rows):
 yy=.96-i*.087;leg.text(0,yy,num,fontsize=10,fontweight='bold',color='#2c6077');leg.text(.13,yy,title,fontsize=9.2,color='#26394c');leg.text(.13,yy-.025,detail,fontsize=7.8,color='#687682')
# line convention legend
leg.text(0,.045,'Solid outlines: floor-level furniture\nGrey dashed: optional 45cm chair pullback\nBrown dashed: upper cat baskets (provisional)\nGreen dashed: overhead lamp head\nPale red dashed: door-approach planning buffers',fontsize=8,linespacing=1.55,color='#586875',va='top')
fig.text(.05,.18,'ROOM  4.90×3.10m overall  ·  14.03m² usable floor  ·  ceiling≈3.02m above floor',fontsize=12,fontweight='bold',color='#293e53')
fig.text(.05,.14,'Positions follow the approved model recipe. One task chair serves two independent work surfaces. Closet internals and door swings are unrecorded.',fontsize=9,color='#536473')
fig.text(.05,.115,f'Cat upper baskets and lamp U-base are approximate. Modeled lamp-base / desk-foot gap≈{lamp_base_foot_gap*100:.0f}cm. Shoe-rack fit inside the unrecorded closet is provisional.',fontsize=8.8,color='#536473')
fig.text(.05,.090,f'Dashed 45cm chair pullback shows movement. Fully open dresser drawers plus main-chair pullback leave≈{drawer_pulledback_gap*100:.0f}cm between them; use these states sequentially.',fontsize=8.8,color='#536473')
fig.text(.05,.065,'Nominal circulation: a 60cm planning circle passes with primary chair working or pulled back 45cm. Open clothes drawers + pulled-back chair block rear passage.',fontsize=8.8,color='#536473')
fig.text(.05,.039,'Geometry: original Polycam metres; generalized walls≈±5–12cm, openings≈±3–6cm. Listing rear bedroom≈4.72×3.00m. Verify installation dimensions.',fontsize=8.5,color='#778491')
# Source hash and footprints for machine reproducibility
footprints=[]
for it in layout['items']:
 x,y=it['position_blender_m'][:2];w,d=dims_world(it);footprints.append({'id':it['id'],'center_xy_m':[x,y],'world_bbox_xy_m':[x-w/2,x+w/2,y-d/2,y+d/2],'front_blender_vector':it.get('front_blender_vector'),'floor_z_m':it['position_blender_m'][2],'dimensions_authority':'layout.json; world_axis_dimensions_m takes precedence, else dimensions rotated by rotation_z_deg'})
delta={
 'source_layout':str(src),'layout_version':layout['layout_version'],'layout_sha256':hashlib.sha256(raw).hexdigest(),
 'positions_modified_by_plan':False,'item_count':len(layout['items']),
 'approved_changes_from_previous_design':['Remove secondary task chair and its monitor/keyboard','Move visitor chairX−4.53→−4.73','Replace two blue artworks with one neutral landscape100×70cm above project bench','Black ALEX and ADILS; neutral Kilanda visitor upholstery; quiet Impasto Taupe6×9 rug'],
 'outputs':['final-furnished-plan.png','final-furnished-plan.pdf'],'room_dimensions_m':[4.9,3.1,3.02],'floor_area_m2':14.028,
 'footprints':footprints,
 'visual_layer_notes':['Solid floor-level footprints; Branch base nominalØ.70104m','Dashed upper cat baskets are provisional modeled offsets, not solid collision rectangle','Honeywell open lamp head is separate overhead layer; U-base details approximate','45cm main-chair pullback and verified.276225m clothes drawer pullout are operational states','Three closet shoe racks conditional, world footprint.27X×.58Y'],
 'fit_disclosures':[{'id':'lamp_foot_gap','value_m':round(lamp_base_foot_gap,6),'status':'approximate U-base model; no position altered by plan'},{'id':'chair_pullback_plus_open_drawer','value_m':round(drawer_pulledback_gap,6),'working_chair_state_gap_m':round(drawer_default_gap,6),'status':'clothes drawer and full chair pullback block rear through-route; tuck chair before clothes access'},{'id':'nominal_continuous_route','person_circle_pass_m':.60,'sampled_person_circle_fail_m':.65,'chair_states':['working','primary45cmrearward'],'authority':'proposed-routing-check.json; generalized walls/open doors/conservative floor envelopes; not measured human clearance or accessibility claim'},{'id':'closet_shoes','status':'unrecorded interior fit remains conditional'},{'id':'cat_upper','status':'branch/basket dimensions unpublished and provisional'},{'id':'standing_desk','status':'UPLIFT separate from fixed bench;16.66cm side separation; no joined extension restricts height travel'},{'id':'frame_proxy','status':'Outside1.0254×.7254m,22.86mm deep presentation assumption; paper100×70cm verified'}]
}
fp=delta.pop('footprints');(G/'final-plan-footprints.json').write_text(json.dumps({'layout_sha256':delta['layout_sha256'],'coordinate_system':'Blender native metric Z-up','footprints':fp},indent=2));delta['footprints_file']='final-plan-footprints.json';(G/'final-furnished-plan-delta.json').write_text(json.dumps(delta,indent=2))
fig.savefig(G/'final-furnished-plan.png',dpi=220,facecolor='white');fig.savefig(G/'final-furnished-plan.pdf',facecolor='white');plt.close(fig)
assert src.read_bytes()==raw,'Layout changed during render; regenerate to match latest canonical.'
print('Plan completed',layout['layout_version'],'sha256',delta['layout_sha256'])
