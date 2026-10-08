import json, hashlib, re
from pathlib import Path
from PIL import Image

ROOT = Path('/workspace/his-office-pinterest/products')
DESKS = ROOT / 'standing-desk-candidates'
WALLS = ROOT / 'wall-finish-candidates'

def asset(path, url, description, inspected=True):
    b = path.read_bytes()
    record = {'path': str(path), 'url': url, 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b), 'description': description, 'original_bytes': True, 'visually_inspected': inspected}
    try:
        with Image.open(path) as im:
            record.update({'pixels': list(im.size), 'format': im.format})
    except Exception:
        pass
    return record

branch = json.loads((DESKS/'branch-tria.json').read_text())
variant = next(v for v in branch['variants'] if v['id'] == 43180424921123)
desk_photo_url = 'https://www.branchfurniture.com/cdn/shop/files/Tria_SD_2026June_Branch_0026_V1_1_-_Copy.webp'
glb_url = 'https://cdn.shopify.com/3d/models/e0b5641a34a57e99/FBX_Tria_Standing_Desk_48x27_Woodgrain_White.glb'
spec_url = 'https://www.branchfurniture.com/cdn/shop/files/specs-tria-standing-desk.pdf?v=6760253827135638948'
owned_area = 42*30*0.0254**2
comparison = {
    'research_date': '2026-10-08', 'status': 'Proposal references only; user choice pending. This does not replace selected-products.json or authorize model mutation.',
    'selection_rationale': 'Tria Black Oak/Charcoal is the architectural/coherent proposal with official product geometry. E7 Black 48×30 is the value and surface-area alternative. Neither is purchased.',
    'owned_baseline': {'name': 'UPLIFT Pheasantwood 42×30in', 'area_m2': owned_area, 'width_m': 42*0.0254, 'depth_m': 30*0.0254},
    'candidates': [
        {'id': 'branch_tria_black_oak_charcoal_48x27', 'brand': 'Branch', 'name': 'Tria Standing Desk', 'configuration': 'Black Oak laminate top / Charcoal powder-coated steel frame / nominal 48×27in',
         'url': 'https://www.branchfurniture.com/products/tria-standing-desk?variant=43180424921123', 'variant_id': variant['id'], 'sku': variant['sku'], 'price_usd': variant['price']/100, 'availability': {'official_shopify_available': variant['available'], 'shipping_destination_not_tested': True},
         'published_actual_top_inches': [47.2, 27], 'published_actual_top_m': [47.2*0.0254, 27*0.0254], 'top_area_m2': 47.2*27*0.0254**2, 'area_gain_over_owned_percent': (47.2*27/(42*30)-1)*100,
         'published_height_inches': [25.5, 48.9], 'published_height_m': [25.5*0.0254, 48.9*0.0254], 'capacity_lb': 275, 'warranty_years': 10,
         'features': ['dual-motor electric lift', 'three-stage columns', 'two memory presets', 'OLED keypad and USB-C port', 'collision detection', 'felt organizer and cable port'],
         'fit_notes': 'Compared with the owned top: 5.2in wider, 3in shallower, only 1.14% more area. Independent second bench supplies the larger working-area gain. Feet and full standing envelope must be checked against lamp, cat tree, bench and art.',
         'photo': asset(DESKS/'branch-tria-blackoak-charcoal-official.jpg', desk_photo_url, 'Official Black Oak/Charcoal finish photograph; depicted size is not independently established, so use official GLB/specification for dimension evidence.'),
         'specification': asset(DESKS/'branch-tria-specs.pdf', spec_url, 'Official Tria specification sheet; actual 47.2×27in top and 25.5–48.9in height.'),
         'geometry': {'asset': asset(DESKS/'branch-tria-official-48x27-woodgrain-white.glb', glb_url, 'Official nominal48×27 product GLB, originally Woodgrain/White; colors differ from Black Oak/Charcoal proposal.', False), 'measurements_file': str(DESKS/'branch-tria-geometry-measurements.json'), 'units': 'meters', 'native_axes': 'X width, Y up, Z depth, right handed', 'source_desktop_dimensions_m': [1.2000001669, .0254000425, .6850000918], 'source_tabletop_upper_surface_m': .7239438295, 'source_overall_dimensions_XYZ_m': [1.2000001669, .7261451081, .6941281259], 'feet_dimensions_width_depth_height_m': [.0800000429, .5999999642, .0300000496], 'feet_center_X_m': [-.5300005078, .5300000310], 'feet_center_Z_m': -.0045641363, 'column_width_depth_m': [.0600003, .09000015], 'source_rounding_note': 'CAD desktop1200×685mm differs by about1.1mm in width and0.8mm in depth from47.2×27in specification. Preserve official geometry and disclose source rounding; do not rescale the complete desk to nominal48in.', 'color_note': 'Rematerialization to Black Oak/Charcoal, if chosen, must be documented rather than described as an exact-color manufacturer GLB.'}},
        {'id': 'flexispot_e7_black_48x30', 'brand': 'FlexiSpot', 'name': 'E7 T-frame with Black laminate48×30in desktop',
         'url': 'https://www.flexispot.com/flexispot-pro-standing-desk-e7?value=cbr4830bd-e7bs', 'configuration': 'E7B_S black T-frame + Premium keypad + CBR4830B-D Black laminate desktop',
         'components': [{'sku': 'E7B_S', 'configurator_id': 70000, 'price_usd': 309.99}, {'sku': 'CBR4830B-D', 'configurator_id': 66031, 'price_usd': 100}], 'component_total_usd': 409.99,
         'price_basis': 'Exact enabled components in current official configurator SSR data. Their mutual exclusion lists permit this pairing. Cart/checkout destination not tested; price can change.',
         'availability': {'both_enabled': True, 'both_outOfStock': False, 'both_inventoryNumFlag': True, 'note': 'Graphite/Ebony48×30 alternatives exist but inventoryNumFlag=false, so they are not treated as equally ready.'},
         'top_inches': [48, 30], 'top_m': [48*.0254,30*.0254], 'top_thickness_inches': 1, 'top_area_m2': 48*30*.0254**2, 'area_gain_over_owned_percent': (48*30/(42*30)-1)*100,
         'frame_height_without_top_inches': [22.8,48.4], 'calculated_top_height_inches': [23.8,49.4], 'height_note': 'Height adds published1in desktop thickness; compare frame-only and top-height numbers consistently.',
         'capacity': {'page_lb': 355, 'current_E7_V3_manual_lb': 352, 'conservative_design_limit_lb': 352, 'note': 'Manual specifies160kg/352lb; current product-page copy says355lb. Preserve the difference.'}, 'warranty': {'frame_mechanical_electronic_years': 15, 'laminate_top_years': 2},
         'geometry_status': 'No verified manufacturer CAD or dimensioned foot length located in bounded research. T-foot form is established by official source photo/manual, but this candidate is not ready for a precise foot collision proof until actual dimensioned drawings or measurements are supplied.',
         'photos': [asset(DESKS/'flexispot-cbr4830b-d-component-angle.png', 'https://staticprod.site.flexispot.com/dev/trantor/attachments/d7e57f9a-b996-4d2c-aa0d-7ba58b15d542.png', 'Official Black laminate top component image; not an assembled desk photograph.'), asset(DESKS/'flexispot-e7b_s-frame-transparent.png', 'https://cnmegk4mhxmt.compat.objectstorage.us-phoenix-1.oraclecloud.com/prod-us2-bucket/trantor/attachments/US/e7bs-0103.png', 'Official exact black E7B_S frame component image.')],
         'manual': asset(DESKS/'flexispot-e7-v3-manual.pdf', 'https://s3.springbeetle.top/prod-common-bucket/commodity/item/E7-V3-US_MANUALET223IB-PRO-ZX01_20260421_C1pdhUwK.pdf', 'Current official E7-V3 US manual; image-only PDF; page2 reviewed visually.'), 'configuration_evidence': [str(DESKS/'flexispot-selected-e7b_s.json'),str(DESKS/'flexispot-selected-cbr4830b-d.json'),str(DESKS/'flexispot-e7-selected-black48x30-page.html')]}],
    'excluded_references': [{'name': 'Legacy Branch48×30 Standing Desk', 'reason': 'Current official URL redirects to Tria; older48×30 model is not the present product.'}, {'name': 'Herman Miller/Fully Jarvis bamboo', 'reason': 'Quality frame but bamboo reads warm against the new cool dark direction; exact dark48in configuration/price not established in this bounded comparison.'}],
    'budget_note': 'Adding Tria to previous checkpoint subtotal1571.90 gives2320.90 before wall treatment/tax/shipping; this is not the final cool-palette budget and any revised visitor chair/rug/storage may change it.'
}
(DESKS/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')

horizontal=json.loads((WALLS/'tempaper-horizontal.json').read_text())
blackroll=next(v for v in horizontal['variants'] if v['id']==42174227087542)
blackimg=blackroll['featured_image']['src']
panels=json.loads((WALLS/'woodupp-blackash.json').read_text());pv=panels['variants'][0]
wall_refs={
    'research_date': '2026-10-08', 'status': 'User chose BOTH B and C as separate designs. A retained as researched alternative. No purchases, installation, or room-model changes by product researcher.',
    'chosen_directions': ['B Charcoal + Slat Bay', 'C Ink Studio'],
    'placement_scope': 'Existing4.2m long white workwall behind the two independent desks only. Brick, window, closet and room openings retained.',
    'candidates': [
        {'direction': 'A Graphite Studio', 'id': 'tempaper_horizontal_black_raven', 'brand': 'Tempaper & Co.', 'name': 'Horizontal Faux Grasscloth Peel and Stick Wallpaper', 'color': 'Textured Black Raven',
         'url': 'https://tempaper.com/products/faux-horizontal-grasscloth-peel-and-stick-wallpaper?variant=42174227087542', 'primary_data_file': str(WALLS/'tempaper-horizontal.json'),
         'roll_options': [{'sku': 'HG5232', 'variant_id':42174227087542, 'price_usd':130, 'available': True, 'width_inches':20.5, 'length_ft':33, 'coverage_sqft':56.37}, {'sku':'HG15232','variant_id':42174216011958,'price_usd':65,'available':True,'width_inches':20.5,'length_ft':16.5,'coverage_sqft':28.18}],
         'material': 'Certified vinyl, self-adhesive and removable', 'match': 'Straight', 'vertical_repeat_inches':20.5, 'depth_note':'Thin wallcovering; manufacturer thickness not published in source.',
         'visual_notes':'Visually inspected original black horizontal woven texture. Low contrast and quiet; no Hoffmann geometric squares.',
         'installation':'Apply to smooth, clean, sound primed/painted eggshell, satin or semi-gloss surfaces. Fresh paint cures at least4weeks. Manufacturer recommends testing a sample and same-lot rolls; clean as specified with1:1water/alcohol. Peels off from a corner; underlying finish and adhesion still require real-wall sample verification.',
         'geometry_takeoff_note':'Room workwall is4.2m×3.02m nominal. Manufacturer recommends double rolls above8ft wall heights; calculate drop count and20.5in pattern repeat from verified installation height, rather than dividing area alone. No final roll quantity claimed.',
         'photo': asset(WALLS/'tempaper-horizontal-black-raven-original.jpg', blackimg, 'Original official Black Raven texture swatch, visually inspected.')},
        {'direction':'B Charcoal + Slat Bay','id':'woodupp_black_ash_black_felt','brand':'WoodUpp','name':'Akupanel Natural Wood Black Ash/Black Felt','sku':pv['sku'],'variant_id':pv['id'],'price_usd':pv['price']/100,'available':pv['available'],
         'url':'https://woodupp.com/products/akupanel-acoustic-panel-natural-wood-black-ash-black-felt-240-x-60-cm','dimensions_m':[.60,.022,2.40],'coverage_m2':1.44,'weight_kg':12.5,
         'materials':'MDF slats faced with real wood veneer; acoustic PET felt with50%recycled plastic. Natural grain/finish variation expected.',
         'chosen_design_quantity': 3, 'chosen_design_material_subtotal_usd': 584.85,
         'proposed_bay':'User chose B as one of two designs; root specified a bounded 1.8m-wide × 2.4m-high bay of three full-width panels behind the project bench. Material subtotal $584.85 excludes end trims/install/tax/shipping. The geometry/installation agent verifies final attachment and positioning.',
         'surrounding_workwall_color': {'brand':'Sherwin-Williams', 'name':'Peppercorn SW7674', 'hex':'#585858', 'rgb':[88,88,88], 'url':'https://www.sherwin-williams.com/en-us/color/color-family/neutral-paint-colors/SW7674-peppercorn', 'source':'Official ColorSnap RGB/HEX PDF', 'note':'Matte neutral charcoal color proposal surrounding the bay; paint system and final physical sample remain to specify.'},
         'room_impact':'Direct-wall installation projects22mm.2.4m-high panels beneath3.02m ceiling leave an intentional0.62m upper band rather than inventing3.02m product height. Additional battens/acoustic insulation increase projection if selected.',
         'installation':'Manufacturer specifies15screws per panel through felt, with appropriate plugs, or mounting adhesive. Either installation may leave wall damage; construction adhesive is not peel-and-stick/rental-removable. Check suitable substrate and attachment after user direction choice.',
         'acoustic_note':'Manufacturer ClassA claim requires its tested installation system; do not promise ClassA for simple direct mounting. Acoustic performance is not simulated in this proposal.',
         'visual_notes':'Original close-up reads cool gray-black and restrained. RusticGreyOak and Wood-like BlackOak samples read noticeably warmer; actual BlackAsh preferred.',
         'photos':[asset(WALLS/'woodupp-blackash-original-0.jpg','https:'+panels['images'][0],'Official overall product panel photo, not a room illustration.'),asset(WALLS/'woodupp-blackash-original-2.jpg','https:'+panels['images'][2],'Original official BlackAsh veneer/felt close-up.')],
         'source_page_file':str(WALLS/'woodupp-blackash-page.html'),'vendor_image_note':'Vendor environment filenames explicitly marked_AI were excluded; no AI lifestyle image is presented as real installed-room photography.'},
        {'direction':'C Ink Studio','id':'sherwin_williams_naval_sw6244','brand':'Sherwin-Williams','name':'Naval SW6244 paint color','url':'https://www.sherwin-williams.com/en-us/color/color-family/blue-paint-colors/SW6244-naval','rgb':[47,61,76],'hex':'#2F3D4C',
         'color_evidence':'RGB/HEX verified directly in the downloaded official ColorSnap PDF; primary Naval color page also downloaded.','rgb_source':'https://images.sherwin-williams.com/content_images/sw-pdf-sherwin-williams-colorc.pdf','source_page_file':str(WALLS/'sherwin-naval-page.html'),
         'chosen_scope':'Separate C design: plain deep ink-blue workwall, no slats. Existing brick, window, closet and all shared furniture geometry retained.',
         'paint_system_note':'Matte/flat finish is a design preference; actual paint line, primer/substrate preparation and quantity not selected. Requires repainting to restore a rental. Sample physical color under actual daylight and overhead light; RGB is screen reference only.'}],
    'rejected_or_conditional': [{'name':'Tempaper Hoffmann BlackSisal','reason':'Real current product but woven geometric-square motif is too busy beside existing brick.'},{'name':'Tempaper FauxBurlap Charcoal BU503','reason':'Old Lowe’s listing does not establish current manufacturer availability; Charcoal absent from current product configurator.'},{'name':'Tempaper HorizontalFauxGrasscloth TexturedNavy HG15226/HG5226','reason':'Current single and double rolls available=false; sample available only. Original navy swatch retained with OUTOFSTOCK filename, not purchase-ready.'},{'name':'Legacy WoodUpp ColoredCharcoal US listing','reason':'Current specific US URL404. EU listing is not evidence of current US fulfillment.'}],
    'lighting_note':'Use existing overhead light with a neutral/cool visual presentation and an optional evening wall wash. Existing fixture dimmability, exact CCT and illuminance are unverified; no new ceiling fixture or electrical change is selected.'
}
(WALLS/'wall-finish-proposals.json').write_text(json.dumps(wall_refs,indent=2)+'\n')
allrefs={'research_date':'2026-10-08','desk_comparison':str(DESKS/'comparison.json'),'wall_proposals':str(WALLS/'wall-finish-proposals.json'),'status':'B and C chosen as two separate designs. Prior selected-products.json is an earlier warm checkpoint pending canonical furniture promotion.'}
(ROOT/'dark-proposal-reference-index.json').write_text(json.dumps(allrefs,indent=2)+'\n')
print('Wrote proposal references, preserving all original photo bytes and prior selected products.')
