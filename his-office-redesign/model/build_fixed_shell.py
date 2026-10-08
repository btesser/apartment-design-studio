"""Correct only newly audited existing features in the unfurnished His-room copy."""
import bpy
import json
import sys
import math
from pathlib import Path

ROOT = Path('/workspace/his-office-redesign/model')
sys.path.insert(0, str(ROOT))
from primitives import box, cylinder, material, export_glb

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'unfurnished-source-shell.blend'))
s = bpy.context.scene
shell = bpy.data.collections['01 Measured room shell']
fixtures = bpy.data.collections['02 Existing fixed feature proxies']
doors = bpy.data.collections.new('02b Existing door leaves — closed observed state')
s.collection.children.link(doors)
white = bpy.data.materials.get('Fixture porcelain') or material('Existing white painted joinery', (.83, .84, .80))
plaster = bpy.data.materials['Reconstructed warm plaster']
metal = material('Existing silver hardware', (.42, .45, .47), .26, .82)
brass = material('Existing exterior brass hardware', (.48, .32, .11), .28, .75)
iron = material('Existing dark cast-iron radiator', (.055, .061, .056), .65, .35)

manifest = {
    'source': '/workspace/apartment/scan.blend',
    'coordinate_frame': 'Native metric Blender Z-up; no normalization or scaling',
    'room_floor_z_m': 1.575, 'room_ceiling_z_m': 4.595,
    'method': 'Room-only source extraction plus calibrated raw orthographic fixed-feature corrections',
    'existing_feature_forms': 'Review proxies; fixture locations are observed, fine profile/hardware dimensions are approximate',
    'features': [],
}


def annotate(o, feature, confidence, role='fixed_fixture'):
    o['role'] = role
    o['room'] = 'his-office'
    o['feature'] = feature
    o['evidence'] = 'Calibrated raw Polycam orthographic audit, 8 October 2026'
    o['confidence'] = confidence
    return o


def fixed_box(name, center, size, mat=white, col=fixtures, feature=None, confidence='Observed placement; proxy form approximate', bevel=.003):
    return annotate(box(name, center, size, mat, col, bevel=bevel), feature or name, confidence,
                    'door_leaf' if col == doors else 'fixed_fixture')


def wall_segment(name, x, ya, yb, lo, hi):
    if yb - ya < .001 or hi - lo < .001:
        return
    o = box(name, (x, (ya + yb) / 2, (lo + hi) / 2), (.10, yb - ya, hi - lo), plaster, shell)
    annotate(o, name, 'Generalized recorded wall; opening changed to new raw-audit frame', 'architecture')


def replace_wall(prefix, x, ya, yb, aperture, top):
    for o in list(shell.objects):
        if o.name.startswith(prefix):
            bpy.data.objects.remove(o, do_unlink=True)
    aa, ab = aperture
    wall_segment(prefix + ' — lower-Y side', x, ya, aa, 1.535, 4.635)
    wall_segment(prefix + ' — upper-Y side', x, ab, yb, 1.535, 4.635)
    wall_segment(prefix + ' — head continuation', x, aa, ab, top, 4.635)
    wall_segment(prefix + ' — below floor continuation', x, aa, ab, 1.535, 1.575)


def frame(name, x, ya, yb, bottom, top, front_axis=0, trim=.043, depth=.10):
    for y in (ya, yb):
        fixed_box(name + ' jamb', (x, y, (bottom + top) / 2), (depth, trim, top - bottom + trim),
                  feature=name)
    fixed_box(name + ' header', (x, (ya + yb) / 2, top), (depth, yb - ya + trim, trim), feature=name)


def replace_exterior_wall():
    for o in list(shell.objects):
        if o.name.startswith('his-office wall5'):
            bpy.data.objects.remove(o, do_unlink=True)
    apertures = [(-2.55, -1.64, 1.575, 3.64), (-.96, -.14, 2.53, 4.37)]
    edges = sorted({-2.79, .31, *(v for a in apertures for v in a[:2])})
    for i, (ya, yb) in enumerate(zip(edges, edges[1:])):
        mid = (ya + yb) / 2
        opening = next((a for a in apertures if a[0] < mid < a[1]), None)
        if opening is None:
            wall_segment(f'his-office wall5 corrected solid {i}', -7.98, ya, yb, 1.535, 4.635)
        else:
            wall_segment(f'his-office wall5 corrected bottom {i}', -7.98, ya, yb, 1.535, opening[2])
            wall_segment(f'his-office wall5 corrected head {i}', -7.98, ya, yb, opening[3], 4.635)


# Calibrated raw geometry corrected the previous oversized/low window proxy.
replace_exterior_wall()
for o in list(fixtures.objects):
    if o.name.startswith('Window '):
        bpy.data.objects.remove(o, do_unlink=True)
glass = bpy.data.materials.get('Window glass') or material('Existing clear glass proxy', (.46, .62, .68), .14)
fixed_box('Observed single-window glazing', (-7.98, -.56, 3.45), (.012, .72, 1.79), glass,
          feature='single exterior window', confidence='Calibrated raw clear/glass width ~0.72 m; precise sash profile approximate')
for y in (-.96, -.14):
    fixed_box('Observed single-window vertical trim', (-7.98, y, 3.45), (.08, .043, 1.84),
              feature='single exterior window', confidence='Calibrated raw outer frame ±0.03–0.05 m')
for z in (2.53, 3.45, 4.37):
    fixed_box('Observed single-window horizontal trim', (-7.98, -.55, z), (.08, .82, .043),
              feature='single exterior window', confidence='Outer sill/header measured; center sash rail approximately interpreted')
fixed_box('Observed single-window projecting sill', (-7.94, -.56, 2.53), (.16, .90, .035),
          feature='single exterior window', confidence='Raw sill widens to Y[-1.01,-0.11]; depth approximate')
fixed_box('Observed single-window sill apron', (-7.95, -.56, 2.485), (.085, .90, .05),
          feature='single exterior window', confidence='Calibrated decorative sill/apron extends down to Z~2.46')
sky = bpy.data.objects.get('Sky outside window')
if sky:
    sky.location.y = -.55
    sky.location.z = 3.45
    sky.dimensions.y = 1.06
    sky.dimensions.z = 2.05
    sky['role'] = 'presentation_only'
manifest['features'].append({'id': 'single-exterior-window', 'wall_x_m': -7.98,
                            'outer_frame_y_m': [-.96, -.14], 'outer_frame_z_m': [2.53, 4.37],
                            'clear_glass_y_m': [-.92, -.20], 'sill_y_m': [-1.01, -.11],
                            'confidence': 'New calibrated raw ortho ±0.03–0.05 m; sash depth/profile approximate',
                            'corrects_old_proxy': 'Old window width and elevation were not independently grounded'})


# Closets were incorrectly represented by a solid wall in the earlier clean proxy.
replace_wall('his-office wall3', -3.78, -1.35, .31, (-.88, -.16), 4.56)
frame('Existing closet frame', -3.81, -.88, -.16, 1.60, 3.65, depth=.18)
fixed_box('Existing closet transom', (-3.81, -.52, 3.675), (.18, .72, .05), feature='closet')
frame('Existing overhead cupboard frame', -3.865, -.88, -.16, 3.70, 4.56, depth=.07)
fixed_box('Existing full-height closet leaf', (-3.855, -.52, (1.61 + 3.64) / 2), (.038, .62, 2.03), col=doors,
          feature='closet', confidence='Raw frame/leaf approximate ±0.03–0.06 m; closed leaf observed')
fixed_box('Existing overhead cupboard panel', (-3.855, -.52, (3.70 + 4.56) / 2), (.03, .62, .86),
          feature='overhead cupboard', confidence='Raw frame/panel approximate ±0.03–0.06 m')
annotate(cylinder('Existing closet metal knob', (-3.905, -.80, 2.53), .021, .035, metal, doors),
         'closet', 'Knob side observed; shape/size approximate', 'door_leaf')
bpy.data.objects['Existing closet metal knob'].rotation_euler.y = 1.57079632679
fixed_box('Existing cupboard metal latch', (-3.891, -.80, 3.82), (.025, .035, .018), metal,
          feature='overhead cupboard', confidence='Latch side observed; shape/size approximate')
manifest['features'].append({'id': 'closet-cupboard', 'wall_x_m': -3.78,
                            'door_leaf_bounds_m': [-3.874, -3.836, -.83, -.21, 1.61, 3.64],
                            'cupboard_panel_bounds_m': [-3.870, -3.840, -.83, -.21, 3.70, 4.56],
                            'outer_frame_y_m': [-.88, -.16],
                            'confidence': 'Calibrated raw scan ±0.03–0.06 m; fine profile approximate'})

# Living door frame was ~0.28 m too narrow in the old proxy. The scan's closed
# flat white leaf and lever are separated so viewer access can toggle the leaf.
replace_wall('his-office wall1', -3.08, -2.79, -1.35, (-2.73, -1.65), 3.65)
frame('Existing living-entry frame', -3.08, -2.73, -1.65, 1.60, 3.65)
fixed_box('Existing living-entry flat white leaf', (-3.08, -2.19, (1.61 + 3.64) / 2), (.04, .99, 2.03), col=doors,
          feature='living-entry door', confidence='Closed white leaf observed; human holes obscure part; exact hinge unverified')
fixed_box('Existing living-entry silver lever', (-3.13, -1.74, 2.52), (.035, .095, .016), metal, doors,
          feature='living-entry door', confidence='Lever side observed; hardware form approximate')
manifest['features'].append({'id': 'living-entry-door', 'frame_wall_x_m': -3.08,
                            'frame_y_m': [-2.73, -1.65], 'frame_z_m': [1.60, 3.65],
                            'observed_state': 'closed', 'hinge_side': 'likely -Y; not verified',
                            'viewer_note': 'Opening is fixed. Hiding/opening the separate leaf is an inferred viewing state.'})

# Exterior door is white six-panel joinery with brass hardware, not a black void.
frame('Existing exterior-door frame', -7.98, -2.55, -1.64, 1.61, 3.64)
fixed_box('Existing exterior-door six-panel leaf', (-7.976, -2.095, (1.61 + 3.64) / 2), (.04, .83, 2.03), col=doors,
          feature='exterior door', confidence='Six-panel white leaf/brass hardware observed; profiles approximate')
for z0, z1 in ((1.78, 2.32), (2.44, 3.06), (3.17, 3.49)):
    for y in (-2.30, -1.89):
        fixed_box('Existing exterior-door raised panel', (-7.950, y, (z0 + z1) / 2), (.012, .30, z1 - z0), col=doors,
                  feature='exterior door', confidence='Six-panel pattern observed; individual rail proportions illustrative')
for name, z in (('knob', 2.50), ('deadbolt', 2.70)):
    o = cylinder('Existing exterior-door brass ' + name, (-7.931, -1.735, z), .023, .03, brass, doors)
    o.rotation_euler.y = 1.57079632679
    annotate(o, 'exterior door', 'Brass hardware and +Y side observed; dimensions approximate', 'door_leaf')
manifest['features'].append({'id': 'exterior-door', 'frame_wall_x_m': -7.98,
                            'frame_y_m': [-2.55, -1.64], 'frame_z_m': [1.61, 3.64],
                            'observed_state': 'closed', 'finish': 'white six-panel leaf, brass hardware'})

# Compact old radiator is in the rear brick corner, beside the exterior door.
# Section fins preserve the audited envelope; fin count is an illustrative proxy.
for i in range(9):
    x = -7.935 + i * (.48 / 8)
    fixed_box('Existing cast-iron radiator section', (x, -2.63, 1.965), (.042, .29, .63), iron,
              feature='radiator', confidence='Location high confidence; envelope ±0.05–0.08 m; fin count approximate', bevel=.015)
for x in (-7.89, -7.50):
    fixed_box('Existing radiator foot', (x, -2.64, 1.635), (.042, .22, .05), iron, feature='radiator')
for z in (1.76, 2.17):
    fixed_box('Existing radiator horizontal connection', (-7.695, -2.63, z), (.51, .05, .05), iron, feature='radiator')
manifest['features'].append({'id': 'radiator', 'audited_bounds_m': [-7.96, -7.43, -2.79, -2.47, 1.61, 2.30],
                            'confidence': 'Location high; envelope ±0.05–0.08 m; fins/profiles approximate',
                            'keepout_note': 'Do not put furniture or cat-tree structure directly against heater/door corner.'})

# Existing shallow white built-in shelf nook, not part of the prior Amy proposal.
fixed_box('Existing built-in shelf white back', (-3.52, -2.735, 2.95), (.82, .012, 1.48),
          feature='entry-side built-in shelving', confidence='White shelf nook observed; missing scan support means exact trim is unverified')
for z in (2.33, 2.61, 2.80, 3.05, 3.24, 3.60):
    fixed_box('Existing built-in shelf board', (-3.52, -2.665, z), (.82, .19, .025),
              feature='entry-side built-in shelving', confidence='Board heights observed approximately; count/profile uncertain')
manifest['features'].append({'id': 'entry-side-built-in-shelves',
                            'observed_bounds_m': [-3.95, -3.08, -2.89, -2.58, 2.30, 3.62],
                            'confidence': 'Scan imperfect; shelf count and detailed profiles approximate',
                            'board_z_m': [2.33, 2.61, 2.80, 3.05, 3.24, 3.60]})

# Preserve the actual rear white pipe instead of flattening the corner.
o = cylinder('Existing rear vertical white pipe', (-7.91, .24, 3.0975), .05, 2.995, white, fixtures)
annotate(o, 'rear pipe', 'Observed location; diameter and merged ceiling end approximate')
manifest['features'].append({'id': 'rear-pipe', 'center_xy_m': [-7.91, .24],
                            'diameter_proxy_m': .10, 'z_m': [1.60, 4.595]})

# The old rectangular white mantel was not supported by the raw scan. Replace it
# with the actual continuous brick chimney projection and recessed arched infill.
for o in list(fixtures.objects):
    if o.name.startswith('HIS '):
        bpy.data.objects.remove(o, do_unlink=True)
brick = bpy.data.materials['Reconstructed exposed brick']
brick_wall = bpy.data.objects['his-office wall0 segment']
brick_wall.location.y = -2.887  # interior observed adjacent brick face=-2.837
brick_wall['confidence'] = 'Raw adjacent brick surface face measured Y~ -2.837; nominal outline is unchanged'


def metric_uv(o, is_brick=False):
    if o.type != 'MESH':
        return
    if not o.data.uv_layers:
        o.data.uv_layers.new(name='MetricProjection')
    uv = o.data.uv_layers.active
    for p in o.data.polygons:
        for li in p.loop_indices:
            q = o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv = (q.x * .714, q.z * 1.667) if is_brick else (q.x * .55, q.y * .55)


def arch_prism(name, ymin, ymax, mat, col):
    xc, half, bottom, top = -5.315, .335, 1.62, 2.48
    spring = top - half
    outline = [(xc-half, bottom), (xc+half, bottom)]
    outline += [(xc + half * math.cos(a * math.pi / 24), spring + half * math.sin(a * math.pi / 24))
                for a in range(25)]
    n = len(outline)
    v = [(x, y, z) for y in (ymin, ymax) for x, z in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], faces)
    me.update()
    # A closed cutter must have outward-facing normals. The outline is drawn
    # in X/Z; its initial cap ordering otherwise inverts the Boolean volume.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    if mat:
        me.materials.append(mat)
    return o


chimney = box('Observed brick chimney projection', (-5.29, (-2.86-2.722)/2, (1.575+4.595)/2),
              (1.62, .138, 3.02), brick, shell)
bpy.context.view_layer.update()
metric_uv(chimney, True)
cut = arch_prism('Temporary measured closed arch cut', -2.98, -2.60, None, shell)
mod = chimney.modifiers.new('Existing arched infill recess', 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
mod.object = cut
bpy.context.view_layer.objects.active = chimney
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cut, do_unlink=True)
annotate(chimney, 'closed fireplace', 'Full-height projection observed; generalized broad edges; faceY=-2.722', 'architecture')
infill = arch_prism('Observed recessed white arched fireplace infill', -2.845, -2.835, white, fixtures)
annotate(infill, 'closed fireplace', 'Recessed white infill surface observed atY=-2.835; arch profile approximate')

# A narrow floor continuation bridges the nominal floor-outline line and the
# measured local brick surface. The canonical generalized polygon is preserved.
strip = box('Local floor continuation to observed brick face', (-5.53, (-2.837-2.79)/2, 1.574),
            (4.90, .047, .002), bpy.data.materials['Reconstructed upper wood'], shell)
bpy.context.view_layer.update()
metric_uv(strip)
annotate(strip, 'local floor continuation', '4.7 cm continuation to raw wall face; nominal room polygon unchanged', 'architecture')
manifest['features'].append({'id': 'closed-fireplace', 'broad_chimney_x_m': [-6.10, -4.48],
                            'adjacent_brick_face_y_m': -2.837, 'chimney_face_y_m': -2.722,
                            'infill_face_y_m': -2.835, 'arch_bounds_xz_m': [-5.65, -4.98, 1.62, 2.48],
                            'big_white_rectangular_mantel_removed': True,
                            'broad_hearth_keepout_xy_m': [-6.10, -4.48, -2.94, -2.48],
                            'keepout_is_metadata_not_solid_hearth': True,
                            'confidence': 'Plane positions measured from actual support; generalized arch/edges remain approximate'})

for name, y, z, width, height in (('thermostat', -1.455, 3.17, .11, .11), ('small wall control', -1.455, 2.84, .06, .09)):
    fixed_box('Existing entry ' + name, (-3.139, y, z), (.018, width, height),
              feature='entry controls', confidence='Observed approximate position; hardware detail unverified')

for o in shell.objects:
    o['role'] = 'architecture'
    o['room'] = 'his-office'
for o in fixtures.objects:
    if 'role' not in o:
        o['role'] = 'fixed_fixture'
for o in doors.objects:
    o['role'] = 'door_leaf'

s['status'] = 'Unfurnished room shell with newly observed fixed features; selected furniture layout pending'
s['original_room_scale_preserved'] = True
manifest['layers'] = {'architecture': shell.name, 'fixed_fixtures': fixtures.name, 'door_leaves': doors.name}
manifest['furniture_count'] = 0
(ROOT / 'fixed-feature-manifest.json').write_text(json.dumps(manifest, indent=2))
export_glb(ROOT / 'his-office-shell.glb', [shell, fixtures])
export_glb(ROOT / 'his-office-door-leaves.glb', [doors])
export_glb(ROOT / 'his-office-unfurnished.glb', [shell, fixtures, doors])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'his-office-shell.blend'))
print('AUDITED_HIS_ONLY_SHELL_READY')
