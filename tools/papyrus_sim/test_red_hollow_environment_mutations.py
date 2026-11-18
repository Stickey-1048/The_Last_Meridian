"""Broken copies of the actual PSC must fail meaningful environment regressions.
No installed files/compiler/game. Original source remains unchanged.
"""
import io,shutil,tempfile,unittest
from pathlib import Path
import test_red_hollow as driver
import test_red_hollow_environment as cases
import test_red_hollow_environment_review_repairs as review_cases
from test_sim import SCRIPTS


class EnvironmentMutations(unittest.TestCase):
    def test_actual_environment_guards_reject_broken_programs(self):
        trials=[
            ('surface cell','RedHollowWalk.psc',' || Game.GetPlayer().GetParentCell() != Ref(Alias_GapArrival).GetParentCell()','',cases.RegionsAndPrime,'test_all_four_regions_require_their_actual_anchor_cell'),
            ('original miner','MQ02CQuest.psc',' || outerActor != RHOriginalMiners[outerIndex]','',cases.CrossCellBlast,'test_missing_wrong_cell_offslot_and_substituted_miner_are_closed'),
            ('exact slot','MQ02CQuest.psc',' || safeSlot != RHSurfaceReceipts[minerIndex]','',cases.CrossCellBlast,'test_wrong_surface_slot_control_anchor_and_player_cell_are_closed'),
            ('exact underground','MQ02CQuest.psc','belowRef != RHBelowAnchor || controlRef != RHBreakControl || ','',cases.CrossCellBlast,'test_wrong_surface_slot_control_anchor_and_player_cell_are_closed'),
            ('before move prime','RedHollowWalk.psc','bool Function MovePlayer(ObjectReference targetRef)\n\tlastSample = -1.0\n\tlastArea = 0','bool Function MovePlayer(ObjectReference targetRef)',cases.RegionsAndPrime,'test_move_invalidates_before_effect_and_after_receipt_reads'),
            ('after receipt prime','RedHollowWalk.psc','bool arrived = Road().PlayerAlive() && Road().At(Game.GetPlayer(),targetRef)\n\tlastSample = -1.0\n\tlastArea = 0','bool arrived = Road().PlayerAlive() && Road().At(Game.GetPlayer(),targetRef)',cases.RegionsAndPrime,'test_move_invalidates_before_effect_and_after_receipt_reads'),
            ('final blast','MQ02CQuest.psc',' || !ClearBlastArea(blastRef,surfaceSlots,controlRef,belowRef)','',cases.CrossCellBlast,'test_final_predicate_blocks_wrong_player_cell_with_all11_still_safe'),
            ('precommit blast','RedHollowWalk.psc',' || !Road().ClearBlastArea(Ref(Alias_BreakClosed),SurfaceSlots,Ref(Alias_BreakControl),Ref(Alias_CageBelow))','',cases.CrossCellBlast,'test_precommit_guard_blocks_any_effect_for_wrong_but_nearby_slot_alias'),
            ('only player transition','RedHollowTalk.psc','Function InvalidatePlayerSample()\n\tIf Who == -1','Function InvalidatePlayerSample()\n\tIf Who >= -1',cases.RegionsAndPrime,'test_nonplayer_cell_events_do_not_invalidate_player_prime'),
            ('late operator context','MQ02CQuest.psc','Return blastRef.GetParentCell() == belowRef.GetParentCell() && controlRef.GetParentCell() == belowRef.GetParentCell() && At(Game.GetPlayer(),controlRef,256.0) && PlayerAlive()','Return true',cases.CrossCellBlast,'test_late_native_receipt_player_context_closes_before_effect_and_recovers'),
            ('final effect receipt order','MQ02CQuest.psc','!KnownSafeSurvivors(surfaceSlots) || !Off(openRef) || !On(closedRef) || !ClearBlastArea(blastRef,surfaceSlots,controlRef,belowRef)','!KnownSafeSurvivors(surfaceSlots) || !ClearBlastArea(blastRef,surfaceSlots,controlRef,belowRef) || !Off(openRef) || !On(closedRef)',review_cases.FinalEffectContext,'test_last_effect_receipt_context_loss_preserves_pending_and_recovers'),
            ('temporary unload latches','RedHollowWalk.psc','ElseIf !Road().OperatorReady(Ref(Alias_FiringControl))\n\t\t\toperatorPaused = true','ElseIf !Road().OperatorReady(Ref(Alias_FiringControl))\n\t\t\tRoad().BlockDeadline()',review_cases.OperatorObservation,'test_operator_and_control_unload_pause_then_prime_and_resume_without_catchup'),
            ('unload sample catchup','RedHollowWalk.psc','If operatorPaused || busy || !Local()','If busy || !Local()',review_cases.OperatorObservation,'test_operator_and_control_unload_pause_then_prime_and_resume_without_catchup'),
            ('fall cell','RedHollowWalk.psc','Game.GetPlayer().GetParentCell() != Ref(fallAlias).GetParentCell()','false',cases.RegionFalls,'test_wrong_cell_nonfall_other_actor_and_dead_player_do_not_recover')
        ]
        original=driver.SCRIPTS_NOW
        try:
            for name,file,needle,replacement,cls,method in trials:
                with self.subTest(mutant=name),tempfile.TemporaryDirectory() as temp:
                    folder=Path(temp)
                    for source in SCRIPTS.glob('*.psc'):shutil.copyfile(source,folder/source.name)
                    target=folder/file;text=target.read_text(encoding='utf-8');self.assertEqual(text.count(needle),1,name)
                    target.write_text(text.replace(needle,replacement),encoding='utf-8');driver.SCRIPTS_NOW=folder
                    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite([cls(method)]))
                    self.assertEqual(result.errors,[],name+' produced an invalid test/program: '+stream.getvalue())
                    self.assertGreater(len(result.failures),0,name+' escaped: '+stream.getvalue())
        finally:driver.SCRIPTS_NOW=original
