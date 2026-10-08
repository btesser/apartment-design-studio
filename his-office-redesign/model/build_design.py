"""Build the chosen fresh His-office design from one canonical placement record."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path('/workspace/his-office-redesign/model')
PRODUCTS = Path('/workspace/his-office-redesign/products/candidates')
sys.path.insert(0, str(ROOT))
from primitives import material, product_root, box, cylinder, rod, bounds_world, export_glb

layout = json.loads((ROOT / 'layout.json').read_text())
by_id = {i['id']: i for i in layout['items']}
catalog = {i['id']: i for i in json.loads((PRODUCTS / 'selected-products.json').read_text())['items']}
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'his-office-shell.blend'))
s = bpy.context.scene
proposal = bpy.data.collections['05 New proposal — pending selected layout']
proposal.name = '05 Chosen new furniture and sourced textiles/art'
provisional = bpy.data.collections.new('06 Provisional contents of unrecorded closet')
s.collection.children.link(provisional)
with bpy.data.libraries.load(str(ROOT / 'keepers-and-taskchairs.blend'), link=False) as (src, dst):
    dst.collections = [n for n in src.collections if n == 'His Office — kept products and two Branch task chairs']
for c in dst.collections:
    if c:
        s.collection.children.link(c)
keepers = dst.collections[0]
if not keepers:
    raise RuntimeError('Kept products collection is missing.')
keeper_ids = {'kept-uplift-desk':'uplift-main-desk','kept-honeywell-02e-pro':'honeywell-lamp',
              'kept-muttros-cat-tree':'muttros-cat-tree','branch-pro-task-chair-1':'branch-primary',
              'branch-pro-task-chair-2':'branch-secondary'}
for source_id, canonical_id in keeper_ids.items():
    p = bpy.data.objects[source_id]
    p.location = by_id[canonical_id]['position_blender_m']
    p['canonical_layout_id'] = canonical_id
    p['role'] = 'furniture'

white = material('New matte white storage/legs', (.82, .83, .79), .62)
black = material('New black equipment/frame', (.012, .015, .017), .48)
dark_top = material('LAGKAPTEN black-brown top', (.035, .026, .019), .58)
warm_wood = material('EKENASET warm brown wooden frame', (.16, .065, .027), .44)
fabric = material('EKENASET slate-teal corduroy', (.043, .097, .108), .85)
wire = material('GREJIG gray powder-coated steel', (.19, .20, .18), .52, .2)
screen = material('Generic monitor screen — functional assumption', (.015, .026, .033), .22)

# Fine directional ribbing represents the photographed corduroy; it changes
# material shading only, not the selected chair's external dimensions.
nodes = fabric.node_tree.nodes
wave = nodes.new('ShaderNodeTexWave')
wave.wave_type = 'BANDS'
wave.bands_direction = 'X'
wave.inputs['Scale'].default_value = 80
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .23
bump.inputs['Distance'].default_value = .0014
fabric.node_tree.links.new(wave.outputs['Fac'], bump.inputs['Height'])
fabric.node_tree.links.new(bump.outputs['Normal'], nodes.get('Principled BSDF').inputs['Normal'])

notes = []
roots = {}


def root_for(id, col=proposal):
    spec = dict(by_id[id])
    cat = catalog.get(spec.get('product_id'), {})
    spec['product_name'] = cat.get('name', spec.get('product_id', id))
    spec['product_url'] = cat.get('source_url', '')
    spec['dimension_source'] = 'Root canonical layout and selected product nominal dimensions'
    p = product_root(spec, col)
    p['role'] = 'furniture'
    p['id'] = id
    if spec.get('hide_in_closed_door_views'):
        p['hide_in_closed_door_views'] = True
        p['placement_confidence'] = spec['placement_confidence']
    roots[id] = p
    return p


def official_asset(asset_id, parent, local_center, target_dims, rotation=0):
    before = set(bpy.data.objects)
    path = PRODUCTS / 'official-3d-assets' / (asset_id + '.glb')
    bpy.ops.import_scene.gltf(filepath=str(path))
    new = set(bpy.data.objects) - before
    meshes = [o for o in new if o.type == 'MESH']
    bpy.context.view_layer.update()
    b = bounds_world(meshes)
    lo, hi = b
    center = Vector(((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, lo[2]))
    scales = [target_dims[i]/(hi[i]-lo[i]) for i in range(3)]
    r = Matrix.Rotation(rotation, 3, 'Z')
    for i, o in enumerate(meshes):
        mw = o.matrix_world.copy()
        me = o.data.copy()
        for v in me.vertices:
            q = mw @ v.co - center
            q = Vector((q.x*scales[0], q.y*scales[1], q.z*scales[2]))
            v.co = r @ q + Vector(local_center)
        clone = bpy.data.objects.new(parent.name + '::official ' + asset_id + f' part{i}', me)
        proposal.objects.link(clone)
        clone.parent = parent
        clone['role'] = 'furniture'
        clone['official_source_asset'] = str(path)
        clone['nominal_envelope_fit_scale'] = scales
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    notes.append({'product': parent.name, 'official_asset': str(path), 'original_bounds_m': b,
                  'small_product_only_fit_scale': scales, 'front': '-Y for ALEX; rotated to+Y for STORKLINTA'})


def texture_mat(name, path):
    m = material(name, (.70, .70, .65), .82)
    tx = m.node_tree.nodes.new('ShaderNodeTexImage')
    tx.image = bpy.data.images.load(str(path), check_existing=True)
    tx.extension = 'EXTEND'
    m.node_tree.links.new(tx.outputs['Color'], m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    return m


def quad(name, coords, uvcoords, mat, parent, col=proposal):
    me = bpy.data.meshes.new(name)
    me.from_pydata(coords, [], [(0, 1, 2, 3)])
    me.update()
    uv = me.uv_layers.new(name='Source photo mapping')
    for i, val in enumerate(uvcoords):
        uv.data[i].uv = val
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.parent = parent
    o['role'] = 'furniture'
    return o


def fit_proxy_children(parent, desired):
    bpy.context.view_layer.update()
    children = [o for o in parent.children if o.type == 'MESH']
    inv = parent.matrix_world.inverted()
    points = [inv @ o.matrix_world @ Vector(c) for o in children for c in o.bound_box]
    lo = [min(q[i] for q in points) for i in range(3)]
    hi = [max(q[i] for q in points) for i in range(3)]
    center = Vector(((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, lo[2]))
    scale = [desired[i]/(hi[i]-lo[i]) for i in range(3)]
    for o in children:
        local = inv @ o.matrix_world
        for v in o.data.vertices:
            q = local @ v.co - center
            v.co = Vector((q.x*scale[0], q.y*scale[1], q.z*scale[2]))
        o.matrix_basis = Matrix.Identity(4)
    parent['dimensioned_proxy_fit'] = scale


# Exact selected configuration: single left ALEX and two right white ADILS.
p = root_for('secondary-workspace')
official_asset('alex-drawers', p, (-.50, 0, 0), (.36, .58, .70))
box('secondary-workspace::black-brown tabletop', (0, 0, .715), (1.4, .60, .03), dark_top, proposal, p, .003)
for y in (-.238, .238):
    cylinder('secondary-workspace::right white ADILS leg', (.60, y, .35), .025, .70, white, proposal, p)
    cylinder('secondary-workspace::black adjustment foot', (.60, y, .009), .025, .018, black, proposal, p)

p = root_for('clothes-dresser')
official_asset('storklinta-low-drawers', p, (0, 0, 0), tuple(by_id['clothes-dresser']['external_dimensions_m']), math.pi)

# EKENASET follows its actual timber frame, separate padded seat/back and dark
# slate-teal corduroy. Detailed joinery remains a dimensioned visual proxy.
p = root_for('visitor-chair')
w, d, h = by_id['visitor-chair']['external_dimensions_m']
seat_w, seat_d, seat_h = .5588, .498475, .45085
box('visitor-chair::padded seat', (0, .06, seat_h-.061), (seat_w, seat_d, .122), fabric, proposal, p, .025)
back = box('visitor-chair::sloping padded back', (0, -.207, .595), (seat_w, .095, .303), fabric, proposal, p, .025)
back.rotation_euler.x = math.radians(12)
for x in (-w/2+.025, w/2-.025):
    rod('visitor-chair::sloping front wooden leg', (x, .31, .013), (x, .20, .616), .020, warm_wood, proposal, p)
    rod('visitor-chair::sloping rear wooden leg', (x, -.355, .013), (x, -.248, .72), .020, warm_wood, proposal, p)
    rod('visitor-chair::rounded wooden arm', (x, -.28, .629), (x, .285, .629), .024, warm_wood, proposal, p)
    rod('visitor-chair::lower side seat support', (x, -.30, .30), (x, .255, .30), .025, warm_wood, proposal, p)
rod('visitor-chair::front timber stretcher', (-w/2+.025, .25, .28), (w/2-.025, .25, .28), .028, warm_wood, proposal, p)
fit_proxy_children(p, (w,d,h))

# Three real wire racks, stacked and rotated so58cm width runs alongY.
for idx in (1, 2, 3):
    id = f'grejig-{idx}'
    p = root_for(id, provisional)
    for x in (-.282, .282):
        for y in (-.127, .127):
            rod(id+'::folded steel leg', (x, y, .003), (x*.96, y*.91, .159), .003, wire, provisional, p, 12)
    for y in (-.127, .127):
        rod(id+'::top long rim', (-.282, y, .159), (.282, y, .159), .003, wire, provisional, p, 12)
    for x in (-.282, .282):
        rod(id+'::top end rim', (x, -.127, .159), (x, .127, .159), .003, wire, provisional, p, 12)
    for x in [(-.25+i*.05) for i in range(11)]:
        rod(id+'::wire lattice across', (x, -.127, .158), (x, .127, .158), .0018, wire, provisional, p, 8)
    for y in (-.085, -.0425, 0, .0425, .085):
        rod(id+'::wire lattice lengthwise', (-.282, y, .158), (.282, y, .158), .0018, wire, provisional, p, 8)

# Provisional floor support is limited to the rack idea, behind the recorded
# closed closet. It is not a modeled or walkable claim about unseen interior size.
floor_support = box('Provisional rack floor support — closet unrecorded', (-3.48, -.54, 1.574),
                    (.36, .67, .002), bpy.data.materials['Reconstructed upper wood'], provisional)
floor_support['role'] = 'inferred_closet_support'
floor_support['hide_in_closed_door_views'] = True
floor_support['confidence'] = 'Unrecorded closet; inferred support for provisional rack placement only'

p = root_for('rug')
L, W, thick = by_id['rug']['external_dimensions_m']
rugmat = texture_mat('Actual selected Inkdrop6x9 textile photograph', by_id['rug']['texture_file'])
box('rug::Standard Pad support', (0, 0, thick/2), (L, W, thick), material('Rug pad edge', (.63, .61, .55), .9), proposal, p)
# UV selects only the rug body from the original photo, with no source-pixel edit.
quad('rug::official6x9 flatwoven textile', [(-L/2,-W/2,thick+.0003),(L/2,-W/2,thick+.0003),
                                         (L/2,W/2,thick+.0003),(-L/2,W/2,thick+.0003)],
     [(.12,.05),(.12,.954),(.883333,.954),(.883333,.05)], rugmat, p)

for id in ('blue-bold-art', 'blue-geometric-art'):
    p = root_for(id)
    paper_w, paper_h = by_id[id]['paper_size_m']
    outer_w, depth, outer_h = by_id[id]['external_dimensions_m']
    face = 1 if id == 'blue-bold-art' else -1
    box(id+'::assumed slim black frame', (0,0,0), (outer_w,depth,outer_h), black, proposal, p, .002)
    y = face*(depth/2+.0005)
    coords = [(-paper_w/2,y,-paper_h/2),(paper_w/2,y,-paper_h/2),
              (paper_w/2,y,paper_h/2),(-paper_w/2,y,paper_h/2)]
    uvs = [(0,0),(1,0),(1,1),(0,1)]
    if face == 1:
        # Viewed from the+Y room side, the local horizontalX direction is reversed.
        uvs = [(1,0),(0,0),(0,1),(1,1)]
        coords = list(reversed(coords))
        uvs = list(reversed(uvs))
    quad(id+'::actual selected print', coords, uvs, texture_mat(id+' official photograph', by_id[id]['texture_file']), p)

# Useful equipment is a declared functional assumption, not extra product choices.
for desk_id, x, y in (('uplift-main-desk', -6.95, .055), ('secondary-workspace', -5.30, .045)):
    h = by_id[desk_id]['external_dimensions_m'][2]
    z = layout['room_floor_z_m'] + h
    ep = bpy.data.objects.new(desk_id+'::generic equipment assumption', None)
    proposal.objects.link(ep)
    ep.location = (x,y,z)
    ep['role'] = 'furniture'
    ep['assumption'] = 'Unselected generic24in monitor and keyboard for usable-work-surface illustration'
    cylinder(ep.name+'::monitor stand', (0,0,.012), .085, .024, black, proposal, ep)
    box(ep.name+'::monitor stem', (0,.015,.08), (.045,.035,.13), black, proposal, ep, .004)
    box(ep.name+'::monitor frame', (0,0,.244), (.54,.038,.325), black, proposal, ep, .006)
    box(ep.name+'::dark display', (0,-.021,.244), (.51,.001,.292), screen, proposal, ep)
    box(ep.name+'::keyboard', (0,-.285,.012), (.41,.135,.024), black, proposal, ep, .004)

# Warm-white painted walls are one material for their full height. Cycles bounce
# lighting avoids carrying the former proxy's sharp gray shading band into images.
plaster = bpy.data.materials['Reconstructed warm plaster']
plaster.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.78,.76,.72,1)
glass = bpy.data.materials.get('Window glass')
if glass:
    pbs = glass.node_tree.nodes.get('Principled BSDF')
    pbs.inputs['Base Color'].default_value = (.91,.95,.98,1)
    pbs.inputs['Transmission Weight'].default_value = 1
    pbs.inputs['Roughness'].default_value = .035

camera_positions = {
    'room-a': ((-3.46,-2.34,3.125),(-6.32,-.40,2.64),24),
    'room-b': ((-7.48,-2.27,3.125),(-4.88,-.48,2.64),24),
    'room-c': ((-4.18,-.35,3.125),(-6.12,-2.22,2.65),24),
    'room-d': ((-7.23,-1.74,3.125),(-4.60,-1.15,2.68),24),
}
cammeta = []
for name,(eye,target,lens) in camera_positions.items():
    cam = bpy.data.objects['CAM '+name]
    cam.location = eye
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens = lens
    cammeta.append({'id':name,'label':name,'filename':f'renders/{name}.jpg','room':'his-office',
                    'eye_blender_m':list(eye),'target_blender_m':list(target),
                    'eye':[eye[0],eye[2],-eye[1]],'target':[target[0],target[2],-target[1]],
                    'lens_mm':lens,'sensor_width_mm':36,'horizontal_FOV_deg':math.degrees(2*math.atan(36/(2*lens))),
                    'coordinate_units':'metres; eye/target GLTF Y-up; explicit native Blender values provided',
                    'render_resolution':[1440,1000],'source_scene':'his-office-design.blend',
                    'view_state':'Observed door leaves closed; fourth view is additional model reference'})
(ROOT/'camera-poses.json').write_text(json.dumps(cammeta,indent=2))

s.render.engine='CYCLES'
s.cycles.samples=64
s.cycles.use_denoising=False  # This CPU Blender build has no OpenImageDenoise.
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.03
s.cycles.adaptive_min_samples=16
s.cycles.max_bounces=8
s.render.resolution_x=1440
s.render.resolution_y=1000
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=96
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.view_settings.exposure=-.5
s.camera=bpy.data.objects['CAM room-a']
s['status']='Chosen fresh warm modern studio, dimensioned source products and measured fixed room features'
s['old_Amy_furniture_count']=0

for c in (proposal,provisional,keepers):
    for o in c.all_objects:
        if o.type=='MESH' and 'role' not in o:
            o['role']='furniture'
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file and im.filepath:
        im.pack()
used_materials={m for o in bpy.data.objects if o.type=='MESH' for m in o.data.materials if m}
active_images={n.image for m in used_materials if m.use_nodes for n in m.node_tree.nodes
               if n.type=='TEX_IMAGE' and n.image}
for im in active_images:
    if min(im.size)<=0 or not im.packed_file:
        raise RuntimeError(f'Active texture lacks pixels/packed bytes: {im.name} {list(im.size)}')

shell=bpy.data.collections['01 Measured room shell']
fixtures=bpy.data.collections['02 Existing fixed feature proxies']
doors=bpy.data.collections['02b Existing door leaves — closed observed state']
export_glb(ROOT/'his-office-furniture.glb',[proposal,provisional,keepers])
export_glb(ROOT/'his-office-design.glb',[shell,fixtures,doors,proposal,provisional,keepers])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'his-office-design.blend'))
bpy.context.view_layer.update()
out=[]
for c in (proposal,provisional,keepers):
    for o in c.all_objects:
        if o.type!='MESH':continue
        out.append({'name':o.name,'parent':o.parent.name if o.parent else None,'world_bounds_m':bounds_world([o]),
                    'role':o.get('role'),'collection':c.name})
(ROOT/'furniture-part-bounds.json').write_text(json.dumps(out,indent=2))
(ROOT/'product-model-notes.json').write_text(json.dumps({'official_assets':notes,
    'textile_pixels_edited':False,'rug_texture_mapping':'Original6x9 photo body selected with UV, source pixels unchanged',
    'provisional_closet':'Interior is unrecorded; racks/support are a conditional fit idea, hidden by closed observed leaf',
    'generic_equipment':'One monitor/keyboard per work surface, not selected purchase products',
    'camera_file':'camera-poses.json','canonical_layout':'layout.json'},indent=2))
print('FRESH_HIS_OFFICE_DESIGN_READY')
