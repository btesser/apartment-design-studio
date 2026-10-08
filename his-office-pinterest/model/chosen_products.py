"""Chosen source-grounded material/detail revision, retaining measured architecture."""
import bpy, json
from pathlib import Path
from mathutils import Vector
from primitives import material, product_root, box
from scene_tools import ROOT, resolve_root, descendants
PHOTOS=ROOT.parent/'products/photos'

def set_material(obj, mat):
    if obj.data.users>1: obj.data=obj.data.copy()
    obj.data.materials.clear(); obj.data.materials.append(mat)

def photographed_material(name, filename, roughness=.75):
    m=material(name,(.55,.52,.48),roughness)
    p=m.node_tree.nodes.get('Principled BSDF')
    image=bpy.data.images.load(str(PHOTOS/filename),check_existing=True)
    t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image
    m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    return m

def woven_beige():
    m=material('Pinterest EKENASET Kilanda light beige woven proxy',(.59,.52,.46),.90)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Sheen Weight'].default_value=.15
    # Fine crossed weave is a material proxy; coarse Kelinge corduroy removed.
    tex=m.node_tree.nodes.new('ShaderNodeTexCoord')
    waves=[]
    for axis in ['X','Y']:
        n=m.node_tree.nodes.new('ShaderNodeTexWave');n.wave_type='BANDS';n.bands_direction=axis
        n.inputs['Scale'].default_value=420
        n.inputs['Distortion'].default_value=.18
        m.node_tree.links.new(tex.outputs['Generated'],n.inputs['Vector']);waves.append(n)
    mix=m.node_tree.nodes.new('ShaderNodeMath');mix.operation='MULTIPLY'
    m.node_tree.links.new(waves[0].outputs['Fac'],mix.inputs[0]);m.node_tree.links.new(waves[1].outputs['Fac'],mix.inputs[1])
    bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.00025
    m.node_tree.links.new(mix.outputs[0],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m

def add_products(bpy, collection, recipe):
    layout=json.loads((ROOT/'layout.json').read_text()); items={s['id']:s for s in layout['items']}
    catalog=json.loads((ROOT.parent/'products/selected-products.json').read_text());products={s['id']:s for s in catalog['items']}
    # Physical 700 mm support + the verified 34.925 mm top: no floating top.
    bench=resolve_root('secondary-workspace');top=next(o for o in descendants(bench) if 'black-brown tabletop' in o.name)
    top.location.z=.7+.034925/2;top.dimensions.z=.034925
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active=top;top.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);top.select_set(False)
    bench['modeled_assembled_height_m']=.734925;bench['catalog_nominal_height_m']=.73
    bench['assembly_height_note']='700mm nominal supports plus34.925mm verified top; assembled proxy734.925mm versus catalog730mm rounded nominal.'
    for o in descendants(bench):
        if 'right white ADILS' in o.name:o.name=o.name.replace('right white ADILS','right black ADILS')
    # ALEX official source CAD is the same five-drawer geometry, recoloured to selected black-brown.
    alex=next(o for o in descendants(bench) if 'official alex-drawers' in o.name)
    alex['selected_sku']='604.735.48';alex['finish_note']='Official white ALEX CAD geometry retained; selected black-brown finish is material proxy governed by official selected product photo.'
    mat=woven_beige()
    for o in descendants(resolve_root('visitor-chair')):
        if o.type=='MESH' and any(m and m.name=='EKENASET slate-teal corduroy' for m in o.data.materials):set_material(o,mat)
        elif o.type=='MESH' and any(m and m.name=='EKENASET warm brown wooden frame' for m in o.data.materials):
            set_material(o,material('Pinterest EKENASET dark beech lacquered frame proxy',(.055,.035,.026),.5))
    rugroot=resolve_root('rug');rug=next(o for o in descendants(rugroot) if 'flatwoven textile' in o.name)
    rug.name='rug::actual Impasto Taupe6x9 flatwoven textile'
    set_material(rug,photographed_material('Pinterest actual selected Impasto Taupe6x9 flatwoven photo','ruggable-impasto-taupe-6x9.jpg',.89))
    # UV rotation preserves the source photograph's long direction along world X (9ft).
    u0,v0,u1,v1=.119375,.0495,.883541667,.953833333
    for li,uv in enumerate([(u0,v0),(u0,v1),(u1,v1),(u1,v0)]):rug.data.uv_layers.active.data[li].uv=uv
    rug['source_body_pixel_box']=[286,138,2121,2852];rug['photo_pixels_edited']=False
    rugroot['selected_finish_reference']=str(PHOTOS/'ruggable-impasto-taupe-6x9.jpg')
    spec=items['abstract-scenery-art'];r=product_root(spec,collection);r['id']=spec['id'];r['role']='furniture'
    r['paper_size_m']=[1.0,.7];r['frame_outer_profile_assumed']=True;r['selected_finish_reference']=str(PHOTOS/'art-abstract-scenery-100x70.jpg')
    black=material('Pinterest selected thin black wood art frame',(.011,.01,.009),.48)
    f=.0127;depth=.02286;outerW=1.0254;outerH=.7254
    for name,pos,dims in [
        ('top',(0,0,outerH/2-f/2),(outerW,depth,f)),
        ('bottom',(0,0,-outerH/2+f/2),(outerW,depth,f)),
        ('left',(-outerW/2+f/2,0,0),(f,depth,.7)),
        ('right',(outerW/2-f/2,0,0),(f,depth,.7))]:
        o=box('abstract-scenery-art::black wood frame '+name,pos,dims,black,collection,r,bevel=.0008);o['role']='furniture'
    mesh=bpy.data.meshes.new('Abstract Scenery100x70 full paper mesh')
    mesh.from_pydata([(-.5,-.0107,-.35),(.5,-.0107,-.35),(.5,-.0107,.35),(-.5,-.0107,.35)],[],[(0,1,2,3)]);mesh.update()
    paper=bpy.data.objects.new('abstract-scenery-art::actual full paper print including printed white border',mesh);collection.objects.link(paper);paper.parent=r;paper['role']='furniture'
    uv=mesh.uv_layers.new(name='Source full100x70 paper UV')
    for li,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=p
    mesh.materials.append(photographed_material('Pinterest actual Abstract Scenery No1 selected100x70 paper','art-abstract-scenery-100x70.jpg',.85))
    # Apply catalog identity to each surviving/new hierarchy without touching their geometry.
    for spec in layout['items']:
        root=resolve_root(spec['id']);prod=products.get(spec.get('product_id'),{})
        root['pinterest_layout_id']=spec['id'];root['selected_product_id']=spec.get('product_id','')
        root['canonical_position_blender_m']=spec['position_blender_m']
        if prod:
            root['product_name']=prod.get('name',root.get('product_name',''))
            root['product_url']=prod.get('source_url',root.get('product_url',''))
        if 'selected_color' in spec:root['selected_color']=spec['selected_color']
    bpy.data.collections['His Office — kept products and two Branch task chairs'].name='His Office — exact kept products and one Branch task chair'
