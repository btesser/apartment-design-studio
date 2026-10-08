#!/usr/bin/env python3
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parent
output=root.parent/'his-office-viewer-source.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False)as archive:
    for file in sorted(root.rglob('*')):
        if not file.is_file()or any(part in ('node_modules','__pycache__')for part in file.relative_to(root).parts):continue
        archive.write(file,'his-office-viewer-source/'+str(file.relative_to(root)))
    # Make editable-model links work when the source package is extracted on
    # its own: the canonical models are siblings of the source viewer folder.
    for variant in ('b-charcoal-slat','c-ink-studio'):
        model=root.parent/'variants'/variant/'model'
        for name in ('his-office-design.blend','layout.json','camera-poses.json','model-manifest.json'):
            file=model/name
            if not file.is_file():raise FileNotFoundError(file)
            archive.write(file,'variants/'+variant+'/model/'+name)
print(output)
