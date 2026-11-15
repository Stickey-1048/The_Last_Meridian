"""Town cleanup may announce living departures, never deaths or failed removal."""
import unittest
from test_act1 import Person, need_act1_build, REF, SCRIPTS, PLUGIN, VANILLA, NATIVES
from sim import run_scenario

class LivingDeparture(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def cues(self, s):
        return [n for n in s.notifications if 'has left the caravan road' in n or 'have left the caravan road' in n]

    def test_living_gang_notice_only_after_town_removal_once(self):
        p = Person(self, coin=1)
        p.to_the_ambush()
        p.press('Dunmore', {'DunmoreHold': [0], 'DunmoreBreaks': [0]}, ['dunmore_speech_success'])
        self.assertEqual(self.cues(p.s), [])
        p.to_town()
        self.assertEqual(self.cues(p.s), ['The surviving Cutters have left the caravan road.'])
        for who in ('Dunmore', 'Cutter1', 'Cutter2', 'Cutter3'):
            actor = p.s.placed[REF + who]
            self.assertFalse(actor.dead)
            self.assertTrue(actor.disabled)
        p.s.invoke('TLM_MQ01', 'ApplyTown', [])
        p.pause()
        self.assertEqual(len(self.cues(p.s)), 1)
        p.hand_over('DebriefSaved')

    def test_lead_death_is_not_a_departure_but_survivors_can_leave_at_town(self):
        p = Person(self)
        p.to_the_ambush()
        p.kill('Dunmore', 'player_kills_lead')
        self.assertEqual(self.cues(p.s), [])
        p.to_town()
        self.assertEqual(len(self.cues(p.s)), 1)
        self.assertTrue(p.s.placed[REF + 'Dunmore'].dead)
        p.hand_over('DebriefSaved')

    def test_all_dead_never_claims_departure(self):
        p = Person(self)
        p.to_the_ambush()
        p.press('Dunmore', {'DunmoreHold': [1], 'DunmoreTurns': [0]}, ['attack_cutter'])
        for who in ('Cutter1', 'Cutter2', 'Cutter3'):
            p.kill(who, 'player_kills_cutter')
        p.kill('Dunmore', 'player_kills_lead')
        p.to_town()
        self.assertEqual(self.cues(p.s), [])

    def test_one_survivor_has_singular_cue(self):
        p = Person(self)
        p.to_the_ambush()
        p.press('Dunmore', {'DunmoreHold': [1], 'DunmoreTurns': [0]}, ['attack_cutter'])
        for who in ('Cutter1', 'Cutter2'):
            p.kill(who, 'player_kills_cutter')
        p.kill('Dunmore', 'player_kills_lead')
        p.to_town()
        self.assertEqual(self.cues(p.s), ['The surviving Cutter has left the caravan road.'])

    def test_failed_disable_never_claims_gang_is_gone(self):
        p = Person(self)
        original = p.s.n_alias_trytodisable
        def blocked(alias, context):
            if alias.ref and alias.ref.editor_id == REF + 'Cutter1':
                return False
            return original(alias, context)
        p.s.n_alias_trytodisable = blocked
        p.to_town()
        self.assertFalse(p.s.placed[REF + 'Cutter1'].disabled)
        self.assertEqual(self.cues(p.s), [])

    def test_missing_alias_does_not_prove_departure(self):
        p = Person(self)
        q = p.s.quests['TLM_MQ01']
        next(a for a in q.aliases.values() if a.name == 'CutterC').ref = None
        p.to_town()
        self.assertEqual(self.cues(p.s), [])

    def test_audit_and_scored_run_have_no_departure_notice_or_extra_boxes(self):
        for scenario in (5, 12):
            s = run_scenario(scenario, SCRIPTS, PLUGIN, VANILLA, NATIVES)
            self.assertEqual(self.cues(s), [], scenario)
            self.assertEqual(s.message_boxes, [], scenario)

if __name__ == '__main__':
    unittest.main()
