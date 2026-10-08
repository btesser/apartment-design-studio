#!/usr/bin/env python3
"""Copy both frozen room alternatives byte-for-byte in their native metre frame."""
import copy
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

source=Path(__file__).resolve().parent
project=source.parent
assets=source/'assets'
variants=[
    ('b-charcoal-slat','B · Charcoal + slat','Charcoal finish with black vertical paneling. Compare the coordinated room arrangement.'),
    ('c-ink-studio','C · Ink studio','Deep ink-blue finish with the same functional room arrangement.'),
]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--variant',choices=[v[0]for v in variants],help='Sync one frozen alternative during assembly; omit for the final two-alternative build.')
parser.add_argument('--final',action='store_true',help='Mark the approved, frozen final model sync ready for delivery.')
args=parser.parse_args()
if args.variant:variants=[v for v in variants if v[0]==args.variant]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
measurements=json.loads((assets/'room-measurements.json').read_text())
polygon=measurements['outline_gltf_xz_m']
width,depth=measurements['overall_dimensions_xy_m']
room={'floor':measurements['floor']['nominal_z_m'],'ceiling':measurements['ceiling']['nominal_z_m'],'width':width,'depth':depth,'area':measurements['area_m2'],'polygon':polygon,'bounds':[min(p[0]for p in polygon),max(p[0]for p in polygon),min(p[1]for p in polygon),max(p[1]for p in polygon)],'eyeHeight':1.55}
products_document=json.loads((project/'products/selected-products.json').read_text())
products_by_id={i['id']:i for i in products_document.get('items',[])+products_document.get('owned_keepers',[])}
labels={'room-a':('From the entry','See the primary desk, clear project bench, lamp and window.'),'room-b':('Rear door side','Look toward the clear project bench, closet and entrance.'),'room-c':('Work wall corner','Review the brick arch, visitor chair and folded-clothes storage.'),'room-d':('Window side','Look across both work surfaces and the visitor area.')}
item_names={'branch-primary':'Primary task chair','secondary-workspace':'Clear project bench','honeywell-lamp':'Honeywell 02E floor lamp','muttros-cat-tree':'MUTTROS cat tree','clothes-dresser':'Folded-clothes drawers','visitor-chair':'Visitor armchair','rug':'Rift rug'}
kind_names={'wall_shelf':'Floating shelf','floating_shelf':'Floating shelf','table_lamp':'Decorative table lamp','floor_plant':'Floor plant','desk_mat':'Desk mat','wall_finish':'Wall finish','accent_panel':'Accent paneling','wall_panel':'Wall paneling','wall_art':'Wall art'}

def footprint(item,dimensions=None,suffix='',provisional=False):
    x,y,_=item['position_blender_m']; w,d,_=dimensions or item.get('collision_dimensions_m')or item['external_dimensions_m']
    if item.get('rolling_base_diameter_m') and not dimensions:w=d=item['rolling_base_diameter_m']
    angle=math.radians(item.get('rotation_z_deg',0)); corners=[]
    for dx,dy in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
        corners.append([x+dx*math.cos(angle)-dy*math.sin(angle),-(y+dx*math.sin(angle)+dy*math.cos(angle))])
    facing=item.get('front_blender_vector');kind=item['kind']
    wall_mounted=kind in ('wall_shelf','floating_shelf','art','wall_art','wall_finish','accent_panel','wall_panel')or item.get('wall_mounted',False)
    walk_blocker=item.get('walk_blocker',not wall_mounted and kind not in ('rug','desk_mat','closet_shoe_rack','table_lamp','decorative_object','shelf_object'))
    return {'id':item['id']+suffix,'kind':kind,'polygon':corners,'center':[x,-y],'facing':[facing[0],-facing[1]]if facing else None,'provisional':provisional or 'provisional'in item.get('placement_confidence','').lower(),'hiddenWhenDoorsClosed':item.get('hide_in_closed_door_views',False),'walkBlocker':walk_blocker}

def product_fact(item):
    product=products_by_id.get(item.get('product_id'),{})
    facing=item.get('front_blender_vector');orientation=''
    if facing:
        if facing[1]<-.5:orientation='Faces into the room from the work wall'
        elif facing[1]>.5:orientation='Faces toward the work wall'
        elif facing[0]>.5:orientation='Faces toward the room entrance'
        elif facing[0]<-.5:orientation='Faces toward the window side'
    name=item_names.get(item['id']) or product.get('name') or item.get('name')or kind_names.get(item['kind'])or item['id'].replace('-',' ').title()
    if item['kind']=='task_chair'and product.get('owned_status'):name=product.get('name',name)
    notes=[]
    if item.get('rolling_base_diameter_m'):notes.append('caster base '+str(round(item['rolling_base_diameter_m']*100))+' cm')
    if item.get('upper_provisional_envelope_m'):notes.append('upper branch reach is approximate')
    if item.get('branch_basket_major_axis')=='Y':notes.append('branches run along the window wall')
    if item['kind']=='rug'and item.get('major_axis')=='X':notes.append('long edge runs parallel to the two work surfaces')
    if item['kind']=='kept_lamp'and item.get('major_axis')=='Y':notes.append('long open head runs along the window wall')
    if item.get('hide_in_closed_door_views'):notes.append('closet interior fit is unverified; hidden with recorded closed doors')
    if item['kind']in ('art','wall_art'):notes.append(item.get('placement_note','installed on the work wall above the project bench'))
    if item['kind']in ('wall_shelf','floating_shelf'):notes.append('wall mounted; does not occupy the floor')
    if item.get('placement_note')and item['kind']not in ('art','wall_art'):notes.append(item['placement_note'])
    if 'desk'in item['kind'] or 'standing'in item['id']:notes.append('worktop height is shown at seated setting')
    return {'id':item['id'],'kind':item['kind'],'name':name,'dimensions_m':item['external_dimensions_m'],'orientation':orientation,'front_blender_vector':facing,'note':'; '.join(notes)}

def finish_facts(layout):
    facts=[]
    roles=layout.get('wall_finish_roles',{})
    if isinstance(roles,list):roles={str(i.get('id',index)):i for index,i in enumerate(roles)}
    if not isinstance(roles,dict):roles={}
    if not roles:
        roles={key:value for key,value in [('workwall',layout.get('workwall_finish')),('windowwall',layout.get('windowwall_finish'))]if value}
    for id,finish in roles.items():
        if not isinstance(finish,dict):finish={'treatment':str(finish)}
        name=finish.get('name')or{'workwall':'Work wall finish','windowwall':'Window wall finish'}.get(id,id.replace('-',' ').replace('_',' ').title())
        notes=[]
        for key in ('paint','treatment','scope','note','mounting_note'):
            if finish.get(key):notes.append(str(finish[key]))
        if finish.get('panel_count')and finish.get('bay_W_H_m'):
            w,h=finish['bay_W_H_m'];notes.append(f'{w:g} × {h:g} m panel bay; {finish["panel_count"]} panels')
        elif finish.get('panels')is False:notes.append('paint finish, without paneling')
        facts.append({'id':'finish-'+id,'kind':'wall_finish','name':name,'dimensions_m':[],'orientation':'','front_blender_vector':None,'note':' · '.join(notes)})
    return facts

catalog={'title':'His office · B and C alternatives','units':'metres','coordinates':'GLTF Y-up; native frame preserved without normalization','status':'final'if args.final else'working model checkpoint','variants':[]}
hashes={}
for id,label,description in variants:
    model=project/'variants'/id/'model'; destination=assets/id;destination.mkdir(parents=True,exist_ok=True)
    layout_path=model/'layout.json'; camera_path=model/'camera-poses.json'
    layout=json.loads(layout_path.read_text()); poses=json.loads(camera_path.read_text());views=poses.get('views',poses)if isinstance(poses,dict)else poses
    # The same native poses and original 24 mm horizontal field of view are retained.
    views=copy.deepcopy(views)
    for view in views:
        if view['id']in labels:view['label'],view['description']=labels[view['id']]
        view.setdefault('eye',view.get('eye_gltf_m'));view.setdefault('target',view.get('target_gltf_m'))
    config={'room':copy.deepcopy(room),'views':views,'assets':{},'footprints':[],'products':[product_fact(i)for i in layout['items']]+finish_facts(layout),'workwall_finish':layout.get('workwall_finish'),'wall_finish_roles':layout.get('wall_finish_roles'), 'notes':'Room outline follows the metric scan. Reconstructed wall locations have approximately 5–12 cm uncertainty. Product profiles are simplified. Door hinges and closet fit require an on-site check.'}
    for item in layout['items']:
        config['footprints'].append(footprint(item))
        if item.get('upper_provisional_envelope_m'):
            reach=footprint(item,item['upper_provisional_envelope_m'],'-provisional-reach',True);reach['kind']='provisional_branch_reach';config['footprints'].append(reach)
    main=next(i for i in layout['items']if i['kind']in ('standing_desk','primary_desk','kept_desk')or('main' in i['id']and'desk'in i['id']))
    config['desk']={'width':main['external_dimensions_m'][0],'depth':main['external_dimensions_m'][1],'operatingHeight':main['external_dimensions_m'][2],'confidence':'Branch Tria electric standing desk; supplier CAD dimensions','dimension_note':main.get('dimension_confidence','')}
    cat=next(i for i in layout['items']if i['id']=='muttros-cat-tree')
    config['catStand']={'baseWidth':cat['external_dimensions_m'][0],'baseDepth':cat['external_dimensions_m'][1],'listedHeight':cat['external_dimensions_m'][2],'branchEnvelope':cat['upper_provisional_envelope_m'],'branchEnvelopeConfidence':'Provisional; full projecting reach is unverified'}
    hashes[id]={}
    for key,name in {'shell':'his-office-shell.glb','doors':'his-office-door-leaves.glb','furniture':'his-office-furniture.glb'}.items():
        origin=model/name;target=destination/name;shutil.copy2(origin,target)
        assert sha(origin)==sha(target)
        config['assets'][key]=id+'/'+name
        hashes[id][key]={'file':id+'/'+name,'canonical_file':str(origin.relative_to(project)),'bytes':target.stat().st_size,'sha256':sha(target)}
    for name in ['layout.json','camera-poses.json','model-manifest.json']:
        origin=model/name
        if origin.exists():shutil.copy2(origin,destination/name)
    scene=model/'his-office-design.blend'
    catalog['variants'].append({'id':id,'label':label,'description':layout.get('viewer_description',description),'model_source':str(scene.relative_to(project)),'model_sha256':sha(scene),'layout_sha256':sha(layout_path),'camera_sha256':sha(camera_path),'config':config})
(assets/'config.json').write_text(json.dumps(catalog,indent=2)+'\n')
(assets/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps({'variants':[i['id']for i in catalog['variants']],'copied_models':sum(len(i)for i in hashes.values())},indent=2))
