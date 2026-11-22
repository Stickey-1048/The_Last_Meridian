from pathlib import Path
import sys,unittest
import verify_footer as v
sys.path.insert(0,str(v.REPO/'tools/papyrus_sim'))
class Footer(unittest.TestCase):
 def test_actual_footer_and_all_other_records_scripts_unchanged(self):self.assertEqual('PASS',v.run()['status'])
 def test_speech_change_and_other_record_change_are_rejected(self):
  raw=(v.ROOT/'build/master-001/TheLastMeridian.esp').read_bytes();old=(v.BUNDLE/'TheLastMeridian.esp').read_bytes()
  for before,after in[(b'Which road do you want to ask about?',b'Which road do you want to ask abouX?'),(b'TLM_MSG_MB_Rail\0',b'TLM_MSG_MB_RaiX\0')]:
   self.assertEqual(1,raw.count(before))
   with self.assertRaises(AssertionError):v.artifact(raw.replace(before,after),old)
def load_tests(loader,tests,pattern):
 import test_mercy_briefing as original
 tests.addTests(loader.loadTestsFromNames(['TheMenu.test_not_now','TheMenu.test_the_three_briefs_each_by_its_own_button','TheTask.test_it_completes_only_after_a_brief_was_shown','TheTask.test_it_stays_complete_and_goes_on_answering'],original));return tests
if __name__=='__main__':unittest.main(verbosity=2)
