"""Independent resolution oracle falsification, including primary 51/52/53/56 and adapters57/58."""
import unittest
from dataclasses import replace
from red_hollow_model import Observed

class RedHollowOracle(unittest.TestCase):
    def base(self):return Observed(0,0,0,0,0,False,False,False,False,False,0,False,False,False,False)
    def test_primary_and_adapter_outcomes(self):
        b=self.base()
        rows=[replace(b,mine=51,safe=11,eleven_ever_safe=True,pact=True,known_fates=True),replace(b,mine=52,safe=11,eleven_ever_safe=True,break_closed=True,known_fates=True),replace(b,mine=53,entombed=11,mouth_closed=True,ordered=True),replace(b,mine=56,entombed=11,mouth_closed=True),replace(b,mine=57,safe=11,eleven_ever_safe=True,known_fates=True),replace(b,mine=58,safe=10,deaths=1,known_fates=True),replace(b,mine=58,deaths=11,known_fates=True)]
        for row in rows:self.assertEqual(row.problems(),[])
        for row in rows:
            self.assertTrue(replace(row,pending=2).problems())
    def test_no_menu_choice_or_missing_reference_is_a_physical_result(self):
        b=self.base()
        for value in (51,52,53,56,57,58):self.assertTrue(replace(b,mine=value).problems())
        self.assertTrue(replace(b,court=12).problems());self.assertTrue(replace(b,court=14).problems())
        self.assertTrue(replace(b,mine=58,deaths=1,safe=9,known_fates=False).problems())
        self.assertTrue(replace(b,mine=56,mouth_closed=True,ordered=True).problems())
