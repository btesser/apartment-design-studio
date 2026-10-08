"""Pure, read-only GLB transform/inventory parity QA."""
import hashlib
import json
import struct
import io
from pathlib import Path
import numpy as np
from PIL import Image

import sys
variant_args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
ROOT=Path(variant_args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
QA.mkdir(parents=True,exist_ok=True)

MODEL=ROOT/'model'
layout=json.loads((MODEL/'layout.json').read_text())
specs={i['id']:i for i in layout['items']}

def read_glb(p):
    b=p.read_bytes(); magic,version,length=struct.unpack_from('<III',b)
    assert magic==0x46546c67 and version==2 and length==len(b)
    pos=12; js=None;binary=None
    while pos<len(b):
        n,k=struct.unpack_from('<II',b,pos); pos+=8
        if k==0x4e4f534a: js=json.loads(b[pos:pos+n])
        if k==0x004e4942: binary=b[pos:pos+n]
        pos+=n
    return js,hashlib.sha256(b).hexdigest(),binary

def matrix(n):
    if 'matrix' in n: return np.array(n['matrix']).reshape(4,4).T
    x,y,z,w=n.get('rotation',[0,0,0,1])
    r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4); m[:3,:3]=r@np.diag(n.get('scale',[1,1,1])); m[:3,3]=n.get('translation',[0,0,0]); return m

def audit(p):
    g,h,binary=read_glb(p); nodes=g['nodes']; worlds={}
    def positions(index):
        ac=g['accessors'][index];view=g['bufferViews'][ac['bufferView']]
        assert ac['componentType']==5126 and ac['type']=='VEC3' and not ac.get('sparse')
        offset=view.get('byteOffset',0)+ac.get('byteOffset',0)
        return np.ndarray((ac['count'],3),dtype='<f4',buffer=binary,offset=offset,strides=(view.get('byteStride',12),4))
    def walk(i,m):
        w=m@matrix(nodes[i]); worlds[i]=w
        for c in nodes[i].get('children',[]): walk(c,w)
    for i in g['scenes'][g.get('scene',0)]['nodes']: walk(i,np.eye(4))
    by_name={n.get('name',''):i for i,n in enumerate(nodes)}
    aliases={n.get('name',''):(n.get('extras',{}).get('canonical_layout_id') or n.get('extras',{}).get('id')) for n in nodes if (n.get('extras',{}).get('canonical_layout_id') or n.get('extras',{}).get('id')) in specs}
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
            actual=positions(pr['attributes']['POSITION'])
            pts=np.column_stack([actual,np.ones(len(actual))])@worlds[i].T
            lo.append(pts[:,:3].min(axis=0)); hi.append(pts[:,:3].max(axis=0))
        lows=np.min(lo,axis=0).tolist(); highs=np.max(hi,axis=0).tolist()
        inventory.append({'name':n.get('name',''),'bounds_gltf_m':[lows,highs],'mesh_index':n['mesh'],
                          'material_names':sorted({g['materials'][pr['material']].get('name','') for pr in g['meshes'][n['mesh']]['primitives'] if 'material' in pr})})
        all_lo.append(lows); all_hi.append(highs)
    source_images=[]
    for im in g.get('images',[]):
        if 'bufferView' not in im:continue
        view=g['bufferViews'][im['bufferView']];data=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
        decoded=Image.open(io.BytesIO(data)).convert('RGB');name=im.get('name','')
        record={**{k:v for k,v in im.items() if k!='bufferView'},'sha256':hashlib.sha256(data).hexdigest(),'pixel_dimensions':list(decoded.size)}
        if name in ['wood-upper','brick-upper']:
            candidates=[Path('/workspace/apartment-model')/(name+'.png')]
            if candidates:
                orig=Image.open(candidates[0]).convert('RGB');pixels=np.asarray(decoded,dtype=float);native_pixels=np.asarray(orig,dtype=float)
                mse=float(np.mean((pixels-native_pixels)**2)) if pixels.shape==native_pixels.shape else None
                record.update(source_file=str(candidates[0]),same_pixel_dimensions=orig.size==decoded.size,mean_squared_8bit_RGB_error=mse,
                              psnr_dB=float(10*np.log10(255*255/mse)) if mse else None,
                              encoding_note='PNG scan-derived texture intentionally re-encoded JPEG95 by existing exporter; not byte-identical. Selected rug/art JPEGs stay exact original bytes.')
        source_images.append(record)
    return {'file':str(p),'sha256':h,'bytes':p.stat().st_size,'mesh_node_count':len(inventory),'material_count':len(g.get('materials',[])),
            'image_count':len(g.get('images',[])),'external_image_uris':[i['uri'] for i in g.get('images',[]) if 'uri' in i],
            'world_bounds_gltf_m':[np.min(all_lo,axis=0).tolist(),np.max(all_hi,axis=0).tolist()],
            'canonical_product_root_checks':roots,'all_product_roots_match':all(c['pass'] for c in roots) and set(c['layout_id'] for c in roots)==set(specs),'mesh_inventory':inventory,
            'materials':g.get('materials',[]),
            'embedded_image_sha256':source_images}

def run():
    files=[audit(MODEL/n) for n in ['his-office-design.glb','his-office-furniture.glb']]
    full={i['name']:i for i in files[0]['mesh_inventory']}; sub=files[1]['mesh_inventory']
    pairs=[]
    for item in sub:
        other=full.get(item['name']); error=float(np.max(np.abs(np.array(item['bounds_gltf_m'])-np.array(other['bounds_gltf_m'])))) if other else None
        pairs.append({'mesh':item['name'],'exists_in_integrated':other is not None,'max_bound_difference_m':error,'pass':error is not None and error<1e-5})
    native=json.loads((QA/'integrated-mesh-checks.json').read_text())
    native_material=json.loads((QA/'material-availability.json').read_text())
    source_hash=hashlib.sha256((MODEL/'his-office-design.blend').read_bytes()).hexdigest()
    exclusions={'Sky outside window':'Presentation background outside measured room; intentionally not exported',
                'Provisional rack floor support — closet unrecorded':'Unrecorded closet infill deliberately excluded; racks remain conditional'}
    native_checks=[]
    for item in native['parts']:
        if item['name'] in exclusions:continue
        other=full.get(item['name'])
        lo,hi=item['bounds'];target=np.array([[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]])
        error=float(np.max(np.abs(target-np.array(other['bounds_gltf_m'])))) if other else None
        native_checks.append({'mesh':item['name'],'group':item['group'],'exists_in_integrated':other is not None,
                              'max_actual_vertex_bound_difference_m':error,'pass':error is not None and error<1e-5})
    material_checks=[];export_mats={m.get('name'):m for m in files[0]['materials']}
    for n in native_material['principled_material_constants']:
        m=export_mats.get(n['name'])
        if m is None:continue # Intentionally nonexported sky/conditional floor material.
        pbr=m.get('pbrMetallicRoughness',{});tests=[]
        for native_key,gltf_key,default in [('base_color','baseColorFactor',[1,1,1,1]),('roughness','roughnessFactor',1),('metallic','metallicFactor',1)]:
            v=n[native_key]
            if not v or v['linked']:continue
            observed=pbr.get(gltf_key,default)
            error=float(np.max(np.abs(np.array(v['value'])-np.array(observed))))
            tests.append({'field':native_key,'error':error,'pass':error<1e-5})
        material_checks.append({'material':n['name'],'constant_fields':tests,'pass':all(x['pass'] for x in tests),
                                'procedural_native_detail_not_fully_encoded_in_core_glTF':n['procedural_nodes']})
    mesh_material_checks=[]
    for item in native_checks:
        other=full.get(item['mesh']);expected=sorted(set(native_material['native_mesh_material_names'].get(item['mesh'],[])))
        actual=other['material_names'] if other else []
        mesh_material_checks.append({'mesh':item['mesh'],'native_names':expected,'gltf_names':actual,'pass':actual==expected})
    original_images={r['packed_sha256'] for r in native_material['records'] if r.get('packed_sha256')}
    selected_images={r['packed_sha256'] for r in native_material['records'] if r.get('packed_sha256') and r['image'] in ['rift-6x9.jpg','dan-hobday-richmond-70x100-official.jpg']}
    exported_images={r['sha256'] for r in files[0]['embedded_image_sha256']}
    out={'coordinate_mapping':'Native Blender [X,Y,Z] maps to exported GLTF [X,Z,-Y], metres, no rescale or mirror.',
         'method':'Read-only GLB v2 scene graph transforms and every actual binary POSITION vertex, compared to native evaluated mesh bounds. Root transforms alone do not establish product geometry inclusion. Transform tolerance checks export parity, not site accuracy.',
         'layout_sha256':hashlib.sha256((MODEL/'layout.json').read_bytes()).hexdigest(),'files':files,
         'furniture_layer_in_integrated_checks':pairs,'all_layer_meshes_present_and_bound_identical':all(i['pass'] for i in pairs),
         'native_proof_source_hash_matches_current':native['source_sha256']==source_hash,'source_sha256':source_hash,
         'intentional_native_mesh_export_exclusions':exclusions,'native_to_export_mesh_checks':native_checks,
         'all_native_product_and_architecture_meshes_present_with_correct_actual_bounds':all(i['pass'] for i in native_checks) and native['source_sha256']==source_hash,
         'native_to_export_material_constant_checks':material_checks,'native_to_export_mesh_material_checks':mesh_material_checks,
         'all_exported_material_constants_and_assignments_match':all(x['pass'] for x in material_checks+mesh_material_checks) and native_material['source_sha256']==source_hash,
         'all_packed_original_image_bytes_preserved_in_integrated_export':original_images==exported_images,
         'all_selected_rug_and_art_original_JPEG_bytes_preserved':selected_images.issubset(exported_images),
         'scan_texture_reencoding_checks':[{k:v for k,v in im.items()} for im in files[0]['embedded_image_sha256'] if im.get('encoding_note')],
         'export_material_limits':['Procedural bump/noise detail is not fully represented by coreglTF; constants/material assignment and packed photographic bytes are compared, final visual appearance reviewed separately.']}
    p=QA/'export-parity.json'; p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'proof':str(p),'all_roots':all(x['all_product_roots_match'] for x in files),'furniture_layer_parity':out['all_layer_meshes_present_and_bound_identical'],
                      'native_mesh_inclusion_and_bounds':out['all_native_product_and_architecture_meshes_present_with_correct_actual_bounds'],
                      'native_missing_or_different':[i for i in native_checks if not i['pass']],'counts':[x['mesh_node_count'] for x in files]}))
if __name__=='__main__': run()
