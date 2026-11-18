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
    def test_apply_evidence_does_not_claim_reference_patch_was_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "config").mkdir()
            (root / "evidence").mkdir()
            (root / "config/patches.json").write_text(json.dumps({
                "standard": ["patches/active.patch"], "oneui_extra": [],
                "research_only": ["patches/reference.patch"],
            }))
            evidence = {"candidates": [
                {"patch": "patches/active.patch", "patch_apply_verified_on_mesa": "a" * 40},
                {"patch": "patches/reference.patch", "patch_apply_verified_on_mesa": "a" * 40},
            ]}
            path = root / "evidence/candidates.json"
            path.write_text(json.dumps(evidence))
            with (patch.object(release_version, "ROOT", root),
                  patch.object(release_version, "EVIDENCE_PATH", path)):
                release_version.update_patch_apply_evidence("b" * 40)
            updated = json.loads(path.read_text())["candidates"]
            self.assertEqual(updated[0]["patch_apply_verified_on_mesa"], "b" * 40)
            self.assertEqual(updated[1]["patch_apply_verified_on_mesa"], "a" * 40)

    def test_candidate_resume_accepts_new_mesa_without_changing_stable_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "config").mkdir()
            note = root / "docs/releases/mesa-26.3.0-devel-v4.5.1.1.md"
            note.parent.mkdir(parents=True)
            note.write_text("prepared candidate\n")
            state = copy.deepcopy(BASE_STATE)
            state.update({"current_version": "4.5.1.1", "stable_version": "4.5.0.1",
                          "last_released_mesa_commit": "a" * 40,
                          "stable_patchset_sha256": "c" * 64,
                          "candidate": {"version": "4.5.1.1", "patchset_sha256": "b" * 64}})
            lock = {"amaral_revision": "4.5.1.1",
                    "mesa": {"version": "26.3.0-devel", "commit": "d" * 40}}
            state_path = root / "config/version-state.json"
            lock_path = root / "config/mesa-lock.json"
            state_path.write_text(json.dumps(state))
            lock_path.write_text(json.dumps(lock))
            output = root / "output"
            with (patch.object(release_version, "ROOT", root),
                  patch.object(release_version, "LOCK_PATH", lock_path),
                  patch.object(release_version, "STATE_PATH", state_path),
                  patch.object(release_version, "patchset_fingerprint", return_value="b" * 64)):
                release_version.resume_release(SimpleNamespace(channel="candidate", github_output=output))
            self.assertIn("resume_available=true", output.read_text())
            self.assertIn("mesa_commit=" + "d" * 40, output.read_text())
            self.assertEqual(json.loads(state_path.read_text()), state)

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
                  patch.object(release_version, "patchset_fingerprint", return_value="b" * 64),
                  patch("promotion_gate.validate_promotion", return_value={})):
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

class CandidateIdentityTests(unittest.TestCase):
    def test_upstream_only_change_creates_candidate_and_preserves_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);(root/'config').mkdir()
            state=copy.deepcopy(BASE_STATE)
            state.update(current_version='4.5.1.1',stable_version='4.5.1.1',last_released_mesa_commit='a'*40,stable_patchset_sha256='b'*64,candidate=None)
            lock={'amaral_revision':'4.5.1.1','mesa':{'commit':'c'*40,'version':'26.3.0-devel'}}
            state_path=root/'config/version-state.json';lock_path=root/'config/mesa-lock.json'
            state_path.write_text(json.dumps(state));lock_path.write_text(json.dumps(lock))
            meta={'commit':'c'*40,'version':'26.3.0-devel','normalized_version':'26.3.0','vulkan_version':'1.4.359','commit_date_utc':'2026-10-20','title':'Correctness fix'}
            with (patch.object(release_version,'ROOT',root),patch.object(release_version,'STATE_PATH',state_path),
                  patch.object(release_version,'LOCK_PATH',lock_path),patch.object(release_version,'patchset_fingerprint',return_value='b'*64),
                  patch.object(release_version,'mesa_metadata',return_value=meta)):
                release_version.prepare_candidate(SimpleNamespace(mesa_src=root,github_output=None,write=True))
            new=json.loads(state_path.read_text())
            self.assertEqual(new['stable_version'],'4.5.1.1')
            self.assertEqual(new['last_released_mesa_commit'],'a'*40)
            self.assertEqual(new['candidate']['mesa_commit'],'c'*40)
            self.assertEqual(new['current_version'],'4.5.2.1')
