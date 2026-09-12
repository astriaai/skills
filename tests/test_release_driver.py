import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "release-driver.py"
SPEC = importlib.util.spec_from_file_location("release_driver", SCRIPT)
release_driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_driver)


class ReleaseDriverTest(unittest.TestCase):
    def test_release_scope_accepts_metadata_and_generated_plugin(self):
        release_driver.require_release_scope(
            [
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                "plugins/astria/.codex-plugin/plugin.json",
                "plugins/astria/skills/example/SKILL.md",
            ]
        )

    def test_release_scope_rejects_unrelated_changes(self):
        with self.assertRaisesRegex(release_driver.ReleaseError, "unexpected files"):
            release_driver.require_release_scope(["README.md", "plugins/astria/plugin.json"])

    def test_find_tag_run_ignores_main_branch_run_for_same_commit(self):
        runs = [
            {"databaseId": 1, "headBranch": "main"},
            {"databaseId": 2, "headBranch": "v2.0.0"},
        ]

        self.assertEqual(release_driver.find_tag_run(runs, "v2.0.0")["databaseId"], 2)

    def test_require_newer_version_rejects_same_or_older_core(self):
        original_root = release_driver.ROOT
        with tempfile.TemporaryDirectory() as directory:
            release_driver.ROOT = Path(directory)
            manifest = release_driver.ROOT / "plugins" / "astria" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"version": "1.5.1"}), encoding="utf-8")
            with self.assertRaisesRegex(release_driver.ReleaseError, "must be newer"):
                release_driver.require_newer_version("1.5.1")
            with self.assertRaisesRegex(release_driver.ReleaseError, "must be newer"):
                release_driver.require_newer_version("1.4.9")
            release_driver.require_newer_version("1.5.2")
        release_driver.ROOT = original_root

    def test_checksum_digest_reads_standard_sha256_file(self):
        with tempfile.TemporaryDirectory() as directory:
            checksum = Path(directory) / "plugin.zip.sha256"
            checksum.write_text(f"{'a' * 64}  plugin.zip\n", encoding="utf-8")

            self.assertEqual(release_driver.checksum_digest(checksum), "a" * 64)

    def test_checksum_digest_rejects_invalid_content(self):
        with tempfile.TemporaryDirectory() as directory:
            checksum = Path(directory) / "plugin.zip.sha256"
            checksum.write_text("not-a-checksum\n", encoding="utf-8")

            with self.assertRaisesRegex(release_driver.ReleaseError, "invalid checksum"):
                release_driver.checksum_digest(checksum)


if __name__ == "__main__":
    unittest.main()
