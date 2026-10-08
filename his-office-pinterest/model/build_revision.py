"""Apply a chosen declarative recipe to the frozen scene in this new directory."""
import argparse
import bpy
import importlib.util
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scene_tools import *

parser = argparse.ArgumentParser()
parser.add_argument('--recipe', default=str(ROOT / 'revision-recipe.json'))
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
recipe_path = Path(args.recipe).resolve()
if not recipe_path.is_relative_to(ROOT):
    raise ValueError('Recipe must be in the new model directory.')
recipe = json.loads(recipe_path.read_text())
read_source()
before = protected_signatures()
ids = [canonical_id(o) for o in bpy.data.objects if o.type == 'EMPTY' and canonical_id(o)]
for ident in recipe['remove_product_ids']:
    if ident in KEEPER_IDS:
        raise ValueError(f'Cannot remove owned keeper {ident}')
    resolve_root(ident)
for name in recipe['remove_equipment_roots']:
    obj = bpy.data.objects.get(name)
    if not obj or obj.type != 'EMPTY' or not obj.get('assumption'):
        raise ValueError(f'Not a known generic equipment root: {name}')
for spec in recipe['move_products']:
    resolve_root(spec['id'])
    if 'scale' in spec or 'dimensions' in spec:
        raise ValueError('Moves support rigid position/rotation only. Model new dimensioned products explicitly.')

plan = {'source_sha256': SOURCE_HASH, 'recipe': str(recipe_path),
        'status': recipe['status'], 'product_ids': sorted(ids),
        'requested_removals': recipe['remove_product_ids'],
        'requested_equipment_removals': recipe['remove_equipment_roots'],
        'requested_moves': recipe['move_products'],
        'protected_structure_meshes': len(before['structure_world_geometry']),
        'protected_owned_keeper_ids': sorted(KEEPER_IDS), 'dry_run': args.dry_run}
if args.dry_run:
    assert_protected(before)
    write_json('pipeline-dry-run.json', plan)
    print('DRY_RUN_READY_NO_DESIGN_APPLIED')
    raise SystemExit(0)
if not recipe.get('ready_to_build'):
    raise RuntimeError('Layout/products are still pending; use --dry-run until root gives the chosen design.')

for ident in recipe['remove_product_ids']:
    delete_tree(resolve_root(ident))
for name in recipe['remove_equipment_roots']:
    delete_tree(bpy.data.objects[name])

equipment_for = {'uplift-main-desk': 'uplift-main-desk::generic equipment assumption',
                 'secondary-workspace': 'secondary-workspace::generic equipment assumption'}
for spec in recipe['move_products']:
    obj = resolve_root(spec['id'])
    old_pose = obj.matrix_world.copy()
    equipment = bpy.data.objects.get(equipment_for.get(spec['id'], ''))
    equipment_pose = equipment.matrix_world.copy() if equipment else None
    obj.location = spec['position_blender_m']
    obj.rotation_euler.z = math.radians(spec.get('rotation_z_deg', 0))
    bpy.context.view_layer.update()
    if equipment:
        equipment.matrix_world = obj.matrix_world @ old_pose.inverted() @ equipment_pose

for update in recipe.get('update_product_metadata', []):
    ident = update['id']
    if ident in KEEPER_IDS:
        raise ValueError('Owned product identity and finish remain source-confirmed.')
    root = resolve_root(ident)
    for key in ['product_name', 'product_url', 'dimension_source', 'dimension_confidence',
                'selected_finish_reference', 'function']:
        if key in update:
            root[key] = update[key]

# Material changes are private to the named product. Global shared-material
# recoloring would accidentally change owned finishes or neighbouring fixtures.
for change in recipe['material_changes']:
    ident = change['product_id']
    if ident in KEEPER_IDS:
        raise ValueError(f'Owned keeper finish is protected: {ident}')
    obj = resolve_root(ident)
    copies = {}
    for child in descendants(obj):
        if child.type != 'MESH':
            continue
        for slot in child.material_slots:
            old = slot.material
            if not old or old.name != change['source_material']:
                continue
            if old.name not in copies:
                private = old.copy()
                private.name = f'Pinterest {ident} — {change.get("new_name", old.name)}'
                p = private.node_tree.nodes.get('Principled BSDF')
                if change.get('disconnect_base_color_texture'):
                    for link in list(p.inputs['Base Color'].links):
                        private.node_tree.links.remove(link)
                for name, value in change.get('principled', {}).items():
                    p.inputs[name].default_value = value
                if change.get('base_color_texture'):
                    image = bpy.data.images.load(str(Path(change['base_color_texture']).resolve()), check_existing=True)
                    tex = private.node_tree.nodes.new('ShaderNodeTexImage'); tex.image = image
                    private.node_tree.links.new(tex.outputs['Color'], p.inputs['Base Color'])
                copies[old.name] = private
            if child.data.users > 1:
                child.data = child.data.copy()
            slot.material = copies[old.name]

new_collection = bpy.data.collections.new('07 Pinterest chosen new products')
bpy.context.scene.collection.children.link(new_collection)
module = recipe.get('new_product_module')
if module:
    path = (ROOT / module).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('New product builder must be in this directory.')
    spec = importlib.util.spec_from_file_location('chosen_products', path)
    loaded = importlib.util.module_from_spec(spec); spec.loader.exec_module(loaded)
    loaded.add_products(bpy, new_collection, recipe)

for item in recipe['camera_changes']:
    camera = bpy.data.objects[item['name']]
    camera.location = item['eye_blender_m']
    camera.rotation_euler = (Vector(item['target_blender_m'])-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens = item['lens_mm']

s = bpy.context.scene; r = recipe['render']
s.render.engine = 'CYCLES'; s.render.resolution_x, s.render.resolution_y = r['resolution']
s.render.resolution_percentage = 100; s.cycles.samples = r['maximum_samples']
s.cycles.use_adaptive_sampling = True; s.cycles.adaptive_threshold = r['adaptive_threshold']
s.cycles.adaptive_min_samples = r['minimum_samples']; s.cycles.use_denoising = False
s.view_settings.exposure = r['exposure']
s['design_revision'] = recipe['design']
bpy.context.view_layer.update()
assert_protected(before)
image_checks = active_image_checks()

structure = {o for name in STRUCTURE_COLLECTIONS for o in bpy.data.collections[name].all_objects}
furniture = {o for o in bpy.data.objects if o.type in {'MESH','EMPTY'} and o.get('role') == 'furniture'}
# Include every hierarchy parent so extras and identity survive export.
for obj in list(furniture):
    parent = obj.parent
    while parent:
        furniture.add(parent); parent = parent.parent
doors=set(bpy.data.collections['02b Existing door leaves — closed observed state'].all_objects)
export_selected(ROOT / 'his-office-pinterest-shell.glb', structure-doors)
export_selected(ROOT / 'his-office-pinterest-door-leaves.glb', doors)
export_selected(ROOT / 'his-office-pinterest-furniture.glb', furniture)
export_selected(ROOT / 'his-office-pinterest-design.glb', structure | furniture)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'his-office-pinterest-design.blend'))
assert_protected(before)
write_json('revision-build-report.json', {**plan, 'dry_run': False, 'images': image_checks,
           'protected_geometry_pass': True, 'prior_source_unchanged': file_hash(SOURCE) == SOURCE_HASH,
           'new_product_objects': len(new_collection.all_objects)})
print('CHOSEN_PINTEREST_REVISION_READY')
