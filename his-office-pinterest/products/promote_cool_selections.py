import copy, json, hashlib
from pathlib import Path

ROOT = Path('/workspace/his-office-pinterest/products')
canonical = ROOT/'selected-products.json'
checkpoint_dir = ROOT/'checkpoints'
checkpoint_dir.mkdir(exist_ok=True)
checkpoint = checkpoint_dir/'selected-products-warm-uplift-checkpoint-2026-10-08.json'
if not checkpoint.exists():
    checkpoint.write_bytes(canonical.read_bytes())
    text_checkpoint = ROOT/'selected-products.txt'
    if text_checkpoint.exists():
        (checkpoint_dir/'selected-products-warm-uplift-checkpoint-2026-10-08.txt').write_bytes(text_checkpoint.read_bytes())
old = json.loads(checkpoint.read_text())
complements = json.loads((ROOT/'proposal-complements/cool-complements.json').read_text())
desk = json.loads((ROOT/'standing-desk-candidates/comparison.json').read_text())['candidates'][0]
walls = json.loads((ROOT/'wall-finish-candidates/wall-finish-proposals.json').read_text())
data = copy.deepcopy(old)
data.update({'version':'selected-shared-cool-furniture-two-directions-B-C-2026-10-08','scope':'User chose BOTH B and C as separate designs with shared dark/cool furniture. Primary owned UPLIFT replaced by actual Branch Tria Black Oak/Charcoal. Honeywell02E lamp and MUTTROS cat tree retained; no purchases.', 'design_palette':'Black oak/charcoal desk, black-brown project bench, gray-blue visitor upholstery, dark-brown/oak folded-clothes dresser, graphite rug and one muted modern art print. B adds Black Ash slats against Peppercorn charcoal; C is plain deep Naval blue. Existing brick and oak floor retained.', 'source_checkpoints':[str(checkpoint)], 'wall_finish_records_file':str(ROOT/'wall-finish-candidates/wall-finish-proposals.json'), 'lighting_note':walls['lighting_note']})
lookup={i['id']:i for i in old['items']}
retained_ids=['lagkapten-alex-black-components','grejig-shoes','branch-pro','black-frame-landscape']
retained=[copy.deepcopy(lookup[k]) for k in retained_ids]
for i in retained:
    i['selection_status']='Selected shared furniture for both B and C; not purchased.'
newdesk={'id':'branch-tria-black-oak-charcoal','category':'primary_standing_desk','name':'Branch Tria Standing Desk, Black Oak/Charcoal, nominal48×27in','selected_color':'Black Oak / Charcoal','sku':desk['sku'],'variant_id':desk['variant_id'],'price_USD':desk['price_usd'],'quantity':1,'line_total_USD':desk['price_usd'],'source_url':desk['url'],'price_checked_date':'2026-10-08','selection_status':'Selected shared primary desk for both B and C; not purchased.','dimensions_m_W_D_H':[1.2000001668930054,.685000091791153,.723943829536438],'dimensions_note':'1:1 supplier GLB desktop width/depth and seated top height. Published actualtop1.19888×.6858m differs by source rounding. Do not rescale to nominal48in.','published_actual_top_m':desk['published_actual_top_m'],'height_range_m':desk['published_height_m'],'capacity_lb':desk['capacity_lb'],'geometry':desk['geometry'],'official_photos':[desk['photo']],'availability_note':desk['availability'],'room_layout_authorization':{'desk_center_room_XY_m':[-6.915,-.131],'shift_from_prior_center_m':[.035,0],'basis':'Root-approved read-only supplier-foot fit proof. Other layout placements maintained by layout/model agent.'}}
newitems=[]
for c in complements['selected_complements']:
    i=copy.deepcopy(c)
    i['selected_color']=i.get('color','Charcoal')
    i['price_checked_date']='2026-10-08'
    i['line_total_USD']=i['price_USD']*i.get('quantity',1)
    i['official_photos']=[i['official_photo']]
    i['official_image_file']=i['official_photo']['file']
    i['selection_status']='Selected shared furniture for both B and C; not purchased.'
    if i['id']=='storklinta-dark-brown':
        preceding=lookup['storklinta-low-drawers']
        for k in ['storage_capacity_cuft','storage_capacity_m3','verified_inside_drawer_W_D_m','verified_drawer_pullout_m']:
            i[k]=preceding[k]
        i['installation_requirement_note']='Proper wall anchoring is mandatory installation. At most one drawer can open before Anchor/Unlock attachment; attachment permits more than one. Confirm suitable wall fixing/spacer against the brick or move dresser closer during installation. Render does not verify hardware reach.'
        i['fit_note']=i['installation_requirement_note']
    if i['id']=='rift':
        i['dimensions_m_W_D_H']=[*i['dimensions_m_W_L'],i['nominal_combined_thickness_m']]
        i['caster_compatibility_note']=lookup['ruggable-impasto-taupe']['caster_compatibility_note']
        i['caster_sources']=lookup['ruggable-impasto-taupe']['caster_sources']
    newitems.append(i)
artsrc=complements['selected_art'];a=artsrc['selected_70x100']
art={'id':'dan-hobday-richmond','name':'Desenio Dan Hobday Richmond print, native landscape100W×70Hcm','sku':a['articleNumber'],'variant_id':a['id'],'selected_color':'Muted grays, browns and greens','dimensions_m_W_D_H':[1,.001,.7],'dimension_note':'Native100×70cm landscape print; image2000×1400px.1mm paper depth is a render approximation, not a manufacturer measurement.','price_USD':a['campaignPrice'] if a.get('campaignPrice') is not None else a['price'],'quantity':1,'source_url':artsrc['source_url'],'price_checked_date':'2026-10-08','selection_status':'Selected shared one art print for both B and C; not purchased.','official_image_file':a['image_file'],'official_photos':[{'file':a['image_file'],'url':a['image_url'],'sha256':a['image_sha256'],'pixel_dimensions':a['actual_image_dimensions'],'pixels_edited':False,'visually_inspected':True}],'orientation_note':'Use native landscape original artwork; do not crop, rotate, mirror or stretch. Keep the printed white border and one retained black70×100frame oriented landscape.','placement_intent':'ONE print above project bench; positions verified by layout/model agent.','availability_note':f"Current official variant stock={a['stock']}; destination fulfillment/checkout not tested.",'source_evidence':complements['art_shortlist_record']}
art['line_total_USD']=art['price_USD']
data['items']=[newdesk,retained[0],newitems[2],retained[1],retained[2],newitems[0],newitems[1],art,retained[3]]
data['owned_keepers']=[i for i in old['owned_keepers'] if i['id']!='desk']
data['owned_history']=[i for i in old['owned_keepers'] if i['id']=='desk']
data['owned_history'][0]['design_status']='Owned UPLIFT retained as source history; replaced in current shared B/C room design.'
total=round(sum(i['line_total_USD'] for i in data['items']),2)
data['total_new_items_before_tax_shipping_USD']=total
data['budgets']={'shared_new_furniture_before_tax_shipping_USD':total,'B_panel_quantity':3,'B_panel_subtotal_USD':584.85,'B_shared_furniture_plus_panels_USD':round(total+584.85,2),'B_pending_costs':['Peppercorn paint quantity/paint system','panel end trims','substrate attachment/install','tax/shipping'],'C_shared_furniture_USD':total,'C_pending_costs':['Naval paint quantity/paint system and substrate preparation','tax/shipping'],'owned_keeper_purchase_cost_USD':0}
data['designs']={k:copy.deepcopy(next(x for x in walls['candidates'] if x['direction'].startswith(k+' '))) for k in ['B','C']}
data['price_note']='October8research price references. No purchases. Shared furniture subtotal counts each component project-bench assembly once and one Branch task chair. Paint quantity/cost pending actual takeoff.'
data['image_provenance_note']='Downloaded original supplier/retailer product-image bytes retained with source URLs and SHA256. Colors in photos guide visual appearance, not laboratory color matching. Supplier Tria GLB is Woodgrain/White; rematerialize to actual Black Oak/Charcoal finish with disclosure. No vendor AI room illustration presented as a real photograph.'
data['dimensions_note']='Use actual selected variants and supplierCAD; do not recolor old visitor shape. SupplierCAD source rounding is disclosed. Frame outside dimensions remain an assumption based on published molding profile, not verifiedCAD. Scan shell/layout and installation attachment checks are separate.'
canonical.write_text(json.dumps(data,indent=2)+'\n')
lines=['Selected shared B/C office products — 2026-10-08','No purchases. Previous warm UPLIFT selection preserved at '+str(checkpoint),'']
for i in data['items']:
    lines.append(f"{i['quantity']} × {i['name']} — ${i['line_total_USD']:,.2f} — {i['source_url']}")
lines += ['',f'Shared furniture: ${total:,.2f}',f'B: 3 Black Ash panels $584.85; furniture + panels ${total+584.85:,.2f}, paint/trims/install/tax/shipping pending.','C: same shared furniture; Naval paint quantity/cost pending.','B Peppercorn SW7674: RGB88,88,88 / #585858. C Naval SW6244: RGB47,61,76 / #2F3D4C.','Existing overhead light; neutral/cool presentation; optional evening wall wash. Dimming/CCT unverified.']
(ROOT/'selected-products.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'shared_furniture_USD':total,'B_furniture_plus_panels_USD':total+584.85,'canonical':str(canonical),'checkpoint':str(checkpoint)},indent=2))
