import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))

import release_version


BASE_STATE = {
    "mesa": {"generation": 4, "normalized_version": "26.3.0"},
    "vulkan": {"generation": 5, "version": "1.4.359"},
    "amaral_revision": 1,
    "upstream_revision": 1,
}


class VersionTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
