"""Prepare five-reference inputs only after final models, matching renders and boards pass provenance checks.

Importing this module does not write files or freeze inputs. Root runs it after canonical QA.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parent

COMMON = '''Create one realistic finished interior photograph from the supplied measured 3D apartment office. Reference 1 is the exact TARGET composition: preserve its camera, crop, perspective, room proportions, ceiling height, opening locations, furniture footprints and facing, and natural occlusion. References 2 and 3 are companion views of the SAME frozen model and establish geometry. References 4 and 5 contain original real supplier/retailer product photographs and selected color/material references. Use those exact product appearances; never copy their showroom architecture, background props, extra equipment or placements. Do not put boards or labels in the photograph.

Preserve the original oak-tone plank floor, red-brown brick wall, tall narrow sash window, recorded white six-panel rear door, radiator BESIDE the rear door in the brick corner, closet door and overhead cupboard, living entry, existing shelf recess, white pipe and shallow arched fireplace with CLOSED recessed white infill. Keep their modeled positions, dimensions and naturally visible portions. Preserve white ceiling, white opening trim and white doors. Only the two explicitly modeled workwall/windowwall surfaces receive the variant paint. Do not add or move openings, stretch the room, mirror the plan, invent a raised hearth or mantel, or open the closed fireplace.

The primary electric desk is Branch Tria Black Oak top / Charcoal frame, exact nominal 48x27 supplier geometry approximately 120x68.5cm, with 25.4mm flat top, two rectangular telescoping columns and low steel feet. Its published actual top is 47.2x27 inches; preserve the MODEL compact dimensions, seated height, position and orientation. It faces into the room with its back at the workwall. Keep ONE modest dark monitor and ONE keyboard at their EXACT final modeled positions: monitor moves 75mm toward the room; keyboard moves a net 25mm toward the room after a 50mm rearward support refinement. Both are raised 3.5mm onto the felt mat. Keep the cable hatch unobstructed. Keep the Grovemade Dark Grey Medium Plus felt desk mat on the main desk: 96.52x40.005cm, fine dark-gray felt, approximately 3.5mm thick. Preserve its actual modeled footprint and the equipment resting on it. No additional monitor, speakers, devices or desktop clutter.

The FIXED project bench is separate and 140x60cm: black-brown LAGKAPTEN top, ONE LEFT black-brown ALEX pedestal with FIVE drawers, and TWO RIGHT slender round black ADILS legs. Preserve its open right knee bay, real top spacing from the standing desk, and the modeled 20mm forward shift for panel clearance. Keep this second usable worktop clear. Do not put a monitor, keyboard, laptop, stool, camera or decor on it.

Exactly ONE daily task chair is the user's OWNED Herman Miller Aeron Large / Size C in MINERAL / LIGHT GRAY. Use the original selected Mineral product photograph and its iconic open mesh seat/back, light-gray frame and mesh, real armrests and five-spoke caster base. Preserve its modeled position facing the main desk, its large Size C proportions and natural occlusion. This is a dimension-and-photo proxy; let the modeled geometry control position and footprint. No black Branch chair, no second task chair, no added headrest or footstool. Keep ONE compact real IKEA EKENASET Axvall dark gray-blue visitor armchair with the actual selected walnut-effect exposed timber frame and gray-blue boucle cushions, approximately 65.1x74x74.9cm, in its exact modeled position and facing. It is not a sofa or recliner.

Keep the OWNED white Honeywell 02E Pro floor lamp at its exact modeled window-side location and orientation. Its horizontal head is an OPEN rectangular perimeter: two narrow LED bars around an empty center, supported by a slim upright and white U-shaped floor base. Keep the open center, not a filled diffuser slab. Keep the OWNED brown 59-inch MUTTROS tree at its exact window-side position and facing: natural wood branches, sisal sections, THREE woven wicker bowl baskets, ONE separate fleece hammock, cylindrical condo with arched entrance and rectangular brown base. Partial basket/base occlusion is correct. Do not alter basket count, relocate the tree, enlarge its branches into furniture or introduce cats/people from product photos.

Keep the compact dark-brown/oak-effect THREE-drawer STORKLINTA clothes chest in its modeled brick-wall bay. On its top only, preserve ONE IKEA FADO opal-white globe table lamp with the selected KAJPLATS bulb, ONE Small Parlor Palm in the actual Westcott Black pot on the opposite side, and the ONE small central modeled illustrative tray between them. Preserve that tray without adding other dresser clutter. FADO is an approximately 25cm opal glass globe, not a standing lamp or exposed bulb. The plant is a compact live nursery selection, published 6–11 inches from nursery bottom; pot height and crown spread are conservative photo proxies. Use healthy leafy green pinnate fronds from the real product photo within the model's compact crown and position, rather than reproducing sparse proxy stems as a bare plant. No large floor palm, no extra floor pot, and no plant on either shallow wall ledge. Closet shoe racks stay concealed behind the recorded closed door; no tall wardrobe.

Keep the real 6x9ft Ruggable Rift Charcoal flatwoven rug at its modeled footprint and rotation, using the selected actual broken horizontal block stripes in gray, cream and muted brown without stretching the pattern. There are exactly TWO matching IKEA MOSSLANDA black picture ledges, each approximately 115cm wide, 12cm deep and 7cm high: one above the FIXED bench at TOP HEIGHT 1.25m above the floor, one above the PRIMARY desk at TOP HEIGHT 2.10m. Their placement comes from the frozen model. Preserve the shallow front lips and only the small modeled illustrative books/tray below 20cm high. No extra shelves, large objects, ledge plants or ledge lighting.

Keep ONE native horizontal 100x70cm Dan Hobday Richmond print in its selected thin black frame, independently HUNG on the wall above the fixed-bench ledge, centered 1.85m above floor. It does not sit on or lean against the ledge. Preserve its exact muted geometric curved/straight forms in slate, charcoal, ivory, brown and quiet olive, model frame position and size. Keep the rest of the wall and brick fireplace clear of additional artwork. Preserve the high primary ledge's full modeled standing-monitor clearance; do not lower it or stretch the monitor.

Refine realism only within this locked composition: subtle black-oak grain, matte charcoal steel, cool light-gray Aeron mesh, gray-blue boucle, fine dark-gray felt, actual brick/oak flooring, natural wicker/fleece and the restrained palm/FADO arrangement. It is an adult studio with functional clear surfaces and closed storage. Use believable window daylight, neutral/cool preserved overhead-light presentation and a restrained local FADO glow, with accurate contact shadows and natural exposure. Keep white lamp and natural wood/wicker accents. No orange wash, RGB/gaming lights, excess decor, clutter, people, animals, collage, text, watermarks or dimension graphics. Landscape photograph only.'''

VARIANT_TEXT = {
    'b': '''THIS IS B — CHARCOAL + SLAT BAY. Matte cool Peppercorn charcoal, screen reference #585858, covers BOTH the actual long workwall AND actual rear/window wall. Keep white ceiling, doors/trim, the exposed brick and other unpainted surfaces exactly as modeled. A bounded THREE-METRE-wide Black Ash / Black Felt bay spans behind BOTH desks, centered X=-6.10m: FIVE adjacent real 60cm panels, each 2.4m high and 22mm proud of the source wall. Preserve actual narrow vertical slat rhythm, cool gray-black veneer, side edges and intentional 62cm charcoal band above. Do not extend slats to ceiling, wrap them onto the windowwall or cover windows/closet. Both black MOSSLANDA ledges and the independently hung Richmond artwork mount to the modeled panel face. This variant uses charcoal paint and black-ash texture, not navy.''',
    'c': '''THIS IS C — INK STUDIO. Matte deep NAVAL BLUE, screen reference #2F3D4C, covers BOTH the actual long workwall AND actual rear/window wall. Preserve painted wall geometry, white ceiling/doors/trim, original brick and other unpainted surfaces. There are NO slat panels, fluting or beadboard. The ONLY added wall ledges are the TWO exact black MOSSLANDA115 ledges already described and modeled. Richmond independently hangs above the lower ledge on the navy workwall. Preserve identical furniture footprints, facing, clear work surfaces and dresser composition from the companion views. This variant uses navy and graphic contrast, not charcoal slats.'''
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def validate_board_provenance(spec_path, catalog_path):
    path = ROOT / 'images/product-reference-boards.sources.json'
    if not path.is_file():
        raise SystemExit(f'Missing final original-product board provenance: {path}')
    metadata = read_json(path)
    for key, source in [('product_selection_sha256', catalog_path), ('design_spec_sha256', spec_path)]:
        if metadata.get(key) != digest(source):
            raise SystemExit(f'Product boards are stale or unsealed: {key}; rebuild boards from final composition.')
    if metadata.get('original_images_modified', metadata.get('original_photographs_modified')) is not False:
        raise SystemExit('Reference-board provenance must certify unmodified original photographs.')
    for relative, row in metadata.get('source_photographs', {}).items():
        photo = Path(relative)
        if not photo.is_absolute():
            photo = ROOT / photo
        if not photo.is_file() or digest(photo) != row['sha256']:
            raise SystemExit(f'Original source photo changed or missing: {photo}')
    return path, metadata


def validate_layout(layout_path, variant, spec):
    layout = read_json(layout_path)
    items = layout['items']
    counts = Counter(item.get('product_id') for item in items)
    for product_id, expected in spec['required_modeled_product_counts'].items():
        if counts[product_id] != expected:
            raise SystemExit(f'Final composition not ready in {layout_path}: {product_id} count {counts[product_id]} != {expected}')
    if counts['branch-pro'] or any(item.get('id') == 'branch-secondary' for item in items):
        raise SystemExit(f'Superseded Branch task chair still present: {layout_path}')
    chair = next(item for item in items if item.get('product_id') == 'aeron-size-c-mineral')
    if chair.get('front_blender_vector') != [0, 1, 0]:
        raise SystemExit(f'Owned Aeron facing changed: {layout_path}')
    finish = layout.get('workwall_finish', {})
    expected_panels = 5 if variant['id'] == 'b' else 0
    panel_quantity = finish.get('panel_count', finish.get('panel_quantity', finish.get('quantity')))
    # Builder layouts may store the same authoritative finish under a nested panel record.
    panel = finish.get('panel')
    if panel_quantity is None and isinstance(panel, dict):
        panel_quantity = panel.get('quantity')
    if variant['id'] == 'b' and panel_quantity != expected_panels:
        raise SystemExit(f'Final five-panel bay not ready or unrecorded: {layout_path}')
    if variant['id'] == 'c' and (panel_quantity not in (None, 0) or finish.get('panels') is True):
        raise SystemExit(f'Unexpected slat panels in C: {layout_path}')
    if finish.get('window_wall_wrap') is not True:
        raise SystemExit(f'Two-wall paint wrap is missing: {layout_path}')
    art = next(item for item in items if item.get('product_id') == 'dan-hobday-richmond')
    required_art_z = layout['room_floor_z_m'] + 1.85
    if abs(art['position_blender_m'][2] - required_art_z) > 0.001:
        raise SystemExit(f'Richmond must independently hang at center1.85m, not lean on ledge: {layout_path}')
    return layout


def validate_renders(directory, model):
    path = directory / 'model/render-provenance.json'
    if not path.is_file():
        raise SystemExit(f'Missing final render provenance: {path}')
    records = read_json(path)
    model_hash = digest(model)
    for letter in 'abc':
        key = f'room-{letter}'
        render = directory / f'model/renders/{key}.jpg'
        row = records.get(key, {})
        if row.get('scene_sha256') != model_hash or not render.is_file() or row.get('image_sha256') != digest(render):
            raise SystemExit(f'Render does not match its frozen model: {render}')
        if row.get('camera') != f'CAM {key}':
            raise SystemExit(f'Wrong source camera: {render}')
    return path


def build_manifest(variant_ids=None):
    spec_path = ROOT / 'design-spec.json'
    catalog_path = ROOT / 'products/selected-products.json'
    spec = read_json(spec_path)
    if variant_ids is not None:
        known_ids = {variant['id'] for variant in spec['variants']}
        if not variant_ids or not set(variant_ids).issubset(known_ids):
            raise ValueError('Request a nonempty subset of the selected B/C variants.')
    if digest(catalog_path) != spec['product_selection_sha256']:
        raise SystemExit('Final product catalog changed after composition specification; reconcile specification first.')
    board_source_path, board_source = validate_board_provenance(spec_path, catalog_path)
    board_outputs = board_source.get('outputs', {})
    views = []
    for variant in spec['variants']:
        if variant_ids is not None and variant['id'] not in variant_ids:
            continue
        directory = ROOT / variant['directory']
        model = directory / 'model/his-office-design.blend'
        layout = directory / 'model/layout.json'
        for required in (model, layout):
            if not required.is_file():
                raise SystemExit(f'Missing frozen authority: {required}')
        validate_layout(layout, variant, spec)
        validate_renders(directory, model)
        boards = [ROOT / 'images/product-board-1.png', ROOT / f'images/product-board-2-{variant["id"]}.png']
        for board in boards:
            relative = str(board.relative_to(ROOT))
            row = board_outputs.get(relative, board_outputs.get(board.name))
            if not board.is_file() or row is None or digest(board) != row['sha256']:
                raise SystemExit(f'Final board missing, stale or unhashed: {board}')
        for letter, companions in [('a', ['b', 'c']), ('b', ['a', 'c']), ('c', ['a', 'b'])]:
            paths = [directory / f'model/renders/room-{x}.jpg' for x in [letter] + companions] + boards
            if len(paths) != 5:
                raise SystemExit('Exactly five references required: three matching model angles and two product boards.')
            for path in paths:
                if not path.is_file():
                    raise SystemExit(f'Missing final reference: {path}')
            target = directory / f'images/concept-{letter}.png'
            views.append({
                'id': f'{variant["id"]}-{letter}',
                'variant': variant['id'], 'view': letter,
                'prompt': f'TARGET {variant["id"].upper()} / VIEW {letter.upper()}. Reference 1 is camera and placement authority.\n\n' + COMMON + '\n\n' + VARIANT_TEXT[variant['id']],
                'referenced_image_paths': [str(path) for path in paths],
                'reference_sha256': [digest(path) for path in paths],
                'target_output': str(target.relative_to(ROOT)),
                'model': str(model.relative_to(ROOT)), 'model_sha256': digest(model),
                'layout': str(layout.relative_to(ROOT)), 'layout_sha256': digest(layout),
            })
    return {
        'workflow': 'Final measured B/C models, three matching modeled angles and two sealed original-product boards per image; no generated pixel editing.',
        'design_spec_sha256': digest(spec_path),
        'product_selection_sha256': digest(catalog_path),
        'product_board_provenance_file': str(board_source_path.relative_to(ROOT)),
        'product_board_provenance_sha256': digest(board_source_path),
        'views': views,
    }


def main():
    manifest = build_manifest()
    out = ROOT / 'images'
    out.mkdir(exist_ok=True)
    for view in manifest['views']:
        (ROOT / view['target_output']).parent.mkdir(exist_ok=True)
    (out / 'generation-inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Prepared {len(manifest["views"])} frozen views with exactly five references each.')


if __name__ == '__main__':
    main()
