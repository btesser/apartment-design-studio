from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, landscape

ROOT = Path('/workspace/apartment-v2')
RENDERS = Path('/workspace/apartment-model/renders')
GEOMETRY = Path('/workspace/geometry-audit')
W, H = landscape(A4)
INK = HexColor('#293e36')
MUTED = HexColor('#62736a')
PAPER = HexColor('#f7f5ed')

rooms = [
    ('living', 'Upstairs living room', 'Sofa backs onto the brick wall and faces the media wall. Sofa size remains estimated.'),
    ('his-office', 'His office', 'Desk sits on the +Y wall near the rear end; the desk chair faces the work surface. Desk size is estimated.'),
    ('her-office', 'Her office', 'Vanity and chest sit on the +Y wall. Two windows remain at the front end; loveseat faces inward.'),
    ('entry', 'Entry', 'The landing, doorway and stair connection retain their recorded locations. Decor is conceptual.'),
    ('bedroom-flex', 'Proposed bedroom in the lower flex space', 'Headboard backs onto the -Y wall. Curtain is movable. Full-size dresser leaves about 0.47 m at the bed foot.'),
    ('basement-open', 'Basement lounge and dining', 'Sofa faces toward the front. Dining lies beyond it, with the table long side across the room.'),
    ('music-gym', 'Music and gym room', 'The former enclosed bedroom is used for music/gym, following Amy\u2019s revised email. Entry approach is preserved.'),
    ('kitchen', 'Existing upstairs kitchen', 'Fixture positions follow the scan. Cabinet and appliance forms are simplified; Amy supplied no kitchen redesign.'),
    ('bathroom', 'Existing upstairs bathroom', 'The bathroom door stays on its rear side wall. Fixtures are location-based proxies, without a proposed redesign.'),
]

c = canvas.Canvas(str(ROOT / 'Apartment-design-review.pdf'), pagesize=(W,H))
c.setTitle('Apartment design: registered 3D model and room views')
c.setAuthor('Apartment spatial review')
page = 0

def base(title, subtitle=''):
    global page
    page += 1
    c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 21)
    c.drawString(32,H-43,title)
    if subtitle:
        c.setFillColor(MUTED); c.setFont('Helvetica',10)
        c.drawString(32,H-64,subtitle)
    c.setStrokeColor(HexColor('#d6ded4')); c.line(32,31,W-32,31)
    c.setFillColor(MUTED); c.setFont('Helvetica',8)
    c.drawString(32,18,'Fixed 3D geometry | metres | dimensional furniture proxies | 7 October 2026')
    c.drawRightString(W-32,18,str(page))

def textblock(lines,x,y,size=12,leading=19,color=INK):
    c.setFillColor(color);c.setFont('Helvetica',size)
    for line in lines:
        c.drawString(x,y,line); y-=leading
    return y

def fitted_image(path,x,y,w,h):
    im=ImageReader(str(path));iw,ih=im.getSize(); s=min(w/iw,h/ih)
    ww,hh=iw*s,ih*s
    c.drawImage(im,x+(w-ww)/2,y+(h-hh)/2,ww,hh,mask='auto')

base('Apartment design, rebuilt on the scan','New views use one unchanged 3D scene. These replace the earlier image-generated geometry samples.')
textblock([
    'Three orientation corrections are now fixed in the model:',
    'Both office work surfaces sit on the +Y walls, registered by the fireplaces, closets and windows.',
    'The basement dining table runs across the room, rather than down the apartment\u2019s length.',
    'The bathroom entry remains on its rear side wall; the living-room media wall stays solid.',
],32,H-106,12,21)
textblock([
    'Dimensions remain in the original Polycam metre frame. The scan has not been stretched.',
    'Wall outlines are generalized, with about 0.05-0.12 m uncertainty. Listing sizes are approximate.',
    'Her office\u2019s short dimension differs by about 13% between the listing and the measured scan.',
    'Lower bathroom, laundry and utility interiors were not recorded; their shells are separately labeled inference.',
],32,H-226,11,20)
textblock([
    'Fit requiring attention: the selected king bed and 118-inch dresser leave about 0.47 m at the bed foot.',
    'The walkthrough includes a dresser-off comparison. Furniture has not been shrunk to conceal tight fits.',
    'Existing sofa/desk sizes and several product depths are estimates; the king retailer has conflicting variant data.',
],32,H-337,11,20)
textblock([
    'Open apartment-walkthrough.html to explore both levels, switch rooms and inspect the source scan.',
    'Choose Walk, then click the view. W/A/S/D move; Escape releases the mouse. Save view exports a PNG.',
    'Repairs and listing-only interiors can be shown separately. The editable Blender model is also supplied.',
],32,H-433,11,20)
c.showPage()

for stem,title in [('upper-dimensioned-plan','Upstairs: dimensions and furniture orientation'),('lower-dimensioned-plan','Basement: dimensions, movable divider and inferred areas')]:
    base(title,'Observed outlines and product footprints; door swings are schematic. Shaded utility interiors are inferred.')
    fitted_image(GEOMETRY/(stem+'.png'),24,40,W-48,H-124)
    c.showPage()

for rid,label,note in rooms:
    paths=[RENDERS/(rid+'-a.jpg'), RENDERS/(rid+'-b.jpg')]
    if not all(p.exists() for p in paths):
        raise FileNotFoundError(f'Missing final pair for {rid}: {paths}')
    base(label)
    col=(W-76)/2
    for i,p in enumerate(paths):
        fitted_image(p,32+i*(col+12),115,col,H-205)
        c.setFillColor(MUTED);c.setFont('Helvetica',9)
        c.drawString(32+i*(col+12),101,'View '+('A' if i==0 else 'B')+' - fixed perspective from the same 3D model')
    # Keep captions comfortably within page width without truncation.
    words=note.split();lines=[];line=''
    for word in words:
        trial=(line+' '+word).strip()
        if c.stringWidth(trial,'Helvetica',10)>W-64:
            lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    textblock(lines,32,77,10,14)
    c.showPage()

base('Source alignment and review trail','Amy\u2019s undimensioned schematic was aligned using room landmarks, without mirroring the scan.')
fitted_image(GEOMETRY/'amy_scan_registration.png',32,121,W-64,H-209)
textblock([
    'Sources: Amy Wu\u2019s reveal boards and shopping list; her revised bedroom/music-room layout email;',
    'the original 8_21_2026.glb capture; the approximate dimensioned listing plan; linked retailer specifications.',
    'Evidence JSONs, camera poses, repair logs and the independent QA report are included in the full download.',
],32,87,10,15)
c.showPage();c.save()
print(ROOT/'Apartment-design-review.pdf')
