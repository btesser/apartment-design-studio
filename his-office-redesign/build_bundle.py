"""Package the finished proposal; do not include previews or unused alternatives."""
from pathlib import Path
import json, hashlib, shutil, zipfile

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / 'delivery'
ZIP = ROOT.parent / 'his-office-redesign.zip'

required = [
    'START-HERE.txt', 'DESIGN-BRIEF.txt', 'His-office-design-review.pdf',
    'his-office-viewer.html',
    'model/his-office-design.blend', 'model/his-office-design.glb',
    'model/his-office-shell.glb', 'model/his-office-door-leaves.glb',
    'model/his-office-furniture.glb', 'model/layout.json',
    'model/camera-poses.json', 'model/dimensioned-plan.png',
    'model/dimensioned-plan.pdf', 'model/product-model-notes.json',
    'model/fixed-feature-manifest.json',
    'model/renders/room-a.jpg', 'model/renders/room-b.jpg',
    'model/renders/room-c.jpg', 'model/renders/room-d.jpg',
    'model/final-model-verification.json', 'model/final-render-verification.json',
    'model/render-revision-note.json', 'model/lamp-visibility.json', 'model/README.txt',
    'images/concept-a.png', 'images/concept-b.png', 'images/concept-c.png',
    'images/generation-manifest.json', 'images/generation-inputs.json',
    'images/product-board-1.png', 'images/product-board-2.png',
    'images/product-reference-boards.pdf', 'images/product-reference-boards.sources.json',
    'geometry/room-measurements.json', 'geometry/fixed-features.json',
    'geometry/final-furnished-plan-delta.json',
    'geometry/final-plan-footprints.json',
]
missing = [name for name in required if not (ROOT / name).is_file()]
if missing:
    raise SystemExit('Final deliverables missing: ' + ', '.join(missing))
if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir()
entries = []

def add(source, target):
    source, target = Path(source), STAGE / target
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    entries.append({'path':str(target.relative_to(STAGE)),
                    'bytes':target.stat().st_size,
                    'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})

for name in required:
    add(ROOT / name, name)
for name in ['His-office-design-review.sources.json', 'his-office-viewer-source.zip']:
    if (ROOT / name).is_file():
        add(ROOT / name, name)

product_record = json.loads((ROOT / 'products/candidates/selected-products.json').read_text())
for item in product_record['items']:
    image_path = Path(item['official_image_file'])
    rel = 'products/photos/' + image_path.name
    add(image_path, rel)
    item['official_image_file'] = rel
    item.pop('rank', None)
    item['selection_status'] = 'Selected for this proposal; not purchased'
    if item['id'] == 'lagkapten-alex-single':
        item['function'] = 'Dedicated second work surface with an open knee bay and five drawers for office storage.'
    # The original retailer URL remains the source for the product details.
    item.pop('source_page_file', None)
for frame in product_record.get('selected_matching_art_frames', []):
    if isinstance(frame, dict) and frame.get('official_image_file'):
        image_path = Path(frame['official_image_file'])
        if image_path.is_file():
            rel = 'products/photos/' + image_path.name
            add(image_path, rel)
            frame['official_image_file'] = rel
            frame.pop('source_page_file', None)
product_record['verified_task_chair']['black_full_res_photo'] = 'products/photos/branch-pro-selected.jpg'
product_record['three_owned_keepers'] = product_record['three_owned_keepers'].replace('products/keepers/keepers-research.json', 'sources/keepers-research.json')
product_record.pop('art_retailer_correction', None)
out = STAGE / 'products/selected-products.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(product_record, indent=2))
entries.append({'path':str(out.relative_to(STAGE)), 'bytes':out.stat().st_size,
                'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
add(ROOT / 'products/candidates/selected-products.txt', 'products/product-links-and-prices.txt')
add(ROOT / 'products/candidates/selected-products.json', 'sources/selected-products-research.json')
add(ROOT / 'products/keepers/keepers-research.json', 'sources/keepers-research.json')
add(ROOT / 'products/keepers/keepers-findings.txt', 'sources/keepers-findings.txt')
for name in ['uplift-live-edge-pheasantwood-front.jpg',
             'uplift-v2-c-frame-industrial-official.png',
             'honeywell-B0C3BVYTXP-MAIN.jpg', 'honeywell-B0C3BVYTXP-DIMN.jpg',
             'muttros-B0HHRC6XBC-MAIN.jpg', 'muttros-B0HHRC6XBC-PT01.jpg']:
    add(ROOT / 'products/keepers' / name, 'products/photos/' + name)
for name in ['reference-brick-wall-annotated.png',
             'reference-rear-door-window-annotated.png',
             'reference-closet-entry-annotated.png']:
    add(ROOT / 'geometry' / name, 'sources/' + name)
for source in sorted((ROOT / 'qa').glob('*')):
    if source.name in {'improved-layout-planning-check.json','image-QA-first-pass.json'}:
        continue
    if source.is_file() and source.suffix in {'.json', '.txt', '.png'}:
        add(source, 'qa/' + source.name)

# Preserve the actual input references used for the final edits. Intermediate
# concepts are kept in their separate attempts folder as provenance only.
gen = json.loads((ROOT / 'images/generation-manifest.json').read_text())
add(ROOT / 'images/generation-manifest.json', 'images/generation-manifest.tool-inputs.json')
gen['original_tool_manifest'] = {
    'path': 'images/generation-manifest.tool-inputs.json',
    'sha256': hashlib.sha256((ROOT / 'images/generation-manifest.json').read_bytes()).hexdigest(),
    'note': 'Unchanged generation record used by image QA. This portable copy changes only reference paths and adds delivery paths.'
}
copied = {entry['path'] for entry in entries}
def portable_references(view):
    actual_paths = view['referenced_image_paths']
    view['tool_input_paths_at_generation'] = actual_paths
    portable = []
    for value in actual_paths:
        source = Path(value)
        relative = str(source.relative_to(ROOT))
        if relative not in copied:
            add(source, relative)
            copied.add(relative)
        portable.append(relative)
    view['referenced_image_paths'] = portable
    for photo in view.get('original_product_photographs', []):
        photo['path'] = 'products/photos/' + Path(photo['path']).name
    if view.get('upstream_generation_inputs'):
        portable_references(view['upstream_generation_inputs'])
for view in gen['views']:
    portable_references(view)
    view['target_output'] = view['delivered_file']
gen_path = STAGE / 'images/generation-manifest.json'
gen_path.write_text(json.dumps(gen, indent=2))
for entry in entries:
    if entry['path'] == 'images/generation-manifest.json':
        entry['bytes'] = gen_path.stat().st_size
        entry['sha256'] = hashlib.sha256(gen_path.read_bytes()).hexdigest()

manifest = {'title':'His office — warm modern studio',
            'date_UTC':'2026-10-08', 'files':entries,
            'scope':'Final proposal; measured 3D model is placement authority. Generated images illustrate finish and style.',
            'original_scan_included':False}
(STAGE / 'FILE-MANIFEST.json').write_text(json.dumps(manifest, indent=2))
with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for source in sorted(STAGE.rglob('*')):
        if source.is_file():
            z.write(source, 'his-office-redesign/' + str(source.relative_to(STAGE)))
print(json.dumps({'zip':str(ZIP), 'bytes':ZIP.stat().st_size,
                  'file_count':len(entries)+1, 'sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest()}, indent=2))
