import pathlib
import tempfile
import unittest

from tools.check_mesa_policy import check


class MesaPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.config = self.root / "src/freedreno/vulkan/00-turnip-defaults.conf"
        self.config.parent.mkdir(parents=True)

    def test_reviewed_rule_is_removed_before_packaging(self):
        self.config.write_text('<application application_name_match="mgs4.exe">'
                               '<option name="force_vk_vendor" value="0x1002" />'
                               '</application>')
        check(self.root)
        with self.assertRaises(ValueError):
            check(self.root, patched=True)

    def test_new_rule_blocks_upstream(self):
        self.config.write_text('<option name="force_vk_vendor" value="0x1234" />')
        with self.assertRaises(ValueError):
            check(self.root)

    def test_clean_config_passes_final_gate(self):
        self.config.write_text('<driconf />')
        check(self.root, patched=True)


if __name__ == "__main__":
    unittest.main()
