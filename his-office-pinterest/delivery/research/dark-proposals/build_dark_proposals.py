import json,pathlib,hashlib,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import fitz
root=pathlib.Path('/workspace/his-office-pinterest/research/dark-proposals')
records=json.loads((root/'pin-records.json').read_text())+json.loads((root/'pin-records-more.json').read_text())
for r in records:
 p=r.get('local_image_path');r['visually_inspected']=bool(p)
 if p:r['original_image_sha256']=hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
 r['auth_access']='Public logged-out Pin page and public Pin image; no session data used.'
(root/'dark-reviewed-pin-records.json').write_text(json.dumps(records,indent=2))
proposals=[
 {'id':'A','name':'Graphite Studio','tagline':'Dark mineral texture. Clear worktops. Crisp light.','hero_label':'dark-cement-paper','palette':[('Graphite','#292D33'),('Slate','#535C66'),('Silver','#B8BDC3'),('Kept timber','#594637'),('Mist','#C6CBD0')],
  'vibe':'Quiet mineral texture, charcoal furniture and one restrained black-and-white print.',
  'work_wall':'Matte charcoal texture on the 4.2 m desk wall. A quiet peel-and-stick finish gives the simplest flexible accent; retain the exposed brick.',
  'room_translation':'A quality primary standing desk and fixed project bench share the work wall. Closed drawers, a charcoal rug and a compact gray visitor chair keep the center open.',
  'lighting':'Use the existing overhead light with a neutral/cool presentation and retain the white ceiling. Keep the white Honeywell task lamp. An optional wall wash creates evening atmosphere.',
  'tradeoff':'Most flexible treatment. Select a quiet finish and test adhesion against the actual wall.',
  'caption':'Inspiration image; actual room geometry and products will be modeled after your choice.'},
 {'id':'B','name':'Charcoal + Slat Bay','tagline':'Architectural texture. Black metal. Studio mood.','hero_label':'slat-ceiling','palette':[('Charcoal','#232930'),('Smoked wood','#43423F'),('Steel','#929DA8'),('Kept timber','#594637'),('Stone','#9DA2A7')],
  'vibe':'A dark slat bay gives the strongest architectural vibe. Cool charcoal and steel-gray textiles keep the room crisp.',
  'work_wall':'A bounded 1.2–1.8 m slat feature behind the fixed project bench, with charcoal across the surrounding desk wall. Define its edges cleanly within the 3.02 m room height.',
  'room_translation':'Keep the primary standing desk clear as it rises. Pair both work surfaces with quiet art, a charcoal rug, closed storage and a compact gray visitor chair.',
  'lighting':'Use the existing overhead light with a neutral/cool presentation and retain the white ceiling. Keep the white Honeywell lamp. Optional wall-wash light reveals the slat texture in the evening.',
  'tradeoff':'Panel thickness, edges and real mounting details are finalized after your choice. Treat wood panels as a fitted wall treatment.',
  'caption':'Inspiration image; keep the owned white lamp and natural cat tree colors.'},
 {'id':'C','name':'Ink Studio','tagline':'Blue-black backdrop. Quiet graphic contrast.','hero_label':'navy-two-desks','palette':[('Ink','#182937'),('Blue slate','#3B5060'),('Fog','#A9B3BD'),('Kept timber','#594637'),('Pearl','#D0D4D8')],
  'vibe':'Deep blue-black creates a cool, distinct identity. Gray textiles and one pale graphic artwork sharpen the contrast.',
  'work_wall':'Deep ink across the 4.2 m desk wall, using matte paint or a quiet verified peel-and-stick finish. Leave the brick wall exposed.',
  'room_translation':'A primary standing desk and fixed project bench form a clear horizontal work strip. Closed drawers, a quiet gray rug and a compact visitor chair keep the room usable.',
  'lighting':'Use the existing overhead light with a neutral/cool presentation and retain the white ceiling. Keep the white Honeywell task lamp. An optional wall wash creates evening atmosphere.',
  'tradeoff':'Most expressive color choice. Compare a physical sample in daylight and under the room’s overhead light.',
  'caption':'Inspiration image; actual room geometry and products will be modeled after your choice.'}
]
for p in proposals:
 r=next(x for x in records if x['label']==p['hero_label']);p['pin_url']=r['url'];p['image_source_url']=r['image_source_url'];p['original_image_path']=r['local_image_path'];p['original_image_sha256']=r['original_image_sha256']
metadata={'stage':'Research stage complete. User selected B and C as two separate modeled alternatives.','created_local_date':'2026-10-08','user_search_url':'https://www.pinterest.com/search/pins/?q=office%20design%20desk%20against%20wall&rs=typed','access_limit':'The exact search page returned a dynamic shell without public Pin results. These are related public Pins individually fetched and visually inspected; no logged-in or personalized feed was read.','source_limit':'Original public Pin image pixels are retained. Images establish aesthetic references, not creator ownership, verified installed products, surveyed dimensions or apartment layout.','room_constraints':['Usable area approximately14.03m²; overall4.90x3.10m irregular outline, ceiling3.02m.','Main white wall approximately4.2m behind two independent desk positions is the only proposed accent plane.','Keep brick rear wall, left window/door/radiator, right closet door and entry geometry.','Primary desk must be a quality standing desk; the owned42x30in Pheasantwood UPLIFT may be retained or replaced after fit/product selection. Keep white Honeywell02E lamp and natural MUTTROS cat tree.','Keep a fixed IKEA project bench as the second genuine work surface, plus folded-clothes/shoe/office storage and visitor chair.','One primary rolling chair may transfer between worktops only if the fit check permits; do not force two permanent chairs into the room.'],'proposals':proposals,'selection_status':'User selected B: Charcoal + Slat Bay and C: Ink Studio; each is to be modeled separately.'}
(root/'dark-direction-proposals.json').write_text(json.dumps(metadata,indent=2))
W,H=1400,1000;c=canvas.Canvas(str(root/'Dark-office-direction-proposals.pdf'),pagesize=(W,H))
def wrapped(text,x,y,width_chars,size=17,leading=25,maxlines=None):
 c.setFont('Helvetica',size)
 lines=textwrap.wrap(text,width_chars)
 if maxlines:lines=lines[:maxlines]
 for line in lines:c.drawString(x,y,line);y-=leading
 return y
for p in proposals:
 c.setFillColor(HexColor('#F1F3F5'));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor('#242C35'));c.setFont('Helvetica-Bold',15);c.drawString(35,955,'HIS OFFICE / DIRECTION PROPOSAL / REFERENCE IMAGE')
 c.setFont('Helvetica-Bold',34);c.drawString(35,909,p['id']+' — '+p['name'])
 c.setFont('Helvetica',19);c.drawString(35,879,p['tagline'])
 img=ImageReader(p['original_image_path']);iw,ih=img.getSize();scale=min(555/iw,710/ih);dw,dh=iw*scale,ih*scale;c.drawImage(img,35+(555-dw)/2,843-dh,width=dw,height=dh,preserveAspectRatio=True)
 x=632;y=824;c.setFont('Helvetica-Bold',18);c.drawString(x,y,'MOOD');y=wrapped(p['vibe'],x,y-27,72,18,26)
 sy=665
 for i,(name,col) in enumerate(p['palette']):
  sx=x+i*142;c.setFillColor(HexColor(col));c.rect(sx,sy,126,54,fill=1,stroke=0);c.setFillColor(HexColor('#242C35'));c.setFont('Helvetica',13);c.drawString(sx,sy-20,name)
 y=598;c.setFont('Helvetica-Bold',17);c.drawString(x,y,'ACCENT WALL');y=wrapped(p['work_wall'],x,y-27,75,17,24)
 y-=24;c.setFont('Helvetica-Bold',17);c.drawString(x,y,'FIT THIS ROOM');y=wrapped(p['room_translation'],x,y-27,75,17,24)
 y-=24;c.setFont('Helvetica-Bold',17);c.drawString(x,y,'LIGHTING');y=wrapped(p['lighting'],x,y-27,75,17,24)
 y-=24;c.setFont('Helvetica-Bold',17);c.drawString(x,y,'DETAIL AFTER YOUR CHOICE');y=wrapped(p['tradeoff'],x,y-27,75,16,22)
 c.setFillColor(HexColor('#405168'));c.setFont('Helvetica',11);c.drawString(35,78,p['pin_url']);c.linkURL(p['pin_url'],(35,74,590,91),relative=0)
 c.setFillColor(HexColor('#242C35'));wrapped(p['caption'],35,111,88,12,17)
 c.setFont('Helvetica',10);c.drawString(35,44,'Related public Pin image, individually reviewed. This is a direction board, not a render of your room. Product/mounting details follow the selected direction.')
 c.showPage()
c.save()
d=fitz.open(root/'Dark-office-direction-proposals.pdf')
for i,page in enumerate(d):page.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(root/f'proposal-{proposals[i]["id"].lower()}.png')
(root/'dark-proposals.txt').write_text('DARK / COOL HIS OFFICE DIRECTION PROPOSALS\n\n'+metadata['access_limit']+'\n\n'+'\n\n'.join(p['id']+' — '+p['name']+'\n'+p['vibe']+'\n'+p['work_wall']+'\n'+p['lighting']+'\nReference: '+p['pin_url'] for p in proposals)+'\n\nStatus: user selects a direction before Blender regeneration.\n')
print('Created three direction boards, linked PDF and provenance JSON; no model changed.')
