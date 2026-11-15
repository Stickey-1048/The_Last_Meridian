"""Execute real entry scripts in a small explicit fixture, not native load proof.

Only the downstream Act1Walk is replaced by a counting stub. Menu state and
current stage getters follow the locally inspected CK Base signatures; native
compilation and actual saved-load event timing remain separate acceptance.
"""
import unittest
from pathlib import Path
from sim import Session, Alias
from test_sim import write_scripts, mini_plugin, quest, SCRIPTS

class EntrySession(Session):
    menu = False
    def g_utility_isinmenumode(self):
        return self.menu
    def n_quest_getcurrentstageid(self, obj, context):
        return max(obj.done, default=0)

class WorldFreshEntry(unittest.TestCase):
    def setUp(self):
        sources={name:(SCRIPTS/name).read_text() for name in ('WorldEntry.psc','WorldEntryPlayer.psc')}
        sources['Act1Walk.psc']='''Scriptname TLM:Act1Walk extends Quest
int calls = 0
Function Begin()
 calls += 1
 Start()
EndFunction
'''
        sources['Empty.psc']='Scriptname Mini:Empty extends Quest\n'
        data=[quest(n,'Mini:Empty') for n in ('Preview','Main','Side')]
        data += [quest('Section','TLM:Act1Walk'),quest('Entry','TLM:WorldEntry')]
        self.s=EntrySession(write_scripts(sources),mini_plugin(data,[('Cell','Clearing'),('Cell','Other')]),None,None)
        self.entry=self.s.quests['Entry'].scripts[0]
        self.section=self.s.quests['Section'].scripts[0]
        for prop,key in [('preview','Preview'),('mainquest','Main'),('sidequest','Side'),('section','Section')]:
            self.entry.props[prop]=self.s.quests[key]
        self.entry.props['clearing']=self.s.forms['Clearing']
        self.s.player.cell=self.s.forms['Clearing']
        alias=Alias(self.s.quests['Entry'],{'Id':0,'Name':'FreshEntryPlayer','Flags':[]})
        alias.ref=self.s.player
        alias.scripts.append(self.s._attach({'Name':'TLM:WorldEntryPlayer','Props':[]},alias,self.s.quests['Entry']))
        self.s.quests['Entry'].aliases[0]=alias

    def queue(self):
        self.s.invoke('Entry','QueueFreshEntry',[])

    def calls(self):
        return self.section.vars['calls']

    def test_nothing_starts_without_explicit_request(self):
        self.s.start_quest(self.s.quests['Entry'])
        self.s.run(40)
        self.assertEqual(self.calls(),0)

    def test_duplicate_queue_starts_once_after_timer_not_synchronously(self):
        self.queue();self.queue()
        self.assertEqual(self.calls(),0)
        self.s.run(3)
        self.assertEqual(self.calls(),1)
        self.queue();self.s.invoke('Entry','Begin',[]);self.s.run(5)
        self.assertEqual(self.calls(),1)

    def test_waits_for_menu_exit_and_correct_loaded_cell(self):
        self.s.menu=True;self.s.player.cell=self.s.forms['Other']
        self.queue();self.s.run(3);self.assertEqual(self.calls(),0)
        self.s.menu=False;self.s.run(5);self.assertEqual(self.calls(),0)
        self.s.player.cell=self.s.forms['Clearing'];self.s.player.disabled=True
        self.s.run(7);self.assertEqual(self.calls(),0)
        self.s.player.disabled=False;self.s.run(9);self.assertEqual(self.calls(),1)

    def test_wrong_cell_times_out_and_cannot_rearm_same_session(self):
        self.s.player.cell=self.s.forms['Other']
        self.queue();self.s.run(32)
        self.assertEqual(self.calls(),0)
        self.assertTrue(self.entry.vars['loadcancelled'])
        self.assertFalse(self.s.timers)
        self.s.player.cell=self.s.forms['Clearing'];self.queue();self.s.run(35)
        self.assertEqual(self.calls(),0)

    def test_existing_quest_or_stage_refuses_without_resetting_any_state(self):
        for name,mode in [('Preview','running'),('Main','running'),('Side','running'),('Main','stage'),('Side','stage'),('Section','running')]:
            with self.subTest(name=name,mode=mode):
                self.setUp()
                q=self.s.quests[name]
                if mode=='running':q.running=True
                else:q.done.append(20)
                self.queue();self.s.run(4)
                self.assertEqual(self.calls(),0)
                self.assertEqual(q.done,[20] if mode=='stage' else [])
                self.assertEqual(q.running,mode=='running')

    def test_changed_state_during_delay_refuses_instead_of_rebinding(self):
        self.queue();self.s.quests['Main'].done.append(10);self.s.run(3)
        self.assertEqual(self.calls(),0)
        self.assertEqual(self.s.quests['Main'].done,[10])

    def test_actual_player_alias_load_handler_cancels_pending_request(self):
        self.s.menu=True;self.queue()
        self.s.actor_event(self.s.player,'OnPlayerLoadGame',[],0)
        self.s.run(2);self.s.menu=False;self.s.run(40)
        self.assertEqual(self.calls(),0)
        self.assertTrue(self.entry.vars['loadcancelled'])
        self.assertFalse(self.s.timers)

    def test_load_after_setup_does_not_restart_or_reset_section(self):
        self.queue();self.s.run(3)
        self.s.actor_event(self.s.player,'OnPlayerLoadGame',[],0)
        self.s.run(4);self.queue();self.s.run(6)
        self.assertEqual(self.calls(),1)
        self.assertTrue(self.s.quests['Section'].running)

    def test_wrong_timer_does_not_start_section(self):
        self.queue();self.s.invoke('Entry','OnTimer',[999])
        self.assertEqual(self.calls(),0)

if __name__=='__main__':unittest.main()
