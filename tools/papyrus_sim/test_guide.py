"""Optional help is repeatable and read-only; this is not visual/game proof."""
import unittest
from test_act1 import Person, need_act1_build, REF, SCRIPTS, PLUGIN, VANILLA, NATIVES
from sim import Session, run_scenario

class DemoGuide(unittest.TestCase):
    def setUp(self):
        self.data = need_act1_build(self)

    def read(self, p, place):
        before = len(p.s.message_boxes)
        p.press(place)
        self.assertEqual(len(p.s.message_boxes), before + 1)
        return p.s.message_boxes[-1]

    def test_three_distinct_help_objects_are_disabled_until_demo_and_repeatable(self):
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        for name in ('GuideWreck', 'GuideRoad', 'GuideMercy'):
            self.assertTrue(s.placed[REF + name].disabled)
        p = Person(self)
        for guide, place in [('GuideWreck', 'Wreck'), ('GuideRoad', 'Caravan road'), ('GuideMercy', 'Mercy Crossing')]:
            for _ in range(2):
                text = self.read(p, guide)
                self.assertIn(place, text)
                self.assertIn('dispatch case', text)
                self.assertIn('this guide is only help', text)
        self.assertEqual(p.has(p.caps), 0)
        self.assertFalse(p.state.has_dispatch)

    def test_early_town_stage34_without_dispatch_redirects_to_wreck(self):
        p = Person(self)
        p.to_town()
        self.assertIn(34, p.s.quests['TLM_MQ01'].done)
        self.assertNotIn(20, p.s.quests['TLM_MQ01'].done)
        self.assertIn('return to the wreck', self.read(p, 'GuideMercy'))

    def test_exterior_copy_flag_keeps_help_read_only_and_uses_the_fenced_yard_route(self):
        p = Person(self)
        for alias in p.s.quests['TLM_A1'].aliases.values():
            if alias.name in ('GuideWreck', 'GuideRoad', 'GuideMercy'):
                for script in alias.scripts:
                    script.props['exterior'] = True
        self.assertIn('fenced cabin yard', self.read(p, 'GuideMercy'))
        p.press('Dispatch', events=['take_dispatch'])
        before = list(p.s.quests['TLM_MQ01'].done)
        text = self.read(p, 'GuideWreck')
        self.assertIn('marked route', text)
        self.assertIn('eastern marked route bypasses', text)
        self.assertNotIn('timber posts', text)
        self.assertEqual(p.s.quests['TLM_MQ01'].done, before)

    def test_dispatch_then_town_points_to_pritchard_without_delivering(self):
        p = Person(self)
        p.press('Dispatch', events=['take_dispatch'])
        self.assertIn('take the dispatch', self.read(p, 'GuideWreck'))
        self.assertIn('hand over', self.read(p, 'GuideMercy'))
        self.assertNotIn(40, p.s.quests['TLM_MQ01'].done)
        p.to_town()
        self.assertIn('hand over', self.read(p, 'GuideMercy'))
        self.assertNotIn(50, p.s.quests['TLM_MQ01'].done)

    def test_mid_handoff_repeats_instruction_without_advancing(self):
        p = Person(self)
        p.press('Dispatch', events=['take_dispatch'])
        p.to_town()
        p.s.quests['TLM_MQ01'].done.append(50)
        # Isolated state query: no model event is asserted by this guide.
        before = list(p.s.quests['TLM_MQ01'].done)
        p.s.press_activate(REF + 'GuideMercy')
        p.pause()
        self.assertIn('speak to Owen Pritchard again', p.s.message_boxes[-1])
        self.assertEqual(p.s.quests['TLM_MQ01'].done, before)

    def test_completion_wins_even_without_dispatch_and_never_offers_fake_routes(self):
        p = Person(self)
        p.s.quests['TLM_MQ01'].done.append(60)
        before = list(p.s.quests['TLM_MQ01'].done)
        p.s.press_activate(REF + 'GuideWreck')
        p.pause()
        text = p.s.message_boxes[-1]
        self.assertIn('First-section demo complete', text)
        self.assertIn('not implemented', text)
        self.assertNotIn('search the ground', text)
        self.assertEqual(p.s.quests['TLM_MQ01'].done, before)

    def test_nonplayer_activation_and_audit_never_show_guide(self):
        p = Person(self)
        guide = p.s.placed[REF + 'GuideWreck']
        before = len(p.s.message_boxes)
        p.s.ref_event(guide, 'OnActivate', [p.s.placed[REF + 'Pritchard']], 0)
        p.pause()
        self.assertEqual(len(p.s.message_boxes), before)
        audit = run_scenario(12, SCRIPTS, PLUGIN, VANILLA, NATIVES)
        self.assertEqual(audit.message_boxes, [])

    def test_guide_source_has_no_quest_inventory_or_actor_mutators(self):
        import re
        source = (SCRIPTS / 'Act1Guide.psc').read_text()
        self.assertEqual(set(re.findall(r'\.(\w+)\(', source)), {'GetPlayer', 'CanReadGuide', 'GetStageDone', 'MessageBox'})
        a1 = next(q for q in self.data['Quests'] if q['EditorId'] == 'TLM_A1')
        guides = a1['Aliases'][-3:]
        old_prefix = ['Marshal', 'Dispatch', 'Revolver', 'Journal', 'Ledger', 'BrakeShoes', 'DrawBar',
                      'AmbushSight', 'AmbushCenter', 'Wagon', 'Nell', 'Abel', 'Dunmore', 'Cutter1', 'Cutter2', 'Cutter3',
                      'TownGate', 'Talbot', 'Pritchard', 'Pike', 'Vane', 'Keene', 'Haskell', 'NoticeBoard', 'Stove', 'CaravanYard',
                      'DecorWreckOuter', 'DecorWreckRear', 'DecorRoadLeft', 'DecorRoadRight', 'DecorMercyLeft', 'DecorMercyRight', 'DecorMercyCounter']
        # The baseline has 33 A1 aliases (plus eight separate trial references);
        # preserve the entire existing A1 prefix in its exact order.
        self.assertEqual([a['Name'] for a in a1['Aliases'][:-3]], old_prefix)
        self.assertEqual([a['Name'] for a in guides], ['GuideWreck', 'GuideRoad', 'GuideMercy'])
        for alias in guides:
            self.assertEqual(alias['Scripts'][0]['Name'], 'TLM:Act1Guide')
        activators = {a['EditorId']: a for a in self.data['Records']}
        for name in ('GuideWreck', 'GuideRoad', 'GuideMercy'):
            self.assertIn('Demo guide', activators['TLM_ACTI_' + name]['Name'])

if __name__ == '__main__':
    unittest.main()
