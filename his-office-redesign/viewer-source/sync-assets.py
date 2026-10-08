#!/usr/bin/env python3
"""Copy the new office-only models and measured metadata without changing scale."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model-dir',type=Path,default=root.parent/'model')
parser.add_argument('--cameras',type=Path,help='Final camera JSON with views in GLTF Y-up coordinates.')
parser.add_argument('--layout',type=Path,help='Layout JSON containing GLTF footprints or native Blender item positions/dimensions.')
args=parser.parse_args()
config=json.loads((root/'assets/config.json').read_text())
config['assets']={'shell':'his-office-shell.glb','doors':'his-office-door-leaves.glb','furniture':'his-office-furniture.glb'}
for key,name in list(config['assets'].items()):
    source=args.model_dir/name
    if source.exists():shutil.copy2(source,root/'assets'/name)
    elif key=='furniture':config['assets'][key]=None
    else:raise FileNotFoundError(source)
measurements=json.loads((root.parent/'geometry/room-measurements.json').read_text())
polygon=measurements['outline_gltf_xz_m'];width,depth=measurements['overall_dimensions_xy_m']
config['room'].update({'floor':measurements['floor']['nominal_z_m'],'ceiling':measurements['ceiling']['nominal_z_m'],'width':width,'depth':depth,'area':measurements['area_m2'],'polygon':polygon,'bounds':[min(p[0]for p in polygon),max(p[0]for p in polygon),min(p[1]for p in polygon),max(p[1]for p in polygon)]})
if args.cameras:
    poses=json.loads(args.cameras.read_text())
    config['views']=poses['views'] if isinstance(poses,dict) else poses
    # Match the shared native camera catalogue while keeping the UI legible.
    labels={'room-a':('From the entry','See both workspaces from the entrance.'),
            'room-b':('Rear door side','Look back toward the workspaces and room entrance.'),
            'room-c':('White wall corner','Review the brick wall, visitor chair and storage.'),
            'room-d':('Window side','An additional view across the new room arrangement.')}
    for view in config['views']:
        if view['id'] in labels:view['label'],view['description']=labels[view['id']]
    heights=[view['eye'][1]-config['room']['floor'] for view in config['views']]
    if heights and max(heights)-min(heights)<.001:config['room']['eyeHeight']=round(heights[0],5)
if args.layout:
    layout=json.loads(args.layout.read_text())
    config['footprints']=layout.get('footprints',[])
    if not config['footprints'] and layout.get('items'):
        # Preserve the canonical Blender frame: GLTF XZ = Blender X,-Y.
        def footprint(item,dimensions=None,suffix='',provisional=False):
            x,y,_=item['position_blender_m']
            width,depth,_=dimensions or item['external_dimensions_m']
            if item.get('rolling_base_diameter_m') and not dimensions:
                width=depth=item['rolling_base_diameter_m']
            angle=math.radians(item.get('rotation_z_deg',0))
            corners=[]
            for dx,dy in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:
                corners.append([x+dx*math.cos(angle)-dy*math.sin(angle),-(y+dx*math.sin(angle)+dy*math.cos(angle))])
            facing=item.get('front_blender_vector')
            kind=item['kind']
            return {'id':item['id']+suffix,'kind':kind,'polygon':corners,'center':[x,-y],
                    'facing':[facing[0],-facing[1]] if facing else None,
                    'provisional':provisional or 'Provisional' in item.get('placement_confidence',''),
                    'hiddenWhenDoorsClosed':item.get('hide_in_closed_door_views',False),
                    'walkBlocker':kind not in ('rug','art','closet_shoe_rack')}
        for item in layout['items']:
            config['footprints'].append(footprint(item))
            if item.get('upper_provisional_envelope_m'):
                reach=footprint(item,item['upper_provisional_envelope_m'],'-provisional-reach',True)
                reach['kind']='provisional_branch_reach'
                config['footprints'].append(reach)
        main=next((item for item in layout['items'] if item['id']=='uplift-main-desk'),None)
        if main:
            config['desk']={'width':main['external_dimensions_m'][0],'depth':main['external_dimensions_m'][1],
                            'confidence':'User-confirmed 42 × 30 inches','operatingHeight':main['external_dimensions_m'][2],
                            'heightConfidence':'Assumed seated operating height'}
        cat=next((item for item in layout['items'] if item['id']=='muttros-cat-tree'),None)
        if cat:
            config['catStand']={'baseWidth':cat['external_dimensions_m'][0],'baseDepth':cat['external_dimensions_m'][1],
                                'listedHeight':cat['external_dimensions_m'][2],'branchEnvelope':cat['upper_provisional_envelope_m'],
                                'branchEnvelopeConfidence':'Provisional; full projecting reach is unverified'}
        shutil.copy2(args.layout,root/'assets/layout.json')
    if 'desk' in layout:config['desk']=layout['desk']
    if 'catStand' in layout:config['catStand']=layout['catStand']
config['status']='final' if config['assets']['furniture'] and args.cameras else 'awaiting final furniture-safe cameras'
config['notes']='The shell follows the metric scan with reconstructed gaps. Generalized wall positions have approximately 5–12 cm uncertainty. Product shapes are simplified.'
(root/'assets/config.json').write_text(json.dumps(config,indent=2)+'\n')
shutil.copy2(root.parent/'geometry/room-measurements.json',root/'assets/room-measurements.json')
hashes={}
for key,name in config['assets'].items():
    if not name:continue
    p=root/'assets'/name
    hashes[key]={'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(root/'assets/source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('Copied office-only models in their original metre coordinates.')
