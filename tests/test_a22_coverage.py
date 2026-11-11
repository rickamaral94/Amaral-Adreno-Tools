import pathlib
import tempfile
import unittest

from tools.check_a22_coverage import (
    classify_chip,
    dev_id_compare,
    validate_catalog,
    validate_source,
)


class A22CoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.devices = self.root / "src/freedreno/common/freedreno_devices.py"
        self.devices.parent.mkdir(parents=True)

    def write_source(self, fd735="0xffff43030B00"):
        self.devices.write_text(
            'add_gpus([\n'
            f' GPUId(chip_id={fd735}, name="FD735"),\n'
            ' GPUId(chip_id=0xffff43030E01, name="Adreno (TM) 735"),\n'
            '], info)\n',
            encoding="utf-8",
        )

    def test_known_source_entries_are_required(self):
        self.write_source()
        self.assertEqual(validate_source(self.root), self.devices)

    def test_legacy_non_wildcard_fd735_is_rejected(self):
        self.write_source("0x43030B00")
        with self.assertRaises(ValueError):
            validate_source(self.root)

    def test_fd735_matches_with_or_without_fuse_bits(self):
        ref = 0xFFFF43030B00
        self.assertTrue(dev_id_compare(ref, 0x43030B00))
        self.assertTrue(dev_id_compare(ref, 0x123443030B00))
        self.assertTrue(dev_id_compare(ref, 0xFFFF43030B00))
        self.assertFalse(dev_id_compare(ref, 0x123443030C00))

    def test_second_735_entry_also_ignores_fuse_bits(self):
        result = classify_chip("0x55aa43030e01")
        self.assertTrue(result["matched"])
        self.assertEqual(result["profiles"], ["Adreno (TM) 735"])

    def test_catalog_gate_checks_generated_records(self):
        catalog = self.root / "GPU_CATALOG_standard.h"
        catalog.write_text(
            'static const struct fd_dev_rec fd_dev_recs[] = {\n'
            '  { {0, 0xffff43030b00}, "FD735", &__info0 },\n'
            '  { {0, 0xffff43030e01}, "Adreno (TM) 735", &__info0 },\n'
            '};\n',
            encoding="utf-8",
        )
        self.assertEqual(validate_catalog(catalog), catalog)


if __name__ == "__main__":
    unittest.main()
