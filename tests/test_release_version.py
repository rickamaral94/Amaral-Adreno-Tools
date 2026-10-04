import copy
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))

import release_version


BASE_STATE = {
    "mesa": {"generation": 4, "normalized_version": "26.3.0"},
    "vulkan": {"generation": 5, "version": "1.4.359"},
    "amaral_revision": 1,
    "upstream_revision": 1,
}


class VersionTests(unittest.TestCase):
    def test_promotion_records_candidate_mesa_as_released(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "config").mkdir()
            notes = root / "docs/releases/mesa-26.3.0-devel-v4.7.4.1.md"
            notes.parent.mkdir(parents=True)
            notes.write_text("**Pré-release para A/B.**")
            state = {"candidate": {"version": "4.7.4.1", "patchset_sha256": "b" * 64},
                     "stable_version": "4.7.3.7", "last_released_mesa_commit": "a" * 40}
            (root / "config/version-state.json").write_text(json.dumps(state))
            (root / "config/mesa-lock.json").write_text(json.dumps({
                "mesa": {"version": "26.3.0-devel", "commit": "c" * 40}}))
            with (patch.object(release_version, "ROOT", root),
                  patch.object(release_version, "LOCK_PATH", root / "config/mesa-lock.json"),
                  patch.object(release_version, "STATE_PATH", root / "config/version-state.json"),
                  patch.object(release_version, "patchset_fingerprint", return_value="b" * 64)):
                release_version.promote_candidate(SimpleNamespace(github_output=None, write=True))
            promoted = json.loads((root / "config/version-state.json").read_text())
            self.assertEqual(promoted["last_released_mesa_commit"], "c" * 40)

    def test_mesa_devel_suffix_does_not_change_numeric_version(self):
        self.assertEqual(
            release_version.normalize_mesa_version("26.3.0-devel"), "26.3.0"
        )

    def test_vulkan_header_uses_complete_version(self):
        header = """\
#define VK_HEADER_VERSION 360
#define VK_HEADER_VERSION_COMPLETE VK_MAKE_API_VERSION(0, 1, 4, VK_HEADER_VERSION)
"""
        self.assertEqual(release_version.parse_vulkan_header(header), "1.4.360")

    def test_upstream_snapshot_only_increments_last_component(self):
        state = copy.deepcopy(BASE_STATE)
        version = release_version.advance_upstream_version(
            state,
            {"normalized_version": "26.3.0", "vulkan_version": "1.4.359"},
        )
        self.assertEqual(version, "4.5.1.2")

    def test_mesa_and_vulkan_changes_increment_their_generations(self):
        state = copy.deepcopy(BASE_STATE)
        version = release_version.advance_upstream_version(
            state,
            {"normalized_version": "26.3.1", "vulkan_version": "1.4.360"},
        )
        self.assertEqual(version, "5.6.1.1")

    def test_resume_uses_recorded_version_without_advancing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "config").mkdir()
            (root / "docs/releases").mkdir(parents=True)
            state = copy.deepcopy(BASE_STATE)
            state.update({"current_version": "4.5.1.1", "stable_version": "4.5.1.1",
                          "last_released_mesa_commit": "a" * 40,
                          "stable_patchset_sha256": "b" * 64, "candidate": None})
            lock = {"amaral_revision": "4.5.1.1",
                    "mesa": {"version": "26.3.0-devel", "commit": "a" * 40}}
            (root / "config/version-state.json").write_text(json.dumps(state))
            (root / "config/mesa-lock.json").write_text(json.dumps(lock))
            note = root / "docs/releases/mesa-26.3.0-devel-v4.5.1.1.md"
            note.write_text("tested release\n")
            output = root / "output"
            with (patch.object(release_version, "ROOT", root),
                  patch.object(release_version, "LOCK_PATH", root / "config/mesa-lock.json"),
                  patch.object(release_version, "STATE_PATH", root / "config/version-state.json"),
                  patch.object(release_version, "patchset_fingerprint", return_value="b" * 64)):
                release_version.resume_release(
                    SimpleNamespace(channel="upstream", github_output=output))
            self.assertIn("release_tag=mesa-26.3.0-devel-v4.5.1.1", output.read_text())
            self.assertEqual(json.loads((root / "config/version-state.json").read_text()), state)


if __name__ == "__main__":
    unittest.main()
