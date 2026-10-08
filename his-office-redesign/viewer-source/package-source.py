#!/usr/bin/env python3
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parent
output=root.parent/'his-office-viewer-source.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as archive:
    for file in root.rglob('*'):
        if not file.is_file() or any(part in ('node_modules','__pycache__') for part in file.relative_to(root).parts):continue
        if file.suffix=='.png':continue
        archive.write(file,'his-office-viewer-source/'+str(file.relative_to(root)))
print(output)
