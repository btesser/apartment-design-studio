#!/usr/bin/env python3
"""Build the design review (eight portrait pages plus the original vector plan) from final files; original images stay unchanged.

Run normally only after the model/QA agent confirms the final files and root saves
images/concept-a.png, concept-b.png and concept-c.png. --preview allows missing
final imagery and emits a clearly labelled layout-only PDF, never the final name.
"""
from __future__ import annotations
import argparse, hashlib, io, json, pathlib, sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = pathlib.Path(__file__).resolve().parent
PW, PH = A4
M = 36
CW = PW - M * 2
C = {'paper': '#F7F4EE', 'ink': '#233440', 'blue': '#30526B',
     'teal': '#496D72', 'line': '#D8D4CB', 'muted': '#66747B', 'white': '#FFFFFF'}
for name, file in [('Studio', 'DejaVuSans.ttf'), ('StudioBold', 'DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/' + file))
DEFAULT = {
    'plan': 'model/dimensioned-plan.png',
    'model_views': {k: f'model/renders/room-{k}.jpg' for k in 'abc'},
    'concept_views': {k: f'images/concept-{k}.png' for k in 'abc'},
    'view_titles': {k: f'View {k.upper()}' for k in 'abc'},
    'operation_notes': [
        'The two desks face the white wall. The owned UPLIFT top stays 42×30 in; the secondary desktop is 140×60 cm with its ALEX pedestal on the left.',
        'Two independent rolling task chairs face their work surfaces. The 6×9 ft rug supports the working chair zone; use the final 3D model to review pullback.',
        'Folded clothes go in STORKLINTA; office bits go in ALEX. Three GREJIG racks are a provisional idea inside the unrecorded closet, behind its closed door.',
        'Keep the living-room entry, rear door, closet approach and sealed fireplace clear. The final fit review supplies the numerical clearances.',
        'The cat-tree base and height are sourced; the full upper basket/branch span is not published. Confirm its overhang against the lamp, window and chair on site.'
    ],
    'fit_review_note': 'Final numerical operation findings are added after the independent model review.',
    'qa_source': 'qa/routing-analysis.json',
    'append_vector_plan': 'model/dimensioned-plan.pdf',
}

def load_json(path):
    return json.loads(path.read_text())

def pth(path):
    p = pathlib.Path(path)
    return p if p.is_absolute() else ROOT / p

def txt(c, x, y, s, size=10, bold=False, color='ink'):
    c.setFillColor(colors.HexColor(C[color])); c.setFont('StudioBold' if bold else 'Studio', size)
    c.drawString(x, y, s)

def para(c, s, x, y, w, size=10, leading=None, color='ink', bold=False):
    style = ParagraphStyle('body', fontName='StudioBold' if bold else 'Studio', fontSize=size,
                           leading=leading or size * 1.42, textColor=colors.HexColor(C[color]))
    pr = Paragraph(s, style); _, h = pr.wrap(w, PH)
    pr.drawOn(c, x, y - h)
    return y - h

def plain(c, s, x, y, w, **kw):
    return para(c, escape(str(s)), x, y, w, **kw)

def rect(c, x, y, w, h, color='white', radius=0, stroke=False):
    c.setFillColor(colors.HexColor(C[color])); c.setStrokeColor(colors.HexColor(C['line']))
    c.roundRect(x, y, w, h, radius, fill=1, stroke=int(stroke))

class Review:
    def __init__(self, output, cfg, preview, products, room, layout):
        self.output, self.cfg, self.preview = output, cfg, preview
        self.products, self.room, self.layout = products, room, layout
        self.by = {x['id']: x for x in products['items']}
        self.frames = {x['id']: x for x in products['selected_matching_art_frames']}
        self.inputs = {}; self.page = 0
        self.total_pages = 9 if cfg.get('append_vector_plan') and pth(cfg['append_vector_plan']).exists() else 8
        self.c = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
        self.c.setTitle('His office — warm modern studio design review')
        self.c.setAuthor('Apartment design review')
        self.c.setSubject('Measured model, selected real products and camera-matched photoreal concepts')
    def record(self, path):
        if not path.exists(): return
        self.inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    def photo(self, path, x, y, w, h, label=None):
        path = pth(path); self.record(path)
        if not path.exists():
            if not self.preview: raise FileNotFoundError(path)
            rect(self.c, x, y, w, h, 'line', 6)
            plain(self.c, label or 'Final image pending', x + 12, y + h / 2 + 10, w - 24, size=12, bold=True, color='muted')
            return
        # PDF display compression only; never write or change the source file.
        with Image.open(path) as src:
            im = ImageOps.exif_transpose(src).convert('RGB')
            ratio = min(w / im.width, h / im.height)
            dw, dh = im.width * ratio, im.height * ratio
            max_px = max(1200, int(max(dw, dh) / 72 * 220))
            if max(im.size) > max_px:
                im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
            buf = io.BytesIO(); im.save(buf, 'JPEG', quality=93, optimize=True)
            self.c.drawImage(ImageReader(buf), x + (w-dw)/2, y + (h-dh)/2, dw, dh, mask='auto')
    def start(self, kicker, title, subtitle=None):
        self.page += 1
        rect(self.c, 0, 0, PW, PH, 'paper')
        txt(self.c, M, PH - 37, 'HIS OFFICE', 9, True, 'blue')
        self.c.setStrokeColor(colors.HexColor(C['line'])); self.c.line(M, PH-49, PW-M, PH-49)
        txt(self.c, M, PH - 76, kicker.upper(), 8.5, True, 'muted')
        txt(self.c, M, PH - 110, title, 23, True)
        if subtitle: plain(self.c, subtitle, M, PH - 129, CW, size=10, color='muted')
        if self.preview:
            txt(self.c, PW - M - 151, PH - 37, 'LAYOUT PREVIEW • DRAFT', 8, True, 'teal')
        self.c.setStrokeColor(colors.HexColor(C['line'])); self.c.line(M, 36, PW-M, 36)
        txt(self.c, M, 22, 'Warm modern studio  •  Design review  •  08 October 2026', 7.5, False, 'muted')
        self.c.setFont('Studio', 8); self.c.drawRightString(PW-M, 22, f'{self.page} / {self.total_pages}')
    def end(self): self.c.showPage()
    def cover(self):
        self.start('Design brief', 'A working studio with warmth', 'Two usable work surfaces, practical closed storage and a comfortable place for a visitor.')
        top=PH-177; gap=10; boxw=(CW-gap*2)/3
        values=[('4.90 × 3.10 m','Overall irregular room'), ('14.03 m²','Generalized measured area'), ('3.02 m','Nominal ceiling height')]
        for i,(value,label) in enumerate(values):
            x=M+i*(boxw+gap); rect(self.c,x,top-65,boxw,65,'white',6)
            txt(self.c,x+12,top-26,value,15,True,'blue');plain(self.c,label,x+12,top-39,boxw-24,size=8.5,color='muted')
        y=top-92
        y=plain(self.c,'Keep the apartment’s brick, light wood floor and warm-white walls. Pheasantwood and brown wicker provide warmth; black details, slate-teal upholstery and blue graphic art give the room a clear modern character.',M,y,CW,size=11)
        colors_row=['#F1EDE4','#B98145','#33464E','#42666C','#24489B']
        labels=['Warm white','Wood / wicker','Charcoal','Slate-teal','Graphic blue']
        sy=y-48; sw=(CW-4*8)/5
        for i,(hexv,label) in enumerate(zip(colors_row,labels)):
            self.c.setFillColor(colors.HexColor(hexv));self.c.roundRect(M+i*(sw+8),sy,sw,17,4,fill=1,stroke=0)
            txt(self.c,M+i*(sw+8),sy-15,label,7.5,False,'muted')
        txt(self.c,M,sy-49,'THREE OWNED PIECES STAY',9,True,'blue')
        images=[('products/keepers/uplift-live-edge-pheasantwood-front.jpg','UPLIFT • 42×30 in','Pheasantwood barkline front / industrial steel C-frame'),('products/keepers/honeywell-B0C3BVYTXP-MAIN.jpg','Honeywell 02E Pro','White open-center LED bars / U-shaped base'),('products/keepers/muttros-B0HHRC6XBC-MAIN.jpg','MUTTROS • 59 in','Brown tree with three wicker baskets')]
        iy=sy-239
        for i,(path,title,note) in enumerate(images):
            x=M+i*(boxw+gap);rect(self.c,x,iy,boxw,170,'white',5);self.photo(path,x+5,iy+7,boxw-10,155)
            plain(self.c,title,x,iy-11,boxw,size=9,bold=True);plain(self.c,note,x,iy-27,boxw,size=8,color='muted')
        yy=iy-79
        yy=para(self.c,'<b>Function:</b> two real desks and two adjustable task chairs; folded-clothes drawers, office drawers, closet shoe storage and a compact visitor lounger.',M,yy,CW,size=10)
        yy=para(self.c,'<b>Process:</b> scan-based room model → product-sized layout and operation review → selected retailer photographs → three camera-matched photoreal concepts.',M,yy-13,CW,size=10)
        plain(self.c,'Catalog photographs establish appearance, not the owned desk’s width. The 42×30 in desktop is user-confirmed. Owned items are excluded from the new-item budget.',M,yy-19,CW,size=8.3,color='muted')
        self.end()
    def plan(self):
        self.start('Measured layout', 'Final furnished plan', 'Furniture, facing directions and fixed architecture come from the reviewed 3D model.')
        self.photo(self.cfg['plan'],M,321,CW,365,'Final dimensioned furnished plan pending')
        plain(self.c,'The original vector plan is appended on page 9 for readable detail. Dimensions summarize Polycam geometry; open/hidden doors in inspection views are inferred states.',M,309,CW,size=8.3,color='muted')
        txt(self.c,M,260,'HOW THE ROOM WORKS',9,True,'blue')
        y=244
        for i,note in enumerate(self.cfg['operation_notes'],1):
            txt(self.c,M,y-10,f'{i:02d}',8.8,True,'teal')
            y=plain(self.c,note,M+28,y,CW-28,size=9.3,leading=12.4)-9
        if self.cfg.get('fit_review_note'):
            plain(self.c,self.cfg['fit_review_note'],M,65,CW,size=8.2,color='muted')
        self.end()
    def card(self,r,x,y,w,h,title,dims,note,frame=None):
        rect(self.c,x,y,w,h,'white',7)
        self.photo(r['official_image_file'],x+10,y+h-154,w-20,132)
        ty=y+h-166
        ty=plain(self.c,title,x+13,ty,w-26,size=10.5,bold=True,leading=13.4)-8
        quantity=r['quantity'];total=r['price_USD']*quantity+(frame['price_USD'] if frame else 0)
        price=f"${total:,.2f}"+(f"  •  {quantity} × ${r['price_USD']:,.2f}" if quantity>1 else '')
        if frame:price+='  •  print + frame'
        txt(self.c,x+13,ty-8,price,10,True,'blue');ty-=24
        ty=plain(self.c,dims,x+13,ty,w-26,size=8.4,color='muted',leading=11.2)-6
        ty=plain(self.c,note,x+13,ty,w-26,size=8.3,leading=11.2)-7
        retailer='IKEA' if 'ikea.com' in r['source_url'] else 'Branch' if 'branchfurniture.com' in r['source_url'] else 'Ruggable' if 'ruggable.com' in r['source_url'] else 'Desenio'
        label=f'{retailer} product / official photo'
        txt(self.c,x+13,y+19,label,8,False,'teal');self.c.linkURL(r.get('selected_variant_url',r['source_url']),(x+13,y+16,x+w-13,y+29),relative=0,thickness=0)
        if frame:
            txt(self.c,x+13,y+6,'Matching black frame',7.2,False,'teal');self.c.linkURL(frame['source_url'],(x+13,y+3,x+w-13,y+14),relative=0,thickness=0)
    def products_page(self, second=False):
        self.start('Selected real products','Textiles, shoes and graphic art' if second else 'Work, storage and a visitor seat','Retailer photographs show the exact selected products and finishes. Links are clickable.')
        gap=16;w=(CW-gap)/2;h=284;positions=[(M,399),(M+w+gap,399),(M,99),(M+w+gap,99)]
        if not second:
            specs=[('lagkapten-alex-single','LAGKAPTEN / ALEX desk','140 × 60 × 73 cm; ALEX on the left','Black-brown top, white office drawers; a real open knee bay supports laptop work.',None),('branch-pro','Ergonomic Chair Pro • black','Two chairs; 70.1 cm caster-base diameter','Adjustable mesh task chairs for both workstations. Use the caster base when checking fit.',None),('storklinta-low-drawers','STORKLINTA • oak effect','69.85 × 47.94 × 74.93 cm','4.2 cu.ft. Wall fixing unlocks drawers: verify brick spacer or move closer.',None),('ekenaset-turquoise','EKENÄSET • gray-turquoise','64 × 78 × 76 cm nominal','Cool corduroy with warm brown wood. Compact relaxed visitor seating; Last Chance listing.',None)]
        else:
            specs=[('ruggable-inkdrop','Inkdrop Slate Blue • 6×9 ft','182.88 × 274.32 cm; flatwoven + Standard Pad','Blue-and-ivory line pattern; flatwoven cover and Standard Pad span the two chair positions.',None),('grejig-shoes','GREJIG • three racks','58 × 27 × 17 cm each; up to three stacked','Gray steel racks; nine nominal shoe pairs. Placement inside the unrecorded closet is provisional.',None),('art-blue-bold','Bold Blue • Desenio','70 × 100 cm print; matching black frame','Expressive cobalt and warm brown above the actual sealed brick fireplace.','art-black-frame-large'),('art-blue-geometric','Blue Geometric • Desenio','50 × 70 cm print; matching black frame','Slate-blue architectural shapes above the main UPLIFT work surface.','art-black-frame')]
        for (id,title,dims,note,frame),(x,y) in zip(specs,positions):self.card(self.by[id],x,y,w,h,title,dims,note,self.frames[frame] if frame else None)
        if second:
            txt(self.c,M,86,'NEW-ITEM TOTAL',9,True,'blue');self.c.setFont('StudioBold',18);self.c.drawRightString(PW-M,83,f"${self.products['total_new_items_with_frames_before_tax_shipping_USD']:,.2f}")
            plain(self.c,'Includes both Branch chairs and both matching frames. Owned keepers excluded; before tax and shipping. US prices checked 08 October 2026; art/frame sale and local stock may change.',M,68,CW,size=8,color='muted',leading=10.5)
        else:plain(self.c,'New furnishings only. Existing UPLIFT desk, Honeywell lamp and MUTTROS cat tree are retained at no new-item cost. Product photos © their respective retailers / brands.',M,89,CW,size=8.3,color='muted')
        self.end()
    def concept(self,key):
        self.start('Photoreal concept',self.cfg['view_titles'][key], 'The generated concept is paired with the exact modeled camera below.')
        self.photo(self.cfg['concept_views'][key],M,296,CW,384,f'Final generated concept {key.upper()} pending')
        txt(self.c,M,277,'GENERATED APPEARANCE STUDY',8,True,'blue')
        self.photo(self.cfg['model_views'][key],M,79,248,173,f'Final modeled camera {key.upper()} pending')
        txt(self.c,M,63,'Exact 3D model reference • same camera',8,True,'muted')
        x=M+269;w=CW-269;y=250
        y=plain(self.c,'Read the two images together',x,y,w,size=12,bold=True)-13
        y=plain(self.c,'The model fixes the room outline, camera, openings and furniture positions/facing. Real selected product photographs guide materials, forms and artwork.',x,y,w,size=9.3)-13
        y=plain(self.c,'The photoreal image illustrates the proposed finish and atmosphere. Use the dimensioned plan and interactive model to assess physical fit and operation.',x,y,w,size=9.3)-13
        plain(self.c,'Generated photographs do not supply new room measurements. Small textile, wood-grain and joinery details remain illustrative.',x,y,w,size=8.3,color='muted')
        self.end()
    def sources(self):
        self.start('Evidence and review limits','What supports this design','The measured model, product records and photographs remain separate, traceable references.')
        y=PH-173
        y=plain(self.c,'GEOMETRY AND THE THREE OWNED PIECES',M,y,CW,size=9.2,bold=True,color='blue')-11
        y=plain(self.c,'Room geometry comes from the uploaded 8_21_2026.zip / Polycam GLB and calibrated scan views. The scan retains the irregular closet notch, rear sash window, rear door, sealed brick fireplace, radiator, pipe and built-in shelf nook. The floor outline is generalized, with typical 5–12 cm uncertainty; area is about 14.03 m².',M,y,CW,size=9.5)-13
        for label,url in [('UPLIFT official desktop lookbook','https://www.upliftdesk.com/desktop-lookbook/'),('UPLIFT official V2 C-frame specification','https://www.content.upliftdesk.com/content/pdfs/desks-and-frames/frma-2-srd-c-v2-standing-desk-spec-sheet.pdf'),('Honeywell 02E Pro product source','https://honeywellsmartlighting.com/products/02e-pro'),('Exact MUTTROS brown cat-tree listing','https://www.amazon.com/dp/B0HHRC6XBC')]:
            y=para(self.c,f'<link href="{escape(url)}" color="{C["teal"]}">{escape(label)}</link>',M,y,CW,size=9)-7
        y-=9;y=plain(self.c,'HOW TO USE THE MODEL AND IMAGES',M,y,CW,size=9.2,bold=True,color='blue')-11
        limitations=[
            'The vendor ALEX/STORKLINTA and Branch source meshes were adapted to the selected size or finish. The owned UPLIFT top is user-confirmed at 42×30 in and shown about 74 cm high. Its nominal modeled sit/stand sweep was checked over 66.2–131.2 cm; actual cables, mechanism and unpublished cat branches still need on-site confirmation. Live-edge shape and wood grain are representative.',
            'STORKLINTA requires its wall fixing to unlock drawers. The modeled rear is about 8.7 cm from the brick face; confirm an approved fixing/spacer or move it closer during installation before relying on drawer operation.',
            'The closet interior was not recorded. Shoe racks behind its closed door are a provisional fit idea. Full cat-tree basket/branch span is unpublished; the upper envelope is a visual estimate, separate from its sourced floor base.',
            'Door leaves were recorded closed. Open/hidden-door viewer states and swing directions support inspection, but are inferred. The sealed fireplace and existing radiator are represented as observed.',
            'Artwork paper sizes are sourced; narrow black frame exterior dimensions/profile are estimated. Monitor, keyboard and similar equipment are illustrative and are not added to the furniture budget.',
            'Generated photographs illustrate appearance. Review the 3D model and its operation findings for geometry; verify the tight real-world fits before installation.'
        ]
        for note in limitations:y=plain(self.c,'• '+note,M,y,CW,size=9.2,leading=12.4)-10
        y-=2;y=plain(self.c,'PRODUCT AND IMAGE PROVENANCE',M,y,CW,size=9.2,bold=True,color='blue')-10
        y=plain(self.c,'Pages 3–4 link each selected product to its official US retailer source. Product photographs © IKEA, Branch, Ruggable, Desenio, UPLIFT and the respective keeper brands/sellers. This studio proposal combines newly selected real products with the three owned pieces.',M,y,CW,size=9)-11
        y=plain(self.c,'Included references: selected-products.json; geometry/room-measurements.json; model/layout.json; camera-poses.json; final source renders and the three original generated PNGs. The interactive viewer lets you inspect the same layout from other angles.',M,y,CW,size=8.5,color='muted')-10
        if self.cfg.get('qa_source'):plain(self.c,'Operation review: '+self.cfg['qa_source'],M,y,CW,size=8.1,color='muted')
        self.end()
    def build(self):
        for name in ['products/candidates/selected-products.json','products/keepers/keepers-research.json','geometry/room-measurements.json','model/layout.json','model/camera-poses.json','model/final-render-verification.json','model/lamp-visibility.json']:
            self.record(pth(name))
        self.record(ROOT / 'build_design_review.py')
        self.record(ROOT / 'design-review-config.json')
        self.record(ROOT / 'qa/keeper-part-checks.json')
        self.record(ROOT / 'qa/desk-height-operation.json')
        for source in ['qa/routing-analysis.json','qa/QA-REPORT.txt','qa/QA-REPORT.json','qa/integrated-mesh-checks.json','qa/lamp-aperture-check.json','qa/image-QA.json','qa/image-QA.txt','images/generation-inputs.json','images/product-reference-boards.sources.json']:
            self.record(ROOT / source)
        if self.cfg.get('qa_source'):self.record(pth(self.cfg['qa_source']))
        self.cover();self.plan();self.products_page();self.products_page(True)
        for key in 'abc':self.concept(key)
        self.sources();self.c.save()
        vector_plan = self.cfg.get('append_vector_plan')
        if vector_plan and pth(vector_plan).exists():
            from pypdf import PdfReader, PdfWriter
            self.record(pth(vector_plan))
            writer = PdfWriter()
            writer.append(PdfReader(str(self.output)))
            writer.append(PdfReader(str(pth(vector_plan))))
            writer.add_outline_item('Full dimensioned furnished plan', 8)
            writer.add_metadata({'/Title': 'His office — warm modern studio design review', '/Author': 'Apartment design review', '/Subject': 'Measured model, selected products and photoreal concepts'})
            temp = self.output.with_suffix('.merged.tmp.pdf')
            with temp.open('wb') as fp: writer.write(fp)
            temp.replace(self.output)
            self.page = len(writer.pages)
        manifest={'built_UTC':datetime.now(timezone.utc).isoformat(),'output':str(self.output),'pages':self.page,'preview_only':self.preview,'input_sha256':self.inputs,'configuration':self.cfg,'original_images_modified':False}
        manifest_path=self.output.with_suffix('.sources.json');manifest_path.write_text(json.dumps(manifest,indent=2))
        return manifest_path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',default=str(ROOT/'design-review-config.json'));ap.add_argument('--output');ap.add_argument('--preview',action='store_true');args=ap.parse_args()
    cfg=DEFAULT.copy();cp=pathlib.Path(args.config)
    if cp.exists():cfg.update(load_json(cp))
    else:cp.write_text(json.dumps(cfg,indent=2))
    required=[pth(cfg['plan'])]+[pth(cfg[k][v]) for k in ['model_views','concept_views'] for v in 'abc']
    if cfg.get('append_vector_plan'): required.append(pth(cfg['append_vector_plan']))
    missing=[str(x) for x in required if not x.exists()]
    if missing and not args.preview:
        print('Final PDF waits for these final image files:\n'+'\n'.join(missing),file=sys.stderr);return 2
    output=pathlib.Path(args.output) if args.output else ROOT/('His-office-design-review-layout-preview.pdf' if args.preview else 'His-office-design-review.pdf')
    if args.preview and output.name=='His-office-design-review.pdf':raise SystemExit('Preview output must have a draft-specific filename.')
    review=Review(output,cfg,args.preview,load_json(ROOT/'products/candidates/selected-products.json'),load_json(ROOT/'geometry/room-measurements.json'),load_json(ROOT/'model/layout.json'))
    manifest=review.build();print(json.dumps({'pdf':str(output),'pages':review.page,'preview':args.preview,'sources':str(manifest)}));return 0
if __name__=='__main__':raise SystemExit(main())
