#!/usr/bin/env python3
"""Bundle only runnable source assets, without build dependencies or test images."""
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parent
target=root.parent/'apartment-walkthrough-source.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as z:
    for file in root.rglob('*'):
        if not file.is_file() or any(p in ('node_modules','tests','__pycache__') for p in file.relative_to(root).parts):continue
        z.write(file,'apartment-walkthrough/'+str(file.relative_to(root)))
print(target)
