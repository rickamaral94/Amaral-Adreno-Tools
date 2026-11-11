import pathlib
import tempfile
import unittest

from tools.collect_a22_android_probe import parse_intish, parse_memtotal_kib, sha256_file


class A22AndroidProbeTests(unittest.TestCase):
    def test_parse_memtotal(self):
        self.assertEqual(parse_memtotal_kib("MemTotal:        8123456 kB\nMemFree: 10 kB\n"), 8123456)
        self.assertIsNone(parse_memtotal_kib("MemFree: 10 kB\n"))

    def test_parse_intish_hex_and_decimal(self):
        self.assertEqual(parse_intish("0xffff43030b00")["hex"], "0xffff43030b00")
        self.assertEqual(parse_intish("1124076299")["decimal"], 1124076299)
        self.assertIsNone(parse_intish("Adreno A22"))

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "sample.bin"
            path.write_bytes(b"a22")
            self.assertEqual(
                sha256_file(path),
                "e40d55bc974cf2a089b5c8e563249ea35ab126b5f42fdd269bd1f625870c15b6",
            )


if __name__ == "__main__":
    unittest.main()
