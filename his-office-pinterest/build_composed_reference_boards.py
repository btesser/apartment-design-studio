#!/usr/bin/env python3
"""Three photographic source sheets: shared products, B finishes, C finishes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'images/reference-boards/composed';OUT.mkdir(parents=True,exist_ok=True)
P=ROOT/'products/photos';C=ROOT/'products/proposal-complements'
for name,fn in [('Studio','DejaVuSans.ttf'),('StudioBold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+fn))

def cell(name,dim,note,files,url,credit,split='horizontal',swatch=None):
    return dict(name=name,dim=dim,note=note,images=[str(p) for p in files],url=url,credit=credit,split=split,swatch=swatch)
shared=[
cell('SELECTED Branch Tria — Black Oak / Charcoal','Nominal desktop47.2×27in / 119.89×68.58cm — $749',
     'Use the final model’s vendor CAD dimensions and frame. Black-oak woodgrain top, charcoal three-stage steel legs, felt underdesk organizer. Catalogue room/lamp/decor are reference context only.',
     [ROOT/'products/standing-desk-candidates/branch-tria-blackoak-charcoal-official.jpg'],
     'https://www.branchfurniture.com/products/tria-standing-desk?variant=43180424921123','Branch original exact Black Oak / Charcoal photograph'),
cell('OWNED Honeywell 02E Pro — WHITE','Overall D×W×H61.01×28.80×196.85cm — owned',
     'Two narrow LED bars form an OPEN rectangular head with EMPTY CENTER. Slim white upright, white U-shaped base. Preserve its model position, orientation and outer size.',
     [P/'honeywell-B0C3BVYTXP-MAIN.jpg'],'https://honeywellsmartlighting.com/products/02e-pro','Exact Honeywell ASINB0C3BVYTXP original photograph'),
cell('OWNED MUTTROS — BROWN / three wicker baskets','H149.86cm; base59.94×55.88cm — owned',
     'Natural brown wicker and branching wood; retain condo and hammock. Preserve final modeled branches and basket orientation. Source cats, plant and room props are context only.',
     [P/'muttros-B0HHRC6XBC-MAIN.jpg'],'https://www.amazon.com/dp/B0HHRC6XBC','Exact MUTTROS ASINB0HHRC6XBC original photograph'),
cell('CLEAR project bench — LAGKAPTEN top','Black-brown140×60cm tabletop804.870.16 — $49.99',
     'Real black-brown tabletop. Keep this work surface EMPTY: no second fixed monitor, keyboard or permanent task chair. It remains independent of the primary standing desk.',
     [P/'lagkapten-top-black.jpg'],'https://www.ikea.com/us/en/p/lagkapten-tabletop-black-brown-80487016/','IKEA original selected black-brown tabletop photograph'),
cell('ONE LEFT ALEX + TWO RIGHT black ADILS','ALEX36×58×70cm — $115; TWO legs — $15 total',
     'Black-brown FIVE-DRAWER ALEX604.735.48 at LEFT / −X. TWO black ADILS702.179.73 at RIGHT. Use the measured final assembly and knee bay; photos show the separate real components.',
     [P/'alex-black-drawers.jpg',P/'adils-black-leg.jpg'],'https://www.ikea.com/us/en/p/alex-drawer-unit-black-brown-60473548/','IKEA original selected drawer unit and leg photographs'),
cell('OWNED Herman Miller Aeron — MINERAL / Size C','ONE owned primary chair — no new chair purchase',
     'Light-gray Mineral mesh/frame, five-star rolling base. Current official Size C photo is a finish/form reference; owned vintage, arm/back/caster/base options are not claimed. Keep the exact final model pose and facing.',
     [ROOT/'products/owned-chair/aeron-c-mineral-official.png'],'https://store.hermanmiller.com/office-chairs-aeron/aeron-chair/100099909.html?lang=en_US','Herman Miller original Mineral Size C reference photograph'),
cell('Grovemade — Dark Grey felt mat','Medium Plus96.52×40.01cm — $100',
     'Actual wool-felt dark-gray mat on the PRIMARY standing desk. Preserve modeled mat footprint/position; source keyboard, mouse and mug are manufacturer styling, not included purchases or additional modeled objects.',
     [ROOT/'products/composition-pieces/grovemade-darkgrey-mediumplus-original.jpg'],'https://grovemade.com/product/wool-felt-desk-pad/?initial=683','Grovemade original exact Medium Plus Dark Grey photograph'),
cell('TWO matching MOSSLANDA — BLACK 115 cm ledges','Native114.99×12×7cm — TWO / $39.98 total',
     'Bench ledge TOP1.25m above floor, beneath independently hung Richmond. Primary-desk ledge TOP2.10m. Small illustrative books only; no plants or tall art on shelves. Use target model anchors and preserve standing desk clearance.',
     [ROOT/'products/composition-pieces/mosslanda-black-original.jpg'],'https://www.ikea.com/us/en/p/mosslanda-picture-ledge-black-70292104/','IKEA original selected black MOSSLANDA photograph')]


finishes=[
cell('EKENÄSET — Axvall dark gray-blue bouclé','W65.09×D73.98×H74.93cm — $399',
     'Exact506.243.26 new chair shape: textured gray-blue bouclé, walnut-effect wood arms/legs. Use actual form in the target model; preserve its position and facing.',
     [C/'photos/ekenaset-axvall-gray-blue.jpg'],'https://www.ikea.com/us/en/p/ekenaeset-armchair-walnut-effect-axvall-dark-gray-blue-50624326/','IKEA original selected Axvall gray-blue photograph'),
cell('Rift Charcoal — selected6×9 Flatwoven','182.88×274.32cm — $369 with Standard Pad',
     'Use this exact6×9 broken-stripe pattern, charcoal ground, gray/cream/muted-brown accents. Keep the model rug rotation and footprint. Do not substitute a blue/taupe rug or stretch the pattern.',
     [C/'photos/rift-6x9.jpg'],'https://ruggable.com/products/rift-charcoal-rug?variant=42130480070711','Ruggable original selected6×9 variant photograph'),
cell('STORKLINTA — dark-brown/oak clothes drawers','W69.85×D47.94×H74.93cm — $149.99',
     'Three flush dark-brown/oak-effect drawers, exact605.592.93. Preserve footprint and placement. Anchor to wall per IKEA instructions; verify brick fixing on site.',
     [C/'photos/storklinta-dark-brown-product.jpg'],'https://www.ikea.com/us/en/p/storklinta-3-drawer-dresser-dark-brown-oak-effect-anchor-unlock-function-60559293/','IKEA original whole-product selected dresser photograph'),
cell('ONE Dan Hobday — Richmond Print','Native LANDSCAPE paper100W×70Hcm — $107',
     'Use the exact unchanged slate/charcoal/olive/ivory/brown artwork and horizontal orientation. ONE independently hung picture above fixed bench, center1.85m above floor. Preserve actual print; never lean70cm-high art on ledge. No art over fireplace/primary desk.',
     [C/'art/dan-hobday-richmond-70x100-official.jpg'],'https://desenio.com/p/posters-prints/featured-artists/dan-hobday/dan-hobday-richmond-print/','Desenio original exact100×70cm landscape artwork'),
cell('Thin BLACK wood frame — landscape','Picture opening100×70cm horizontally — $101.15',
     'Use only the narrow black frame material/profile. Retailer photograph is portrait, while the actual model/artwork are horizontal. Do not copy placeholder lettering or add a second picture.',
     [P/'black-frame-landscape.jpg'],'https://desenio.com/p/frames/wood-frames/black-wood-frames/black-picture-frame-28-x-39-in/','Desenio original frame photograph — profile only')]

finishes.extend([
cell('FADO / KAJPLATS — WHITE OPAL GLOBE','Kit with smart bulb and remote — $44.98 regular',
     'Actual FADO white opal globe on DARK DRESSER, opposite the small palm. Catalog Ø25.4×H22.86cm; final source CAD shape controls. Neutral white decorative light; no colored RGB glow, invented ceiling fixture or floor lamp.',
     [ROOT/'products/composition-pieces/fado-white-original.jpg'],'https://www.ikea.com/us/en/p/fado-kajplats-table-lamp-with-led-bulb-smart-color-and-white-spectrum-s29654971/','IKEA original globe photo; selected kit adds bulb/remote'),
cell('Small Parlor Palm + Westcott BLACK planter','The Sill Small6–11in plant + pot — $79',
     'A SMALL palm in a black cylindrical pot on DRESSER opposite opal lamp. Plant height varies15–28cm from growpot bottom; no floor tree, oversized foliage or plant on12cm ledge. Exact final modeled envelope/position governs.',
     [ROOT/'products/composition-pieces/sill-small-parlor-westcott-black-original.jpg'],'https://www.thesill.com/products/parlor-palm?variant=41732265410665','The Sill original selected Small/Westcott/Black photograph')])
walls=json.loads((ROOT/'products/wall-finish-candidates/wall-finish-proposals.json').read_text())
wood=next(x for x in walls['candidates'] if x['id']=='woodupp_black_ash_black_felt')
woodphoto=next(x for x in wood['photos'] if x['path'].endswith('-2.jpg'))
pepper_url='https://www.sherwin-williams.com/en-us/color/color-family/neutral-paint-colors/SW7674-peppercorn'
naval_url='https://www.sherwin-williams.com/en-us/color/color-family/blue-paint-colors/SW6244-naval'
wallB=cell('B ONLY — FIVE Black Ash panels + Peppercorn','5 panels 60W×240H×2.2D cm — $974.75 before extras',
     'Bounded3m-wide VERTICAL slat bay behind BOTH worktops, spanX[-7.60,-4.60], exactly as modeled. Peppercorn#585858 wraps workwall AND adjacent windowwall. White ceiling/trim and existing brick stay. Angled photo is material detail only.',
     [Path(woodphoto['path'])],wood['url'],'WoodUpp original Black Ash veneer / black felt detail',swatch={'name':'Peppercorn SW7674','hex':'#585858','rgb':[88,88,88],'url':pepper_url})
wallC=cell('C ONLY — Naval SW6244 matte paint','Verified screen reference RGB47,61,76 / #2F3D4C',
     'Deep NAVY wraps the EXISTING smooth workwall AND adjacent windowwall, exactly as modeled. No slats/grooves copied from Pin. Keep white ceiling/trim and actual brick; reproduce the TWO selected black ledges at model anchors.',
     [],naval_url,'Sherwin-Williams official ColorSnap RGB / HEX data',swatch={'name':'Naval SW6244','hex':'#2F3D4C','rgb':[47,61,76],'url':naval_url})
refs=json.loads((ROOT/'research/cohesive-composition/complete-room-composition-sources.json').read_text())['selected_references']
pinmap={'B':refs[0],'C':refs[1]}

def para(c,text,x,y,width,size=13,bold=False,color='#233440'):
    s=ParagraphStyle('cell',fontName='StudioBold' if bold else 'Studio',fontSize=size,leading=size*1.25,textColor=colors.HexColor(color))
    p=Paragraph(escape(text),s);_,hh=p.wrap(width,1000);p.drawOn(c,x,y-hh);return y-hh
def contain(c,path,x,y,w,h):
    with Image.open(path) as im:iw,ih=im.size
    ratio=min(w/iw,h/ih);dw,dh=iw*ratio,ih*ratio
    c.drawImage(ImageReader(path),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
def walk(o,index):
    if isinstance(o,dict):
        if ('file' in o or 'path' in o) and ('url' in o or 'image_url' in o):index[o.get('file',o.get('path'))]=o
        for v in o.values():walk(v,index)
    elif isinstance(o,list):
        for v in o:walk(v,index)
idx={};walk(json.loads((ROOT/'products/selected-products.json').read_text()),idx)
walk(json.loads((ROOT/'products/composition-pieces/finishing-selected-products.json').read_text()),idx)
walk(json.loads((ROOT/'products/owned-chair/owned-aeron-size-c-mineral.json').read_text()),idx)
prior=json.loads((ROOT/'images/proposals/product-candidates.sources.json').read_text())
for p,o in prior['source_photographs'].items():idx[p]={'url':o['source_image_url'],'sha256':o['sha256']}
idx[woodphoto['path']]={'url':woodphoto['url'],'sha256':woodphoto['sha256']}
for p in pinmap.values():idx[p['local_image_path']]={'url':p['image_source_url'],'sha256':p['original_image_sha256']}
sources={};swatches=[]
def record(v):
    for p in v['images']:
        path=Path(p);sha=hashlib.sha256(path.read_bytes()).hexdigest();ref=idx.get(p,{})
        if ref.get('sha256'):assert sha==ref['sha256'],p
        assert ref.get('url',ref.get('image_url')),p
        with Image.open(path) as im:dims=list(im.size)
        product_url='https://www.ikea.com/us/en/p/adils-leg-black-70217973/' if path.name=='adils-black-leg.jpg' else v['url']
        sources[p]={'sha256':sha,'source_image_url':ref.get('url',ref.get('image_url')),'product_or_Pin_url':product_url,'role':v['name'],'pixel_dimensions':dims,'full_original_contained':True,'original_pixels_edited':False}
    if v.get('swatch'):swatches.append(v['swatch'])
def drawcell(c,v,x,y,cw,ch):
    c.setFillColor(colors.white);c.setStrokeColor(colors.HexColor('#D3D8DB'));c.roundRect(x,y,cw,ch,6,fill=1,stroke=1)
    yy=para(c,v['name'],x+15,y+ch-13,cw-30,14,True)
    yy=para(c,v['dim'],x+15,yy-5,cw-30,11.8,False,'#4C6676')
    ih=ch-191;ix,iy,iw=x+13,y+135,cw-26
    images=v['images'];sw=v.get('swatch')
    if sw and images:
        contain(c,images[0],ix,iy,iw*.66,ih)
        c.setFillColor(colors.HexColor(sw['hex']));c.rect(ix+iw*.71,iy+25,iw*.27,ih-50,fill=1,stroke=0)
        para(c,sw['name'],ix+iw*.68,iy+20,iw*.32,9.4)
    elif sw:
        c.setFillColor(colors.HexColor(sw['hex']));c.rect(ix+45,iy+15,iw-90,ih-30,fill=1,stroke=0)
    elif len(images)==1:contain(c,images[0],ix,iy,iw,ih)
    elif images:
        n=len(images);gap=8;each=(iw-(n-1)*gap)/n
        for i,p in enumerate(images):contain(c,p,ix+i*(each+gap),iy,each,ih)
    low=para(c,v['note'],x+15,y+121,cw-30,10.8)
    assert low>y+29,(v['name'],low,y)
    para(c,v['credit'],x+15,y+27,cw-30,9.3,False,'#64737B')
    c.linkURL(v['url'],(x+12,y+9,x+cw-12,y+33),relative=0,thickness=0)
    if sw:c.linkURL(sw['url'],(ix+iw*.68,iy,ix+iw,iy+ih),relative=0,thickness=0)
    record(v)
def header(c,W,H,title):
    c.setFillColor(colors.HexColor('#F1F3F3'));c.rect(0,0,W,H,fill=1,stroke=0)
    para(c,title,28,H-23,W-56,23,True)
    para(c,'FIXED TARGET MODEL / CAMERA = GEOMETRY. Real product photos = finishes and exact forms. Pin = atmosphere only. Preserve all positions, dimensions, furniture facing, doors and the existing room.',28,H-60,W-56,12)
def footer(c,W):
    para(c,'Original photographs fully contained • no crop, recoloring or original pixel edits • verified paint swatches are authored from official RGB data • links / SHA-256 in product-reference-boards.sources.json',28,29,W-56,9.5)

W=1440;H=1500;pdf=OUT/'composed-reference-boards.pdf';c=canvas.Canvas(str(pdf),pagesize=(W,H),pageCompression=1)
c.setTitle('His office B and C — complete composition original photographic references')
header(c,W,H,'SHARED PRODUCTS — exact desk / clear bench / ONE owned Mineral Aeron')
for i,v in enumerate(shared):
    col,row=i%3,i//3;drawcell(c,v,28+col*466,55+(2-row)*453,448,437)
x,y=960,55
cfill=colors.HexColor('#E1E7EA');c.setFillColor(cfill);c.roundRect(x,y,448,437,6,fill=1,stroke=0)
yy=para(c,'ONE COHERENT COMPOSITION',x+18,y+417,412,19,True)
for text in [
 'Two work surfaces stay independent. The project bench is clear, with no second permanent task chair or monitor.',
 'Two matching black ledges: one below Richmond above fixed bench, one HIGH above primary standing desk. Only small modeled books / objects.',
 'Dark folded-clothes console carries ONE opal globe + ONE small palm and illustrative tray. No floor palm.',
 'Retain white Honeywell open LED rectangle, natural cat tree, white ceiling/trim, actual brick and oak floor.',
 'Target model controls room dimensions, furniture facing, door locations, camera and exact quantities.'
]:yy=para(c,text,x+18,yy-19,412,13)
assert yy>y+20,yy
footer(c,W);c.showPage()
for variant,wall in [('B',wallB),('C',wallC)]:
    header(c,W,H,variant+' — exact textiles / console / print / separate two-wall direction')
    for i,v in enumerate(finishes+[wall]):
        col,row=i%3,i//3;drawcell(c,v,28+col*466,55+(2-row)*453,448,437)
    p=pinmap[variant]
    v=cell(variant+' WHOLE-ROOM PIN — INSPIRATION ONLY','Public Pin '+p['pin_id'],
      'Borrow linked work/shelf/art, decorative light and visitor grouping. Actual target room and selected products remain authoritative. No copied sofa, large bookcase, ceiling, floor plant, grooves, worktops or extra furniture.',
      [Path(p['local_image_path'])],p['url'],'Original public Pin; creator / production method unverified')
    drawcell(c,v,960,55,448,437)
    footer(c,W);c.showPage()
c.save()
names=['shared-products-1','finishes-B-2','finishes-C-2'];outputs={}
for i,n in enumerate(names,1):
    png=OUT/(n+'.png');subprocess.run(['pdftoppm','-f',str(i),'-l',str(i),'-singlefile','-r','150','-png',str(pdf),str(png.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    with Image.open(png) as im:dims=list(im.size)
    outputs[n]={'file':str(png),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'pixel_dimensions':dims,'source_pdf_page':i}
for n,alias in zip(names,['product-board-1.png','product-board-2-b.png','product-board-2-c.png']):
    dest=ROOT/'images'/alias;dest.write_bytes(Path(outputs[n]['file']).read_bytes())
    outputs[alias]={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'pixel_dimensions':outputs[n]['pixel_dimensions']}
for p,o in sources.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==o['sha256']
selection=ROOT/'products/selected-products.json';spec=ROOT/'design-spec.json'
manifest={'created_UTC':datetime.now(timezone.utc).isoformat(),'usage':{'B':['product-board-1.png','product-board-2-b.png'],'C':['product-board-1.png','product-board-2-c.png']},
 'status':'User requested upgraded cohesive composition; root selected all exact products. No purchases. Target model geometry and matched cameras govern final generation.',
 'product_selection_sha256':hashlib.sha256(selection.read_bytes()).hexdigest(),'design_spec_sha256':hashlib.sha256(spec.read_bytes()).hexdigest() if spec.exists() else None,
 'original_photographs_modified':False,'authoring':'ReportLab entire-original-photo containment + primary-source-color vector swatches, rasterized by pdftoppm150DPI. No source photo crop/recolor/pixel edits.',
 'shared_cells':shared,'finish_cells':finishes,'variant_wall_cells':{'B':wallB,'C':wallC},'source_photographs':sources,'official_paint_swatches':swatches,'outputs':outputs,
 'PDF':{'file':str(pdf),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'composed-reference-boards.sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ROOT/'images/product-reference-boards.sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
(ROOT/'images/reference-boards/STATUS.txt').write_text('Current generation references are images/product-board-1.png and variant-specific product-board-2-b.png / product-board-2-c.png, sourced by product-reference-boards.sources.json. Earlier Branch/3panel wall-study boards remain historical checkpoints; never use them for current generation.\n')
print(json.dumps(outputs,indent=2))
