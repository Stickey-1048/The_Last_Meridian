"""Falsify actual PSC guards by running the existing player tests against copied mutated source.
These are deliberate broken programs, never build/native candidates.
"""
import io
import shutil
import tempfile
import unittest
from pathlib import Path
import test_red_hollow as cases
from test_sim import SCRIPTS
import test_red_hollow_repairs as repairs

class MutationDetection(unittest.TestCase):
    def test_actual_player_cases_reject_broken_consequential_guards(self):
        trials=[
            ('projectile required','RedHollowWalk.psc',' && akProjectile && !abBashAttack && !abHitBlocked','',cases.TravelCourt,'test_only_registered_player_projectile_releases'),
            ('release arrival','MQ02CQuest.psc',' || !At(prisonerActor, releaseRef)','',cases.TravelCourt,'test_rope_partial_move_recovers_without_another_hit'),
            ('actual fee transfer','MQ02CQuest.psc','feeAsked && paymentBox && Game.GetPlayer().GetItemCount(Caps) <= feePlayerBefore - 60 && paymentBox.GetItemCount(Caps) >= feeBoxBefore + 60','feeAsked',cases.TravelCourt,'test_refused_fee_does_not_release_or_repeat_transfer'),
            ('no auto57','MQ02CQuest.psc','shiftEverSafe = true','shiftEverSafe = true\n\t\tmineValue = 57\n\t\tSetStage(57)',cases.MineRoutes,'test_normal_unpledged_rescue_requires_explicit57_then_report'),
            ('correct timeout cause','MQ02CQuest.psc','playerOrdered = ordered','playerOrdered = true',cases.MineRoutes,'test_questions_do_not_arm_and_actual_warned_timeout56'),
            ('menu pause','RedHollowWalk.psc','Utility.IsInMenuMode()','false',cases.AdverseContexts,'test_all_menus_absence_and_load_gap_pause_deadline'),
            ('report exact Continue','RedHollowWalk.psc','detailAnswer != 0','detailAnswer == 1',cases.CustodyAndReports,'test_report_each_detail_page_closes_on_invalid_or_participant_loss'),
            ('living operator','MQ02CQuest.psc','&& Speaking(Alias_Blevins) && At(operatorActor,controlRef,192.0)','&& At(operatorActor,controlRef,192.0)',cases.AdverseContexts,'test_operator_death_or_combat_during_final_ack_does_not_fire'),
            ('current docket','MQ02CQuest.psc','Return Game.GetPlayer() && Game.GetPlayer().GetItemCount(DocketItem) > 0','Return true',cases.CustodyAndReports,'test_drop_copy_during_ack_never_adjourns_or_refills'),
            ('stop moves on player death','RedHollowWalk.psc','If !Ready() || !minerActor || minerActor.IsDisabled()','If !minerActor || minerActor.IsDisabled()',cases.CustodyAndReports,'test_player_dies_during_rescue_effect_stops_remaining_moves'),
            ('actual collapse','MQ02CQuest.psc',' || !Off(openRef) || !On(closedRef)','',cases.AdverseContexts,'test_refused_collapse_is_pending_and_recoverable'),
            ('cancel execution','RedHollowWalk.psc','Road().StopWatching()','; deliberately omitted cancellation',cases.FurtherRefusals,'test_cancelled_execution_is_not_reoffered_without_new_watch'),
            ('short menu edges','RedHollowWalk.psc','; Both edges discard the interval, including a menu wholly between ticks.\n\tlastSample = -1.0\n\tlastArea = 0','; deliberately missing interval invalidation',repairs.MenuEdges,'test_short_registered_open_and_close_discard_the_entire_between_tick_interval'),
            ('reachable pending inspection','RedHollowWalk.psc','; Only the player returns; delivered miners and pending2 remain untouched.\n\t\tMovePlayer(Ref(Alias_CageBelow))','; deliberately missing return',repairs.RescueRecovery,'test_corpse_only_requires_reachable_return_and_real_inspection_then58'),
        ]
        for name,file,old,new,kind,method in trials:
            with self.subTest(guard=name):
                target=Path(tempfile.mkdtemp(prefix='tlm-rh-mutated-'))
                for p in SCRIPTS.glob('*.psc'):shutil.copyfile(p,target/p.name)
                p=target/file;text=p.read_text();self.assertIn(old,text,name);p.write_text(text.replace(old,new))
                previous=cases.SCRIPTS_NOW
                try:
                    cases.SCRIPTS_NOW=target
                    result=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite([kind(method)]))
                finally:cases.SCRIPTS_NOW=previous
                self.assertFalse(result.wasSuccessful(),'broken actual PSC guard escaped: '+name)
