import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))

import publish_release


class PublicationTests(unittest.TestCase):
    def test_resume_only_uploads_missing_identical_assets(self):
        expected = {"standard.zip": "sha256:aaa", "oneui.zip": "sha256:bbb"}
        existing = [{"name": "standard.zip", "digest": "sha256:aaa"}]
        self.assertEqual(publish_release.missing_assets(existing, expected), ["oneui.zip"])

    def test_resume_refuses_to_replace_different_asset(self):
        with self.assertRaisesRegex(RuntimeError, "differs from tested build"):
            publish_release.missing_assets(
                [{"name": "standard.zip", "digest": "sha256:other"}],
                {"standard.zip": "sha256:aaa"},
            )

    def test_annotated_tag_resolves_to_source_commit(self):
        def fake_gh(*args, **_kwargs):
            if args[-1].endswith("refs/tags/v1"):
                return {"object": {"type": "tag", "sha": "tag-object"}}
            return {"object": {"type": "commit", "sha": "source-commit"}}

        with patch.object(publish_release, "gh", side_effect=fake_gh):
            self.assertEqual(publish_release.tag_commit("owner/repo", "v1"), "source-commit")


if __name__ == "__main__":
    unittest.main()
