from pathlib import Path
import json,hashlib,datetime
b=Path('/workspace/his-office-redesign'); q=b/'qa'
hashf=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
final='607e11d67b8fc8813da0872b5f18278733c6a40cd9e1988c3b1cb743971ada0a'
assert hashf(b/'model/his-office-design.blend')==final
r=json.loads((q/'QA-REPORT.json').read_text())
r['timestamp_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
r['source_scene_sha256']=final
r['scope']='Fresh His-office redesign, frozen canonical layout. Independent read-only geometry, operation, material/export and browser camera/keyboard checks, plus separate nonmetric visual concept and document reviews.'
s=r['summary']; s.update(native_evaluated_meshes=271,exported_integrated_mesh_nodes=270,exported_furniture_mesh_nodes=188)
s.pop('all_187_furniture_layer_meshes_present_with_identical_bounds_in_integrated',None)
s['all_188_furniture_layer_meshes_present_with_identical_bounds_in_integrated']=True
s['native_and_current_viewer_lamp_13_aperture_and_positive_control_rays_pass']=True
s['lamp_exact_left_center_native_three_raycast_hits']=True
s['lamp_exact_left_center_accelerated_BVH_precision_miss']=True
s['all_three_final_concept_views_pass_nonmetric_visual_QA']=True
s['final_pdf_9_pages_14_links_no_overflow_or_draft']=True
r['limits']=[x.replace('has5–12cm','has 5–12 cm').replace('but~34 cm','but ~34 cm').replace('8.7cm','8.7 cm') for x in r['limits']]
r['limits'] += [
 'Generated concepts preserve visual topology and facing, but do not validate metric dimensions; fine silhouettes, materials and lighting are representative. View B retains one cosmetic secondary-tabletop spot/grommet absent from the modeled IKEA top.',
 'At one exact triangulation-edge LED probe the accelerated viewer BVH misses while native THREE raycasting returns two hits. Both offset LED positive controls, nine empty aperture rays and both rim controls pass; the exported bar is valid. This is documented numerical ray precision, not a product geometry gap.'
]
proofs=['window-calibration-check.json','integrated-mesh-checks.json','export-parity.json','material-availability.json','routing-analysis.json','operation-clearances.json','desk-height-operation.json','chair-pullback-operation.json','fireplace-recess-check.json','lamp-aperture-check.json','viewer-independent-checks.json','viewer-lamp-aperture-check.json','image-QA.json','image-QA.txt','pdf-layout-check.json']
r['proofs']=[{'file':n,'sha256':hashf(q/n)} for n in proofs]
r['current_assets']=[{'file':str(p.relative_to(b)),'sha256':hashf(p)} for p in [b/'model/his-office-design.blend',b/'model/his-office-design.glb',b/'model/his-office-furniture.glb',b/'viewer-source/tests/final-asset-proof.json']]
for n in ['integrated-mesh-checks.json','material-availability.json','desk-height-operation.json','chair-pullback-operation.json','fireplace-recess-check.json','lamp-aperture-check.json']:
 assert json.loads((q/n).read_text())['source_sha256']==final,n
parity=json.loads((q/'export-parity.json').read_text()); assert parity['all_layer_meshes_present_and_bound_identical']
for f in parity['files']: assert hashf(Path(f['file']))==f['sha256'],f['file']
a=json.loads((q/'viewer-lamp-aperture-check.json').read_text()); assert a['allRaysPass'] and not a['errors'] and len(a['centerDiagnostic']['baselineHits'])==2
print('Final assets and native/current-runtime proofs match.')
(q/'QA-REPORT.json').write_text(json.dumps(r,indent=2)+'\n')
text='''HIS OFFICE REDESIGN — INDEPENDENT FIT QA
PASS FOR NOMINAL MODELED FIT; FIELD VERIFICATION REQUIRED

The frozen layout preserves the measured metric room and corrected rear window, rear door, closet/cupboard, radiator and recessed fireplace. Blender [X,Y,Z] exports to GLTF [X,Z,-Y] without rescaling or mirroring. All 14 product roots match the canonical layout. All 188 furniture-layer meshes, including the provisional closet support, exist with identical world bounds in the integrated GLB. Its 270 mesh nodes exclude only the presentation sky from 271 native meshes.

Actual evaluated component tests find zero unintended cross-product, wall, fixed-fixture or closed-door triangle intersections. Expected thin soft rug-pad contacts are separately documented. All 32 used image nodes have available pixel data and packed/existing backing files; exported GLB images are embedded. Four browser viewpoints agree with the frozen layout and restored materials. All four clear starts accept actual W input and move, with zero page errors. Native and exported-viewer fireplace topology each passes 13 rays: white infill lies 11.3 cm behind the brick face.

The corrected Honeywell head has two narrow LED bars surrounding an empty center within unchanged product bounds. Native and current runtime tests each pass nine empty-aperture rays plus four LED/rim positive controls. One exact left-bar triangulation-edge probe misses the accelerated BVH but hits twice with unpatched THREE raycasting. Offset probes hit both bars. This numerical precision diagnostic does not indicate missing exported geometry or require a model change.

Two workstations: main desk faces room (-Y), both task chairs face their work surfaces (+Y); secondary ALEX pedestal is on the left, with about 89.5 cm modeled knee bay to the right legs. Both full 70.104 cm caster circles stay on the 6×9 rug at work and after 45 cm pullback. Actual chair meshes show no unintended triangle crossings at 17 pullback steps; the only swept candidate is the main chair/keypad. A conservative 50 cm planning-person route connects entry and rear door in both states; 55 cm fails. This is a tight nominal plan, not a surveyed human-clearance or compliance claim.

The clothes dresser's verified 27.62 cm drawer travel leaves about 79 cm to main caster in working position, about 34 cm with chair fully pulled back. Tuck the chair for drawer access. Nominal approach offsets include dresser/rear-door box 3.1 cm, secondary desk/closet approach 5 cm, visitor/hearth buffer 8.9 cm and visitor/entry approach 12.9 cm. These planning boxes are not measured swing envelopes. Selected STORKLINTA requires Anchor/Unlock wall fixing; its model sits about 8.7 cm forward of the corrected brick face. Approved masonry attachment/spacer or final on-site position must be verified; mounting hardware is not modeled.

Owned-product checks: modeled lamp U-base clears desk steel foot by about 11 cm; low cat basket lies about 15.3 cm below seated tabletop underside (about 7.5 cm at lowest official height). Upper desk assembly/equipment swept bounds over 66.167–131.191 cm nominal top height do not overlap cat/lamp/fixed surfaces. The only swept candidate was keypad/chair; 33 evenly spaced heights plus current/mid/endpoints showed no triangle crossings. This verifies external proxy clearance, not cables, actuator internals, loading or stability.

All three untouched final generated PNGs pass concept visual review against model cameras, companion angles and selected real product photos. Room features, workstation fronts/chair facing, left ALEX knee bay and opposite-wall artwork remain coherent. A has the corrected open lamp head; B retains one cosmetic secondary-tabletop spot/grommet; C preserves the shallow brick course within the chimney footprint. Generated pixels do not establish metric dimensions. Image-QA records accepted file hashes and visual limits.

The final review PDF independently passes document checks: nine pages, 14 clickable source links, no draft labels or out-of-page text, and matching budget/operation qualifications. Product-card and sources-page layout were visually inspected.

Limits requiring field checks: room outline is generalized by 5–12 cm; actual cat-tree branch/basket offsets and lamp U-base shape are unpublished; top basket proxy is only about 2 cm off rear wall; door hinges/swings are inferred; closet interior and hanging hems are unrecorded. Confirm these before installation and rotate/reposition the owned pieces as needed. Three GREJIG racks are provisional behind the observed closed closet. Rug compression is not simulated. Triangle-surface tests do not rule out every fully contained solid, and sampled operation candidates do not mathematically prove every intermediate state. Numerical export tolerances are not site accuracy.

Authoritative proofs:
'''
text+=''.join('  '+n+'\n' for n in proofs)
text+='\nFrozen native scene SHA256: '+final+'\n'
(q/'QA-REPORT.txt').write_text(text)
print(json.dumps({'report_sha256':hashf(q/'QA-REPORT.txt'),'json_sha256':hashf(q/'QA-REPORT.json'),'scene_sha256':final}))
