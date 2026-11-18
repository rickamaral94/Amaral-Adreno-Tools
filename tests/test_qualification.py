import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from promotion_gate import validate_promotion
from validate_elf import validate


def qualification():
    return {'version':'5.7.8.1','mesa_commit':'a'*40,'patchset_sha256':'b'*64,
            'artifacts':{v:{'zip_sha256':'c'*64,'elf_sha256':'d'*64} for v in ('standard','oneui')},
            **{v:{'status':'pass','evidence':['https://example.invalid/test-fixture']} for v in ('ci','reproducibility','cts','vvl','regressions')},
            'hardware':{'status':'pass','evidence':['fixture'], 'families':['A6xx','A7xx','A8xx']},
            'reviewer':'test fixture','reviewed_at':'2026-10-20',
            'ab':{'status':'pass','rounds':5,'thermal_gate':'fixture','evidence':['fixture']}}


class QualificationTests(unittest.TestCase):
    def run_gate(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'evidence/qualifications/5.7.8.1.json';p.parent.mkdir(parents=True)
            if data is not None:p.write_text(json.dumps(data))
            return validate_promotion(root, {'version':'5.7.8.1','patchset_sha256':'b'*64}, {'mesa':{'commit':'a'*40}})

    def test_missing_hardware_blocks_even_with_green_ci(self):
        data=qualification();data['hardware']['status']='not-run'
        with self.assertRaises(RuntimeError):self.run_gate(data)

    def test_different_mesa_invalidates_qualification(self):
        data=qualification();data['mesa_commit']='e'*40
        with self.assertRaises(RuntimeError):self.run_gate(data)

    def test_a740_only_does_not_qualify_universal_release(self):
        data=qualification();data['hardware']['families']=['A7xx']
        with self.assertRaises(RuntimeError):self.run_gate(data)

    def test_missing_qualification_fails_closed(self):
        with self.assertRaises(RuntimeError):self.run_gate(None)

    def test_complete_record_passes_structural_gate(self):
        self.run_gate(qualification())

    def test_thermal_gate_required(self):
        data=qualification();del data['ab']['thermal_gate']
        with self.assertRaises(RuntimeError):self.run_gate(data)


    def owner_exception(self, waived):
        data=qualification()
        for key in waived:
            if key=='hardware_families':data['hardware']['families']=['A7xx','A8xx']
            else:data[key]={'status':'not-run'}
        data['owner_exception']={'approved_by':'owner','approved_at':'2026-10-31','rationale':'fixture','waived':waived}
        return data

    def test_owner_exception_waives_listed_gates(self):
        self.run_gate(self.owner_exception(['cts','vvl','regressions','ab','hardware_families']))

    def test_owner_exception_cannot_waive_hardware(self):
        data=self.owner_exception(['cts']);data['owner_exception']['waived']=['cts','hardware'];data['hardware']['status']='not-run'
        with self.assertRaises(RuntimeError):self.run_gate(data)

    def test_waived_gate_cannot_claim_pass(self):
        data=self.owner_exception(['cts']);data['cts']={'status':'pass','evidence':['fixture']}
        with self.assertRaises(RuntimeError):self.run_gate(data)

    def test_owner_exception_requires_approver(self):
        data=self.owner_exception(['cts']);del data['owner_exception']['approved_by']
        with self.assertRaises(RuntimeError):self.run_gate(data)

    def test_unlisted_gate_is_still_enforced(self):
        data=self.owner_exception(['cts']);data['vvl']={'status':'not-run'}
        with self.assertRaises(RuntimeError):self.run_gate(data)


class ElfTests(unittest.TestCase):
    symbols='1: 0 8 OBJECT GLOBAL DEFAULT 12 HMI'
    def test_host_dependency_rejected(self):
        with self.assertRaises(ValueError):validate('(NEEDED) Shared library: [libstdc++.so.6]',self.symbols)
    def test_android_dependencies_and_icd_entrypoints(self):
        self.assertEqual(validate('(NEEDED) Shared library: [libc.so]\n(NEEDED) Shared library: [libhardware.so]',self.symbols),['libc.so','libhardware.so'])
    def test_undefined_symbol_is_not_an_export(self):
        with self.assertRaises(ValueError):validate('(NEEDED) Shared library: [libc.so]',self.symbols.replace('DEFAULT 12','DEFAULT UND'))
