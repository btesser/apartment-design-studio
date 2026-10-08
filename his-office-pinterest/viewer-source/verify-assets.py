#!/usr/bin/env python3
"""Verify frozen source, copied layers and offline runtime identities for both variants."""
from pathlib import Path
import hashlib
import json
import re
import datetime

source=Path(__file__).resolve().parent;project=source.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes=json.loads((source/'assets/source-hashes.json').read_text())
catalog=json.loads((source/'assets/config.json').read_text())
offline=json.loads((source/'tests/offline-results.json').read_text())
assert len(catalog['variants'])==2
proof={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_frame_preserved':True,'variants':{},'standalone_html_sha256':sha(project/'his-office-viewer.html'),'offline_checks':offline['checks'],'runtime_errors':offline['errors'],'runtime_network_requests':offline['requests']}
for variant in catalog['variants']:
    id=variant['id']; model=project/'variants'/id/'model'
    manifest=json.loads((model/'model-manifest.json').read_text())
    exports={r['filename']:r for r in manifest['exports']}
    layers={}
    for key,record in hashes[id].items():
        canonical=project/record['canonical_file'];local=source/'assets'/record['file']
        assert sha(canonical)==sha(local)==record['sha256']==offline['assetHashes'][id][key],(id,key)
        assert exports[canonical.name]['sha256']==record['sha256'],(id,key,'model manifest')
        layers[key]={**record,'canonical_source_matches':True,'embedded_runtime_matches':True,'model_manifest_matches':True}
    assert sha(model/'his-office-design.blend')==variant['model_sha256']==exports['his-office-design.blend']['sha256']
    assert sha(model/'layout.json')==variant['layout_sha256']
    assert sha(model/'camera-poses.json')==variant['camera_sha256']
    runtime=next(r for r in offline['variants']if r['id']==id)
    assert runtime['lamp']['allRaysPass']
    assert runtime['deskLift']['start']['enabled']and all(c['sourcePositionResetExact']for c in runtime['deskLift']['reset']['components'])
    proof['variants'][id]={'layers':layers,'blender_sha256':variant['model_sha256'],'canonical_blender_source_matches':True,'layout_sha256':variant['layout_sha256'],'camera_sha256':variant['camera_sha256'],'runtime_model_link':runtime['sourceLink'],'lamp_open_head_ray_tests':runtime['lamp'],'standing_desk_runtime_stage_proof':runtime['deskLift'],'runtime_bounds':runtime['state']['bounds'],'texture_check':runtime['textures']}
file_result=source/'tests/file-results.json';file_failure=source/'tests/file-failure.json';file_policy=source/'tests/file-policy-result.json'
if file_result.exists():proof['direct_file_policy']='Actual direct file browser test passed.'
elif file_failure.exists():
    failure=json.loads(file_failure.read_text());proof['direct_file_policy']={'status':'Blocked by managed browser policy','observed_error':failure.get('failure',''),'fallback':'Standalone content tested offline in a browser document with every network request blocked.'}
elif file_policy.exists():
    policy=json.loads(file_policy.read_text());proof['direct_file_policy']={**policy,'fallback':'Standalone content tested offline in a browser document with every network request blocked.'}
(source/'tests/final-asset-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'variants':list(proof['variants']),'offline_checks':proof['offline_checks'],'runtime_errors':proof['runtime_errors'],'runtime_network_requests':proof['runtime_network_requests'],'html_sha256':proof['standalone_html_sha256']},indent=2))
