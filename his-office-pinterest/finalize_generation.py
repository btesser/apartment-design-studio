"""Deliver untouched generator originals and verify all authority/reference hashes."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

inputs = json.loads((ROOT/'images/generation-inputs.json').read_text())
results = json.loads((ROOT/'images/generated-files.json').read_text())
by_id = {item['id']:item for item in results}
if len(by_id) != len(results):
    raise SystemExit('Duplicate generated view IDs')
for file, key in [('design-spec.json','design_spec_sha256'),('products/selected-products.json','product_selection_sha256')]:
    if digest(ROOT/file) != inputs[key]:
        raise SystemExit(f'Authority changed after generation: {file}')
manifest = {'workflow':inputs['workflow'], 'date_UTC':'2026-10-08',
            'generated_pixels_edited':False, 'views':[],
            'limitations':'Models and plans define placement and dimensions. Generated images illustrate finishes and can vary product detail.'}
for view in inputs['views']:
    if view['id'] not in by_id:
        raise SystemExit(f'Generated original missing: {view["id"]}')
    for file,key in [(view['model'],'model_sha256'),(view['layout'],'layout_sha256')]:
        if digest(ROOT/file) != view[key]:
            raise SystemExit(f'Model/layout changed: {file}')
    for path, expected in zip(view['referenced_image_paths'],view['reference_sha256']):
        if digest(Path(path)) != expected:
            raise SystemExit(f'Generation reference changed: {path}')
    result=by_id[view['id']]
    source=Path(result['generator_file'])
    if not source.is_file():
        raise SystemExit(f'Missing generator file: {source}')
    target=ROOT/view['target_output']
    shutil.copy2(source,target)
    manifest['views'].append({**view,'generator_original_file':str(source),
                             'tool_output_hint':result.get('output_hint'),
                             'generated_file_sha256':digest(source),
                             'delivered_sha256':digest(target)})
(ROOT/'images/generation-manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'Delivered{len(manifest["views"])} untouched originals; authority and reference hashes match.')
