"""Current successor provenance and mutation checks; old guards remain frozen."""
import json,shutil,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import rh_return_account_candidate as c
class ReturnAccountCandidate(unittest.TestCase):
    def copy(self,root):
        m=json.loads(c.MANIFEST.read_text(encoding='utf-8'))
        for n in c.expected_names(m['baselineFiles']):
            p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c.ROOT/n,p)
    def repin(self,root):
        p=root/c.NAME;m=json.loads(p.read_text(encoding='utf-8'));m.update(c.describe(root));p.write_text(json.dumps(m),encoding='utf-8')
    def test_current_successor_nominal_and_runtime_selection(self):
        self.assertEqual(c.problems(),[])
        m=json.loads(c.MANIFEST.read_text(encoding='utf-8'));self.assertEqual(len(m['sourceTextSha256']),34)
        self.assertEqual((len(m['runtimeSelection']['reusedReviewedPex']),len(m['runtimeSelection']['freshlyCompiled'])),(16,18))
    def test_repin_cannot_waive_runtime_old_guard_workflow_or_approved_message_mutations(self):
        for name in ('scripts/Source/User/TLM/MQ03Quest.psc','scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/SpecRedHollow.cs','tools/player_guidance_terrain_candidate.py','tools/win/player-guidance-terrain-candidate.json','.github/workflows/portable-checks.yml'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);self.copy(root);p=root/name;p.write_text(p.read_text(encoding='utf-8-sig')+'\n# unapproved\n',encoding='utf-8')
                # A broken old JSON manifest cannot be a new nominal candidate either.
                try:self.repin(root)
                except ValueError:pass
                self.assertTrue(c.problems(root))
    def test_added_workflow_and_allocation_shift_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.copy(root);(root/'.github/workflows/extra.yml').write_text('name: unexpected\n',encoding='utf-8');self.repin(root)
            self.assertIn('Exact return/account source membership changed',c.problems(root))
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.copy(root);p=root/'tools/PluginBuilder/formkeys.txt';p.write_text(p.read_text(encoding='utf-8').replace('3632\n','9999\n'),encoding='utf-8');self.repin(root)
            self.assertIn('Exact32append-only Message allocations changed',c.problems(root))
    def test_only_four_exact_old_provenance_methods_move_to_real13c_context(self):
        import run_composed_tests as d
        from composed_test_contexts import AFTERMATH_BASE,CONTEXT_DIGESTS
        moved={n for n,r in d.EXACT.items() if r==AFTERMATH_BASE}
        self.assertEqual(len(moved),4);self.assertTrue(all(n.startswith('test_composed_source.CurrentComposition.') for n in moved))
        self.assertEqual(CONTEXT_DIGESTS[AFTERMATH_BASE],c.BASELINE_DIGEST)
        for n in ('test_rh_return_account.ReturnAccount.test_all_eleven_actual_originals_and_single_optional_sentence','test_composed_source.CurrentComposition.test_current_clone_keeps_original101_aliases_and_appends_only_scriptfilled_report_target'):
            self.assertNotIn(n,d.EXACT);self.assertNotIn(n.split('.')[0],d.WHOLE)
if __name__=='__main__':unittest.main()
