"""Vector plan from frozen final B/C layouts; no scene or model mutations."""
import datetime
import hashlib
import json
import math
import shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, Ellipse, FancyBboxPatch

P=Path('/workspace/his-office-pinterest'); OUT=P/'layout'
B=P/'variants/b-charcoal-slat/model/layout.json'; C=P/'variants/c-ink-studio/model/layout.json'
ROOM=Path('/workspace/his-office-redesign/geometry/room-measurements.json')
FIXED=Path('/workspace/his-office-redesign/geometry/fixed-features.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources={str(p):sha(p) for p in (B,C,ROOM,FIXED,P/'products/selected-products.json')}
b,c,room,fixed=[json.loads(p.read_text()) for p in (B,C,ROOM,FIXED)]
bi={i['id']:i for i in b['items']};ci={i['id']:i for i in c['items']}
assert len(bi)==len(ci)==17 and set(bi)==set(ci)
wall_ids={'richmond-art','project-display-ledge','primary-display-ledge'}
comparison=[]
for rid in bi:
    x,y=bi[rid],ci[rid]
    delta=[y['position_blender_m'][i]-x['position_blender_m'][i] for i in range(3)]
    assert x['external_dimensions_m']==y['external_dimensions_m']
    assert x.get('rotation_z_deg',0)==y.get('rotation_z_deg',0)
    assert x.get('front_blender_vector')==y.get('front_blender_vector')
    if rid in wall_ids: assert all(abs(delta[i]-[0,.022,0][i])<1e-7 for i in range(3))
    else:assert all(abs(d)<1e-9 for d in delta)
    comparison.append({'id':rid,'C_minus_B_position_xyz_m':delta,'dimensions_orientation_identical':True,
        'status':'Intentional22mm wall-normal difference for B panel thickness' if rid in wall_ids else 'Exact same XYZ/orientation'})

checkpoint=OUT/'checkpoints/pre-composition-furnished-plan';checkpoint.mkdir(parents=True,exist_ok=True)
for name in ['final-furnished-plan.png','final-furnished-plan.pdf','final-furnished-plan-delta.json',
             'final-plan-footprints.json','final-plan-verification.json']:
    p=OUT/name
    if p.exists() and not (checkpoint/name).exists():shutil.copy2(p,checkpoint/name)

# Final QA agent owns this note-only handoff. A missing report makes no pass
# claim; regenerating after delivery changes neither layout nor models.
QA_NOTES=OUT/'final-plan-operation-notes.json'
if QA_NOTES.exists():
    qa=json.loads(QA_NOTES.read_text());sources[str(QA_NOTES)]=sha(QA_NOTES)
    assert qa.get('layout_sha256_B')==sources[str(B)]
    assert qa.get('layout_sha256_C')==sources[str(C)]
    for report_path in qa.get('source_report_paths',[]):
        if Path(report_path).exists():sources[report_path]=sha(report_path)
    operation_notes=qa['display_notes']
else:
    qa={'status':'Final independent operation notes pending; no clearance pass asserted'}
    operation_notes=['Final independent operation review pending.','No route or installation clearance pass is asserted by this plan.']

ids=list(bi); numbers={rid:n+1 for n,rid in enumerate(ids)}
footprints=[]
def world_dims(i):
    if 'world_axis_dimensions_m' in i:return i['world_axis_dimensions_m'][:2]
    w,d=i['external_dimensions_m'][:2];a=math.radians(i.get('rotation_z_deg',0))
    return abs(w*math.cos(a))+abs(d*math.sin(a)),abs(w*math.sin(a))+abs(d*math.cos(a))
for rid,i in bi.items():
    x,y=i['position_blender_m'][:2];w,d=world_dims(i)
    footprints.append({'id':rid,'key_number':numbers[rid],'position_blender_xyz_m':i['position_blender_m'],
       'external_dimensions_product_local_m':i['external_dimensions_m'],'rotation_z_deg':i.get('rotation_z_deg',0),
       'front_blender_vector':i.get('front_blender_vector'),'nominal_world_bbox_xy_m':[x-w/2,x+w/2,y-d/2,y+d/2],
       'layer':'elevated wall-mounted' if rid in wall_ids else 'supported tabletop' if not i.get('walk_blocker',True) else 'floor/conditional closet',
       'dimension_confidence':i.get('dimension_confidence',i.get('shape_confidence','Source-guided current layout'))})

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig=plt.figure(figsize=(16.54,11.69),facecolor='white')
fig.text(.04,.951,'HIS OFFICE  /  FINAL FURNISHED PLAN',fontsize=22,weight='bold',color='#25363F')
fig.text(.04,.923,'Frozen composed B/C layouts  •  17 product instances  •  Native metric geometry  •  One owned Mineral Aeron Size C',fontsize=11,color='#5D6D76')
ax=fig.add_axes([.035,.315,.59,.57]);ax.set_aspect('equal');ax.axis('off')
ax.set_xlim(-8.7,-2.44);ax.set_ylim(-3.39,1.06)
ax.add_patch(Polygon(room['outline_blender_xy_m'],closed=True,fc='#F2EEE7',ec='#3B4A52',lw=2.5,zorder=1))
ax.add_patch(Rectangle((-3.78,-1.35),.7,1.66,fc='#E4E7E8',ec='#A1AAAF',hatch='///',lw=.8,zorder=1))
ax.text(-3.43,-1.06,'Unrecorded\ncloset interior',ha='center',va='center',fontsize=7,color='#66757D')
ax.plot([-7.98,-3.78],[.31,.31],color='#364D59',lw=5,zorder=2)
ax.plot([-7.98,-7.98],[-2.79,.31],color='#364D59',lw=5,zorder=2)
ax.plot([-7.98,-3.08],[-2.79,-2.79],color='#A37158',lw=5,zorder=2)
features={v['id']:v for v in fixed['features']}
for rid,col in [('rear-radiator','#A8B0B1'),('closed-fireplace','#C4AD9B'),('front-shelf-nook','#D3D9DB')]:
    f=features[rid];r=f['bounds_blender_xyz_m']
    ax.add_patch(Rectangle((r[0],r[2]),r[1]-r[0],r[3]-r[2],fc=col,ec='#8A969B',lw=.7,zorder=4))
ax.plot([-5.65,-4.98],[-2.79,-2.79],color='white',lw=5,zorder=5)
ax.text(-5.3,-3.10,'Brick / white infilled fireplace',ha='center',fontsize=7.5,color='#8C614D')
ax.text(-3.5,-3.10,'Existing shelf nook',ha='center',fontsize=7.1,color='#66757D')
ax.annotate('Radiator',xy=(-7.7,-2.64),xytext=(-8.25,-2.95),fontsize=7.5,color='#66757D',ha='center',arrowprops={'arrowstyle':'-','lw':.7,'color':'#8A969B'})
for x,y0,y1,label,tx,ty in [(-7.98,-2.55,-1.64,'Rear exterior door',-8.2,-2.05),
                          (-3.08,-2.73,-1.65,'Living entry',-2.83,-2.2),
                          (-3.78,-.83,-.21,'Closet / upper cupboard',-3.29,.47)]:
    ax.plot([x,x],[y0,y1],color='white',lw=7,zorder=5)
    ax.plot([x,x],[y0,y1],color='#9AABB2',lw=1.2,zorder=6)
    ax.text(tx,ty,label,ha='center',va='center',rotation=90 if x==-7.98 else 0,fontsize=7.5,color='#66757D')
ax.plot([-7.98,-7.98],[-.96,-.14],color='white',lw=8,zorder=5)
ax.plot([-7.98,-7.98],[-.96,-.14],color='#94BCCB',lw=3,zorder=6)
ax.text(-8.17,-.55,'Window / sill ≈95.5cm',rotation=90,ha='center',fontsize=7.5,color='#4B7C91')
ax.add_patch(Circle((-7.91,.24),.05,fc='white',ec='#8A969B',lw=.7,zorder=7))
ax.text(-7.8,.41,'White pipe',fontsize=7,color='#66757D')

def tag(rid,x,y,color='#26363F',size=9):
    ax.text(x,y,str(numbers[rid]),ha='center',va='center',fontsize=size,color=color,weight='bold',zorder=12,
            bbox={'boxstyle':'circle,pad=.2','fc':'white','ec':'#C3CCD0','lw':.6})
def rect(rid,color,z=6,label=True,ls='-'):
    i=bi[rid];x,y=i['position_blender_m'][:2];w,d=world_dims(i)
    ax.add_patch(Rectangle((x-w/2,y-d/2),w,d,fc=color,ec='#596B75',lw=.9,zorder=z,ls=ls))
    if label:tag(rid,x,y)
    return x,y,w,d
rect('rug','#C7C9CB',z=3,label=False,ls='--');tag('rug',-5.70,-1.87)
for rid,color in [('standing-main-desk','#2E3B43'),('secondary-workspace','#42484C')]:
    x,y,w,d=rect(rid,color,label=False);tag(rid,x,y)
    ax.annotate('',xy=(x,y-d/2-.09),xytext=(x,y-d/2+.03),arrowprops={'arrowstyle':'-|>','lw':.8,'color':'#3F5967'},zorder=10)
x,y,w,d=bi['secondary-workspace']['position_blender_m'][:2]+bi['secondary-workspace']['external_dimensions_m'][:2]
ax.add_patch(Rectangle((x-w/2+.035,y-d/2+.02),.36,d-.04,fill=False,ec='#C4CCCF',lw=.7,ls='--',zorder=8))
for yy in (y-d/2+.05,y+d/2-.05):ax.add_patch(Circle((x+w/2-.07,yy),.025,fc='#DAE0E2',zorder=8))
ax.text(x,-.49,'LEFT ALEX + TWO RIGHT ADILS',ha='center',fontsize=6.8,color='#61737D')
x,y,w,d=rect('primary-felt-mat','#5F6970',label=False,z=8);tag('primary-felt-mat',x+.33,y+.12,size=7)
x,y=bi['aeron-primary']['position_blender_m'][:2]
ax.add_patch(Ellipse((x,y),.71882,.71882,fc='#D7DFE3',ec='#647A86',lw=1.1,zorder=6))
ax.add_patch(Circle((x,y),.6731/2,fill=False,ec='#99A8B0',lw=.7,zorder=7))
ax.add_patch(Rectangle((x-.80264/2,y-.71882/2),.80264,.71882,fill=False,ec='#86969F',ls=':',lw=.8,zorder=7))
ax.add_patch(Rectangle((x-.22,y-.13),.44,.30,fc='#AABAC2',ec='white',lw=.6,zorder=8));tag('aeron-primary',x,y)
ax.annotate('',xy=(x,y+.49),xytext=(x,y+.28),arrowprops={'arrowstyle':'-|>','lw':.9,'color':'#547D91'},zorder=10)
ax.add_patch(Circle((x,y-.45),.6731/2,fill=False,ec='#9DA7AD',ls='--',lw=.8,zorder=4))
rect('visitor-chair','#6E8998');x,y=bi['visitor-chair']['position_blender_m'][:2]
ax.annotate('',xy=(x,y+.50),xytext=(x,y+.30),arrowprops={'arrowstyle':'-|>','lw':.9,'color':'#547D91'},zorder=10)
x,y,w,d=rect('clothes-dresser','#756353',label=False);tag('clothes-dresser',x,y-.19,size=8)
ax.add_patch(Rectangle((x-w/2,y+d/2),w,bi['clothes-dresser']['drawer_pullout_m'],fill=False,ec='#AB9274',ls='--',lw=.9,zorder=4))
for rid,col in [('dresser-fado','#FAF8F1'),('dresser-parlor-palm','#5F7752')]:
    i=bi[rid];x,y=i['position_blender_m'][:2];w,d=i['external_dimensions_m'][:2]
    ax.add_patch(Ellipse((x,y),w,d,fc=col,ec='#718174',lw=.8,zorder=9,ls=':' if 'palm' in rid else '-'))
    tag(rid,x,y,size=7)
x,y,w,d=rect('muttros-cat-tree','#B39878')
ax.add_patch(Ellipse((x,y),.7,1.1,fill=False,ec='#A2815F',ls=':',lw=.8,zorder=7))
rect('honeywell-lamp','#FFFFFF')
x,y,w,d=rect('grejig-1','#DDE2D5',label=False,ls='--');ax.text(x,y,'9–11\n×3',ha='center',va='center',fontsize=8,color='#5F7259',zorder=10)
for rid in wall_ids:
    i=bi[rid];x,y=i['position_blender_m'][:2];w,d=i['external_dimensions_m'][:2]
    ax.add_patch(Rectangle((x-w/2,y-d/2),w,d,fill=False,ec='#A48B61',lw=.9,ls='--',zorder=11))
ax.text(-5.85,.57,'Elevated items 12–14 shown below',ha='center',fontsize=7.8,color='#997F53')
ax.text(-5.45,-1.07,'WORK',ha='center',fontsize=10,weight='bold',color='#667E8A')
ax.text(-6.6,-3.0,'CONSOLE',ha='center',fontsize=9,weight='bold',color='#937653')
ax.text(-4.66,-1.43,'LOUNGE',ha='center',fontsize=9,weight='bold',color='#6A8268')

def dimension(a,b,label,text,rotation=0):
    ax.annotate('',xy=a,xytext=b,arrowprops={'arrowstyle':'<->','lw':.9,'color':'#415762'})
    ax.text(*text,label,ha='center',va='center',fontsize=9,color='#415762',rotation=rotation)
dimension((-7.98,.91),(-3.08,.91),'4.90 m overall',(-5.53,1.0))
dimension((-7.98,.71),(-3.78,.71),'4.20 m main rectangle',(-5.88,.79))
dimension((-2.59,-2.79),(-2.59,.31),'3.10 m',(-2.48,-1.24),90)
ax.annotate('',xy=(-3.78,.65),xytext=(-3.08,.65),arrowprops={'arrowstyle':'<->','lw':.7,'color':'#81919A'})
ax.text(-3.43,.76,'.70 m notch',ha='center',fontsize=7.1,color='#7A8C96')
ax.annotate('',xy=(-3.17,-1.35),xytext=(-3.17,.31),arrowprops={'arrowstyle':'<->','lw':.7,'color':'#81919A'})
ax.text(-3.02,-.53,'1.66 m notch',ha='center',fontsize=7.1,color='#7A8C96',rotation=90)
ax.text(-7.94,-3.31,'Rear / backyard (−X)',ha='left',fontsize=7.3,color='#7A8B94')
ax.text(-3.12,-3.31,'Front / living (+X)',ha='right',fontsize=7.3,color='#7A8B94')

# A separate true-X/height elevation prevents elevated products reading as
# extra furniture occupying the floor or as a second project worktop.
e=fig.add_axes([.055,.075,.54,.215]);e.set_xlim(-7.8,-4.40);e.set_ylim(-.08,3.12)
e.set_aspect('auto');e.spines[['right','top','bottom']].set_visible(False)
e.set_xticks([]);e.set_yticks([0,.74,1.25,1.85,2.10,2.4,3.02])
e.set_yticklabels(['0','.74','1.25','1.85','2.10','2.40','3.02'],fontsize=7,color='#66757D')
e.set_ylabel('Height above floor (m)',fontsize=7.8,color='#66757D')
e.set_title('WORKWALL ELEVATION  /  native X and authored heights',loc='left',fontsize=10,weight='bold',color='#3D515D',pad=8)
for k in range(5):e.add_patch(Rectangle((-7.6+k*.6,0),.6,2.4,fc='#ECEDEE',ec='#C8CDCF',lw=.6,hatch='|||',zorder=1))
e.axhline(3.02,color='#8D9DA5',lw=.8);e.axhline(0,color='#66757D',lw=.9)
for rid in ('standing-main-desk','secondary-workspace'):
    i=bi[rid];x=i['position_blender_m'][0];w=i['external_dimensions_m'][0];h=i['external_dimensions_m'][2]
    e.add_patch(Rectangle((x-w/2,h-.0254),w,.0254,fc='#3C474E',zorder=3))
    e.text(x,.18,str(numbers[rid]),ha='center',fontsize=9,color='#415762',weight='bold')
for rid in ('project-display-ledge','primary-display-ledge'):
    i=bi[rid];x=i['position_blender_m'][0];w,_,h=i['external_dimensions_m'];top=i['top_height_above_floor_m']
    e.add_patch(Rectangle((x-w/2,top-h),w,h,fc='#282D31',zorder=4))
    e.text(x,top+.07,str(numbers[rid])+'  top '+str(top)+' m',ha='center',fontsize=8,color='#997F53',zorder=5)
i=bi['richmond-art'];x=i['position_blender_m'][0];z=i['position_blender_m'][2]-b['room_floor_z_m'];w,_,h=i['external_dimensions_m']
e.add_patch(Rectangle((x-w/2,z-h/2),w,h,fc='#F2F0E7',ec='#28343A',lw=1.5,zorder=4))
e.text(x,z,'12  RICHMOND\n100 × 70 cm paper\ncenter 1.85 m',ha='center',va='center',fontsize=7.5,color='#596970',zorder=5)
e.text(-7.68,2.66,'B: five panels 3.00 × 2.40 m\nC: smooth Naval at the same workwall',fontsize=7.4,color='#66757D',va='center')
e.text(-6.12,-.2,'Independently mounted art; shelf books illustrative. Same X/Z in B and C.',ha='center',fontsize=7.3,color='#66757D')

key=fig.add_axes([.65,.345,.325,.535]);key.axis('off')
key.text(0,1.02,'PRODUCT KEY  /  source dimensions',fontsize=12,weight='bold',color='#2E4552')
rows=[
 ('1','Tria standing desk','120.0 × 68.5 cm; shown top H74.0 cm'),
 ('2','Owned Mineral Aeron Size C','71.882 × 71.882 cm; base Ø67.31 cm'),
 ('3','Clear LAGKAPTEN / ALEX / ADILS','140 × 60 cm; left ALEX + two right legs'),
 ('4','Owned Honeywell 02E Pro','28.80 × 61.01 cm outer head; H196.85 cm'),
 ('5','Owned brown MUTTROS','Base59.94 × 55.88 cm; H149.86 cm'),
 ('6','Dark STORKLINTA clothes drawers','69.85 × 47.94 × H74.93 cm'),
 ('7','Axvall gray-blue EKENÄSET','65.09 × 73.98 × H74.93 cm'),
 ('8','Rift Charcoal flatwoven / pad','274.32 × 182.88 cm / 6 × 9 ft'),
 ('9–11','GREJIG ×3, conditional closet stack','58 × 27 × H17 cm each; rotated90°'),
 ('12','Richmond + thin black frame','100 × 70 cm paper; frame102.54 × 72.54 cm*'),
 ('13','Bench MOSSLANDA ledge','114.993 × 12 × H7 cm; lip top H125 cm'),
 ('14','Main MOSSLANDA ledge','114.993 × 12 × H7 cm; lip top H210 cm'),
 ('15','FADO / KAJPLATS on dresser','Source body Ø23.99 × H23.65 cm*'),
 ('16','Small Parlor Palm / Westcott Black','PotØ12.7 cm; proxy crownØ28 × H27.94 cm*'),
 ('17','Grovemade Dark Grey Medium Plus','96.52 × 40.005 cm; 3.5 mm thick')]
for n,(num,title,detail) in enumerate(rows):
    yy=.965-n*.0615
    key.text(0,yy,num,fontsize=8.5,weight='bold',color='#577889')
    key.text(.12,yy,title,fontsize=8.9,color='#334B59')
    key.text(.12,yy-.022,detail,fontsize=7.8,color='#73838C')

notes=fig.add_axes([.65,.072,.325,.245]);notes.axis('off')
notes.text(0,1,'OPERATION + PROXY LIMITS',fontsize=10.5,weight='bold',color='#354F5E')
lines=[]
for line in operation_notes:lines.append(str(line))
lines.extend(['Dotted chair box: published80.264 cm expanded-arm envelope.',
              'Dashed circle:45 cm rearward chair pose; drawer dash:27.62 cm pullout.',
              '* Frame outside profile assumed. FADO source CAD retained;',
              '  catalogØ25.4/H22.86 cm differs. Palm crown/pot height unpublished.',
              'Closet shoe-rack capacity, door swings, cat upper branches and',
              'lamp U-base detail need field confirmation. Actual hardware unrecorded.'])
notes.text(0,.90,'\n'.join(lines),fontsize=7.8,color='#647681',va='top',linespacing=1.55)
fig.text(.04,.025,'Room outline ≈4.90 × 3.10 m / 14.03 m²; ceiling≈3.02 m. Generalized scan walls typically±5–12 cm. Dimensioned model diagram; verify on site.',fontsize=8.1,color='#7B8D96')

fig.savefig(OUT/'final-furnished-plan.png',dpi=200,facecolor='white')
fig.savefig(OUT/'final-furnished-plan.pdf',facecolor='white')
# Reflow the original vector artists into the review's compact diagram panel;
# this is a fresh vector render, never a pixel crop of the standalone image.
key.remove();notes.remove()
for artist in list(fig.texts):artist.remove()
fig.set_size_inches(12,26/3)
ax.set_position([.01,.26,.97,.73])
e.set_position([.075,.065,.555,.175])
e.set_title('ELEVATED WORKWALL ITEMS 12–14',loc='left',fontsize=8.2,weight='bold',pad=4)
e.set_yticks([0,1.25,1.85,2.10,3.02])
e.set_yticklabels(['0','1.25','1.85','2.10','3.02'],fontsize=6.5,color='#66757D')
e.set_ylabel('Height above floor (m)',fontsize=6.7,color='#66757D')
for text_artist in e.texts:
    if text_artist.get_text().startswith('12  RICHMOND'):
        text_artist.set_text('12 Richmond / 100 × 70 cm\ncenter 1.85 m')
        text_artist.set_fontsize(7.3)
    elif text_artist.get_text().startswith('13  top'):
        text_artist.set_text('13 bench ledge / top 1.25 m')
        text_artist.set_y(1.0)
        text_artist.set_fontsize(7.3)
    elif text_artist.get_text().startswith('14  top'):
        text_artist.set_text('14 main ledge / top 2.10 m')
        text_artist.set_fontsize(7.3)
small=fig.add_axes([.665,.05,.315,.20]);small.axis('off')
small.text(0,1.0,'FURNISHED REVIEW DIAGRAM',fontsize=9.2,weight='bold',color='#354F5E',va='top')
small.text(0,.82,'1 Tria    2 Owned Aeron    3 Clear bench\n4 Honeywell    5 Cat tree    6 Clothes chest\n7 Visitor chair    8 Rift rug\n\nB/C: same floor furniture and facing.\nC art/ledges sit22mm farther toward wall;\nB five panels account for the offset.',
           fontsize=7.8,color='#657983',va='top',linespacing=1.4)
compact_review_note='Operation review pending; no clearance pass claimed.' if not QA_NOTES.exists() else '600 mm nominal route passes working +450 mm pullback; drawers/full pullback sequential. See sealed QA.'
fig.text(.5,.013,'Measured outline ≈14.03 m². Notch is architectural mass; closet interior unrecorded. '+compact_review_note,
         ha='center',fontsize=6.9,color='#7B8D96')
fig.savefig(OUT/'final-furnished-review-diagram.png',dpi=150,facecolor='white')
plt.close(fig)
proof={'schema_version':2,'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'stage':'Frozen composed final B/C furnished plan','source_layout_B':str(B),'source_layout_C':str(C),
 'source_sha256':sources,'item_count':17,'all_items_drawn_in_floor_or_elevated_layer':ids,
 'furniture_positions_modified':False,'model_mutations':False,'B_C_comparison':comparison,
 'shared_exact_XYZ_orientation_count':14,'intentional_wall_normal_offset_count':3,
 'intentional_offset_note':'C Richmond and both ledges Y=B+22mm; panel-depth mounting offset. All X/Z/dimensions/orientations identical.',
 'room_dimensions_xy_m':room['overall_dimensions_xy_m'],'room_outline_confidence':room['outline_confidence'],
 'floor_area_m2':room['area_m2'],'footprints':footprints,'operation_note_authority':qa,
 'B_panels':b['workwall_finish'],'C_finish':c['workwall_finish'],
 'earlier_plan_checkpoint':str(checkpoint),'display_floor_area_m2':14.03,
 'compact_diagram_note':'Same vector artists/data reflowed, not a pixel crop; numbered core furniture/facing plus elevated-layer drawing. No changes to dimensions or placements.',
 'outputs':{str(OUT/name):sha(OUT/name) for name in ['final-furnished-plan.png','final-furnished-plan.pdf','final-furnished-review-diagram.png']},
 'source_hashes_unchanged_after_plan':{p:sha(p)==h for p,h in sources.items()}}
assert all(proof['source_hashes_unchanged_after_plan'].values())
(OUT/'final-furnished-plan-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
(OUT/'final-plan-footprints.json').write_text(json.dumps({'layout_sha256_B':sources[str(B)],'layout_sha256_C':sources[str(C)],'footprints':footprints},indent=2)+'\n')
(OUT/'final-furnished-plan-delta.json').write_text(json.dumps({k:v for k,v in proof.items() if k!='footprints'},indent=2)+'\n')
print(json.dumps({'PNG':str(OUT/'final-furnished-plan.png'),'PDF':str(OUT/'final-furnished-plan.pdf'),
 'item_count':17,'operation_notes_status':qa.get('status'),'shared_exact_placements':14,'wall_offset_instances':3}))
