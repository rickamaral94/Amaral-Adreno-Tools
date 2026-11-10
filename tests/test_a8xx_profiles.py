import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import check_a8xx_profiles as gate


def record(chip, values, generation=8):
    return dict(gpu_id=0, chip_id=chip, name=str(chip), info={
        'chip': generation, 'num_sp_cores': values[0],
        **dict(zip(gate.FIELDS, values)), 'props': {'inherited_property': True}})


def fixture():
    baseline = [record(chip | gate.FUSE_MASK, values)
                for chip, values in gate.EXPECTED.items()
                if chip not in (0x44010200, 0x44030000)]
    baseline.append(record(0x43050a01, (4, 0, 32, 32, 16384, 16384, 32768), 7))
    baseline[-1]['info']['props']['enable_tp_ubwc_flag_hint'] = False
    current = copy.deepcopy(baseline)
    alias = copy.deepcopy(current[0])
    alias.update(chip_id=0x44010200, name='A812')
    current.append(alias)
    a825 = record(0x44030000, gate.EXPECTED[0x44030000])
    a825['info']['props'].update({
        'gmem_ccu_color_cache_fraction': 1, 'gmem_per_ccu_color_cache_size': 131072,
        'gmem_ccu_depth_cache_fraction': 1, 'gmem_per_ccu_depth_cache_size': 131072,
        'sysmem_ccu_color_cache_fraction': 0, 'sysmem_per_ccu_color_cache_size': 131072,
        'sysmem_ccu_depth_cache_fraction': 3, 'sysmem_per_ccu_depth_cache_size': 98304,
        'gmem_vpc_attr_buf_size': 49152, 'gmem_vpc_pos_buf_size': 24576,
        'gmem_vpc_bv_pos_buf_size': 32768,
    })
    current.append(a825)
    return current, baseline


class ProfileGateTests(unittest.TestCase):
    def setUp(self):
        self.current, self.baseline = fixture()

    def check(self, variant='standard'):
        return gate.validate(self.current, self.baseline, variant)

    def test_reviewed_profiles_and_fuse_variants(self):
        self.assertEqual(len(self.check()), 8)
        self.assertEqual(gate.resolve(self.current, 0x123444050a21)['num_slices'], 2)
        self.assertEqual(gate.resolve(self.current, 0x44050a31)['num_slices'], 3)

    def test_wrong_topology_even_when_also_upstream(self):
        for rows in (self.current, self.baseline):
            gate.resolve(rows, 0x44050a21)['num_slices'] = 3
        with self.assertRaisesRegex(ValueError, 'num_slices'):
            self.check()

    def test_global_shared_memory_change_rejected(self):
        for row in self.current:
            row['info']['cs_shared_mem_size'] = 65536
        with self.assertRaisesRegex(ValueError, 'upstream profile'):
            self.check()

    def test_inherited_property_change_rejected(self):
        gate.resolve(self.current, 0x44050000)['props']['disable_gmem'] = True
        with self.assertRaisesRegex(ValueError, 'upstream profile'):
            self.check()

    def test_a825_unreviewed_capability_rejected(self):
        gate.resolve(self.current, 0x44030000)['props']['has_new_capability'] = True
        with self.assertRaisesRegex(ValueError, 'expanded A825'):
            self.check()

    def test_a812_must_remain_reviewed_alias(self):
        gate.resolve(self.current, 0x44010200)['props']['disable_gmem'] = True
        with self.assertRaisesRegex(ValueError, 'A812'):
            self.check()

    def test_duplicate_table_entry_rejected(self):
        self.current.append(copy.deepcopy(self.current[0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.check()

    def test_conflicting_raw_and_wildcard_rejected(self):
        extra = copy.deepcopy(self.current[0])
        extra['chip_id'] = 0x44010000
        extra['info']['num_slices'] = 2
        self.current.append(extra)
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            self.check()

    def test_unknown_chip_is_not_inferred(self):
        for chip in (0x44050a41, 0x44030001, 0x44041430, 0x44051431):
            with self.assertRaisesRegex(ValueError, 'Missing'):
                gate.resolve(self.current, chip)

    def test_oneui_is_only_reviewed_fd740_property(self):
        gate.resolve(self.current, 0x43050a01)['props']['enable_tp_ubwc_flag_hint'] = True
        self.check('oneui')
        with self.assertRaisesRegex(ValueError, 'upstream profile'):
            self.check('standard')
        gate.resolve(self.current, 0x44050a31)['props']['enable_tp_ubwc_flag_hint'] = True
        with self.assertRaisesRegex(ValueError, 'upstream profile'):
            self.check('oneui')

    def test_removed_upstream_profile_rejected(self):
        del self.current[0]
        with self.assertRaisesRegex(ValueError, 'Removed'):
            self.check()

    def test_new_chip_needs_review(self):
        self.current.append(record(0x44051431, gate.EXPECTED[0x44050a31]))
        with self.assertRaisesRegex(ValueError, 'extra GPU'):
            self.check()


if __name__ == '__main__':
    unittest.main()
