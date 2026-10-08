from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
path=ROOT/'images/generation-inputs.json'; data=json.loads(path.read_text())
view=next(v for v in data['views'] if v['id']=='c')
prior={k:v for k,v in view.items() if k not in ['id','target_output']}
snapshot=ROOT/'images/attempts/repaired-c-before-edge.png'
shutil.copy2(ROOT/'images/concept-c.png',snapshot)
refs=[snapshot,ROOT/'model/renders/room-c.jpg']
view['upstream_generation_inputs']=prior
view['referenced_image_paths']=[str(p) for p in refs]
view['reference_sha256']=[hashlib.sha256(p.read_bytes()).hexdigest() for p in refs]
view['prompt']='''Make ONE tiny cleanup edit to the FIRST finished room photograph. The SECOND image is its matching exact 3D camera render. Preserve the first photograph's camera, crop, lighting, room, all furniture, every product finish, the artwork and shallow fireplace bottom rim.

Remove only the short bright horizontal WHITE LAMP BAR protruding from the extreme upper-right edge of the first photograph, near the top of the visible window strip. It extends leftward in front of the wall/window at approximately x95%-100%, y18%-20% of the frame. It is a stray floating lamp-head segment. The actual Honeywell lamp head is outside this camera view, and the matching 3D render has NO projecting bar there. Replace this stray bar with the continuation of the existing background behind it. Preserve the legitimate vertical window frame, real sash/muntin rails, glass and sill; do not remove window parts. Do not bring any other lamp or lamp post into the crop.

Do not change anything else. Keep the same teal wood-arm visitor chair, two black task chairs, oak three-drawer dresser, black radiator, white six-panel door/brass locks, natural brown cat tree at right, ivory-blue Inkdrop rug, Bold Blue art on brick, closed arched white fireplace infill and very shallow lower brick rim. No added items or new interpretation. One landscape photograph with exactly the same framing. This is local removal of that single stray horizontal lamp bar.'''
view['iteration_note']='Local edge cleanup: remove a lamp fragment outside the authoritative camera frustum. Upstream room/product references and prompts are recorded separately.'
path.write_text(json.dumps(data,indent=2))
print('C edge edit prepared, two viewed references; upstream inputs preserved')
