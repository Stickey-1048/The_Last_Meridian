"""Account for every discovered test; route only explicit historical contracts."""
import json,subprocess,sys,unittest
from pathlib import Path
from composed_test_contexts import ROOT,FD7,GUIDANCE,TERRAIN,AFTERMATH_BASE,SKELETON_BASE,context,prepare
MODULES=('test_rh_return_account_skeleton', 'test_rh_return_account', 'test_rh_return_account_candidate', 'test_act1', 'test_case_read_access', 'test_case_read_access_candidate', 'test_composed_source', 'test_conversation', 'test_death_ack', 'test_departure', 'test_four_flags', 'test_four_flags_candidate', 'test_four_flags_late_custody', 'test_four_flags_mutations', 'test_four_flags_projection', 'test_four_flags_recovery', 'test_greenwater', 'test_greenwater_candidate', 'test_greenwater_clarity', 'test_greenwater_clarity_projection', 'test_greenwater_projection', 'test_greenwater_relief', 'test_greenwater_relief_candidate', 'test_greenwater_relief_history', 'test_greenwater_relief_mutations', 'test_greenwater_relief_projection', 'test_greenwater_relief_review_repair', 'test_greenwater_repair', 'test_greenwater_world_clone', 'test_guide', 'test_matrix_cases', 'test_mercy_briefing', 'test_mercy_briefing_candidate', 'test_mercy_briefing_projection', 'test_night_mail', 'test_night_mail_candidate', 'test_night_mail_mutations', 'test_night_mail_projection', 'test_night_mail_review_repairs', 'test_night_mail_router', 'test_night_mail_scenes', 'test_night_mail_world_clone', 'test_overlap', 'test_people', 'test_placed', 'test_player_guidance', 'test_player_guidance_candidate', 'test_player_guidance_terrain', 'test_red_hollow', 'test_red_hollow_candidate', 'test_red_hollow_environment', 'test_red_hollow_environment_candidate', 'test_red_hollow_environment_mutations', 'test_red_hollow_environment_projection', 'test_red_hollow_environment_review_repairs', 'test_red_hollow_mutations', 'test_red_hollow_projection', 'test_red_hollow_repairs', 'test_red_hollow_world_clone', 'test_rh_terrain_002', 'test_sim', 'test_world_entry')
WHOLE={'test_case_read_access_candidate':FD7,'test_player_guidance_candidate':GUIDANCE}
EXACT={
 'test_rh_return_account_candidate.ReturnAccountCandidate.test_added_workflow_and_allocation_shift_are_rejected':SKELETON_BASE,
 'test_rh_return_account_candidate.ReturnAccountCandidate.test_current_successor_nominal_and_runtime_selection':SKELETON_BASE,
 'test_rh_return_account_candidate.ReturnAccountCandidate.test_only_four_exact_old_provenance_methods_move_to_real13c_context':SKELETON_BASE,
 'test_rh_return_account_candidate.ReturnAccountCandidate.test_repin_cannot_waive_runtime_old_guard_workflow_or_approved_message_mutations':SKELETON_BASE,

 'test_composed_source.CurrentComposition.test_fixture_repair_keeps_all_runtime_and_production_builder_sources_exact':AFTERMATH_BASE,
 'test_composed_source.CurrentComposition.test_exact_modules_baseline_and_combined_runtime_selection':AFTERMATH_BASE,
 'test_composed_source.CurrentComposition.test_repin_does_not_waive_baseline_module_or_integration_changes':AFTERMATH_BASE,
 'test_composed_source.CurrentComposition.test_added_workflow_is_not_an_implicit_composition_input':AFTERMATH_BASE,

 'test_greenwater_candidate.TheCandidate.test_the_earlier_manifests_and_verifiers_are_as_they_were_and_say_nothing_of_it':FD7,
 'test_red_hollow_world_clone.RedHollowClone.test_101_aliases_have_exact_mixed_ownership_and_no_new_condemned':FD7,
 'test_rh_terrain_002.Terrain002.test_exact_source_candidate_and_frozen_negative':TERRAIN,
 'test_four_flags_projection.FourFlagsProjection.test_every_old_message_is_exact_except_twelve_declared_technical_availability_updates':FD7,
}
for name in ('test_original99_aliases_and_same_original_reference_keys_are_preserved','test_all241_new_allocations_match_actual_append_and_raw_emission','test_all_unrelated_old_record_payloads_and_ids_remain_exact','test_geometry_readback_contains_real_enclosures_supported_shelters_and_all_cohort_space','test_raw_guard_rejects_nonflat_land_without_trusting_writer'):
    EXACT['test_red_hollow_environment_projection.EnvironmentProjection.'+name]=FD7

def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item
def classify(ids):
    if len(ids)!=len(set(ids)):raise AssertionError('Duplicate discovered test IDs')
    modules={n.split('.')[0] for n in ids}
    if modules!=set(MODULES):raise AssertionError('Unaccounted/missing test modules: '+repr(modules^set(MODULES)))
    if not set(EXACT)<=set(ids):raise AssertionError('Historical exact test ID removed or renamed')
    groups={}
    for name in ids:groups.setdefault(EXACT.get(name,WHOLE.get(name.split('.')[0],'current')),[]).append(name)
    if sum(map(len,groups.values()))!=len(ids):raise AssertionError('Test accounting mismatch')
    return groups
def main():
    prepare()
    sys.path.insert(0,str(ROOT/'tools/papyrus_sim'))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tools/papyrus_sim'))
    tests=list(flatten(suite));groups=classify([t.id() for t in tests]);byid={t.id():t for t in tests}
    ledger={'scope':'Historical preservation contexts plus current behavioral/composed source tests; not all-current','groups':groups,'results':{}}
    live=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(byid[n] for n in groups.get('current',[])))
    ledger['results']['current']={'tests':live.testsRun,'failures':len(live.failures),'errors':len(live.errors),'skips':len(live.skipped)}
    failed=not live.wasSuccessful() or bool(live.skipped)
    code="import sys,unittest; r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])); sys.exit(not r.wasSuccessful() or bool(r.skipped))"
    for revision,names in groups.items():
        if revision=='current':continue
        target=context(revision)
        # Some archived tests need ordinary baseline metadata. Reproducible
        # same-master construction is part of prepare, never a leftover build.
        result=subprocess.run([sys.executable,'-B','-c',code]+names,cwd=target/'tools/papyrus_sim',capture_output=True,text=True)
        log=ROOT/'build/composed'/('historical-tests-'+revision[:8]+'.txt');log.write_text(result.stdout+result.stderr,encoding='utf-8')
        print('== historical context '+revision+'; '+str(len(names))+' accounted tests ==',flush=True)
        print(result.stdout+result.stderr,flush=True)
        ledger['results'][revision]={'accountedTests':len(names),'exitCode':result.returncode,'log':str(log)}
        failed=failed or result.returncode!=0
    path=ROOT/'build/composed/test-context-ledger.json';path.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
    print('Context accounting: '+str(len(tests))+' discovered; '+str(len(groups.get('current',[])))+' current; '+str(len(tests)-len(groups.get('current',[])))+' exact historical; ledger '+str(path),flush=True)
    return int(failed)
if __name__=='__main__':sys.exit(main())
