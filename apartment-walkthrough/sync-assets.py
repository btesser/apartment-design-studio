#!/usr/bin/env python3
"""Synchronize audited source models and room coordinates without rescaling."""
import argparse
import json
from pathlib import Path
import shutil

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model-dir',type=Path,default=Path('/workspace/apartment-model'))
parser.add_argument('--scan',type=Path,default=Path('/workspace/apartment/8_21_2026.glb'))
parser.add_argument('--furniture',type=Path)
args=parser.parse_args()
metadata=json.loads((args.model_dir/'model-metadata.json').read_text())
auditPath=args.model_dir.parent/'geometry-audit/geometry.json'
if auditPath.exists():
    audited={r['id']:r for r in json.loads(auditPath.read_text())['rooms']}
    for room in metadata['rooms']:
        if room['id'] in audited:room.update(audited[room['id']])
        room['polygon_gltf_xz']=[[x,-y] for x,y in room['outline']]
        room['floor_y']=room['floor_z_m'];room['ceiling_y']=room['ceiling_z_m']
shutil.copy2(args.scan,root/'assets/scan.glb')
assets={'scan':'scan.glb','architecture':'architectural-shell.glb','repairs':'repair-shell.glb','furniture':'proposal-furniture.glb','fixtures':'observed-fixtures.glb','utilities':'inferred-utility-shell.glb','dresser':'proposed-dresser.glb','entry':'entry-design.glb'}
for key in ('architecture','repairs','fixtures','utilities'):
    source=args.model_dir/assets[key]
    if source.exists():shutil.copy2(source,root/'assets'/source.name)
if args.furniture:
    shutil.copy2(args.furniture,root/'assets/proposal-furniture.glb')
    dresser=args.furniture.parent/'proposed-dresser.glb'
    if dresser.exists():shutil.copy2(dresser,root/'assets/proposed-dresser.glb')
entrySource=args.model_dir.parent/'design-fidelity/entry-design.glb'
if entrySource.exists():shutil.copy2(entrySource,root/'assets/entry-design.glb')
floors={}
for level,value in metadata['levels'].items():
    id='basement' if level=='lower' else level
    ceilings=[r['ceiling_y'] for r in metadata['rooms'] if r['level']==level]
    floors[id]={'label':'Basement' if id=='basement' else 'Upstairs','height':value['floor_y'],'ceiling':value['ceiling_y'],'maxCeiling':max(ceilings),'bounds':value['bounds'],'eyeHeight':1.58,'walkablePolygons':[r['polygon_gltf_xz'] for r in metadata['rooms'] if r['level']==level]}
floors['upper']['walkStart']=[2.60,3.115,.15]
floors['upper']['walkLook']=[-.8,3.0,1.30]
floors['basement']['walkStart']=[7.0,.195,.40]
floors['basement']['walkLook']=[2.0,.195,1.1]
labels={'his-office':'His office','her-office':'Her office','living':'Living room','upper-kitchen':'Kitchen','bathroom-upper':'Upstairs bathroom','music-gym':'Music / gym','bedroom-flex':'Bedroom / flex area','basement-open':'Basement living / dining'}
short={'his-office':'His office','her-office':'Her office','living':'Living','upper-kitchen':'Kitchen','bathroom-upper':'Bath','music-gym':'Music / gym','bedroom-flex':'Bedroom','basement-open':'Living / dining'}
poses={
 'his-office':([-3.60,2.3],[-6.0,.25]),
 'her-office':([4.32,.25],[6.6,1.05]),
 'living':([2.60,.15],[-.80,1.3]),
 'upper-kitchen':([-2.5,-1.65],[-6.30,-1.20]),
 'bathroom-upper':([.70,-.95],[-.40,-2.15]),
 'music-gym':([-4.08,1.85],[-6.3,.4]),
 'bedroom-flex':([-3.4,.25],[-1.3,1.3]),
 'basement-open':([7.0,.4],[2.0,1.1]),
}
rooms=[]
for r in metadata['rooms']:
    poly=r['polygon_gltf_xz'];floor='basement' if r['level']=='lower' else 'upper'
    minx,maxx=min(p[0]for p in poly),max(p[0]for p in poly)
    minz,maxz=min(p[1]for p in poly),max(p[1]for p in poly)
    # The bounding-box center is an orbit target, never a claim of a rectangular room.
    center=[(minx+maxx)/2,r['floor_y'],(minz+maxz)/2]
    cleanFloor=metadata['levels']['lower']['floor_y'] if r['id']=='bedroom-flex' else r['floor_y']
    center[1]=cleanFloor
    a,b=poses[r['id']]
    dims=r.get('main_dimensions_scan_m')
    dimensionLabel=(f'{dims[0]:.2f} × {dims[1]:.2f} m · main scan envelope' if dims else f'{maxx-minx:.2f} × {maxz-minz:.2f} m · overall envelope')
    if r['id']=='bedroom-flex':dimensionLabel='Proposed bedroom zone · divider inferred'
    description='Irregular measured room outline; geometry and furniture share the original metre scale.'
    if r['id']=='bedroom-flex':description='Amy’s revised bedroom zone within the open flex space. The curtain divider location is inferred.'
    if r['id']=='music-gym':description='Amy’s revised room use. Furniture here is a provisional functional layout.'
    rooms.append({'id':r['id'],'label':labels[r['id']],'shortLabel':short[r['id']],'floor':floor,'polygon':poly,'center':center,'floorHeight':cleanFloor,'rawFloorHeight':r['floor_y'],'ceilingHeight':r['ceiling_y'],'dimensionsLabel':dimensionLabel,'description':description,'eye':[a[0],cleanFloor+1.58,a[1]],'look':[b[0],cleanFloor+1.35,b[1]],'orbit':[center[0]+2.5,cleanFloor+4.4,center[2]-4.1]})
entryPolygon=[[1.28,-.39],[3.73,-.39],[3.73,-1.84],[1.28,-1.84]]
rooms.append({'id':'entry','label':'Entry / stair landing','shortLabel':'Entry','floor':'upper','polygon':entryPolygon,'center':[2.5,1.535,-1.1],'floorHeight':1.535,'ceilingHeight':4.185,'eye':[2.6,3.115,-.8],'look':[1.30,2.45,-.85],'dimensionsLabel':'Part of the living / circulation area','description':'Amy’s entry pieces use provisional placements against measured walls. The original proposal gives no positions.'})
config={'units':'metres','coordinates':metadata['coordinate_system'],'assets':assets,'floorOrder':['upper','basement'],'floors':floors,'rooms':rooms,'collisions':[],
        'stair':{'lowerX':5.4,'upperX':1.95,'lowerY':metadata['levels']['lower']['floor_y'],'upperY':metadata['levels']['upper']['floor_y'],'zBounds':[-2.76,-1.86],'confidence':metadata['stair']['confidence']},
        'notes':metadata['uncertainty']}
manifestPath=(args.furniture.parent/'furniture-manifest.json') if args.furniture else Path('/workspace/apartment-furniture/furniture-manifest.json')
if manifestPath.exists():
    manifest=json.loads(manifestPath.read_text())
    config['furnitureFootprints']=[]
    for item in manifest['items']:
        polygon=item.get('footprint_blender_xy')
        if not polygon:continue
        position=item['position']; facing=item.get('facing_blender_xy',[0,1])
        floor=next((r['floor'] for r in rooms if r['id']==item['room']),'upper')
        config['furnitureFootprints'].append({'id':item['id'],'room':item['room'],'floor':floor,'polygon':[[x,-y] for x,y in polygon], 'center':[position[0],-position[1]],'front':[position[0]+facing[0]*.4,-position[1]-facing[1]*.4], 'confidence':item.get('dimension_confidence','Dimension unverified')})
    config['layoutNotes']=manifest.get('layout_notes',[])
entryManifest=args.model_dir.parent/'design-fidelity/entry-manifest.json'
if entryManifest.exists():
    for item in json.loads(entryManifest.read_text())['items']:
        position=item['position'];facing=item.get('facing_blender_xy',[0,1])
        config.setdefault('furnitureFootprints',[]).append({'id':item['id'],'room':'entry','floor':'upper','layer':'entry','polygon':[[x,-y]for x,y in item['footprint_blender_xy']],'center':[position[0],-position[1]],'front':[position[0]+facing[0]*.4,-position[1]-facing[1]*.4],'confidence':item['placement_confidence']})
(root/'assets/config.json').write_text(json.dumps(config,indent=2)+'\n')
print('Synchronized measured room coordinates and all available model layers.')
