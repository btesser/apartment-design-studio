"""Deliver untouched generator originals with validated optional attempt histories.

Hashes bind source bytes and declared inputs; visual fidelity is reviewed separately.
All six views are preflighted before any delivery file is written.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
EXPECTED_IDS = {f'{variant}-{view}' for variant in 'bc' for view in 'abc'}

class ProvenanceError(ValueError):
    pass

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else ROOT / path

def check_hash(path, expected, label):
    path = resolve(path)
    if not path.is_file():
        raise ProvenanceError(f'Missing {label}: {path}')
    actual = digest(path)
    if actual != expected:
        raise ProvenanceError(f'{label} hash mismatch: {path}')
    return path, actual

def unique_views(views, label):
    if not isinstance(views, list) or not all(isinstance(v, dict) and 'id' in v for v in views):
        raise ProvenanceError(f'{label} must contain view objects with IDs')
    by_id = {v['id']: v for v in views}
    if len(by_id) != len(views):
        raise ProvenanceError(f'Duplicate {label} IDs')
    if set(by_id) != EXPECTED_IDS:
        raise ProvenanceError(f'{label} IDs must be exactly {sorted(EXPECTED_IDS)}')
    return by_id

def validate_authorities(inputs):
    for file, key in [('design-spec.json', 'design_spec_sha256'),
                      ('products/selected-products.json', 'product_selection_sha256')]:
        check_hash(file, inputs.get(key), 'Authority')
    check_hash(inputs.get('product_board_provenance_file', ''),
               inputs.get('product_board_provenance_sha256'), 'Product-board provenance')

def validate_view(view):
    if not isinstance(view.get('prompt'), str) or not view['prompt'].strip():
        raise ProvenanceError(f'Missing exact prompt for {view["id"]}')
    for file, key in [(view['model'], 'model_sha256'), (view['layout'], 'layout_sha256')]:
        check_hash(file, view.get(key), 'Model/layout authority')
    paths, hashes = view.get('referenced_image_paths'), view.get('reference_sha256')
    if not isinstance(paths, list) or not isinstance(hashes, list) or not paths or len(paths) != len(hashes):
        raise ProvenanceError(f'Reference path/hash counts differ for {view["id"]}')
    for path, expected in zip(paths, hashes):
        check_hash(path, expected, 'Generation reference')

def view_binding(inputs, view):
    payload = {'view': view, 'authorities': {
        key: inputs[key] for key in ['design_spec_sha256', 'product_selection_sha256',
                                     'product_board_provenance_sha256']}}
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

def original_file(path, expected=None):
    path = resolve(path)
    if not path.is_file():
        raise ProvenanceError(f'Missing generator original: {path}')
    with path.open('rb') as stream:
        if stream.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ProvenanceError(f'Generator original is not a PNG: {path}')
    actual = digest(path)
    if expected is not None and expected != actual:
        raise ProvenanceError(f'Generator original hash mismatch: {path}')
    return path, actual

def pick(record, *keys):
    for key in keys:
        if record.get(key) is not None:
            return record[key]
    return None

def validate_attempts(result, view, inputs, source, source_sha):
    raw = result.get('generation_attempts')
    if raw is None:
        return None
    if not isinstance(raw, list) or not raw:
        raise ProvenanceError(f'Empty/malformed attempt history for {view["id"]}')
    history, accepted, seen = [], [], set()
    active_binding = view_binding(inputs, view)
    for index, attempt in enumerate(raw, 1):
        if not isinstance(attempt, dict):
            raise ProvenanceError(f'Malformed attempt for {view["id"]}')
        attempt_id = attempt.get('attempt_id', f'{view["id"]}-attempt-{index}')
        if attempt_id in seen:
            raise ProvenanceError(f'Duplicate attempt ID: {attempt_id}')
        seen.add(attempt_id)
        status = attempt.get('status')
        if status not in {'accepted', 'superseded', 'rejected'}:
            raise ProvenanceError(f'Invalid attempt status: {attempt_id}')
        authority_file = pick(attempt, 'input_authority_file', 'inputs_file')
        authority_sha = pick(attempt, 'input_authority_sha256', 'inputs_sha256')
        original = pick(attempt, 'generator_file', 'generator_original_file', 'original_file')
        expected_original = pick(attempt, 'generator_file_sha256', 'generator_sha256', 'original_sha256')
        if not all([authority_file, authority_sha, original, expected_original]):
            raise ProvenanceError(f'Attempt needs hashed input authority and original: {attempt_id}')
        authority_path, _ = check_hash(authority_file, authority_sha, 'Attempt input authority')
        snapshot = json.loads(authority_path.read_text())
        validate_authorities(snapshot)
        snapshot_views = unique_views(snapshot.get('views'), 'Attempt input views')
        view_id = attempt.get('view_id', view['id'])
        if view_id != view['id']:
            raise ProvenanceError(f'Attempt belongs to another view: {attempt_id}')
        attempted_view = snapshot_views[view_id]
        validate_view(attempted_view)
        binding = view_binding(snapshot, attempted_view)
        if attempt.get('view_input_sha256') not in [None, binding]:
            raise ProvenanceError(f'Attempt view-input binding mismatch: {attempt_id}')
        for field in ['prompt', 'referenced_image_paths', 'reference_sha256']:
            if field in attempt and attempt[field] != attempted_view[field]:
                raise ProvenanceError(f'Attempt {field} differs from authority: {attempt_id}')
        original_path, original_sha = original_file(original, expected_original)
        record = {**attempt, 'attempt_id': attempt_id, 'view_id': view_id,
                  'input_authority_file': str(authority_path), 'input_authority_sha256': authority_sha,
                  'view_input_sha256': binding, 'generator_original_file': str(original_path),
                  'generator_original_sha256': original_sha,
                  'prompt': attempted_view['prompt'],
                  'referenced_image_paths': attempted_view['referenced_image_paths'],
                  'reference_sha256': attempted_view['reference_sha256'],
                  'reference_count': len(attempted_view['referenced_image_paths']),
                  'generation_revision': attempted_view.get('generation_revision', 1),
                  'model': attempted_view['model'], 'model_sha256': attempted_view['model_sha256'],
                  'layout': attempted_view['layout'], 'layout_sha256': attempted_view['layout_sha256']}
        history.append(record)
        if status == 'accepted':
            if binding != active_binding:
                raise ProvenanceError(f'Accepted attempt does not match ACTIVE prompt/references: {attempt_id}')
            if original_path.resolve() != source.resolve() or original_sha != source_sha:
                raise ProvenanceError(f'Accepted attempt differs from selected original: {attempt_id}')
            accepted.append(attempt_id)
    if len(accepted) != 1:
        raise ProvenanceError(f'Exactly one accepted attempt required for {view["id"]}')
    if result.get('selected_attempt_id') not in [None, accepted[0]]:
        raise ProvenanceError(f'Selected attempt ID is not accepted for {view["id"]}')
    return history

def preflight(inputs, results):
    input_views = unique_views(inputs.get('views'), 'Input views')
    result_views = unique_views(results, 'Generated result views')
    validate_authorities(inputs)
    prepared = []
    for view in input_views.values():
        validate_view(view)
        result = result_views[view['id']]
        expected = pick(result, 'generator_file_sha256', 'generator_sha256', 'generated_file_sha256')
        source, source_sha = original_file(result['generator_file'], expected)
        history = validate_attempts(result, view, inputs, source, source_sha)
        target = resolve(view['target_output']).resolve()
        if not target.is_relative_to(ROOT.resolve()) or target == source.resolve():
            raise ProvenanceError(f'Invalid delivery target for {view["id"]}: {target}')
        prepared.append({'view': view, 'result': result, 'source': source,
                         'sha': source_sha, 'target': target, 'history': history})
    return prepared

def main():
    input_path = ROOT / 'images/generation-inputs.json'
    results_path = ROOT / 'images/generated-files.json'
    input_sha, result_sha = digest(input_path), digest(results_path)
    inputs, results = json.loads(input_path.read_text()), json.loads(results_path.read_text())
    prepared = preflight(inputs, results)
    manifest = {'schema_version': 2, 'workflow': inputs['workflow'],
                'date_UTC': '2026-10-08', 'finalized_UTC': datetime.now(timezone.utc).isoformat(),
                'generation_inputs_sha256': input_sha, 'generated_results_sha256': result_sha,
                'generated_pixels_edited': False, 'views': [],
                'history_note': 'Attempts bind unchanged originals to hashed exact prompts and ordered references. Visual fidelity is separately reviewed.',
                'limitations': 'Models and plans define placement and dimensions. Generated images illustrate finishes and can vary product detail.'}
    with tempfile.TemporaryDirectory(prefix='.generation-stage-', dir=ROOT) as temporary:
        staged = []
        for item in prepared:
            staged_file = Path(temporary) / (item['view']['id'] + '.png')
            shutil.copy2(item['source'], staged_file)
            if digest(staged_file) != item['sha'] or digest(item['source']) != item['sha']:
                raise ProvenanceError(f'Original/copy changed while staging: {item["view"]["id"]}')
            row = {**item['view'], 'generator_original_file': str(item['source']),
                   'tool_output_hint': item['result'].get('output_hint'),
                   'generated_file_sha256': item['sha'], 'delivered_sha256': item['sha'],
                   'reference_count': len(item['view']['referenced_image_paths']),
                   'view_input_sha256': view_binding(inputs, item['view'])}
            if item['history'] is not None:
                row['generation_attempts'] = item['history']
                row['selected_attempt_id'] = next(a['attempt_id'] for a in item['history'] if a['status'] == 'accepted')
            manifest['views'].append(row)
            staged.append((staged_file, item['target']))
        if digest(input_path) != input_sha or digest(results_path) != result_sha:
            raise ProvenanceError('Inputs/results changed during validation; no deliveries written')
        for staged_file, target in staged:
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_file, target)
        for row, item in zip(manifest['views'], prepared):
            if digest(item['target']) != row['generated_file_sha256']:
                raise ProvenanceError(f'Delivery differs from original: {row["id"]}')
        manifest_stage = Path(temporary) / 'generation-manifest.json'
        manifest_stage.write_text(json.dumps(manifest, indent=2) + '\n')
        os.replace(manifest_stage, ROOT / 'images/generation-manifest.json')
    print(f'Delivered {len(manifest["views"])} untouched originals; authorities, references and optional histories match.')

if __name__ == '__main__':
    try:
        main()
    except (ProvenanceError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f'Generation provenance validation failed: {exc}')
