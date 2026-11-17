"""Behavioral probes must reject damaged actual PSC, not just match its text."""
import unittest
from sim import SimError
from test_act1 import changed_scripts
from test_four_flags import Fair,R


class FourFlagsMutations(unittest.TestCase):
    def caught(self,file,old,new,probe):
        scripts=changed_scripts(file,old,new)
        try:probe(scripts)
        except (AssertionError,SimError):return
        self.fail('actual behavior accepted the damaged source: '+old)

    def test_original_reference_effect_and_receipt_mutations_are_detected(self):
        def take(scripts):
            a=Fair(self,scripts=scripts);a.scene(3,Occupation=0,OccupationSeen=0,Take=0)
            self.assertEqual(a.v('response'),44)
            self.assertIs(a.s.placed[R+'OriginalCase'].container,a.s.player)
        self.caught('MQ03Quest.psc','\trecipient.AddItem(original,1,true)\n','',take)

        def occupation(scripts):
            a=Fair(self,scripts=scripts);a.scene(0,Occupation=0,OccupationSeen=0)
            self.assertIn(70,a.q.done)
        self.caught('MQ03Quest.psc','\tSetStage(70)\n','',occupation)

        def concession(scripts):
            a=Fair(self,scripts=scripts);a.scene(2)
            self.assertEqual(a.v('response'),43);self.assertTrue(a.v('crowdSpared'))
        self.caught('MQ03Quest.psc','\tcrowdSpared = true\n','\tcrowdSpared = false\n',concession)

        def heard(scripts):
            a=Fair(self,scripts=scripts);a.scene(1,Occupation=0,OccupationSeen=0)
            self.assertTrue(a.v('courierHeard'))
        self.caught('MQ03Quest.psc','\tcourierHeard = true\n','\tcourierHeard = false\n',heard)

        def dead_scene(scripts):
            a=Fair(self,scripts=scripts);a.s.placed[R+'Juno'].dead=True
            shown=a.scene(0,DeadCourier=0,Occupation=0,OccupationSeen=0)
            self.assertIn(45,a.q.done);self.assertNotIn(46,a.q.done);self.assertNotIn('Shot',shown)
        self.caught('MQ03Quest.psc','\t\tSetStage(45)\n','\t\tSetStage(46)\n',dead_scene)

        def read(scripts):
            a=Fair(self,scripts=scripts);a.scene(0,Occupation=0,OccupationSeen=0);a.read()
            self.assertIn(100,a.q.done);self.assertNotIn(101,a.q.done)
        self.caught('MQ03Quest.psc','\tSetStage(100)\n','',read)

        def load(scripts):
            a=Fair(self,scripts=scripts);a.hook('Shot',a.load_inside_native)
            a.scene(0,Occupation=0,OccupationSeen=0)
            self.assertNotIn(40,a.q.done)
        self.caught('MQ03Quest.psc','\tgeneration += 1\n','\tgeneration += 0\n',load)

