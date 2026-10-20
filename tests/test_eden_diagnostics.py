import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location(
    "eden_diagnostics", Path(__file__).parents[1] / "tools/summarize_eden_diagnostics.py")
eden = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eden)


class DiagnosticTests(unittest.TestCase):
    def test_tampered_payload_is_rejected_before_metrics(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "capture.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("report.json", "{}")
                archive.writestr("manifest.json", json.dumps({"files": [
                    {"name": "report.json", "bytes": 2, "sha256": "0" * 64}]}))
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                eden.summarize(path)

    def test_unlisted_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "capture.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("report.json", "{}")
                archive.writestr("manifest.json", '{"files":[]}')
            with self.assertRaisesRegex(ValueError, "cover exactly"):
                eden.summarize(path)

    def test_same_binary_cannot_measure_driver_speedup(self):
        capture = dict(emulator_commit="abc", settings_sha256="def", force_max_clock="false",
                       schema=2, driver_elf_sha256=["a" * 64], system={})
        result = eden.compare(capture, capture)
        self.assertFalse(result["driver_ab_qualified"])
        self.assertIn("same_driver_binary", result["reasons"])

    def test_missing_identity_is_not_equal_driver_evidence(self):
        capture = dict(emulator_commit="abc", settings_sha256="def", force_max_clock="false",
                       schema=1, driver_elf_sha256=[], system={})
        result = eden.compare(capture, capture)
        self.assertIn("missing_loaded_driver_hash", result["reasons"])
        self.assertNotIn("same_driver_binary", result["reasons"])
