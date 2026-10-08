from pathlib import Path
import json, shutil, hashlib, copy
from PIL import Image
R=Path('/workspace/his-office-pinterest/products')
OLD=Path('/workspace/his-office-redesign/products/candidates')
old=json.loads((OLD/'selected-products.json').read_text())
ix={x['id']:x for x in old['items']}
def src(name):
 for fn in ['initial-source-extracts','additional-source-extracts','retained-source-extracts']:
  for s in json.loads((R/(fn+'.json')).read_text()):
   if s['id']==name:return s
 raise KeyError(name)
def page_price(name):
 s=src(name)
 for d in s['json_ld']:
  if isinstance(d,dict) and d.get('@type')=='Product':return d
 raise KeyError(name)
def photo_record(file,url,role='Official unmodified original retailer product photo'):
 p=R/'photos'/file
 return {'file':str(p),'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'pixel_dimensions':list(Image.open(p).size),'role':role,'pixels_edited':False,'visually_inspected':True}
def base(k,name,color,dims,price,qty,source,files):
 return {'id':k,'name':name,'selected_color':color,'dimensions_m_W_D_H':dims,'price_USD':price,'quantity':qty,'line_total_USD':round(price*qty,2),'source_url':source,'price_checked_date':'2026-10-08','currency':'USD','selection_status':'Design recommendation only; not purchased','official_photos':files,'nominal_dimensions_note':'Manufacturer nominal catalogue dimensions; not physically measured.'}
components=[]
for k,name,color,dims,price,qty in [('lagkapten-top-black','IKEA LAGKAPTEN tabletop','Black-brown',[1.4,.6,.034925],49.99,1),('alex-black-drawers','IKEA ALEX five-drawer unit','Black-brown',[.36,.58,.7],115,1),('adils-black-leg','IKEA ADILS leg','Black',[None,None,.7],7.5,2)]:
 s=src(k);d=page_price(k);rec=base(k,name,color,dims,price,qty,s['source_url'],[photo_record(k+'.jpg',s['download_url'])]);rec['sku']=d['sku'];rec['source_page_file']=s['html_file'];rec['availability_note']='Official page metadata lists InStock; destination-specific IKEA store and delivery availability not verified without ZIP.';components.append(rec)
desk=base('lagkapten-alex-black-components','IKEA LAGKAPTEN / ALEX / ADILS component project bench','Black-brown top and ALEX drawers; black ADILS legs',[1.4,.6,.73],179.99,1,'https://www.ikea.com/us/en/p/lagkapten-tabletop-black-brown-80487016/',[])
desk.update(components=components,office_storage='Five drawers in LEFT ALEX pedestal; two ADILS legs at RIGHT end; never add a second pedestal that narrows knee bay.',geometry={'top_W_D_m':[1.4,.6],'pedestal_W_D_H_m':[.36,.58,.7],'pedestal_count':1,'calculated_knee_width_before_leg_setback_m':1.04},limits='Honeycomb top is not suitable for a mounted screen stand. Use ordinary desk-foot monitor, not a clamp monitor arm. Retailer maximum evenly distributed load110lb, concentrated load33lb. Assembled height73cm nominal; retailer top thickness1 3/8in=34.925mm and adjustable legs can require leveling during assembly.',availability_note='All three real components verified individually at US retailer. There is no claimed exact single-drawer black bundle SKU. Rejected495.214.90 is a door cabinet;895.214.93 has two pedestals.')
items=[desk]
for k in ['storklinta-low-drawers','grejig-shoes','branch-pro']:
 x=copy.deepcopy(ix[k]);p=Path(x['official_image_file']);dest=R/'photos'/p.name;shutil.copy2(p,dest);s=src(k);d=page_price(k)
 x.pop('rank',None);x.pop('recommended_quantity',None);x['official_image_file']=str(dest);x['source_page_file']=s['html_file'];x['official_photos']=[photo_record(dest.name,x['official_image_urls'][0])];x['price_checked_date']='2026-10-08';x['line_total_USD']=round(x['price_USD']*x['quantity'],2);x['selection_status']='Retained recommendation from preceding office proposal; not an owned product, not purchased.'
 if k=='storklinta-low-drawers':
  x['installation_requirement_note']='Securely anchor as retailer requires. Anchor/Unlock permits more than one drawer open after anchoring; one drawer can open before anchoring. For layout, confirm suitable masonry fixing and any spacer required by gap to brick or move dresser closer to wall during installation.'
  x['limits']='Dedicated clothes dresser, not a work surface. Proper anchoring required for installation. At most one drawer opens before Anchor/Unlock wall attachment; attachment permits more than one.'
  x['availability_note']='Official metadata InStock; destination store and delivery availability not verified without ZIP.'
 elif k=='grejig-shoes':x['availability_note']='Official metadata InStoreOnly on2026-10-08; local IKEA stock unverified. Inside-closet fit and shoe height clearance remain conditional.'
 else:
  x['quantity']=1;x['line_total_USD']=499
  x['availability_note']='Exact Black mesh/StandardCylinder variant40553208840227 page permits ordering and metadata InStock; do not infer immediate shipment or local physical inventory.'
 items.append(x)
s=src('ekenaset-beige');v=base('ekenaset-beige','IKEA EKENÄSET armchair, Kilanda light beige','Kilanda light beige',[.64135,.78105,.758825],199,1,s['source_url'],[photo_record('ekenaset-beige.jpg',s['official_image_urls'][0])]);v.update(sku='305.334.93',regular_price_USD=299,source_page_file=s['html_file'],metric_catalog_nominal_W_D_H_m=[.64,.78,.76],US_retailer_nominal_W_D_H_in=[25.25,30.75,29.875],seat_W_D_H_m=[.5588,.498475,.45085],armrest_height_m=.62865,material='Kilanda light beige woven polyester upholstery; dark-brown-stained solid beech arms/front rail with tinted clear lacquer.',availability_note='Clearance33%off, $199 vs$299, price valid fromSeptember30,2026 while supply lasts. Local stock/delivery unverified without ZIP.',function='Compact firm visitor lounge chair; it is not the second task chair.',official_image_file=str(R/'photos/ekenaset-beige.jpg'))
items.append(v)
s=src('ruggable-impasto-taupe');url='https://cdn.shopify.com/s/files/1/1033/0751/files/impasto-taupe-A-FLW-BT016-69_12e09309-6359-4602-876f-81c9a9893eaf.jpg?v=1771369540'
v=base('ruggable-impasto-taupe','Ruggable Impasto Taupe Flatwoven6×9ft + StandardPad','Taupe Beige / cream / ivory',[1.8288,2.7432,.005175],369,1,'https://ruggable.com/products/impasto-taupe-rug?variant=42112443547703',[photo_record('ruggable-impasto-taupe-6x9.jpg',url)]);v.update(sku='RUG-SYS-IND-RCT-CHN-BT016-06x09',variant_id=42112443547703,source_page_file=s['html_file'],official_image_file=str(R/'photos/ruggable-impasto-taupe-6x9.jpg'),style='Low-contrast abstract paint texture in taupe, cream, ivory and gray; no tassels/fringe.',material='Flatwoven polyester cover2mm + StandardPad1/8in=3.175mm; nominal combined5.175mm is calculated, uncompressed.',caster_compatibility_note='Manufacturer office-rug guide recommends low-pile FlatwovenTwoPiece for rolling chairs; StandardPad page says low profile works under rolling furniture. Select StandardPad, not cushioned pad. Actual caster feel and flat installation still require on-site check.',caster_sources=['https://ruggable.com/collections/office-rugs?page=4','https://ruggable.com/products/standard-rug-pad'],availability_note='Exact6×9standardpad system InStock metadata; made to order, site currently says1–2weeks shipping, subject to change.',function='Same full two-workstation6×9ft footprint as checked plan; cover both chair caster envelopes and pullback area.')
items.append(v)
s=src('art-abstract-scenery');url='https://media.desenio.com/site_images/685b32d320f7978d2595cbb3_1774051928_14699-1.jpg'
v=base('art-abstract-scenery','Desenio Abstract Scenery No1 Print,70×100cm mounted landscape','Cream / beige / muted brown',[1.0,None,.7],58.8,1,s['source_url'],[photo_record('art-abstract-scenery-100x70.jpg',url)]);v.update(sku='14699-1',regular_price_USD=98,source_page_file=s['html_file'],official_image_file=str(R/'photos/art-abstract-scenery-100x70.jpg'),orientation_note='True horizontal design, official selected image2000×1400pixels. Paper70×100cm displayed100cmwide×70cmhigh; retain printed white border; do not rotate the painting motif.',placement_intent='ONE wide restrained artwork above secondary project bench; blank wall above UPLIFT and above sealed fireplace.',availability_note='Selected14699-1 variant InStock; $58.80 sale vs$98 regular, priceValidUntilOctober 8, 2026. Print only; frame separate.')
items.append(v)
s=src('black-frame-landscape');v=base('black-frame-landscape','Desenio black wood frame,70×100cm used landscape','Black',[1.0254,.02286,.7254],101.15,1,s['source_url'],[photo_record('black-frame-landscape.jpg',s['download_url'])]);v.update(sku='AASP-50105',regular_price_USD=119,source_page_file=s['html_file'],official_image_file=str(R/'photos/black-frame-landscape.jpg'),picture_opening_m_W_H=[1.0,.7],published_molding_width_m=.0127,published_depth_m=.02286,outside_frame_dimensions_verified=False,dimension_note='Retailer molding width0.5in and depth0.9in published. Picture70×100cm is confirmed by retailer image. Exterior dimensions1.0254×.7254m assume full molding added outside opening, relation not dimensionedCAD.',material='Solid yellow poplar painted black, acrylic front; rear metal hangers permit both portrait and landscape.',availability_note='Selected frame InStock; sale$101.15 vs$119 validOctober 8, 2026.')
items.append(v)
keepers=json.loads(Path('/workspace/his-office-redesign/products/keepers/keepers-research.json').read_text())
owned=[]
for key in ['desk','lamp','cat_tree']:
 prod=copy.deepcopy(keepers['products'][key]);selected=[]
 for im in prod['primary_images']:
  p=Path(im['file']);dest=R/'photos'/p.name;shutil.copy2(p,dest);selected.append(photo_record(dest.name,im['url'],im.get('role','Existing keeper appearance reference')))
 prod['official_photos']=selected;prod['primary_images']=selected;prod['owned_status']='User explicitly asked to keep; excluded from new-piece budget.'
 for k in list(prod):
  if k.startswith('saved_'):prod.pop(k)
 if key=='lamp':prod['forms']='OPEN rectangular head with empty center and two narrow LED bars on perimeter; white U-shaped floor base, slim rectangular post and rotary knob. Never turn head into a solid diffuser slab.'
 owned.append({'id':key,**prod})
result={'version':'pinterest-quiet-warm-modern-office-2026-10-08','scope':'Adult clean office revision. Retain user42×30UPLIFT desk, Honeywell02E lamp and MUTTROS cat tree. Real product appearances support the geometry-frozen Blender room; no purchases.','design_palette':'Warm white architecture, existing red-brown brick and oak floor, Pheasantwood/dark wood, charcoal black, warmstone/beige; no blue/teal graphic accent pieces.','items':items,'owned_keepers':owned,'research_date':'2026-10-08','date_timezone':'America/New_York','total_new_items_before_tax_shipping_USD':round(sum(x['line_total_USD'] for x in items),2),'price_note':'US advertised prices checked October 8, 2026; sales/local availability can change. Includes 1 Branch task chair, 1 landscape print + 1 frame, 3 GREJIG shoe racks. Owned keepers excluded. No purchases.','dimensions_note':'Nominal manufacturer dimensions or explicitly calculated values; model and measured-plan control room geometry/placement. Scan uncertainty and conditional closet internals remain.','image_provenance_note':'All source photos are original downloaded or byte-identical reused originals. No photo pixels altered. Reused keeper/Branch/STORK/GREJIG photos carry originalretailerURL+SHA256.','rejected_candidates':[{'id':'lagkapten-alex-black-49521490','reason':'Single DOOR cabinet, not five drawers. Not selected.'},{'id':'lagkapten-alex-black-89521493','reason':'Two pedestal units reduce open knee width. Not selected.'},{'id':'art-monochrome-mist','reason':'Actual portrait photograph does not match desired single wide format. Not selected.'}]}
(R/'selected-products.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
lines=['PINTEREST OFFICE PRODUCT SELECTION — October 8, 2026','US advertised prices before tax/shipping; recommendations only, no purchases.','']
for i in items:
 lines.extend([f"{i['name']} — {i['selected_color']}",f"Quantity {i['quantity']} × ${i['price_USD']:,.2f} = ${i['line_total_USD']:,.2f}",i['source_url']])
 for c in i.get('components',[]):lines.append(f"  {c['name']}: quantity {c['quantity']}×${c['price_USD']:,.2f}: {c['source_url']}")
 lines.append(i.get('availability_note',''))
 lines.append('')
lines.extend([f"TOTAL ${result['total_new_items_before_tax_shipping_USD']:,.2f}",'Closet shoe fit conditional. Anchor dresser asrequired. Flatwoven+StandardPad selected for rolling taskchairs. LAGKAPTEN uses ordinary monitor foot, no clamp stand.'])
(R/'selected-products.txt').write_text('\n'.join(lines)+'\n')
manifest=[]
for p in sorted((R/'photos').iterdir()):manifest.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'pixel_dimensions':list(Image.open(p).size),'pixels_edited':False})
(R/'photo-manifest.json').write_text(json.dumps({'research_date':'2026-10-08','files':manifest},indent=2)+'\n')
print('Selected types',len(items),'Total',result['total_new_items_before_tax_shipping_USD'],'Photos',len(manifest))
