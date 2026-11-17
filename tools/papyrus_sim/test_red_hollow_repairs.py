"""Consolidated Sam/Nora repair regressions. Actual PSC, seeded adverse native
responses and supplied synthetic fixtures; no native-game acceptance.
Reachable recovery refuses the test driver's cross-zone walk_to shortcut.
"""
import json
import unittest
from sim import Session
from test_red_hollow import Hollow,P,R


def zone(pos):
    x,y,z=pos
    if -128<=x<=1664:return 'court'
    if 2944<=x<=4864:return 'surface'
    if 6016<=x<=7808:return 'below'
    if 9088<=x<=10624:return 'gallery'
    return None


def reachable(a,name,**answers):
    a.t.assertEqual(a.s.player.cell,a.ref(name).cell)
    a.t.assertIsNotNone(zone(a.s.player.pos))
    a.t.assertEqual(zone(a.s.player.pos),zone(a.ref(name).pos),'unrepresented cross-zone walk_to is forbidden')
    a.use(name,**answers)


def set_start_gate(a,quest_id,result):
    old=a.s.n_quest_start
    def gate(q,ctx):
        if q.editor_id==quest_id:return result  # SEEDED refusal or anomalous true-without-running
        return old(q,ctx)
    a.s.n_quest_start=gate
    return old


class RescueRecovery(unittest.TestCase):
    def deliver(self,mode):
        a=Hollow(self);a.below();victim=a.ref('Miner07');victim.protected_override=False
        old=a.s.n_objectreference_moveto
        def during_move(ref,ctx,*args):
            target=a.s._ref_of(args[0])
            player_surface=ref is a.s.player and target is a.ref('CageSurface')
            if player_surface and mode=='before':a.s.n_actor_kill(victim,None,a.s.player)
            result=old(ref,ctx,*args)
            if player_surface and mode=='after':a.s.n_actor_kill(victim,None,a.s.player)
            if player_surface and mode=='corpse':victim.dead=True  # SEEDED corpse, no death event or killer evidence
            return result
        a.s.n_objectreference_moveto=during_move
        a.rescue();a.s.n_objectreference_moveto=old
        self.assertEqual(zone(a.s.player.pos),'surface');self.assertEqual(a.g('MinePending'),2)
        self.assertEqual(a.g('Survivors'),10);self.assertEqual(a.g('ShiftSaved'),0)
        return a
    def test_actual_event_before_and_after_player_surface_move_recovers_from_surface_control(self):
        for mode in ('before','after'):
            with self.subTest(boundary=mode):
                a=self.deliver(mode);delivered={i:a.ref('Miner%02d'%i).pos for i in range(1,12) if i!=7}
                calls={i:a.calls.count(('moveto',a.s._whom(a.ref('Miner%02d'%i)))) for i in delivered}
                self.assertTrue(a.v('minerDeathEventSeen')[6]);self.assertEqual(a.v('minerDeathCauses')[6],1)
                reachable(a,'CageControl',PendingRescue=0,Rescue=0)
                self.assertEqual(a.g('MinePending'),0);self.assertEqual(a.g('ObservedDeaths'),1)
                self.assertEqual(a.g('Survivors'),10);self.assertEqual(a.v('minerfates')[6],4)
                for i,pos in delivered.items():
                    self.assertEqual(a.ref('Miner%02d'%i).pos,pos)
                    self.assertEqual(a.calls.count(('moveto',a.s._whom(a.ref('Miner%02d'%i)))),calls[i])
                reachable(a,'Resolve',Resolve=2);self.assertEqual(a.g('Mine'),58);self.assertEqual(a.g('ShiftSaved'),0)
    def test_corpse_only_requires_reachable_return_and_real_inspection_then58(self):
        a=self.deliver('corpse');delivered={i:a.ref('Miner%02d'%i).pos for i in range(1,12) if i!=7}
        self.assertFalse(a.v('minerDeathEventSeen')[6]);self.assertEqual(a.g('ObservedDeaths'),0)
        reachable(a,'CageControl',PendingRescue=0,Rescue=0)
        self.assertEqual(a.g('MinePending'),2);self.assertEqual(a.g('ObservedDeaths'),0)
        reachable(a,'CageControl',PendingRescue=1)
        self.assertEqual(zone(a.s.player.pos),'below');self.assertEqual(a.g('MinePending'),2)
        reachable(a,'Roster');self.assertEqual(a.g('ObservedDeaths'),1);self.assertEqual(a.v('minerDeathCauses')[6],3)
        reachable(a,'BelowControl',HoistBelow=0,Rescue=0)
        self.assertEqual(zone(a.s.player.pos),'surface');self.assertEqual(a.g('MinePending'),0)
        for i,pos in delivered.items():self.assertEqual(a.ref('Miner%02d'%i).pos,pos)
        reachable(a,'Resolve',Resolve=2);self.assertEqual(a.g('Mine'),58);self.assertEqual(a.g('Survivors'),10)
    def test_return_cancel_and_missing_fate_never_clear_pending_or_infer_death(self):
        a=self.deliver('corpse');before=a.s.player.pos
        reachable(a,'CageControl',PendingRescue=2);self.assertEqual(a.g('MinePending'),2)
        self.assertEqual(zone(a.s.player.pos),'surface');self.assertEqual(a.g('ObservedDeaths'),0)
        seven=next(x for x in a.q.aliases.values() if x.name=='Miner07');seven.ref=None
        reachable(a,'CageControl',PendingRescue=1);reachable(a,'Roster')
        self.assertEqual(a.g('MinePending'),2);self.assertEqual(a.g('ObservedDeaths'),0);self.assertEqual(a.g('Mine'),0)


class PrisonerRestaging(unittest.TestCase):
    def test_refused_initial_move_is_retried_by_nearby_court_without_resetting_old_actor(self):
        a=Hollow(self,False);lead=a.s.placed['TLM_REF_A1_Dunmore'];key=('moveto',a.s._whom(lead));a.refuse.add(key)
        a.use('MercyTravel',Travel=0);self.assertTrue(a.walk.vars['setupdone']);self.assertIsNone(a.walk.props['alias_condemned'].ref)
        a.refuse.clear();reachable(a,'CourtRecord',Court=3)
        self.assertIs(a.walk.props['alias_condemned'].ref,lead);self.assertTrue(a.v('prisonerStaged'))
        original=next(x for x in a.s.quests['TLM_MQ01'].aliases.values() if x.name=='CutterLead')
        self.assertIs(original.ref,lead);self.assertEqual(a.g('Court'),0);self.assertFalse(lead.dead)
        calls=a.calls.count(key);reachable(a,'CourtRecord',Court=3);self.assertEqual(a.calls.count(key),calls)
    def test_initially_unavailable_cast_can_be_staged_later_but_no_resurrection(self):
        a=Hollow(self,False);oldactors=[x.ref for x in a.s.quests['TLM_MQ01'].aliases.values() if x.name in ('CutterLead','CutterA','CutterB','CutterC')]
        for actor in oldactors:actor.combat_target=a.s.player
        a.use('MercyTravel',Travel=0);self.assertIsNone(a.walk.props['alias_condemned'].ref)
        for actor in oldactors:actor.combat_target=None
        reachable(a,'CourtRecord',Court=3);self.assertIs(a.walk.props['alias_condemned'].ref,oldactors[0])
        oldactors[0].dead=True;before=len(a.calls);reachable(a,'CourtRecord',Court=3)
        self.assertTrue(oldactors[0].dead);self.assertEqual(a.walk.props['alias_condemned'].ref,oldactors[0]);self.assertFalse(any(k[0]=='moveto' for k in a.calls[before:]))
    def test_resolved_and_pending_prisoner_are_never_relocated_by_setup_retry(self):
        a=Hollow(self);a.shoot();prisoner=a.walk.props['alias_condemned'].ref;key=('moveto',a.s._whom(prisoner));before=a.calls.count(key)
        a.s.invoke('TLM_RH','SetUp',[]);self.assertEqual(a.g('Court'),11);self.assertEqual(a.calls.count(key),before)


class StartupBoundaries(unittest.TestCase):
    def test_road_start_failure_has_no_cast_move_claim_or_busy_leak_and_retry_works(self):
        for result in (False,True):
            with self.subTest(start_result=result):
                a=Hollow(self,False);old=set_start_gate(a,'TLM_MQ02C',result)
                a.use('MercyTravel',Travel=0)
                self.assertFalse(a.q.running);self.assertFalse(a.walk.vars['setupdone']);self.assertFalse(a.walk.vars['busy'])
                self.assertTrue(a.ref('Quill').disabled);self.assertIsNone(a.walk.props['alias_condemned'].ref);self.assertEqual(a.q.done,[])
                self.assertTrue(all(x.ref is None for x in a.q.aliases.values()))
                a.s.n_quest_start=old;a.use('MercyTravel',Travel=0);self.assertIn(10,a.q.done);self.assertFalse(a.ref('Quill').disabled)
    def test_controller_start_failure_is_retried_through_ordinary_pritchard_activation(self):
        for result in (False,True):
            old=Session.n_quest_start
            def gate(session,q,ctx,result=result):
                if q.editor_id=='TLM_RH':return result
                return old(session,q,ctx)
            Session.n_quest_start=gate
            try:a=Hollow(self,False)
            finally:Session.n_quest_start=old
            self.assertFalse(a.w.running);self.assertTrue(a.ref('MercyTravel').disabled);self.assertFalse(a.walk.vars['busy'])
            a.s.answers={'TLM_MSG_MB_Hub':[3]};a.s.walk_to('TLM_REF_A1_Pritchard');a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
            self.assertTrue(a.w.running);self.assertFalse(a.ref('MercyTravel').disabled)
            a.use('MercyTravel',Travel=0);self.assertIn(10,a.q.done)
    def test_evidence_start_failure_preserves_copy_and_issues_no_history_claim_until_running(self):
        for result in (False,True):
            a=Hollow(self,False);old=set_start_gate(a,'TLM_MQ02C',result)
            a.s.answers={'TLM_MSG_MB_Hub':[2],'TLM_MSG_MB_Pike':[0],'TLM_MSG_MB_Docket':[0]}
            a.s.walk_to('TLM_REF_A1_Pritchard');a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
            self.assertEqual(a.p.has('TLM_BOOK_Docket2298'),1);self.assertFalse(a.q.running);self.assertEqual(a.q.done,[])
            self.assertEqual(a.g('Docket2298Held'),0);self.assertTrue(a.ref('Quill').disabled)
            a.s.n_quest_start=old;a.wait();self.assertIn(16,a.q.done);self.assertNotIn(10,a.q.done);self.assertEqual(a.g('Docket2298Held'),1)
            self.assertEqual(a.p.has('TLM_BOOK_Docket2298'),1)


class DeathAttribution(unittest.TestCase):
    def test_distant_actual_events_preserve_player_or_nonplayer_through_later_inspection(self):
        for cause in (1,2,3):
            a=Hollow(self);a.below();a.use('BelowControl',HoistBelow=1)
            victim=a.ref('Miner04');victim.protected_override=False
            a.s.n_actor_kill(victim,None,a.s.player if cause==1 else a.ref('Quill') if cause==2 else None);a.wait()
            self.assertEqual(a.v('minerDeathCauses')[3],cause);self.assertTrue(a.v('minerDeathEventSeen')[3]);self.assertNotEqual(a.v('minerfates')[3],4)
            a.use('CageControl',Descend=0);reachable(a,'Roster')
            self.assertEqual(a.v('minerDeathCauses')[3],cause);self.assertEqual(a.v('minerfates')[3],4)
            a.s.invoke('TLM_MQ02C','ObserveDeath',[3]);self.assertEqual(a.v('minerDeathCauses')[3],cause)
            self.assertEqual(a.s.invoke('TLM_MQ02C','DeathCauseCount',[cause]),1)
    def test_corpse_only_is_unknown_and_report_has_separate_current_unknown_count(self):
        a=Hollow(self);a.below();a.ref('Miner05').dead=True;reachable(a,'Roster')
        self.assertEqual(a.v('minerDeathCauses')[4],3);self.assertEqual(a.s.invoke('TLM_MQ02C','DeathCauseCount',[1]),0);self.assertEqual(a.s.invoke('TLM_MQ02C','DeathCauseCount',[2]),0)
        reachable(a,'BelowControl',HoistBelow=0,Rescue=0);reachable(a,'Resolve',Resolve=2);a.return_report()
        self.assertEqual(a.g('Reported'),1)
        text=a.messages[P+'ReportFacts']['Text'];self.assertIn('known nonplayer %g; unknown %g',text)
        self.assertEqual(a.s.invoke('TLM_MQ02C','DeathCauseCount',[3]),1)


class MenuEdges(unittest.TestCase):
    def test_short_registered_open_and_close_discard_the_entire_between_tick_interval(self):
        for name in ('PauseMenu','PipboyMenu','ContainerMenu','TerminalMenu','MessageBoxMenu'):
            a=Hollow(self);a.below(True);a.wait(2);left=a.v('deadlineSeconds')
            self.assertIn(name,a.s.menu_watches)
            a.s.menu_event(name,True);a.s.run(a.s.now);self.assertEqual(a.walk.vars['lastsample'],-1)
            a.s.now+=0.75;a.s.menu_event(name,False);a.s.run(a.s.now);self.assertEqual(a.walk.vars['lastsample'],-1)
            a.s.invoke('TLM_RH','OnTimer',[1],until=a.s.now)
            self.assertEqual(a.v('deadlineSeconds'),left)
            a.wait(1.05);self.assertAlmostEqual(a.v('deadlineSeconds'),left-1,places=5)
    def test_court_short_menu_and_nested_menus_pause_both_edges(self):
        a=Hollow(self);a.use('Watch',Court=1,Watch=0);a.wait(2);left=a.v('courtRemaining')
        a.s.menu_event('PipboyMenu',True);a.s.run(a.s.now);a.s.menu_event('PipboyHolotapeMenu',True);a.s.run(a.s.now)
        a.s.now+=0.7;a.s.menu_event('PipboyHolotapeMenu',False);a.s.run(a.s.now);a.s.invoke('TLM_RH','OnTimer',[1],until=a.s.now)
        self.assertEqual(a.v('courtRemaining'),left)
        a.s.menu_event('PipboyMenu',False);a.s.run(a.s.now);a.s.invoke('TLM_RH','OnTimer',[1],until=a.s.now);self.assertEqual(a.v('courtRemaining'),left)
    def test_court_uncertainty_is_recoverable_only_through_new_explicit_watch_warning(self):
        a=Hollow(self);a.use('Watch',Court=1,Watch=0);a.s.menu_event('UnverifiedModMenu',True);a.wait()
        self.assertTrue(a.walk.vars['menuuncertain']);self.assertFalse(a.v('courtWatching'))
        a.s.menu_event('UnverifiedModMenu',False);a.wait();a.use('Watch',Court=1,Watch=0)
        self.assertFalse(a.walk.vars['menuuncertain']);self.assertTrue(a.v('courtWatching'))
        before=a.v('courtRemaining');a.wait(2);self.assertLess(a.v('courtRemaining'),before)

    def test_load_reregisters_exact_supported_names_without_wildcard_and_keeps_gap_paused(self):
        a=Hollow(self);a.below(True);left=a.v('deadlineSeconds');a.s.menu_watches={};a.s.now+=900
        a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0);a.s.run(a.s.now)
        self.assertEqual(len(a.s.menu_watches),26);self.assertNotIn('*',a.s.menu_watches)
        a.s.menu_event('PauseMenu',True);a.s.run(a.s.now);a.s.now+=0.75;a.s.menu_event('PauseMenu',False);a.s.run(a.s.now);a.s.invoke('TLM_RH','OnTimer',[1],until=a.s.now)
        self.assertEqual(a.v('deadlineSeconds'),left);self.assertEqual(a.g('Mine'),0)
    def test_observed_unregistered_menu_uncertainty_blocks_until_explicit_warning_renewal(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();a.s.menu_event('UnverifiedModMenu',True);a.wait()
        self.assertTrue(a.walk.vars['menuuncertain']);self.assertEqual(a.g('DeadlineArmed'),0)
        a.s.menu_event('UnverifiedModMenu',False);a.wait(700);self.assertEqual(a.g('Mine'),0)
        a.warning();self.assertFalse(a.walk.vars['menuuncertain']);self.assertEqual(a.g('DeadlineArmed'),1)


class TranscriptAndNotice(unittest.TestCase):
    def transcript(self,missed):
        a=Hollow(self,False);a.s.set_global('TLM_G_CaravanOutcome',4 if missed else 1) # Explicit resolved prior-road fixture, not a newly played route.
        lead=a.s.placed['TLM_REF_A1_Dunmore'];lead.dead=True
        a.use('MercyTravel',Travel=0);prisoner=a.walk.props['alias_condemned'].ref
        self.assertIsNot(prisoner,lead);self.assertFalse(prisoner.dead)
        node='cutter_rope_missed' if missed else 'cutter_rope';a.answer(**{node:0});a.s.player.pos=prisoner.pos;a.s.press_activate(a.s._whom(prisoner));a.wait();self.assertEqual(a.g('SilverRoad'),1)
        a.pos('Transcript');a.s.answers={P+'T_'+node+'_1':[0]};before=len(a.s.messages_shown);a.s.press_activate(R+'Transcript');a.wait()
        self.assertEqual(a.s.messages_shown[before:],[P+'T_'+node+'_1'])
    def test_each_cutter_transcript_uses_only_its_actual_context(self):
        self.transcript(False);self.transcript(True)
    def test_living_roark_does_not_make_untimed_notice_claim_she_is_unavailable(self):
        a=Hollow(self);a.mouth();a.listen();a.pos('CageControl')
        self.assertTrue(a.s.invoke('TLM_RH','TalkOK',[a.ref('Roark')]));self.assertTrue(a.s.invoke('TLM_MQ02C','OperatorReady',[a.ref('FiringControl')]))
        a.use('CageControl',NoWarning=0,Descend=0)
        self.assertIn(P+'NoWarning',a.s.messages_shown);self.assertEqual(a.g('DeadlineArmed'),0)
        self.assertEqual(a.messages[P+'NoWarning']['Text'],'[Rescue fallback]\n\nNo warned rescue deadline has been accepted. You can operate the staged hoist without arming one.')


class SuppliedIdentity(unittest.TestCase):
    def test_delivered_death_requires_actual_assigned_actor_not_only_who_number(self):
        a=Hollow(self);a.below();a.ref('Miner06').dead=True;a.ref('Miner07').dead=True
        a.s.invoke('TLM_RH','HollowActorDied',[106,1,a.ref('Miner07')])
        self.assertFalse(a.v('minerDeathEventSeen')[5]);self.assertEqual(a.v('minerDeathCauses')[5],0)
        a.s.invoke('TLM_RH','HollowActorDied',[106,1,a.ref('Miner06')])
        self.assertTrue(a.v('minerDeathEventSeen')[5]);self.assertEqual(a.v('minerDeathCauses')[5],1)
