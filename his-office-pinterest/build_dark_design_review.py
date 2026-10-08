#!/usr/bin/env python3
"""Build an eight-page B/C comparison from final source files; originals stay unchanged."""
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
DEFAULT={
 'plan':'layout/final-furnished-plan.png',
 'final_geometry_qa_ready':False,'final_images_accepted':False,
 'layout_source':'model/layout.json','qa_source':'qa/final-variants/QA-REPORT.json',
 'owned_task_chair':{'id':'herman-miller-owned','name':'Owned gray Herman Miller XL','price_USD':0,'line_total_USD':0,'quantity':1,'owned':True,'official_image_file':'products/owned-chair/model-confirmation-pending.jpg','source_url':None,'dimensions_note':'Exact model, footprint and source photograph pending confirmation.','note':'One owned ergonomic chair; no new-chair purchase. Final fit must use its confirmed geometry.'},
 'operation_notes':[
  'Two independent worktops face the existing workwall: vendor-sized Tria standing desk plus clear140 × 60 cm project bench. One primary task chair can transfer between them.',
  'Office items go in the Left five-drawer ALEX; folded clothes in the three-drawer STORKLINTA. Three GREJIG racks are conditional inside the unrecorded closet.',
  'Tuck the task chair before fully opening clothes drawers or moving past that area. Drawer access and maximum chair pullback are sequential uses.',
  'Keep the entry-to-rear route, closet approach, window, radiator and sealed fireplace visible and clear. Review the final model for physical fit.'
 ],
 'fit_comparison':[
  ['Earlier two-chair plan','50 cm nominal route;55 cm failed'],
  ['Final one-chair plan','Final independent route result pending'],
  ['Dresser fully open + chair pulled back','Sequential use; tuck chair for drawer access']
 ],
 'fit_note':'Scan outline uncertainty is about5–12 cm. Modeled nominal routes are planning checks, not site or accessibility guarantees.',
 'operation_summary':'Final numerical operation proof will be cited after the final variant model review.',
 'variants':{v:{'renders':{k:f'variants/{slug}/model/renders/room-{k}.jpg' for k in 'abc'},'concepts':{k:f'variants/{slug}/images/concept-{k}.png' for k in 'abc'}} for v,slug in VARIANTS.items()},
 'view_titles':{'a':'Across the workwall','b':'Toward the worktops','c':'Brick, storage and visitor seat'},
 'source_files':['products/selected-products.json','products/proposal-complements/cool-complements.json','products/wall-finish-candidates/wall-finish-proposals.json','research/dark-proposals/dark-direction-proposals.json','images/reference-boards/dark-reference-boards.sources.json']
}

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
    self.panel_subtotal=self.products['designs']['B'].get('chosen_design_material_subtotal_usd',584.85)
    self.taskchair=cfg['owned_task_chair'];self.by[self.taskchair['id']]=self.taskchair
    self.c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
    self.c.setTitle('His office — B Charcoal + Slat Bay and C Ink Studio')
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
    self.c.setFillColor(colors.HexColor(MUTED));self.c.setFont('Studio',8);self.c.drawRightString(W-M,17,f'{self.page} / 8')
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
    self.start('Design brief','One working layout. Two distinct atmospheres.','A practical studio with a standing workstation, clear project bench, closed storage and a comfortable visitor chair.')
    factw=(CW-20)/3
    for i,(v,label) in enumerate([('4.90 × 3.10 m','Irregular overall room'),('14.03 m²','Approximate measured floor area'),('3.02 m','Nominal ceiling height')]):
        x=M+i*(factw+10);box(self.c,x,469,factw,48);text(self.c,v,x+12,506,factw-24,15,True,BLUE);text(self.c,label,x+12,485,factw-24,8.2,False,MUTED)
    colw=(CW-24)/2
    for v,x in [('B',M),('C',M+colw+24)]:
        title='B — Charcoal + Slat Bay' if v=='B' else 'C — Ink Studio'
        text(self.c,title,x,455,colw,15,True)
        self.photo(self.cfg['variants'][v]['concepts']['a'],x,214,colw,228,f'Final {v} conceptA pending')
        note='A bounded vertical Black Ash bay adds architectural texture; Peppercorn charcoal surrounds it. A restrained slate/gray palette keeps the existing brick and wood floor in balance.' if v=='B' else 'Smooth deep Naval blue gives the existing workwall a clear graphic identity. The same dark furniture, gray-blue seat and muted landscape artwork keep the rest of the room calm.'
        text(self.c,note,x,201,colw,9.5)
        cost=f'${self.shared_subtotal+self.panel_subtotal:,.2f} furniture + three panels' if v=='B' else f'${self.shared_subtotal:,.2f} shared furniture'
        text(self.c,cost,x,139,colw,14,True,BLUE)
        text(self.c,'Paint / installation / extras / tax / shipping remain outside these subtotals.',x,118,colw,8.2,False,MUTED)
    box(self.c,M,48,CW,44,'#E0E7EA')
    text(self.c,'Owned gray Herman Miller chair, white Honeywell and brown wicker MUTTROS stay. The selected Branch Tria replaces the owned UPLIFT in this room proposal. One rolling chair serves two independent worktops; brick, oak floor, white ceiling and openings remain.',M+12,81,CW-24,9)
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
     ('lagkapten-alex-black-components','LAGKAPTEN / ALEX / ADILS bench','140 × 60 cm; coherent assembly H73.49cm','Left five-drawer ALEX + two right black legs; leave the project surface clear.',['products/photos/lagkapten-top-black.jpg','products/photos/alex-black-drawers.jpg','products/photos/adils-black-leg.jpg']),
     (self.taskchair['id'],self.taskchair['name'],self.taskchair['dimensions_note'],self.taskchair['note'],None),
     ('ekenaset-axvall-gray-blue','EKENÄSET · Axvall dark gray-blue','65.1 × 74.0 × 74.9 cm (W × D × H)','Compact bouclé visitor seat with walnut-effect arms; actual refreshed product form.',None),
     ('storklinta-dark-brown','STORKLINTA · dark-brown/oak','69.9 × 47.9 × 74.9 cm; three drawers','Folded-clothes storage. Anchor per IKEA instructions; verify brick fixing.',None),
     ('grejig-shoes','GREJIG · three shoe racks','58 × 27 × 17 cm each; up to three stacked','Conditional inside the existing closet; interior and hanging hems were not recorded.',None)]
    for i,(id,title,dims,note,files) in enumerate(specs):
        col,row=i%3,i//3;self.card(self.by[id],M+col*(cw+gap),62+(1-row)*232,cw,ch,title,dims,note,files)
    self.end()
 def products2(self):
    self.start('Textile, artwork and separate wall options','Shared finishes. B and C keep their own wall treatment.','The Richmond print stays horizontal above the clear project bench. Furniture prices are identical between the alternatives.')
    gap=16;cw=(CW-gap)/2;ch=205;x1=M;x2=M+cw+gap
    self.card(self.by['rift'],x1,310,cw,ch,'Rift Charcoal · 6×9 Flatwoven','182.9 × 274.3 cm; Standard Pad included','Quiet geometric low-pile cover; exact selected 6×9 pattern and rug footprint.')
    self.card(self.by['dan-hobday-richmond'],x2,310,cw,ch,'Dan Hobday — Richmond + black frame','Native landscape paper100 × 70 cm horizontally','One unchanged slate/charcoal/olive artwork; narrow black wood frame.',extra=self.by['black-frame-landscape'])
    y=91;wallB=self.products['designs']['B'];wallC=self.products['designs']['C']
    for v,x,wall in [('B',x1,wallB),('C',x2,wallC)]:
        box(self.c,x,y,cw,ch)
        if v=='B':
            ph=next(p for p in wall['photos'] if p['path'].endswith('-2.jpg'));self.photo(ph['path'],x+12,y+ch-97,150,82)
            self.c.setFillColor(colors.HexColor('#585858'));self.c.rect(x+184,y+ch-99,100,75,fill=1,stroke=0)
            title='B — Black Ash bay + Peppercorn';price='$584.85 · three panels';dims='Bay 180 × 240 cm; projection 2.2 cm';note='A fitted vertical-slat feature behind the bench. Panel mounting/end trims and paint remain to specify.';url=wall['url']
        else:
            self.c.setFillColor(colors.HexColor('#2F3D4C'));self.c.rect(x+30,y+ch-97,cw-60,82,fill=1,stroke=0)
            title='C — Naval SW6244 matte wall';price='Paint system / quantity unpriced';dims='Official RGB 47, 61, 76 · HEX #2F3D4C';note='Smooth deep-navy color on the existing workwall. Verify a physical sample in daylight and the actual overhead light.';url=wall['url']
        yy=text(self.c,title,x+12,y+ch-109,cw-24,10.5,True)-5;yy=text(self.c,price,x+12,yy,cw-24,10.2,True,BLUE)-5
        yy=text(self.c,dims,x+12,yy,cw-24,8.1,False,MUTED)-5;yy=text(self.c,note,x+12,yy,cw-24,8.2)
        assert yy>y+19,('wall card overflow',v,yy,y)
        self.link('Official wall material / color source',url,x+12,y+15,cw-24,7.7)
    text(self.c,f'Shared new furniture ${self.shared_subtotal:,.2f}  |  B + panels ${self.shared_subtotal+self.panel_subtotal:,.2f}  |  C ${self.shared_subtotal:,.2f} before paint',M,76,CW,11,True,BLUE)
    text(self.c,'Owned Herman Miller / lamp / tree excluded. Prices checked 08 Oct 2026; tax, shipping, paint preparation and installation excluded. Product photos © their respective brands / retailers.',M,56,CW,7.8,False,MUTED)
    self.end()
 def comparison(self,k):
    self.start('Camera-matched comparison',f'View {k.upper()} — '+self.cfg['view_titles'][k],'Two separate alternatives from the same modeled camera. Concepts illustrate appearance; the small model views show the geometry authority.')
    gap=24;cw=(CW-gap)/2
    for v,x in [('B',M),('C',M+cw+gap)]:
        text(self.c,'B — Charcoal + Slat Bay' if v=='B' else 'C — Ink Studio',x,517,cw,12,True,BLUE)
        self.photo(self.cfg['variants'][v]['concepts'][k],x,238,cw,267,f'Final {v} concept{k.upper()} pending')
        text(self.c,'GENERATED APPEARANCE STUDY',x,225,cw,8,True,MUTED)
        self.photo(self.cfg['variants'][v]['renders'][k],x+64,55,cw-128,151,f'Final {v} model{k.upper()} pending')
        text(self.c,'Exact 3D model reference · same camera',x,49,cw,7.9,False,MUTED)
    self.end()
 def sources(self):
    self.start('Evidence and practical limits','Use the 3D model to review physical fit','Selected retail photographs, measured model views and generated concepts remain separate, traceable references.')
    gap=30;cw=(CW-gap)/2;x1=M;x2=M+cw+gap;y=515
    y=text(self.c,'GEOMETRY, PRODUCTS AND INSPIRATION',x1,y,cw,10,True,BLUE)-15
    notes=[
     'Architecture comes from the uploaded 8_21_2026.zip Polycam scan and calibrated views: irregular closet notch, doors, rear window, sealed brick fireplace, radiator, pipe and built-in shelf nook. Source floor outline uncertainty is about5–12 cm.',
     'Supplier Tria geometry is kept at native dimensions and rematerialized to the selected Black Oak/Charcoal finish. The source Woodgrain/White GLB is not an exact-color Black Oak CAD file. Vendor dimensions have millimeter-level published/CAD rounding differences.',
     'The new Axvall visitor chair uses its actual refreshed footprint. IKEA/Branch furniture meshes and keeper proxies remain representative of product detailing. Monitor/keyboard/cables are illustrative equipment, excluded from the new-piece cost.',
     'Public Pinterest images supplied atmosphere only. The exact search returned a dynamic page shell; related public Pins were inspected individually. No logged-in personalized Pinterest browser feed was read.'
    ]
    for n in notes:y=text(self.c,n,x1,y,cw,9,leading=12.0)-13
    y=text(self.c,'ORIGINAL REFERENCES AND LINKS',x1,y,cw,10,True,BLUE)-12
    pins=read('research/dark-proposals/dark-direction-proposals.json')
    for v in ['B','C']:
        pin=next(p for p in pins['proposals'] if p['id']==v);y=self.link(v+' selected public inspiration Pin',pin['pin_url'],x1,y,cw,8.5)-7
    y=self.link('Honeywell 02E Pro official product source','https://honeywellsmartlighting.com/products/02e-pro',x1,y,cw,8.5)-7
    y=self.link('Exact owned MUTTROS brown tree source','https://www.amazon.com/dp/B0HHRC6XBC',x1,y,cw,8.5)-7
    assert y>51,('source column overflow',y)
    y=515;y=text(self.c,'OPERATION AND INSTALLATION',x2,y,cw,10,True,BLUE)-15
    limitations=[
     self.cfg['operation_summary'],
     'STORKLINTA: anchor to the wall per IKEA instructions. At most one drawer opens before Anchor/Unlock attachment; proper attachment permits multiple drawers. Confirm approved brick fixing/spacer or move it closer during installation.',
     'The closet interior and hanging hems were not recorded; shoe-rack fit remains conditional. The tree’s full branch/basket envelope is unpublished, and the lamp U-base is approximate. Verify actual reach, cables and clearances on site.',
     'Door leaves were recorded closed. Inspection views that open/hide doors use inferred states. Review the fixed architecture, door approaches and final modeled movement separately from photographic styling.',
     'B’s three panels form an intentional1.8 × 2.4 m bay under a3.02 m ceiling. Mounting may mark the wall and needs substrate-specific fixing; direct mounting does not establish the supplier’s full acoustic rating. C paint needs actual system/quantity and physical sampling.',
     'Use existing overhead lighting with a neutral/cool visual presentation and the retained white task lamp. Existing dimming, CCT and illumination level are unverified; no new ceiling fixture is selected.',
     'Generated photos are appearance studies and cannot verify dimensions. Artwork/patterns, small woodgrain and joinery details may vary; use model, product records and source photos for decisions.'
    ]
    for n in limitations:y=text(self.c,n,x2,y,cw,8.8,leading=11.6)-11
    assert y>51,('limits column overflow',y)
    text(self.c,'Products / source photos © IKEA, Branch, Ruggable, Desenio, WoodUpp, Sherwin-Williams and keeper brands. Original photos/PNGs remain unmodified; PDF uses display compression only.',M,47,CW,7.3,False,MUTED)
    self.end()
 def build(self):
    for p in self.cfg['source_files']+[self.cfg['layout_source'],self.cfg['qa_source'],'build_dark_design_review.py','dark-design-review-config.json']:
        self.record(p)
    for v,slug in VARIANTS.items():
        for p in [f'variants/{slug}/model/layout.json',f'variants/{slug}/model/camera-poses.json',f'variants/{slug}/model/final-render-verification.json',f'variants/{slug}/images/generation-manifest.json',f'variants/{slug}/qa/image-QA.json']:
            self.record(p)
    for p in sorted((ROOT/'qa/final-variants').glob('*.json')):self.record(p)
    for p in sorted((ROOT/'qa/final-variants').glob('*.txt')):self.record(p)
    self.cover();self.plan();self.products1();self.products2()
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
