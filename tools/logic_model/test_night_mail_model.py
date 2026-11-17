"""Independent contract examples for the Night Mail state model; not native proof."""
import itertools
import unittest
import night_mail_model as nm


def cut(**world):
    r=nm.Line(**world);r.travel()
    if r.lockridge:r.talk_lockridge(pick='ride')
    r.use_depart()
    return r


class NightMailContract(unittest.TestCase):
    def test_run_and_reverse_work_without_either_yard_actor(self):
        for lockridge,billie,route in itertools.product((False,True),(False,True),('run','back')):
            with self.subTest(lockridge=lockridge,billie=billie,route=route):
                r=cut(lockridge=lockridge,billie=billie);r.use_train(pick=route)
                self.assertEqual((r.outcome,r.mail),(nm.NM_RUN,nm.NM_MAIL_DELIVERED) if route=='run' else (nm.NM_BACKED,nm.NM_MAIL_RETAINED))
                self.assertFalse(r.problems())

    def test_dole_death_and_delivery_are_distinct(self):
        r=cut();r.dole_dies(by_player=True)
        self.assertEqual((r.outcome,r.mail),(nm.NM_DEFEAT,nm.NM_MAIL_ABOARD))
        r.use_train(pick='forward')
        self.assertEqual((r.outcome,r.mail,r.engine),(nm.NM_DEFEAT,nm.NM_MAIL_DELIVERED,nm.NM_ENGINE_SOUND))
        self.assertFalse(r.problems())

    def test_later_death_never_replaces_finished_run(self):
        r=cut();r.use_train(pick='run');r.dole_dies(by_player=True)
        self.assertEqual((r.outcome,r.mail),(nm.NM_RUN,nm.NM_MAIL_DELIVERED))
        self.assertFalse(r.problems())

    def test_stamp_delivery_requires_separate_yard_acknowledgment(self):
        r=cut();r.use_train(pick='back');r.use_drawer(stamp='take');r.leave()
        self.assertFalse(r.lockridge_reported)
        r.report(acknowledge=False)
        self.assertTrue(r.stamp_delivered)
        self.assertFalse(r.lockridge_reported)
        r.report(acknowledge=True)
        self.assertTrue(r.lockridge_reported)
        self.assertEqual((r.stamps,r.stamps_with_sheriff),(0,1))
        self.assertFalse(r.problems())

    def test_keeping_and_countersigning_are_different_and_exclusive(self):
        for choice,mark in (('keep',nm.NM_STAMP_KEPT),('sign',nm.NM_STAMP_SIGNED)):
            r=cut();r.use_train(pick='back');r.use_drawer(stamp=choice)
            self.assertEqual(r.stamp,mark)
            r.use_drawer(stamp='take')
            self.assertEqual((r.stamp,r.stamps,r.stamp_delivered),(mark,0,False))
            self.assertFalse(r.problems())

    def test_refusing_departure_leaves_no_encounter_or_delivery(self):
        r=nm.Line();r.travel();r.talk_lockridge(pick='ride');r.use_depart(go=False);r.leave()
        self.assertEqual((r.outcome,r.mail,r.train),(nm.NM_NONE,nm.NM_MAIL_ABOARD,nm.NM_TRAIN_YARD))
        self.assertNotIn(100,r.stages)
        self.assertFalse(r.problems())


if __name__=='__main__':unittest.main()
