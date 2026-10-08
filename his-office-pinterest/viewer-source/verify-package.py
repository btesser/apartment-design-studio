#!/usr/bin/env python3
"""Check source archive contents without extracting or copying native models."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

source = Path(__file__).resolve().parent
project = source.parent
package = project / 'his-office-viewer-source.zip'


def sha(stream):
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
    return digest.hexdigest()


with zipfile.ZipFile(package) as archive:
    assert archive.testzip() is None, 'ZIP checksum failure'
    names = archive.namelist()
    assert len(names) == len(set(names)), 'Duplicate archive path'
    assert all('node_modules' not in Path(name).parts for name in names)
    assert all('__pycache__' not in Path(name).parts for name in names)
    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in names)
    for required in (
        'app.js', 'index.html', 'style.css', 'README.txt', 'TESTING.txt',
        'serve.py', 'sync-assets.py', 'build-standalone.mjs',
        'vendor/THREE-LICENSE.txt', 'vendor/BVH-LICENSE.txt',
        'tests/final-asset-proof.json', 'tests/source-results.json',
        'tests/offline-results.json', 'tests/file-policy-result.json',
    ):
        assert 'his-office-viewer-source/' + required in names, required
    verified_models = {}
    for variant in ('b-charcoal-slat', 'c-ink-studio'):
        for filename in ('his-office-design.blend', 'layout.json', 'camera-poses.json', 'model-manifest.json'):
            relative = f'variants/{variant}/model/{filename}'
            with archive.open(relative) as packed, (project / relative).open('rb') as canonical:
                packed_sha, canonical_sha = sha(packed), sha(canonical)
            assert packed_sha == canonical_sha, relative
            verified_models[relative] = packed_sha
    with package.open('rb') as stream:
        package_sha = sha(stream)
    proof = {
        'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'package_file': package.name,
        'package_sha256': package_sha,
        'package_bytes': package.stat().st_size,
        'entries': len(names),
        'zip_checksums_pass': True,
        'source_and_license_files_present': True,
        'node_modules_and_python_cache_excluded': True,
        'editable_models_and_relative_links_preserved': verified_models,
        'proof_note': 'Written after ZIP creation; package identity proof is stored beside the source rather than recursively included in its own archive.',
    }
(source / 'tests/source-package-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({key: value for key, value in proof.items() if key != 'editable_models_and_relative_links_preserved'}, indent=2))
