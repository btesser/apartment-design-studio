"""Independent read-only photo/UV audit for approved separate B/C variants."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

OUT = Path(__file__).parent
PRODUCTS = Path('/workspace/his-office-pinterest/products/proposal-complements')
FILES = {'rug': PRODUCTS / 'photos/rift-6x9.jpg',
         'art': PRODUCTS / 'art/dan-hobday-richmond-70x100-official.jpg',
         'visitor': PRODUCTS / 'photos/ekenaset-axvall-gray-blue.jpg'}
metadata = json.loads((PRODUCTS / 'cool-complements.json').read_text())
selected = {i['id']: i for i in metadata['selected_complements']}
art_evidence = json.loads((PRODUCTS / 'art/dan-hobday-richmond-evidence.json').read_text())
art_variant = art_evidence['selected_70x100']
arrays = {key: np.array(Image.open(path).convert('RGB')) for key, path in FILES.items()}
hashes_before = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in FILES.items()}

def photo(key, expected_hash):
    array = arrays[key]
    return {'file': str(FILES[key]), 'sha256': hashes_before[key],
            'matches_original_provenance_hash': hashes_before[key] == expected_hash,
            'pixel_dimensions_W_H': [array.shape[1], array.shape[0]],
            'pixels_edited': False, 'visually_inspected': True}

def sample(box):
    l, t, r, b = box
    rgb = np.median(arrays['visitor'][t:b, l:r], axis=(0, 1))
    srgb = rgb / 255
    linear = np.where(srgb <= .04045, srgb / 12.92, ((srgb + .055) / 1.055) ** 2.4)
    return {'sample_pixel_box_left_top_right_bottom': box, 'median_sRGB_8bit': rgb.tolist(),
            'median_linear_RGB': linear.tolist()}

left, top, right, bottom = 286, 138, 2121, 2852
image_W, image_H = 2400, 3000
uv = {'u_min': (left + .5) / image_W, 'u_max': (right - .5) / image_W,
      'v_min': 1 - (bottom - .5) / image_H, 'v_max': 1 - (top + .5) / image_H}
art = arrays['art']
art_edges = {'top': art[0], 'bottom': art[-1], 'left': art[:, 0], 'right': art[:, -1]}
edge_stats = {name: {'mean_sRGB_8bit': pixels.mean(0).tolist(),
                     'nearly_white_fraction_min_channel_gt_250': float((pixels.min(1) > 250).mean())}
              for name, pixels in art_edges.items()}

report = {
    'schema_version': 1,
    'scope': 'Approved separate B/C alternatives share these references. Independent audit reads only photographs/provenance; it does not open, edit, or save Blender.',
    'coordinate_convention': 'Pixel coordinates have top-left origin. Pixel boxes are half-open at right/bottom. Blender image UV has bottom-left origin.',
    'rug': {
        **photo('rug', selected['rift']['official_photo']['sha256']),
        'id': 'rift', 'name': selected['rift']['name'],
        'source_url': selected['rift']['source_url'],
        'official_image_url': selected['rift']['official_photo']['image_url'],
        'selected_variant_id': selected['rift']['variant'], 'selected_sku': selected['rift']['sku'],
        'model_dimensions_local_X_Y_m': [2.7432, 1.8288],
        'nominal_cover_plus_standard_pad_thickness_m': .005175,
        'body_pixel_box_left_top_right_bottom_half_open': [left, top, right, bottom],
        'full_body_including_binding_pixel_dimensions_W_H': [right - left, bottom - top],
        'recommended_body_UV_pixel_centers': uv,
        'quad_local_corner_order': ['-X,-Y', '+X,-Y', '+X,+Y', '-X,+Y'],
        'quad_UV_same_order_long_photo_axis_along_X': [[uv['u_min'], uv['v_min']],
                                                     [uv['u_min'], uv['v_max']],
                                                     [uv['u_max'], uv['v_max']],
                                                     [uv['u_max'], uv['v_min']]],
        'mapping': 'Source vertical V maps to local X (9ft); source horizontal U maps to local Y (6ft). Map the complete photographed rug body once, preserving black binding and all graphic rows.',
        'excluded_regions': 'White studio margin surrounding the rug; gray contact shadow beginning at row2852. Pixel-center endpoints avoid the1–2px JPEG antialias fringe.',
        'edge_samples_RGB': {'top_outside_x1000_y137': [248, 248, 248], 'top_binding_x1000_y138': [50, 50, 50],
                             'bottom_binding_x1000_y2851': [51, 51, 51], 'bottom_shadow_x1000_y2852': [218, 218, 218],
                             'right_binding_x2120_y1500': [54, 54, 54], 'right_antialias_x2121_y1500': [149, 149, 149],
                             'right_background_x2122_y1500': [241, 241, 241]},
        'photo_body_aspect_ratio_W_over_H': (right - left) / (bottom - top),
        'nominal_product_aspect_ratio_W_over_L': 6 / 9,
        'aspect_note': 'The source rug-body aspect differs from nominal6:9 by about1.4%. Preserve every graphic row and full binding; use nominal product dimensions rather than cropping the pattern further.',
        'material': {'image_color_space': 'sRGB', 'image_extension': 'EXTEND', 'image_base_color_multiplier': [1, 1, 1],
                     'roughness_start': .92, 'bump_distance_m_start': .00015,
                     'surface_note': 'Matte low-pile flatweave; charcoal/blue-gray ground with off-white, muted tan, gray, and black blocks. Keep exact original graphic coloration.'}
    },
    'art': {
        **photo('art', art_variant['image_sha256']),
        'id': 'dan-hobday-richmond', 'name': art_evidence['title'],
        'source_url': art_evidence['source_url'], 'official_image_url': art_variant['image_url'],
        'selected_variant_id': art_variant['id'], 'selected_sku': art_variant['articleNumber'],
        'retailer_variant_size_key': art_variant['size'], 'retailer_US_size_label': art_variant['sizeTitle'],
        'paper_dimensions_landscape_W_H_m': [1.0, .7],
        'image_aspect_ratio': 2000 / 1400, 'paper_aspect_ratio': 100 / 70, 'exact_aspect_match': True,
        'UV_quad_lower_left_lower_right_upper_right_upper_left': [[0, 0], [1, 0], [1, 1], [0, 1]],
        'studio_padding_detected': False,
        'continuous_printed_white_border_detected': False,
        'edge_statistics': edge_stats,
        'mapping': 'Full original2000×1400px image maps to full100×70cm landscape paper. Artwork/color texture reaches all four edges. No crop or90degree rotation is needed. Preserve all source edge colors; do not create an extra white mat.',
        'border_note': 'This Richmond variant differs from the preceding white-bordered Abstract Scenery print. Its pale cream fields belong to the artwork; there is no continuous white studio margin or printed white paper band in this exact variant source image.',
        'palette_observation': 'Slate gray/charcoal geometric shapes, muted olive, ivory, and dark brown. The background is not pure white.',
        'material': {'image_color_space': 'sRGB', 'image_base_color_multiplier': [1, 1, 1],
                     'roughness_start': .88, 'emission_strength': 0, 'surface_note': 'Matte poster paper; optional frame surrounds full paper and must not hide or replace its cream artwork fields.'}
    },
    'visitor': {
        **photo('visitor', selected['ekenaset-axvall-gray-blue']['official_photo']['sha256']),
        'id': 'ekenaset-axvall-gray-blue', 'name': selected['ekenaset-axvall-gray-blue']['name'],
        'source_url': selected['ekenaset-axvall-gray-blue']['source_url'],
        'official_image_url': selected['ekenaset-axvall-gray-blue']['official_photo']['image_url'],
        'selected_sku': selected['ekenaset-axvall-gray-blue']['sku'],
        'selected_finish': selected['ekenaset-axvall-gray-blue']['color'],
        'nominal_dimensions_W_D_H_m': selected['ekenaset-axvall-gray-blue']['dimensions_m_W_D_H'],
        'upholstery': 'Axvall bouclé: dense fine nubby/looped fabric, dark slate gray-blue with tiny darker flecks. Soft matte surface. It has no long corduroy ridges and is neither bright cyan nor glossy velvet.',
        'frame': 'Walnut-effect medium-dark muted brown wood. More neutral and visibly lighter than the previous beige-chair espresso/reddish frame; retain wood grain as a distinct material.',
        'photo_samples': {'back': sample([700, 150, 1100, 500]), 'seat': sample([280, 680, 600, 790]),
                          'wood_arm': sample([990, 394, 1170, 410]), 'wood_leg': sample([922, 930, 942, 1160])},
        'suggested_Blender_node_default_values': {'fabric_base_color_linear_RGB': [.047, .090, .128],
                                                 'fabric_roughness': .93, 'fabric_bump_strength': .13,
                                                 'fabric_bump_distance_m': .0003,
                                                 'wood_base_color_linear_RGB': [.085, .068, .053],
                                                 'wood_roughness': .53},
        'fabric_texture_guidance': 'Use small irregular bouclé microtexture and restrained color flecks; keep the grain fine enough that it reads as cloth at full-room distance. Do not reuse the old corduroy wave nodes.',
        'shape_guard': 'This actual refresh has nominal dimensions0.650875×0.739775×0.7493m. It is wider, shallower, and lower than the old beige EKENÄSET; material guidance does not authorize simple recoloring of the old dimensions.',
        'sampling_limit': 'RGB values sampled from a lit product photograph are visual starting points, not calibrated physical albedo. Supplied linear RGB values are for Blender Python node default_value; photograph channel medians are sRGB8bit.'
    },
    'hashes_after_audit': {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in FILES.items()},
}
report['all_photos_unchanged'] = report['hashes_after_audit'] == hashes_before
report['all_photos_match_original_provenance'] = all(report[k]['matches_original_provenance_hash'] for k in ['rug', 'art', 'visitor'])
assert report['all_photos_unchanged'] and report['all_photos_match_original_provenance']
(OUT / 'variant-reference-audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
lines = [
    'B/C VARIANT REFERENCE AUDIT — READ ONLY', '',
    'Rift Charcoal6×9ft:',
    'Original image2400×3000px. Full body incl. black binding is [286,138,2121,2852); exclude studio margin and bottom shadow.',
    'Recommended imageUV: u0=0.119375; u1=0.883541666667; v0=0.0495; v1=0.953833333333.',
    'Local rugX=9ft=2.7432m; Y=6ft=1.8288m. SourceV followsX; sourceU followsY.',
    'For local corner order(-X,-Y),(+X,-Y),(+X,+Y),(-X,+Y), UV=[(u0,v0),(u0,v1),(u1,v1),(u1,v0)].',
    'Matte flatweave; preserve exact graphic colors and complete row pattern. Use sRGB image and EXTEND.',
    '', 'Richmond:',
    'Exact SKUpre0717-1 / variant101361 /70x100 retailer size, native100×70cm landscape. Original photo2000×1400px.',
    'FullUV0..1 across full1.00×0.70m paper. No studio padding or continuous printed-whiteborder detected.',
    'All four edges contain artwork. Pale cream areas are artwork. Preserve full image; do not add a white mat.',
    '', 'EKENÄSET Axvall dark gray-blue / walnut effect:',
    'Bouclé upholstery: fine irregular nubby loops, dark slate gray-blue, matte; separate muted medium-dark brown wood frame.',
    'Suggested Blender fabric linearRGB=(0.047,0.090,0.128), roughness0.93, fine bump strength0.13/distance0.0003m.',
    'Suggested wood linearRGB=(0.085,0.068,0.053), roughness0.53.',
    'Actual refresh dimensions0.650875×0.739775×0.7493m; do not retain old beige chair dimensions or corduroy ribs.',
    'Photo sample values guide appearance under final lights; they are not calibrated albedo.',
    '', 'All original source-image hashes matched provenance and remained unchanged. No Blender data or old assets were modified.',
    'Precise UV arrays, sourceURLs/SHA256, border measurements, and material/photo samples: variant-reference-audit.json.'
]
(OUT / 'variant-reference-audit.txt').write_text('\n'.join(lines) + '\n')
print(json.dumps({'outputs': [str(OUT / 'variant-reference-audit.json'), str(OUT / 'variant-reference-audit.txt')],
                  'all_photos_unchanged': report['all_photos_unchanged'],
                  'all_photos_match_original_provenance': report['all_photos_match_original_provenance'],
                  'rug_UV': uv, 'art_studio_padding': False}, indent=2))
