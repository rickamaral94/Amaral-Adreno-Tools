import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest


class ReproducibilityLogsTests(unittest.TestCase):
    def test_failed_build_keeps_output_and_exit_status(self):
        source = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copy(source / "scripts/check_reproducibility.sh", scripts)
            builder = scripts / "build_universal.sh"
            builder.write_text(
                '#!/usr/bin/env bash\n'
                'echo "GPU generator failed"\n'
                'echo "diagnostic on stderr" >&2\n'
                'exit 7\n'
            )
            builder.chmod(0o755)
            result = subprocess.run(
                ["bash", str(scripts / "check_reproducibility.sh")],
                env={**os.environ, "NDK_ROOT": str(root / "ndk"),
                     "DRIVER_VARIANT": "standard", "REPRO_ROOT": str(root / "repro")},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 7)
            self.assertIn("GPU generator failed", result.stdout)
            self.assertIn("diagnostic on stderr", result.stdout)
            log = root / "repro/standard/first/build.log"
            self.assertIn("GPU generator failed", log.read_text())
            self.assertIn("diagnostic on stderr", log.read_text())
            self.assertFalse((root / "repro/standard/second").exists())


if __name__ == "__main__":
    unittest.main()
