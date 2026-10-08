"""Pure, read-only GLB transform/inventory parity QA."""
import hashlib
import json
import struct
from pathlib import Path
import numpy as np

ROOT=Path('/workspace/his-office-redesign')
MODEL=ROOT/'model'
layout=json.loads((MODEL/'layout.json').read_text())
specs={i['id']:i for i in layout['items']}
aliases={'kept-uplift-desk':'uplift-main-desk','kept-honeywell-02e-pro':'honeywell-lamp',
         'kept-muttros-cat-tree':'muttros-cat-tree','branch-pro-task-chair-1':'branch-primary',
         'branch-pro-task-chair-2':'branch-secondary'}
aliases.update({i:i for i in specs if i not in aliases.values()})

def read_glb(p):
    b=p.read_bytes(); magic,version,length=struct.unpack_from('<III',b)
    assert magic==0x46546c67 and version==2 and length==len(b)
    pos=12; js=None
    while pos<len(b):
        n,k=struct.unpack_from('<II',b,pos); pos+=8
        if k==0x4e4f534a: js=json.loads(b[pos:pos+n])
        pos+=n
    return js,hashlib.sha256(b).hexdigest()

def matrix(n):
    if 'matrix' in n: return np.array(n['matrix']).reshape(4,4).T
    x,y,z,w=n.get('rotation',[0,0,0,1])
    r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4); m[:3,:3]=r@np.diag(n.get('scale',[1,1,1])); m[:3,3]=n.get('translation',[0,0,0]); return m

def audit(p):
    g,h=read_glb(p); nodes=g['nodes']; worlds={}
    def walk(i,m):
        w=m@matrix(nodes[i]); worlds[i]=w
        for c in nodes[i].get('children',[]): walk(c,w)
    for i in g['scenes'][g.get('scene',0)]['nodes']: walk(i,np.eye(4))
    by_name={n.get('name',''):i for i,n in enumerate(nodes)}
    roots=[]; inventory=[]; all_lo=[]; all_hi=[]
    for name,canonical in aliases.items():
        i=by_name.get(name); actual=worlds[i][:3,3].tolist() if i is not None else None
        x,y,z=specs[canonical]['position_blender_m']; target=[x,z,-y]
        delta=max(abs(a-b) for a,b in zip(actual,target)) if actual else None
        roots.append({'root':name,'layout_id':canonical,'actual_gltf_m':actual,'target_gltf_m':target,'max_delta_m':delta,'pass':delta is not None and delta<1e-5})
    for i,n in enumerate(nodes):
        if 'mesh' not in n or i not in worlds: continue
        lo=[]; hi=[]
        for pr in g['meshes'][n['mesh']]['primitives']:
            ac=g['accessors'][pr['attributes']['POSITION']]
            pts=np.array([[a,b,c,1] for a in (ac['min'][0],ac['max'][0]) for b in (ac['min'][1],ac['max'][1]) for c in (ac['min'][2],ac['max'][2])])@worlds[i].T
            lo.append(pts[:,:3].min(axis=0)); hi.append(pts[:,:3].max(axis=0))
        lows=np.min(lo,axis=0).tolist(); highs=np.max(hi,axis=0).tolist()
        inventory.append({'name':n.get('name',''),'bounds_gltf_m':[lows,highs],'mesh_index':n['mesh']})
        all_lo.append(lows); all_hi.append(highs)
    return {'file':str(p),'sha256':h,'bytes':p.stat().st_size,'mesh_node_count':len(inventory),'material_count':len(g.get('materials',[])),
            'image_count':len(g.get('images',[])),'external_image_uris':[i['uri'] for i in g.get('images',[]) if 'uri' in i],
            'world_bounds_gltf_m':[np.min(all_lo,axis=0).tolist(),np.max(all_hi,axis=0).tolist()],
            'canonical_product_root_checks':roots,'all_product_roots_match':all(c['pass'] for c in roots),'mesh_inventory':inventory}

def run():
    files=[audit(MODEL/n) for n in ['his-office-design.glb','his-office-furniture.glb']]
    full={i['name']:i for i in files[0]['mesh_inventory']}; sub=files[1]['mesh_inventory']
    pairs=[]
    for item in sub:
        other=full.get(item['name']); error=float(np.max(np.abs(np.array(item['bounds_gltf_m'])-np.array(other['bounds_gltf_m'])))) if other else None
        pairs.append({'mesh':item['name'],'exists_in_integrated':other is not None,'max_bound_difference_m':error,'pass':error is not None and error<1e-5})
    out={'coordinate_mapping':'Native Blender [X,Y,Z] maps to exported GLTF [X,Z,-Y], metres, no rescale or mirror.',
         'method':'Read-only GLB v2 scene graph world transforms and POSITION accessor bounds. Transform tolerance checks export parity, not site measurement accuracy.',
         'layout_sha256':hashlib.sha256((MODEL/'layout.json').read_bytes()).hexdigest(),'files':files,
         'furniture_layer_in_integrated_checks':pairs,'all_layer_meshes_present_and_bound_identical':all(i['pass'] for i in pairs)}
    p=ROOT/'qa/export-parity.json'; p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'proof':str(p),'all_roots':all(x['all_product_roots_match'] for x in files),'furniture_layer_parity':out['all_layer_meshes_present_and_bound_identical'],'counts':[x['mesh_node_count'] for x in files]}))
if __name__=='__main__': run()
