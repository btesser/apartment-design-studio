"""Read back the archive and independently verify every manifest-listed byte stream."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
archive = ROOT.parent / 'his-office-dark-designs.zip'
prefix = 'his-office-dark-designs/'
with zipfile.ZipFile(archive) as z:
    manifest = json.loads(z.read(prefix + 'FILE-MANIFEST.json'))
    expected = {prefix + row['path'] for row in manifest['files']}
    actual = {name for name in z.namelist() if not name.endswith('/')}
    assert actual == expected | {prefix + 'FILE-MANIFEST.json'}, 'Archive member inventory differs'
    for row in manifest['files']:
        digest = hashlib.sha256()
        size = 0
        with z.open(prefix + row['path']) as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                digest.update(chunk)
                size += len(chunk)
        assert size == row['bytes'], row['path'] + ': byte count differs'
        assert digest.hexdigest() == row['sha256'], row['path'] + ': SHA-256 differs'
    generated = json.loads(z.read(prefix + 'images/generation-manifest.json'))
    assert len(generated['views']) == 6
    for view in generated['views']:
        row = next(r for r in manifest['files'] if r['path'] == view['target_output'])
        assert row['sha256'] == view['generated_file_sha256'] == view['delivered_sha256']
        assert sum(a['status'] == 'accepted' for a in view['generation_attempts']) == 1
    assert generated['generated_pixels_edited'] is False
report = {'status':'PASS', 'archive':str(archive), 'file_count':len(actual),
          'verified_manifest_files':len(manifest['files']), 'generated_views':6,
          'all_archive_bytes_sha256_verified':True, 'generator_originals_unchanged':True}
(ROOT / 'qa/delivery-integrity.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
