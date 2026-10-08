"""Read-only validation and hash manifest for the final matched six-view set."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

base=Path('/workspace/his-office-pinterest/variants')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
poses={}
for variant in ['b-charcoal-slat','c-ink-studio']:
    root=base/variant/'model'
    native_sha=sha(root/'his-office-design.blend')
    provenance=json.loads((root/'render-provenance.json').read_text())
    poses[variant]=json.loads((root/'camera-poses.json').read_text())
    assert set(provenance)=={'room-a','room-b','room-c'}
    for name in ['room-a','room-b','room-c']:
        path=root/'renders'/(name+'.jpg')
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            assert img.size==(1440,1000)
        proof=provenance[name]
        assert proof['scene_sha256']==native_sha
        assert proof['image_sha256']==sha(path)
        assert proof['maximum_samples']==64 and proof['denoising'] is False
        assert abs(proof['exposure']+.9)<1e-6
        records.append({'variant':variant,'view':name,'path':str(path),
                        'source_blend_sha256':native_sha,'render_sha256':sha(path),
                        'bytes':path.stat().st_size,'pixels':[1440,1000],
                        'provenance':proof})
    exports=[]
    for filename in ['his-office-design.blend','his-office-design.glb',
                     'his-office-shell.glb','his-office-door-leaves.glb',
                     'his-office-furniture.glb','layout.json','camera-poses.json',
                     'model-manifest.json','export-inventory-repair.json','MODEL-NOTES.txt']:
        path=root/filename
        exports.append({'filename':filename,'sha256':sha(path),'bytes':path.stat().st_size})
    (root/'final-artifacts.json').write_text(json.dumps({'variant':variant,
        'sealed_utc':datetime.now(timezone.utc).isoformat(),
        'frozen_native_scene_unchanged':True,'artifacts':exports,
        'renders':[r for r in records if r['variant']==variant]},indent=2))
assert poses['b-charcoal-slat']==poses['c-ink-studio'],'Variant cameras must match exactly'
(base/'six-view-render-manifest.json').write_text(json.dumps({
    'sealed_utc':datetime.now(timezone.utc).isoformat(),
    'image_count':6,'same_cameras_for_both_variants':True,
    'render_settings':'CyclesCPU64samples; adaptive.025/min16; exposure-.9; no denoiser',
    'renders':records},indent=2))
print('SIX_MATCHED_RENDER_SET_VERIFIED')
