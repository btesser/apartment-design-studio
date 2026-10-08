#!/usr/bin/env python3
"""Typeset original product photographs for the two approved dark office directions."""
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
OUT=ROOT/'images/proposals'; OUT.mkdir(parents=True,exist_ok=True)
P=ROOT/'products/photos'; C=ROOT/'products/proposal-complements'
W,H=1000,960
for name,fn in [('Studio','DejaVuSans.ttf'),('StudioBold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+fn))

def file(p):return str(p)
def item(name,price,size,note,images,urls,display):
    return dict(name=name,price=price,size=size,note=note,images=[file(p) for p in images],urls=urls,display=display)

cells=[
item('Branch Tria — Black Oak / Charcoal','$749','47.2×27 in / 119.89×68.58 cm',
     'Standing height 25.5–48.9 in. Real replacement candidate; source photo shows its styling context.',
     [ROOT/'products/standing-desk-candidates/branch-tria-blackoak-charcoal-official.jpg'],
     ['https://www.branchfurniture.com/products/tria-standing-desk?variant=43180424921123'],'branchfurniture.com · Tria'),
item('Clear black-brown project bench','$179.99 total','140×60 cm; assembly H73.49 cm',
     'LAGKAPTEN $49.99 + LEFT five-drawer ALEX $115 + TWO right black ADILS $15. Keep worktop clear.',
     [P/'lagkapten-top-black.jpg',P/'alex-black-drawers.jpg',P/'adils-black-leg.jpg'],
     ['https://www.ikea.com/us/en/p/lagkapten-tabletop-black-brown-80487016/','https://www.ikea.com/us/en/p/alex-drawer-unit-black-brown-60473548/','https://www.ikea.com/us/en/p/adils-leg-black-70217973/'],'ikea.com · LAGKAPTEN / ALEX / ADILS'),
item('ONE Branch Ergonomic Chair Pro','$499','Black; caster base Ø70.10 cm',
     'One ergonomic work chair. It can transfer to the clear project bench; no second permanent task chair.',
     [P/'branch-pro-selected.jpg'],
     ['https://www.branchfurniture.com/products/ergonomic-chair-pro?variant=40553208840227'],'branchfurniture.com · Ergonomic Chair Pro'),
item('EKENÄSET — Axvall dark gray-blue','$399','W65.09×D73.98×H74.93 cm',
     'Bouclé textile + walnut-effect frame. Current new shape is 4.13 cm shallower than beige checkpoint; recheck fit in final model.',
     [C/'photos/ekenaset-axvall-gray-blue.jpg'],
     ['https://www.ikea.com/us/en/p/ekenaeset-armchair-walnut-effect-axvall-dark-gray-blue-50624326/'],'ikea.com · EKENÄSET 506.243.26'),
item('Rift Charcoal — exact 6×9 Flatwoven','$369 incl. Standard Pad','182.88×274.32 cm; nominal 5.18 mm system',
     'Quiet broken-stripe graphic in charcoal, gray, cream and muted brown. Low 2 mm cover supports chair movement.',
     [C/'photos/rift-6x9.jpg'],
     ['https://ruggable.com/products/rift-charcoal-rug?variant=42130480070711'],'ruggable.com · Rift Charcoal'),
item('STORKLINTA — dark-brown/oak effect','$149.99','W69.85×D47.94×H74.93 cm',
     'Same footprint and three clothes drawers as oak checkpoint. Anchor to wall per IKEA instructions; verify brick fixing on site.',
     [C/'photos/storklinta-dark-brown-product.jpg'],
     ['https://www.ikea.com/us/en/p/storklinta-3-drawer-dresser-dark-brown-oak-effect-anchor-unlock-function-60559293/'],'ikea.com · STORKLINTA 605.592.93'),
item('Dan Hobday — Richmond Print','$107 print; frame extra','Native LANDSCAPE paper W100×H70 cm',
     'Slate / charcoal geometry with muted olive, ivory and brown. One wide focal artwork; source is the exact horizontal product.',
     [C/'art/dan-hobday-richmond-70x100-official.jpg'],
     ['https://desenio.com/p/posters-prints/featured-artists/dan-hobday/dan-hobday-richmond-print/'],'desenio.com · Richmond / pre0717-1'),
item('B / C — TWO separate workwall options','$584.85 B panels; C paint unpriced','B:3×60W×240H×2.2D cm Black Ash panels',
     'B: bounded Black Ash bay + PeppercornSW7674. C: smooth deep-navy NavalSW6244 wall. Both retain white ceiling / existing brick; not a hybrid.',
     [ROOT/'products/wall-finish-candidates/woodupp-blackash-original-2.jpg'],
     ['https://woodupp.com/products/akupanel-acoustic-panel-natural-wood-black-ash-black-felt-240-x-60-cm','https://www.sherwin-williams.com/en-us/color/color-family/blue-paint-colors/SW6244-naval'],'woodupp.com · Black Ash / sherwin-williams.com · Naval'),
item('Retained accents — white lamp + wicker','OWNED — $0 new cost','Honeywell H196.85 cm; cat tree H149.86 cm',
     'Keep Honeywell’s OPEN head with two LED bars and white U-base; retain the brown three-basket MUTTROS tree. No pictured room props.',
     [P/'honeywell-B0C3BVYTXP-MAIN.jpg',P/'muttros-B0HHRC6XBC-MAIN.jpg'],
     ['https://honeywellsmartlighting.com/products/02e-pro','https://www.amazon.com/dp/B0HHRC6XBC'],'honeywellsmartlighting.com / amazon.com'),
]

def para(c,text,x,y,width,size=10,bold=False,color='#26323b'):
    style=ParagraphStyle('cell',fontName='StudioBold' if bold else 'Studio',fontSize=size,leading=size*1.25,textColor=colors.HexColor(color))
    p=Paragraph(escape(text),style);_,hh=p.wrap(width,900);p.drawOn(c,x,y-hh);return y-hh
def contain(c,path,x,y,w,h):
    with Image.open(path) as im:iw,ih=im.size
    ratio=min(w/iw,h/ih);dw,dh=iw*ratio,ih*ratio
    c.drawImage(ImageReader(path),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
def walk(o,index):
    if isinstance(o,dict):
        if 'file' in o and 'url' in o:index[o['file']]=o
        for v in o.values():walk(v,index)
    elif isinstance(o,list):
        for v in o:walk(v,index)
idx={};walk(json.loads((ROOT/'products/selected-products.json').read_text()),idx)
for x in json.loads((ROOT/'products/standing-desk-candidates/branch-tria-image-sources.json').read_text()):
    idx[x['file']]={'url':x.get('download_url',x['url'])}
idx[str(C/'photos/ekenaset-axvall-gray-blue.jpg')]={'url':'https://www.ikea.com/us/en/images/products/ekenaeset-armchair-walnut-effect-axvall-dark-gray-blue__1489628_pe1003902_s5.jpg'}
idx[str(C/'photos/storklinta-dark-brown-product.jpg')]={'url':'https://www.ikea.com/us/en/images/products/storklinta-3-drawer-dresser-dark-brown-oak-effect-anchor-unlock-function__1590138_pe1038779_s5.jpg'}
rif=json.loads((C/'source-pages/rift-shop-js.json').read_text());rv=next(v for v in rif['variants'] if v['id']==42130480070711)
idx[str(C/'photos/rift-6x9.jpg')]={'url':rv['featured_image']['src']}
art=json.loads((C/'art/dan-hobday-richmond-evidence.json').read_text())['selected_70x100']
idx[art['image_file']]={'url':art['image_url'],'sha256':art['image_sha256']}
idx[str(ROOT/'products/wall-finish-candidates/woodupp-blackash-original-2.jpg')]={'url':'https://cdn.shopify.com/s/files/1/0956/1561/5323/files/1013_akupanel_tonal_black_ash_black_felt_03.jpg?v=1777062017'}

pdf=OUT/'product-candidates.pdf';c=canvas.Canvas(str(pdf),pagesize=(W,H),pageCompression=1)
c.setTitle('His office — real product candidates for two dark studio directions')
c.setFillColor(colors.HexColor('#F0F2F2'));c.rect(0,0,W,H,fill=1,stroke=0)
para(c,'REAL PRODUCTS FOR TWO DARK STUDIO DIRECTIONS',24,H-20,W-48,19,True)
para(c,'Candidates for shared furniture: B = black-ash slats + charcoal; C = deep blue-black + graphic art. Final geometry and wall quantity are still to be checked. US prices checked 8 Oct 2026; tax / shipping excluded.',24,H-51,W-48,10)
sources={}
for i,v in enumerate(cells):
    col,row=i%3,i//3;x=24+col*324;y=39+(2-row)*282;cw,ch=304,267
    c.setFillColor(colors.white);c.setStrokeColor(colors.HexColor('#D1D6D8'));c.roundRect(x,y,cw,ch,5,fill=1,stroke=1)
    yy=para(c,v['name'],x+11,y+ch-10,cw-22,10.6,True)
    yy=para(c,v['price']+'  |  '+v['size'],x+11,yy-4,cw-22,9.4,False,'#4A6778')
    # Every photograph is fully contained; sources never cropped or altered.
    ix,iy,iw,ih=x+9,y+91,cw-18,126
    if len(v['images'])==1:contain(c,v['images'][0],ix,iy,iw,ih)
    else:
        n=len(v['images']);gap=5;each=(iw-(n-1)*gap)/n
        for k,p in enumerate(v['images']):contain(c,p,ix+k*(each+gap),iy,each,ih)
    yy=para(c,v['note'],x+11,y+80,cw-22,8.8)
    assert yy>=y+21,(v['name'],yy,y)
    para(c,v['display'],x+11,y+17,cw-22,8,False,'#315D75')
    for k,u in enumerate(v['urls']):
        ww=(cw-22)/len(v['urls']);c.linkURL(u,(x+11+k*ww,y+5,x+11+(k+1)*ww,y+21),relative=0,thickness=0)
    for p in v['images']:
        sha=hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=idx.get(p,{})
        if ref.get('sha256'):assert sha==ref['sha256'],p
        assert ref.get('url'),p
        with Image.open(p) as im:dims=list(im.size)
        sources[p]={'sha256':sha,'source_image_url':ref['url'],'product_urls':v['urls'],'role':v['name'],'pixel_dimensions':dims,'original_pixels_edited':False,'full_original_contained':True}
para(c,'Original retailer / manufacturer photos. Lifestyle backgrounds and props are context only; this board is not a floor plan. PDF product labels link to official pages.',24,23,W-48,8)
c.showPage();c.save()
subprocess.run(['pdftoppm','-singlefile','-r','216','-png',str(pdf),str(OUT/'product-candidates')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
png=OUT/'product-candidates.png'
with Image.open(png) as im:dim=list(im.size)
manifest={'created_UTC':datetime.now(timezone.utc).isoformat(),'status':'Two user-approved style directions; products remain candidates, not purchases or geometry-final selections.','authoring':'ReportLab typesetting of full original photographs, then PDF rasterization at216DPI. No original photograph pixels edited.','cells':cells,'source_photographs':sources,'outputs':{'png':{'file':str(png),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'pixel_dimensions':dim},'pdf':{'file':str(pdf),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'product-candidates.sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest['outputs'],indent=2))
