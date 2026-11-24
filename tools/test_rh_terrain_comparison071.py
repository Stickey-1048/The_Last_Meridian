"""Focused symmetric selection provenance and actual binary terrain regressions."""
import importlib.util,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import composed_test_contexts as contexts,rh_terrain_comparison as comparison
class Comparison071(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.common,cls.current,cls.selected=comparison.select(ROOT,contexts.archive)
 def test_guidance_quests_aliases_and_all_unrelated_source_literal(self):
  accepted=contexts.archive(contexts.GUIDANCE)
  self.assertEqual(self.common,accepted)
  changed={n for n in set(self.common)|set(self.current) if self.common.get(n)!=self.current.get(n)}
  self.assertEqual(changed,{'tools/PluginBuilder/'+n for n in comparison.FILES}|{'tools/PluginBuilder/formkeys.txt'})
  for n in ('Spec.cs','SpecRedHollow.cs'):
   self.assertEqual(self.current['tools/PluginBuilder/'+n],accepted['tools/PluginBuilder/'+n])
  self.assertNotIn(b'BlackLedger',self.current['tools/PluginBuilder/Spec.cs'])
  self.assertNotIn(b'Blackstone',self.current['tools/PluginBuilder/Spec.cs'])
 def test_current_terrain_mutation_is_not_hidden_by_historical_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path=root/'tools/PluginBuilder/RedHollowTerrain.cs';path.parent.mkdir(parents=True)
   text=(ROOT/'tools/PluginBuilder/RedHollowTerrain.cs').read_text();self.assertIn('if(y<=16)return 0;',text)
   path.write_text(text.replace('if(y<=16)return 0;','if(y<=16)return 8;'))
   with self.assertRaisesRegex(AssertionError,'current RH terrain differs'):comparison.select(root,contexts.archive)
 def test_access_exclusion_is_exact_and_cannot_hide_other_current_change(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for n in comparison.FILES:
    p=root/'tools/PluginBuilder'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'tools/PluginBuilder'/n).read_bytes())
   p=root/'tools/PluginBuilder/RedHollowEnvironment.cs';p.write_text(p.read_text().replace('BuildRedHollowAccess();','BuildOtherLocation();'))
   with self.assertRaisesRegex(AssertionError,'access-only exclusion'):comparison.select(root,contexts.archive)
 def test_selected_current_formkey_mutation_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for n in comparison.FILES+('formkeys.txt',):
    p=root/'tools/PluginBuilder'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'tools/PluginBuilder'/n).read_bytes())
   p=root/'tools/PluginBuilder/formkeys.txt';text=p.read_text();self.assertIn('TLM_REF_RHE_T2_BedA',text);p.write_text(text.replace('TLM_REF_RHE_T2_BedA','TLM_REF_RHE_T2_Unauthorized'))
   with self.assertRaisesRegex(AssertionError,'allocation prefix/tail'):comparison.select(root,contexts.archive)
if __name__=='__main__':unittest.main()
