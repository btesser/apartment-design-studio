"""Read-only texture orientation, panel envelope and selected workwall finish."""
import bpy
import hashlib
import json
import sys
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:];ROOT=Path(args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
SOURCE=ROOT/'model/his-office-design.blend'
REF=Path('/workspace/his-office-pinterest/variants/pipeline/variant-reference-audit.json')
references=json.loads(REF.read_text());layout=json.loads((ROOT/'model/layout.json').read_text())
specs={i['id']:i for i in layout['items']};bpy.ops.wm.open_mainfile(filepath=str(SOURCE))


def owns(o,identifier):
    while o:
        if (o.get('canonical_layout_id') or o.get('id'))==identifier:return True
        o=o.parent
    return False


def image_nodes(o):
    out=[]
    for m in o.data.materials:
        if not m or not m.use_nodes:continue
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:
                im=n.image
                out.append({'material':m.name,'image':im.name,'pixel_dimensions':list(im.size),
                            'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest() if im.packed_file else None,
                            'colorspace':im.colorspace_settings.name,'extension':n.extension})
    return out


def loops(o):
    uv=o.data.uv_layers.active
    return [{'position_blender_m':list(o.matrix_world@o.data.vertices[l.vertex_index].co),
             'uv':list(uv.data[l.index].uv)} for l in o.data.loops] if uv else []


texture_results={}
for key,ident in [('rug','rug'),('art','richmond-art')]:
    ref=references[key];expected=ref['sha256'];matches=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or not owns(o,ident):continue
        nodes=image_nodes(o)
        if any(n['packed_sha256']==expected for n in nodes):matches.append((o,nodes))
    if len(matches)!=1:
        texture_results[key]={'pass':False,'matching_source_image_mesh_count':len(matches)};continue
    o,nodes=matches[0];data=loops(o);xyz=[p['position_blender_m'] for p in data]
    bounds=[[min(p[k] for p in xyz) for k in range(3)],[max(p[k] for p in xyz) for k in range(3)]]
    if key=='rug':
        corners=[(bounds[0][0],bounds[0][1]),(bounds[1][0],bounds[0][1]),
                 (bounds[1][0],bounds[1][1]),(bounds[0][0],bounds[1][1])]
        expected_uv=ref['quad_UV_same_order_long_photo_axis_along_X']
        observed=[min(data,key=lambda p:(p['position_blender_m'][0]-x)**2+(p['position_blender_m'][1]-y)**2)['uv'] for x,y in corners]
        error=max(abs(a-b) for x,y in zip(observed,expected_uv) for a,b in zip(x,y))
        dims=[bounds[1][0]-bounds[0][0],bounds[1][1]-bounds[0][1]]
        fit=max(abs(a-b) for a,b in zip(dims,specs[ident]['external_dimensions_m'][:2]))<2e-6
    else:
        # Full native horizontal paper: left→u0/right→u1, bottom→v0/top→v1.
        corners=[(bounds[0][0],bounds[0][2]),(bounds[1][0],bounds[0][2]),
                 (bounds[1][0],bounds[1][2]),(bounds[0][0],bounds[1][2])]
        expected_uv=[[0,0],[1,0],[1,1],[0,1]]
        observed=[min(data,key=lambda p:(p['position_blender_m'][0]-x)**2+(p['position_blender_m'][2]-z)**2)['uv'] for x,z in corners]
        error=max(abs(a-b) for x,y in zip(observed,expected_uv) for a,b in zip(x,y))
        dims=[bounds[1][0]-bounds[0][0],bounds[1][2]-bounds[0][2]]
        fit=max(abs(a-b) for a,b in zip(dims,[1,.7]))<2e-6
    texture_results[key]={'mesh':o.name,'source_sha256':expected,'image_nodes':nodes,'surface_dimensions_m':dims,
                          'expected_corner_uv':expected_uv,'actual_corner_uv':observed,'max_uv_error':error,
                          'dimensions_match':fit,'pass':error<2e-6 and fit and all(n['colorspace']=='sRGB' for n in nodes if n['packed_sha256']==expected)}

panels=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('WoodUpp panel')]
panel_data={'mesh_count':len(panels),'expected_in_variant':ROOT.name=='b-charcoal-slat'}
if panels:
    pts=[o.matrix_world@v.co for o in panels for v in o.data.vertices]
    bounds=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]]
    top=next(o for o in bpy.context.scene.objects if o.type=='MESH' and owns(o,'secondary-workspace') and 'tabletop' in o.name)
    bench_back=max((top.matrix_world@v.co).y for v in top.data.vertices)
    artpts=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and owns(o,'richmond-art') for v in o.data.vertices]
    artback=max(v.y for v in artpts)
    panel_data.update(bounds_blender_m=bounds,dimensions_m=[bounds[1][k]-bounds[0][k] for k in range(3)],
                      ceiling_band_m=layout['room_ceiling_z_m']-bounds[1][2],
                      front_to_bench_rear_gap_m=bounds[0][1]-bench_back,
                      front_to_art_back_gap_m=bounds[0][1]-artback)
    panel_data['pass']=abs((bounds[1][2]-bounds[0][2])-2.4)<2e-6 and abs((bounds[1][1]-bounds[0][1])-.022)<2e-6 and bounds[0][1]>bench_back and bounds[0][1]>artback
else:panel_data['pass']=ROOT.name=='c-ink-studio'
workwall=bpy.data.objects['his-office wall4 segment']
materials=[]
for m in workwall.data.materials:
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m and m.use_nodes else None
    materials.append({'name':m.name if m else None,'base_color':list(p.inputs['Base Color'].default_value) if p else None})
out={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'layout_sha256':hashlib.sha256((ROOT/'model/layout.json').read_bytes()).hexdigest(),'reference_audit_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),
     'method':'Untouched packed source-photo hash plus actual native UV/metric surface corner mapping; observed panel vertex bounds/contact gaps. No model/image modified.',
     'textures':texture_results,'all_selected_texture_orientations_pass':all(v['pass'] for v in texture_results.values()),
     'panels':panel_data,'workwall_materials':materials,'selected_workwall_finish':layout.get('workwall_finish'),
     'limits':['Frame outside profile is an assumed presentation envelope; paper100×70cm is retailer verified.',
               'Panel rear fastening, actual site baseboard, adhesives and acoustic performance are not modeled; no workwall baseboard appears in the recorded geometry.',
               'One-millimetre mounting/contact gaps and UV precision refer to authored model, not site tolerances or installation clearance.',
               'Digital paint chips/photo colors under renderer lighting are appearance references, not calibrated installed albedo.']}
(QA/'texture-panel-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'texture_pass':out['all_selected_texture_orientations_pass'],'textures':texture_results,'panels':panel_data}))
