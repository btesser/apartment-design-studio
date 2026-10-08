import json,pathlib,hashlib,datetime
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import fitz
root=pathlib.Path('/workspace/his-office-pinterest/research')
records=json.loads((root/'pin-records.json').read_text())
notes={
'warm-minimal-desk':('Useful detail','Warm timber, black desk mat, raised laptop. Omit shelves full of decor, cyan lighting and crowded peripherals.'),
'warm-standing-desk':('Reject layout','Quiet ivory palette is attractive; freestanding oval desk with massive ribbed pedestals sacrifices room and is incompatible with kept UPLIFT.'),
'wall-storage':('Reject visual treatment','Closed drawers can be useful; open cubby wall and many pinned papers add clutter and bulk.'),
'monochrome-office':('Alternative style','Crisp charcoal closed cabinet fronts contrast white walls. Full-height dark wall and floated desk would feel heavy and consume space here.'),
'brick-wall-desk':('Useful architectural detail','Exposed brick paired with charcoal is compatible with existing shell. Discard floated meeting-table layout and busy notice board.'),
'minimal-office-storage':('Reject layout','Smooth closed drawers are useful; heavy freestanding glossy desk is oversized and aesthetically corporate.'),
'hidden-storage':('Reject source as inspiration','Promotional infographic, not a room concept. Its clutter-free claims are not evidence of a fitted solution.'),
'japandi-1':('Alternative style','Warm wood, restrained art and quiet rug. Elaborate full-height slats, decorative pedestal and freestanding desk are impractical for this footprint.'),
'japandi-stillness':('Useful palette','Warm ivory, natural wood and single restrained print. Tall full-room slat lining and plant are optional decorative architecture, not geometry references.'),
'japandi-work':('Useful work-wall detail','Desk faces wall with a clear front edge; wood and black brackets work. Reduce plants and shelves to preserve blank space and avoid standing-desk clashes.'),
'japandi-2':('Strong reference','Wall-facing desk, clear knee opening, closed drawer storage and warm wood/white mix. Use the organization, not unverified built-ins or room dimensions.'),
'japandi-3':('Duplicate','Same image as Japandi-1; count once in visual review.'),
'double-wall-desk':('Strongest functional reference','Long shallow wall-facing surface, two independent chair bays and unbroken working strip. Keep UPLIFT independent and do not replace it with a dining table.'),
'white-wood-office':('Useful palette','Warm white fronts and timber worktop. Too many pendants, live-edge shelves and tabletop vases; simplify them away.'),
'warm-naturalwood':('Useful visitor/texture reference','Warm natural materials and restrained neutral rug. Five-picture gallery and decorative lamp consume attention/work area; use one larger piece instead.'),
'clean-ultrawide':('Useful desk detail','Large desk mat and deliberately empty foreground support usable work area. Oversized ultrawide monitor would consume most of the 42-inch kept desk; equipment is not a purchase recommendation.'),
'wood-panel-wall':('Useful linear arrangement','Long wall strip and drawer pedestal. Rough timber wall, visible cables and colorful rug are busier than requested.'),
'minimal-wall-wood':('Reject source as inspiration','Close-up of timber corner, not enough view to judge usable workstation or room composition.'),
'walnut-simple':('Strongest aesthetic reference','One wide restrained art piece, warm wood, simple black lamp and uncluttered desk. Adapt the aesthetic to kept desk and ergonomic task chair.'),
'minimal-wall-decor':('Unavailable','No image returned in fetched page.'),
'industrial-darkwood':('Unavailable','No image returned in fetched page.')}
for r in records:
 label=r['label'];r['visual_review_category'],r['visual_review']=notes[label]
 if r.get('local_image_path'):
  p=pathlib.Path(r['local_image_path']);r['original_image_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  r['visual_reviewed']=label!='japandi-3'
 else:r['visual_reviewed']=False
 r['auth_access']='Public logged-out HTTP request; no account or session data used.'
(root/'reviewed-pin-records.json').write_text(json.dumps(records,indent=2))
styles=[
 {'rank':1,'name':'Warm architectural studio','functional_fit_score_out_of_10':9.4,'palette':['warm white #EAE5DC','warm dark timber #684A31','charcoal #292B2D','stone #B5ACA1','muted olive #676B56'],'primary_pins':['818740407293933462','461196818109099025','298011700363513170'],'fit':'Low visual clutter; repeated horizontal desk edges; closed storage; timber and black metal already match Pheasantwood desk, exposed brick and cat tree. Warm white lamp belongs naturally. A quiet rug and one art focal point keep the room adult without adding furniture.','translation':'Two independent wall-facing work surfaces on existing white wall, both with real knee space; understated warm-stone rug; quiet large art; olive or charcoal compact visitor chair; closed folded/office storage; keep existing brick visible.'},
 {'rank':2,'name':'Restrained Japandi','functional_fit_score_out_of_10':8.4,'palette':['chalk white','light oak','oatmeal','ink black'],'primary_pins':['607493437271382718','298011700363513170','1036742776715452888'],'fit':'Clean and calm; natural wicker cat tree integrates well. Pale all-wood treatment competes with dark Pheasantwood unless the contrast is deliberate. Full slat walls and many shelves add expense, obstructions and bulk.','translation':'Borrow quiet rug, empty worktop and closed drawers; omit slat rebuild, large plants and decorative chair as the main task chair.'},
 {'rank':3,'name':'Soft industrial monochrome','functional_fit_score_out_of_10':7.6,'palette':['charcoal','warm white','walnut','brick red'],'primary_pins':['492651646743363660','5348093277836021','957859414475071779'],'fit':'Strong adult contrast and good compatibility with existing brick/industrial desk. Risks making this narrow 14m² room heavy and visually technical. White lamp remains more conspicuous than in warm studio.','translation':'Borrow black hardware and cable discipline; avoid painting every wall charcoal or adding a full dark cabinet wall.'}
]
recommend={
 'review_date':'2026-10-08','user_search_url':'https://www.pinterest.com/search/pins/?q=office%20design%20desk%20against%20wall&rs=typed',
 'access_limit':'The exact public search URL returned a dynamic app shell with no Pin results. Related public Pins were discovered via web search, fetched individually and their actual images visually reviewed. This is not a review of a logged-in personalized search feed.',
 'counts':{'pin_pages_fetched':21,'accessible_images':19,'unique_images_visually_reviewed':18,'duplicate_images':1,'unavailable_images':2},
 'source_type_limit':'Pinterest images are aesthetic inspiration. Creator authorship, render/photograph status and exact furniture dimensions are not independently established. They cannot define the apartment geometry.',
 'ranked_styles':styles,
 'recommendation':'Warm architectural studio',
 'frozen_requirements':['Keep exact owned 42x30in Pheasantwood UPLIFT and industrial C-frame','Keep white Honeywell 02E open-frame LED lamp','Keep natural MUTTROS 59in tree with three wicker baskets, hammock and condo','Add second usable desk with knee space; do not count cabinet top as second workplace','Folded clothing, shoes and assorted office storage; hanging storage already in closet','Compact usable visitor lounge chair','Preserve scan shell, all doors, window, pipe, radiator, fireplace and orientations'],
 'working_room_principles':['Place both independent worktops against the existing long white wall to leave the center clear.','Keep 60cm or greater depth for the second real work surface; 140cm width is feasible in prior verified footprint.','A 160cm second top requires a new fit-tested shift: unchanged 140cm right edge X=-4.85 protects closet approach, extending left conflicts with UPLIFT.','Use one daily task chair plus a stowed/secondary seat only if user workflow allows it; avoid inventing two clear rolling chair paths.','Keep standing-desk swept volume clear; do not add low shelves over UPLIFT monitor travel.','Store office supplies in a drawer pedestal; folded clothes in closed chest; shoes in closet only after interior fit check.','Use one restrained large print and a quiet low pile rug rather than the prior graphic blue motif.','No decorative items in the main forward working zones.','Keep owned white lamp and wicker tree visible; coordinate palette around them rather than recoloring them.'],
 'recommended_materials':{'work_wall':'existing warm white; optional warm stone paint only as a finish suggestion','second_desk':'warm dark wood to coordinate with owned Pheasantwood without claiming an exact species match','storage':'matte warm-white or dark brown fronts; do not recolor a product while labelling it as another finish','visitor_chair':'muted olive, charcoal or warm gray low-bulk upholstery','rug':'ivory/stone low pile with very quiet border or texture; under both chair operating zones','art':'one large restrained black/ivory or earth-tone work; product imagery needed for exact selection','lighting':'owned neutral-white Honeywell plus warm overall ambient appearance; no RGB strips'},
 'proof_files':{'search_shell':'pinterest-search-response.html','reviewed_pin_metadata':'reviewed-pin-records.json','original_images':'pins/*.jpg'}}
(root/'aesthetic-recommendation.json').write_text(json.dumps(recommend,indent=2))
text='PINTEREST AESTHETIC REVIEW — HIS OFFICE\n\n'
text+=recommend['access_limit']+'\n\n'
text+='Reviewed 18 unique images from 21 public Pin pages; one duplicate and two unavailable pages. Images are inspiration, not surveyed geometry or verified product CAD.\n\n'
for st in styles:
 text+=f"{st['rank']}. {st['name']} — functional fit {st['functional_fit_score_out_of_10']}/10\n{st['fit']}\n{st['translation']}\n\n"
text+='Selected direction: Warm architectural studio. Favor space to work, calm visual rhythm, dark warm wood, existing warm white and brick, charcoal detailing and quiet stone textiles. Retain real keeper colors.\n\n'
text+='Best directly reviewed references:\n'
for label in ['double-wall-desk','walnut-simple','japandi-2','japandi-stillness','monochrome-office']:
 r=next(x for x in records if x['label']==label);text+=r['url']+'\n'+r['visual_review']+'\n\n'
text+='Functional translation:\n'+'\n'.join('- '+x for x in recommend['working_room_principles'])+'\n'
(root/'aesthetic-review.txt').write_text(text)
# Document layout contains unmodified source images; original JPEGs and hashes retained.
W,H=1000,850;c=canvas.Canvas(str(root/'Pinterest-aesthetic-review.pdf'),pagesize=(W,H))
sets=[(['double-wall-desk','walnut-simple','japandi-2'], 'Recommended: warm architectural studio', 'A long clear working strip, one restrained art focal point, closed storage.'),(['japandi-stillness','monochrome-office','brick-wall-desk'],'Other useful directions','Borrow calm textiles, charcoal details and existing brick; preserve the actual room.')]
for labels,title,subtitle in sets:
 c.setFillColor(HexColor('#F5F1EB'));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor('#232B2D'));c.setFont('Helvetica-Bold',24);c.drawString(35,808,title)
 c.setFont('Helvetica',12);c.drawString(35,783,subtitle)
 for i,label in enumerate(labels):
  r=next(x for x in records if x['label']==label);x=35+i*323;top=750;img=ImageReader(r['local_image_path']);iw,ih=img.getSize();bw,bh=298,475;scale=min(bw/iw,bh/ih);dw,dh=iw*scale,ih*scale
  c.drawImage(img,x+(bw-dw)/2,top-dh,width=dw,height=dh,preserveAspectRatio=True)
  y=255;c.setFont('Helvetica-Bold',12);c.drawString(x,y,r['visual_review_category'])
  from textwrap import wrap
  c.setFont('Helvetica',10)
  for line in wrap(r['visual_review'],48):y-=14;c.drawString(x,y,line)
  y-=22;c.setFillColor(HexColor('#355D72'));c.setFont('Helvetica',9);c.drawString(x,y,'Open original Pinterest Pin');c.linkURL(r['url'],(x,y-2,x+170,y+10),relative=0);c.setFillColor(HexColor('#232B2D'))
 c.setFont('Helvetica',9);c.drawString(35,49,'Public related Pins, individually reviewed. Exact search feed could not load without its dynamic session.')
 c.drawString(35,34,'Images establish appearance only. Apartment scan/model control geometry; original image pixels retained.')
 c.showPage()
c.save()
doc=fitz.open(root/'Pinterest-aesthetic-review.pdf')
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(root/f'pinterest-reference-board-{i+1}.png')
print('Wrote review, recommendation, 2-page linked PDF and reference board PNGs')
