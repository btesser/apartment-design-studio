"""Correct camera ambiguity without changing the frozen model or source product photographs."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
checkpoint = ROOT / 'images/checkpoints/first-generation-repeated-camera'
if (checkpoint / 'generation-inputs.json').exists():
    raise SystemExit('Initial checkpoint already sealed. Refusing to replace generation history.')
checkpoint.mkdir(parents=True, exist_ok=True)
source = ROOT / 'images/generation-inputs.json'
shutil.copy2(source, checkpoint / 'generation-inputs.json')
inputs = json.loads(source.read_text())
camera_text = {
    'b': 'CAMERA B: The camera is in the WINDOW/REAR-DOOR corner looking toward the CLOSET and visitor chair. Match the FIRST render exactly. The large light-gray Aeron back is cropped in the LEFT FOREGROUND, with part of the monitor and primary desktop at the far left. The project bench, lower ledge and Richmond art are center-left. The WHITE CLOSET DOOR with separate overhead cupboard is CENTER-RIGHT; the living entry/white door is at the RIGHT. The gray-blue visitor armchair is FULLY visible at the RIGHT, facing the workwall. The rug fills the center foreground. There is NO visible sash window, rear six-panel door, cat tree, dresser or brick fireplace in this composition; all remain behind this camera or naturally occluded. Do not show the complete two-desk workwall from the living-entry corner. Do not move the task chair or armchair to get a prettier shot.',
    'c': 'CAMERA C: The camera is beside the CLOSET at the right end of the workwall, looking BACK toward the BRICK WALL and REAR DOOR. Match the FIRST render exactly. Exposed brick fills the LEFT and center background. The CLOSED white arched infill in the shallow brick recess is at LOWER LEFT, with the gray-blue visitor armchair cropped in the LEFT FOREGROUND. The THREE-drawer clothes chest and its compact FADO/palm/tray arrangement are CENTER, with the BLACK RADIATOR immediately to its RIGHT beside the WHITE SIX-PANEL REAR DOOR. The rear door is CENTER-RIGHT. The light-gray Aeron back/arms and brown cat tree are cropped at the RIGHT FOREGROUND, still facing their fixed modeled directions. A partial narrow white sash window is at the far right edge. The rug fills the center foreground. Neither desk nor the Richmond print should be prominently visible; they are behind this camera. Do not turn this into a desk-facing photograph. The fireplace is a CLOSED white arched infill with an approximately 45mm shallow brick lip, not an open fireplace, raised hearth or mantel.',
}
for view in inputs['views']:
    if view['view'] == 'a':
        continue
    old_paths = view['referenced_image_paths']
    view['referenced_image_paths'] = [old_paths[0], old_paths[3], old_paths[4]]
    view['reference_sha256'] = [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in view['referenced_image_paths']]
    prompt = view['prompt']
    old = 'References 2 and 3 are companion views of the SAME frozen model and establish geometry. References 4 and 5 contain original real supplier/retailer product photographs and selected color/material references.'
    prompt = prompt.replace(old, 'References 2 and 3 contain original real supplier/retailer product photographs and selected color/material references. Only reference 1 defines camera and geometry. Do not take any camera, architecture or room composition from product-board room photos.')
    prompt = prompt.replace('from the companion views', 'from the first measured render')
    view['prompt'] = 'Render the EXACT FIRST IMAGE camera as one photorealistic interior photograph. The first image is not inspiration: it is the fixed projection to preserve. Preserve every visible object at its first-image screen position and size.\n\n' + camera_text[view['view']] + '\n\n' + prompt
    view['generation_revision'] = 2
    view['revision_reason'] = 'Initial multi-angle references caused the generator to repeat camera A; this attempt uses only the exact target projection plus the two original-product boards. Other measured angles remain in the native model/render provenance.'
inputs['workflow'] = 'Measured B/C models and three verified native angles establish geometry. Camera A uses all three source views plus two supplier boards; corrected B/C tool calls use only the exact target projection plus the two supplier boards to avoid competing-camera ambiguity. Generated pixels are not manually edited.'
source.write_text(json.dumps(inputs, indent=2) + '\n')
print('Prepared four exact-camera correction calls; retained all initial inputs in checkpoint.')
