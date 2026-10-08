#!/usr/bin/env python3
"""A source-photo design proposal, with no generated room imagery."""
import hashlib,json
from pathlib import Path
from PIL import Image
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

ROOT=Path('/workspace/his-office-pinterest')
OUT=ROOT/'images/composition-proposal'
W,H=1200,1410
pdfmetrics.registerFont(TTFont('DS','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
INK=HexColor('#202A32'); MUTED=HexColor('#53616B'); LINE=HexColor('#D9E0E3'); GOLD=HexColor('#92743B')
SOURCES={}
PDF=OUT/'Cohesive-office-composition-proposal.pdf'
c=canvas.Canvas(str(PDF),pagesize=(W,H))
c.setTitle('His office — cohesive composition proposal, B and C')
c.setAuthor('Design review prepared from original product and public Pin references')

def box(x,y,w,h,fill='#FFFFFF',stroke='#D9E0E3'):
 c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.roundRect(x,H-y-h,w,h,8,fill=1,stroke=1)
def txt(s,x,y,size=12,bold=False,color=INK):
 c.setFillColor(color);c.setFont('DB' if bold else 'DS',size);c.drawString(x,H-y-size,s)
def para(s,x,y,w,size=12,color=INK,leading=None):
 p=Paragraph(s,ParagraphStyle('p',fontName='DS',fontSize=size,leading=leading or size*1.38,textColor=color))
 _,h=p.wrap(w,1000);p.drawOn(c,x,H-y-h);return h
def photo(rel,x,y,w,h,url='',image_url='',role='Original source photograph'):
 path=ROOT/rel
 with Image.open(path) as im: pw,ph=im.size
 k=min(w/pw,h/ph);dw,dh=pw*k,ph*k
 c.drawImage(ImageReader(str(path)),x+(w-dw)/2,H-y-h+(h-dh)/2,dw,dh,mask='auto')
 SOURCES[str(path)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixel_dimensions':[pw,ph],
  'product_or_Pin_url':url,'original_image_url':image_url,'role':role,'pixels_edited':False,'placement':'Entire source image contained; no crop, palette edit or background removal'}
 if url:c.linkURL(url,(x,H-y-h,x+w,H-y),relative=0,thickness=0)
def link(s,url,x,y,size=9):
 txt(s,x,y,size,color=MUTED);c.linkURL(url,(x,H-y-size-3,x+pdfmetrics.stringWidth(s,'DS',size),H-y+1),relative=0,thickness=0)
def product(rel,name,detail,price,url,x,y,w,h,source_url=''):
 box(x,y,w,h);photo(rel,x+10,y+12,w-20,h-93,url,source_url)
 txt(name,x+12,y+h-74,12,True)
 para(detail,x+12,y+h-54,w-24,10.3)
 txt(price,x+12,y+h-25,11,True,color=GOLD)

txt('HIS OFFICE / COMPOSITION PROPOSAL',34,24,11,True,color=MUTED)
txt('A connected workspace, console and visitor corner',34,47,26,True)
para('Two coherent alternatives share one furnished plan. Real product photographs and inspiration images guide the next model revision.',34,86,1120,12.2)
zones=[('01  WORK','Two dark worktops, matching black ledges and a grouped landscape print. Proposed high shelf above the standing desk; lift clearance awaits QA. One owned Aeron serves both surfaces.'),
 ('02  CONSOLE','Folded-clothes storage doubles as a styled console: a white opal globe, small palm in a black pot and a modest reused tray.'),
 ('03  LOUNGE','Gray-blue bouclé, a charcoal graphic rug and natural wicker connect the visitor corner. Keep the floor route clear; no additional floor plant.')]
for i,(title,body) in enumerate(zones):
 x=34+i*381;box(x,122,370,112,'#F4F6F6');txt(title,x+14,136,13,True);para(body,x+14,160,342,10.7)

txt('WHOLE-ROOM REFERENCES / BORROW THE GROUPING',34,254,11,True,color=MUTED)
photo('research/cohesive-composition/full-dark-office-existing-reference.jpg',34,279,260,298,
 'https://www.pinterest.com/pin/488922103315018879/',
 'https://i.pinimg.com/736x/7e/a0/b6/7ea0b681287492b121c0555d738aa31b.jpg','Public Pin inspiration; geometry is not transferred')
photo('research/cohesive-composition/pins/moody-refined.jpg',309,279,190,298,
 'https://www.pinterest.com/pin/479703797832033753/',
 'https://i.pinimg.com/736x/b2/3e/0f/b23e0fecfba2fc6df75493f0232cb2ab.jpg','Public Pin inspiration; geometry is not transferred')
para('Borrow the shelf / art / light hierarchy and dark walls with white trim. Our measured room, products and clearances control the layout.',34,586,465,10.4)

box(526,254,309,363,'#F5F5F5');txt('B / CHARCOAL + SLAT BAY',542,269,14,True)
photo('products/wall-finish-candidates/woodupp-blackash-original-2.jpg',542,305,143,171,
 'https://woodupp.com/products/akupanel-acoustic-panel-natural-wood-black-ash-black-felt-240-x-60-cm',
 'https://cdn.shopify.com/s/files/1/0956/1561/5323/files/1013_akupanel_tonal_black_ash_black_felt_03.jpg?v=1777062017')
c.setFillColor(HexColor('#585858'));c.rect(698,H-305-112,121,112,fill=1,stroke=0)
txt('Peppercorn SW7674',698,428,9.8,True);txt('#585858',698,446,9.7)
para('Five Black Ash panels form a 3.0 m × 2.4 m bay across both desks. Peppercorn wraps the surrounding work wall and adjacent window wall.',542,493,277,11)
link('WoodUpp / Sherwin-Williams sources','https://www.sherwin-williams.com/en-us/color/color-family/neutral-paint-colors/SW7674-peppercorn',542,588,9)

box(852,254,314,363,'#F5F5F5');txt('C / NAVAL STUDIO',869,269,14,True)
c.setFillColor(HexColor('#2F3D4C'));c.rect(869,H-305-171,280,171,fill=1,stroke=0)
c.setFillColor(HexColor('#FFFFFF'));c.setFont('DB',17);c.drawString(886,H-365,'Naval SW6244')
c.setFont('DS',12);c.drawString(886,H-389,'#2F3D4C / smooth matte')
para('The same two-wall wrap in deep navy. Matching ledges, the exact Richmond print and the lit console create the composition without a slat bay.',869,493,280,11)
link('Official Sherwin-Williams color','https://www.sherwin-williams.com/en-us/color/color-family/blue-paint-colors/SW6244-naval',869,588,9)

txt('THE SHARED PALETTE / EXACT SELECTED SOURCES',34,637,11,True,color=MUTED)
items=[
 ('products/owned-chair/aeron-c-mineral-official.png','OWNED MINERAL AERON','Large / Size C. Already owned; current reference photo.','$0 / owned','https://store.hermanmiller.com/office-chairs-aeron/aeron-chair/100099909.html?lang=en_US'),
 ('products/proposal-complements/photos/ekenaset-axvall-gray-blue.jpg','GRAY-BLUE VISITOR','EKENÄSET / Axvall dark gray-blue; 65.1 × 74.0 × 74.9 cm.','$399','https://www.ikea.com/us/en/p/ekenaeset-armchair-walnut-effect-axvall-dark-gray-blue-50624326/'),
 ('products/proposal-complements/photos/rift-6x9.jpg','RIFT CHARCOAL RUG','6 × 9 ft Flatwoven + Standard Pad; quiet broken-stripe pattern.','$369','https://ruggable.com/products/rift-charcoal-rug?variant=42130480070711'),
 ('products/proposal-complements/photos/storklinta-dark-brown-product.jpg','DARK CLOTHES CONSOLE','STORKLINTA 3 drawers; 69.85 × 47.94 × 74.93 cm.','$149.99','https://www.ikea.com/us/en/p/storklinta-3-drawer-dresser-dark-brown-oak-effect-anchor-unlock-function-60559293/'),
 ('products/proposal-complements/art/dan-hobday-richmond-70x100-official.jpg','RICHMOND LANDSCAPE','Native 100 × 70 cm landscape print with black frame.','$107 print / $101.15 frame','https://desenio.com/p/posters-prints/featured-artists/dan-hobday/dan-hobday-richmond-print/')]
for i,item in enumerate(items):product(*item,34+i*228,661,220,221)

txt('FOUR COMPOSITION ADDITIONS / FIVE PIECES',34,905,11,True,color=MUTED)
add=[
 ('products/composition-pieces/mosslanda-black-original.jpg','TWO BLACK LEDGES','MOSSLANDA 115 × 12 cm. Bench top H1.25 m; high shelf top H2.10 m.','$39.98 / 2 × $19.99','https://www.ikea.com/us/en/p/mosslanda-picture-ledge-black-70292104/','https://www.ikea.com/us/en/images/products/mosslanda-picture-ledge-black__0634120_pe696314_s5.jpg'),
 ('products/composition-pieces/grovemade-darkgrey-mediumplus-original.jpg','PRIMARY DESK / FELT MAT','Dark Grey Medium Plus; 96.52 × 40.01 cm. Photo props not included.','$100','https://grovemade.com/product/wool-felt-desk-pad/?initial=683','https://grovemade.com/shop-static/shop/variant/grovemade-woolfelt-desk-pad-dark-deepmedium-galA-A1.jpg?_v=1631199017.5250502'),
 ('products/composition-pieces/fado-white-original.jpg','CONSOLE / OPAL LIGHT','FADO / KAJPLATS kit with remote; Ø25.4 × H22.86 cm; 4000 K option.','$44.98 / kit regular price','https://www.ikea.com/us/en/p/fado-kajplats-table-lamp-with-led-bulb-smart-color-and-white-spectrum-s29654971/','https://www.ikea.com/us/en/images/products/fado-table-lamp-white__0606976_pe682645_s5.jpg'),
 ('products/composition-pieces/sill-small-parlor-westcott-black-original.jpg','CONSOLE / SMALL GREENERY','Small Parlor Palm + Westcott black. Supplier plant height 6–11 in; crown varies.','$79 / plant + pot','https://www.thesill.com/products/parlor-palm?variant=41732265410665','https://cdn.shopify.com/s/files/1/0150/6262/files/the-sill_Small-Parlor-Palm_Small_Westcott_Black_Variant.jpg?v=1770151098')]
for i,(rel,name,detail,price,url,imurl) in enumerate(add):product(rel,name,detail,price,url,34+i*285,929,276,209,imurl)

txt('MEASURED ZONES / PROPOSED GROUPINGS',34,1158,11,True,color=MUTED)
plan=OUT/'composition-plan-only.png'
if not plan.exists():plan=OUT/'composition-plan.png'
photo(str(plan.relative_to(ROOT)),34,1181,641,194,role='Authored vector plan; actual room outline and saved furniture anchors, with proposed composition annotations')
txt('THE RESULT',700,1161,12,True)
para('A repeated black shelf finish links the two worktops. The slate print and blue-gray textiles soften the dark wrap; opal glass, Mineral mesh and white trim repeat light accents. Natural wicker and small greenery add warmth.',700,1185,458,10.5)
txt('C  $2,334.06      B  $3,308.81',700,1264,17,True,color=GOLD)
para('Core new furniture $2,070.10 + additions $263.96. B adds five panels $974.75. Paint, trims, mounting, installation, tax and shipping excluded. Owned items excluded.',700,1293,458,9.9)
para('Proposal before the revised model. Shelf fixing, lift clearance and console plant envelope need fit checks. Anchor STORKLINTA per IKEA instructions; verify brick fixing on site. Books/tray are illustrative reused objects. White ceiling, trim and brick stay.',700,1346,458,8.9)
txt('Original photos remain unchanged. Click photos for sources. Public Pin inspiration is not a measured layout or an authenticated Pinterest feed.',34,1391,8.6,color=MUTED)
c.showPage();c.save()
doc=fitz.open(str(PDF));page=doc[0];pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False)
PNG=OUT/'Cohesive-office-composition-proposal.png';pix.save(str(PNG))
manifest={'stage':'Concrete composition proposal before revised Blender build','alternatives':['B Charcoal + Slat Bay','C Naval Studio'],'original_photographs':SOURCES,
 'authored_color_swatches':{'B':{'color':'Peppercorn SW7674','RGB':[88,88,88],'HEX':'#585858'},'C':{'color':'Naval SW6244','RGB':[47,61,76],'HEX':'#2F3D4C'}},
 'placement_notes':{'B_panels':{'quantity':5,'bay_m':[3.0,2.4],'X_span':[-7.60,-4.60]},'ledge_tops_above_floor_m':{'bench':1.25,'primary':2.10},'primary_ledge_center_X':-6.915,'Richmond_frame_center_above_floor_m':1.85,'print_independent_mount':True,'plant':'Actual small Parlor Palm + Westcott black on dresser; no floor palm','task_chair':'One owned Mineral Aeron Size C; exact vintage/options unconfirmed'},
 'costs_USD':{'shared_core':2070.10,'composition_additions':263.96,'C':2334.06,'B_panels':974.75,'B':3308.81},
 'sources_limit':'Public logged-out Pins, creator and image-production methods not independently verified. Inspiration only; measured model controls room geometry. Source photos fully contained; no cropping/color editing/background removal.',
 'outputs':{str(PDF):hashlib.sha256(PDF.read_bytes()).hexdigest(),str(PNG):hashlib.sha256(PNG.read_bytes()).hexdigest()}}
for f in ['products/selected-products.json','products/owned-chair/owned-aeron-size-c-mineral.json','products/composition-pieces/sill-parlor-js.json','products/composition-pieces/mosslanda-jsonld.json','products/composition-pieces/fado-kajplats-jsonld.json','products/composition-pieces/grovemade-felt-mediumplus-jsonld.json','research/cohesive-composition/complete-room-composition-sources.json','images/composition-proposal/composition-plan-current.json','products/composition-pieces/finishing-selected-products.json']:
 path=ROOT/f
 manifest.setdefault('evidence_source_hashes',{})[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
# Attach published original image URLs for unchanged palette sources.
for record in json.loads((ROOT/'products/proposal-complements/cool-complements.json').read_text())['selected_complements']:
 ph=record.get('official_photo',{})
 path=ph.get('file')
 if path in SOURCES:SOURCES[path]['original_image_url']=ph.get('image_url','')
SOURCES[str(ROOT/'products/proposal-complements/art/dan-hobday-richmond-70x100-official.jpg')]['original_image_url']='https://media.desenio.com/site_images/69f09dd9f1a24127f43492c5_936071704_pre0717-1.jpg'
chair=json.loads((ROOT/'products/owned-chair/owned-aeron-size-c-mineral.json').read_text())
for ph in chair['official_photos']:
 if ph['file'] in SOURCES:SOURCES[ph['file']]['original_image_url']=ph['url']
(OUT/'Cohesive-office-composition-proposal.sources.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'PDF':str(PDF),'PNG':str(PNG),'photos':len(SOURCES),'pixels':[pix.width,pix.height]}))
