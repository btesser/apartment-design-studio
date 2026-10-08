"""Package the final B/C comparison with untouched source images and packed models."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / 'delivery'
ARCHIVE = ROOT.parent / 'his-office-dark-designs.zip'
VARIANTS = ['b-charcoal-slat', 'c-ink-studio']

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    required = [
        'START-HERE.txt', 'DESIGN-BRIEF.txt', 'His-office-B-C-design-review.pdf',
        'his-office-viewer.html', 'his-office-viewer-source.zip', 'design-spec.json',
        'images/generation-manifest.json', 'images/generation-inputs.json',
        'images/generated-files.json', 'variants/six-view-render-manifest.json',
        'qa/final-variants/final-image-QA.json', 'qa/final-variants/final-image-QA.txt',
        'qa/final-variants/final-model-QA.json', 'qa/final-variants/QA-REPORT.txt',
        'images/checkpoints/first-generation-repeated-camera/generation-inputs.json',
        'images/checkpoints/first-generation-repeated-camera/generated-files.json',
        'images/checkpoints/second-generation-camera-corrections/generation-inputs.json',
        'images/checkpoints/second-generation-camera-corrections/generated-files.json',
        'images/product-board-1.png', 'images/product-board-2-b.png',
        'images/product-board-2-c.png', 'images/product-reference-boards.sources.json',
        'products/selected-products.json',
        'layout/final-furnished-plan.png', 'layout/final-furnished-plan.pdf',
        'layout/final-furnished-plan-proof.json',
        'layout/final-furnished-review-diagram.png',
        'layout/final-plan-operation-notes.json',
    ]
    for variant in VARIANTS:
        base = f'variants/{variant}'
        required += [f'{base}/model/{name}' for name in [
            'his-office-design.blend', 'layout.json', 'his-office-design.glb',
            'his-office-shell.glb', 'his-office-furniture.glb', 'his-office-door-leaves.glb',
            'camera-poses.json', 'model-manifest.json',
            'render-provenance.json', 'tria-component-map.json',
            'MODEL-NOTES.txt', 'export-inventory-repair.json', 'final-artifacts.json',
            'renders/room-a.jpg', 'renders/room-b.jpg', 'renders/room-c.jpg',
        ]]
        required += [f'{base}/images/concept-{v}.png' for v in 'abc']
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit('Final files missing: ' + ', '.join(missing))
    generation = json.loads((ROOT / 'images/generation-manifest.json').read_text())
    if len(generation.get('views', [])) != 6:
        raise SystemExit('Expected six final generated views.')
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir()
    paths = set(required)
    for folder in ['products', 'images/reference-boards', 'images/composition-proposal',
                   'research/cohesive-composition', 'research/dark-proposals',
                   'qa/final-variants', 'layout/geometry-fit-preflight',
                   'layout/final-variants']:
        for source in (ROOT / folder).rglob('*'):
            if source.is_file() and 'checkpoints' not in source.parts and '__pycache__' not in source.parts:
                paths.add(str(source.relative_to(ROOT)))
    for name in ['His-office-B-C-design-review.sources.json', 'prepare_generation.py',
                 'finalize_generation.py', 'build_delivery_bundle.py',
                 'build_dark_design_review.py', 'dark-design-review-config.json',
                 'build_generation_revision.py', 'seal_generation_history.py',
                 'verify_delivery_bundle.py', 'model/README.txt']:
        if (ROOT / name).is_file():
            paths.add(name)
    entries = []
    for name in sorted(paths):
        source = ROOT / name
        target = STAGE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append({'path': name, 'bytes': target.stat().st_size, 'sha256': sha(target)})
    manifest = {
        'title': 'His office — two cohesive dark design alternatives',
        'authority': 'Packed Blender models/layouts define the proposed geometry. Generated images illustrate appearance.',
        'source_paths_note': 'Research and tool manifests retain original workspace paths as evidence. All delivery files are listed here by relative path.',
        'repository': 'https://github.com/btesser/apartment-design-studio',
        'files': entries,
    }
    (STAGE / 'FILE-MANIFEST.json').write_text(json.dumps(manifest, indent=2))
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for source in sorted(STAGE.rglob('*')):
            if source.is_file():
                z.write(source, 'his-office-dark-designs/' + str(source.relative_to(STAGE)))
    result = {'zip': str(ARCHIVE), 'bytes': ARCHIVE.stat().st_size,
              'file_count': len(entries) + 1, 'sha256': sha(ARCHIVE)}
    (ROOT / 'delivery-manifest.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
