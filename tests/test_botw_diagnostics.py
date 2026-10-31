import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('botw', Path(__file__).resolve().parents[1] / 'tools/analyze_botw_diagnostics.py')
botw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(botw)
REPORT = '''===== performance diagnosis: 60 s, 3000 presents (2900 in gameplay, 100 in menus or events)
run: driver turnip_amaral_v5.7.13.1 (Mesa) | LRZ on | internal resolution 1x | frame generation 2x | frame rate 60
summary: 25.00 real frames a second | screen p50 16.7 p95 33.4 p99 41.8 ms | GPU 15.00 ms per real frame
thread render (host thread, tid 12345): run 40%
  its own CPU clock: 30.0% of 60.0 s busy (6.00 ms/frame)
GPU timestamps read in the window: 100 counted, 50 inside an earlier one's span
'''


class Diagnostics(unittest.TestCase):
    def test_cpu_denominator_and_no_private_identifiers(self):
        row = botw.parse(REPORT)[0]
        self.assertEqual(row['render_cpu_ms_per_present_reported'], 6)
        self.assertEqual(row['render_cpu_ms_per_real_frame_approx'], 12)
        self.assertNotIn('12345', str(row))

    def test_embedded_and_standalone_match(self):
        embedded = '\n'.join('12:34:56 [diag] ' + line for line in REPORT.splitlines())
        self.assertEqual(botw.parse(REPORT), botw.parse(embedded))

    def test_repeated_exports_are_not_independent_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'input.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('a.txt', REPORT)
                z.writestr('b.txt', REPORT)
                z.writestr('../must-not-extract.txt', 'private data')
            result = botw.analyze(archive)
            self.assertEqual(result['exact_duplicate_text_members'], 1)
            self.assertEqual(result['distinct_summary_groups'], 1)
            self.assertEqual(result['reports'][0]['occurrences'], 2)
            self.assertFalse((Path(tmp).parent / 'must-not-extract.txt').exists())
            self.assertNotIn('private data', str(result))

    def test_missing_measurement_is_absent_not_zero(self):
        text = REPORT.split('thread render')[0]
        self.assertNotIn('render_cpu_ms_per_real_frame_approx', botw.parse(text)[0])
        self.assertEqual(botw.parse('incomplete capture without summary'), [])


if __name__ == '__main__':
    unittest.main()
