#!/usr/bin/env python3
"""Stage only the viewer runtime files for GitHub Pages (Python standard library)."""
import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
VIEWERS = ("apartment-walkthrough", "his-office-redesign/viewer-source")
REDIRECTS = {
    "apartment-walkthrough.html": "./apartment-walkthrough/",
    "apartment-v2/apartment-walkthrough.html": "../apartment-walkthrough/",
    "his-office-redesign/his-office-viewer.html": "./viewer-source/",
    "his-office-redesign/delivery/his-office-viewer.html": "../viewer-source/",
}
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"


def runtime_files(root):
    paths = [Path("index.html")]
    for viewer in VIEWERS:
        base = Path(viewer)
        paths.extend(base / name for name in ("index.html", "app.js", "style.css", "assets/config.json"))
        paths.extend(p.relative_to(root) for p in sorted((root / base / "vendor").rglob("*")) if p.is_file())
        config = json.loads((root / base / "assets/config.json").read_text())
        for name in config["assets"].values():
            if not name:
                continue
            asset = Path(name)
            if asset.is_absolute() or ".." in asset.parts:
                raise ValueError(f"Asset must stay within {viewer}/assets: {name}")
            paths.append(base / "assets" / asset)
    return paths


def validate_file(path):
    if not path.is_file():
        raise ValueError(f"Missing runtime file: {path}. Run git lfs pull before building.")
    with path.open("rb") as stream:
        header = stream.read(128)
    if header.startswith(LFS_HEADER):
        raise ValueError(f"Unresolved Git LFS pointer: {path}. Run git lfs pull before building.")
    if path.suffix == ".glb" and header[:4] != b"glTF":
        raise ValueError(f"Invalid GLB model: {path}")


def build(root=ROOT, output=OUTPUT):
    paths = runtime_files(root)
    # Validate before replacing a previous build; never publish LFS pointer text.
    for path in paths:
        validate_file(root / path)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for path in paths:
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / path, target)
    for path, destination in REDIRECTS.items():
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        url = escape(destination, quote=True)
        target.write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta http-equiv="refresh" content="0;url={url}">'
            '<title>Open 3D viewer</title></head><body>'
            f'<a href="{url}">Open the 3D viewer</a></body></html>\n'
        )
    (output / ".nojekyll").touch()
    size = sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
    print(f"Built {output}: {len(paths)} runtime files, {size / 1048576:.1f} MiB")


if __name__ == "__main__":
    build()
