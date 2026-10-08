"""Copy untouched generator outputs and record their actual inputs."""
from pathlib import Path
import json, hashlib, shutil

ROOT = Path(__file__).resolve().parent
inputs = json.loads((ROOT / 'images/generation-inputs.json').read_text())
results = json.loads((ROOT / 'images/generated-files.json').read_text())
by_id = {item['id']:item for item in results}
manifest = {'workflow':'Frozen measured 3D room renders plus original online product photographs, image generation',
            'date_UTC':'2026-10-08',
            'geometry_authority':'model/his-office-design.blend and model/layout.json',
            'geometry_layout_sha256':hashlib.sha256((ROOT / 'model/layout.json').read_bytes()).hexdigest(),
            'model_sha256':hashlib.sha256((ROOT / 'model/his-office-design.blend').read_bytes()).hexdigest(),
            'generated_pixels_edited':False,
            'limitations':'Generated photographs illustrate the design finish. For placement, orientation and measurements use the 3D model and plan; image generation can vary product detail.',
            'views':[]}
for view in inputs['views']:
    result = by_id[view['id']]
    source = Path(result['generator_file'])
    target = ROOT / view['target_output']
    if not source.is_file(): raise SystemExit(f'Generator file absent: {source}')
    for path, digest in zip(view['referenced_image_paths'], view['reference_sha256']):
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
            raise SystemExit(f'Reference changed after generation preparation: {path}')
    shutil.copy2(source, target)
    manifest['views'].append({**view,
        'generator_original_file':str(source), 'tool_output_hint':result.get('output_hint'),
        'generated_file_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'delivered_file':str(target.relative_to(ROOT)),
        'delivered_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(ROOT / 'images/generation-manifest.json').write_text(json.dumps(manifest,indent=2))
print('Copied three untouched generated originals; all reference hashes match.')
