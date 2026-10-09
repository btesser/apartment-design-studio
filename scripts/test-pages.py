#!/usr/bin/env python3
"""Check deployment assets and URL resolution under a GitHub project prefix."""
import importlib.util
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

spec = importlib.util.spec_from_file_location("build_pages", Path(__file__).with_name("build-pages.py"))
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.urls = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs if key in ("href", "src"))


class PagesTests(unittest.TestCase):
    def test_site_under_project_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory) / "site"
            pages.build(output=site)
            prefix = "https://example.github.io/apartment-design-studio/"
            for html in site.rglob("*.html"):
                for link in Links(html.read_text()).urls:
                    if link.startswith("data:"):
                        continue
                    resolved = urljoin(prefix + html.relative_to(site).as_posix(), link)
                    self.assertTrue(resolved.startswith(prefix), resolved)
                    target = site / urlparse(resolved[len(prefix):]).path
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), str(target))
            for viewer in pages.VIEWERS:
                config = json.loads((site / viewer / "assets/config.json").read_text())
                for asset in pages.asset_names(config):
                    if asset:
                        self.assertEqual((site / viewer / "assets" / asset).read_bytes()[:4], b"glTF")
            self.assertTrue((site / ".nojekyll").exists())
            self.assertFalse((site / "attachments").exists())
            self.assertFalse(list(site.rglob("*.blend")))

    def test_reject_unresolved_lfs_missing_and_invalid_models(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.glb"
            with self.assertRaisesRegex(ValueError, "Missing runtime file"):
                pages.validate_file(path)
            path.write_bytes(pages.LFS_HEADER + b"\noid sha256:example\nsize 123\n")
            with self.assertRaisesRegex(ValueError, "Unresolved Git LFS pointer"):
                pages.validate_file(path)
            path.write_bytes(b"not a model")
            with self.assertRaisesRegex(ValueError, "Invalid GLB"):
                pages.validate_file(path)


if __name__ == "__main__":
    unittest.main()
