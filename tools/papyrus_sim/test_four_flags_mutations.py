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

    def test_late_pickup_probe_detects_the_historical_stale_holder_enable_program(self):
        from test_four_flags_late_custody import observe_late_pickup
        def guarded(scripts):
            a=Fair(self,scripts=scripts);a.use('Ready',Ready=0,Shot=1)
            original,fired,enabled=observe_late_pickup(a)
            self.assertEqual(len(fired),1);self.assertNotIn(True,enabled)
            self.assertEqual(enabled,[]);self.assertIs(original.container,a.s.player)
        safe='''\tcourier.Enable()
\tIf !Road().BeginEncounter(courier,original,player,capturedEpoch)
\t\tReturn
\tEndIf
\t; Finish yielding eligibility reads before sampling the effect boundary.
\t; An already-enabled paused original needs no Enable, held or otherwise.
\tbool needsEnable = original.IsDisabled()
\tObjectReference holder = original.GetContainer()
\tIf capturedEpoch != Road().Epoch()
\t\tReturn
\tEndIf
\tIf needsEnable && !holder
\t\toriginal.Enable()
\tEndIf
'''
        broken='''\tcourier.Enable()
\tObjectReference holder = original.GetContainer()
\tIf !Road().BeginEncounter(courier,original,player,capturedEpoch)
\t\tReturn
\tEndIf
\tIf !holder
\t\toriginal.Enable()
\tEndIf
'''
        self.caught('FourFlagsWalk.psc',safe,broken,guarded)

    def test_held_scene_recovery_and_changed_custody_regressions_detect_broken_source(self):
        from test_four_flags_recovery import pickup,retry
        def recovery(scripts):
            a=Fair(self,scripts=scripts);a.use('Ready',Ready=0,Shot=1)
            original=pickup(a);retry(a)
            self.assertIn(40,a.q.done);self.assertIs(original.container,a.s.player)
            self.assertNotIn(44,a.q.done)
        self.caught('MQ03Quest.psc','\t\tcustody = custody && holder == player\n','\t\tcustody = false\n',recovery)

        def changed_holder(scripts):
            a=Fair(self,scripts=scripts);a.use('Ready',Ready=0,Shot=1)
            original=pickup(a)
            a.hook('Shot',lambda:a.s.n_objectreference_additem(a.originals[0],None,original,1,True))
            retry(a);self.assertNotIn(40,a.q.done);self.assertIs(original.container,a.originals[0])
        self.caught('MQ03Quest.psc','\tcustody = custody && original.GetContainer() == holder\n','',changed_holder)

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

