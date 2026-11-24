# Cloud invariant058 author handoff

Base064b11d580147fcb8f5f0db39b28e0c19b0ef0f1, NEW isolated successor. The cloud's two failed tests exposed stale invariant preconditions after accepted056 model alignment. Before editing, actual SQ01Exhaustive.test_no_invariant_violations reproduced exactly224 states flagged for missing20 and64 for missing25.

ONLY two existing condition lines change in tools/logic_model/invariants.py: both forward obligations now additionally require `(s.e1 or s.e2)`, matching unchanged production SQ01Quest.PhysicalComparisonDone/RecomputeEvidence and accepted model. Existing ledger, evidence level, undecided and missing-stage conditions remain. No obligation/message is removed; reverse stage-validity, outcome, custody, metrics, all other state/edge invariants and test sites remain literal. Existing20 objective repair remains056 model behavior and is unchanged here. No production PSC, model, generator, generated cases/data, workflow, history or existing test changes.

Four focused methods PASS0.007s: genuine ledger/journal both orders and paper+Ada Book level2 remain valid without20/25; either physical clue still requires20, and level2 with actual part still requires25; independent corrupted stage/custody/outcome-objective states remain rejected; exact two-condition inverse pins every other invariant byte to the parent. Actual parent check_sq01_state substituted into the new paper-only regression fails as intended, confirming sensitivity to this defect. The tests do not hide missing20/25 after physical inspection.

One authorized existing logic-only aggregate run:150 tests in41.889s, zero failures/errors, eight unchanged historical skips. It executes the affected exhaustive SQ01 graph and random joint walks, plus existing model tests; no test count or skip was edited. Generator --check PASS53cases/335steps/1340checks. Production/model/generator/MatrixCases/JSON/test_invariants/run_checks Git-LF pins and exact inverse are recorded in provenance.json. No build/compiler/SDK/native/network, ancestor replay or cloud aggregate success claim. Further pipeline stops remain possible and must be handled on their actual evidence.

Freeze requires independent Luis/root review before publication. Initial056 intentional assertions and cloud history remain preserved.

Sam, author, 2026-11-24.
