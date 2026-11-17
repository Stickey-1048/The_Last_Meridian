"""Execute accepted historical safety/mutation cases on their actual Git export.
The current candidate has additional independent confirmation guards. Preserve
the original probes unchanged as well as the current adapted source checks.
"""
import subprocess
import sys
import unittest
from source_snapshot import snapshot, built_red_hollow, RED_HOLLOW


class HistoricalGreenwater(unittest.TestCase):
    def test_all_accepted_greenwater_repair_and_mutation_cases(self):
        built_red_hollow()
        got=subprocess.run([sys.executable,'-B','-m','unittest','test_greenwater_repair'],
                           cwd=snapshot(RED_HOLLOW)/'tools/papyrus_sim',capture_output=True,text=True)
        self.assertEqual(got.returncode,0,got.stdout+got.stderr)
        self.assertIn('Ran 63 tests',got.stderr)
        self.assertIn('OK',got.stderr)
