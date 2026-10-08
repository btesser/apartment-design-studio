"""Read-only product-photo UV and appearance audit; no photo/scene edits."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

OUT = Path('/workspace/his-office-pinterest/model')
PHOTOS = Path('/workspace/his-office-pinterest/products/photos')
FILES = {'rug': PHOTOS / 'ruggable-impasto-taupe-6x9.jpg',
         'art': PHOTOS / 'art-abstract-scenery-100x70.jpg',
         'visitor': PHOTOS / 'ekenaset-beige.jpg'}
before = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in FILES.items()}
arrays = {key: np.array(Image.open(path).convert('RGB')) for key, path in FILES.items()}

def photo_record(key):
    a = arrays[key]
    return {'file': str(FILES[key]), 'sha256': before[key], 'pixel_dimensions_W_H': [a.shape[1], a.shape[0]],
            'read_only': True, 'pixels_edited': False, 'visually_inspected': True}

def sample(box):
    left, top, right, bottom = box
    patch = arrays['visitor'][top:bottom, left:right]
    median = np.median(patch, axis=(0, 1))
    srgb = median / 255
    linear = np.where(srgb <= .04045, srgb / 12.92, ((srgb + .055) / 1.055) ** 2.4)
    return {'pixel_box_left_top_right_bottom_half_open': list(box),
            'median_sRGB_8bit': median.tolist(), 'median_sRGB_0to1': srgb.tolist(),
            'median_linear_RGB': linear.tolist()}

# First/last sampled rug-body pixels preserve the thin beige edge binding.
# The top and bottom observations are made across the central 1400 columns;
# the side observations are made across central 2300 rows. JPEG edge noise is
# avoided by using the body pixel centers for the UV endpoints.
left, top, right, bottom = 286, 138, 2121, 2852
width, height = 2400, 3000
body_edges = {'u_min': left / width, 'u_max': right / width,
              'v_min': 1 - bottom / height, 'v_max': 1 - top / height}
body_centers = {'u_min': (left + .5) / width, 'u_max': (right - .5) / width,
                'v_min': 1 - (bottom - .5) / height, 'v_max': 1 - (top + .5) / height}
report = {
    'schema_version': 1,
    'scope': 'Independent read-only source-photo audit. No images modified and no model built.',
    'coordinate_convention': 'Pixel boxes use top-left origin and half-open right/bottom endpoints. Blender UV has bottom-left origin.',
    'rug': {
        **photo_record('rug'),
        'selected_product': 'Ruggable Impasto Taupe Flatwoven 6×9 ft + Standard Pad',
        'nominal_body_dimensions_m': [1.8288, 2.7432],
        'rug_body_pixel_box_left_top_right_bottom_half_open': [left, top, right, bottom],
        'rug_body_pixel_dimensions_W_H': [right - left, bottom - top],
        'body_pixel_aspect_ratio_W_over_H': (right - left) / (bottom - top),
        'nominal_product_aspect_ratio_W_over_H': 6 / 9,
        'normalized_UV_body_edges': body_edges,
        'recommended_normalized_UV_pixel_centers': body_centers,
        'recommended_UV_quad_order_lower_left_lower_right_upper_right_upper_left': [
            [body_centers['u_min'], body_centers['v_min']], [body_centers['u_max'], body_centers['v_min']],
            [body_centers['u_max'], body_centers['v_max']], [body_centers['u_min'], body_centers['v_max']]],
        'mapping': 'Map full rectangular product body once across rug top; source image vertical axis follows 9ft length and horizontal axis follows 6ft width. Preserve thin beige binding. Keep image as sRGB; use EXTEND to avoid tiling.',
        'excluded': 'White studio background outside x286..2120/y138..2851 and gray bottom contact shadow beginning at y2852.',
        'edge_evidence': {
            'central_top_pixel_RGB': {'y137': [246, 245, 241], 'y138': [204, 201, 192]},
            'central_bottom_row_pixel_RGB': {'y2851': [207, 202, 196], 'y2852': [216, 213, 208]},
            'central_right_pixel_RGB': {'x2120': [204, 202, 190], 'x2121': [222, 219, 212], 'x2122': [241, 240, 238]},
            'inspection_note': 'Full-resolution row/column RGB profiles and visible continuous beige binding distinguish product body from white background/shadow; JPEG antialias transition is 1–2 pixels.'},
        'source_aspect_limit': 'Photo body aspect differs from nominal 6:9 by about 1.4%; use manufacturer 6×9ft model dimensions while mapping the full photographed rug body. Do not crop the design further to force source pixels into a 2:3 ratio.',
        'material_guidance': 'Matte flatwoven low-pile surface, roughness about0.85–0.95; shallow fine textile bump, restrained intensity. Photograph carries beige/taupe/ivory variation.'
    },
    'art': {
        **photo_record('art'),
        'selected_product': 'Desenio Abstract Scenery No1 Print, 70×100cm mounted landscape',
        'paper_dimensions_m_W_H': [1.0, .7], 'image_aspect_ratio_W_over_H': 2000 / 1400,
        'paper_aspect_ratio_W_over_H': 100 / 70, 'aspect_ratio_exact_match': True,
        'recommended_UV_quad_order_lower_left_lower_right_upper_right_upper_left': [[0, 0], [1, 0], [1, 1], [0, 1]],
        'paper_white_border_preserved': True,
        'mapping': 'Map entire unmodified 2000×1400 image across the entire 100×70cm landscape paper. No UV crop and no 90-degree rotation.',
        'printed_border': 'Visible white area on all four edges is part of the selected print paper. Preserve it inside the frame opening; do not remove it as a studio margin or add another wide mat.',
        'printed_border_observation_px': 'About140px each side; JPEG transition adds small edge artifacts. This observation is descriptive and must not be used to crop the UVs.',
        'orientation_cue': 'Cream sky occupies upper field; darker muted brown abstract landscape/horizon occupies lower field.',
        'material_guidance': 'Paper diffuse/roughness about0.8–0.95; retain original sRGB image without multiplication by beige tint. Frame can surround the full paper with restrained slim black profile.'
    },
    'visitor': {
        **photo_record('visitor'), 'selected_product': 'IKEA EKENÄSET Kilanda light beige',
        'upholstery_appearance': 'Light warm greige/beige fine woven upholstery, with small irregular texture and soft highlights. Avoid teal, strong orange/sand saturation, glossy finish, or long corduroy ribs.',
        'wood_appearance': 'Dark brown espresso/walnut finish with subtle warm reddish-brown grain. Arm tops catch light; legs remain darker. Use a separate wood material from upholstery.',
        'photo_samples': {'upholstery_back_midtones': sample((700, 150, 1100, 500)),
                          'upholstery_seat_lit': sample((280, 680, 600, 790)),
                          'wood_arm': sample((980, 383, 1190, 405)),
                          'wood_front_leg': sample((924, 915, 948, 1150))},
        'suggested_starting_materials': {
            'fabric_base_color_linear_RGB': [.59, .52, .46], 'fabric_roughness': .9,
            'fabric_bump_strength': .12, 'fabric_bump_distance_m': .00025,
            'wood_base_color_linear_RGB': [.045, .025, .019], 'wood_roughness': .5},
        'sample_limit': 'Photograph samples include lighting and camera response. Values guide a visual approximation, not calibrated manufacturer albedo. Listed linear RGB is suitable for Blender Python node default_value; the separate sRGB values are for display/reference.'
    },
    'unchanged_photo_hashes_after_audit': {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in FILES.items()},
}
report['all_photos_unchanged'] = report['unchanged_photo_hashes_after_audit'] == before
assert report['all_photos_unchanged']
(OUT / 'reference-texture-audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
lines = [
    'READ-ONLY REFERENCE TEXTURE AUDIT', '',
    'RUG — Ruggable Impasto Taupe 6×9ft',
    'Source: ' + str(FILES['rug']),
    'Image2400×3000; full rug-body box [286,138,2121,2852) in top-left pixel coordinates.',
    'Preserve thin beige binding; exclude surrounding white margin and bottom gray shadow.',
    'Recommended Blender UV min=(0.119375,0.0495), max=(0.883541667,0.953833333).',
    'Map vertical photo axis to9ft length and horizontal axis to6ft width, once across entire rug top.',
    'Nominal model1.8288×2.7432m. Body-photo ratio is about1.4% different; keep complete photographed body.',
    '', 'ART — Abstract Scenery No1',
    'Source: ' + str(FILES['art']),
    'Image2000×1400 matches100×70cm paper ratio exactly.',
    'UV=(0,0)–(1,1) on full1.00×0.70m landscape paper. Preserve printed white border.',
    'Keep cream sky above the muted brown abstract landscape. No painted-image crop and no extra wide mat.',
    '', 'VISITOR — EKENÄSET Kilanda light beige',
    'Source: ' + str(FILES['visitor']),
    'Fine warm greige woven fabric, matte; dark espresso/walnut wood frame.',
    'Blender starting fabric linearRGB=(0.59,0.52,0.46), roughness0.90, fine bump strength0.12/distance0.00025m.',
    'Wood starting linearRGB=(0.045,0.025,0.019), roughness0.50. Match photo appearance under final scene lights.',
    'Photo samples include illumination; they are visual guidance, not calibrated manufacturer albedo.',
    '', 'All three photos were visually inspected and read only. Their SHA256 hashes remain unchanged.',
    'Machine-readable UV values, source hashes, sample boxes, and appearance guidance: reference-texture-audit.json.'
]
(OUT / 'reference-texture-audit.txt').write_text('\n'.join(lines) + '\n')
print(json.dumps({'all_photos_unchanged': report['all_photos_unchanged'],
                  'rug_UV': body_centers, 'art_aspect_ratio_exact_match': True,
                  'outputs': ['reference-texture-audit.json', 'reference-texture-audit.txt']}, indent=2))
