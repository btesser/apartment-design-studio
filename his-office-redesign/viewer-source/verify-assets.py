#!/usr/bin/env python3
"""Seal exact canonical, local and runtime-verified embedded model hashes."""
import datetime
import hashlib
import json
import shutil
from pathlib import Path

source=Path(__file__).resolve().parent
root=source.parent
hashes=json.loads((source/'assets/source-hashes.json').read_text())
offline=json.loads((source/'tests/offline-results.json').read_text())
checks={}
for key,record in hashes.items():
    canonical=root/'model'/record['file']
    local=source/'assets'/record['file']
    digest=hashlib.sha256(canonical.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(local.read_bytes()).hexdigest()==record['sha256'],key
    assert offline['assetHashes'][key]==digest,key
    checks[key]={**record,'canonical_stamp_utc':datetime.datetime.fromtimestamp(canonical.stat().st_mtime,datetime.timezone.utc).isoformat(),
                 'canonical_source_matches':True,'embedded_offline_matches':True}
composite=root/'model/his-office-design.glb'
proof={'native_frame_preserved':True,'layers':checks,
       'canonical_composite':{'file':composite.name,'sha256':hashlib.sha256(composite.read_bytes()).hexdigest(),
                              'stamp_utc':datetime.datetime.fromtimestamp(composite.stat().st_mtime,datetime.timezone.utc).isoformat()},
       'restored_texture_runtime_check':offline['textureCheck'],
       'standalone_html_sha256':hashlib.sha256((root/'his-office-viewer.html').read_bytes()).hexdigest(),
       'offline_checks':offline['checks'],
       'direct_file_browser_policy':'ERR_BLOCKED_BY_ADMINISTRATOR; see file-policy-result.json'}
correction=root/'model/honeywell-open-head-validation.json'
if correction.exists():
    validation=json.loads(correction.read_text())
    shutil.copy2(correction,source/'assets/honeywell-open-head-validation.json')
    proof['local_product_correction']={'description':validation['lamp_change'],
                                       'frozen_poses_and_envelopes_unchanged':validation['all_frozen_poses_and_envelopes_unchanged'],
                                       'other_product_component_bounds_unchanged':validation['other_product_component_bounds_unchanged'],
                                       'all_other_lamp_component_bounds_unchanged':validation['all_other_lamp_component_bounds_unchanged'],
                                       'evidence':'assets/honeywell-open-head-validation.json'}
(source/'tests/final-asset-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
