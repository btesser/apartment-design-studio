#!/usr/bin/env python3
"""Typeset original product photographs in PDF; rasterize pages as imagegen references."""
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
OUT=ROOT/'images'
OUT.mkdir(exist_ok=True)
P=ROOT/'products/candidates/official-images'
K=ROOT/'products/keepers'
W,H=1440,1200
for name,fn in [('Studio','DejaVuSans.ttf'),('StudioBold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+fn))

boards=[
    {'title':'Owned keepers + two real workstations','cells':[
        {'name':'Owned UPLIFT V2 — finish references','dim':'Actual owned top: 42×30 in / 106.68×76.2 cm','note':'Pheasantwood barkline front; square back; brushed-nickel grommets. Industrial Style steel C-frame. Catalogue photographs show another width: keep modeled size.','images':[K/'uplift-live-edge-pheasantwood-front.jpg',K/'uplift-v2-c-frame-industrial-official.png'],'credit':'UPLIFT official product photographs','urls':['https://www.upliftdesk.com/desktop-lookbook/','https://checkout.upliftdesk.com/test-uplift-2-leg-standing-desk-frame/']},
        {'name':'Owned Honeywell 02E Pro — white','dim':'Overall D×W×H: 61.01×28.80×196.85 cm','note':'Flat rectangular light panel, slim upright, white U-shaped floor base. Exact owned model.','images':[K/'honeywell-B0C3BVYTXP-MAIN.jpg'],'credit':'Exact Honeywell ASIN B0C3BVYTXP product photo','urls':['https://www.amazon.com/dp/B0C3BVYTXP']},
        {'name':'Owned MUTTROS 59-inch — brown','dim':'Height 149.86 cm; base 59.94×55.88 cm','note':'Three wicker baskets, branching wood, bottom condo, hammock. Full upper span unpublished; source lifestyle cats/props stay in this reference only.','images':[K/'muttros-B0HHRC6XBC-MAIN.jpg'],'credit':'Exact MUTTROS ASIN B0HHRC6XBC product photo','urls':['https://www.amazon.com/dp/B0HHRC6XBC']},
        {'name':'IKEA LAGKAPTEN / ALEX — single pedestal','dim':'Desktop W×D: 140×60 cm; desk H: 73 cm','note':'Black-brown top / white drawers and legs. ONE ALEX on the LEFT / x-negative end. Two legs at the right.','images':[P/'lagkapten-alex-single.jpg'],'credit':'IKEA official product photograph','urls':['https://www.ikea.com/us/en/p/lagkapten-alex-desk-black-brown-white-s59432163/']},
        {'name':'Branch Ergonomic Chair Pro — BLACK ×2','dim':'Body 63.5×60.96 cm; caster base Ø70.10 cm','note':'Black mesh back, upholstered black seat, black five-star rolling base. Two identical usable task seats.','images':[P/'branch-pro-selected.jpg'],'credit':'Branch official selected BLACK variant photograph','urls':['https://www.branchfurniture.com/products/ergonomic-chair-pro?variant=40553208840227']},
    ]},
    {'title':'Warm modern studio — exact selected finishes','cells':[
        {'name':'IKEA STORKLINTA — oak effect','dim':'Nominal W×D×H: 70×48×75 cm','note':'Three flush drawers for folded clothes. The photographed room/props are original retailer context only.','images':[P/'storklinta-low-drawers.jpg'],'credit':'IKEA official product photograph','urls':['https://www.ikea.com/us/en/p/storklinta-3-drawer-dresser-oak-effect-anchor-unlock-function-80559292/']},
        {'name':'IKEA EKENÄSET — Kelinge gray-turquoise','dim':'Nominal W×D×H: 64×78×76 cm','note':'Cool gray-turquoise corduroy; warm brown wooden arms and legs. Compact visitor lounge chair.','images':[P/'ekenaset-turquoise.jpg'],'credit':'IKEA official selected upholstery photograph','urls':['https://www.ikea.com/us/en/p/ekenaeset-armchair-kelinge-gray-turquoise-90533485/']},
        {'name':'Jonathan Adler Inkdrop Slate Blue','dim':'EXACT 6×9 ft / 182.88×274.32 cm','note':'Ruggable Flatwoven + Standard Pad. Ivory field, dark slate-blue stepped ink geometry. Photograph is the selected 6×9 variant.','images':[P/'ruggable-inkdrop-selected.jpg'],'credit':'Ruggable official selected 6×9 flatlay photograph','urls':['https://ruggable.com/products/jonathan-adler-inkdrop-slate-blue-rug?variant=39402849828919']},
        {'name':'Desenio Bold Blue Print','dim':'Selected print: 70×100 cm; thin black frame','note':'Use this exact artwork above the existing sealed brick fireplace; keep modeled location and mounting size.','images':[P/'art-blue-bold-selected.jpg'],'credit':'Desenio official selected artwork photograph','urls':['https://desenio.com/p/posters-prints/art-prints/abstract-art/bold-blue-print/']},
        {'name':'Desenio Blue Geometric Print','dim':'Selected print: 50×70 cm; thin black frame','note':'Use this exact artwork above the owned UPLIFT workstation; keep modeled location and mounting size.','images':[P/'art-blue-geometric-selected.jpg'],'credit':'Desenio official selected artwork photograph','urls':['https://desenio.com/p/posters-prints/art-prints/graphical/blue-geometric-print/']},
    ]}
]

def para(c,text,x,y,width,size=13,bold=False,color='#233440'):
    s=ParagraphStyle('cell',fontName='StudioBold' if bold else 'Studio',fontSize=size,leading=size*1.3,textColor=colors.HexColor(color))
    q=Paragraph(escape(text),s); _,hh=q.wrap(width,1000); q.drawOn(c,x,y-hh); return y-hh

def contain(c,path,x,y,w,h):
    with Image.open(path) as im: iw,ih=im.size
    scale=min(w/iw,h/ih); nw,nh=iw*scale,ih*scale
    c.drawImage(ImageReader(str(path)),x+(w-nw)/2,y+(h-nh)/2,nw,nh,mask='auto')

pdf=OUT/'product-reference-boards.pdf'
c=canvas.Canvas(str(pdf),pagesize=(W,H),pageCompression=1)
c.setTitle('His office — original product photograph references')
sources={}
for bi,board in enumerate(boards):
    c.setFillColor(colors.HexColor('#F7F4EE'));c.rect(0,0,W,H,fill=1,stroke=0)
    para(c,board['title'],30,H-24,W-60,26,True)
    para(c,'MODEL IS GEOMETRY AUTHORITY • These retailer photographs control products / finishes only. Preserve all modeled positions, scale, orientations and camera.',30,H-62,W-60,12)
    for ci,cell in enumerate(board['cells']):
        col,row=ci%3,ci//3;x=30+col*466;y=52+(1-row)*520;cw,ch=448,504
        c.setFillColor(colors.white);c.setStrokeColor(colors.HexColor('#D8D4CB'));c.roundRect(x,y,cw,ch,8,fill=1,stroke=1)
        top=y+ch
        para(c,cell['name'],x+16,top-15,cw-32,15,True)
        para(c,cell['dim'],x+16,top-43,cw-32,12,False,'#30526B')
        ix,iy,iw,ih=x+14,y+130,cw-28,302
        if len(cell['images'])==1:contain(c,cell['images'][0],ix,iy,iw,ih)
        else:
            contain(c,cell['images'][0],ix,iy+170,iw,132)
            contain(c,cell['images'][1],ix,iy,iw,164)
        para(c,cell['note'],x+16,y+116,cw-32,11.5)
        para(c,cell['credit'],x+16,y+34,cw-32,9.5,False,'#66747B')
        for ii,p in enumerate(cell['images']):
            sources[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_url':cell['urls'][min(ii,len(cell['urls'])-1)],'role':cell['name'],'full_photo_contained':True}
        if cell['urls']:c.linkURL(cell['urls'][0],(x+12,y+10,x+cw-12,y+45),relative=0,thickness=0)
    x=30+2*466;y=52
    para(c,'Fixed geometry and product guardrails',x+16,y+ch-35,cw-32,19,True)
    text='Use the target model camera exactly. Companion model views describe this same irregular room. Do not enlarge the room, move furniture, mirror the plan, invent storage, hide doors, remove the radiator/pipe, or change desk-facing directions. Product catalogue room backgrounds, cats, plants and props do not become room contents. Preserve the source artwork and rug pattern. New design: warm white, wood, black metal and slate-blue / teal accents.'
    para(c,text,x+16,y+ch-83,cw-32,15)
    para(c,'Full original photographs • no cropping or source-image pixel edits • Source URLs and SHA-256 hashes recorded in the adjacent JSON manifest.',30,32,W-60,10)
    c.showPage()
c.save()
subprocess.run(['pdftoppm','-r','150','-png',str(pdf),str(OUT/'product-board')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
outputs={}
for i in [1,2]:
    p=OUT/f'product-board-{i}.png'
    with Image.open(p) as im:dims=im.size
    outputs[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pixel_dimensions':dims,'source_pdf_page':i}
for rel,d in sources.items():
    if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=d['sha256']:raise RuntimeError('Source changed')
manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'authoring':'ReportLab PDF layout, rasterized with pdftoppm at 150 DPI; full photograph containment; no originals changed.','original_images_modified':False,'source_photographs':sources,'board_records':[{**b,'cells':[{**v,'images':[str(z.relative_to(ROOT)) for z in v['images']]} for v in b['cells']]} for b in boards],'outputs':outputs,'source_pdf':{'file':str(pdf.relative_to(ROOT)),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'product-reference-boards.sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(outputs,indent=2))
