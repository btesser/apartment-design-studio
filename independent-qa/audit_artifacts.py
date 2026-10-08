"""Independent source/geometry checks; writes JSON evidence, changes no model."""
import json, pathlib, struct, math, numpy as np
from shapely.geometry import Polygon

ROOT=pathlib.Path('/workspace')

def read_glb(path):
    raw=path.read_bytes(); off=12; js=None; binbuf=None
    while off<len(raw):
        size,kind=struct.unpack_from('<II',raw,off); block=raw[off+8:off+8+size]; off+=8+size
        if kind==0x4E4F534A: js=json.loads(block)
        elif kind==0x004E4942: binbuf=block
    return js,binbuf

def accessor(j,b,index):
    a=j['accessors'][index]; v=j['bufferViews'][a['bufferView']]
    dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    stride=v.get('byteStride',np.dtype(dtype).itemsize*n)
    return np.ndarray((a['count'],n),dtype=dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dtype).itemsize))

def matrix(n):
    if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
    x,y,z,w=n.get('rotation',[0,0,0,1]); q=np.array([
       [1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
       [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
       [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4);m[:3,:3]=q@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m

def world_bounds(path):
    j,b=read_glb(path); bounds={}
    def visit(i,parent):
        n=j['nodes'][i];m=parent@matrix(n);name=n.get('name',str(i));pts=[]
        if 'mesh'in n:
            for p in j['meshes'][n['mesh']]['primitives']:
                v=accessor(j,b,p['attributes']['POSITION']);pts.append(v@m[:3,:3].T+m[:3,3])
            if pts:
                v=np.concatenate(pts);bounds[name]=[v.min(0).tolist(),v.max(0).tolist()]
        for child in n.get('children',[]):visit(child,m)
    for n in j['scenes'][j.get('scene',0)]['nodes']:visit(n,np.eye(4))
    return bounds

report={}
source=ROOT/'apartment/8_21_2026.glb';copied=ROOT/'apartment-walkthrough/assets/scan.glb'
report['original_scan_byte_exact_copy']=source.read_bytes()==copied.read_bytes()
report['original_scan_bounds']=world_bounds(source)
geo=json.load(open(ROOT/'geometry-audit/geometry.json'));rooms={r['id']:r for r in geo['rooms']}
report['scan_vs_listing_relative_discrepancy']={r['id']:[round(a/b-1,4) for a,b in zip(r['main_dimensions_scan_m'],r['listing_m'])] for r in geo['rooms'] if r['id'] in ['his-office','her-office']}
report['dimension_comparability_notes']={r['id']:r['dimension_note'] for r in geo['rooms'] if 'dimension_note'in r}
manifest=ROOT/'apartment-furniture/furniture-manifest.json'
if manifest.exists():
    furniture=json.load(open(manifest));items=furniture['items'];polygons={i['id']:Polygon(i['footprint_blender_xy']) for i in items}
    report['outside_room_footprints']=[]
    for i in items:
        if i['room'] not in rooms:continue
        poly=polygons[i['id']];room=Polygon(rooms[i['room']]['outline'])
        outside=poly.difference(room).area
        if outside>.005 and i['kind'] not in ['curtain','art','sconce']:
            report['outside_room_footprints'].append({'id':i['id'],'room':i['room'],'outside_m2':round(outside,4)})
    report['overlapping_furniture_footprints']=[]
    for k,a in enumerate(items):
        excluded=['rug','lamp','curtain','art','chandelier','dome_lamp','led_lamp','cylinder_lamp','sconce','tv']
        if a['kind'] in excluded:continue
        for b in items[k+1:]:
            if a['room']!=b['room'] or b['kind'] in excluded:continue
            overlap=polygons[a['id']].intersection(polygons[b['id']]).area
            if overlap>.015:report['overlapping_furniture_footprints'].append({'a':a['id'],'b':b['id'],'overlap_m2':round(overlap,4)})
    report['orientation']= {i['id']:{'rotation':i['rotation_deg'],'front':i.get('front_blender_xy',i.get('facing_blender_xy')),'seated_gaze':i.get('seated_gaze_blender_xy')} for i in items if i['kind'] in ['sofa','chair','bed','desk','cabinet','console']}
    glb=ROOT/'apartment-furniture/furniture.glb'
    if glb.exists():report['furniture_actual_mesh_world_bounds']=world_bounds(glb)
repair=ROOT/'apartment-model/repair-shell.glb'
if repair.exists():report['repair_actual_mesh_world_bounds']=world_bounds(repair)
out=ROOT/'independent-qa/artifact-checks.json';json.dump(report,open(out,'w'),indent=2)
print(json.dumps({k:v for k,v in report.items() if 'bounds' not in k},indent=2))
print('Evidence saved:',out)
