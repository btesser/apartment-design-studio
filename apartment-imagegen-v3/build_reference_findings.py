import json
from pathlib import Path
P=Path('/workspace/apartment-imagegen-v3')
cams=json.loads(Path('/workspace/apartment-model/render-cameras.json').read_text())
F={
 'living':{
  'board':'Lana & Ben LIVING ROOM.jpeg',
  'preferred_base':'living-a.jpg',
  'preserve':['Sofa back follows long -Y brick wall; seats face +Y toward white media/bath wall. TV and console face sofa, coffee table between them.','Keep actual narrow 3.20m seating width and 6.70m central X span; existing 4.0m sofa envelope is an unmeasured modeled assumption, not permission to enlarge the room.','Keep both end doorways and sightlines to HIS at -X and HER at +X. Bathroom entry is on rear-facing X=-1.24 wall, not behind media console.'],
  'camera_a':'View from front +X toward rear -X: brick/sofa at image left, TV/console at image right, HIS opening in background.',
  'camera_b':'Opposite view from rear -X toward front +X: brick/sofa at image right, TV/console at image left, HER doorway in background. This reversal is camera rotation, not a mirrored floorplan.',
  'visible_weaknesses':['Grey/white wall boundary is a renderer material/shading seam, not a chair rail, ledge or half-height wall.']},
 'his-office':{
  'board':'Lana & Ben HIS OFFICE.jpeg',
  'preferred_base':'his-office-a.jpg',
  'preserve':['Desk sits against +Y white wall near rear -X end, not against the -X window/door wall. Chair faces +Y monitor; monitor screen faces into room -Y.','Keep rear exterior door and one window on -X wall. Keep closet projection and living doorway at +X end.','Three bookcases remain along +Y wall to the desk side; slim console on -Y brick side remains at X=-6.70, clear of measured fireplace center X=-5.31. Room overall approximately X4.90 byY3.10m.'],
  'camera_a':'From living entrance corner toward desk/rear end: exterior door is left, window behind/left of desk, bookcases to right. Preserve desk-wall/window-wall corner angle.',
  'camera_b':'From rear end toward closet/entry: desk is cropped at left, chair back foreground, bookcases center, large closet projection and living doorway right.',
  'visible_weaknesses':['Black exterior-door proxy in A lacks a realistic leaf/hardware; refine it as existing door/opening without moving it or turning it into an accent panel.','Neither current view clearly shows the fireplace/long brick wall; its absence from the crop is not permission to remove or relocate it.']},
 'her-office':{
  'board':'Lana & Ben HER OFFICE.jpeg',
  'preferred_base':'her-office-a.jpg',
  'preserve':['Vanity and chest sit on +Y wall, not on -X wall opposite windows. Pink chair faces +Y mirror; maintain furniture spacing and chest position toward +X window end.','Two windows share +X exterior wall. Brick/fireplace is -Y, with fireplace/art center X=5.61; closet projection and living entry are at -X.','Loveseat stays near +X/-Y corner, rotated40deg with seat facing diagonally toward -X/+Y room interior. Keep final +.08mY hearth-clearance shift. Model front-room widthY3.62m is retained; listingY3.20m disagreement does not authorize resizing.'],
  'camera_a':'From entry/brick corner toward windows: vanity left, chest center, two windows right; diagonal loveseat partially cropped right foreground.',
  'camera_b':'From window end toward entry/brick: brick fireplace/art left, closet/entry right, loveseat left foreground, pink chair cropped right. Keep clear visible hearth strip rather than sliding loveseat under fireplace.',
  'visible_weaknesses':['One window is cropped in A and both are behind the camera in B; do not reduce actual window count to one.','Grey wall shading seam is not a new architectural step or wainscot.']},
 'bedroom-flex':{
  'board':'Lana & Ben BEDROOM.jpeg',
  'preferred_base':'bedroom-flex-b.jpg',
  'preserve':['King headboard is on -Y white perimeter wall; bed foot points +Y across room. Two nightstands stay at headboard ends, not at bed foot.','Divider curtain is at X=.35, perpendicular to headboard wall and between bed and lounge. It is movable furniture, not a window curtain or a wall behind headboard.','Music/gym doorway stays at rear X=-3.80,Y[-2.15,-1.35], with approach clear. 118in dresser is offset to X=-2.225 along +Y wall, not centered on moved bed; bed-foot clearance remains approximately .47m.','Keep low basement ceiling/soffit, approximately2.63m main height. Bedroom is a zone in open flex space, with proposed X4.15 byY3.08m envelope.'],
  'camera_a':'From front/foot-side corner toward headboard: headboard centered, MUSIC/GYM doorway visible right, front-side nightstand cropped left. Preserve that doorway.',
  'camera_b':'From rear/foot-side corner: curtain on image left and white headboard wall on right; dresser is only a thin cropped strip at extreme left.',
  'visible_weaknesses':['Both cameras crop most of the dresser and foot aisle; board shows dresser front-and-center but must not override model crop or imply a wider room.','Use B plus lower dimensioned plan to prevent copying the board curtain as a backdrop behind the bed.']},
 'basement-open':{
  'board':'Lana & Ben BASEMENT.jpeg',
  'preferred_base':'basement-open-b.jpg',
  'preserve':['Lounge sofa back is toward divider/rear -X, seat faces +X dining/kitchen. Two orange swivel chairs face back toward sofa, angled inward. Keep two coffee tables between them.','Dining table long axis follows +Y across the room, not +X apartment length. Preserve six chairs facing table. Dining center is X5.00,Y-.56.','Keep stair flight and soffit/columns on +Y side; stairs ascend toward -X. Preserve roughly2.63m ceiling height, real column positions and side circulation.','Room order along +X: bedroom/curtain, lounge, dining, existing kitchen. Art on -Y wall is framed orange artwork, not a real new window.'],
  'camera_a':'From near curtain/sofa toward kitchen: stairs/columns image left, dining/kitchen far end, orange chair fronts facing toward camera/sofa; sofa is mostly cropped lower left.',
  'camera_b':'From kitchen/dining toward rear: dining table dominates foreground, stairs/columns image right, orange chair backs in midground, sofa and divider curtain in background.',
  'visible_weaknesses':['Stair proxy appears as stacked solid gold blocks/wood mass; preserve flight outline and position while giving realistic stair detailing, do not turn it into decorative timber wall.','Several black round discs are swivel-chair pedestal bases; do not duplicate them as additional coffee tables.','High black kitchen rectangles are existing opening/window proxies; preserve openings rather than using board orange artwork as a new exterior window.','B has strong wide-angle foreground enlargement of table; do not physically enlarge table or reduce lounge to reproduce its apparent size.']},
 'entry':{
  'board':'Lana & Ben ENTRYWAY.jpeg',
  'preferred_base':'entry-a.jpg',
  'preserve':['Small entry alcove remains connected to living, with existing bath/entry wall return and nearby stair/door opening. Preserve these corner and doorway lines rather than making a grand foyer.','Gold console and faceted mirror stay on X≈1.28 bath-side wall; shoe cabinet stays on opposing X≈3.7 side wall; small rug stays in entry floor. These positions are provisional staging, not an Amy-confirmed placement plan.','Keep existing sightline to living sofa/brick wall and separate opening toward HER room. Keep stair/entry passage clear.'],
  'camera_a':'From street-side alcove toward console: console/mirror foreground right, living sofa/brick background left. Use as primary frame; background living furniture is outside entry zone.',
  'camera_b':'Reverse alcove view: shoe cabinet central foreground, dark entry-door proxy left, HER sightline at right. This is opposite wall, not a second cabinet next to console.',
  'visible_weaknesses':['A lacks view of shoe cabinet/rug and B lacks console; do not force all board items into one wall or invent visible items outside crop.','Dark left rectangle in B is a door/opening placeholder, not a black feature wall.','Amy board wallpaper/paint is a finish reference, not permission to shift wall position or wrap wallpaper over living brick.']}
}
for room,r in F.items():
 r['primary_render']='/workspace/apartment-model/renders/'+r['preferred_base']
 r['paired_render']='/workspace/apartment-model/renders/'+room+'-'+('b' if '-a.' in r['preferred_base'] else 'a')+'.jpg'
 r['designer_board']='/workspace/apartment-design/designer-boards/'+r['board']
 r['cameras']={key:cams[key] for key in [room+'-a',room+'-b']}
D={'method':'Independent visual review of twelve final modeled camera renders, with final furniture manifest, measured room geometry and Amy boards. No model changes.','global_constraints':['Model camera image determines geometry, viewpoint, cropping, furniture footprints and opening locations. Amy board determines product appearance/materials, not camera or architecture.','All images are opposite views of one fixed layout; do not mirror rooms or relocate furniture to improve composition.','Use approximately81.2deg horizontal FOV from21mm/36mm camera model; do not substitute frontal moodboard framing.','Renderer wall color/shadow seams and simplified black reflective surfaces are appearance proxies, not new architectural features.'],'references':F}
(P/'geometry-reference-findings.json').write_text(json.dumps(D,indent=2))
lines=['IMAGE GENERATION GEOMETRY REFERENCE REVIEW','Reviewed all twelve final camera renders. Use modeled image as composition/geometry authority; use Amy board for finish/product appearance. Opposite views are camera changes, not mirrored layouts. All are approximately81.2degree horizontal FOV.','']
for room,r in F.items():
 lines += [room.upper()+' — preferred base '+r['preferred_base'],'A: '+r['camera_a'],'B: '+r['camera_b']]
 lines += ['Keep: '+s for s in r['preserve']]
 lines += ['Visible risk: '+s for s in r['visible_weaknesses']]
 lines += ['']
(P/'geometry-reference-findings.txt').write_text('\n'.join(lines))
print('Wrote six-room findings JSON/TXT')
