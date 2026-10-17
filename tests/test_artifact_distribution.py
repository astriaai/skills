import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install-plugin-release.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class ArtifactDistributionTest(unittest.TestCase):
    def test_source_only_checkout_builds_all_artifacts_and_installable_marketplace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "dist", "plugins", ".cache", "__pycache__"))
            output = root / "dist"
            for target, prefix in (("openai", "astria"), ("claude", "astria-claude"),
                                   ("grok", "astria-grok"), ("marketplace", "astria-marketplace")):
                result = subprocess.run(["python3", str(root / "scripts/build-plugin.py"), "--target", target],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                version = json.loads((root / "packaging/openai/plugin.json").read_text())["version"]
                archive = output / f"{prefix}-{version}.zip"
                self.assertTrue(archive.is_file())
                self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                                 archive.with_suffix(".zip.sha256").read_text().split()[0])
            name = f"astria-marketplace-{version}.zip"
            payload = (output / name).read_bytes()
            checksum = (output / f"{name}.sha256").read_text()
            installed = Path(directory) / "installed"
            # Exercise the same verified download/extraction flow used by end users.
            with patch.object(installer, "download", side_effect=[payload, checksum.encode()]):
                installer.install(version, installed)
            for relative, key in ((".agents/plugins/marketplace.json", "codex"),
                                  (".claude-plugin/marketplace.json", "claude"),
                                  (".grok-plugin/marketplace.json", "grok"),
                                  (".cursor-plugin/marketplace.json", "cursor")):
                entry = json.loads((installed / relative).read_text())["plugins"][0]
                source = entry["source"]
                path = source["path"] if isinstance(source, dict) else source
                self.assertTrue((installed / path / "skills/astria-api/SKILL.md").is_file(), key)
            self.assertTrue((installed / "plugins/astria/bin/astria").stat().st_mode & 0o111)
            self.assertEqual(json.loads((installed / "plugins/astria/plugin.json").read_text())["name"], "astria")
            with zipfile.ZipFile(output / f"astria-{version}.zip") as bundle:
                self.assertEqual(json.loads(bundle.read("plugin.json"))["name"], "astria-mcp")
            (output / "marketplace/stale-payload").write_text("must not ship")
            result = subprocess.run(["python3", str(root / "scripts/build-plugin.py"), "--target", "marketplace"], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((output / name).read_bytes(), payload)
            self.assertFalse((root / "plugins").exists())
            self.assertFalse((root / ".agents/plugins/marketplace.json").exists())
            result = subprocess.run(["python3", str(root / "scripts/set-plugin-version.py"), "9.8.7"], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run(["python3", str(root / "scripts/build-plugin.py"), "--target", "marketplace"], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "astria-marketplace-9.8.7.zip").is_file())

    def test_rejects_corrupt_download_before_extracting(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "plugin"
            with self.assertRaisesRegex(ValueError, "checksum"):
                installer.extract_verified(b"corrupt", "0" * 64, destination)
            self.assertFalse(destination.exists())

    def test_rejects_archive_traversal_and_symlinks(self):
        for filename, mode in (("../outside", 0o100644), ("/outside", 0o100644), ("link", 0o120777)):
            payload = io.BytesIO()
            with zipfile.ZipFile(payload, "w") as archive:
                member = zipfile.ZipInfo(filename)
                member.external_attr = mode << 16
                archive.writestr(member, "outside")
            contents = payload.getvalue()
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(ValueError, "unsafe path|symlink"):
                    installer.extract_verified(contents, hashlib.sha256(contents).hexdigest(), Path(directory))

    def test_rejects_existing_install_without_downloading_or_changing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            (destination / "user-file").write_text("keep")
            with patch.object(installer, "download") as download:
                with self.assertRaisesRegex(ValueError, "already exists"):
                    installer.install("1.5.17", destination)
                download.assert_not_called()
            self.assertEqual((destination / "user-file").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
