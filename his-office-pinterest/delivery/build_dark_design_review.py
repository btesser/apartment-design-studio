#!/usr/bin/env python3
"""Build an nine-page B/C comparison from final source files; originals stay unchanged."""
from __future__ import annotations
import argparse, hashlib, io, json
from pathlib import Path
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
W,H=864,648;M=32;CW=W-2*M
INK='#25343D';MUTED='#66747B';LINE='#D6DDDF';PAPER='#F1F3F3';BLUE='#335C76'
for name,fn in [('Studio','DejaVuSans.ttf'),('StudioBold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+fn))
VARIANTS={'B':'b-charcoal-slat','C':'c-ink-studio'}
DEFAULT={'plan': 'layout/final-furnished-review-diagram.png', 'final_geometry_qa_ready': True, 'final_images_accepted': True, 'layout_source': 'variants/b-charcoal-slat/model/layout.json', 'qa_source': 'qa/final-variants/QA-REPORT.txt', 'operation_notes': ['The Tria standing desk and clear 140 × 60 cm project bench are independent. One owned Mineral Aeron transfers between the two surfaces.', 'Office storage: LEFT five-drawer ALEX and two shallow MOSSLANDA ledges. Folded clothes: STORKLINTA. Three GREJIG racks are conditional inside the unrecorded closet.', 'Tuck the Aeron for clothes-drawer access and rear passage. Full drawer opening and maximum chair pullback are sequential uses.', 'Bench ledge top 1.25 m; Richmond independently hung at center 1.85 m. Primary ledge top 2.10 m; modeled Tria lift range 64.8–124.2 cm clears ledges/equipment.', 'Opal globe and small palm sit on the dresser; desk mat grounds the primary worktop. Keep the floor route and visitor corner clear.'], 'fit_comparison': [['Earlier two-chair plan', '50 cm nominal route;55 cm failed'], ['Final owned-Aeron plan', '60 cm working/pulled passes;61 cm pulled fails'], ['Open dresser + pulled chair', '33.4 cm gap; tuck chair for drawers/rear access']], 'fit_note': 'Scan outline uncertainty is about 5–12 cm. Modeled routes are nominal planning checks, not site or accessibility guarantees.', 'operation_summary': 'Nominal 60 cm person-circle routes pass working and 45 cm chair pullback; 61 cm pulled-back fails. Open-drawer gap: 78.4 cm working, 33.4 cm pulled. Tuck chair for clothes drawers/rear access; not a surveyed passage.', 'variants': {'B': {'renders': {'a': 'variants/b-charcoal-slat/model/renders/room-a.jpg', 'b': 'variants/b-charcoal-slat/model/renders/room-b.jpg', 'c': 'variants/b-charcoal-slat/model/renders/room-c.jpg'}, 'concepts': {'a': 'variants/b-charcoal-slat/images/concept-a.png', 'b': 'variants/b-charcoal-slat/images/concept-b.png', 'c': 'variants/b-charcoal-slat/images/concept-c.png'}}, 'C': {'renders': {'a': 'variants/c-ink-studio/model/renders/room-a.jpg', 'b': 'variants/c-ink-studio/model/renders/room-b.jpg', 'c': 'variants/c-ink-studio/model/renders/room-c.jpg'}, 'concepts': {'a': 'variants/c-ink-studio/images/concept-a.png', 'b': 'variants/c-ink-studio/images/concept-b.png', 'c': 'variants/c-ink-studio/images/concept-c.png'}}}, 'view_titles': {'a': 'Across the workwall', 'b': 'Toward the worktops', 'c': 'Brick, storage and visitor seat'}, 'source_files': ['products/selected-products.json', 'products/proposal-complements/cool-complements.json', 'products/owned-chair/owned-aeron-size-c-mineral.json', 'products/composition-pieces/finishing-selected-products.json', 'products/wall-finish-candidates/wall-finish-proposals.json', 'research/cohesive-composition/complete-room-composition-sources.json', 'images/product-reference-boards.sources.json', 'images/composition-proposal/Cohesive-office-composition-proposal.sources.json', 'design-spec.json', 'variants/c-ink-studio/model/layout.json', 'layout/final-furnished-plan-proof.json', 'images/generation-manifest.json', 'images/generation-inputs.json', 'layout/final-furnished-plan.pdf', 'layout/final-furnished-plan.png', 'qa/final-variants/final-model-QA.json', 'layout/final-variants/final-nominal-routing.json', 'layout/final-variants/final-nominal-routing.txt', 'images/generated-files.json', 'images/checkpoints/first-generation-repeated-camera/generation-inputs.json', 'images/checkpoints/first-generation-repeated-camera/generated-files.json', 'images/checkpoints/second-generation-camera-corrections/generation-inputs.json', 'images/checkpoints/second-generation-camera-corrections/generated-files.json', 'variants/six-view-render-manifest.json', 'variants/b-charcoal-slat/model/final-artifacts.json', 'variants/c-ink-studio/model/final-artifacts.json', 'qa/final-variants/final-image-QA.json', 'qa/final-variants/final-image-QA.txt', 'qa/final-variants/independent-viewer-QA.json', 'build_generation_revision.py', 'seal_generation_history.py', 'finalize_generation.py'], 'owned_task_chair': {'id': 'aeron-size-c-mineral', 'name': 'Owned Herman Miller Aeron Large / Size C, Mineral light gray', 'price_USD': 0, 'line_total_USD': 0, 'quantity': 1, 'source_url': 'https://store.hermanmiller.com/office-chairs-aeron/aeron-chair/100099909.html?lang=en_US', 'official_image_file': '/workspace/his-office-pinterest/products/owned-chair/aeron-c-mineral-official.png', 'owned': True, 'dimensions_note': 'Size C source normal width 71.9 cm.', 'note': 'Owned light-gray Mineral. Current source photo is representative; exact vintage/options unconfirmed.'}}

def pth(p):
    p=Path(p);return p if p.is_absolute() else ROOT/p
def read(p):return json.loads(pth(p).read_text())
def text(c,s,x,y,w,size=10,bold=False,color=INK,leading=None):
    st=ParagraphStyle('body',fontName='StudioBold' if bold else 'Studio',fontSize=size,leading=leading or size*1.32,textColor=colors.HexColor(color))
    p=Paragraph(escape(str(s)),st);_,hh=p.wrap(w,H);p.drawOn(c,x,y-hh);return y-hh
def box(c,x,y,w,h,color='#FFFFFF',radius=5):
    c.setFillColor(colors.HexColor(color));c.setStrokeColor(colors.HexColor(LINE));c.roundRect(x,y,w,h,radius,fill=1,stroke=0)
def line(c,x,y,w):c.setStrokeColor(colors.HexColor(LINE));c.line(x,y,x+w,y)

class Review:
 def __init__(self,out,cfg,preview):
    self.out,self.cfg,self.preview=out,cfg,preview;self.inputs={};self.page=0
    self.products=read('products/selected-products.json');self.by={x['id']:x for x in self.products['items']}
    # User corrected the task seat to an owned gray Herman Miller. Exclude the
    # earlier proposed Branch even if an old canonical checkpoint is still present.
    self.shared_subtotal=sum(x.get('line_total_USD',x['price_USD']*x.get('quantity',1)) for x in self.products['items'] if x['id']!='branch-pro')
    self.panel_subtotal=self.products['designs']['B']['chosen_design_material_subtotal_usd']
    self.taskchair=cfg['owned_task_chair'];self.by[self.taskchair['id']]=self.taskchair
    self.c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
    self.c.setTitle('His office — B Charcoal + Slat Bay and C Naval Studio')
    self.c.setAuthor('Apartment design review')
    self.c.setSubject('Two coherent alternatives sharing a measured furnished layout, selected real products and camera-matched concepts')
 def record(self,p):
    p=pth(p)
    if p.is_file():self.inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 def photo(self,p,x,y,w,h,label='Final image pending'):
    p=pth(p);self.record(p)
    if not p.exists():
        if not self.preview:raise FileNotFoundError(p)
        box(self.c,x,y,w,h,'#DFE5E8');text(self.c,label,x+12,y+h/2+8,w-24,12,True,MUTED);return
    with Image.open(p) as src:
        im=ImageOps.exif_transpose(src).convert('RGB');scale=min(w/im.width,h/im.height);dw,dh=im.width*scale,im.height*scale
        # Display compression only. No original source image file is written.
        maxpx=max(1000,int(max(dw,dh)/72*230))
        if max(im.size)>maxpx:im.thumbnail((maxpx,maxpx),Image.Resampling.LANCZOS)
        buf=io.BytesIO();im.save(buf,'JPEG',quality=94,optimize=True)
        self.c.drawImage(ImageReader(buf),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
 def start(self,kicker,title,sub):
    self.page+=1;box(self.c,0,0,W,H,PAPER,0)
    text(self.c,'HIS OFFICE  /  B + C',M,H-19,CW,9,True,BLUE)
    if self.preview:text(self.c,'LAYOUT PREVIEW — FINAL IMAGES / QA PENDING',W-322,H-19,290,8,True,MUTED)
    line(self.c,M,H-41,CW);text(self.c,kicker.upper(),M,H-57,CW,8.5,True,MUTED)
    text(self.c,title,M,H-75,CW,24,True)
    text(self.c,sub,M,H-111,CW,10,False,MUTED)
    line(self.c,M,33,CW);text(self.c,'Two separate dark studio alternatives • 08 October 2026',M,24,650,7.5,False,MUTED)
    self.c.setFillColor(colors.HexColor(MUTED));self.c.setFont('Studio',8);self.c.drawRightString(W-M,17,f'{self.page} / 9')
 def end(self):self.c.showPage()
 def link(self,label,url,x,y,w,size=8.5):
    low=text(self.c,label,x,y,w,size,False,BLUE);self.c.linkURL(url,(x,low-2,x+w,y+1),relative=0,thickness=0);return low
 def product_photo(self,r):
    if r.get('official_image_file'):return r['official_image_file']
    if r.get('official_photo'):return r['official_photo'].get('file',r['official_photo'].get('path'))
    ph=r.get('official_photos',[])
    if ph:return ph[0].get('file',ph[0].get('path'))
    return None
 def cover(self):
    self.start('Design brief','One working layout. Two distinct atmospheres.','An anchored workspace, softly lit clothes-storage console and connected visitor corner; the same practical layout in two wall treatments.')
    factw=(CW-20)/3
    for i,(v,label) in enumerate([('4.90 × 3.10 m','Irregular overall room'),('14.03 m²','Approximate measured floor area'),('3.02 m','Nominal ceiling height')]):
        x=M+i*(factw+10);box(self.c,x,469,factw,48);text(self.c,v,x+12,506,factw-24,15,True,BLUE);text(self.c,label,x+12,485,factw-24,8.2,False,MUTED)
    colw=(CW-24)/2
    for v,x in [('B',M),('C',M+colw+24)]:
        title='B — Charcoal + Slat Bay' if v=='B' else 'C — Naval Studio'
        text(self.c,title,x,455,colw,15,True)
        self.photo(self.cfg['variants'][v]['concepts']['a'],x,214,colw,219,f'Final {v} conceptA pending')
        note='A 3m-wide Black Ash bay anchors both worktops. Peppercorn wraps the work and window walls; matching ledges, slate art and a lit console connect the room.' if v=='B' else 'Smooth Naval wraps the same two walls. The repeated black ledges, Richmond print, opal globe and small greenery form a composed studio with gray-blue textiles.'
        text(self.c,note,x,201,colw,9.5)
        cost=f'${self.shared_subtotal+self.panel_subtotal:,.2f} pieces + five panels' if v=='B' else f'${self.shared_subtotal:,.2f} furniture + composition'
        text(self.c,cost,x,139,colw,14,True,BLUE)
        text(self.c,'Paint / installation / extras / tax / shipping remain outside these subtotals.',x,118,colw,8.2,False,MUTED)
    box(self.c,M,48,CW,44,'#E0E7EA')
    text(self.c,'Owned Mineral Aeron Size C, white Honeywell and brown wicker MUTTROS stay. The selected Branch Tria replaces the owned UPLIFT in this room proposal. One rolling chair serves two independent worktops; brick, oak floor, white ceiling and openings remain.',M+12,81,CW-24,9)
    self.end()
 def plan(self):
    self.start('Measured shared layout','Same room, furniture and facing in B and C','Final product-sized geometry controls the proposal. The original dimensioned plan is also included as a standalone PDF.')
    self.photo(self.cfg['plan'],M,131,528,384,'Final Tria / Axvall dimensioned plan pending')
    text(self.c,self.cfg['fit_note'],M,116,528,8.3,False,MUTED)
    x=582;rw=W-M-x;y=513
    text(self.c,'HOW IT WORKS',x,y,rw,10,True,BLUE);y-=24
    for i,s in enumerate(self.cfg['operation_notes'],1):
        y=text(self.c,f'{i:02d}  '+s,x,y,rw,9.1,leading=12.3)-13
    y=text(self.c,self.cfg['operation_summary'],x,y-2,rw,8.1,False,MUTED)
    assert y>=62,('plan notes overflow',y)
    # Compact comparison sits below the diagram, without claiming unreviewed site clearances.
    bx,by,bw,bh=M,51,528,42;box(self.c,bx,by,bw,bh,'#E0E7EA')
    rows=self.cfg['fit_comparison'];s=' | '.join(f'{r[0]}: {r[1]}' for r in rows)
    low=text(self.c,s,bx+10,by+bh-9,bw-20,7.7,leading=10.1);assert low>by+3,('comparison overflow',low)
    self.end()
 def card(self,r,x,y,w,h,title,dims,note,files=None,extra=None):
    box(self.c,x,y,w,h)
    ims=files or [self.product_photo(r)];ims=[i for i in ims if i]
    iw=(w-24-6*(len(ims)-1))/max(1,len(ims))
    for k,p in enumerate(ims):self.photo(p,x+12+k*(iw+6),y+h-111,iw,96)
    yy=text(self.c,title,x+12,y+h-121,w-24,10.5,True,leading=13.0)-5
    total=r.get('line_total_USD',r['price_USD']*r.get('quantity',1))
    if extra:total+=extra['price_USD']*extra.get('quantity',1)
    yy=text(self.c,('$0 new cost · OWNED' if r.get('owned') else f'${total:,.2f}')+(' · print + frame' if extra else ''),x+12,yy,w-24,10.5,True,BLUE)-5
    yy=text(self.c,dims,x+12,yy,w-24,8.1,False,MUTED,leading=10.3)-5
    yy=text(self.c,note,x+12,yy,w-24,8.2,leading=10.6)
    assert yy>y+19,('card overflow',title,yy,y)
    if r.get('source_url'):self.link('Official product / original photograph',r['source_url'],x+12,y+15,w-24,7.7)
    else:text(self.c,'Exact owned model / source pending',x+12,y+15,w-24,7.7,False,MUTED)
    if extra:self.c.linkURL(extra['source_url'],(x+w/2,y+4,x+w-12,y+19),relative=0,thickness=0)
 def products1(self):
    self.start('Selected real furniture','Two usable work surfaces, one daily work chair','Original retailer photographs and clickable source links. Exact product sizes, quantities and finishes support the model.')
    gap=12;cw=(CW-2*gap)/3;ch=220
    specs=[
     ('branch-tria-black-oak-charcoal','Branch Tria · Black Oak / Charcoal','120 × 68.5 cm top; adjustable 64.8–124.2 cm','Quality motorized primary desk, felt cable tray and charcoal three-stage frame.',None),
     ('lagkapten-alex-black-components','LAGKAPTEN / ALEX / ADILS bench','140 × 60 cm; coherent assembly H73.49 cm','Left five-drawer ALEX + two right black legs; leave the project surface clear.',['products/photos/lagkapten-top-black.jpg','products/photos/alex-black-drawers.jpg','products/photos/adils-black-leg.jpg']),
     (self.taskchair['id'],'Aeron Size C · OWNED Mineral',self.taskchair['dimensions_note'],self.taskchair['note'],None),
     ('ekenaset-axvall-gray-blue','EKENÄSET · Axvall dark gray-blue','65.1 × 74.0 × 74.9 cm (W × D × H)','Compact bouclé visitor seat with walnut-effect arms; actual refreshed product form.',None),
     ('storklinta-dark-brown','STORKLINTA · dark-brown/oak','69.9 × 47.9 × 74.9 cm; three drawers','Folded-clothes storage. Anchor per IKEA instructions; verify brick fixing.',None),
     ('grejig-shoes','GREJIG · three shoe racks','58 × 27 × 17 cm each; up to three stacked','Conditional inside the existing closet; interior and hanging hems were not recorded.',None)]
    for i,(id,title,dims,note,files) in enumerate(specs):
        col,row=i%3,i//3;self.card(self.by[id],M+col*(cw+gap),62+(1-row)*232,cw,ch,title,dims,note,files)
    self.end()
 def products2(self):
    self.start('Textile, artwork and separate wall options','A shared palette with two wall treatments','The Richmond print stays horizontal above the clear project bench. Furniture prices are identical between the alternatives.')
    gap=16;cw=(CW-gap)/2;ch=205;x1=M;x2=M+cw+gap
    self.card(self.by['rift'],x1,310,cw,ch,'Rift Charcoal · 6×9 Flatwoven','182.9 × 274.3 cm; Standard Pad included','Quiet geometric low-pile cover; exact selected 6×9 pattern and rug footprint.')
    self.card(self.by['dan-hobday-richmond'],x2,310,cw,ch,'Dan Hobday — Richmond + black frame','Native landscape paper 100 × 70 cm horizontally','One unchanged slate/charcoal/olive artwork; narrow black wood frame.',extra=self.by['black-frame-landscape'])
    y=91;wallB=self.products['designs']['B'];wallC=self.products['designs']['C']
    for v,x,wall in [('B',x1,wallB),('C',x2,wallC)]:
        box(self.c,x,y,cw,ch)
        if v=='B':
            ph=next(p for p in wall['photos'] if p['path'].endswith('-2.jpg'));self.photo(ph['path'],x+12,y+ch-97,150,82)
            self.c.setFillColor(colors.HexColor('#585858'));self.c.rect(x+184,y+ch-99,100,75,fill=1,stroke=0)
            title='B — Black Ash bay + Peppercorn';price='$974.75 · FIVE panels';dims='Bay 300 × 240 cm; projection 2.2 cm';note='Feature across BOTH desk sections, with Peppercorn work/window wall wrap. Mounting and paint remain to specify.';url=wall['url']
        else:
            self.c.setFillColor(colors.HexColor('#2F3D4C'));self.c.rect(x+30,y+ch-97,cw-60,82,fill=1,stroke=0)
            title='C — Naval SW6244 matte wall';price='Paint system / quantity unpriced';dims='Official RGB 47, 61, 76 · HEX #2F3D4C';note='Smooth Naval wraps work AND window walls. White trim, ceiling and existing brick stay; verify a physical sample.';url=wall['url']
        yy=text(self.c,title,x+12,y+ch-109,cw-24,10.5,True)-5;yy=text(self.c,price,x+12,yy,cw-24,10.2,True,BLUE)-5
        yy=text(self.c,dims,x+12,yy,cw-24,8.1,False,MUTED)-5;yy=text(self.c,note,x+12,yy,cw-24,8.2)
        assert yy>y+19,('wall card overflow',v,yy,y)
        self.link('Official wall material / color source',url,x+12,y+15,cw-24,7.7)
    text(self.c,f'Shared pieces ${self.shared_subtotal:,.2f}  |  B + panels ${self.shared_subtotal+self.panel_subtotal:,.2f}  |  C ${self.shared_subtotal:,.2f} before paint',M,76,CW,11,True,BLUE)
    text(self.c,'Owned Mineral Aeron / lamp / tree excluded. Prices checked 08 Oct 2026; tax, shipping, paint preparation and installation excluded. Product photos © their respective brands / retailers.',M,56,CW,7.8,False,MUTED)
    self.end()
 def composition_pieces(self):
    self.start('The complete composition','Repeated shelving. Opal light. Small greenery.','These actual selected pieces make the workwall and console feel intentional; they are shared by B and C.')
    gap=16;cw=(CW-gap)/2;ch=220
    specs=[
      ('mosslanda-black-display-ledge','TWO MOSSLANDA black 115 cm ledges','Native 115 × 12 × 7 cm; TWO at $19.99','Bench ledge top 1.25 m; high primary ledge top 2.10 m. Small illustrative books only; Richmond is separately mounted.'),
      ('grovemade-dark-grey-medium-plus','Grovemade · Dark Grey Medium Plus','96.52 ×40.01cm wool-felt mat','On primary Tria worktop. Source keyboard/mouse/mug are styling props, not included purchases.'),
      ('fado-kajplats-opal-table-lamp','FADO / KAJPLATS opal-light kit','Catalog Ø25.4 × H22.86 cm; bulb + remote','One white opal globe on clothes console; 4000 K preset. Model preserves supplier body Ø24.0 ×H23.6cm; catalog label differs.'),
      ('sill-small-parlor-westcott-black','Small Parlor Palm + Westcott Black','Supplier plant height 6–11 in; pot approx Ø12.7 cm','One small real palm opposite FADO on dresser. Delivered crown varies; no floor palm or ledge plant.')]
    for i,(id,title,dims,note) in enumerate(specs):
        col,row=i%2,i//2;self.card(self.by[id],M+col*(cw+gap),62+(1-row)*232,cw,ch,title,dims,note)
    text(self.c,'Five pieces / four additions: $263.96  ·  Shared core pieces $2,070.10  ·  C total $2,334.06  ·  B total $3,308.81',M,49,CW,8.4,True,BLUE)
    self.end()
 def comparison(self,k):
    self.start('Camera-matched comparison',f'View {k.upper()} — '+self.cfg['view_titles'][k],'Two separate alternatives from the same modeled camera. Concepts illustrate appearance; the small model views show the geometry authority.')
    gap=24;cw=(CW-gap)/2
    for v,x in [('B',M),('C',M+cw+gap)]:
        text(self.c,'B — Charcoal + Slat Bay' if v=='B' else 'C — Naval Studio',x,517,cw,12,True,BLUE)
        self.photo(self.cfg['variants'][v]['concepts'][k],x,238,cw,257,f'Final {v} concept{k.upper()} pending')
        text(self.c,'GENERATED APPEARANCE STUDY',x,225,cw,8,True,MUTED)
        self.photo(self.cfg['variants'][v]['renders'][k],x+64,55,cw-128,151,f'Final {v} model{k.upper()} pending')
        text(self.c,'Exact 3D model reference · same camera',x,49,cw,7.9,False,MUTED)
    self.end()
 def sources(self):
    self.start('Evidence and practical limits','Use the 3D model to review physical fit','Selected retail photographs, measured model views and generated concepts remain separate, traceable references.')
    gap=30;cw=(CW-gap)/2;x1=M;x2=M+cw+gap;y=515
    y=text(self.c,'GEOMETRY, PRODUCTS AND INSPIRATION',x1,y,cw,10,True,BLUE)-15
    notes=[
     'Architecture comes from the uploaded 8_21_2026.zip Polycam scan and calibrated views: irregular closet notch, doors, rear window, sealed brick fireplace, radiator, pipe and built-in shelf nook. Source floor outline uncertainty is about 5–12 cm.',
     'Supplier Tria geometry is kept at native dimensions and rematerialized to the selected Black Oak/Charcoal finish. The source Woodgrain/White GLB is not an exact-color Black Oak CAD file. Vendor dimensions have millimeter-level published/CAD rounding differences.',
     'The new Axvall visitor chair uses its actual refreshed footprint. IKEA/Branch furniture meshes and keeper proxies remain representative of product detailing. Monitor/keyboard/cables are illustrative equipment, excluded from the new-piece cost.',
     'Public Pinterest images supplied atmosphere only. The search was a dynamic shell; public Pins were inspected individually, without a logged-in personalized feed.',
     'Three native angles per variant were checked. Initial five-reference calls repeated a camera. Final B-angle calls used the exact model view + two product boards; A/C edits used the prior generated original + exact model view + two boards. All 14 attempts are traceable; final PNG bytes are unchanged.'
    ]
    for n in notes:y=text(self.c,n,x1,y,cw,9,leading=12.0)-13
    y=text(self.c,'ORIGINAL REFERENCES AND LINKS',x1,y,cw,10,True,BLUE)-12
    pins=read('research/cohesive-composition/complete-room-composition-sources.json')['selected_references']
    for i,pin in enumerate(pins[:2]):
        y=self.link('Whole-room composition reference '+str(i+1),pin['url'],x1,y,cw,8.5)-7
    y=self.link('Honeywell 02E Pro official product source','https://honeywellsmartlighting.com/products/02e-pro',x1,y,cw,8.5)-7
    y=self.link('Exact owned MUTTROS brown tree source','https://www.amazon.com/dp/B0HHRC6XBC',x1,y,cw,8.5)-7
    assert y>51,('source column overflow',y)
    y=515;y=text(self.c,'OPERATION AND INSTALLATION',x2,y,cw,10,True,BLUE)-15
    limitations=[
     self.cfg['operation_summary'],
     'STORKLINTA: anchor to the wall per IKEA instructions. At most one drawer opens before Anchor/Unlock attachment; proper attachment permits multiple drawers. Confirm approved brick fixing/spacer or move it closer during installation.',
     'The closet interior and hanging hems were not recorded; shoe-rack fit remains conditional. The tree’s full branch/basket envelope is unpublished, and the lamp U-base is approximate. Verify actual reach, cables and clearances on site.',
     'Door leaves were recorded closed. Inspection views that open/hide doors use inferred states. Review the fixed architecture, door approaches and final modeled movement separately from photographic styling.',
     'B’s FIVE panels form a 3.0 × 2.4 m bay across both desks. Both alternatives wrap work/window walls. Panels and ledges need substrate-specific attachment; direct mounting does not establish full acoustic ratings. Paint needs actual sampling/system/takeoff.',
     'Two ledges use source CAD; independently hang the 70 cm-high Richmond print. Verify full lift with actual equipment. Small Parlor Palm crown varies; keep it on dresser, never inflate it into a floor tree. Existing overhead CCT/dimming are unverified; FADO adds decorative light.',
     'Generated photos are appearance studies and cannot verify dimensions. Artwork/patterns, small woodgrain and joinery details may vary; use model, product records and source photos for decisions.'
    ]
    for n in limitations:y=text(self.c,n,x2,y,cw,8.8,leading=11.6)-11
    assert y>51,('limits column overflow',y)
    text(self.c,'Source photos © their respective brands / retailers. Originals remain unmodified; PDF uses display compression only. Retailer links and source hashes accompany the review.',M,47,CW,7.3,False,MUTED)
    self.end()
 def build(self):
    for p in self.cfg['source_files']+[self.cfg['layout_source'],self.cfg['qa_source'],'build_dark_design_review.py','dark-design-review-config.json']:
        self.record(p)
    for v,slug in VARIANTS.items():
        for p in [f'variants/{slug}/model/layout.json',f'variants/{slug}/model/camera-poses.json',f'variants/{slug}/model/final-render-verification.json',f'variants/{slug}/images/generation-manifest.json',f'variants/{slug}/qa/image-QA.json']:
            self.record(p)
    for p in sorted((ROOT/'qa/final-variants').rglob('*.json')):
        if 'checkpoints' not in p.parts:self.record(p)
    for p in sorted((ROOT/'qa/final-variants').rglob('*.txt')):
        if 'checkpoints' not in p.parts:self.record(p)
    self.cover();self.plan();self.products1();self.products2();self.composition_pieces()
    for k in 'abc':self.comparison(k)
    self.sources();self.c.save()
    manifest={'built_UTC':datetime.now(timezone.utc).isoformat(),'output':str(self.out),'pdf_sha256':hashlib.sha256(self.out.read_bytes()).hexdigest(),'pages':self.page,'preview_only':self.preview,'input_sha256':self.inputs,'configuration':self.cfg,'original_source_images_modified':False,'PDF_display_compression_only':True}
    mp=self.out.with_suffix('.sources.json');mp.write_text(json.dumps(manifest,indent=2)+'\n');return mp

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',default=str(ROOT/'dark-design-review-config.json'));ap.add_argument('--preview',action='store_true');ap.add_argument('--output');args=ap.parse_args()
    cp=Path(args.config);cfg=DEFAULT.copy()
    if cp.exists():cfg.update(json.loads(cp.read_text()))
    else:cp.write_text(json.dumps(cfg,indent=2)+'\n')
    if not args.preview:
        if not cfg['final_geometry_qa_ready'] or not cfg['final_images_accepted']:raise SystemExit('Final PDF waits for final geometry QA and root-accepted B/C concepts; set the configuration only after those internal checks finish.')
        required=[cfg['plan'],cfg['layout_source'],cfg['qa_source']]+[cfg['variants'][v][typ][k] for v in 'BC' for typ in ['renders','concepts'] for k in 'abc']
        missing=[str(pth(p)) for p in required if not pth(p).exists()]
        if missing:raise SystemExit('Final sources missing:\n'+'\n'.join(missing))
    out=Path(args.output) if args.output else ROOT/('His-office-B-C-design-review-layout-preview.pdf' if args.preview else 'His-office-B-C-design-review.pdf')
    if args.preview and out.name=='His-office-B-C-design-review.pdf':raise SystemExit('A preview must use a draft-specific filename.')
    review=Review(out,cfg,args.preview);m=review.build();print(json.dumps({'pdf':str(out),'sources':str(m),'pages':review.page},indent=2))
if __name__=='__main__':main()
