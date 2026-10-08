import copy, hashlib, json
from pathlib import Path
from PIL import Image

ROOT=Path('/workspace/his-office-pinterest/products')
DIR=ROOT/'owned-chair'

def asset(name,url,description,inspected=False):
    path=DIR/name
    b=path.read_bytes()
    x={'file':str(path),'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'description':description,'pixels_edited':False,'visually_inspected':inspected}
    try:
        with Image.open(path) as im:x['pixel_dimensions']=list(im.size)
    except Exception:pass
    return x

ref=json.loads((DIR/'aeron-mineral-size-c-reference-variant.json').read_text())
photo=asset('aeron-c-mineral-official.png',ref['image'],'Original official product photo attached to exact current Mineral/Satin Aluminum Size C reference SKU100099909. Owned base polish/back/arm/caster options are not confirmed.',True)
cad_prefix='https://www.hermanmiller.com/content/dam/hmicom/app_assets/product_models/a/aeron_chairs/aeron_chair_c_size_fully_adjustable_arms/'
cad_assets=[]
for name in ['HMI_Aeron_Chair_C_Size_Fully_Adjustable_Arms.skp','HMI_Aeron_Chair_C_Size_Fully_Adjustable_Arms_3D.dwg','HMI_Aeron_Chair_C_Size_Fully_Adjustable_Arms_2D.dwg']:
    cad_assets.append(asset(name,cad_prefix+name,'Original supplier Size C Fully Adjustable Arms planning asset from current primary Aeron professional resources page; not converted or geometrically measured.'))
record={
    'id':'aeron-size-c-mineral','category':'owned_primary_task_chair','name':'Owned Herman Miller Aeron Large / Size C, Mineral light gray','brand':'Herman Miller','owned_status':'Already owned by user; no chair purchase','quantity':1,'price_USD':0,'line_total_USD':0,
    'user_confirmed':{'model':'Aeron','size':'Large / Size C','finish':'Light gray / Mineral'},
    'unconfirmed_owned_details':['Classic versus Remastered vintage','base material/polish','arm-adjustability configuration','back support configuration','caster surface specification','cylinder-height option'],
    'source_reference':{'source_url':ref['offers']['url'],'reference_sku':ref['sku'],'reference_configuration':ref['name'],'reference_only_note':'Current manufacturer remastered-family Mineral Size C reference; do not identify the owned chair as this exact SKU or vintage. No price is used because the chair is owned.'},
    'source_url':ref['offers']['url'],'selected_color':'Mineral light gray','official_image_file':photo['file'],'official_photos':[photo],
    'dimensions_m_W_D_H':[.71882,.71882,1.0922],
    'dimensions_note':'Current manufacturer Size C normal-width/max-depth and retail43in nominal height for display. Final pose height derives from seat-height setting. This is a source-guided proxy envelope, not measurements of the actual owned chair.',
    'manufacturer_specs':{
        'source_url':'https://www.hermanmiller.com/products/seating/office-chairs/aeron-chair/specs/',
        'source_file':str(DIR/'aeron-specs.html'),
        'fully_adjustable_arm_model':{'overall_height_inches':[40,45.4],'overall_height_m':[1.016,1.15316],'overall_width_inches':[28.3,31.6],'overall_width_m':[.71882,.80264],'overall_depth_inches':[27.5,28.3],'overall_depth_m':[.6985,.71882],'seat_depth_inches':18.5,'seat_depth_m':.4699,'seat_height_inches':[15.8,22.8],'seat_height_m':[.40132,.57912],'arm_height_above_seat_inches':[7.5,11.5],'arm_height_above_seat_m':[.1905,.2921]},
        'notes':'Width varies with arm configuration/position. These current manufacturer ranges vary by cylinder/arm options; actual owned settings are not established. Overall-depth range is the correct room-fit reference;18.5in is seat pan, not overall chair depth.'},
    'retail_reference_specs':{'source_file':str(DIR/'aeron-mineral-size-c-store.html'),'normal_width_inches':28.25,'base_diameter_inches':26.5,'base_diameter_m':.6731,'caster_diameter_inches':2.5,'caster_diameter_m':.0635,'seat_height_inches':[16,20.5],'seat_height_m':[.4064,.5207],'nominal_height_inches':43,'nominal_height_m':1.0922,'difference_note':'Retail normal width28.25in versus professional nominal28.3in is rounding. Retail standard-cylinder seat travel differs from professional available-cylinder range; preserve both sources.'},
    'collision_footprint_m':[.80264,.71882],'base_diameter_m':.6731,'caster_diameter_m':.0635,
    'fit_note':'Check chair transfer/turning with the maximum published expanded-arm envelope, plus ergonomic clearance; do not use seat-pan depth as floor footprint. Arm settings can be reduced for the transfer if actual user configuration supports it. Layout agent owns the resulting fit proof.',
    'geometry_source':{'official_assets':cad_assets,'source_page_url':'https://www.hermanmiller.com/products/seating/office-chairs/aeron-chair/pro-resources/','source_page_file':str(DIR/'aeron-pro-resources.html'),'source_subtype':'Aeron Chair C Size Fully Adjustable Arms','status':'Official original SketchUp/AutoCAD files downloaded. No directly advertised supplier GLB/OBJ/DAE/3DS located in bounded primary research; no successful conversion to Blender geometry yet.','units_note':'Native CAD units/bounds not yet decoded; do not assume SketchUp numeric coordinates are meters. Blender proxy must be scaled to verified published Size C envelope and disclosed until converted CAD is validated.','model_vintage_note':'Model files are currently published by manufacturer; SKU/photo references are current remastered-family. Source file or brochure does not prove the exact vintage/options of the owned chair.','preview':asset('aeron-c-official-cad-preview.jpg',cad_prefix+'HMI_Aeron_Chair_C_Size_Fully_Adjustable_Arms_mdl_c.jpg','Manufacturer generic supplier CAD preview, not Mineral finish photography.',True),'outline':asset('aeron-c-official-dimension-drawing.jpg','https://www.hermanmiller.com/content/dam/hmicom/page_assets/products/aeron_chair/202106/dim_prd_spc_aeron_chair_c_size_fully_adjustable_arms.jpg','Official C-size outline. Image itself has no dimension labels; numerical dimensions come from primary specs page.',True)},
    'source_evidence_files':[str(DIR/'aeron-mineral-size-c-reference-variant.json'),str(DIR/'aeron-mineral-size-c-store-jsonld.json'),str(DIR/'aeron-specs.html')],
    'research_date':'2026-10-08','selection_status':'User-confirmed owned model/size/finish. Reference options/vintage remain disclosed; no purchases or room-model changes by product researcher.'
}
(DIR/'owned-aeron-size-c-mineral.json').write_text(json.dumps(record,indent=2)+'\n')

# Preserve the proposed-chair selection; replace its purchase with a zero-cost owned record.
canonical=ROOT/'selected-products.json'
current=json.loads(canonical.read_text())
checkpoint=ROOT/'checkpoints/selected-products-cool-shared-with-proposed-branch-checkpoint-2026-10-08.json'
if not checkpoint.exists():checkpoint.write_bytes(canonical.read_bytes())
former=[x for x in current['items'] if x['id']=='branch-pro']
if former:
    current.setdefault('superseded_product_history',[]).extend(former)
current['items']=[x for x in current['items'] if x['id']!='branch-pro']
current['owned_keepers']=[x for x in current['owned_keepers'] if x.get('id')!='aeron-size-c-mineral']+[record]
total=round(sum(x['line_total_USD'] for x in current['items']),2)
current['version']='selected-shared-cool-furniture-B-C-owned-aeron-mineral-2026-10-08'
current['source_checkpoints']=list(dict.fromkeys(current.get('source_checkpoints',[])+[str(checkpoint)]))
current['total_new_items_before_tax_shipping_USD']=total
current['design_palette']=current['design_palette'].replace('one Branch task chair','owned Mineral Aeron Size C task chair')
current['scope']='Two separate B and C office designs share the actual Branch Tria desk, dark project bench/storage, gray-blue visitor chair and owned light-gray Mineral Aeron Size C. Owned Honeywell02E lamp and MUTTROS cat tree retained. No purchases.'
current['budgets']['shared_new_furniture_before_tax_shipping_USD']=total
current['budgets']['B_shared_furniture_plus_panels_USD']=round(total+584.85,2)
current['budgets']['C_shared_furniture_USD']=total
current['price_note']='October8 source research. No purchases. Owned Aeron costs$0 and replaces the proposed$499 Branch task chair; only eight new furniture/product assembly lines are counted. Paint quantities/costs and installation extras pending.'
canonical.write_text(json.dumps(current,indent=2)+'\n')
lines=['Selected shared B/C office products — owned Mineral Aeron update 2026-10-08','No purchases. Previous proposed Branch task chair preserved in checkpoint.','']
for x in current['items']:lines.append(f"{x['quantity']} × {x['name']} — ${x['line_total_USD']:,.2f} — {x['source_url']}")
lines += ['', 'Owned: Herman Miller Aeron Large/Size C, Mineral light gray — $0',f'Shared new furniture: ${total:,.2f}',f'B: panels$584.85; shared furniture+panels ${total+584.85:,.2f}, paint/trims/install/tax/shipping pending.','C: same shared furniture; Naval paint quantity/cost pending.','Chair source options/vintage are reference-only; exact owner cylinder/arm/caster settings are unresolved.']
(ROOT/'selected-products.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'owned_record':str(DIR/'owned-aeron-size-c-mineral.json'),'shared_USD':total,'B_furniture_plus_panels_USD':total+584.85,'preserved_checkpoint':str(checkpoint)},indent=2))
