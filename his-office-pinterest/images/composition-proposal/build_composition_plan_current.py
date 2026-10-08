#!/usr/bin/env python3
"""Read sources and draw a diagram only; never open or mutate Blender scenes."""
import copy
import datetime
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, Ellipse, FancyBboxPatch

OUT = Path(__file__).resolve().parent
BASE = Path('/workspace/his-office-pinterest')
LAYOUT = BASE/'variants/b-charcoal-slat/model/layout.json'
ROOM = Path('/workspace/his-office-redesign/geometry/room-measurements.json')
FIXED = Path('/workspace/his-office-redesign/geometry/fixed-features.json')
CATALOG = BASE/'products/selected-products.json'
SOURCE_BLEND = BASE/'variants/b-charcoal-slat/model/his-office-design.blend'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
layout, room, fixed, catalog = [json.loads(p.read_text()) for p in (LAYOUT, ROOM, FIXED, CATALOG)]
items = {v['id']: copy.deepcopy(v) for v in layout['items']}
chair = next(v for v in catalog['owned_keepers'] if v['id']=='aeron-size-c-mineral')
photo = Path(chair['official_image_file'])
sources = [{'file':str(p),'sha256':sha(p)} for p in (LAYOUT, ROOM, FIXED, CATALOG, SOURCE_BLEND, photo)]
composition_ids=['mosslanda-black-display-ledge','fado-kajplats-opal-table-lamp',
                 'grovemade-dark-grey-medium-plus','sill-small-parlor-westcott-black']
composition_catalog=[v for v in catalog['items'] if v['id'] in composition_ids]

# The old chair location is retained only as the proposal anchor. The file on
# disk still identifies Branch; the diagram must disclose that stale status.
aeron = copy.deepcopy(items['branch-primary'])
aeron.update(id='owned-aeron', product_id=chair['id'], kind='owned_task_chair',
    external_dimensions_m=chair['dimensions_m_W_D_H'],
    expanded_arm_footprint_m=chair['collision_footprint_m'],
    rolling_base_diameter_m=chair['base_diameter_m'],
    source='Confirmed owned chair catalog; current saved chair anchor',
    pose_status='Proposal anchor retained from saved layout; new owned-chair scene is not built',
    actual_owned_options_status='Vintage, base, arm/back/caster options unconfirmed')
selected = [items[k] for k in ('standing-main-desk','secondary-workspace','visitor-chair',
    'clothes-dresser','honeywell-lamp','muttros-cat-tree','rug','richmond-art')]+[aeron]
for v in selected:
    if v['id']!='owned-aeron':
        v['source']=str(LAYOUT)
        v['placement_status']='Existing saved layout anchor; diagram does not move furniture'

features={v['id']:v for v in fixed['features']}
zones=[
 {'id':'WORK','members':['standing-main-desk','secondary-workspace','owned-aeron','honeywell-lamp','muttros-cat-tree'],
  'label_anchor_blender_xy_m':[-5.6,-.9],'status':'Diagram grouping only; no clearance boundary'},
 {'id':'CONSOLE','members':['clothes-dresser'],'label_anchor_blender_xy_m':[-6.6,-2.99],
  'status':'Existing chest grouped as console; no furniture change'},
 {'id':'LOUNGE','members':['visitor-chair'],'label_anchor_blender_xy_m':[-4.7,-1.4],
  'status':'Diagram grouping only; existing fireplace/brick retained'}]
proposals=[
 {'id':'bench-ledge','label':'MOSSLANDA ledge','dimensions_m_W_D':[1.15,.12],
  'suggestion_target_blender_xy_m':[-5.55,.31],'alignment':'Centered above fixed clear bench',
  'product_id':'mosslanda-black-display-ledge','top_above_floor_m':1.25,'top_native_z_m':2.825,
  'styling':'Small illustrative books only, maximum20cm high; no large plants',
  'status':'Provisional idea only; not modeled or fit-tested'},
 {'id':'main-ledge','label':'Second matching MOSSLANDA ledge','dimensions_m_W_D':[1.15,.12],
  'product_id':'mosslanda-black-display-ledge','suggestion_target_blender_xy_m':[-6.915,.31],
  'alignment':'Centered above primary Tria desk','top_above_floor_m':2.10,'top_native_z_m':3.675,
  'styling':'Small illustrative books only; full desk lift/hardware clearance pending builder and QA',
  'status':'Provisional shelf anchor; not modeled or fit-tested'},
 {'id':'console-lamp-palm-tray','label':'FADO/KAJPLATS lamp opposite Small Parlor Palm / Westcott Black, central useful tray space',
  'suggestion_target_blender_xy_m':items['clothes-dresser']['position_blender_m'][:2],
  'product_ids':['fado-kajplats-opal-table-lamp','sill-small-parlor-westcott-black'],
  'lamp_envelope_m_D_H':[.254,.2286],'plant_nursery_bottom_height_range_m':[.1524,.2794],
  'pot_outer_diameter_m':.127,'pot_height_status':'Not published; any proxy height must be disclosed',
  'floor_plant':False,'status':'Selected real products; styling symbols only, final placement/foliage fit pending'},
 {'id':'main-desk-mat','label':'Grovemade Dark Grey Medium Plus desk mat',
  'product_id':'grovemade-dark-grey-medium-plus','dimensions_m_W_D_H':[.9652,.40005,.0035],
  'suggestion_target_blender_xy_m':[-6.915,-.20],
  'status':'Selected real product; additive proposed worktop anchor, not modeled or hardware-fit-tested'},
 {'id':'independent-richmond','label':'Independently hung Richmond above bench ledge',
  'center_above_floor_m':1.85,'center_native_z_m':3.425,'center_blender_x_m':-5.55,
  'paper_dimensions_m_W_H':[1.0,.7],'frame_external_height_proxy_m':.7254,
  'frame_bottom_above_floor_m':1.4873,'gap_above_ledge_top_m':.2373,
  'picture_ledge_manufacturer_max_picture_height_m':.45,
  'mounting':'Independent wall mounting; never lean this70cm-high print on a ledge rated for45cm pictures',
  'status':'Root-directed proposal anchor; existing scene art height remains unchanged'}]
wall=[
 {'variant':'B','paint':'Peppercorn SW7674','paint_sRGB':[88,88,88],
  'wrap_surfaces':['existing workwall +Y','adjacent rear windowwall -X'],
  'slat_material':'Black Ash / black felt','panel_count':5,
  'panel_width_m':.6,'total_bay_width_m':3.0,
  'bay_span_blender_x_m':[-7.60,-4.60],'bay_center_blender_x_m':-6.10,
  'bay_status':'Exact root-directed proposal across both desk sections; not installed geometry'},
 {'variant':'C','paint':'Naval SW6244','paint_sRGB':[47,61,76],
  'wrap_surfaces':['existing smooth workwall +Y','adjacent rear windowwall -X'],
  'slats':False}]
data={
 'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'Composition proposal diagram for review before any new model changes',
 'coordinate_system':'Blender native metric XY; +Y workwall, -Y exposed brick; -X rear windowwall',
 'source_files':sources,'room_outline_blender_xy_m':room['outline_blender_xy_m'],
 'room_outline_confidence':room['outline_confidence'],
 'room_floor_z_m':layout['room_floor_z_m'],'room_ceiling_z_m':layout['room_ceiling_z_m'],
 'fixed_architecture':fixed['features'],'existing_furniture_and_owned_chair_proposal':selected,
 'zones':zones,'provisional_additions':proposals,'wall_finish_proposals':wall,
 'selected_composition_product_records':composition_catalog,
 'budgets_from_cost_authority':catalog.get('budgets'),
 'cost_authority':str(CATALOG),'cost_note':'Use current canonical catalog quantities/line totals; no estimate is made by the diagram author.',
 'retained':['White ceiling','Existing white door/window trim and doors','Exposed brick and infilled fireplace',
             'Existing radiator, pipe, closet/upper cupboard, shelf nook and controls'],
 'source_transition_note':'Saved layout still uses Branch Pro and a 3-panel bay. This diagram replaces the chair label/envelope from confirmed owned Mineral Aeron Size C catalog and shows root-directed 5-panel/wrap proposals. These overrides are not represented as existing model geometry.',
 'limits':['Furniture is shown as simplified product envelopes, not a render.',
           'No additions have been modeled, purchased or physically fit-tested.',
           'No dimensional clearance, door-swing, accessibility or installation claim is made.',
           'Dashed symbols/arrows are suggestions; height/product choices remain open.'],
 'model_mutations':False}
(OUT/'composition-plan-current.json').write_text(json.dumps(data,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig=plt.figure(figsize=(16,10),facecolor='#F6F7F7')
fig.text(.06,.947,'HIS OFFICE  /  COMPOSITION PROPOSAL',fontsize=22,weight='bold',color='#24333B')
fig.text(.06,.912,'Shared arrangement for B + C  •  Measured room + saved furniture anchors  •  Review before model changes',fontsize=11,color='#52616A')
ax=fig.add_axes([.05,.12,.66,.75]);ax.set_aspect('equal');ax.axis('off')
ax.set_xlim(-8.8,-2.63);ax.set_ylim(-3.65,1.0)
outline=room['outline_blender_xy_m']
ax.add_patch(Polygon(outline,closed=True,facecolor='#F1EDE6',edgecolor='#36444B',lw=2.7,zorder=1))
# Zones provide compositional emphasis only, not measured path reserves.
ax.add_patch(FancyBboxPatch((-7.83,-1.6),3.32,1.84,boxstyle='round,pad=0,rounding_size=.11',
 facecolor='#DBE4E7',edgecolor='none',alpha=.46,zorder=2))
ax.add_patch(FancyBboxPatch((-7.2,-2.76),1.24,.6,boxstyle='round,pad=0,rounding_size=.08',
 facecolor='#E4D8C6',edgecolor='none',alpha=.55,zorder=2))
ax.add_patch(FancyBboxPatch((-5.17,-2.46),1.1,1.03,boxstyle='round,pad=0,rounding_size=.1',
 facecolor='#D9E1D8',edgecolor='none',alpha=.6,zorder=2))
ax.add_patch(Rectangle((-3.78,-1.35),.7,1.66,facecolor='#E4E6E7',edgecolor='#8C999F',lw=1,zorder=1))
ax.text(-3.41,-.31,'Closet /\nupper cupboard',ha='center',va='center',fontsize=8,color='#67747B')

# Colored edge traces represent proposed paint, without changing room geometry.
ax.plot([-7.98,-3.78],[.31,.31],color='#344D5C',lw=7,zorder=3,solid_capstyle='butt')
ax.plot([-7.98,-7.98],[.31,-2.79],color='#344D5C',lw=7,zorder=3,solid_capstyle='butt')
ax.text(-6.42,.78,'DARK WORKWALL',ha='center',fontsize=10,weight='bold',color='#344D5C')
ax.annotate('Wrap onto windowwall',xy=(-7.98,-1.24),xytext=(-8.52,-.04),rotation=90,
 ha='center',va='center',fontsize=8,color='#344D5C',arrowprops={'arrowstyle':'-','color':'#344D5C'})
ax.plot([-7.98,-3.08],[-2.79,-2.79],color='#A46B51',lw=6,zorder=3,solid_capstyle='butt')
ax.text(-5.34,-3.52,'EXISTING BRICK + WHITE INFILLED FIREPLACE RETAINED',ha='center',fontsize=8,color='#87583E')

# Architecture boundaries. Leaves stay closed; no inferred swing is drawn.
for key in ('rear-exterior-door','living-entry','closet-door'):
 f=features[key];b=f['bounds_blender_xyz_m'];x=(b[0]+b[1])/2
 if key=='rear-exterior-door':x=-7.98
 if key=='living-entry':x=-3.08
 if key=='closet-door':x=-3.78
 ax.plot([x,x],[b[2],b[3]],lw=7,color='white',zorder=8)
 ax.plot([x,x],[b[2],b[3]],lw=1.2,color='#8A979D',zorder=9)
ax.annotate('Rear door',xy=(-7.98,-2.1),xytext=(-8.4,-2.36),ha='center',fontsize=8,color='#52616A',
 arrowprops={'arrowstyle':'-','color':'#8A979D'})
ax.text(-2.91,-2.19,'Living\nentry',ha='center',fontsize=8,color='#52616A')
ax.text(-3.95,-.53,'Closet\ndoor',ha='right',fontsize=7.5,color='#52616A')
wf=features['rear-window']['bounds_blender_xyz_m']
ax.plot([-7.98,-7.98],[wf[2],wf[3]],lw=9,color='white',zorder=8)
ax.plot([-7.98,-7.98],[wf[2],wf[3]],lw=3,color='#9EC2D1',zorder=9)
ax.text(-8.16,-.62,'Window',rotation=90,ha='center',fontsize=8,color='#344D5C')
def fixed_box(key,color,label=None):
 b=features[key]['bounds_blender_xyz_m']
 ax.add_patch(Rectangle((b[0],b[2]),b[1]-b[0],b[3]-b[2],facecolor=color,edgecolor='#728087',lw=.7,zorder=8))
 if label: ax.text((b[0]+b[1])/2,(b[2]+b[3])/2,label,ha='center',va='center',fontsize=7,color='#39474D',zorder=10)
fixed_box('rear-radiator','#ABB0AE','Radiator')
fixed_box('closed-fireplace','#CAB7A9')
ax.plot([-5.65,-4.98],[-2.79,-2.79],color='white',lw=7,zorder=10)
ax.text(-5.32,-3.03,'Infilled fireplace',ha='center',fontsize=7,color='#87583E')
fixed_box('front-shelf-nook','#D5D9DA','Existing\nshelf nook')
ax.add_patch(Circle(tuple(features['rear-pipe']['approx_center_xy']),.05,facecolor='white',edgecolor='#8A979D',zorder=9))
ax.text(-7.78,.44,'Pipe',fontsize=7,color='#52616A')

def footprint(item,color,edge='#46545C',ls='-',lw=1.1,z=5):
 x,y=item['position_blender_m'][:2];w,d=item['external_dimensions_m'][:2]
 ax.add_patch(Rectangle((x-w/2,y-d/2),w,d,facecolor=color,edgecolor=edge,linestyle=ls,lw=lw,zorder=z))
 return x,y,w,d
rug=items['rug'];footprint(rug,'#CACBCD',edge='#ACB2B6',ls='--',lw=.8,z=3)
ax.text(-5.46,-1.85,'Rift Charcoal 6 × 9 ft',fontsize=7,color='#69747B',ha='center',zorder=4)
for key,label,color in [('standing-main-desk','MAIN TRIA','#29333A'),('secondary-workspace','CLEAR BENCH','#3C4246')]:
 x,y,w,d=footprint(items[key],color)
 ax.text(x,y+.035,label,ha='center',va='center',color='white',fontsize=9,weight='bold',zorder=6)
 ax.text(x,y-.12,'120 × 68.5 cm' if key=='standing-main-desk' else '140 × 60 cm',ha='center',color='#DAE0E2',fontsize=7,zorder=6)
# ALEX and ADILS details below the clear top are schematic and source-aligned.
x,y,w,d=items['secondary-workspace']['position_blender_m'][:2]+items['secondary-workspace']['external_dimensions_m'][:2]
ax.add_patch(Rectangle((x-w/2+.035,y-d/2+.02),.36,d-.04,facecolor='none',edgecolor='#DAE0E2',lw=.8,linestyle='--',zorder=7))
for yy in (y-d/2+.05,y+d/2-.05):ax.add_patch(Circle((x+w/2-.07,yy),.025,facecolor='#D7DDDF',zorder=7))
ax.text(-5.55,-.5,'LEFT ALEX + 2 RIGHT ADILS',ha='center',fontsize=7,color='#46545C')
# Chair is a simplified catalog envelope at the saved anchor, visibly disclosed.
x,y=aeron['position_blender_m'][:2];w,d=aeron['external_dimensions_m'][:2]
ax.add_patch(Ellipse((x,y),w,d,facecolor='#DBDFE1',edgecolor='#697980',lw=1.2,zorder=6))
ax.add_patch(Rectangle((x-.24,y-.12),.48,.3,facecolor='#ADB9BE',edgecolor='white',lw=.8,zorder=7))
ax.text(x,y-.45,'OWNED MINERAL AERON C',ha='center',fontsize=7.3,weight='bold',color='#46545C',zorder=8)
x,y,w,d=footprint(items['visitor-chair'],'#637D8B')
ax.add_patch(Rectangle((x-.21,y-.15),.42,.32,facecolor='#829BA6',edgecolor='white',lw=.7,zorder=7))
ax.text(x,y,'VISITOR',ha='center',va='center',color='white',fontsize=8,zorder=8)
ax.text(x,y-.5,'Axvall gray-blue',ha='center',fontsize=7.3,color='#46545C')
x,y,w,d=footprint(items['clothes-dresser'],'#6B5B4E')
ax.text(x,y,'CHEST',ha='center',va='center',fontsize=8,color='white',weight='bold',zorder=7)
ax.text(x,y+.34,'STORKLINTA',ha='center',fontsize=7,color='#46545C')
x,y,w,d=footprint(items['muttros-cat-tree'],'#B39573')
ax.add_patch(Ellipse((x,y),.7,1.1,facecolor='none',edgecolor='#A48360',lw=.7,ls=':',zorder=6))
ax.annotate('Owned brown tree',xy=(x,y),xytext=(-8.51,-1.39),ha='center',fontsize=7.5,color='#765C40',
 arrowprops={'arrowstyle':'-','color':'#A48360'},zorder=10)
x,y,w,d=footprint(items['honeywell-lamp'],'white')
ax.add_patch(Rectangle((x-.144,y-.305),.288,.61,facecolor='none',edgecolor='#B9C2C6',lw=.6,zorder=6))
ax.annotate('Owned white Honeywell\nopen head / 2 LED bars',xy=(x,y),xytext=(-8.46,.57),ha='center',fontsize=7.4,color='#52616A',
 arrowprops={'arrowstyle':'-','color':'#9AA5AB'},zorder=10)
# Wall art is a projected line and label; its actual paper remains native landscape.
ax.plot([-6.0627,-5.0373],[.365,.365],color='#69727A',lw=2,zorder=9)
ax.text(-5.55,.5,'Richmond 100 × 70 cm above bench',ha='center',fontsize=7.8,color='#52616A')
ax.plot([-7.60,-4.60],[.16,.16],lw=3,ls=(0,(3,2)),color='#A39079',zorder=9)
ax.text(-6.1,.96,'B: FIVE BLACK ASH PANELS  /  3 m ACROSS BOTH DESKS',ha='center',fontsize=8,color='#796B5A',weight='bold')
ax.text(-5.7,-1.01,'WORK',ha='center',fontsize=12,weight='bold',color='#5A707C')
ax.text(-6.6,-3.01,'CONSOLE',ha='center',fontsize=11,weight='bold',color='#8B7152')
ax.text(-4.66,-1.47,'LOUNGE',ha='center',fontsize=11,weight='bold',color='#688067')

# Provisional additions are arrows and markers, not simulated full-size objects.
gold='#BE8A35'
ax.plot([-6.125,-4.975],[.1,.1],color=gold,lw=2.5,ls='--',zorder=10)
ax.plot([-7.49,-6.34],[.1,.1],color=gold,lw=2.5,ls='--',zorder=10)
ax.annotate('1',xy=(-5.55,.1),xytext=(-4.48,.84),ha='center',va='center',fontsize=10,weight='bold',color='white',
 bbox={'boxstyle':'circle,pad=.32','fc':gold,'ec':'none'},arrowprops={'arrowstyle':'->','color':gold,'lw':1.4},zorder=11)
ax.annotate('2',xy=(-6.6,-2.51),xytext=(-7.21,-3.17),ha='center',va='center',fontsize=10,weight='bold',color='white',
 bbox={'boxstyle':'circle,pad=.32','fc':gold,'ec':'none'},arrowprops={'arrowstyle':'->','color':gold,'lw':1.4},zorder=11)
# Lamp and pot markers are proposed top styling. Plant crown has no guessed width.
ax.add_patch(Circle((-6.80,-2.51),.127,facecolor='#F7F5ED',edgecolor=gold,lw=1.1,zorder=9))
ax.add_patch(Circle((-6.36,-2.51),.0635,facecolor='#54674B',edgecolor=gold,lw=1.1,zorder=9))
ax.add_patch(Rectangle((-6.635,-2.60),.11,.17,facecolor='none',edgecolor=gold,lw=.9,ls='--',zorder=9))
ax.add_patch(Rectangle((-7.3976,-.400025),.9652,.40005,facecolor='none',edgecolor=gold,lw=1.1,ls='--',zorder=9))
ax.annotate('3',xy=(-6.45,-.37),xytext=(-6.08,-1.57),ha='center',va='center',fontsize=10,weight='bold',color='white',
 bbox={'boxstyle':'circle,pad=.32','fc':gold,'ec':'none'},arrowprops={'arrowstyle':'->','color':gold,'lw':1.4},zorder=11)

notes=fig.add_axes([.74,.13,.23,.735]);notes.axis('off')
def note(y,title,body,color='#24333B'):
 notes.text(0,y,title,fontsize=12,weight='bold',color=color,va='top')
 notes.text(0,y-.045,body,fontsize=10,color='#52616A',va='top',linespacing=1.55)
note(1.0,'KEEP THE ARRANGEMENT','Main desk + clear project bench.\nOne owned task chair.\nChest anchors the console zone.\nVisitor chair faces into the room.')
note(.79,'SELECTED COMPOSITION LAYERS',
 '1  TWO black MOSSLANDA ledges\n    Bench top H1.25 m; main H2.10 m.\n    Small illustrative books only.\n    Richmond independently hung,\n    center H1.85 m above floor.\n\n2  FADO lamp + small palm / black pot\n    opposite ends of the chest;\n    center remains useful for a tray.\n\n3  Grovemade Dark Grey Medium Plus\n    mat on the main Tria worktop.',gold)
note(.31,'B / C WALL COMPOSITION',
 'B  Peppercorn + 5 Black Ash panels\n     spanning both desk sections.\nC  Naval, smooth painted wall.\n\nBoth wrap onto the windowwall.\nWhite ceiling, trim and brick stay.')
notes.add_patch(Rectangle((0,-.003),.16,.025,transform=notes.transAxes,facecolor='#585858',edgecolor='none',clip_on=False))
notes.text(.2,.01,'B  Peppercorn',fontsize=9,va='center',color='#52616A')
notes.add_patch(Rectangle((.57,-.003),.16,.025,transform=notes.transAxes,facecolor='#2F3D4C',edgecolor='none',clip_on=False))
notes.text(.77,.01,'C  Naval',fontsize=9,va='center',color='#52616A')
fig.text(.06,.074,'SOLID = source layout / measured architecture     GOLD DASH + ARROWS = provisional ideas',fontsize=9,weight='bold',color='#52616A')
fig.text(.06,.043,'Aeron uses the saved chair anchor with its confirmed Size C source envelope. Additions and new wall treatment await review; no fit or installation claims.',fontsize=8.4,color='#68767D')
fig.savefig(OUT/'composition-plan-current.png',dpi=150,facecolor=fig.get_facecolor())
# Re-layout the same vector artists for a compact poster panel. No source raster
# is cropped, and no room render is synthesized.
notes.remove()
for artist in list(fig.texts):artist.remove()
fig.set_size_inches(10,22/3)
ax.set_position([.015,.055,.97,.925])
fig.text(.5,.018,'WORK / CONSOLE / LOUNGE   •   GOLD = PROPOSED ADDITIONS   •   SOURCE-SIZED DIAGRAM',
         ha='center',fontsize=8,color='#52616A')
fig.savefig(OUT/'composition-plan-only.png',dpi=150,facecolor=fig.get_facecolor())
plt.close(fig)
data['outputs']={'PNG':{'file':str(OUT/'composition-plan-current.png'),'sha256':sha(OUT/'composition-plan-current.png')},
                 'compact_PNG':{'file':str(OUT/'composition-plan-only.png'),'sha256':sha(OUT/'composition-plan-only.png'),
                                'pixel_dimensions':[1500,1100],'export_method':'Same source vector artists re-laid out; no raster crop'},
                 'script':{'file':str(Path(__file__).resolve()),'sha256':sha(Path(__file__).resolve())}}
data['source_hashes_rechecked_after_diagram']={r['file']:sha(r['file'])==r['sha256'] for r in sources}
(OUT/'composition-plan-current.json').write_text(json.dumps(data,indent=2)+'\n')
(OUT/'composition-plan-current.txt').write_text(
 'Read-only composition proposal, diagram rather than room render.\n'
 'Furniture/architecture: source layout and measured feature anchors.\n'
 'Owned Mineral Aeron C: confirmed catalog envelope at saved chair anchor; replacement is not yet built.\n'
 'Root wall proposals: B5 panels3m X[-7.60,-4.60] across both desks + Peppercorn wrap; C smooth Naval wrap.\n'
 'Two MOSSLANDA115x12cm ledges: benchTOP1.25m/mainTOP2.10m above floor; small illustrative books only.\n'
 'Richmond independently mounted center1.85m abovefloor; not leaned on ledge.\n'
 'Dresser: FADO/KAJPLATS opposite Small Parlor Palm / Westcott Black, central useful tray space; no floor plant.\n'
 'Main worktop: Grovemade Dark Grey Medium Plus mat96.52x40.005cm.\n'
 'No source files changed, no Blender modeling, no metric clearance/installation claims.\n'
 'See composition-plan-current.json for exact coordinates, source hashes, status and limits.\n')
print(json.dumps({'PNG':str(OUT/'composition-plan-current.png'),'compact_PNG':str(OUT/'composition-plan-only.png'),
                  'JSON':str(OUT/'composition-plan-current.json'),
                  'source_hashes_unchanged':all(data['source_hashes_rechecked_after_diagram'].values())}))
