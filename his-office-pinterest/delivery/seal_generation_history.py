"""Attach the actual immutable input authority to every untouched generator result."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    return json.loads(p.read_text())
current = ROOT / 'images/generation-inputs.json'
initial = ROOT / 'images/checkpoints/first-generation-repeated-camera/generation-inputs.json'
second = ROOT / 'images/checkpoints/second-generation-camera-corrections/generation-inputs.json'
initial_results = {r['id']:r for r in read(initial.parent / 'generated-files.json')}
second_results = {r['id']:r for r in read(second.parent / 'generated-files.json')}
results_path = ROOT / 'images/generated-files.json'
results = read(results_path)
def attempt(result, authority, status, reason):
    file = Path(result['generator_file'])
    return {'status':status, 'input_authority_file':str(authority.relative_to(ROOT)),
            'input_authority_sha256':sha(authority), 'view_id':result['id'],
            'generator_file':str(file), 'generator_file_sha256':sha(file),
            'reason':reason, 'tool_output_hint':result.get('output_hint')}
for result in results:
    history = [attempt(initial_results[result['id']], initial, 'superseded',
                       'Camera B/C were incorrectly repeated as A; A also needed smaller nursery palm.')]
    if result['id'].endswith('-c'):
        history.append(attempt(second_results[result['id']], second, 'superseded',
                               'Correct target camera; nursery palm foliage still oversized.'))
    history.append(attempt(result, current, 'accepted',
                           'Final selected appearance study; native model and plan remain dimension authority.'))
    result['generation_attempts'] = history
results_path.write_text(json.dumps(results, indent=2) + '\n')
print('Sealed six delivered original paths and fourteen total recorded generation attempts.')
