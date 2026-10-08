"""Seal reviewed model proofs and explicitly supplied final circulation proof."""
import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone

BASE=Path('/workspace/his-office-pinterest');QA=BASE/'qa/final-variants'
if len(sys.argv)<2:raise SystemExit('Supply final circulation JSON path after independent review')
route=Path(sys.argv[1]);routing=json.loads(route.read_text())
names=['b-charcoal-slat','c-ink-studio'];records=[]
for name in names:
 q=QA/name;m=BASE/'variants'/name/'model';layout=json.loads((m/'layout.json').read_text())
 read=lambda f:json.loads((q/f).read_text())
 mesh=read('integrated-mesh-checks.json');protected=read('protected-source-parity.json');supplier=read('tria-supplier-parity.json')
 motion=read('tria-height-operation.json');chair=read('owned-chair-motion.json');support=read('composition-support-checks.json')
 exports=read('export-parity.json');textures=read('texture-panel-checks.json');materials=read('material-availability.json')
 blend_hash=hashlib.sha256((m/'his-office-design.blend').read_bytes()).hexdigest();layout_hash=hashlib.sha256((m/'layout.json').read_bytes()).hexdigest()
 route_variant=next(v for v in routing['variants'] if v['variant']==name)
 route_cases=[case for profile in route_variant['profiles'] for case in profile['cases']]
 nominal60=[c for case in route_cases for c in case['routing_checks'] if c['person_circle_diameter_m']==.6]
 all_passing=[c for case in route_cases for c in case['routing_checks'] if c['route_pass']]
 assertions={
  'all17canonical_roots':len(layout['items'])==17 and mesh['all_roots_match_canonical'],
  'native_assembly_no_unintended_surface_crossings':mesh['unintended_surface_intersection_count']==0,
  'all_original_architecture_keeper_world_geometry_UVs_unchanged':protected['all_original_geometry_unchanged'],
  'retained_Honeywell_cat_materials_unchanged':protected['all_keeper_materials_unchanged'],
  'only_eight_authorized_wall_materials_changed':protected['intentional_two_wall_whitelist_changes_only'] and len(protected['fixed_material_changes'])==8,
  'all_supplier_Tria_components_unscaled':supplier['all_supplier_components_unscaled_and_correctly_positioned'],
  'full_published_stroke_includes_monitor_mat_ownedchair_ledge':motion['all_tested_external_clearance_pass'] and not motion['excluded_pending_task_chair_meshes'] and len(motion['whole_range_swept_candidates'])==0,
  'owned_chair_45cm_pullback_transfer_full_turn':chair['one_task_chair'] and chair['all_sampled_motion_pass'],
  'actual_mat_books_lamp_plant_supports_and_supplier_forms':support['all_composition_supports_pass'],
  'all_native_geometry_present_in_corrected_export':exports['all_native_product_and_architecture_meshes_present_with_correct_actual_bounds'],
  'furniture_layer_full_composite_geometry_parity':exports['all_layer_meshes_present_and_bound_identical'],
  'export_material_assignments_constants_match':exports['all_exported_material_constants_and_assignments_match'],
  'selected_original_rug_art_JPEG_bytes_and_UVs':exports['all_selected_rug_and_art_original_JPEG_bytes_preserved'] and textures['all_selected_texture_orientations_pass'],
  'all_active_images_available_and_packed':materials['all_used_image_nodes_available'] and all(x['packed_bytes']>0 for x in materials['records']),
  'variant_panel_envelope':textures['panels']['pass'],
  'all_native_proof_hashes_current':all(d.get('current_sha256',d.get('source_sha256'))==blend_hash for d in [mesh,protected,supplier,motion,chair,support,textures,materials]),
  'all_proof_layout_hashes_current':all(d.get('layout_sha256',d.get('canonical_layout_sha256'))==layout_hash for d in [mesh,supplier,motion,chair,support,exports,textures]),
  'final_route_proof_cites_current_layout_and_native_proxy':route_variant['layout']['sha256']==layout_hash and route_variant['chair_native_source_blend_sha256']==blend_hash,
  'normal_maxarm_working_pulled_nominal60cm_paths_pass':len(nominal60)==4 and all(c['route_pass'] for c in nominal60),
  'every_passing_route_has_validated_continuous_witness':all(c['path_witness']['witness_found'] and c['path_witness']['exact_free_space_covers_witness'] for c in all_passing),
 }
 if not all(assertions.values()):raise SystemExit('Failed proof requirements: '+str({k:v for k,v in assertions.items() if not v}))
 files={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in m.iterdir() if p.name in ['his-office-design.blend','layout.json','his-office-design.glb','his-office-furniture.glb','his-office-shell.glb','his-office-door-leaves.glb','camera-poses.json','tria-component-map.json']}
 evidence={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in q.glob('*.json')}
 records.append({'variant':name,'assertions':assertions,'files':files,'evidence_sha256':evidence,'mesh_counts':{'native':mesh['mesh_count'],'integrated':exports['files'][0]['mesh_node_count'],'furniture':exports['files'][1]['mesh_node_count']}})
shared=json.loads((QA/'shared-B-C-layout-parity.json').read_text());assert shared['all_shared_layout_and_world_bounds_pass']
out={'status':'PASS FOR FROZEN MODELED GEOMETRY AND NOMINAL OPERATION, SUBJECT TO EXPLICIT FIELD CHECKS','sealed_UTC':datetime.now(timezone.utc).isoformat(),
 'variants':records,'shared_layout_and_geometry_proof_sha256':hashlib.sha256((QA/'shared-B-C-layout-parity.json').read_bytes()).hexdigest(),
 'circulation_proof_file':str(route),'circulation_proof_sha256':hashlib.sha256(route.read_bytes()).hexdigest(),
 'circulation_review':'Independent route proof reviewed separately before invoking this seal; documented60cm planning-circle paths, not real-world accessibility/installation certification.',
 'images_status':'Photographic concepts require separate visual QA; this model seal is not image-based metric validation.',
 'limits':[
 'Room surfaces are generalized from the original Polycam record with typical5–12cm uncertainty. Exact supplier/export equality is an authored-coordinate check, not site accuracy.',
 'Owned AeronSizeC/Mineral is a manufacturer-photo/spec-guided proxy. Actual vintage/options/arm/cylinder/caster settings are unconfirmed; normal/max-arm planning bounds and stated displayed pose are distinguished.',
 'Nominal60cm route has little spare tolerance; dresser draws and full chair pullback are sequential operations. No accessibility/code or real shoulder-width guarantee.',
 'Tria stroke proof translates supplier upper parts/equipment/mat byfullheight andmiddle stages byhalf. Mechanism load/stability, realhuman body, cables, hatch operation and equipment changes are not simulated.',
 'HoneywellUbase detail/catbranch reach are photo-derived and must be measured onsite; closet interior/rack fit and door swings remain conditional/inferred.',
 'Anchor STORKLINTA per IKEA instructions: at most one drawer can open before attachment, proper Anchor/Unlock attachment permits multiple. The modeled87mm rear gap needs an approved brick spacer/fixing or dresser repositioning at installation.',
 'Wall ledge/frame fasteners, substrate/baseboard detail, electrical outlet/cord reach and book loads require site verification. Books/tray/plant are illustrative.',
 'FADO body preserves supplier239.9mm diameter/236.5mmheight1:1; US catalog254mm/228.6mm differs. Separate illustrative cord is not included in globe sizing.',
 'Palm proxy envelope actual230×221×279.83mm fits the declared280mm crown allowance, with a0.43mm rachis cap-height overshoot explicitly recorded; live plant dimensions are not guaranteed.',
 'Soft5.2mmrug-pad contacts with feet/casters are expected; compression is not simulated. Procedural detail differs between Blender/coreglTF; source photographic JPEGs retain exact bytes, recorded floor/brick PNGs are JPEG95 reencoded.'
 ]}
(QA/'final-model-QA.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(QA/'final-model-QA.json'),'status':out['status'],'variants':[x['variant'] for x in records]}))
