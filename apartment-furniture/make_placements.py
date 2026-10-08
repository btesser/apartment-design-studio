import json, math
R='/workspace/apartment-furniture'
items=[]
def add(id,room,kind,pos,dims,a=0,row=None,confidence='Assumed external envelope; product proportions inferred from Amy board',**kw):
 it=dict(id=id,room=room,kind=kind,position=pos,dimensions=dims,rotation_deg=a,shopping_row=row,dimension_confidence=confidence,**kw)
 items.append(it);return it
zu=1.575;zl=-1.385
# Object local front is +Y, Z is up. Chairs' local front is their seated gaze.
add('living-sofa','living','sofa',[-.15,-2.215,1.535],[4.0,.95,.93],cushions=4,material='Charcoal leather',pillow_material='Blush pink velvet',confidence='Existing sofa: 4.00m width and .95m depth are unmeasured placeholders; not a verified SKU')
add('living-rug','living','rug',[-.15,-1.24,1.536],[3.6576,2.7432,.012],row=16,confidence='Shopping list exact selected 9 x 12 feet; dimensions rotated to long room axis',pattern='living',material='Rug tan')
add('living-media-console','living','cabinet',[-.15,.115,1.535],[1.75006,.39878,.55118],180,row=15,rows=1,cols=4,confidence='Shopping list exact 68.9 W x15.7 D x21.7 H inches')
add('living-tv','living','tv',[-.15,.285,2.285],[1.43,.035,.8],180,confidence='Existing TV presence/size unmeasured; concept display')
add('living-coffee-table','living','table',[-.25,-.96,1.535],[1.27,.65,.38],row=17,oval=True,material='Tabletop ivory')
for i,x in enumerate([-2.28,2.24]):add('living-side-table-'+str(i+1),'living','table',[x,(-1.43 if i==0 else -2.18),1.535],[.43,.43,.51],row=21,round=True,pedestal=False,material='Tabletop ivory',base_material='Gold brushed metal')
# Her office: vanity + chest on +Y wall; chair faces into work surface +Y.
add('her-vanity','her-office','desk',[5.48,.565,1.585],[1.2192,.47,.76],180,row=26,confidence='48-inch width from selected URL; depth and height assumed',vanity=True,material='Natural oak')
add('her-vanity-chair','her-office','chair',[5.48,-.11,1.585],[.56,.58,.83],0,row=29,office=True,material='Blush pink velvet')
add('her-white-chest','her-office','cabinet',[7.02,.555,1.585],[1.397,.45,1.0],180,row=30,rows=4,cols=2,confidence='55-inch width from selected URL; depth/height unverified')
add('her-loveseat','her-office','sofa',[6.73,-1.80,1.585],[1.27508,.6858,.889],40,row=32,confidence='Verified retailer 50.2 W x27 D x35 H inches',fluted=True,material='Ivory velvet',legs='Gold brushed metal',pillows=False)
add('her-round-rug','her-office','rug',[6.18,-1.28,1.586],[1.8542,1.8542,.012],row=36,confidence='Shopping list exact 6 feet1 inch diameter',round=True,material='Rug pink')
add('her-teal-side-table','her-office','table',[7.21,-.995,1.585],[.36,.36,.51],row=37,round=True,material='Teal painted wood')
# His office: desk at +Y rear wall. Three sourced bookshelves on same wall farther forward.
add('his-standing-desk','his-office','desk',[-6.78,-.095,zu],[1.40,.70,.76],180,confidence='Existing desk: 1.4 x .7m envelope unmeasured; standing desk set at seated height',material='Walnut')
add('his-office-chair','his-office','chair',[-6.78,-1.00,zu],[.67,.67,1.12],0,row=42,office=True,material='Black steel')
add('his-rug','his-office','rug',[-5.82,-1.23,zu+.001],[3.9624,2.6924,.012],row=47,confidence='Shopping list exact 8 feet10 inches x13 feet',pattern='office',material='Rug ivory')
for i,x in enumerate([-5.25,-4.815,-4.38]):add('his-bookcase-'+str(i+1),'his-office','shelf',[x,.177,zu],[.421894,.184912,1.108964],180,row=44,confidence='Shopping list exact 16.61 W x7.28 D x43.66 H inches')
add('his-desk-floor-lamp','his-office','dome_lamp',[-7.71,-.39,zu],[.25,.25,1.651],row=43,confidence='65-inch height from selected URL; diameter assumed')
add('his-bookcase-floor-lamp','his-office','led_lamp',[-3.98,.065,zu],[.2,.2,1.4478],row=45,confidence='57-inch height from selected URL; diameter assumed')
add('his-slim-console','his-office','console',[-6.70,-2.55,zu],[1.00076,.26,.79],0,row=46,confidence='39.4-inch width from selected URL; depth/height unverified',material='Walnut')
# Basement bedroom has conservative King envelope; provisional layout pending stand specs.
add('bedroom-king-bed','bedroom-flex','bed',[-1.43,-1.355,-1.415],[2.190,2.098,1.07],0,row=59,confidence='King mattress1.930x2.032m; retailer King frame width2.190 and length2.098m; retailer conflicting overall block flagged')
add('bedroom-rug','bedroom-flex','rug',[-1.43,-.98,-1.414],[3.048,2.3876,.012],row=68,confidence='Shopping list exact7 feet10 inches x10feet',pattern='bedroom',material='Rug green')
for i,x in enumerate([-2.815,-.045]):
 add('bedroom-nightstand-'+str(i+1),'bedroom-flex','cabinet',[x,-2.19,-1.415],[.508,.4064,.59944],0,row=66,confidence='Verified selectedNatural retailer20 W x16 D x23.6 H inches',rows=3,cols=1,fluted=False,material='Natural oak')
 add('bedroom-nightstand-lamp-'+str(i+1),'bedroom-flex','cylinder_lamp',[x,-2.19,-.81556],[.23,.23,.635],row=67,confidence='25-inch height from chosen retailer title; shade diameter assumed',material='Gold brushed metal')
add('bedroom-large-dresser','bedroom-flex','cabinet',[-2.225,.362,-1.415],[2.9972,.39624,.82296],180,row=57,rows=2,cols=4,fluted=False,material='Natural oak',confidence='Verified retailer118 W x15.6 D x32.4 H inches; only0.47m foot clearance in arrangement, needs onsite verification')
# Divider spans the bed zone along X; side opening to +Y circulation. The schematic divider is a movable furnishing.
add('bedroom-divider','bedroom-flex','curtain',[.35,-.945,-1.415],[2.87,.085,2.32],90,row=69,confidence='Rail selected9-12ft; modeled2.87m rail perpendicular to long apartment; height clipped to measured soffit clearance; full drape length needs alteration')
# Lounge sofa back at divider (-X), front faces dining (+X). Width goes along Y.
add('basement-sofa','basement-open','sofa',[.98,-1.285,zl],[2.1082,.92,.89],-90,row=48,confidence='83-inch width from chosen retailer title; depth/height assumed',material='Warm ivory boucle',cushions=2,fluted=True)
add('basement-lounge-rug','basement-open','rug',[2.28,-1.29,zl+.001],[2.7432,1.8288,.012],row=53,confidence='Shopping list exact6x9feet',pattern='nazco',material='Rug ivory')
add('basement-coffee-table-large','basement-open','table',[2.16,-1.16,zl],[.75946,.75946,.43942],row=49,round=True,material='Black marble',confidence='Height17.3in verified; presumed circular29.9in diameter conflicts retailer reported depth, footprint unresolved')
add('basement-coffee-table-small','basement-open','table',[1.83,-1.63,zl],[.46,.46,.37],row=49,round=True,material='Black marble')
for i,(y,a) in enumerate([(-1.82,62),(-.63,118)]):add('basement-orange-chair-'+str(i+1),'basement-open','chair',[3.27,y,zl],[.762,.79,.79],a,row=50,swivel=True,material='Burnt orange chenille',confidence='30-inch width from selected retailer title; depth/height assumed; faces inward toward sofa')
add('basement-lounge-side-table','basement-open','table',[3.73,-1.20,zl],[.29,.29,.57],row=51,round=True,material='Walnut')
add('basement-lounge-table-lamp','basement-open','lamp',[3.73,-1.20,zl+.57],[.22,.22,.37],row=52,material='Black steel')
# Dining table long axis Y (source plan table horizontal u), chairs' gaze always inward.
add('basement-dining-table','basement-open','table',[5.0,-.56,zl],[1.6002,.81,.76],90,row=54,material='Natural oak',confidence='63-inch length from selected URL; width/height unverified')
for i,(x,y,a) in enumerate([(4.25,-.995,-90),(4.25,-.125,-90),(5.75,-.995,90),(5.75,-.125,90),(5.0,-1.645,0),(5.0,.525,180)]):add('basement-dining-chair-'+str(i+1),'basement-open','chair',[x,y,zl],[.54,.57,.84],a,row=55,material='Camel fabric',confidence='Six chair footprints inferred from designer plan; chosen chairs width/depth/height unverified')
# Music room board only includes a rug and existing storage arrangement; no invented gym equipment layout.
add('music-rug','music-gym','rug',[-5.85,-1.63,-1.445],[1.8288,1.2192,.012],row=58,confidence='Shopping list exact4x6feet; placement inferred from music fragment',pattern='office',material='Rug ivory')
# Wall art and lights fit actual ceiling and source-facing walls.
add('living-abstract-art','living','art',[-.15,-2.745,2.55],[2.0574,.045,1.524],0,row=19,confidence='Shopping selected81x60in; board palette concept, not exact artwork')
for i,x in enumerate([-1.60,1.30]):add('living-sconce-'+str(i+1),'living','sconce',[x,-2.72,3.38],[.23,.18,.28],0,row=20,confidence='Source-board fixture shape; dimensions assumed')
add('her-branch-chandelier','her-office','chandelier',[6.18,-1.28,3.735],[.64,.64,.85],0,row=35,confidence='Polished brass branch form approximated from source board; dimensions assumed')
for i,y in enumerate([-1.96,-.09]):add('her-window-curtains-'+str(i+1),'her-office','window_curtain',[7.76,y,1.635],[1.30,.07,2.6924],90,row=39,confidence='Selected106-inch length; folded panel width/rod span adapted to measured window, sheer appearance approximation')
add('her-fireplace-blush-art','her-office','art',[5.61,-2.69,3.22],[1.016,.045,.762],0,row=38,confidence='Shopping40x30in; blush/gold source-board palette approximation',art_palette='blush')
add('basement-dining-orange-art','basement-open','art',[5.0,-2.305,-.42],[.75,.045,1.0],0,row=56,confidence='Shopping75x100cm; source-board orange window-light approximation',art_palette='orange-window',frame_material='Black steel')
# Clean shell uses the measured open-basement architecture floor. Keep raw local mode separate.
for it in items:
 if it['room']=='bedroom-flex':
  it['position'][2]=round(it['position'][2]+.03,6)
  it['grounding']={'raw_local_scan_floor_mode_z_m':-1.415,'clean_architecture_floor_z_m':-1.385,'clean_shell_grounding_delta_z_m':.03,'note':'Vertical grounding correction only; original X/Y and product dimensions preserved.'}
manifest={'items':items,'default_variant':'faithful-proposal','default_dresser_visible':True,'glb_layers':{'furniture.glb':'All furniture/decor except separately toggleable dresser','proposed-dresser.glb':'Full selected118-inch dresser, visible by default in walkthrough'},'furniture_grounding':{'bedroom-flex':{'raw_local_scan_floor_mode_z_m':-1.415,'clean_architecture_floor_z_m':-1.385,'delta_z_m':.03}},'layout_notes':['All room walls and source plan orientation registered to scan via geometry_audit, not generated design photos.','Source Amy living media centered slightly within actual solid wall run to fit selected console.','Her angled loveseat moved +Y .08m to clear observed low stone hearth lip; source40-degree inward facing retained.','Divider moved from provisional X -.7 to X +.35; King bed and selected20-inch nightstands shifted forward to preserve music-room doorway. This is proposed furniture-zone adaptation, not a measured wall.','Basement bed/dresser foot aisle narrow0.47m; renderer does not imply installation approval.','Basement 104-inch drape length exceeds observed ceiling/soffit. Modeled rod at2.32m clears soffit; purchase specification needs alteration.','No exact entry console position was given by Amy, so entry furniture withheld until layout evidence supports it.']}
json.dump(manifest,open(R+'/placements.json','w'),indent=2)
