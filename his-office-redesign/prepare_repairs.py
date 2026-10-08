from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
path=ROOT/'images/generation-inputs.json'
data=json.loads(path.read_text())
prompts={
'b':'''Edit the FIRST photograph to correct the specific mistakes below while retaining its realistic lighting, style, camera, crop and all existing furniture. The SECOND image is the exact 3D camera/geometry/placement authority for this view B. The THIRD image shows the same room's main workstation from a companion angle, so you can understand artwork placement. Images FOUR and FIVE contain original retailer product photographs for appearance only. Never import their backgrounds, props, labels or room layouts.

CRITICAL ART CORRECTION: the white wall directly above the SECOND dark IKEA desk must be BLANK. Remove the entire Blue Geometric poster currently above its monitor. Remove the Bold Blue painting currently at the far left on the white wall. Bold Blue belongs on the opposite brick fireplace wall, which is completely outside this camera crop; none of it is visible in this photograph. Blue Geometric belongs above the small main UPLIFT wood desk, farther left. In source model view B its right edge is barely clipped by the EXTREME LEFT boundary of the frame. Reproduce only that tiny clipped portion of Blue Geometric if visible at the same extreme left position; do not relocate a full print above the second desk. Use the second reference's blank wall and exact clipping as authority.

WOOD CORRECTION: deepen the main UPLIFT desk wood at lower left to the actual Pheasantwood reference: rich dark amber/brown, pronounced alternating chocolate-brown and golden grain stripes. It is not pale blond oak. Preserve the owned top's 42 x 30 inch dimensions, barkline front, square back, two brushed-nickel grommets and industrial-gray steel C-frame. The wide catalog photograph controls finish only and must not enlarge the modeled small desktop. Remove the invented round metal grommet on the second black-brown desktop: IKEA LAGKAPTEN has a plain solid top.

Everything else stays as placed by the second model reference: one 140 x 60 cm second desktop, ONE white five-drawer ALEX pedestal on its LEFT and TWO white round legs on its right with clear knee space; exactly two black mesh Branch task chairs facing their desks and white wall, one slate-teal corduroy EKENASET visitor chair with brown wooden frame at right facing as modeled; unchanged closet leaf/overhead cupboard and living-room entrance; unchanged ivory/slate-blue 6 x 9 foot Inkdrop rug. Keep the room size, floor, wall/door positions, desk footprint, chair spacing and direction. Do not add a cabinet, mirror, shelf, light, people, cat, art, doorway, window or text. One photorealistic landscape image, no collage. Make only the requested corrections.''',
'c':'''Edit the FIRST photograph, preserving its realistic colors, camera, crop, existing furniture and the correct Bold Blue artwork above the brick fireplace. The SECOND image is the exact 3D view C geometry/placement authority. The THIRD image is the same room's other angle. Images FOUR and FIVE contain original real retailer product photographs for exact products/finishes only. Their backgrounds and labels never become room contents.

CRITICAL FIREPLACE CORRECTION: remove the invented raised, deep, projecting brick hearth/step below and in front of the white arched closure. Match the second reference's low arch and recessed CLOSED white infill. The model has only a very shallow bottom brick rim, about 45 mm tall, at the existing chimney front plane. Preserve that thin lower brick course but do not build it outward into a platform or thick threshold. The normal oak plank floor remains level and continues to that chimney plane. Preserve the authentic radial brickwork appearance around the arch, its measured size and the white infill recessed behind the front brick by about 11 cm. Do not open the fireplace or enlarge the recess. No new mantel or shelves.

Keep all other objects in their modeled places and orientations: correct blue Bold Blue print only above the brick arch; the separate small oak STORKLINTA with exactly THREE flush drawers in the bay beside the radiator, not a wardrobe/desk; black radiator beside the six-panel white exterior door with brass hardware; window/cat tree at the right edge; compact slate-teal corduroy EKENASET visitor chair with warm brown wood arms/legs at lower left; two black Branch task chairs oriented toward their desks and the white wall; actual ivory/slate-blue 6 x 9 foot Inkdrop rug. Preserve the MUTTROS natural branches, three wicker baskets plus fleece hammock/condo with naturally occluded portions remaining occluded. The Honeywell head is outside this camera crop: do not insert it into the image. Do not alter furniture sizes, room dimensions, camera, crop, wall/door positions or rug footprint. Do not add props, art, cats, people or text. One realistic landscape photograph, no collage. Only the shallow lower-rim correction is needed.'''
}
for letter, companion in [('b','a'),('c','b')]:
    view=next(v for v in data['views'] if v['id']==letter)
    refs=[ROOT/f'images/attempts/initial-{letter}.png',
          ROOT/f'model/generation-guides/pre-lamp-correction-room-{letter}.jpg',
          ROOT/f'model/generation-guides/pre-lamp-correction-room-{companion}.jpg',
          ROOT/'images/product-board-1.png',ROOT/'images/product-board-2.png']
    view['prompt']=prompts[letter]
    view['referenced_image_paths']=[str(p) for p in refs]
    view['reference_sha256']=[hashlib.sha256(p.read_bytes()).hexdigest() for p in refs]
    view['iteration_note']='Targeted repair of first concept against frozen source geometry and original product photographs.'
path.write_text(json.dumps(data,indent=2))
print('B/C repair inputs prepared, each with five viewed references')
