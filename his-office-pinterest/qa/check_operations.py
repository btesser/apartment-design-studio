"""Independent nominal operations/clearance arithmetic from canonical inputs."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path('/workspace/his-office-pinterest')
lp=ROOT/'model/layout.json'
layout=json.loads(lp.read_text());items={i['id']:i for i in layout['items']}
mesh=json.loads((ROOT/'qa/integrated-mesh-checks.json').read_text())
parts=mesh['parts']
product_file=ROOT/'products/selected-products.json'
products={p['id']:p for p in json.loads(product_file.read_text())['items']}

def bbox(id):
    x,y,z=items[id]['position_blender_m'];w,d,h=items[id]['external_dimensions_m']
    return [[x-w/2,y-d/2,z],[x+w/2,y+d/2,z+h]]

def actual(group, name):
    xs=[p['bounds'] for p in parts if p['group']==group and name.lower() in p['name'].lower()]
    return [[min(a[0][k] for a in xs) for k in range(3)], [max(a[1][k] for a in xs) for k in range(3)]]

rug=bbox('rug');radius=items['branch-primary']['rolling_base_diameter_m']/2
caster=[]
for id in ['branch-primary']:
    for pullback in [0,.45]:
        x,y,z=items[id]['position_blender_m'];y-=pullback
        margins=[x-radius-rug[0][0],rug[1][0]-x-radius,y-radius-rug[0][1],rug[1][1]-y-radius]
        caster.append({'chair':id,'backward_translation_m':pullback,'caster_center_blender_xy_m':[x,y],
                       'rug_edge_margins_left_right_rear_front_m':margins,'entire_nominal_caster_circle_on_rug':min(margins)>=0})

dresser=bbox('clothes-dresser');visitor=bbox('visitor-chair');secondary=bbox('secondary-workspace')
drawer_travel=products['storklinta-low-drawers']['verified_drawer_pullout_m']
drawer_front=dresser[1][1]+drawer_travel
primary_y=items['branch-primary']['position_blender_m'][1]
low_basket=actual('muttros-cat-tree','Low side wicker basket')
top=actual('uplift-main-desk','solid wood barkline')
lamp_base=actual('honeywell-lamp','U-base')
desk_left_foot=[p['bounds'] for p in parts if p['group']=='uplift-main-desk' and p['name']=='C-frame steel foot'][0]
lamp_stem=actual('honeywell-lamp','upright')
upper_basket=actual('muttros-cat-tree','top wicker basket')
alex=actual('secondary-workspace','official alex-drawers')
right_leg=actual('secondary-workspace','ADILS leg')
records={
 'dresser_rear_door_planning_rectangle_x_gap_m':dresser[0][0]-(-6.98),
 'dresser_conservative_hearth_x_gap_m':(-6.10)-dresser[1][0],
 'dresser_radiator_broad_x_gap_m':dresser[0][0]-(-7.43),
 'dresser_drawer_verified_travel_m':drawer_travel,
 'dresser_drawer_front_when_fully_open_y_m':drawer_front,
 'dresser_rear_to_corrected_brick_face_y_gap_m':dresser[0][1]-(-2.837),
 'open_drawer_to_main_caster_gap_working_m':primary_y-radius-drawer_front,
 'open_drawer_to_main_caster_gap_full_0_45_pullback_m':primary_y-.45-radius-drawer_front,
 'visitor_entry_planning_rectangle_x_gap_m':(-4.08)-visitor[1][0],
 'visitor_conservative_hearth_y_gap_m':visitor[0][1]-(-2.48),
 'secondary_top_to_closet_approach_x_gap_m':(-4.80)-secondary[1][0],
 'secondary_top_to_observed_closet_frame_forward_plane_x_gap_m':(-3.90)-secondary[1][0],
 'secondary_nominal_knee_bay_width_between_ALEX_and_ADILS_m':right_leg[0][0]-alex[1][0],
 'lamp_U_base_to_left_desk_steel_foot_horizontal_gap_m':desk_left_foot[0][0]-lamp_base[1][0],
 'lamp_outer_panel_to_broad_pipe_y_gap_m':.14-bbox('honeywell-lamp')[1][1],
 'cat_low_basket_top_to_seated_table_underside_vertical_gap_m':top[0][2]-low_basket[1][2],
 'cat_low_basket_top_to_lowest_nominal_table_underside_vertical_gap_m':1.575+.66167-.04445-low_basket[1][2],
 'cat_low_basket_to_lamp_upright_y_gap_m':lamp_stem[0][1]-low_basket[1][1],
 'cat_top_basket_back_to_modeled_rear_wall_inner_face_x_gap_m':upper_basket[0][0]-(-7.93),
}
out={'canonical_layout_sha256':hashlib.sha256(lp.read_bytes()).hexdigest(),'native_source_scene_sha256':mesh['source_sha256'],
     'product_catalog_sha256':hashlib.sha256(product_file.read_bytes()).hexdigest(),
     'method':'Nominal canonical product envelopes and conservative caster circles, plus evaluated actual proxy part bounds. Metres in native Blender coordinates.',
     'clearance_values_m':records,'caster_on_rug_checks':caster,
     'dresser_operation':'Open drawer comfortably accessed in working chair pose; tuck the primary chair before prolonged standing at the dresser. Full chair pullback and open drawers leave only ~34cm nominal separation, not a through passage.',
     'dresser_mounting':'Selected STORKLINTA SKU 805.592.92 has Anchor/Unlock wall attachment. Its modeled rear is about8.7cm forward of the measured brick plane; mounting hardware reach is not verified. Verify approved masonry attachment/spacer or adjust toward the wall on site before relying on unlock/drawer function.',
     'closet_operation':'Secondary tabletop clears the conservative approach rectangle; closet leaf hinge/swing is inferred, and shoes/hanging hems/internal shelf capacity are not observed.',
     'field_checks':['Measure owned cat-tree full assembled branch/basket offsets and rotate/reposition if needed; top basket proxy is only ~2cm off reconstructed rear wall.',
                    'Measure Honeywell U-base shape/footprint; modeled base is photo-derived despite verified overall panel/height dimensions.',
                    'Check actual door swings and dresser handle clearance against room measurement uncertainty.',
                    'Confirm closet interior depth/width, hanging hems and real GREJIG stacking before installing racks.',
                    'Check UPLIFT actual cable slack and desk/chair settings through height changes.',
                    'Thin area rug and pad contact is compressed/soft in reality; final proxy rests at floor plane without simulating local pad compression.'],
     'limits':['Small nominal gaps such as 3cm dresser/door-box and 5cm closet-approach offsets are not reliable surveyed gaps: room outline is generalized by5–12cm, fixtures also have stated uncertainty.',
               'Human-route diameter is a planning assumption, not compliance or ergonomic certification.',
               'Subcomponent gap numbers describe this review model, not published assembled cat-tree or lamp-base measurements.']}
p=ROOT/'qa/operation-clearances.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'values':records,'primary_caster_always_on_rug':all(c['entire_nominal_caster_circle_on_rug'] for c in caster)}))
