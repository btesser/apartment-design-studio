from pathlib import Path
import json, hashlib

ROOT = Path(__file__).resolve().parent
PHOTOS = [
    'products/keepers/uplift-live-edge-pheasantwood-front.jpg',
    'products/keepers/uplift-v2-c-frame-industrial-official.png',
    'products/keepers/honeywell-B0C3BVYTXP-MAIN.jpg',
    'products/keepers/muttros-B0HHRC6XBC-MAIN.jpg',
    'products/candidates/official-images/lagkapten-alex-single.jpg',
    'products/candidates/official-images/branch-pro-selected.jpg',
    'products/candidates/official-images/storklinta-low-drawers.jpg',
    'products/candidates/official-images/ekenaset-turquoise.jpg',
    'products/candidates/official-images/ruggable-inkdrop-selected.jpg',
    'products/candidates/official-images/art-blue-bold-selected.jpg',
    'products/candidates/official-images/art-blue-geometric-selected.jpg',
]
COMMON = '''Create a realistic finished interior photograph by upgrading the supplied 3D-rendered room. This is a carefully dimensioned existing apartment office, not a freely redesigned room. The FIRST reference is the locked target composition: preserve its exact camera, crop, perspective, architecture, floor outline, ceiling height, furniture locations, facing and size relationships. References 2 and 3 show companion angles of the SAME frozen 3D room and establish its geometry; do not switch to their cameras or insert objects from outside the target crop. References 4 and 5 are reference sheets made from the original real retailer product photographs, with simple identification labels. Use each photographed product for exact appearance only; do not put the sheets or their labels in the result. Never copy their showroom architecture, background props, dimensions or camera.

Keep the warm-white painted walls, exposed red-brown brick wall, existing oak-toned plank floor, tall narrow rear sash window and its shade/bars, white six-panel exterior door, radiator beside that door in the brick corner, closet leaf and overhead cupboard, living entrance, existing shelf recess and actual low arched brick fireplace with recessed CLOSED white infill. Keep those features where the model puts them, including any naturally occluded portions. No added windows, doorways, mantel, raised hearth, built-in wall cabinets or room enlargement. Do not mirror or recenter the layout. Do not turn the fireplace into an open fire.

The main UPLIFT desk is exactly 42 x 30 inches (106.68 x 76.2 cm), with a thick Pheasantwood solid-wood barkline FRONT edge, square back edge against the white wall, two brushed-nickel grommets and an industrial-gray steel two-leg C-frame. Its real catalog wood photo is appearance reference only; DO NOT widen the modeled desk to match the wide catalog photograph. The white Honeywell 02E Pro floor lamp has a slender rectangular post, horizontal open rectangular LED head and flat U-shaped foot. Retain its modeled position and orientation beside the main desk on the window side.

The brown MUTTROS 59-inch cat tree has natural wood branches and sisal sections, THREE woven wicker bowl baskets at staggered heights, ONE separate brown fleece hammock, a brown cylindrical condo with arched entrance and a rectangular brown base. Use the actual photo to improve the branches, wicker and fleece within the model's allotted envelope; preserve the model's window-side placement and rotation with branches running along the window wall. Do not move it to another corner, extend branches through the desk or wall, or replace it with a generic square-platform tree. Do not introduce cats or people from the product photos.

The second workspace is the 140 x 60 cm IKEA LAGKAPTEN/ALEX: dark black-brown rectangular top, ONE white five-drawer ALEX pedestal on the modeled LEFT end and TWO slender white round legs on the right. Keep the real open knee bay on the right. Both desk fronts face into the room and both BLACK Branch Ergonomic Chair Pro task chairs face their desks/white wall; there are exactly TWO task chairs. Preserve detailed mesh backs, black seats, armrests and five-star caster bases, with the modeled caster footprint and working position. Keep a single modest dark monitor and keyboard on each desk, and preserve useful clear worktop area.

The separate clothes chest is the small 70 cm wide oak-effect STORKLINTA with THREE flush drawers, placed in the brick-wall bay shown in the model. It is not a wardrobe or a desk. The visitor seat is the compact EKENASET with dark slate-teal/gray-turquoise corduroy upholstery and warm brown exposed wood arms and legs. There is exactly ONE visitor chair beside the brick fireplace, facing as modeled; do not replace it with a sofa, office chair, recliner or oversized lounger.

Keep the actual 6 x 9 foot ivory/slate-blue Jonathan Adler Inkdrop rug at its modeled footprint and rotation under the two work-chair areas. Preserve its recognizable stepped linear dot/stripe pattern from the actual selected photo. The two thin black-framed prints retain the actual artwork and their modeled sizes and positions: Desenio Bold Blue above the fireplace, Desenio Blue Geometric above the UPLIFT desk. No extra posters, decorative mirrors or plants from the retailer backgrounds. Closet shoe racks remain concealed behind the recorded closed closet door; do not add visible shoe storage elsewhere.

Make the finishes rich and convincing: natural Pheasantwood grain, warm oak and brick, matte white/industrial steel, woven wicker, fine corduroy and black mesh. Soft realistic daylight from the EXISTING window, gentle lamp illumination, accurate contact shadows, natural neutral exposure and believable scale. Stylish warm modern studio, practical and lived-in without clutter. Keep all recorded furniture positions rather than optimizing the photo. This is one landscape photograph, not a collage or labeled diagram. No text, watermarks or dimension graphics.'''

views = []
for letter, other in [('a',['b','c']),('b',['a','c']),('c',['a','b'])]:
    paths = []
    for x in [letter]+other:
        refined = ROOT / f'model/renders/room-{x}.jpg'
        paths.append(refined if refined.is_file() else ROOT / f'model/generation-guides/room-{x}.jpg')
    paths += [ROOT / 'images/product-board-1.png', ROOT / 'images/product-board-2.png']
    for path in paths:
        if not path.is_file(): raise SystemExit(f'Missing final reference: {path}')
    views.append({'id':letter,
                  'prompt':f'TARGET VIEW {letter.upper()}. Preserve reference 1 exactly as the camera/placement authority.\n\n'+COMMON,
                  'referenced_image_paths':[str(p) for p in paths],
                  'reference_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],
                  'target_output':f'images/concept-{letter}.png',
                  'original_product_photographs':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in PHOTOS]})
out = ROOT / 'images'
out.mkdir(exist_ok=True)
(out / 'generation-inputs.json').write_text(json.dumps({'views':views},indent=2))
print(f'Prepared {len(views)} views with {len(views[0]["referenced_image_paths"])} references each')
