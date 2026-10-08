#!/usr/bin/env python3
"""Typeset full original product/Pin photos as two image-generation reference sheets."""
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

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'images';OUT.mkdir(exist_ok=True)
P=ROOT/'products/photos'
W,H=1440,1200
for name,fn in [('Studio','DejaVuSans.ttf'),('StudioBold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+fn))

def cell(name,dim,note,files,url,credit,split='vertical'):
    return dict(name=name,dim=dim,note=note,images=[str(P/f) for f in files],url=url,credit=credit,split=split)
boards=[{'title':'Warm architectural studio — owned pieces + real workbench','cells':[
cell('OWNED UPLIFT V2 — exact finish','Owned top: 42×30 in / 106.68×76.2 cm','Pheasantwood barkline FRONT, square back, two nickel grommets. Industrial steel C-frame. Catalogue image shows another width: keep the modeled 42-inch top.',['uplift-live-edge-pheasantwood-front.jpg','uplift-v2-c-frame-industrial-official.png'],'https://www.upliftdesk.com/desktop-lookbook/','UPLIFT official original photographs'),
cell('OWNED Honeywell 02E Pro — white','Overall D×W×H: 61.01×28.80×196.85 cm','Two narrow LED bars form an OPEN rectangular head with EMPTY CENTER. Slim white upright, white U-shaped floor base. Do not fill the head with a diffuser.',['honeywell-B0C3BVYTXP-MAIN.jpg'],'https://honeywellsmartlighting.com/products/02e-pro','Exact Honeywell ASIN B0C3BVYTXP photo'),
cell('OWNED MUTTROS — brown / three baskets','Height 149.86 cm; base 59.94×55.88 cm','Brown wicker baskets and branching wood, condo and hammock. Keep brown material. Lifestyle cats, plant and room props remain reference context only.',['muttros-B0HHRC6XBC-MAIN.jpg'],'https://www.amazon.com/dp/B0HHRC6XBC','Exact MUTTROS ASIN B0HHRC6XBC photo'),
cell('CLEAR project bench — LAGKAPTEN top','Black-brown top: 140×60 cm','Real selected component 804.870.16. Keep the project bench EMPTY: no second fixed monitor, keyboard, task chair or decorative clutter. Separate from height-adjustable UPLIFT.',['lagkapten-top-black.jpg'],'https://www.ikea.com/us/en/p/lagkapten-tabletop-black-brown-80487016/','IKEA original selected tabletop photograph'),
cell('ONE LEFT ALEX + TWO RIGHT ADILS','ALEX 36×58×70 cm; legs H70 cm','Black-brown FIVE-DRAWER ALEX 604.735.48 on LEFT / −X. TWO black ADILS 702.179.73 at RIGHT. Photos are components; use the modeled assembly and knee bay.',['alex-black-drawers.jpg','adils-black-leg.jpg'],'https://www.ikea.com/us/en/p/alex-drawer-unit-black-brown-60473548/','IKEA original drawer/leg photos','horizontal'),
cell('ONE primary Branch Ergonomic Chair Pro','Black mesh; caster base Ø70.10 cm','ONE daily ergonomic task chair at the UPLIFT workstation. Black mesh back, black seat and five-star rolling base. No second permanent task chair.',['branch-pro-selected.jpg'],'https://www.branchfurniture.com/products/ergonomic-chair-pro?variant=40553208840227','Branch original selected BLACK variant photo'),
]},{'title':'Quiet neutral finishes — exact products + ONE inspiration Pin','cells':[
cell('EKENÄSET — Kilanda light beige','Nominal W×D×H: 64×78×76 cm','Warm light-beige woven upholstery, dark brown wood arms/legs. Keep visitor chair at the final modeled position and facing. No teal or blue upholstery.',['ekenaset-beige.jpg'],'https://www.ikea.com/us/en/p/ekenaeset-armchair-kilanda-light-beige-30533493/','IKEA original selected Kilanda photograph'),
cell('Ruggable Impasto Taupe — exact 6×9','182.88×274.32 cm; Flatwoven + Standard Pad','Quiet distressed taupe / ivory textile. Use the actual selected pattern and modeled rug rotation/footprint. No previous blue geometric motif.',['ruggable-impasto-taupe-6x9.jpg'],'https://ruggable.com/products/impasto-taupe-rug?variant=42112443547703','Ruggable original selected 6×9 photograph'),
cell('STORKLINTA — oak clothes drawers','Nominal W×D×H: 70×48×75 cm','Three oak-effect flush drawers. Retain final footprint. Wall fixing unlocks drawers; installation fit needs verification. Original lifestyle background/props are not room contents.',['storklinta-low-drawers.jpg'],'https://www.ikea.com/us/en/p/storklinta-3-drawer-dresser-oak-effect-anchor-unlock-function-80559292/','IKEA original selected dresser photograph'),
cell('ONE Abstract Scenery No1 Print','LANDSCAPE paper: 100 cm wide × 70 cm high','Only this artwork: horizontal ABOVE THE CLEAR PROJECT BENCH. Use the exact cream / muted-brown artwork. Keep the fireplace and UPLIFT wall free of art.',['art-abstract-scenery-100x70.jpg'],'https://desenio.com/p/posters-prints/art-prints/abstract-scenery-no1-print/','Desenio original selected landscape artwork'),
cell('Thin BLACK wood frame — landscape','Picture opening: 100×70 cm horizontally','Retailer photo is portrait: use only its narrow black frame material/profile, in the modeled landscape orientation. Do not reproduce placeholder lettering or add another picture.',['black-frame-landscape.jpg'],'https://desenio.com/p/frames/wood-frames/black-wood-frames/black-picture-frame-28-x-39-in/','Desenio original frame photo — profile only'),
dict(name='PINTEREST INSPIRATION ONLY',dim='Public Pin 461196818109099025',note='Borrow quiet composition, warm wood and one wide art focal point ONLY. Do NOT copy this room, desk, chair, lamp, plant or dimensions. The target 3D model controls all geometry and furniture positions.',images=[str(ROOT/'research/pins/walnut-simple.jpg')],url='https://www.pinterest.com/pin/461196818109099025/',credit='Original public Pin image; photographer not verified',split='vertical'),
]}]

def para(c,text,x,y,width,size=13,bold=False,color='#233440'):
    s=ParagraphStyle('cell',fontName='StudioBold' if bold else 'Studio',fontSize=size,leading=size*1.3,textColor=colors.HexColor(color))
    q=Paragraph(escape(text),s);_,hh=q.wrap(width,1000);q.drawOn(c,x,y-hh);return y-hh
def contain(c,path,x,y,w,h):
    with Image.open(path) as im:iw,ih=im.size
    scale=min(w/iw,h/ih);nw,nh=iw*scale,ih*scale
    c.drawImage(ImageReader(path),x+(w-nw)/2,y+(h-nh)/2,nw,nh,mask='auto')
def lookup(obj,out):
    if isinstance(obj,dict):
        if 'file' in obj and 'url' in obj:out[obj['file']]=obj
        for v in obj.values():lookup(v,out)
    elif isinstance(obj,list):
        for v in obj:lookup(v,out)
product_data=json.loads((ROOT/'products/selected-products.json').read_text());index={};lookup(product_data,index)
pin_data=json.loads((ROOT/'research/reviewed-pin-records.json').read_text())
pin=next(p for p in pin_data if p.get('pin_id')=='461196818109099025')
index[pin['local_image_path']]={'url':pin['image_source_url'],'sha256':pin['original_image_sha256']}

pdf=OUT/'product-reference-boards.pdf';c=canvas.Canvas(str(pdf),pagesize=(W,H),pageCompression=1)
c.setTitle('His office — Pinterest studio original photograph references')
sources={}
for bi,board in enumerate(boards):
    c.setFillColor(colors.HexColor('#F7F4EE'));c.rect(0,0,W,H,fill=1,stroke=0)
    para(c,board['title'],30,H-24,W-60,23,True)
    para(c,'FIXED TARGET MODEL / CAMERA = GEOMETRY. Product photos = exact products and finishes. Pin = atmosphere only. Preserve all positions, scale, facing, doors and the existing architecture.',30,H-58,W-60,12)
    for ci,item in enumerate(board['cells']):
        col,row=ci%3,ci//3;x=30+col*466;y=52+(1-row)*520;cw,ch=448,504
        c.setFillColor(colors.white);c.setStrokeColor(colors.HexColor('#D8D4CB'));c.roundRect(x,y,cw,ch,8,fill=1,stroke=1)
        if item['name'].startswith('PINTEREST'):c.setStrokeColor(colors.HexColor('#A87A45'));c.roundRect(x,y,cw,ch,8,fill=0,stroke=1)
        para(c,item['name'],x+16,y+ch-15,cw-32,14.5,True)
        para(c,item['dim'],x+16,y+ch-44,cw-32,12,False,'#73583B')
        ix,iy,iw,ih=x+14,y+135,cw-28,296
        ims=item['images']
        if len(ims)==1:contain(c,ims[0],ix,iy,iw,ih)
        elif item['split']=='horizontal':
            contain(c,ims[0],ix,iy,iw/2-5,ih);contain(c,ims[1],ix+iw/2+5,iy,iw/2-5,ih)
        else:
            contain(c,ims[0],ix,iy+166,iw,130);contain(c,ims[1],ix,iy,iw,160)
        para(c,item['note'],x+16,y+119,cw-32,11.2)
        para(c,item['credit'],x+16,y+28,cw-32,9.1,False,'#66747B')
        c.linkURL(item['url'],(x+12,y+10,x+cw-12,y+37),relative=0,thickness=0)
        for p in ims:
            pp=Path(p);s=hashlib.sha256(pp.read_bytes()).hexdigest();ref=index.get(p,{})
            if ref.get('sha256'):assert s==ref['sha256'],p
            sources[str(pp.relative_to(ROOT))]={'sha256':s,'image_source_url':ref.get('url'),'product_or_pin_url':item['url'],'role':item['name'],'full_original_contained':True}
    para(c,'Full original photographs • no cropping or original pixel edits • source URLs and SHA-256 hashes in product-reference-boards.sources.json',30,31,W-60,10)
    c.showPage()
c.save()
subprocess.run(['pdftoppm','-r','150','-png',str(pdf),str(OUT/'product-board')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
outputs={}
for i in [1,2]:
    p=OUT/f'product-board-{i}.png'
    with Image.open(p) as im:dims=im.size
    outputs[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pixel_dimensions':dims,'source_pdf_page':i}
for rel,record in sources.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==record['sha256']
manifest={'created_UTC':datetime.now(timezone.utc).isoformat(),'authoring':'Full original photographs typeset in ReportLab PDF, rasterized with pdftoppm at150DPI. No cropping, retouching, substitutions or original pixel edits.','original_images_modified':False,'source_photographs':sources,'boards':boards,'outputs':outputs,'source_pdf':{'file':str(pdf.relative_to(ROOT)),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'product-reference-boards.sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(outputs,indent=2))
