"""Freeze exact five-reference image-generation inputs for both reviewed designs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / 'design-spec.json').read_text())

COMMON = '''Create one realistic finished interior photograph from the supplied measured 3D apartment office. Reference1 is the exact TARGET composition: preserve its camera, crop, perspective, room proportions, ceiling height, opening locations, every furniture footprint and facing, and natural occlusion. References2 and3 are companion views of the SAME frozen model and establish geometry. References4 and5 are boards containing original real supplier/retailer product photographs, a selected inspiration image and color references. Use their product appearances and atmosphere; never copy their showroom architecture, background props or furniture placements. Do not put boards or labels in the result.

Preserve the existing oak-tone plank floor, red-brown brick wall, tall narrow sash window, recorded white six-panel rear door, radiator BESIDE the door in the brick corner, closet door with overhead cupboard, living entry, existing shelf recess and actual shallow arched fireplace with CLOSED recessed white infill. Keep all their modeled positions, dimensions and visible portions. Keep white ceiling and light surrounding walls. Do not add or move openings, stretch the room, mirror the plan, create a raised hearth/mantel or open the closed fireplace.

The primary standing desk is the real Branch Tria Black Oak top and Charcoal frame. Its nominal48x27-inch supplier model is approximately120x68.5cm, with25.4mm flat top, two telescoping rectangular columns and low angled steel feet. Preserve the modeled compact dimensions and orientation, seated height and black-oak grain; do not copy a wider showroom desk. It faces into the room with its back at the workwall. Keep ONE modest dark monitor and keyboard on this primary desk only; ordinary office equipment is illustrative. Keep its useable working area clear.

The separate FIXED project bench is140x60cm: black-brown LAGKAPTEN top, ONE LEFT black-brown ALEX pedestal with FIVE drawers, TWO RIGHT slender round black ADILS legs. Preserve the open right knee bay and actual spacing from the primary desk. Its entire top is clear: no second monitor, keyboard, laptop, camera, speakers, stool or extra equipment. There is exactly ONE black Branch Ergonomic Chair Pro with mesh back, armrests and five-star caster base, in its modeled main working position facing the primary desk. Do not add a second task chair.

The owned white Honeywell02E Pro floor lamp remains at its EXACT modeled window-side location and orientation. Its head is a horizontal OPEN rectangular perimeter: two narrow LED bars with an empty center, supported by a slim upright, with a flat white U-shaped base. Preserve the open center rather than turning the head into a filled glowing slab. The brown59-inch MUTTROS cat tree remains exactly in its measured window-side position and orientation, with natural wood branches, sisal sections, THREE staggered woven wicker bowl baskets, ONE separate fleece hammock, cylindrical condo with an arched entrance and rectangular brown base. Natural partial occlusion is correct. Do not change its basket count, move it, enlarge branches into the desk or introduce cats/people from product photography.

Keep the compact THREE-drawer dark-brown/oak-effect STORKLINTA clothes chest in the recorded brick-wall bay; no tall wardrobe. Keep ONE real EKENASET Axvall dark gray-blue visitor armchair, walnut-effect exposed wood frame, gray-blue boucle cushions, in its modeled position and orientation. It is a compact65.1x74x74.9cm seat, not a sofa or recliner. Closet shoe racks remain concealed behind its recorded closed door.

Keep the6x9ft Ruggable Rift Charcoal low-pile rug at its precise modeled footprint/rotation. Use the actual charcoal broken horizontal-block stripes in gray, cream and muted brown from its selected product photo, with no motif stretching. Keep ONE native horizontal100x70cm Dan Hobday Richmond artwork in a thin black frame ABOVE THE PROJECT BENCH. Use its exact muted geometric curved/straight forms in slate, charcoal, ivory, brown and quiet olive. Preserve the model's frame position and size. Leave the wall above the primary desk and the brick fireplace clear of additional artwork.

Refine materials and realism within this locked composition: subtle dark-oak grain, matte charcoal steel, authentic brick and oak floor, cool gray-blue boucle, fine black mesh, natural wicker and fleece. The result is a clean adult studio with atmosphere and generous clear working surfaces. Use believable existing-window daylight and a neutral/cool overhead-light presentation with accurate contact shadows and natural exposure. Preserve white lamp and natural wood/wicker accents. No orange color wash, RGB/gaming lights, oversized plants, clutter or extra decorative props. Landscape photograph only, with no watermarks, collage, text or dimension graphics.'''

VARIANT_TEXT = {
    'b': '''THIS IS B — CHARCOAL + SLAT BAY. The actual long workwall is matte cool charcoal (Peppercorn screen reference#585858). A bounded1.8m-wide Black Ash/Black Felt slat bay sits behind the fixed project bench: THREE adjacent real60cm panels, each2.4m high and22mm proud of the wall. Preserve the actual narrow vertical slat rhythm and cool gray-black veneer, the clean bounded side edges and intentional62cm charcoal band above it. Do not extend panels to the ceiling, around the room or across the window/closet. The Richmond artwork hangs on this panel bay at the modeled center. This room uses charcoal and black-ash texture, not navy paint.''',
    'c': '''THIS IS C — INK STUDIO. The actual long workwall is matte deep NAVY BLUE (Sherwin-Williams Naval screen reference#2F3D4C), a clearly cool blue-black surface. Preserve the flat painted-wall geometry and its junctions with the existing light surrounding walls. There are NO slat panels, fluting, beadboard, shelving or new built-ins. The Richmond artwork hangs directly on this navy workwall at the modeled center. Keep the exact same furniture placements and clear working surfaces as the companion model views. This room uses navy and graphic contrast, not charcoal slats.'''
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

views = []
for variant in SPEC['variants']:
    directory = ROOT / variant['directory']
    model = directory / 'model/his-office-design.blend'
    layout = directory / 'model/layout.json'
    for required in (model, layout):
        if not required.is_file():
            raise SystemExit(f'Missing frozen authority: {required}')
    for letter, companions in [('a', ['b','c']), ('b', ['a','c']), ('c', ['a','b'])]:
        paths = [directory / f'model/renders/room-{x}.jpg' for x in [letter]+companions]
        paths += [ROOT / 'images/product-board-1.png', ROOT / f'images/product-board-2-{variant["id"]}.png']
        for path in paths:
            if not path.is_file():
                raise SystemExit(f'Missing final reference: {path}')
        target = directory / f'images/concept-{letter}.png'
        target.parent.mkdir(exist_ok=True)
        views.append({
            'id': f'{variant["id"]}-{letter}',
            'variant': variant['id'], 'view': letter,
            'prompt': f'TARGET {variant["id"].upper()} / VIEW {letter.upper()}. Reference1 is camera and placement authority.\n\n'+COMMON+'\n\n'+VARIANT_TEXT[variant['id']],
            'referenced_image_paths': [str(p) for p in paths],
            'reference_sha256': [digest(p) for p in paths],
            'target_output': str(target.relative_to(ROOT)),
            'model': str(model.relative_to(ROOT)), 'model_sha256': digest(model),
            'layout': str(layout.relative_to(ROOT)), 'layout_sha256': digest(layout),
        })
out = ROOT / 'images'
out.mkdir(exist_ok=True)
manifest = {'workflow':'Frozen measured models, three views and two original-product/reference boards per image',
            'design_spec_sha256':digest(ROOT/'design-spec.json'),
            'product_selection_sha256':digest(ROOT/'products/selected-products.json'),
            'views':views}
(out / 'generation-inputs.json').write_text(json.dumps(manifest,indent=2))
print(f'Prepared{len(views)} frozen views with five references each.')
