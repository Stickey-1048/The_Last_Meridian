"""Actual composed binary cloning and malformed-source refusal; no terrain or native claim."""
import json
import math
import unittest
from test_greenwater_world_clone import clone

class RedHollowClone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        got=clone()
        if got.returncode:raise AssertionError(got.stdout+got.stderr)
        cls.out=json.loads(got.stdout)
    def test_101_aliases_have_exact_mixed_ownership_and_no_new_condemned(self):
        q=self.out['redHollow'];self.assertEqual(q['script'],'TLM:RedHollowWalk')
        aliases=q['aliases'];self.assertEqual(len(aliases),101);self.assertEqual(len({a['id'] for a in aliases}),101)
        exterior={a['name']:a for a in aliases if a['owner']=='TLMWorldSlice.esp'}
        self.assertEqual(set(exterior),{'MercyTravel','MercyReturn'})
        self.assertEqual(sum(a['owner']=='TheLastMeridian.esp' for a in aliases),97)
        self.assertEqual(next(a for a in aliases if a['name']=='Condemned')['reference'],'script-filled')
        self.assertEqual(next(a for a in aliases if a['name']=='Player')['owner'],'Fallout4.esm')
        self.assertEqual(self.out['persistentReferences'],68)
        for a in exterior.values():self.assertEqual([a['x'],a['y'],a['z']],self.out['redHollowSites'][a['name']])
        self.assertEqual(self.out['firstSection']['forms']['TLM_RedHollow'],'TLM_WS_RH')
        self.assertEqual(q['forms']['TLM_MQ02C'],'TLM_MQ02C in TheLastMeridian.esp')
        self.assertNotIn('TLM_MQ02C',self.out['quests'])
    def test_sites_preserve_prior_routes_and_stay_clear_of_known_people(self):
        for name,(x,y,z) in self.out['redHollowSites'].items():
            self.assertTrue(3432<x<3560 and 2560<y<2672,name)
            for px,py in ((3260,2530),(2850,2530),(3380,2500),(3150,2620),(3150,2700),(2950,2640),(3000,2580)):
                self.assertGreaterEqual(math.hypot(x-px,y-py),128,name)
            self.assertGreater(z,0)
    def test_bad_bindings_allocations_and_prisoner_clone_are_refused(self):
        for damage in ('red-hollow-binding-removed','red-hollow-binding-to-another-quest','red-hollow-alias-dropped','red-hollow-placement-missing','red-hollow-road-missing','red-hollow-cell-missing','red-hollow-prisoner-forced'):
            with self.subTest(damage=damage):
                got=clone(damage);self.assertEqual(got.returncode,1,got.stdout+got.stderr);self.assertIn('REFUSED',got.stderr)
    def test_previous_night_mail_composition_still_clones(self):
        got=clone('source-without-red-hollow');self.assertEqual(got.returncode,0,got.stdout+got.stderr)
        out=json.loads(got.stdout);self.assertFalse(out['redHollow']['present']);self.assertTrue(out['nightMail']['present']);self.assertEqual(out['persistentReferences'],64)
